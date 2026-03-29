# DataHub API 및 SDK 개요

DataHub는 플랫폼의 메타데이터를 조작하기 위한 여러 API를 제공합니다. 아래는 사용 사례에 맞는 API를 선택하는 데 도움이 되는 API 목록과 각각의 장단점입니다.

| API                                                        | 정의                               | 장점                                       | 단점                                                                                                                      |
| ---------------------------------------------------------- | ---------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| **[Python SDK](/metadata-ingestion/as-a-library.md)**      | SDK                                | 매우 유연하며 대량 실행에 적합             | 메타데이터 변경 이벤트에 대한 이해가 필요함                                                                               |
| **[Java SDK](/metadata-integration/java/as-a-library.md)** | SDK                                | 매우 유연하며 대량 실행에 적합             | 메타데이터 변경 이벤트에 대한 이해가 필요함                                                                               |
| **[GraphQL API](docs/api/graphql/getting-started.md)**     | GraphQL 인터페이스                 | 직관적이며 UI 기능을 그대로 반영           | SDK보다 유연성이 낮고 GraphQL 문법에 대한 지식이 필요함                                                                   |
| **[OpenAPI](docs/api/openapi/openapi-usage-guide.md)**     | 고급 사용자를 위한 저수준 API      | 가장 강력하고 유연함                       | 간단한 사용 사례에는 사용하기 어려울 수 있으며 대응하는 SDK가 없지만 제품 내에서 OpenAPI 스펙이 생성됨                   |

일반적으로 **Python 및 Java SDK**는 DataHub 인스턴스의 동작을 확장하고 커스터마이징하는 데, 특히 프로그래밍 방식의 사용 사례에 가장 권장되는 도구입니다.

:::warning
API의 비동기 사용에 대하여 - DataHub의 비동기 API는 MCP 요청을 수신할 때 MCP Kafka 토픽에 직접 프로덕션하는 방식과 유사하게 기본적인 스키마 유효성 검사만 수행합니다. 요청이 수락되려면 MCP 스키마를 준수해야 하지만, 실제 처리는 파이프라인의 후속 단계에서 발생합니다. 초기 수락 이후에 발생하는 처리 실패는 Failed MCP 토픽에 기록되지만, 비동기적으로 발생하기 때문에 API 호출자에게 즉시 노출되지 않습니다.
:::

## Python 및 Java SDK

DataHub는 Python과 Java 모두에 대한 SDK를 제공하며, CRUD 작업 및 DataHub에 구현하고자 하는 복잡한 기능에 대한 완전한 기능을 지원합니다. 대부분의 사용 사례에 SDK 사용을 권장합니다. SDK 사용 예시는 다음과 같습니다:

- 데이터 엔티티 간 lineage 정의
- 대량 작업 실행 - 예: 여러 dataset에 태그 추가
- 커스텀 메타데이터 엔티티 생성

SDK에 대해 더 알아보기:

- **[Python SDK →](/metadata-ingestion/as-a-library.md)**
- **[Java SDK →](/metadata-integration/java/as-a-library.md)**

## GraphQL API

`graphql` API는 DataHub 프론트엔드에서 사용하는 기본 API입니다. GraphQL API에 대한 접근은 프론트엔드에서 이루어진다고 일반적으로 가정되므로 기본 캐싱, 동기 작업 등 UI 중심의 동작들이 함께 제공됩니다. 이 때문에 프로그래밍 방식으로 데이터를 조회하거나 업데이트할 때는 주의가 필요하며, 작업의 범위가 의도적으로 제한되어 있습니다. 가장 일반적인 작업을 단순화하는 고수준 API로 설계되었습니다.

GraphQL API는 DataHub를 처음 시작할 때 유용하며, 특히 GraphiQL을 사용할 때 더욱 사용자 친화적이고 직관적입니다. GraphQL API 사용 예시는 다음과 같습니다:

- 조건을 사용하여 dataset 검색
- 엔티티 간 관계 조회

GraphQL API에 대해 더 알아보기:

- **[GraphQL API →](docs/api/graphql/getting-started.md)**

## DataHub API 비교

DataHub는 각각 고유한 사용 방식과 형식을 가진 여러 API를 지원합니다.
각 API가 수행할 수 있는 작업에 대한 개요는 다음과 같습니다.

> 마지막 업데이트: 2024년 2월 16일

| 기능                                                       | GraphQL                                                                       | Python SDK                                                                                                                                     | OpenAPI |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| Dataset 생성                                               | 🚫                                                                            | ✅ [[가이드]](/docs/api/tutorials/datasets.md)                                                                                                  | ✅      |
| Dataset 삭제 (소프트 삭제)                                 | ✅ [[가이드]](/docs/api/tutorials/datasets.md#delete-dataset)                  | ✅ [[가이드]](/docs/api/tutorials/datasets.md#delete-dataset)                                                                                   | ✅      |
| Dataset 삭제 (하드 삭제)                                   | 🚫                                                                            | ✅ [[가이드]](/docs/api/tutorials/datasets.md#delete-dataset)                                                                                   | ✅      |
| Dataset 검색                                               | ✅ [[가이드]](/docs/how/search.md#graphql)                                     | ✅                                                                                                                                             | ✅      |
| Dataset 지원 종료(Deprecation) 읽기                        | ✅                                                                            | ✅                                                                                                                                             | ✅      |
| Dataset 엔티티 읽기 (V2)                                   | ✅                                                                            | ✅                                                                                                                                             | ✅      |
| 태그 생성                                                  | ✅ [[가이드]](/docs/api/tutorials/tags.md#create-tags)                         | ✅ [[가이드]](/docs/api/tutorials/tags.md#create-tags)                                                                                          | ✅      |
| 태그 읽기                                                  | ✅ [[가이드]](/docs/api/tutorials/tags.md#read-tags)                           | ✅ [[가이드]](/docs/api/tutorials/tags.md#read-tags)                                                                                            | ✅      |
| Dataset에 태그 추가                                        | ✅ [[가이드]](/docs/api/tutorials/tags.md#add-tags-to-a-dataset)               | ✅ [[가이드]](/docs/api/tutorials/tags.md#add-tags-to-a-dataset)                                                                                | ✅      |
| Dataset 컬럼에 태그 추가                                   | ✅ [[가이드]](/docs/api/tutorials/tags.md#add-tags-to-a-column-of-a-dataset)   | ✅ [[가이드]](/docs/api/tutorials/tags.md#add-tags-to-a-column-of-a-dataset)                                                                    | ✅      |
| Dataset에서 태그 제거                                      | ✅ [[가이드]](/docs/api/tutorials/tags.md#remove-tags)                         | ✅ [[가이드]](/docs/api/tutorials/tags.md#add-tags#remove-tags)                                                                                 | ✅      |
| 용어집 용어 생성                                           | ✅ [[가이드]](/docs/api/tutorials/terms.md#create-terms)                       | ✅ [[가이드]](/docs/api/tutorials/terms.md#create-terms)                                                                                        | ✅      |
| Dataset에서 용어 읽기                                      | ✅ [[가이드]](/docs/api/tutorials/terms.md#read-terms)                         | ✅ [[가이드]](/docs/api/tutorials/terms.md#read-terms)                                                                                          | ✅      |
| Dataset 컬럼에 용어 추가                                   | ✅ [[가이드]](/docs/api/tutorials/terms.md#add-terms-to-a-column-of-a-dataset) | ✅ [[가이드]](/docs/api/tutorials/terms.md#add-terms-to-a-column-of-a-dataset)                                                                  | ✅      |
| Dataset에 용어 추가                                        | ✅ [[가이드]](/docs/api/tutorials/terms.md#add-terms-to-a-dataset)             | ✅ [[가이드]](/docs/api/tutorials/terms.md#add-terms-to-a-dataset)                                                                              | ✅      |
| 도메인 생성                                                | ✅ [[가이드]](/docs/api/tutorials/domains.md#create-domain)                    | ✅ [[가이드]](/docs/api/tutorials/domains.md#create-domain)                                                                                     | ✅      |
| 도메인 읽기                                                | ✅ [[가이드]](/docs/api/tutorials/domains.md#read-domains)                     | ✅ [[가이드]](/docs/api/tutorials/domains.md#read-domains)                                                                                      | ✅      |
| Dataset에 도메인 추가                                      | ✅ [[가이드]](/docs/api/tutorials/domains.md#add-domains)                      | ✅ [[가이드]](/docs/api/tutorials/domains.md#add-domains)                                                                                       | ✅      |
| Dataset에서 도메인 제거                                    | ✅ [[가이드]](/docs/api/tutorials/domains.md#remove-domains)                   | ✅ [[가이드]](/docs/api/tutorials/domains.md#remove-domains)                                                                                    | ✅      |
| 사용자 생성/업서트                                         | ✅ [[가이드]](/docs/api/tutorials/owners.md#upsert-users)                      | ✅ [[가이드]](/docs/api/tutorials/owners.md#upsert-users)                                                                                       | ✅      |
| 그룹 생성/업서트                                           | ✅ [[가이드]](/docs/api/tutorials/owners.md#upsert-group)                      | ✅ [[가이드]](/docs/api/tutorials/owners.md#upsert-group)                                                                                       | ✅      |
| Dataset 소유자 읽기                                        | ✅ [[가이드]](/docs/api/tutorials/owners.md#read-owners)                       | ✅ [[가이드]](/docs/api/tutorials/owners.md#read-owners)                                                                                        | ✅      |
| Dataset에 소유자 추가                                      | ✅ [[가이드]](/docs/api/tutorials/owners.md#add-owners)                        | ✅ [[가이드]](/docs/api/tutorials/owners.md#add-owners#remove-owners)                                                                           | ✅      |
| Dataset에서 소유자 제거                                    | ✅ [[가이드]](/docs/api/tutorials/owners.md#remove-owners)                     | ✅ [[가이드]](/docs/api/tutorials/owners.md)                                                                                                    | ✅      |
| Lineage 추가                                               | ✅ [[가이드]](/docs/api/tutorials/lineage.md)                                  | ✅ [[가이드]](/docs/api/tutorials/lineage.md#add-lineage)                                                                                       | ✅      |
| 컬럼 수준(세밀한) Lineage 추가                             | 🚫                                                                            | ✅ [[가이드]](docs/api/tutorials/lineage.md#add-column-level-lineage)                                                                           | ✅      |
| Dataset 컬럼에 문서(설명) 추가                             | ✅ [[가이드]](/docs/api/tutorials/descriptions.md#add-description-on-column)   | ✅ [[가이드]](/docs/api/tutorials/descriptions.md#add-description-on-column)                                                                    | ✅      |
| Dataset에 문서(설명) 추가                                  | ✅ [[가이드]](/docs/api/tutorials/descriptions.md#add-description-on-dataset)  | ✅ [[가이드]](/docs/api/tutorials/descriptions.md#add-description-on-dataset)                                                                   | ✅      |
| Dataset에 커스텀 속성 추가/제거/교체                       | 🚫                                                                            | ✅ [[가이드]](/docs/api/tutorials/custom-properties.md)                                                                                         | ✅      |
| ML Feature를 ML Feature Table에 추가                       | 🚫                                                                            | ✅ [[가이드]](/docs/api/tutorials/ml.md#add-mlfeature-to-mlfeaturetable)                                                                        | ✅      |
| ML Feature를 MLModel에 추가                                | 🚫                                                                            | ✅ [[가이드]](/docs/api/tutorials/ml.md#add-mlfeature-to-mlmodel)                                                                               | ✅      |
| ML Group을 MLFeatureTable에 추가                           | 🚫                                                                            | ✅ [[가이드]](/docs/api/tutorials/ml.md#add-mlgroup-to-mlfeaturetable)                                                                          | ✅      |
| MLFeature 생성                                             | 🚫                                                                            | ✅ [[가이드]](/docs/api/tutorials/ml.md#create-mlfeature)                                                                                       | ✅      |
| MLFeatureTable 생성                                        | 🚫                                                                            | ✅ [[가이드]](/docs/api/tutorials/ml.md#create-mlfeaturetable)                                                                                  | ✅      |
| MLModel 생성                                               | 🚫                                                                            | ✅ [[가이드]](/docs/api/tutorials/ml.md#create-mlmodel)                                                                                         | ✅      |
| MLModelGroup 생성                                          | 🚫                                                                            | ✅ [[가이드]](/docs/api/tutorials/ml.md#create-mlmodelgroup)                                                                                    | ✅      |
| MLPrimaryKey 생성                                          | 🚫                                                                            | ✅ [[가이드]](/docs/api/tutorials/ml.md#create-mlprimarykey)                                                                                    | ✅      |
| MLFeatureTable 생성                                        | 🚫                                                                            | ✅ [[가이드]](/docs/api/tutorials/ml.md#create-mlfeaturetable)                                                                                  | ✅      |
| MLFeature 읽기                                             | ✅ [[가이드]](/docs/api/tutorials/ml.md#read-mlfeature)                        | ✅ [[가이드]](/docs/api/tutorials/ml.md#read-mlfeature)                                                                                         | ✅      |
| MLFeatureTable 읽기                                        | ✅ [[가이드]](/docs/api/tutorials/ml.md#read-mlfeaturetable)                   | ✅ [[가이드]](/docs/api/tutorials/ml.md#read-mlfeaturetable)                                                                                    | ✅      |
| MLModel 읽기                                               | ✅ [[가이드]](/docs/api/tutorials/ml.md#read-mlmodel)                          | ✅ [[가이드]](/docs/api/tutorials/ml.md#read-mlmodel)                                                                                           | ✅      |
| MLModelGroup 읽기                                          | ✅ [[가이드]](/docs/api/tutorials/ml.md#read-mlmodelgroup)                     | ✅ [[가이드]](/docs/api/tutorials/ml.md#read-mlmodelgroup)                                                                                      | ✅      |
| MLPrimaryKey 읽기                                          | ✅ [[가이드]](/docs/api/tutorials/ml.md#read-mlprimarykey)                     | ✅ [[가이드]](/docs/api/tutorials/ml.md#read-mlprimarykey)                                                                                      | ✅      |
| 데이터 제품 생성                                           | 🚫                                                                            | ✅ [[코드]](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/examples/library/dataproduct_create.py)                  | ✅      |
| Chart와 Dashboard 간 Lineage 생성                          | 🚫                                                                            | ✅ [[코드]](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/examples/library/lineage_chart_dashboard.py)             | ✅      |
| Dataset과 Chart 간 Lineage 생성                            | 🚫                                                                            | ✅ [[코드]](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/examples/library/lineage_dataset_chart.py)               | ✅      |
| Dataset과 DataJob 간 Lineage 생성                          | 🚫                                                                            | ✅ [[코드]](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/examples/library/lineage_dataset_job_dataset.py)         | ✅      |
| DataJob에 대한 Dataset의 세밀한 Lineage 생성               | 🚫                                                                            | ✅ [[코드]](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/examples/library/lineage_emitter_datajob_finegrained.py) | ✅      |
| Dataset의 세밀한 Lineage 생성                              | 🚫                                                                            | ✅ [[코드]](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/examples/library/lineage_emitter_dataset_finegrained.py) | ✅      |
| Dataflow를 사용한 DataJob 생성                             | 🚫                                                                            | ✅ [[코드]](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/examples/library/lineage_job_dataflow.py)                | ✅      |
| 프로그래밍 방식 파이프라인 생성                            | 🚫                                                                            | ✅ [[코드]](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/examples/library/programatic_pipeline.py)                | ✅      |
