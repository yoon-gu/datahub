import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Assertions

<FeatureAvailability saasOnly />

이 가이드는 **DataHub Cloud** 네이티브 assertions에 Assertion API를 사용하는 방법을 구체적으로 다룹니다:

- [Freshness Assertions](/docs/managed-datahub/observe/freshness-assertions.md)
- [Volume Assertions](/docs/managed-datahub/observe/volume-assertions.md)
- [Column Assertions](/docs/managed-datahub/observe/column-assertions.md)
- [Schema Assertions](/docs/managed-datahub/observe/schema-assertions.md)
- [Custom SQL Assertions](/docs/managed-datahub/observe/custom-sql-assertions.md)

## Assertions API를 사용하는 이유

Assertions API를 사용하면 DataHub Cloud로 Assertions를 생성, 예약, 실행, 삭제할 수 있습니다. 또한 assertions 상태 변경 또는 다른 entity 변경이 발생할 때 알림을 받기 위한 구독을 관리할 수 있습니다.

### 이 가이드의 목표

이 가이드는 테이블에 대한 Assertions를 생성, 예약, 실행 및 삭제하는 방법을 보여줍니다.

## 사전 요구 사항

API 호출을 수행하는 액터는 해당 테이블에 대해 `Edit Assertions` 및 `Edit Monitors` 권한이 있어야 합니다.

이 가이드의 Python 예제를 사용하는 경우 DataHub Cloud SDK 확장을 설치하세요:

```bash
pip install acryl-datahub-cloud
```

## Assertions 생성

다음 API를 사용하여 DataHub에 새 dataset Assertions를 생성할 수 있습니다.

### Freshness Assertion

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

새 freshness assertion을 생성하려면 `upsertDatasetFreshnessAssertionMonitor` GraphQL Mutation을 사용하세요.

```graphql
mutation upsertDatasetFreshnessAssertionMonitor {
  upsertDatasetFreshnessAssertionMonitor(
    input: {
      entityUrn: "<urn of entity being monitored>"
      schedule: {
        type: FIXED_INTERVAL
        fixedInterval: { unit: HOUR, multiple: 8 }
      }
      evaluationSchedule: {
        timezone: "America/Los_Angeles"
        cron: "0 */8 * * *"
      }
      evaluationParameters: { sourceType: INFORMATION_SCHEMA }
      mode: ACTIVE
    }
  ) {
    urn
  }
}
```

성공하면 이 API는 새 assertion에 대한 고유 식별자(URN)를 반환합니다:

```json
{
  "data": {
    "upsertDatasetFreshnessAssertionMonitor": {
      "urn": "urn:li:assertion:your-new-assertion-id"
    }
  },
  "extensions": {}
}
```

</TabItem>
<TabItem value="python" label="Python">

```python
from datahub.sdk import DataHubClient
from datahub.metadata.urns import DatasetUrn

# 클라이언트 초기화
client = DataHubClient(server="<your_server>", token="<your_token>")

# smart freshness assertion 생성 (AI 기반 이상 탐지)
dataset_urn = DatasetUrn.from_string("urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.table,PROD)")

smart_freshness_assertion = client.assertions.sync_smart_freshness_assertion(
    dataset_urn=dataset_urn,
    display_name="Smart Freshness Anomaly Monitor",
    # 감지 메커니즘 - information_schema 권장
    detection_mechanism="information_schema",
    # Smart 민감도 설정
    sensitivity="medium",  # 옵션: "low", "medium", "high"
    # 그룹화를 위한 태그
    tags=["automated", "freshness", "data_quality"],
    # assertion 활성화
    enabled=True
)

print(f"Created smart freshness assertion: {smart_freshness_assertion.urn}")

# 전통적인 freshness assertion 생성 (고정 간격)
freshness_assertion = client.assertions.sync_freshness_assertion(
    dataset_urn=dataset_urn,
    display_name="Fixed Interval Freshness Check",
    # 고정 간격 검사 - 테이블이 lookback window 내에서 업데이트되어야 함
    freshness_schedule_check_type="fixed_interval",
    # Lookback window - 테이블이 8시간 내에 업데이트되어야 함
    lookback_window={"unit": "HOUR", "multiple": 8},
    # 감지 메커니즘
    detection_mechanism="information_schema",
    # 평가 스케줄 - 얼마나 자주 확인할지
    schedule="0 */2 * * *",  # 2시간마다 확인
    # 태그
    tags=["automated", "freshness", "fixed_interval"],
    enabled=True
)

print(f"Created freshness assertion: {freshness_assertion.urn}")

# 마지막 확인 이후 freshness assertion 생성
since_last_check_assertion = client.assertions.sync_freshness_assertion(
    dataset_urn=dataset_urn,
    display_name="Since Last Check Freshness",
    # 마지막 확인 이후 - 마지막 평가 이후 테이블이 업데이트되어야 함
    freshness_schedule_check_type="since_the_last_check",
    # 마지막 수정 컬럼을 사용한 감지 메커니즘
    detection_mechanism={
        "type": "last_modified_column",
        "column_name": "updated_at",
        "additional_filter": "status = 'active'"
    },
    # 평가 스케줄 - 얼마나 자주 확인할지
    schedule="0 */6 * * *",  # 6시간마다 확인
    # 태그
    tags=["automated", "freshness", "since_last_check"],
    enabled=True
)

print(f"Created since last check assertion: {since_last_check_assertion.urn}")

# high watermark 컬럼을 사용한 freshness assertion 생성
watermark_freshness_assertion = client.assertions.sync_freshness_assertion(
    dataset_urn=dataset_urn,
    display_name="High Watermark Freshness Check",
    # 특정 lookback window를 사용한 고정 간격 검사
    freshness_schedule_check_type="fixed_interval",
    # Lookback window - 지난 24시간 내 업데이트 확인
    lookback_window={"unit": "DAY", "multiple": 1},
    # high watermark 컬럼을 사용한 감지 메커니즘 (예: 자동 증가 ID)
    detection_mechanism={
        "type": "high_watermark_column",
        "column_name": "id",
        "additional_filter": "status != 'deleted'"
    },
    # 평가 스케줄
    schedule="0 8 * * *",  # 매일 오전 8시 확인
    # 태그
    tags=["automated", "freshness", "high_watermark"],
    enabled=True
)

print(f"Created watermark freshness assertion: {watermark_freshness_assertion.urn}")
```

</TabItem>
</Tabs>

자세한 내용은 [Freshness Assertions](/docs/managed-datahub/observe/freshness-assertions.md) 가이드를 참조하세요.

### Volume Assertions

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

새 volume assertion을 생성하려면 `upsertDatasetVolumeAssertionMonitor` GraphQL Mutation을 사용하세요.

```graphql
mutation upsertDatasetVolumeAssertionMonitor {
  upsertDatasetVolumeAssertionMonitor(
    input: {
      entityUrn: "<urn of entity being monitored>"
      type: ROW_COUNT_TOTAL
      rowCountTotal: {
        operator: BETWEEN
        parameters: {
          minValue: { value: "10", type: NUMBER }
          maxValue: { value: "20", type: NUMBER }
        }
      }
      evaluationSchedule: {
        timezone: "America/Los_Angeles"
        cron: "0 */8 * * *"
      }
      evaluationParameters: { sourceType: INFORMATION_SCHEMA }
      mode: ACTIVE
    }
  ) {
    urn
  }
}
```

성공하면 이 API는 새 assertion에 대한 고유 식별자(URN)를 반환합니다:

```json
{
  "data": {
    "upsertDatasetVolumeAssertionMonitor": {
      "urn": "urn:li:assertion:your-new-assertion-id"
    }
  },
  "extensions": {}
}
```

</TabItem>

<!-- TODO: move the python examples to metadata-ingestion/examples/library -->
<TabItem value="python" label="Python">

```python
from datahub.sdk import DataHubClient
from datahub.metadata.urns import DatasetUrn

# 클라이언트 초기화
client = DataHubClient(server="<your_server>", token="<your_token>")

# smart volume assertion 생성 (AI 기반 이상 탐지)
dataset_urn = DatasetUrn.from_string("urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.table,PROD)")

smart_volume_assertion = client.assertions.sync_smart_volume_assertion(
    dataset_urn=dataset_urn,
    display_name="Smart Volume Check",
    # 감지 메커니즘 옵션
    detection_mechanism="information_schema",
    # Smart 민감도 설정
    sensitivity="medium",  # 옵션: "low", "medium", "high"
    # 그룹화를 위한 태그
    tags=["automated", "volume", "data_quality"],
    # 선택 사항: 데이터를 일별/주별 시간 버킷으로 분할
    time_bucketing_strategy={
        "timestamp_field_path": "created_at",
        "bucket_interval": {"unit": "DAY", "multiple": 1},
        "timezone": "America/Los_Angeles",
    },
    # 선택 사항: 더 스마트한 예측을 위한 과거 데이터 보정
    backfill_config={"backfill_start_date_ms": 1704067200000},  # 2024-01-01
    # assertion 활성화
    enabled=True
)

print(f"Created smart volume assertion: {smart_volume_assertion.urn}")

# 전통적인 volume assertion 생성 (고정 임계값 범위)
volume_assertion = client.assertions.sync_volume_assertion(
    dataset_urn=dataset_urn,
    display_name="Row Count Range Check",
    criteria_condition="ROW_COUNT_IS_WITHIN_A_RANGE",
    criteria_parameters=(1000, 10000),  # 1000에서 10000 행 사이
    # 감지 메커니즘
    detection_mechanism="information_schema",
    # 평가 스케줄
    schedule="0 */4 * * *",  # 4시간마다
    # 태그
    tags=["automated", "volume", "threshold_check"],
    enabled=True
)

print(f"Created volume assertion: {volume_assertion.urn}")

# 단일 임계값 예시
min_volume_assertion = client.assertions.sync_volume_assertion(
    dataset_urn=dataset_urn,
    display_name="Minimum Row Count Check",
    criteria_condition="ROW_COUNT_IS_GREATER_THAN_OR_EQUAL_TO",
    criteria_parameters=500,  # 최소 500행
    detection_mechanism="information_schema",
    schedule="0 */2 * * *",  # 2시간마다
    tags=["automated", "volume", "minimum_check"],
    enabled=True
)

print(f"Created minimum volume assertion: {min_volume_assertion.urn}")

# 성장 기반 assertion 예시
growth_volume_assertion = client.assertions.sync_volume_assertion(
    dataset_urn=dataset_urn,
    display_name="Daily Growth Check",
    criteria_condition="ROW_COUNT_GROWS_BY_AT_MOST_ABSOLUTE",
    criteria_parameters=1000,  # 검사 간 최대 1000행 증가
    detection_mechanism="information_schema",
    schedule="0 6 * * *",  # 매일 오전 6시
    tags=["automated", "volume", "growth_check"],
    enabled=True
)

print(f"Created growth volume assertion: {growth_volume_assertion.urn}")
```

</TabItem>
</Tabs>

자세한 내용은 [Volume Assertions](/docs/managed-datahub/observe/volume-assertions.md) 가이드를 참조하세요.

### Column Assertions

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

새 column assertion을 생성하려면 `upsertDatasetFieldAssertionMonitor` GraphQL Mutation을 사용하세요.

```graphql
mutation upsertDatasetFieldAssertionMonitor {
  upsertDatasetFieldAssertionMonitor(
    input: {
      entityUrn: "<urn of entity being monitored>"
      type: FIELD_VALUES
      fieldValuesAssertion: {
        field: {
          path: "<name of the column to be monitored>"
          type: "NUMBER"
          nativeType: "NUMBER(38,0)"
        }
        operator: GREATER_THAN
        parameters: { value: { type: NUMBER, value: "10" } }
        failThreshold: { type: COUNT, value: 0 }
        excludeNulls: true
      }
      evaluationSchedule: {
        timezone: "America/Los_Angeles"
        cron: "0 */8 * * *"
      }
      evaluationParameters: { sourceType: ALL_ROWS_QUERY }
      mode: ACTIVE
    }
  ) {
    urn
  }
}
```

성공하면 이 API는 새 assertion에 대한 고유 식별자(URN)를 반환합니다:

```json
{
  "data": {
    "upsertDatasetFieldAssertionMonitor": {
      "urn": "urn:li:assertion:your-new-assertion-id"
    }
  },
  "extensions": {}
}
```

</TabItem>
<TabItem value="python" label="Python">

```python
from datahub.sdk import DataHubClient
from datahub.metadata.urns import DatasetUrn

# 클라이언트 초기화
client = DataHubClient(server="<your_server>", token="<your_token>")

# smart column metric assertion 생성 (AI 기반 이상 탐지).
# 참고: Smart Assertions는 현재 다음 column metric만 지원합니다:
# null_count, unique_count, empty_count, zero_count, negative_count.
# 다른 메트릭(예: min, max, mean)의 경우 고정 임계값을 사용하는 일반 column metric assertion을 사용하세요
# (아래 참조).
dataset_urn = DatasetUrn.from_string("urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.table,PROD)")

smart_column_assertion = client.assertions.sync_smart_column_metric_assertion(
    dataset_urn=dataset_urn,
    column_name="user_id",
    metric_type="null_count",
    display_name="Smart Null Count Check - user_id",
    # column metric을 위한 감지 메커니즘
    detection_mechanism="all_rows_query_datahub_dataset_profile",
    # Smart 민감도 설정
    sensitivity="medium",  # 옵션: "low", "medium", "high"
    # 선택 사항: 데이터를 일별 시간 버킷으로 분할
    time_bucketing_strategy={
        "timestamp_field_path": "created_at",
        "bucket_interval": {"unit": "DAY", "multiple": 1},
        "timezone": "UTC",
    },
    # 선택 사항: 더 스마트한 예측을 위한 과거 데이터 보정
    backfill_config={"backfill_start_date_ms": 1704067200000},  # 2024-01-01
    # 태그
    tags=["automated", "column_quality", "null_checks"],
    enabled=True
)

print(f"Created smart column assertion: {smart_column_assertion.urn}")

# 일반 column metric assertion 생성 (집계 메트릭에 대한 고정 임계값).
# Smart Assertions가 지원하지 않는 메트릭(예: min, max, mean, median, stddev)에 사용하세요.
column_metric_assertion = client.assertions.sync_column_metric_assertion(
    dataset_urn=dataset_urn,
    column_name="price",
    metric_type="min",
    operator="greater_than_or_equal_to",
    criteria_parameters=0,
    display_name="Price Minimum Check",
    # 평가 스케줄
    schedule="0 */4 * * *",  # 4시간마다
    # 태그
    tags=["automated", "column_quality", "price_validation"],
    enabled=True
)

print(f"Created column metric assertion: {column_metric_assertion.urn}")

# ----------------------------
# Column value assertions (행 수준 검사)
# ----------------------------

# 예시 1: 정규식 패턴을 사용한 간단한 이메일 유효성 검사
# 모든 이메일 값이 유효한 이메일 형식과 일치하는지 확인
email_regex_assertion = client.assertions.sync_column_value_assertion(
    dataset_urn=dataset_urn,
    column_name="email",
    operator="regex_match",
    criteria_parameters=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

print(f"Created email regex assertion: {email_regex_assertion.urn}")

# 예시 2: 모든 파라미터를 포함한 상세 column value assertion
# 의미론적 제약 조건에 대해 컬럼의 개별 행 값 유효성 검사
column_value_assertion = client.assertions.sync_column_value_assertion(
    dataset_urn=dataset_urn,
    column_name="quantity",
    display_name="Quantity Positive Check",
    # 각 행의 값에 적용되는 연산자 (예: "greater_than", "between", "regex_match", "not_null")
    operator="greater_than",
    criteria_parameters=0,  # 각 수량은 반드시 > 0 이어야 함
    # 선택 사항: 유효성 검사 전에 변환 적용 (현재 문자열의 경우 "length" 지원)
    # transform="length",
    # 실패 임계값 구성
    fail_threshold_type="count",  # 실패를 세는 방법: "count" (절대 수) 또는 "percentage"
    fail_threshold_value=0,  # 이 수의 행이 실패하면 assertion 실패 (0 = 무관용)
    # 유효성 검사에서 null 값 제외 여부
    exclude_nulls=True,
    # 평가 스케줄 - 얼마나 자주 확인할지
    schedule="0 */4 * * *",  # 4시간마다 (cron 형식)
    # 그룹화 및 분류를 위한 태그
    tags=["automated", "column_quality", "value_validation"],
    # assertion 활성화
    enabled=True
)

print(f"Created column value assertion: {column_value_assertion.urn}")
```

</TabItem>
</Tabs>

자세한 내용은 [Column Assertions](/docs/managed-datahub/observe/column-assertions.md) 가이드를 참조하세요.

### Custom SQL Assertions

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

새 custom SQL assertion을 생성하려면 `upsertDatasetSqlAssertionMonitor` GraphQL Mutation을 사용하세요.

```graphql
mutation upsertDatasetSqlAssertionMonitor {
  upsertDatasetSqlAssertionMonitor(
    assertionUrn: "<urn of assertion created in earlier query>"
    input: {
      entityUrn: "<urn of entity being monitored>"
      type: METRIC
      description: "<description of the custom assertion>"
      statement: "<SQL query to be evaluated>"
      operator: GREATER_THAN_OR_EQUAL_TO
      parameters: { value: { value: "100", type: NUMBER } }
      evaluationSchedule: {
        timezone: "America/Los_Angeles"
        cron: "0 */6 * * *"
      }
      mode: ACTIVE
    }
  ) {
    urn
  }
}
```

성공하면 이 API는 새 assertion에 대한 고유 식별자(URN)를 반환합니다:

```json
{
  "data": {
    "upsertDatasetSqlAssertionMonitor": {
      "urn": "urn:li:assertion:your-new-assertion-id"
    }
  },
  "extensions": {}
}
```

---

**smart SQL** assertion(AI 이상 탐지)을 생성하려면 동일한 mutation에 `inferWithAI: true`를 사용하세요.

```graphql
mutation upsertDatasetSqlAssertionMonitor {
  upsertDatasetSqlAssertionMonitor(
    input: {
      entityUrn: "<urn of entity being monitored>"
      type: METRIC
      description: "<description of the smart SQL assertion>"
      statement: "<SQL query to be evaluated>"
      inferWithAI: true
      inferenceSettings: { sensitivity: { level: 5 } }
      # 플레이스홀더 연산자 및 파라미터 (AI가 실제 임계값을 추론함)
      operator: GREATER_THAN_OR_EQUAL_TO
      parameters: { value: { value: "0", type: NUMBER } }
      evaluationSchedule: {
        timezone: "America/Los_Angeles"
        cron: "0 */6 * * *"
      }
      mode: ACTIVE
    }
  ) {
    urn
  }
}
```

</TabItem>
<TabItem value="python" label="Python">

```python
from datahub.sdk import DataHubClient
from datahub.metadata.urns import DatasetUrn

# 클라이언트 초기화
client = DataHubClient(server="<your_server>", token="<your_token>")

# custom SQL assertion 생성
dataset_urn = DatasetUrn.from_string("urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.table,PROD)")

sql_assertion = client.assertions.sync_sql_assertion(
    dataset_urn=dataset_urn,
    display_name="Revenue Quality Check",
    statement="SELECT SUM(revenue) FROM database.schema.table WHERE date >= CURRENT_DATE - INTERVAL '1 day'",
    criteria_condition="IS_GREATER_THAN_OR_EQUAL_TO",
    criteria_parameters=1000,
    # 평가 스케줄
    schedule="0 6 * * *",  # 매일 오전 6시
    # 태그
    tags=["automated", "revenue", "data_quality"],
    enabled=True
)

print(f"Created SQL assertion: {sql_assertion.urn}")

# 범위 검사 예시
range_sql_assertion = client.assertions.sync_sql_assertion(
    dataset_urn=dataset_urn,
    display_name="Daily Order Count Range Check",
    statement="SELECT COUNT(*) FROM database.schema.orders WHERE DATE(created_at) = CURRENT_DATE",
    criteria_condition="IS_WITHIN_A_RANGE",
    criteria_parameters=(50, 500),  # 하루 50에서 500개 주문 사이
    schedule="0 */6 * * *",  # 6시간마다
    tags=["automated", "orders", "volume_check"],
    enabled=True
)

print(f"Created range SQL assertion: {range_sql_assertion.urn}")

# ----------------------------
# Smart SQL assertions (AI 이상 탐지)
# ----------------------------

smart_sql_assertion = client.assertions.sync_smart_sql_assertion(
    dataset_urn=dataset_urn,
    display_name="Smart Revenue Monitor",
    # 평가할 SQL 문 - 단일 숫자 값을 반환해야 함
    statement="SELECT SUM(revenue) FROM database.schema.table WHERE date >= CURRENT_DATE - INTERVAL '1 day'",
    # AI 민감도 설정
    sensitivity="medium",  # 옵션: "low", "medium", "high"
    # 평가 스케줄
    schedule="0 */6 * * *",  # 6시간마다
    # 선택 사항: 훈련 데이터 lookback
    training_data_lookback_days=60,
    # 태그
    tags=["automated", "revenue", "smart_sql"],
    enabled=True
)

print(f"Created smart SQL assertion: {smart_sql_assertion.urn}")
```

</TabItem>
</Tabs>

자세한 내용은 [Custom SQL Assertions](/docs/managed-datahub/observe/custom-sql-assertions.md) 가이드를 참조하세요.

### Schema Assertions

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

새 schema assertion을 생성하려면 `upsertDatasetSchemaAssertionMonitor` GraphQL Mutation을 사용하세요.

```graphql
mutation upsertDatasetSchemaAssertionMonitor {
  upsertDatasetSchemaAssertionMonitor(
    assertionUrn: "urn:li:assertion:existing-assertion-id"
    input: {
      entityUrn: "<urn of the table to be monitored>"
      assertion: {
        compatibility: EXACT_MATCH
        fields: [
          { path: "id", type: STRING }
          { path: "count", type: NUMBER }
          { path: "struct", type: STRUCT }
          { path: "struct.nestedBooleanField", type: BOOLEAN }
        ]
      }
      description: "<description of the schema assertion>"
      mode: ACTIVE
    }
  )
}
```

성공하면 이 API는 새 assertion에 대한 고유 식별자(URN)를 반환합니다:

```json
{
  "data": {
    "upsertDatasetSchemaAssertionMonitor": {
      "urn": "urn:li:assertion:your-new-assertion-id"
    }
  },
  "extensions": {}
}
```

</TabItem>
<TabItem value="python" label="Python">

```python
from datahub.sdk import DataHubClient
from datahub.metadata.urns import DatasetUrn

# 클라이언트 초기화
client = DataHubClient(server="<your_server>", token="<your_token>")

# exact match 호환성을 사용한 schema assertion 생성
dataset_urn = DatasetUrn.from_string("urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.table,PROD)")

schema_assertion = client.assertions.sync_schema_assertion(
    dataset_urn=dataset_urn,
    display_name="Expected Schema Check",
    # 호환성 모드 - schema를 얼마나 엄격하게 일치시킬지
    compatibility="EXACT_MATCH",  # 옵션: "EXACT_MATCH", "SUPERSET", "SUBSET"
    # 예상 schema 필드
    fields=[
        {"path": "id", "type": "STRING"},
        {"path": "count", "type": "NUMBER"},
        {"path": "created_at", "type": "TIME"},
        {"path": "is_active", "type": "BOOLEAN"},
    ],
    # 그룹화를 위한 태그
    tags=["automated", "schema", "data_quality"],
    # assertion 활성화
    enabled=True
)

print(f"Created schema assertion: {schema_assertion.urn}")

# superset 호환성을 사용한 schema assertion 생성
# (실제 schema는 적어도 이 필드를 포함해야 하지만 더 있어도 됨)
superset_assertion = client.assertions.sync_schema_assertion(
    dataset_urn=dataset_urn,
    display_name="Required Fields Check",
    compatibility="SUPERSET",
    fields=[
        {"path": "id", "type": "STRING"},
        {"path": "name", "type": "STRING"},
    ],
    # 평가 스케줄
    schedule="0 */6 * * *",  # 6시간마다
    tags=["automated", "schema", "required_fields"],
    enabled=True
)

print(f"Created superset schema assertion: {superset_assertion.urn}")

# 네이티브 유형 지정을 포함한 schema assertion 생성
detailed_schema_assertion = client.assertions.sync_schema_assertion(
    dataset_urn=dataset_urn,
    display_name="Detailed Schema Validation",
    compatibility="EXACT_MATCH",
    fields=[
        {"path": "id", "type": "STRING", "native_type": "VARCHAR(255)"},
        {"path": "amount", "type": "NUMBER", "native_type": "DECIMAL(10,2)"},
        {"path": "metadata", "type": "STRUCT"},
        {"path": "metadata.key", "type": "STRING"},
        {"path": "tags", "type": "ARRAY"},
    ],
    enabled=True
)

print(f"Created detailed schema assertion: {detailed_schema_assertion.urn}")
```

</TabItem>
</Tabs>

자세한 내용은 [Schema Assertions](/docs/managed-datahub/observe/schema-assertions.md) 가이드를 참조하세요.

## Assertions 실행

다음 API를 사용하여 생성한 assertions를 온디맨드로 실행할 수 있습니다. 이는 프로덕션 데이터 파이프라인에서와 같이 사용자 지정 스케줄로 assertions를 실행하는 데 특히 유용합니다.

> **장기 실행 Assertions**: assertion을 동기적으로 실행하는 타임아웃은 현재 최대 30초로 제한됩니다.
> 다음 API들은 모두 `async` 파라미터를 지원하며, `true`로 설정하면 비동기적으로 assertion을 실행할 수 있습니다.
> `true`로 설정하면 API가 assertion 실행을 시작하고 즉시 null을 반환합니다. assertion 결과를 보려면
> `assertion(urn: String!)` GraphQL 쿼리의 `runEvents` 필드를 조회하세요.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

### Assertion 실행

```graphql
mutation runAssertion {
  runAssertion(urn: "urn:li:assertion:your-assertion-id", saveResult: true) {
    type
    nativeResults {
      key
      value
    }
  }
}
```

여기서 **type**은 assertion 실행 결과인 `SUCCESS`, `FAILURE`, 또는 `ERROR` 중 하나를 포함합니다.

`saveResult` 인수는 assertion의 결과가 DataHub 백엔드에 저장되어 DataHub UI를 통해 볼 수 있는지 여부를 결정합니다. `false`로 설정하면 결과가 DataHub 백엔드에 저장되지 않습니다. **기본값: `true`** (지정하지 않으면 결과가 저장됨).

`async` 인수는 assertion이 비동기적으로 실행되는지 여부를 제어합니다. `true`로 설정하면 API가 assertion 실행을 시작하고 즉시 반환합니다. `false`로 설정하거나 생략하면 assertion이 30초 타임아웃으로 동기적으로 실행됩니다. **기본값: `false`** (지정하지 않으면 동기 실행).

assertion이 외부 assertion인 경우(DataHub에서 네이티브로 실행되지 않는 경우) 이 API는 오류를 반환합니다.

assertion 실행이 성공하면 결과가 다음과 같이 반환됩니다:

```json
{
  "data": {
    "runAssertion": {
      "type": "SUCCESS",
      "nativeResults": [
        {
          "key": "Value",
          "value": "1382"
        }
      ]
    }
  },
  "extensions": {}
}
```

### Assertions 그룹 실행

```graphql
mutation runAssertions {
  runAssertions(
    urns: [
      "urn:li:assertion:your-assertion-id-1"
      "urn:li:assertion:your-assertion-id-2"
    ]
    saveResults: true
  ) {
    passingCount
    failingCount
    errorCount
    results {
      urn
      result {
        type
        nativeResults {
          key
          value
        }
      }
    }
  }
}
```

여기서 **type**은 assertion 실행 결과인 `SUCCESS`, `FAILURE`, 또는 `ERROR` 중 하나를 포함합니다.

`saveResults` 인수는 assertion의 결과가 DataHub 백엔드에 저장되어 DataHub UI를 통해 볼 수 있는지 여부를 결정합니다. `false`로 설정하면 결과가 DataHub 백엔드에 저장되지 않습니다. **기본값: `true`** (지정하지 않으면 결과가 저장됨).

`async` 인수는 assertions가 비동기적으로 실행되는지 여부를 제어합니다. `true`로 설정하면 API가 assertion 실행을 시작하고 즉시 반환합니다. `false`로 설정하거나 생략하면 assertions가 assertion당 30초 타임아웃으로 동기적으로 실행됩니다. **기본값: `false`** (지정하지 않으면 동기 실행).

assertion 중 외부 assertion(DataHub에서 네이티브로 실행되지 않는 경우)이 있으면 결과 집합에서 단순히 제외됩니다.

assertions 실행이 성공하면 결과가 다음과 같이 반환됩니다:

```json
{
  "data": {
    "runAssertions": {
      "passingCount": 2,
      "failingCount": 0,
      "errorCount": 0,
      "results": [
        {
          "urn": "urn:li:assertion:your-assertion-id-1",
          "result": {
            "type": "SUCCESS",
            "nativeResults": [
              {
                "key": "Value",
                "value": "1382"
              }
            ]
          }
        },
        {
          "urn": "urn:li:assertion:your-assertion-id-2",
          "result": {
            "type": "FAILURE",
            "nativeResults": [
              {
                "key": "Value",
                "value": "12323"
              }
            ]
          }
        }
      ]
    }
  },
  "extensions": {}
}
```

각 assertion마다 하나의 결과 오브젝트가 표시되어야 합니다.

### 테이블의 모든 Assertions 실행

`runAssertionsForAsset` mutation을 사용하여 특정 데이터 자산에 대한 모든 assertions를 실행할 수도 있습니다.

```graphql
mutation runAssertionsForAsset {
  runAssertionsForAsset(
    urn: "urn:li:dataset:(urn:li:dataPlatform:snowflake,purchase_events,PROD)"
    saveResults: true
  ) {
    passingCount
    failingCount
    errorCount
    results {
      urn
      result {
        type
        nativeResults {
          key
          value
        }
      }
    }
  }
}
```

여기서 `type`은 assertion 실행 결과인 `SUCCESS`, `FAILURE`, 또는 `ERROR` 중 하나를 포함합니다.

`saveResults` 인수는 assertion의 결과가 DataHub 백엔드에 저장되어 DataHub UI를 통해 볼 수 있는지 여부를 결정합니다. `false`로 설정하면 결과가 DataHub 백엔드에 저장되지 않습니다. **기본값: `true`** (지정하지 않으면 결과가 저장됨).

`async` 인수는 assertions가 비동기적으로 실행되는지 여부를 제어합니다. `true`로 설정하면 API가 assertion 실행을 시작하고 즉시 반환합니다. `false`로 설정하거나 생략하면 assertions가 assertion당 30초 타임아웃으로 동기적으로 실행됩니다. **기본값: `false`** (지정하지 않으면 동기 실행).

assertion 중 외부 assertion(DataHub에서 네이티브로 실행되지 않는 경우)이 있으면 결과 집합에서 단순히 제외됩니다.

assertions 실행이 성공하면 결과가 다음과 같이 반환됩니다:

```json
{
  "data": {
    "runAssertionsForAsset": {
      "passingCount": 2,
      "failingCount": 0,
      "errorCount": 0,
      "results": [
        {
          "urn": "urn:li:assertion:your-assertion-id-1",
          "result": {
            "type": "SUCCESS",
            "nativeResults": [
              {
                "key": "Value",
                "value": "1382"
              }
            ]
          }
        },
        {
          "urn": "urn:li:assertion:your-assertion-id-2",
          "result": {
            "type": "FAILURE",
            "nativeResults": [
              {
                "key": "Value",
                "value": "12323"
              }
            ]
          }
        }
      ]
    }
  },
  "extensions": {}
}
```

각 assertion마다 하나의 결과 오브젝트가 표시되어야 합니다.

### 테이블의 Assertions 그룹 실행

주어진 테이블에 대한 _모든_ assertions를 항상 실행하고 싶지 않다면 _Assertion Tags_를 사용하여 테이블 assertions의 하위 집합을 실행할 수도 있습니다. 먼저 assertions에 태그를 추가하여 그룹화하고 분류한 다음, `runAssertionsForAsset` mutation을 `tagUrns` 인수와 함께 호출하여 해당 태그가 있는 assertions만 필터링합니다.

#### 1단계: Assertion에 태그 추가

현재 DataHub GraphQL API를 통해서만 assertion에 태그를 추가할 수 있습니다. 다음 mutation을 사용하면 됩니다:

```graphql
mutation addTags {
  addTag(
    input: {
      resourceUrn: "urn:li:assertion:your-assertion"
      tagUrn: "urn:li:tag:my-important-tag"
    }
  )
}
```

#### 2단계: 태그가 있는 테이블의 모든 Assertions 실행

이제 `runAssertionsForAsset` mutation에 `tagUrns` 입력 파라미터를 사용하여 특정 태그가 있는 테이블의 모든 assertions를 실행할 수 있습니다:

```graphql
mutation runAssertionsForAsset {
  runAssertionsForAsset(
    urn: "urn:li:dataset:(urn:li:dataPlatform:snowflake,purchase_events,PROD)"
    tagUrns: ["urn:li:tag:my-important-tag"]
  ) {
    passingCount
    failingCount
    errorCount
    results {
      urn
      result {
        type
        nativeResults {
          key
          value
        }
      }
    }
  }
}
```

**곧 출시 예정**: DataHub UI를 통해 assertions에 태그를 추가하는 지원 기능.

</TabItem>

<TabItem value="python" label="Python">

### Assertion 실행

```python
{{ inline /metadata-ingestion/examples/library/run_assertion.py show_path_as_comment }}
```

### Assertions 그룹 실행

```python
{{ inline /metadata-ingestion/examples/library/run_assertions.py show_path_as_comment }}
```

### 테이블의 모든 Assertions 실행

```python
{{ inline /metadata-ingestion/examples/library/run_assertions_for_asset.py show_path_as_comment }}
```

</TabItem>

</Tabs>

### Assertions에 동적 파라미터 제공

assertions에 **동적 파라미터**를 제공하여 동작을 사용자 정의할 수 있습니다. 이는 하루 중 시간에 따라 변하는 임계값과 같이 동적 파라미터가 필요한 assertions에 특히 유용합니다.

동적 파라미터는 모든 Assertion의 SQL 단편 부분에 삽입할 수 있습니다. 예를 들어 [Custom SQL](/docs/managed-datahub/observe/custom-sql-assertions.md) Assertion의 SQL 문의 모든 부분이나 [Column](/docs/managed-datahub/observe/column-assertions.md), [Volume](/docs/managed-datahub/observe/volume-assertions.md), 또는 [Freshness](/docs/managed-datahub/observe/freshness-assertions.md) Assertion의 **고급 > 필터** 섹션에 나타날 수 있습니다.

이를 위해 먼저 동적 파라미터를 포함하도록 SQL 단편을 편집해야 합니다. 동적 파라미터는 SQL 단편에서 `${parameterName}` 형식으로 나타납니다.

다음으로 `runAssertion`, `runAssertions`, 또는 `runAssertionsForAsset` mutation을 `parameters` 입력 인수와 함께 호출합니다. 이 인수는 키-값 튜플의 목록으로, 키는 파라미터 이름이고 값은 파라미터 값입니다:

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```graphql
mutation runAssertion {
  runAssertion(
    urn: "urn:li:assertion:your-assertion-id"
    parameters: [{ key: "parameterName", value: "parameterValue" }]
  ) {
    type
    nativeResults {
      key
      value
    }
  }
}
```

</TabItem>

<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/run_assertion_with_parameters.py show_path_as_comment }}
```

</TabItem>

</Tabs>

런타임에 SQL 단편의 `${parameterName}` 플레이스홀더가 제공된 `parameterValue`로 대체된 후 쿼리가 데이터베이스에 실행을 위해 전송됩니다.

## Assertion 상세 정보 조회

다음 API를 사용하여

1. 기존 assertion 정의 + 실행 이력 가져오기
2. 주어진 테이블과 관련된 assertions + 실행 이력 가져오기

를 할 수 있습니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

### 테이블에 대한 Assertions 가져오기

테이블에 대한 모든 assertions를 조회하려면 다음 GraphQL Query를 사용할 수 있습니다.

```graphql
query dataset {
  dataset(
    urn: "urn:li:dataset:(urn:li:dataPlatform:snowflake,purchases,PROD)"
  ) {
    assertions(start: 0, count: 1000) {
      start
      count
      total
      assertions {
        urn
        # 관련된 각 assertion의 마지막 실행을 가져옵니다.
        runEvents(status: COMPLETE, limit: 1) {
          total
          failed
          succeeded
          runEvents {
            timestampMillis
            status
            result {
              type
              nativeResults {
                key
                value
              }
            }
          }
        }
        info {
          type
          description
          lastUpdated {
            time
            actor
          }
          datasetAssertion {
            datasetUrn
            scope
            aggregation
            operator
            parameters {
              value {
                value
                type
              }
              minValue {
                value
                type
              }
              maxValue {
                value
                type
              }
            }
            fields {
              urn
              path
            }
            nativeType
            nativeParameters {
              key
              value
            }
            logic
          }
          freshnessAssertion {
            type
            entityUrn
            schedule {
              type
              cron {
                cron
                timezone
              }
              fixedInterval {
                unit
                multiple
              }
            }
            filter {
              type
              sql
            }
          }
          sqlAssertion {
            type
            entityUrn
            statement
            changeType
            operator
            parameters {
              value {
                value
                type
              }
              minValue {
                value
                type
              }
              maxValue {
                value
                type
              }
            }
          }
          fieldAssertion {
            type
            entityUrn
            filter {
              type
              sql
            }
            fieldValuesAssertion {
              field {
                path
                type
                nativeType
              }
              transform {
                type
              }
              operator
              parameters {
                value {
                  value
                  type
                }
                minValue {
                  value
                  type
                }
                maxValue {
                  value
                  type
                }
              }
              failThreshold {
                type
                value
              }
              excludeNulls
            }
            fieldMetricAssertion {
              field {
                path
                type
                nativeType
              }
              metric
              operator
              parameters {
                value {
                  value
                  type
                }
                minValue {
                  value
                  type
                }
                maxValue {
                  value
                  type
                }
              }
            }
          }
          volumeAssertion {
            type
            entityUrn
            filter {
              type
              sql
            }
            rowCountTotal {
              operator
              parameters {
                value {
                  value
                  type
                }
                minValue {
                  value
                  type
                }
                maxValue {
                  value
                  type
                }
              }
            }
            rowCountChange {
              type
              operator
              parameters {
                value {
                  value
                  type
                }
                minValue {
                  value
                  type
                }
                maxValue {
                  value
                  type
                }
              }
            }
          }
          schemaAssertion {
            entityUrn
            compatibility
            fields {
              path
              type
              nativeType
            }
            schema {
              fields {
                fieldPath
                type
                nativeDataType
              }
            }
          }
          source {
            type
            created {
              time
              actor
            }
          }
        }
      }
    }
  }
}
```

### Assertion 상세 정보 가져오기

다음 GraphQL 쿼리를 사용하여 URN으로 assertion의 상세 정보와 평가 이력을 가져올 수 있습니다.

```graphql
query getAssertion {
  assertion(urn: "urn:li:assertion:assertion-id") {
    urn
    # assertion에 대한 마지막 10개의 실행을 가져옵니다.
    runEvents(status: COMPLETE, limit: 10) {
      total
      failed
      succeeded
      runEvents {
        timestampMillis
        status
        result {
          type
          nativeResults {
            key
            value
          }
        }
      }
    }
    info {
      type
      description
      lastUpdated {
        time
        actor
      }
      datasetAssertion {
        datasetUrn
        scope
        aggregation
        operator
        parameters {
          value {
            value
            type
          }
          minValue {
            value
            type
          }
          maxValue {
            value
            type
          }
        }
        fields {
          urn
          path
        }
        nativeType
        nativeParameters {
          key
          value
        }
        logic
      }
      freshnessAssertion {
        type
        entityUrn
        schedule {
          type
          cron {
            cron
            timezone
          }
          fixedInterval {
            unit
            multiple
          }
        }
        filter {
          type
          sql
        }
      }
      sqlAssertion {
        type
        entityUrn
        statement
        changeType
        operator
        parameters {
          value {
            value
            type
          }
          minValue {
            value
            type
          }
          maxValue {
            value
            type
          }
        }
      }
      fieldAssertion {
        type
        entityUrn
        filter {
          type
          sql
        }
        fieldValuesAssertion {
          field {
            path
            type
            nativeType
          }
          transform {
            type
          }
          operator
          parameters {
            value {
              value
              type
            }
            minValue {
              value
              type
            }
            maxValue {
              value
              type
            }
          }
          failThreshold {
            type
            value
          }
          excludeNulls
        }
        fieldMetricAssertion {
          field {
            path
            type
            nativeType
          }
          metric
          operator
          parameters {
            value {
              value
              type
            }
            minValue {
              value
              type
            }
            maxValue {
              value
              type
            }
          }
        }
      }
      volumeAssertion {
        type
        entityUrn
        filter {
          type
          sql
        }
        rowCountTotal {
          operator
          parameters {
            value {
              value
              type
            }
            minValue {
              value
              type
            }
            maxValue {
              value
              type
            }
          }
        }
        rowCountChange {
          type
          operator
          parameters {
            value {
              value
              type
            }
            minValue {
              value
              type
            }
            maxValue {
              value
              type
            }
          }
        }
      }
      schemaAssertion {
        entityUrn
        compatibility
        fields {
          path
          type
          nativeType
        }
        schema {
          fields {
            fieldPath
            type
            nativeDataType
          }
        }
      }
      source {
        type
        created {
          time
          actor
        }
      }
    }
  }
}
```

</TabItem>

<TabItem value="python" label="Python">

```python
Python support coming soon!
```

</TabItem>
</Tabs>

## Assertion에 태그 추가

개별 assertions에 태그를 추가하여 우선순위나 심각도 등으로 그룹화하고 분류할 수 있습니다.
태그가 DataHub에 이미 존재해야 하며, 그렇지 않으면 작업이 실패합니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```graphql
mutation addTags {
  addTag(
    input: {
      resourceUrn: "urn:li:assertion:your-assertion"
      tagUrn: "urn:li:tag:my-important-tag"
    }
  )
}
```

다음 응답이 표시되면 작업이 성공한 것입니다:

```json
{
  "data": {
    "addTag": true
  },
  "extensions": {}
}
```

`createTag` mutation 또는 UI를 통해 새 태그를 생성할 수 있습니다.

</TabItem>
</Tabs>

## Assertions 삭제

다음 API를 사용하여 DataHub의 dataset 삭제 작업을 수행할 수 있습니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```graphql
mutation deleteAssertion {
  deleteAssertion(urn: "urn:li:assertion:test")
}
```

다음 응답이 표시되면 작업이 성공한 것입니다:

```json
{
  "data": {
    "deleteAssertion": true
  },
  "extensions": {}
}
```

</TabItem>

<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/assertion_delete.py show_path_as_comment }}
```

</TabItem>
</Tabs>

## (고급) Custom Assertions 생성 및 결과 보고

DataHub Cloud 외부에서 실행 및 평가되는 자체 custom assertions를 생성하고 결과를 보고하려면 2개의 중요한 Assertion Entity aspect를 생성하고 assertion에 다음 형식의 고유 URN을 부여해야 합니다:

1. assertion에 대한 고유 URN 생성

```plaintext
urn:li:assertion:<unique-assertion-id>
```

2. assertion에 대한 [**AssertionInfo**](/docs/generated/metamodel/entities/assertion.md#assertion-info) aspect를 생성합니다. Python SDK를 사용하여 이를 수행할 수 있습니다. assertion에 `type`과 DataHub 자체가 실행하는 것이 아닌 외부 assertion임을 표시하는 `EXTERNAL` 유형의 `source`를 지정하세요.

3. Python SDK를 사용하여 [**AssertionRunEvent**](/docs/generated/metamodel/entities/assertion.md#assertionrunevent-timeseries) 타임시리즈 aspect를 생성합니다. 이 aspect는 주어진 타임스탬프에서의 assertion 실행 결과를 포함해야 하며 DataHub UI의 결과 그래프에 표시됩니다.

## 구독 생성 및 제거

Dataset 또는 Assertions에 대한 구독을 생성하고 제거하는 방법은 [Subscriptions SDK](/docs/api/tutorials/subscriptions.md)를 참조하세요.
