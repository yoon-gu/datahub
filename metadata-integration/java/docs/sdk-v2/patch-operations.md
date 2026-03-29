# Patch 작업 가이드

SDK V2는 메타데이터의 효율적이고 수술적인 수정을 위해 **patch 기반 업데이트**를 사용합니다. 이 가이드는 patches가 어떻게 작동하는지 설명하고 언제 사용해야 하는지 안내합니다.

## Patches란 무엇인가요?

Patches는 전체 aspect를 교체하지 않고 특정 필드만 수정하는 **점진적 업데이트**입니다. 전체 `datasetProperties` aspect를 전송하는 대신 patch는 변경 사항만 전송합니다.

### Patch vs 전체 업데이트

**전체 업데이트 (V1 스타일):**

```java
// Fetch entire aspect
DatasetProperties props = getDatasetProperties(urn);

// Modify one field
props.setDescription("New description");

// Send entire aspect back (overwrites everything)
sendAspect(urn, props);
```

**Patch 업데이트 (V2 스타일):**

```java
// Send only the change
dataset.setDescription("New description");
client.entities().update(dataset);
// Sends JSON Patch: { "op": "add", "path": "/description", "value": "New description" }
```

### Patches의 이점

1. **효율성** - 변경된 필드만 네트워크로 전송
2. **동시성 안전성** - 동시 변경을 덮어쓸 위험 감소
3. **원자성** - 여러 patches가 함께 적용되거나 전혀 적용되지 않음
4. **대역폭** - 축소된 페이로드 크기

## SDK V2에서 Patches 작동 방식

### Patch 축적 패턴

Entity는 저장 시까지 대기 목록에 patches를 축적합니다:

```java
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .build();

// Each method creates a patch MCP and adds to pendingPatches list
dataset.addTag("pii");              // Patch 1
dataset.addTag("sensitive");        // Patch 2
dataset.addOwner("user", OwnershipType.TECHNICAL_OWNER);  // Patch 3

// Check pending patches
System.out.println("Pending patches: " + dataset.getPendingPatches().size());
// Output: Pending patches: 3

// Emit all patches atomically
client.entities().update(dataset);

// Patches cleared after emission
System.out.println("Pending patches: " + dataset.getPendingPatches().size());
// Output: Pending patches: 0
```

### 내부 동작

```java
// From Dataset.java
public Dataset addTag(@Nonnull String tagUrn) {
    // Create patch using existing patch builder
    GlobalTagsPatchBuilder patch = new GlobalTagsPatchBuilder()
        .urn(getUrn())
        .addTag(tag, null);

    // Add to pending patches list
    addPatchMcp(patch.build());

    return this;
}
```

`update()`가 호출되면:

```java
// From EntityClient.java
public void upsert(Entity entity) {
    if (entity.hasPendingPatches()) {
        // Emit patches
        for (MetadataChangeProposal patchMcp : entity.getPendingPatches()) {
            emitter.emit(patchMcp, null);
        }
        entity.clearPendingPatches();
    } else {
        // No patches, emit full aspects
        for (MetadataChangeProposalWrapper mcp : entity.toMCPs()) {
            emitter.emit(mcp);
        }
    }
}
```

## 기존 Patch 빌더 재사용

SDK V2는 `datahub.client.patch` 패키지의 **기존 patch 빌더를 재사용**합니다:

### 사용 가능한 Patch 빌더

| 빌더                                 | 목적                    | 예제                                   |
| --------------------------------------- | -------------------------- | ----------------------------------------- |
| `OwnershipPatchBuilder`                 | 소유자 추가/제거          | `addOwner()`, `removeOwner()`             |
| `GlobalTagsPatchBuilder`                | 태그 추가/제거            | `addTag()`, `removeTag()`                 |
| `GlossaryTermsPatchBuilder`             | 용어 추가/제거           | `addTerm()`, `removeTerm()`               |
| `DomainsPatchBuilder`                   | 도메인 설정/제거          | `setDomain()`, `removeDomain()`           |
| `DatasetPropertiesPatchBuilder`         | 속성 업데이트          | `setDescription()`, `addCustomProperty()` |
| `EditableDatasetPropertiesPatchBuilder` | 편집 가능한 속성 업데이트 | `setEditableDescription()`                |

### 왜 재사용하나요?

- **검증됨** - Python SDK V2에서 프로덕션으로 사용
- **정확성** - 복잡한 JSON Patch 로직 이미 검증됨
- **일관성** - 언어별 SDK 전체에서 동일한 의미론
- **유지보수성** - 유지관리할 단일 구현

## Patches를 사용할 때

### Patches 사용 케이스:

✅ **기존 entity에 대한 점진적 변경**

```java
Dataset dataset = client.entities().get(urn);
dataset.addTag("new-tag");
client.entities().update(dataset);  // Patch
```

✅ **entity에 메타데이터 추가**

```java
dataset.addOwner("urn:li:corpuser:new_owner", OwnershipType.TECHNICAL_OWNER);
dataset.addCustomProperty("updated_at", String.valueOf(System.currentTimeMillis()));
client.entities().update(dataset);  // Multiple patches
```

✅ **전체 entity 지식 없이 수술적 업데이트**

```java
// Don't need to fetch entire entity
dataset.addTag("gdpr");
client.entities().update(dataset);  // Just adds tag
```

### 전체 Upsert 사용 케이스:

✅ **새 entity 생성**

```java
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .description("New dataset")
    .build();

client.entities().upsert(dataset);  // Full upsert
```

✅ **전체 aspect 교체**

```java
// Set complete schema
SchemaMetadata schema = buildCompleteSchema();
dataset.setSchema(schema);
client.entities().upsert(dataset);  // Sends full schema aspect
```

✅ **빌더 제공 메타데이터**

```java
Dataset dataset = Dataset.builder()
    .platform("postgres")
    .name("my_table")
    .description("Description from builder")
    .build();

// Builder populates aspectCache with full aspects
client.entities().upsert(dataset);  // Sends cached aspects
```

## Entity별 Patch 작업

### Dataset Patches

**소유권:**

```java
dataset.addOwner("urn:li:corpuser:john", OwnershipType.TECHNICAL_OWNER);
dataset.removeOwner("urn:li:corpuser:jane");
```

**태그:**

```java
dataset.addTag("pii");
dataset.removeTag("deprecated");
```

**Glossary Terms:**

```java
dataset.addTerm("urn:li:glossaryTerm:CustomerData");
dataset.removeTerm("urn:li:glossaryTerm:OldTerm");
```

**도메인:**

```java
dataset.setDomain("urn:li:domain:Marketing");
dataset.removeDomain();
```

**속성:**

```java
dataset.addCustomProperty("team", "data-eng");
dataset.removeCustomProperty("old_property");
dataset.setDescription("New description");
```

### Chart Patches

Chart는 Dataset과 동일한 patch 작업을 지원합니다:

```java
chart.addOwner("urn:li:corpuser:analyst", OwnershipType.TECHNICAL_OWNER);
chart.addTag("visualization");
chart.addTerm("urn:li:glossaryTerm:SalesMetrics");
chart.setDomain("urn:li:domain:BusinessIntelligence");
```

자세한 내용은 [Chart Entity 가이드](./chart-entity.md)를 참조하세요.

## 고급: 수동 Patch 구성

고급 사용 사례의 경우 직접 patches를 구성하세요:

```java
import com.linkedin.metadata.aspect.patch.builder.OwnershipPatchBuilder;
import com.linkedin.common.urn.Urn;

// Manual patch construction
OwnershipPatchBuilder patchBuilder = new OwnershipPatchBuilder()
    .urn(dataset.getUrn())
    .addOwner(
        Urn.createFromString("urn:li:corpuser:alice"),
        OwnershipType.DATA_STEWARD
    );

MetadataChangeProposal patch = patchBuilder.build();

// Add to entity's pending patches
dataset.addPatchMcp(patch);

// Or emit directly
emitter.emit(patch, null);
```

## Patch vs Upsert 결정 트리

```
빌더에서 새 entity인가요?
├─ 예 → upsert() 사용 (캐시된 aspect 전송)
└─ 아니요 → 서버에서 로드되거나 참조인가요?
    ├─ 예 → 점진적 변경을 만드나요?
    │   ├─ 예 → update() 사용 (patches 전송)
    │   └─ 아니요 → 전체 aspect를 교체하나요?
    │       └─ 예 → upsert() 사용 (전체 aspect 전송)
    └─ 아니요 → 그냥 태그/소유자 등을 추가하나요?
        └─ 예 → update() 사용 (patches 전송)
```

## 대기 중인 Patches 관리

### 대기 중인 Patches 확인

```java
if (dataset.hasPendingPatches()) {
    System.out.println("Entity has pending patches");
}
```

### 대기 중인 Patches 가져오기

```java
List<MetadataChangeProposal> patches = dataset.getPendingPatches();
for (MetadataChangeProposal patch : patches) {
    System.out.println("Patch for aspect: " + patch.getAspectName());
}
```

### 대기 중인 Patches 지우기

```java
// Manually clear without emitting
dataset.clearPendingPatches();
```

### 여러 변경 사항 배치

```java
// Accumulate many patches
dataset.addTag("tag1")
       .addTag("tag2")
       .addTag("tag3")
       .addOwner("user1", OwnershipType.TECHNICAL_OWNER)
       .addOwner("user2", OwnershipType.DATA_STEWARD)
       .addCustomProperty("key1", "value1")
       .addCustomProperty("key2", "value2");

// All 7 patches emitted in single update() call
client.entities().update(dataset);
```

## 성능 고려사항

### 네트워크 효율성

```java
// Inefficient: 3 separate network calls
dataset.addTag("tag1");
client.entities().update(dataset);
dataset.addTag("tag2");
client.entities().update(dataset);
dataset.addTag("tag3");
client.entities().update(dataset);

// Efficient: 1 network call with 3 patches
dataset.addTag("tag1")
       .addTag("tag2")
       .addTag("tag3");
client.entities().update(dataset);
```

### 페이로드 크기

**전체 upsert (datasetProperties):**

- 일반적인 dataset aspect의 경우 ~2-5 KB

**Patch (태그 추가):**

- 단일 태그 patch의 경우 ~200-300 바이트

**태그 10개:** Patches = ~3 KB, 전체 upsert = ~5 KB

## JSON Patch 형식

Patches는 [JSON Patch (RFC 6902)](https://datatracker.ietf.org/doc/html/rfc6902) 형식을 사용합니다:

**추가 작업:**

```json
{
  "op": "add",
  "path": "/tags/urn:li:tag:pii",
  "value": {
    "tag": "urn:li:tag:pii"
  }
}
```

**제거 작업:**

```json
{
  "op": "remove",
  "path": "/tags/urn:li:tag:deprecated"
}
```

SDK V2는 이 복잡성을 추상화합니다 - JSON이 아닌 Java 메서드로 작업합니다.

## 문제 해결

### Patches가 적용되지 않음

**문제:** DataHub에서 변경 사항이 보이지 않음

**해결 방법:**

- `update()`가 호출되었는지 확인 (patches는 자동으로 emit되지 않음)
- emission 응답에서 오류 확인
- entity가 클라이언트에 바인딩되어 있는지 확인

### 동시 업데이트

**문제:** Patches가 동시 변경과 충돌

**해결 방법:**

- Patches는 일반적으로 동시 업데이트에 안전함
- 각 patch는 원자적
- 복잡한 시나리오의 경우 최신 상태를 얻기 위해 먼저 entity 로드

### Patch가 예기치 않게 지워짐

**문제:** 대기 중인 patches가 사라짐

**이유:** `upsert()` 또는 `update()`가 emission 후 patches를 지움

**해결책:** 이것은 예상된 동작입니다 - patches는 일회용

## 다음 단계

- **[설계 원칙](./design-principles.md)** - patches 뒤의 아키텍처
- **[Dataset Entity 가이드](./dataset-entity.md)** - dataset을 위한 모든 patch 작업
- **[마이그레이션 가이드](./migration-from-v1.md)** - 전체 업데이트에서 patches로 이동

## API 참조

주요 클래스:

- Entity.java - Patch 축적
- EntityClient.java - Patch emission
- datahub.client.patch.\* - Patch 빌더
