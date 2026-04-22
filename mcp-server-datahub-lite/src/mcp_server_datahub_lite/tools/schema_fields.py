"""`list_schema_fields` tool — dataset schema field 조회/검색/페이지네이션."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ..lite import get_client
from ..server import mcp


def _extract_fields(schema_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for f in schema_metadata.get("fields", []) or []:
        out.append(
            {
                "fieldPath": f.get("fieldPath"),
                "nativeDataType": f.get("nativeDataType"),
                "type": (f.get("type") or {}).get("type"),
                "description": f.get("description"),
                "nullable": f.get("nullable"),
                "isPartitioningKey": f.get("isPartitioningKey"),
                "tags": [t.get("tag") for t in ((f.get("globalTags") or {}).get("tags") or [])],
                "glossaryTerms": [
                    t.get("urn") for t in ((f.get("glossaryTerms") or {}).get("terms") or [])
                ],
            }
        )
    return out


def _match_keywords(field: Dict[str, Any], keywords: List[str]) -> int:
    haystack_parts = [
        field.get("fieldPath") or "",
        field.get("description") or "",
        field.get("nativeDataType") or "",
        " ".join(field.get("tags") or []),
        " ".join(field.get("glossaryTerms") or []),
    ]
    haystack = " ".join(haystack_parts).lower()
    return sum(1 for kw in keywords if kw.lower() in haystack)


@mcp.tool
def list_schema_fields(
    urn: str,
    keywords: Optional[Union[str, List[str]]] = None,
    limit: int = 100,
    offset: int = 0,
) -> Dict[str, Any]:
    """List schema fields for a dataset with optional keyword filtering and pagination.

    Args:
        urn: Dataset URN.
        keywords: Optional keywords to filter. Single string is treated as ONE exact keyword
            (not split on whitespace). List of strings does OR matching. Matches against
            fieldPath, description, nativeDataType, tags, glossary terms.
        limit: Maximum fields to return (default 100).
        offset: Skip for pagination (default 0).

    Returns:
        dict with urn, fields, totalFields, returned, remainingCount, matchingCount, offset.
    """
    client = get_client()
    schema = client.get_aspect(urn, "schemaMetadata") or {}
    all_fields = _extract_fields(schema)
    total_fields = len(all_fields)

    matching_count: Optional[int] = None
    if keywords:
        kw_list = [keywords] if isinstance(keywords, str) else list(keywords)
        scored = [(f, _match_keywords(f, kw_list)) for f in all_fields]
        matched = [f for f, score in scored if score > 0]
        matched.sort(key=lambda f: -_match_keywords(f, kw_list))
        matching_count = len(matched)
        candidates = matched
    else:
        candidates = all_fields

    sliced = candidates[offset : offset + limit]
    remaining = max(0, len(candidates) - (offset + len(sliced)))

    return {
        "urn": urn,
        "fields": sliced,
        "totalFields": total_fields,
        "returned": len(sliced),
        "remainingCount": remaining,
        "matchingCount": matching_count,
        "offset": offset,
    }
