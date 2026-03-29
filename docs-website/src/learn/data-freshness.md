---
title: "데이터 최신성 보장: 왜 중요하고 어떻게 달성할까"
description: 최신 데이터 유지의 중요성, 관련 과제, 그리고 SLA를 충족하기 위해 데이터를 최신 상태로 유지하는 방법을 탐색합니다.
tags: ["Data Freshness", "Use Case", "For Data Engineers"]
image: /img/learn/use-case-data-freshness.png
hide_table_of_contents: false
audience: ["Data Engineers"]
date: 2024-06-03T01:00
---

# 데이터 최신성 보장: 왜 중요하고 어떻게 달성할까

최신 데이터 유지의 중요성, 관련 과제, 그리고 SLA를 충족하기 위해 데이터를 최신 상태로 유지하는 방법을 탐색합니다.

<!--truncate-->

## 소개

고객 경험을 직접 지원하는 테이블이나 머신러닝(ML) 모델을 오래된 데이터로 인해 납기가 지연된 경험이 있으신가요? 시의적절한 데이터를 보장하는 것은 이러한 미션 크리티컬 제품의 효율성과 신뢰성을 유지하는 데 필수적입니다. 이 글에서는 데이터 최신성의 중요성, 관련 과제, 그리고 DataHub가 데이터 최신성 SLA를 일관되게 충족하는 데 어떻게 도움을 줄 수 있는지 살펴보겠습니다.

## 데이터 최신성이란 무엇인가요?

데이터 최신성은 테이블과 ML 모델을 구축하는 데 사용되는 데이터의 적시성과 완전성을 말합니다. 구체적으로, 최신성은 어떤 이벤트가 *실제로 발생한* 시점과 그 이벤트의 기록이 dataset이나 AI 모델 학습에 반영되는 시점 간의 시간 차이로 측정할 수 있습니다.

구체적인 예를 들어보겠습니다. 티셔츠를 판매하는 전자상거래 사업을 운영한다고 가정해 봅시다. 사용자가 구매를 완료하기 위해 최종 "구매" 버튼을 클릭하면 이 상호작용이 기록되어 결국 데이터 웨어하우스의 통합된 "click_events" 테이블에 저장됩니다. 이 경우 데이터 최신성은 실제 클릭이 수행된 시점과 해당 클릭 기록이 데이터 웨어하우스에 저장된 시점을 비교하여 측정할 수 있습니다. 실제로 최신성은 대상 테이블, 모델 또는 기타 데이터 제품이 새 데이터로 업데이트되는 시점에 대해 이벤트 시간, 수집 시간 또는 기타 기준점 등 어떤 기준점과도 비교하여 측정할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/blogs/data-freshness/freshness-concept.png"/>
 <br />
  <i style={{color:"grey"}}>데이터 최신성</i>
</p>

데이터 파이프라인은 종종 가용성 지연 또는 데이터 최신성 SLA라는 잘 정의된 기준을 충족하도록 설계되며, 이 유형의 합의에 따라 데이터 파이프라인이 실행되는 방식과 시기가 결정됩니다.

현대 데이터 환경에서 데이터를 최신 상태로 유지하는 것은 일상적인 회사 결정을 이끄는 보고 대시보드부터 개인화되고 동적인 데이터 또는 AI 기반 제품 경험까지 고품질 데이터 제품을 구축하는 데 필수적입니다.

## 데이터 최신성이 왜 중요한가요?

많은 조직에서 최신 데이터는 '있으면 좋은' 것 이상의 의미를 갖습니다.

가격 예측이나 사기 탐지에 사용되는 것과 같은 미션 크리티컬 ML 모델은 정확한 예측을 위해 최신 데이터에 크게 의존합니다. 이러한 모델 업데이트의 지연은 매출 손실과 회사 평판 손상으로 이어질 수 있습니다.

추천 기능과 같은 고객 대면 데이터 제품도 고객이 가장 최신의 관련 개인화된 정보를 받을 수 있도록 시의적절한 업데이트가 필요합니다. 데이터 최신성 지연은 고객 불만, 사용자 이탈 및 신뢰 손실로 이어질 수 있습니다.

### 조직을 위한 주요 고려 사항

**중요한 데이터 및 ML 모델:**

조직에서 미션 크리티컬 dataset과 ML 모델의 적시성을 유지하는 데 어려움을 겪은 사례를 기억하실 수 있나요? 조직이 구체적인 제품 경험, 규정 준수 감사 또는 고품질 일상적 의사결정을 위해 데이터에 의존한다면 오래된 데이터는 매출과 고객 만족도에 상당한 영향을 미칠 수 있습니다. 어떤 dataset과 모델이 운영에 가장 중요한지 파악하고 지연의 비즈니스 영향을 정량화하는 것을 고려해 보세요.

**영향 파악 및 대응:**

데이터는 고도로 상호 연결되어 있기 때문에 데이터 최신성 지연은 특히 조직에 문제를 신속하게 파악하고 해결하는 강력한 시스템이 없는 경우 연쇄적인 문제로 이어질 수 있습니다. 조직은 이러한 사고를 어떻게 우선순위를 정하고 관리하나요? 근본 원인을 신속하게 파악하고 해결하는 프로세스는 매출과 평판에 대한 부정적인 영향을 최소화하는 데 필수적입니다.

**자동화된 최신성 모니터링:**

데이터 최신성 문제가 오랫동안 감지되지 않는 경우, 핵심 테이블과 AI 모델에 대한 이러한 문제의 감지를 자동화하여 팀이 문제가 발생했을 때 가장 먼저 알 수 있도록 할 기회가 있을 수 있습니다.

## 데이터 최신성을 보장하는 방법

데이터 최신성을 보장하는 것은 여러 모범 사례와 전략을 포함합니다. 다음은 이를 달성하는 방법입니다:

### 모범 사례 및 전략

**데이터 Lineage 추적:**

데이터 lineage 추적을 활용하여 시스템을 통해 흐르는 데이터에 대한 조감도 - 조직 내 데이터 공급망의 그림 - 를 확립하세요. 이는 지연이 발생하는 핫스팟을 정확히 찾아내고 효과적인 대응을 조율하기 위해 이러한 지연의 전체적인 영향을 이해하는 데 도움이 됩니다.

**자동화 및 모니터링:**

자동화된 최신성 모니터링을 구현하여 문제를 신속하게 감지하고 해결하세요. 이를 통해 수동 디버깅의 필요성이 줄어들고 더 빠른 대응 시간이 가능합니다. 또한 가장 중요한 에셋을 대상으로 안심감을 높이는 데 도움이 됩니다.

**사고 관리:**

데이터 최신성 문제를 효과적으로 우선순위를 정하고 해결하기 위한 명확한 사고 관리 프로토콜을 수립하세요. 여기에는 시의적절한 개입을 위한 알림 및 경고 설정, 그리고 문제 발생 시 (하위 스트림의 이해관계자까지 포함한) 모든 이해관계자를 포함하는 광범위한 커뮤니케이션 전략이 포함됩니다.

### 대안

Slack과 같은 도구를 사용하는 수동 조사 및 커뮤니케이션은 문제를 분류하는 데 도움이 될 수 있지만, 최신성과 관련된 데이터 품질 문제를 해결하는 데 시간이 많이 걸리고 비효율적이며 비공식적인 프로세스로 이어지는 경우가 많아 결국 더 낮은 품질의 결과물로 이어집니다. 전용 데이터 모니터링 도구를 통한 자동화된 최신성 사고 감지 및 구조화된 사고 관리는 데이터 최신성 문제를 감지, 커뮤니케이션 및 해결하기 위한 단일 장소를 제공하여 상황을 개선하는 데 도움이 됩니다.

### DataHub가 어떻게 도움이 되나요?

DataHub는 데이터 최신성 과제를 해결하기 위해 설계된 포괄적인 기능을 제공합니다:


**[엔드-투-엔드 데이터 Lineage](https://docs.datahub.com/docs/features/feature-guides/lineage) 및 [영향 분석](https://docs.datahub.com/docs/act-on-metadata/impact-analysis):** 조직 내 데이터 흐름을 쉽게 추적하여 지연을 신속하게 파악, 디버그 및 해결합니다.
<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/blogs/data-freshness/lineage.png"/>
 <br />
  <i style={{color:"grey"}}>데이터 Lineage</i>
</p>


**최신성 모니터링 및 경고:** 핵심 dataset의 업데이트를 사전에 모니터링하여 데이터 최신성 문제가 발생했을 때 자동으로 감지하고 경고하여 시의적절한 업데이트를 보장합니다. **DataHub Cloud 전용**으로 제공되는 [Assertions](https://docs.datahub.com/docs/managed-datahub/observe/assertions) 및 [Freshness Assertions](https://docs.datahub.com/docs/managed-datahub/observe/freshness-assertions)를 확인하세요.

<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/blogs/data-freshness/freshness-assertions.png"/>
 <br />
  <i style={{color:"grey"}}>Freshness Assertions 결과</i>
</p>


<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/blogs/data-freshness/smart-assertions.png"/>
 <br />
  <i style={{color:"grey"}}>스마트 Assertions는 기본적으로 감사 로그를 사용하여 테이블 히스토리에 기반한 주기로 변경 사항을 확인합니다.</i>
</p>


**[사고 관리](https://docs.datahub.com/docs/incidents/incidents)**: 데이터 사고 관리를 중앙화하고 모든 관련 이해관계자에 대한 데이터 최신성 문제를 효과적으로 분류, 우선순위 지정, 커뮤니케이션 및 해결하기 시작하세요. [구독 및 알림](https://docs.datahub.com/docs/managed-datahub/subscription-and-notification) 기능도 확인하세요.

<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/blogs/data-freshness/incidents.png"/>
</p>


이러한 솔루션을 구현하면 핵심 dataset과 모델이 항상 최신 상태를 유지하여 조직 내 중요한 사용 사례에 대한 관련성, 정확성 및 신뢰성을 유지할 수 있습니다.

## 결론

데이터 최신성 보장은 중요한 dataset과 AI/ML 모델의 성능과 신뢰성을 위해 필수적입니다. 데이터 최신성의 중요성을 이해하고 모범 사례와 자동화된 솔루션을 구현함으로써 지연을 효과적으로 관리하고 완화하여 매출과 평판을 보호할 수 있습니다. DataHub는 이를 달성하는 데 도움을 주기 위해 설계되었으며, 데이터를 최신 상태로 유지하고 운영을 원활하게 유지하는 데 필요한 도구와 기능을 제공합니다.
