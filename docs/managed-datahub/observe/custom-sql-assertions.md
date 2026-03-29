---
description: 이 페이지에서는 DataHub SQL Assertions 사용 방법에 대한 개요를 제공합니다
---

import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Custom SQL Assertions

<FeatureAvailability saasOnly />

> **Custom SQL Assertions** 기능은 DataHub Cloud의 **DataHub Cloud Observe** 모듈의 일부로 제공됩니다.
> **DataHub Cloud Observe**에 대해 더 알아보거나 체험해 보고 싶다면 [웹사이트를 방문](https://datahub.com/products/data-observability/)하세요.

## 소개

의존하는 데이터 웨어하우스 테이블의 의미가 예고도 없이 근본적으로 바뀐 경험이 있으신가요?
그렇다면 어떻게 알게 되셨나요? 내부 보고 대시보드를 보던 누군가가, 또는 더 심하게는 제품을 사용하는 사용자가 수치가 이상해 보인다며 경보를 울렸을 것입니다. 예를 들어, 처음에는 회사 이커머스 웹 스토어의 구매 내역을 추적하던 테이블에 갑자기 회사의 새 모바일 앱을 통한 구매도 포함되기 시작했을 수 있습니다.

Snowflake, Redshift, BigQuery, Databricks의 중요한 테이블이 의미 면에서 변경되는 이유는 다양합니다 - 애플리케이션 코드 버그, 새 기능 출시, 핵심 지표 정의 변경 등. 이러한 변경은 종종 보고 대시보드나 데이터 기반 제품 기능과 같은 주요 다운스트림 데이터 제품 구축에 사용되는 데이터에 대한 중요한 가정을 깨뜨립니다.

데이터 담당자가 다른 누구보다 먼저 데이터 문제를 인식할 수 있도록 인시던트 감지 시간을 단축할 수 있다면 어떨까요? DataHub Cloud **Custom SQL Assertions**를 통해 이것이 가능합니다.

DataHub Cloud를 통해 사용자는 커스텀 SQL 쿼리를 통해 특정 웨어하우스 테이블에 대한 복잡한 기대치를 정의하고, 테이블이 성장하고 변화함에 따라 시간이 지나도 해당 기대치를 모니터링할 수 있습니다.

이 문서에서는 Custom SQL Assertions 모니터링의 기본 사항(정의, 구성 방법 등)을 다루어 팀이 중요한 데이터 자산에 대한 신뢰를 구축할 수 있도록 돕겠습니다.

시작해 봅시다!

## 지원 현황

Custom SQL Assertions는 현재 다음을 지원합니다:

1. Snowflake
2. Redshift
3. BigQuery
4. Databricks

DataHub Cloud의 **Ingestion** 탭에서 선택한 데이터 플랫폼에 대한 수집 소스가 _반드시_ 구성되어 있어야 합니다.

> DataHub CLI를 사용하여 웨어하우스에 연결하는 경우 SQL Assertions는 아직 지원되지 않습니다.

## Custom SQL Assertion이란?

**Custom SQL Assertion**은 데이터 웨어하우스 테이블의 의미에서 예상치 못한 또는 갑작스러운 변화를 모니터링하는 데 사용되는 고도로 구성 가능한 데이터 품질 규칙입니다. Custom SQL Assertions는 테이블에 대해 평가되는 원시 SQL 쿼리를 통해 정의됩니다. SQL 쿼리를 완전히 제어할 수 있으며 데이터 웨어하우스에서 지원하는 모든 SQL 기능을 사용할 수 있습니다.
Custom SQL Assertions는 중요한 지표나 보고서를 생성하는 데 사용되는 복잡한 테이블이나 관계가 있고 테이블의 의미가 시간이 지나도 안정적이어야 하는 경우에 특히 유용합니다.
데이터를 모니터링하는 데 이미 사용하는 기존 SQL 쿼리가 있다면, Custom SQL Assertions가 시작하기 좋은 쉬운 방법이 될 수 있습니다.

예를 들어, 회사 이커머스 웹 스토어에서 이루어진 구매 수를 추적하는 테이블이 있다고 가정해 봅시다. 지난 24시간 내의 구매 수를 계산하는 SQL 쿼리가 있고, 항상 1000보다 크도록 이 지표를 시간에 따라 모니터링하려고 합니다. Custom SQL Assertion을 사용하여 이것을 할 수 있습니다!

### Custom SQL Assertion의 구조

**Custom SQL Assertions**는 기본적으로 몇 가지 중요한 구성 요소로 이루어집니다:

1. **평가 스케줄**
2. **쿼리**
3. **조건 유형**

이 섹션에서 각각에 대한 개요를 설명합니다.

#### 1. 평가 스케줄

**평가 스케줄**: 지정된 웨어하우스 테이블을 쿼리하는 빈도를 정의합니다. 일반적으로 테이블의 예상 변경 빈도에 맞게 구성해야 하지만, 요구 사항에 따라 더 낮은 빈도로 설정할 수도 있습니다. 주의 특정 요일, 시간 내의 특정 시, 또는 시간 내의 특정 분을 지정할 수도 있습니다.

#### 2. 쿼리

**쿼리**: 테이블을 평가하는 데 사용될 SQL 쿼리입니다. 쿼리는 **단일 행**에 **단일 숫자형 컬럼**(정수, 부동소수점)을 포함하는 결과를 반환해야 합니다.
쿼리는 원하는 만큼 단순하거나 복잡하게 작성할 수 있으며 데이터 웨어하우스에서 지원하는 모든 SQL 기능을 사용할 수 있습니다. 이를 위해 구성된 사용자 계정에 자산에 대한 읽기 액세스 권한이 있어야 합니다. 쿼리에서 테이블의 완전히 정규화된 이름을 사용해야 합니다.

"Try it out" 버튼을 사용하여 쿼리를 테스트하고 단일 컬럼이 있는 단일 행을 반환하는지 확인하세요. 쿼리는 구성된 사용자 계정 컨텍스트에서 테이블에 대해 실행되므로 사용자에게 테이블에 대한 읽기 액세스 권한이 있는지 확인하세요.

#### 3. 조건 유형

**조건 유형**: Assertion이 **실패**하는 조건을 정의합니다. 지원되는 작업 목록:

- **Is Equal To**: 쿼리 결과가 구성된 값과 같으면 assertion이 실패합니다
- **Is Not Equal To**: 쿼리 결과가 구성된 값과 다르면 assertion이 실패합니다
- **Is Greater Than**: 쿼리 결과가 구성된 값보다 크면 assertion이 실패합니다
- **Is Less Than**: 쿼리 결과가 구성된 값보다 작으면 assertion이 실패합니다
- **Is Outside a Range**: 쿼리 결과가 구성된 범위를 벗어나면 assertion이 실패합니다
- **Grows More Than**: 쿼리 결과가 구성된 범위보다 많이 증가하면 assertion이 실패합니다. 비율(**Percentage**) 또는 값(**Value**) 중 하나를 사용할 수 있습니다.
- **Grows Less Than**: 쿼리 결과가 구성된 비율보다 적게 증가하면 assertion이 실패합니다. 비율(**Percentage**) 또는 값(**Value**) 중 하나를 사용할 수 있습니다.
- **Growth is outside a range**: 쿼리 결과 성장이 구성된 범위를 벗어나면 assertion이 실패합니다. 비율(**Percentage**) 또는 값(**Value**) 중 하나를 사용할 수 있습니다.

Custom SQL Assertions에는 끄기 스위치도 있습니다: 버튼 클릭 한 번으로 언제든지 시작하거나 중지할 수 있습니다.

## Custom SQL Assertion 생성

### 사전 요구 사항

1. **권한**: DataHub에서 특정 entity에 대한 Custom SQL Assertions를 생성하거나 삭제하려면 해당 entity에 대해 `Edit Assertions`, `Edit Monitors`, **그리고 추가적으로 `Edit SQL Assertion Monitors`** 권한이 부여되어야 합니다. 이 권한은 기본적으로 `Asset Owners - Metadata Policy`의 일환으로 Entity 소유자에게 부여됩니다.

2. **데이터 플랫폼 연결**: Custom SQL Assertion을 생성하려면 **Integrations** 탭에서 데이터 플랫폼(Snowflake, BigQuery, Redshift 또는 Databricks)에 대한 **수집 소스**가 구성되어 있어야 합니다.

이러한 사전 조건이 갖춰지면 Custom SQL Assertions를 생성할 준비가 된 것입니다!

### 단계

1. 모니터링할 테이블로 이동합니다
2. **Quality** 탭을 클릭합니다

<p align="left">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/freshness/profile-validation-tab.png"/>
</p>

3. **+ Create Assertion**을 클릭합니다

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/custom/assertion-builder-custom-choose-type.png"/>
</p>

4. **Custom**을 선택합니다

5. 평가 **스케줄**을 구성합니다. 이는 assertion이 통과 또는 실패 결과를 생성하기 위해 평가되는 빈도이며 쿼리가 실행되는 시간입니다.

6. 테이블을 평가하는 데 사용될 SQL **쿼리**를 제공합니다. 쿼리는 단일 컬럼이 있는 단일 행을 반환해야 합니다. 현재 숫자 값만 지원됩니다(정수 및 부동소수점). 쿼리는 원하는 만큼 단순하거나 복잡하게 작성할 수 있으며 데이터 웨어하우스에서 지원하는 모든 SQL 기능을 사용할 수 있습니다. 쿼리에서 테이블의 완전히 정규화된 이름을 사용해야 합니다.

<p align="left">
  <img width="50%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/custom/assertion-builder-custom-query-editor.png"/>
</p>

7. 평가 **조건 유형**을 구성합니다. 이는 새로운 assertion이 평가될 때 실패하는 경우를 결정합니다.

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/custom/assertion-builder-custom-condition-type.png"/>
</p>

8. Custom SQL Assertion이 통과하거나 실패할 때 취해야 할 작업을 구성합니다

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/assertion-builder-actions.png"/>
</p>

- **Raise incident**: Custom SQL Assertion이 실패할 때마다 해당 테이블에 대한 새 DataHub 인시던트를 자동으로 발생시킵니다. 이는 테이블이 사용하기에 부적합함을 나타낼 수 있습니다. **Settings**에서 Slack 알림을 구성하여 Assertion 실패로 인해 인시던트가 생성될 때 알림을 받으세요.

- **Resolve incident**: 이 Custom SQL Assertion의 실패로 인해 발생한 인시던트를 자동으로 해결합니다. 다른 인시던트에는 영향을 미치지 않습니다.

9. (선택 사항) **Try it out** 버튼을 사용하여 쿼리를 테스트하고 단일 컬럼이 있는 단일 행을 반환하며 구성된 조건 유형을 통과하는지 확인합니다.

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/custom/assertion-builder-custom-try-it-out.png"/>
</p>

10. **Next**를 클릭한 다음 설명을 추가합니다.

11. **Save**를 클릭합니다.

이제 DataHub가 테이블의 Custom SQL Assertion 모니터링을 시작합니다.

assertion이 실행되면 테이블의 성공 또는 실패 상태를 확인할 수 있습니다

<p align="left">
  <img width="45%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/custom/profile-passing-custom-assertions-expanded.png"/>
</p>

## Custom SQL Assertion 중지

assertion 평가를 일시적으로 중지하려면:

1. assertion이 있는 테이블의 **Quality** 탭으로 이동합니다
2. **Custom SQL**을 클릭하여 SQL Assertion assertions를 엽니다
3. 일시 중지하려는 assertion의 "Stop" 버튼을 클릭합니다.

<p align="left">
  <img width="25%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/stop-assertion.png"/>
</p>

assertion을 재개하려면 **Start**를 클릭하세요.

<p align="left">
  <img width="25%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/start-assertion.png"/>
</p>

## Smart Assertions를 활용한 이상 탐지 ⚡

**DataHub Cloud Observe** 모듈의 일환으로 DataHub Cloud는 기본 제공 [Smart Assertions](./smart-assertions.md)도 제공합니다. 이는 수동 설정 없이 SQL 쿼리로 계산된 지표를 모니터링하는 데 사용할 수 있는 동적 AI 기반 Custom SQL Assertions입니다.

UI에서 `Detect with AI` 옵션을 선택하여 smart assertions를 생성할 수 있습니다:

<p align="left">
  <img width="90%"  src="/imgs/observe/custom/custom-sql-smart-assertion.png"/>
</p>

## API를 통한 Custom SQL Assertions 생성

내부적으로 DataHub Cloud는 두 가지 개념을 사용하여 Custom SQL Assertion 모니터링을 구현합니다:

- **Assertion**: 커스텀 assertion에 대한 특정 기대치(예: "테이블이 지난 7시간 이내에 변경됨" 또는 "테이블이 매일 오전 8시까지 변경되는 일정으로 변경됨"). 이것은 "무엇"입니다.

- **Monitor**: 지정된 평가 스케줄에 따라 특정 메커니즘을 사용하여 Assertion을 평가하는 프로세스. 이것은 "어떻게"입니다.

DataHub에서 특정 entity에 대한 Assertions 및 Monitors를 생성하거나 삭제하려면 해당 entity에 대한 `Edit Assertions` 및 `Edit Monitors` 권한이 필요합니다.

#### GraphQL

Custom SQL Assertion을 생성하거나 업데이트하려면 `upsertDatasetSqlAssertionMonitor` mutation을 사용하세요.

##### 예시

8시간마다 실행되며 쿼리 결과가 100보다 큰지 확인하는 Custom SQL Assertion entity를 생성하려면:

```graphql
mutation upsertDatasetSqlAssertionMonitor {
  upsertDatasetSqlAssertionMonitor(
    input: {
      entityUrn: "<urn of entity being monitored>"
      type: METRIC
      description: "<description of the custom assertion>"
      statement: "<SQL query to be evaluated>"
      operator: GREATER_THAN_OR_EQUAL_TO
      parameters: { value: { value: "100", type: NUMBER } }
      evaluationSchedule: {
        timezone: "America/Los_Angeles"
        cron: "0 */8 * * *"
      }
      mode: ACTIVE
    }
  ) {
    urn
  }
}
```

동일한 엔드포인트에 assertion urn 입력을 제공하여 기존 Custom SQL Assertion 및 해당 Monitor를 업데이트할 수 있습니다.

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
