---
title: "Ingestion 프레임워크"
---

# 메타데이터 Ingestion 아키텍처

DataHub는 푸시(push), 풀(pull), 비동기(asynchronous), 동기(synchronous) 모델을 모두 지원하는 매우 유연한 ingestion 아키텍처를 제공합니다.
아래 그림은 원하는 시스템을 DataHub에 연결하기 위한 모든 옵션을 설명합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion-architecture.png"/>
</p>

## Metadata Change Proposal: 핵심 구성 요소

Ingestion의 핵심 구성 요소는 [Metadata Change Proposal]로, 조직의 메타데이터 그래프에 대한 메타데이터 변경 요청을 나타냅니다.
Metadata Change Proposal은 소스 시스템으로부터의 확장 가능한 비동기 게시를 위해 Kafka를 통해 전송될 수 있습니다. 또한 동기식 성공/실패 응답을 받기 위해 DataHub 서비스 계층이 노출하는 HTTP 엔드포인트로 직접 전송할 수도 있습니다.

## 풀(Pull) 기반 통합

DataHub는 Python 기반 [메타데이터 ingestion 시스템](../../metadata-ingestion/README.md)과 함께 제공되며, 다양한 소스에 연결하여 메타데이터를 가져올 수 있습니다. 이 메타데이터는 Kafka 또는 HTTP를 통해 DataHub 스토리지 계층으로 전송됩니다. 메타데이터 ingestion 파이프라인은 [Airflow와 통합](../../metadata-ingestion/README.md#lineage-with-airflow)하여 예약된 ingestion을 설정하거나 lineage를 캡처할 수 있습니다. 이미 지원되는 소스를 찾지 못한 경우, [직접 작성](../../metadata-ingestion/README.md#contributing)하는 것도 매우 쉽습니다.

## 푸시(Push) 기반 통합

Kafka에 [Metadata Change Proposal (MCP)] 이벤트를 발행하거나 HTTP를 통해 REST 호출을 할 수 있다면, 어떤 시스템이든 DataHub와 통합할 수 있습니다. 편의를 위해 DataHub는 시스템에 통합하여 발생 지점에서 메타데이터 변경(MCP)을 발행할 수 있는 간단한 [Python emitter]도 제공합니다.

## 내부 컴포넌트

### DataHub 메타데이터 서비스에 Metadata Change Proposal 적용 (mce-consumer-job)

DataHub는 Metadata Change Proposal을 소비하여 `/ingest` 엔드포인트를 통해 DataHub 메타데이터 서비스(datahub-gms)에 기록하는 Spring 작업인 [mce-consumer-job]과 함께 제공됩니다.

[Metadata Change Proposal (MCP)]: ../what/mxe.md#metadata-change-proposal-mcp
[Metadata Change Proposal]: ../what/mxe.md#metadata-change-proposal-mcp
[Metadata Change Log (MCL)]: ../what/mxe.md#metadata-change-log-mcl
[equivalent Pegasus format]: https://linkedin.github.io/rest.li/how_data_is_represented_in_memory#the-data-template-layer
[mce-consumer-job]: ../../metadata-jobs/mce-consumer-job
[Python emitters]: ../../metadata-ingestion/README.md#using-as-a-library
