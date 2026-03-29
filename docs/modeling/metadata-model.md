---
title: 메타데이터 모델
sidebar_label: 메타데이터 모델
slug: /metadata-modeling/metadata-model
---

# DataHub는 메타데이터를 어떻게 모델링하는가?

DataHub는 메타데이터를 모델링할 때 스키마 우선(schema-first) 방식을 채택합니다. 오픈소스 Pegasus 스키마 언어([PDL](https://linkedin.github.io/rest.li/pdl_schema))에 커스텀 어노테이션 세트를 확장하여 메타데이터를 모델링합니다. DataHub의 저장, 서빙, 인덱싱, 수집 레이어는 메타데이터 모델 위에서 직접 동작하며, 클라이언트에서 저장 레이어까지 강한 타입을 지원합니다.

개념적으로 메타데이터는 다음과 같은 추상화를 사용하여 모델링됩니다.

- **Entities**: entity는 메타데이터 그래프의 기본 노드입니다. 예를 들어, Dataset 또는 CorpUser의 인스턴스가 entity입니다. entity는 타입(예: 'dataset'), 고유 식별자(예: 'urn'), 그리고 aspect라고 부르는 메타데이터 속성 그룹으로 구성됩니다.

- **Aspects**: aspect는 entity의 특정 면모를 설명하는 속성들의 집합입니다. DataHub에서 쓰기의 최소 원자 단위입니다. 즉, 동일한 entity에 연관된 여러 aspect를 독립적으로 업데이트할 수 있습니다. 예를 들어 DatasetProperties는 Dataset을 설명하는 속성들의 집합을 포함합니다. aspect는 entity 간에 공유될 수 있는데, 예를 들어 "Ownership"은 소유자가 있는 모든 entity에서 재사용되는 aspect입니다. 일반적인 aspect는 다음과 같습니다.

  - [ownership](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/Ownership.pdl): entity를 소유하는 사용자와 그룹을 캡처합니다.
  - [globalTags](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/GlobalTags.pdl): entity에 연관된 태그에 대한 참조를 캡처합니다.
  - [glossaryTerms](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/GlossaryTerms.pdl): entity에 연관된 용어집 용어에 대한 참조를 캡처합니다.
  - [institutionalMemory](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/InstitutionalMemory.pdl): entity에 연관된 사내 문서(예: 링크!)를 캡처합니다.
  - [status](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/Status.pdl): entity의 "삭제" 상태, 즉 소프트 삭제 여부를 캡처합니다.
  - [subTypes](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/SubTypes.pdl): 더 일반적인 entity 타입의 하나 이상의 "서브 타입"을 캡처합니다. 예를 들어 "Looker Explore" Dataset, "View" Dataset 등이 있습니다. 특정 서브 타입은 주어진 entity에 추가적인 aspect가 존재함을 의미할 수 있습니다.

- **Relationships**: relationship은 두 entity 사이의 명명된 엣지를 나타냅니다. aspect 내의 외래 키 속성과 커스텀 어노테이션(@Relationship)을 통해 선언됩니다. relationship은 양방향으로 엣지를 탐색할 수 있게 합니다. 예를 들어, Chart는 "OwnedBy"라는 relationship을 통해 CorpUser를 소유자로 참조할 수 있습니다. 이 엣지는 Chart _또는_ CorpUser 인스턴스에서 시작하여 탐색할 수 있습니다.

- **식별자 (Keys & Urns)**: key는 개별 entity를 고유하게 식별하는 필드를 포함하는 특수한 종류의 aspect입니다. Key aspect는 _Urns_ 로 직렬화될 수 있으며, Urns는 기본 키 조회에 사용되는 문자열로 표현된 키 필드를 나타냅니다. 또한 _Urns_ 는 다시 key aspect 구조체로 변환될 수 있어, key aspect는 일종의 "가상" aspect입니다. Key aspect는 클라이언트가 Dataset 이름, 플랫폼 이름 등 일반적으로 유용한 기본 키를 쉽게 읽을 수 있는 메커니즘을 제공합니다. Urns는 완전히 구체화된 구조체 없이도 entity를 쿼리할 수 있는 친숙한 핸들을 제공합니다.

다음은 3가지 entity 타입(CorpUser, Chart, Dashboard), 2가지 relationship 타입(OwnedBy, Contains), 3가지 메타데이터 aspect 타입(Ownership, ChartInfo, DashboardInfo)으로 구성된 예시 그래프입니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/metadata-model-chart.png"/>
</p>

## 핵심 Entities

DataHub의 "핵심" entity 타입은 현대 데이터 스택을 구성하는 데이터 자산을 모델링합니다.

1. **[Data Platform](docs/generated/metamodel/entities/dataPlatform.md)**: 데이터 "플랫폼" 타입. 즉, 데이터 자산의 처리, 저장 또는 시각화에 관여하는 외부 시스템입니다. MySQL, Snowflake, Redshift, S3 등이 예시입니다.
2. **[Dataset](docs/generated/metamodel/entities/dataset.md)**: 데이터 컬렉션. 테이블, 뷰, 스트림, 문서 컬렉션, 파일 등은 DataHub에서 "Dataset"으로 모델링됩니다. Dataset에는 태그, 소유자, 링크, 용어집 용어, 설명을 첨부할 수 있습니다. "View", "Collection", "Stream", "Explore" 등 특정 서브 타입을 가질 수도 있습니다. Postgres 테이블, MongoDB 컬렉션, S3 파일 등이 예시입니다.
3. **[Chart](docs/generated/metamodel/entities/chart.md)**: Dataset에서 파생된 단일 데이터 시각화. 하나의 Chart는 여러 Dashboard의 일부가 될 수 있습니다. Chart에는 태그, 소유자, 링크, 용어집 용어, 설명을 첨부할 수 있습니다. Superset 또는 Looker Chart가 예시입니다.
4. **[Dashboard](docs/generated/metamodel/entities/dashboard.md)**: 시각화를 위한 Chart 컬렉션. Dashboard에는 태그, 소유자, 링크, 용어집 용어, 설명을 첨부할 수 있습니다. Superset 또는 Mode Dashboard가 예시입니다.
5. **[Data Job](docs/generated/metamodel/entities/dataJob.md)** (태스크): 데이터 자산을 처리하는 실행 가능한 작업. "처리"는 데이터 소비, 데이터 생성 또는 양쪽 모두를 의미합니다. Data Job에는 태그, 소유자, 링크, 용어집 용어, 설명을 첨부할 수 있습니다. 단일 Data Flow에 속해야 합니다. Airflow Task가 예시입니다.
6. **[Data Flow](docs/generated/metamodel/entities/dataFlow.md)** (파이프라인): 의존성이 있는 Data Job들의 실행 가능한 컬렉션 또는 DAG. Data Job에는 태그, 소유자, 링크, 용어집 용어, 설명을 첨부할 수 있습니다. Airflow DAG가 예시입니다.

왼쪽의 **메타데이터 모델링/Entities** 섹션을 참조하여 전체 모델을 탐색하세요.

## Entity Registry

DataHub에서 entity와 그 aspect들은 어디에 정의되어 있을까요? 메타데이터 모델은 어디에 "존재"할까요? 메타데이터 모델은 **Entity Registry**를 통해 구성됩니다. Entity Registry는 메타데이터 그래프를 구성하는 entity들의 카탈로그와 각 entity에 연관된 aspect들로 이루어져 있습니다. 간단히 말해, 이것이 모델의 "스키마"가 정의되는 곳입니다.

전통적으로 Entity Registry는 [Snapshot](https://github.com/datahub-project/datahub/tree/master/metadata-models/src/main/pegasus/com/linkedin/metadata/snapshot) 모델을 사용하여 구성되었습니다. 이 모델은 entity와 연관된 aspect를 명시적으로 연결하는 스키마입니다. [DatasetSnapshot](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/metadata/snapshot/DatasetSnapshot.pdl)이 핵심 `Dataset` entity를 정의하는 예시입니다.
Dataset entity의 aspect들은 특수한 "Aspect" 스키마 내의 union 필드를 통해 캡처됩니다. [DatasetAspect](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/metadata/aspect/DatasetAspect.pdl)가 그 예시입니다.
이 파일은 dataset 특정 aspect([DatasetProperties](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/dataset/DatasetProperties.pdl) 등)와 공통 aspect([Ownership](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/Ownership.pdl),
[InstitutionalMemory](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/InstitutionalMemory.pdl),
[Status](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/Status.pdl))를 Dataset entity에 연결합니다. 이 entity 정의 방식은 곧 새로운 방식으로 대체될 예정입니다.

2022년 1월부로 DataHub는 새로운 entity 추가 수단으로서 Snapshot 모델에 대한 지원을 중단했습니다. 대신, Entity Registry는 시작 시 DataHub의 메타데이터 서비스에 제공되는 [entity-registry.yml](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/resources/entity-registry.yml)이라는 YAML 설정 파일 안에 정의됩니다. 이 파일은 entity와 aspect를 그들의 [이름](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/Ownership.pdl#L7)으로 참조하여 선언합니다.
부팅 시 DataHub는 registry 파일의 구조를 유효성 검사하고 설정에서 제공된 각 aspect 이름에 대한 PDL 스키마를 찾을 수 있는지 확인합니다([@Aspect](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/common/Ownership.pdl#L6) 어노테이션을 통해).

이 형식으로 전환함으로써 메타데이터 모델을 발전시키기가 훨씬 쉬워졌습니다. entity와 aspect 추가가 새로운 Snapshot/Aspect 파일을 생성하는 대신 YAML 설정에 항목을 추가하는 것으로 간단해졌습니다.

## DataHub의 메타데이터 모델 탐색

현재 DataHub 메타데이터 모델을 탐색하려면 서로 다른 entity와 그들 간의 관계를 보여주는 엣지가 있는 다음 고수준 그림을 확인하세요.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/datahub-metadata-model.png"/>
</p>

특정 entity에 대한 aspect 모델을 탐색하고 `foreign-key` 개념을 사용하여 관계를 탐색하려면, 데모 환경에서 확인하거나 왼쪽 **메타데이터 모델링/Entities** 섹션의 자동 생성된 문서를 탐색하세요.

예를 들어, DataHub 메타데이터 모델에서 가장 많이 사용되는 entity들에 대한 유용한 링크입니다.

- [Dataset](docs/generated/metamodel/entities/dataset.md): [프로필](<https://demo.datahub.com/dataset/urn:li:dataset:(urn:li:dataPlatform:datahub,Dataset,PROD)/Schema?is_lineage_mode=false>) [문서](<https://demo.datahub.com/dataset/urn:li:dataset:(urn:li:dataPlatform:datahub,Dataset,PROD)/Documentation?is_lineage_mode=false>)
- [Dashboard](docs/generated/metamodel/entities/dashboard.md): [프로필](<https://demo.datahub.com/dataset/urn:li:dataset:(urn:li:dataPlatform:datahub,Dashboard,PROD)/Schema?is_lineage_mode=false>) [문서](<https://demo.datahub.com/dataset/urn:li:dataset:(urn:li:dataPlatform:datahub,Dashboard,PROD)/Documentation?is_lineage_mode=false>)
- [사용자 (a.k.a CorpUser)](docs/generated/metamodel/entities/corpuser.md): [프로필](<https://demo.datahub.com/dataset/urn:li:dataset:(urn:li:dataPlatform:datahub,Corpuser,PROD)/Schema?is_lineage_mode=false>) [문서](<https://demo.datahub.com/dataset/urn:li:dataset:(urn:li:dataPlatform:datahub,Corpuser,PROD)/Documentation?is_lineage_mode=false>)
- [파이프라인 (a.k.a DataFlow)](docs/generated/metamodel/entities/dataFlow.md): [프로필](<https://demo.datahub.com/dataset/urn:li:dataset:(urn:li:dataPlatform:datahub,DataFlow,PROD)/Schema?is_lineage_mode=false>) [문서](<https://demo.datahub.com/dataset/urn:li:dataset:(urn:li:dataPlatform:datahub,DataFlow,PROD)/Documentation?is_lineage_mode=false>)
- [피처 테이블 (a.k.a. MLFeatureTable)](docs/generated/metamodel/entities/mlFeatureTable.md): [프로필](<https://demo.datahub.com/dataset/urn:li:dataset:(urn:li:dataPlatform:datahub,MlFeatureTable,PROD)/Schema?is_lineage_mode=false>) [문서](<https://demo.datahub.com/dataset/urn:li:dataset:(urn:li:dataPlatform:datahub,MlFeatureTable,PROD)/Documentation?is_lineage_mode=false>)
- 메타데이터 모델의 전체 entity 목록은 [여기](https://demo.datahub.com/browse/dataset/prod/datahub/entities)에서 탐색하거나 왼쪽 **메타데이터 모델링/Entities** 섹션을 사용하세요.

### 메타데이터 모델 문서 생성

- 이 웹사이트: 이 웹사이트의 메타데이터 모델 문서는 `./gradlew :docs-website:yarnBuild`를 사용하여 생성되며, `metadata-ingestion` 모듈의 `modelDocGen` 태스크에 모델 문서 생성을 위임합니다.
- 실행 중인 DataHub 인스턴스에 문서 업로드: 메타데이터 모델 문서는 `./gradlew :metadata-ingestion:modelDocUpload` 명령을 사용하여 생성하고 실행 중인 DataHub 인스턴스에 업로드할 수 있습니다. **_참고_**: 환경 변수 `$DATAHUB_SERVER`에 설정된 DataHub 인스턴스(기본값: http://localhost:8080)에 모델 문서가 업로드됩니다.

## 메타데이터 그래프 쿼리

DataHub의 모델링 언어를 사용하면 쿼리 패턴에 맞게 메타데이터 지속성을 최적화할 수 있습니다.

메타데이터 그래프를 쿼리하는 방법은 세 가지입니다: 기본 키 조회, 검색 쿼리, 관계 탐색.

> [PDL](https://linkedin.github.io/rest.li/pdl_schema) 파일이 처음이신가요? 걱정하지 마세요. PDL 파일은 DataHub의 aspect에 대한 JSON 문서 "스키마"를 정의하는 방법에 불과합니다. DataHub의 메타데이터 서비스에 수집되는 모든 데이터는 PDL 스키마에 대해 검증되며, 각 @Aspect는 단일 스키마에 해당합니다. 구조적으로 PDL은 [Protobuf](https://developers.google.com/protocol-buffers)와 매우 유사하며 JSON으로 편리하게 매핑됩니다.

### Entity 쿼리

#### 최신 Entity Aspects 가져오기 (Snapshot)

기본 키로 entity를 쿼리하는 것은 검색할 entity의 urn을 전달하여 "entities" 엔드포인트를 사용함을 의미합니다.

예를 들어, Chart entity를 가져오려면 다음 `curl`을 사용할 수 있습니다:

```
curl --location --request GET 'http://localhost:8080/entities/urn%3Ali%3Achart%3Acustomers
```

이 요청은 각 aspect의 최신 버전을 포함하는 버전이 지정된 aspect 집합을 반환합니다.

보시다시피, entity에 연관된 url 인코딩된 _Urn_ 을 사용하여 조회를 수행합니다.
응답은 entity 스냅샷(entity에 연관된 최신 aspect들을 포함)을 포함하는 "Entity" 레코드가 됩니다.

#### 버전이 지정된 Aspects 가져오기

DataHub는 aspect라고 부르는 entity에 대한 개별 메타데이터 조각 가져오기도 지원합니다. 이를 위해 entity의 기본 키(urn)와 함께 검색할 aspect 이름과 버전을 제공합니다.

예를 들어, Dataset의 SchemaMetadata aspect의 최신 버전을 가져오려면 다음 쿼리를 실행합니다:

```
curl 'http://localhost:8080/aspects/urn%3Ali%3Adataset%3A(urn%3Ali%3AdataPlatform%3Afoo%2Cbar%2CPROD)?aspect=schemaMetadata&version=0'

{
   "version":0,
   "aspect":{
      "com.linkedin.schema.SchemaMetadata":{
         "created":{
            "actor":"urn:li:corpuser:fbar",
            "time":0
         },
         "platformSchema":{
            "com.linkedin.schema.KafkaSchema":{
               "documentSchema":"{\"type\":\"record\",\"name\":\"MetadataChangeEvent\",\"namespace\":\"com.linkedin.mxe\",\"doc\":\"Kafka event for proposing a metadata change for an entity.\",\"fields\":[{\"name\":\"auditHeader\",\"type\":{\"type\":\"record\",\"name\":\"KafkaAuditHeader\",\"namespace\":\"com.linkedin.avro2pegasus.events\",\"doc\":\"Header\"}}]}"
            }
         },
         "lastModified":{
            "actor":"urn:li:corpuser:fbar",
            "time":0
         },
         "schemaName":"FooEvent",
         "fields":[
            {
               "fieldPath":"foo",
               "description":"Bar",
               "type":{
                  "type":{
                     "com.linkedin.schema.StringType":{

                     }
                  }
               },
               "nativeDataType":"string"
            }
         ],
         "version":0,
         "hash":"",
         "platform":"urn:li:dataPlatform:foo"
      }
   }
}
```

#### Timeseries Aspects 가져오기

DataHub는 entity에 대한 Timeseries aspect 그룹을 가져오는 API를 지원합니다. 예를 들어, 이 API를 사용하여 Dataset에 대한 최근 프로파일링 실행 및 통계를 가져올 수 있습니다. 이를 위해 `/aspects` 엔드포인트에 "get" 요청을 보낼 수 있습니다.

예를 들어, Dataset의 dataset profile(통계)을 가져오려면 다음 쿼리를 실행합니다:

```
curl -X POST 'http://localhost:8080/aspects?action=getTimeseriesAspectValues' \
--data '{
    "urn": "urn:li:dataset:(urn:li:dataPlatform:redshift,global_dev.larxynx_carcinoma_data_2020,PROD)",
    "entity": "dataset",
    "aspect": "datasetProfile",
    "startTimeMillis": 1625122800000,
    "endTimeMillis": 1627455600000
}'

{
   "value":{
      "limit":2000,
      "aspectName":"datasetProfile",
      "endTimeMillis":1627455600000,
      "startTimeMillis":1625122800000,
      "entityName":"dataset",
      "values":[
         {
            "aspect":{
               "value":"{\"timestampMillis\":1626912000000,\"fieldProfiles\":[{\"uniqueProportion\":1.0,\"sampleValues\":[\"123MMKK12\",\"13KDFMKML\",\"123NNJJJL\"],\"fieldPath\":\"id\",\"nullCount\":0,\"nullProportion\":0.0,\"uniqueCount\":3742},{\"uniqueProportion\":1.0,\"min\":\"1524406400000\",\"max\":\"1624406400000\",\"sampleValues\":[\"1640023230002\",\"1640343012207\",\"16303412330117\"],\"mean\":\"1555406400000\",\"fieldPath\":\"date\",\"nullCount\":0,\"nullProportion\":0.0,\"uniqueCount\":3742},{\"uniqueProportion\":0.037,\"min\":\"21\",\"median\":\"68\",\"max\":\"92\",\"sampleValues\":[\"45\",\"65\",\"81\"],\"mean\":\"65\",\"distinctValueFrequencies\":[{\"value\":\"12\",\"frequency\":103},{\"value\":\"54\",\"frequency\":12}],\"fieldPath\":\"patient_age\",\"nullCount\":0,\"nullProportion\":0.0,\"uniqueCount\":79},{\"uniqueProportion\":0.00820873786407767,\"sampleValues\":[\"male\",\"female\"],\"fieldPath\":\"patient_gender\",\"nullCount\":120,\"nullProportion\":0.03,\"uniqueCount\":2}],\"rowCount\":3742,\"columnCount\":4}",
               "contentType":"application/json"
            }
         },
      ]
   }
}
```

aspect 자체가 이스케이프된 JSON으로 직렬화되어 있음을 알 수 있습니다. 이는 다양한 방식으로 aspect를 직렬화할 수 있는 더 일반적인 READ/WRITE API 세트로 전환하는 과정의 일부입니다. 기본적으로 콘텐츠 타입은 JSON이며, aspect는 원하는 언어로 일반 JSON 객체로 역직렬화할 수 있습니다. 이것이 개별 aspect를 읽고 쓰는 사실상의 방식이 될 예정입니다.

### 검색 쿼리

검색 쿼리를 사용하면 임의의 문자열과 일치하는 entity를 검색할 수 있습니다.

예를 들어, "customers"라는 용어와 일치하는 entity를 검색하려면 다음 CURL을 사용할 수 있습니다:

```
curl --location --request POST 'http://localhost:8080/entities?action=search' \
--header 'X-RestLi-Protocol-Version: 2.0.0' \
--header 'Content-Type: application/json' \
--data-raw '{
    "input": "\"customers\"",
    "entity": "chart",
    "start": 0,
    "count": 10
}'
```

주목할 매개변수는 `input`과 `entity`입니다. `input`은 실행 중인 쿼리를 지정하고 `entity`는 검색할 entity 타입을 지정합니다. 이것은 @Entity 정의에서 정의된 entity의 일반 이름입니다. 응답에는 전체 entity를 가져오는 데 사용할 수 있는 Urns 목록이 포함됩니다.

### 관계 쿼리

관계 쿼리를 사용하면 특정 타입의 엣지를 통해 특정 소스 entity에 연결된 entity를 찾을 수 있습니다.

예를 들어, 특정 Chart의 소유자를 찾으려면 다음 CURL을 사용할 수 있습니다:

```
curl --location --request GET --header 'X-RestLi-Protocol-Version: 2.0.0' 'http://localhost:8080/relationships?direction=OUTGOING&urn=urn%3Ali%3Achart%3Acustomers&types=List(OwnedBy)'
```

주목할 매개변수는 `direction`, `urn`, `types`입니다. 응답에는 "OwnedBy"라는 관계로 기본 entity(urn:li:chart:customer)에 연결된 모든 entity와 관련된 _Urns_ 가 포함됩니다. 즉, 주어진 chart의 소유자를 가져올 수 있습니다.

### 특수 Aspects

언급할 가치가 있는 몇 가지 특수 aspect가 있습니다:

1. Key aspects: entity를 고유하게 식별하는 속성을 포함합니다.
2. Browse Paths aspect: entity에 연관된 계층적 경로를 나타냅니다.

#### Key aspects

위에서 소개한 바와 같이, Key aspects는 entity를 고유하게 식별하는 필드를 포함하는 구조체/레코드입니다. Key aspects에 있을 수 있는 필드에는 몇 가지 제약이 있습니다:

- 모든 필드는 STRING 또는 ENUM 타입이어야 합니다.
- 모든 필드는 REQUIRED여야 합니다.

Key는 _Urns_ 로 생성되고 _Urns_ 로 변환될 수 있습니다. Urns는 Key 레코드의 문자열화된 버전을 나타냅니다.
변환에 사용되는 알고리즘은 간단합니다: Key aspect의 필드는 정의 순서에 따라 인덱스를 기반으로 다음 템플릿을 사용하여 문자열 템플릿에 대입됩니다:

```aidl
// 경우 1: 키 필드 수 == 1
urn:li:<entity-name>:key-field-1

// 경우 2: 키 필드 수 > 1
urn:li:<entity-name>:(key-field-1, key-field-2, ... key-field-n)
```

관례상 key aspects는 [metadata-models/src/main/pegasus/com/linkedin/metadata/key](https://github.com/datahub-project/datahub/tree/master/metadata-models/src/main/pegasus/com/linkedin/metadata/key) 아래에 정의됩니다.

##### 예시

CorpUser는 일반적으로 LDAP 이름에 해당하는 "username"으로 고유하게 식별될 수 있습니다.

따라서 Key Aspect는 다음과 같이 정의됩니다:

```aidl
namespace com.linkedin.metadata.key

/**
 * Key for a CorpUser
 */
@Aspect = {
  "name": "corpUserKey"
}
record CorpUserKey {
  /**
  * The name of the AD/LDAP user.
  */
  username: string
}
```

그리고 Entity Snapshot 모델은 다음과 같이 정의됩니다.

```aidl
/**
 * A metadata snapshot for a specific CorpUser entity.
 */
@Entity = {
  "name": "corpuser",
  "keyAspect": "corpUserKey"
}
record CorpUserSnapshot {

  /**
   * URN for the entity the metadata snapshot is associated with.
   */
  urn: CorpuserUrn

  /**
   * The list of metadata aspects associated with the CorpUser. Depending on the use case, this can either be all, or a selection, of supported aspects.
   */
  aspects: array[CorpUserAspect]
}
```

이 모델들이 제공하는 정보의 조합을 사용하여, CorpUser에 해당하는 Urn을 다음과 같이 생성할 수 있습니다:

```
urn:li:corpuser:<username>
```

사용자명이 "johnsmith"인 CorpUser entity가 있다고 상상해 보세요. 이 경우 해당 entity와 연관된 Key Aspect의 JSON 버전은 다음과 같습니다:

```aidl
{
  "username": "johnsmith"
}
```

그리고 해당하는 Urn은 다음과 같습니다:

```aidl
urn:li:corpuser:johnsmith
```

#### BrowsePaths aspect

BrowsePaths aspect를 사용하면 entity에 대한 커스텀 "browse path"를 정의할 수 있습니다. browse path는 entity를 계층적으로 구성하는 방법입니다. 이것은 UI의 "탐색" 기능 내에서 나타나며, 사용자가 주어진 타입의 관련 entity 트리를 탐색할 수 있게 합니다.

특정 entity에 대한 탐색을 지원하려면, `entity-registry.yml` 파일에서 entity에 "browsePaths" aspect를 추가하세요.

```aidl
/// entity-registry.yml
entities:
  - name: dataset
    doc: Datasets represent logical or physical data assets stored or represented in various data platforms. Tables, Views, Streams are all instances of datasets.
    keyAspect: datasetKey
    aspects:
      ...
      - browsePaths
```

이 aspect를 선언함으로써, 커스텀 browse path를 생성하고 다음과 같은 CURL을 사용하여 수동으로 browse path를 쿼리할 수 있습니다:

```aidl
curl --location --request POST 'http://localhost:8080/entities?action=browse' \
--header 'X-RestLi-Protocol-Version: 2.0.0' \
--header 'Content-Type: application/json' \
--data-raw '{
    "path": "/my/custom/browse/path",
    "entity": "dataset",
    "start": 0,
    "limit": 10
}'
```

다음을 제공해야 합니다:

- 결과를 가져올 "/"로 구분된 루트 경로.
- 일반 이름을 사용하는 entity "타입" (위 예시에서는 "dataset").

### Aspect의 종류

메타데이터 Aspect에는 2가지 "종류"가 있습니다. 둘 다 PDL 스키마를 사용하여 모델링되며, 동일한 방식으로 수집될 수 있습니다. 그러나 그들이 나타내는 것과 DataHub의 메타데이터 서비스에서 처리되는 방식에서 차이가 있습니다.

#### 1. Versioned Aspects

Versioned Aspects는 각각 관련된 **숫자 버전**을 가집니다. aspect의 필드가 변경될 때마다, 새 버전이 자동으로 생성되어 DataHub의 백엔드에 저장됩니다. 실제로 모든 versioned aspect는 백업 및 복원이 가능한 관계형 데이터베이스에 저장됩니다. Versioned aspect는 소유권, 설명, 태그, 용어집 용어 등을 포함한 많은 UI 경험을 구동합니다. 예로는 Ownership, Global Tags, Glossary Terms가 있습니다.

#### 2. Timeseries Aspects

Timeseries Aspects는 각각 관련된 **타임스탬프**를 가집니다. entity에 대한 시간 순서의 이벤트를 나타내는 데 유용합니다. 예를 들어, Dataset 프로파일링 결과 또는 매일 실행되는 데이터 품질 검사 세트 등이 있습니다. Timeseries aspect는 관계형 저장소에 저장되지 않고, 대신 검색 인덱스(예: elasticsearch)와 메시지 큐(Kafka)에만 저장된다는 점이 중요합니다. 이로 인해 재해 시나리오에서 timeseries aspect를 복원하는 것이 다소 어렵습니다. Timeseries aspect는 시간 범위로 쿼리할 수 있으며, 이것이 Versioned Aspects와 가장 다른 점입니다.
Timeseries aspect는 [@Aspect](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/dataset/DatasetProfile.pdl#L8) 어노테이션의 "timeseries" [타입](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/dataset/DatasetProfile.pdl#L10)으로 식별할 수 있습니다.
예로는 [DatasetProfile](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/dataset/DatasetProfile.pdl)과 [DatasetUsageStatistics](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/dataset/DatasetUsageStatistics.pdl)가 있습니다.

Timeseries aspect는 timestampMillis 필드를 가지는 aspect로, 데이터 프로파일, 사용 통계 등 시간 기반으로 지속적으로 변경되는 aspect를 위해 설계되었습니다.

각 timeseries aspect는 "type": "timeseries"로 선언되어야 하며 timestampMillis 필드를 포함하는 [TimeseriesAspectBase](https://github.com/datahub-project/datahub/tree/master/metadata-models/src/main/pegasus/com/linkedin/timeseries/TimeseriesAspectBase.pdl)를 포함해야 합니다.

Timeseries aspect도 @Searchable 및 @Relationship으로 어노테이션된 필드를 가질 수 있습니다.

Timeseries aspect의 예시는 [DatasetProfile](https://github.com/datahub-project/datahub/tree/master/metadata-models/src/main/pegasus/com/linkedin/dataset/DatasetProfile.pdl)을 참조하세요.

Timeseries aspect는 자주 업데이트되기 때문에, 이러한 aspect의 수집은 로컬 DB에 저장되는 대신 elasticsearch로 바로 전달됩니다.

Timeseries aspect는 "aspects?action=getTimeseriesAspectValues" 엔드포인트를 사용하여 검색할 수 있습니다.

##### 집계 가능한 Timeseries aspects

Timeseries aspect에 대해 SQL과 유사한 _group by + aggregate_ 작업을 수행하는 것은 이런 종류의 데이터(dataset 프로파일, 사용 통계 등)에 매우 자연스러운 사용 사례입니다. 이 섹션에서는 timeseries aspect를 정의하고, 수집하고, 집계 쿼리를 수행하는 방법을 설명합니다.

###### 새로운 집계 가능한 Timeseries aspect 정의하기

_@TimeseriesField_ 와 _@TimeseriesFieldCollection_ 은 집계 쿼리의 일부가 될 수 있도록 _Timeseries aspect_ 의 필드에 첨부할 수 있는 두 가지 새 어노테이션입니다. 이렇게 어노테이션된 필드에 허용되는 집계 유형은 필드 타입과 집계 종류에 따라 다릅니다([집계 수행하기](#performing-an-aggregation-on-a-timeseries-aspect) 참조).

- `@TimeseriesField = {}` - 이 어노테이션은 기본 타입 및 레코드와 같은 비컬렉션 타입 필드에 사용할 수 있습니다([TestEntityProfile.pdl](https://github.com/datahub-project/datahub/blob/master/test-models/src/main/pegasus/com/datahub/test/TestEntityProfile.pdl)의 _stat_, _strStat_, _strArray_ 필드 참조).

- `@TimeseriesFieldCollection {"key":"<컬렉션 항목 타입의 키 필드 이름>"}` 어노테이션은 컬렉션 타입(현재는 배열 타입 컬렉션만 지원)의 항목에 대한 집계 지원을 가능하게 합니다. 여기서 `"key"` 값은 group-by 절을 지정하는 데 사용될 컬렉션 항목 타입의 필드 이름입니다([DatasetUsageStatistics.pdl](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/dataset/DatasetUsageStatistics.pdl)의 _userCounts_ 및 _fieldCounts_ 필드 참조).

적절한 Timeseries 어노테이션으로 새 aspect를 정의하는 것 외에도, [entity-registry.yml](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/resources/entity-registry.yml) 파일도 업데이트해야 합니다. 아래와 같이 적절한 entity에 대한 aspect 목록 아래에 새 aspect 이름을 추가하세요. 예를 들어, DatasetUsageStatistics aspect의 경우 `datasetUsageStatistics`를 추가합니다.

```yaml
entities:
  - name: dataset
    keyAspect: datasetKey
    aspects:
      - datasetProfile
      - datasetUsageStatistics
```

###### Timeseries aspect 수집하기

Timeseries aspect는 GMS REST 엔드포인트 `/aspects?action=ingestProposal` 또는 Python API를 통해 수집할 수 있습니다.

예시1: curl을 사용한 GMS REST API.

```shell
curl --location --request POST 'http://localhost:8080/aspects?action=ingestProposal' \
--header 'X-RestLi-Protocol-Version: 2.0.0' \
--header 'Content-Type: application/json' \
--data-raw '{
  "proposal" : {
    "entityType": "dataset",
    "entityUrn" : "urn:li:dataset:(urn:li:dataPlatform:hive,SampleHiveDataset,PROD)",
    "changeType" : "UPSERT",
    "aspectName" : "datasetUsageStatistics",
    "aspect" : {
      "value" : "{ \"timestampMillis\":1629840771000,\"uniqueUserCount\" : 10, \"totalSqlQueries\": 20, \"fieldCounts\": [ {\"fieldPath\": \"col1\", \"count\": 20}, {\"fieldPath\" : \"col2\", \"count\": 5} ]}",
      "contentType": "application/json"
    }
  }
}'
```

예시2: Kafka(또는 REST)에 대한 Python API

```python
from datahub.metadata.schema_classes import (
    ChangeTypeClass,
    DatasetFieldUsageCountsClass,
    DatasetUsageStatisticsClass,
)
from datahub.emitter.kafka_emitter import DatahubKafkaEmitter
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter

usageStats = DatasetUsageStatisticsClass(
            timestampMillis=1629840771000,
            uniqueUserCount=10,
            totalSqlQueries=20,
            fieldCounts=[
                DatasetFieldUsageCountsClass(
                    fieldPath="col1",
                    count=10
                )
            ]
        )

mcpw = MetadataChangeProposalWrapper(
    entityType="dataset",
    aspectName="datasetUsageStatistics",
    changeType=ChangeTypeClass.UPSERT,
    entityUrn="urn:li:dataset:(urn:li:dataPlatform:hive,SampleHiveDataset,PROD)",
    aspect=usageStats,
)

# 적절한 이미터 인스턴스화(kafka_emitter/rest_emitter)
# my_emitter = DatahubKafkaEmitter("""<config>""")
my_emitter = DatahubRestEmitter("http://localhost:8080")
my_emitter.emit(mcpw)
```

###### Timeseries aspect에서 집계 수행하기

Timeseries aspect에 대한 집계는 `/analytics?action=getTimeseriesStats`의 GMS REST API를 통해 수행할 수 있으며, 다음 매개변수를 허용합니다:

- `entityName` - aspect가 연관된 entity의 이름.
- `aspectName` - aspect의 이름.
- `filter` - 그룹화 및 집계 수행 전의 사전 필터링 기준.
- `metrics` - 집계 사양 목록. 집계 사양의 `fieldPath` 멤버는 집계를 수행할 필드 이름을 참조하고, `aggregationType`은 집계 종류를 지정합니다.
- `buckets` - 그룹화 버킷 사양 목록. 각 그룹화 버킷에는 그룹화에 사용할 필드를 참조하는 `key` 필드가 있습니다. `type` 필드는 그룹화 버킷의 종류를 지정합니다.

Timeseries 어노테이션된 필드에 대한 집계 쿼리에서 지정할 수 있는 세 가지 집계 유형을 지원합니다. `aggregationType`이 취할 수 있는 값은 다음과 같습니다:

- `LATEST`: 각 버킷의 필드 최신 값. 모든 타입의 필드에 지원됩니다.
- `SUM`: 각 버킷의 필드 누적 합계. 정수 타입에만 지원됩니다.
- `CARDINALITY`: 각 버킷에서 고유 값의 수 또는 집합의 카디널리티. 문자열 및 레코드 타입에 지원됩니다.

집계를 수행할 버킷을 정의하기 위한 두 가지 그룹화 유형을 지원합니다:

- `DATE_GROUPING_BUCKET`: 초, 분, 시, 일, 주, 월, 분기, 년 등 시간 기반 버킷 생성을 허용합니다. 값이 _epoch_ 이후의 밀리초로 표현된 타임스탬프 필드와 함께 사용해야 합니다. `timeWindowSize` 매개변수는 날짜 히스토그램 버킷 너비를 지정합니다.
- `STRING_GROUPING_BUCKET`: 필드의 고유 값으로 그룹화된 버킷 생성을 허용합니다. 항상 문자열 타입 필드와 함께 사용해야 합니다.

API는 입력 매개변수를 에코하는 것 외에도 `group-by/aggregate` 쿼리의 결과를 포함하는 출력의 `table` 멤버로 일반 SQL과 유사한 테이블을 반환합니다.

- `columnNames`: 테이블 열의 이름. group-by `key` 이름은 요청에서 지정된 순서와 같은 순서로 나타납니다. 집계 사양은 요청에서 지정된 순서와 같은 순서로 그룹화 필드 뒤에 오며, `<agg_name>_<fieldPath>`로 이름이 붙습니다.
- `columnTypes`: 열의 데이터 타입.
- `rows`: 데이터 값, 각 행은 해당 버킷에 대응합니다.

예시: 각 날짜의 최신 고유 사용자 수.

```shell
# 쿼리
curl --location --request POST 'http://localhost:8080/analytics?action=getTimeseriesStats' \
--header 'X-RestLi-Protocol-Version: 2.0.0' \
--header 'Content-Type: application/json' \
--data-raw '{
    "entityName": "dataset",
    "aspectName": "datasetUsageStatistics",
    "filter": {
        "criteria": []
    },
    "metrics": [
        {
            "fieldPath": "uniqueUserCount",
            "aggregationType": "LATEST"
        }
    ],
    "buckets": [
        {
            "key": "timestampMillis",
            "type": "DATE_GROUPING_BUCKET",
            "timeWindowSize": {
                "multiple": 1,
                "unit": "DAY"
            }
        }
    ]
}'

# 샘플 응답
{
    "value": {
        "filter": {
            "criteria": []
        },
        "aspectName": "datasetUsageStatistics",
        "entityName": "dataset",
        "groupingBuckets": [
            {
                "type": "DATE_GROUPING_BUCKET",
                "timeWindowSize": {
                    "multiple": 1,
                    "unit": "DAY"
                },
                "key": "timestampMillis"
            }
        ],
        "aggregationSpecs": [
            {
                "fieldPath": "uniqueUserCount",
                "aggregationType": "LATEST"
            }
        ],
        "table": {
            "columnNames": [
                "timestampMillis",
                "latest_uniqueUserCount"
            ],
            "rows": [
                [
                    "1631491200000",
                    "1"
                ]
            ],
            "columnTypes": [
                "long",
                "int"
            ]
        }
    }
}
```

복잡한 타입의 group-by/aggregation에 대한 더 많은 예시는 [TimeseriesAspectServiceTestBase.java](https://github.com/datahub-project/datahub/blob/master/metadata-io/src/test/java/com/linkedin/metadata/timeseries/search/TimeseriesAspectServiceTestBase.java)의 `getAggregatedStats` 그룹에서 테스트를 참조하세요.
