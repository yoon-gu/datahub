# Bootstrap MetadataChangeProposals (MCPs)

Bootstrap MCP는 `system-update` 작업이 실행될 때 로드되는 템플릿화된 MCP입니다. 이를 통해 환경 변수 재정의를 통해 사용자 정의할 수 있는 기능을 갖추고 설치 시 DataHub에 entity와 aspect를 추가할 수 있습니다.

내장된 bootstrap MCP 프로세스는 커스텀 MCP로 확장될 수도 있습니다. 이는 표준 수집 레시피, 데이터 플랫폼, 사용자 그룹 또는 기타 설정의 집합을 커스텀 스크립트 개발 없이 적용할 수 있는 배포 시나리오를 간소화할 수 있습니다.

## 프로세스 개요

DataHub가 설치되거나 업그레이드될 때 `system-update`라는 작업이 실행됩니다. 이 작업은 데이터 마이그레이션(특히 Elasticsearch 인덱스)을 담당하고 다음 버전의 DataHub를 위해 데이터를 준비합니다. 또한 bootstrap MCP를 적용하는 작업이기도 합니다.

`system-update` 작업은 설정에 따라 두 가지 단계 순서로 분할될 수 있습니다. 분할되지 않으면 모든 단계가 블로킹됩니다.

1. GMS 및 다른 컴포넌트의 새 버전 이전에 실행되는 초기 블로킹 시퀀스
2. GMS 및 다른 컴포넌트가 실행되도록 허용되는 동시에 추가 데이터 마이그레이션 단계가 백그라운드에서 계속되는 두 번째 시퀀스

bootstrap MCP를 적용할 때 `system-update`는 다음 단계를 수행합니다:

1. `bootstrap_mcps.yaml` 파일을 기본 클래스패스 위치 `bootstrap_mcps.yaml`에서 읽거나, 환경 변수 `SYSTEM_UPDATE_BOOTSTRAP_MCP_CONFIG`가 제공하는 파일시스템 위치에서 읽습니다.
2. 블로킹 또는 비블로킹 모드에 따라 설정 파일의 각 항목이 순서대로 실행됩니다.
3. 템플릿 MCP 파일이 클래스패스 또는 파일시스템 위치에서 로드되고 템플릿 값이 적용됩니다.
4. 렌더링된 템플릿 MCP가 `bootstrap_mcps.yaml`에 지정된 옵션으로 실행됩니다.

## `bootstrap_mcps.yaml` 설정

`bootstrap_mcps.yaml` 파일은 다음 형식을 가집니다.

```yaml
bootstrap:
  templates:
    - name: <name>
      version: <version>
      force: false
      blocking: false
      async: true
      optional: false
      mcps_location: <classpath or file location>
      values_env: <environment variable>
```

템플릿 목록의 각 항목은 하나 이상의 MCP 객체를 포함할 수 있는 단일 yaml 파일을 가리킵니다. 템플릿 MCP의 실행은 재실행을 방지하기 위해 이름과 버전으로 추적됩니다. MCP 객체는 각 `name`/`version` 조합에 대해 `force=true`가 아닌 한 한 번만 실행됩니다.

템플릿 설정의 각 필드에 대한 설명은 다음 표를 참조하세요.

| 필드          | 기본값  | 필수 여부 | 설명                                                                                                       |
| ------------- | ------- | --------- | ---------------------------------------------------------------------------------------------------------- |
| name          |         | `true`    | 템플릿 MCP 컬렉션의 이름.                                                                                  |
| version       |         | `true`    | 템플릿 MCP 컬렉션의 문자열 버전.                                                                           |
| force         | `false` | `false`   | 이전 실행 기록을 무시하고 이전에 실행된 경우에도 건너뛰지 않습니다.                                         |
| blocking      | `false` | `false`   | 분할 블로킹/비블로킹 모드에서 업그레이드/설치 중 GMS 및 다른 컴포넌트보다 먼저 실행합니다.                 |
| async         | `true`  | `false`   | MCP가 동기식 또는 비동기식 수집으로 실행되는지 제어합니다.                                                  |
| optional      | `false` | `false`   | 실패를 무시할지 아니면 전체 `system-update` 작업을 실패로 처리할지 여부.                                    |
| mcps_location |         | `true`    | 템플릿 MCP를 포함하는 파일의 위치.                                                                         |
| values_env    |         | `false`   | 재정의 템플릿 값을 포함하는 환경 변수.                                                                     |

## 템플릿 MCPs

템플릿 MCP는 선택적 환경 변수에서 값을 채우기 위해 mustache 템플릿 라이브러리를 사용하는 yaml 파일에 저장됩니다. 재정의를 선택 사항으로 만들기 위해 인라인으로 기본값을 제공할 수 있습니다.

일반적으로 파일에는 MCP의 스키마 정의를 정확히 따르는 MCP 목록이 포함됩니다. `headers`와 같은 선택적 필드를 포함한 MCP의 유효한 모든 필드가 허용됩니다.

### 예시: 네이티브 그룹

네이티브 그룹을 생성하는 예시 템플릿 MCP 컬렉션, 설정, 값 환경 변수가 아래에 나와 있습니다.

```yaml
- entityUrn: urn:li:corpGroup:{{group.id}}
  entityType: corpGroup
  aspectName: corpGroupInfo
  changeType: UPSERT
  aspect:
   description: {{group.description}}{{^group.description}}Default description{{/group.description}}
   displayName: {{group.displayName}}
   created: {{&auditStamp}}
   members: [] # aspect의 스키마 정의의 일부로 필수
   groups: [] # aspect의 스키마 정의의 일부로 필수
   admins: [] # aspect의 스키마 정의의 일부로 필수
- entityUrn: urn:li:corpGroup:{{group.id}}
  entityType: corpGroup
  aspectName: origin
  changeType: UPSERT
  aspect:
     type: NATIVE
```

환경 변수 `DATAHUB_TEST_GROUP_VALUES`에서 값을 채우기 위해 `bootstrap_mcps.yaml`에 항목을 만들기:

```yaml
- name: test-group
  version: v1
  mcps_location: "bootstrap_mcps/test-group.yaml"
  values_env: "DATAHUB_TEST_GROUP_VALUES"
```

`DATAHUB_TEST_GROUP_VALUES` 환경 변수에서 로드되는 예시 json 값은 다음과 같을 수 있습니다.

```json
{
  "group": {
    "id": "mygroup",
    "displayName": "My Group",
    "description": "Description of the group"
  }
}
```

표준 mustache 템플릿 시맨틱을 사용하여 환경의 값이 yaml 구조에 삽입되고 `system-update`가 실행될 때 수집됩니다.

#### 기본값

위 예시에서 그룹의 `description`이 제공되지 않으면 표준 mustache 템플릿 시맨틱에 따라 환경 변수 재정의에 포함된 값이 지정되지 않은 경우 `Default description`이 기본값으로 사용됩니다.

#### AuditStamp

특수 템플릿 참조 `{{&auditStamp}}`를 사용하여 aspect에 `auditStamp`를 주입할 수 있습니다. 이는 MCP가 적용될 때 계산된 `auditStamp`의 필수 필드를 채우는 데 사용할 수 있습니다. 이는 `auditStamp`의 인라인 json 표현을 위치에 삽입하고 `&` 문자로 표시된 표준 mustache 템플릿에 따라 html 문자 이스케이프를 방지합니다.

### 수집 템플릿 MCPs

수집 템플릿 MCP는 `recipe`가 aspect 내에 json 문자열로 저장되기 때문에 약간 더 복잡합니다.
수집 레시피의 경우, 일반적으로 인코딩된 json 문자열 대신 yaml로 자연스럽게 설명할 수 있도록 특별 처리가 추가되었습니다.

이는 아래 예시에서 `aspect.config.recipe` 경로 아래의 구조가 자동으로 필요한 json 구조로 변환되어 문자열로 저장됨을 의미합니다.

```yaml
- entityType: dataHubIngestionSource
  entityUrn: urn:li:dataHubIngestionSource:demo-data
  aspectName: dataHubIngestionSourceInfo
  changeType: UPSERT
  aspect:
    type: "demo-data"
    name: "demo-data"
    config:
      recipe:
        source:
          type: "datahub-gc"
          config: {}
      executorId: default
```

## `bootstrap_mcps.yaml` 재정의

추가로 `bootstrap_mcps.yaml`을 재정의할 수 있습니다.
이는 helm 정의 템플릿 값을 사용할 때 버전 변경을 적용하는 데 유용할 수 있습니다.

```yaml
bootstrap:
  templates:
    - name: myMCPTemplate
      version: v1
      mcps_location: <classpath or file location>
      values_env: <value environment variable>
      revision_env: REVISION_ENV
```

위 예시에서 `revision_env`를 추가했으며, 이를 통해 MCP bootstrap 정의 자체를 재정의할 수 있습니다(`revision_env` 제외).

이 예시에서 `REVISION_ENV`를 타임스탬프나 해시로 설정할 수 있습니다: `{"version":"2024060600"}`
이 값은 helm에서 제공한 템플릿 값이 변경될 때마다 변경/증분될 수 있습니다. 이렇게 하면 배포 중에 MCP가 최신 값으로 업데이트됩니다.

## 알려진 제한 사항

- 지원되는 변경 타입:
  - UPSERT
  - CREATE
  - CREATE_ENTITY
