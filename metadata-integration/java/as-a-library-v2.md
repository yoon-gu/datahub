# Java SDK V2

DataHub Java SDK V2는 DataHub의 메타데이터 플랫폼과 상호작용하기 위한 현대적이고 타입 안전한 인터페이스를 제공합니다. 기존 DataHub 인프라 위에 구축된 SDK V2는 메타데이터 entity를 생성하고 관리하기 위한 직관적인 플루언트 API를 제공합니다.

## 왜 SDK V2인가?

SDK V2는 [V1 emitter 기반 접근 방식](./as-a-library.md)에서 크게 발전하여 다음을 제공합니다:

### **타입 안전 Entity 빌더**

유효한 entity를 생성하도록 안내하는 플루언트 빌더와 함께 Java의 타입 시스템을 활용하세요. 더 이상 수동으로 URN을 구성하거나 aspect를 연결할 필요가 없습니다.

```java
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_database.my_schema.my_table")
    .env("PROD")
    .description("User profile dataset")
    .build();
```

### **단순화된 CRUD 작업**

깔끔하고 직관적인 API로 생성, 읽기, 업데이트, 삭제 작업을 수행하세요:

```java
client.entities().upsert(dataset);          // Create or update
client.entities().update(dataset);          // Update with patches
Dataset loaded = client.entities().get(urn); // Read from server
```

### **효율적인 Patch 기반 업데이트**

전체 aspect를 가져오거나 교체하지 않고 메타데이터를 점진적으로 변경하세요:

```java
dataset.addTag("pii")
       .addOwner("urn:li:corpuser:john", OwnershipType.TECHNICAL_OWNER)
       .addCustomProperty("team", "data-engineering");

client.entities().update(dataset);  // Applies only the changes
```

### **지연 로딩 및 캐싱**

불필요한 네트워크 호출을 줄이는 내장 TTL 기반 캐싱으로 entity aspect를 필요에 따라 효율적으로 가져옵니다.

### **모드 인식 설계**

사용 사례에 맞게 대화형 SDK 모드와 고처리량 ingestion 모드를 모두 지원합니다.

## 설치

프로젝트에 DataHub 클라이언트 라이브러리를 추가하세요:

### Gradle

```gradle
dependencies {
    implementation 'io.acryl:datahub-client:__version__'
}
```

### Maven

```xml
<dependency>
    <groupId>io.acryl</groupId>
    <artifactId>datahub-client</artifactId>
    <version>__version__</version>
</dependency>
```

> **참고:** 최신 버전은 [Maven 저장소](https://mvnrepository.com/artifact/io.acryl/datahub-client)에서 확인하세요.

## 빠른 시작

다음은 SDK V2를 사용하여 메타데이터와 함께 dataset을 생성하는 전체 예제입니다:

```java
import datahub.client.v2.DataHubClientV2;
import datahub.client.v2.entity.Dataset;
import com.linkedin.common.OwnershipType;

// Create the client
DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .token("your-access-token")  // Optional for authentication
    .build();

// Build a dataset with metadata
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("analytics.public.user_events")
    .env("PROD")
    .description("User interaction events")
    .displayName("User Events")
    .build();

// Add tags and owners
dataset.addTag("pii")
       .addTag("analytics")
       .addOwner("urn:li:corpuser:datateam", OwnershipType.TECHNICAL_OWNER)
       .addCustomProperty("retention", "90_days");

// Upsert to DataHub
client.entities().upsert(dataset);

System.out.println("Created dataset: " + dataset.getUrn());

// Close the client when done
client.close();
```

## 핵심 개념

### Entities

SDK V2는 주요 DataHub entity 타입에 대한 entity 클래스를 제공합니다:

- **Dataset** - 테이블, 뷰 및 기타 데이터 컨테이너
- **Chart** - 시각화 및 보고서
- **Dashboard** - chart 모음 (출시 예정)

각 entity는 메타데이터 관리를 위한 플루언트 빌더와 메서드를 제공합니다.

### 클라이언트 작업

`DataHubClientV2`는 작업에 대한 중앙 집중식 접근을 제공합니다:

- `entities()` - entity에 대한 CRUD 작업
- `testConnection()` - DataHub 서버와의 연결 확인

### Patch 기반 업데이트

전체 aspect를 교체하는 대신, SDK V2는 patch 작업을 사용하여 특정 메타데이터 필드에 대해 수술적 업데이트를 수행합니다. 이는 더 효율적이며 동시 변경 사항을 덮어쓸 위험을 줄입니다.

## 문서

SDK V2 작업을 위한 상세 가이드를 살펴보세요:

- **[시작하기 가이드](./docs/sdk-v2/getting-started.md)** - 인증, 구성, 기본 작업이 포함된 종합 튜토리얼
- **[설계 원칙](./docs/sdk-v2/design-principles.md)** - SDK V2의 아키텍처 개요 및 엔지니어링 원칙
- **[DataHubClientV2](./docs/sdk-v2/client.md)** - 클라이언트 구성, 연결 관리 및 작업 모드
- **[Entities 개요](./docs/sdk-v2/entities-overview.md)** - 모든 entity 타입에 걸친 공통 패턴
- **[Dataset Entity](./docs/sdk-v2/dataset-entity.md)** - dataset 작업에 대한 완전한 가이드
- **[Chart Entity](./docs/sdk-v2/chart-entity.md)** - chart entity 생성 및 관리
- **[Patch 작업](./docs/sdk-v2/patch-operations.md)** - 효율적인 점진적 업데이트에 대한 심층 분석
- **[V1에서 마이그레이션](./docs/sdk-v2/migration-from-v1.md)** - SDK V1에서 업그레이드하기 위한 단계별 가이드

## 예제 코드

[examples 디렉토리](./examples/src/main/java/io/datahubproject/examples/v2/)에서 완전하고 실행 가능한 예제를 찾을 수 있습니다:

- [DatasetCreateExample.java](./examples/src/main/java/io/datahubproject/examples/v2/DatasetCreateExample.java) - 기본 dataset 생성
- [DatasetPatchExample.java](./examples/src/main/java/io/datahubproject/examples/v2/DatasetPatchExample.java) - 태그, 소유자 및 커스텀 속성 추가
- [DatasetFullExample.java](./examples/src/main/java/io/datahubproject/examples/v2/DatasetFullExample.java) - 포괄적인 메타데이터 관리
- [ChartCreateExample.java](./examples/src/main/java/io/datahubproject/examples/v2/ChartCreateExample.java) - Chart entity 생성

## V1과의 비교

| 기능              | V1 (RestEmitter)               | V2 (DataHubClientV2)            |
| ------------------- | ------------------------------ | ------------------------------- |
| **Entity 생성** | 수동 MCP 구성        | 플루언트 entity 빌더          |
| **타입 안전성**     | 낮음 - 수동 aspect 연결     | 높음 - 컴파일 타임 검증  |
| **URN 관리**  | 수동 문자열 구성     | 빌더에서 자동 생성          |
| **업데이트**         | 전체 aspect 교체         | Patch 기반 점진적 업데이트 |
| **API 스타일**       | 저수준 emitter              | 고수준 CRUD 작업      |
| **학습 곡선**  | 가파름 - MCP 지식 필요 | 완만함 - 직관적인 빌더     |

V1에서 V2로 전환하는 방법은 [상세 마이그레이션 가이드](./docs/sdk-v2/migration-from-v1.md)를 참조하세요.

## 지원

질문, 이슈 또는 기여:

- [DataHub GitHub](https://github.com/datahub-project/datahub)
- [DataHub Slack](https://datahub.com/slack)
- [API 튜토리얼](../../docs/api/tutorials) - Java 예제가 포함된 언어 독립적 가이드

## 다음 단계

- **시작하기**: [종합 튜토리얼](./docs/sdk-v2/getting-started.md)을 따라 첫 번째 애플리케이션을 만들어 보세요
- **아키텍처 학습**: SDK V2의 [설계 원칙](./docs/sdk-v2/design-principles.md)을 읽어보세요
- **Entities 탐색**: [Dataset](./docs/sdk-v2/dataset-entity.md) 또는 [Chart](./docs/sdk-v2/chart-entity.md) 가이드를 살펴보세요
- **V1에서 마이그레이션**: [마이그레이션 가이드](./docs/sdk-v2/migration-from-v1.md)를 사용하여 기존 코드를 업그레이드하세요
