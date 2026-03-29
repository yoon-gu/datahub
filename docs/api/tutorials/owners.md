import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Ownership

## 사용자와 그룹을 사용하는 이유

사용자와 그룹은 데이터 ownership을 관리하는 데 필수적입니다. 사용자 계정을 생성하거나 업데이트하고 적절한 그룹에 배정함으로써, 관리자는 올바른 사람들이 업무 수행에 필요한 데이터에 접근할 수 있도록 보장할 수 있습니다. 이를 통해 특정 dataset에 대한 책임자에 대한 혼란이나 충돌을 방지하고 전반적인 효율성을 향상시킬 수 있습니다.

### 이 가이드의 목표

이 가이드에서는 다음을 수행하는 방법을 보여드립니다

- 생성: 사용자 및 그룹을 생성하거나 업데이트합니다.
- 조회: dataset에 연결된 owner를 조회합니다.
- 추가: 사용자 그룹을 dataset의 owner로 추가합니다.
- 제거: dataset에서 owner를 제거합니다.

## 사전 조건

이 튜토리얼을 위해 DataHub Quickstart를 배포하고 샘플 데이터를 ingest해야 합니다.
자세한 내용은 [DataHub Quickstart 가이드](/docs/quickstart.md)를 참조하세요.

:::note
이 가이드에서 샘플 데이터 ingestion은 선택 사항입니다.
:::

## 사용자 Upsert

<Tabs>
<TabItem value="cli" label="CLI">

이 `user.yaml`을 로컬 파일로 저장합니다.

```yaml
- id: bar@acryl.io
  first_name: The
  last_name: Bar
  email: bar@acryl.io
  slack: "@the_bar_raiser"
  description: "I like raising the bar higher"
  title: "Analytics Engineer"
  groups:
    - foogroup@acryl.io
- id: datahub
  slack: "@datahubproject"
  phone: "1-800-GOT-META"
  description: "The DataHub Project"
  title: "Data Engineer"
  picture_link: "https://raw.githubusercontent.com/datahub-project/datahub/master/datahub-web-react/src/images/datahub-logo-color-stable.svg"
```

사용자 데이터를 ingest하기 위해 다음 CLI 명령어를 실행합니다.
datahub 사용자가 이미 샘플 데이터에 존재하므로, 사용자 정보에 대한 업데이트는 기존 데이터를 덮어씁니다.

```
datahub user upsert -f user.yaml
```

다음 로그가 표시되면 작업이 성공한 것입니다:

```shell
Update succeeded for urn urn:li:corpuser:bar@acryl.io.
Update succeeded for urn urn:li:corpuser:datahub.
```

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/upsert_user.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### 사용자 Upsert의 예상 결과

`Settings > Access > Users & Groups`에서 사용자 `The bar`가 생성되고 사용자 `Datahub`가 업데이트된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/user-upserted.png"/>
</p>

## 그룹 Upsert

<Tabs>
<TabItem value="cli" label="CLI">

이 `group.yaml`을 로컬 파일로 저장합니다. 그룹에는 owner이자 멤버인 사용자 목록이 포함되어 있습니다. 이 목록에서 사용자를 ID 또는 URN으로 참조할 수 있으며, 그룹 설명 내에 인라인으로 메타데이터를 지정할 수도 있습니다. 아래 예시를 참고하여 로컬에서 이 파일을 수정해 보고 로컬 DataHub 인스턴스에서 변경 사항의 효과를 확인해 보세요.

```yaml
id: foogroup@acryl.io
display_name: Foo Group
owners:
  - datahub
members:
  - bar@acryl.io # refer to a user either by id or by urn
  - id: joe@acryl.io # inline specification of user
    slack: "@joe_shmoe"
    display_name: "Joe's Hub"
```

이 그룹의 정보를 ingest하기 위해 다음 CLI 명령어를 실행합니다.

```
datahub group upsert -f group.yaml
```

다음 로그가 표시되면 작업이 성공한 것입니다:

```shell
Update succeeded for group urn:li:corpGroup:foogroup@acryl.io.
```

</TabItem>

<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/upsert_group.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### 그룹 Upsert의 예상 결과

`Settings > Access > Users & Groups`에서 그룹 `Foo Group`이 생성된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/group-upserted.png"/>
</p>

## Owner 조회

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
query {
  dataset(urn: "urn:li:dataset:(urn:li:dataPlatform:hive,SampleHiveDataset,PROD)") {
    ownership {
      owners {
        owner {
          ... on CorpUser {
            urn
            type
          }
          ... on CorpGroup {
            urn
            type
          }
        }
      }
    }
  }
}
```

다음 응답이 표시되면 작업이 성공한 것입니다:

```json
{
  "data": {
    "dataset": {
      "ownership": {
        "owners": [
          {
            "owner": {
              "urn": "urn:li:corpuser:jdoe",
              "type": "CORP_USER"
            }
          },
          {
            "owner": {
              "urn": "urn:li:corpuser:datahub",
              "type": "CORP_USER"
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
--data-raw '{ "query": "{ dataset(urn: \"urn:li:dataset:(urn:li:dataPlatform:hive,SampleHiveDataset,PROD)\") { ownership { owners { owner { ... on CorpUser { urn type } ... on CorpGroup { urn type } } } } } }", "variables":{}}'
```

예상 응답:

```json
{
  "data": {
    "dataset": {
      "ownership": {
        "owners": [
          { "owner": { "urn": "urn:li:corpuser:jdoe", "type": "CORP_USER" } },
          { "owner": { "urn": "urn:li:corpuser:datahub", "type": "CORP_USER" } }
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
{{ inline /metadata-ingestion/examples/library/dataset_query_owners.py show_path_as_comment }}
```

</TabItem>
</Tabs>

## Owner 추가

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```python
mutation addOwners {
    addOwner(
      input: {
        ownerUrn: "urn:li:corpGroup:bfoo",
        resourceUrn: "urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)",
        ownerEntityType: CORP_GROUP,
        type: TECHNICAL_OWNER
			}
    )
}
```

예상 응답:

```python
{
  "data": {
    "addOwner": true
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
--data-raw '{ "query": "mutation addOwners { addOwner(input: { ownerUrn: \"urn:li:corpGroup:bfoo\", resourceUrn: \"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)\", ownerEntityType: CORP_GROUP, type: TECHNICAL_OWNER }) }", "variables":{}}'
```

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_owner.py show_path_as_comment }}
```

</TabItem>
</Tabs>

## Owner 추가의 예상 결과

이제 `bfoo`가 `fct_users_created` dataset의 owner로 추가된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/owner-added.png"/>
</p>

## Owner 제거

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

```json
mutation removeOwners {
    removeOwner(
      input: {
        ownerUrn: "urn:li:corpuser:jdoe",
        resourceUrn: "urn:li:dataset:(urn:li:dataPlatform:hdfs,SampleHdfsDataset,PROD)",
			}
    )
}
```

`batchRemoveOwners`를 사용하여 여러 entity 또는 하위 리소스에서 owner를 제거할 수도 있습니다.

```json
mutation batchRemoveOwners {
    batchRemoveOwners(
      input: {
        ownerUrns: ["urn:li:corpuser:jdoe"],
        resources: [
          { resourceUrn:"urn:li:dataset:(urn:li:dataPlatform:hdfs,SampleHdfsDataset,PROD)"} ,
          { resourceUrn:"urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)"} ,]
      }
    )
}
```

예상 응답:

```python
{
  "data": {
    "removeOwner": true
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
--data-raw '{ "query": "mutation removeOwner { removeOwner(input: { ownerUrn: \"urn:li:corpuser:jdoe\", resourceUrn: \"urn:li:dataset:(urn:li:dataPlatform:hdfs,SampleHdfsDataset,PROD)\" }) }", "variables":{}}'
```

</TabItem>
<TabItem value="python" label="Python">

```python
{{ inline /metadata-ingestion/examples/library/dataset_remove_owner_execute_graphql.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Owner 제거의 예상 결과

이제 `John Doe`가 `fct_users_created` dataset의 owner에서 제거된 것을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/owner-removed.png"/>
</p>
