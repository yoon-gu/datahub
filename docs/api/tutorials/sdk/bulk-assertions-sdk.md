import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Python SDK로 Smart Assertions 대량 생성

<FeatureAvailability saasOnly />

이 가이드는 [DataHub Cloud Python SDK](https://pypi.org/project/acryl-datahub-cloud/)를 사용하여 **smart assertions를 대량 생성**하는 방법을 구체적으로 다룹니다:

- Smart Freshness Assertions
- Smart Volume Assertions
- Smart Column Metric Assertions
- Smart SQL Assertions

이는 대규모로 많은 테이블과 컬럼에 데이터 품질 검사를 적용하는 데 특히 유용합니다.

## Assertion 대량 생성을 사용하는 이유

Python SDK로 assertions를 대량 생성하면 다음이 가능합니다:

- **데이터 품질 확장**: 수백 또는 수천 개의 테이블에 일관된 assertions 적용
- **assertion 관리 자동화**: 메타데이터 패턴을 기반으로 assertions를 프로그래밍 방식으로 생성 및 업데이트
- **거버넌스 정책 구현**: 모든 중요 테이블에 적절한 데이터 품질 검사 보장
- **시간 절약**: UI에서 하나씩 수동으로 assertions를 생성하는 번거로움 없애기

## 사전 요구 사항

다음이 필요합니다:

- DataHub Cloud Python SDK 설치 (`pip install acryl-datahub-cloud`)
- 유효한 DataHub Cloud 자격 증명 구성 (서버 URL 및 적절한 권한을 가진 액세스 토큰)

API 호출을 수행하는 액터는 해당 dataset에 대해 `Edit Assertions` 및 `Edit Monitors` 권한이 있어야 합니다.

:::note
assertions를 생성하기 전에 대상 dataset이 DataHub 인스턴스에 이미 존재하는지 확인해야 합니다.
존재하지 않는 entities에 대해 assertions를 생성하려고 하면 GMS가 로그에 오류를 계속 보고합니다.
:::

### 이 가이드의 목표

이 가이드에서는 DataHub Cloud Python SDK를 사용하여 대량의 smart assertions를 프로그래밍 방식으로 생성하는 방법을 보여줍니다.

## 개요

assertion 대량 생성 프로세스는 다음 단계를 따릅니다:

1. **테이블 탐색**: 검색 또는 직접 테이블 쿼리를 사용하여 dataset 찾기
2. **테이블 수준 assertions 생성**: 각 테이블에 freshness 및 volume assertions 추가
3. **컬럼 정보 가져오기**: 각 테이블의 schema 세부 정보 조회
4. **컬럼 수준 assertions 생성**: 각 관련 컬럼에 column metric assertions 추가
5. **assertion URN 저장**: 향후 업데이트를 위해 assertion 식별자 저장

## 설정

DataHub 인스턴스에 연결하세요:

```python
from datahub.sdk import DataHubClient

client = DataHubClient(server="<your_server>", token="<your_token>")
```

- **server**: DataHub GMS 서버의 URL
  - 로컬: `http://localhost:8080`
  - 호스팅: `https://<your_datahub_url>/gms`
- **token**: DataHub 인스턴스에서 [Personal Access Token을 생성](../../../authentication/personal-access-tokens.md)해야 합니다.

또는 `DATAHUB_GMS_URL` 및 `DATAHUB_GMS_TOKEN` 환경 변수를 설정하거나 `datahub init` 실행을 통해 `~/.datahubenv` 파일을 생성한 후 `from_env()` 메서드를 사용하여 초기화할 수 있습니다.

```python
from datahub.sdk import DataHubClient

client = DataHubClient.from_env()
```

## 병렬 처리에 대한 중요 고려 사항

- 경쟁 조건을 방지하기 위해 주어진 dataset에 대한 assertion 대량 생성은 항상 단일 스레드에서 실행하세요.
- 경쟁 조건을 방지하기 위해 주어진 dataset에 대한 구독 API는 항상 단일 스레드에서 호출하세요.
  - assertions에 직접 구독하는 경우 스크립트를 dataset당 단일 스레드에서 실행하세요.

## 1단계: 테이블 탐색

### 옵션 A: 특정 테이블 가져오기

```python
from datahub.metadata.urns import DatasetUrn

# assertions를 추가할 특정 테이블 정의
table_urns = [
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.users,PROD)",
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.orders,PROD)",
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.products,PROD)",
]

# DatasetUrn 오브젝트로 변환
datasets = [DatasetUrn.from_string(urn) for urn in table_urns]
```

### 옵션 B: 패턴으로 테이블 검색

포괄적인 검색 기능 및 필터 옵션은 [Search API 문서](../sdk/search_client.md)를 참조하세요.

```python
from datahub.sdk.search_filters import FilterDsl
from datahub.metadata.urns import DatasetUrn

# 기준에 맞는 테이블 검색
def find_tables_by_pattern(client, platform="snowflake", name_pattern="production_*"):
    """특정 패턴과 일치하는 테이블을 찾습니다."""
    # 특정 플랫폼에서 이름 패턴을 가진 dataset에 대한 필터 생성
    filters = FilterDsl.and_(
        FilterDsl.entity_type("dataset"),
        FilterDsl.platform(platform),
        FilterDsl.custom_filter("name", "EQUAL", [name_pattern])
    )

    # 검색 클라이언트를 사용하여 일치하는 dataset 찾기
    urns = list(client.search.get_urns(filter=filters))
    return [DatasetUrn.from_string(str(urn)) for urn in urns]

# 검색 함수 사용
datasets = find_tables_by_pattern(client, platform="snowflake", name_pattern="production_*")
```

### 옵션 C: 태그 또는 도메인으로 테이블 가져오기

```python
def find_tables_by_tag(client, tag_name="critical"):
    """특정 태그가 있는 테이블을 찾습니다."""
    # 특정 태그가 있는 dataset에 대한 필터 생성
    filters = FilterDsl.and_(
        FilterDsl.entity_type("dataset"),
        FilterDsl.custom_filter("tags", "EQUAL", [f"urn:li:tag:{tag_name}"])
    )

    # 검색 클라이언트를 사용하여 일치하는 dataset 찾기
    urns = list(client.search.get_urns(filter=filters))
    return [DatasetUrn.from_string(str(urn)) for urn in urns]

# "critical"로 태그된 모든 테이블 찾기
critical_datasets = find_tables_by_tag(client, "critical")
```

## 2단계: 테이블 수준 Assertions 생성

### Smart Freshness Assertions

```python
# assertion URN 저장소 (이후 업데이트용)
assertion_registry = {
    "freshness": {},
    "volume": {},
    "smart_sql": {},
    "column_metrics": {}
}

def create_freshness_assertions(datasets, client, registry):
    """여러 dataset에 대한 smart freshness assertions를 생성합니다."""

    for dataset_urn in datasets:
        try:
            # smart freshness assertion 생성
            freshness_assertion = client.assertions.sync_smart_freshness_assertion(
                dataset_urn=dataset_urn,
                display_name=f"Freshness Anomaly Monitor",
                # 감지 메커니즘 - information_schema 권장
                detection_mechanism="information_schema",
                # Smart 민감도 설정
                sensitivity="medium",  # 옵션: "low", "medium", "high"
                # 그룹화를 위한 태그 (URN 또는 일반 태그 이름 지원!)
                tags=["automated", "freshness", "data_quality"],
                # assertion 활성화
                enabled=True
            )

            # 향후 참조를 위해 assertion URN 저장
            registry["freshness"][str(dataset_urn)] = str(freshness_assertion.urn)

            print(f"✅ Created freshness assertion for {dataset_urn.name}: {freshness_assertion.urn}")

        except Exception as e:
            print(f"❌ Failed to create freshness assertion for {dataset_urn.name}: {e}")

# 모든 dataset에 대한 freshness assertions 생성
create_freshness_assertions(datasets, client, assertion_registry)
```

### Smart Volume Assertions

```python
def create_volume_assertions(datasets, client, registry):
    """여러 dataset에 대한 smart volume assertions를 생성합니다."""

    for dataset_urn in datasets:
        try:
            # smart volume assertion 생성
            volume_assertion = client.assertions.sync_smart_volume_assertion(
                dataset_urn=dataset_urn,
                display_name=f"Smart Volume Check",
                # 감지 메커니즘 옵션
                detection_mechanism="information_schema",
                # Smart 민감도 설정
                sensitivity="medium",
                # 그룹화를 위한 태그
                tags=["automated", "volume", "data_quality"],
                # 스케줄 (선택 사항 - 기본값은 매시간)
                schedule="0 */6 * * *",  # 6시간마다
                # assertion 활성화
                enabled=True
            )

            # assertion URN 저장
            registry["volume"][str(dataset_urn)] = str(volume_assertion.urn)

            print(f"✅ Created volume assertion for {dataset_urn.name}: {volume_assertion.urn}")

        except Exception as e:
            print(f"❌ Failed to create volume assertion for {dataset_urn.name}: {e}")

# 모든 dataset에 대한 volume assertions 생성
create_volume_assertions(datasets, client, assertion_registry)
```

### Smart SQL Assertions

```python
def create_smart_sql_assertions(datasets, client, registry):
    """여러 dataset에 대한 smart SQL assertions를 생성합니다."""

    # 각 테이블에서 실행할 SQL 쿼리 정의
    sql_queries = {
        "row_count": "SELECT COUNT(*) FROM {table_name}",
        "null_check": "SELECT COUNT(*) FROM {table_name} WHERE id IS NULL",
        "active_records": "SELECT COUNT(*) FROM {table_name} WHERE status = 'active'",
    }

    for dataset_urn in datasets:
        registry["smart_sql"][str(dataset_urn)] = {}

        for query_name, query_template in sql_queries.items():
            try:
                # 테이블 이름으로 쿼리 구성
                table_name = dataset_urn.name
                statement = query_template.format(table_name=table_name)

                # smart SQL assertion 생성
                sql_assertion = client.assertions.sync_smart_sql_assertion(
                    dataset_urn=dataset_urn,
                    display_name=f"Smart SQL - {query_name}",
                    statement=statement,
                    # AI 기반 민감도 설정
                    sensitivity="medium",  # 옵션: "low", "medium", "high"
                    # 그룹화를 위한 태그
                    tags=["automated", "smart_sql", query_name],
                    # 스케줄
                    schedule="0 */6 * * *",  # 6시간마다
                    # assertion 활성화
                    enabled=True
                )

                # assertion URN 저장
                registry["smart_sql"][str(dataset_urn)][query_name] = str(sql_assertion.urn)

                print(f"✅ Created smart SQL assertion '{query_name}' for {dataset_urn.name}: {sql_assertion.urn}")

            except Exception as e:
                print(f"❌ Failed to create smart SQL assertion '{query_name}' for {dataset_urn.name}: {e}")

# 모든 dataset에 대한 smart SQL assertions 생성
create_smart_sql_assertions(datasets, client, assertion_registry)
```

## 3단계: 컬럼 정보 가져오기

```python
def get_dataset_columns(client, dataset_urn):
    """dataset의 컬럼 정보를 가져옵니다."""
    try:
        # entities 클라이언트를 사용하여 dataset 가져오기
        dataset = client.entities.get(dataset_urn)
        if dataset and hasattr(dataset, 'schema') and dataset.schema:
            return [
                {
                    "name": field.field_path,
                    "type": field.native_data_type,
                    "nullable": field.nullable if hasattr(field, 'nullable') else True
                }
                for field in dataset.schema.fields
            ]
        return []
    except Exception as e:
        print(f"❌ Failed to get columns for {dataset_urn}: {e}")
        return []

# 각 dataset의 컬럼 가져오기
dataset_columns = {}
for dataset_urn in datasets:
    columns = get_dataset_columns(client, dataset_urn)
    dataset_columns[str(dataset_urn)] = columns
    print(f"📊 Found {len(columns)} columns in {dataset_urn.name}")
```

## 4단계: 컬럼 수준 Assertions 생성

### Smart Column Metric Assertions

```python
def create_column_assertions(datasets, columns_dict, client, registry):
    """여러 dataset 및 컬럼에 대한 smart column metric assertions를 생성합니다."""

    # 어떤 컬럼에 어떤 assertions를 적용할지에 대한 규칙 정의
    assertion_rules = {
        # 중요 컬럼에 대한 null count 검사
        "null_checks": {
            "column_patterns": ["id", "*_id", "user_id", "email"],
            "metric_type": "null_count",
        },
        # ID 컬럼에 대한 unique count 검사
        "unique_checks": {
            "column_patterns": ["*_id", "email", "username"],
            "metric_type": "unique_count",
        },
        # 문자열 컬럼에 대한 empty count 검사
        "empty_checks": {
            "column_patterns": ["name", "description", "title"],
            "metric_type": "empty_count",
        },
    }

    for dataset_urn in datasets:
        dataset_key = str(dataset_urn)
        columns = columns_dict.get(dataset_key, [])

        if not columns:
            print(f"⚠️ No columns found for {dataset_urn.name}")
            continue

        registry["column_metrics"][dataset_key] = {}

        for column in columns:
            column_name = column["name"]
            column_type = column["type"].upper()

            # 컬럼 이름 및 유형을 기반으로 assertion 규칙 적용
            for rule_name, rule_config in assertion_rules.items():
                if should_apply_rule(column_name, column_type, rule_config):
                    try:
                        assertion = client.assertions.sync_smart_column_metric_assertion(
                            dataset_urn=dataset_urn,
                            column_name=column_name,
                            metric_type=rule_config["metric_type"],
                            display_name=f"{rule_name.replace('_', ' ').title()} - {column_name}",
                            # 컬럼 메트릭을 위한 감지 메커니즘
                            detection_mechanism="all_rows_query_datahub_dataset_profile",
                            # 태그 (일반 이름은 자동으로 URN으로 변환됨)
                            tags=["automated", "column_quality", rule_name],
                            enabled=True
                        )

                        # assertion URN 저장
                        if column_name not in registry["column_metrics"][dataset_key]:
                            registry["column_metrics"][dataset_key][column_name] = {}
                        registry["column_metrics"][dataset_key][column_name][rule_name] = str(assertion.urn)

                        print(f"✅ Created {rule_name} assertion for {dataset_urn.name}.{column_name}")

                    except Exception as e:
                        print(f"❌ Failed to create {rule_name} assertion for {dataset_urn.name}.{column_name}: {e}")

def should_apply_rule(column_name, column_type, rule_config):
    """컬럼에 규칙을 적용할지 결정합니다."""
    import fnmatch

    # 컬럼 이름 패턴 확인
    for pattern in rule_config["column_patterns"]:
        if fnmatch.fnmatch(column_name.lower(), pattern.lower()):
            return True

    # 필요한 경우 유형 기반 규칙 추가
    if rule_config.get("column_types"):
        return any(col_type in column_type for col_type in rule_config["column_types"])

    return False

# 컬럼 assertions 생성
create_column_assertions(datasets, dataset_columns, client, assertion_registry)
```

## 5단계: 구독 생성

dataset 또는 assertions에 대한 구독을 생성하는 방법은 [Subscriptions SDK](/docs/api/tutorials/subscriptions.md)를 참조하세요.

:::note
대량으로 구독을 생성할 때는 경쟁 조건을 방지하기 위해 단일 스레드에서 작업을 수행해야 합니다. 또한 개별 assertions가 아닌 dataset 수준에서 구독을 생성하는 것을 권장합니다. 이렇게 하면 지속적인 관리가 훨씬 쉬워집니다.
:::

## 6단계: Assertion URN 저장

### 파일로 저장

```python
import json
from datetime import datetime

def save_assertion_registry(registry, filename=None):
    """향후 참조를 위해 assertion URN을 파일로 저장합니다."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"assertion_registry_{timestamp}.json"

    # 메타데이터 추가
    registry_with_metadata = {
        "created_at": datetime.now().isoformat(),
        "total_assertions": {
            "freshness": len(registry["freshness"]),
            "volume": len(registry["volume"]),
            "column_metrics": sum(
                len(cols) for cols in registry["column_metrics"].values()
            )
        },
        "assertions": registry
    }

    with open(filename, 'w') as f:
        json.dump(registry_with_metadata, f, indent=2)

    print(f"💾 Saved assertion registry to {filename}")
    return filename

# 레지스트리 저장
registry_file = save_assertion_registry(assertion_registry)
```

### 파일에서 로드 (업데이트용)

```python
def load_assertion_registry(filename):
    """이전에 저장된 파일에서 assertion URN을 로드합니다."""
    with open(filename, 'r') as f:
        data = json.load(f)
    return data["assertions"]

# 나중에 업데이트를 위해 로드
# assertion_registry = load_assertion_registry("assertion_registry_20240101_120000.json")
```

## 7단계: 기존 Assertions 업데이트

```python
def update_existing_assertions(registry, client):
    """저장된 URN을 사용하여 기존 assertions를 업데이트합니다."""

    # freshness assertions 업데이트
    for dataset_urn, assertion_urn in registry["freshness"].items():
        try:
            updated_assertion = client.assertions.sync_smart_freshness_assertion(
                dataset_urn=dataset_urn,
                urn=assertion_urn,  # 업데이트를 위해 기존 URN 제공
                # 필요에 따라 파라미터 업데이트
                sensitivity="high",  # 민감도 변경
                tags=["automated", "freshness", "data_quality", "updated"],
                enabled=True
            )
            print(f"🔄 Updated freshness assertion {assertion_urn}")
        except Exception as e:
            print(f"❌ Failed to update freshness assertion {assertion_urn}: {e}")

# 필요 시 assertions 업데이트
# update_existing_assertions(assertion_registry, client)
```

## 고급 패턴

### 조건부 Assertion 생성

```python
def create_conditional_assertions(datasets, client):
    """dataset 메타데이터 조건을 기반으로 assertions를 생성합니다."""

    for dataset_urn in datasets:
        try:
            # dataset 메타데이터 가져오기
            dataset = client.entities.get(dataset_urn)

            # dataset에 특정 태그가 있는지 확인
            if dataset.tags and any("critical" in str(tag.tag) for tag in dataset.tags):
                # 중요 dataset에 더 엄격한 assertions 생성
                client.assertions.sync_smart_freshness_assertion(
                    dataset_urn=dataset_urn,
                    sensitivity="high",
                    detection_mechanism="information_schema",
                    tags=["critical", "automated", "freshness"]
                )

            # dataset 크기 확인 및 적절한 volume 검사 적용
            if dataset.dataset_properties:
                # 테이블 특성에 따라 다른 volume assertions 생성
                pass

        except Exception as e:
            print(f"❌ Error processing {dataset_urn}: {e}")
```

### 오류 처리를 포함한 배치 처리

```python
import time
from typing import List, Dict, Any

def batch_create_assertions(
    datasets: List[DatasetUrn],
    client: DataHubClient,
    batch_size: int = 10,
    delay_seconds: float = 1.0
) -> Dict[str, Any]:
    """오류 처리 및 속도 제한을 포함하여 배치 단위로 assertions를 생성합니다."""

    results = {
        "successful": [],
        "failed": [],
        "total_processed": 0
    }

    for i in range(0, len(datasets), batch_size):
        batch = datasets[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}: {len(batch)} datasets")

        for dataset_urn in batch:
            try:
                # assertion 생성
                assertion = client.assertions.sync_smart_freshness_assertion(
                    dataset_urn=dataset_urn,
                    tags=["batch_created", "automated"],
                    enabled=True
                )
                results["successful"].append({
                    "dataset_urn": str(dataset_urn),
                    "assertion_urn": str(assertion.urn)
                })

            except Exception as e:
                results["failed"].append({
                    "dataset_urn": str(dataset_urn),
                    "error": str(e)
                })

            results["total_processed"] += 1

        # 배치 간 속도 제한
        if i + batch_size < len(datasets):
            time.sleep(delay_seconds)

    return results

# 배치 처리 사용
batch_results = batch_create_assertions(datasets, client, batch_size=5)
print(f"Batch results: {batch_results['total_processed']} processed, "
      f"{len(batch_results['successful'])} successful, "
      f"{len(batch_results['failed'])} failed")
```

## 모범 사례

### 1. **태그 전략**

- assertions 그룹화를 위한 일관된 태그 이름 사용: `["automated", "freshness", "critical"]`
- 일반 태그 이름은 자동으로 URN으로 변환됨: `"my_tag"` → `"urn:li:tag:my_tag"`
- 다양한 assertion 유형 및 우선순위에 대한 태그 계층 생성

### 2. **오류 처리**

- 항상 assertion 생성을 try-catch 블록으로 감싸기
- 나중에 조사할 수 있도록 실패 로그 기록
- 일시적인 오류에 대한 재시도 로직 구현

### 3. **URN 관리**

- assertion URN을 영구 저장소(파일, 데이터베이스 등)에 저장
- 타임스탬프가 포함된 의미 있는 파일 이름 사용
- assertions가 언제, 왜 생성되었는지에 대한 메타데이터 포함

### 4. **성능 고려 사항**

백엔드는 대규모 작업을 처리하도록 설계되었습니다. 그러나 쓰기 작업은 Kafka 큐에 비동기적으로 제출되므로 작업 적용에 상당한 지연이 발생할 수 있습니다. 문제가 발생하면 다음 팁이 도움이 될 수 있습니다:

- **대규모 대량 작업의 경우 비수요 시간에 실행**하여 Kafka 지연 스파이크 방지
- **재실행 동기화 전** (즉, 업데이트를 위해) GMS가 이전 실행 처리를 완료할 때까지 기다려 불일치 및 중복 방지: 마지막으로 수집된 항목이 GMS에 반영되었는지 확인
- DataHub UI 또는 API를 통해 **처리 상태를 모니터링**하여 작업이 성공적으로 완료되는지 확인
- API 과부하를 방지하기 위해 **dataset를 배치 단위로 처리**
- 필요한 경우 배치 처리 사이에 **지연 추가**

### 5. **테스트 전략**

- 테스트를 위해 소규모 dataset 하위 집합으로 시작
- 대량 처리 전에 assertion 생성 유효성 검사
- 기존 assertions로 업데이트 시나리오 테스트

## 완성된 예제 스크립트

```python
#!/usr/bin/env python3
"""
smart assertions를 대량 생성하는 완성된 예제 스크립트.
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any

from datahub.sdk import DataHubClient
from datahub.ingestion.graph.client import DataHubGraph
from datahub.metadata.urns import DatasetUrn

def main():
    # DataHub 클라이언트 초기화
    client = DataHubClient(
        server="https://your-datahub-instance.com",
        token="your-access-token",
    )

    # 클라이언트는 검색 및 entity 액세스 모두 제공

    # 대상 dataset 정의
    table_urns = [
        "urn:li:dataset:(urn:li:dataPlatform:snowflake,prod.analytics.users,PROD)",
        "urn:li:dataset:(urn:li:dataPlatform:snowflake,prod.analytics.orders,PROD)",
        "urn:li:dataset:(urn:li:dataPlatform:snowflake,prod.analytics.products,PROD)",
    ]

    datasets = [DatasetUrn.from_string(urn) for urn in table_urns]

    # assertion URN 저장을 위한 레지스트리
    assertion_registry = {
        "freshness": {},
        "volume": {},
        "column_metrics": {}
    }

    print(f"🚀 Starting bulk assertion creation for {len(datasets)} datasets")

    # 1단계: 테이블 수준 assertions 생성
    print("\n📋 Creating freshness assertions...")
    create_freshness_assertions(datasets, client, assertion_registry)

    print("\n📊 Creating volume assertions...")
    create_volume_assertions(datasets, client, assertion_registry)

    # 2단계: 컬럼 정보 가져오기 및 컬럼 assertions 생성
    print("\n🔍 Analyzing columns and creating column assertions...")
    dataset_columns = {}
    for dataset_urn in datasets:
        columns = get_dataset_columns(client, dataset_urn)
        dataset_columns[str(dataset_urn)] = columns

    create_column_assertions(datasets, dataset_columns, client, assertion_registry)

    # 3단계: 결과 저장
    print("\n💾 Saving assertion registry...")
    registry_file = save_assertion_registry(assertion_registry)

    # 요약
    total_assertions = (
        len(assertion_registry["freshness"]) +
        len(assertion_registry["volume"]) +
        sum(len(cols) for cols in assertion_registry["column_metrics"].values())
    )

    print(f"\n✅ Bulk assertion creation complete!")
    print(f"   📈 Total assertions created: {total_assertions}")
    print(f"   🕐 Freshness assertions: {len(assertion_registry['freshness'])}")
    print(f"   📊 Volume assertions: {len(assertion_registry['volume'])}")
    print(f"   🎯 Column assertions: {sum(len(cols) for cols in assertion_registry['column_metrics'].values())}")
    print(f"   💾 Registry saved to: {registry_file}")

if __name__ == "__main__":
    main()
```

이 가이드는 DataHub Cloud Python SDK를 사용하여 smart assertions를 대량 생성하는 포괄적인 접근 방식을 제공합니다. 새로운 태그 이름 자동 변환 기능을 통해 간단하고 읽기 쉬운 태그 이름으로 assertions를 더 쉽게 구성하고 관리할 수 있으며, 이 이름은 자동으로 적절한 URN 형식으로 변환됩니다.
