---
description: 이 페이지에서는 DataHub Column Assertions 사용 방법에 대한 개요를 제공합니다
---

import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Column Assertions

<FeatureAvailability saasOnly />

> **Column Assertions** 기능은 DataHub Cloud의 **DataHub Cloud Observe** 모듈의 일부로 제공됩니다.
> **DataHub Cloud Observe**에 대해 더 알아보거나 체험해 보고 싶다면 [웹사이트를 방문](https://datahub.com/products/data-observability/)하세요.

## 소개

예고도 없이 중요한 웨어하우스 테이블 컬럼이 급격하게 변경된 경험이 있으신가요? 아마도 null 값의 수가 갑자기 급증하거나, 고정된 값 집합에 새로운 값이 추가되었을 수 있습니다. 그렇다면 처음에 어떻게 알게 되셨나요? 내부 보고 대시보드를 보던 누군가가, 또는 더 심하게는 제품을 사용하는 사용자가 수치가 이상해 보인다며 경보를 울렸을 것입니다.

Snowflake, Redshift, BigQuery, Databricks 테이블의 중요한 컬럼이 변경되는 이유는 다양합니다 - 애플리케이션 코드 버그, 새 기능 출시 등. 이러한 변경은 종종 보고 대시보드나 데이터 기반 제품 기능과 같은 주요 다운스트림 데이터 제품 구축에 사용되는 데이터에 대한 중요한 가정을 깨뜨립니다.

데이터 담당자가 다른 누구보다 먼저 데이터 문제를 인식할 수 있도록 인시던트 감지 시간을 단축할 수 있다면 어떨까요? DataHub Cloud Column Assertions를 통해 이것이 가능합니다.

DataHub Cloud를 사용하면 컬럼의 각 값이 특정 제약 조건을 충족하는지 확인하는 **Column Value** assertion과 컬럼에서 계산된 지표가 기대치에 부합하는지 확인하는 **Column Metric** assertion을 정의할 수 있습니다. 문제가 발생하는 즉시 데이터 문제가 더 큰 인시던트로 번지기 전에 팀이 가장 먼저 알게 됩니다.

이 가이드에서는 Column Assertions의 기본 사항(정의, 구성 방법 등)을 다루어 팀이 중요한 데이터 자산에 대한 신뢰를 구축할 수 있도록 돕겠습니다.

자세히 살펴봅시다!

## 지원 현황

Column Assertions는 현재 다음을 지원합니다:

1. Snowflake
2. Redshift
3. BigQuery
4. Databricks
5. DataHub Dataset Profile Metrics (수집을 통해 수집됨)

DataHub Cloud의 **Ingestion** 탭에서 선택한 데이터 플랫폼에 대한 수집 소스가 _반드시_ 구성되어 있어야 합니다.

> DataHub CLI를 사용하여 웨어하우스에 연결하는 경우 Column Assertions는 아직 지원되지 않습니다.

## Column Assertion이란?

**Column Assertion**은 데이터 웨어하우스 테이블의 특정 컬럼에서 예상치 못한 변화를 모니터링하는 데 사용되는 고도로 구성 가능한 데이터 품질 규칙입니다.

Column Assertions는 특정 컬럼을 검증하도록 정의되며, 다음 두 가지 용도로 사용할 수 있습니다:

1. 컬럼 값이 여러 행에 걸쳐 특정 제약 조건(regex, 허용 값, 최대, 최소 등)과 일치하는지 검증하거나
2. 특정 컬럼 집계 지표가 여러 행에 걸쳐 특정 기대치와 일치하는지 검증합니다.

Column Assertions는 특히 컬럼 수준 "계약"(즉, 데이터 생산자와 소비자 간의 조율에 사용할 수 있는 특정 컬럼의 예상 내용에 대한 공식적인 사양)을 문서화하고 시행하는 데 유용합니다.

### Column Assertion의 구조

Column Assertions는 두 가지 주요 유형으로 나눌 수 있습니다: **Column Value** 및 **Column Metric** Assertions.

**Column Value Assertion**은 테이블의 특정 컬럼 값을 모니터링하고 모든 행이 특정 조건을 따르도록 보장하는 데 사용됩니다. 반면 **Column Metric Assertion**은 해당 컬럼에 대한 지표를 계산하고 해당 지표 값이 특정 조건을 따르도록 보장하는 데 사용됩니다.

기본적으로 두 유형 모두 몇 가지 중요한 구성 요소로 이루어집니다:

1. **평가 스케줄**
2. **컬럼 선택**
3. **평가 기준**
4. **행 평가 유형**

이 섹션에서 각각에 대한 개요를 설명합니다.

#### 1. 평가 스케줄

**평가 스케줄**: 지정된 웨어하우스 테이블에 대해 Column Assertion을 평가하는 빈도를 정의합니다. 일반적으로 테이블의 예상 변경 빈도에 맞게 구성해야 하지만, 요구 사항에 따라 더 낮은 빈도로 설정할 수도 있습니다. 주의 특정 요일, 시간 내의 특정 시, 또는 시간 내의 특정 분을 지정할 수도 있습니다.

#### 2. 컬럼 선택

**컬럼 선택**: Column Assertion으로 모니터링해야 할 컬럼을 정의합니다. 드롭다운에 나열된 테이블의 어떤 컬럼에서도 선택할 수 있습니다. struct/object 유형의 컬럼은 현재 지원되지 않습니다.

#### 3. 평가 기준

**평가 기준**: Column Assertion이 통과하기 위해 충족되어야 하는 조건을 정의합니다.

**Column Value Assertions**의 경우, 컬럼 값에 적용할 수 있는 연산자 집합에서 선택할 수 있습니다. 표시되는 옵션은 선택된 컬럼의 데이터 유형에 따라 달라집니다. 예를 들어 숫자형 컬럼을 선택한 경우 컬럼 값이 특정 값보다 크다는 것을 확인할 수 있습니다. 문자열 유형의 경우 컬럼 값이 특정 regex 패턴과 일치하는지 확인할 수 있습니다. 또한 NULL 값 존재 시 검사 동작을 제어할 수 있습니다. **Allow Nulls** 옵션이 _비활성화_된 경우 assertion을 평가할 때 발견된 null 값은 실패로 보고됩니다. **Allow Nulls**가 활성화된 경우 null 값은 무시되며, 컬럼 값이 null이 아닌 행에 대해서만 조건이 평가됩니다.

**Column Metric Assertions**의 경우, 일반적인 컬럼 지표 목록(MAX, MIN, MEAN, NULL COUNT 등)에서 선택한 다음 이러한 지표 값을 예상 값과 비교할 수 있습니다. 지표 목록은 선택된 컬럼의 유형에 따라 달라집니다. 예를 들어 숫자형 컬럼을 선택한 경우 컬럼의 MEAN 값을 계산한 다음 특정 숫자보다 크다고 assertion할 수 있습니다. 문자열 유형의 경우 모든 컬럼 값에 걸쳐 문자열의 MAX LENGTH를 계산한 다음 특정 숫자보다 작다고 assertion할 수 있습니다.

#### 4. 행 선택 집합

**행 선택 집합**: Column Assertion이 평가될 테이블의 행을 정의합니다. 다음 옵션에서 선택할 수 있습니다:

- **All Table Rows**: 테이블의 모든 행에 대해 Column Assertion을 평가합니다. 기본 옵션입니다. 대용량 테이블에는 적합하지 않을 수 있습니다.

- **Only Rows That Have Changed**: 마지막 assertion 평가 이후 변경된 행에 대해서만 Column Assertion을 평가합니다. 이 옵션을 선택하면 어떤 행이 변경되었는지 판단하는 데 도움이 되는 **High Watermark Column**을 지정해야 합니다. **High Watermark Column**은 날짜, 시간 또는 항상 증가하는 다른 숫자와 같이 지속적으로 증가하는 값을 포함하는 컬럼으로, 이전 평가 이후 추가된 "새 행"을 찾는 데 사용됩니다. 선택하면 이전 assertion 평가 이후 변경된 행만 찾기 위해 테이블에 쿼리가 실행됩니다.

## Column Assertion 생성

### 사전 요구 사항

1. **권한**: DataHub에서 특정 entity에 대한 Column Assertions를 생성하거나 삭제하려면 해당 entity에 대해 `Edit Assertions` 및 `Edit Monitors` 권한이 부여되어야 합니다. 이 권한은 기본적으로 `Asset Owners - Metadata Policy`의 일환으로 Entity 소유자에게 부여됩니다.

2. (선택 사항) **데이터 플랫폼 연결**: DataHub 메타데이터 대신 데이터 소스를 직접 쿼리하는 Column Assertion을 생성하려면 **Ingestion** 탭에서 데이터 플랫폼(Snowflake, BigQuery 또는 Redshift)에 대한 **수집 소스**가 구성되어 있어야 합니다.

이러한 사전 조건이 갖춰지면 Column Assertions를 생성할 준비가 된 것입니다!

### 단계

#### 1. 모니터링할 테이블로 이동합니다

#### 2. **Quality** 탭을 클릭합니다

<p align="left">
  <img width="90%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/freshness/profile-validation-tab.png"/>
</p>

#### 3. **+ Create Assertion**을 클릭합니다

#### 4. **'Column'**을 선택합니다

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/column/assertion-builder-column-choose-type.png"/>
</p>

#### 5. 평가 **스케줄**을 구성합니다.

이는 assertion이 통과 또는 실패 결과를 생성하기 위해 평가되는 빈도이며 컬럼 값이 확인되는 시간입니다.

#### 6. **컬럼 assertion 유형**을 구성합니다.

**Column Value** 또는 **Column Metric** 중에서 선택할 수 있습니다.
**Column Value** assertions는 테이블의 특정 컬럼 값을 모니터링하고 모든 행이 특정 조건을 따르도록 보장합니다. **Column Metric** assertions는 해당 컬럼에 대한 지표를 계산한 다음 해당 지표 값을 기대치와 비교합니다.

<p align="left">
  <img width="30%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/column/assertion-builder-column-assertion-type.png"/>
</p>

#### 7. **컬럼 선택**을 구성합니다.

Column Assertion으로 모니터링해야 할 컬럼을 정의합니다.
드롭다운에 나열된 테이블의 어떤 컬럼에서도 선택할 수 있습니다.

<p align="left">
  <img width="30%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/column/assertion-builder-column-field-selection.png"/>
</p>

#### 8. **평가 기준**을 구성합니다. 이 단계는 이전 단계에서 선택한 assertion 유형에 따라 달라집니다.

- **Column Value Assertions**: 컬럼 값에 적용할 수 있는 연산자 집합에서 선택할 수 있습니다. 표시되는 옵션은 선택된 컬럼의 데이터 유형에 따라 달라집니다. 예를 들어 숫자 유형의 경우 컬럼 값이 특정 값보다 큰지 확인할 수 있습니다. 문자열 유형의 경우 컬럼 값이 특정 regex 패턴과 일치하는지 확인할 수 있습니다. 또한 컬럼의 null 값 동작을 제어할 수 있습니다. **Allow Nulls** 옵션이 _비활성화_된 경우 assertion을 평가할 때 발견된 null 값은 실패로 보고됩니다. 참고로 Smart Assertions는 현재 Column Value Assertions에는 지원되지 않습니다.

  또한 In Set 및 Not In Set 연산자의 경우 허용 값 집합을 제공하는 방법을 선택할 수 있습니다:

  - 정적 목록: 값 목록을 수동으로 입력합니다(예: "chicago", "new york"과 같은 도시 이름).
  - Custom SQL: 집합에 대한 가능한 값의 단일 컬럼을 반환하는 SQL 쿼리를 제공합니다. 평가 시 DataHub는 구성된 데이터 플랫폼 연결을 사용하여 이 쿼리를 실행하고 각 행의 컬럼 값을 반환된 집합과 비교합니다.

  집합에 Custom SQL 사용 시 참고 사항:

  - 쿼리는 정확히 하나의 컬럼을 반환해야 합니다. 필요한 경우 중복을 피하려면 `SELECT DISTINCT`를 사용하세요.
  - 반환된 값은 선택된 컬럼의 데이터 유형과 비교 가능해야 합니다(예: VARCHAR/STRING 컬럼의 경우 문자열, 숫자 컬럼의 경우 숫자).
  - 쿼리는 dataset에 구성된 것과 동일한 웨어하우스 연결에서 실행됩니다. 계정에 참조된 오브젝트에 대한 읽기 액세스 권한이 있는지 확인하고 완전히 정규화된 테이블 이름을 사용하세요.
  - 크거나 복잡한 쿼리는 웨어하우스의 평가 지연 및 비용에 영향을 줄 수 있습니다.

  예시(참조 테이블에서 가져온 허용 도시 값):

  ```sql
  SELECT DISTINCT city
  FROM reference_data.geo.cities
  WHERE active = TRUE
  ```

- **Column Metric Assertions**: 일반적인 지표 목록에서 선택한 다음 비교할 연산자와 값을 지정할 수 있습니다. 지표 목록은 선택된 컬럼의 데이터 유형에 따라 달라집니다. 예를 들어 숫자 유형의 경우 컬럼의 평균 값을 계산한 다음 특정 숫자보다 크다고 assertion할 수 있습니다. 문자열 유형의 경우 모든 컬럼 값의 최대 길이를 계산한 다음 특정 숫자보다 작다고 assertion할 수 있습니다. **Detect with AI** 옵션을 선택하여 Smart Assertions를 사용하여 컬럼 지표의 이상을 탐지할 수 있습니다. **Detect with AI** 옵션은 현재 **null_count**, **unique_count**, **empty_count**, **zero_count**, **negative_count** 지표에만 사용할 수 있습니다. 기타 지표(예: min, max, mean)는 고정 임계값을 사용하는 일반 Column Metric Assertions를 사용하세요.

#### 9. **행 평가 유형**을 구성합니다. Column Assertion이 평가해야 할 테이블의 행을 정의합니다.

- **All Table Rows**: 테이블의 모든 행에 대해 Column Assertion을 평가합니다. 기본 옵션입니다. 대용량 테이블에는 적합하지 않을 수 있습니다.

- **Only Rows That Have Changed**: 마지막 평가 이후 변경된 행에 대해서만 Column Assertion을 평가합니다. 이 옵션을 선택하면 어떤 행이 변경되었는지 판단하는 데 도움이 되는 **High Watermark Column**을 지정해야 합니다. **High Watermark Column**은 날짜, 시간 또는 항상 증가하는 다른 숫자와 같이 지속적으로 증가하는 값을 포함하는 컬럼입니다. 선택하면 마지막 assertion 실행 이후 변경된 행만 찾기 위해 테이블에 쿼리가 실행됩니다.

<p align="left">
  <img width="60%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/column/assertion-builder-column-row-evaluation-type.png"/>
</p>

#### 10. (선택 사항) **Advanced**를 클릭하여 Column Assertion을 추가로 사용자 정의합니다.

여기에 나열된 옵션은 이전 단계에서 선택한 assertion 유형에 따라 달라집니다.

- **Invalid Values Threshold**: **Column Value** assertions의 경우 assertion이 실패로 표시되기 전에 허용되는 유효하지 않은 값(즉, 행)의 수를 구성할 수 있습니다. 컬럼에서 제한된 수의 유효하지 않은 값을 허용하려는 경우에 유용합니다. 기본값은 0으로, assertion은 유효하지 않은 컬럼 값이 있는 행이 있으면 실패합니다.

- **Source**: **Column Metric** assertions의 경우 컬럼 지표를 얻는 데 사용될 메커니즘을 선택할 수 있습니다. **Query**는 dataset에 쿼리를 실행하여 지표를 계산합니다. 정보 스키마보다 비용이 많이 드는 테이블 쿼리가 발생합니다.
  **DataHub Dataset Profile**은 DataHub Dataset Profile 메타데이터를 사용하여 지표를 계산합니다. 가장 저렴한 옵션이지만 DataHub에 Dataset Profile이 보고되어야 합니다. 기본적으로 수집 시 DataHub에 Dataset Profile을 보고하지만 빈도가 낮을 수 있습니다. 더 빈번하고 신뢰할 수 있는 데이터를 위해 DataHub API를 통해 Dataset Profile을 보고할 수 있습니다.

- **Additional Filters**: assertion을 평가하는 데 사용될 쿼리에 추가 필터를 추가하도록 선택할 수 있습니다. 테이블의 행 일부로 assertion을 제한하려는 경우에 유용합니다. **DataHub Dataset Profile**을 **소스**로 선택한 경우 이 옵션을 사용할 수 없습니다.

#### 11. Column Assertion이 통과하거나 실패할 때 취해야 할 작업을 구성합니다

<p align="left">
  <img width="45%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/assertion-builder-actions.png"/>
</p>

- **Raise incident**: Column Assertion이 실패할 때마다 해당 테이블에 대한 새 DataHub `Column` 인시던트를 자동으로 발생시킵니다. 이는 테이블이 사용하기에 부적합함을 나타낼 수 있습니다. **Settings**에서 Slack 알림을 구성하여 Assertion 실패로 인해 인시던트가 생성될 때 알림을 받으세요.
- **Resolve incident**: 이 Column Assertion의 실패로 인해 발생한 인시던트를 자동으로 해결합니다. 다른 인시던트에는 영향을 미치지 않습니다.

#### 12. **Next**를 클릭한 다음 **Save**를 클릭합니다.

이제 DataHub가 테이블의 Column Assertion 모니터링을 시작합니다.

assertion이 실행되면 테이블의 성공 또는 실패 상태를 확인할 수 있습니다

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/column/profile-passing-column-assertions-expanded.png"/>
</p>

## Smart Assertions를 활용한 이상 탐지 ⚡

**DataHub Cloud Observe** 모듈의 일환으로 DataHub Cloud는 기본 제공 [Smart Assertions](./smart-assertions.md)도 제공합니다. 이는 수동 설정 없이 중요한 웨어하우스 테이블의 컬럼 지표에 대한 이상을 모니터링하는 데 사용할 수 있는 동적 AI 기반 Column Metric Assertions입니다.

:::note 지원 지표
Column Metrics의 Smart Assertions는 현재 **null_count**, **unique_count**, **empty_count**, **zero_count**, **negative_count**만 지원합니다. 기타 컬럼 지표(예: min, max, mean, median, stddev)는 고정 임계값을 사용하는 표준 Column Metric Assertions에는 사용할 수 있지만, 현재 **Detect with AI** 옵션으로는 사용할 수 없습니다. 다른 지표를 사용하는 기존 Smart Assertions는 정상적으로 계속 작동합니다.
:::

UI에서 모니터링할 컬럼과 지표를 선택한 다음 `Detect with AI` 옵션을 클릭하여 smart assertions를 생성할 수 있습니다:

<p align="left">
  <img width="40%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/column/column-smart-assertion.png"/>
</p>

**여러 컬럼에 대한 일괄 생성**

테이블의 여러 컬럼을 한 번에 모니터링하도록 선택하려면 Column Metric Assertion 작성 UI의 컬럼 선택기 아래에 있는 **Bulk-Create Smart Assertions** 버튼을 사용할 수 있습니다.

<iframe width="560" height="343" src="https://www.loom.com/embed/e71598c4394c4d8dba0770b8fc67ff06?sid=25326338-8a72-4382-98b5-026486233ef9" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

## Column Metric Assertions의 시계열 버킷팅

기본적으로 column metric assertions는 테이블의 모든 행 또는 변경된 행에 걸쳐 지표(예: null count, min, max)를 평가합니다. **시계열 버킷팅**을 사용하면 데이터를 시간 기반 버킷(예: 일별 또는 주별)으로 분할하고 각 버킷 내에서 컬럼 지표를 평가할 수 있습니다.

다음과 같은 경우에 유용합니다:

- 일별 또는 주별 세분성으로 컬럼 품질을 모니터링하려는 경우
- 전체 테이블을 확인하는 대신 "오늘 데이터의 null count가 급증했다"와 같은 문제를 탐지하려는 경우
- 컬럼 지표에 요일 또는 연도 시기에 따라 변동하는 계절적 패턴이 있는 경우

### 버킷팅 구성

column assertions의 시계열 버킷팅 전략은 다음으로 구성됩니다:

- **타임스탬프 컬럼**: 행을 버킷으로 분할하는 데 사용되는 날짜/시간 컬럼(예: `created_at`, `updated_at`).
- **버킷 간격**: **일별** (1 DAY) 또는 **주별** (1 WEEK).
- **시간대**: 버킷 경계에 대한 IANA 시간대. 기본값은 UTC입니다.
- **늦은 도착 유예 기간** (선택 사항): 평가 전 버킷 종료 시간 이후의 버퍼.

:::note
시계열 버킷팅이 활성화되면 평가 스케줄은 버킷 구성에서 자동으로 계산됩니다. Column Value assertions(`FIELD_VALUES` 유형)는 시계열 버킷팅을 지원하지 않으며, Column Metric assertions(`FIELD_METRIC` 유형)만 지원합니다.
:::

### UI에서 버킷팅 구성

column metric assertion 생성 시 세 가지 옵션이 있는 **Row Evaluation Type** 섹션이 표시됩니다:

<p align="left">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/bucketing/column-metric-timeseries-bucketing.png"/>
</p>

- **All Table Rows**: 테이블의 모든 행에 대해 assertion을 평가합니다(기본값).
- **Only Rows That Have Changed**: high watermark 컬럼을 사용하여 새 행만 평가합니다.
- **Rows Within a Time Bucket**: 데이터를 일별 또는 주별 시간 버킷으로 분할하고 각 버킷을 독립적으로 평가합니다.

**Rows Within a Time Bucket**을 선택하면 타임스탬프 컬럼, 버킷 크기, 시간대, 선택적 유예 기간을 구성합니다.

### Python SDK를 통한 버킷팅 구성

```python
from datahub.sdk import DataHubClient
from datahub.metadata.urns import DatasetUrn

client = DataHubClient(server="<your_server>", token="<your_token>")
dataset_urn = DatasetUrn.from_string(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.table,PROD)"
)

# 일별 버킷팅을 사용한 column metric assertion
column_assertion = client.assertions.sync_column_metric_assertion(
    dataset_urn=dataset_urn,
    column_name="price",
    metric_type="min",
    operator="greater_than_or_equal_to",
    criteria_parameters=0,
    display_name="Daily Price Min Check",
    time_bucketing_strategy={
        "timestamp_field_path": "order_date",
        "bucket_interval": {"unit": "DAY", "multiple": 1},
        "timezone": "America/Los_Angeles",
    },
    tags=["automated", "column_quality"],
    enabled=True,
)

# 주별 버킷팅과 보정을 사용한 smart column metric assertion
smart_column = client.assertions.sync_smart_column_metric_assertion(
    dataset_urn=dataset_urn,
    column_name="user_id",
    metric_type="null_count",
    display_name="Weekly Null Count Monitor",
    detection_mechanism="all_rows_query_datahub_dataset_profile",
    sensitivity="medium",
    time_bucketing_strategy={
        "timestamp_field_path": "created_at",
        "bucket_interval": {"unit": "WEEK", "multiple": 1},
    },
    backfill_config={"backfill_start_date_ms": 1704067200000},
    enabled=True,
)
```

:::info
버킷팅이 활성화된 smart column metric assertions의 경우 지표 이력을 채우기 위해 **과거 데이터 보정**을 구성할 수 있습니다. 자세한 내용은 [Assertion 이력 보정](./assertion-backfill.md)을 참조하세요.
:::

## Column Assertion 중지

assertion 평가를 일시적으로 중지하려면:

1. assertion이 있는 테이블의 **Quality** 탭으로 이동합니다
2. **Column**을 클릭하여 Column Assertion assertions를 엽니다
3. 일시 중지하려는 assertion의 "Stop" 버튼을 클릭합니다.

<p align="left">
  <img width="25%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/stop-assertion.png"/>
</p>

assertion을 재개하려면 **Start**를 클릭하세요.

<p align="left">
  <img width="25%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/start-assertion.png"/>
</p>

## API를 통한 Column Assertions 생성

내부적으로 DataHub Cloud는 두 가지 개념을 사용하여 Column Assertion 모니터링을 구현합니다:

- **Assertion**: 컬럼 지표에 대한 특정 기대치(예: "테이블의 모든 행에서 정수 컬럼의 값이 10보다 크다"). 이것은 "무엇"입니다.
- **Monitor**: 지정된 평가 스케줄에 따라 특정 메커니즘을 사용하여 Assertion을 평가하는 프로세스. 이것은 "어떻게"입니다.

DataHub에서 특정 entity에 대한 Assertions 및 Monitors를 생성하거나 삭제하려면 해당 entity에 대한 `Edit Assertions` 및 `Edit Monitors` 권한이 필요합니다.

#### GraphQL

Column Assertion을 생성하거나 업데이트하려면 `upsertDatasetColumnAssertionMonitor` mutation을 사용할 수 있습니다.

#### 예시

8시간마다 실행되는 Field Values Column Assertion 생성:

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

AI Smart Column Nullness Metric Assertion 생성:

```graphql
mutation upsertDatasetFreshnessAssertionMonitor {
  upsertDatasetFreshnessAssertionMonitor(
    input: {
      entityUrn: "<urn of entity being monitored>"
      type: FIELD_METRIC
      inferWithAI: true
      fieldMetricAssertion: {
        field: {
          path: "<name of the column to be monitored>"
          type: "NUMBER"
          nativeType: "NUMBER(38,0)"
        }
        metric: NULL_PERCENTAGE
        operator: BETWEEN
        # AI 엔진에 의해 지속적으로 덮어써지므로 여기에 어떤 값이든 제공할 수 있습니다
        parameters: {
          minValue: { value: "0", type: NUMBER }
          maxValue: { value: "0", type: NUMBER }
        }
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

동일한 엔드포인트에 assertion urn 입력을 제공하여 기존 Column Assertion 및 해당 Monitor를 업데이트할 수 있습니다.

```graphql
mutation upsertDatasetFieldAssertionMonitor {
  upsertDatasetFieldAssertionMonitor(
    assertionUrn: "<urn of assertion created in earlier query>"
    input: {
      entityUrn: "<urn of entity being monitored>"
      type: FIELD_VALUES
      fieldValuesAssertion: {
        field: {
          path: "<name of the column to be monitored>"
          type: "NUMBER"
          nativeType: "NUMBER(38,0)"
        }
        operator: GREATER_THAN_OR_EQUAL_TO
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
