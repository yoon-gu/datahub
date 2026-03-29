# 검색

DataHub의 Python SDK를 사용하면 데이터 생태계 전반에 걸쳐 메타데이터를 쉽게 검색하고 탐색할 수 있습니다. 알 수 없는 dataset을 탐색하거나, 환경별로 필터링하거나, 고급 검색 도구를 구축하려는 경우 이 가이드에서 프로그래밍 방식으로 이를 수행하는 방법을 안내합니다.

**Search SDK를 사용하면 다음을 할 수 있습니다:**

- 키워드 또는 구조화된 필터를 사용하여 데이터 에셋 검색
- 환경, 플랫폼, 타입, 커스텀 속성 또는 기타 메타데이터 필드로 필터링
- 고급 쿼리를 위한 `AND` / `OR` / `NOT` 논리 사용

## 시작하기

DataHub SDK를 사용하려면 [`acryl-datahub`](https://pypi.org/project/acryl-datahub/)를 설치하고 DataHub 인스턴스에 대한 연결을 설정해야 합니다. 시작하려면 [설치 가이드](https://docs.datahub.com/docs/metadata-ingestion/cli-ingestion#installing-datahub-cli)를 따르세요.

DataHub 인스턴스에 연결하기:

```python
from datahub.sdk import DataHubClient

client = DataHubClient(server="<your_server>", token="<your_token>")
```

- **server**: DataHub GMS 서버의 URL
  - 로컬: `http://localhost:8080`
  - 호스팅: `https://<your_datahub_url>/gms`
- **token**: DataHub 인스턴스에서 [개인 액세스 토큰을 생성](../../../authentication/personal-access-tokens.md)해야 합니다.

## 검색 유형

DataHub는 두 가지 주요 검색 방식을 제공합니다:

- **쿼리 기반 검색**: 이름, 설명, 컬럼 이름과 같은 공통 필드에서 간단한 키워드를 사용하여 검색합니다.
- **필터 기반 검색**: 플랫폼, 환경, 엔티티 타입 및 기타 메타데이터 필드로 결과 범위를 좁히기 위해 구조화된 필터를 사용하여 검색합니다.

:::note 쿼리와 필터 결합하기

쿼리와 필터를 함께 사용하면 더 정밀한 검색이 가능합니다. 자세한 내용은 [이 예시](#find-all-snowflake-datasets-related-to-forecast)를 확인하세요.

:::

### 쿼리 기반 검색

쿼리 기반 검색을 통해 간단한 키워드로 검색할 수 있습니다. 이름, 설명, 컬럼 이름과 같은 공통 필드에서 일치하는 결과를 찾습니다. 찾고 있는 에셋을 정확히 모를 때 탐색에 유용합니다.

#### 판매 관련 모든 엔티티 찾기

예를 들어, 아래 스크립트는 메타데이터에 `sales`가 포함된 에셋을 검색합니다.

```python
{{ inline /metadata-ingestion/examples/library/search_with_query.py show_path_as_comment }}
```

예시 출력:

```python
[
  DatasetUrn("urn:li:dataset:(urn:li:dataPlatform:snowflake,sales_revenue_2023,PROD)"),
  DatasetUrn("urn:li:dataset:(urn:li:dataPlatform:snowflake,sales_forecast,PROD)")
]
```

### 필터 기반 검색

필터 기반 검색을 통해 플랫폼, 환경, 엔티티 타입 및 기타 구조화된 필드로 결과를 좁힐 수 있습니다.
특정 에셋 타입이나 메타데이터 필드로 결과를 좁히고 싶을 때 유용합니다.

#### 모든 Snowflake 엔티티 찾기

예를 들어, 아래 스크립트는 Snowflake 플랫폼의 엔티티를 검색합니다.

```python
{{ inline /metadata-ingestion/examples/library/search_with_filter.py show_path_as_comment }}
```

#### Forecast 관련 모든 Snowflake Dataset 찾기

쿼리와 필터를 결합하여 검색 결과를 더욱 세밀하게 조정할 수 있습니다.
예를 들어, "forecast"를 포함하면서 차트 또는 Snowflake dataset인 항목을 검색합니다.

```python
{{ inline /metadata-ingestion/examples/library/search_with_query_and_filter.py show_path_as_comment }}
```

사용 가능한 필터에 대한 자세한 내용은 [필터 옵션](#filter-options)을 참고하세요.

## 일반적인 검색 패턴

다음은 필터와 논리 연산을 사용한 고급 쿼리의 일반적인 예시들입니다:

#### 모든 Dashboard 찾기

```python
{{ inline /metadata-ingestion/examples/library/search_filter_by_entity_type.py show_path_as_comment }}
```

#### 모든 Snowflake 엔티티 찾기

```python
{{ inline /metadata-ingestion/examples/library/search_filter_by_platform.py show_path_as_comment }}
```

#### 프로덕션 환경의 모든 엔티티 찾기

```python
{{ inline /metadata-ingestion/examples/library/search_filter_by_env.py show_path_as_comment }}
```

#### 특정 도메인의 모든 엔티티 찾기

```python
{{ inline /metadata-ingestion/examples/library/search_filter_by_domain.py show_path_as_comment }}
```

#### 특정 서브타입을 가진 모든 엔티티 찾기

```python
{{ inline /metadata-ingestion/examples/library/search_filter_by_entity_subtype.py show_path_as_comment }}
```

#### 특정 커스텀 속성을 가진 모든 엔티티 찾기

```python
{{ inline /metadata-ingestion/examples/library/search_filter_by_custom_property.py show_path_as_comment }}
```

#### 모든 Chart와 Snowflake Dataset 찾기

`and_`, `or_`, `not_`과 같은 논리 연산을 사용하여 필터를 결합하여 고급 쿼리를 만들 수 있습니다. 자세한 내용은 [논리 연산자 옵션](#logical-operator-options)을 확인하세요.

```python
{{ inline /metadata-ingestion/examples/library/search_filter_combined_operation.py show_path_as_comment }}
```

#### 프로덕션 환경에 없는 모든 Chart 찾기

```python
{{ inline /metadata-ingestion/examples/library/search_filter_not.py show_path_as_comment }}
```

#### 고급: 다른 검색 가능한 필드로 엔티티 찾기

`F.custom_filter()`를 사용하여 urn, name, description과 같은 특정 필드를 대상으로 할 수 있습니다. 허용된 `condition` 값의 전체 목록은 [커스텀 필터를 위한 지원 조건](#supported-conditions-for-custom-filter)을 확인하세요.

```python
{{ inline /metadata-ingestion/examples/library/search_filter_custom.py show_path_as_comment }}
```

:::note 검색 가능한 필드
`F.custom_filter()`를 사용하면 PDL 파일에서 `@Searchable`로 어노테이션된 필드를 필터링에 사용할 수 있습니다. 예를 들어, [DataJobInfo.pdl](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/datajob/DataJobInfo.pdl#L21)에서 `@Searchable`로 어노테이션되어 있으므로 datajob 엔티티를 `name`, `description`, `env` 등의 필드로 필터링할 수 있습니다.
:::

## Search SDK 레퍼런스

전체 레퍼런스는 [search SDK 레퍼런스](../../../../python-sdk/sdk-v2/search-client.mdx)를 참고하세요.

### 필터 옵션

SDK에서 사용 가능한 필터 옵션은 다음과 같습니다:

| 필터 타입       | 예시 코드                                      |
| --------------- | ---------------------------------------------- |
| 플랫폼          | `F.platform("snowflake")`                      |
| 환경            | `F.env("PROD")`                                |
| 엔티티 타입     | `F.entity_type("dataset")`                     |
| 도메인          | `F.domain("urn:li:domain:xyz")`                |
| 서브타입        | `F.entity_subtype("ML Experiment")`            |
| 삭제 상태       | `F.soft_deleted("NOT_SOFT_DELETED")`           |
| 커스텀 속성     | `F.has_custom_property("department", "sales")` |

### 논리 연산자 옵션

필터를 결합하는 데 사용할 수 있는 논리 연산자는 다음과 같습니다:

| 연산자 | 예시 코드     | 설명                                             |
| ------ | ------------- | ------------------------------------------------ |
| AND    | `F.and_(...)` | 모든 지정된 조건에 일치하는 엔티티를 반환합니다. |
| OR     | `F.or_(...)`  | 하나 이상의 조건에 일치하는 엔티티를 반환합니다. |
| NOT    | `F.not_(...)` | 주어진 조건에 일치하는 엔티티를 제외합니다.      |

### 커스텀 필터를 위한 지원 조건

`F.custom_filter()`를 사용하여 urn, name, description과 같은 특정 필드에 조건을 적용합니다.

| 조건           | 설명                                                                                      |
| -------------- | ----------------------------------------------------------------------------------------- |
| `EQUAL`        | 문자열 필드의 정확한 일치.                                                                |
| `CONTAIN`      | 문자열 필드에 부분 문자열 포함 여부.                                                      |
| `START_WITH`   | 특정 부분 문자열로 시작하는지 여부.                                                       |
| `END_WITH`     | 특정 부분 문자열로 끝나는지 여부.                                                         |
| `GREATER_THAN` | 숫자 또는 타임스탬프 필드에서 값이 지정된 값보다 큰지 확인합니다.                        |
| `LESS_THAN`    | 숫자 또는 타임스탬프 필드에서 값이 지정된 값보다 작은지 확인합니다.                      |

## FAQ

**인증은 어떻게 처리하나요?**
DataHub 인스턴스 설정에서 개인 액세스 토큰을 생성하여 `DataHubClient`에 전달하세요. [개인 액세스 토큰 가이드](../../../authentication/personal-access-tokens.md)를 확인하세요.

**쿼리와 필터를 결합할 수 있나요?**
네. 더 정밀한 검색을 위해 `query`와 `filter`를 함께 사용하세요.
