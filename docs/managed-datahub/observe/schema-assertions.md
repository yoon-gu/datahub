---
description: 이 페이지에서는 DataHub Schema Assertions 사용 방법에 대한 개요를 제공합니다
---

import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Schema Assertions

<FeatureAvailability saasOnly />

> **Schema Assertions** 기능은 DataHub Cloud의 **DataHub Cloud Observe** 모듈의 일부로 제공됩니다.
> **DataHub Cloud Observe**에 대해 더 알아보거나 체험해 보고 싶다면 [웹사이트를 방문](https://datahub.com/products/data-observability/)하세요.

## 소개

데이터 웨어하우스의 핵심 테이블에 예고 없이 컬럼이 추가, 제거 또는 변경된 경험이 있으신가요?
이로 인해 다운스트림 테이블, 뷰, 대시보드, 데이터 파이프라인 또는 AI 모델이 손상된 적이 있으신가요?

Snowflake, Redshift, BigQuery의 중요한 테이블 구조가 변경되어 테이블의 다운스트림 소비자의 기대를 깨뜨리는 이유는 다양합니다.

데이터 담당자가 다른 누구보다 먼저 데이터 문제를 인식할 수 있도록 인시던트 감지 시간을 단축할 수 있다면 어떨까요? DataHub Cloud **Schema Assertions**를 통해 이것이 가능합니다.

DataHub Cloud를 통해 사용자는 테이블의 컬럼과 데이터 유형에 대한 기대치를 정의하고, 이를 시간에 따라 모니터링하고 검증하며, 주요 변경이 발생했을 때 알림을 받을 수 있습니다.

이 문서에서는 Schema Assertions 모니터링의 기본 사항(정의, 구성 방법 등)을 다루어 팀이 중요한 데이터 자산에 대한 신뢰를 구축할 수 있도록 돕겠습니다.

시작해 봅시다!

## 지원 현황

Schema Assertions는 현재 일반 수집 프로세스를 통해 schema를 제공하는 모든 데이터 소스를 지원합니다.

## Schema Assertion이란?

**Schema Assertion**은 특정 테이블의 컬럼과 데이터 유형을 모니터링하는 데 사용되는 데이터 품질 규칙입니다.
테이블에 "필수" 컬럼 집합과 예상 유형을 정의하고, 변경이 발생했을 때 실패한 assertion을 통해 알림을 받을 수 있습니다.

이 유형의 assertion은 직접 제어할 수 없는 테이블의 구조를 모니터링하려는 경우에 특히 유용합니다. 예를 들어, 업스트림 애플리케이션의 ETL 프로세스 결과 또는 서드파티 데이터 벤더가 제공하는 테이블 등이 해당됩니다. 잠재적으로 문제가 될 schema 변경이 발생하는 즉시 알림을 받아 다운스트림 자산에 부정적인 영향을 미치기 전에 대처할 수 있습니다.

### Schema Assertion의 구조

**Schema Assertions**는 기본적으로 몇 가지 중요한 구성 요소로 이루어집니다:

1. **조건 유형**
2. **예상 컬럼** 집합

이 섹션에서 각각에 대한 개요를 설명합니다.

#### 1. 조건 유형

**조건 유형**은 Assertion이 **실패**하는 조건을 정의합니다. 더 구체적으로, _예상_ 컬럼과 schema에서 실제로 발견된 _실제_ 컬럼을 비교하여 데이터 품질 검사의 통과 또는 실패 상태를 결정하는 방법을 결정합니다.

지원되는 조건 유형 목록:

- **Contains**: 실제 schema에 예상 컬럼과 해당 유형이 모두 포함되지 않으면 assertion이 실패합니다.
- **Exact Match**: 실제 schema가 예상 컬럼과 해당 유형과 정확히 일치하지 않으면 assertion이 실패합니다. 추가 컬럼은 허용되지 않습니다.

Schema Assertions는 기본 테이블의 schema 변경이 감지될 때마다 평가됩니다.
또한 끄기 스위치도 있습니다: 시작(재생) 또는 중지(일시 정지) 버튼을 눌러 언제든지 시작하거나 중지할 수 있습니다.

#### 2. 예상 컬럼

**예상 컬럼**은 테이블에서 _실제로_ 발견된 컬럼과 비교하는 데 사용해야 하는 컬럼 **이름** 및 고수준 **데이터 유형** 집합입니다. 기본적으로 예상 컬럼 집합은 테이블에서 현재 발견된 컬럼 집합에서 파생됩니다. 이를 통해 클릭 몇 번으로 테이블의 현재 schema를 "동결" 또는 "잠금"할 수 있습니다.

각 "예상 컬럼"은 다음으로 구성됩니다:

1. **Name**: 테이블에 존재해야 하는 컬럼의 이름. 중첩 컬럼은 중첩 컬럼에 대한 점 구분 경로를 제공하여 평탄화된 방식으로 지원됩니다. 예를 들어, `user.id`는 중첩 컬럼 `id`입니다.
   복잡한 배열 또는 맵의 경우, 배열 또는 맵의 요소에 있는 각 필드는 점 구분 컬럼으로 처리됩니다.
   기본 배열 또는 맵의 오브젝트 특정 유형 확인은 현재 지원되지 않습니다. 비교는 현재 대소문자를 구분하지 않습니다.

2. **Type**: 테이블의 컬럼의 고수준 데이터 유형. 이 유형은 의도적으로 "고수준"으로 설정되어 있어 불필요하게 assertion이 실패할 위험 없이 일반적인 컬럼 확장 작업을 허용합니다. 예를 들어 `varchar(64)`와 `varchar(256)`는 모두 동일한 고수준 "STRING" 유형으로 해석됩니다. 현재 지원되는 데이터 유형 집합은 다음과 같습니다:

   - String
   - Number
   - Boolean
   - Date
   - Timestamp
   - Struct
   - Array
   - Map
   - Union
   - Bytes
   - Enum

## Schema Assertion 생성

### 사전 요구 사항

- **권한**: DataHub에서 특정 entity에 대한 Schema Assertions를 생성하거나 삭제하려면 해당 entity에 대해 `Edit Assertions`, `Edit Monitors` 권한이 부여되어야 합니다. 이 권한은 기본적으로 `Asset Owners - Metadata Policy`의 일환으로 Entity 소유자에게 부여됩니다.

이러한 사전 조건이 갖춰지면 Schema Assertions를 생성할 준비가 된 것입니다!

### 단계

1. 모니터링할 테이블로 이동합니다
2. **Quality** 탭을 클릭합니다

<p align="left">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/freshness/profile-validation-tab.png"/>
</p>

3. **+ Create Assertion**을 클릭합니다

<p align="left">
  <img width="45%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/schema/assertion-builder-choose-type.png"/>
</p>

4. **Schema**를 선택합니다

5. **조건 유형**을 선택합니다.

6. 실제 컬럼 집합과 지속적으로 비교될 **예상 컬럼**을 정의합니다. 기본값은 테이블의 현재 컬럼으로 설정됩니다.

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/schema/assertion-builder-config.png"/>
</p>

7. assertion이 통과하거나 실패할 때 취해야 할 작업을 구성합니다

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/assertion-builder-actions.png"/>
</p>

- **Raise incident**: Custom SQL Assertion이 실패할 때마다 해당 테이블에 대한 새 DataHub 인시던트를 자동으로 발생시킵니다. 이는 테이블이 사용하기에 부적합함을 나타낼 수 있습니다. **Settings**에서 Slack 알림을 구성하여 Assertion 실패로 인해 인시던트가 생성될 때 알림을 받으세요.

- **Resolve incident**: 이 Custom SQL Assertion의 실패로 인해 발생한 인시던트를 자동으로 해결합니다. 다른 인시던트에는 영향을 미치지 않습니다.

**Next**를 클릭합니다.

7. (선택 사항) assertion에 대한 **설명**을 추가합니다. 이는 assertion에 대한 사람이 읽을 수 있는 설명입니다. 제공하지 않으면 자동으로 생성됩니다.

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/assertion-builder-description.png"/>
</p>

8. **Save**를 클릭합니다.

이제 DataHub가 테이블의 Schema Assertion 모니터링을 시작합니다.

assertion이 실행되면 성공 또는 실패 상태를 확인할 수 있습니다:

<p align="left">
  <img width="45%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/schema/assertion-results.png"/>
</p>

## Schema Assertion 중지

assertion 평가를 일시적으로 중지하려면:

1. assertion이 있는 테이블의 **Quality** 탭으로 이동합니다
2. **Schema**를 클릭하여 Schema Assertion을 엽니다
3. "Stop" 버튼을 클릭합니다.

<p align="left">
  <img width="25%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/stop-assertion.png"/>
</p>

assertion을 재개하려면 **Start**를 클릭하세요.

<p align="left">
  <img width="25%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/start-assertion.png"/>
</p>

## API를 통한 Schema Assertions 생성

DataHub에서 특정 entity에 대한 Assertions 및 Monitors를 생성하거나 삭제하려면 API를 통해 schema assertion을 생성하기 위해 `Edit Assertions` 및 `Edit Monitors` 권한이 필요합니다.

#### GraphQL

Schema Assertions를 생성하려면 `upsertDatasetSchemaAssertionMonitor` mutation을 사용하세요.

##### 예시

특정 컬럼 집합의 존재를 확인하는 Schema Assertion을 생성하려면:

```graphql
mutation upsertDatasetSchemaAssertionMonitor {
  upsertDatasetSchemaAssertionMonitor(
    input: {
      entityUrn: "<urn of the table to be monitored>"
      assertion: {
        compatibility: SUPERSET # 예상 필드(다음에 제공)와 실제 컬럼을 비교하는 방법
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

지원되는 호환성 유형은 `EXACT_MATCH` 및 `SUPERSET`(Contains)입니다.

동일한 엔드포인트에 assertion urn 입력을 제공하여 기존 Schema Assertion을 업데이트할 수 있습니다. `assertionUrn` 필드를 추가하기만 하면 됩니다:

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
