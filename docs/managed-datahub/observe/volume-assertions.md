---
description: 이 페이지에서는 DataHub Volume Assertions 사용 방법에 대한 개요를 제공합니다
---

import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Volume Assertions

<FeatureAvailability saasOnly />

> **Volume Assertions** 기능은 DataHub Cloud의 **DataHub Cloud Observe** 모듈의 일부로 제공됩니다.
> **DataHub Cloud Observe**에 대해 더 알아보거나 체험해 보고 싶다면 [웹사이트를 방문](https://datahub.com/products/data-observability/)하세요.

## 소개

의존하는 데이터 웨어하우스 테이블의 의미가 예고도 없이 근본적으로 바뀐 경험이 있으신가요?
그렇다면 어떻게 알게 되셨나요? 내부 보고 대시보드를 보던 누군가가, 또는 더 심하게는 제품을 사용하는 사용자가 수치가 이상해 보인다며 경보를 울렸을 것입니다. 예를 들어, 처음에는 회사 이커머스 웹 스토어의 구매 내역을 추적하던 테이블에 갑자기 회사의 새 모바일 앱을 통한 구매도 포함되기 시작했을 수 있습니다.

Snowflake, Redshift, BigQuery, Databricks의 중요한 테이블이 의미 면에서 변경되는 이유는 다양합니다 - 애플리케이션 코드 버그, 새 기능 출시, 핵심 지표 정의 변경 등. 이러한 변경은 종종 보고 대시보드나 데이터 기반 제품 기능과 같은 주요 다운스트림 데이터 제품 구축에 사용되는 데이터에 대한 중요한 가정을 깨뜨립니다.

데이터 담당자가 다른 누구보다 먼저 데이터 문제를 인식할 수 있도록 인시던트 감지 시간을 단축할 수 있다면 어떨까요? DataHub Cloud **Volume Assertions**를 통해 이것이 가능합니다.

DataHub Cloud를 통해 사용자는 특정 웨어하우스 테이블의 정상 volume 또는 크기에 대한 기대치를 정의하고, 테이블이 성장하고 변화함에 따라 시간이 지나도 해당 기대치를 모니터링할 수 있습니다.

이 문서에서는 Volume Assertions 모니터링의 기본 사항(정의, 구성 방법 등)을 다루어 팀이 중요한 데이터 자산에 대한 신뢰를 구축할 수 있도록 돕겠습니다.

시작해 봅시다!

## 지원 현황

Volume Assertions는 현재 다음을 지원합니다:

1. Snowflake
2. Redshift
3. BigQuery
4. Databricks
5. DataHub Dataset Profile (수집을 통해 수집됨)

DataHub Cloud의 **Ingestion** 탭에서 선택한 데이터 플랫폼에 대한 수집 소스가 _반드시_ 구성되어 있어야 합니다.

> DataHub CLI를 사용하여 웨어하우스에 연결하는 경우 Volume Assertions는 아직 지원되지 않습니다.

## Volume Assertion이란?

**Volume Assertion**은 데이터 웨어하우스 테이블의 "volume"(행 수)에서 예상치 못한 또는 갑작스러운 변화를 모니터링하는 데 사용되는 구성 가능한 데이터 품질 규칙입니다. Volume Assertions는 특히 성장 또는 감소 패턴이 비교적 안정적인 자주 변경되는 테이블에 유용합니다.

예를 들어, 이커머스 웹사이트에서 수집된 사용자 클릭을 저장하는 Snowflake 테이블이 있다고 가정해 봅시다. 이 테이블은 특정 주기(시간당 1회)로 새 데이터로 업데이트됩니다. 그리고 이 "클릭" 테이블에 저장된 데이터를 기반으로 생성된 Looker의 비즈니스 분석 대시보드가 "일일 세일" 배너 클릭 수와 같은 중요한 지표를 보여줍니다. 클릭 테이블이 매시간 올바른 수의 행으로 업데이트되는 것이 중요한데, 그렇지 않으면 다운스트림 지표 대시보드가 부정확해질 수 있습니다. 이러한 상황의 위험은 명확합니다: 조직이 불완전한 정보에 기반하여 잘못된 결정을 내릴 수 있습니다.

이런 경우, Snowflake "클릭" 테이블이 예상대로 성장하고 있는지, 테이블에 추가되거나 제거되는 행에 갑작스러운 증가나 감소가 없는지 확인하는 **Volume Assertion**을 사용할 수 있습니다. 한 시간 내에 너무 많은 행이 추가되거나 제거되면 주요 이해관계자에게 알리고 데이터 이해관계자에게 영향을 미치기 전에 근본 원인을 파악할 수 있습니다.

### Volume Assertion의 구조

**Volume Assertions**는 기본적으로 몇 가지 중요한 구성 요소로 이루어집니다:

1. **평가 스케줄**
2. **Volume 조건**
3. **Volume 소스**

이 섹션에서 각각에 대한 개요를 설명합니다.

#### 1. 평가 스케줄

**평가 스케줄**: 지정된 웨어하우스 테이블의 volume을 확인하는 빈도를 정의합니다. 일반적으로 테이블의 예상 변경 빈도에 맞게 구성해야 하지만, 요구 사항에 따라 더 낮은 빈도로 설정할 수도 있습니다. 주의 특정 요일, 시간 내의 특정 시, 또는 시간 내의 특정 분을 지정할 수도 있습니다.

#### 2. Volume 조건

**Volume 조건**: 모니터링하려는 조건의 유형, 즉 Assertion이 실패해야 하는 경우를 정의합니다.

조건에는 **총 Volume** 및 **변경 Volume**의 2가지 범주가 있습니다.

_총_ volume 조건은 테이블의 특정 시점 총 행 수에 대해 정의됩니다. 다음과 같은 조건을 지정할 수 있습니다:

1. **테이블 행이 너무 많음**: 테이블은 항상 1000행 미만이어야 합니다
2. **테이블 행이 너무 적음**: 테이블은 항상 1000행 이상이어야 합니다
3. **테이블 행 수가 범위를 벗어남**: 테이블은 항상 1000에서 2000행 사이여야 합니다.

_변경_ volume 조건은 테이블 volume의 연속적인 검사 사이에 측정된 성장 또는 감소율에 대해 정의됩니다. 다음과 같은 조건을 지정할 수 있습니다:

1. **테이블 성장이 너무 빠름**: 테이블 volume을 확인할 때 이전 검사 시보다 1000행 미만으로 더 많아야 합니다.
2. **테이블 성장이 너무 느림**: 테이블 volume을 확인할 때 이전 검사 시보다 1000행 이상으로 더 많아야 합니다.
3. **테이블 성장이 범위를 벗어남**: 테이블 volume을 확인할 때 이전 검사 시보다 1000에서 2000행 사이로 더 많아야 합니다.

변경 volume 조건의 경우, 비정상적인 성장 패턴을 가진 테이블을 식별하기 위해 _절대_ 행 수 변화와 상대적 비율 변화가 모두 지원됩니다.

#### 3. Volume 소스

**Volume 소스**: DataHub Cloud가 테이블 volume(행 수)을 결정하는 데 사용해야 하는 메커니즘입니다. 지원되는 소스 유형은 플랫폼에 따라 다르지만 일반적으로 다음 범주에 속합니다:

- **Information Schema**: 데이터베이스 및 테이블(행 수 포함)에 대한 실시간 정보를 담고 있는 데이터 웨어하우스 시스템 테이블입니다. 일반적으로 효율적으로 확인할 수 있지만, 테이블에 변경이 이루어진 후 업데이트가 약간 지연될 수 있습니다. 대부분의 데이터 플랫폼에서 비용과 정확도 간의 최적 균형을 제공합니다.

- **Query**: 선택적 SQL 필터가 적용된(플랫폼에 따라 다름) `COUNT(*)` 쿼리를 사용하여 테이블의 최신 행 수를 검색합니다. 테이블 크기에 따라 확인 효율성이 낮을 수 있습니다. 이 접근 방식은 시스템 웨어하우스 테이블을 포함하지 않아 데이터 웨어하우스 및 데이터 레이크 공급자 간에 쉽게 이식 가능합니다. 정보 스키마보다 비용이 많이 드는 테이블 쿼리가 발생합니다.

- **DataHub Dataset Profile**: DataHub Dataset Profile aspect를 사용하여 테이블의 최신 행 수 정보를 검색합니다. 이 옵션을 사용하면 데이터 플랫폼에 접촉하지 않고 DataHub Dataset Profile 메타데이터를 사용하여 Volume Assertions를 평가합니다. DataHub를 통해 관리되는 수집 소스를 구성하지 않은 경우, 이것이 유일하게 사용 가능한 옵션일 수 있습니다. 가장 저렴한 옵션이지만 DataHub에 Dataset Profile이 보고되어야 합니다. 기본적으로 수집 시 DataHub에 Dataset Profile을 보고하지만 빈도가 낮을 수 있습니다. 더 빈번하고 신뢰할 수 있는 데이터를 위해 DataHub API를 통해 Dataset Profile을 보고할 수 있습니다.

Volume Assertions에는 끄기 스위치도 있습니다: 버튼 클릭 한 번으로 언제든지 시작하거나 중지할 수 있습니다.

## Volume Assertion 생성

### 사전 요구 사항

1. **권한**: DataHub에서 특정 entity에 대한 Volume Assertions를 생성하거나 삭제하려면 해당 entity에 대해 `Edit Assertions` 및 `Edit Monitors` 권한이 부여되어야 합니다. 이 권한은 기본적으로 `Asset Owners - Metadata Policy`의 일환으로 Entity 소유자에게 부여됩니다.

2. (선택 사항) **데이터 플랫폼 연결**: DataHub 메타데이터 대신 소스 데이터 플랫폼을 직접 쿼리하는 Volume Assertion을 생성하려면 **Integrations** 탭에서 데이터 플랫폼(Snowflake, BigQuery 또는 Redshift)에 대한 **수집 소스**가 구성되어 있어야 합니다.

이러한 사전 조건이 갖춰지면 Volume Assertions를 생성할 준비가 된 것입니다!

데이터 상태 페이지의 [모니터링 규칙](/docs/managed-datahub/observe/data-health-dashboard.md#monitoring-rules)을 사용하여 Smart Volume Assertions를 대규모로 적용할 수도 있습니다.

### 단계

1. volume을 모니터링할 테이블로 이동합니다
2. **Quality** 탭을 클릭합니다

<p align="left">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/freshness/profile-validation-tab.png"/>
</p>

3. **+ Create Assertion**을 클릭합니다

<p align="left">
  <img width="45%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/volume/assertion-builder-volume-choose-type.png"/>
</p>

4. **Volume**을 선택합니다

5. 평가 **스케줄**을 구성합니다. 이는 assertion이 통과 또는 실패 결과를 생성하기 위해 평가되는 빈도이며 테이블 volume을 확인하는 시간입니다.

6. 평가 **조건 유형**을 구성합니다. 이는 새로운 assertion이 평가될 때 실패하는 경우를 결정합니다.

<p align="left">
  <img width="30%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/volume/assertion-builder-volume-condition-type.png"/>
</p>

7. (선택 사항) **Advanced**를 클릭하여 volume **소스**를 사용자 정의합니다. 이는 테이블 행 수 지표를 얻는 데 사용될 메커니즘입니다. 각 데이터 플랫폼은 Information Schema, Query, DataHub Dataset Profile을 포함한 다양한 옵션을 지원합니다.

<p align="left">
  <img width="30%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/volume/assertion-builder-volume-select-source-type.png"/>
</p>

- **Information Schema**: 데이터 플랫폼 시스템 메타데이터 테이블을 확인하여 테이블 행 수를 결정합니다.
- **Query**: 테이블에 `COUNT(*)` 쿼리를 실행하여 행 수를 결정합니다.
- **DataHub Dataset Profile**: DataHub Dataset Profile 메타데이터를 사용하여 행 수를 결정합니다.

8. Volume Assertion이 통과하거나 실패할 때 취해야 할 작업을 구성합니다

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/assertion-builder-actions.png"/>
</p>

- **Raise incident**: Volume Assertion이 실패할 때마다 해당 테이블에 대한 새 DataHub `Volume` 인시던트를 자동으로 발생시킵니다. 이는 테이블이 사용하기에 부적합함을 나타낼 수 있습니다. **Settings**에서 Slack 알림을 구성하여 Assertion 실패로 인해 인시던트가 생성될 때 알림을 받으세요.

- **Resolve incident**: 이 Volume Assertion의 실패로 인해 발생한 인시던트를 자동으로 해결합니다. 다른 인시던트에는 영향을 미치지 않습니다.

9. **Next**를 클릭하고 설명을 제공합니다.

10. **Save**를 클릭합니다.

이제 DataHub가 테이블의 Volume Assertion 모니터링을 시작합니다.

assertion이 실행되면 테이블의 성공 또는 실패 상태를 확인할 수 있습니다

<p align="left">
  <img width="45%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/volume/profile-passing-volume-assertions-expanded.png"/>
</p>

## Smart Assertions를 활용한 이상 탐지 ⚡

**DataHub Cloud Observe** 모듈의 일환으로 DataHub Cloud는 기본 제공 **Smart Assertions**도 제공합니다. 이는 수동 설정 없이 중요한 웨어하우스 테이블의 volume을 모니터링하는 데 사용할 수 있는 동적 AI 기반 Volume Assertions입니다.

UI에서 `Detect with AI` 옵션을 선택하여 smart assertions를 생성할 수 있습니다:

<p align="left">
  <img width="90%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/volume/volume-smart-assertion.png"/>
</p>

## 시계열 버킷팅

기본적으로 volume assertions는 특정 시점의 테이블 **총 행 수**를 평가합니다. **시계열 버킷팅**을 사용하면 데이터를 시간 기반 버킷(예: 일별 또는 주별)으로 분할하고 각 버킷 내에서 volume 지표를 평가할 수 있습니다. 이는 assertion이 측정하는 내용을 근본적으로 변경합니다:

|                      | 버킷팅 없음                          | 버킷팅 있음                                              |
| -------------------- | ------------------------------------------ | ----------------------------------------------------------- |
| **총 행 수**  | 테이블 총 행 수                      | 타임스탬프-버킷 조건과 일치하는 행 수             |
| 예시              | "총 행 수는 10,000 이상을 유지해야 합니다" | "하루에 추가되는 행은 500 이상이어야 합니다"                    |
| **행 수 변화** | 이전 평가 이후 행 수 변화 | 이전 버킷과 비교한 행 수                       |
| 예시              | "행 수는 최소 100 증가해야 합니다"    | "주당 추가된 행의 차이는 5,000을 초과해서는 안 됩니다" |

시계열 버킷팅은 다음과 같은 경우에 유용합니다:

- 테이블에 행이 생성되거나 업데이트된 시간을 나타내는 타임스탬프 컬럼이 있는 경우
- 전체 테이블이 아닌 일별 또는 주별 세분성으로 데이터 품질을 모니터링하려는 경우
- "오늘 데이터가 도착하지 않았다" 또는 "이번 주 volume이 비정상적으로 낮다"와 같은 문제를 탐지하려는 경우

### 버킷팅 구성

시계열 버킷팅 전략은 다음으로 구성됩니다:

- **타임스탬프 컬럼**: 행을 버킷으로 분할하는 데 사용되는 날짜/시간 컬럼(예: `created_at`, `event_date`).
- **버킷 간격**: 각 시간 버킷의 크기. 현재 지원되는 간격은 **일별** (1 DAY)과 **주별** (1 WEEK)입니다.
- **시간대**: 버킷 경계에 대한 IANA 시간대(예: `America/Los_Angeles`, `UTC`). 타임스탬프 컬럼의 시간대와 일치해야 합니다. 기본값은 UTC입니다.
- **늦은 도착 유예 기간** (선택 사항): 버킷이 완료된 것으로 간주되기 전 버킷 종료 시간 이후의 버퍼. 늦게 도착하는 데이터를 고려합니다. 예를 들어, 일별 버킷에 2일 유예 기간은 월요일 버킷이 화요일 자정 대신 목요일 자정까지 평가되지 않음을 의미합니다.

:::note
시계열 버킷팅이 활성화되면 assertion의 **평가 스케줄이 자동으로 계산**됩니다. 버킷팅된 assertion에 대해 cron 스케줄을 수동으로 설정할 필요가 없습니다(할 수도 없습니다).
:::

### 제한 사항

- **Query** 소스 유형만 버킷팅을 지원합니다. Information Schema와 DataHub Dataset Profile 소스는 버킷팅할 수 없습니다.
- 단일 단위 버킷 간격만 지원됩니다(1 DAY 또는 1 WEEK, 2 DAY는 불가).
- 버킷팅 구성(타임스탬프 컬럼, 버킷 간격, 시간대)은 **생성 후 변경할 수 없습니다**. 늦은 도착 유예 기간은 업데이트할 수 있습니다.
- 다운타임으로 인해 버킷이 누락된 경우 소급하여 평가되지 않습니다.

### UI에서 버킷팅 구성

volume assertion 생성 시:

<p align="left">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/bucketing/volume-timeseries-bucketing.png"/>
</p>

1. assertion 빌더에서 **Time-Series Bucketing** 섹션을 펼칩니다.
2. 버킷팅을 **켜기**로 전환합니다.
3. 드롭다운에서 **타임스탬프 컬럼**을 선택합니다(날짜/시간 필드로 필터링됨).
4. **버킷 크기**(일별 또는 주별)를 선택합니다.
5. 타임스탬프 컬럼의 시간대와 일치하는 **시간대**를 선택합니다.
6. (선택 사항) 늦게 도착하는 데이터를 고려하기 위해 **유예 기간**을 설정합니다.

### Python SDK를 통한 버킷팅 구성

```python
from datahub.sdk import DataHubClient
from datahub.metadata.urns import DatasetUrn

client = DataHubClient(server="<your_server>", token="<your_token>")
dataset_urn = DatasetUrn.from_string(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.table,PROD)"
)

# 일별 버킷팅을 사용한 volume assertion
volume_assertion = client.assertions.sync_volume_assertion(
    dataset_urn=dataset_urn,
    display_name="Daily Row Count Check",
    criteria_condition="ROW_COUNT_IS_GREATER_THAN_OR_EQUAL_TO",
    criteria_parameters=100,
    detection_mechanism="information_schema",
    time_bucketing_strategy={
        "timestamp_field_path": "created_at",
        "bucket_interval": {"unit": "DAY", "multiple": 1},
        "timezone": "America/Los_Angeles",
        "late_arrival_grace_period": {"unit": "DAY", "multiple": 2},
    },
    tags=["automated", "volume", "daily"],
    enabled=True,
)

# 주별 버킷팅과 보정을 사용한 smart volume assertion
smart_volume = client.assertions.sync_smart_volume_assertion(
    dataset_urn=dataset_urn,
    display_name="Weekly Volume Anomaly Monitor",
    detection_mechanism="information_schema",
    sensitivity="medium",
    time_bucketing_strategy={
        "timestamp_field_path": "event_date",
        "bucket_interval": {"unit": "WEEK", "multiple": 1},
        "timezone": "UTC",
    },
    backfill_config={"backfill_start_date_ms": 1704067200000},
    enabled=True,
)
```

더 많은 예시는 [Assertions SDK 튜토리얼](/docs/api/tutorials/assertions.md)을 참조하세요.

:::info
버킷팅이 활성화된 smart assertions의 경우 assertion의 지표 이력을 채우기 위해 **과거 데이터 보정**도 구성할 수 있습니다. 자세한 내용은 [Assertion 이력 보정](./assertion-backfill.md)을 참조하세요.
:::

## Volume Assertion 중지

assertion 평가를 일시적으로 중지하려면:

1. assertion이 있는 테이블의 **Quality** 탭으로 이동합니다
2. **Volume**을 클릭하여 Volume Assertion assertions를 엽니다
3. 일시 중지하려는 assertion의 "Stop" 버튼을 클릭합니다.

<p align="left">
  <img width="25%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/stop-assertion.png"/>
</p>

assertion을 재개하려면 **Start**를 클릭하세요.

<p align="left">
  <img width="25%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/start-assertion.png"/>
</p>

## API를 통한 Volume Assertions 생성

내부적으로 DataHub Cloud는 두 가지 개념을 사용하여 Volume Assertion 모니터링을 구현합니다:

- **Assertion**: volume에 대한 특정 기대치(예: "테이블이 지난 7시간 이내에 변경됨" 또는 "테이블이 매일 오전 8시까지 변경되는 일정으로 변경됨"). 이것은 "무엇"입니다.

- **Monitor**: 지정된 평가 스케줄에 따라 특정 메커니즘을 사용하여 Assertion을 평가하는 프로세스. 이것은 "어떻게"입니다.

DataHub에서 특정 entity에 대한 Assertions 및 Monitors를 생성하거나 삭제하려면 해당 entity에 대한 `Edit Assertions` 및 `Edit Monitors` 권한이 필요합니다.

#### GraphQL

Volume Assertion을 생성하거나 업데이트하려면 `upsertDatasetVolumeAssertionMonitor` mutation을 사용하세요.

##### 예시

테이블의 행 수가 10에서 20 사이인지 확인하고 8시간마다 실행되는 Volume Assertion entity를 생성하려면:

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

8시간마다 실행되는 AI Smart Freshness Assertion을 생성하려면:

```graphql
mutation upsertDatasetFreshnessAssertionMonitor {
  upsertDatasetFreshnessAssertionMonitor(
    input: {
      entityUrn: "<urn of entity being monitored>"
      inferWithAI: true
      type: ROW_COUNT_TOTAL
      # AI 엔진에 의해 지속적으로 덮어써지므로 여기에 어떤 값이든 제공할 수 있습니다
      rowCountTotal: {
        operator: BETWEEN
        parameters: {
          minValue: { value: "0", type: NUMBER }
          maxValue: { value: "0", type: NUMBER }
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

지원되는 volume assertion 유형은 `ROW_COUNT_TOTAL` 및 `ROW_COUNT_CHANGE`입니다. 기타(예: 증가 세그먼트) 유형은 아직 지원되지 않습니다.
지원되는 연산자 유형은 `GREATER_THAN`, `GREATER_THAN_OR_EQUAL_TO`, `LESS_THAN`, `LESS_THAN_OR_EQUAL_TO`, `BETWEEN`(minValue, maxValue 필요)입니다.
지원되는 파라미터 유형은 `NUMBER`입니다.

동일한 엔드포인트에 assertion urn 입력을 제공하여 기존 Volume Assertion 및 해당 Monitor를 업데이트할 수 있습니다:

```graphql
mutation upsertDatasetVolumeAssertionMonitor {
  upsertDatasetVolumeAssertionMonitor(
    assertionUrn: "<urn of assertion created in earlier query>"
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
        cron: "0 */6 * * *"
      }
      evaluationParameters: { sourceType: INFORMATION_SCHEMA }
      mode: ACTIVE
    }
  ) {
    urn
  }
}
```

GraphQL mutations인 `deleteAssertion` 및 `deleteMonitor`를 사용하여 assertions와 모니터를 함께 삭제할 수 있습니다.

### 팁

:::info
**인증**

GraphQL API를 호출할 때는 항상 DataHub Personal Access Token을 제공해야 합니다. 다음과 같이 'Authorization' 헤더를 추가하세요:

```
Authorization: Bearer <personal-access-token>
```

**GraphQL API 탐색**

`https://your-account-id.acryl.io/api/graphiql`에서 DataHub Cloud GraphQL API의 인터랙티브 버전을 사용해 볼 수 있습니다.
:::
