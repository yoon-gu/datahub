---
title: SQL 파싱
---

# DataHub SQL 파서

많은 데이터 플랫폼이 SQL을 기반으로 구축되어 있으므로, SQL 쿼리를 깊이 이해하는 것은 컬럼 수준 lineage, 사용 현황 분석 등에 있어 매우 중요합니다.

DataHub의 SQL 파서는 [sqlglot](https://github.com/tobymao/sqlglot) 위에 구축되었으며, SQL 파싱의 정확도를 향상시키기 위한 다수의 추가 기능을 제공합니다.

벤치마크에서 DataHub SQL 파서는 97~99%의 정확도로 lineage를 생성하며, 다른 SQL 파서들보다 훨씬 뛰어난 성능을 보입니다.

파서의 기술적 세부 사항에 관한 블로그 포스트를 게시했습니다: [SQL 쿼리에서 컬럼 Lineage 추출하기](https://medium.com/datahub-project/extracting-column-level-lineage-from-sql-779b8ce17567).

## 기본 제공 SQL 파싱 지원

DataHub가 이미 [통합을 지원하는](https://docs.datahub.com/integrations) 도구를 사용 중이라면, 해당 통합의 문서를 확인하세요.
Snowflake, BigQuery, Redshift, dbt, Looker, PowerBI, Airflow 등 대부분의 통합은 SQL 파서를 사용하여 컬럼 수준 lineage 및 사용 통계를 생성합니다.

기본적으로 컬럼 수준 lineage를 지원하지 않지만 데이터베이스 쿼리 로그를 사용할 수 있는 다른 데이터베이스 시스템을 사용하는 경우, [SQL queries](../generated/ingestion/sources/sql-queries.md) 커넥터를 통해 쿼리 로그에서 컬럼 수준 lineage 및 테이블/컬럼 사용 통계를 생성할 수 있습니다.

## SDK 지원

SDK는 SQL 쿼리를 프로그래밍 방식으로 파싱하기 위한 [`DataHubGraph.parse_sql_lineage()`](../../python-sdk/clients/graph-client.mdx#datahub.ingestion.graph.client.DataHubGraph.parse_sql_lineage) 메서드를 제공합니다.

결과 객체에는 파서의 신뢰도를 나타내는 0~1 범위의 값인 `sql_parsing_result.debug_info.confidence_score` 필드가 포함되어 있습니다.

`datahub.sql_parsing` 모듈에도 다수의 유틸리티가 있습니다. `SqlParsingAggregator`는 임시 테이블 및 테이블 이름 변경/교체에 걸친 lineage를 해석할 수 있어 특히 유용합니다.
이러한 유틸리티는 DataHub SDK의 공식 지원 대상이 아니므로, SDK의 나머지 부분과 동일한 수준의 안정성과 지원이 보장되지 않습니다.

## 지원 기능

### 지원됨

- `SELECT`, `CREATE`, `INSERT`, `UPDATE`, `DELETE`, `MERGE` 구문에 대한 테이블 수준 lineage
- `SELECT` (including `SELECT INTO`), `CREATE VIEW`, `CREATE TABLE AS SELECT` (CTAS), `INSERT`, `UPDATE` 구문에 대한 컬럼 수준 lineage
- 서브쿼리
- CTE
- `UNION ALL` 구문 - `UNION`의 각 절에 걸쳐 lineage를 병합합니다
- `SELECT *` 및 유사 표현식은 DataHub에 등록된 테이블 schema를 기반으로 자동 확장됩니다. 플랫폼 인스턴스도 지원됩니다.
- 테이블과 컬럼 이름이 대소문자를 구분하지 않는 시스템에 대한 자동 처리. 일반적으로 해당 테이블 schema를 DataHub로 수집할 때 `convert_urns_to_lowercase`가 활성화되어 있어야 합니다.
  - 구체적으로, 올바른 URN을 확인하기 위해 테이블 이름과 schema에 대해 퍼지 매칭을 수행합니다. 대소문자만 다른 여러 테이블/컬럼은 지원하지 않습니다.
- BigQuery의 경우 샤딩된 테이블 접미사가 자동으로 정규화됩니다. 예를 들어 `proj.dataset.table_20230616`은 `proj.dataset.table_yyyymmdd`로 정규화됩니다. 이는 DataHub BigQuery ingestion 커넥터의 동작 방식과 일치하므로 lineage가 올바르게 연결됩니다.

### 지원되지 않음

- 스칼라 `UDF` - UDF의 입력 컬럼을 가리키는 lineage는 생성하지만, UDF 자체를 이해할 수는 없습니다.
- 테이블 값 함수 (테이블 형식 `UDF` 포함)
- `json_extract` 및 유사 함수
- `UNNEST` - 최대한 처리하지만 `UNNEST` 구문이 있는 경우 컬럼 수준 lineage를 신뢰성 있게 생성할 수 없습니다.
- Struct - struct 하위 필드를 최대한 해석하려 하지만 보장되지 않습니다. 이는 컬럼 수준 lineage에만 영향을 미칩니다.
  - BigQuery에서 `SELECT IF (main.id is not null, main, extras).* FROM my_schema.main_users main FULL JOIN my_schema.external_users extras USING (id)` 와 같은 동적 테이블 언패킹도 포함됩니다.
- Snowflake의 다중 테이블 INSERT
- 다중 구문 SQL / SQL 스크립팅

### 제한 사항

- 기반 [sqlglot](https://github.com/tobymao/sqlglot) 라이브러리에서 지원하는 20개 이상의 SQL 방언만 지원합니다.
- 현재 지원하지 않지만 향후 지원할 예정인 몇 가지 SQL 구문이 있습니다.
  - `INSERT INTO (col1_new, col2_new) SELECT col1_old, col2_old FROM ...`. `INSERT INTO` 구문은 (1) 컬럼 목록을 지정하지 않거나, (2) `SELECT` 절의 컬럼과 일치하는 컬럼 목록을 지정하는 경우만 지원합니다.
  - `MERGE INTO` 구문 - 이 구문에 대한 컬럼 수준 lineage는 생성하지 않습니다.
- DataHub의 테이블 schema 정보가 오래되었거나 올바르지 않은 경우 정확한 컬럼 수준 lineage를 생성하지 못할 수 있습니다.
- 테이블 이름 접두사가 있는 BigQuery의 `_partitiontime` 및 `_partitiondate` 의사 컬럼(예: `my_table._partitiontime`)을 처리할 때 오류가 발생할 수 있습니다. 단, `_partitiontime` 및 `_partitiondate`와 같이 한정자 없이 참조하는 경우는 정상적으로 처리됩니다.
- `WHERE`, `GROUP BY`, `ORDER BY`, `JOIN`, `HAVING`, `PARTITION BY`와 같은 필터링 또는 정렬 절에서 참조된 컬럼은 lineage의 일부로 간주하지 않습니다. 예를 들어 `SELECT col1, col2 FROM upstream_table WHERE col3 = 3`은 `col3`과 관련된 lineage를 생성하지 않습니다.
- 일반적으로 정적 테이블 참조만 분석합니다. 예를 들어 `identifier` 함수가 SQL 런타임에 해석되기 때문에 `SELECT * FROM identifier('my_db.my_schema.my_table')` 같은 Snowflake 쿼리는 lineage를 생성하지 않습니다.
