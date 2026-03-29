---
description: 이 페이지에서는 DataHub Freshness Assertions 사용 방법에 대한 개요를 제공합니다
---

import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Freshness Assertions

<FeatureAvailability saasOnly />

> **Freshness Assertions** 기능은 DataHub Cloud의 **DataHub Cloud Observe** 모듈의 일부로 제공됩니다.
> **DataHub Cloud Observe**에 대해 더 알아보거나 체험해 보고 싶다면 [웹사이트를 방문](https://datahub.com/products/data-observability/)하세요.

## 소개

데이터 웨어하우스 테이블이 며칠, 몇 주, 심지어 몇 달 동안 새로운 데이터로 업데이트되지 않아 곤란했던 경험이 있으신가요?

업스트림 Airflow DAG에 버그가 도입되었거나, 더 심각한 경우 테이블을 관리하던 담당자가 조직을 떠났을 수도 있습니다.
Snowflake, Redshift, BigQuery, Databricks의 중요한 테이블이 예상만큼 자주 업데이트되지 않는 이유는 다양합니다.

데이터 담당자가 다른 누구보다 먼저 데이터 문제를 인식할 수 있도록 인시던트 감지 시간을 단축할 수 있다면 어떨까요? 테이블의 freshness 또는 변경 빈도에 대한 약속을 명시할 수 있다면 어떨까요? DataHub Cloud Freshness Assertions를 통해 이것이 가능합니다.

DataHub Cloud를 통해 사용자는 웨어하우스의 특정 테이블이 언제 변경되어야 하는지에 대한 기대치를 정의하고, 시간에 따라 해당 기대치를 모니터링하며, 문제가 발생했을 때 알림을 받을 수 있습니다.

이 문서에서는 Freshness Assertions 모니터링의 기본 사항(정의, 구성 방법 등)을 다루어 팀이 중요한 데이터 자산에 대한 신뢰를 구축할 수 있도록 돕겠습니다.

시작해 봅시다!

## 지원 현황

Freshness Assertions는 현재 다음을 지원합니다:

1. Snowflake
2. Redshift
3. BigQuery
4. Databricks
5. DataHub Operations (수집을 통해 수집됨)

DataHub Cloud의 **Ingestion** 탭에서 선택한 데이터 플랫폼에 대한 수집 소스가 _반드시_ 구성되어 있어야 합니다.

> DataHub CLI를 사용하여 웨어하우스에 연결하는 경우 Freshness Assertions는 아직 지원되지 않습니다.

## Freshness Assertion이란?

**Freshness Assertion**은 데이터 웨어하우스의 테이블이 지정된 기간 내에 업데이트되었는지 여부를 판단하는 데 사용되는 구성 가능한 데이터 품질 규칙입니다. Freshness Assertions는 특히 자주 변경되는 테이블에 유용합니다.

예를 들어, 이커머스 웹사이트에서 수집된 사용자 클릭을 저장하는 Snowflake 테이블이 있다고 가정해 봅시다. 이 테이블은 특정 주기(시간당 1회)로 새 데이터로 업데이트됩니다. 그리고 이 "클릭" 테이블에 저장된 데이터를 기반으로 생성된 Looker의 비즈니스 분석 대시보드가 "일일 세일" 배너 클릭 수와 같은 중요한 지표를 보여줍니다. 클릭 테이블이 매시간 계속 업데이트되는 것이 중요한데, 업데이트가 중단되면 다운스트림 지표 대시보드가 부정확해질 수 있습니다. 이러한 상황의 위험은 명확합니다: 조직이 불완전한 정보에 기반하여 잘못된 결정을 내릴 수 있습니다.

이런 경우, Snowflake "클릭" 테이블이 예상대로 매시간 새로운 데이터로 업데이트되는지 확인하는 **Freshness Assertion**을 사용할 수 있습니다. 한 시간이 지나도록 변경이 없으면 팀에 즉시 알려 부정적인 영향을 방지할 수 있습니다.

### Freshness Assertion의 구조

**Freshness Assertions**는 기본적으로 몇 가지 중요한 구성 요소로 이루어집니다:

1. **평가 스케줄**
2. **변경 윈도우**
3. **변경 소스**

이 섹션에서 각각에 대한 개요를 설명합니다.

#### 1. 평가 스케줄

**평가 스케줄**: 지정된 웨어하우스 테이블에서 새로운 업데이트를 확인하는 빈도를 정의합니다. 일반적으로 테이블의 예상 변경 빈도에 맞게 구성해야 하지만, 더 자주 확인하도록 설정할 수도 있습니다.
테이블이 일별로 변경된다면 일별로, 시간별로 변경된다면 시간별로 설정하세요. 주의 특정 요일, 시간 내의 특정 시, 또는 시간 내의 특정 분을 지정할 수도 있습니다.

#### 2. 변경 윈도우

**변경 윈도우**: 테이블의 변경 여부를 판단할 때 사용되는 시간 윈도우를 정의합니다.
테이블의 변경 여부는 다음 중 하나로 확인할 수 있습니다:

- _freshness 검사가 마지막으로 평가된 이후_. 예를 들어, 평가 스케줄이 매일 오전 8시 PST에 실행되도록 설정된 경우, 전날 오전 8시와 다음날 오전 8시 사이에 변경이 있었는지 확인할 수 있습니다.

- _freshness 검사가 평가되는 시점으로부터 특정 시간 이내_ (고정 간격). 예를 들어, 평가 스케줄이 매일 오전 8시 PST에 실행되도록 설정된 경우, 검사가 평가되기 _이전 8시간_ 내에 변경이 있었는지 확인할 수 있습니다(자정 12시부터 오전 8시 PST 사이).

#### 3. 변경 소스

**변경 소스**: DataHub Cloud가 테이블 변경 여부를 판단하는 데 사용해야 하는 메커니즘입니다. 지원되는 변경 소스 유형은 플랫폼에 따라 다르지만 일반적으로 다음 범주에 속합니다:

- **감사 로그** (기본값): 데이터 웨어하우스가 노출하는 메타데이터 API 또는 테이블로, 각 테이블에 수행된 작업에 대한 정보를 담고 있습니다. 일반적으로 효율적으로 확인할 수 있지만, 일부 유용한 작업은 모든 주요 웨어하우스 플랫폼에서 완전히 지원되지 않습니다. Databricks의 경우 [이 옵션](https://docs.databricks.com/en/delta/history.html)은 Delta 형식으로 저장된 테이블에만 사용 가능합니다.

- **정보 스키마**: 데이터베이스 및 테이블에 대한 실시간 정보(행 수 포함)를 담고 있는 데이터 웨어하우스 시스템 테이블입니다. 일반적으로 효율적으로 확인할 수 있지만, 특정 테이블의 마지막 변경 _유형_(예: 작업 자체 - INSERT, UPDATE, DELETE, 영향받은 행 수 등)에 대한 세부 정보가 부족합니다. Databricks의 경우 [이 옵션](https://docs.databricks.com/en/delta/table-details.html)은 Delta 형식으로 저장된 테이블에만 사용 가능합니다.

- **Last Modified Column**: 특정 _행_이 마지막으로 수정된 시간을 나타내는 날짜 또는 타임스탬프 컬럼입니다. 각 웨어하우스 테이블에 Last Modified Column을 추가하는 패턴은 변경 관리와 관련된 기존 사용 사례에서 자주 사용됩니다. 이 변경 소스를 사용하면 특정 시간 윈도우(변경 윈도우 기반) 내에 수정된 행을 찾기 위해 테이블에 쿼리가 실행됩니다.

- **High Watermark Column**: 날짜, 시간 또는 항상 증가하는 다른 숫자와 같이 지속적으로 증가하는 값을 포함하는 컬럼입니다. 이 변경 소스를 사용하면 이전에 관찰된 값보다 높은 새로운 "high watermark"(즉, 이전 값보다 높은 값)를 가진 행을 찾아 테이블이 지정된 기간 내에 변경되었는지 여부를 판단하기 위해 쿼리가 실행됩니다. 이 접근 방식은 변경 윈도우가 고정 간격을 사용하지 않는 경우에만 지원됩니다.

- **DataHub Operation**: DataHub "Operation" aspect는 entity에 대한 변경 사항을 설명하는 데 사용되는 시계열 정보를 포함합니다. 이 옵션을 사용하면 데이터 플랫폼에 접촉하지 않고 DataHub Operation 메타데이터를 사용하여 Freshness Assertions를 평가합니다. 이는 수집을 통해 또는 DataHub API를 통해 DataHub에 Operation이 보고되는 것에 의존합니다([API를 통한 Operation 보고](#reporting-operations-via-api) 참조). DataHub를 통해 수집 소스를 구성하지 않은 경우, 이것이 유일하게 사용 가능한 옵션일 수 있습니다. 기본적으로 발견된 모든 작업 유형은 유효한 변경으로 간주됩니다. 이 옵션을 선택할 때 **Operation Types** 드롭다운을 사용하여 유효한 변경으로 간주되어야 할 작업 유형을 지정하세요. DataHub의 표준 Operation Types 중 하나를 선택하거나 작업 유형 이름을 입력하여 "Custom" Operation Type을 지정할 수 있습니다.

- **File Metadata** (Databricks 전용): Unity Catalog 및 Hive Metastore 기반 테이블 모두에서 Databricks가 노출하는 컬럼으로, 테이블 파일이 마지막으로 변경된 시간에 대한 정보를 포함합니다. [여기](https://docs.databricks.com/en/ingestion/file-metadata-column.html)에서 자세히 알아보세요.

  컬럼 값 접근 방식(**Last Modified Column** 또는 **High Watermark Column**) 중 하나를 사용하면 테이블의 특정 유형의 변경이 이루어졌는지 여부를 결정하도록 사용자 지정할 수 있어 유용합니다.
  또한 이러한 유형의 assertion은 시스템 웨어하우스 테이블을 포함하지 않으므로 데이터 웨어하우스 및 데이터 레이크 공급자 간에 쉽게 이식 가능합니다.

Freshness Assertions에는 끄기 스위치도 있습니다: 버튼 클릭 한 번으로 언제든지 시작하거나 중지할 수 있습니다.

## Freshness Assertion 생성

### 사전 요구 사항

1. **권한**: DataHub에서 특정 entity에 대한 Freshness Assertions를 생성하거나 삭제하려면 해당 entity에 대해 `Edit Assertions` 및 `Edit Monitors` 권한이 부여되어야 합니다. 이 권한은 기본적으로 `Asset Owners - Metadata Policy`의 일환으로 Entity 소유자에게 부여됩니다.
2. (선택 사항) **데이터 플랫폼 연결**: DataHub 메타데이터 대신 소스 데이터 플랫폼을 직접 쿼리하는 Freshness Assertion을 생성하려면 **Integrations** 탭에서 데이터 플랫폼(Snowflake, BigQuery 또는 Redshift)에 대한 **수집 소스**가 구성되어 있어야 합니다.

이러한 사전 조건이 갖춰지면 Freshness Assertions를 생성할 준비가 된 것입니다!

데이터 상태 페이지의 [모니터링 규칙](/docs/managed-datahub/observe/data-health-dashboard.md#monitoring-rules)을 사용하여 Smart Freshness Assertions를 대규모로 적용할 수도 있습니다.

### 단계

1. freshness를 모니터링할 테이블로 이동합니다
2. **Quality** 탭을 클릭합니다

<p align="left">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/freshness/profile-validation-tab.png"/>
</p>

3. **+ Create Assertion**을 클릭합니다

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/freshness/assertion-builder-choose-type.png"/>
</p>

4. **Freshness**를 선택합니다

5. 평가 **스케줄**을 구성합니다. 이는 테이블의 변경 여부를 확인하는 빈도로, 테이블이 업데이트되어야 한다는 기대 빈도를 나타냅니다.
6. 평가 **기간**을 구성합니다. 이는 테이블의 변경 여부를 확인할 때 고려할 시간 범위를 정의합니다. _Since the previous check_를 선택하여 이전 평가 이후 테이블이 변경되었는지 확인하거나, _In the past X hours_를 선택하여 테이블 검사 시 사용되는 고정 간격을 구성하세요.

_연속적인 검사 평가 사이에 테이블이 변경되었는지 확인_

<p align="left">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/freshness/assertion-builder-freshness-since-last.png"/>
</p>

_특정 시간 윈도우 내에 테이블이 변경되었는지 확인_

<p align="left">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/freshness/assertion-builder-freshness-fixed-interval.png"/>
</p>

7. (선택 사항) **Advanced**를 클릭하여 평가 **소스**를 사용자 정의합니다. 이는 검사를 평가하는 데 사용될 메커니즘입니다. 각 데이터 플랫폼은 감사 로그, 정보 스키마, Last Modified Column, High Watermark Column, DataHub Operation을 포함한 다양한 옵션을 지원합니다.

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/freshness/assertion-builder-freshness-source-type.png"/>
</p>

- **Audit Log**: 데이터 플랫폼 운영 감사 로그를 확인하여 평가 기간 내에 테이블이 변경되었는지 여부를 판단합니다. No-Ops(예: `INSERT 0`)를 필터링합니다. 단, 데이터 플랫폼에 따라 감사 로그가 몇 시간 지연될 수 있습니다. 또한 정보 스키마보다 웨어하우스에 더 많은 비용이 발생합니다.
- **Information Schema**: 데이터 플랫폼 시스템 메타데이터 테이블을 확인하여 평가 기간 내에 테이블이 변경되었는지 여부를 판단합니다. 대부분의 데이터 플랫폼에서 비용과 정확도 간의 최적 균형을 제공합니다.
- **Last Modified Column**: 테이블의 특정 행이 마지막으로 변경된 시간을 반영하는 "Last Modified Time" 컬럼의 행 존재 여부를 확인하여 평가 기간 내에 테이블이 변경되었는지 여부를 판단합니다. 정보 스키마보다 비용이 많이 드는 테이블 쿼리가 발생합니다.
- **High Watermark Column**: 지속적으로 증가하는 "high watermark" 컬럼 값의 변경을 모니터링하여 테이블이 변경되었는지 여부를 판단합니다. 이 옵션은 시간이 지남에 따라 일관되게 성장하는 테이블(예: 팩트 또는 이벤트(클릭스트림 등) 테이블)에 특히 유용합니다. 고정 되돌아보기 기간을 사용할 때는 사용할 수 없습니다. 정보 스키마보다 비용이 많이 드는 테이블 쿼리가 발생합니다.
- **DataHub Operation**: DataHub Operations를 사용하여 평가 기간 내에 테이블이 변경되었는지 여부를 판단합니다. 가장 저렴한 옵션이지만 DataHub에 Operations가 보고되어야 합니다. 기본적으로 수집 시 DataHub에 Operations를 보고하지만 빈도가 낮을 수 있습니다. 더 빈번하고 신뢰할 수 있는 데이터를 위해 DataHub API를 통해 Operations를 보고할 수 있습니다.

8. Freshness Assertion이 통과하거나 실패할 때 취해야 할 작업을 구성합니다

<p align="left">
  <img width="45%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/assertion-builder-actions.png"/>
</p>

- **Raise incident**: Freshness Assertion이 실패할 때마다 해당 테이블에 대한 새 DataHub `Freshness` 인시던트를 자동으로 발생시킵니다. 이는 테이블이 사용하기에 부적합함을 나타낼 수 있습니다. **Settings**에서 Slack 알림을 구성하여 Assertion 실패로 인해 인시던트가 생성될 때 알림을 받으세요.

- **Resolve incident**: 이 Freshness Assertion의 실패로 인해 발생한 인시던트를 자동으로 해결합니다. 다른 인시던트에는 영향을 미치지 않습니다.

9. **Next**를 클릭하고 설명을 추가합니다.

10. **Save**를 클릭합니다.

이제 DataHub가 테이블의 Freshness Assertion 모니터링을 시작합니다.

assertion이 실행되면 테이블의 성공 또는 실패 상태를 확인할 수 있습니다

<p align="left">
  <img width="45%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/freshness/failing-assertions-section.png"/>
</p>

## Freshness Assertion 중지

assertion 평가를 일시적으로 중지하려면:

1. assertion이 있는 테이블의 **Quality** 탭으로 이동합니다
2. **Freshness**를 클릭하여 Freshness Assertion assertions를 엽니다
3. 일시 중지하려는 assertion의 "Stop" 버튼을 클릭합니다.

<p align="left">
  <img width="25%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/stop-assertion.png"/>
</p>

assertion을 재개하려면 **Start**를 클릭하세요.

<p align="left">
  <img width="25%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/start-assertion.png"/>
</p>

## Smart Assertions를 활용한 이상 탐지 ⚡

**DataHub Cloud Observe** 모듈의 일환으로 DataHub Cloud는 기본 제공 **Smart Assertions**도 제공합니다. 이는 수동 설정 없이 중요한 웨어하우스 테이블의 freshness를 모니터링하는 데 사용할 수 있는 동적 AI 기반 Freshness Assertions입니다. Smart Assertion의 ML 모델은 [`operation` aspect](../../api/tutorials/operations.md)에 캡처된 테이블 변경 이력을 기반으로 학습합니다. 일반적으로 수집 실행 시간에 채워집니다.

UI에서 `Detect with AI` 옵션을 선택하여 smart assertions를 생성할 수 있습니다:

<p align="left">
  <img width="90%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/freshness/freshness-smart-assertion.png"/>
</p>

## API를 통한 Freshness Assertions 생성

내부적으로 DataHub Cloud는 두 가지 개념을 사용하여 Freshness Assertion 모니터링을 구현합니다:

- **Assertion**: freshness에 대한 특정 기대치(예: "테이블이 지난 7시간 이내에 변경됨" 또는 "테이블이 매일 오전 8시까지 변경되는 일정으로 변경됨"). 이것은 "무엇"입니다.
- **Monitor**: 지정된 평가 스케줄에 따라 특정 메커니즘을 사용하여 Assertion을 평가하는 프로세스. 이것은 "어떻게"입니다.

DataHub에서 특정 entity에 대한 Assertions 및 Monitors를 생성하거나 삭제하려면 해당 entity에 대한 `Edit Assertions` 및 `Edit Monitors` 권한이 필요합니다.

#### GraphQL

Freshness Assertion을 생성하거나 업데이트하려면 `upsertDatasetFreshnessAssertionMonitor` mutation을 사용하세요.

##### 예시

8시간마다 실행되며 테이블이 지난 8시간 이내에 업데이트되었는지 확인하는 Freshness Assertion entity를 생성하려면:

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

AI Smart Freshness Assertion을 생성하려면:

```graphql
mutation upsertDatasetFreshnessAssertionMonitor {
  upsertDatasetFreshnessAssertionMonitor(
    input: {
      entityUrn: "<urn of entity being monitored>"
      inferWithAI: true
      evaluationSchedule: { timezone: "America/Los_Angeles", cron: "0 * * * *" }
      evaluationParameters: { sourceType: INFORMATION_SCHEMA }
      mode: ACTIVE
    }
  ) {
    urn
  }
}
```

동일한 엔드포인트에 assertion urn 입력을 제공하여 기존 Freshness Assertion 및 해당 Monitor를 업데이트할 수 있습니다:

```graphql
mutation upsertDatasetFreshnessAssertionMonitor {
  upsertDatasetFreshnessAssertionMonitor(
    assertionUrn: "<urn of assertion created in earlier query>"
    input: {
      entityUrn: "<urn of entity being monitored>"
      schedule: {
        type: FIXED_INTERVAL
        fixedInterval: { unit: HOUR, multiple: 6 }
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

### API를 통한 Operations 보고

DataHub Operations를 사용하여 entity에 대한 변경 사항을 캡처할 수 있습니다. 이는 기본 데이터 플랫폼이 변경 사항을 캡처하는 메커니즘을 제공하지 않거나, 데이터 플랫폼의 메커니즘이 신뢰할 수 없는 경우에 유용합니다. operation을 보고하려면 `reportOperation` GraphQL mutation을 사용하면 됩니다.

##### 예시

```graphql
mutation reportOperation {
  reportOperation(
    input: {
      urn: "<urn of the dataset being reported>"
      operationType: INSERT
      sourceType: DATA_PLATFORM
      timestampMillis: 1693252366489
    }
  )
}
```

`timestampMillis` 필드를 사용하여 작업이 발생한 시간을 지정하세요. 값이 제공되지 않으면 현재 시간이 사용됩니다.

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
