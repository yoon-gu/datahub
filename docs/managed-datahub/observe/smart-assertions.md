---
description: 이 페이지에서는 Smart Assertions(AI 이상 탐지)에 대한 개요를 제공합니다
---

import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Smart Assertions (AI 이상 탐지) ⚡

<FeatureAvailability saasOnly />

## Smart Assertions이란?

Smart Assertions는 데이터의 과거 패턴을 학습하고 '정상'이 어떤 모습인지 예측하는 이상 탐지 모니터입니다. 계절성을 포함하여 다양한 데이터 트렌드를 처리할 수 있는 정교한 ML 파이프라인으로 구동됩니다.

<p align="left">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/smart-assertion-example.png"/>
</p>

## Smart Assertions를 어떻게 생성하나요?

현재 4가지 유형의 assertions에 대해 Smart Assertions를 생성할 수 있습니다. 각각에 대해 자세히 알아보려면 아래의 링크를 클릭하세요:

1. [Volume](./volume-assertions.md#anomaly-detection-with-smart-assertions-)
2. [Freshness](./freshness-assertions.md#anomaly-detection-with-smart-assertions-)
3. [Column Metrics](./column-assertions.md#anomaly-detection-with-smart-assertions-)
4. [Custom SQL](./custom-sql-assertions.md#anomaly-detection-with-smart-assertions-)

데이터 상태 페이지의 [모니터링 규칙](/docs/managed-datahub/observe/data-health-dashboard.md#monitoring-rules)을 사용하여 Smart Assertions를 대규모로 생성할 수도 있습니다. 모니터링 규칙을 통해 검색 조건(예: 도메인, 플랫폼, schema)을 정의하고 일치하는 모든 dataset에 Freshness, Volume, Schema 이상 탐지 모니터를 자동으로 적용할 수 있으며, 새로운 dataset이 추가되면 자동으로 포함됩니다.

## 시계열 버킷팅

Smart Assertions는 일별 또는 주별 세분성으로 데이터 품질을 평가하도록 **시계열 버킷팅**으로 구성할 수 있습니다. 매번 전체 테이블을 확인하는 대신, assertion이 타임스탬프 컬럼을 사용하여 행을 시간 버킷으로 분할하고 각 버킷을 독립적으로 평가합니다.

이는 AI 모델이 "월요일은 항상 volume이 높다" 또는 "주말 null count는 일반적으로 낮다"와 같은 패턴을 학습할 수 있어 Smart Assertions에서 특히 강력하며, 더 정확한 이상 탐지로 이어집니다.

시계열 버킷팅은 다음을 지원합니다:

- [Smart Volume Assertions](./volume-assertions.md#time-series-bucketing)
- [Smart Column Metric Assertions](./column-assertions.md#time-series-bucketing-for-column-metric-assertions)

## Assertion 이력 보정

시계열 버킷팅으로 Smart Assertion을 생성할 때 AI 모델이 첫날부터 정확한 예측을 할 수 있도록 충분한 컨텍스트를 가질 수 있게 **과거 데이터를 보정**할 수 있습니다. 보정 없이는 모델이 이상을 안정적으로 감지하기 전에 예약된 평가를 통해 충분한 데이터 포인트를 축적하는 데 며칠 또는 몇 주가 걸릴 수 있습니다.

보정이 활성화되면 시스템이 과거 데이터를 위해 웨어하우스에 쿼리하고 즉시 assertion의 지표 이력을 채웁니다. 이는 데이터의 계절성 패턴을 완전히 인식하여 처음부터 의미 있는 이상 탐지 임계값을 얻을 수 있음을 의미합니다.

보정 작동 방식, 구성 방법, 실패한 보정 재시도 방법에 대한 자세한 내용은 전용 [Assertion 이력 보정](./assertion-backfill.md) 페이지를 참조하세요.

<div align="center"><iframe width="640" height="444" src="https://www.loom.com/embed/61a201aea8464f58826c965fdbfbe255" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>

## Smart assertion 품질 개선

두 가지 주요 방법으로 예측을 개선할 수 있습니다:

1. 튜닝
2. 이상 피드백

### 튜닝

Assertion 프로필의 **Tune Predictions** 버튼이나 **Settings 탭**을 통해 접근할 수 있는 3가지 주요 작업으로 대부분의 Smart Assertions를 수정할 수 있습니다 - 올바른 학습 데이터, 민감도 조정, 되돌아보기 윈도우 늘리기.

<div align="center"><iframe width="560" height="315" src="https://www.loom.com/embed/880ce4785b944a50a8662557e2ccf733?sid=192afcf0-7930-4734-9628-dba4b6717495" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>

**제외 윈도우**
학습 데이터에서 제외할 시간 윈도우를 설정합니다. 알려진 유지보수 윈도우나 기타 다운타임 기간, 계절적 급증(예: 휴일) 또는 정상적인 데이터 트렌드를 대표하지 않는 다른 윈도우를 제외하는 데 유용합니다.

**민감도**
민감도가 높을수록 데이터에 더 엄밀하게 맞춰집니다. 민감도가 낮을수록 이상으로 표시되기 전에 더 많은 데이터 변동을 허용합니다.

**학습 데이터 되돌아보기 윈도우**
ML 모델이 예측을 생성하기 위해 학습 데이터를 수집할 때 되돌아보는 일수입니다. 너무 크면 더 이상 현재 트렌드의 일부가 아닌 오래된 데이터를 포함할 수 있습니다. 너무 짧으면 주요 계절적 패턴을 놓칠 수 있습니다. 제외 윈도우와 함께 이것을 활용하여 예측 품질을 개선할 수 있습니다.

### 이상 피드백

#### 오탐 알림

smart assertion이 이상을 표시할 때 결과 점 위에 마우스를 올려 `Mark as Normal`을 선택할 수 있습니다. 이렇게 하면 해당 데이터 포인트가 학습 세트에 포함되고 모델이 더 이상 그러한 데이터 포인트를 이상으로 표시하지 않도록 조정됩니다.

**그러나** 이상이 실제로 예상되는 경우가 있습니다. 예를 들어, 데이터가 갑자기 증가했지만 **이것이 앞으로의 새로운 정상이 될 경우**, `Train as new Normal` 옵션을 선택하는 것을 권장합니다. 이렇게 하면 이 실행 이벤트 이전의 모든 데이터에 제외 윈도우가 추가되고 smart assertion이 이 시점부터의 데이터 포인트를 기반으로 학습을 시작합니다.

#### 누락된 알림

Smart Assertions에서 이상이 탐지되지 않은 경우 다음과 같은 몇 가지 조치를 권장합니다:

1. `Mark as Anomaly`를 클릭하여 이 특정 데이터 포인트를 이상으로 표시할 수 있습니다. 이렇게 하면 해당 데이터 포인트가 학습 데이터에서 제외됩니다.
2. assertion에서 **Tune Predictions**를 클릭한 다음 학습 세트에서 모든 "불량한" 과거 기간을 제외합니다(`Exclusion Window` 추가). 이는 오래된 인시던트나 일회성 이벤트가 모델의 "정상" 개념을 오염시키는 경우에 유용합니다.
3. 마지막으로 **Settings 탭**에서 assertion의 민감도를 높이면 허용 가능한 값의 범위가 줄어듭니다.

<p align="left">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/shared/smart-assertion-feedback.png"/>
</p>
