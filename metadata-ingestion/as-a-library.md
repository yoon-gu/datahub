# Python Emitter

경우에 따라 메타데이터 이벤트를 직접 구성하고 프로그래밍 방식으로 DataHub에 메타데이터를 내보내고 싶을 수 있습니다. 주로 push 기반의 사용 사례로, CI/CD pipeline, 커스텀 오케스트레이터 등에서 메타데이터 이벤트를 내보내는 경우가 포함됩니다.

`acryl-datahub` Python 패키지는 REST 및 Kafka emitter API를 제공하며, 자신의 코드에서 쉽게 가져와 호출할 수 있습니다.

> **Pro Tip!** API 가이드 전반에 걸쳐 Python API SDK 사용 예시가 있습니다.
> 튜토리얼 내의 `| Python |` 탭을 확인하세요.

## 설치

`acryl-datahub` 패키지의 설치 가이드는 [여기](./README.md#install-from-pypi)를 참조하세요. emitter별 설치 방법은 계속 읽어보세요.

## REST Emitter

REST emitter는 `requests` 모듈 위에 얇은 래퍼로, HTTP를 통해 메타데이터 이벤트를 전송하기 위한 블로킹 인터페이스를 제공합니다. 메타데이터 내보내기의 처리량보다 단순성과 DataHub 메타데이터 저장소에 메타데이터가 저장되었는지 확인이 더 중요한 경우에 사용하세요. 메타데이터를 쓰고 즉시 읽는 등의 읽기-쓰기 시나리오가 있는 경우에도 사용하세요.

### 설치

```console
pip install -U `acryl-datahub[datahub-rest]`
```

### 사용 예시

```python
import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.schema_classes import DatasetPropertiesClass

from datahub.emitter.rest_emitter import DatahubRestEmitter

# REST를 통해 DataHub에 연결하는 emitter 생성
emitter = DatahubRestEmitter(gms_server="http://localhost:8080", extra_headers={})

# DataHub Cloud의 경우, DataHub Cloud 서버의 GMS 엔드포인트를 가리켜야 합니다
# emitter = DatahubRestEmitter(gms_server="https://<your-domain>.acryl.io/gms", token="<your token>", extra_headers={})

# 연결 테스트
emitter.test_connection()

# dataset 속성 객체 구성
dataset_properties = DatasetPropertiesClass(description="This table stored the canonical User profile",
    customProperties={
         "governance": "ENABLED"
    })

# MetadataChangeProposalWrapper 객체 구성
metadata_event = MetadataChangeProposalWrapper(
    entityUrn=builder.make_dataset_urn("bigquery", "my-project.my-dataset.user-table"),
    aspect=dataset_properties,
)

# 메타데이터 내보내기! 블로킹 호출입니다
emitter.emit(metadata_event)
```

기타 예시:

- [lineage_emitter_mcpw_rest.py](./examples/library/lineage_emitter_mcpw_rest.py) - MetadataChangeProposalWrapper로 REST를 통해 간단한 bigquery 테이블 간(dataset 간) lineage를 내보냅니다.

### Emitter 코드

REST emitter 코드에 관심이 있다면 [여기](./src/datahub/emitter/rest_emitter.py)에서 확인할 수 있습니다.

## Kafka Emitter

Kafka emitter는 `confluent-kafka`의 SerializingProducer 클래스 위에 얇은 래퍼로, DataHub에 메타데이터 이벤트를 전송하기 위한 비블로킹 인터페이스를 제공합니다. Kafka를 고가용성 메시지 버스로 활용하여 메타데이터 프로듀서를 DataHub 메타데이터 서버의 가동 시간에서 분리하고 싶을 때 사용하세요. 예를 들어 계획된 또는 예상치 못한 중단으로 DataHub 메타데이터 서비스가 다운된 경우에도 Kafka로 전송하여 미션 크리티컬 시스템에서 계속 메타데이터를 수집할 수 있습니다. 또한 메타데이터가 DataHub 백엔드 저장소에 저장되었는지 확인보다 메타데이터 내보내기의 처리량이 더 중요한 경우에도 이 emitter를 사용하세요.

**_참고_**: Kafka emitter는 Avro를 사용하여 메타데이터 이벤트를 Kafka로 직렬화합니다. DataHub는 현재 Kafka를 통한 메타데이터 이벤트가 Avro로 직렬화될 것으로 예상하므로 직렬화기를 변경하면 처리할 수 없는 이벤트가 발생합니다.

### 설치

```console
# Kafka를 통한 내보내기
pip install -U `acryl-datahub[datahub-kafka]`
```

### 사용 예시

```python
import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.schema_classes import DatasetPropertiesClass

from datahub.emitter.kafka_emitter import DatahubKafkaEmitter, KafkaEmitterConfig
# Kafka에 연결하는 emitter 생성
kafka_config = {
    "connection": {
        "bootstrap": "localhost:9092",
        "schema_registry_url": "http://localhost:8081",
        "schema_registry_config": {}, # 하위 schema registry 클라이언트에 전달되는 schema_registry 구성
        "producer_config": {}, # 하위 kafka 프로듀서에 전달되는 추가 프로듀서 구성
    }
}

emitter = DatahubKafkaEmitter(
    KafkaEmitterConfig.parse_obj(kafka_config)
)

# dataset 속성 객체 구성
dataset_properties = DatasetPropertiesClass(description="This table stored the canonical User profile",
    customProperties={
         "governance": "ENABLED"
    })

# MetadataChangeProposalWrapper 객체 구성
metadata_event = MetadataChangeProposalWrapper(
    entityUrn=builder.make_dataset_urn("bigquery", "my-project.my-dataset.user-table"),
    aspect=dataset_properties,
)


# 메타데이터 내보내기! 비블로킹 호출입니다
emitter.emit(
    metadata_event,
    callback=lambda exc, message: print(f"Message sent to topic:{message.topic()}, partition:{message.partition()}, offset:{message.offset()}") if message else print(f"Failed to send with: {exc}")
)

# 모든 보류 중인 이벤트 전송
emitter.flush()
```

### Emitter 코드

Kafka emitter 코드에 관심이 있다면 [여기](./src/datahub/emitter/kafka_emitter.py)에서 확인할 수 있습니다.

## 다른 언어

Emitter API는 다음 언어에서도 지원됩니다:

- [Java](../metadata-integration/java/as-a-library.md)
