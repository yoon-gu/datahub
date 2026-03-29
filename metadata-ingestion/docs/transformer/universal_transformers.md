---
title: "Universal transformers"
---

# Transformers

아래 표는 해당 aspect를 가진 모든 entity의 aspect를 변환할 수 있는 transformer를 보여줍니다.

| Aspect          | Transformer                           |
| --------------- | ------------------------------------- |
| `browsePathsV2` | - [Set browsePaths](#set-browsepaths) |

## Set browsePaths

이 transformer는 `browsePathsV2` aspect에서 작동합니다. ingestion 소스에서 내보내지 않은 경우 transformer가 생성합니다. 기본적으로 설정된 경로를 원래 경로 앞에 추가합니다 (접두사로 추가합니다).

### Config 세부 사항

| Field              | Required | Type         | Default | Description                                                                                         |
| ------------------ | -------- | ------------ | ------- | --------------------------------------------------------------------------------------------------- |
| `path`             | ✅       | list[string] |         | 새 경로의 노드 목록.                                                                                |
| `replace_existing` |          | boolean      | `false` | 기존 browse path를 덮어쓸지 여부. `false`로 설정하면 설정된 경로가 앞에 추가됩니다.               |

가장 기본적인 경우 `path`에는 정적 문자열 목록이 포함됩니다. 예를 들어 아래 config는:

```yaml
transformers:
  - type: "set_browse_path"
    config:
      path:
        - abc
        - def
```

모든 entity가 `abc`와 `def` 노드가 접두사로 붙은 경로를 갖게 됩니다 (`def`는 `abc` 내에 포함됩니다).

### Variable substitution

transformer에는 경로의 변수 치환 메커니즘이 있습니다. 변수 목록은 entity의 기존 `browsePathsV2` aspect를 기반으로 구성됩니다. 기존 경로의 모든 _노드_가 다른 entity(예: `container` 또는 `dataPlatformInstance`)에 대한 참조를 포함하는 한 사용할 변수 목록에 저장됩니다. 동일한 타입의 entity(예: `containers`)에 대한 여러 참조가 browse path에 있을 수 있으므로, 원래 순서를 유지하면서 목록 형태의 객체에 저장됩니다. 실제 상황의 예를 살펴보겠습니다. Snowflake 소스에서 수집된 테이블이 있고 `platform_instance`가 일부 값으로 설정된 경우, 해당 테이블은 다음 참조를 포함하는 `browsePathsV2` aspect를 갖게 됩니다:

```yaml
- urn:li:dataPlatformInstance:(urn:li:dataPlatform:snowflake,my_platform_instance)
- urn:li:container:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
- urn:li:container:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
```

여기서 `urn:li:container:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`는 Snowflake의 _데이터베이스_를 나타내는 `container`를 식별하고,
`urn:li:container:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`는 Snowflake의 _스키마_를 나타내는 `container`를 식별합니다.
기존 경로는 아래와 같이 변수로 매핑됩니다:

```python
dataPlatformInstance[0] = "urn:li:dataPlatformInstance:(urn:li:dataPlatform:snowflake,my_platform_instance)"
container[0] = "urn:li:container:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
container[1] = "urn:li:container:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
```

이 변수들은 아래와 같이 config에서 `$` 문자를 사용하여 참조할 수 있습니다:

```yaml
transformers:
  - type: "set_browse_path"
    config:
      path:
        - $dataPlatformInstance[0]
        - $container[0]
        - $container[1]
```

추가로 변수 해석에 다음 2가지 규칙이 적용됩니다:

- 변수가 존재하지 않는 경우(또는 인덱스가 목록 길이를 벗어나는 경우) 무시되고 경로에서 사용되지 않으며, 다른 모든 노드는 사용되고 경로가 수정됩니다.
- `$variable[*]`는 변수의 전체 목록을 경로의 여러 _노드_로 확장합니다 (flat map으로 생각하면 됩니다). 예를 들어, 위 config와 동일한 효과를 내는 설정은:
  ```yaml
  transformers:
    - type: "set_browse_path"
      config:
        path:
          - $dataPlatformInstance[0]
          - $container[*]
  ```

### 예제

소스에서 내보낸 경로에 최상위 노드 "datahub"를 추가(접두사):

```yaml
transformers:
  - type: "set_browse_path"
    config:
      path:
        - datahub
```

container 구조를 유지하면서 경로에서 data platform instance를 제거(설정된 경우):

```yaml
transformers:
  - type: "set_browse_path"
    config:
      replace_existing: true
      path:
        - $container[*]
```
