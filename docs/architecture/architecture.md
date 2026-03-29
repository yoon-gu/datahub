---
title: "DataHub 아키텍처 개요"
---

# DataHub 아키텍처 개요

DataHub는 현대적인 데이터 스택을 위해 구축된 [3세대](https://engineering.linkedin.com/blog/2020/datahub-popular-metadata-architectures-explained) 데이터 카탈로그로, 데이터 발견, 협업, 거버넌스, 그리고 종단간 관찰 가능성을 지원합니다. DataHub는 모델 우선(model-first) 철학을 채택하여 서로 다른 도구 및 시스템 간의 상호운용성을 확보하는 데 초점을 맞춥니다.

아래 그림은 DataHub의 고수준 아키텍처를 설명합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/datahub-architecture.png"/>
</p>

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/saas/DataHub-Architecture.png"/>
</p>

아키텍처를 구성하는 컴포넌트에 대한 더 자세한 내용은 [컴포넌트](../components.md)를 확인하세요.

## 아키텍처 주요 특징

DataHub 아키텍처에는 세 가지 주요 특징이 있습니다.

### 메타데이터 모델링의 스키마 우선 접근 방식

DataHub의 메타데이터 모델은 [직렬화 독립적 언어](https://linkedin.github.io/rest.li/pdl_schema)를 사용하여 설명됩니다. [REST](../../metadata-service)와 [GraphQL API](../../datahub-web-react/src/graphql) 모두 지원됩니다. 또한 DataHub는 Kafka를 통해 메타데이터 변경 사항을 전달하고 구독하기 위한 [AVRO 기반 API](../../metadata-events)를 지원합니다. [로드맵](../roadmap.md)에는 코드 없이 메타데이터 모델을 편집하는 기능을 지원하는 마일스톤이 포함되어 있어, 타입이 지정된 API의 모든 이점을 유지하면서 더욱 편리한 사용이 가능해질 예정입니다. 메타데이터 모델링에 대한 내용은 [메타데이터 모델링][metadata modeling]을 참조하세요.

### 스트림 기반 실시간 메타데이터 관리 플랫폼

DataHub의 메타데이터 인프라는 스트림 지향으로 설계되어, 메타데이터 변경 사항이 플랫폼 내에서 수 초 내에 전달되고 반영됩니다. 또한 DataHub의 메타데이터에서 발생하는 변경 사항을 구독할 수 있어, 실시간 메타데이터 기반 시스템을 구축할 수 있습니다. 예를 들어, 이전에는 모든 사용자가 읽을 수 있었던 dataset에 PII가 포함된 새 schema 필드가 추가되는 것을 감지하고 해당 dataset을 액세스 제어 검토를 위해 잠그는 액세스 제어 시스템을 구축할 수 있습니다.

### 연합(Federated) 메타데이터 서빙

DataHub는 오픈소스 저장소의 일부로 단일 [메타데이터 서비스(GMS)](../../metadata-service)를 제공합니다. 그러나 서로 다른 팀이 소유하고 운영하는 연합 메타데이터 서비스도 지원합니다. 실제로 LinkedIn이 DataHub를 내부적으로 운영하는 방식이 바로 이것입니다. 연합 서비스는 Kafka를 통해 중앙 검색 인덱스 및 그래프와 통신하여, 분리된 메타데이터 소유권을 유지하면서도 글로벌 검색 및 발견을 지원합니다. 이러한 아키텍처는 [data mesh](https://martinfowler.com/articles/data-monolith-to-mesh.html)를 구현하는 기업에 매우 적합합니다.

[metadata modeling]: ../modeling/metadata-model.md
[PDL]: https://linkedin.github.io/rest.li/pdl_schema
[metadata architectures blog post]: https://engineering.linkedin.com/blog/2020/datahub-popular-metadata-architectures-explained
[datahub-serving]: metadata-serving.md
[datahub-ingestion]: metadata-ingestion.md
[react-frontend]: ../../datahub-web-react/README.md
