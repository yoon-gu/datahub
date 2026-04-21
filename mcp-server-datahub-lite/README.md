# mcp-server-datahub-lite

DataHub 메타데이터를 로컬 `datahub-lite` (DuckDB) 인스턴스에서 읽어 MCP 로 노출하는 서버.

공식 `mcp-server-datahub` 가 DataHub GMS (GraphQL + Elasticsearch) 를 전제로 하는 데 비해,
이 구현은 **Docker 없이 DuckDB 파일만으로** 동작 → 오프라인 / 에어갭 환경에 친화적.

## 노출 도구

원본 `mcp-server-datahub` 의 6개 tool 을 lite 에서 재구현. 파라미터 이름은 가능한 한 동일.

| 도구 | 구현 상태 | 비고 |
|---|---|---|
| `search` | ✅ | `/q` prefix + `+`AND / OR / NOT / "phrase". 필터는 `=` AND-only 서브셋. 와일드카드·facet 미지원 |
| `get_entities` | ✅ | 단일 또는 배열, `{urn,exists,entity_type,aspects}` 반환 |
| `list_schema_fields` | ✅ | keywords (단일=정확매치 / 리스트=OR), limit/offset |
| `get_lineage` | ✅ | BFS, DataJob 을 실제 노드로 포함, `degree`=hop 거리 |
| `get_lineage_paths_between` | ✅ | `nx.all_simple_paths`, column 레벨 fineGrained 엣지까지 포함 |
| `get_dataset_queries` | ✅ | `querySubjects` 역인덱스, `column` 지정 시 schemaField URN 매칭 |

원본 대비 차이:
- 풀텍스트 검색: DuckDB 해이스택 위 substring 매칭 — Elasticsearch 의 랭킹/와일드카드/facet aggregation 없음
- 컬럼 리니지 경로: `fineGrainedLineages` 가 기록된 edge 만 경로에 노출
- `sort_by=lastOperationTime` 같은 프로파일링-의존 필드 미지원

## 셋업 (개발)

```bash
cd mcp-server-datahub-lite
pip install -e .

# 1) lite 인스턴스 준비
datahub lite init --type duckdb

# 2) 기존 GMS 메타데이터를 lite 로 덤프 (개발기에서만 필요)
.venv/bin/python scripts/populate_lite_from_gms.py

# 3) 서버 기동 (stdio)
mcp-server-datahub-lite --transport stdio
```

## 셋업 (온프렘, 오프라인)

에어갭 환경 반입 절차:

1. 개발기에서 wheelhouse 생성
   ```bash
   pip download --dest ./wheelhouse --python-version 3.10 \
     --platform manylinux2014_x86_64 --only-binary=:all: \
     mcp-server-datahub-lite
   ```
2. wheelhouse + populate 된 `datahub.duckdb` 파일을 함께 반입
3. 온프렘에서
   ```bash
   pip install --no-index --find-links=./wheelhouse mcp-server-datahub-lite
   mcp-server-datahub-lite --lite-db /data/datahub.duckdb
   ```

## Claude Desktop 연결

`claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "datahub-lite": {
      "command": "/path/to/.venv/bin/mcp-server-datahub-lite",
      "args": ["--lite-db", "/path/to/datahub.duckdb"]
    }
  }
}
```
