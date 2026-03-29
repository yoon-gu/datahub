# Container Entity

Container entity는 데이터 자산의 계층적 그룹(데이터베이스, 스키마, 폴더, 프로젝트)을 나타냅니다. 이 가이드는 SDK V2의 container 작업을 다룹니다.

## 개요

Container는 데이터 자산을 계층적 구조로 구성합니다. 일반적인 사용 사례:

- **데이터베이스 계층**: 데이터베이스 → 스키마 → 테이블
- **데이터 레이크 구조**: 버킷 → 폴더 → 파일
- **프로젝트 계층**: 프로젝트 → Dataset → 테이블

Container는 속성(플랫폼, 데이터베이스, 스키마 등)에서 생성된 GUID 기반 URN을 사용하여 동일한 논리적 container에 대해 결정론적 URN을 보장합니다.

## URN 구성

Container URN은 다음 패턴을 따릅니다:

```
urn:li:container:{guid}
```

GUID는 속성 집합(플랫폼, 데이터베이스, 스키마, 환경 등)을 해싱하여 생성됩니다. 이를 통해:

- 결정론적 URN: 동일한 속성은 항상 동일한 URN 생성
- 고유성: 서로 다른 container는 서로 다른 URN 보유
- 계층적 구성: 부모-자식 관계가 명시적

**예제:**

```java
Container database = Container.builder()
    .platform("snowflake")
    .database("analytics_db")
    .env("PROD")
    .displayName("Analytics Database")
    .build();

String urn = database.getContainerUrn();
// urn:li:container:{guid-based-on-properties}
```

## Container 생성

### 데이터베이스 Container

```java
Container database = Container.builder()
    .platform("snowflake")
    .database("analytics_db")
    .env("PROD")
    .displayName("Analytics Database")
    .description("Production analytics database")
    .qualifiedName("prod.snowflake.analytics_db")
    .build();
```

### 부모가 있는 스키마 Container

```java
Container schema = Container.builder()
    .platform("snowflake")
    .database("analytics_db")
    .schema("public")
    .env("PROD")
    .displayName("Public Schema")
    .qualifiedName("prod.snowflake.analytics_db.public")
    .parentContainer(database.getContainerUrn())
    .build();
```

### 커스텀 속성 포함

```java
Map<String, String> properties = new HashMap<>();
properties.put("size_gb", "2500");
properties.put("table_count", "150");
properties.put("owner_team", "data_platform");

Container database = Container.builder()
    .platform("postgres")
    .database("production")
    .displayName("Production Database")
    .customProperties(properties)
    .build();
```

### 외부 URL 포함

```java
Container database = Container.builder()
    .platform("bigquery")
    .database("analytics")
    .displayName("Analytics Database")
    .externalUrl("https://console.cloud.google.com/bigquery/project/analytics")
    .build();
```

## 계층적 관계

### 부모-자식 구조

Container는 데이터 자산을 계층적으로 구성하기 위한 명시적인 부모-자식 관계를 지원합니다.

**데이터베이스 → 스키마 계층:**

```java
// Level 1: Database
Container database = Container.builder()
    .platform("postgres")
    .database("production")
    .env("PROD")
    .displayName("Production Database")
    .build();

// Level 2: Schema (child of database)
Container schema = Container.builder()
    .platform("postgres")
    .database("production")
    .schema("public")
    .env("PROD")
    .displayName("Public Schema")
    .parentContainer(database.getContainerUrn())
    .build();
```

### 3단계 계층

**데이터베이스 → 스키마 → 테이블 그룹:**

```java
// Level 1: Database
Container database = Container.builder()
    .platform("snowflake")
    .database("analytics")
    .displayName("Analytics Database")
    .build();

// Level 2: Schema
Container schema = Container.builder()
    .platform("snowflake")
    .database("analytics")
    .schema("public")
    .displayName("Public Schema")
    .parentContainer(database.getContainerUrn())
    .build();

// Level 3: Logical grouping
Container tableGroup = Container.builder()
    .platform("snowflake")
    .database("analytics")
    .schema("public")
    .displayName("Customer Tables")
    .qualifiedName("analytics.public.customer_group")
    .parentContainer(schema.getContainerUrn())
    .build();
```

### 부모 관계 관리

```java
// Set parent container
container.setContainer("urn:li:container:{parent-guid}");

// Get parent container
String parentUrn = container.getParentContainer();

// Clear parent container
container.clearContainer();
```

## Container 작업

### 태그 추가

태그로 container 분류:

```java
container.addTag("production");
container.addTag("tier1");
container.addTag("pii");

// Or use full URN
container.addTag("urn:li:tag:critical");
```

### 소유자 관리

다양한 소유권 타입으로 소유자 추가:

```java
import com.linkedin.common.OwnershipType;

// Add technical owner
container.addOwner("urn:li:corpuser:data_platform_team",
                   OwnershipType.TECHNICAL_OWNER);

// Add data steward
container.addOwner("urn:li:corpuser:analytics_lead",
                   OwnershipType.DATA_STEWARD);

// Remove owner
container.removeOwner("urn:li:corpuser:data_platform_team");
```

### Glossary Terms 추가

비즈니스 glossary 용어 연관:

```java
container.addTerm("urn:li:glossaryTerm:ProductionDatabase");
container.addTerm("urn:li:glossaryTerm:CustomerData");

// Remove term
container.removeTerm("urn:li:glossaryTerm:ProductionDatabase");
```

### 도메인 설정

container를 도메인에 할당:

```java
container.setDomain("urn:li:domain:Analytics");

// Clear all domains
container.clearDomains();
```

### 설명 업데이트

container 설명 설정 또는 업데이트:

```java
// Updates editableContainerProperties
container.setDescription("Production database for analytics workloads");
```

## 빌더 속성

### 필수 속성

- **platform**: 플랫폼 이름 (예: "snowflake", "bigquery", "postgres")
- **displayName**: container의 사람이 읽을 수 있는 이름

### 선택적 속성

- **database**: 데이터베이스 이름 (데이터베이스/스키마 container의 경우)
- **schema**: 스키마 이름 (스키마 container의 경우)
- **env**: 환경 (기본값: "PROD")
- **platformInstance**: 플랫폼 인스턴스 식별자
- **qualifiedName**: 완전 정규화된 이름 (예: "prod.snowflake.analytics_db")
- **description**: Container 설명
- **externalUrl**: container에 대한 외부 링크
- **parentContainer**: 부모 container URN
- **customProperties**: 커스텀 키-값 속성의 맵

## 속성 접근

### 속성 읽기

```java
// Display name
String displayName = container.getDisplayName();

// Qualified name
String qualifiedName = container.getQualifiedName();

// Description
String description = container.getDescription();

// External URL
String externalUrl = container.getExternalUrl();

// Custom properties
Map<String, String> customProps = container.getCustomProperties();

// Parent container
String parentUrn = container.getParentContainer();
```

## 공통 패턴

### 데이터 웨어하우스 구조

**Snowflake 데이터베이스 및 스키마:**

```java
// Database container
Container database = Container.builder()
    .platform("snowflake")
    .database("analytics")
    .env("PROD")
    .displayName("Analytics Database")
    .description("Primary analytics database")
    .build();

database
    .addTag("production")
    .addTag("analytics")
    .addOwner("urn:li:corpuser:data_platform", OwnershipType.TECHNICAL_OWNER)
    .setDomain("urn:li:domain:Analytics");

// Schema container
Container schema = Container.builder()
    .platform("snowflake")
    .database("analytics")
    .schema("public")
    .env("PROD")
    .displayName("Public Schema")
    .description("Main schema for analytics tables")
    .parentContainer(database.getContainerUrn())
    .build();

schema
    .addTag("public")
    .addOwner("urn:li:corpuser:analytics_team", OwnershipType.TECHNICAL_OWNER)
    .setDomain("urn:li:domain:Analytics");
```

### BigQuery 프로젝트 및 Dataset

```java
// Project container
Container project = Container.builder()
    .platform("bigquery")
    .database("my-project")
    .env("PROD")
    .displayName("My GCP Project")
    .externalUrl("https://console.cloud.google.com/bigquery/project/my-project")
    .build();

// Dataset container
Container dataset = Container.builder()
    .platform("bigquery")
    .database("my-project")
    .schema("analytics")
    .env("PROD")
    .displayName("Analytics Dataset")
    .parentContainer(project.getContainerUrn())
    .build();
```

### 데이터 레이크 폴더 구조

```java
// Bucket container
Container bucket = Container.builder()
    .platform("s3")
    .database("my-data-lake")
    .env("PROD")
    .displayName("Data Lake Bucket")
    .build();

// Folder container
Map<String, String> folderProps = new HashMap<>();
folderProps.put("folder_path", "/raw/customer_data");
folderProps.put("file_count", "1500");

Container folder = Container.builder()
    .platform("s3")
    .database("my-data-lake")
    .schema("raw")
    .env("PROD")
    .displayName("Customer Data Folder")
    .parentContainer(bucket.getContainerUrn())
    .customProperties(folderProps)
    .build();
```

## 플루언트 API

모든 변경 작업은 메서드 체이닝을 위해 container 인스턴스를 반환합니다:

```java
Container database = Container.builder()
    .platform("snowflake")
    .database("analytics")
    .displayName("Analytics Database")
    .build();

database
    .addTag("production")
    .addTag("tier1")
    .addOwner("urn:li:corpuser:data_team", OwnershipType.TECHNICAL_OWNER)
    .addOwner("urn:li:corpuser:analytics_lead", OwnershipType.DATA_STEWARD)
    .addTerm("urn:li:glossaryTerm:ProductionDatabase")
    .setDomain("urn:li:domain:Analytics")
    .setDescription("Production analytics database");
```

## DataHub에 Upserting

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .build();

// Create hierarchy
Container database = Container.builder()
    .platform("snowflake")
    .database("analytics")
    .displayName("Analytics Database")
    .build();

Container schema = Container.builder()
    .platform("snowflake")
    .database("analytics")
    .schema("public")
    .displayName("Public Schema")
    .parentContainer(database.getContainerUrn())
    .build();

// Upsert in order: parent before children
client.entities().upsert(database);
client.entities().upsert(schema);
```

## 완전한 예제

```java
import com.linkedin.common.OwnershipType;
import datahub.client.v2.DataHubClientV2;
import datahub.client.v2.entity.Container;
import java.util.HashMap;
import java.util.Map;

public class ContainerExample {
  public static void main(String[] args) throws Exception {
    DataHubClientV2 client = DataHubClientV2.builder()
        .server("http://localhost:8080")
        .build();

    // Create database container
    Map<String, String> dbProps = new HashMap<>();
    dbProps.put("database_type", "analytics");
    dbProps.put("size_gb", "5000");

    Container database = Container.builder()
        .platform("snowflake")
        .database("analytics_db")
        .env("PROD")
        .displayName("Analytics Database")
        .qualifiedName("prod.snowflake.analytics_db")
        .description("Production analytics database")
        .externalUrl("https://snowflake.example.com/databases/analytics_db")
        .customProperties(dbProps)
        .build();

    database
        .addTag("production")
        .addTag("analytics")
        .addTag("tier1")
        .addOwner("urn:li:corpuser:data_platform", OwnershipType.TECHNICAL_OWNER)
        .addOwner("urn:li:corpuser:analytics_lead", OwnershipType.DATA_STEWARD)
        .addTerm("urn:li:glossaryTerm:ProductionDatabase")
        .setDomain("urn:li:domain:Analytics");

    // Create schema container
    Map<String, String> schemaProps = new HashMap<>();
    schemaProps.put("table_count", "150");
    schemaProps.put("refresh_schedule", "hourly");

    Container schema = Container.builder()
        .platform("snowflake")
        .database("analytics_db")
        .schema("public")
        .env("PROD")
        .displayName("Public Schema")
        .qualifiedName("prod.snowflake.analytics_db.public")
        .description("Main schema for analytics tables")
        .parentContainer(database.getContainerUrn())
        .customProperties(schemaProps)
        .build();

    schema
        .addTag("public")
        .addTag("production-ready")
        .addOwner("urn:li:corpuser:analytics_team", OwnershipType.TECHNICAL_OWNER)
        .setDomain("urn:li:domain:Analytics");

    // Upsert to DataHub
    client.entities().upsert(database);
    client.entities().upsert(schema);

    System.out.println("Created container hierarchy:");
    System.out.println("  Database: " + database.getContainerUrn());
    System.out.println("  Schema: " + schema.getContainerUrn());

    client.close();
  }
}
```

## 모범 사례

1. **생성 순서**: 항상 자식 container보다 부모 container를 먼저 upsert
2. **완전 정규화된 이름**: 명확성을 위해 완전 정규화된 이름 사용 (예: "prod.snowflake.analytics_db.public")
3. **커스텀 속성**: 크기, 테이블 수, 소유자 팀 등의 추가 메타데이터 저장
4. **일관된 환경**: 관련 container 전체에 일관된 환경 값 사용
5. **외부 URL**: 쉬운 탐색을 위해 소스 시스템의 container에 대한 링크 제공
6. **계층적 태그**: 특정 태그와 상속된 태그 모두 적용 (예: 데이터베이스 수준에서 "production", 스키마 수준에서 "public")

## 참조

- [Entities 개요](entities-overview.md)
- [Dataset Entity 가이드](dataset-entity.md)
- [Patch 작업](patch-operations.md)
- [시작하기](getting-started.md)
