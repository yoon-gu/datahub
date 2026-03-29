---
description: 이 페이지에서는 데이터 상태 대시보드에 대한 개요를 제공합니다
---

import FeatureAvailability from '@site/src/components/FeatureAvailability';

# 데이터 상태 대시보드

<FeatureAvailability saasOnly />

## 데이터 상태 대시보드란

데이터 상태 대시보드는 두 가지 중요한 사용 사례를 해결하는 것을 목표로 합니다:

1. 데이터 품질 이슈 분류
2. 전체적인 데이터 품질 커버리지 및 트렌드 이해

사이드바 내비게이션에서 접근할 수 있습니다. _Observe_ 섹션에서 찾을 수 있습니다.

<p align="left">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/data-health/overview.png"/>
</p>

## 사용 방법

### Assertions 탭

assertions를 슬라이스하는 두 가지 방법이 있습니다:

1. Assertion 기준
2. 테이블 기준

**`By Assertion` 사용 시기**

이 뷰는 assertion 실행 활동 로그를 특정 assertion이 마지막으로 실행된 시간 순으로 정렬하여 표시합니다. 데이터 품질 검사의 트렌드를 분류하고 감지하는 데 매우 유용합니다.

예를 들어, 시간 범위 필터(예: `Last 7 Days`)를 적용하고 `Results`를 `At least one failure`로 설정하면 지난 7일 동안 적어도 한 번 실패한 assertions를 빠르게 확인할 수 있습니다. 또한 실행 빈도 대비 실패 빈도를 확인할 수 있어 불안정한 검사를 빠르게 찾아 조사할 수 있습니다.

**`By Table` 사용 시기**

이 뷰는 적어도 하나의 assertion이 실행된 테이블 목록을 표시합니다. 해당 테이블에서 assertion이 마지막으로 실행된 시간 순으로 정렬됩니다. 상태 점은 해당 테이블에서 지정된 유형의 assertion의 마지막 상태를 나타냅니다.

이 뷰는 팀의 테이블 전반에 걸친 모니터링 커버리지를 이해하는 데 매우 유용합니다.

### 인시던트 탭

인시던트 탭은 활성 인시던트가 열려 있는 테이블을 표시합니다. 해당 테이블에서 인시던트 활동이 마지막으로 보고된 시간 순으로 정렬됩니다.

한눈에 특정 테이블에 열린 인시던트 수, 해당 테이블에서 마지막으로 업데이트된 인시던트, 소유자를 확인할 수 있습니다.

**곧 출시 예정:** 향후 테이블 커버리지, 해결 시간 등에 대한 유용한 통계를 제공하는 고수준 시각적 카드를 도입할 예정입니다.
또한 특정 기간 동안의 assertion 실패 타임라인 뷰도 도입할 예정입니다. 단 한 번의 시선으로 데이터 품질 실패의 트렌드를 훨씬 쉽게 감지할 수 있도록 하는 것이 목표입니다.

## 대시보드 개인화

각 팀, 심지어 개인마다 다른 데이터 하위 집합에 관심이 있을 수 있다는 것을 이해합니다.
이를 위해 대시보드를 관심 있는 특정 데이터 하위 집합으로 드릴다운하기 쉽도록 다양한 필터를 포함했습니다. 다음으로 필터링할 수 있습니다:

1. Dataset 소유자
2. Dataset 도메인
3. Dataset 태그
   ...그리고 훨씬 더 많은 것들.

또한 `By Tables` 탭과 `Incidents` 탭 모두 전역 `View`(DataHub 내비게이션 상단의 검색 바를 통해 관리됨)를 적용합니다. 따라서 팀을 위한 뷰가 이미 생성되어 있다면 이 탭들은 자동으로 보고서를 관심 있는 데이터 하위 집합으로만 필터링합니다.

<p align="left">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/data-health/view-applied.png"/>
</p>

## 모니터링 규칙

모니터링 규칙을 사용하면 검색 기반 조건을 사용하여 데이터 환경 전반에 [Smart Assertions](./smart-assertions.md)(AI 이상 탐지 모니터)를 자동으로 적용할 수 있습니다. 개별 테이블에 assertions를 수동으로 생성하는 대신, _어떤_ dataset을 모니터링할지와 _무엇을_ 모니터링할지를 설명하는 규칙을 정의하면 DataHub가 나머지를 처리합니다.

### 사전 요구 사항

모니터링 규칙을 생성하고 관리하려면 **`Manage Tests`** 플랫폼 권한이 있어야 합니다. 이 권한이 없는 경우 DataHub 관리자에게 문의하세요.

### 작동 방식

1. **검색 조건 정의** — DataHub 도메인, 데이터 플랫폼, schema, 태그 또는 검색 기준의 조합과 같은 필터를 사용하여 모니터링할 dataset을 지정합니다.
2. **assertion 유형 선택** — 일치하는 dataset에 대해 Freshness, Volume, Schema 이상 탐지 모니터링 중 하나 이상을 활성화합니다.
3. **구독 구성** — 이상이 감지될 때 귀하 또는 팀에 알림이 전송되도록 알림 구독을 설정합니다.
4. **규칙 저장** — DataHub가 현재 조건과 일치하는 모든 dataset에 자동으로 Smart Assertions를 생성합니다.

**데이터 상태 대시보드**에서 **Monitoring Rules** 버튼을 클릭하여 모니터링 규칙을 생성하고 관리할 수 있습니다.

<div align="center"><iframe width="561" height="409" src="https://www.loom.com/embed/6b372ee252e840dbb504cc2561e88712" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>

### 자동 수명주기 관리

모니터링 규칙은 데이터 환경이 변화함에 따라 지속적으로 평가됩니다:

- 조건과 **일치하는 새 dataset**에는 자동으로 Smart Assertions가 생성됩니다.
- 조건과 **더 이상 일치하지 않는 dataset**에는 해당 규칙에 의해 생성된 Smart Assertions가 중지되고 제거됩니다.
- **규칙을 중지하면** 해당 규칙에 의해 생성된 모든 Smart Assertions가 중지됩니다.

:::note 구독 동작
모니터링 규칙에 의해 생성된 구독은 dataset이 조건에서 벗어나거나 규칙이 중지될 때 제거되지 **않습니다**. 이는 모니터링 범위가 변경된 후에도 진행 중인 알림이나 인시던트에 대한 가시성을 유지할 수 있게 합니다. 필요한 경우 구독을 독립적으로 관리할 수 있습니다.
:::
