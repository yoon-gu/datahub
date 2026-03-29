# Entities 개요

SDK V2는 DataHub 메타데이터 entity를 나타내는 고수준 entity 클래스를 제공합니다. 이 가이드는 모든 entity 타입에 걸친 공통 패턴을 다룹니다.

## 지원되는 Entities

SDK V2는 Dataset, Chart, Dashboard, Container, DataFlow, DataJob, MLModel, MLModelGroup을 포함한 모든 주요 DataHub entity 타입을 지원합니다. 각 entity 타입에는 포괄적인 예제와 API 문서가 포함된 전용 가이드가 있습니다.

사용 가능한 entity 목록과 해당 문서는 사이드바의 **Entity 가이드** 섹션을 참조하세요.

## 공통 패턴

### Entity 수명 주기

모든 entity는 일관된 수명 주기를 따릅니다:

1. **구성** - 플루언트 빌더를 사용하여 entity 빌드
2. **메타데이터 추가** - 메서드를 통해 태그, 소유자, 속성 추가
3. **지속** - DataHub에 upsert 또는 update
4. **로딩** - 서버에서 기존 entity 가져오기

```java
// 1. Construction
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .build();

// 2. Metadata Addition
dataset.addTag("pii")
       .addOwner("urn:li:corpuser:john", OwnershipType.TECHNICAL_OWNER);

// 3. Persistence
client.entities().upsert(dataset);

// 4. Loading
Dataset loaded = client.entities().get(datasetUrn);
```

### URN 관리

각 entity 타입에는 강력한 타입의 URN 클래스가 있습니다:

```java
// Dataset
DatasetUrn datasetUrn = dataset.getDatasetUrn();

// Chart
ChartUrn chartUrn = chart.getChartUrn();

// Dashboard
DashboardUrn dashboardUrn = dashboard.getDashboardUrn();

// DataJob
DataJobUrn dataJobUrn = dataJob.getDataJobUrn();

// Generic access
Urn genericUrn = entity.getUrn();
```

**URN 구성:**

```java
// Built automatically from builder
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("db.schema.table")
    .env("PROD")
    .build();
// URN: urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)
```

### 플루언트 메서드 체이닝

모든 변경 메서드는 메서드 체이닝을 위해 `this`를 반환합니다:

```java
dataset.addTag("pii")
       .addTag("analytics")
       .addOwner("urn:li:corpuser:owner1", OwnershipType.TECHNICAL_OWNER)
       .addCustomProperty("team", "data-eng")
       .setDomain("urn:li:domain:Finance");
```

### 세 가지 생성 모드

#### 모드 1: 처음부터 시작 (빌더)

```java
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .description("My description")
    .build();
// aspectCache populated with builder aspects
// pendingPatches empty
```

#### 모드 2: 서버에서 로드

```java
DatasetUrn urn = new DatasetUrn("snowflake", "my_table", "PROD");
Dataset dataset = client.entities().get(urn);
// aspectCache populated with server aspects
// Aspects have timestamps for freshness tracking
```

#### 모드 3: 지연 로딩으로 참조

```java
// Entity bound to client enables lazy loading
Dataset dataset = client.entities().reference(urn);
dataset.bindToClient(client, mode);
String desc = dataset.getDescription();  // Fetches on first access
```

## Aspect 관리

### Aspect 캐싱

Entity는 TTL 기반 신선도를 가진 aspect를 로컬에 캐시합니다:

```java
// Cached aspects with 60-second default TTL
dataset.setCacheTtlMs(120000);  // 2 minutes

// Check cache status
Map<String, RecordTemplate> aspects = dataset.getAllAspects();
```

### 지연 로딩

클라이언트에 바인딩된 경우 aspect는 요청 시 가져옵니다:

```java
Dataset dataset = client.entities().get(urn);
// aspectCache may not have all aspects

String description = dataset.getDescription();
// Triggers lazy fetch if not cached or expired
```

## Patch 기반 작업

### 대기 중인 Patches

변경 사항은 저장 시까지 patches로 축적됩니다:

```java
dataset.addTag("tag1");     // Creates patch
dataset.addTag("tag2");     // Creates patch
dataset.addOwner("user", OwnershipType.TECHNICAL_OWNER);  // Creates patch

// Check pending patches
boolean hasPending = dataset.hasPendingPatches();
List<MetadataChangeProposal> patches = dataset.getPendingPatches();

// Emit all patches
client.entities().update(dataset);

// Patches cleared after emission
dataset.clearPendingPatches();
```

### 전송되는 내용 이해하기

`upsert()` 메서드는 entity에 축적된 모든 것을 emit합니다:

1. **캐시된 aspect** (빌더에서)
2. **전체 aspect 교체** (`set*()` 메서드에서)
3. **Patches** (`add*/remove*` 메서드에서)

**entity가 어떻게 생성되었고 어떤 작업을 수행했는지에 따라 전송되는 내용이 달라집니다:**

**patches가 있는 빌더:**

```java
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .description("Description")
    .build();
dataset.addTag("pii");  // Creates patch
client.entities().upsert(dataset);  // Sends: cached aspects + tag patch
```

**patches만 (로드된 entity):**

```java
Dataset dataset = client.entities().get(urn);
dataset.addTag("pii");  // Creates patch
client.entities().upsert(dataset);  // Sends: tag patch only
```

**전체 aspect 교체:**

```java
Dataset dataset = client.entities().get(urn);
dataset.setDescription("New description");  // Creates full aspect MCP
client.entities().upsert(dataset);  // Sends: complete description aspect
```

**결합된 작업:**

```java
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .build();
dataset.setDescription("Description");  // Full aspect MCP
dataset.addTag("pii");  // Patch
dataset.addOwner("user", OwnershipType.TECHNICAL_OWNER);  // Patch
client.entities().upsert(dataset);  // Sends: cached aspects + description aspect + 2 patches
```

## 모드 인식 작업

Entity는 클라이언트의 작업 모드를 존중합니다:

```java
// SDK mode client
DataHubClientV2 sdkClient = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .operationMode(OperationMode.SDK)  // Default
    .build();

dataset.setDescription("User description");
sdkClient.entities().upsert(dataset);
// Writes to editableDatasetProperties

// INGESTION mode client
DataHubClientV2 ingestionClient = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .operationMode(OperationMode.INGESTION)
    .build();

dataset.setDescription("Ingested description");
ingestionClient.entities().upsert(dataset);
// Writes to datasetProperties
```

## 공통 메타데이터 작업

### 태그

```java
// Add tags
entity.addTag("pii");
entity.addTag("urn:li:tag:analytics");

// Remove tags
entity.removeTag("pii");
```

### 소유자

```java
import com.linkedin.common.OwnershipType;

// Add owners
entity.addOwner("urn:li:corpuser:john", OwnershipType.TECHNICAL_OWNER);
entity.addOwner("urn:li:corpuser:jane", OwnershipType.DATA_STEWARD);

// Remove owners
entity.removeOwner("urn:li:corpuser:john");
```

### Glossary Terms

```java
// Add terms
entity.addTerm("urn:li:glossaryTerm:CustomerData");
entity.addTerm("urn:li:glossaryTerm:PII");

// Remove terms
entity.removeTerm("urn:li:glossaryTerm:CustomerData");
```

### 도메인

```java
// Set domain
entity.setDomain("urn:li:domain:Marketing");

// Remove domain
entity.removeDomain();
```

### 커스텀 속성

```java
// Add custom properties
entity.addCustomProperty("team", "data-engineering");
entity.addCustomProperty("retention", "90_days");

// Remove custom properties
entity.removeCustomProperty("retention");
```

## 오류 처리

오류를 우아하게 처리하세요:

```java
try {
    client.entities().upsert(dataset);
} catch (IOException e) {
    // Network or serialization errors
    log.error("I/O error: {}", e.getMessage());
} catch (ExecutionException e) {
    // Server-side errors
    log.error("Server error: {}", e.getCause().getMessage());
} catch (InterruptedException e) {
    // Operation cancelled
    Thread.currentThread().interrupt();
    log.error("Operation interrupted");
}
```

## Entity별 가이드

각 entity 타입에는 다음을 포함한 상세 정보가 있는 전용 가이드가 있습니다:

- URN 구조 및 구성
- Entity별 속성 및 작업
- 포괄적인 코드 예제
- 모범 사례 및 공통 패턴
- Lineage 및 관계 관리

사용 가능한 entity 문서의 전체 목록은 **사이드바의 Entity 가이드 섹션**을 참조하세요.

예시 가이드로는 [Dataset Entity](./dataset-entity.md), [Chart Entity](./chart-entity.md), [Dashboard Entity](./dashboard-entity.md), [DataJob Entity](./datajob-entity.md)가 있습니다.
