# Java SDK V2 시작하기

이 가이드는 DataHub Java SDK V2를 설정하고 사용하여 DataHub의 메타데이터 플랫폼과 상호작용하는 방법을 안내합니다.

## 사전 요구사항

- Java 8 이상
- DataHub 인스턴스에 대한 접근 권한 (Cloud 또는 자체 호스팅)
- (선택 사항) 인증을 위한 DataHub 개인 액세스 토큰

## 설치

프로젝트의 빌드 구성에 DataHub 클라이언트 라이브러리를 추가하세요.

### Gradle

`build.gradle`에 추가:

```gradle
dependencies {
    implementation 'io.acryl:datahub-client:__version__'
}
```

### Maven

`pom.xml`에 추가:

```xml
<dependency>
    <groupId>io.acryl</groupId>
    <artifactId>datahub-client</artifactId>
    <version>__version__</version>
</dependency>
```

> **팁:** [Maven Central](https://mvnrepository.com/artifact/io.acryl/datahub-client)에서 최신 버전을 확인하세요.

## 클라이언트 생성

`DataHubClientV2`는 모든 SDK 작업의 진입점입니다. DataHub 서버 URL을 지정하여 생성하세요:

```java
import datahub.client.v2.DataHubClientV2;

DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .build();
```

### 인증 포함

DataHub Cloud 또는 보안이 적용된 인스턴스의 경우 개인 액세스 토큰을 제공하세요:

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("https://your-instance.acryl.io")
    .token("your-personal-access-token")
    .build();
```

> **토큰 발급 방법:** DataHub UI에서 설정 → 액세스 토큰 → 개인 액세스 토큰 생성으로 이동하세요

### 연결 테스트

클라이언트가 DataHub 서버에 접근할 수 있는지 확인하세요:

```java
try {
    boolean connected = client.testConnection();
    if (connected) {
        System.out.println("Successfully connected to DataHub!");
    } else {
        System.out.println("Failed to connect to DataHub");
    }
} catch (Exception e) {
    System.err.println("Connection error: " + e.getMessage());
}
```

## 첫 번째 Entity 생성

메타데이터와 함께 dataset을 생성해 봅시다.

### 1단계: 필요한 클래스 임포트

```java
import datahub.client.v2.DataHubClientV2;
import datahub.client.v2.entity.Dataset;
import com.linkedin.common.OwnershipType;
```

### 2단계: Dataset 빌드

플루언트 빌더를 사용하여 dataset을 구성하세요:

```java
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("analytics.public.user_events")
    .env("PROD")
    .description("User interaction events from web and mobile")
    .displayName("User Events")
    .build();
```

**빌더 파라미터 설명:**

- `platform` - 데이터 플랫폼 식별자 (예: "snowflake", "bigquery", "postgres")
- `name` - 완전 정규화된 dataset 이름 (database.schema.table 또는 유사한 형식)
- `env` - 환경 (PROD, DEV, STAGING 등)
- `description` - dataset에 대한 사람이 읽을 수 있는 설명
- `displayName` - DataHub UI에 표시되는 친숙한 이름

### 3단계: 메타데이터 추가

태그, 소유자 및 커스텀 속성으로 dataset을 풍부하게 만드세요:

```java
dataset.addTag("pii")
       .addTag("analytics")
       .addOwner("urn:li:corpuser:john_doe", OwnershipType.TECHNICAL_OWNER)
       .addCustomProperty("retention_days", "90")
       .addCustomProperty("team", "data-engineering");
```

### 4단계: DataHub에 Upsert

dataset을 DataHub에 전송하세요:

```java
try {
    client.entities().upsert(dataset);
    System.out.println("Successfully created dataset: " + dataset.getUrn());
} catch (IOException | ExecutionException | InterruptedException e) {
    System.err.println("Failed to create dataset: " + e.getMessage());
}
```

## 완전한 예제

다음은 완전하고 실행 가능한 예제입니다:

```java
import datahub.client.v2.DataHubClientV2;
import datahub.client.v2.entity.Dataset;
import com.linkedin.common.OwnershipType;
import java.io.IOException;
import java.util.concurrent.ExecutionException;

public class DataHubQuickStart {
    public static void main(String[] args) {
        // Create client
        DataHubClientV2 client = DataHubClientV2.builder()
            .server("http://localhost:8080")
            .token("your-token-here")  // Optional
            .build();

        try {
            // Test connection
            if (!client.testConnection()) {
                System.err.println("Cannot connect to DataHub");
                return;
            }

            // Build dataset
            Dataset dataset = Dataset.builder()
                .platform("snowflake")
                .name("analytics.public.user_events")
                .env("PROD")
                .description("User interaction events")
                .displayName("User Events")
                .build();

            // Add metadata
            dataset.addTag("pii")
                   .addTag("analytics")
                   .addOwner("urn:li:corpuser:datateam", OwnershipType.TECHNICAL_OWNER)
                   .addCustomProperty("retention_days", "90");

            // Upsert to DataHub
            client.entities().upsert(dataset);
            System.out.println("Created dataset: " + dataset.getUrn());

        } catch (IOException | ExecutionException | InterruptedException e) {
            e.printStackTrace();
        } finally {
            try {
                client.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
```

더 완전한 예제는 [Dataset Entity 가이드](./dataset-entity.md#examples)를 참조하세요.

## Entities 읽기

DataHub에서 기존 entity를 로드하세요:

```java
import com.linkedin.common.urn.DatasetUrn;

DatasetUrn urn = new DatasetUrn(
    "snowflake",
    "analytics.public.user_events",
    "PROD"
);

try {
    Dataset loaded = client.entities().get(urn);
    if (loaded != null) {
        System.out.println("Dataset description: " + loaded.getDescription());
        System.out.println("Is read-only: " + loaded.isReadOnly());  // true
    }
} catch (IOException | ExecutionException | InterruptedException e) {
    e.printStackTrace();
}
```

> **중요:** 서버에서 가져온 entity는 **기본적으로 읽기 전용**입니다. 추가 aspect는 필요에 따라 지연 로딩됩니다.

### 읽기 전용 Entity 이해하기

DataHub에서 entity를 가져오면 우발적인 수정을 방지하기 위해 불변 상태가 됩니다:

```java
Dataset dataset = client.entities().get(urn);

// Reading works fine
String description = dataset.getDescription();
List<String> tags = dataset.getTags();

// But mutation throws ReadOnlyEntityException
// dataset.addTag("pii");  // ERROR: Cannot mutate read-only entity!
```

**왜 그런가요?** 기본적인 불변성은 변경 의도를 명시적으로 만들고, 함수 간에 entity를 전달할 때 우발적인 변경을 방지하며, entity 공유를 안전하게 활성화합니다.

## Patches로 Entities 업데이트

가져온 entity를 수정하려면 먼저 변경 가능한 복사본을 만드세요:

```java
// 1. Load existing dataset (read-only)
Dataset dataset = client.entities().get(urn);

// 2. Get mutable copy
Dataset mutable = dataset.mutable();

// 3. Add new tags and owners (patch operations)
mutable.addTag("gdpr")
       .addOwner("urn:li:corpuser:new_owner", OwnershipType.TECHNICAL_OWNER);

// 4. Apply patches to DataHub
client.entities().update(mutable);
```

`update()` 메서드는 전체 entity가 아닌 변경 사항(patches)만 DataHub에 전송합니다. 이는 더 효율적이며 동시 업데이트에 더 안전합니다.

### Entity 수명 주기

entity가 변경 가능한 상태와 읽기 전용 상태인 경우 이해하기:

**빌더로 생성된 entity** - 생성 시 변경 가능:

```java
Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .build();

dataset.isMutable();  // true - can mutate immediately
dataset.addTag("test");  // Works without .mutable()
```

**서버에서 가져온 entity** - 기본적으로 읽기 전용:

```java
Dataset dataset = client.entities().get(urn);

dataset.isReadOnly();  // true
// dataset.addTag("test");  // ERROR!

Dataset mutable = dataset.mutable();  // Get writable copy
mutable.addTag("test");  // Now works
```

자세한 내용은 [Patch 작업 가이드](./patch-operations.md)를 참조하세요.

## Upserting vs Updating

SDK V2는 entity를 지속하기 위한 두 가지 메서드를 제공합니다:

### `upsert(entity)`

- **용도:** 새 entity 또는 전체 교체
- **전송:** entity의 모든 aspect
- **동작:** 존재하지 않으면 생성, 존재하면 교체

```java
client.entities().upsert(dataset);
```

### `update(entity)`

- **용도:** 기존 entity에 대한 점진적 변경
- **전송:** entity가 로드되거나 생성된 이후 축적된 대기 중인 patches만
- **동작:** 특정 필드에 대한 수술적 업데이트 적용

```java
client.entities().update(dataset);
```

## 다른 Entities 작업

SDK V2는 dataset 외에도 여러 entity 타입을 지원합니다:

### Charts

```java
import datahub.client.v2.entity.Chart;

Chart chart = Chart.builder()
    .tool("looker")
    .id("my_sales_chart")
    .title("Sales Performance by Region")
    .description("Monthly sales broken down by geographic region")
    .build();

client.entities().upsert(chart);
```

자세한 내용은 [Chart Entity 가이드](./chart-entity.md)를 참조하세요.

### Dashboards

출시 예정! Dashboard entity 지원은 향후 릴리스에서 계획되어 있습니다.

## 구성 옵션

환경에 맞게 클라이언트를 커스터마이징하세요:

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("https://your-instance.acryl.io")
    .token("your-access-token")

    // Configure operation mode
    .operationMode(DataHubClientConfigV2.OperationMode.SDK)  // or INGESTION

    // Customize underlying REST emitter
    .restEmitterConfig(config -> config
        .timeoutSec(30)
        .maxRetries(5)
        .retryIntervalSec(2)
    )

    .build();
```

### 작업 모드

SDK V2는 두 가지 작업 모드를 지원합니다:

- **SDK 모드** (기본값): 대화형 애플리케이션용, patch 기반 업데이트 및 지연 로딩 제공
- **INGESTION 모드**: ETL 파이프라인용, 고처리량 배치 작업에 최적화

```java
// SDK mode (default) - interactive use
DataHubClientV2 sdkClient = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .operationMode(DataHubClientConfigV2.OperationMode.SDK)
    .build();

// Ingestion mode - ETL pipelines
DataHubClientV2 ingestionClient = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .operationMode(DataHubClientConfigV2.OperationMode.INGESTION)
    .build();
```

모든 사용 가능한 옵션은 [DataHubClientV2 구성](./client.md)을 참조하세요.

## 오류 처리

오류를 우아하게 처리하세요:

```java
try {
    client.entities().upsert(dataset);
} catch (IOException e) {
    // Network or serialization errors
    System.err.println("I/O error: " + e.getMessage());
} catch (ExecutionException e) {
    // Server-side errors
    System.err.println("Server error: " + e.getCause().getMessage());
} catch (InterruptedException e) {
    // Operation cancelled
    Thread.currentThread().interrupt();
}
```

## 리소스 관리

리소스를 해제하기 위해 완료되면 항상 클라이언트를 닫으세요:

```java
try (DataHubClientV2 client = DataHubClientV2.builder()
        .server("http://localhost:8080")
        .build()) {

    // Use client here
    client.entities().upsert(dataset);

} // Client automatically closed
```

또는 명시적으로 닫으세요:

```java
try {
    // Use client
} finally {
    client.close();
}
```

## 다음 단계

첫 번째 entity를 생성했으니 더 고급 주제를 탐색해 보세요:

- **[설계 원칙](./design-principles.md)** - SDK V2의 아키텍처 이해
- **[Dataset Entity 가이드](./dataset-entity.md)** - 포괄적인 dataset 작업
- **[Chart Entity 가이드](./chart-entity.md)** - chart entity 작업
- **[Patch 작업](./patch-operations.md)** - 점진적 업데이트에 대한 심층 분석
- **[클라이언트 구성](./client.md)** - 고급 클라이언트 설정 및 옵션

또는 entity 가이드의 완전한 예제를 확인하세요:

- [Dataset 예제](./dataset-entity.md#examples)
- [Chart 예제](./chart-entity.md#examples)
- [Dashboard 예제](./dashboard-entity.md#examples)
- [DataJob 예제](./datajob-entity.md#examples)
