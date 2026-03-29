# DataHubClientV2 구성

`DataHubClientV2`는 SDK V2를 사용하여 DataHub와 상호작용하기 위한 주요 진입점입니다. 이 가이드는 클라이언트 구성, 연결 관리 및 작업 모드를 다룹니다.

## 클라이언트 생성

### 기본 구성

최소 구성은 서버 URL만 필요합니다:

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

> **토큰 발급:** DataHub UI → 설정 → 액세스 토큰 → 개인 액세스 토큰 생성

### 환경 변수에서 구성

환경 변수를 사용하여 클라이언트를 구성하세요:

```bash
export DATAHUB_SERVER=http://localhost:8080
export DATAHUB_TOKEN=your-token-here
```

```java
DataHubClientConfig V2 config = DataHubClientConfigV2.fromEnv();
DataHubClientV2 client = new DataHubClientV2(config);
```

**지원되는 환경 변수:**

- `DATAHUB_SERVER` 또는 `DATAHUB_GMS_URL` - 서버 URL (필수)
- `DATAHUB_TOKEN` 또는 `DATAHUB_GMS_TOKEN` - 인증 토큰 (선택 사항)

## 구성 옵션

### 타임아웃

느린 네트워크를 처리하기 위한 요청 타임아웃 구성:

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .timeoutMs(30000)  // 30 seconds
    .build();
```

**기본값:** 10초 (10000ms)

### 재시도

실패한 요청에 대한 자동 재시도 구성:

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .maxRetries(5)  // Retry up to 5 times
    .build();
```

**기본값:** 3회 재시도

### SSL 인증서 검증

테스트 환경에서는 SSL 검증을 비활성화할 수 있습니다:

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("https://localhost:8443")
    .disableSslVerification(true)  // WARNING: Only for testing!
    .build();
```

> **경고:** 프로덕션에서는 SSL 검증을 절대 비활성화하지 마세요! 이렇게 하면 중간자 공격에 취약해집니다.

## 작업 모드

SDK V2는 DataHub에 메타데이터가 기록되는 방식을 제어하는 두 가지 작업 모드를 지원합니다:

### SDK 모드 (기본값)

**사용 목적:** 대화형 애플리케이션, 사용자 주도 메타데이터 편집, 실시간 UI 업데이트

**동작:**

- **편집 가능한 aspect**에 쓰기 (예: `editableDatasetProperties`)
- 즉각적인 일관성을 위해 **동기 DB 쓰기** 사용
- 메타데이터가 데이터베이스에 커밋된 후에만 반환

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .operationMode(DataHubClientConfigV2.OperationMode.SDK)  // Default
    .build();

Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .build();

dataset.setDescription("User-provided description");
client.entities().upsert(dataset);
// Writes to editableDatasetProperties synchronously
// Metadata immediately visible after return
```

### INGESTION 모드

**사용 목적:** ETL 파이프라인, 데이터 ingestion 작업, 자동화된 메타데이터 수집, 배치 처리

**동작:**

- **시스템 aspect**에 쓰기 (예: `datasetProperties`)
- 높은 처리량을 위해 **비동기 Kafka 쓰기** 사용
- 메시지가 큐에 추가된 후 즉시 반환

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .operationMode(DataHubClientConfigV2.OperationMode.INGESTION)
    .build();

Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .build();

dataset.setDescription("Ingested from Snowflake");
client.entities().upsert(dataset);
// Writes to datasetProperties asynchronously via Kafka
// High throughput for batch ingestion
```

### 모드 비교

| Aspect              | SDK 모드                    | INGESTION 모드                   |
| ------------------- | --------------------------- | -------------------------------- |
| **대상 Aspect**  | 편집 가능한 aspect            | 시스템 aspect                   |
| **쓰기 경로**      | 동기 (DB 직접)  | 비동기 (Kafka를 통해)         |
| **일관성**     | 즉각적 (선형화 가능)    | 최종적 (비동기 처리)      |
| **처리량**      | 낮음 (DB 대기)        | 높음 (큐)                  |
| **사용 사례**        | UI/API를 통한 사용자 편집       | 파이프라인 메타데이터 추출     |
| **우선순위**      | 높음 (시스템 재정의)   | 낮음 (사용자 편집에 의해 재정의됨) |
| **예시 Aspect** | `editableDatasetProperties` | `datasetProperties`              |
| **지연 시간**         | ~100-500ms                  | ~10-50ms (큐잉만)         |
| **오류 처리**  | 즉각적 피드백          | 최종적 (로그 확인)            |

**왜 두 가지 모드인가요?**

- **명확한 출처**: 사람의 편집과 기계 생성 메타데이터 구분
- **비파괴적 업데이트**: Ingestion이 사용자 문서를 덮어쓰지 않고 새로 고침 가능
- **UI 일관성**: DataHub UI가 편집 가능한 aspect를 사용자 재정의로 표시
- **성능 최적화**: 고볼륨 배치 쓰기를 위한 비동기 ingestion, 대화형 편집을 위한 동기

## 비동기 모드 제어 (탈출구)

기본적으로 비동기 모드는 작업 모드에서 자동으로 추론됩니다:

- SDK 모드 → 동기 쓰기 (즉각적 일관성)
- INGESTION 모드 → 비동기 쓰기 (높은 처리량)

그러나 완전한 제어가 필요할 때 `asyncIngest` 파라미터를 사용하여 이 동작을 명시적으로 재정의할 수 있습니다:

### INGESTION 모드에서 동기 강제

즉각적인 일관성 보장이 필요한 파이프라인의 경우:

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .operationMode(DataHubClientConfigV2.OperationMode.INGESTION)
    .asyncIngest(false)  // Override: force synchronous despite INGESTION mode
    .build();

Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .build();

dataset.setDescription("Ingested description");
client.entities().upsert(dataset);
// Writes to datasetProperties synchronously, waits for DB commit
// Use when you need guaranteed consistency before proceeding
```

**사용 사례:**

- 쓰기 성공을 반드시 확인해야 하는 중요 ingestion 작업
- 각 단계가 이전 쓰기에 의존하는 순차적 처리
- 결정론적 동작이 필요한 테스트 시나리오
- 감사 추적 확인이 필요한 컴플라이언스 워크플로

### SDK 모드에서 비동기 강제

최종적 일관성을 허용하는 고볼륨 SDK 작업의 경우:

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .operationMode(DataHubClientConfigV2.OperationMode.SDK)
    .asyncIngest(true)  // Override: force async despite SDK mode
    .build();

Dataset dataset = Dataset.builder()
    .platform("snowflake")
    .name("my_table")
    .build();

dataset.setDescription("User-provided description");
client.entities().upsert(dataset);
// Writes to editableDatasetProperties via Kafka for higher throughput
// Trade immediate consistency for performance
```

**사용 사례:**

- 관리 도구에서의 대량 메타데이터 업데이트
- 대량의 데이터를 이동하는 마이그레이션 스크립트
- 성능이 중요한 배치 작업
- 부하 테스트 및 벤치마킹

### 결정 가이드

| 시나리오                | 작업 모드 | asyncIngest | 결과                           |
| ----------------------- | -------------- | ----------- | -------------------------------- |
| 웹 UI에서 사용자 편집    | SDK            | (기본값)   | 편집 가능한 aspect에 동기 쓰기  |
| ETL 파이프라인 ingestion  | INGESTION      | (기본값)   | 시스템 aspect에 비동기 쓰기   |
| 중요 데이터 마이그레이션 | INGESTION      | false       | 시스템 aspect에 동기 쓰기    |
| 대량 관리 업데이트      | SDK            | true        | 편집 가능한 aspect에 비동기 쓰기 |

**기본 동작은 95%의 사용 사례에 최적입니다.** 특정 성능이나 일관성 요구 사항이 있을 때만 명시적인 `asyncIngest`를 사용하세요.

## 연결 테스트

작업을 수행하기 전에 연결을 확인하세요:

```java
try {
    boolean connected = client.testConnection();
    if (connected) {
        System.out.println("Connected to DataHub!");
    } else {
        System.err.println("Failed to connect");
    }
} catch (Exception e) {
    System.err.println("Connection error: " + e.getMessage());
}
```

`testConnection()` 메서드는 서버가 접근 가능한지 확인하기 위해 `/config` 엔드포인트에 GET 요청을 수행합니다.

## 클라이언트 수명 주기

### 리소스 관리

클라이언트는 자동 리소스 관리를 위해 `AutoCloseable`을 구현합니다:

```java
try (DataHubClientV2 client = DataHubClientV2.builder()
        .server("http://localhost:8080")
        .build()) {

    // Use client
    client.entities().upsert(dataset);

} // Client automatically closed
```

### 수동 닫기

try-with-resources를 사용하지 않는 경우 명시적으로 클라이언트를 닫으세요:

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    .build();

try {
    // Use client
} finally {
    client.close();  // Release HTTP connections
}
```

**왜 닫아야 하나요?** 클라이언트를 닫으면 기본 HTTP 연결 풀이 해제됩니다.

## 고급 구성

### 완전한 구성 예제

```java
import datahub.client.v2.DataHubClientV2;
import datahub.client.v2.config.DataHubClientConfigV2;

DataHubClientV2 client = DataHubClientV2.builder()
    // Server configuration
    .server("https://your-instance.acryl.io")
    .token("your-personal-access-token")

    // Timeout configuration
    .timeoutMs(30000)  // 30 seconds

    // Retry configuration
    .maxRetries(5)

    // Operation mode (SDK or INGESTION)
    .operationMode(DataHubClientConfigV2.OperationMode.SDK)

    // Async mode control (optional - overrides mode-based default)
    // .asyncIngest(false)  // Explicit control: true=async, false=sync

    // SSL configuration (testing only!)
    .disableSslVerification(false)

    .build();
```

### 기본 RestEmitter 접근

고급 사용 사례의 경우 저수준 REST emitter에 접근하세요:

```java
RestEmitter emitter = client.getEmitter();
// Direct access to emission methods
```

> **참고:** 대부분의 사용자는 고수준 `client.entities()` API를 사용해야 합니다.

## Entity 작업

구성이 완료되면 클라이언트를 사용하여 entity 작업을 수행하세요:

### CRUD 작업

```java
// Create/Update (upsert)
client.entities().upsert(dataset);

// Update with patches
client.entities().update(dataset);

// Read
Dataset loaded = client.entities().get(datasetUrn);
```

포괄적인 예제는 [시작하기 가이드](./getting-started.md)를 참조하세요.

## 구성 모범 사례

### 프로덕션 배포

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server(System.getenv("DATAHUB_SERVER"))
    .token(System.getenv("DATAHUB_TOKEN"))
    .timeoutMs(30000)       // Higher timeout for production
    .maxRetries(5)          // More retries for reliability
    .operationMode(DataHubClientConfigV2.OperationMode.SDK)
    .disableSslVerification(false)  // Always verify SSL!
    .build();
```

### ETL 파이프라인

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server(System.getenv("DATAHUB_SERVER"))
    .token(System.getenv("DATAHUB_TOKEN"))
    .timeoutMs(60000)       // Higher timeout for batch jobs
    .maxRetries(3)
    .operationMode(DataHubClientConfigV2.OperationMode.INGESTION)  // Async by default
    .build();
```

### 중요 데이터 마이그레이션

진행하기 전에 확인이 필요한 마이그레이션의 경우:

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server(System.getenv("DATAHUB_SERVER"))
    .token(System.getenv("DATAHUB_TOKEN"))
    .timeoutMs(60000)
    .maxRetries(5)
    .operationMode(DataHubClientConfigV2.OperationMode.INGESTION)
    .asyncIngest(false)     // Force sync for guaranteed consistency
    .build();
```

### 로컬 개발

```java
DataHubClientV2 client = DataHubClientV2.builder()
    .server("http://localhost:8080")
    // No token needed for local quickstart
    .timeoutMs(10000)
    .build();
```

## 문제 해결

### 연결 거부

**오류:** `java.net.ConnectException: Connection refused`

**해결 방법:**

- DataHub 서버가 실행 중인지 확인
- 서버 URL이 올바른지 확인
- 포트가 접근 가능한지 확인 (방화벽 규칙)

### 인증 실패

**오류:** `401 Unauthorized`

**해결 방법:**

- 토큰이 유효하고 만료되지 않았는지 확인
- 토큰에 올바른 권한이 있는지 확인
- 토큰이 서버 환경과 일치하는지 확인

### 타임아웃

**오류:** `java.util.concurrent.TimeoutException`

**해결 방법:**

- `timeoutMs` 구성 증가
- DataHub 서버에 대한 네트워크 지연 시간 확인
- 서버가 과부하되지 않았는지 확인

### SSL 인증서 오류

**오류:** `javax.net.ssl.SSLHandshakeException`

**해결 방법:**

- 서버 SSL 인증서가 유효한지 확인
- Java 트러스트스토어에 CA 인증서 추가
- 테스트 전용: `disableSslVerification(true)` 사용

## 다음 단계

- **[Entities 개요](./entities-overview.md)** - 다양한 entity 타입 작업
- **[Dataset Entity 가이드](./dataset-entity.md)** - 포괄적인 dataset 작업
- **[Patch 작업](./patch-operations.md)** - 효율적인 점진적 업데이트
- **[시작하기 가이드](./getting-started.md)** - 완전한 안내

## API 참조

완전한 API 문서는 다음을 참조하세요:

- [DataHubClientV2.java](../../datahub-client/src/main/java/datahub/client/v2/DataHubClientV2.java)
- [DataHubClientConfigV2.java](../../datahub-client/src/main/java/datahub/client/v2/config/DataHubClientConfigV2.java)
