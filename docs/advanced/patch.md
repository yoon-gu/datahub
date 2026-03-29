import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# DataHub에 Patch 업데이트 내보내기

## Patch를 사용하는 이유

기본적으로 대부분의 SDK 튜토리얼과 API는 aspect 수준에서 전체 upsert, 즉 aspect를 완전히 교체하는 방식을 사용합니다.
이는 다른 필드를 수정하지 않고 aspect 내의 단일 필드만 변경하려면 기존 필드를 덮어쓰지 않기 위해 읽기-수정-쓰기를 수행해야 함을 의미합니다.
이러한 시나리오를 지원하기 위해, DataHub는 다른 기존 메타데이터에 영향을 주지 않고 개별 필드 또는 필드 배열 내의 값에 대한 대상 변경이 가능하도록 `PATCH` 작업을 지원합니다.

:::note

PATCH 지원은 이제 [OpenAPI](../api/openapi/openapi-usage-guide.md#generic-patching)를 통해 일반적으로 지원됩니다. 전통적인 PATCH 지원은 선택된 aspect 집합에만 사용할 수 있습니다. 지원되는 aspect의 전체 목록은 [여기](https://github.com/datahub-project/datahub/blob/master/entity-registry/src/main/java/com/linkedin/metadata/aspect/patch/template/AspectTemplateEngine.java#L23)의 `SUPPORTED_TEMPLATES` 상수로 유지됩니다.

:::

## Patch 사용 방법

Patch 빌더는 Python 및 Java SDK 모두에서 사용 가능합니다:

<Tabs groupId="sdk-language">
<TabItem value="python" label="Python SDK" default>

Python Patch 빌더는 entity 지향적이며 [metadata-ingestion](https://github.com/datahub-project/datahub/tree/9588440549f3d99965085e97b214a7dabc181ed2/metadata-ingestion/src/datahub/specific) 모듈에 위치하며 `datahub.specific` 모듈에 있습니다.
Patch 빌더 헬퍼 클래스는 다음에 대해 존재합니다:

- [Datasets](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/src/datahub/specific/dataset.py)
- [Charts](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/src/datahub/specific/chart.py)
- [Dashboards](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/src/datahub/specific/dashboard.py)
- [Data Jobs (Tasks)](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/src/datahub/specific/datajob.py)
- [Data Products](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/src/datahub/specific/dataproduct.py)

그리고 Containers, Data Flows (Pipelines), Tags, Glossary Terms, Domains, ML Models에 대한 기여를 기꺼이 받습니다.

</TabItem>
<TabItem value="java" label="Java SDK">

Java Patch 빌더는 aspect 지향적이며 `datahub.client.patch` 네임스페이스 아래의 [datahub-client](https://github.com/datahub-project/datahub/tree/master/metadata-integration/java/datahub-client/src/main/java/datahub/client/patch) 모듈에 위치합니다.

</TabItem>
</Tabs>

### Dataset에 대한 소유자 추가 및 제거

dataset에 대한 특정 소유자를 추가하고 제거하려면:

<Tabs groupId="sdk-language">
<TabItem value="python" label="Python SDK" default>

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_owner_patch.py show_path_as_comment }}
```

</TabItem>

</Tabs>

### Dataset에 대한 태그 추가 및 제거

dataset에 대한 특정 태그를 추가하고 제거하려면:

<Tabs groupId="sdk-language">
<TabItem value="python" label="Python SDK" default>

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_tag_patch.py show_path_as_comment }}
```

Dataset 내의 특정 스키마 필드에 대해서:

```python
{{ inline /metadata-ingestion/examples/library/dataset_field_add_tag_patch.py show_path_as_comment }}
```

</TabItem>

</Tabs>

### Dataset에 대한 Glossary Terms 추가 및 제거

dataset에 대한 특정 용어집 용어를 추가하고 제거하려면:

<Tabs groupId="sdk-language">
<TabItem value="python" label="Python SDK" default>

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_glossary_term_patch.py show_path_as_comment }}
```

Dataset 내의 특정 스키마 필드에 대해서:

```python
{{ inline /metadata-ingestion/examples/library/dataset_field_add_glossary_term_patch.py show_path_as_comment }}
```

</TabItem>
</Tabs>

### Dataset에 대한 구조화된 속성 추가 및 제거

dataset에 대한 구조화된 속성을 추가하고 제거하려면:

<Tabs groupId="sdk-language">
<TabItem value="python" label="Python SDK" default>

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_structured_properties_patch.py show_path_as_comment }}
```

</TabItem>

</Tabs>

### Dataset에 대한 업스트림 Lineage 추가 및 제거

dataset과 그 업스트림 또는 입력을 dataset 및 스키마 필드 수준 모두에서 연결하는 lineage 엣지를 추가하고 제거하려면:

<Tabs groupId="sdk-language">
<TabItem value="python" label="Python SDK" default>

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_upstream_lineage_patch.py show_path_as_comment }}
```

</TabItem>

</Tabs>

### Dataset에 대한 읽기 전용 커스텀 속성 추가 및 제거

dataset에 대한 특정 커스텀 속성을 추가하고 제거하려면:

<Tabs groupId="sdk-language">
<TabItem value="python" label="Python SDK" default>

```python
{{ inline /metadata-ingestion/examples/library/dataset_add_remove_custom_properties_patch.py show_path_as_comment }}
```

</TabItem>
<TabItem value="java" label="Java SDK">

```java
{{ inline /metadata-integration/java/examples/src/main/java/io/datahubproject/examples/DatasetCustomPropertiesAddRemove.java show_path_as_comment }}
```

</TabItem>
</Tabs>

### Data Job Lineage 추가 및 제거

<Tabs groupId="sdk-language">
<TabItem value="python" label="Python SDK" default>

```python
{{ inline /metadata-ingestion/examples/library/datajob_add_lineage_patch.py show_path_as_comment }}
```

</TabItem>
<TabItem value="java" label="Java SDK">

```java
{{ inline /metadata-integration/java/examples/src/main/java/io/datahubproject/examples/DataJobLineageAdd.java show_path_as_comment }}
```

</TabItem>
</Tabs>

## 고급: Patch가 작동하는 방법

patching이 어떻게 작동하는지 이해하려면 [모델](../what/aspect.md)에 대해 조금 이해하는 것이 중요합니다. entity는 객체 모델의 JSON 표현으로 추론할 수 있는 Aspect들로 구성됩니다. 이것들을 patch할 수 있도록 [JsonPatch](https://jsonpatch.com/)를 활용합니다. JSON Patch의 구성 요소는 경로, 작업, 값입니다.

### 경로

JSON 경로는 스키마 내의 값을 참조합니다. 이는 경로가 무엇인지에 따라 단일 필드 또는 전체 객체 참조가 될 수 있습니다.
patch의 경우 주로 필드 내의 단일 필드 또는 단일 배열 요소를 대상으로 합니다. id로 배열 요소를 대상으로 하기 위해, 배열을 맵으로 변환하는 스키마의 변환 프로세스를 거칩니다. 이를 통해 경로가 인덱스가 아닌 키로 특정 배열 요소를 참조할 수 있습니다. 예를 들어 dataset에 추가되는 특정 태그 urn이 있습니다.

#### 예시

업스트림 dataset을 대상으로 하는 patch 경로:

`/upstreams/urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created_upstream,PROD)`

분석:

- `/upstreams` -> Urn이 키인 Upstream 객체의 배열인 UpstreamLineage aspect의 upstreams 필드를 참조합니다.
- `/urn:...` -> 작업으로 대상이 되는 dataset

세분화된 lineage upstream을 대상으로 하는 patch 경로:

`/fineGrainedLineages/TRANSFORM/urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD),foo)/urn:li:query:queryId/urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created_upstream,PROD),bar)`

분석:

- `/fineGrainedLineages` -> transformOperation, 다운스트림 urn, 쿼리 urn을 키로 하는 FineGrainedLineage 객체의 배열인 UpstreamLineage의 fineGrainedLineages 필드를 참조합니다.
- `/TRANSFORM` -> transformOperation, fineGrainedLineage의 키를 결정하는 필드 중 하나
- `/urn:li:schemaField:...` -> 이 스키마에서 참조되는 다운스트림 schemaField, fineGrainedLineage의 키의 일부
- `/urn:li:query:...` -> 이 관계가 파생된 쿼리 urn, fineGrainedLineage의 키의 일부
- `/urn:li:schemaField:` -> 이 patch 작업으로 대상이 되는 업스트림 urn

이는 일부 경우 객체의 키가 간단하고, 다른 경우에는 결정하기 복잡할 수 있지만, 완전히 지원되는 사용 사례에서는 필요한 메서드 매개변수를 제공하는 한 Java 및 Python 측 모두에서 이러한 patch를 생성하는 SDK 지원이 있습니다.
경로는 일반적으로 스키마와 JSON 경로 탐색에 대한 심층적인 지식이 필요하기 때문에 patch에서 추론하기 가장 복잡한 부분입니다.

### 작업

작업은 JSON Patch 명세에서 직접 가져온 몇 가지 지원 타입으로 제한된 열거형입니다. DataHub는 이러한 옵션 중 현재 시스템 내에서 사용 사례가 없는 다른 patch 작업은 지원하지 않으므로 `ADD`와 `REMOVE`만 지원합니다.

#### Add

Add는 JSON Patch 명세에서 다소 잘못된 이름으로, 명시적인 추가가 아닌 upsert/교체입니다. 지정된 경로가 존재하지 않으면 생성되지만, 경로가 이미 존재하면 값이 교체됩니다. Patch 작업은 경로 수준에서 적용되므로 add를 사용하여 스키마에서 배열이나 객체를 완전히 교체하는 것이 가능하지만, 일반적으로 patch의 가장 유용한 사용 사례는 전체 upsert가 표준 수집으로 지원되므로 다른 요소에 영향을 주지 않고 배열에 요소를 추가하는 것입니다.

#### Remove

Remove 작업은 지정된 경로가 존재해야 하며, 그렇지 않으면 오류가 발생하고, 그렇지 않으면 예상대로 작동합니다. 지정된 경로가 aspect에서 제거됩니다.

### 값

값은 경로에 저장될 실제 정보입니다. 경로가 객체를 참조하면 해당 객체의 JSON 키-값 쌍이 포함됩니다.

#### 예시

UpstreamLineage 객체 값의 예시:

```json
{
  "auditStamp": {
    "time": 0,
    "actor": "urn:li:corpuser:unknown"
  },
  "dataset": "urn:li:dataset:(urn:li:dataPlatform:s3,my-bucket/my-folder/my-file.txt,PROD)",
  "type": "TRANSFORMED"
}
```

이전 경로 예시(`/upstreams/urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created_upstream,PROD)`)의 경우, 이 객체는 해당 경로에 대한 UpstreamLineage 객체를 나타냅니다.
이는 해당 객체를 올바르게 나타내는 데 필요한 필드를 지정합니다. 참고: 이 경로를 수정하면 다음과 같이 UpstreamLineage 객체 자체 내의 단일 필드를 참조할 수 있습니다:

```json
{
  "path": "/upstreams/urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created_upstream,PROD)/type",
  "op": "ADD",
  "value": "VIEW"
}
```

### 구현 세부 사항

#### 템플릿 클래스

템플릿 클래스는 필드를 해당 JSON 경로에 매핑하는 메커니즘입니다. DataMap은 진정한 JSON이 아니므로, 먼저 RecordTemplate을 JSON 문자열로 변환하고, 배열 필드를 키에 매핑하는 추가 처리를 수행하고, patch를 적용한 다음, JSON 객체를 다시 RecordTemplate으로 변환하여 나머지 애플리케이션과 함께 작업합니다.

현재 지원하는 템플릿 클래스는 `entity-registry` 모듈에서 찾을 수 있습니다. GenericTemplate이 직접 지원되지 않는 모든 aspect에 적용되는 것과 함께 aspect별로 분리됩니다.
GenericTemplate은 아직 직접 지원하지 못한 사용 사례를 허용하지만, 사용자가 올바르게 patch를 생성하는 부담이 더 큽니다.

템플릿 클래스는 MCP가 patch인지 표준 upsert인지 결정하는 `EntityServiceImpl`에서 활용되며, 그런 다음 EntityRegistry에 등록된 저장된 템플릿으로 라우팅됩니다.
각 템플릿이 실행하는 핵심 로직 흐름은 `Template` 인터페이스에 설정되어 있으며, 배열 필드 키 구성/해체를 위한 하위 수준 인터페이스에 더 구체적인 로직이 있습니다.
이 클래스들 주변의 복잡성의 대부분은 스키마 및 JSON 경로 탐색에 대한 지식입니다.

##### ArrayMergingTemplate & CompoundKeyTemplate

`ArrayMergingTemplate`은 배열 필드가 있는 모든 aspect에 사용되며 직접 사용되거나 `CompoundKeyTemplate`을 사용할 수 있습니다. `ArrayMergingTemplate`은 단일 값 키에만 직접 사용할 수 있는 더 간단한 것입니다. `CompoundKeyTemplate`은 다중 필드 키 지원을 허용합니다. FineGrainedLineage와 같은 더 복잡한 예시의 경우 다른 aspect로 일반화할 수 없어 키를 구성하기 위한 추가 로직이 필요합니다. 전체 특수 케이스 구현은 `UpstreamLineageTemplate`을 참조하세요.

#### PatchBuilders

Java와 Python 모두에서 patch를 구성하기 위한 patch 빌더 SDK 클래스가 있습니다. Java patch 빌더는 모두 patch 빌더 서브타입을 위한 기본 기능을 설정하는 `AbstractMultiFieldPatchBuilder`를 확장합니다. 이 추상 클래스의 각 구현은 특정 aspect를 대상으로 하며 가장 일반적인 사용 사례에 대한 특정 필드 기반 업데이트 메서드를 포함합니다. Python 측에서 patch 빌더는 `src/specific/` 디렉토리에 있으며 entity 타입별로 구성됩니다.
