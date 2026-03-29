import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Data Contracts

<FeatureAvailability saasOnly />

이 가이드는 **DataHub Cloud**에서 Data Contract API를 사용하는 방법을 구체적으로 다룹니다.

## Data Contract API를 사용하는 이유

Assertions API를 사용하면 Data Contracts를 프로그래밍 방식으로 생성, 업데이트, 평가할 수 있습니다. 이는 데이터의 품질 및 schema 준수 모니터링을 자동화하는 데 특히 유용합니다.

### 이 가이드의 목표

이 가이드에서는 Data Contract를 생성, 업데이트하고 상태를 확인하는 방법을 보여줍니다.

## 사전 요구 사항

### 필요한 권한

API 호출을 수행하는 액터는 해당 테이블에 대해 `Edit Data Contract` 권한이 있어야 합니다.

### Assertions

Data Contract를 생성하기 전에 Data Contract와 연결할 Assertions를 이미 생성해 두어야 합니다.
DataHub Assertions 생성 방법은 [Assertions](/docs/api/tutorials/assertions.md) 가이드를 참조하세요.

## Data Contract 생성 및 업데이트

다음 API를 사용하여 "중요한" assertions의 묶음인 새 Data Contract를 생성할 수 있습니다.

<Tabs>
<TabItem value="graphql" label="GraphQL" default>

Data Contract를 생성하거나 업데이트하려면 `upsertDataContract` GraphQL Mutation을 사용하세요.

```graphql
mutation upsertDataContract {
    upsertDataContract(
      input: {
        entityUrn: "urn:li:dataset:(urn:li:dataPlatform:snowflake,purchases,PROD)", # Contract를 생성할 테이블
        freshness: [
            {
                assertionUrn: "urn:li:assertion:your-freshness-assertion-id",
            }
        ],
        schema: [
            {
                assertionUrn: "urn:li:assertion:your-schema-assertion-id",
            }
        ],
        dataQuality: [
            {
                assertionUrn: "urn:li:assertion:your-column-assertion-id-1",
            },
            {
                assertionUrn: "urn:li:assertion:your-column-assertion-id-2",
            }
        ]
      }) {
        urn
      }
  )
}
```

성공하면 이 API는 Data Contract에 대한 고유 식별자(URN)를 반환합니다:

```json
{
  "data": {
    "upsertDataContract": {
      "urn": "urn:li:dataContract:your-new-contract-id"
    }
  },
  "extensions": {}
}
```

기존 Data Contract를 업데이트하려면 동일한 API를 사용하되 `upsertDataContract` mutation에 `urn` 파라미터도 전달하면 됩니다.

```graphql
mutation upsertDataContract {
    upsertDataContract(
      urn: "urn:li:dataContract:your-existing-contract-id",
      input: {
        freshness: [
            {
                assertionUrn: "urn:li:assertion:your-freshness-assertion-id",
            }
        ],
        schema: [
            {
                assertionUrn: "urn:li:assertion:your-schema-assertion-id",
            }
        ],
        dataQuality: [
            {
                assertionUrn: "urn:li:assertion:your-column-assertion-id-1",
            },
            {
                assertionUrn: "urn:li:assertion:your-column-assertion-id-2",
            }
        ]
      }) {
        urn
      }
  )
}
```

</TabItem>
</Tabs>

## Contract 상태 확인

다음 API를 사용하여 Data Contract의 통과 또는 실패 여부를 확인할 수 있습니다. 이는 contract와 연결된 assertions의 마지막 상태에 의해 결정됩니다.

<Tabs>

<TabItem value="graphql" label="GraphQL" default>

### 테이블의 Contract 상태 확인

```graphql
query getTableContractStatus {
  dataset(urn: "urn:li:dataset(urn:li:dataPlatform:snowflake,purchases,PROD") {
    contract {
      result {
        type # 통과 또는 실패.
        assertionResults {
          # 각 contract assertion의 결과.
          assertion {
            urn
          }
          result {
            type
            nativeResults {
              key
              value
            }
          }
        }
      }
    }
  }
}
```

쿼리에 `refresh` 인수를 제공하여 모든 Contract Assertions를 온디맨드로 평가함으로써 _강제 새로 고침_할 수도 있습니다.

```graphql
query getTableContractStatus {
  dataset(urn: "urn:li:dataset(urn:li:dataPlatform:snowflake,purchases,PROD") {
    contract(refresh: true) {
      ...same
    }
  }
}
```

이렇게 하면 Data Contract를 구성하는 모든 네이티브 DataHub Cloud assertions가 실행됩니다. 주의하세요! contract의 일부인 네이티브 assertions 수에 따라 시간이 걸릴 수 있습니다.

성공하면 테이블 Contract의 최신 상태를 얻을 수 있습니다:

```json
{
  "data": {
    "dataset": {
      "contract": {
        "result": {
          "type": "PASSING",
          "assertionResults": [
            {
              "assertion": {
                "urn": "urn:li:assertion:your-freshness-assertion-id"
              },
              "result": {
                "type": "SUCCESS",
                "nativeResults": [
                  {
                    "key": "Value",
                    "value": "1382"
                  }
                ]
              }
            },
            {
              "assertion": {
                "urn": "urn:li:assertion:your-volume-assertion-id"
              },
              "result": {
                "type": "SUCCESS",
                "nativeResults": [
                  {
                    "key": "Value",
                    "value": "12323"
                  }
                ]
              }
            }
          ]
        }
      }
    }
  },
  "extensions": {}
}
```

</TabItem>

</Tabs>
