import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Tags

## Dataset에 Tags를 사용하는 이유

Tag는 검색 및 발견을 돕는 비공식적이고 느슨하게 관리되는 레이블입니다. dataset, dataset 스키마 또는 컨테이너에 추가하여 entity를 레이블링하거나 분류하는 쉬운 방법을 제공합니다 — 더 광범위한 business glossary나 어휘와 연결할 필요 없이 사용할 수 있습니다.
Tag에 대한 자세한 내용은 [DataHub Tags 소개](/docs/tags.md)를 참조하세요.

### 이 가이드의 목표

이 가이드에서는 다음을 수행하는 방법을 보여드립니다

- 생성: tag를 생성합니다.
- 조회: dataset에 연결된 tag를 조회합니다.
- 추가: dataset의 컬럼 또는 dataset 자체에 tag를 추가합니다.
- 제거: dataset에서 tag를 제거합니다.

## 사전 조건

이 튜토리얼을 위해 DataHub Quickstart를 배포하고 샘플 데이터를 ingest해야 합니다.
자세한 내용은 [DataHub Quickstart 가이드](/docs/quickstart.md)를 참조하세요.

:::note
Tag를 수정하기 전에 대상 dataset이 DataHub 인스턴스에 이미 존재하는지 확인해야 합니다.
존재하지 않는 entity를 조작하려고 하면 작업이 실패합니다.
이 가이드에서는 샘플 ingestion의 데이터를 사용합니다.
:::

GraphQL 설정 방법에 대한 자세한 내용은 [GraphQL 설정 방법](/docs/api/graphql/how-to-set-up-graphql.md)을 참조하세요.

## Tags 생성

다음 코드는 `Deprecated` tag를 생성합니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
mutation createTag {
    createTag(input:
    {
      name: "Deprecated",
      id: "deprecated",
      description: "Having this tag means this column or table is deprecated."
    })
}
```

다음 응답이 표시되면 작업이 성공한 것입니다:

```python
{
  "data": {
    "createTag": "urn:li:tag:deprecated"
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
--data-raw '{ "query": "mutation createTag { createTag(input: { name: \"Deprecated\", id: \"deprecated\",description: \"Having this tag means this column or table is deprecated.\" }) }", "variables":{}}'
```

예상 응답:

```json
{ "data": { "createTag": "urn:li:tag:deprecated" }, "extensions": {} }
```

</TabItem>

<TabItem value="java" label="Java">

```java
{{ inline /metadata-integration/java/examples/src/main/java/io/datahubproject/examples/TagCreate.java show_path_as_comment }}
```

</TabItem>

<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/tag_create.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Tags 생성의 예상 결과

이제 새 tag `Deprecated`가 생성된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/tag-created.png"/>
</p>

이 코드를 실행한 후 `datahub` CLI를 사용하여 프로그래밍 방식으로 `Deprecated` tag를 검색하여 이 작업을 확인할 수도 있습니다.

```shell
datahub get --urn "urn:li:tag:deprecated" --aspect tagProperties

{
  "tagProperties": {
    "description": "Having this tag means this column or table is deprecated.",
    "name": "Deprecated"
  }
}
```

## Tags 조회

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
query {
  dataset(urn: "urn:li:dataset:(urn:li:dataPlatform:hive,SampleHiveDataset,PROD)") {
    tags {
      tags {
        tag {
          name
          urn
        	properties {
        	  description
        	  colorHex
        	}
        }
      }
    }
  }
}
```

다음 응답이 표시되면 작업이 성공한 것입니다:

```python
{
  "data": {
    "dataset": {
      "tags": {
        "tags": [
          {
            "tag": {
              "name": "Legacy",
              "urn": "urn:li:tag:Legacy",
              "properties": {
                "description": "Indicates the dataset is no longer supported",
                "colorHex": null,
                "name": "Legacy"
              }
            }
          }
        ]
      }
    }
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
--data-raw '{ "query": "{dataset(urn: \"urn:li:dataset:(urn:li:dataPlatform:hive,SampleHiveDataset,PROD)\") {tags {tags {tag {name urn properties { description colorHex } } } } } }", "variables":{}}'
```

예상 응답:

```json
{
  "data": {
    "dataset": {
      "tags": {
        "tags": [
          {
            "tag": {
              "name": "Legacy",
              "urn": "urn:li:tag:Legacy",
              "properties": {
                "description": "Indicates the dataset is no longer supported",
                "colorHex": null
              }
            }
          }
        ]
      }
    }
  },
  "extensions": {}
}
```

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/dataset_query_tags.py show_path_as_comment }}
```

</TabItem>
</Tabs>

## Tags 추가

### Dataset에 Tags 추가

다음 코드는 dataset에 tag를 추가하는 방법을 보여줍니다.
아래 코드에서는 `fct_users_created`라는 dataset에 `Deprecated` tag를 추가합니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
mutation addTags {
    addTags(
      input: {
        tagUrns: ["urn:li:tag:deprecated"],
        resourceUrn: "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)",
      }
    )
}
```

다음 응답이 표시되면 작업이 성공한 것입니다:

```python
{
  "data": {
    "addTags": true
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
--data-raw '{ "query": "mutation addTags { addTags(input: { tagUrns: [\"urn:li:tag:deprecated\"], resourceUrn: \"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)\" }) }", "variables":{}}'
```

예상 응답:

```json
{ "data": { "addTags": true }, "extensions": {} }
```

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_tag.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Dataset 컬럼에 Tags 추가

아래 예시에서 `subResource`는 스키마의 `fieldPath`입니다.

<Tabs>
<TabItem value="graphql" label="GraphQL">

```json
mutation addTags {
    addTags(
      input: {
        tagUrns: ["urn:li:tag:deprecated"],
        resourceUrn: "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)",
        subResourceType:DATASET_FIELD,
        subResource:"user_name"})
}
```

</TabItem>
<TabItem value="curl" label="Curl">

```shell
curl --location --request POST 'http://localhost:8080/api/graphql' \
--header 'Authorization: Bearer <my-access-token>' \
--header 'Content-Type: application/json' \
--data-raw '{ "query": "mutation addTags { addTags(input: { tagUrns: [\"urn:li:tag:deprecated\"], resourceUrn: \"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)\", subResourceType: DATASET_FIELD, subResource: \"user_name\" }) }", "variables":{}}'
```

예상 응답:

```json
{ "data": { "addTags": true }, "extensions": {} }
```

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_column_tag.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Tags 추가의 예상 결과

이제 `user_name` 컬럼에 `Deprecated` tag가 추가된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/tag-added.png"/>
</p>

`datahub` CLI를 사용하여 `globalTags` aspect를 확인하는 방식으로 이 작업을 프로그래밍 방식으로 검증할 수도 있습니다.

```shell
datahub get --urn "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)" --aspect globalTags
```

## Tags 제거

다음 코드는 dataset에서 tag를 제거합니다.
이 코드를 실행하면 `user_name` 컬럼에서 `Deprecated` tag가 제거됩니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
mutation removeTag {
    removeTag(
      input: {
        tagUrn: "urn:li:tag:deprecated",
        resourceUrn: "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)",
        subResourceType:DATASET_FIELD,
        subResource:"user_name"})
}
```

</TabItem>
<TabItem value="curl" label="Curl">

```shell
curl --location --request POST 'http://localhost:8080/api/graphql' \
--header 'Authorization: Bearer <my-access-token>' \
--header 'Content-Type: application/json' \
--data-raw '{ "query": "mutation removeTag { removeTag(input: { tagUrn: \"urn:li:tag:deprecated\", resourceUrn: \"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)\" }) }", "variables":{}}'
```

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/dataset_remove_tag_execute_graphql.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Tags 제거의 예상 결과

이제 `user_name` 컬럼에서 `Deprecated` tag가 제거된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/tag-removed.png"/>
</p>

`datahub` CLI를 사용하여 `gloablTags` aspect를 확인하는 방식으로 이 작업을 프로그래밍 방식으로 검증할 수도 있습니다.

```shell
datahub get --urn "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)" --aspect globalTags

{
  "globalTags": {
    "tags": []
  }
}
```
