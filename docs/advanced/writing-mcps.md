# MCP를 파일로 저장하기

## MCP란 무엇인가?

`MetadataChangeProposal`(MCP)은 DataHub 메타데이터 그래프에서 변경의 원자적 단위를 나타냅니다. 각 MCP는 페이로드에 단일 aspect를 전달하며 DataHub의 메타데이터에 변경을 제안하는 데 사용됩니다.

- 단일 aspect 변경을 나타냅니다.
- DataHub에 메타데이터 변경을 제안하는 데 사용됩니다.
- 메타데이터 수집의 기본 빌딩 블록 역할을 합니다.

자세한 내용은 [DataHub 메타데이터 이벤트](../what/mxe.md) 및 [MCP](mcp-mcl.md) 가이드를 참조하세요.

## 왜 MCP를 파일로 쓰는가?

JSON 파일 형식의 MCP는 DataHub에서 가장 낮고 가장 세분화된 이벤트 형식을 나타내기 때문에 특히 가치가 있습니다. 이전에 저장된 MCP 파일을 사용하는 두 가지 주요 사용 사례가 있습니다:

### 테스트

MCP를 사용하면 메타데이터를 쉽게 수집할 수 있습니다. 다음이 가능합니다:

- 수집 커넥터에 대한 의존성 없이 간단한 명령으로 entity 수집에 사용할 수 있습니다:
  ```bash
  datahub ingest mcps <file_name>.json
  ```
- 메타데이터 수집을 위한 재현 가능한 테스트 케이스를 만들 수 있습니다.
- DataHub에 기여할 때 테스트를 작성하고 실행할 수 있습니다(자세한 내용은 DataHub 테스팅 가이드를 참조하세요).

### 디버깅

MCP는 다음을 할 수 있기 때문에 디버깅에 유용합니다:

- DataHub 인스턴스의 entity를 세분화된 수준에서 검사할 수 있습니다.
- 분석을 위해 기존 entity를 MCP 파일로 내보낼 수 있습니다.
- 수집 전 entity 구조와 관계를 확인할 수 있습니다.

예를 들어, DataHub 인스턴스에서 entity의 구조를 이해하려면 MCP 파일로 내보내고 그 내용을 자세히 검사할 수 있습니다.

## MCP를 파일로 저장하기

### 수집 소스에서 내보내기

레시피에서 `file` 싱크 타입을 사용하여 수집 소스(BigQuery, Snowflake 등)에서 파일로 MCP를 내보낼 수 있습니다. 이 접근 방식은 다음과 같은 경우에 유용합니다:

- 나중에 수집하기 위해 MCP 저장
- 소스에서 기존 entity 검사
- 수집 문제 디버깅

시작하려면 대상 소스와 파일 `sink` 타입을 지정하는 레시피 파일(예: `export_mcps.yaml`)을 만드세요:

```yaml
source:
  type: bigquery # 소스 타입으로 교체하세요
  config: ... # 소스 설정을 여기에 추가하세요
sink:
  type: "file"
  config:
    filename: "mcps.json"
```

다음 명령으로 수집을 실행하세요:

```python
datahub ingest -c export_mcps.yaml
```

이 명령은 소스에서 모든 entity를 추출하고 MCP 형식으로 `mcps.json`에 씁니다.

`file` 싱크 타입에 대한 자세한 내용은 [메타데이터 파일](../../metadata-ingestion/sink_docs/metadata-file.md)을 참조하세요.

### DataHub 인스턴스에서 내보내기

유사한 레시피 접근 방식을 사용하여 기존 DataHub 인스턴스에서 직접 MCP를 내보낼 수도 있습니다. 이 방법은 다음과 같은 경우에 특히 유용합니다:

- DataHub 인스턴스에 이미 있는 entity 검사
- 실제 데이터를 기반으로 테스트 케이스 만들기
- entity 관계 디버깅

프로세스는 수집 소스에서 내보내는 것과 유사하며, 유일한 차이점은 소스 타입으로 `datahub`를 사용한다는 것입니다.
다음 설정으로 레시피 파일(예: `export_mcps.yaml`)을 만드세요:

```yaml
source:
  type: datahub
  config:
    # DataHub 연결 설정을 여기에 추가하세요
    server: "http://localhost:8080"
    token: "your-access-token" # 인증이 필요한 경우

sink:
  type: "file"
  config:
    filename: "mcps.json"
```

수집을 실행하세요:

```python
datahub ingest -c export_mcps.yaml
```

이렇게 하면 DataHub 인스턴스에서 모든 entity를 추출하고 MCP 형식으로 `mcps.json`에 저장합니다.

### Python SDK로 MCP 만들기

`write_metadata_file` 헬퍼를 사용하여 프로그래밍 방식으로 MCP를 생성할 수 있습니다:

```python
from datahub.ingestion.sink.file import write_metadata_file
from pathlib import Path
from datahub.metadata.schema_classes import DatasetPropertiesClass
from datahub.emitter.mcp import MetadataChangeProposalWrapper

records = [
    MetadataChangeProposalWrapper(
        entityType="dataset",
        entityUrn="urn:li:dataset:(urn:li:dataPlatform:hive,example_dataset,PROD)",
        changeType="UPSERT",
        aspectName="datasetProperties",
        aspect=DatasetPropertiesClass(
            description="Example dataset description",
            customProperties={"encoding": "utf-8"}
        ))

]
write_metadata_file(
    file=Path("mcps.json"),
    records=records,
)
```

필요에 맞는 이벤트와 entity를 만들기 위해 `records`를 편집하세요.

Python 스크립트를 실행하여 정의된 MCP를 생성하고 파일에 저장하세요:

```bash
python <file_name>.py
```

예를 들어, 위 스크립트는 단일 dataset entity가 포함된 MCP 파일을 생성합니다.

```json
[
  {
    "entityType": "dataset",
    "entityUrn": "urn:li:dataset:(urn:li:dataPlatform:hive,example_dataset,PROD)",
    "changeType": "UPSERT",
    "aspectName": "datasetProperties",
    "aspect": {
      "json": {
        "customProperties": {
          "encoding": "utf-8"
        },
        "description": "Example dataset description",
        "tags": []
      }
    }
  }
]
```
