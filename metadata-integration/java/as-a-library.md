# Java Emitter

> **참고:** 이 문서는 메타데이터 이벤트를 위한 저수준 emitter를 제공하는 Java SDK V1을 설명합니다.
>
> 새 프로젝트에서는 **[Java SDK V2](./as-a-library-v2.md)** 사용을 권장합니다. V2는 다음을 제공합니다:
>
> - 플루언트 API를 갖춘 타입 안전 entity 빌더
> - 단순화된 CRUD 작업
> - 효율적인 메타데이터 관리를 위한 patch 기반 업데이트
> - DataHub의 entity 모델과의 더 나은 통합
>
> V1에서 V2로 전환하는 방법은 [마이그레이션 가이드](./docs/sdk-v2/migration-from-v1.md)를 참조하세요.

경우에 따라 Metadata 이벤트를 직접 구성하고 프로그래밍 방식으로 DataHub에 해당 메타데이터를 emit하고 싶을 수 있습니다. 이런 사용 사례는 일반적으로 푸시 기반이며, CI/CD 파이프라인이나 커스텀 오케스트레이터 등에서 메타데이터 이벤트를 emit하는 것을 포함합니다.

[`io.acryl:datahub-client`](https://mvnrepository.com/artifact/io.acryl/datahub-client) Java 패키지는 REST emitter API를 제공하며, JVM 기반 시스템에서 메타데이터를 쉽게 emit하는 데 사용할 수 있습니다. 예를 들어, Spark lineage 통합은 Java emitter를 사용하여 Spark 작업에서 메타데이터 이벤트를 emit합니다.

> **프로 팁!** API 가이드 전반에 걸쳐 Java API SDK 사용 예제가 있습니다.
> 튜토리얼 내 `| Java |` 탭을 확인하세요.

## 설치

빌드 시스템에 맞는 지침에 따라 적절한 버전의 패키지에 대한 의존성을 선언하세요.

**_참고_**: 아래 지침을 따르기 전에 [Maven 저장소](https://mvnrepository.com/artifact/io.acryl/datahub-client)에서 최신 버전을 확인하세요.

### Gradle

`build.gradle`에 다음을 추가하세요.

```gradle
implementation 'io.acryl:datahub-client:__version__'
```

### Maven

`pom.xml`에 다음을 추가하세요.

```xml
<!-- https://mvnrepository.com/artifact/io.acryl/datahub-client -->
<dependency>
    <groupId>io.acryl</groupId>
    <artifactId>datahub-client</artifactId>
    <!-- replace __version__ with the latest version number -->
    <version>__version__</version>
</dependency>
```

## REST Emitter

REST emitter는 [`Apache HttpClient`](https://hc.apache.org/httpcomponents-client-4.5.x/index.html) 라이브러리의 얇은 래퍼입니다. 메타데이터의 비블로킹 emission을 지원하며, 네트워크를 통한 메타데이터 aspect의 JSON 직렬화를 처리합니다.

REST Emitter 구성은 람다 기반의 플루언트 빌더 패턴을 따릅니다. 설정 파라미터는 대부분 Python emitter [설정](../../metadata-ingestion/sink_docs/datahub.md#config-details)과 동일합니다. 또한, HttpClient 빌더에 커스터마이징을 전달하여 내부적으로 생성되는 HttpClient를 직접 구성할 수도 있습니다.

```java
import datahub.client.rest.RestEmitter;
//...
RestEmitter emitter = RestEmitter.create(b -> b
                                              .server("http://localhost:8080")
//Auth token for DataHub Cloud              .token(AUTH_TOKEN_IF_NEEDED)
//Override default timeout of 10 seconds      .timeoutSec(OVERRIDE_DEFAULT_TIMEOUT_IN_SECONDS)
//Add additional headers                      .extraHeaders(Collections.singletonMap("Session-token", "MY_SESSION"))
// Customize HttpClient's connection ttl      .customizeHttpAsyncClient(c -> c.setConnectionTimeToLive(30, TimeUnit.SECONDS))
                                    );
```

### 사용법

```java
import com.linkedin.dataset.DatasetProperties;
import com.linkedin.events.metadata.ChangeType;
import datahub.event.MetadataChangeProposalWrapper;
import datahub.client.rest.RestEmitter;
import datahub.client.Callback;
// ... followed by

// Creates the emitter with the default coordinates and settings
RestEmitter emitter = RestEmitter.createWithDefaults();

MetadataChangeProposalWrapper mcpw = MetadataChangeProposalWrapper.builder()
        .entityType("dataset")
        .entityUrn("urn:li:dataset:(urn:li:dataPlatform:bigquery,my-project.my-dataset.user-table,PROD)")
        .upsert()
        .aspect(new DatasetProperties().setDescription("This is the canonical User profile dataset"))
        .build();

// Blocking call using Future.get()
MetadataWriteResponse requestFuture = emitter.emit(mcpw, null).get();

// Non-blocking using callback
emitter.emit(mcpw, new Callback() {
      @Override
      public void onCompletion(MetadataWriteResponse response) {
        if (response.isSuccess()) {
          System.out.println(String.format("Successfully emitted metadata event for %s", mcpw.getEntityUrn()));
        } else {
          // Get the underlying http response
          HttpResponse httpResponse = (HttpResponse) response.getUnderlyingResponse();
          System.out.println(String.format("Failed to emit metadata event for %s, aspect: %s with status code: %d",
              mcpw.getEntityUrn(), mcpw.getAspectName(), httpResponse.getStatusLine().getStatusCode()));
          // Print the server side exception if it was captured
          if (response.getServerException() != null) {
            System.out.println(String.format("Server side exception was %s", response.getServerException()));
          }
        }
      }

      @Override
      public void onFailure(Throwable exception) {
        System.out.println(
            String.format("Failed to emit metadata event for %s, aspect: %s due to %s", mcpw.getEntityUrn(),
                mcpw.getAspectName(), exception.getMessage()));
      }
    });
```

### REST Emitter 코드

REST emitter 코드에 관심이 있다면 [여기](./datahub-client/src/main/java/datahub/client/rest/RestEmitter.java)에서 확인할 수 있습니다.

## Kafka Emitter

Kafka emitter는 `confluent-kafka`의 SerializingProducer 클래스의 얇은 래퍼로, DataHub에 메타데이터 이벤트를 전송하기 위한 비블로킹 인터페이스를 제공합니다. Kafka를 고가용성 메시지 버스로 활용하여 메타데이터 프로듀서를 DataHub 메타데이터 서버의 가동 시간으로부터 분리하고 싶을 때 사용하세요. 예를 들어, 계획된 또는 예기치 않은 중단으로 인해 DataHub 메타데이터 서비스가 다운된 경우에도 Kafka로 전송하여 중요 시스템에서 메타데이터를 계속 수집할 수 있습니다. 또한, 메타데이터 emission의 처리량이 DataHub 백엔드 저장소에 대한 메타데이터 지속성 확인보다 중요할 때도 이 emitter를 사용하세요.

**_참고_**: Kafka emitter는 Avro를 사용하여 메타데이터 이벤트를 Kafka로 직렬화합니다. 직렬화기를 변경하면 DataHub가 현재 Kafka를 통한 메타데이터 이벤트를 Avro로 직렬화된 형태로 기대하기 때문에 처리할 수 없는 이벤트가 생성됩니다.

### 사용법

```java


import java.io.IOException;
import java.util.concurrent.ExecutionException;
import com.linkedin.dataset.DatasetProperties;
import datahub.client.kafka.KafkaEmitter;
import datahub.client.kafka.KafkaEmitterConfig;
import datahub.event.MetadataChangeProposalWrapper;

// ... followed by

// Creates the emitter with the default coordinates and settings
KafkaEmitterConfig.KafkaEmitterConfigBuilder builder = KafkaEmitterConfig.builder(); KafkaEmitterConfig config = builder.build();
KafkaEmitter emitter = new KafkaEmitter(config);

//Test if topic is available

if(emitter.testConnection()){

	MetadataChangeProposalWrapper mcpw = MetadataChangeProposalWrapper.builder()
	        .entityType("dataset")
	        .entityUrn("urn:li:dataset:(urn:li:dataPlatform:bigquery,my-project.my-dataset.user-table,PROD)")
	        .upsert()
	        .aspect(new DatasetProperties().setDescription("This is the canonical User profile dataset"))
	        .build();

	// Blocking call using future
	Future<MetadataWriteResponse> requestFuture = emitter.emit(mcpw, null).get();

	// Non-blocking using callback
	emitter.emit(mcpw, new Callback() {

	      @Override
	      public void onFailure(Throwable exception) {
	        System.out.println("Failed to send with: " + exception);
	      }
	      @Override
	      public void onCompletion(MetadataWriteResponse metadataWriteResponse) {
	        if (metadataWriteResponse.isSuccess()) {
	          RecordMetadata metadata = (RecordMetadata) metadataWriteResponse.getUnderlyingResponse();
	          System.out.println("Sent successfully over topic: " + metadata.topic());
	        } else {
	          System.out.println("Failed to send with: " + metadataWriteResponse.getUnderlyingResponse());
	        }
	      }
	    });

}
else {
	System.out.println("Kafka service is down.");
}
```

### Kafka Emitter 코드

Kafka emitter 코드에 관심이 있다면 [여기](./datahub-client/src/main/java/datahub/client/kafka/KafkaEmitter.java)에서 확인할 수 있습니다.

## File Emitter

File emitter는 메타데이터 변경 제안 이벤트(MCP)를 JSON 파일에 기록하며, 나중에 Python [Metadata File source](docs/generated/ingestion/sources/metadata-file.md)에 전달하여 ingestion할 수 있습니다. 이는 Python의 [Metadata File sink](../../metadata-ingestion/sink_docs/metadata-file.md)와 유사하게 동작합니다. 메타데이터 이벤트를 생성하는 시스템이 DataHub의 REST 서버나 Kafka 브로커에 직접 연결할 수 없을 때 이 메커니즘을 사용할 수 있습니다. 생성된 JSON 파일은 나중에 전송되어 [Metadata File source](docs/generated/ingestion/sources/metadata-file.md)를 사용하여 DataHub에 ingestion할 수 있습니다.

### 사용법

```java


import datahub.client.file.FileEmitter;
import datahub.client.file.FileEmitterConfig;
import datahub.event.MetadataChangeProposalWrapper;

// ... followed by


// Define output file co-ordinates
String outputFile = "/my/path/output.json";

//Create File Emitter
FileEmitter emitter = new FileEmitter(FileEmitterConfig.builder().fileName(outputFile).build());

// A couple of sample metadata events
MetadataChangeProposalWrapper mcpwOne = MetadataChangeProposalWrapper.builder()
        .entityType("dataset")
        .entityUrn("urn:li:dataset:(urn:li:dataPlatform:bigquery,my-project.my-dataset.user-table,PROD)")
        .upsert()
        .aspect(new DatasetProperties().setDescription("This is the canonical User profile dataset"))
        .build();

MetadataChangeProposalWrapper mcpwTwo = MetadataChangeProposalWrapper.builder()
        .entityType("dataset")
        .entityUrn("urn:li:dataset:(urn:li:dataPlatform:bigquery,my-project.my-dataset.fact-orders-table,PROD)")
        .upsert()
        .aspect(new DatasetProperties().setDescription("This is the canonical Fact table for orders"))
        .build();

MetadataChangeProposalWrapper[] mcpws = { mcpwOne, mcpwTwo };
for (MetadataChangeProposalWrapper mcpw : mcpws) {
   emitter.emit(mcpw);
}
emitter.close(); // calling close() is important to ensure file gets closed cleanly

```

### File Emitter 코드

File emitter 코드에 관심이 있다면 [여기](./datahub-client/src/main/java/datahub/client/file/FileEmitter.java)에서 확인할 수 있습니다.

### S3, GCS 등 지원

File emitter는 현재 로컬 파일 시스템에 대한 쓰기만 지원합니다. S3, GCS 등의 지원을 추가하는 데 관심이 있다면 기여를 환영합니다!

## 다른 언어

Emitter API는 다음 언어에서도 지원됩니다:

- [Python](../../metadata-ingestion/as-a-library.md)
