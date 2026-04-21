"""Dump metadata from a running DataHub GMS into datahub-lite (DuckDB).

사용:
    .venv/bin/python mcp-server-datahub-lite/scripts/populate_lite_from_gms.py

환경변수 (옵션):
    DATAHUB_GMS_URL     (기본: http://localhost:8080)
    DATAHUB_GMS_TOKEN   (기본: 아래 하드코드된 로컬 dev 토큰)

처리 방식:
    1) GMS의 `searchAcrossEntities` 를 모든 관심 entity type에 대해 페이지네이션으로 순회
    2) 각 entity 의 모든 aspect 를 `datahub get --urn` 으로 조회
    3) `datahub.lite.duckdb_lite.DuckDBLite` 에 MetadataChangeProposal 형태로 적재

GraphQL 스키마 차이 때문에 직접 GraphQL 을 쓰기보다 DataHub CLI 래퍼 (`get_graph_v2`) 를 사용.
"""

from __future__ import annotations

import os
import sys
import time
from typing import Iterator

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig
from datahub.lite.duckdb_lite import DuckDBLite
from datahub.lite.duckdb_lite_config import DuckDBLiteConfig
from datahub.metadata.schema_classes import SystemMetadataClass


GMS_URL = os.environ.get("DATAHUB_GMS_URL", "http://localhost:8080")
GMS_TOKEN = os.environ.get(
    "DATAHUB_GMS_TOKEN",
    "",
)

ENTITY_TYPES = [
    "dataset",
    "dataFlow",
    "dataJob",
    "chart",
    "dashboard",
    "mlModel",
    "mlModelGroup",
    "mlFeatureTable",
    "mlFeature",
    "tag",
    "glossaryTerm",
    "glossaryNode",
    "domain",
    "corpuser",
    "corpGroup",
    "dataProduct",
    "container",
    "query",
    "assertion",
    "schemaField",
]


def iter_urns(graph: DataHubGraph, entity_type: str) -> Iterator[str]:
    yield from graph.get_urns_by_filter(entity_types=[entity_type], batch_size=500)


def emit_to_lite(lite: DuckDBLite, urn: str, aspects: dict) -> int:
    written = 0
    now_ms = int(time.time() * 1000)
    for aspect_name, aspect_obj in aspects.items():
        if aspect_obj is None:
            continue
        try:
            mcp = MetadataChangeProposalWrapper(
                entityUrn=urn,
                aspect=aspect_obj,
                systemMetadata=SystemMetadataClass(
                    lastObserved=now_ms,
                    runId="populate-from-gms",
                    properties={},
                ),
            )
            lite.write(mcp)
            written += 1
        except Exception as e:
            print(f"  [skip] {urn} / {aspect_name}: {e}", file=sys.stderr)
    return written


def main() -> int:
    graph = DataHubGraph(DataHubGraphConfig(server=GMS_URL, token=GMS_TOKEN))
    graph.test_connection()
    print(f"[*] connected to {GMS_URL}")

    lite = DuckDBLite(DuckDBLiteConfig(file="/Users/yoon-gu/.datahub/lite/datahub.duckdb"))
    print("[*] lite db opened")

    total_entities = 0
    total_aspects = 0
    for etype in ENTITY_TYPES:
        count = 0
        for urn in iter_urns(graph, etype):
            aspects = graph.get_entity_semityped(urn)
            if not aspects:
                continue
            n = emit_to_lite(lite, urn, aspects)
            total_aspects += n
            count += 1
        print(f"  - {etype:20s} entities={count}")
        total_entities += count

    print(f"[*] done. entities={total_entities} aspects={total_aspects}")
    lite.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
