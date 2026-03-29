# 메타데이터 수집 Source 추가하기

:::tip DataHub Skills로 커넥터를 더 빠르게 개발하기

새로운 커넥터를 개발하는 가장 빠른 방법은 **DataHub Skills**를 사용하는 것입니다. 이는 간단한 구성으로 프로덕션 수준의 커넥터를 생성하는 AI 기반 프레임워크입니다. 아래의 수동 단계를 시작하기 전에, [DataHub Skills 가이드](./datahub-skills.md)를 확인하고 몇 주 대신 몇 분 만에 통합을 구축해 보세요.

:::

메타데이터 ingestion source를 추가하는 방법은 두 가지가 있습니다.

1. 커스텀 source를 Datahub 프로젝트에 직접 기여하는 경우.
2. 직접 사용하기 위해 커스텀 source를 작성하고 (아직) 기여하지 않는 경우.

경우 (1)의 경우 아래 1~9단계를 따르세요. 직접 사용하기 위해 개발하는 경우에는
4~8단계를 건너뛸 수 있으며(단, 본인을 위한 테스트와 문서 작성은 권장합니다) Datahub를 포크하지 않고
[커스텀 ingestion source 사용 방법](../docs/how/add-custom-ingestion-source.md)에 대한 문서를 따르세요.

:::note

이 가이드는 로컬 환경 설정을 위해 이미 메타데이터 ingestion [개발 가이드](./developing.md)를 따랐다고 가정합니다.

:::

### 1. 구성 모델 설정하기

구성에는 [pydantic](https://pydantic-docs.helpmanual.io/)을 사용하며, 모든 모델은 `ConfigModel`을 상속해야 합니다. [file source](./src/datahub/ingestion/source/file.py)가 좋은 예시입니다.

#### 구성 클래스 문서화

구성 플래그를 문서화하기 위해 [pydantic](https://pydantic-docs.helpmanual.io) 규칙을 사용합니다. `description` 속성을 사용하여 구성 필드에 대한 풍부한 문서를 작성하세요.

예를 들어 다음 코드:

```python
from pydantic import Field
from datahub.api.configuration.common import ConfigModel

class LookerAPIConfig(ConfigModel):
    client_id: str = Field(description="Looker API client id.")
    client_secret: str = Field(description="Looker API client secret.")
    base_url: str = Field(
        description="Url to your Looker instance: `https://company.looker.com:19999` or `https://looker.company.com`, or similar. Used for making API calls to Looker and constructing clickable dashboard and chart urls."
    )
    transport_options: Optional[TransportOptionsConfig] = Field(
        default=None,
        description="Populates the [TransportOptions](https://github.com/looker-open-source/sdk-codegen/blob/94d6047a0d52912ac082eb91616c1e7c379ab262/python/looker_sdk/rtl/transport.py#L70) struct for looker client",
    )
```

는 다음과 같은 문서를 생성합니다:

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/metadata-ingestion/generated_config_docs.png"/>
</p>

:::note
인라인 마크다운이나 코드 스니펫은 아직 필드 레벨 문서에서 지원되지 않습니다.
:::

### 2. 리포터 설정하기

리포터 인터페이스를 통해 source는 실행에 대한 통계, 경고, 실패 및 기타 정보를 보고할 수 있습니다.
일부 source는 기본 `SourceReport` 클래스를 사용하지만, 다른 source는 이 클래스를 상속하고 확장합니다.

### 3. Source 자체 구현하기

source의 핵심은 `get_workunits_internal` 메서드로, 메타데이터 이벤트(일반적으로 MCP 객체)의 스트림을 MetadataWorkUnit으로 감싸서 생성합니다.
[file source](./src/datahub/ingestion/source/file.py)가 좋고 간단한 예시입니다.

MetadataChangeEventClass는 `metadata-ingestion/src/datahub/metadata/schema_classes.py`에 생성되는 메타데이터 모델에서 정의됩니다. 일반적으로 사용되는 작업을 위한 [편의 메서드](./src/datahub/emitter/mce_builder.py)도 있습니다.

### 4. 의존성 설정하기

참고: 4~8단계는 source를 Datahub 프로젝트에 기여할 의도가 있는 경우에만 필요합니다.

[설정 스크립트](./setup.py)의 `plugins` 변수에 source의 pip 의존성을 선언합니다.

### 5. 검색 가능성 활성화하기

[설정 스크립트](./setup.py)의 `entry_points` 변수에 source를 선언합니다. 이를 통해 `datahub check plugins` 실행 시 source가 목록에 표시되고, recipe에서 사용할 source의 단축 별칭을 설정합니다.

### 6. 테스트 작성하기

테스트는 `tests` 디렉토리에 작성합니다. [pytest 프레임워크](https://pytest.org/)를 사용합니다.

### 7. 문서 작성하기

#### 7.1 자동 문서화를 위한 source 클래스 설정

- `@platform_name` 데코레이터를 사용하여 이 source 클래스가 메타데이터를 생성하는 플랫폼 이름을 표시합니다. 사람이 읽기 쉬운 플랫폼 이름(예: bigquery 대신 BigQuery)을 선호합니다.
- `@config_class` 데코레이터를 사용하여 source에서 사용하는 구성 클래스를 표시합니다.
- `@support_status` 데코레이터를 사용하여 커넥터의 지원 상태를 표시합니다.
- `@capability` 데코레이터를 사용하여 커넥터가 지원하는 기능(및 지원하지 않는 중요 기능)을 표시합니다.
- Python 클래스의 docstring을 활용하여 커넥터에 대한 풍부한 문서를 추가합니다. 마크다운이 지원됩니다.

모든 source에 이를 적용하는 간단한 예시는 아래를 참조하세요.

```python

from datahub.ingestion.api.decorators import (
    SourceCapability,
    SupportStatus,
    capability,
    config_class,
    platform_name,
    support_status,
)

@platform_name("File")
@support_status(SupportStatus.CERTIFIED)
@config_class(FileSourceConfig)
@capability(
    SourceCapability.PLATFORM_INSTANCE,
    "File based ingestion does not support platform instances",
    supported=False,
)
@capability(SourceCapability.DOMAINS, "Enabled by default")
@capability(SourceCapability.DATA_PROFILING, "Optionally enabled via configuration")
@capability(SourceCapability.DESCRIPTIONS, "Enabled by default")
@capability(SourceCapability.LINEAGE_COARSE, "Enabled by default")
class FileSource(Source):
   """

   The File Source can be used to produce all kinds of metadata from a generic metadata events file.
   :::note
   Events in this file can be in MCE form or MCP form.
   :::

   """

   ... source code goes here

```

#### 7.2 커스텀 문서 작성하기

- [`source-docs-template.md`](./source-docs-template.md)의 사본을 만들고 관련 구성 요소를 편집합니다.
- 문서 이름을 `<plugin.md>`로 지정하고 `metadata-ingestion/docs/sources/<platform>/<plugin>.md`로 이동합니다. 예를 들어 Kafka 플랫폼의 `kafka` 플러그인의 경우, 문서를 `metadata-ingestion/docs/sources/kafka/kafka.md`로 이동합니다.
- 플러그인에 해당하는 빠른 시작 recipe를 `metadata-ingestion/docs/sources/<platform>/<plugin>_recipe.yml`에 추가합니다. 예를 들어 Kafka 플랫폼의 `kafka` 플러그인에는 `metadata-ingestion/docs/sources/kafka/kafka_recipe.yml`에 빠른 시작 recipe가 있습니다.
- 플랫폼별 문서(플러그인 간 공통)를 작성하려면 `metadata-ingestion/docs/sources/<platform>/README.md`에 문서를 작성합니다. 예를 들어 BigQuery 플랫폼의 플러그인 간 공통 문서는 `metadata-ingestion/docs/sources/bigquery/README.md`에 있습니다.

#### 7.3 문서 확인하기

source의 문서는 `docs-website` 모듈에서 문서 생성기를 실행하여 확인할 수 있습니다.

##### 1단계: 수집 문서 빌드하기

```console
# DataHub 저장소 루트에서
./gradlew :metadata-ingestion:docGen
```

성공적으로 완료되면 다음과 같은 출력 메시지가 표시됩니다:

```console
Ingestion Documentation Generation Complete
############################################
{
  "source_platforms": {
    "discovered": 40,
    "generated": 40
  },
  "plugins": {
    "discovered": 47,
    "generated": 47,
    "failed": 0
  }
}
############################################
```

DataHub 저장소 루트를 기준으로 `./docs/generated/ingestion/sources`에 생성된 문서 파일도 확인할 수 있습니다. 특정 source의 마크다운 파일을 찾아 예상대로 보이는지 확인할 수 있습니다.

#### 2단계: 전체 문서 빌드하기

이 문서가 브라우저에서 어떻게 보이는지 확인하려면 한 단계가 더 필요합니다. `docs-website` 모듈에서 전체 docusaurus 페이지를 빌드합니다.

```console
# DataHub 저장소 루트에서
./gradlew :docs-website:build
```

이렇게 하면 다음과 같은 메시지가 생성됩니다:

```console
...
> Task :docs-website:yarnGenerate
yarn run v1.22.0
$ rm -rf genDocs/* && ts-node -O '{ "lib": ["es2020"], "target": "es6" }' generateDocsDir.ts && mv -v docs/* genDocs/
Including untracked files in docs list:
docs/graphql -> genDocs/graphql
Done in 2.47s.

> Task :docs-website:yarnBuild
yarn run v1.22.0
$ docusaurus build

╭──────────────────────────────────────────────────────────────────────────────╮│                                                                              ││                Update available 2.0.0-beta.8 → 2.0.0-beta.18                 ││                                                                              ││       To upgrade Docusaurus packages with the latest version, run the        ││                             following command:                               ││                    yarn upgrade @docusaurus/core@latest                      ││   @docusaurus/plugin-ideal-image@latest @docusaurus/preset-classic@latest    ││                                                                              │╰──────────────────────────────────────────────────────────────────────────────╯


[en] Creating an optimized production build...
Invalid docusaurus-plugin-ideal-image version 2.0.0-beta.7.
All official @docusaurus/* packages should have the exact same version as @docusaurus/core (2.0.0-beta.8).
Maybe you want to check, or regenerate your yarn.lock or package-lock.json file?
Browserslist: caniuse-lite is outdated. Please run:
  npx browserslist@latest --update-db
  Why you should do it regularly: https://github.com/browserslist/browserslist#browsers-data-updating
ℹ Compiling Client
ℹ Compiling Server
✔ Client: Compiled successfully in 1.95s
✔ Server: Compiled successfully in 7.52s
Success! Generated static files in "build".

Use `npm run serve` command to test your build locally.

Done in 11.59s.

Deprecated Gradle features were used in this build, making it incompatible with Gradle 7.0.
Use '--warning-mode all' to show the individual deprecation warnings.
See https://docs.gradle.org/6.9.2/userguide/command_line_interface.html#sec:command_line_warnings

BUILD SUCCESSFUL in 35s
36 actionable tasks: 16 executed, 20 up-to-date
```

이후 `docs-website` 모듈에서 다음 스크립트를 실행해야 합니다.

```console
cd docs-website
npm run serve
```

이제 http://localhost:3000 또는 npm이 실행 중인 포트로 이동하여 문서를 탐색합니다.
source는 왼쪽 사이드바의 `Metadata Ingestion / Sources` 아래에 표시됩니다.

### 8. SQL Alchemy 매핑 추가 (해당되는 경우)

source에 sqlalchemy source가 있는 경우 [sql_common.py](./src/datahub/ingestion/source/sql/sql_common.py)의 `get_platform_from_sqlalchemy_uri` 함수에 source를 추가합니다.

### 9. 플랫폼 로고 추가하기

[images 폴더](../datahub-web-react/src/images)에 로고 이미지를 추가하고 [시작 시](../metadata-service/configuration/src/main/resources/bootstrap_mcps/data-platforms.yaml) 수집되도록 추가합니다.

### 10. UI 기반 ingestion을 위한 프론트엔드 업데이트

현재 UI 기반 관리 ingestion에서 사용 가능한 source를 표시하는 더 동적인 방식으로 전환 중입니다. 당분간은 다음 단계를 따라 UI Ingestion 탭에 source를 표시하세요.

#### 10.1 sources.json에 추가하기

[sources.json](https://github.com/datahub-project/datahub/blob/master/datahub-web-react/src/app/ingest/source/builder/sources.json)의 목록에 기본 빠른 시작 recipe를 포함한 새 source를 추가합니다. 이렇게 하면 UI에서 새 recipe를 생성할 때 옵션 목록에 source가 표시됩니다.

#### 10.2 React 앱에 로고 추가하기

React [images 폴더](https://github.com/datahub-project/datahub/tree/master/datahub-web-react/src/images)에 source 로고를 추가하여 메모리에서 이미지를 사용할 수 있도록 합니다.

#### 10.3 constants.ts 업데이트하기

[constants.ts](https://github.com/datahub-project/datahub/blob/master/datahub-web-react/src/app/ingest/source/builder/constants.ts)에 source URN과 source 이름에 대한 새 상수를 생성합니다. PLATFORM_URN_TO_LOGO를 업데이트하여 source URN을 images 폴더에 새로 추가한 로고에 매핑합니다.
