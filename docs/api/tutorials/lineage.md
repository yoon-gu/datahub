# Lineage

DataHub의 Python SDK를 사용하면 메타데이터 entity 간의 lineage를 프로그래밍 방식으로 정의하고 조회할 수 있습니다. DataHub Lineage SDK를 통해 다음이 가능합니다:

- dataset, data job, dashboard, chart 전반에 걸친 **테이블 수준 및 컬럼 수준 lineage** 추가
- SQL 쿼리에서 **lineage 자동 추론**
- 특정 entity 또는 컬럼에 대한 lineage(upstream 또는 downstream) **조회**
- 구조화된 필터를 사용한 **lineage 결과 필터링**

## 시작하기

DataHub SDK를 사용하려면 [`acryl-datahub`](https://pypi.org/project/acryl-datahub/)를 설치하고 DataHub 인스턴스에 대한 연결을 설정해야 합니다. [설치 가이드](https://docs.datahub.com/docs/metadata-ingestion/cli-ingestion#installing-datahub-cli)를 참조하여 시작하세요.

DataHub 인스턴스에 연결:

```python
from datahub.sdk import DataHubClient

client = DataHubClient(server="<your_server>", token="<your_token>")
```

- **server**: DataHub GMS 서버의 URL
  - 로컬: `http://localhost:8080`
  - 호스팅: `https://<your_datahub_url>/gms`
- **token**: DataHub 인스턴스에서 [Personal Access Token을 생성](https://docs.datahub.com/docs/authentication/personal-access-tokens)해야 합니다.

## Lineage 추가

`add_lineage()` 메서드를 사용하면 두 entity 간의 lineage를 정의할 수 있습니다.

### Entity Lineage 추가

두 dataset, data job, dashboard 또는 chart 간의 lineage를 생성할 수 있습니다. `upstream`과 `downstream` 매개변수는 연결하려는 entity의 URN이어야 합니다.

#### Dataset 간 Entity Lineage 추가

```python
{{ inline /metadata-ingestion/examples/library/lineage_dataset_add.py show_path_as_comment }}
```

#### Datajob 간 Entity Lineage 추가

```python
{{ inline /metadata-ingestion/examples/library/lineage_datajob_to_datajob.py show_path_as_comment }}
```

:::note Lineage 조합
지원되는 lineage 조합은 [지원되는 Lineage 조합](#supported-lineage-combinations)을 참조하세요.
:::

### 컬럼 Lineage 추가

dataset을 연결할 때 `column_lineage` 매개변수를 사용하여 컬럼 수준 lineage를 추가할 수 있습니다.

#### 퍼지 매칭을 사용한 컬럼 Lineage 추가

```python
{{ inline /metadata-ingestion/examples/library/lineage_dataset_column.py show_path_as_comment }}
```

`column_lineage`를 **True**로 설정하면 DataHub는 이름을 기반으로 컬럼을 자동으로 매핑하며, 퍼지 매칭을 허용합니다. 이는 upstream과 downstream dataset의 컬럼 이름이 유사하지만 완전히 동일하지 않을 때 유용합니다. (예: upstream의 `customer_id`와 downstream의 `CustomerId`). 자세한 내용은 [컬럼 Lineage 옵션](#column-lineage-options)을 참조하세요.

#### 엄격한 매칭을 사용한 컬럼 Lineage 추가

```python
{{ inline /metadata-ingestion/examples/library/lineage_dataset_column_auto_strict.py show_path_as_comment }}
```

이 방식은 엄격한 매칭으로 컬럼 수준 lineage를 생성하며, upstream과 downstream dataset 간에 컬럼 이름이 정확히 일치해야 합니다.

#### 사용자 정의 매핑을 사용한 컬럼 Lineage 추가

사용자 정의 매핑의 경우, 키가 downstream 컬럼 이름이고 값이 upstream 컬럼 이름 목록인 딕셔너리를 사용할 수 있습니다. 이를 통해 복잡한 관계를 지정할 수 있습니다.

```python
{{ inline /metadata-ingestion/examples/library/lineage_dataset_column_custom_mapping.py show_path_as_comment }}
```

### SQL에서 Lineage 추론

`infer_lineage_from_sql()`을 사용하면 SQL 쿼리에서 직접 lineage를 추론할 수 있습니다. 쿼리를 파싱하여 upstream 및 downstream dataset을 결정하고, lineage(가능한 경우 컬럼 수준 lineage 포함)와 SQL 변환 로직을 보여주는 쿼리 노드를 자동으로 추가합니다.

```python
{{ inline /metadata-ingestion/examples/library/lineage_dataset_from_sql.py show_path_as_comment }}
```

:::note DataHub SQL 파서

SQL 파싱 처리 방법에 대한 자세한 내용은 아래를 참조하세요.

- [DataHub SQL 파서 문서](../../lineage/sql_parsing.md)
- [블로그 포스트: SQL에서 컬럼 수준 Lineage 추출하기](https://medium.com/datahub-project/extracting-column-level-lineage-from-sql-779b8ce17567)

:::

### Lineage와 함께 쿼리 노드 추가

`add_lineage`에 `transformation_text`를 제공하면 DataHub는 변환 로직을 나타내는 쿼리 노드를 생성합니다. 이는 dataset 간에 데이터가 어떻게 변환되는지 추적하는 데 유용합니다.

```python
{{ inline /metadata-ingestion/examples/library/lineage_dataset_add_with_query_node.py show_path_as_comment }}
```

변환 텍스트는 Python 스크립트, Airflow DAG 코드, 또는 upstream dataset이 downstream dataset으로 변환되는 방식을 설명하는 기타 코드 등 어떤 변환 로직도 사용할 수 있습니다.

<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/query-node.png"/>
</p>

:::note
`transformation_text`를 제공해도 컬럼 lineage는 생성되지 않습니다. 컬럼 수준 lineage를 활성화하려면 `column_lineage` 매개변수를 지정해야 합니다.

변환을 설명하는 SQL 쿼리가 있는 경우 [infer_lineage_from_sql](#infer-lineage-from-sql)을 사용하여 쿼리를 자동으로 파싱하고 컬럼 수준 lineage를 추가할 수 있습니다.
:::

## Lineage 조회

`get_lineage()` 메서드를 사용하면 특정 entity의 lineage를 조회할 수 있습니다.

### Entity Lineage 조회

#### Dataset의 Upstream Lineage 조회

dataset이 의존하는 직접적인 upstream entity를 반환합니다. 기본적으로 바로 위의 upstream entity만 조회합니다 (1홉).

```python
{{ inline /metadata-ingestion/examples/library/lineage_get_basic.py show_path_as_comment }}
```

#### 여러 홉에 걸친 Dataset의 Downstream Lineage 조회

1홉 이상 떨어진 upstream/downstream entity를 조회하려면 `max_hops` 매개변수를 사용할 수 있습니다. 이를 통해 지정된 홉 수만큼 lineage 그래프를 탐색할 수 있습니다.

```python
{{ inline /metadata-ingestion/examples/library/lineage_get_with_hops.py show_path_as_comment }}

```

:::note MAX_HOPS 사용 시 주의사항
`max_hops`가 2보다 크면 전체 lineage 그래프를 탐색하고 `count`로 결과를 제한합니다.
:::

#### 반환 타입

`get_lineage()`는 `LineageResult` 객체의 목록을 반환합니다.

```python
results = [
  LineageResult(
    urn="urn:li:dataset:(urn:li:dataPlatform:snowflake,table_2,PROD)",
    type="DATASET",
    hops=1,
    direction="downstream",
    platform="snowflake",
    name="table_2", # entity 이름
    paths=[] # 컬럼 수준 lineage에만 값이 채워짐
  )
]
```

### 컬럼 수준 Lineage 조회

#### Dataset 컬럼의 Downstream Lineage 조회

`source_column` 매개변수를 지정하여 컬럼 수준 lineage를 조회할 수 있습니다. 지정된 컬럼을 포함하는 lineage 경로를 반환합니다.

```python
{{ inline /metadata-ingestion/examples/library/lineage_column_get.py show_path_as_comment }}
```

`SchemaFieldUrn`을 `source_urn`으로 전달하여 컬럼 수준 lineage를 조회할 수도 있습니다.

```python
{{ inline /metadata-ingestion/examples/library/lineage_column_get_from_schemafield.py show_path_as_comment }}

```

#### 반환 타입

반환 타입은 entity lineage와 동일하지만, 컬럼 lineage 경로를 포함하는 추가적인 `paths` 필드가 있습니다.

```python
results = [
  LineageResult(
    urn="urn:li:dataset:(urn:li:dataPlatform:snowflake,table_2,PROD)",
    type="DATASET",
    hops=1,
    direction="downstream",
    platform="snowflake",
    name="table_2", # entity 이름
    paths=[
      LineagePath(
        urn="urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,table_1,PROD),col1)",
        column_name="col1", # 컬럼 이름
        entity_name="table_1", # 컬럼을 포함하는 entity 이름
      ),
      LineagePath(
        urn="urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,table_2,PROD),col4)",
        column_name="col4", # 컬럼 이름
        entity_name="table_2", # 컬럼을 포함하는 entity 이름
      )
    ] # 컬럼 수준 lineage에만 값이 채워짐
  )
]
```

결과 해석 방법에 대한 자세한 내용은 [Lineage 결과 해석](#interpreting-lineage-results)을 참조하세요.

### Lineage 결과 필터링

플랫폼, 타입, 도메인, 환경 등으로 필터링할 수 있습니다.

```python
{{ inline /metadata-ingestion/examples/library/lineage_get_with_filter.py show_path_as_comment }}
```

사용 가능한 필터에 대한 자세한 내용은 [Search SDK 문서](./sdk/search_client.md#filter-based-search)에서 확인할 수 있습니다.

## Lineage SDK 참조

전체 참조는 [lineage SDK 참조](../../../python-sdk/sdk-v2/lineage-client.mdx)를 참조하세요.

### 지원되는 Lineage 조합

Lineage API는 다음 entity 조합을 지원합니다:

| Upstream Entity | Downstream Entity |
| --------------- | ----------------- |
| Dataset         | Dataset           |
| Dataset         | DataJob           |
| DataJob         | DataJob           |
| DataJob         | Dataset           |
| Dataset         | Dashboard         |
| Chart           | Dashboard         |
| Dashboard       | Dashboard         |
| Dataset         | Chart             |

> ℹ️ 컬럼 수준 lineage와 변환 텍스트를 사용한 쿼리 노드 생성은 `Dataset → Dataset` lineage에서만 **지원됩니다**.

### 컬럼 Lineage 옵션

dataset 간 lineage의 경우 `add_lineage()`의 `column_lineage` 매개변수를 여러 방식으로 지정할 수 있습니다:

| 값              | 설명                                                                         |
| --------------- | ---------------------------------------------------------------------------- |
| `False`         | 컬럼 수준 lineage 비활성화 (기본값)                                          |
| `True`          | 자동 매핑으로 컬럼 수준 lineage 활성화 ("auto_fuzzy"와 동일)                 |
| `"auto_fuzzy"`  | 퍼지 매칭으로 컬럼 수준 lineage 활성화 (유사한 컬럼 이름에 유용)            |
| `"auto_strict"` | 엄격한 매칭으로 컬럼 수준 lineage 활성화 (정확한 컬럼 이름 일치 필요)       |
| 컬럼 매핑       | downstream 컬럼 이름을 upstream 컬럼 이름 목록에 매핑하는 딕셔너리           |

:::note `auto_fuzzy` vs `auto_strict`

- **`auto_fuzzy`**: 유사한 이름을 기반으로 컬럼을 자동으로 매칭하여 명명 규칙에 유연성을 허용합니다. 예를 들어 다음 두 컬럼은 매칭으로 간주됩니다:
  - user_id → userId
  - customer_id → CustomerId
- **`auto_strict`**: upstream과 downstream dataset 간에 정확한 컬럼 이름 일치가 필요합니다. 예를 들어 upstream dataset의 `customer_id`는 downstream dataset의 `customer_id`와 정확히 일치해야 합니다.

:::

### 컬럼 Lineage 결과 해석

컬럼 수준 lineage를 조회하면 dataset 간에 컬럼이 어떻게 관련되는지를 보여주는 `paths`가 결과에 포함됩니다. 각 경로는 소스 컬럼에서 대상 컬럼까지의 lineage를 나타내는 컬럼 URN 목록입니다.

예를 들어, 세 테이블에 걸친 다음과 같은 lineage가 있다고 가정해 보겠습니다:

<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/column-lineage.png"/>
</p>

#### `max_hops=1` 예시

```python
>>> client.lineage.get_lineage(
        source_urn="urn:li:dataset:(urn:li:dataPlatform:snowflake,table_1,PROD)",
        source_column="col1",
        direction="downstream",
        max_hops=1
    )
```

**반환값:**

```python
[
    {
        "urn": "...table_2...",
        "hops": 1,
        "paths": [
            ["...table_1.col1", "...table_2.col4"],
            ["...table_1.col1", "...table_2.col5"]
        ]
    }
]
```

#### `max_hops=2` 예시

```python
>>> client.lineage.get_lineage(
        source_urn="urn:li:dataset:(urn:li:dataPlatform:snowflake,table_1,PROD)",
        source_column="col1",
        direction="downstream",
        max_hops=2
    )
```

**반환값:**

```python
[
    {
        "urn": "...table_2...",
        "hops": 1,
        "paths": [
            ["...table_1.col1", "...table_2.col4"],
            ["...table_1.col1", "...table_2.col5"]
        ]
    },
    {
        "urn": "...table_3...",
        "hops": 2,
        "paths": [
            ["...table_1.col1", "...table_2.col4", "...table_3.col7"]
        ]
    }
]
```

## 대안: Lineage GraphQL API

일반적으로 lineage에는 Python SDK 사용을 권장하지만, GraphQL API를 사용하여 lineage를 추가하고 조회할 수도 있습니다.

#### GraphQL로 Dataset 간 Lineage 추가

```graphql
mutation updateLineage {
  updateLineage(
    input: {
      edgesToAdd: [
        {
          downstreamUrn: "urn:li:dataset:(urn:li:dataPlatform:hive,logging_events,PROD)"
          upstreamUrn: "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_deleted,PROD)"
        }
      ]
      edgesToRemove: []
    }
  )
}
```

#### GraphQL로 Downstream Lineage 조회

```graphql
query scrollAcrossLineage {
  scrollAcrossLineage(
    input: {
      query: "*"
      urn: "urn:li:dataset:(urn:li:dataPlatform:hive,logging_events,PROD)"
      count: 10
      direction: DOWNSTREAM
      orFilters: [
        {
          and: [
            {
              condition: EQUAL
              negated: false
              field: "degree"
              values: ["1", "2", "3+"]
            }
          ]
        }
      ]
    }
  ) {
    searchResults {
      degree
      entity {
        urn
        type
      }
    }
  }
}
```

#### GraphQL로 시간 필터링된 Lineage 조회

`lineageFlags`를 사용하여 마지막 업데이트 시간으로 lineage 엣지를 필터링합니다:

```graphql
query searchAcrossLineage {
  searchAcrossLineage(
    input: {
      query: "*"
      urn: "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.orders,PROD)"
      count: 10
      direction: UPSTREAM
      orFilters: [{ and: [{ field: "degree", values: ["1"] }] }]
      lineageFlags: {
        startTimeMillis: 1625097600000
        endTimeMillis: 1627776000000
      }
    }
  ) {
    searchResults {
      entity {
        urn
        type
      }
      degree
    }
  }
}
```

이 쿼리는 2021년 7월 1일과 8월 1일 사이에 마지막으로 업데이트된 upstream lineage 엣지만 반환합니다.

## FAQ

**컬럼 수준에서 lineage를 조회할 수 있나요?**
네 — dataset 간 lineage의 경우 `add_lineage()`와 `get_lineage()` 모두 컬럼 수준 lineage를 지원합니다.

**SQL 쿼리를 전달하면 lineage를 자동으로 얻을 수 있나요?**
네 — `infer_lineage_from_sql()`을 사용하면 쿼리를 파싱하고 테이블 및 컬럼 lineage를 추출할 수 있습니다.

**lineage 조회 시 필터를 사용할 수 있나요?**
네 — `get_lineage()`는 Search SDK와 동일하게 `FilterDsl`을 통한 구조화된 필터를 허용합니다.
