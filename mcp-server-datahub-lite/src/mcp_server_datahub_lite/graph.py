"""Lineage graph builder over lite's DuckDB.

엣지 원천:
    - `upstreamLineage.upstreams[].dataset`          : Dataset → Dataset (DownstreamOf)
    - `upstreamLineage.fineGrainedLineages[]`        : 컬럼 레벨 (dataset 레벨 엣지로도 투영)
    - `dataJobInputOutput.inputDatasets|edges`       : Dataset → DataJob (Consumes)
    - `dataJobInputOutput.outputDatasets|edges`      : DataJob → Dataset (Produces)

LRU 캐시 후 hot path 에 in-memory NetworkX DiGraph. 메타데이터 변경 시 `reset_graph()`.
"""

from __future__ import annotations

import threading
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import networkx as nx

from .lite import get_client


EDGE_TYPE_DOWNSTREAM_OF = "DownstreamOf"
EDGE_TYPE_CONSUMES = "Consumes"
EDGE_TYPE_PRODUCES = "Produces"


def _parse_upstream_aspect(raw: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
    upstreams = []
    for u in raw.get("upstreams") or []:
        d = u.get("dataset")
        if d:
            upstreams.append(d)
    finegrained = raw.get("fineGrainedLineages") or []
    return upstreams, finegrained


def _parse_job_io(raw: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    inputs = list(raw.get("inputDatasets") or [])
    for e in raw.get("inputDatasetEdges") or []:
        dst = e.get("destinationUrn")
        if dst:
            inputs.append(dst)
    outputs = list(raw.get("outputDatasets") or [])
    for e in raw.get("outputDatasetEdges") or []:
        dst = e.get("destinationUrn")
        if dst:
            outputs.append(dst)
    return inputs, outputs


def _build() -> nx.DiGraph:
    """Build an upstream-direction DiGraph.

    Edge `(u, v)` in this graph means "`u` is upstream of `v`" i.e.
    data flows u → v. downstream traversal follows edges forward,
    upstream traversal follows them backward.

    Edge attributes:
        edge_type: DownstreamOf | Consumes | Produces
        finegrained: optional list of column-level edges (dataset-dataset only)
    """
    client = get_client()
    g = nx.DiGraph()

    for urn, data in client.all_aspects_by_name("upstreamLineage"):
        ups, finegrained = _parse_upstream_aspect(data)
        for up in ups:
            g.add_edge(up, urn, edge_type=EDGE_TYPE_DOWNSTREAM_OF)
        if finegrained:
            for fg in finegrained:
                for src_f in fg.get("upstreams") or []:
                    src_ds = _dataset_of_schemafield(src_f)
                    for dst_f in fg.get("downstreams") or []:
                        dst_ds = _dataset_of_schemafield(dst_f)
                        if src_ds and dst_ds and src_ds != dst_ds:
                            if not g.has_edge(src_ds, dst_ds):
                                g.add_edge(src_ds, dst_ds, edge_type=EDGE_TYPE_DOWNSTREAM_OF)
                            g[src_ds][dst_ds].setdefault("finegrained", []).append(
                                {"upstream": src_f, "downstream": dst_f}
                            )

    for urn, data in client.all_aspects_by_name("dataJobInputOutput"):
        inputs, outputs = _parse_job_io(data)
        for inp in inputs:
            g.add_edge(inp, urn, edge_type=EDGE_TYPE_CONSUMES)
        for out in outputs:
            g.add_edge(urn, out, edge_type=EDGE_TYPE_PRODUCES)

    return g


def _dataset_of_schemafield(field_urn: Optional[str]) -> Optional[str]:
    if not field_urn:
        return None
    if field_urn.startswith("urn:li:schemaField:("):
        inner = field_urn[len("urn:li:schemaField:(") : -1]
        if inner.startswith("urn:li:dataset:"):
            depth = 0
            for i, ch in enumerate(inner):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                elif ch == "," and depth == 0:
                    return inner[:i]
    if field_urn.startswith("urn:li:dataset:"):
        return field_urn
    return None


_graph_lock = threading.Lock()


@lru_cache(maxsize=1)
def _cached_graph() -> nx.DiGraph:
    with _graph_lock:
        return _build()


def get_graph() -> nx.DiGraph:
    return _cached_graph()


def reset_graph() -> None:
    _cached_graph.cache_clear()


def bfs_hop(
    graph: nx.DiGraph,
    start: str,
    max_hops: int,
    direction: str = "downstream",
) -> Dict[str, int]:
    """Return {urn: min_hop} for all nodes reachable within max_hops from start.

    direction: "downstream" follows edges u→v; "upstream" follows v→u.
    """
    if start not in graph:
        return {}

    out: Dict[str, int] = {}
    visited: Set[str] = {start}
    frontier: List[str] = [start]
    for hop in range(1, max_hops + 1):
        nxt: List[str] = []
        for node in frontier:
            if direction == "downstream":
                neighbors: Iterable[str] = graph.successors(node)
            else:
                neighbors = graph.predecessors(node)
            for n in neighbors:
                if n not in visited:
                    visited.add(n)
                    out[n] = hop
                    nxt.append(n)
        frontier = nxt
        if not frontier:
            break
    return out


def simple_paths_between(
    graph: nx.DiGraph,
    source: str,
    target: str,
    cutoff: int = 6,
    direction: Optional[str] = None,
) -> List[List[str]]:
    """Return list of simple node paths (inclusive of source & target).

    direction:
        - "downstream": paths from source → target (edges forward)
        - "upstream":   paths from target → source (edges forward, but roles flipped)
        - None        : try downstream first, then upstream
    """
    if source not in graph or target not in graph:
        return []

    def _downstream() -> List[List[str]]:
        try:
            return list(nx.all_simple_paths(graph, source, target, cutoff=cutoff))
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return []

    def _upstream() -> List[List[str]]:
        try:
            raw = list(nx.all_simple_paths(graph, target, source, cutoff=cutoff))
            return [list(reversed(p)) for p in raw]
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return []

    if direction == "downstream":
        return _downstream()
    if direction == "upstream":
        return _upstream()
    paths = _downstream()
    if paths:
        return paths
    return _upstream()
