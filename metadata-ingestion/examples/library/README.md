# DataHub Library Examples

이 디렉토리에는 DataHub Python SDK 및 메타데이터 내보내기 API 사용 방법을 보여주는 예제가 포함되어 있습니다.

## 구조

각 예제는 특정 사용 사례를 보여주는 독립적인 Python 스크립트입니다:

- **Create 예제**: 새 메타데이터 entity를 생성하는 방법
- **Update 예제**: 기존 메타데이터를 수정하는 방법
- **Query 예제**: 메타데이터를 읽고 쿼리하는 방법
- **Delete 예제**: 메타데이터를 제거하는 방법

## 테스트 가능한 예제 작성

예제를 유지 관리 가능하고 올바르게 유지하기 위해 새 예제를 작성할 때 이 패턴을 따르세요:

### 패턴 개요

예제에는 두 가지 주요 구성 요소가 있어야 합니다:

1. **테스트 가능한 함수**: 의존성을 매개변수로 받아 값/메타데이터를 반환하는 순수 함수
2. **Main 함수**: 의존성을 생성하고 테스트 가능한 함수를 호출하는 진입점

### 예제 구조

```python
from typing import Optional
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter


def create_entity_metadata(...) -> MetadataChangeProposalWrapper:
    """
    Create metadata for an entity.

    This function is pure and testable - it doesn't have side effects.

    Args:
        ... (all required parameters)

    Returns:
        MetadataChangeProposalWrapper containing the metadata
    """
    # Build and return the MCP
    return MetadataChangeProposalWrapper(...)


def main(emitter: Optional[DatahubRestEmitter] = None) -> None:
    """
    Main function demonstrating the example use case.

    Args:
        emitter: Optional emitter for testing. If not provided, creates a new one.
    """
    emitter = emitter or DatahubRestEmitter(gms_server="http://localhost:8080")

    # Use the testable function
    mcp = create_entity_metadata(...)

    # Emit the metadata
    emitter.emit(mcp)
    print(f"Successfully created entity")


if __name__ == "__main__":
    main()
```

### SDK 기반 예제의 경우

DataHub SDK(`DataHubClient`)를 사용할 때:

```python
from typing import Optional
from datahub.sdk import DataHubClient


def perform_operation(client: DataHubClient, ...) -> ...:
    """
    Perform an operation using the DataHub client.

    Args:
        client: DataHub client to use
        ...: Other parameters

    Returns:
        Result of the operation
    """
    # Perform the operation
    return result


def main(client: Optional[DataHubClient] = None) -> None:
    """
    Main function demonstrating the example use case.

    Args:
        client: Optional client for testing. If not provided, creates one from env.
    """
    client = client or DataHubClient.from_env()

    result = perform_operation(client, ...)
    print(f"Operation result: {result}")


if __name__ == "__main__":
    main()
```

### 이 패턴의 장점

1. **테스트 가능성**: 실행 중인 DataHub 인스턴스 없이도 핵심 로직을 단위 테스트할 수 있습니다.
2. **재사용성**: 테스트 가능한 함수를 다른 코드에서 가져와 사용할 수 있습니다.
3. **명확성**: 비즈니스 로직과 인프라 설정을 분리합니다.
4. **유연성**: 예제를 독립 실행형으로 실행할 수 있으면서도 테스트 가능합니다.

### 예제 실행

**독립 스크립트로 실행:**

```bash
python examples/library/notebook_create.py
```

**테스트에서 실행:**

```python
from examples.library.create_notebook import create_notebook_metadata

# Unit test
mcp = create_notebook_metadata(...)
assert mcp.entityUrn == "..."

# Integration test
from examples.library.create_notebook import main
main(emitter=test_emitter)  # Inject test emitter
```

## 테스트

예제는 두 가지 수준에서 테스트됩니다:

### 단위 테스트

`tests/unit/test_library_examples.py`에 위치:

- 예제가 컴파일되고 import가 해결되는지 테스트
- 핵심 함수가 유효한 메타데이터 구조를 생성하는지 테스트
- 실제 DataHub 인스턴스 없이도 동작하도록 mocking 사용
- 빠르고 모든 커밋 시 실행됩니다.

### 통합 테스트

`tests/integration/library_examples/`에 위치:

- 실제 DataHub 인스턴스에 대해 예제 테스트
- 쓰기 후 읽기를 포함한 end-to-end 기능 검증
- 메타데이터가 올바르게 유지되고 조회 가능한지 테스트
- 느리고 덜 자주 실행될 수 있습니다.

### 테스트 실행

```bash
# Run all example tests (unit only)
pytest tests/unit/test_library_examples.py

# Run specific unit tests
pytest tests/unit/test_library_examples.py::test_create_notebook_metadata

# Run integration tests (requires running DataHub)
pytest tests/integration/library_examples/ -m integration

# Run all tests
pytest tests/unit/test_library_examples.py tests/integration/library_examples/
```

## 가이드라인

1. **예제를 단순하게 유지**: 하나의 개념을 명확하게 시연하는 데 집중
2. **현실적인 데이터 사용**: URN, 이름, 값은 실제 사용 사례처럼 보여야 합니다.
3. **주석 추가**: 명확하지 않은 선택이나 중요한 세부 사항을 설명합니다.
4. **패턴 따르기**: 테스트 가능한 함수 + main() 패턴 사용
5. **매개변수 문서화**: 타입 힌트가 있는 명확한 docstring 사용
6. **오류 처리**: 관련 있는 경우 적절한 오류 처리 방법 제시
7. **예제 테스트**: 새 예제에 대한 단위 테스트 추가

## 예제 카테고리

### Entity 생성

- `notebook_create.py` - notebook entity 생성
- `data_platform_create.py` - 커스텀 데이터 플랫폼 생성
- `glossary_term_create.py` - glossary terms 생성

### 메타데이터 업데이트

- `dataset_add_term.py` - dataset에 glossary terms 추가
- `dataset_add_owner.py` - 소유권 정보 추가
- `notebook_add_tags.py` - notebook에 태그 추가

### 메타데이터 쿼리

- `dataset_query_deprecation.py` - dataset이 deprecated인지 확인
- `search_with_query.py` - entity 검색
- `lineage_column_get.py` - 컬럼 수준 lineage 쿼리

## 도움 받기

- [DataHub 문서](https://datahubproject.io/docs/)
- [Python SDK 참조](https://datahubproject.io/docs/python-sdk/)
- [메타데이터 모델](https://datahubproject.io/docs/metadata-model/)
- [GitHub Issues](https://github.com/datahub-project/datahub/issues)
