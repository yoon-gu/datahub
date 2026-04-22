"""`get_lineage` / `get_lineage_paths_between` tools."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..graph import get_graph, bfs_hop, simple_paths_between
from ..lite import get_client
from ..server import mcp


def _summarize_entity(urn: str) -> Dict[str, Any]:
    client = get_client()
    name_aspect = client.get_aspect(urn, "datasetProperties") or client.get_aspect(urn, "dataJobInfo") or {}
    display_name = name_aspect.get("name")
    entity_type = urn.split(":")[2] if urn.startswith("urn:li:") else None
    return {"urn": urn, "name": display_name, "entity_type": entity_type}


def _filter_by_entity_types(urns: List[str], entity_types: Optional[List[str]]) -> List[str]:
    if not entity_types:
        return urns
    types = set(entity_types)
    return [u for u in urns if (u.split(":")[2] if u.startswith("urn:li:") else None) in types]


@mcp.tool
def get_lineage(
    urn: str,
    upstream: bool = True,
    max_hops: int = 1,
    entity_types: Optional[List[str]] = None,
    max_results: int = 30,
    offset: int = 0,
) -> Dict[str, Any]:
    """Get upstream or downstream lineage for a dataset, dashboard, chart, or dataJob.

    Args:
        urn: Source entity URN.
        upstream: True for upstream, False for downstream.
        max_hops: Maximum hop distance (BFS depth). `3` is effectively unlimited for this env.
        entity_types: Optional filter on returned entities by type (e.g. ["dataset"]).
        max_results: Page size.
        offset: Pagination offset.

    Returns:
        dict with source, total, returned, hasMore, and results[] where each
        result has {urn, name, entity_type, degree}.
    """
    graph = get_graph()
    direction = "upstream" if upstream else "downstream"
    hop_map = bfs_hop(graph, urn, max_hops=max_hops, direction=direction)
    sorted_urns = sorted(hop_map.keys(), key=lambda u: (hop_map[u], u))
    filtered = _filter_by_entity_types(sorted_urns, entity_types)

    page = filtered[offset : offset + max_results]
    results = []
    for u in page:
        entry = _summarize_entity(u)
        entry["degree"] = hop_map[u]
        results.append(entry)

    return {
        "source": _summarize_entity(urn),
        "direction": direction,
        "max_hops": max_hops,
        "total": len(filtered),
        "returned": len(results),
        "hasMore": offset + len(results) < len(filtered),
        "offset": offset,
        "results": results,
    }


@mcp.tool
def get_lineage_paths_between(
    source_urn: str,
    target_urn: str,
    source_column: Optional[str] = None,
    target_column: Optional[str] = None,
    direction: Optional[str] = None,
    max_depth: int = 6,
    max_paths: int = 20,
) -> Dict[str, Any]:
    """Get detailed lineage path(s) between two entities or columns.

    Returns simple paths through the lineage graph, including intermediate
    DataJob nodes. Column-level paths are surfaced via the `fineGrainedLineages`
    information attached to each dataset→dataset edge when available.

    Args:
        source_urn: Source dataset/job URN.
        target_urn: Target dataset/job URN.
        source_column: Column in source dataset (requires target_column).
        target_column: Column in target dataset.
        direction: "downstream" | "upstream" | None (auto-discover).
        max_depth: Maximum path length in edges.
        max_paths: Cap number of simple paths returned.
    """
    graph = get_graph()
    paths = simple_paths_between(graph, source_urn, target_urn, cutoff=max_depth, direction=direction)
    limited = paths[:max_paths]

    path_objs = []
    for p in limited:
        edges = []
        for i in range(len(p) - 1):
            u, v = p[i], p[i + 1]
            data = graph.get_edge_data(u, v) or {}
            edge = {"from": u, "to": v, "edge_type": data.get("edge_type")}
            if data.get("finegrained"):
                edge["finegrained"] = data["finegrained"]
            edges.append(edge)
        path_objs.append({"nodes": p, "edges": edges, "length": len(edges)})

    result: Dict[str, Any] = {
        "source": _summarize_entity(source_urn),
        "target": _summarize_entity(target_urn),
        "pathCount": len(path_objs),
        "truncated": len(paths) > len(limited),
        "paths": path_objs,
    }

    if source_column and target_column:
        matching = []
        for p in path_objs:
            for e in p["edges"]:
                for fg in e.get("finegrained", []) or []:
                    if source_column in (fg.get("upstream") or "") and target_column in (fg.get("downstream") or ""):
                        matching.append({"path": p, "column_edge": fg})
                        break
        result["columnMatches"] = matching
        result["columnMatchCount"] = len(matching)

    return result
