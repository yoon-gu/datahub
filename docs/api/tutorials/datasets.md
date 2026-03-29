import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Dataset

## Dataset을 왜 사용하나요?

dataset 엔티티는 메타데이터 모델에서 가장 중요한 엔티티 중 하나입니다. 데이터베이스(BigQuery, Snowflake, Redshift 등)의 테이블 또는 뷰, 스트림 처리 환경(Kafka, Pulsar 등)의 스트림, 데이터 레이크 시스템(S3, ADLS 등)의 파일이나 폴더 번들로 표현되는 데이터 컬렉션을 나타냅니다.
dataset에 대한 자세한 내용은 [dataset 레퍼런스](/docs/generated/metamodel/entities/dataset.md)를 참고하세요.

### 이 가이드의 목표

이 가이드에서는 다음을 수행하는 방법을 안내합니다.

- 생성: 세 개의 컬럼을 가진 dataset을 생성합니다.
- 삭제: dataset을 삭제합니다.

## 사전 요구 사항

이 튜토리얼을 위해서는 DataHub Quickstart를 배포하고 샘플 데이터를 수집해야 합니다.
자세한 단계는 [DataHub Quickstart 가이드](/docs/quickstart.md)를 참고하세요.

## Dataset 생성

<Tabs>
<TabItem value="graphql" label="GraphQL">

> 🚫 `graphql`을 통한 dataset 생성은 현재 지원되지 않습니다.
> 자세한 내용은 [API 기능 비교표](/docs/api/datahub-apis.md#datahub-api-comparison)를 확인하세요.

</TabItem>
<TabItem value="java" label="Java">

```java
{{ inline /metadata-integration/java/examples/src/main/java/io/datahubproject/examples/DatasetAdd.java show_path_as_comment }}
```

</TabItem>
<TabItem value="python" label="Python" default>

```python
{{ inline /metadata-ingestion/examples/library/dataset_schema.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Dataset 생성 예상 결과

이제 `realestate_db.sales` dataset이 생성된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/dataset-created.png"/>
</p>

## Dataset 삭제

dataset이 더 이상 필요하지 않거나, 잘못되거나 민감한 정보가 포함되어 있거나, 테스트 목적으로 생성되어 프로덕션에서 더 이상 필요하지 않은 경우 삭제할 수 있습니다.
[CLI를 통해 엔티티를 삭제](/docs/how/delete-metadata.md)할 수도 있지만, 확장성을 위해서는 프로그래밍 방식이 필요합니다.

삭제에는 두 가지 방법이 있습니다: 소프트 삭제와 하드 삭제입니다.
**소프트 삭제**는 엔티티의 Status aspect를 Removed로 설정하여 해당 엔티티와 모든 aspect가 UI에서 반환되지 않도록 숨깁니다.
**하드 삭제**는 엔티티의 모든 aspect에 대한 모든 행을 물리적으로 삭제합니다.

소프트 삭제와 하드 삭제에 대한 자세한 내용은 [DataHub에서 메타데이터 제거하기](/docs/how/delete-metadata.md#delete-by-urn)를 참고하세요.

<Tabs>
<TabItem value="graphql" label="GraphQL">

> 🚫 `graphql`을 통한 하드 삭제는 현재 지원되지 않습니다.
> 자세한 내용은 [API 기능 비교표](/docs/api/datahub-apis.md#datahub-api-comparison)를 확인하세요.

```json
mutation batchUpdateSoftDeleted {
    batchUpdateSoftDeleted(input:
      { urns: ["urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_deleted,PROD)"],
        deleted: true })
}
```

다음과 같은 응답이 표시되면 작업이 성공한 것입니다:

```json
{
  "data": {
    "batchUpdateSoftDeleted": true
  },
  "extensions": {}
}
```

</TabItem>
<TabItem value="curl" label="Curl">

```shell
curl --location --request POST 'http://localhost:8080/api/graphql' \
--header 'Authorization: Bearer <my-access-token>' \
--header 'Content-Type: application/json' \
--data-raw '{ "query": "mutation batchUpdateSoftDeleted { batchUpdateSoftDeleted(input: { deleted: true, urns: [\"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_deleted,PROD)\"] }) }", "variables":{}}'
```

예상 응답:

```json
{ "data": { "batchUpdateSoftDeleted": true }, "extensions": {} }
```

</TabItem>
<TabItem value="python" label="Python" default>

```python
{{ inline /metadata-ingestion/examples/library/dataset_delete.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Dataset 삭제 예상 결과

`fct_users_deleted` dataset이 삭제되었으므로, `fct_users_delete`라는 이름의 hive dataset을 검색해도 더 이상 찾을 수 없습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/dataset-deleted.png"/>
</p>
