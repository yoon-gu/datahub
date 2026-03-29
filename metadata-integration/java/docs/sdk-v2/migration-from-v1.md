# 마이그레이션 가이드: V1에서 V2로

이 가이드는 Java SDK V1 (RestEmitter)에서 V2 (DataHubClientV2)로 마이그레이션하는 데 도움을 드립니다. 나란히 비교하는 예제를 보여드리고 주요 차이점을 강조합니다.

## 왜 마이그레이션해야 하나요?

V2는 V1보다 크게 개선되었습니다:

- ✅ 수동 MCP 구성 대신 **타입 안전 entity 빌더**
- ✅ 문자열 조작 대신 **자동 URN 생성**
- ✅ 효율적인 점진적 변경을 위한 **Patch 기반 업데이트**
- ✅ 메서드 체이닝을 가진 **플루언트 API**
- ✅ 캐싱을 통한 **지연 로딩**
- ✅ **모드 인식 작업** (SDK vs INGESTION)

## 주요 차이점

| Aspect               | V1 (RestEmitter)        | V2 (DataHubClientV2)         |
| -------------------- | ----------------------- | ---------------------------- |
| **추상화**      | 저수준 MCP          | 고수준 entity          |
| **URN 구성** | 수동 문자열          | 빌더에서 자동 생성       |
| **업데이트**          | 전체 aspect 교체 | Patch 기반 점진적      |
| **타입 안전성**      | 최소                 | 강력한 컴파일 타임 검사 |
| **API 스타일**        | 명령형 emission     | 플루언트 빌더            |
| **Entity 지원**   | 제네릭 MCP            | Dataset, Chart, Dashboard    |

## 마이그레이션 예제

### 예제 1: Dataset 생성

**V1 (RestEmitter):**

```java
import datahub.client.rest.RestEmitter;
import datahub.event.MetadataChangeProposalWrapper;
import com.linkedin.dataset.DatasetProperties;
import com.linkedin.common.urn.DatasetUrn;

// Manual URN construction
DatasetUrn urn = new DatasetUrn(
    new DataPlatformUrn("snowflake"),
    "my_database.my_schema.my_table",
    FabricType.PROD
);

// Manual aspect construction
DatasetProperties props = new DatasetProperties();
props.setDescription("My dataset description");
props.setName("My Dataset");

// Manual MCP construction
MetadataChangeProposalWrapper mcp = MetadataChangeProposalWrapper.builder()
    .entityType("dataset")
    .entityUrn(urn)
    .upsert()
    .aspect(props)
    .build();

// Create emitter
RestEmitter emitter = RestEmitter.create(b -> b.server("http://localhost:8080"));

// Emit
emitter.emit(mcp, null).get();
```

**V2 (DataHubClientV2):**

```java
import datahub.client.v2.DataHubClientV2;
import datahub.client.v2.entity.Dataset;

// Fluent builder
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_database.my_schema.my_table")
    .env("PROD")
    .description("My dataset description")
    .displayName("My Dataset")
    .build();

// Create client
DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .build();

// Upsert (URN auto-generated, aspect auto-wired)
client.entities().upsert(dataset);
```

**변경 사항:**

- ❌ 수동 URN 구성 없음
- ❌ 수동 aspect 생성 없음
- ❌ MCP 래퍼 구성 없음
- ✅ 플루언트 빌더가 모든 것을 처리
- ✅ 타입 안전 메서드 호출
- ✅ 자동 aspect 연결

### 예제 2: 태그 추가

**V1 (RestEmitter):**

```java
import com.linkedin.common.GlobalTags;
import com.linkedin.common.TagAssociation;
import com.linkedin.common.TagAssociationArray;
import com.linkedin.common.urn.TagUrn;

// Fetch existing tags or create new
GlobalTags tags = fetchExistingTags(urn);  // You implement this
if (tags == null) {
    tags = new GlobalTags();
    tags.setTags(new TagAssociationArray());
}

// Add new tag
TagAssociation newTag = new TagAssociation();
newTag.setTag(new TagUrn("pii"));
tags.getTags().add(newTag);

// Create MCP to replace entire GlobalTags aspect
MetadataChangeProposalWrapper mcp = MetadataChangeProposalWrapper.builder()
    .entityType("dataset")
    .entityUrn(urn)
    .upsert()
    .aspect(tags)
    .build();

emitter.emit(mcp, null).get();
```

**V2 (DataHubClientV2):**

```java
// Just add the tag - patch handles everything
dataset.addTag("pii");
client.entities().update(dataset);
```

**변경 사항:**

- ❌ 기존 태그 가져오기 없음
- ❌ 수동 aspect 조작 없음
- ❌ MCP 구성 없음
- ✅ 단일 메서드 호출
- ✅ Patch 기반 (다른 태그를 덮어쓰지 않음)
- ✅ 자동 URN 처리

### 예제 3: 소유자 추가

**V1 (RestEmitter):**

```java
import com.linkedin.common.Ownership;
import com.linkedin.common.Owner;
import com.linkedin.common.OwnerArray;
import com.linkedin.common.OwnershipType;
import com.linkedin.common.urn.Urn;

// Fetch existing owners or create new
Ownership ownership = fetchExistingOwnership(urn);
if (ownership == null) {
    ownership = new Ownership();
    ownership.setOwners(new OwnerArray());
}

// Add new owner
Owner newOwner = new Owner();
newOwner.setOwner(Urn.createFromString("urn:li:corpuser:john_doe"));
newOwner.setType(OwnershipType.TECHNICAL_OWNER);
ownership.getOwners().add(newOwner);

// Create MCP
MetadataChangeProposalWrapper mcp = MetadataChangeProposalWrapper.builder()
    .entityType("dataset")
    .entityUrn(urn)
    .upsert()
    .aspect(ownership)
    .build();

emitter.emit(mcp, null).get();
```

**V2 (DataHubClientV2):**

```java
dataset.addOwner("urn:li:corpuser:john_doe", OwnershipType.TECHNICAL_OWNER);
client.entities().update(dataset);
```

**변경 사항:**

- ❌ 기존 소유자 가져오기 없음
- ❌ 수동 Owner 객체 생성 없음
- ❌ 배열 조작 없음
- ✅ 파라미터가 있는 단일 메서드
- ✅ 타입 안전 소유권 타입 열거형
- ✅ 자동 patch 생성

### 예제 4: 여러 메타데이터 추가

**V1 (RestEmitter):**

```java
// Create dataset properties
DatasetProperties props = new DatasetProperties();
props.setDescription("My description");

// Create tags
GlobalTags tags = new GlobalTags();
TagAssociationArray tagArray = new TagAssociationArray();
tagArray.add(createTagAssociation("pii"));
tagArray.add(createTagAssociation("sensitive"));
tags.setTags(tagArray);

// Create ownership
Ownership ownership = new Ownership();
OwnerArray ownerArray = new OwnerArray();
ownerArray.add(createOwner("urn:li:corpuser:john", OwnershipType.TECHNICAL_OWNER));
ownership.setOwners(ownerArray);

// Create 3 separate MCPs and emit each
emitter.emit(createMCP(urn, props), null).get();
emitter.emit(createMCP(urn, tags), null).get();
emitter.emit(createMCP(urn, ownership), null).get();
```

**V2 (DataHubClientV2):**

```java
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .description("My description")
    .build();

dataset.addTag("pii")
       .addTag("sensitive")
       .addOwner("urn:li:corpuser:john", OwnershipType.TECHNICAL_OWNER);

client.entities().upsert(dataset);  // Single call, all metadata included
```

**변경 사항:**

- ❌ 별도로 여러 aspect 생성 없음
- ❌ 여러 emission 호출 없음
- ✅ 플루언트 API를 위한 메서드 체이닝
- ✅ 단일 upsert가 모든 것을 emit
- ✅ 원자적 작업

### 예제 5: 기존 Entity 업데이트

**V1 (RestEmitter):**

```java
// 1. Fetch current state from DataHub
DatasetProperties existingProps = fetchAspect(urn, DatasetProperties.class);

// 2. Modify
existingProps.setDescription("Updated description");

// 3. Send back (overwrites entire aspect)
MetadataChangeProposalWrapper mcp = MetadataChangeProposalWrapper.builder()
    .entityType("dataset")
    .entityUrn(urn)
    .upsert()
    .aspect(existingProps)
    .build();

emitter.emit(mcp, null).get();
```

**V2 (DataHubClientV2):**

```java
// Just modify - patch handles incremental update
Dataset dataset = client.entities().get(urn);  // Optional: load existing
dataset.setDescription("Updated description");
client.entities().update(dataset);  // Patch only changes description
```

**변경 사항:**

- ✅ patches의 경우 가져오지 않고 업데이트 가능
- ✅ Patch 기반 점진적 업데이트
- ✅ 다른 필드를 덮어쓸 위험 없음
- ✅ 더 효율적인 페이로드

## 마이그레이션 체크리스트

### 1. 의존성 업데이트

기존 의존성 유지 (하위 호환 가능):

```gradle
dependencies {
    implementation 'io.acryl:datahub-client:__version__'
}
```

### 2. 임포트 변경

**교체:**

```java
import datahub.client.rest.RestEmitter;
import datahub.event.MetadataChangeProposalWrapper;
```

**다음으로:**

```java
import datahub.client.v2.DataHubClientV2;
import datahub.client.v2.entity.Dataset;
import datahub.client.v2.entity.Chart;
```

### 3. RestEmitter를 DataHubClientV2로 교체

**이전:**

```java
RestEmitter emitter = RestEmitter.create(b -> b
    .server("http://localhost:8080")
    .token("my-token")
);
```

**이후:**

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .token("my-token")
    .build();
```

### 4. Entity 빌더 사용

수동 MCP/URN 구성을 entity 빌더로 교체:

**이전:**

```java
DatasetUrn urn = new DatasetUrn(...);
DatasetProperties props = new DatasetProperties();
props.setDescription("...");
MetadataChangeProposalWrapper mcp = MetadataChangeProposalWrapper.builder()...
emitter.emit(mcp, null).get();
```

**이후:**

```java
Dataset dataset = Dataset.builder()
    .platform("...")
    .name("...")
    .description("...")
    .build();
client.entities().upsert(dataset);
```

### 5. 업데이트에 Patch 작업 사용

가져오기-수정-전송을 patches로 교체:

**이전:**

```java
GlobalTags tags = fetch(...);
tags.getTags().add(...);
emit(tags);
```

**이후:**

```java
dataset.addTag("...");
client.entities().update(dataset);
```

## 점진적 마이그레이션 전략

V1과 V2를 함께 사용하면서 점진적으로 마이그레이션할 수 있습니다:

```java
// V1 emitter (for unsupported operations)
RestEmitter emitter = RestEmitter.create(b -> b.server("..."));

// V2 client (for entities)
DataHubClientV2 client = DataHubClientV2.builder()
    .server("...")
    .build();

// Use V2 for supported entities
Dataset dataset = Dataset.builder()...
client.entities().upsert(dataset);

// Fall back to V1 for custom MCPs
MetadataChangeProposalWrapper customMcp = ...;
emitter.emit(customMcp, null).get();
```

## 일반적인 함정

### 1. `update()` 또는 `upsert()` 호출 잊기

**문제:**

```java
dataset.addTag("pii");  // Patch created but not emitted!
// Missing: client.entities().update(dataset);
```

**해결책:**
항상 변경 사항을 emit하기 위해 `update()` 또는 `upsert()`를 호출하세요.

### 2. V2 Entity에서 V1 패턴 사용

**문제:**

```java
Dataset dataset = Dataset.builder()...;
// Don't do this - use client.entities() instead
emitter.emit(dataset.toMCPs(), null);  // Wrong!
```

**해결책:**
V2의 EntityClient를 사용하세요:

```java
client.entities().upsert(dataset);
```

### 3. 작업 모드 혼합

**문제:**

```java
// Client in SDK mode
DataHubClientV2 client = DataHubClientV2.builder()
    .operationMode(OperationMode.SDK)
    .build();

// But manually setting system description (conflicts with mode)
dataset.setSystemDescription("...");  // Inconsistent!
```

**해결책:**
모드 인식 메서드를 사용하거나 모드와 명시적 메서드를 일치시키세요:

```java
dataset.setDescription("...");  // Mode-aware
```

## 마이그레이션 후 이점

- **일반적인 작업의 코드 50-80% 감소**
- **타입 안전성**이 컴파일 타임에 오류를 잡음
- **patches로 더 나은 성능**
- **모의 entity로 더 쉬운 테스트**
- **자동완성으로 더 나은 IDE 지원**

## 도움이 필요하신가요?

- **V2 문서**: [시작하기 가이드](./getting-started.md)
- **Entity 가이드**: [Dataset](./dataset-entity.md), [Chart](./chart-entity.md)
- **예제**: [V2 예제 디렉토리](../../examples/src/main/java/io/datahubproject/examples/v2/)
- **V1 문서**: [Java SDK V1](../../as-a-library.md) (참조용)

## 여전히 V1 기능을 사용 중이신가요?

일부 고급 기능은 아직 V1 전용입니다:

- **KafkaEmitter** - Kafka 기반 emission에는 V1 사용
- **FileEmitter** - 파일 기반 emission에는 V1 사용
- **커스텀 MCP** - V2에 아직 없는 entity 타입에는 V1 사용
- **직접 aspect 접근** - 세밀한 제어에는 V1 사용

동일한 애플리케이션에서 V1과 V2를 모두 사용할 수 있습니다!
