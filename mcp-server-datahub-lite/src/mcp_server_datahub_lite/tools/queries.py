"""`get_dataset_queries` tool — dataset 또는 column 을 참조하는 SQL 쿼리 조회."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..lite import get_client
from ..server import mcp


@mcp.tool
def get_dataset_queries(
    urn: str,
    column: Optional[str] = None,
    source: Optional[str] = None,
    start: int = 0,
    count: int = 10,
) -> Dict[str, Any]:
    """Get SQL queries associated with a dataset or column.

    Args:
        urn: Target dataset URN.
        column: Optional field path to filter queries that explicitly reference this column
            (via QuerySubjects with schemaField entity).
        source: "MANUAL" | "SYSTEM" | None.
        start: Pagination offset.
        count: Page size.

    Returns:
        {total, start, count, queries: [{urn, statement, source, name, subjects}]}
    """
    client = get_client()
    matched: List[Dict[str, Any]] = []
    for qurn, subjects_aspect in client.all_aspects_by_name("querySubjects"):
        subjects = (subjects_aspect.get("subjects") or [])
        subject_urns = {s.get("entity") for s in subjects if s.get("entity")}
        if urn not in subject_urns:
            if column:
                wanted_field = f"urn:li:schemaField:({urn},{column})"
                if wanted_field not in subject_urns:
                    continue
            else:
                continue

        props = client.get_aspect(qurn, "queryProperties") or {}
        q_source = props.get("source")
        if source and q_source != source:
            continue

        statement = (props.get("statement") or {})
        matched.append(
            {
                "urn": qurn,
                "name": props.get("name"),
                "description": props.get("description"),
                "source": q_source,
                "statement": {
                    "value": statement.get("value"),
                    "language": statement.get("language"),
                },
                "subjects": sorted(subject_urns),
            }
        )

    matched.sort(key=lambda q: q["urn"])
    total = len(matched)
    page = matched[start : start + count]

    return {
        "total": total,
        "start": start,
        "count": len(page),
        "queries": page,
    }
