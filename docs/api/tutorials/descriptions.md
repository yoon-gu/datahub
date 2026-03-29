import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# 설명(Description)

## Dataset에 설명을 왜 사용하나요?

dataset에 설명과 관련 링크를 추가하면 데이터의 출처, 수집 방법 및 잠재적 용도와 같은 중요한 정보를 제공할 수 있습니다. 이를 통해 다른 사람들이 데이터의 맥락과 자신의 작업이나 연구에 어떻게 관련될 수 있는지 이해하는 데 도움이 됩니다. 관련 링크를 포함하면 추가 리소스나 관련 dataset에 대한 접근도 제공하여 사용자가 이용할 수 있는 정보를 더욱 풍부하게 만들 수 있습니다.

### 이 가이드의 목표

이 가이드에서는 다음을 수행하는 방법을 안내합니다.

- Dataset 설명 읽기: dataset의 설명을 읽습니다.
- 컬럼 설명 읽기: dataset 컬럼의 설명을 읽습니다.
- Dataset 설명 추가: dataset에 설명과 링크를 추가합니다.
- 컬럼 설명 추가: dataset의 컬럼에 설명을 추가합니다.

## 사전 요구 사항

이 튜토리얼을 위해서는 DataHub Quickstart를 배포하고 샘플 데이터를 수집해야 합니다.
자세한 단계는 [DataHub Quickstart 가이드](/docs/quickstart.md)를 참고하세요.

:::note
설명을 추가하기 전에 대상 dataset이 이미 DataHub에 존재하는지 확인해야 합니다.
존재하지 않는 엔티티를 조작하려고 하면 작업이 실패합니다.
이 가이드에서는 샘플 ingestion의 데이터를 사용합니다.
:::

이 예시에서는 `fct_users_deleted` dataset의 `user_name` 컬럼에 설명을 추가합니다.

## Dataset 설명 읽기

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
query {
  dataset(urn: "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_deleted,PROD)") {
    properties {
      description
    }
  }
}
```

다음과 같은 응답이 표시되면 작업이 성공한 것입니다:

```json
{
  "data": {
    "dataset": {
      "properties": {
        "description": "table containing all the users deleted on a single day"
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
--data-raw '{ "query": "query { dataset(urn: \"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_deleted,PROD)\") { properties { description } } }", "variables":{}}'
```

예상 응답:

```json
{
  "data": {
    "dataset": {
      "properties": {
        "description": "table containing all the users deleted on a single day"
      }
    }
  },
  "extensions": {}
}
```

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/dataset_query_description.py show_path_as_comment }}
```

</TabItem>
</Tabs>

## 컬럼 설명 읽기

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
query {
  dataset(urn: "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_deleted,PROD)") {
    schemaMetadata {
      fields {
        fieldPath
        description
      }
    }
  }
}
```

다음과 같은 응답이 표시되면 작업이 성공한 것입니다:

```json
{
  "data": {
    "dataset": {
      "schemaMetadata": {
        "fields": [
          {
            "fieldPath": "user_name",
            "description": "Name of the user who was deleted"
          },
          ...
          {
            "fieldPath": "deletion_reason",
            "description": "Why the user chose to deactivate"
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
--data-raw '{ "query": "query { dataset(urn: \"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_deleted,PROD)\") { schemaMetadata { fields { fieldPath description } } } }", "variables":{}}'
```

예상 응답:

```json
{
  "data": {
    "dataset": {
      "schemaMetadata": {
        "fields": [
          {
            "fieldPath": "user_name",
            "description": "Name of the user who was deleted"
          },
          {
            "fieldPath": "timestamp",
            "description": "Timestamp user was deleted at"
          },
          { "fieldPath": "user_id", "description": "Id of the user deleted" },
          {
            "fieldPath": "browser_id",
            "description": "Cookie attached to identify the browser"
          },
          {
            "fieldPath": "session_id",
            "description": "Cookie attached to identify the session"
          },
          {
            "fieldPath": "deletion_reason",
            "description": "Why the user chose to deactivate"
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
{{ inline /metadata-ingestion/examples/library/dataset_query_description_on_columns.py show_path_as_comment }}
```

</TabItem>
</Tabs>

## Dataset에 설명 추가

<Tabs>
<TabItem value="graphQL" label="GraphQL">

```graphql
mutation updateDataset {
  updateDataset(
    urn: "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)"
    input: {
      editableProperties: {
        description: "## The Real Estate Sales Dataset\nThis is a really important Dataset that contains all the relevant information about sales that have happened organized by address.\n"
      }
      institutionalMemory: {
        elements: {
          author: "urn:li:corpuser:jdoe"
          url: "https://wikipedia.com/real_estate"
          description: "This is the definition of what real estate means"
        }
      }
    }
  ) {
    urn
  }
}
```

예상 응답:

```json
{
  "data": {
    "updateDataset": {
      "urn": "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)"
    }
  },
  "extensions": {}
}
```

</TabItem>

<TabItem value="curl" label="Curl" default>

```shell
curl --location --request POST 'http://localhost:8080/api/graphql' \
--header 'Authorization: Bearer <my-access-token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "query": "mutation updateDataset { updateDataset( urn:\"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)\", input: { editableProperties: { description: \"## The Real Estate Sales Dataset\nThis is a really important Dataset that contains all the relevant information about sales that have happened organized by address.\n\" } institutionalMemory: { elements: { author: \"urn:li:corpuser:jdoe\", url: \"https://wikipedia.com/real_estate\", description: \"This is the definition of what real estate means\" } } } ) { urn } }",
  "variables": {}
}'
```

예상 응답:

```json
{
  "data": {
    "updateDataset": {
      "urn": "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)"
    }
  },
  "extensions": {}
}
```

</TabItem>
<TabItem value="python" label="Python" default>

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_documentation.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Dataset에 설명 추가 예상 결과

이제 `fct_users_deleted`에 설명이 추가된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/dataset-description-added.png"/>
</p>

## 컬럼에 설명 추가

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
mutation updateDescription {
  updateDescription(
    input: {
      description: "Name of the user who was deleted. This description is updated via GrpahQL.",
      resourceUrn:"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_deleted,PROD)",
      subResource: "user_name",
      subResourceType:DATASET_FIELD
    }
  )
}
```

`description`에는 일반 마크다운을 사용할 수 있습니다. 예를 들어 다음과 같이 작성할 수 있습니다.

```json
mutation updateDescription {
  updateDescription(
    input: {
      description: """
      ### User Name
      The `user_name` column is a primary key column that contains the name of the user who was deleted.
      """,
      resourceUrn:"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_deleted,PROD)",
      subResource: "user_name",
      subResourceType:DATASET_FIELD
    }
  )
}
```

`updateDescription`은 현재 Dataset Schema 필드와 컨테이너만 지원합니다.
`updateDescription` mutation에 대한 자세한 내용은 [updateLineage](https://docs.datahub.com/docs/graphql/mutations/#updateDescription)를 참고하세요.

다음과 같은 응답이 표시되면 작업이 성공한 것입니다:

```json
{
  "data": {
    "updateDescription": true
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
--data-raw '{ "query": "mutation updateDescription { updateDescription ( input: { description: \"Name of the user who was deleted. This description is updated via GrpahQL.\", resourceUrn: \"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_deleted,PROD)\", subResource: \"user_name\", subResourceType:DATASET_FIELD }) }", "variables":{}}'
```

예상 응답:

```json
{ "data": { "updateDescription": true }, "extensions": {} }
```

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_column_documentation.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### 컬럼에 설명 추가 예상 결과

이제 `fct_users_deleted`의 `user_name` 컬럼에 설명이 추가된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/column-description-added.png"/>
</p>
