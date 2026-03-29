---
title: "서빙 계층"
---

# DataHub 서빙 아키텍처

아래 그림은 DataHub 서빙 계층의 고수준 시스템 다이어그램을 보여줍니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/datahub-serving.png"/>
</p>

주요 컴포넌트는 [메타데이터 서비스](../../metadata-service)로, 메타데이터에 대한 CRUD 작업을 수행하기 위한 REST API와 GraphQL API를 노출합니다. 이 서비스는 보조 인덱스 스타일 쿼리, 전문 검색 쿼리, 그리고 lineage와 같은 relationship 쿼리를 지원하기 위한 검색 및 그래프 쿼리 API도 노출합니다. 또한 [datahub-frontend](../../datahub-frontend) 서비스는 메타데이터 그래프 위에 GraphQL API를 노출합니다.

## DataHub 서빙 계층 컴포넌트

### 메타데이터 스토리지

DataHub 메타데이터 서비스는 메타데이터를 문서 저장소(MySQL, Postgres, Cassandra 등 RDBMS)에 영구 저장합니다.

### Metadata Change Log 스트림 (MCL)

DataHub 서비스 계층은 메타데이터 변경 사항이 영구 스토리지에 성공적으로 커밋되면 커밋 이벤트인 [Metadata Change Log]를 발행합니다. 이 이벤트는 Kafka를 통해 전송됩니다.

MCL 스트림은 공개 API이며 외부 시스템(예: Actions Framework)이 구독할 수 있어, 메타데이터에서 발생하는 변경 사항에 실시간으로 반응하는 매우 강력한 방법을 제공합니다. 예를 들어, 메타데이터 변경(예: 이전에 모든 사용자가 읽을 수 있었던 dataset에 PII 필드가 추가됨)에 반응하여 해당 dataset을 즉시 잠그는 액세스 제어 시행자를 구축할 수 있습니다.
모든 MCP가 MCL로 이어지는 것은 아닙니다. DataHub 서빙 계층은 메타데이터에 대한 중복 변경을 무시하기 때문입니다.

### 메타데이터 인덱스 적용기 (mae-consumer-job)

[Metadata Change Log]는 또 다른 Spring 작업인 [mae-consumer-job]에 의해 소비되며, 이 작업은 변경 사항을 [그래프][graph] 및 [검색 인덱스][search index]에 적절히 적용합니다.
이 작업은 entity에 독립적이며, 특정 메타데이터 aspect가 변경될 때 작업에 의해 호출되는 해당 그래프 및 검색 인덱스 빌더를 실행합니다.
빌더는 메타데이터 변경을 기반으로 그래프와 검색 인덱스를 어떻게 업데이트할지 작업에 지시해야 합니다.

메타데이터 변경 사항이 올바른 시간 순서로 처리되도록 보장하기 위해, MCL은 entity [URN][URN]을 키로 사용합니다. 즉, 특정 entity에 대한 모든 MAE는 단일 스레드에 의해 순차적으로 처리됩니다.

### 메타데이터 쿼리 서빙

메타데이터에 대한 기본 키 기반 읽기(예: `dataset-urn`을 기반으로 dataset의 schema 메타데이터 가져오기)는 문서 저장소로 라우팅됩니다. 메타데이터에 대한 보조 인덱스 기반 읽기는 검색 인덱스로 라우팅됩니다(또는 [여기]()에 설명된 강력한 일관성 보조 인덱스 지원을 사용할 수도 있습니다). 전문 검색 및 고급 검색 쿼리는 검색 인덱스로 라우팅됩니다. lineage와 같은 복잡한 그래프 쿼리는 그래프 인덱스로 라우팅됩니다.

[RecordTemplate]: https://github.com/linkedin/rest.li/blob/master/data/src/main/java/com/linkedin/data/template/RecordTemplate.java
[GenericRecord]: https://github.com/apache/avro/blob/master/lang/java/avro/src/main/java/org/apache/avro/generic/GenericRecord.java
[Pegasus]: https://linkedin.github.io/rest.li/DATA-Data-Schema-and-Templates
[relationship]: ../what/relationship.md
[entity]: ../what/entity.md
[aspect]: ../what/aspect.md
[GMS]: ../what/gms.md
[Metadata Change Log]: ../what/mxe.md#metadata-change-log-mcl
[rest.li]: https://rest.li
[Metadata Change Proposal (MCP)]: ../what/mxe.md#metadata-change-proposal-mcp
[Metadata Change Log (MCL)]: ../what/mxe.md#metadata-change-log-mcl
[MCP]: ../what/mxe.md#metadata-change-proposal-mcp
[MCL]: ../what/mxe.md#metadata-change-log-mcl
[equivalent Pegasus format]: https://linkedin.github.io/rest.li/how_data_is_represented_in_memory#the-data-template-layer
[graph]: ../what/graph.md
[search index]: ../what/search-index.md
[mce-consumer-job]: ../../metadata-jobs/mce-consumer-job
[mae-consumer-job]: ../../metadata-jobs/mae-consumer-job
[Remote DAO]: ../architecture/metadata-serving.md#remote-dao
[URN]: ../what/urn.md
[Metadata Modelling]: ../modeling/metadata-model.md
[Entity]: ../what/entity.md
[Relationship]: ../what/relationship.md
[Search Document]: ../what/search-document.md
[metadata aspect]: ../what/aspect.md
[Python emitters]: https://docs.datahub.com/docs/metadata-ingestion/#using-as-a-library
