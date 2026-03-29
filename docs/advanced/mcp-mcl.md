# MetadataChangeProposal & MetadataChangeLog 이벤트

## 개요 및 비전

v0.8.7 릴리스부터 두 가지 중요한 새 이벤트 스트림이 도입되었습니다: MetadataChangeProposal & MetadataChangeLog. 이 토픽들은 DataHub 메타데이터 그래프에 대한 변경 사항을 a) 제안하고 b) 기록하는 데 사용되는 기존 MetadataChangeEvent 및 MetadataAuditEvent 이벤트의 더 일반적인(더 적절하게 명명된) 버전 역할을 합니다.

이 이벤트들과 함께, 메타데이터 모델이 이벤트 스키마 자체의 강하게 타입화된 부분이 아닌 더 일반적인 세계로 나아갑니다. 이는 유연성을 제공하여, 메타데이터 그래프를 구성하는 핵심 모델들이 메타데이터 수집 및 서빙에 사용되는 Kafka나 REST API 스키마에 구조적 업데이트를 요구하지 않고 동적으로 추가되고 변경될 수 있게 합니다.

또한, DataHub에서 "aspect"를 쓰기의 원자적 단위로 집중했습니다. MetadataChangeProposal & MetadataChangeLog는 오늘날의 MCE & MAE가 전달하는 aspect 목록과 달리 페이로드에 단일 aspect만을 전달합니다. 이는 메타데이터 모델의 원자성 계약을 더 정확하게 반영하며, 다중 aspect 쓰기에 대한 트랜잭션 보장에 관한 혼란을 줄이고 소비자가 관심 있는 메타데이터 변경에 더 쉽게 집중할 수 있게 합니다.

이 이벤트들을 더 일반적으로 만드는 것은 공짜가 아닙니다. Restli 및 Kafka 네이티브 스키마 검증을 포기하고 이 책임을 메타데이터 그래프 모델 계약의 유일한 집행자인 DataHub 자체에게 위임합니다. 또한, 이벤트/응답 본문 자체와 중첩된 메타데이터 aspect의 이중 역직렬화를 요구함으로써 실제 메타데이터를 언번들링하는 추가 단계가 생깁니다.

이러한 단점을 완화하기 위해, 어려운 작업을 대신 처리할 수 있는 다국어 클라이언트 라이브러리를 제공하기로 했습니다. DataHub가 제공하는 "기본" 모델 세트에서 생성된 강타입 아티팩트로 이를 게시할 계획입니다. 이는 DataHub의 백엔드(gms)에 강타입 모델을 제공하는 OpenAPI 레이어를 도입하는 이니셔티브에 추가됩니다.

궁극적으로, 생성된 코드를 요구하지 않고 단일 메가 모델 스키마를 유지하지 않고도(Snapshot.pdl을 보세요) entity 및 Aspect 스키마를 변경할 수 있는 상태를 실현하고자 합니다. 의도는 메타데이터 모델의 변경이 오늘날보다 훨씬 쉬워지는 것입니다.

### 동기식 수집 아키텍처

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/advanced/mcp-mcl/sync-ingestion.svg"/>
</p>

### 비동기식 수집 아키텍처

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/advanced/mcp-mcl/async-ingestion.svg"/>
</p>

## 모델링

Metadata Change Proposal은 PDL로 다음과 같이 정의됩니다.

```protobuf
record MetadataChangeProposal {

  /**
   * Kafka audit header. See go/kafkaauditheader for more info.
   */
  auditHeader: optional KafkaAuditHeader

  /**
   * Type of the entity being written to
   */
  entityType: string

  /**
   * Urn of the entity being written
   **/
  entityUrn: optional Urn,

  /**
   * Key aspect of the entity being written
   */
  entityKeyAspect: optional GenericAspect

  /**
   * Type of change being proposed
   */
  changeType: ChangeType

  /**
   * Aspect of the entity being written to
   * Not filling this out implies that the writer wants to affect the entire entity
   * Note: This is only valid for CREATE and DELETE operations.
   **/
  aspectName: optional string

  aspect: optional GenericAspect

  /**
   * A string->string map of custom properties that one might want to attach to an event
   **/
  systemMetadata: optional SystemMetadata

  /**
  * Headers - intended to mimic http headers
  */
  headers: optional map[string, string]
}
```

각 proposal은 다음으로 구성됩니다:

1. entityType

   entity의 타입을 참조합니다. 예: dataset, chart

2. entityUrn

   업데이트되는 entity의 Urn. **정확히 하나의** entityUrn 또는 entityKeyAspect가 entity를 올바르게 식별하기 위해 입력되어야 합니다.

3. entityKeyAspect

   entity의 key aspect. 문자열 URN 대신 key aspect 구조체로 entity를 식별하는 것을 지원할 것입니다. 참고로, 이것은 현재 지원되지 않습니다.

4. changeType

   제안하는 변경 타입: 다음 중 하나

   - UPSERT: 존재하지 않으면 삽입, 그렇지 않으면 업데이트
   - CREATE: aspect가 존재하지 않으면 삽입, 그렇지 않으면 실패
   - CREATE_ENTITY: entity가 존재하지 않으면 삽입, 그렇지 않으면 실패
   - UPDATE: 존재하면 업데이트, 그렇지 않으면 실패
   - DELETE: 삭제
   - PATCH: 전체 교체 대신 aspect를 patch 적용

   현재 UPSERT, CREATE, CREATE_ENTITY, DELETE, PATCH만 지원됩니다.

5. aspectName

   aspect의 이름. "@Aspect" 어노테이션의 이름과 일치해야 합니다.

6. aspect

   기존 aspect들의 union을 추적하지 않고도 강타입 aspect를 지원하기 위해, GenericAspect라는 새 객체를 도입했습니다.

   ```xml
   record GenericAspect {
       value: bytes
       contentType: string
   }
   ```

   직렬화 타입과 직렬화된 값을 포함합니다. 현재는 "application/json"만 contentType으로 지원되지만 향후 더 많은 직렬화 형식을 추가할 것입니다. 직렬화된 객체의 유효성 검사는 GMS에서 aspectName과 일치하는 스키마에 대해 수행됩니다.

7. systemMetadata

   run_id 또는 업데이트된 타임스탬프와 같은 proposal에 대한 추가 메타데이터.

8. headers

   http 헤더를 모방하기 위한 선택적 헤더. 현재 조건부 쓰기 로직을 구현하는 데 사용됩니다.

GMS는 proposal을 처리하고 다음과 같은 Metadata Change Log를 생성합니다.

```protobuf
record MetadataChangeLog includes MetadataChangeProposal {

  previousAspectValue: optional GenericAspect

  previousSystemMetadata: optional SystemMetadata

}
```

proposal의 모든 필드를 포함하지만, 이전 버전의 aspect 값과 시스템 메타데이터도 포함합니다. 이를 통해 MCL 프로세서는 모든 인덱스를 업데이트하기로 결정하기 전에 이전 값을 알 수 있습니다.

## 토픽

이벤트 모델의 변화에 따라 4개의 새 토픽을 도입했습니다. 이 모델로 완전히 마이그레이션하면 이전 토픽들은 사용 중단될 예정입니다.

1. **MetadataChangeProposal_v1, FailedMetadataChangeProposal_v1**

   MCE 토픽과 유사하게, MetadataChangeProposal_v1 토픽에 생성된 proposal은 GMS에 비동기적으로 수집되고, 수집 실패 시 FailedMetadataChangeProposal_v1 토픽에 실패한 MCP가 생성됩니다.

2. **MetadataChangeLog_Versioned_v1**

   MAE 토픽과 유사하게, versioned aspect에 대한 MCL이 이 토픽에 생성됩니다. versioned aspect는 별도로 백업될 수 있는 진실의 원천을 가지고 있으므로, 이 토픽의 보존 기간은 짧습니다(기본값 7일). 이 토픽과 다음 토픽 모두 동일한 MCL 프로세서에 의해 소비됩니다.

3. **MetadataChangeLog_Timeseries_v1**

   MAE 토픽과 유사하게, timeseries aspect에 대한 MCL이 이 토픽에 생성됩니다. timeseries aspect는 진실의 원천을 가지지 않고 elasticsearch에 직접 수집되기 때문에, 이 토픽의 보존 기간은 더 길게 설정됩니다(90일). 이 토픽을 재생하여 timeseries aspect를 백업할 수 있습니다.

## 설정

MetadataChangeProposal 및 MetadataChangeLog와 함께, 메타데이터 entity와 aspect 간의 연관 관계를 설정하는 새 메커니즘을 도입합니다. 구체적으로 Snapshot.pdl 모델은 더 이상 [Rest.li](http://rest.li) union을 통해 이 정보를 인코딩하지 않습니다. 대신, 더 명시적인 yaml 파일이 이러한 링크를 제공할 것입니다. 이 파일은 런타임에 글로벌 메타데이터 스키마와 일부 추가 메타데이터를 포함하는 인메모리 Entity Registry를 구성하는 데 사용됩니다.

MCP & MCL에 사용될 설정 파일의 예시로, "dataset" entity를 "datasetKey"와 "datasetProfile"의 두 aspect에 연관시키는 것이 있습니다.

```
# entity-registry.yml

entities:
  - name: dataset
    keyAspect: datasetKey
    aspects:
      - datasetProfile
```

## 기능

### 조건부 쓰기

조건부 쓰기 시맨틱은 조건이 충족되지 않을 경우 새 aspect를 쓰지 않기 위해 MCP `headers` 필드에 포함된 추가 정보를 사용합니다.

#### If-Version-Match

aspect가 업데이트될 때마다 aspect에 대한 변경을 나타내는 `version`이 증가합니다. 이 `version`은 `SystemMetadata`에 저장되고 반환됩니다.

작성자는 요청을 시작할 때 예상 `version`이 포함된 헤더를 제공할 수 있습니다. 예상 `version`이 데이터베이스에 저장된 실제 `version`과 일치하지 않으면 쓰기가 실패합니다. 이는 다른 프로세스에 의해 수정된 aspect를 덮어쓰는 것을 방지합니다.

참고: aspect가 아직 존재하지 않으면 `version`은 `-1`입니다. 작성자는 이 `version`을 사용하여 aspect가 존재하지 않을 때만 생성할 수 있습니다. 아래 _변경 타입: [`CREATE`, `CREATE_ENTITY`]_ 섹션도 참조하세요.

#### If-Modified-Since / If-Unmodified-Since

작성자는 http 헤더 시맨틱을 사용하여 시간 기반 조건을 지정할 수도 있습니다. 버전 기반 조건부 쓰기와 유사하게 이 방법은 aspect를 읽은 후 대상 aspect가 수정된 경우 쓰기를 방지하는 데 사용할 수 있습니다. http 명세에 따라 날짜는 ISO-8601 표준을 준수해야 합니다.

`If-Unmodified-Since`:
작성자는 [If-Unmodified-Since](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Unmodified-Since) http 헤더를 따라 특정 시간 이후 aspect가 수정되지 않았어야 한다고 지정할 수 있습니다.

`If-Modified-Since`
작성자는 [If-Modified-Since](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Modified-Since) http 헤더를 따라 특정 시간 이후 aspect가 수정되었어야 한다고 지정할 수 있습니다.

#### 변경 타입: [`CREATE`, `CREATE_ENTITY`]

aspect 또는 entity의 존재를 고려하는 또 다른 형태의 조건부 쓰기는 다음 변경 타입을 사용합니다.

`CREATE` - aspect가 아직 존재하지 않으면 생성합니다.

`CREATE_ENTITY` - entity에 대한 aspect가 존재하지 않으면 aspect를 생성합니다.

기본적으로 `CREATE`/`CREATE_ENTITY` 제약이 위반되면 유효성 검사 예외가 발생합니다. 예외로 간주하지 않고 쓰기 작업이 취소되어야 하는 경우, MCP에 `If-None-Match: *` 헤더를 추가하세요.

### 동기식 ElasticSearch 업데이트

elasticsearch에 대한 쓰기는 기본적으로 비동기식입니다. 작성자는 특정 MCP에 대해 elasticsearch의 동기식 업데이트를 활성화하기 위해 MCP `headers`에 `true`로 설정된 값과 함께 커스텀 헤더 `X-DataHub-Sync-Index-Update`를 추가할 수 있습니다.

## Aspect 크기 유효성 검사

매우 큰 aspect 크기가 생성되거나 소비되는 것을 방지하기 위해 aspect 크기를 유효성 검사합니다.

**디버깅 플래그 - 기본적으로 비활성화됩니다.** 설정 세부 정보 및 사용 지침은 [환경 변수 - Aspect 크기 유효성 검사](../deploy/environment-vars.md#aspect-size-validation)를 참조하세요.

```yaml
datahub:
  validation:
    aspectSize:
      prePatch:
        enabled: false # patch 적용 전 DB에서 기존 aspect를 유효성 검사합니다
        warnSizeBytes: null # 선택 사항: 차단 없이 이 크기에서 경고 로그를 남깁니다(관찰 가능성 목적)
        maxSizeBytes: 16000000 # 16MB - INGESTION_MAX_SERIALIZED_STRING_LENGTH와 동일
        oversizedRemediation: IGNORE # IGNORE(쓰기 건너뛰기, 경고 로그) 또는 DELETE(쓰기 건너뛰기 및 aspect 삭제)
      postPatch:
        enabled: false # patch 후, DB 쓰기 전 aspect를 유효성 검사합니다
        warnSizeBytes: null # 선택 사항: 차단 없이 이 크기에서 경고 로그를 남깁니다(관찰 가능성 목적)
        maxSizeBytes: 16000000 # 16MB - INGESTION_MAX_SERIALIZED_STRING_LENGTH와 동일
        oversizedRemediation: IGNORE # IGNORE(쓰기 건너뛰기, 경고 로그) 또는 DELETE(쓰기 건너뛰기 및 aspect 삭제)
```

**크기 임계값:**

- `warnSizeBytes` (선택 사항): 초과하면 경고를 로그로 남기지만 쓰기는 계속 진행됩니다. 점진적 도입 중 관찰 가능성을 위해 유용합니다. `maxSizeBytes`보다 낮아야 합니다. `maxSizeBytes`보다 높게 설정하면 경고가 발생하기 전에 쓰기가 건너뜁니다.
- `maxSizeBytes`: 초과하면 쓰기를 건너뛰고 설정된 remediation 전략을 적용합니다.

**Remediation 전략:**

- `IGNORE`: 경고 로그, 쓰기 건너뛰기, MCP를 FailedMetadataChangeProposal 토픽으로 라우팅합니다.
- `DELETE`: 경고 로그, 쓰기 건너뛰기, MCP를 FailedMetadataChangeProposal 토픽으로 라우팅하고 aspect를 삭제합니다.

## MCL 생성을 위한 CDC(변경 데이터 캡처) 모드

### 개요

DataHub는 MetadataChangeLog를 생성하기 위한 선택적 CDC(변경 데이터 캡처) 모드를 지원합니다. CDC 모드에서 MCL은 MCP를 처리한 후 GMS에서 생성되는 것이 아니라, 메타데이터 저장 레이어에서 직접 캡처된 데이터베이스 변경 이벤트에서 생성됩니다. 이 메커니즘은 **MCL이 데이터베이스 쓰기와 동일한 순서로 생성되도록 보장하여** 메타데이터 변경에 대한 더 강력한 순서 보장을 제공합니다.

### CDC 대 전통적인 MCL 생성

**전통적인 모드 (기본값)**:

- GMS가 MCP를 처리하고 데이터베이스에 씁니다.
- GMS가 성공적인 데이터베이스 쓰기 후 즉시 Kafka에 MCL을 생성합니다.
- MCL 순서는 MCP 처리 순서와 일치합니다.

**CDC 모드**:

- GMS가 MCP를 처리하고 데이터베이스에 씁니다(MCL 생성 비활성화).
- CDC 시스템(Debezium)이 발생하는 데이터베이스 변경을 캡처합니다.
- MCE Consumer가 CDC 이벤트를 읽고 EntityService를 통해 MCL을 생성합니다.
- MCL 순서는 데이터베이스 트랜잭션 커밋 순서와 일치합니다.

### 아키텍처

CDC 모드에서 흐름은 다음과 같습니다:

```
MCP → GMS (DB에 쓰기, MCL 없음) → CDC 소스 → CDC 토픽 → MCE Consumer → EntityService를 통한 MCL 생성 → MCL 토픽
```

자세한 설정 지침은 다음을 참조하세요:

- [CDC 설정 가이드](../how/configure-cdc.md)
- [환경 변수 참조](../deploy/environment-vars.md#change-data-capture-cdc-configuration)
