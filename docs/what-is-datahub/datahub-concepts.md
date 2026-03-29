# DataHub 개념

DataHub의 주요 개념을 탐색하여 데이터 관리에 있어 DataHub의 역량을 최대한 활용하세요.

## 일반 개념

### URN (Uniform Resource Name)

URN(Uniform Resource Name)은 DataHub에서 모든 리소스를 고유하게 정의하기 위해 선택된 URI 체계입니다. 다음과 같은 형식을 가집니다.

```
urn:<Namespace>:<Entity Type>:<ID>
```

예시로는 `urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)`, `urn:li:corpuser:jdoe` 등이 있습니다.

> - [URN이란 무엇인가?](/docs/what/urn.md)

### Policy

DataHub의 액세스 정책은 누가 어떤 리소스에 무엇을 할 수 있는지를 정의합니다.

> - [인가: Policies 가이드](/docs/authorization/policies.md)
> - [개발자 가이드: DataHubPolicy](/docs/generated/metamodel/entities/dataHubPolicy.md)
> - [기능 가이드: DataHub 액세스 정책 소개](/docs/authorization/access-policies-guide.md)

### Role

DataHub는 권한 관리를 위해 Role을 사용하는 기능을 제공합니다.

> - [인가: DataHub Role 소개](/docs/authorization/roles.md)
> - [개발자 가이드: DataHubRole](/docs/generated/metamodel/entities/dataHubRole.md)

### Access Token (Personal Access Token)

Personal Access Token(PAT)은 보안이 중요한 배포 환경에서 사용자가 코드로 자신을 표현하고 DataHub API를 프로그래밍 방식으로 사용할 수 있게 해줍니다.
[인증이 활성화된 메타데이터 서비스](/docs/authentication/introducing-metadata-service-authentication.md)와 함께 사용하면, PAT는 인가된 사용자만 자동화된 방식으로 작업을 수행할 수 있도록 DataHub에 보호 계층을 추가합니다.

> - [인증: DataHub Personal Access Token 소개](/docs/authentication/personal-access-tokens.md)
> - [개발자 가이드: DataHubAccessToken](/docs/generated/metamodel/entities/dataHubAccessToken.md)

### View

View를 사용하면 DataHub를 탐색할 때 재사용할 필터 세트를 저장하고 공유할 수 있습니다. View는 공개 또는 개인으로 설정할 수 있습니다.

> - [DataHubView](/docs/generated/metamodel/entities/dataHubView.md)

### Deprecation

Deprecation은 entity의 사용 중단 상태를 나타내는 aspect입니다. 일반적으로 Boolean 값으로 표현됩니다.

> - [dataset의 Deprecation](/docs/generated/metamodel/entities/dataset.md#deprecation)

### Ingestion Source

Ingestion source는 메타데이터를 추출하는 데이터 시스템을 지칭합니다. 예를 들어, BigQuery, Looker, Tableau 등 다양한 소스에 대한 연결을 지원합니다.

> - [Sources](/metadata-ingestion/README.md#sources)
> - [DataHub 통합](https://docs.datahub.com/integrations)

### Container

관련 데이터 자산의 컨테이너입니다.

> - [개발자 가이드: Container](/docs/generated/metamodel/entities/container.md)

### Data Platform

Data Platform은 메타데이터 그래프에 모델링된 dataset, Dashboard, Chart 및 기타 모든 종류의 데이터 자산을 포함하는 시스템 또는 도구입니다.

<details><summary>
Data Platform 목록
</summary>

- Azure Data Lake (Gen 1)
- Azure Data Lake (Gen 2)
- Airflow
- Ambry
- ClickHouse
- Couchbase
- External Source
- HDFS
- SAP HANA
- Hive
- Iceberg
- AWS S3
- Kafka
- Kafka Connect
- Kusto
- Mode
- MongoDB
- MySQL
- MariaDB
- OpenAPI
- Oracle
- Pinot
- PostgreSQL
- Presto
- Tableau
- Vertica

참고: [data_platforms.yaml](https://github.com/datahub-project/datahub/blob/master/metadata-service/configuration/src/main/resources/bootstrap_mcps/data-platforms.yaml)

</details>

> - [개발자 가이드: Data Platform](/docs/generated/metamodel/entities/dataPlatform.md)

### Dataset

Dataset은 데이터베이스(예: BigQuery, Snowflake, Redshift 등)의 테이블 또는 뷰, 스트림 처리 환경(Kafka, Pulsar 등)의 스트림, 데이터 레이크 시스템(S3, ADLS 등)의 파일이나 폴더 묶음으로 일반적으로 표현되는 데이터 컬렉션을 나타냅니다.

> - [개발자 가이드: Dataset](/docs/generated/metamodel/entities/dataset.md)

### Chart

Dataset에서 파생된 단일 데이터 시각화입니다. 하나의 Chart는 여러 Dashboard의 일부가 될 수 있습니다. Chart에는 태그, 소유자, 링크, 용어집 용어, 설명을 추가할 수 있습니다. Superset 또는 Looker Chart가 예시입니다.

> - [개발자 가이드: Chart](/docs/generated/metamodel/entities/chart.md)

### Dashboard

시각화를 위한 Chart 컬렉션입니다. Dashboard에는 태그, 소유자, 링크, 용어집 용어, 설명을 추가할 수 있습니다. Superset 또는 Mode Dashboard가 예시입니다.

> - [개발자 가이드: Dashboard](/docs/generated/metamodel/entities/dashboard.md)

### Data Job

데이터 자산을 처리하는 실행 가능한 작업으로, "처리"는 데이터 소비, 데이터 생성 또는 둘 다를 의미합니다.
오케스트레이션 시스템에서는 "DAG" 내의 개별 "Task"로 불리기도 합니다. Airflow Task가 예시입니다.

> - [개발자 가이드: Data Job](/docs/generated/metamodel/entities/dataJob.md)

### Data Flow

서로 간에 의존성을 가진 Data Job의 실행 가능한 컬렉션, 즉 DAG입니다.
"Pipeline"이라고도 합니다. Airflow DAG가 예시입니다.

> - [개발자 가이드: Data Flow](/docs/generated/metamodel/entities/dataFlow.md)

### Glossary Term

데이터 생태계 내에서 공유되는 어휘입니다.

> - [기능 가이드: Glossary](/docs/glossary/business-glossary.md)
> - [개발자 가이드: GlossaryTerm](/docs/generated/metamodel/entities/glossaryTerm.md)

### Glossary Term Group

Glossary Term Group은 폴더와 유사하며, Term과 다른 Term Group을 포함하여 중첩 구조를 허용합니다.

> - [기능 가이드: Term & Term Group](/docs/glossary/business-glossary.md#terms--term-groups)

### Tag

태그는 비공식적이고 느슨하게 통제되는 라벨로, 검색 및 탐색을 돕습니다. dataset, dataset schema, 또는 container에 추가하여 entity를 쉽게 분류하거나 범주화할 수 있으며, 더 넓은 비즈니스 용어집이나 어휘와 연결할 필요가 없습니다.

> - [기능 가이드: DataHub Tag 소개](/docs/tags.md)
> - [개발자 가이드: Tags](/docs/generated/metamodel/entities/tag.md)

### Domain

Domain은 관련 자산을 명시적으로 그룹화할 수 있는 큐레이션된 최상위 폴더 또는 카테고리입니다.

> - [기능 가이드: DataHub Domain 소개](/docs/domains.md)
> - [개발자 가이드: Domain](/docs/generated/metamodel/entities/domain.md)

### Owner

Owner는 entity에 대한 소유권을 가진 사용자 또는 그룹을 지칭합니다. 예를 들어, dataset, 컬럼, 또는 dataset에 소유자를 설정할 수 있습니다.

> - [시작하기: Dataset/컬럼에 소유자 추가](/docs/api/tutorials/owners.md#add-owners)

### Users (CorpUser)

CorpUser는 기업 내 개인(또는 계정)의 아이덴티티를 나타냅니다.

> - [개발자 가이드: CorpUser](/docs/generated/metamodel/entities/corpuser.md)

### Groups (CorpGroup)

CorpGroup은 기업 내 사용자 그룹의 아이덴티티를 나타냅니다.

> - [개발자 가이드: CorpGroup](/docs/generated/metamodel/entities/corpGroup.md)

## 메타데이터 모델

### Entity

Entity는 메타데이터 그래프의 기본 노드입니다. 예를 들어, Dataset 또는 CorpUser의 인스턴스가 Entity입니다.

> - [DataHub는 메타데이터를 어떻게 모델링하는가?](/docs/modeling/metadata-model.md)

### Aspect

Aspect는 entity의 특정 측면을 설명하는 속성들의 집합입니다.
Aspect는 entity 간에 공유될 수 있습니다. 예를 들어, "Ownership"은 소유자를 가진 모든 Entity에서 재사용되는 aspect입니다.

> - [메타데이터 aspect란 무엇인가?](/docs/what/aspect.md)
> - [DataHub는 메타데이터를 어떻게 모델링하는가?](/docs/modeling/metadata-model.md)

### Relationships

Relationship은 두 entity 간의 명명된 엣지를 나타냅니다. Aspect 내의 외래 키 속성과 커스텀 어노테이션(@Relationship)을 통해 선언됩니다.

> - [relationship란 무엇인가?](/docs/what/relationship.md)
> - [DataHub는 메타데이터를 어떻게 모델링하는가?](/docs/modeling/metadata-model.md)
