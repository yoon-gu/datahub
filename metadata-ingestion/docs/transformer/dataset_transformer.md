---
title: "Dataset"
---

# Dataset Transformers

아래 표는 [Dataset](../../../docs/generated/metamodel/entities/dataset.md) entity의 aspect를 변환할 수 있는 transformer를 보여줍니다.

| Dataset Aspect      | Transformer                                                                                                                                                                                                                                                                                                                                                           |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `status`            | - [Mark Dataset status](#mark-dataset-status)                                                                                                                                                                                                                                                                                                                         |
| `ownership`         | - [Simple Add Dataset ownership](#simple-add-dataset-ownership)<br/> - [Pattern Add Dataset ownership](#pattern-add-dataset-ownership)<br/> - [Simple Remove Dataset Ownership](#simple-remove-dataset-ownership)<br/> - [Extract Ownership from Tags](#extract-ownership-from-tags)<br/> - [Clean suffix prefix from Ownership](#clean-suffix-prefix-from-ownership) |
| `globalTags`        | - [Simple Add Dataset globalTags ](#simple-add-dataset-globaltags)<br/> - [Pattern Add Dataset globalTags](#pattern-add-dataset-globaltags)<br/> - [Add Dataset globalTags](#add-dataset-globaltags)                                                                                                                                                                  |
| `browsePaths`       | - [Set Dataset browsePath](#set-dataset-browsepath)                                                                                                                                                                                                                                                                                                                   |
| `glossaryTerms`     | - [Simple Add Dataset glossaryTerms ](#simple-add-dataset-glossaryterms)<br/> - [Pattern Add Dataset glossaryTerms](#pattern-add-dataset-glossaryterms)<br/> - [Tags to Term Mapping](#tags-to-term-mapping)                                                                                                                                                          |
| `schemaMetadata`    | - [Pattern Add Dataset Schema Field glossaryTerms](#pattern-add-dataset-schema-field-glossaryterms)<br/> - [Pattern Add Dataset Schema Field globalTags](#pattern-add-dataset-schema-field-globaltags)                                                                                                                                                                |
| `datasetProperties` | - [Simple Add Dataset datasetProperties](#simple-add-dataset-datasetproperties)<br/> - [Add Dataset datasetProperties](#add-dataset-datasetproperties)                                                                                                                                                                                                                |
| `domains`           | - [Simple Add Dataset domains](#simple-add-dataset-domains)<br/> - [Pattern Add Dataset domains](#pattern-add-dataset-domains)<br/> - [Domain Mapping Based on Tags](#domain-mapping-based-on-tags)                                                                                                                                                                   |
| `dataProduct`       | - [Simple Add Dataset dataProduct ](#simple-add-dataset-dataproduct)<br/> - [Pattern Add Dataset dataProduct](#pattern-add-dataset-dataproduct)<br/> - [Add Dataset dataProduct](#add-dataset-dataproduct)                                                                                                                                                            |

## Extract Ownership from Tags

### Config 세부 사항

| Field                                 | Required | Type           | Default           | Description                                                                                                                                                                                                                                                                                       |
| ------------------------------------- | -------- | -------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tag_pattern`                         |          | str            |                   | 매칭할 태그에 사용할 Regex. 내용을 제거하는 데 사용되는 패턴을 Regex로 지원합니다. 나머지 문자열은 소유자 URN 생성을 위한 소유자 ID로 간주됩니다.                                                                                                                                               |
| `is_user`                             |          | bool           | `true`            | 사용자로 간주할지 여부. `false`이면 그룹으로 간주됩니다.                                                                                                                                                                                                                                         |
| `tag_character_mapping`               |          | dict[str, str] |                   | 태그 문자를 datahub 소유자 문자로 매핑하는 딕셔너리. 제공된 경우, `tag_pattern` config는 매핑에 따라 변환된 태그에 대해 매칭되어야 합니다.                                                                                                                                                     |
| `email_domain`                        |          | str            |                   | 설정되면 소유자 URN 생성을 위해 추가됩니다.                                                                                                                                                                                                                                                     |
| `extract_owner_type_from_tag_pattern` |          | str            | `false`           | 제공된 태그 패턴의 첫 번째 그룹에서 소유권 타입을 추출할지 여부. `true`이면 owner_type 및 owner_type_urn config를 제공할 필요가 없습니다. 예: 태그 패턴이 `(.*)_owner_email:`이고 실제 태그가 `developer_owner_email`이면, 추출된 소유권 타입은 `developer`가 됩니다.                          |
| `owner_type`                          |          | str            | `TECHNICAL_OWNER` | 소유권 타입.                                                                                                                                                                                                                                                                                     |
| `owner_type_urn`                      |          | str            | `None`            | 커스텀 소유권을 사용하는 경우 커스텀 소유권 타입의 URN으로 설정합니다.                                                                                                                                                                                                                          |

dataset 태그의 일부를 기반으로 dataset 소유권을 추가하려 한다고 가정해 봅시다. 이를 위해 ingestion 프레임워크에 포함된 `extract_ownership_from_tags` transformer를 사용할 수 있습니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다:

```yaml
transformers:
  - type: "extract_ownership_from_tags"
    config:
      tag_pattern: "owner_email:"
```

입력 dataset 태그가 다음과 같다면

- `urn:li:tag:owner_email:abc@email.com`
- `urn:li:tag:owner_email:xyz@email.com`

매칭된 태그 패턴 이후의 태그 부분이 소유자로 변환됩니다. 따라서 사용자 `abc@email.com`과 `xyz@email.com`이 소유자로 추가됩니다.

### 예제

- 소유자를 추가하되, 소유자는 그룹으로 간주하고 태그 문자열에 이메일 도메인이 포함되지 않은 경우. 예: 태그 URN `urn:li:tag:owner:abc`에서 추출된 소유자 URN이 `urn:li:corpGroup:abc@email.com`이어야 한다면 config는 다음과 같습니다:
  ```yaml
  transformers:
    - type: "extract_ownership_from_tags"
      config:
        tag_pattern: "owner:"
        is_user: false
        email_domain: "email.com"
  ```
- 소유자를 추가하되, 소유권 타입과 소유권 타입 URN을 외부에서 제공하려는 경우. 예: 태그 URN `urn:li:tag:owner_email:abc@email.com`에서 소유권 타입이 `CUSTOM`이고 소유권 타입 URN이 `"urn:li:ownershipType:data_product"`이어야 한다면 config는 다음과 같습니다:
  ```yaml
  transformers:
    - type: "extract_ownership_from_tags"
      config:
        tag_pattern: "owner_email:"
        owner_type: "CUSTOM"
        owner_type_urn: "urn:li:ownershipType:data_product"
  ```
- 소유자를 추가하되, 일부 태그 문자를 소유자 추출 전에 다른 문자로 교체해야 하는 경우. 예: 태그 URN `urn:li:tag:owner__email:abc--xyz-email_com`에서 추출된 소유자 URN이 `urn:li:corpGroup:abc.xyz@email.com`이어야 한다면 config는 다음과 같습니다:
  ```yaml
  transformers:
    - type: "extract_ownership_from_tags"
      config:
        tag_pattern: "owner_email:"
        tag_character_mapping:
          "_": "."
          "-": "@"
          "--": "-"
          "__": "_"
  ```
- 소유자를 추가하되, 태그 패턴에서 소유권 타입도 추출해야 하는 경우. 예: 태그 URN `urn:li:tag:data_producer_owner_email:abc@email.com`에서 추출된 소유권 타입이 `data_producer`이어야 한다면 config는 다음과 같습니다:
  ```yaml
  transformers:
    - type: "extract_ownership_from_tags"
      config:
        tag_pattern: "(.*)_owner_email:"
        extract_owner_type_from_tag_pattern: true
  ```

## Clean suffix prefix from Ownership

### Config 세부 사항

| Field                 | Required | Type         | Default | Description                                           |
| --------------------- | -------- | ------------ | ------- | ----------------------------------------------------- |
| `pattern_for_cleanup` | ✅       | list[string] |         | 소유자 URN에서 제거할 접미사/접두사 목록 |

소유자 URN에 매칭하여 URN에서 매칭 부분을 제거합니다.

```yaml
transformers:
  - type: "pattern_cleanup_ownership"
    config:
      pattern_for_cleanup:
        - "ABCDEF"
        - (?<=_)(\w+)
```

## Mark Dataset Status

### Config 세부 사항

| Field     | Required | Type    | Default | Description                                 |
| --------- | -------- | ------- | ------- | ------------------------------------------- |
| `removed` | ✅       | boolean |         | UI에서 dataset 가시성을 제어하는 플래그. |

dataset이 UI에 표시되지 않도록 하려면 dataset의 status를 removed로 표시해야 합니다.

소스 recipe에서 이 transformer를 사용하여 status를 removed로 표시할 수 있습니다.

```yaml
transformers:
  - type: "mark_dataset_status"
    config:
      removed: true
```

## Simple Add Dataset ownership

### Config 세부 사항

| Field              | Required | Type         | Default     | Description                                                                                                |
| ------------------ | -------- | ------------ | ----------- | ---------------------------------------------------------------------------------------------------------- |
| `owner_urns`       | ✅       | list[string] |             | 소유자 URN 목록.                                                                                           |
| `ownership_type`   |          | string       | "DATAOWNER" | 소유자들의 소유권 타입 (enum 또는 소유권 타입 URN으로 지정)                                               |
| `replace_existing` |          | boolean      | `false`     | ingestion 소스에서 전송된 entity의 소유권을 제거할지 여부.                                                 |
| `semantics`        |          | enum         | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.                                                  |
| `on_conflict`      |          | enum         | `DO_UPDATE` | 도메인이 이미 존재하는 경우 변경 여부. DO_NOTHING으로 설정하면 `semantics` 설정은 무관합니다.             |

`replace_existing` 및 `semantics`에 대한 transformer 동작은 [replace_existing과 semantics의 관계](#relationship-between-replace_existing-and-semantics) 섹션을 참고하세요.

<br/>
일반적인 ingestion 중에는 감지되지 않지만 dataset을 소유하고 있는 사용자들을 추가하려 한다고 가정해 봅시다. 이를 위해 ingestion 프레임워크에 포함된 `simple_add_dataset_ownership` transformer를 사용할 수 있습니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다.

아래 config는 ownership aspect에 나열된 owner_urns를 추가합니다.

```yaml
transformers:
  - type: "simple_add_dataset_ownership"
    config:
      owner_urns:
        - "urn:li:corpuser:username1"
        - "urn:li:corpuser:username2"
        - "urn:li:corpGroup:groupname"
      ownership_type: "PRODUCER"
```

`simple_add_dataset_ownership`은 다양한 방식으로 설정할 수 있습니다.

- 소유자를 추가하되, ingestion 소스에서 전송된 기존 소유자를 교체하는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_ownership"
      config:
        replace_existing: true # false가 기본 동작
        owner_urns:
          - "urn:li:corpuser:username1"
          - "urn:li:corpuser:username2"
          - "urn:li:corpGroup:groupname"
        ownership_type: "urn:li:ownershipType:__system__producer"
  ```
- 소유자를 추가하되, DataHub GMS에서 dataset에 사용 가능한 소유자를 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_ownership"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        owner_urns:
          - "urn:li:corpuser:username1"
          - "urn:li:corpuser:username2"
          - "urn:li:corpGroup:groupname"
        ownership_type: "urn:li:ownershipType:__system__producer"
  ```
- 소유자를 추가하되, DataHub GMS에서 dataset에 사용 가능한 소유자를 유지하는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_ownership"
      config:
        semantics: PATCH
        owner_urns:
          - "urn:li:corpuser:username1"
          - "urn:li:corpuser:username2"
          - "urn:li:corpGroup:groupname"
        ownership_type: "PRODUCER"
  ```

## Pattern Add Dataset ownership

### Config 세부 사항

| Field              | Required | Type                 | Default     | Description                                                                                                                  |
| ------------------ | -------- | -------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `owner_pattern`    | ✅       | map[regx, list[urn]] |             | 정규 표현식이 있는 entity URN과 매칭된 entity URN에 적용할 소유자 URN 목록.                                                  |
| `ownership_type`   |          | string               | "DATAOWNER" | 소유자들의 소유권 타입 (enum 또는 소유권 타입 URN으로 지정)                                                                  |
| `replace_existing` |          | boolean              | `false`     | ingestion 소스에서 전송된 entity에서 소유자를 제거할지 여부.                                                                  |
| `semantics`        |          | enum                 | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.                                                                     |
| `is_container`     |          | bool                 | `false`     | container도 함께 고려할지 여부. true이면 dataset과 해당 container 모두에 소유권이 부여됩니다.                                  |
| `on_conflict`      |          | enum                 | `DO_UPDATE` | 도메인이 이미 존재하는 경우 변경 여부. DO_NOTHING으로 설정하면 `semantics` 설정은 무관합니다.                                 |

데이터 소스에서 일반적인 ingestion 중에는 감지되지 않지만 특정 dataset을 소유하고 있는 일련의 사용자들을 추가하려 한다고 가정해 봅시다. 이를 위해 ingestion 프레임워크에 포함된 `pattern_add_dataset_ownership` 모듈을 사용할 수 있습니다. 이 모듈은 패턴을 dataset의 `urn`과 매칭하여 각각의 소유자를 할당합니다.

is_container 필드가 true로 설정되면, 모듈은 매칭된 dataset에 소유권을 연결할 뿐만 아니라 해당 dataset과 관련된 container를 찾아 연결합니다. 즉, dataset과 해당 container 모두 지정된 소유자와 연관됩니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다:

```yaml
transformers:
  - type: "pattern_add_dataset_ownership"
    config:
      owner_pattern:
        rules:
          ".*example1.*": ["urn:li:corpuser:username1"]
          ".*example2.*": ["urn:li:corpuser:username2"]
      ownership_type: "DEVELOPER"
```

`pattern_add_dataset_ownership`은 다양한 방식으로 설정할 수 있습니다.

- 소유자를 추가하되, ingestion 소스에서 전송된 기존 소유자를 교체하는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_ownership"
      config:
        replace_existing: true # false가 기본 동작
        owner_pattern:
          rules:
            ".*example1.*": ["urn:li:corpuser:username1"]
            ".*example2.*": ["urn:li:corpuser:username2"]
        ownership_type: "urn:li:ownershipType:__system__producer"
  ```
- 소유자를 추가하되, DataHub GMS에서 dataset에 사용 가능한 소유자를 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_ownership"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        owner_pattern:
          rules:
            ".*example1.*": ["urn:li:corpuser:username1"]
            ".*example2.*": ["urn:li:corpuser:username2"]
        ownership_type: "urn:li:ownershipType:__system__producer"
  ```
- 소유자를 추가하되, DataHub GMS에서 dataset에 사용 가능한 소유자를 유지하는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_ownership"
      config:
        semantics: PATCH
        owner_pattern:
          rules:
            ".*example1.*": ["urn:li:corpuser:username1"]
            ".*example2.*": ["urn:li:corpuser:username2"]
        ownership_type: "PRODUCER"
  ```
- dataset과 해당 container에 소유자 추가
  ```yaml
  transformers:
    - type: "pattern_add_dataset_ownership"
      config:
        is_container: true
        replace_existing: true # false가 기본 동작
        semantics: PATCH / OVERWRITE # 사용자 선택에 따라
        owner_pattern:
          rules:
            ".*example1.*": ["urn:li:corpuser:username1"]
            ".*example2.*": ["urn:li:corpuser:username2"]
        ownership_type: "PRODUCER"
  ```
  ⚠️ 경고:
  동일한 container에 있는 두 dataset에 서로 다른 소유자가 있는 경우, 해당 dataset container에 모든 소유자가 추가됩니다.

예를 들어:

```yaml
transformers:
  - type: "pattern_add_dataset_ownership"
    config:
      is_container: true
      owner_pattern:
        rules:
          ".*example1.*": ["urn:li:corpuser:username1"]
          ".*example2.*": ["urn:li:corpuser:username2"]
```

example1과 example2가 같은 container에 있다면, urn:li:corpuser:username1과 urn:li:corpuser:username2 모두 각각의 dataset container에 추가됩니다.

## Simple Remove Dataset ownership

ingestion 소스에서 전송된 기존 소유자를 모두 제거하려면 `simple_remove_dataset_ownership` transformer를 사용하면 됩니다.

```yaml
transformers:
  - type: "simple_remove_dataset_ownership"
    config: {}
```

`simple_remove_dataset_ownership`의 주요 사용 사례는 소스에 있는 잘못된 소유자를 제거하는 것입니다. [Simple Add Dataset ownership](#simple-add-dataset-ownership)과 함께 사용하여 잘못된 소유자를 제거하고 올바른 소유자를 추가할 수 있습니다.

`simple_remove_dataset_ownership`을 통해 전송하는 소유자는 UI에 있는 소유자를 덮어씁니다.

## Extract Dataset globalTags

### Config 세부 사항

| Field                | Required | Type    | Default     | Description                                                         |
| -------------------- | -------- | ------- | ----------- | ------------------------------------------------------------------- |
| `extract_tags_from`  | ✅       | string  | `urn`       | 태그를 추출할 필드. 현재는 `urn`만 지원됩니다.                      |
| `extract_tags_regex` | ✅       | string  | `.*`        | 태그 추출에 사용할 Regex.                                           |
| `replace_existing`   |          | boolean | `false`     | ingestion 소스에서 전송된 entity에서 globalTags를 제거할지 여부.    |
| `semantics`          |          | enum    | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.           |

URN의 일부를 기반으로 dataset 태그를 추가하려 한다고 가정해 봅시다. 이를 위해 ingestion 프레임워크에 포함된 `extract_dataset_tags` transformer를 사용할 수 있습니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다:

```yaml
transformers:
  - type: "extract_dataset_tags"
    config:
      extract_tags_from: "urn"
      extract_tags_regex: ".([^._]*)_"
```

입력 URN이 다음과 같다면

- `urn:li:dataset:(urn:li:dataPlatform:kafka,clusterid.USA-ops-team_table1,PROD)`
- `urn:li:dataset:(urn:li:dataPlatform:kafka,clusterid.Canada-marketing_table1,PROD)`

각각 `USA-ops-team`과 `Canada-marketing`이라는 태그가 추가됩니다. 이는 dataset에서 접두사를 사용하여 다양한 항목을 구분하는 경우에 유용합니다. 이제 DataHub에서 해당 구분을 dataset의 태그로 변환하여 추가로 활용할 수 있습니다.

## Simple Add Dataset globalTags

### Config 세부 사항

| Field              | Required | Type         | Default     | Description                                                        |
| ------------------ | -------- | ------------ | ----------- | ------------------------------------------------------------------ |
| `tag_urns`         | ✅       | list[string] |             | globalTags URN 목록.                                               |
| `replace_existing` |          | boolean      | `false`     | ingestion 소스에서 전송된 entity에서 globalTags를 제거할지 여부.   |
| `semantics`        |          | enum         | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.          |

dataset 태그 세트를 추가하려 한다고 가정해 봅시다. 이를 위해 ingestion 프레임워크에 포함된 `simple_add_dataset_tags` transformer를 사용할 수 있습니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다:

```yaml
transformers:
  - type: "simple_add_dataset_tags"
    config:
      tag_urns:
        - "urn:li:tag:NeedsDocumentation"
        - "urn:li:tag:Legacy"
```

`simple_add_dataset_tags`는 다양한 방식으로 설정할 수 있습니다.

- 태그를 추가하되, ingestion 소스에서 전송된 기존 태그를 교체하는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_tags"
      config:
        replace_existing: true # false가 기본 동작
        tag_urns:
          - "urn:li:tag:NeedsDocumentation"
          - "urn:li:tag:Legacy"
  ```
- 태그를 추가하되, DataHub GMS에서 dataset에 사용 가능한 태그를 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_tags"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        tag_urns:
          - "urn:li:tag:NeedsDocumentation"
          - "urn:li:tag:Legacy"
  ```
- 태그를 추가하되, DataHub GMS에서 dataset에 사용 가능한 태그를 유지하는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_tags"
      config:
        semantics: PATCH
        tag_urns:
          - "urn:li:tag:NeedsDocumentation"
          - "urn:li:tag:Legacy"
  ```

## Pattern Add Dataset globalTags

### Config 세부 사항

| Field              | Required | Type                 | Default     | Description                                                                           |
| ------------------ | -------- | -------------------- | ----------- | ------------------------------------------------------------------------------------- |
| `tag_pattern`      | ✅       | map[regx, list[urn]] |             | 정규 표현식이 있는 entity URN과 매칭된 entity URN에 적용할 태그 URN 목록.            |
| `replace_existing` |          | boolean              | `false`     | ingestion 소스에서 전송된 entity에서 globalTags를 제거할지 여부.                      |
| `semantics`        |          | enum                 | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.                             |

특정 dataset에 일련의 태그를 추가하려 한다고 가정해 봅시다. 이를 위해 ingestion 프레임워크에 포함된 `pattern_add_dataset_tags` 모듈을 사용할 수 있습니다. 이 모듈은 정규 표현식 패턴을 dataset의 `urn`과 매칭하여 배열에 지정된 각각의 태그 URN을 할당합니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다:

```yaml
transformers:
  - type: "pattern_add_dataset_tags"
    config:
      tag_pattern:
        rules:
          ".*example1.*": ["urn:li:tag:NeedsDocumentation", "urn:li:tag:Legacy"]
          ".*example2.*": ["urn:li:tag:NeedsDocumentation"]
```

`pattern_add_dataset_tags`는 다양한 방식으로 설정할 수 있습니다.

- 태그를 추가하되, ingestion 소스에서 전송된 기존 태그를 교체하는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_tags"
      config:
        replace_existing: true # false가 기본 동작
        tag_pattern:
          rules:
            ".*example1.*":
              ["urn:li:tag:NeedsDocumentation", "urn:li:tag:Legacy"]
            ".*example2.*": ["urn:li:tag:NeedsDocumentation"]
  ```
- 태그를 추가하되, DataHub GMS에서 dataset에 사용 가능한 태그를 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_tags"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        tag_pattern:
          rules:
            ".*example1.*":
              ["urn:li:tag:NeedsDocumentation", "urn:li:tag:Legacy"]
            ".*example2.*": ["urn:li:tag:NeedsDocumentation"]
  ```
- 태그를 추가하되, DataHub GMS에서 dataset에 사용 가능한 태그를 유지하는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_tags"
      config:
        semantics: PATCH
        tag_pattern:
          rules:
            ".*example1.*":
              ["urn:li:tag:NeedsDocumentation", "urn:li:tag:Legacy"]
            ".*example2.*": ["urn:li:tag:NeedsDocumentation"]
  ```

## Add Dataset globalTags

### Config 세부 사항

| Field              | Required | Type                                       | Default     | Description                                                                |
| ------------------ | -------- | ------------------------------------------ | ----------- | -------------------------------------------------------------------------- |
| `get_tags_to_add`  | ✅       | callable[[str], list[TagAssociationClass]] |             | entity URN을 입력으로 받아 TagAssociationClass를 반환하는 함수.            |
| `replace_existing` |          | boolean                                    | `false`     | ingestion 소스에서 전송된 entity에서 globalTags를 제거할지 여부.           |
| `semantics`        |          | enum                                       | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.                  |

태그 할당에 더 복잡한 로직을 추가하려면 더 일반적인 add_dataset_tags transformer를 사용할 수 있습니다. 이 transformer는 사용자가 제공한 함수를 호출하여 각 dataset의 태그를 결정합니다.

```yaml
transformers:
  - type: "add_dataset_tags"
    config:
      get_tags_to_add: "<your_module>.<your_function>"
```

TagAssociationClass 태그 목록을 반환하는 함수를 다음과 같이 정의합니다:

```python
import logging

import datahub.emitter.mce_builder as builder
from datahub.metadata.schema_classes import (
    TagAssociationClass
)

def custom_tags(entity_urn: str) -> List[TagAssociationClass]:
    """Compute the tags to associate to a given dataset."""

    tag_strings = []

    ### Add custom logic here
    tag_strings.append('custom1')
    tag_strings.append('custom2')

    tag_strings = [builder.make_tag_urn(tag=n) for n in tag_strings]
    tags = [TagAssociationClass(tag=tag) for tag in tag_strings]

    logging.info(f"Tagging dataset {entity_urn} with {tag_strings}.")
    return tags
```

마지막으로 [여기에 표시된](#installing-the-package) 방법으로 커스텀 transformer를 설치하고 사용할 수 있습니다.

`add_dataset_tags`는 다양한 방식으로 설정할 수 있습니다.

- 태그를 추가하되, ingestion 소스에서 전송된 기존 태그를 교체하는 경우
  ```yaml
  transformers:
    - type: "add_dataset_tags"
      config:
        replace_existing: true # false가 기본 동작
        get_tags_to_add: "<your_module>.<your_function>"
  ```
- 태그를 추가하되, DataHub GMS에서 dataset에 사용 가능한 태그를 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "add_dataset_tags"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        get_tags_to_add: "<your_module>.<your_function>"
  ```
- 태그를 추가하되, DataHub GMS에서 dataset에 사용 가능한 태그를 유지하는 경우
  ```yaml
  transformers:
    - type: "add_dataset_tags"
      config:
        semantics: PATCH
        get_tags_to_add: "<your_module>.<your_function>"
  ```

## Set Dataset browsePath

> **⚠️ 지원 중단:** 이 transformer는 v1.3.0에서 제거될 예정입니다. 대신 [set browse_path](./universal_transformers.md#set-browsepaths)를 사용하세요.

### Config 세부 사항

| Field              | Required | Type         | Default     | Description                                                        |
| ------------------ | -------- | ------------ | ----------- | ------------------------------------------------------------------ |
| `path_templates`   | ✅       | list[string] |             | 경로 템플릿 목록.                                                  |
| `replace_existing` |          | boolean      | `false`     | ingestion 소스에서 전송된 entity에서 browsePath를 제거할지 여부.   |
| `semantics`        |          | enum         | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.          |

dataset의 browse path를 추가하려면 이 transformer를 사용할 수 있습니다. dataset `urn`에서 정보를 가져오는 데 사용할 수 있는 선택적 변수가 3개 있습니다:

- ENV: 전달된 환경 (기본값: prod)
- PLATFORM: `mysql`, `postgres` 또는 datahub이 지원하는 다른 플랫폼
- DATASET_PARTS: 슬래시로 구분된 dataset 이름의 부분들. 예: postgres의 경우 `database_name/schema_name/[table_name]`

예를 들어, `postgres` 데이터베이스에서 `superset.public.logs` 테이블에 대해 `/prod/postgres/superset/public/logs`와 같은 browse path를 생성하는 데 사용할 수 있습니다.

```yaml
transformers:
  - type: "set_dataset_browse_path"
    config:
      path_templates:
        - /ENV/PLATFORM/DATASET_PARTS
```

환경은 원하지 않고 데이터베이스 인스턴스 이름과 같은 정적 내용을 browse path에 추가하려면 다음을 사용합니다.

```yaml
transformers:
  - type: "set_dataset_browse_path"
    config:
      path_templates:
        - /PLATFORM/marketing_db/DATASET_PARTS
```

`mysql` 데이터베이스 인스턴스에서 `sales.orders` 테이블에 대해 `/mysql/marketing_db/sales/orders`와 같은 browse path가 생성됩니다.

여러 browse path를 추가할 수도 있습니다. 서로 다른 사람들이 동일한 데이터 자산을 다른 이름으로 알고 있을 수 있습니다.

```yaml
transformers:
  - type: "set_dataset_browse_path"
    config:
      path_templates:
        - /PLATFORM/marketing_db/DATASET_PARTS
        - /data_warehouse/DATASET_PARTS
```

이를 통해 `mysql` 데이터베이스 인스턴스에서 `sales.orders` 테이블에 대해 `/mysql/marketing_db/sales/orders`와 `/data_warehouse/sales/orders` 두 개의 browse path가 추가됩니다.

transform의 기본 동작은 새 browse path를 추가하는 것입니다. 선택적으로 `replace_existing: True`를 설정하면 transform이 _append_ 대신 _set_ 작업이 됩니다.

```yaml
transformers:
  - type: "set_dataset_browse_path"
    config:
      replace_existing: True
      path_templates:
        - /ENV/PLATFORM/DATASET_PARTS
```

이 경우 결과 dataset은 transform에서 설정된 하나의 browse path만 갖게 됩니다.

`set_dataset_browse_path`는 다양한 방식으로 설정할 수 있습니다.

- browsePath를 추가하되, ingestion 소스에서 전송된 기존 browsePath를 교체하는 경우
  ```yaml
  transformers:
    - type: "set_dataset_browse_path"
      config:
        replace_existing: true # false가 기본 동작
        path_templates:
          - /PLATFORM/marketing_db/DATASET_PARTS
  ```
- browsePath를 추가하되, DataHub GMS에서 dataset에 사용 가능한 browsePath를 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "set_dataset_browse_path"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        path_templates:
          - /PLATFORM/marketing_db/DATASET_PARTS
  ```
- browsePath를 추가하되, DataHub GMS에서 dataset에 사용 가능한 browsePath를 유지하는 경우
  ```yaml
  transformers:
    - type: "set_dataset_browse_path"
      config:
        semantics: PATCH
        path_templates:
          - /PLATFORM/marketing_db/DATASET_PARTS
  ```

## Simple Add Dataset glossaryTerms

### Config 세부 사항

| Field              | Required | Type         | Default     | Description                                                           |
| ------------------ | -------- | ------------ | ----------- | --------------------------------------------------------------------- |
| `term_urns`        | ✅       | list[string] |             | glossaryTerms URN 목록.                                               |
| `replace_existing` |          | boolean      | `false`     | ingestion 소스에서 전송된 entity에서 glossaryTerms를 제거할지 여부.   |
| `semantics`        |          | enum         | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.             |

유사한 방식으로 [Glossary Terms](../../../docs/generated/ingestion/sources/business-glossary.md)를 dataset에 연관시킬 수 있습니다.
ingestion 프레임워크에 포함된 `simple_add_dataset_terms` transformer를 사용할 수 있습니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다:

```yaml
transformers:
  - type: "simple_add_dataset_terms"
    config:
      term_urns:
        - "urn:li:glossaryTerm:Email"
        - "urn:li:glossaryTerm:Address"
```

`simple_add_dataset_terms`는 다양한 방식으로 설정할 수 있습니다.

- 용어를 추가하되, ingestion 소스에서 전송된 기존 용어를 교체하는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_terms"
      config:
        replace_existing: true # false가 기본 동작
        term_urns:
          - "urn:li:glossaryTerm:Email"
          - "urn:li:glossaryTerm:Address"
  ```
- 용어를 추가하되, DataHub GMS에서 dataset에 사용 가능한 용어를 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_terms"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        term_urns:
          - "urn:li:glossaryTerm:Email"
          - "urn:li:glossaryTerm:Address"
  ```
- 용어를 추가하되, DataHub GMS에서 dataset에 사용 가능한 용어를 유지하는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_terms"
      config:
        semantics: PATCH
        term_urns:
          - "urn:li:glossaryTerm:Email"
          - "urn:li:glossaryTerm:Address"
  ```

## Pattern Add Dataset glossaryTerms

### Config 세부 사항

| Field              | Required | Type                 | Default     | Description                                                                                    |
| ------------------ | -------- | -------------------- | ----------- | ---------------------------------------------------------------------------------------------- |
| `term_pattern`     | ✅       | map[regx, list[urn]] |             | 정규 표현식이 있는 entity URN과 매칭된 entity URN에 적용할 glossaryTerms URN 목록.             |
| `replace_existing` |          | boolean              | `false`     | ingestion 소스에서 전송된 entity에서 glossaryTerms를 제거할지 여부.                            |
| `semantics`        |          | enum                 | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.                                      |

regex 필터를 기반으로 dataset에 glossary terms를 추가할 수 있습니다.

```yaml
transformers:
  - type: "pattern_add_dataset_terms"
    config:
      term_pattern:
        rules:
          ".*example1.*":
            ["urn:li:glossaryTerm:Email", "urn:li:glossaryTerm:Address"]
          ".*example2.*": ["urn:li:glossaryTerm:PostalCode"]
```

`pattern_add_dataset_terms`는 다양한 방식으로 설정할 수 있습니다.

- 용어를 추가하되, ingestion 소스에서 전송된 기존 용어를 교체하는 경우

  ```yaml
  transformers:
    - type: "pattern_add_dataset_terms"
      config:
        replace_existing: true # false가 기본 동작
        term_pattern:
          rules:
            ".*example1.*":
              ["urn:li:glossaryTerm:Email", "urn:li:glossaryTerm:Address"]
            ".*example2.*": ["urn:li:glossaryTerm:PostalCode"]
  ```

- 용어를 추가하되, DataHub GMS에서 dataset에 사용 가능한 용어를 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_terms"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        term_pattern:
          rules:
            ".*example1.*":
              ["urn:li:glossaryTerm:Email", "urn:li:glossaryTerm:Address"]
            ".*example2.*": ["urn:li:glossaryTerm:PostalCode"]
  ```
- 용어를 추가하되, DataHub GMS에서 dataset에 사용 가능한 용어를 유지하는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_terms"
      config:
        semantics: PATCH
        term_pattern:
          rules:
            ".*example1.*":
              ["urn:li:glossaryTerm:Email", "urn:li:glossaryTerm:Address"]
            ".*example2.*": ["urn:li:glossaryTerm:PostalCode"]
  ```

## Tags to Term Mapping

### Config 세부 사항

| Field       | Required | Type      | Default     | Description                                                                                    |
| ----------- | -------- | --------- | ----------- | ---------------------------------------------------------------------------------------------- |
| `tags`      | ✅       | List[str] |             | 용어를 생성하고 dataset에 연관시킬 태그 이름 목록.                                             |
| `semantics` |          | enum      | "OVERWRITE" | DataHub GMS에서 dataset에 연관된 용어를 OVERWRITE할지 PATCH할지 결정합니다.                    |

<br/>

`tags_to_term` transformer는 DataHub 내에서 특정 태그를 glossary terms에 매핑하도록 설계되었습니다. 이 transformer는 glossary terms로 변환되어야 하는 태그의 설정을 받습니다. dataset의 컬럼 수준 또는 dataset 최상위 수준에서 발견된 태그에 이러한 매핑을 적용할 수 있습니다.

설정에서 태그를 지정할 때는 전체 태그 URN 대신 태그의 단순 이름을 사용합니다.

예를 들어, 태그 URN `urn:li:tag:snowflakedb.snowflakeschema.tag_name:tag_value` 대신 매핑 설정에서 단순히 `tag_name`을 지정해야 합니다.

```yaml
transformers:
  - type: "tags_to_term"
    config:
      semantics: OVERWRITE # OVERWRITE가 기본 동작
      tags:
        - "tag_name"
```

`tags_to_term` transformer는 다음과 같은 방식으로 설정할 수 있습니다:

- 태그를 기반으로 용어를 추가하되, DataHub GMS에서 dataset에 사용 가능한 용어를 덮어쓰는 경우

```yaml
transformers:
  - type: "tags_to_term"
    config:
      semantics: OVERWRITE # OVERWRITE가 기본 동작
      tags:
        - "example1"
        - "example2"
        - "example3"
```

- 태그를 기반으로 용어를 추가하되, DataHub GMS에서 dataset에 사용 가능한 용어를 유지하는 경우

```yaml
transformers:
  - type: "tags_to_term"
    config:
      semantics: PATCH
      tags:
        - "example1"
        - "example2"
        - "example3"
```

## Tags to Structured Properties

### 설명

`tags_to_structured_properties` transformer는 DataHub 태그를 Structured Properties로 변환합니다. key-value 형식의 태그(예: `dept:Finance`)와 설정을 통해 매핑된 단순 태그 이름 모두 지원합니다. Structured Properties는 변환 실행 전에 DataHub에 미리 생성되어 있어야 합니다 - 동적으로 생성되지 않습니다.

변환(및 파이프라인)이 실패하는 오류 시나리오에는 다음이 포함됩니다:

- **잘못된 속성 값**: 태그 값이 Structured Property에 정의된 허용 값과 일치하지 않는 경우
- **속성이 존재하지 않음**: 변환된 속성 URN이 존재하지 않는 Structured Property를 참조하는 경우

이러한 실패는 백엔드 유효성 검사 오류를 트리거하며 예상된 동작입니다 - DataHub에서 누락된 Structured Properties를 생성하거나 기존 속성의 허용 값을 조정해야 하는 설정 문제를 나타냅니다.

### Config 세부 사항

| Field                         | Required | Type                                        | Default | Description                                                               |
| ----------------------------- | -------- | ------------------------------------------- | ------- | ------------------------------------------------------------------------- |
| `process_key_value_tags`      |          | boolean                                     | `false` | key:value 형식의 태그 파싱 활성화                                         |
| `key_value_separator`         |          | string                                      | `:`     | key-value 태그의 구분자 문자                                              |
| `key_value_property_prefix`   |          | string                                      | `""`    | key-value 태그에서 파생된 속성 ID에 추가할 접두사                         |
| `tag_structured_property_map` |          | map[property_id, StructuredPropertyMapping] | `{}`    | 구조화된 속성 ID를 태그 키워드 설정에 매핑                                |
| `remove_original_tags`        |          | boolean                                     | `false` | 구조화된 속성으로 변환 후 원래 태그를 제거할지 여부                       |
| `semantics`                   |          | enum                                        | `PATCH` | DataHub GMS에서 구조화된 속성을 OVERWRITE할지 PATCH할지 여부              |

`tags_to_structured_properties` transformer는 DataHub 태그를 구조화된 속성으로 변환합니다. 두 가지 모드를 지원합니다:

1. **Key-Value 태그**: `key:value` 형식의 태그(예: `dept:Finance`)로, 키가 속성 이름이 됩니다.
2. **키워드 태그**: 설정을 통해 속성에 매핑된 단순 태그 이름

이 transformer는 태그를 내보내는 모든 소스(Tableau, dbt, Snowflake 등)에서 작동하며, 태그에서 구조화된 속성으로 마이그레이션하는 데 사용할 수 있습니다.

### Key-Value 태그 예제

`department:Finance` 및 `sensitivity:PII`와 같은 태그를 구조화된 속성으로 변환:

```yaml
transformers:
  - type: "tags_to_structured_properties"
    config:
      process_key_value_tags: true
      key_value_separator: ":"
      key_value_property_prefix: "io.company."
      remove_original_tags: false
```

이 config를 사용하면:

- 태그 `department:Finance` → 속성 `io.company.department`, 값 `Finance`
- 태그 `sensitivity:PII` → 속성 `io.company.sensitivity`, 값 `PII`

### 키워드 태그 매핑 예제

특정 태그 키워드를 미리 정의된 구조화된 속성에 매핑:

```yaml
transformers:
  - type: "tags_to_structured_properties"
    config:
      tag_structured_property_map:
        "io.company.department":
          values: ["Finance", "Sales", "Marketing", "Engineering"]
        "io.company.dataClassification":
          values: ["PII", "Confidential", "Public"]
        "io.company.qualityLevel":
          values: ["Certified", "Draft", "Deprecated"]
      remove_original_tags: false
```

이 config를 사용하면:

- 태그 `Finance` → 속성 `io.company.department`, 값 `Finance`
- 태그 `PII` → 속성 `io.company.dataClassification`, 값 `PII`
- 태그 `Certified` → 속성 `io.company.qualityLevel`, 값 `Certified`

### 복합 예제

key-value 파싱과 키워드 매핑을 함께 사용:

```yaml
transformers:
  - type: "tags_to_structured_properties"
    config:
      # key-value 처리 활성화
      process_key_value_tags: true
      key_value_separator: ":"
      key_value_property_prefix: "io.company."

      # key-value 형식이 아닌 태그에 대한 키워드 매핑
      tag_structured_property_map:
        "io.company.department":
          values: ["Finance", "Sales", "Marketing"]
        "io.company.dataClassification":
          values: ["PII", "Confidential"]

      # 원래 태그도 유지
      remove_original_tags: false

      # 기존 구조화된 속성과 병합
      semantics: PATCH
```

### 참고 사항

- 태그가 key-value 형식과 키워드 매핑 모두에 일치하는 경우 key-value가 우선합니다.
- `tag_structured_property_map`에서 첫 번째로 일치하는 속성이 태그 값을 받습니다.
- 매칭되지 않는 태그는 경고를 생성하지만 변환에 실패하지는 않습니다.
- 여러 태그가 동일한 속성에 매핑될 수 있습니다 (값은 배열로 누적됩니다).
- Structured Properties는 변환 실행 전에 DataHub에 미리 생성되어 있어야 합니다.

## Pattern Add Dataset Schema Field glossaryTerms

### Config 세부 사항

| Field              | Required | Type                 | Default     | Description                                                                                    |
| ------------------ | -------- | -------------------- | ----------- | ---------------------------------------------------------------------------------------------- |
| `term_pattern`     | ✅       | map[regx, list[urn]] |             | 정규 표현식이 있는 entity URN과 매칭된 entity URN에 적용할 glossaryTerms URN 목록.             |
| `replace_existing` |          | boolean              | `false`     | ingestion 소스에서 전송된 entity에서 glossaryTerms를 제거할지 여부.                            |
| `semantics`        |          | enum                 | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.                                      |

regex 필터를 기반으로 schema 필드에 glossary terms를 추가할 수 있습니다.

첫 번째 매칭 패턴의 용어만 적용됩니다.

```yaml
transformers:
  - type: "pattern_add_dataset_schema_terms"
    config:
      term_pattern:
        rules:
          ".*email.*": ["urn:li:glossaryTerm:Email"]
          ".*name.*": ["urn:li:glossaryTerm:Name"]
```

`pattern_add_dataset_schema_terms`는 다양한 방식으로 설정할 수 있습니다.

- 용어를 추가하되, ingestion 소스에서 전송된 기존 용어를 교체하는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_schema_terms"
      config:
        replace_existing: true # false가 기본 동작
        term_pattern:
          rules:
            ".*email.*": ["urn:li:glossaryTerm:Email"]
            ".*name.*": ["urn:li:glossaryTerm:Name"]
  ```
- 용어를 추가하되, DataHub GMS에서 dataset에 사용 가능한 용어를 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_schema_terms"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        term_pattern:
          rules:
            ".*email.*": ["urn:li:glossaryTerm:Email"]
            ".*name.*": ["urn:li:glossaryTerm:Name"]
  ```
- 용어를 추가하되, DataHub GMS에서 dataset에 사용 가능한 용어를 유지하는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_schema_terms"
      config:
        semantics: PATCH
        term_pattern:
          rules:
            ".*email.*": ["urn:li:glossaryTerm:Email"]
            ".*name.*": ["urn:li:glossaryTerm:Name"]
  ```

## Pattern Add Dataset Schema Field globalTags

### Config 세부 사항

| Field              | Required | Type                 | Default     | Description                                                                           |
| ------------------ | -------- | -------------------- | ----------- | ------------------------------------------------------------------------------------- |
| `tag_pattern`      | ✅       | map[regx, list[urn]] |             | 정규 표현식이 있는 entity URN과 매칭된 entity URN에 적용할 태그 URN 목록.            |
| `replace_existing` |          | boolean              | `false`     | ingestion 소스에서 전송된 entity에서 globalTags를 제거할지 여부.                      |
| `semantics`        |          | enum                 | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.                             |

특정 schema 필드에 일련의 태그를 추가할 수도 있습니다. `pattern_add_dataset_schema_tags` transformer를 사용하면 됩니다. 이 transformer는 정규 표현식 패턴을 각 schema 필드 경로에 매칭하여 배열에 지정된 각각의 태그 URN을 할당합니다.

첫 번째 매칭 패턴의 태그만 적용됩니다.

config는 다음과 같습니다:

```yaml
transformers:
  - type: "pattern_add_dataset_schema_tags"
    config:
      tag_pattern:
        rules:
          ".*email.*": ["urn:li:tag:Email"]
          ".*name.*": ["urn:li:tag:Name"]
```

`pattern_add_dataset_schema_tags`는 다양한 방식으로 설정할 수 있습니다.

- 태그를 추가하되, ingestion 소스에서 전송된 기존 태그를 교체하는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_schema_tags"
      config:
        replace_existing: true # false가 기본 동작
        tag_pattern:
          rules:
            ".*example1.*":
              ["urn:li:tag:NeedsDocumentation", "urn:li:tag:Legacy"]
            ".*example2.*": ["urn:li:tag:NeedsDocumentation"]
  ```
- 태그를 추가하되, DataHub GMS에서 dataset에 사용 가능한 태그를 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_schema_tags"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        tag_pattern:
          rules:
            ".*example1.*":
              ["urn:li:tag:NeedsDocumentation", "urn:li:tag:Legacy"]
            ".*example2.*": ["urn:li:tag:NeedsDocumentation"]
  ```
- 태그를 추가하되, DataHub GMS에서 dataset에 사용 가능한 태그를 유지하는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_schema_tags"
      config:
        semantics: PATCH
        tag_pattern:
          rules:
            ".*example1.*":
              ["urn:li:tag:NeedsDocumentation", "urn:li:tag:Legacy"]
            ".*example2.*": ["urn:li:tag:NeedsDocumentation"]
  ```

## Simple Add Dataset datasetProperties

### Config 세부 사항

| Field              | Required | Type           | Default     | Description                                                               |
| ------------------ | -------- | -------------- | ----------- | ------------------------------------------------------------------------- |
| `properties`       | ✅       | dict[str, str] |             | 키-값 쌍의 맵.                                                            |
| `replace_existing` |          | boolean        | `false`     | ingestion 소스에서 전송된 entity에서 datasetProperties를 제거할지 여부.   |
| `semantics`        |          | enum           | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.                 |

`simple_add_dataset_properties` transformer는 설정에서 dataset entity에 속성을 할당합니다.
`properties` 필드는 문자열 값의 딕셔너리입니다. 키가 충돌하는 경우 config의 값이 기존 값을 덮어씁니다.

```yaml
transformers:
  - type: "simple_add_dataset_properties"
    config:
      properties:
        prop1: value1
        prop2: value2
```

`simple_add_dataset_properties`는 다양한 방식으로 설정할 수 있습니다.

- dataset 속성을 추가하되, ingestion 소스에서 전송된 기존 dataset 속성을 교체하는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_properties"
      config:
        replace_existing: true # false가 기본 동작
        properties:
          prop1: value1
          prop2: value2
  ```
- dataset 속성을 추가하되, DataHub GMS에서 dataset에 사용 가능한 dataset 속성을 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_properties"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        properties:
          prop1: value1
          prop2: value2
  ```
- dataset 속성을 추가하되, DataHub GMS에서 dataset에 사용 가능한 dataset 속성을 유지하는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_properties"
      config:
        semantics: PATCH
        properties:
          prop1: value1
          prop2: value2
  ```

## Add Dataset datasetProperties

### Config 세부 사항

| Field                           | Required | Type                                   | Default     | Description                                                               |
| ------------------------------- | -------- | -------------------------------------- | ----------- | ------------------------------------------------------------------------- |
| `add_properties_resolver_class` | ✅       | Type[AddDatasetPropertiesResolverBase] |             | `AddDatasetPropertiesResolverBase`를 확장하는 클래스                      |
| `replace_existing`              |          | boolean                                | `false`     | ingestion 소스에서 전송된 entity에서 datasetProperties를 제거할지 여부.   |
| `semantics`                     |          | enum                                   | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.                 |

속성 할당에 더 복잡한 로직을 추가하려면 `add_dataset_properties` transformer를 사용할 수 있습니다. 이 transformer는 사용자가 제공한 클래스(`AddDatasetPropertiesResolverBase` 클래스를 확장)를 호출하여 각 dataset의 속성을 결정합니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다:

```yaml
transformers:
  - type: "add_dataset_properties"
    config:
      add_properties_resolver_class: "<your_module>.<your_class>"
```

커스텀 속성 목록을 반환하는 클래스를 다음과 같이 정의합니다:

```python
import logging
from typing import Dict
from datahub.ingestion.transformer.add_dataset_properties import AddDatasetPropertiesResolverBase

class MyPropertiesResolver(AddDatasetPropertiesResolverBase):
    def get_properties_to_add(self, entity_urn: str) -> Dict[str, str]:
        ### Add custom logic here
        properties= {'my_custom_property': 'property value'}
        logging.info(f"Adding properties: {properties} to dataset: {entity_urn}.")
        return properties
```

`add_dataset_properties`는 다양한 방식으로 설정할 수 있습니다.

- dataset 속성을 추가하되, ingestion 소스에서 전송된 기존 dataset 속성을 교체하는 경우

  ```yaml
  transformers:
    - type: "add_dataset_properties"
      config:
        replace_existing: true # false가 기본 동작
        add_properties_resolver_class: "<your_module>.<your_class>"
  ```

- dataset 속성을 추가하되, DataHub GMS에서 dataset에 사용 가능한 dataset 속성을 덮어쓰는 경우

  ```yaml
  transformers:
    - type: "add_dataset_properties"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        add_properties_resolver_class: "<your_module>.<your_class>"
  ```

- dataset 속성을 추가하되, DataHub GMS에서 dataset에 사용 가능한 dataset 속성을 유지하는 경우
  ```yaml
  transformers:
    - type: "add_dataset_properties"
      config:
        semantics: PATCH
        add_properties_resolver_class: "<your_module>.<your_class>"
  ```

## Replace ExternalUrl Dataset

### Config 세부 사항

| Field           | Required | Type   | Default | Description                  |
| --------------- | -------- | ------ | ------- | ---------------------------- |
| `input_pattern` | ✅       | string |         | 교체할 문자열 또는 패턴      |
| `replacement`   | ✅       | string |         | 교체 문자열                  |

dataset 속성의 externalUrl에서 전체/부분 문자열을 매칭하여 교체 문자열로 바꿉니다.

```yaml
transformers:
  - type: "replace_external_url"
    config:
      input_pattern: '\b\w*hub\b'
      replacement: "sub"
```

## Replace ExternalUrl Container

### Config 세부 사항

| Field           | Required | Type   | Default | Description                  |
| --------------- | -------- | ------ | ------- | ---------------------------- |
| `input_pattern` | ✅       | string |         | 교체할 문자열 또는 패턴      |
| `replacement`   | ✅       | string |         | 교체 문자열                  |

container 속성의 externalUrl에서 전체/부분 문자열을 매칭하여 교체 문자열로 바꿉니다.

```yaml
transformers:
  - type: "replace_external_url_container"
    config:
      input_pattern: '\b\w*hub\b'
      replacement: "sub"
```

## Clean User URN in DatasetUsageStatistics Aspect

### Config 세부 사항

| Field                 | Required | Type         | Default | Description                                           |
| --------------------- | -------- | ------------ | ------- | ----------------------------------------------------- |
| `pattern_for_cleanup` | ✅       | list[string] |         | 소유자 URN에서 제거할 접미사/접두사 목록              |

DatasetUsageStatistics aspect의 사용자 URN에 매칭하여 해당 부분을 제거합니다.

```yaml
transformers:
  - type: "pattern_cleanup_dataset_usage_user"
    config:
      pattern_for_cleanup:
        - "ABCDEF"
        - (?<=_)(\w+)
```

## Simple Add Dataset domains

### Config 세부 사항

| Field              | Required | Type                  | Default     | Description                                                      |
| ------------------ | -------- | --------------------- | ----------- | ---------------------------------------------------------------- |
| `domains`          | ✅       | list[union[urn, str]] |             | 단순 도메인 이름 또는 도메인 URN 목록.                           |
| `replace_existing` |          | boolean               | `false`     | ingestion 소스에서 전송된 entity에서 도메인을 제거할지 여부.     |
| `semantics`        |          | enum                  | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.        |

`replace_existing` 및 `semantics`에 대한 transformer 동작은 [replace_existing과 semantics의 관계](#relationship-between-replace_existing-and-semantics) 섹션을 참고하세요.

<br/>

dataset에 일련의 도메인을 추가하려 한다면 `simple_add_dataset_domain` transformer를 사용할 수 있습니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다.

여기서 도메인을 URN(예: urn:li:domain:engineering) 또는 단순 도메인 이름(예: engineering)으로 설정할 수 있으며, 두 경우 모두 도메인이 DataHub GMS에 미리 프로비저닝되어 있어야 합니다.

```yaml
transformers:
  - type: "simple_add_dataset_domain"
    config:
      semantics: OVERWRITE
      domains:
        - urn:li:domain:engineering
```

`simple_add_dataset_domain`은 다양한 방식으로 설정할 수 있습니다.

- 도메인을 추가하되, ingestion 소스에서 전송된 기존 도메인을 교체하는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_domain"
      config:
        replace_existing: true # false가 기본 동작
        domains:
          - "urn:li:domain:engineering"
          - "urn:li:domain:hr"
  ```
- 도메인을 추가하되, DataHub GMS에서 dataset에 사용 가능한 도메인을 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_domain"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        domains:
          - "urn:li:domain:engineering"
          - "urn:li:domain:hr"
  ```
- 도메인을 추가하되, DataHub GMS에서 dataset에 사용 가능한 도메인을 유지하는 경우
  ```yaml
  transformers:
    - type: "simple_add_dataset_domain"
      config:
        semantics: PATCH
        domains:
          - "urn:li:domain:engineering"
          - "urn:li:domain:hr"
  ```

## Pattern Add Dataset domains

### Config 세부 사항

| Field              | Required | Type                            | Default     | Description                                                                                                                |
| ------------------ | -------- | ------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------- |
| `domain_pattern`   | ✅       | map[regx, list[union[urn, str]] |             | 정규 표현식이 있는 dataset URN과 매칭된 dataset URN에 적용할 단순 도메인 이름 또는 도메인 URN 목록.                        |
| `replace_existing` |          | boolean                         | `false`     | ingestion 소스에서 전송된 entity에서 도메인을 제거할지 여부.                                                               |
| `semantics`        |          | enum                            | `OVERWRITE` | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.                                                                  |
| `is_container`     |          | bool                            | `false`     | container도 함께 고려할지 여부. true이면 도메인이 dataset과 해당 container 모두에 연결됩니다.                              |

특정 dataset에 일련의 도메인을 추가하려 한다고 가정해 봅시다. 이를 위해 ingestion 프레임워크에 포함된 pattern_add_dataset_domain transformer를 사용할 수 있습니다.
이 transformer는 dataset의 URN에 정규 표현식 패턴을 매칭하여 배열에 지정된 각각의 도메인 URN을 할당합니다.

is_container 필드가 true로 설정되면, 모듈은 매칭된 dataset에 도메인을 연결할 뿐만 아니라 해당 dataset과 관련된 container를 찾아 연결합니다. 즉, dataset과 해당 container 모두 지정된 소유자와 연관됩니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다.
여기서 도메인 목록을 URN(예: urn:li:domain:hr) 또는 단순 도메인 이름(예: hr)으로 설정할 수 있으며, 두 경우 모두 도메인이 DataHub GMS에 미리 프로비저닝되어 있어야 합니다.

```yaml
transformers:
  - type: "pattern_add_dataset_domain"
    config:
      semantics: OVERWRITE
      domain_pattern:
        rules:
          'urn:li:dataset:\(urn:li:dataPlatform:postgres,postgres\.public\.n.*':
            ["hr"]
          'urn:li:dataset:\(urn:li:dataPlatform:postgres,postgres\.public\.t.*':
            ["urn:li:domain:finance"]
```

`pattern_add_dataset_domain`은 다양한 방식으로 설정할 수 있습니다.

- 도메인을 추가하되, ingestion 소스에서 전송된 기존 도메인을 교체하는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_domain"
      config:
        replace_existing: true # false가 기본 동작
        domain_pattern:
          rules:
            'urn:li:dataset:\(urn:li:dataPlatform:postgres,postgres\.public\.n.*':
              ["hr"]
            'urn:li:dataset:\(urn:li:dataPlatform:postgres,postgres\.public\.t.*':
              ["urn:li:domain:finance"]
  ```
- 도메인을 추가하되, DataHub GMS에서 dataset에 사용 가능한 도메인을 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "pattern_add_dataset_domain"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        domain_pattern:
          rules:
            'urn:li:dataset:\(urn:li:dataPlatform:postgres,postgres\.public\.n.*':
              ["hr"]
            'urn:li:dataset:\(urn:li:dataPlatform:postgres,postgres\.public\.t.*':
              ["urn:li:domain:finance"]
  ```
- 도메인을 추가하되, DataHub GMS에서 dataset에 사용 가능한 도메인을 유지하는 경우

  ```yaml
  transformers:
    - type: "pattern_add_dataset_domain"
      config:
        semantics: PATCH
        domain_pattern:
          rules:
            'urn:li:dataset:\(urn:li:dataPlatform:postgres,postgres\.public\.n.*':
              ["hr"]
            'urn:li:dataset:\(urn:li:dataPlatform:postgres,postgres\.public\.t.*':
              ["urn:li:domain:finance"]
  ```

- dataset과 해당 container에 도메인 추가
  ```yaml
  transformers:
    - type: "pattern_add_dataset_domain"
      config:
        is_container: true
        semantics: PATCH / OVERWRITE # 사용자 선택에 따라
        domain_pattern:
          rules:
            'urn:li:dataset:\(urn:li:dataPlatform:postgres,postgres\.public\.n.*':
              ["hr"]
            'urn:li:dataset:\(urn:li:dataPlatform:postgres,postgres\.public\.t.*':
              ["urn:li:domain:finance"]
  ```
  ⚠️ 경고:
  동일한 container에 있는 두 dataset에 서로 다른 도메인이 있는 경우, 해당 dataset container에 모든 도메인이 추가됩니다.

예를 들어:

```yaml
transformers:
  - type: "pattern_add_dataset_domain"
    config:
      is_container: true
      domain_pattern:
        rules:
          ".*example1.*": ["hr"]
          ".*example2.*": ["urn:li:domain:finance"]
```

example1과 example2가 같은 container에 있다면, hr과 finance 도메인 모두 각각의 dataset container에 추가됩니다.

## Domain Mapping Based on Tags

### Config 세부 사항

| Field            | Required | Type           | Default     | Description                                                                             |
| ---------------- | -------- | -------------- | ----------- | --------------------------------------------------------------------------------------- |
| `domain_mapping` | ✅       | Dict[str, str] |             | Dataset entity 태그를 키로, 도메인 URN 또는 이름을 값으로 하여 dataset 자산과 매핑.    |
| `semantics`      |          | enum           | "OVERWRITE" | DataHub GMS에 있는 entity를 OVERWRITE할지 PATCH할지 여부.                               |

<br/>

태그를 기반으로 dataset에 도메인을 추가하려 한다면 `domain_mapping_based_on_tags` transformer를 사용할 수 있습니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다.

도메인을 URN(예: urn:li:domain:engineering) 또는 단순 도메인 이름(예: engineering)으로 설정할 수 있으며, 두 경우 모두 도메인이 DataHub GMS에 미리 프로비저닝되어 있어야 합니다.

도메인 매핑에서 태그를 지정할 때는 전체 태그 URN 대신 태그의 단순 이름을 사용합니다.

예를 들어, 태그 URN urn:li:tag:NeedsDocumentation 대신 도메인 매핑 설정에서 단순 태그 이름 NeedsDocumentation을 지정해야 합니다.

```yaml
transformers:
  - type: "domain_mapping_based_on_tags"
    config:
      domain_mapping:
        "NeedsDocumentation": "urn:li:domain:documentation"
```

`domain_mapping_based_on_tags`는 다양한 방식으로 설정할 수 있습니다.

- 태그를 기반으로 도메인을 추가하되, DataHub GMS에서 dataset에 사용 가능한 도메인을 덮어쓰는 경우
  ```yaml
  transformers:
    - type: "domain_mapping_based_on_tags"
      config:
        semantics: OVERWRITE # OVERWRITE가 기본 동작
        domain_mapping:
          "example1": "urn:li:domain:engineering"
          "example2": "urn:li:domain:hr"
  ```
- 태그를 기반으로 도메인을 추가하되, DataHub GMS에서 dataset에 사용 가능한 도메인을 유지하는 경우
  ```yaml
  transformers:
    - type: "domain_mapping_based_on_tags"
      config:
        semantics: PATCH
        domain_mapping:
          "example1": "urn:li:domain:engineering"
          "example2": "urn:li:domain:hr"
  ```

## Simple Add Dataset dataProduct

### Config 세부 사항

| Field                          | Required | Type           | Default | Description                                                                             |
| ------------------------------ | -------- | -------------- | ------- | --------------------------------------------------------------------------------------- |
| `dataset_to_data_product_urns` | ✅       | Dict[str, str] |         | Dataset entity URN을 키로, dataproduct URN을 값으로 하여 dataset 자산과 함께 생성.      |

특정 dataset을 자산으로 하는 dataproduct 세트를 추가하려 한다고 가정해 봅시다. 이를 위해 ingestion 프레임워크에 포함된 `simple_add_dataset_dataproduct` transformer를 사용할 수 있습니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다:

```yaml
transformers:
  - type: "simple_add_dataset_dataproduct"
    config:
      dataset_to_data_product_urns:
        "urn:li:dataset:(urn:li:dataPlatform:bigquery,example1,PROD)": "urn:li:dataProduct:first"
        "urn:li:dataset:(urn:li:dataPlatform:bigquery,example2,PROD)": "urn:li:dataProduct:second"
```

## Pattern Add Dataset dataProduct

### Config 세부 사항

| Field                                  | Required | Type           | Default | Description                                                                                                                    |
| -------------------------------------- | -------- | -------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `dataset_to_data_product_urns_pattern` | ✅       | map[regx, urn] |         | 정규 표현식이 있는 dataset entity URN과 매칭된 entity URN에 적용할 dataproduct URN.                                            |
| `is_container`                         |          | bool           | `false` | container도 함께 고려할지 여부. true이면 data product가 dataset과 해당 container 모두에 연결됩니다.                            |

특정 dataset 또는 해당 container를 자산으로 하는 일련의 data product를 추가하려 한다고 가정해 봅시다. 이를 위해 ingestion 프레임워크에 포함된 pattern_add_dataset_dataproduct 모듈을 사용할 수 있습니다. 이 모듈은 정규 표현식 패턴을 dataset의 URN과 매칭하여 주어진 URN으로 data product entity를 생성하고, 매칭된 dataset을 자산으로 연관시킵니다.

is_container 필드가 true로 설정되면, 모듈은 매칭된 dataset에 data product를 연결할 뿐만 아니라 해당 dataset과 관련된 container를 찾아 연결합니다. 즉, dataset과 해당 container 모두 지정된 data product와 연관됩니다.

ingestion recipe YAML에 추가할 config는 다음과 같습니다:

- dataset에 Product 추가
  ```yaml
  transformers:
    - type: "pattern_add_dataset_dataproduct"
      config:
        dataset_to_data_product_urns_pattern:
          rules:
            ".*example1.*": "urn:li:dataProduct:first"
            ".*example2.*": "urn:li:dataProduct:second"
  ```
- dataset container에 Product 추가
  ```yaml
  transformers:
    - type: "pattern_add_dataset_dataproduct"
      config:
        is_container: true
        dataset_to_data_product_urns_pattern:
          rules:
            ".*example1.*": "urn:li:dataProduct:first"
            ".*example2.*": "urn:li:dataProduct:second"
  ```
  ⚠️ 경고:
  동일한 container에 있는 두 dataset에 서로 다른 data product가 있는 경우, container에는 하나의 data product만 연결될 수 있습니다.

예를 들어:

```yaml
transformers:
  - type: "pattern_add_dataset_dataproduct"
    config:
      is_container: true
      dataset_to_data_product_urns_pattern:
        rules:
          ".*example1.*": "urn:li:dataProduct:first"
          ".*example2.*": "urn:li:dataProduct:second"
```

example1과 example2가 같은 container에 있다면 urn:li:dataProduct:first만 추가됩니다. 그러나 서로 다른 container에 있다면 시스템이 예상대로 작동하여 올바른 data product URN을 할당합니다.

## Add Dataset dataProduct

### Config 세부 사항

| Field                     | Required | Type                           | Default | Description                                                                              |
| ------------------------- | -------- | ------------------------------ | ------- | ---------------------------------------------------------------------------------------- |
| `get_data_product_to_add` | ✅       | callable[[str], Optional[str]] |         | dataset entity URN을 입력으로 받아 생성할 dataproduct URN을 반환하는 함수.               |

dataproduct 생성에 더 복잡한 로직을 추가하려면 더 일반적인 add_dataset_dataproduct transformer를 사용할 수 있습니다. 이 transformer는 사용자가 제공한 함수를 호출하여 지정된 dataset을 자산으로 하는 생성할 dataproduct를 결정합니다.

```yaml
transformers:
  - type: "add_dataset_dataproduct"
    config:
      get_data_product_to_add: "<your_module>.<your_function>"
```

dataproduct entity URN을 반환하는 함수를 다음과 같이 정의합니다:

```python
import datahub.emitter.mce_builder as builder

def custom_dataproducts(entity_urn: str) -> Optional[str]:
    """Compute the dataproduct urn to a given dataset urn."""

    dataset_to_data_product_map = {
        builder.make_dataset_urn("bigquery", "example1"): "urn:li:dataProduct:first"
    }
    return dataset_to_data_product_map.get(dataset_urn)
```

마지막으로 [여기에 표시된](#installing-the-package) 방법으로 커스텀 transformer를 설치하고 사용할 수 있습니다.

## Relationship Between replace_existing and semantics

여기서 설명하는 transformer 동작은 `simple_add_dataset_ownership`의 맥락이지만, `replace_existing` 및 `semantics` 설정 속성을 지원하는 모든 dataset transformer에 적용됩니다. 예를 들어 `simple_add_dataset_tags`는 이 섹션에서 설명한 동작에 따라 태그를 추가하거나 제거합니다.

`replace_existing`은 현재 실행 중인 ingestion 파이프라인에서 소유자를 제거할지 여부를 제어합니다.

`semantics`는 DataHub GMS 서버에 있는 소유자를 덮어쓸지 patch할지 여부를 제어합니다. 이러한 소유자는 DataHub Portal에서 추가되었을 수 있습니다.

`replace_existing`이 `true`이고 `semantics`가 `OVERWRITE`인 경우 transformer는 다음 단계를 수행합니다.

1. `replace_existing`이 `true`이므로 입력 entity(즉, dataset)에서 소유자를 제거합니다.
2. ingestion recipe에 명시된 소유자를 입력 entity에 추가합니다.
3. `semantics`가 `OVERWRITE`이므로 DataHub GMS 서버에서 입력 entity의 소유자를 가져올 필요가 없습니다.
4. 입력 entity를 반환합니다.

`replace_existing`이 `true`이고 `semantics`가 `PATCH`인 경우 transformer는 다음 단계를 수행합니다.

1. `replace_existing`이 `true`이므로 먼저 입력 entity(즉, dataset)에서 소유자를 제거합니다.
2. ingestion recipe에 명시된 소유자를 입력 entity에 추가합니다.
3. `semantics`가 `PATCH`이므로 DataHub GMS 서버에서 입력 entity의 소유자를 가져옵니다.
4. DataHub GMS 서버에서 가져온 소유자를 입력 entity에 추가합니다.
5. 입력 entity를 반환합니다.

`replace_existing`이 `false`이고 `semantics`가 `OVERWRITE`인 경우 transformer는 다음 단계를 수행합니다.

1. `replace_existing`이 `false`이므로 입력 entity에 있는 소유자를 그대로 유지합니다.
2. ingestion recipe에 명시된 소유자를 입력 entity에 추가합니다.
3. `semantics`가 `OVERWRITE`이므로 DataHub GMS 서버에서 입력 entity의 소유자를 가져올 필요가 없습니다.
4. 입력 entity를 반환합니다.

`replace_existing`이 `false`이고 `semantics`가 `PATCH`인 경우 transformer는 다음 단계를 수행합니다.

1. `replace_existing`이 `false`이므로 입력 entity에 있는 소유자를 그대로 유지합니다.
2. ingestion recipe에 명시된 소유자를 입력 entity에 추가합니다.
3. `semantics`가 `PATCH`이므로 DataHub GMS 서버에서 입력 entity의 소유자를 가져옵니다.
4. DataHub GMS 서버에서 가져온 소유자를 입력 entity에 추가합니다.
5. 입력 entity를 반환합니다.

## Writing a custom transformer from scratch

위의 몇 가지 예제에서는 ingestion 프레임워크에 이미 구현된 클래스를 사용했습니다. 그러나 더 고급 사례에서는 커스텀 코드가 필요할 수 있습니다. 예를 들어 조건부 로직을 활용하거나 속성을 재작성하려는 경우가 있습니다. 이러한 경우 자체 모듈을 추가하고 커스텀 transformer로서 인수를 정의할 수 있습니다.

예를 들어, 위의 미리 설정된 목록이 아닌 외부 소스(예: API 엔드포인트 또는 파일)에 의존하는 소유권 필드 세트를 메타데이터에 추가하려 한다고 가정해 봅시다. 이 경우 커스텀 설정에 인수로 JSON 파일을 설정하고, transformer가 이 파일을 읽어 포함된 소유권 요소를 모든 메타데이터 이벤트에 추가하도록 할 수 있습니다.

JSON 파일은 다음과 같은 형태일 수 있습니다:

```json
[
  "urn:li:corpuser:athos",
  "urn:li:corpuser:porthos",
  "urn:li:corpuser:aramis",
  "urn:li:corpGroup:the_three_musketeers"
]
```

### Config 정의

시작하기 위해 [`datahub.configuration.common.ConfigModel`](../../src/datahub/configuration/common.py)에서 상속받는 `AddCustomOwnershipConfig` 클래스를 초기화합니다. 유일한 매개변수는 소유자 URN 목록을 포함한 JSON 파일의 경로를 기대하는 `owners_json`입니다. 이는 `custom_transform_example.py`라는 파일에 들어갑니다.

```python
from datahub.configuration.common import ConfigModel

class AddCustomOwnershipConfig(ConfigModel):
    owners_json: str
```

### Transformer 정의

다음으로 [`datahub.ingestion.api.transform.Transformer`](../../src/datahub/ingestion/api/transform.py)에서 상속받아야 하는 transformer 자체를 정의합니다. 프레임워크는 transformer 작성을 매우 간단하게 만들어주는 [`datahub.ingestion.transformer.base_transformer.BaseTransformer`](../../src/datahub/ingestion/transformer/base_transformer.py)라는 헬퍼 클래스를 제공합니다.
먼저 모든 import를 추가합니다:

```python
# append these to the start of custom_transform_example.py
import json
from typing import List, Optional

from datahub.configuration.common import ConfigModel
from datahub.ingestion.api.common import PipelineContext
from datahub.ingestion.transformer.add_dataset_ownership import Semantics
from datahub.ingestion.transformer.base_transformer import (
    BaseTransformer,
    SingleAspectTransformer,
)
from datahub.metadata.schema_classes import (
    OwnerClass,
    OwnershipClass,
    OwnershipTypeClass,
)

```

다음으로 클래스의 기본 스캐폴딩을 정의합니다:

```python
# append this to the end of custom_transform_example.py

class AddCustomOwnership(BaseTransformer, SingleAspectTransformer):
    """Transformer that adds owners to datasets according to a callback function."""

    # context param to generate run metadata such as a run ID
    ctx: PipelineContext
    # as defined in the previous block
    config: AddCustomOwnershipConfig

    def __init__(self, config: AddCustomOwnershipConfig, ctx: PipelineContext):
        super().__init__()
        self.ctx = ctx
        self.config = config

        with open(self.config.owners_json, "r") as f:
            raw_owner_urns = json.load(f)

        self.owners = [
            OwnerClass(owner=owner, type=OwnershipTypeClass.DATAOWNER)
            for owner in raw_owner_urns
        ]
```

transformer는 두 가지 함수가 있어야 합니다: 초기화를 위한 `create()` 함수와 변환을 실행하는 `transform()` 함수. `BaseTransformer`와 `SingleAspectTransformer`를 확장하는 transformer는 더 복잡한 `transform` 함수를 구현하지 않고 `transform_aspect` 함수만 구현하면 됩니다.

설정 딕셔너리를 파싱하는 `create()` 메서드를 추가합니다:

```python
# add this as a function of AddCustomOwnership

@classmethod
def create(cls, config_dict: dict, ctx: PipelineContext) -> "AddCustomOwnership":
    config = AddCustomOwnershipConfig.parse_obj(config_dict)
    return cls(config, ctx)
```

다음으로 변환하려는 entity 타입과 aspect를 헬퍼 클래스에 알려야 합니다. 이 경우 `dataset` entity만 처리하고 `ownership` aspect를 변환하려 합니다.

```python
def entity_types(self) -> List[str]:
    return ["dataset"]

def aspect_name(self) -> str:
    return "ownership"
```

마지막으로 커스텀 소유권 클래스를 추가하는 실제 작업을 수행하는 `transform_aspect()` 메서드를 구현해야 합니다. 이 메서드는 upstream 소스에서 이 aspect의 값이 있는 경우 선택적으로 채워진 aspect 값과 함께 프레임워크에 의해 호출됩니다. 프레임워크는 MCE와 MCP 모두의 전처리를 처리하므로 `transform_aspect()` 함수는 entity당 한 번만 호출됩니다. 우리의 역할은 단지 입력 aspect(또는 부재)를 검사하고 이 aspect에 대한 변환된 값을 생성하는 것입니다. 이 메서드에서 `None`을 반환하면 이 aspect가 내보내지지 않습니다.

```python
# add this as a function of AddCustomOwnership

def transform_aspect(  # type: ignore
    self, entity_urn: str, aspect_name: str, aspect: Optional[OwnershipClass]
) -> Optional[OwnershipClass]:

    owners_to_add = self.owners
    assert aspect is None or isinstance(aspect, OwnershipClass)

    if owners_to_add:
        ownership = (
            aspect
            if aspect
            else OwnershipClass(
                owners=[],
            )
        )
        ownership.owners.extend(owners_to_add)

    return ownership
```

### 더 고급 기능: 변환 중 DataHub 호출

일부 고급 사례에서는 변환을 수행하기 전에 DataHub에 확인하고 싶을 수 있습니다. 좋은 예로는 ingestion 프로세스 중에 새 소유자 세트를 제공하기 전에 dataset의 현재 소유자 세트를 조회하는 것이 있습니다. transformer가 항상 그래프를 쿼리할 수 있도록 프레임워크는 context 객체 `ctx`를 통해 그래프에 대한 접근 권한을 제공합니다. 파이프라인이 REST sink를 사용할 때마다 그래프에 대한 연결이 자동으로 초기화됩니다. Kafka sink를 사용하는 경우 파이프라인에서 이를 설정하여 그래프에 대한 접근을 추가로 제공할 수 있습니다.

다음은 Kafka를 sink로 사용하지만 `datahub_api`를 명시적으로 설정하여 그래프에 대한 접근을 제공하는 recipe 예제입니다.

```yaml
source:
  type: mysql
  config:
     # ..source configs

sink:
  type: datahub-kafka
  config:
     connection:
        bootstrap: localhost:9092
	schema_registry_url: "http://localhost:8081"

datahub_api:
  server: http://localhost:8080
  # standard configs accepted by datahub rest client ...
```

#### 고급 사용 사례: Patching Owners

위 기능을 활용하여 메타데이터 변경을 실행하기 전에 서버 측 상태를 확인할 수 있는 더 강력한 transformer를 구축할 수 있습니다.
예를 들어, AddDatasetOwnership transformer가 서버에 저장된 소유자를 절대 삭제하지 않도록 PATCH semantics를 지원하는 방법은 다음과 같습니다.

```python
def transform_one(self, mce: MetadataChangeEventClass) -> MetadataChangeEventClass:
    if not isinstance(mce.proposedSnapshot, DatasetSnapshotClass):
        return mce
    owners_to_add = self.config.get_owners_to_add(mce.proposedSnapshot)
    if owners_to_add:
        ownership = builder.get_or_add_aspect(
            mce,
            OwnershipClass(
                owners=[],
            ),
        )
        ownership.owners.extend(owners_to_add)

        if self.config.semantics == Semantics.PATCH:
            assert self.ctx.graph
            patch_ownership = AddDatasetOwnership.get_ownership_to_set(
                self.ctx.graph, mce.proposedSnapshot.urn, ownership
            )
            builder.set_aspect(
                mce, aspect=patch_ownership, aspect_type=OwnershipClass
            )
    return mce
```

### Installing the package

이제 transformer를 정의했으니 DataHub에서 볼 수 있도록 만들어야 합니다. 가장 쉬운 방법은 recipe와 같은 디렉토리에 배치하는 것으로, 이 경우 모듈 이름은 파일 이름과 동일합니다 – 이 경우 `custom_transform_example`입니다.

<details>
  <summary>고급: 패키지로 설치하고 검색 가능하게 만들기</summary>
또는 transform 스크립트와 같은 디렉토리에 `setup.py`를 생성하여 전역으로 볼 수 있게 만듭니다. 이 패키지를 설치하면(예: `python setup.py` 또는 `pip install -e .`를 사용하여) 모듈이 설치되고 `custom_transform_example`로 가져올 수 있게 됩니다.

```python
from setuptools import find_packages, setup

setup(
    name="custom_transform_example",
    version="1.0",
    packages=find_packages(),
    # if you don't already have DataHub installed, add it under install_requires
    # install_requires=["acryl-datahub"],
    entry_points={
        "datahub.ingestion.transformer.plugins": [
            "custom_transform_example_alias = custom_transform_example:AddCustomOwnership",
        ],
    },
)
```

또한 setup 스크립트의 `entry_points` 변수 아래에 transformer를 선언합니다. 이를 통해 `datahub check plugins` 실행 시 transformer가 나열되고, recipe에서 사용할 transformer의 단축 별칭이 설정됩니다.

</details>

### Running the transform

```yaml
transformers:
  - type: "custom_transform_example_alias"
    config:
      owners_json: "<path_to_owners_json>" # the JSON file mentioned at the start
```

`datahub ingest -c <path_to_recipe>`를 실행하면 MCE에 다음과 같은 소유자가 추가됩니다:

```json
"owners": [
    {
        "owner": "urn:li:corpuser:athos",
        "type": "DATAOWNER",
        "source": null
    },
    {
        "owner": "urn:li:corpuser:porthos",
        "type": "DATAOWNER",
        "source": null
    },
    {
        "owner": "urn:li:corpuser:aramis",
        "type": "DATAOWNER",
        "source": null
    },
    {
        "owner": "urn:li:corpGroup:the_three_musketeers",
        "type": "DATAOWNER",
        "source": null
    },
	// ...and any additional owners
],
```

### Using this in the remote executor (DataHub Cloud only)

transformer가 포함된 이미지를 빌드합니다.

```
docker build -t acryldata:customtransform1 -f metadata-ingestion/examples/transforms/example.Dockerfile metadata-ingestion/examples/transforms
```

작동하는지 테스트합니다.

```
docker run -it --rm acryldata:customtransform1 bash
```

docker 컨테이너 내에서:

```
source venv/bin/activate
datahub ingest -c ./custom_transformer/recipe.dhub.yaml
```

이 이미지를 remote executor에 사용한다면 ingestion에서 transformer를 설치하는 추가 pip 의존성으로 `file:///datahub-executor/custom_transformer`를 설정할 수 있습니다.

이 튜토리얼의 모든 파일은 [여기](../../examples/transforms/)에서 찾을 수 있습니다.
