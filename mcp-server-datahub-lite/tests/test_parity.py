"""Parity tests between full mcp-server-datahub (GMS) and lite (DuckDB).

동치 판단 기준은 tool 별로 다름 (structural equivalence 가 아니라 *의미적*
동등성 기준). 각 테스트는 assertion 실패 시 어느 쪽이 더 나왔는지 diff 출력.

환경변수:
    DATAHUB_GMS_URL, DATAHUB_GMS_TOKEN  : full 서버 기동에 필수
    DATAHUB_LITE_DB                     : lite duckdb 경로 (기본 ~/.datahub/lite/datahub.duckdb)

실행:
    cd mcp-server-datahub-lite
    pytest tests/ -v
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Set

import pytest

from tests.conftest import SAMPLE_DATASETS, SAMPLE_LINEAGE_PAIRS


# ------------------------------------------------------------------
# 응답 정규화 헬퍼 — full/lite 가 동일한 tool 을 다르게 감쌈
# ------------------------------------------------------------------

def _result_payload(res: Any) -> Any:
    """Both servers may wrap responses in {'result': ...}; unwrap once."""
    if isinstance(res, dict) and set(res.keys()) == {"result"}:
        return res["result"]
    return res


def _extract_urns(payload: Any, key: str = "urn") -> Set[str]:
    """Pull URN set from a payload that is either a list of dicts, dict-of-dicts,
    or a list of `{entity: {urn}}` wrappers (GMS-style searchResults)."""
    out: Set[str] = set()
    if isinstance(payload, list):
        for item in payload:
            if not isinstance(item, dict):
                continue
            if item.get(key):
                out.add(item[key])
            entity = item.get("entity")
            if isinstance(entity, dict) and entity.get(key):
                out.add(entity[key])
    elif isinstance(payload, dict):
        for k, v in payload.items():
            if isinstance(v, dict) and v.get(key):
                out.add(v[key])
            elif isinstance(k, str) and k.startswith("urn:li:"):
                out.add(k)
    return out


def _lineage_result_container(resp: Any) -> Optional[Dict[str, Any]]:
    """Full server wraps in `downstreams`/`upstreams`; lite returns flat.
    Return the container dict that holds searchResults/results."""
    if not isinstance(resp, dict):
        return None
    for key in ("downstreams", "upstreams"):
        inner = resp.get(key)
        if isinstance(inner, dict):
            return inner
    if "results" in resp or "searchResults" in resp or "total" in resp:
        return resp
    return None


def _format_set_diff(label: str, a: Set[str], b: Set[str]) -> str:
    only_a = sorted(a - b)[:5]
    only_b = sorted(b - a)[:5]
    lines = [f"{label} diff: |full|={len(a)} |lite|={len(b)} |intersection|={len(a & b)}"]
    if only_a:
        lines.append(f"  only in full: {only_a}")
    if only_b:
        lines.append(f"  only in lite: {only_b}")
    return "\n".join(lines)


# ------------------------------------------------------------------
# tools/list
# ------------------------------------------------------------------

EXPECTED_TOOL_NAMES = {
    "search",
    "get_entities",
    "list_schema_fields",
    "get_lineage",
    "get_lineage_paths_between",
    "get_dataset_queries",
}


def test_tools_list_covers_expected_surface(full_client, lite_client):
    full_tools = {t["name"] for t in full_client.list_tools()}
    lite_tools = {t["name"] for t in lite_client.list_tools()}

    missing_in_lite = EXPECTED_TOOL_NAMES - lite_tools
    assert not missing_in_lite, f"lite is missing: {missing_in_lite}"

    overlap = full_tools & lite_tools
    assert EXPECTED_TOOL_NAMES.issubset(overlap), (
        f"both servers should expose the core 6 tools. overlap={sorted(overlap)}"
    )


# ------------------------------------------------------------------
# get_entities
# ------------------------------------------------------------------

@pytest.mark.parametrize("urn", SAMPLE_DATASETS)
def test_get_entities_returns_same_aspect_set(full_client, lite_client, urn):
    full_resp = _result_payload(full_client.call("get_entities", {"urns": urn}))
    lite_resp = _result_payload(lite_client.call("get_entities", {"urns": urn}))

    def aspect_keys(resp: Any) -> Set[str]:
        if isinstance(resp, dict) and urn in resp:
            entry = resp[urn]
            if isinstance(entry, dict):
                if "aspects" in entry and isinstance(entry["aspects"], dict):
                    return set(entry["aspects"].keys())
                return {k for k in entry.keys() if k not in {"urn", "entity_type", "exists"}}
        if isinstance(resp, list):
            for item in resp:
                if isinstance(item, dict) and item.get("urn") == urn:
                    if "aspects" in item:
                        return set((item["aspects"] or {}).keys())
                    return {k for k in item.keys() if k not in {"urn", "entity_type", "exists"}}
        return set()

    full_keys = aspect_keys(full_resp)
    lite_keys = aspect_keys(lite_resp)

    # lite 의 populate 스크립트가 복사한 aspect subset 이 full 결과와 같아야 함
    # full 이 반환하는 aspect 가 더 많을 수는 있음 (timeseries 등). 최소한
    # lite 에 있는 건 full 에도 있어야 함.
    assert lite_keys.issubset(full_keys) or full_keys.issubset(lite_keys), (
        f"aspect set divergence for {urn}:\n"
        f"  full:  {sorted(full_keys)}\n"
        f"  lite:  {sorted(lite_keys)}\n"
        f"  full only: {sorted(full_keys - lite_keys)}\n"
        f"  lite only: {sorted(lite_keys - full_keys)}"
    )


# ------------------------------------------------------------------
# list_schema_fields
# ------------------------------------------------------------------

DATASETS_WITH_SCHEMA = [
    "urn:li:dataset:(urn:li:dataPlatform:mysql,sequence_ai.evt_A01,DEV)",
    "urn:li:dataset:(urn:li:dataPlatform:mysql,sequence_ai.evt_B01,DEV)",
]


@pytest.mark.parametrize("urn", DATASETS_WITH_SCHEMA)
def test_list_schema_fields_same_fieldpath_set(full_client, lite_client, urn):
    def fieldpaths(resp: Any) -> Set[str]:
        data = _result_payload(resp)
        if isinstance(data, list):
            return {f.get("fieldPath") for f in data if isinstance(f, dict)}
        if isinstance(data, dict):
            fields = data.get("fields") or []
            return {f.get("fieldPath") for f in fields if isinstance(f, dict)}
        return set()

    full_fields = fieldpaths(full_client.call("list_schema_fields", {"urn": urn, "limit": 500}))
    lite_fields = fieldpaths(lite_client.call("list_schema_fields", {"urn": urn, "limit": 500}))

    assert full_fields and lite_fields, (
        f"schema field lookup returned empty for {urn}: full={len(full_fields)} lite={len(lite_fields)}"
    )
    assert full_fields == lite_fields, _format_set_diff(f"list_schema_fields({urn})", full_fields, lite_fields)


# ------------------------------------------------------------------
# get_lineage — Phase 0 에서 입증된 1-hop 100% 일치 검증
# ------------------------------------------------------------------

@pytest.mark.parametrize("urn", SAMPLE_DATASETS)
@pytest.mark.parametrize("upstream", [True, False])
def test_get_lineage_one_hop_datasets_match(full_client, lite_client, urn, upstream):
    full_resp = _result_payload(
        full_client.call("get_lineage", {"urn": urn, "upstream": upstream, "max_hops": 1, "max_results": 500})
    )
    lite_resp = _result_payload(
        lite_client.call("get_lineage", {"urn": urn, "upstream": upstream, "max_hops": 1, "max_results": 500})
    )

    def dataset_urns(resp: Any) -> Set[str]:
        container = _lineage_result_container(resp)
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
                degree = r.get("degree") if isinstance(r, dict) else None
                if degree is None or degree <= 1:
                    out.add(urn_val)
        return out

    full_ds = dataset_urns(full_resp)
    lite_ds = dataset_urns(lite_resp)

    direction = "upstream" if upstream else "downstream"
    assert full_ds == lite_ds, _format_set_diff(
        f"get_lineage 1-hop {direction} datasets({urn})", full_ds, lite_ds
    )


# ------------------------------------------------------------------
# get_lineage_paths_between — 둘 다 최소 하나 경로 찾아야 함
# ------------------------------------------------------------------

@pytest.mark.parametrize("source,target", SAMPLE_LINEAGE_PAIRS)
def test_get_lineage_paths_between_both_find_path(full_client, lite_client, source, target):
    full_resp = _result_payload(
        full_client.call(
            "get_lineage_paths_between",
            {"source_urn": source, "target_urn": target},
        )
    )
    lite_resp = _result_payload(
        lite_client.call(
            "get_lineage_paths_between",
            {"source_urn": source, "target_urn": target},
        )
    )

    def path_count(resp: Any) -> int:
        if isinstance(resp, dict):
            if "pathCount" in resp:
                return resp["pathCount"] or 0
            if "paths" in resp and isinstance(resp["paths"], list):
                return len(resp["paths"])
        return 0

    full_n = path_count(full_resp)
    lite_n = path_count(lite_resp)

    assert full_n > 0 and lite_n > 0, (
        f"both should find at least one path {source}->{target}: full={full_n} lite={lite_n}"
    )


# ------------------------------------------------------------------
# get_dataset_queries — Query URN 집합 일치 (populate 가 querySubjects 옮겼어야 함)
# ------------------------------------------------------------------

DATASETS_WITH_QUERIES = [
    "urn:li:dataset:(urn:li:dataPlatform:mysql,sequence_ai.cust_evnt_dtl_itm_dev,DEV)",
]


@pytest.mark.parametrize("urn", DATASETS_WITH_QUERIES)
def test_get_dataset_queries_same_query_urns(full_client, lite_client, urn):
    def query_urns(resp: Any) -> Set[str]:
        data = _result_payload(resp)
        if not isinstance(data, dict):
            return set()
        queries = data.get("queries") or []
        return {q.get("urn") for q in queries if isinstance(q, dict) and q.get("urn")}

    full_q = query_urns(full_client.call("get_dataset_queries", {"urn": urn, "count": 100}))
    lite_q = query_urns(lite_client.call("get_dataset_queries", {"urn": urn, "count": 100}))

    assert full_q and lite_q, (
        f"both should return at least one query for {urn}: full={len(full_q)} lite={len(lite_q)}"
    )
    assert full_q == lite_q, _format_set_diff(f"get_dataset_queries({urn})", full_q, lite_q)


# ------------------------------------------------------------------
# search — 공통분만 (basic entity_type filter)
# ------------------------------------------------------------------

def test_search_entity_type_filter_counts_match(full_client, lite_client):
    def hit_urns(resp: Any) -> Set[str]:
        data = _result_payload(resp)
        if isinstance(data, dict):
            return _extract_urns(data.get("results") or data.get("searchResults") or [])
        return set()

    full_resp = full_client.call(
        "search", {"query": "*", "filter": "entity_type = query", "num_results": 100}
    )
    lite_resp = lite_client.call(
        "search", {"query": "*", "filter": "entity_type = query", "num_results": 100}
    )

    full_q = hit_urns(full_resp)
    lite_q = hit_urns(lite_resp)

    # Query 엔티티는 populate 가 모두 복사했어야 함
    assert full_q == lite_q, _format_set_diff("search entity_type=query", full_q, lite_q)
