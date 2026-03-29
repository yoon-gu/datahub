import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Custom Assertions

이 가이드는 DataHub에서 custom assertions를 생성하고 결과를 보고하는 방법을 구체적으로 다룹니다.
Custom Assertions는 DataHub에서 기본적으로 실행되거나 직접 모델링되지 않으며 서드파티 프레임워크나 도구에서 관리되는 것입니다.

DataHub가 관리하도록 API를 사용하여 _기본_ assertions를 생성하려면 [Assertions API](./assertions.md)를 참조하세요.

이 가이드는 자체 모니터링 도구를 DataHub와 통합하려는 파트너를 위한 참조로 사용될 수 있습니다.

## 이 가이드의 목표

이 가이드에서 다음을 배우게 됩니다:

1. GraphQL 및 Python API를 통해 custom assertions 생성 및 업데이트
2. GraphQL 및 Python API를 통해 custom assertions 결과 보고
3. GraphQL 및 Python API를 통해 custom assertions 결과 조회
4. GraphQL 및 Python API를 통해 custom assertions 삭제

## 사전 요구 사항

API 호출을 수행하는 액터는 모니터링 중인 테이블에 대해 `Edit Assertions` 및 `Edit Monitors` 권한이 있어야 합니다.

## Custom Assertions 생성 및 업데이트

DataHub의 Dataset에 대해 다음 API를 사용하여 custom assertions를 생성할 수 있습니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

새 assertion을 생성하려면 `upsertCustomAssertion` GraphQL Mutation을 사용하세요. 이 mutation을 사용하면 지정된 assertion을 생성하고 업데이트할 수 있습니다.

```graphql
mutation upsertCustomAssertion {
  upsertCustomAssertion(
    urn: "urn:li:assertion:my-custom-assertion-id" # 선택 사항: 커스텀 ID를 제공하려는 경우. 그렇지 않으면 자동으로 생성됩니다.
    input: {
      entityUrn: "<urn of entity being monitored>"
      type: "My Custom Category" # 이것이 DataHub에서 assertion이 분류되어 표시되는 방식입니다.
      description: "The description of my external assertion for my dataset"
      platform: {
        urn: "urn:li:dataPlatform:great-expectations" # 또는 플랫폼 URN이 없는 경우 name: "My Custom Platform"을 제공할 수 있습니다.
      }
      fieldPath: "field_foo" # 선택 사항: 특정 필드와 연결하려는 경우
      externalUrl: "https://my-monitoring-tool.com/result-for-this-assertion" # 선택 사항: 모니터링 도구 링크를 제공하려는 경우
      # 선택 사항: assertion에 대한 커스텀 SQL 쿼리를 제공하려는 경우. UI에서 쿼리로 렌더링됩니다.
      # logic: "SELECT * FROM X WHERE Y"
    }
  ) {
    urn
  }
}
```

assertion에 고유한 `urn`을 제공할 수 있으며, 이는 다음 형식으로 해당 assertion urn을 생성하는 데 사용됩니다:

`urn:li:assertion:<your-new-assertion-id>`

또는 임의의 urn이 자동으로 생성되어 반환됩니다. 이 ID는 시간이 지나도 안정적이어야 하며 각 assertion마다 고유해야 합니다.

upsert API가 성공하면 assertion에 대한 고유 식별자(URN)를 반환합니다:

```json
{
  "data": {
    "upsertExternalAssertion": {
      "urn": "urn:li:assertion:your-new-assertion-id"
    }
  },
  "extensions": {}
}
```

</TabItem>

<TabItem value="python" label="Python">

Python에서 assertion을 upsert하려면 DataHub Client 오브젝트의 `upsert_external_assertion` 메서드를 사용하세요.

```python
{{ inline /metadata-ingestion/examples/library/upsert_custom_assertion.py show_path_as_comment }}
```

</TabItem>

</Tabs>

## Custom Assertions 결과 보고

dataset에 대해 assertion이 평가되거나 새 결과가 사용 가능할 때 다음 API를 사용하여 DataHub에 결과를 보고할 수 있습니다.

보고되면 assertion의 평가 이력에 표시되며 DataHub UI에서 assertion이 통과 또는 실패로 표시되는지 결정하는 데 사용됩니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

custom에 대한 결과를 보고하려면 `reportAssertionResult` GraphQL Mutation을 사용하세요. 이 mutation을 사용하면 지정된 assertion을 생성하고 업데이트할 수 있습니다.

```graphql
mutation reportAssertionResult {
  reportAssertionResult(
    urn: "urn:li:assertion:<your-new-assertion-id>"
    result: {
      timestampMillis: 1620000000000 # Unix 타임스탬프(밀리초). 제공되지 않으면 현재 시간이 사용됩니다.
      type: SUCCESS # 또는 FAILURE 또는 ERROR 또는 INIT
      properties: [{ key: "my_custom_key", value: "my_custom_value" }]
      externalUrl: "https://my-great-expectations.com/results/1234" # 선택 사항: 외부 도구의 결과 URL
      # 선택 사항: type이 ERROR인 경우 추가 컨텍스트를 제공할 수 있습니다. 아래의 전체 오류 유형 목록 참조.
      # error: {
      #    type: UNKNOWN_ERROR,
      #    message: "The assertion failed due to an unknown error"
      # }
    }
  )
}
```

`type` 필드는 assertion의 최신 상태를 전달하는 데 사용됩니다.

`properties` 필드는 DataHub UI에서 결과와 함께 표시될 추가 키-값 쌍 컨텍스트를 제공하는 데 사용됩니다.

지원되는 전체 오류 유형 목록:

- SOURCE_CONNECTION_ERROR
- SOURCE_QUERY_FAILED
- INSUFFICIENT_DATA
- INVALID_PARAMETERS
- INVALID_SOURCE_TYPE
- UNSUPPORTED_PLATFORM
- CUSTOM_SQL_ERROR
- FIELD_ASSERTION_ERROR
- UNKNOWN_ERROR

```json
{
  "data": {
    "reportAssertionResult": true
  },
  "extensions": {}
}
```

결과가 `true`이면 결과가 성공적으로 보고된 것입니다.

</TabItem>

<TabItem value="python" label="Python">

Python에서 assertion 결과를 보고하려면 DataHub Client 오브젝트의 `report_assertion_result` 메서드를 사용하세요.

```python
{{ inline /metadata-ingestion/examples/library/report_assertion_result.py show_path_as_comment }}
```

</TabItem>

</Tabs>

## Custom Assertions 결과 조회

assertion이 생성되고 실행된 후 특정 dataset URN과 관련된 assertions 집합에 표시됩니다.
다음 API를 사용하여 이러한 assertions의 결과를 조회할 수 있습니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

### Dataset에 대한 Assertions 가져오기

테이블/dataset에 대한 모든 assertions를 조회하려면 다음 GraphQL Query를 사용할 수 있습니다.

```graphql
query dataset {
  dataset(
    urn: "urn:li:dataset:(urn:li:dataPlatform:snowflake,purchases,PROD)"
  ) {
    assertions(start: 0, count: 1000) {
      start
      count
      total
      assertions {
        urn
        # 관련된 각 assertion의 마지막 실행을 가져옵니다.
        runEvents(status: COMPLETE, limit: 1) {
          total
          failed
          succeeded
          runEvents {
            timestampMillis
            status
            result {
              type
              nativeResults {
                key
                value
              }
            }
          }
        }
        info {
          type # CUSTOM이 됩니다
          customType # 커스텀 유형이 됩니다.
          description
          lastUpdated {
            time
            actor
          }
          customAssertion {
            entityUrn
            fieldPath
            externalUrl
            logic
          }
          source {
            type
            created {
              time
              actor
            }
          }
        }
      }
    }
  }
}
```

### Assertion 상세 정보 가져오기

다음 GraphQL 쿼리를 사용하여 URN으로 assertion의 상세 정보와 평가 이력을 가져올 수 있습니다.

```graphql
query getAssertion {
  assertion(urn: "urn:li:assertion:my-custom-assertion-id") {
    urn
    # assertion에 대한 마지막 10개의 실행을 가져옵니다.
    runEvents(status: COMPLETE, limit: 10) {
      total
      failed
      succeeded
      runEvents {
        timestampMillis
        status
        result {
          type
          nativeResults {
            key
            value
          }
        }
      }
    }
    info {
      type # CUSTOM이 됩니다
      customType # 커스텀 유형이 됩니다.
      description
      lastUpdated {
        time
        actor
      }
      customAssertion {
        entityUrn
        fieldPath
        externalUrl
        logic
      }
      source {
        type
        created {
          time
          actor
        }
      }
    }
    # assertion이 연결된 entities 가져오기
    relationships(input: { types: ["Asserts"], direction: OUTGOING }) {
      total
      relationships {
        entity {
          urn
        }
      }
    }
  }
}
```

</TabItem>
</Tabs>
