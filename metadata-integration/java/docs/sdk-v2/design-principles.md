# Java SDK V2 설계 원칙

이 문서는 DataHub Java SDK V2의 아키텍처 개요를 제공하며, 타입 안전하고 효율적인 메타데이터 관리 기능을 가능하게 하는 엔지니어링 원칙과 설계 패턴을 탐구합니다.

## 아키텍처 철학

SDK V2는 **실용적인 재사용, 지능적인 캐싱, 계층화된 추상화**를 기반으로 구축되었습니다. 인프라를 재발명하는 대신, 검증된 컴포넌트를 일관되고 직관적인 API로 구성하면서 효율적인 메타데이터 작업을 위한 새로운 패턴을 도입합니다.

### 핵심 원칙

1. **기존 인프라 활용** - 검증된 컴포넌트 위에 구축
2. **타입 안전성을 최우선 관심사로** - 컴파일 타임 정확성을 위해 Java의 타입 시스템 활용
3. **관심사 분리** - entity, 작업, 전송 계층 사이의 명확한 경계
4. **Patches를 통한 효율성** - 전체 교체 대신 수술적 업데이트
5. **지능적인 리소스 관리** - 지연 로딩, 캐싱, 배칭

## 레이어 아키텍처

SDK V2는 책임의 명확한 분리를 가진 3계층 아키텍처를 채택합니다:

```
┌─────────────────────────────────────────────────────────────┐
│                    Entity Layer                              │
│  (Dataset, Chart, Dashboard - Business Logic)                │
│  - Fluent builders for entity construction                   │
│  - Patch accumulation and aspect management                  │
│  - Mode-aware behavior (SDK vs INGESTION)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                 Operations Layer                             │
│  (EntityClient - CRUD Operations)                            │
│  - Entity lifecycle management                               │
│  - Patch vs full aspect emission logic                       │
│  - Lazy loading coordination                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                  Transport Layer                             │
│  (RestEmitter, Patch Builders)                               │
│  - HTTP communication with DataHub                           │
│  - MCP serialization and emission                            │
│  - Patch builder integration                                 │
└─────────────────────────────────────────────────────────────┘
```

## 설계 패턴

### 1. 플루언트 빌더 패턴

Entity 구성은 개발자가 필수 필드를 안내받고 IDE 자동완성 지원을 받을 수 있는 **플루언트 빌더 패턴**을 따릅니다:

```java
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("analytics.public.events")
    .env("PROD")
    .description("User events")
    .build();
```

**엔지니어링 이점:**

- **컴파일 타임 검증** - 누락된 필수 필드 (platform, name)는 컴파일 시 실패
- **불변 구성** - 빌더가 상태를 축적; `build()`는 불변 entity 생성
- **발견 가능성** - IDE 자동완성이 사용 가능한 메서드 표시
- **확장성** - 기존 코드를 깨뜨리지 않고 새로운 선택적 파라미터 추가

### 2. Patch 축적 패턴

aspect를 직접 수정하는 대신, 변경이 대기 목록에 축적되는 **patch MCP**를 생성합니다:

```java
dataset.addTag("pii")                          // Creates patch MCP
       .addOwner("user", TECHNICAL_OWNER)      // Creates patch MCP
       .addCustomProperty("retention", "90");  // Creates patch MCP

client.entities().upsert(dataset);  // Emits all patches atomically
```

**엔지니어링 이점:**

- **지연된 실행** - 여러 변경 사항을 단일 네트워크 왕복으로 배칭
- **원자적 업데이트** - 모든 patches가 함께 적용되거나 하나도 적용되지 않음
- **효율적인 전송** - 변경된 필드만 네트워크로 전송
- **검증된 인프라 재사용** - 기존 `datahub.client.patch` 빌더 활용

**구현 세부 사항:**
Entity 베이스 클래스는 여러 변경 추적 메커니즘을 유지합니다:

```java
// From Entity.java
protected final Map<String, RecordTemplate> aspectCache;        // Cached aspects from builder
protected final List<MetadataChangeProposalWrapper> pendingMCPs; // Full aspect replacements
protected final List<MetadataChangeProposal> pendingPatches;     // Incremental patches
```

각 변경 (addTag, addOwner)은 기존 빌더를 사용하여 patch를 생성합니다:

```java
// From Dataset.java
public Dataset addTag(@Nonnull String tagUrn) {
    GlobalTagsPatchBuilder patch = new GlobalTagsPatchBuilder()
        .urn(getUrn())
        .addTag(tag, null);
    addPatchMcp(patch.build());  // Adds to pendingPatches list
    return this;
}
```

`EntityClient.upsert()`가 호출되면 entity에 축적된 **모든 것**을 순서대로 emit합니다:

```java
// From EntityClient.upsert()

// Step 1: Emit cached aspects (from builder)
if (!entity.toMCPs().isEmpty()) {
    for (MetadataChangeProposalWrapper mcp : entity.toMCPs()) {
        emitter.emit(mcp);
    }
}

// Step 2: Emit pending full aspect MCPs (from set*() methods)
if (entity.hasPendingMCPs()) {
    for (MetadataChangeProposalWrapper mcp : entity.getPendingMCPs()) {
        emitter.emit(mcp);
    }
    entity.clearPendingMCPs();
}

// Step 3: Emit all pending patches (from add*/remove* methods)
if (entity.hasPendingPatches()) {
    for (MetadataChangeProposal patchMcp : entity.getPendingPatches()) {
        emitter.emit(patchMcp, null);
    }
    entity.clearPendingPatches();
}
```

**핵심 인사이트:** `upsert()`는 양자택일 작업이 아닙니다 - entity에 축적된 **모든** 변경 사항을 emit합니다. 전송되는 내용은 어떤 메서드를 호출하느냐가 아니라 entity에 무엇을 축적했는지에 따라 달라집니다.

### 3. TTL 기반 캐싱을 통한 지연 로딩

Entity는 데이터 신선도를 보장하면서 네트워크 호출을 최소화하는 **지연 aspect 로딩**을 지원합니다:

```java
// Entity maintains aspect cache with timestamps
protected final Map<String, RecordTemplate> aspectCache;
protected final Map<String, Long> aspectTimestamps;
protected long cacheTtlMs = 60000;  // 60-second default TTL
```

**로딩 전략:**

1. **캐시 전용 접근** (`getAspectCached`) - 캐시된 aspect 반환 또는 null
2. **지연 로딩** (`getAspectLazy`) - 캐시 신선도 확인, 오래된 경우 서버에서 가져옴
3. **가져오거나 생성** (`getOrCreateAspect`) - 캐시된 것을 반환하거나 로컬에서 새로운 빈 aspect 생성

**구현:**

```java
protected <T extends RecordTemplate> T getAspectLazy(@Nonnull Class<T> aspectClass) {
    String aspectName = getAspectName(aspectClass);

    // Check cache freshness
    if (aspectCache.containsKey(aspectName)) {
        Long timestamp = aspectTimestamps.get(aspectName);
        if (timestamp != null && System.currentTimeMillis() - timestamp < cacheTtlMs) {
            return aspectClass.cast(aspectCache.get(aspectName));
        }
    }

    // Fetch from server if client is bound
    if (client != null) {
        T aspect = client.getAspect(urn, aspectClass);
        if (aspect != null) {
            aspectCache.put(aspectName, aspect);
            aspectTimestamps.put(aspectName, System.currentTimeMillis());
        }
        return aspect;
    }

    return null;
}
```

**엔지니어링 이점:**

- **네트워크 효율성** - 중복 서버 호출 감소
- **신선도 보장** - 구성 가능한 TTL로 데이터가 오래되지 않도록 보장
- **호출자에게 투명** - 복잡성이 단순한 getter 뒤에 숨겨짐
- **클라이언트 바인딩** - EntityClient에 바인딩된 entity가 지연 로딩 활성화

### 4. 모드 인식 Aspect 선택

SDK V2는 **사용자 주도 편집** (SDK 모드)과 **시스템/파이프라인 쓰기** (INGESTION 모드)를 구분합니다:

```java
public enum OperationMode {
    SDK,        // Interactive use - writes to editable aspects
    INGESTION   // ETL pipelines - writes to system aspects
}
```

**Aspect 라우팅:**

- **SDK 모드** → `editableDatasetProperties`, `editableSchemaMetadata`
- **INGESTION 모드** → `datasetProperties`, `schemaMetadata`

**구현:**

```java
public Dataset setDescription(@Nonnull String description) {
    if (isIngestionMode()) {
        return setSystemDescription(description);  // datasetProperties
    } else {
        return setEditableDescription(description); // editableDatasetProperties
    }
}
```

**엔지니어링 이점:**

- **명확한 출처** - 사람과 기계의 편집을 구분
- **UI 일관성** - DataHub UI가 편집 가능한 aspect를 사용자 재정의로 표시
- **비파괴적** - 사용자가 문서를 추가해도 시스템 데이터 보존
- **lineage 보존** - ingestion 파이프라인이 사용자 편집을 덮어쓰지 않고 시스템 데이터 새로 고침 가능

### 5. 두 가지 Entity 수명 주기 패턴

Entity는 두 가지 방식으로 인스턴스화될 수 있으며 각각 고유한 의미를 가집니다:

#### **패턴 1: 빌더 구성 (새 Entity)**

```java
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .build();
// aspectCache populated with builder-provided aspects
// aspectTimestamps empty - indicates new entity
```

**사용 사례:** 처음부터 새 entity 생성

#### **패턴 2: 서버 로딩 (기존 Entity)**

```java
Dataset dataset = client.entities().get(urn);
// aspectCache populated with server aspects
// aspectTimestamps records fetch time for each aspect
// Entity automatically bound to client for lazy loading
```

**사용 사례:** 현재 서버 상태로 기존 entity 수정. 이미 캐시되지 않은 aspect에 접근할 때 entity는 자동으로 서버에서 가져옵니다 (지연 로딩).

### 6. 지연 로딩을 위한 클라이언트 바인딩

Entity는 서버에서 로드되거나 `upsert()` 중에 지연 aspect 가져오기를 활성화하기 위해 **자동으로 EntityClient에 바인딩**됩니다:

```java
public void bindToClient(@Nonnull EntityClient client,
                        @Nonnull OperationMode mode) {
    if (this.client == null) {
        this.client = client;
    }
    if (this.mode == null) {
        this.mode = mode;
    }
}
```

**바인딩은 `upsert()` 중에 자동으로 발생합니다:**

```java
// From EntityClient.upsert()
entity.bindToClient(this, config.getMode());
```

**엔지니어링 이점:**

- **투명한 지연 로딩** - 캐시되지 않은 경우 첫 번째 접근 시 aspect 가져옴
- **자동 바인딩** - `get()` 또는 `upsert()` 작업 중 entity가 클라이언트에 바인딩
- **모드 전파** - 클라이언트 모드가 자동으로 entity에 적용

## 타입 안전성 및 제네릭 설계

### 강력한 타입의 Aspect 처리

SDK V2는 Java 제네릭을 활용하여 aspect에 대한 컴파일 타임 타입 안전성을 제공합니다:

```java
// Type-safe aspect retrieval
protected <T extends RecordTemplate> T getAspectLazy(@Nonnull Class<T> aspectClass) {
    String aspectName = getAspectName(aspectClass);
    RecordTemplate aspect = aspectCache.get(aspectName);
    return aspectClass.cast(aspect);
}

// Usage - compiler enforces type correctness
DatasetProperties props = dataset.getAspectLazy(DatasetProperties.class);
```

**엔지니어링 이점:**

- **컴파일 타임 검사** - 타입 불일치가 런타임 전에 발견
- **리팩토링 안전성** - IDE가 코드베이스 전체에서 aspect 사용을 추적 가능
- **자동완성 지원** - IDE가 사용 가능한 aspect 제안
- **런타임 안전성** - 올바른 사용으로 `ClassCastException` 불가능

### URN 타입 안전성

Entity별 URN 타입이 잘못된 URN 사용을 방지합니다:

```java
public class Dataset extends Entity {
    public DatasetUrn getDatasetUrn() {
        return (DatasetUrn) urn;
    }
}

// Compile-time enforcement
DatasetUrn urn = dataset.getDatasetUrn();  // Type-safe
Urn genericUrn = dataset.getUrn();         // Also available
```

## 기존 인프라와의 통합

### Patch 빌더 재사용

SDK V2는 새로운 구현을 만들지 않고 `datahub.client.patch`의 **기존 patch 빌더를 재사용**합니다:

- `OwnershipPatchBuilder` - 소유자 추가/제거
- `GlobalTagsPatchBuilder` - 태그 관리
- `GlossaryTermsPatchBuilder` - 용어 연관
- `DomainsPatchBuilder` - 도메인 할당
- `DatasetPropertiesPatchBuilder` - 속성 업데이트
- `EditableDatasetPropertiesPatchBuilder` - 편집 가능한 속성 업데이트

**엔지니어링 이점:**

- **검증된 로직** - Patch 빌더는 Python SDK에서 프로덕션으로 사용
- **일관성** - 언어별 SDK 전체에서 동일한 patch 의미론
- **유지보수성** - 유지관리할 단일 구현
- **정확성** - 복잡한 JSON Patch 로직 이미 검증됨

**통합 예제:**

```java
public Dataset addOwner(@Nonnull String ownerUrn, @Nonnull OwnershipType type) {
    Urn owner = Urn.createFromString(ownerUrn);
    OwnershipPatchBuilder patch = new OwnershipPatchBuilder()
        .urn(getUrn())
        .addOwner(owner, type);
    addPatchMcp(patch.build());  // Stores patch MCP
    return this;
}
```

### RestEmitter 활용

전송 계층은 HTTP 통신을 위해 `RestEmitter`를 재사용합니다:

- 미래를 이용한 비블로킹 emission
- 구성 가능한 재시도 및 타임아웃
- 토큰 기반 인증
- 비동기 HTTP 클라이언트 풀링

**RestEmitter에 변경 없음** - SDK V2는 순수하게 추가적입니다.

## 리소스 관리 및 효율성

### 배치 Emission

여러 patches가 축적되어 원자적으로 emit됩니다:

```java
dataset.addTag("tag1").addTag("tag2").addOwner("user1", OWNER);
client.entities().upsert(dataset);  // Single network call, 3 patches
```

### 연결 풀링

RestEmitter는 효율적인 HTTP 재사용을 위해 연결 풀링을 사용하는 `CloseableHttpAsyncClient`를 사용합니다.

### 우아한 성능 저하

지연 로딩 실패는 기록되지만 충돌하지 않습니다:

```java
catch (Exception e) {
    log.warn("Failed to lazy-load aspect {}: {}", aspectName, e.getMessage());
    return null;  // Graceful degradation
}
```

## 비교: V1 vs V2 아키텍처

| Aspect                | V1 (RestEmitter)               | V2 (DataHubClientV2)        |
| --------------------- | ------------------------------ | --------------------------- |
| **추상화 수준** | 낮음 - MCP                     | 높음 - Entities             |
| **URN 구성**  | 수동 문자열                 | 빌더에서 자동 생성      |
| **Aspect 연결**     | 수동 MCP 빌딩            | entity 메서드에 숨겨짐    |
| **업데이트**           | 전체 aspect 교체        | Patch 기반 점진적     |
| **타입 안전성**       | 최소 - 제네릭 MCP         | 강력 - 타입 entity     |
| **지연 로딩**      | 지원 안 됨                  | TTL 기반 캐싱           |
| **모드 인식**    | 지원 안 됨                  | SDK vs INGESTION 모드      |
| **학습 곡선**    | 가파름 - MCP 지식 필요 | 완만함 - 직관적인 빌더 |

## 성능 특성

### 네트워크 효율성

- **Patch 기반 업데이트**: O(변경된_필드) vs O(모든_필드)
- **지연 로딩**: 접근 시에만 aspect 가져옴
- **배치 emission**: 여러 patches를 단일 flush로 전송
- **연결 재사용**: HTTP 클라이언트 풀링

### 메모리 효율성

- **Aspect 캐싱**: 가져온 aspect만 저장
- **TTL 만료**: 오래된 aspect가 GC 대상이 됨
- **지연 인스턴스화**: Aspect가 요청 시 생성

### 시간 복잡도

- **Entity 생성**: O(1) - 빌더 축적
- **Patch 추가**: O(1) - 목록에 추가
- **Upsert 작업**: O(n), n = 대기 중인 patches 또는 캐시된 aspect
- **지연 가져오기**: O(1) 캐시 조회 + 미스 시 O(1) 네트워크

## 확장 포인트

SDK V2는 확장성을 위해 설계되었습니다:

1. **새 entity 타입** - `Entity` 베이스 클래스 확장
2. **커스텀 aspects** - `getAspectLazy` / `getOrCreateAspect` 사용
3. **새 patch 타입** - 기존 patch 빌더 활용
4. **커스텀 캐싱** - `cacheTtlMs` 재정의
5. **전송 커스터마이징** - 빌더를 통해 RestEmitter 커스터마이징

## 요약

Java SDK V2는 원칙적인 설계를 통해 목표를 달성합니다:

- **재발명보다 재사용** - 기존 patch 빌더와 RestEmitter 활용
- **교체보다 patches** - 효율적인 점진적 업데이트
- **즉시 로딩보다 지연 로딩** - 캐싱으로 요청 시 aspect 가져오기
- **편의보다 타입 안전성** - 전체에 걸친 강력한 타이핑
- **모놀리스보다 계층** - entity, 작업, 전송의 명확한 분리
- **순수성보다 실용성** - 모드 인식 동작이 실제 사용 패턴과 일치

그 결과 Java 개발자에게 자연스럽게 느껴지는 SDK가 생성되며, 대규모 프로덕션 메타데이터 관리에 필요한 효율성과 정확성을 제공합니다.
