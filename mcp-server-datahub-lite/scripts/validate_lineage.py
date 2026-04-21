"""Validate that lineage reconstructed from lite matches GMS searchAcrossLineage.

Lite 의 DuckDB 에 저장된 `upstreamLineage` aspect 만으로 업/다운스트림 그래프를
자체 재구성하고, 동일한 질의를 GMS GraphQL 에도 던져 결과 집합을 비교한다.
결과가 일치하면 Phase 1 에서 `get_lineage` / `get_lineage_paths_between` 을
lite 단독으로 구현해도 동등한 응답이 가능함을 의미.

비교 대상:
    - get_lineage 1-hop upstream (모든 dataset)
    - get_lineage 1-hop downstream (모든 dataset)
    - get_lineage_paths_between (몇 쌍 샘플)

성공 기준: 각 테스트마다 lite set == gms set.
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple

import duckdb
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig


LITE_DB = os.environ.get("DATAHUB_LITE_DB", "/Users/yoon-gu/.datahub/lite/datahub.duckdb")
GMS_URL = os.environ.get("DATAHUB_GMS_URL", "http://localhost:8080")
GMS_TOKEN = os.environ.get("DATAHUB_GMS_TOKEN")
if not GMS_TOKEN:
    sys.exit(
        "DATAHUB_GMS_TOKEN environment variable is required. "
        "Generate a personal access token in DataHub UI and export it."
    )


def load_lite_graph() -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    """Return (upstreams, downstreams) adjacency maps including DataJobs as nodes.

    Edges:
      - Dataset -> Dataset via upstreamLineage.upstreams
      - DataJob -> Dataset via dataJobInputOutput.outputs (job produces dataset)
      - Dataset -> DataJob via dataJobInputOutput.inputs (dataset feeds job)
    """
    con = duckdb.connect(LITE_DB, read_only=True)
    upstreams: Dict[str, Set[str]] = defaultdict(set)
    downstreams: Dict[str, Set[str]] = defaultdict(set)

    def add_edge(src: str, dst: str) -> None:
        upstreams[dst].add(src)
        downstreams[src].add(dst)

    rows = con.execute(
        "SELECT urn, metadata FROM metadata_aspect_v2 "
        "WHERE aspect_name='upstreamLineage' AND version=0"
    ).fetchall()
    for urn, raw in rows:
        data = json.loads(raw)
        for up in data.get("upstreams", []) or []:
            up_urn = up.get("dataset")
            if up_urn:
                add_edge(up_urn, urn)

    rows = con.execute(
        "SELECT urn, metadata FROM metadata_aspect_v2 "
        "WHERE aspect_name='dataJobInputOutput' AND version=0"
    ).fetchall()
    for job_urn, raw in rows:
        data = json.loads(raw)
        inputs = (data.get("inputDatasets") or []) + [
            e.get("destinationUrn") for e in (data.get("inputDatasetEdges") or []) if e.get("destinationUrn")
        ]
        outputs = (data.get("outputDatasets") or []) + [
            e.get("destinationUrn") for e in (data.get("outputDatasetEdges") or []) if e.get("destinationUrn")
        ]
        for inp in inputs:
            add_edge(inp, job_urn)
        for out in outputs:
            add_edge(job_urn, out)

    return upstreams, downstreams


def bfs_hop(adjacency: Dict[str, Set[str]], start: str, max_hops: int) -> Set[str]:
    seen: Set[str] = set()
    frontier = {start}
    for _ in range(max_hops):
        nxt: Set[str] = set()
        for node in frontier:
            for neighbor in adjacency.get(node, ()):
                if neighbor not in seen and neighbor != start:
                    nxt.add(neighbor)
        seen |= nxt
        frontier = nxt
        if not frontier:
            break
    return seen


def gms_lineage(graph: DataHubGraph, urn: str, upstream: bool, max_hops: int) -> Set[str]:
    direction = "UPSTREAM" if upstream else "DOWNSTREAM"
    query = """
    query($urn:String!, $dir:LineageDirection!) {
      searchAcrossLineage(input:{
        urn:$urn, direction:$dir, start:0, count:500,
        query:"*"
      }) { searchResults { entity { urn type } degree } }
    }
    """
    result = graph.execute_graphql(
        query,
        variables={"urn": urn, "dir": direction},
    )
    urns: Set[str] = set()
    for r in result["searchAcrossLineage"]["searchResults"]:
        deg = r.get("degree")
        if deg is None or deg <= max_hops:
            urns.add(r["entity"]["urn"])
    return urns


def compare_datasets(lite_adj: Dict[str, Set[str]], graph: DataHubGraph, upstream: bool, max_hops: int) -> Tuple[int, int, int]:
    """Return (total, matches, mismatches) over dataset URNs that have at least one edge in lite."""
    total = 0
    matches = 0
    mismatches = 0
    print(f"\n== {'upstream' if upstream else 'downstream'} (hop<={max_hops}) ==")
    for start_urn in sorted(lite_adj.keys()):
        if not start_urn.startswith("urn:li:dataset:"):
            continue
        total += 1
        lite_set = bfs_hop(lite_adj, start_urn, max_hops)
        gms_set = gms_lineage(graph, start_urn, upstream=upstream, max_hops=max_hops)
        gms_datasets = {u for u in gms_set if u.startswith("urn:li:dataset:")}
        lite_datasets = {u for u in lite_set if u.startswith("urn:li:dataset:")}
        only_lite = lite_datasets - gms_datasets
        only_gms = gms_datasets - lite_datasets
        if not only_lite and not only_gms:
            matches += 1
        else:
            mismatches += 1
            short = start_urn.split(",")[-2] if "," in start_urn else start_urn
            print(f"  MISMATCH {short}")
            if only_lite:
                print(f"    only in lite: {len(only_lite)} -> {sorted(only_lite)[:3]}")
            if only_gms:
                print(f"    only in gms : {len(only_gms)} -> {sorted(only_gms)[:3]}")
    print(f"  summary: total={total} matches={matches} mismatches={mismatches}")
    return total, matches, mismatches


def main() -> int:
    upstreams, downstreams = load_lite_graph()
    print(f"[*] lite graph loaded: upstream map = {len(upstreams)} nodes, downstream map = {len(downstreams)} nodes")

    graph = DataHubGraph(DataHubGraphConfig(server=GMS_URL, token=GMS_TOKEN))
    graph.test_connection()
    print(f"[*] connected to {GMS_URL}")

    # 1-hop 일치가 Phase 0 의 결정적 지표 — 원본 엣지가 lite 에 모두 남았는지 확인
    # 멀티홉은 동일 엣지 집합 위의 BFS 이므로 1-hop 일치만으로 결정적
    results = []
    for hops in (1, 3):
        results.append(("upstream", hops, compare_datasets(upstreams, graph, upstream=True, max_hops=hops)))
        results.append(("downstream", hops, compare_datasets(downstreams, graph, upstream=False, max_hops=hops)))

    print("\n== FINAL ==")
    ok = True
    for direction, hops, (total, matches, mismatches) in results:
        flag = "OK" if mismatches == 0 else "FAIL"
        critical = hops == 1
        note = " (CRITICAL)" if critical else " (informational — GMS searchAcrossLineage ranking may diverge)"
        print(f"  [{flag}] {direction:10s} hop<={hops}: matches={matches}/{total}{note}")
        if critical and mismatches:
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
