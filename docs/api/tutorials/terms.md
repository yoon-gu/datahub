import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Terms

## Dataset에 Terms를 사용하는 이유

DataHub의 비즈니스 Glossary(Term) 기능은 표준화된 데이터 개념 집합을 정의하는 프레임워크를 제공하고, 이를 데이터 생태계 내에 존재하는 물리적 자산과 연결함으로써 조직 내에서 공유된 어휘를 사용할 수 있도록 도와줍니다.

Terms에 대한 자세한 내용은 [DataHub 비즈니스 Glossary 소개](/docs/glossary/business-glossary.md)를 참조하세요.

### 이 가이드의 목표

이 가이드에서는 다음을 수행하는 방법을 보여드립니다

- 생성: term을 생성합니다.
- 조회: dataset에 연결된 term을 조회합니다.
- 추가: dataset의 컬럼 또는 dataset 자체에 term을 추가합니다.
- 제거: dataset에서 term을 제거합니다.

## 사전 조건

이 튜토리얼을 위해 DataHub Quickstart를 배포하고 샘플 데이터를 ingest해야 합니다.
자세한 내용은 [DataHub Quickstart 가이드](/docs/quickstart.md)를 참조하세요.

:::note
Term을 수정하기 전에 대상 dataset이 DataHub 인스턴스에 이미 존재하는지 확인해야 합니다.
존재하지 않는 entity를 조작하려고 하면 작업이 실패합니다.
이 가이드에서는 샘플 ingestion의 데이터를 사용합니다.
:::

GraphQL 설정 방법에 대한 자세한 내용은 [GraphQL 설정 방법](/docs/api/graphql/how-to-set-up-graphql.md)을 참조하세요.

## Terms 생성

다음 코드는 `Rate of Return` term을 생성합니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
mutation createGlossaryTerm {
  createGlossaryTerm(input: {
    name: "Rate of Return",
    id: "rateofreturn",
    description: "A rate of return (RoR) is the net gain or loss of an investment over a specified time period."
  },
  )
}
```

다음 응답이 표시되면 작업이 성공한 것입니다:

```python
{
  "data": {
    "createGlossaryTerm": "urn:li:glossaryTerm:rateofreturn"
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
--data-raw '{ "query": "mutation createGlossaryTerm { createGlossaryTerm(input: { name: \"Rate of Return\", id:\"rateofreturn\", description: \"A rate of return (RoR) is the net gain or loss of an investment over a specified time period.\" }) }", "variables":{}}'
```

예상 응답:

```json
{
  "data": { "createGlossaryTerm": "urn:li:glossaryTerm:rateofreturn" },
  "extensions": {}
}
```

</TabItem>

<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/glossary_term_create_simple.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Terms 생성의 예상 결과

이제 새 term `Rate of Return`이 생성된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/term-created.png"/>
</p>

이 코드를 실행한 후 `datahub` CLI를 사용하여 프로그래밍 방식으로 `Rate of Return` term을 검색하여 이 작업을 확인할 수도 있습니다.

```shell
datahub get --urn "urn:li:glossaryTerm:rateofreturn" --aspect glossaryTermInfo

{
  "glossaryTermInfo": {
    "definition": "A rate of return (RoR) is the net gain or loss of an investment over a specified time period.",
    "name": "Rate of Return",
    "termSource": "INTERNAL"
  }
}
```

## Terms 조회

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
query {
  dataset(urn: "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)") {
    glossaryTerms {
      terms {
        term {
          urn
          glossaryTermInfo {
            name
            description
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
      "glossaryTerms": {
        "terms": [
          {
            "term": {
              "urn": "urn:li:glossaryTerm:CustomerAccount",
              "glossaryTermInfo": {
                "name": "CustomerAccount",
                "description": "account that represents an identified, named collection of balances and cumulative totals used to summarize customer transaction-related activity over a designated period of time"
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
--data-raw '{ "query": "{dataset(urn: \"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)\") {glossaryTerms {terms {term {urn glossaryTermInfo { name description } } } } } }", "variables":{}}'
```

예상 응답:

````json
{"data":{"dataset":{"glossaryTerms":{"terms":[{"term":{"urn":"urn:li:glossaryTerm:CustomerAccount","glossaryTermInfo":{"name":"CustomerAccount","description":"account that represents an identified, named collection of balances and cumulative totals used to summarize customer transaction-related activity over a designated period of time"}}}]}}},"extensions":{}}```
````

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/dataset_query_terms.py show_path_as_comment }}
```

</TabItem>
</Tabs>

## Terms 추가

### Dataset에 Terms 추가

다음 코드는 dataset에 term을 추가하는 방법을 보여줍니다.
아래 코드에서는 `fct_users_created`라는 dataset에 `Rate of Return` term을 추가합니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
mutation addTerms {
    addTerms(
      input: {
        termUrns: ["urn:li:glossaryTerm:rateofreturn"],
        resourceUrn: "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)",
      }
  )
}
```

다음 응답이 표시되면 작업이 성공한 것입니다:

```python
{
  "data": {
    "addTerms": true
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
--data-raw '{ "query": "mutation addTerm { addTerms(input: { termUrns: [\"urn:li:glossaryTerm:rateofreturn\"], resourceUrn: \"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)\" }) }", "variables":{}}'
```

예상 응답:

```json
{ "data": { "addTerms": true }, "extensions": {} }
```

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_term.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Dataset 컬럼에 Terms 추가

<Tabs>
<TabItem value="graphql" label="GraphQL">

```json
mutation addTerms {
    addTerms(
      input: {
        termUrns: ["urn:li:glossaryTerm:rateofreturn"],
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
--data-raw '{ "query": "mutation addTerms { addTerms(input: { termUrns: [\"urn:li:glossaryTerm:rateofreturn\"], resourceUrn: \"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)\", subResourceType: DATASET_FIELD, subResource: \"user_name\" }) }", "variables":{}}'
```

예상 응답:

```json
{ "data": { "addTerms": true }, "extensions": {} }
```

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_column_term.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Terms 추가의 예상 결과

이제 `user_name` 컬럼에 `Rate of Return` term이 추가된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/term-added.png"/>
</p>

## Terms 제거

다음 코드는 dataset에서 term을 제거합니다.
이 코드를 실행하면 `user_name` 컬럼에서 `Rate of Return` term이 제거됩니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
mutation removeTerm {
    removeTerm(
      input: {
        termUrn: "urn:li:glossaryTerm:rateofreturn",
        resourceUrn: "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)",
        subResourceType:DATASET_FIELD,
        subResource:"user_name"})
}
```

`subResourceType`과 `subResource`를 지정하지 않으면 dataset에서 term을 제거할 수도 있습니다.

```json
mutation removeTerm {
    removeTerm(
      input: {
        termUrn: "urn:li:glossaryTerm:rateofreturn",
        resourceUrn: "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)",
      })
}
```

`batchRemoveTerms`를 사용하여 여러 entity 또는 하위 리소스에서 term을 제거할 수도 있습니다.

```json
mutation batchRemoveTerms {
    batchRemoveTerms(
      input: {
        termUrns: ["urn:li:glossaryTerm:rateofreturn"],
        resources: [
          { resourceUrn:"urn:li:dataset:(urn:li:dataPlatform:hdfs,SampleHdfsDataset,PROD)"} ,
          { resourceUrn:"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)"} ,]
      }
    )
}
```

</TabItem>
<TabItem value="curl" label="Curl">

```shell
curl --location --request POST 'http://localhost:8080/api/graphql' \
--header 'Authorization: Bearer <my-access-token>' \
--header 'Content-Type: application/json' \
--data-raw '{ "query": "mutation removeTerm { removeTerm(input: { termUrn: \"urn:li:glossaryTerm:rateofreturn\", resourceUrn: \"urn:li:dataset:(urn:li:dataPlatform:hdfs,SampleHdfsDataset,PROD)\" }) }", "variables":{}}'
```

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/dataset_remove_term_execute_graphql.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Terms 제거의 예상 결과

이제 `user_name` 컬럼에서 `Rate of Return` term이 제거된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/term-removed.png"/>
</p>
