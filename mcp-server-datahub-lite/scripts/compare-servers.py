"""Side-by-side diff report: full mcp-server-datahub vs lite.

각 테스트 케이스마다 양쪽 서버에서 key 응답 필드를 뽑아 좌/우 컬럼으로 출력.
MATCH / DIFF 판정까지 표시해 눈으로 훑기 좋게 구성.

사용:
    DATAHUB_GMS_TOKEN=<PAT> \\
        .venv/bin/python mcp-server-datahub-lite/scripts/compare-servers.py

옵션:
    --tools search,get_lineage   특정 tool 만
    --no-color                   ANSI 끄기
    --col-width 70               컬럼 폭 (기본 60)
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests import test_cases  # noqa: E402
from tests.mcp_client import McpStdioClient, full_client_args, lite_client_args  # noqa: E402


# ----------------------------------------------------------------------
# Terminal rendering helpers
# ----------------------------------------------------------------------


class Style:
    def __init__(self, use_color: bool):
        self.use_color = use_color and sys.stdout.isatty()

    def _c(self, code: str, text: str) -> str:
        if not self.use_color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def bold(self, t: str) -> str:
        return self._c("1", t)

    def dim(self, t: str) -> str:
        return self._c("2", t)

    def green(self, t: str) -> str:
        return self._c("32", t)

    def red(self, t: str) -> str:
        return self._c("31", t)

    def yellow(self, t: str) -> str:
        return self._c("33", t)

    def cyan(self, t: str) -> str:
        return self._c("36", t)


def _pad(s: str, width: int) -> str:
    if len(s) >= width:
        return s[: width - 1] + "…"
    return s + " " * (width - len(s))


def render_side_by_side(
    header: str,
    case_label: str,
    left_lines: Sequence[str],
    right_lines: Sequence[str],
    verdict: str,
    style: Style,
    col_width: int = 60,
) -> None:
    full_width = col_width * 2 + 3
    print()
    print(style.bold(header) + "   " + style.dim(case_label))
    print("─" * full_width)
    print(f"{_pad(style.cyan('FULL'), col_width + len(style.cyan('')) - 0)}   {style.cyan('LITE')}")
    print("─" * full_width)
    rows = max(len(left_lines), len(right_lines))
    pad_left = list(left_lines) + [""] * (rows - len(left_lines))
    pad_right = list(right_lines) + [""] * (rows - len(right_lines))
    left_set = set(l.strip() for l in pad_left if l.strip())
    right_set = set(r.strip() for r in pad_right if r.strip())
    for l, r in zip(pad_left, pad_right):
        l_marker = "  " if l.strip() in right_set or not l.strip() else style.red(" *")
        r_marker = "  " if r.strip() in left_set or not r.strip() else style.red(" *")
        print(f"{_pad(l, col_width)}{l_marker} {_pad(r, col_width)}{r_marker}")
    print("─" * full_width)
    print(verdict)


def verdict_for(match: bool, note: str = "", style: Style = Style(True)) -> str:
    if match:
        return style.green("  ✓ MATCH") + (f"   {style.dim(note)}" if note else "")
    return style.red("  ✗ DIFF") + (f"   {style.yellow(note)}" if note else "")


# ----------------------------------------------------------------------
# Response shape normalization (copied/trimmed from test_parity.py)
# ----------------------------------------------------------------------


def _result_payload(res: Any) -> Any:
    if isinstance(res, dict) and set(res.keys()) == {"result"}:
        return res["result"]
    return res


def _lineage_container(resp: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(resp, dict):
        return None
    for k in ("downstreams", "upstreams"):
        inner = resp.get(k)
        if isinstance(inner, dict):
            return inner
    return resp if isinstance(resp, dict) else None


def _short(urn: str) -> str:
    if "," in urn:
        parts = urn.rstrip(")").split(",")
        if len(parts) >= 2:
            return parts[-2]
    return urn.split(":")[-1] if ":" in urn else urn


# ----------------------------------------------------------------------
# Per-tool extractors + case runners
# ----------------------------------------------------------------------


def _find_entity(data: Any, urn: str) -> Optional[Dict[str, Any]]:
    """Given full/lite get_entities response, locate the entry matching urn.

    full (graphql projection):  response is the entity itself at top level
    lite (our shape):           {"<urn>": {aspects: {...}, ...}}
    both may also be a list.
    """
    if isinstance(data, dict):
        if data.get("urn") == urn:
            return data
        if urn in data and isinstance(data[urn], dict):
            return data[urn]
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("urn") == urn:
                return item
    return None


def extract_entity_summary(resp: Any, urn: str) -> Dict[str, Any]:
    """Pull semantic attributes that should match between full/lite."""
    data = _result_payload(resp)
    entry = _find_entity(data, urn) or {}
    aspects = entry.get("aspects") if isinstance(entry.get("aspects"), dict) else None

    def _nested_urn(x: Any) -> Optional[str]:
        if isinstance(x, str) and x.startswith("urn:li:"):
            return x
        if isinstance(x, dict):
            u = x.get("urn")
            if isinstance(u, str):
                return u
            for k in ("owner", "tag", "term", "entity", "domain"):
                nested = _nested_urn(x.get(k))
                if nested:
                    return nested
        return None

    def _extract_urn_list(*candidates: Any) -> List[str]:
        for c in candidates:
            if not c:
                continue
            if isinstance(c, list):
                out: List[str] = []
                for x in c:
                    u = _nested_urn(x)
                    if u:
                        out.append(u)
                if out:
                    return sorted(set(out))
        return []

    owners = _extract_urn_list(
        (entry.get("ownership") or {}).get("owners"),
        ((aspects or {}).get("ownership") or {}).get("owners"),
    )
    tags = _extract_urn_list(
        (entry.get("tags") or {}).get("tags"),
        ((aspects or {}).get("globalTags") or {}).get("tags"),
    )
    terms = _extract_urn_list(
        (entry.get("glossaryTerms") or {}).get("terms"),
        ((aspects or {}).get("glossaryTerms") or {}).get("terms"),
    )

    # domains
    full_domain = entry.get("domain") or {}
    domain_urn = None
    if isinstance(full_domain, dict):
        d = full_domain.get("domain")
        if isinstance(d, dict):
            domain_urn = d.get("urn")
        elif isinstance(d, str):
            domain_urn = d
    if not domain_urn and aspects:
        doms = (aspects.get("domains") or {}).get("domains") or []
        if doms:
            domain_urn = doms[0]

    # schema field count
    schema_fields = 0
    sm_full = entry.get("schemaMetadata") or {}
    if isinstance(sm_full.get("fields"), list):
        schema_fields = len(sm_full["fields"])
    elif aspects:
        sm = aspects.get("schemaMetadata") or {}
        if isinstance(sm.get("fields"), list):
            schema_fields = len(sm["fields"])

    has_upstream = False
    if aspects and aspects.get("upstreamLineage"):
        has_upstream = bool((aspects["upstreamLineage"] or {}).get("upstreams"))
    # full exposes upstreamLineage too via GraphQL projection
    up_full = entry.get("upstream") or entry.get("upstreamLineage")
    if up_full and not has_upstream:
        if isinstance(up_full, dict):
            has_upstream = bool(up_full.get("total") or up_full.get("upstreams"))

    return {
        "owners": owners,
        "tags": tags,
        "terms": terms,
        "domain": domain_urn,
        "schemaFields": schema_fields,
        "hasUpstream": has_upstream,
    }


def extract_fieldpaths(resp: Any) -> Set[str]:
    data = _result_payload(resp)
    fields = []
    if isinstance(data, dict):
        fields = data.get("fields") or []
    elif isinstance(data, list):
        fields = data
    return {f.get("fieldPath") for f in fields if isinstance(f, dict) and f.get("fieldPath")}


def extract_lineage_datasets(resp: Any) -> Set[str]:
    container = _lineage_container(resp)
    if container is None:
        return set()
    results = container.get("results") or container.get("searchResults") or []
    out: Set[str] = set()
    for r in results:
        if not isinstance(r, dict):
            continue
        entity = r.get("entity") or r
        urn_val = entity.get("urn") if isinstance(entity, dict) else None
        if isinstance(urn_val, str) and urn_val.startswith("urn:li:dataset:"):
            degree = r.get("degree")
            if degree is None or degree <= 1:
                out.add(urn_val)
    return out


def extract_lineage_all(resp: Any) -> Tuple[int, int, int]:
    """Return (n_datasets, n_jobs, total)."""
    container = _lineage_container(resp)
    if container is None:
        return 0, 0, 0
    results = container.get("results") or container.get("searchResults") or []
    n_ds = n_job = 0
    for r in results:
        if not isinstance(r, dict):
            continue
        entity = r.get("entity") or r
        urn_val = entity.get("urn") if isinstance(entity, dict) else None
        if not isinstance(urn_val, str):
            continue
        if urn_val.startswith("urn:li:dataset:"):
            n_ds += 1
        elif urn_val.startswith("urn:li:dataJob:"):
            n_job += 1
    return n_ds, n_job, len(results)


def extract_query_urns(resp: Any) -> Set[str]:
    data = _result_payload(resp)
    if not isinstance(data, dict):
        return set()
    queries = data.get("queries") or []
    return {q.get("urn") for q in queries if isinstance(q, dict) and q.get("urn")}


def extract_search_urns(resp: Any) -> Set[str]:
    data = _result_payload(resp)
    if not isinstance(data, dict):
        return set()
    results = data.get("results") or data.get("searchResults") or []
    out: Set[str] = set()
    for r in results:
        if not isinstance(r, dict):
            continue
        if r.get("urn"):
            out.add(r["urn"])
        ent = r.get("entity")
        if isinstance(ent, dict) and ent.get("urn"):
            out.add(ent["urn"])
    return out


def extract_path_count(resp: Any) -> int:
    if not isinstance(resp, dict):
        return 0
    if "pathCount" in resp:
        return resp["pathCount"] or 0
    if isinstance(resp.get("paths"), list):
        return len(resp["paths"])
    return 0


# ----------------------------------------------------------------------
# Cases
# ----------------------------------------------------------------------


def _summary_lines(s: Dict[str, Any]) -> List[str]:
    lines = [
        f"schemaFields: {s['schemaFields']}",
        f"hasUpstream:  {s['hasUpstream']}",
        f"domain:       {s['domain'] or '-'}",
        f"owners ({len(s['owners'])}):",
    ]
    lines += [f"  {o.split(':')[-1]}" for o in s["owners"]]
    lines.append(f"tags ({len(s['tags'])}):")
    lines += [f"  {t.split(':')[-1]}" for t in s["tags"]]
    lines.append(f"terms ({len(s['terms'])}):")
    lines += [f"  {t.split(':')[-1]}" for t in s["terms"]]
    return lines


def run_get_entities(full, lite, style, col_width) -> int:
    fails = 0
    for urn in test_cases.DATASETS:
        f = full.call("get_entities", {"urns": urn})
        l = lite.call("get_entities", {"urns": urn})
        fs = extract_entity_summary(f, urn)
        ls = extract_entity_summary(l, urn)
        match = (
            fs["owners"] == ls["owners"]
            and fs["tags"] == ls["tags"]
            and fs["terms"] == ls["terms"]
            and fs["domain"] == ls["domain"]
            and fs["schemaFields"] == ls["schemaFields"]
        )
        mismatches = []
        for k in ("owners", "tags", "terms", "domain", "schemaFields"):
            if fs[k] != ls[k]:
                mismatches.append(k)
        note = ",".join(mismatches) if mismatches else "all attrs equal"
        render_side_by_side(
            "[get_entities]", f"urn={_short(urn)}",
            _summary_lines(fs),
            _summary_lines(ls),
            verdict_for(match, note, style), style, col_width,
        )
        if not match:
            fails += 1
    return fails


def run_list_schema_fields(full, lite, style, col_width) -> int:
    fails = 0
    for urn in test_cases.DATASETS_WITH_SCHEMA:
        f = full.call("list_schema_fields", {"urn": urn, "limit": 500})
        l = lite.call("list_schema_fields", {"urn": urn, "limit": 500})
        ff = sorted(extract_fieldpaths(f))
        lf = sorted(extract_fieldpaths(l))
        match = ff == lf  # 양쪽 모두 빈 집합이어도 의미상 동치
        note = f"full={len(ff)} lite={len(lf)}" + (" (both empty — dataset has no schemaMetadata)" if not ff and not lf else "")
        render_side_by_side(
            "[list_schema_fields]", f"urn={_short(urn)}",
            [f"fieldPath ({len(ff)})"] + [f"  {p}" for p in ff],
            [f"fieldPath ({len(lf)})"] + [f"  {p}" for p in lf],
            verdict_for(match, note, style), style, col_width,
        )
        if not match:
            fails += 1
    return fails


def run_get_lineage(full, lite, style, col_width) -> int:
    fails = 0
    for urn in test_cases.DATASETS_WITH_LINEAGE + test_cases.DATASETS[:4]:
        for upstream in (True, False):
            f = full.call("get_lineage", {"urn": urn, "upstream": upstream, "max_hops": 1, "max_results": 500})
            l = lite.call("get_lineage", {"urn": urn, "upstream": upstream, "max_hops": 1, "max_results": 500})
            fs = sorted(extract_lineage_datasets(f))
            ls = sorted(extract_lineage_datasets(l))
            match = fs == ls
            fd, fj, ft = extract_lineage_all(f)
            ld, lj, lt = extract_lineage_all(l)
            note = f"full:ds={fd} job={fj} total={ft} | lite:ds={ld} job={lj} total={lt}"
            direction = "upstream" if upstream else "downstream"
            render_side_by_side(
                f"[get_lineage 1-hop {direction}]", f"urn={_short(urn)}",
                [f"datasets ({len(fs)})"] + [f"  {_short(u)}" for u in fs],
                [f"datasets ({len(ls)})"] + [f"  {_short(u)}" for u in ls],
                verdict_for(match, note, style), style, col_width,
            )
            if not match:
                fails += 1
    return fails


def run_get_lineage_paths_between(full, lite, style, col_width) -> int:
    fails = 0
    for src, tgt in test_cases.LINEAGE_PAIRS:
        f = full.call("get_lineage_paths_between", {"source_urn": src, "target_urn": tgt})
        l = lite.call("get_lineage_paths_between", {"source_urn": src, "target_urn": tgt})
        fp = extract_path_count(f)
        lp = extract_path_count(l)
        match = fp > 0 and lp > 0
        note = f"full_paths={fp} lite_paths={lp}"
        render_side_by_side(
            "[get_lineage_paths_between]", f"{_short(src)} → {_short(tgt)}",
            [f"pathCount: {fp}"],
            [f"pathCount: {lp}"],
            verdict_for(match, note, style), style, col_width,
        )
        if not match:
            fails += 1
    return fails


def run_get_dataset_queries(full, lite, style, col_width) -> int:
    fails = 0
    for urn in test_cases.DATASETS_WITH_QUERIES:
        f = full.call("get_dataset_queries", {"urn": urn, "count": 100})
        l = lite.call("get_dataset_queries", {"urn": urn, "count": 100})
        fq = sorted(extract_query_urns(f))
        lq = sorted(extract_query_urns(l))
        match = fq == lq and len(fq) > 0
        note = f"full={len(fq)} lite={len(lq)}"
        render_side_by_side(
            "[get_dataset_queries]", f"urn={_short(urn)}",
            [f"queries ({len(fq)})"] + [f"  {q.split(':')[-1]}" for q in fq],
            [f"queries ({len(lq)})"] + [f"  {q.split(':')[-1]}" for q in lq],
            verdict_for(match, note, style), style, col_width,
        )
        if not match:
            fails += 1
    return fails


def _search_total(resp: Any) -> int:
    data = _result_payload(resp)
    if isinstance(data, dict) and isinstance(data.get("total"), int):
        return data["total"]
    return -1


def _search_paginate(client, args: Dict[str, Any], page_size: int = 50, limit: int = 500) -> Tuple[int, Set[str]]:
    offset = 0
    urns: Set[str] = set()
    total = 0
    while offset < limit:
        call_args = dict(args, num_results=page_size, offset=offset)
        resp = client.call("search", call_args)
        total = _search_total(resp)
        page = extract_search_urns(resp)
        if not page:
            break
        urns |= page
        if len(urns) >= (total if total >= 0 else limit):
            break
        offset += page_size
    return total, urns


def run_search(full, lite, style, col_width) -> int:
    fails = 0
    for label, args in test_cases.SEARCH_CASES:
        ft, fu = _search_paginate(full, args)
        lt, lu = _search_paginate(lite, args)
        match = ft == lt and fu == lu
        mismatch_note = []
        if ft != lt:
            mismatch_note.append(f"total diff ({ft} vs {lt})")
        if fu != lu:
            only_full = len(fu - lu)
            only_lite = len(lu - fu)
            mismatch_note.append(f"URN diff: only_full={only_full}, only_lite={only_lite}")
        note = "; ".join(mismatch_note) or f"all {ft} URNs equal"
        render_side_by_side(
            "[search]", label,
            [f"total = {ft}", f"URNs ({len(fu)}):"] + [f"  {u.split(':', 3)[-1][:56]}" for u in sorted(fu)[:30]],
            [f"total = {lt}", f"URNs ({len(lu)}):"] + [f"  {u.split(':', 3)[-1][:56]}" for u in sorted(lu)[:30]],
            verdict_for(match, note, style), style, col_width,
        )
        if not match:
            fails += 1
    return fails


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


RUNNERS: Dict[str, Callable] = {
    "get_entities": run_get_entities,
    "list_schema_fields": run_list_schema_fields,
    "get_lineage": run_get_lineage,
    "get_lineage_paths_between": run_get_lineage_paths_between,
    "get_dataset_queries": run_get_dataset_queries,
    "search": run_search,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tools", default=",".join(RUNNERS.keys()),
                        help="Comma-separated list. Default: all")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--col-width", type=int, default=60)
    args = parser.parse_args()

    style = Style(not args.no_color)

    print(style.bold("[*] Starting both MCP servers..."))
    full_args, full_env = full_client_args()
    lite_args, lite_env = lite_client_args()

    with McpStdioClient(full_args, env=full_env, name="full") as full, \
         McpStdioClient(lite_args, env=lite_env, name="lite") as lite:
        print(style.dim(f"    full tools: {len(full.list_tools())}, lite tools: {len(lite.list_tools())}"))

        total_fails = 0
        totals: List[Tuple[str, int]] = []
        for name in args.tools.split(","):
            name = name.strip()
            if name not in RUNNERS:
                print(style.red(f"unknown tool: {name}"))
                continue
            print(style.bold(f"\n╔══ {name} " + "═" * (60 - len(name))))
            n = RUNNERS[name](full, lite, style, args.col_width)
            total_fails += n
            totals.append((name, n))

    print()
    print(style.bold("══ SUMMARY ═══════════════════════════════════════════════════"))
    for name, n in totals:
        status = style.green("OK") if n == 0 else style.red(f"{n} DIFF")
        print(f"  {status:<30s}  {name}")
    print()
    if total_fails == 0:
        print(style.green(f"ALL MATCH ({sum(1 for _ in totals)} tools)"))
        return 0
    print(style.red(f"TOTAL DIFFS: {total_fails}"))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
