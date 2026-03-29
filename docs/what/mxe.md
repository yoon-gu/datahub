# 메타데이터 이벤트

DataHub는 운영을 위해 몇 가지 중요한 Kafka 이벤트를 사용합니다. 가장 주목할 만한 이벤트는 다음과 같습니다.

1. Metadata Change Proposal
2. Metadata Change Log (버전 관리형 + 시계열형)
3. Platform Event

각 이벤트는 LinkedIn이 개발한 모델링 언어인 [PDL](https://linkedin.github.io/rest.li/pdl_schema)을 사용하여 작성된 후, Kafka에서 이벤트를 쓰고 읽을 때 사용되는 Avro 형식으로 변환됩니다.

이 문서에서는 각 이벤트의 구조 및 의미론적 특성을 포함하여 각 이벤트를 상세히 설명합니다.

## Metadata Change Proposal (MCP)

Metadata Change Proposal은 기업의 메타데이터 그래프에서 특정 [aspect](aspect.md)를 변경하기 위한 요청을 나타냅니다. 각 MCP는 주어진 aspect의 새로운 값을 제공합니다. 예를 들어, 단일 MCP로 데이터 자산의 소유권, 문서, 도메인 또는 사용 중단 상태를 변경하도록 발행할 수 있습니다.

### 발행 (Emission)

MCP는 메타데이터 ingestion 과정에서 DataHub의 저수준 ingestion API 클라이언트(예: ingestion 소스)가 발행할 수 있습니다. DataHub Python API는 MCP를 DataHub로 쉽게 전송할 수 있는 인터페이스를 제공합니다.

MCP의 기본 Kafka 토픽 이름은 `MetadataChangeProposal_v1`입니다.

### 소비 (Consumption)

DataHub의 스토리지 계층은 새로운 Metadata Change Proposal을 능동적으로 수신하여 메타데이터 그래프에 요청된 변경 사항을 적용하려고 시도합니다.

### 스키마

| 이름               | 타입   | 설명                                                                                                                                                                                                                                       | 선택적 여부 |
| ------------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| entityUrn          | String | 변경 대상 Entity의 고유 식별자. 예: Dataset의 URN.                                                                                                                                                                                         | False    |
| entityType         | String | 새 aspect와 연관된 entity의 타입. DataHub Entity Registry의 entity 이름에 해당합니다. 예: 'dataset'.                                                                                                                                       | False    |
| entityKeyAspect    | Object | 변경된 entity의 키 구조체. Metadata Change Proposal이 원시 키 구조체를 포함한 경우에만 존재합니다.                                                                                                                                          | True     |
| changeType         | String | 변경 타입. 현재 CREATE, UPSERT, DELETE가 지원됩니다. PATCH는 특정 aspect에 대해 제한적으로 지원됩니다.                                                                                                                                      | False    |
| aspectName         | String | 변경된 entity aspect.                                                                                                                                                                                                                       | False    |
| aspect             | Object | 새로운 aspect 값. aspect가 삭제된 경우 Null.                                                                                                                                                                                                | True     |
| aspect.contentType | String | aspect 자체의 직렬화 타입. 지원되는 유일한 값은 `application/json`입니다.                                                                                                                                                                   | False    |
| aspect.value       | String | 직렬화된 aspect. PDL로 정의된 aspect 문서를 JSON으로 직렬화한 것입니다. 자세한 내용은 https://github.com/datahub-project/datahub/tree/master/metadata-models/src/main/pegasus/com/linkedin 을 참조하세요.                                   | False    |
| systemMetadata     | Object | 새로운 시스템 메타데이터. ingestion 실행 ID, 모델 레지스트리 등을 포함합니다. 전체 구조는 https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/mxe/SystemMetadata.pdl 을 참조하세요.         | True     |

PDL 스키마는 [여기](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/mxe/MetadataChangeProposal.pdl)에서 확인할 수 있습니다.

### 예시

특정 Dataset의 'ownership' aspect 업데이트 요청을 나타내는 MCP:

```json
{
  "entityType": "dataset",
  "entityUrn": "urn:li:dataset:(urn:li:dataPlatform:hdfs,SampleHdfsDataset,PROD)",
  "changeType": "UPSERT",
  "aspectName": "ownership",
  "aspect": {
    "value": "{\"owners\":[{\"type\":\"DATAOWNER\",\"owner\":\"urn:li:corpuser:datahub\"}],\"lastModified\":{\"actor\":\"urn:li:corpuser:datahub\",\"time\":1651516640488}}",
    "contentType": "application/json"
  },
  "systemMetadata": {
    "lastObserved": 1651516640493,
    "runId": "no-run-id-provided",
    "registryName": "unknownRegistry",
    "registryVersion": "0.0.0.0-dev",
    "properties": null
  }
}
```

aspect 페이로드가 "value" 필드 내에 JSON으로 직렬화된 방식에 주목하세요. aspect의 정확한 구조는 PDL 스키마에 의해 결정됩니다. (예: [ownership](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/Ownership.pdl) 스키마)

## Metadata Change Log (MCL)

Metadata Change Log는 메타데이터 그래프에 적용된 _모든_ 변경 사항을 나타냅니다.
Metadata Change Log 이벤트는 변경 사항이 내구성 있는 스토리지에 기록된 직후 Kafka로 발행됩니다.

Metadata Change Log에는 _버전 관리형(versioned)_ 과 _시계열형(timeseries)_ 의 두 가지 유형이 있습니다. 이는 주어진 변경에 대해 업데이트된 aspect의 타입에 해당합니다. **버전 관리형** aspect는 일부 속성의 "최신" 상태를 나타내는 것으로, 예를 들어 자산의 가장 최근 소유자나 문서가 해당됩니다. **시계열형** aspect는 특정 시점에 발생한 자산 관련 이벤트를 나타내는 것으로, 예를 들어 Dataset의 프로파일링이 해당됩니다.

### 발행 (Emission)

MCL은 DataHub 메타데이터 그래프의 entity에 _어떠한_ 변경이든 적용될 때 발행됩니다. 여기에는 entity의 어떤 aspect에 대한 쓰기도 포함됩니다.

Metadata Change Log에는 두 개의 별도 토픽이 유지됩니다. **버전 관리형** aspect의 기본 Kafka 토픽 이름은 `MetadataChangeLog_Versioned_v1`이고, **시계열형** aspect의 경우 `MetadataChangeLog_Timeseries_v1`입니다.

### 소비 (Consumption)

DataHub는 MCL을 수신하여 DataHub의 검색 및 그래프 인덱스를 업데이트하고, 아래에서 설명하는 파생 Platform Event를 생성하는 Kafka Consumer Job(mae-consumer-job)과 함께 제공됩니다.

또한, [Actions Framework](../actions/README.md)는 [Metadata Change Log](../actions/events/metadata-change-log-event.md) 이벤트 API를 지원하기 위해 Metadata Change Log를 소비합니다.

### 스키마

| 이름                            | 타입   | 설명                                                                                                                                                                                                                                            | 선택적 여부 |
| ------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| entityUrn                       | String | 변경 대상 Entity의 고유 식별자. 예: Dataset의 URN.                                                                                                                                                                                              | False    |
| entityType                      | String | 새 aspect와 연관된 entity의 타입. DataHub Entity Registry의 entity 이름에 해당합니다. 예: 'dataset'.                                                                                                                                             | False    |
| entityKeyAspect                 | Object | 변경된 entity의 키 구조체. Metadata Change Proposal이 원시 키 구조체를 포함한 경우에만 존재합니다.                                                                                                                                               | True     |
| changeType                      | String | 변경 타입. 현재 CREATE, UPSERT, DELETE가 지원됩니다.                                                                                                                                                                                             | False    |
| aspectName                      | String | 변경된 entity aspect.                                                                                                                                                                                                                             | False    |
| aspect                          | Object | 새로운 aspect 값. aspect가 삭제된 경우 Null.                                                                                                                                                                                                     | True     |
| aspect.contentType              | String | aspect 자체의 직렬화 타입. 지원되는 유일한 값은 `application/json`입니다.                                                                                                                                                                        | False    |
| aspect.value                    | String | 직렬화된 aspect. PDL로 정의된 aspect 문서를 JSON으로 직렬화한 것입니다. 자세한 내용은 https://github.com/datahub-project/datahub/tree/master/metadata-models/src/main/pegasus/com/linkedin 을 참조하세요.                                        | False    |
| previousAspectValue             | Object | 이전 aspect 값. 해당 aspect가 이전에 존재하지 않았다면 Null.                                                                                                                                                                                     | True     |
| previousAspectValue.contentType | String | aspect 자체의 직렬화 타입. 지원되는 유일한 값은 `application/json`입니다.                                                                                                                                                                        | False    |
| previousAspectValue.value       | String | 직렬화된 aspect. PDL로 정의된 aspect 문서를 JSON으로 직렬화한 것입니다. 자세한 내용은 https://github.com/datahub-project/datahub/tree/master/metadata-models/src/main/pegasus/com/linkedin 을 참조하세요.                                        | False    |
| systemMetadata                  | Object | 새로운 시스템 메타데이터. ingestion 실행 ID, 모델 레지스트리 등을 포함합니다. 전체 구조는 https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/mxe/SystemMetadata.pdl 을 참조하세요.              | True     |
| previousSystemMetadata          | Object | 이전 시스템 메타데이터. ingestion 실행 ID, 모델 레지스트리 등을 포함합니다. 전체 구조는 https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/mxe/SystemMetadata.pdl 을 참조하세요.               | True     |
| created                         | Object | 메타데이터 변경을 트리거한 사람과 시점에 대한 감사 스탬프.                                                                                                                                                                                       | False    |
| created.time                    | Number | aspect 변경이 발생한 시점의 밀리초 단위 타임스탬프.                                                                                                                                                                                              | False    |
| created.actor                   | String | 변경을 트리거한 행위자(예: corpuser)의 URN.                                                                                                                                                                                                      |

PDL 스키마는 [여기](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/mxe/MetadataChangeLog.pdl)에서 확인할 수 있습니다.

### 예시

특정 Dataset의 'ownership' aspect 변경에 해당하는 MCL:

```json
{
  "entityType": "dataset",
  "entityUrn": "urn:li:dataset:(urn:li:dataPlatform:hdfs,SampleHdfsDataset,PROD)",
  "changeType": "UPSERT",
  "aspectName": "ownership",
  "aspect": {
    "value": "{\"owners\":[{\"type\":\"DATAOWNER\",\"owner\":\"urn:li:corpuser:datahub\"}],\"lastModified\":{\"actor\":\"urn:li:corpuser:datahub\",\"time\":1651516640488}}",
    "contentType": "application/json"
  },
  "previousAspectValue": {
    "value": "{\"owners\":[{\"owner\":\"urn:li:corpuser:jdoe\",\"type\":\"DATAOWNER\"},{\"owner\":\"urn:li:corpuser:datahub\",\"type\":\"DATAOWNER\"}],\"lastModified\":{\"actor\":\"urn:li:corpuser:jdoe\",\"time\":1581407189000}}",
    "contentType": "application/json"
  },
  "systemMetadata": {
    "lastObserved": 1651516640493,
    "runId": "no-run-id-provided",
    "registryName": "unknownRegistry",
    "registryVersion": "0.0.0.0-dev",
    "properties": null
  },
  "previousSystemMetadata": {
    "lastObserved": 1651516415088,
    "runId": "file-2022_05_02-11_33_35",
    "registryName": null,
    "registryVersion": null,
    "properties": null
  },
  "created": {
    "time": 1651516640490,
    "actor": "urn:li:corpuser:datahub",
    "impersonator": null
  }
}
```

aspect 페이로드가 "value" 필드 내에 JSON으로 직렬화된 방식에 주목하세요. aspect의 정확한 구조는 PDL 스키마에 의해 결정됩니다. (예: [ownership](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/Ownership.pdl) 스키마)

## Platform Event (PE)

Platform Event는 DataHub가 발행하는 임의의 비즈니스 로직 이벤트를 나타냅니다. 각
Platform Event는 콘텐츠를 결정하는 `name`을 가집니다.

### 타입

- **Entity Change Event** (entityChangeEvent): 가장 중요한 Platform Event로 **Entity Change Event**라고 하며, DataHub에서 발생한 의미론적 변경(태그 추가, 제거, 사용 중단 변경 등)의 로그를 나타냅니다. DataHub Actions Framework의 중요한 구성 요소로 사용됩니다.

등록된 모든 Platform Event 타입은 DataHub Entity Registry(`entity-registry.yml`) 내에 선언됩니다.

### 발행 (Emission)

모든 Platform Event는 DataHub 자체의 정상 운영 중에 생성됩니다.

PE는 매우 동적입니다. `name`에 따라 임의의 페이로드를 포함할 수 있으므로,
다양한 상황에서 발행될 수 있습니다.

모든 Platform Event의 기본 Kafka 토픽 이름은 `PlatformEvent_v1`입니다.

### 소비 (Consumption)

[Actions Framework](../actions/README.md)는 [Entity Change Event](../actions/events/entity-change-event.md) API를 지원하기 위해 Platform Event를 소비합니다.

### 스키마

| 이름                   | 타입   | 설명                                                                                                                                                                                                                       | 선택적 여부 |
| ---------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| header                 | Object | 헤더 필드                                                                                                                                                                                                                  | False    |
| header.timestampMillis | Long   | 이벤트가 생성된 시점.                                                                                                                                                                                                      | False    |
| name                   | String | 이벤트의 이름/타입.                                                                                                                                                                                                        | False    |
| payload                | Object | 이벤트 자체.                                                                                                                                                                                                               | False    |
| payload.contentType    | String | 이벤트 페이로드의 직렬화 타입. 지원되는 유일한 값은 `application/json`입니다.                                                                                                                                              | False    |
| payload.value          | String | 직렬화된 페이로드. PDL로 정의된 페이로드 문서를 JSON으로 직렬화한 것입니다. 자세한 내용은 https://github.com/datahub-project/datahub/tree/master/metadata-models/src/main/pegasus/com/linkedin 을 참조하세요.              | False    |

전체 PDL 스키마는 [여기](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/mxe/PlatformEvent.pdl)에서 확인할 수 있습니다.

### 예시

Dataset에 새 소유자가 추가될 때 발행되는 'Entity Change Event' Platform Event 예시:

```json
{
  "header": {
    "timestampMillis": 1655390732551
  },
  "name": "entityChangeEvent",
  "payload": {
    "value": "{\"entityUrn\":\"urn:li:dataset:abc\",\"entityType\":\"dataset\",\"category\":\"OWNER\",\"operation\":\"ADD\",\"modifier\":\"urn:li:corpuser:jdoe\",\"parameters\":{\"ownerUrn\":\"urn:li:corpuser:jdoe\",\"ownerType\":\"BUSINESS_OWNER\"},\"auditStamp\":{\"actor\":\"urn:li:corpuser:jdoe\",\"time\":1649953100653}}",
    "contentType": "application/json"
}
```

이벤트의 실제 페이로드가 'payload' 필드 내에 JSON으로 직렬화된 방식에 주목하세요. Platform Event의 정확한 구조는 PDL 스키마에 의해 결정됩니다. (예: [Entity Change Event](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/platform/event/v1/EntityChangeEvent.pdl) 스키마)

## Failed Metadata Change Proposal (FMCP)

Metadata Change Proposal을 성공적으로 처리할 수 없는 경우, 해당 이벤트는 Failed Metadata Change Proposal (FMCP)라는 이벤트로 [dead letter queue](https://en.wikipedia.org/wiki/Dead_letter_queue)에 기록됩니다.

이 이벤트는 원본 Metadata Change Proposal과 거부 이유가 담긴 오류 메시지를 단순히 래핑합니다.
이 이벤트는 잠재적인 ingestion 문제를 디버깅하거나 필요 시 이전에 거부된 proposal을 재처리하는 데 활용할 수 있습니다.

### 발행 (Emission)

FMCE는 MCE를 DataHub의 스토리지 계층에 성공적으로 커밋할 수 없을 때 발행됩니다.

FMCPs의 기본 Kafka 토픽 이름은 `FailedMetadataChangeProposal_v1`입니다.

### 소비 (Consumption)

활성 소비자 없음.

### 스키마

PDL 스키마는 [여기](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/mxe/FailedMetadataChangeProposal.pdl)에서 확인할 수 있습니다.

# 사용 중단된 이벤트

DataHub에는 메타데이터 그래프에 대한 변경을 제안하고 기록하는 데 과거에 사용된 사용 중단된 이벤트 세트가 포함되어 있습니다.

이 카테고리의 각 이벤트는 비유연성으로 인해 사용 중단되었습니다. 구체적으로는 새로운 aspect가 도입될 때마다 스키마를 업데이트해야 했던 문제가 있었습니다. 이 이벤트들은 위에서 설명한 더 유연한 이벤트(Metadata Change Proposal, Metadata Change Log)로 대체되었습니다.

사용 중단된 이벤트에 의존성을 구축하는 것은 권장되지 않습니다.

## Metadata Change Event (MCE)

Metadata Change Event는 동일한 entity에 대한 여러 aspect 변경 요청을 나타냅니다.
이는 동일한 entity에 대한 강타입 aspect 목록인 `Snapshot`이라는 사용 중단된 개념을 활용합니다.

MCE는 메타데이터 변경 집합에 대한 "제안"이며, 이는 커밋된 변경을 전달하는 [MAE](#metadata-audit-event-mae)와 대조됩니다.
따라서 성공적으로 수락 및 처리된 MCE만이 해당 MAE / MCL의 발행으로 이어집니다.

### 발행 (Emission)

MCE는 메타데이터 ingestion 과정에서 DataHub의 저수준 ingestion API 클라이언트(예: ingestion 소스)가 발행할 수 있습니다.

MCE의 기본 Kafka 토픽 이름은 `MetadataChangeEvent_v4`입니다.

### 소비 (Consumption)

DataHub의 스토리지 계층은 새로운 Metadata Change Event를 능동적으로 수신하여 메타데이터 그래프에 요청된 변경 사항을 적용하려고 시도합니다.

### 스키마

PDL 스키마는 [여기](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/mxe/MetadataChangeEvent.pdl)에서 확인할 수 있습니다.

### 예시

Entity의 'ownership' aspect를 변경하기 위해 발행된 MCE 예시:

```json
{
  "proposedSnapshot": {
    "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot": {
      "urn": "urn:li:dataset:(urn:li:dataPlatform:hive,SampleHiveDataset,PROD)",
      "aspects": [
        {
          "com.linkedin.pegasus2avro.common.Ownership": {
            "owners": [
              {
                "owner": "urn:li:corpuser:jdoe",
                "type": "DATAOWNER",
                "source": null
              },
              {
                "owner": "urn:li:corpuser:datahub",
                "type": "DATAOWNER",
                "source": null
              }
            ],
            "lastModified": {
              "time": 1581407189000,
              "actor": "urn:li:corpuser:jdoe",
              "impersonator": null
            }
          }
        }
      ]
    }
  }
}
```

## Metadata Audit Event (MAE)

Metadata Audit Event는 특정 [entity](entity.md)와 연관된 하나 또는 여러 메타데이터 [aspect](aspect.md)에 대한 변경을 캡처합니다. 변경 전의 메타데이터 [snapshot](snapshot.md)(사용 중단됨)과 변경 후의 메타데이터 snapshot 형태로 표현됩니다.

특정 메타데이터 aspect의 모든 진실의 원천(source-of-truth)은 해당 aspect에 변경이 커밋될 때마다 MAE를 발행해야 합니다. 이를 보장함으로써, MAE의 모든 리스너는 모든 aspect의 최신 상태에 대한 완전한 뷰를 구성할 수 있습니다.
또한 각 MAE에는 "변경 후 이미지"가 포함되어 있으므로, MAE 발행 시 실수가 발생하더라도 수정된 내용으로 후속 MAE를 발행함으로써 쉽게 수정할 수 있습니다. 같은 이유로, 새로 추가된 entity에 대한 초기 부트스트랩 문제도 해당 entity와 연관된 모든 최신 메타데이터 aspect를 포함한 MAE를 발행함으로써 해결할 수 있습니다.

### 발행 (Emission)

> 참고: DataHub의 최근 버전(2022년 중반 이후)에서는 MAE가 더 이상 능동적으로 발행되지 않으며, 곧 DataHub에서 완전히 제거될 예정입니다.
> 대신 Metadata Change Log를 사용하세요.

MAE는 메타데이터 변경이 DataHub의 스토리지 계층에 성공적으로 커밋된 후 발행됩니다.

MAE의 기본 Kafka 토픽 이름은 `MetadataAuditEvent_v4`입니다.

### 소비 (Consumption)

활성 소비자 없음.

### 스키마

PDL 스키마는 [여기](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/mxe/MetadataAuditEvent.pdl)에서 확인할 수 있습니다.

### 예시

Entity의 'ownership' aspect 변경(소유자 제거)을 나타내는 MAE 예시:

```json
{
  "oldSnapshot": {
    "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot": {
      "urn": "urn:li:dataset:(urn:li:dataPlatform:hive,SampleHiveDataset,PROD)",
      "aspects": [
        {
          "com.linkedin.pegasus2avro.common.Ownership": {
            "owners": [
              {
                "owner": "urn:li:corpuser:jdoe",
                "type": "DATAOWNER",
                "source": null
              },
              {
                "owner": "urn:li:corpuser:datahub",
                "type": "DATAOWNER",
                "source": null
              }
            ],
            "lastModified": {
              "time": 1581407189000,
              "actor": "urn:li:corpuser:jdoe",
              "impersonator": null
            }
          }
        }
      ]
    }
  },
  "newSnapshot": {
    "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot": {
      "urn": "urn:li:dataset:(urn:li:dataPlatform:hive,SampleHiveDataset,PROD)",
      "aspects": [
        {
          "com.linkedin.pegasus2avro.common.Ownership": {
            "owners": [
              {
                "owner": "urn:li:corpuser:datahub",
                "type": "DATAOWNER",
                "source": null
              }
            ],
            "lastModified": {
              "time": 1581407189000,
              "actor": "urn:li:corpuser:jdoe",
              "impersonator": null
            }
          }
        }
      ]
    }
  }
}
```

## Failed Metadata Change Event (FMCE)

Metadata Change Event를 성공적으로 처리할 수 없는 경우, 해당 이벤트는 Failed Metadata Change Event (FMCE)라는 이벤트로 [dead letter queue](https://en.wikipedia.org/wiki/Dead_letter_queue)에 기록됩니다.

이 이벤트는 원본 Metadata Change Event와 거부 이유가 담긴 오류 메시지를 단순히 래핑합니다.
이 이벤트는 잠재적인 ingestion 문제를 디버깅하거나 필요 시 이전에 거부된 proposal을 재처리하는 데 활용할 수 있습니다.

### 발행 (Emission)

FMCE는 MCE를 DataHub의 스토리지 계층에 성공적으로 커밋할 수 없을 때 발행됩니다.

### 소비 (Consumption)

활성 소비자 없음.

### 스키마

PDL 스키마는 [여기](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/mxe/FailedMetadataChangeEvent.pdl)에서 확인할 수 있습니다.

FMCE의 기본 Kafka 토픽 이름은 `FailedMetadataChangeEvent_v4`입니다.
