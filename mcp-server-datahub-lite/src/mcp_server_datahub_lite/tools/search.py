"""`search` tool — DuckDB 위에서 가벼운 풀텍스트 + 필터 검색."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from ..lite import get_client
from ..server import mcp


FILTER_FIELDS = {
    "entity_type",
    "platform",
    "tag",
    "glossary_term",
    "owner",
    "domain",
    "subtype",
    "entity_subtype",
    "env",
}


def _parse_simple_filter(expr: Optional[str]) -> List[Tuple[str, str]]:
    """Very small WHERE-like parser: `field = value [AND field = value]...`.

    IN / OR / NOT / parentheses are not supported in this lite impl — we log
    unsupported tokens for the caller. Values may be quoted with "..." or '...'.
    """
    if not expr:
        return []
    parts = re.split(r"(?i)\s+AND\s+", expr.strip())
    out: List[Tuple[str, str]] = []
    for p in parts:
        m = re.match(r"^\s*(\w+)\s*=\s*(.+?)\s*$", p)
        if not m:
            continue
        field, value = m.group(1), m.group(2).strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if field in FILTER_FIELDS:
            out.append((field, value))
    return out


def _urn_entity_type(urn: str) -> Optional[str]:
    parts = urn.split(":")
    return parts[2] if len(parts) >= 3 else None


def _dataset_platform(urn: str) -> Optional[str]:
    if not urn.startswith("urn:li:dataset:("):
        return None
    inner = urn[len("urn:li:dataset:(") : -1]
    if inner.startswith("urn:li:dataPlatform:"):
        rest = inner[len("urn:li:dataPlatform:") :]
        if "," in rest:
            return rest.split(",", 1)[0]
    return None


def _dataset_env(urn: str) -> Optional[str]:
    if urn.endswith(",PROD)"):
        return "PROD"
    if urn.endswith(",DEV)"):
        return "DEV"
    if urn.endswith(",STAGING)"):
        return "STAGING"
    return None


def _has_tag(aspects: Dict[str, Any], tag_urn: str) -> bool:
    tags = (aspects.get("globalTags") or {}).get("tags") or []
    return any(t.get("tag") == tag_urn for t in tags)


def _has_owner(aspects: Dict[str, Any], owner_urn: str) -> bool:
    owners = (aspects.get("ownership") or {}).get("owners") or []
    return any(o.get("owner") == owner_urn for o in owners)


def _has_term(aspects: Dict[str, Any], term_urn: str) -> bool:
    terms = (aspects.get("glossaryTerms") or {}).get("terms") or []
    return any(t.get("urn") == term_urn for t in terms)


def _has_domain(aspects: Dict[str, Any], domain_urn: str) -> bool:
    d = (aspects.get("domains") or {}).get("domains") or []
    return domain_urn in d


def _text_haystack(urn: str, aspects: Dict[str, Any]) -> str:
    parts = [urn]
    for aname in ("datasetProperties", "dataJobInfo", "dashboardInfo", "chartInfo", "mlModelProperties", "queryProperties", "glossaryTermInfo", "tagProperties"):
        a = aspects.get(aname) or {}
        for key in ("name", "description", "customProperties"):
            val = a.get(key)
            if isinstance(val, str):
                parts.append(val)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        parts.append(str(item.get("value", "")))
                        parts.append(str(item.get("key", "")))
    return " ".join(parts).lower()


def _parse_query(raw_query: str) -> Tuple[List[List[str]], List[str]]:
    """Return (ORgroups_of_ANDs, NOT_terms). Very small parser for `/q` prefix.

    Supports:
        - leading "/q" (stripped)
        - `+term`     -> AND (default)
        - `term`      -> AND
        - `NOT term`  -> exclude
        - `term OR term` -> OR grouping
        - `"exact phrase"` -> exact match (case-insensitive)
    `AND` / `NOT` / `OR` are case-insensitive.
    """
    q = raw_query.strip()
    if q.startswith("/q"):
        q = q[2:].strip()
    if not q or q == "*":
        return [[]], []

    raw_tokens = re.findall(r'"[^"]+"|\S+', q)
    tokens: List[str] = []
    for t in raw_tokens:
        if t.startswith('"'):
            tokens.append(t)
            continue
        for part in re.split(r"\+", t):
            if part:
                tokens.append(part)

    or_groups: List[List[str]] = [[]]
    negatives: List[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        upper = tok.upper()
        if upper == "OR":
            or_groups.append([])
        elif upper == "AND":
            pass
        elif upper == "NOT":
            i += 1
            if i < len(tokens):
                negatives.append(tokens[i].strip('"').lower())
        else:
            term = tok.strip('"').lower()
            or_groups[-1].append(term)
        i += 1

    if not any(or_groups):
        return [[]], negatives
    return or_groups, negatives


def _matches_query(haystack: str, or_groups: List[List[str]], negatives: List[str]) -> bool:
    for neg in negatives:
        if neg in haystack:
            return False
    if not any(or_groups):
        return True
    for group in or_groups:
        if not group:
            return True
        if all(term in haystack for term in group):
            return True
    return False


@mcp.tool
def search(
    query: str = "*",
    filter: Optional[str] = None,  # noqa: A002 - matches official tool name
    num_results: int = 10,
    offset: int = 0,
) -> Dict[str, Any]:
    """Search across DataHub entities stored in datahub-lite.

    SUBSET of the full mcp-server-datahub search grammar:
      - Query: `/q <terms>` with `+` (AND), `OR`, `NOT`, and `"phrases"`.
        `*` (or empty) = match all. Wildcards are NOT supported in lite.
      - Filter (SQL-like, AND-joined, `=` only):
          entity_type=dataset, platform=snowflake, env=PROD, tag=urn:li:tag:PII,
          owner=urn:li:corpuser:alice, glossary_term=urn:li:glossaryTerm:...,
          domain=urn:li:domain:marketing, subtype=Table
      - No facets, no ranking by search score — results ordered by URN alpha.

    Returns:
        {query, filter, total, returned, offset, results:[{urn, entity_type, platform, name}]}
    """
    client = get_client()
    filter_pairs = _parse_simple_filter(filter)
    filter_map = {k: v for k, v in filter_pairs}
    or_groups, negatives = _parse_query(query or "*")

    target_type = filter_map.get("entity_type")
    urns_iter = client.iter_urns_by_type(target_type) if target_type else client.all_urns()

    results = []
    for urn in urns_iter:
        etype = _urn_entity_type(urn)
        if target_type and etype != target_type:
            continue
        if "env" in filter_map and _dataset_env(urn) != filter_map["env"]:
            continue
        if "platform" in filter_map and _dataset_platform(urn) != filter_map["platform"]:
            continue

        aspects = client.get_all_aspects(urn)

        if "tag" in filter_map and not _has_tag(aspects, filter_map["tag"]):
            continue
        if "owner" in filter_map and not _has_owner(aspects, filter_map["owner"]):
            continue
        if "glossary_term" in filter_map and not _has_term(aspects, filter_map["glossary_term"]):
            continue
        if "domain" in filter_map and not _has_domain(aspects, filter_map["domain"]):
            continue
        if "subtype" in filter_map or "entity_subtype" in filter_map:
            want = filter_map.get("subtype") or filter_map.get("entity_subtype")
            sub = (aspects.get("subTypes") or {}).get("typeNames") or []
            if want not in sub:
                continue

        haystack = _text_haystack(urn, aspects)
        if not _matches_query(haystack, or_groups, negatives):
            continue

        name = None
        for aname in ("datasetProperties", "dataJobInfo", "dashboardInfo", "chartInfo", "mlModelProperties", "queryProperties"):
            a = aspects.get(aname) or {}
            if isinstance(a.get("name"), str):
                name = a["name"]
                break

        results.append(
            {
                "urn": urn,
                "entity_type": etype,
                "platform": _dataset_platform(urn),
                "env": _dataset_env(urn),
                "name": name,
            }
        )

    total = len(results)
    page = results[offset : offset + num_results]

    return {
        "query": query,
        "filter": filter,
        "total": total,
        "returned": len(page),
        "offset": offset,
        "hasMore": offset + len(page) < total,
        "results": page,
    }
