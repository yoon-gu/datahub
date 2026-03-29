# CLI Ingestion

배치 ingestion은 source 시스템에서 메타데이터를 대량으로 추출하는 작업입니다. 일반적으로 [메타데이터 수집](../docs/components.md#ingestion-framework) 프레임워크를 사용하여 사전 정의된 일정에 따라 실행됩니다.
추출되는 메타데이터에는 dataset, chart, dashboard, pipeline, 사용자, 그룹, 사용량, 작업 메타데이터의 특정 시점 인스턴스가 포함됩니다.

## DataHub CLI 설치

:::note 필요한 Python 버전
DataHub CLI를 설치하려면 Python 3.6 이상이 필요합니다.
:::

터미널에서 다음 명령어를 실행하세요:

```
python3 -m pip install --upgrade pip wheel setuptools
python3 -m pip install --upgrade acryl-datahub
python3 -m datahub version
```

이 명령어를 성공적으로 실행하면 커맨드라인에서 DataHub의 정확한 버전이 출력됩니다.

추가 설치 옵션 및 문제 해결 팁은 [CLI 설치 가이드](../docs/cli.md#installation)를 참조하세요.

## 커넥터 플러그인 설치

CLI는 플러그인 아키텍처를 따릅니다. 서로 다른 데이터 source에 대한 커넥터를 개별적으로 설치해야 합니다.
지원되는 모든 데이터 source 목록은 [오픈소스 문서](../docs/cli.md#sources)를 참조하세요.
원하는 커넥터를 찾으면 `pip install`을 사용하여 간단히 설치할 수 있습니다.
예를 들어 `mysql` 커넥터를 설치하려면 다음을 실행하세요:

```shell
pip install --upgrade 'acryl-datahub[mysql]'
```

추가 참고 자료는 [대체 설치 옵션](../docs/cli.md#alternate-installation-options)을 확인하세요.

:::tip 새 커넥터를 개발 중이신가요?

아직 존재하지 않는 커넥터가 필요하다면, [datahub-skills](./datahub-skills.md)는
계획 및 스캐폴딩부터 표준 검토 및 커뮤니티 테스트까지 커넥터 개발을 가속화하는
Claude Code 플러그인입니다.

:::

## Recipe 구성하기

아래와 같이 메타데이터의 source와 sink를 정의하는 [Recipe](recipe_overview.md) yaml 파일을 생성합니다.

```yaml
# example-recipe.yml

# MySQL source 구성
source:
  type: mysql
  config:
    username: root
    password: password
    host_port: localhost:3306

# Recipe sink 구성
sink:
  type: "datahub-rest"
  config:
    server: "https://<your domain name>.acryl.io/gms"
    token: <Your API key>
```

**source** 구성 블록은 메타데이터를 추출할 위치를 정의합니다. OLTP 데이터베이스 시스템, 데이터 웨어하우스, 또는 단순한 파일일 수도 있습니다. 각 source에는 해당 source에서 메타데이터를 접근하는 데 필요한 사항에 따라 커스텀 구성이 있습니다. 지원되는 각 source에 필요한 구성을 보려면 [Sources](source_overview.md) 문서를 참조하세요.

**sink** 구성 블록은 메타데이터를 전송할 위치를 정의합니다. 각 sink 유형에는 특정 구성이 필요하며, 자세한 내용은 [Sinks](sink_overview.md) 문서에 설명되어 있습니다.

DataHub 인스턴스를 ingestion의 목적지로 구성하려면, 아래와 같이 recipe의 "server" 필드를 DataHub Cloud 인스턴스의 도메인에 `/gms` 경로를 붙인 값으로 설정하세요.
MySQL에서 읽어 DataHub 인스턴스에 쓰는 완전한 DataHub recipe 파일 예시:

recipe 구성에 대한 자세한 정보와 예시는 [Recipes](recipe_overview.md)를 참조하세요.

### 인증이 필요한 Recipe 사용하기

DataHub Cloud 배포에서는 `datahub-rest` sink만 지원됩니다. 이는 메타데이터가 DataHub 인스턴스가 노출하는 REST 엔드포인트로 전송된다는 것을 의미합니다. 이 sink에 필요한 구성은 다음과 같습니다:

1. **server**: DataHub 인스턴스가 노출하는 REST API의 위치
2. **token**: 인스턴스의 REST API 요청을 인증하는 데 사용되는 고유한 API 키

토큰은 관리자로 로그인하여 얻을 수 있습니다. 설정 페이지로 이동하여 원하는 만료 날짜로 개인 액세스 토큰을 생성할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/saas/home-(1).png"/>
</p>

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/saas/settings.png"/>
</p>

:::info API 키 보안
API 키를 안전하게 보관하고 공유하지 마세요.
DataHub Cloud를 사용 중이고 어떤 이유로든 키가 유출된 경우, support@acryl.io로 DataHub 팀에 문의하세요.
:::

## 메타데이터 수집하기

마지막 단계는 DataHub CLI를 호출하여 recipe 구성 파일을 기반으로 메타데이터를 수집하는 것입니다.
이를 위해 YAML recipe 파일을 가리키는 포인터와 함께 `datahub ingest`를 실행하기만 하면 됩니다:

```shell
datahub ingest -c <path/to/recipe.yml>
```

## Ingestion 일정 예약하기

Ingestion은 시스템 관리자가 임시로 실행하거나 반복 실행을 위해 일정을 예약할 수 있습니다. 가장 일반적으로 ingestion은 일별로 실행됩니다.
Ingestion 작업을 예약하려면 [Apache Airflow](https://airflow.apache.org/)와 같은 작업 스케줄러를 사용하는 것이 좋습니다. 더 단순한 배포의 경우, 항상 실행 중인 시스템에 예약된 CRON 작업도 사용할 수 있습니다.
각 source 시스템에는 별도의 recipe 파일이 필요합니다. 이를 통해 서로 다른 source에서의 ingestion을 독립적으로 또는 함께 예약할 수 있습니다.
ingestion 일정 예약에 대한 자세한 내용은 [Ingestion 일정 예약 가이드](/metadata-ingestion/schedule_docs/intro.md)를 참조하세요.

## 참고 자료

CLI ingestion에 대한 고급 가이드는 다음 페이지를 참조하세요.

- [`datahub ingest` 명령어 참조](../docs/cli.md#ingest)
- [UI Ingestion 가이드](../docs/ui-ingestion.md)

:::tip 호환성

DataHub 서버는 3자리 버전 체계를 사용하고, CLI는 4자리 체계를 사용합니다. 예를 들어 DataHub 서버 버전 0.10.0을 사용하는 경우 CLI 버전 0.10.0.x를 사용해야 합니다. 여기서 x는 패치 버전입니다.
서버 릴리스는 한 달에 두 번 정도인 반면, CLI 릴리스는 보통 며칠마다 이루어지므로 이러한 방식을 사용합니다.

ingestion source의 경우, 주요 변경 사항은 [릴리스 노트](../docs/how/updating-datahub.md)에 강조 표시됩니다. 필드가 deprecated되거나 변경되면 두 서버 릴리스(약 4-6주) 동안 하위 호환성을 유지하려고 노력합니다. CLI는 deprecated 옵션이 사용될 때마다 경고를 출력합니다.
:::
