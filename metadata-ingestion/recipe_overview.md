import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Recipe

recipe는 메타데이터 ingestion의 주요 구성 파일입니다. 데이터를 어디에서 가져올지(source)와 어디에 저장할지(sink)를 ingestion 스크립트에 알려줍니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/sources-sinks.png"/>
</p>

## Recipe 구성하기

recipe 파일의 기본 형식은 다음으로 구성됩니다:

- `source`: 데이터 source의 구성을 포함합니다. ([Sources](source_overview.md) 참조)
- `sink`: 메타데이터의 목적지를 정의합니다. ([Sinks](sink_overview.md) 참조)

다음은 MSSQL(source)에서 메타데이터를 가져와 기본 sink(datahub rest)에 저장하는 간단한 recipe입니다.

```yaml
# MSSQL에서 메타데이터를 가져와 Rest API를 사용하여 DataHub에 저장하는 가장 간단한 recipe
source:
  type: mssql
  config:
    username: sa
    password: ${MSSQL_PASSWORD}
    database: DemoData
# 기본 datahub-rest sink를 사용하므로 sink 섹션을 생략합니다
sink:
  type: "datahub-rest"
  config:
    server: "http://localhost:8080"
```

여러 recipe 예제가 [examples/recipes](./examples/recipes) 디렉토리에 포함되어 있습니다. 각 source와 sink에 대한 전체 정보는 [플러그인 표](../docs/cli.md#installing-plugins)에 설명된 페이지를 참조하세요.

:::note recipe 하나에 source/sink 하나!
하나의 recipe 파일에는 source 1개와 sink 1개만 포함할 수 있습니다. 여러 source가 필요한 경우 여러 recipe 파일이 필요합니다.
:::

## Recipe 실행하기

DataHub는 CLI 또는 UI를 통해 recipe를 실행할 수 있습니다.

<Tabs>
<TabItem value="cli" label="CLI" default>

CLI와 ingestion 플러그인을 설치합니다.

```shell
python3 -m pip install --upgrade acryl-datahub
pip install 'acryl-datahub[datahub-rest]'
```

이 recipe 실행은 다음과 같이 간단합니다:

```shell
datahub ingest -c recipe.dhub.yaml
```

CLI를 통한 recipe 실행에 대한 자세한 가이드는 [CLI Ingestion 가이드](cli-ingestion.md)를 참조하세요.

</TabItem>

<TabItem value="ui" label="UI">

DataHub의 **Ingestion** 탭에서 recipe를 구성하고 실행할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion-tab.png"/>
</p>

- **메타데이터 수집 관리 & 시크릿 관리** 권한이 있는지 확인하세요.
- DataHub의 **Ingestion** 탭으로 이동합니다.
- UI를 통해 ingestion source를 생성하고 recipe를 구성합니다.
- **실행**을 클릭합니다.

UI를 통한 recipe 실행에 대한 자세한 가이드는 [UI Ingestion 가이드](../docs/ui-ingestion.md)를 참조하세요.

</TabItem>
</Tabs>

## 고급 구성

### Recipe에서 민감한 정보 처리하기

구성에서 환경 변수를 자동으로 확장합니다 (예: `${MSSQL_PASSWORD}`).
GNU bash나 docker-compose 파일의 변수 치환과 유사합니다.
자세한 내용은 [variable-substitution](https://docs.docker.com/compose/compose-file/compose-file-v2/#variable-substitution)을 참조하세요.
이 환경 변수 치환을 사용하여 recipe 파일의 민감한 정보를 마스킹해야 합니다. 환경 변수를 ingestion 프로세스에 안전하게 전달할 수 있다면 recipe에 민감한 정보를 저장할 필요가 없습니다.

### Recipe에서 민감한 데이터를 파일로 로드하기

일부 source(예: kafka, bigquery, mysql)는 로컬 파일 시스템의 파일 경로를 필요로 합니다. 이는 recipe가 완전히 자급자족해야 하는 UI ingestion에서는 작동하지 않습니다. 필요한 구성의 일부로 ingestion 프로세스에 파일을 추가하기 위해, DataHub는 `__DATAHUB_TO_FILE_` 지시어를 제공하여 recipe가 파일 내용을 설정할 수 있도록 합니다.

이 지시어의 구문은 `__DATAHUB_TO_FILE_<property>: <value>`로, `<property>: <value를 포함하는 파일 경로>`로 변환됩니다. 값은 인라인으로 지정하거나 환경 변수/시크릿을 사용하여 지정할 수 있습니다.

예시:

```yaml
source:
  type: mysql
  config:
    # 연결 정보
    host_port: localhost:3306
    database: dbname

    # 자격 증명
    username: root
    password: example
    # MySQL에서 SSL을 사용해야 하는 경우:
    options:
      connect_args:
        __DATAHUB_TO_FILE_ssl_key: '${secret}' # 파일에 마운트해야 하는 시크릿에 사용
        # 다음으로 변환됩니다:
        # ssl_key: /tmp/path/to/file # 파일에 ${secret}의 내용이 포함됩니다
   ...
```

### Transformation

ingestion sink에 도달하기 전에 데이터를 수정하고 싶다면 – 예를 들어 추가 소유자나 태그를 추가하는 경우 – transformer를 사용하여 자체 모듈을 작성하고 DataHub와 통합할 수 있습니다. Transformer는 실행하려는 transformer를 설명하는 새 섹션을 recipe에 추가해야 합니다.

예를 들어, MSSQL에서 메타데이터를 수집하고 모든 dataset에 기본 "important" 태그를 적용하는 pipeline은 다음과 같이 설명됩니다:

```yaml
# MSSQL에서 메타데이터를 수집하고 모든 테이블에 기본 태그를 적용하는 recipe
source:
  type: mssql
  config:
    username: sa
    password: ${MSSQL_PASSWORD}
    database: DemoData

transformers: # 순차적으로 적용되는 transformer 배열
  - type: simple_add_dataset_tags
    config:
      tag_urns:
        - "urn:li:tag:Important"
# 기본 sink, 구성 불필요
```

Transformer를 사용하여 메타데이터 처리를 위한 유연한 pipeline을 만드는 방법에 대해 자세히 알아보려면 [transformer 가이드](./docs/transformer/intro.md)를 확인하세요!

### 자동완성 및 구문 검증

vscode나 intellij를 자동완성 및 구문 검증이 있는 recipe 편집기로 사용하려면 recipe 파일의 확장자를 **.dhub.yaml**로 지정하세요(예: `myrecipe.dhub.yaml`). 편집기에 yaml 플러그인이 설치되어 있는지 확인하세요:

- vscode의 경우 [Redhat의 yaml 플러그인](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)을 설치하세요
- intellij의 경우 [공식 yaml 플러그인](https://plugins.jetbrains.com/plugin/13126-yaml)을 설치하세요
