# DataHub 오픈 데이터 품질 Assertions 명세

DataHub는 간단한 범용 YAML 기반 형식을 사용하여 데이터 품질 검사/기대치/assertions를 선언하고, 이를 [Snowflake DMFs](https://docs.snowflake.com/en/user-guide/data-quality-intro), dbt 테스트, Great Expectations 또는 DataHub Cloud와 같은 서드파티 데이터 품질 도구에서 직접 등록하거나 실행할 수 있는 아티팩트로 컴파일할 수 있는 오픈소스 데이터 품질 Assertions 명세 및 컴파일러를 개발하고 있습니다.

궁극적으로 우리의 목표는 데이터 품질 검사를 정의하기 위한 프레임워크에 구애받지 않는 이식성 높은 형식을 제공하여, DataHub와 같은 카탈로그 도구에서 이러한 데이터 품질 검사 결과의 최종 소비자에게 서비스 중단 없이 기본 assertion 엔진을 원활하게 교체할 수 있도록 하는 것입니다.

## 통합

현재 DataHub 오픈 Assertions 명세는 다음 통합을 지원합니다:

- [Snowflake DMF Assertions](snowflake/snowflake_dmfs.md)

그리고 다음 통합 구축에 대한 기여를 찾고 있습니다:

- [기여 요청] dbt 테스트
- [기여 요청] Great Expectation 검사

아래에서 YAML로 assertions를 정의하는 방법을 살펴보고 지원되는 각 통합에 대한 사용 개요를 제공합니다.

## 명세: YAML로 데이터 품질 Assertions 선언

다음 assertion 유형은 현재 DataHub YAML Assertion 명세에서 지원됩니다:

- [Freshness](/docs/managed-datahub/observe/freshness-assertions.md)
- [Volume](/docs/managed-datahub/observe/volume-assertions.md)
- [Column](/docs/managed-datahub/observe/column-assertions.md)
- [Custom SQL](/docs/managed-datahub/observe/custom-sql-assertions.md)
- [Schema](/docs/managed-datahub/observe/schema-assertions.md)

각 assertion 유형은 구조에서 크기, 컬럼 무결성, 커스텀 지표에 이르기까지 구조화된 테이블(예: 데이터 웨어하우스 또는 데이터 레이크)의 다른 측면을 검증하는 것을 목표로 합니다.

이 섹션에서는 각각을 정의하는 예시를 살펴보겠습니다.

### Freshness Assertions

Freshness Assertions를 사용하면 데이터가 예상 기간 내에 업데이트되었는지 확인할 수 있습니다.
아래에서 YAML을 통해 다양한 유형의 freshness assertions를 정의하는 예시를 찾을 수 있습니다.

#### 테이블이 6시간마다 업데이트되는지 확인

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: freshness
    lookback_interval: "6 hours"
    last_modified_field: updated_at
    schedule:
      type: interval
      interval: "6 hours" # 6시간마다 실행
```

이 assertion은 `test_db.public` 스키마의 `purchase_events` 테이블이 지난 6시간 이내에 `updated_at` 컬럼을 사용하여 업데이트가 이루어졌는지 결정하는 쿼리를 실행하여 확인합니다.
이 검사를 사용하려면 특정 행의 마지막 수정 타임스탬프를 포함하는 필드를 지정해야 합니다.

`lookback_interval` 필드는 assertion의 "되돌아보기 윈도우"를 지정하는 데 사용되고, `schedule` 필드는 assertion을 실행하는 빈도를 지정하는 데 사용됩니다.
이를 통해 되돌아보기 윈도우와 다른 빈도로 assertion을 예약할 수 있습니다. 예를 들어 더 자주 검사하여 데이터가 "오래된" 즉시 감지할 수 있습니다.

#### 지원되는 소스 유형

현재 Freshness Assertions에 지원되는 유일한 `sourceType`은 `LAST_MODIFIED_FIELD`입니다. 향후에는 `HIGH_WATERMARK` 및 `AUDIT_LOG`, `INFORMATION_SCHEMA`와 같은 데이터 소스별 유형을 포함한 추가 소스 유형을 지원할 수 있습니다.

### Volume Assertions

Volume Assertions를 사용하면 dataset의 레코드 수가 기대치를 충족하는지 확인할 수 있습니다.
아래에서 YAML을 통해 다양한 유형의 volume assertions를 정의하는 예시를 찾을 수 있습니다.

#### 테이블 행 수가 예상 범위 내에 있는지 확인

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: volume
    metric: "row_count"
    condition:
      type: between
      min: 1000
      max: 10000
    # filters: "event_type = 'purchase'" 선택적으로 필터 추가.
    schedule:
      type: on_table_change # 테이블에 새 데이터가 추가될 때 실행.
```

이 assertion은 `test_db.public` 스키마의 `purchase_events` 테이블에 1000에서 10000개의 레코드가 있는지 확인합니다.
`condition` 필드를 사용하여 비교 유형을 지정하고, `min` 및 `max` 필드를 사용하여 비교할 값 범위를 지정할 수 있습니다.
`filters` 필드를 사용하여 선택적으로 집계할 레코드를 필터링하는 SQL WHERE 절을 지정할 수 있습니다.
`schedule` 필드를 사용하여 고정 스케줄 또는 테이블에 새 데이터가 추가될 때 assertion이 실행되어야 하는 시기를 지정할 수 있습니다.
현재 지원되는 유일한 지표는 `row_count`입니다.

#### 테이블 행 수가 값보다 작은지 확인

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: volume
    metric: "row_count"
    condition:
      type: less_than_or_equal_to
      value: 1000
    # filters: "event_type = 'purchase'" 선택적으로 필터 추가.
    schedule:
      type: on_table_change # 테이블에 새 데이터가 추가될 때 실행.
```

#### 테이블 행 수가 값보다 큰지 확인

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: volume
    metric: "row_count"
    condition:
      type: greater_than_or_equal_to
      value: 1000
    # filters: "event_type = 'purchase'" 선택적으로 필터 추가.
    schedule:
      type: on_table_change # 테이블에 새 데이터가 추가될 때 실행.
```

#### 지원되는 조건

지원되는 전체 volume assertion 조건 집합:

- `equal_to`
- `not_equal_to`
- `greater_than`
- `greater_than_or_equal_to`
- `less_than`
- `less_than_or_equal_to`
- `between`

### Column Assertions

Column Assertions를 사용하면 컬럼의 값이 기대치를 충족하는지 확인할 수 있습니다.
아래에서 YAML을 통해 다양한 유형의 column assertions를 정의하는 예시를 찾을 수 있습니다.

명세는 현재 2가지 유형의 Column Assertions를 지원합니다:

- **Field Value**: 컬럼의 값이 특정 조건을 충족한다고 asserts합니다.
- **Field Metric**: 컬럼의 값에 대해 집계된 특정 지표가 특정 조건을 충족한다고 asserts합니다.

아래에서 각각의 예시를 살펴보겠습니다.

#### Field Values Assertion: 모든 컬럼 값이 예상 범위 내에 있는지 확인

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: field
    field: amount
    condition:
      type: between
      min: 0
      max: 10
    exclude_nulls: True
    # filters: "event_type = 'purchase'" 선택적으로 Column Assertion에 대한 필터 추가.
    # failure_threshold:
    #  type: count
    #  value: 10
    schedule:
      type: on_table_change
```

이 assertion은 `test_db.public` 스키마의 `purchase_events` 테이블에서 `amount` 컬럼의 모든 값이 0에서 10 사이에 있는지 확인합니다.
`field` 필드를 사용하여 assertion할 컬럼을 지정하고, `condition` 필드를 사용하여 비교 유형을 지정하며, `min` 및 `max` 필드를 사용하여 비교할 값 범위를 지정할 수 있습니다.
`schedule` 필드를 사용하여 고정 스케줄 또는 테이블에 새 데이터가 추가될 때 assertion이 실행되어야 하는 시기를 지정할 수 있습니다.
`filters` 필드를 사용하여 선택적으로 집계할 레코드를 필터링하는 SQL WHERE 절을 지정할 수 있습니다.
`exclude_nulls` 필드를 사용하여 assertion에서 NULL 값을 제외할지 여부를 지정할 수 있습니다. 이는 NULL이 검사를 실패시키는 대신 무시됨을 의미합니다.
`failure_threshold`를 사용하여 assertion이 실패로 간주되기 전에 실패할 수 있는 행의 임계값을 설정할 수 있습니다.

#### Field Values Assertion: 모든 컬럼 값이 예상 집합 내에 있는지 확인

값 집합 중 하나를 포함해야 하는 VARCHAR/STRING 컬럼을 검증하려면:

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: field
    field: product_id
    condition:
      type: in
      value:
        - "product_1"
        - "product_2"
        - "product_3"
    exclude_nulls: False
    # filters: "event_type = 'purchase'" 선택적으로 Column Assertion에 대한 필터 추가.
    # failure_threshold:
    #  type: count
    #  value: 10
    schedule:
      type: on_table_change
```

#### Field Values Assertion: 모든 컬럼 값이 이메일 주소인지 확인

문자열 컬럼에 유효한 이메일 주소가 포함되어 있는지 검증하려면:

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: field
    field: email_address
    condition:
      type: matches_regex
      value: "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"
    exclude_nulls: False
    # filters: "event_type = 'purchase'" 선택적으로 Column Assertion에 대한 필터 추가.
    # failure_threshold:
    #  type: count
    #  value: 10
    schedule:
      type: on_table_change
```

#### Field Values Assertion: 지원되는 조건

지원되는 전체 field value 조건 집합:

- `in`
- `not_in`
- `is_null`
- `is_not_null`
- `equal_to`
- `not_equal_to`
- `greater_than` # 숫자 전용
- `greater_than_or_equal_to` # 숫자 전용
- `less_than` # 숫자 전용
- `less_than_or_equal_to` # 숫자 전용
- `between` # 숫자 전용
- `matches_regex` # 문자열 전용
- `not_empty` # 문자열 전용
- `length_greater_than` # 문자열 전용
- `length_less_than` # 문자열 전용
- `length_between` # 문자열 전용

#### Field Metric Assertion: 컬럼에 누락된 값이 없는지 확인

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: field
    field: col_date
    metric: null_count
    condition:
      type: equal_to
      value: 0
    # filters: "event_type = 'purchase'" 선택적으로 Column Assertion에 대한 필터 추가.
    schedule:
      type: on_table_change
```

이 assertion은 `test_db.public` 스키마의 `purchase_events` 테이블에서 `col_date` 컬럼에 NULL 값이 없는지 확인합니다.

#### Field Metric Assertion: 컬럼에 중복이 없는지 확인

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: field
    field: id
    metric: unique_percentage
    condition:
      type: equal_to
      value: 100
    # filters: "event_type = 'purchase'" 선택적으로 Column Assertion에 대한 필터 추가.
    schedule:
      type: on_table_change
```

이 assertion은 `test_db.public` 스키마의 `purchase_events` 테이블에서 `id` 컬럼에 중복이 없는지
고유 비율이 100%인지 확인합니다.

#### Field Metric Assertion: 문자열 컬럼이 빈 문자열이 아닌지 확인

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: field
    field: name
    metric: empty_percentage
    condition:
      type: equal_to
      value: 0
    # filters: "event_type = 'purchase'" 선택적으로 Column Assertion에 대한 필터 추가.
    schedule:
      type: on_table_change
```

이 assertion은 `test_db.public` 스키마의 `purchase_events` 테이블에서 `name` 컬럼이 빈 비율이 0%인지 확인하여 절대 빈 값이 없음을 보장합니다.

#### Field Metric Assertion: 지원되는 지표

지원되는 전체 field 지표 집합:

- `null_count`
- `null_percentage`
- `unique_count`
- `unique_percentage`
- `empty_count`
- `empty_percentage`
- `min`
- `max`
- `mean`
- `median`
- `stddev`
- `negative_count`
- `negative_percentage`
- `zero_count`
- `zero_percentage`

### Field Metric Assertion: 지원되는 조건

지원되는 전체 field metric 조건 집합:

- `equal_to`
- `not_equal_to`
- `greater_than`
- `greater_than_or_equal_to`
- `less_than`
- `less_than_or_equal_to`
- `between`

### Custom SQL Assertions

Custom SQL Assertions를 사용하면 커스텀 SQL 쿼리를 정의하여 데이터가 기대치를 충족하는지 확인할 수 있습니다.
유일한 조건은 SQL 쿼리가 단일 값을 반환해야 하며 이것이 예상 값과 비교된다는 것입니다.
아래에서 YAML을 통해 다양한 유형의 custom SQL assertions를 정의하는 예시를 찾을 수 있습니다.

SQL Assertions는 다른 assertion 유형으로 쉽게 표현할 수 없는 더 복잡한 데이터 품질 검사에 유용하며, 커스텀 지표, 복잡한 집계, 크로스 테이블 무결성 검사(JOIN) 또는 기타 SQL 기반 데이터 품질 검사를 assert하는 데 사용할 수 있습니다.

#### 외래 키 무결성 확인

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: sql
    statement: |
      SELECT COUNT(*)
      FROM test_db.public.purchase_events AS pe
      LEFT JOIN test_db.public.products AS p
      ON pe.product_id = p.id
      WHERE p.id IS NULL
    condition:
      type: equal_to
      value: 0
    schedule:
      type: interval
      interval: "6 hours" # 6시간마다 실행
```

이 assertion은 `test_db.public` 스키마의 `purchase_events` 테이블에서 `product_id` 컬럼이 `products` 테이블의 `id`에 해당하는 값이 없는 행이 없는지 확인합니다.

#### 여러 테이블 간 행 수 비교

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: sql
    statement: |
      SELECT COUNT(*) FROM test_db.public.purchase_events
      - (SELECT COUNT(*) FROM test_db.public.purchase_events_raw) AS row_count_difference
    condition:
      type: equal_to
      value: 0
    schedule:
      type: interval
      interval: "6 hours" # 6시간마다 실행
```

이 assertion은 처리된 테이블의 행 수에서 raw 테이블의 행 수를 빼서 `purchase_events`의 행 수가 업스트림 `purchase_events_raw` 테이블의 행 수와 정확히 일치하는지 확인합니다.

#### 지원되는 조건

지원되는 전체 custom SQL assertion 조건 집합:

- `equal_to`
- `not_equal_to`
- `greater_than`
- `greater_than_or_equal_to`
- `less_than`
- `less_than_or_equal_to`
- `between`

### Schema Assertions (출시 예정)

Schema Assertions를 사용하면 커스텀 SQL 쿼리를 정의하여 데이터가 기대치를 충족하는지 확인할 수 있습니다.
아래에서 YAML을 통해 다양한 유형의 custom SQL assertions를 정의하는 예시를 찾을 수 있습니다.

명세는 현재 2가지 유형의 Schema Assertions를 지원합니다:

- **Exact Match**: 테이블의 schema(컬럼 이름 및 데이터 유형)가 예상 schema와 정확히 일치한다고 asserts합니다
- **Contains Match** (하위 집합): 테이블의 schema(컬럼 이름 및 데이터 유형)가 예상 schema의 하위 집합이라고 asserts합니다

#### 실제 Schema가 예상 Schema와 정확히 같은지 확인

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: schema
    condition:
      type: exact_match
      columns:
        - name: id
          type: INTEGER
        - name: product_id
          type: STRING
        - name: amount
          type: DECIMAL
        - name: updated_at
          type: TIMESTAMP
    schedule:
      type: interval
      interval: "6 hours" # 6시간마다 실행
```

이 assertion은 `test_db.public` 스키마의 `purchase_events` 테이블이 정확한 컬럼 이름 및 데이터 유형으로 지정된 것과 정확히 일치하는 schema를 가지고 있는지 확인합니다.

#### 실제 Schema가 예상 Schema를 모두 포함하는지 확인

```yaml
version: 1
assertions:
  - entity: urn:li:dataset:(urn:li:dataPlatform:snowflake,test_db.public.purchase_events,PROD)
    type: schema
    condition:
      type: contains
      columns:
        - name: id
          type: integer
        - name: product_id
          type: string
        - name: amount
          type: number
    schedule:
      type: interval
      interval: "6 hours" # 6시간마다 실행
```

이 assertion은 `test_db.public` 스키마의 `purchase_events` 테이블이 정확한 컬럼 이름 및 데이터 유형으로 예상 schema에 지정된 모든 컬럼을 포함하는지 확인합니다.
실제 schema에는 예상 schema에 지정되지 않은 추가 컬럼이 포함될 수 있습니다.

#### 지원되는 데이터 유형

Schema Assertion 명세에서 현재 지원되는 고수준 데이터 유형:

- string
- number
- boolean
- date
- timestamp
- struct
- array
- map
- union
- bytes
- enum
