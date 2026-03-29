---
slug: /metadata-modeling/extending-the-metadata-model
---

# 메타데이터 모델 확장하기

새로운 entity를 생성하거나 기존 entity를 확장하여 메타데이터 모델을 확장할 수 있습니다. 새 entity를 생성해야 할지, 기존 entity에 aspect를 추가해야 할지 확실하지 않으신가요? 변경하기 전에 [metadata-model](./metadata-model.md)을 읽어 이 두 가지 개념을 이해하세요.

## 포크할 것인가, 말 것인가?

메타데이터 모델을 확장하기로 결정한 후 발생하는 중요한 질문은 메인 저장소를 포크해야 하는지 여부입니다. 아래 다이어그램을 사용하여 이 결정을 내리는 방법을 이해하세요.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/metadata-model-to-fork-or-not-to.png"/>
</p>

초록색 선은 장기적으로 코드를 유지 관리하는 데 마찰이 적은 경로를 나타냅니다. 빨간색 선은 향후 충돌 위험이 높은 경로를 나타냅니다. 저희는 커스텀 DataHub 포크를 유지 관리하지 않고도 핵심 메타데이터 모델을 확장할 수 있도록 대부분의 모델 확장 사용 사례를 코드 없음/저코드 방식으로 이동하기 위해 노력하고 있습니다.

이 문서의 나머지 부분에서 두 가지 옵션을 **오픈소스 포크**와 **커스텀 저장소** 방식으로 부르겠습니다.

## 이 가이드에 대해

이 가이드는 Dashboard entity를 추가하는 실제 예시를 통해 새 entity를 추가하는 경험이 어떻게 이루어지는지 설명합니다. 기존 entity를 확장하려는 경우 바로 [3단계](#step-3-define-custom-aspects-or-attach-existing-aspects-to-your-entity)로 건너뛸 수 있습니다.

높은 수준에서, entity는 다음으로 구성됩니다:

1. Key Aspect: entity의 인스턴스를 고유하게 식별합니다.
2. entity에 첨부되는 관련 속성 그룹인 지정된 aspect 목록.

## Entity 정의하기

이제 메타데이터 모델에 대한 확장을 생성, 수집, 조회하는 데 필요한 단계를 살펴보겠습니다. 설명을 위해 기존 "Dashboard" entity를 사용하겠습니다.

### <a name="step_1"></a>1단계: Entity Key Aspect 정의하기

key는 entity를 고유하게 식별하는 필드를 나타냅니다. DataHub의 레거시 아키텍처에 익숙한 분들은 이 필드들이 이전에는 각 entity에 대해 정의된 Urn Java 클래스의 일부였다는 것을 알 것입니다.

이 구조체는 Urn으로 표현되는 직렬화된 문자열 키를 생성하는 데 사용됩니다. key 구조체의 각 필드는 정의된 순서대로 Urn의 튜플의 단일 부분으로 변환됩니다.

새로운 Dashboard entity에 대한 Key aspect를 정의해 보겠습니다.

```
namespace com.linkedin.metadata.key

/**
 * Key for a Dashboard
 */
@Aspect = {
  "name": "dashboardKey",
}
record DashboardKey {
  /**
  * The name of the dashboard tool such as looker, redash etc.
  */
  @Searchable = {
    ...
  }
  dashboardTool: string

  /**
  * Unique id for the dashboard. This id should be globally unique for a dashboarding tool even when there are multiple deployments of it. As an example, dashboard URL could be used here for Looker such as 'looker.linkedin.com/dashboards/1234'
  */
  dashboardId: string
}

```

위에 표시된 Key의 Urn 표현은 다음과 같습니다:

```
urn:li:dashboard:(<tool>,<id>)
```

key는 aspect이므로 @Aspect 어노테이션으로 어노테이션해야 합니다. 이는 DataHub에게 이 구조체가 일부가 될 수 있음을 지시합니다.

key에는 두 가지 인덱스 어노테이션인 @Relationship과 @Searchable도 어노테이션할 수 있습니다. 이는 DataHub 인프라에게 key의 필드를 사용하여 관계를 생성하고 검색을 위한 필드를 인덱싱하도록 지시합니다. 어노테이션 모델에 대한 자세한 내용은 [3단계](#step-3-define-custom-aspects-or-attach-existing-aspects-to-your-entity)를 참조하세요.

**제약사항**: Key Aspect의 각 필드는 반드시 String 또는 Enum 타입이어야 합니다.

### <a name="step_2"></a>2단계: key aspect와 함께 새 entity 만들기

`entity-registry.yml` 파일 내에서 entity를 정의합니다. 접근 방식에 따라 이 파일의 위치가 달라질 수 있습니다. 자세한 내용은 [4단계](#step-4-choose-a-place-to-store-your-model-extension)와 [5단계](#step-5-attaching-your-non-key-aspects-to-the-entity)를 참조하세요.

예시:

```yaml
- name: dashboard
  doc: A container of related data assets.
  keyAspect: dashboardKey
```

- name: entity 이름/타입, Urn의 일부로 표시됩니다.
- doc: entity에 대한 간단한 설명.
- keyAspect: 1단계에서 정의한 Key Aspect의 이름. 이 이름은 PDL 어노테이션의 값과 일치해야 합니다.

#

### <a name="step_3"></a>3단계: 커스텀 aspect 정의 또는 entity에 기존 aspect 첨부하기

Ownership 및 GlobalTags와 같은 일부 aspect는 entity 간에 재사용 가능합니다. 이들은 entity의 aspect 집합에 자유롭게 포함될 수 있습니다. 기존 aspect에 포함되지 않은 속성을 포함하려면 새 aspect를 만들어야 합니다.

새 aspect에 무엇이 들어가는지에 대한 예시로 DashboardInfo aspect를 살펴보겠습니다.

```
namespace com.linkedin.dashboard

import com.linkedin.common.AccessLevel
import com.linkedin.common.ChangeAuditStamps
import com.linkedin.common.ChartUrn
import com.linkedin.common.Time
import com.linkedin.common.Url
import com.linkedin.common.CustomProperties
import com.linkedin.common.ExternalReference

/**
 * Information about a dashboard
 */
@Aspect = {
  "name": "dashboardInfo"
}
record DashboardInfo includes CustomProperties, ExternalReference {

  /**
   * Title of the dashboard
   */
  @Searchable = {
    "fieldType": "TEXT_WITH_PARTIAL_MATCHING",
    "queryByDefault": true,
    "enableAutocomplete": true,
    "boostScore": 10.0
  }
  title: string

  /**
   * Detailed description about the dashboard
   */
  @Searchable = {
    "fieldType": "TEXT",
    "queryByDefault": true,
    "hasValuesFieldName": "hasDescription"
  }
  description: string

  /**
   * Charts in a dashboard
   */
  @Relationship = {
    "/*": {
      "name": "Contains",
      "entityTypes": [ "chart" ]
    }
  }
  charts: array[ChartUrn] = [ ]

  /**
   * Captures information about who created/last modified/deleted this dashboard and when
   */
  lastModified: ChangeAuditStamps

  /**
   * URL for the dashboard. This could be used as an external link on DataHub to allow users access/view the dashboard
   */
  dashboardUrl: optional Url

  /**
   * Access level for the dashboard
   */
  @Searchable = {
    "fieldType": "KEYWORD",
    "addToFilters": true
  }
  access: optional AccessLevel

  /**
   * The time when this dashboard last refreshed
   */
  lastRefreshed: optional Time
}
```

Aspect는 네 가지 핵심 구성 요소를 가집니다: 속성, @Aspect 어노테이션, @Searchable 어노테이션, @Relationship 어노테이션. 각각을 분석해 보겠습니다:

- **Aspect 속성**: 레코드의 속성은 레코드의 필드로 선언하거나, Aspect의 정의에 다른 레코드를 포함시켜 선언할 수 있습니다(`record DashboardInfo includes CustomProperties, ExternalReference {`). 속성은 PDL 기본 타입, 열거형, 레코드, 컬렉션([pdl 스키마 문서](https://linkedin.github.io/rest.li/pdl_schema) 참조), 다른 entity에 대한 참조(Urn 타입 또는 선택적으로 `<Entity>Urn`)로 정의할 수 있습니다.
- **@Aspect 어노테이션**: 레코드가 Aspect임을 선언하고 entity를 직렬화할 때 포함시킵니다. 다음 두 어노테이션과 달리, @Aspect는 특정 필드가 아닌 전체 레코드에 적용됩니다. 참고로, aspect를 timeseries aspect로 표시할 수 있습니다. 자세한 내용은 이 [문서](metadata-model.md#timeseries-aspects)를 참조하세요.
- **@Searchable 어노테이션**: 이 어노테이션은 기본 필드나 맵 필드에 적용하여 Elasticsearch에 인덱싱하고 검색할 수 있음을 나타낼 수 있습니다. 검색 어노테이션 사용에 대한 완전한 가이드는 이 문서 아래 어노테이션 문서를 참조하세요.
- **@Relationship 어노테이션**: 이 어노테이션은 entity가 수집될 때 entity의 Urn과 어노테이션된 필드의 대상 사이에 엣지를 생성합니다. @Relationship 어노테이션은 Urn 타입의 필드에 적용해야 합니다. DashboardInfo의 경우, `charts` 필드는 Urn의 배열입니다. @Relationship 어노테이션은 Urn 배열에 직접 적용할 수 없습니다. 그래서 @Relationship 어노테이션을 Urn에 직접 적용하기 위해 어노테이션 오버라이드(`"/*":`)를 사용합니다. 오버라이드에 대한 자세한 내용은 이 페이지 아래 어노테이션 문서를 참조하세요.
- **@UrnValidation**: 이 어노테이션은 entity 타입 제한 및 존재를 포함하여 Urn 필드에 제약 조건을 강제할 수 있습니다.

Aspect를 만든 후에는 적용되는 모든 entity에 첨부해야 합니다.

**제약사항**: 모든 aspect는 반드시 Record 타입이어야 합니다.

### <a name="step_4"></a>4단계: 모델 확장을 저장할 위치 선택하기

이 문서의 시작 부분에서 모델 확장을 위해 오픈소스 DataHub 저장소의 포크를 유지해야 하는지, 아니면 DataHub 저장소와 독립적으로 유지될 수 있는 모델 확장 저장소를 사용해도 되는지 결정하는 데 도움이 되는 순서도를 안내했습니다. 어떤 경로를 선택했느냐에 따라 aspect 모델 파일(.pdl 파일)과 entity-registry 파일(`entity-registry.yaml` 또는 `entity-registry.yml`이라는 yaml 파일)을 저장하는 위치가 달라집니다.

- 오픈소스 포크: Aspect 파일은 메인 저장소의 [`metadata-models`](../../metadata-models) 모듈 아래에, entity registry는 [`metadata-models/src/main/resources/entity-registry.yml`](../../metadata-models/src/main/resources/entity-registry.yml)에 저장됩니다. 자세한 내용은 [5단계](#step-5-attaching-your-non-key-aspects-to-the-entity)를 참조하세요.
- 커스텀 저장소: [metadata-models-custom](../../metadata-models-custom/README.md) 문서를 읽어 aspect 모델과 registry를 저장하고 버전 관리하는 방법을 알아보세요.

### <a name="step_5"></a>5단계: 비-key Aspect를 entity에 첨부하기

비-key aspect를 entity에 첨부하는 것은 entity registry yaml 파일에 추가하기만 하면 됩니다. 이 파일의 위치는 oss-fork 경로를 따르는지 custom-repository 경로를 따르는지에 따라 다릅니다.

다음은 새로운 `DashboardInfo` aspect를 `Dashboard` entity에 추가하는 최소한의 예시입니다.

```yaml
entities:
   - name: dashboard
   - keyAspect: dashBoardKey
   aspects:
     # aspect의 이름은 클래스의 @Aspect 어노테이션과 동일해야 합니다
     - dashboardInfo
```

이전에는 entity의 모든 aspect를 Aspect union에 추가해야 했습니다. 코드베이스 전반에 걸쳐 이 패턴의 예시를 볼 수 있습니다(예: `DatasetAspect`, `DashboardAspect` 등). 이제 이것은 더 이상 필요하지 않습니다.

### <a name="step_6"></a>6단계 (Oss-Fork 방식): 새로운 또는 업데이트된 entity에 접근하기 위해 DataHub 재빌드하기

DataHub의 `metadata-models` 저장소에서 모델을 편집하는 오픈소스 포크 방식을 선택한 경우, 아래 단계를 사용하여 DataHub 메타데이터 서비스를 재빌드해야 합니다. 커스텀 모델 저장소 방식을 따르는 경우에는 커스텀 모델 저장소만 빌드하고 실행 중인 메타데이터 서비스 인스턴스에 배포하여 새 모델 확장을 사용하여 메타데이터를 읽고 쓸 수 있습니다.

oss-fork 옵션을 위해 DataHub를 재빌드하는 방법을 이해하려면 계속 읽으세요.

**_참고_**: 기존 타입을 업데이트했거나 빌드 시 `Incompatible changes` 경고가 표시되는 경우, `build`를 실행하기 전에 다음을 실행해야 합니다:
`./gradlew :metadata-service:restli-servlet-impl:build -Prest.model.compatibility=ignore`

그런 다음, 저장소 루트에서 `./gradlew build`를 실행하여 새 entity에 접근할 수 있는 DataHub를 재빌드합니다.

그런 다음, metadata-service(gms), mae-consumer, mce-consumer(번들되지 않은 상태로 실행하는 경우 선택적으로)를 재배포합니다. 개발 중에 배포하는 방법에 대한 자세한 내용은 [도커 개발](../../docker/README.md)을 참조하세요. 이렇게 하면 DataHub가 새 entity 또는 기존 entity에 대한 확장을 읽고 쓸 수 있게 되며, 해당 entity 타입에 대한 검색 및 그래프 쿼리를 서빙할 수 있습니다.

### <a name="step_7"></a>(선택 사항) 7단계: Python SDK와 커스텀 모델 사용하기

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs queryString="python-custom-models">
<TabItem value="local" label="로컬 CLI" default>

커스텀 모델을 로컬에서만 사용하는 경우, DataHub CLI의 로컬 개발 모드 설치를 사용할 수 있습니다.

[개발자 지침](../../metadata-ingestion/developing.md)에 따라 DataHub CLI를 로컬로 설치합니다.
`./gradlew build` 명령은 이미 로컬 수집 cli 도구가 사용할 avro 스키마를 생성했습니다.
개발 가이드를 따른 후, 로컬 DataHub CLI를 사용하여 새 이벤트를 내보낼 수 있어야 합니다.

</TabItem>
<TabItem value="packaged" label="커스텀 모델 패키지">

DataHub를 포크하지 않고 로컬 머신 이외에서 커스텀 모델을 사용하려면, 다른 위치에서 설치할 수 있는 커스텀 모델 패키지를 생성할 수 있습니다.

이 패키지는 기본 `acryl-datahub` 패키지와 함께 설치해야 하며, 해당 메타데이터 모델은 기본 모델보다 우선합니다.

```bash
$ cd metadata-ingestion
$ ../gradlew customPackageGenerate -Ppackage_name=my-company-datahub-models -Ppackage_version="0.0.1"
<bunch of log lines>
Successfully built my-company-datahub-models-0.0.1.tar.gz and acryl_datahub_cloud-0.0.1-py3-none-any.whl

Generated package at custom-package/my-company-datahub-models
This package should be installed alongside the main acryl-datahub package.

Install the custom package locally with `pip install custom-package/my-company-datahub-models`
To enable others to use it, share the file at custom-package/my-company-datahub-models/dist/<wheel file>.whl and have them install it with `pip install <wheel file>.whl`
Alternatively, publish it to PyPI with `twine upload custom-package/my-company-datahub-models/dist/*`
```

이것은 팀 내에서 배포하거나 PyPI에 게시할 수 있는 Python 빌드 아티팩트를 생성합니다.
명령 출력에는 사용할 수 있는 추가 세부 정보와 정확한 CLI 명령이 포함됩니다.

이 패키지가 설치되면 DataHub CLI를 정상적으로 사용할 수 있으며 커스텀 모델을 사용합니다.
임포트를 변경하여 IDE 지원으로 해당 모델을 임포트할 수도 있습니다.

```diff
- from datahub.metadata.schema_classes import DatasetPropertiesClass
+ from my_company_datahub_models.metadata.schema_classes import DatasetPropertiesClass
```

</TabItem>
</Tabs>

### <a name="step_8"></a>(선택 사항) 8단계: GraphQL 및 React에서 entity를 보기 위해 DataHub 프론트엔드 확장하기

추가적인 aspect로 entity를 확장하는 경우, 자동 렌더링 사양을 사용하여 이러한 aspect를 만족스럽게 자동 렌더링할 수 있다면 커스텀 코드를 작성할 필요가 없습니다.

그러나 모델 확장을 렌더링하기 위해 특정 코드를 작성하거나, 완전히 새로운 entity를 도입하여 고유한 페이지를 제공하려면 GraphQL 또는 React에서 entity를 보고 변경하기 위한 커스텀 React 및 GraphQL 코드를 작성해야 합니다. GraphQL 그래프 확장을 시작하는 방법에 대한 지침은 [graphql 문서](../../datahub-graphql-core/README.md)를 참조하세요. 그런 다음, [여기](../../datahub-web-react/README.md)의 가이드를 따라 React UI에 entity를 추가할 수 있습니다.

## 메타데이터 어노테이션

DataHub가 인식하는 네 가지 핵심 어노테이션이 있습니다:

#### @Entity

**레거시**
이 어노테이션은 DashboardSnapshot.pdl과 같은 각 Entity Snapshot 레코드에 적용됩니다. 루트 Snapshot.pdl 모델에 포함된 각 항목은 이 어노테이션을 가져야 합니다.

다음 매개변수를 취합니다:

- **name**: string - entity를 식별하는 데 사용되는 일반 이름. DataHub가 인식하는 모든 entity 중에서 고유해야 합니다.

##### 예시

```aidl
@Entity = {
  // API에서 entity를 참조할 때 사용되는 이름.
  String name;
}
```

#### @Aspect

이 어노테이션은 DashboardInfo.pdl과 같은 각 Aspect 레코드에 적용됩니다. `entity-registry.yml`에서 entity의 aspect 집합에 포함된 각 aspect는 이 어노테이션을 가져야 합니다.

다음 매개변수를 취합니다:

- **name**: string - Aspect를 식별하는 데 사용되는 일반 이름. DataHub가 인식하는 모든 aspect 중에서 고유해야 합니다.
- **type**: string (선택 사항) - 이 aspect를 timeseries로 표시하려면 "timeseries"로 설정합니다. 자세한 내용은 이 [문서](metadata-model.md#timeseries-aspects)를 참조하세요.
- **autoRender**: boolean (선택 사항) - 기본값은 false입니다. true로 설정하면 aspect가 기본 렌더러를 사용하여 탭에서 entity 페이지에 자동으로 표시됩니다. **_현재 Charts, Dashboards, DataFlows, DataJobs, Datasets, Domains, GlossaryTerms에만 지원됩니다_**.
- **renderSpec**: RenderSpec (선택 사항) - autoRender aspect가 표시되는 방법을 제어하는 구성입니다. **_현재 Charts, Dashboards, DataFlows, DataJobs, Datasets, Domains, GlossaryTerms에만 지원됩니다_**. 세 가지 필드를 포함합니다:
  - **displayType**: `tabular`, `properties` 중 하나. Tabular는 데이터 요소 목록에 사용하고, properties는 단일 데이터 묶음에 사용합니다.
  - **displayName**: UI에서 aspect를 어떻게 지칭할지. entity 페이지의 탭 이름을 결정합니다.
  - **key**: `tabular` aspect에만 해당. 렌더링할 배열을 찾을 수 있는 키를 지정합니다.

##### 예시

```aidl
@Aspect = {
  // API에서 aspect를 참조할 때 사용되는 이름.
  String name;
}
```

#### @Searchable

이 어노테이션은 Aspect 내의 필드에 적용됩니다. DataHub에게 검색 API를 통해 검색될 수 있도록 해당 필드를 Elasticsearch에 인덱싱하도록 지시합니다.

:::note 이미 데이터가 있는 필드에 @Searchable을 추가하는 경우, [api를 통해](https://docs.datahub.com/docs/api/restli/restore-indices/) 또는 [업그레이드 단계를 통해](https://github.com/datahub-project/datahub/blob/master/metadata-service/factories/src/main/java/com/linkedin/metadata/boot/steps/RestoreGlossaryIndices.java) 인덱스를 복원하여 기존 데이터로 채워야 합니다.

다음 매개변수를 취합니다:

- **fieldType**: string - 각 필드가 인덱싱되는 방식에 대한 설정은 필드 타입으로 정의됩니다. 일반적으로 이는 Elasticsearch 문서에서 필드가 인덱싱되는 방식을 정의합니다. **참고**: 새로운 검색 티어 시스템에서 `fieldType`은 주로 필드의 저장 형식과 개별 쿼리 기능을 결정합니다. 전체 텍스트 검색 기능은 이제 주로 티어 할당에 따라 여러 aspect의 필드를 통합하는 공통 `_search.tier_{tier}` 필드에 의해 처리됩니다.

  **사용 가능한 필드 타입:**

  1. _KEYWORD_ - 정확한 일치만 지원하는 짧은 텍스트 필드, 종종 필터링에만 사용됩니다. **기본 길이 제한**: 100자(티어 필드), 255자(일반 필드).

  2. _TEXT_ - 공백/슬래시/마침표로 구분되는 텍스트 필드. 문자열 변수의 기본 필드 타입. **기본 길이 제한**: 100자(티어 필드), 255자(일반 필드).

  3. _BOOLEAN_ - 필터링에 사용되는 불린 필드.

  4. _COUNT_ - 필터링에 사용되는 카운트 필드.

  5. _DATETIME_ - 타임스탬프를 나타내는 데 사용되는 날짜/시간 필드.

  6. _OBJECT_ - 객체의 각 속성은 Elasticsearch에서 추가 열이 되며 쿼리에서 `field.property`로 참조할 수 있습니다. **기본 제한**: 최대 1000개의 객체 키, 값당 최대 4096자. 많은 속성을 가진 객체에 사용하면 Elasticsearch에서 매핑 폭발이 발생할 수 있으므로 주의하세요.

  7. _DOUBLE_ - 필터링 및 계산에 사용되는 배정밀도 수치 필드.

  8. _MAP_ARRAY_ - Elasticsearch에서 맵으로 저장되는 배열 필드. **기본 제한**: 최대 1000개의 배열 요소, 값당 최대 4096자.

  **⚠️ 더이상 사용되지 않는 필드 타입 (새 코드에서 사용 금지):**

  10. ~~_TEXT_PARTIAL_~~ - **사용 중단**: 부분 매칭을 지원하는 텍스트 필드. 이 필드 타입은 비용이 많이 들며 긴 값이 있는 필드에 적용해서는 안 됩니다. 대신 TEXT를 사용하세요.

  11. ~~_WORD_GRAM_~~ - **사용 중단**: 단어 gram 지원이 있는 텍스트 필드. 이 필드 타입은 비용이 많이 들며 긴 값이 있는 필드에 적용해서는 안 됩니다. 대신 TEXT를 사용하세요.

  12. ~~_BROWSE_PATH_~~ - **사용 중단**: browse path의 필드 타입. Browse path는 이름으로 처리되며 `browsePathV2` 필드 이름을 사용합니다. 주어진 entity에 대해 하나만 있을 수 있습니다.

  13. ~~_URN_~~ - **사용 중단**: 각 하위 구성 요소가 인덱싱되는 Urn 필드. 대신 KEYWORD를 사용하세요.

  14. ~~_URN_PARTIAL_~~ - **사용 중단**: 부분 매칭을 지원하는 Urn 필드. 대신 KEYWORD를 사용하세요.

**⚠️ 중요한 길이 제한:**

- **티어 필드**: `searchTier`가 있는 필드는 검색 성능 최적화를 위해 자동으로 **100자**로 제한됩니다.
- **일반 필드**: `searchTier`가 없는 필드는 Elasticsearch 호환성을 위해 **255자**로 제한됩니다.
- **객체 필드**: 매핑 폭발을 방지하기 위해 최대 **1000개의 객체 키** 및 **값당 4096자**
- **배열 필드**: 최대 **1000개의 배열 요소** 및 **값당 4096자**
- **필드 이름**: Elasticsearch 필드 이름 호환성을 위해 최대 **255자**

**설정 재정의:**

- **환경 변수**: 일부 제한은 환경 변수를 통해 설정할 수 있습니다:
  - `SEARCH_DOCUMENT_MAX_VALUE_LENGTH`: 객체/배열 값의 기본 4096자 제한을 재정의합니다.
  - `SEARCH_DOCUMENT_MAX_ARRAY_LENGTH`: 배열의 기본 1000개 요소 제한을 재정의합니다.
  - `SEARCH_DOCUMENT_MAX_OBJECT_KEYS`: 객체의 기본 1000개 키 제한을 재정의합니다.
- **특수 필드**: 일부 시스템 필드는 다른 제한을 가집니다:
  - **URN 필드**: 자동으로 **512자**로 설정됩니다(`ignore_above: 512`)
  - **티어 필드**: 성능 최적화를 위해 **100자**로 하드 코딩됩니다.

**참고**: `ignore_above` 설정은 시스템에 의해 자동으로 적용됩니다. 일부 제한은 환경 변수를 통해 설정할 수 있지만, 티어 필드 제한(100자)과 일반 필드 제한(255자)은 하드 코딩되어 있으며 어노테이션이나 설정을 통해 재정의할 수 없습니다.

**중요**: 더 긴 키워드 필드를 가지는 기능은 시스템 수준 설정과 특수 필드 타입으로 제한됩니다. 일반 사용자 정의 필드는 항상 성능 및 호환성 이유로 기본 제한을 적용받습니다.

- **fieldName**: string (선택 사항) - 검색 인덱스 문서에서 필드의 이름. 기본값은 어노테이션이 위치한 필드 이름입니다.

- **queryByDefault**: boolean (선택 사항) - **⚠️ 사용 중단**: 기본 검색 쿼리에 대해 필드를 매칭할지 여부. 텍스트 및 urn 필드의 경우 기본값은 true입니다. **더 나은 검색 구성 및 성능을 위해 `searchTier`를 대신 사용하세요.**

- **enableAutocomplete**: boolean (선택 사항) - **⚠️ 사용 중단**: 자동 완성에 필드를 사용할지 여부. 기본값은 false입니다. **자동 완성 필드가 검색 관련성에 매우 중요하다는 사실에 기반하여 `searchTier: 1`을 사용하세요.**

- **addToFilters**: boolean (선택 사항) - 필터에 필드를 추가할지 여부. 기본값은 false입니다.

- **addHasValuesToFilters**: boolean (선택 사항) - 필터에 "has values"를 추가할지 여부. 기본값은 true입니다.

- **filterNameOverride**: string (선택 사항) - UI에서 필터의 표시 이름.

- **hasValuesFilterNameOverride**: string (선택 사항) - UI에서 "has values" 필터의 표시 이름.

- **boostScore**: double (선택 사항) - **⚠️ 사용 중단**: 일치 점수에 대한 부스트 배수. boost score가 높은 필드의 일치가 더 높은 순위를 가집니다. **더 정교한 순위 제어를 위해 `searchLabel`을 사용하세요.**

- **hasValuesFieldName**: string (선택 사항) - 설정된 경우, 필드가 존재하는지 확인하는 주어진 이름의 인덱스 필드를 추가합니다.

- **numValuesFieldName**: string (선택 사항) - 설정된 경우, 요소 수를 확인하는 주어진 이름의 인덱스 필드를 추가합니다.

- **weightsPerFieldValue**: map[object, double] (선택 사항) - **⚠️ 사용 중단**: 주어진 값에 대한 점수에 적용할 가중치. **값 기반 점수 매기기를 위해 `searchLabel`과 `@SearchScore` 어노테이션을 사용하세요.**

- **fieldNameAliases**: array[string] (선택 사항) - 정렬 및 기타 작업에 사용할 수 있는 이 필드의 별칭. 이 별칭은 aspect 이름 접두사와 함께 생성됩니다(예: `metadata.aliasName`). 동일한 필드 데이터에 접근하는 여러 경로를 만드는 데 유용합니다.

- **includeSystemModifiedAt**: boolean (선택 사항) - **⚠️ 사용 중단**: 이 검색 가능한 필드에 대해 시스템 수정 타임스탬프 필드를 포함할지 여부. **향후 버전에서 모든 aspect에 대해 프로그래밍 방식으로 처리됩니다.**

- **systemModifiedAtFieldName**: string (선택 사항) - **⚠️ 사용 중단**: 시스템 수정 타임스탬프 필드의 커스텀 이름. **향후 버전에서 모든 aspect에 대해 표준화됩니다.**

- **includeQueryEmptyAggregation**: boolean (선택 사항) - 해당 필드 쿼리 시 누락된 필드 집계를 생성할지 여부. 쿼리 시간에만 영향을 미치며 매핑에는 영향을 주지 않습니다. 분석 및 리포팅에 유용합니다.

- **searchTier**: integer (선택 사항) - 필드에 대한 검색 티어(1 이상의 정수 값). `_search.tier_{tier}`로 필드 값을 복사하는 copy_to 필드를 만듭니다. searchTier가 있는 필드는 `searchIndexed`가 true가 아닌 한 자동으로 `index: false`로 설정됩니다. **참고**: searchTier는 KEYWORD 또는 TEXT 필드 타입에만 사용할 수 있습니다.

- **searchLabel**: string (선택 사항) - 검색 작업을 위한 통합 레이블. `_search.{label}`(접두사 없음)로 필드 값을 복사하는 copy_to 필드를 만듭니다. 이전 `sortLabel` 및 `boostLabel` 어노테이션을 대체합니다. searchLabel이 있는 필드는 자동으로 `index: false`로 설정됩니다.

- **searchIndexed**: boolean (선택 사항) - `searchTier`와 결합하면, 직접 접근을 위해 `_search` 외부에서 필드가 인덱싱되는지 여부를 결정합니다. 필드는 KEYWORD로 강제되지 않고 실제 필드 타입(KEYWORD 또는 TEXT)을 사용하여 인덱싱됩니다. **참고**: searchIndexed는 searchTier가 지정된 경우에만 true가 될 수 있으며 KEYWORD 또는 TEXT 필드 타입에만 사용할 수 있습니다. 기본값은 false입니다.

- **entityFieldName**: string (선택 사항) - 설정된 경우, 이 필드는 `_search.{entityFieldName}`으로 복사되고 루트 별칭이 그곳을 가리킵니다. 이를 통해 여러 aspect가 단일 entity 수준 필드로 통합될 수 있습니다.

- **eagerGlobalOrdinals**: boolean (선택 사항) - 이 필드에 대해 `eager_global_ordinals`를 true로 설정할지 여부. 이는 인덱싱 시점에 ordinal을 미리 빌드하여 자주 집계되는 키워드 필드의 집계 성능을 향상시킵니다. **참고**: eagerGlobalOrdinals는 KEYWORD, URN 또는 URN_PARTIAL 필드 타입에만 true가 될 수 있습니다. 기본값은 false입니다.

**⚠️ 사용 중단된 매개변수에 대한 참고사항:** `queryByDefault`, `enableAutocomplete`, `boostScore`, `weightsPerFieldValue`와 같은 일부 매개변수는 검색 버전 2를 사용할 때 여전히 작동하지만 향후 버전에서 새로운 기능으로 대체될 예정입니다. 더 고급 검색 기능을 위해 새로운 티어 기반 및 레이블 기반 어노테이션을 사용하는 것을 고려하세요.

**사용 중단된 매개변수 마이그레이션:**

- **`queryByDefault`** → 기본 검색 쿼리에 필드를 포함하려면 `searchTier: 1`에서 `searchTier: 4`를 사용하세요.
- **`enableAutocomplete`** → `searchTier: 1`을 사용하세요.
- **`boostScore`** → 더 정교한 순위 제어를 위해 `searchLabel`을 사용하세요.
- **`weightsPerFieldValue`** → 값 기반 점수 매기기 제어를 위해 `searchLabel`을 사용하세요.

##### 예시

`DashboardInfo.pdl`의 `title` 필드를 사용하는 실제 예시를 살펴보겠습니다:

```aidl
record DashboardInfo {
 /**
   * Title of the dashboard
   */
  @Searchable = {
    "fieldType": "KEYWORD",
    "searchTier": 1,
    "entityFieldName": "name"
  }
  title: string
  ....
}
```

이 어노테이션은 title 필드를 Elasticsearch에 인덱싱하겠다는 것을 나타냅니다. `searchTier: 1`은 이 필드가 높은 관련성으로 기본 검색 쿼리에 포함되도록 합니다. `entityFieldName: "name"`은 이 필드를 entity 수준의 `_search.name` 필드로 통합하여 다른 aspect가 동일한 통합 필드에 기여할 수 있게 합니다.

**새 기능을 사용한 고급 예시:**

```aidl
record DashboardInfo {
  /**
   * Priority level for the dashboard
   */
  @Searchable = {
    "fieldType": "COUNT",
    "searchLabel": "priority",
    "addToFilters": true
  }
  priority: int

  /**
   * Status of the dashboard
   */
  @Searchable = {
    "fieldType": "KEYWORD",
    "addToFilters": true,
    "filterNameOverride": "Dashboard Status",
    "eagerGlobalOrdinals": true
  }
  status: string

  /**
   * Owner URN for the dashboard
   */
  @Searchable = {
    "fieldType": "URN",
    "addToFilters": true,
    "eagerGlobalOrdinals": true,
    "searchLabel": "owner"
  }
  owner: string
}
```

이 예시는 여러 새 기능을 보여줍니다:

- **Priority 필드**: `fieldType: "COUNT"`와 `searchLabel: "priority"`를 함께 사용하면 적절한 숫자 정렬 작업을 위해 `_search.priority`로 복사되는 숫자 필드가 생성되고, `addToFilters: true`로 필터로 사용할 수 있게 됩니다.
- **Status 필드**: `addToFilters: true`로 필터로 사용할 수 있게 되고, `filterNameOverride`는 커스텀 표시 이름 "Dashboard Status"를 제공하며, `eagerGlobalOrdinals: true`는 자주 필터링되는 이 필드의 집계 성능을 최적화합니다.
- **Owner 필드**: `fieldType: "URN"`과 `eagerGlobalOrdinals: true`는 소유자 기반 필터링의 집계 성능을 최적화하고, `searchLabel: "owner"`는 순위 작업을 위해 필드를 `_search.owner`로 복사합니다.

이제 DataHub가 Dashboard를 수집할 때 priority와 status 필드를 Elasticsearch에 인덱싱합니다. priority 필드는 정렬 작업에 사용할 수 있고, 두 필드 모두 UI에서 필터로 사용할 수 있습니다.

@Searchable 어노테이션이 맵에 적용되면 "key.toString()=value.toString()"을 요소로 갖는 목록으로 변환됩니다. 이를 통해 인덱싱되는 열 수를 늘리지 않고도 맵 필드를 인덱싱할 수 있습니다. 이렇게 하면 `aMapField:key1=value1`로 키를 쿼리할 수 있습니다.

@Searchable 어노테이션에서 fieldType을 OBJECT로 지정하여 이 동작을 변경할 수 있습니다. 이렇게 하면 직렬화된 키-값 쌍의 배열 대신 각 키를 Elasticsearch의 열에 넣습니다. 이 방법으로 쿼리는 `aMapField.key1:value1`과 같이 보입니다. 이 방법은 각 고유 키마다 열 수가 증가하므로 맵이 커질 것으로 예상되는 경우 OBJECT fieldType을 사용해서는 안 됩니다.

#### @SearchScore ⚠️ 사용 중단

**⚠️ 사용 중단**: 이 어노테이션은 더 이상 사용되지 않으며 새 코드에서 사용해서는 안 됩니다. 순위 기능을 위해 새로운 검색 티어 시스템과 함께 `searchLabel`을 사용하세요.

#### 검색 티어 및 레이블 시스템

새로운 검색 티어 및 레이블 시스템은 검색 필드를 구성하고 특화된 검색 경험을 만드는 강력한 방법을 제공합니다:

**검색 티어 (`searchTier`):**

- `searchTier`가 있는 필드는 자동으로 `_search.tier_{tier}` 필드로 복사됩니다.
- 이것은 검색 아키텍처의 근본적인 변화를 만듭니다: **전체 텍스트 검색 기능은 이제 개별 필드 타입이 아닌 티어에 의해 결정됩니다.**
- 동일한 티어에 할당된 모든 필드(예: `_search.tier_1`)는 개별 `fieldType`에 관계없이 단일 검색 가능 필드로 통합됩니다.
- 이를 통해 다양한 검색 우선순위에 기여하는 다양한 필드가 있는 계층화된 검색 경험을 만들 수 있습니다.
- 티어 기능을 유지하면서 직접 필터링/정렬 접근이 필요한 경우 `searchIndexed: true`를 사용하세요.

**검색 레이블 (`searchLabel`):**

- `searchLabel`이 있는 필드는 `_search.{label}` 필드(접두사 없음)로 복사됩니다.
- 통합 접근 방식을 위해 이전 `sortLabel` 및 `boostLabel` 어노테이션을 대체합니다.
- 여러 aspect에 걸쳐 특화된 검색, 정렬, 순위 작업을 만드는 데 유용합니다.
- 스토리지 최적화를 위해 `index: false`를 자동으로 설정합니다.

**Entity 필드 통합 (`entityFieldName`):**

- 여러 aspect가 단일 entity 수준 필드로 통합될 수 있게 합니다.
- 다양한 aspect 타입에 걸친 통합 검색 경험을 만드는 데 유용합니다.
- 필드는 루트 수준 별칭과 함께 `_search.{entityFieldName}`으로 복사됩니다.

**새 시스템의 이점:**

1. **정리된 검색 필드**: 모든 검색 관련 필드가 `_search.*` 아래에 그룹화됩니다.
2. **효율적인 인덱싱**: 원본 필드는 인덱싱되지 않고(index: false) 검색 필드로 복사됩니다.
3. **쉬운 접근**: 별칭이 루트 수준에서 필드에 편리하게 접근할 수 있게 합니다.
4. **유연한 쿼리**: 검색 쿼리가 특정 티어, 정렬 또는 순위 필드를 대상으로 할 수 있습니다.
5. **성능**: 복잡한 검색 시나리오에 최적화된 스토리지 및 쿼리 패턴.

**아키텍처 영향:**

- **이전**: 각 필드의 `fieldType`이 개별 검색 기능과 분석기를 결정했습니다.
- **이후**: `searchTier`가 전체 텍스트 검색 기능을 결정하는 반면, `fieldType`은 주로 저장 형식과 개별 필드 쿼리에 영향을 줍니다.
- **검색 통합**: 동일한 티어의 다양한 aspect에서 온 필드가 자동으로 통합된 검색 필드로 통합됩니다.
- **단순화된 검색 로직**: 검색 쿼리가 개별 필드 대신 전체 티어를 대상으로 할 수 있어 복잡한 검색 시나리오를 더 쉽게 관리할 수 있습니다.

#### 사용 중단된 기능 마이그레이션 가이드

현재 사용 중단된 필드 타입이나 매개변수를 사용하고 있다면, 새 시스템으로 마이그레이션하는 방법은 다음과 같습니다:

**필드 타입 마이그레이션:**

| 사용 중단됨       | 권장 대체안            | 참고                                                         |
| --------------- | ---------------------- | ------------------------------------------------------------ |
| `TEXT_PARTIAL`  | `TEXT`                 | 부분 매칭을 위해 적절한 분석기와 함께 TEXT 사용              |
| `WORD_GRAM`     | `TEXT`                 | 단어 기반 검색을 위해 단어 구분 분석기와 함께 TEXT 사용      |
| `BROWSE_PATH`   | `BROWSE_PATH_V2`       | 개선된 경로 계층 지원을 위해 BROWSE_PATH_V2 사용             |
| `URN`           | `TEXT`                 | 구성 요소 기반 검색을 위해 URN 분석기와 함께 TEXT 사용       |
| `URN_PARTIAL`   | `TEXT`                 | URN 분석기와 부분 매칭으로 TEXT 사용                         |

**매개변수 마이그레이션:**

| 사용 중단된 패턴                            | 새 패턴         | 이점                                                                      |
| ------------------------------------------ | --------------- | ------------------------------------------------------------------------- |
| `queryByDefault: true`                     | `searchTier: 1` | 검색 동작에 대한 더 명시적인 제어와 더 나은 성능                           |
| `enableAutocomplete: true`                 | `searchTier: 1` | 더 나은 성능 및 구성                                                       |
| `includeSystemModifiedAt: true`            | **자동**        | 시스템 수정 추적은 이제 모든 aspect에 대해 자동으로 처리됩니다.             |
| `systemModifiedAtFieldName: "customName"`  | **자동**        | 시스템 수정 필드 이름은 이제 자동으로 표준화됩니다.                         |

**마이그레이션 예시:**

```aidl
// 이전 사용 중단된 방식
@Searchable = {
  "fieldType": "TEXT_PARTIAL",
  "queryByDefault": true,
  "enableAutocomplete": true,
  "boostScore": 10.0
}
title: string

// 새로운 권장 방식
@Searchable = {
  "fieldType": "TEXT",
  "searchTier": 1,
  "entityFieldName": "name"
}
title: string
```

**티어 통합 예시:**

```aidl
// 이제 여러 aspect가 동일한 검색 티어에 기여할 수 있습니다
record DatasetInfo {
  @Searchable = {
    "fieldType": "KEYWORD",
    "searchTier": 1,
    "entityFieldName": "name"
  }
  name: string

  @Searchable = {
    "fieldType": "TEXT",
    "searchTier": 1,
    "entityFieldName": "description"
  }
  description: string
}

record ChartInfo {
  @Searchable = {
    "fieldType": "KEYWORD",
    "searchTier": 1,
    "entityFieldName": "name"
  }
  chartName: string
}
```

이 예시에서 세 필드(`name`, `description`, `chartName`)는 모두 자동으로 `_search.tier_1`로 통합됩니다. `_search.tier_1:*`에 대한 단일 검색 쿼리는 개별 aspect 및 필드 위치에 관계없이 이 모든 필드를 동시에 검색합니다. `fieldType`은 이제 주로 각 필드가 개별적으로 저장되고 접근되는 방식을 결정하는 반면, 티어는 전체 텍스트 검색에 참여하는 방식을 결정합니다.

**마이그레이션 이점:**

- 최적화된 인덱싱을 통한 더 나은 검색 성능
- 더 체계화된 검색 필드 구조
- 티어 기반 타겟팅으로 향상된 쿼리 기능
- 사용 중단되지 않을 미래 지향적 어노테이션
- 향상된 Elasticsearch 매핑 효율성

#### @Relationship

이 어노테이션은 Aspect 내의 필드에 적용됩니다. 이 어노테이션은 entity가 수집될 때 entity의 Urn과 어노테이션된 필드의 대상 사이에 엣지를 생성합니다. @Relationship 어노테이션은 Urn 타입의 필드에 적용해야 합니다.

다음 매개변수를 취합니다:

- **name**: string - 관계 타입을 식별하는 데 사용되는 이름.
- **entityTypes**: array[string] (선택 사항) - 외래 키 관계 필드의 유효한 값인 entity 타입 목록.

##### 예시

이 어노테이션이 어떻게 사용되는지 보기 위해 실제 예시를 살펴보겠습니다. `Owner.pdl` 구조체는 `Ownership.pdl` aspect에서 참조됩니다.
