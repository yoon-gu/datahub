# 메타데이터 수집 개발하기

메타데이터 ingestion을 단순히 사용하고 싶다면 [사용자 중심](./README.md) 가이드를 확인하세요.
이 문서는 메타데이터 ingestion 프레임워크를 개발하고 기여하고자 하는 개발자를 위한 것입니다.

또한 [source 추가 가이드](./adding-source.md)를 참조하세요.

## 시작하기

### 요구 사항

1. 호스트 환경에 Python 3.9 이상이 설치되어 있어야 합니다.
2. Java 17 (gradle은 더 최신 또는 더 오래된 버전과 호환되지 않습니다)
3. Debian/Ubuntu의 경우: `sudo apt install python3-dev python3-venv`
4. Fedora (LDAP source 통합을 사용하는 경우): `sudo yum install openldap-devel`

### Python 환경 설정하기

저장소 루트에서:

```shell
cd metadata-ingestion
../gradlew :metadata-ingestion:installDev
source venv/bin/activate
datahub version  # "DataHub CLI version: unavailable (installed in develop mode)"가 출력되어야 합니다
```

### (선택 사항) Airflow 플러그인 개발을 위한 Python 환경 설정하기

저장소 루트에서:

```shell
cd metadata-ingestion-modules/airflow-plugin
../../gradlew :metadata-ingestion-modules:airflow-plugin:installDev
source venv/bin/activate
datahub version  # "DataHub CLI version: unavailable (installed in develop mode)"가 출력되어야 합니다

# airflow 웹 서버 시작
export AIRFLOW_HOME=~/airflow
airflow webserver --port 8090 -d

# airflow 스케줄러 시작
airflow scheduler

# airflow 서비스에 접속하여 DAG 실행
# http://localhost:8090/ 을 엽니다
# 원하는 DAG를 선택하고 `play arrow` 버튼을 클릭하여 DAG 시작

# 코드베이스에 디버그 줄 추가, 예: ./src/datahub_airflow_plugin/datahub_listener.py
logger.debug("this is the sample debug line")

# DAG를 다시 실행하면 다음 위치의 task_run 로그에서 디버그 줄을 확인할 수 있습니다:
#1. `Last Run` 열의 `timestamp`를 클릭합니다
#2. 태스크를 선택합니다
#3. `log` 옵션을 클릭합니다
```

> **P.S. 로그 줄이 보이지 않는 경우 `airflow scheduler`를 재시작하고 DAG를 다시 실행하세요**

### (선택 사항) Dagster 플러그인 개발을 위한 Python 환경 설정하기

저장소 루트에서:

```shell
cd metadata-ingestion-modules/dagster-plugin
../../gradlew :metadata-ingestion-modules:dagster-plugin:installDev
source venv/bin/activate
datahub version  # "DataHub CLI version: unavailable (installed in develop mode)"가 출력되어야 합니다
```

### (선택 사항) Prefect 플러그인 개발을 위한 Python 환경 설정하기

저장소 루트에서:

```shell
cd metadata-ingestion-modules/prefect-plugin
../../gradlew :metadata-ingestion-modules:prefect-plugin:installDev
source venv/bin/activate
datahub version   # "DataHub CLI version: unavailable (installed in develop mode)"가 출력되어야 합니다
```

### (선택 사항) GX 플러그인 개발을 위한 Python 환경 설정하기

저장소 루트에서:

```shell
cd metadata-ingestion-modules/gx-plugin
../../gradlew :metadata-ingestion-modules:gx-plugin:installDev
source venv/bin/activate
datahub version  # "DataHub CLI version: unavailable (installed in develop mode)"가 출력되어야 합니다
```

### (선택 사항) Dagster 플러그인 개발을 위한 Python 환경 설정하기

저장소 루트에서:

```shell
cd metadata-ingestion-modules/dagster-plugin
../../gradlew :metadata-ingestion-modules:dagster-plugin:installDev
source venv/bin/activate
datahub version  # "DataHub CLI version: unavailable (installed in develop mode)"가 출력되어야 합니다
```

### 일반적인 설정 문제

일반적인 문제 (클릭하여 펼치기):

<details>
  <summary>심볼릭 링크 오류로 가상 환경 생성 실패 (Nix, 변경 불가 파일 시스템, Windows)</summary>

Nix, 변경 불가 Python 설치, 특정 파일 시스템 구성의 Windows, 또는 심볼릭 링크가 제대로 작동하지 않는 컨테이너 환경을 사용하는 경우 가상 환경 생성 중 오류가 발생할 수 있습니다.

gradle 명령어를 실행하기 전에 환경 변수를 설정하여 Python venv에 `--copies` 플래그를 활성화할 수 있습니다:

```shell
export DATAHUB_VENV_USE_COPIES=true
../gradlew :metadata-ingestion:installDev
```

이는 심볼릭 링크 대신 Python 바이너리를 복사합니다. 디스크 사용량과 설정 시간이 증가하므로 기본 심볼릭 링크 방식에서 문제가 발생할 때만 활성화하세요.

</details>

<details>
  <summary>PyPI 설치 후 datahub 명령어를 찾을 수 없음</summary>

pip install을 이미 실행했지만 커맨드라인에서 `datahub`를 실행해도 작동하지 않는 경우, PATH 설정과 Python에 문제가 있을 가능성이 큽니다.

이를 해결하는 가장 쉬운 방법은 Python을 통해 설치 및 실행하고 `datahub` 대신 `python3 -m datahub`를 사용하는 것입니다.

```shell
python3 -m pip install --upgrade acryl-datahub
python3 -m datahub --help
```

</details>

<details>
  <summary>휠 관련 문제, 예: "Failed building wheel for avro-python3" 또는 "error: invalid command 'bdist_wheel'"</summary>

이는 Python의 `wheel`이 설치되지 않은 것을 의미합니다. 다음 명령어를 실행한 후 다시 시도하세요.

```shell
pip install --upgrade pip wheel setuptools
pip cache purge
```

</details>

<details>
  <summary>confluent_kafka 설치 실패: "error: command 'x86_64-linux-gnu-gcc' failed with exit status 1"</summary>

이는 Kafka의 C 라이브러리와 Python 래퍼 라이브러리 간의 버전 불일치가 있을 때 발생할 수 있습니다. `pip install confluent_kafka==1.5.0`을 실행한 후 다시 시도하세요.

</details>

<details>
  <summary>충돌: acryl-datahub가 pydantic 1.10을 필요로 함</summary>

기본 `acryl-datahub` 패키지는 Pydantic 1.x와 2.x 모두를 지원합니다. 그러나 일부 특정 source는 전이 의존성으로 인해 Pydantic 1.x를 필요로 합니다.

`acryl-datahub`를 SDK용으로 주로 사용하는 경우, Pydantic 버전 관련 충돌 없이 `acryl-datahub`와 일부 추가 기능(예: `acryl-datahub[sql-parser]`)을 설치할 수 있습니다.

주 환경에 전체 ingestion source를 설치하지 않는 것이 좋습니다(예: `acryl-datahub[snowflake]` 또는 기타 ingestion source에 대한 의존성 추가 피하기).
대신 UI 기반 ingestion을 사용하거나 [가상 환경](https://docs.python.org/3/library/venv.html)을 사용하여 ingestion pipeline을 격리하는 것이 좋습니다. 오케스트레이터를 사용하는 경우 종종 가상 환경에 대한 일급 지원을 제공합니다 - [Airflow 예시](./schedule_docs/airflow.md)를 참조하세요.

</details>

### 개발에서 플러그인 사용하기

개발 환경에서 플러그인을 설치하는 구문은 약간 다릅니다. 예를 들어:

```diff
- uv pip install 'acryl-datahub[bigquery,datahub-rest]'
+ uv pip install -e '.[bigquery,datahub-rest]'
```

## 아키텍처

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/datahub-metadata-ingestion-framework.png"/>
</p>

이 메타데이터 ingestion 프레임워크의 아키텍처는 [Apache Gobblin](https://gobblin.apache.org/)(원래 LinkedIn 프로젝트!)에서 크게 영감을 받았습니다. 표준화된 형식인 MetadataChangeEvent와 각각 이 객체를 생성하고 소비하는 source 및 sink가 있습니다. source는 다양한 데이터 시스템에서 메타데이터를 가져오고, sink는 주로 이 메타데이터를 DataHub로 이동하는 역할을 합니다.

## 코드 레이아웃

- CLI 인터페이스는 [entrypoints.py](./src/datahub/entrypoints.py)와 [cli](./src/datahub/cli) 디렉토리에 정의되어 있습니다.
- 고수준 인터페이스는 [API 디렉토리](./src/datahub/ingestion/api)에 정의되어 있습니다.
- 실제 [source](./src/datahub/ingestion/source)와 [sink](./src/datahub/ingestion/sink)는 각자의 디렉토리를 가지고 있습니다. 해당 디렉토리의 레지스트리 파일이 구현체를 가져옵니다.
- 메타데이터 모델은 코드 생성을 사용하여 만들어지며, 최종적으로 `./src/datahub/metadata` 디렉토리에 위치합니다. 그러나 이 파일들은 체크인되지 않고 빌드 시 생성됩니다. 자세한 내용은 [codegen](./scripts/codegen.sh) 스크립트를 참조하세요.
- 테스트는 [`tests`](./tests) 디렉토리에 있으며, 작은 단위 테스트와 큰 통합 테스트로 나뉩니다.

## 코드 스타일

일관된 코드 스타일과 품질을 보장하기 위해 ruff와 mypy를 사용합니다.

```shell
# 가정: ../gradlew :metadata-ingestion:installDev 완료 및 venv 활성화 상태
ruff check src/ tests/
mypy src/ tests/
```

또는 저장소 루트에서 실행할 수 있습니다:

```shell
./gradlew :metadata-ingestion:lint

# 일부 린팅 문제를 자동으로 수정합니다.
./gradlew :metadata-ingestion:lintFix
```

기타 참고 사항:

- 긴 상속 계층보다 믹스인 클래스를 선호합니다.
- 가능한 모든 곳에 타입 어노테이션을 작성합니다.
- `typing.Protocol`을 사용하여 암묵적 인터페이스를 명시적으로 만듭니다.
- 코드의 큰 덩어리를 복사하여 붙여넣는 경우 더 좋은 방법이 있을 가능성이 큽니다.
- `@staticmethod`보다 독립적인 헬퍼 메서드를 선호합니다.
- `__hash__` 메서드를 직접 정의하지 않는 것이 좋습니다. `@dataclass(frozen=True)`를 사용하는 것이 해시 가능한 클래스를 얻는 좋은 방법입니다.
- 전역 상태를 피합니다. source에서는 효과적으로 source의 "전역" 상태로 기능하는 인스턴스 변수도 포함됩니다.
- 다른 함수 내에 함수를 정의하지 않습니다. 코드를 읽고 테스트하기 어렵게 만듭니다.
- 외부 API와 상호 작용할 때 응답 객체에서 직접 작업하는 대신 응답을 데이터클래스로 파싱합니다.

## 의존성 관리

대부분의 의존성은 "core" 패키지에서 필요하지 않고 Python "extras"를 사용하여 선택적으로 설치할 수 있습니다. 이를 통해 core 패키지를 가볍게 유지할 수 있습니다. core 프레임워크에 새 의존성을 추가할 때는 신중해야 합니다.

가능하면 버전 의존성을 고정하지 않아야 합니다. `acryl-datahub` 패키지는 라이브러리로 자주 사용되어 다른 도구와 함께 설치됩니다. 의존성 버전을 제한해야 하는 경우 `>=1.2.3,<2.0.0`와 같은 범위나 `>=1.2.3, !=1.2.7`과 같은 부정 제약 조건을 사용하세요. 모든 상한 및 부정 제약 조건에는 필요한 이유를 설명하는 주석이 있어야 합니다.

주의: Great Expectations나 Airflow와 같은 일부 패키지는 자주 주요 변경 사항을 만듭니다. 이러한 패키지의 경우 현재 최신 버전과 함께 "방어적인" 상한을 추가하고 주석을 달아도 됩니다. 이러한 상한을 최소한 한 달에 한 번 재검토하고 가능하면 범위를 넓히는 것이 중요합니다.

### 잠금 파일 업데이트하기

`setup.py`에서 의존성을 변경한 후, 생성된 모든 파일을 재생성합니다:

```shell
../gradlew :metadata-ingestion:updateLockFile
```

이렇게 하면 전체 체인이 실행됩니다: `setup.py` → `pyproject.toml` → `uv.lock` → `constraints.txt`.

생성된 모든 파일이 최신 상태인지 수정하지 않고 검증하려면:

```shell
../gradlew :metadata-ingestion:checkLockFile
```

이는 CI에서 `check`의 일부로 자동으로 실행되므로, 오래된 생성 파일이 있는 PR은 실패합니다.

단계를 수동으로 실행할 수도 있습니다:

```shell
python scripts/generate_pyproject_deps.py   # setup.py → pyproject.toml
python scripts/verify_pyproject_equivalence.py  # 동등성 검증
uv lock                                      # uv.lock 업데이트
uv export --format requirements-txt --no-hashes --all-extras --no-emit-project -o constraints.txt
```

## Ingestion 구성 가이드라인

ingestion 구성을 정의하기 위해 [pydantic](https://pydantic-docs.helpmanual.io/)을 사용합니다.
구성이 일관성 있고 사용하기 쉽도록 몇 가지 가이드라인이 있습니다:

#### 명명

- 가장 중요한 점: **source 시스템의 용어와 일치**시켜야 합니다. 예를 들어 snowflake는 `host_port`가 아닌 `account_id`를 가져야 합니다.
- 대안이 충분히 설명적이지 않을 때는 약간 더 긴 이름을 선호합니다. 예를 들어 단순한 `id` 대신 `client_id` 또는 `tenant_id`, 단순한 `secret` 대신 `access_secret`.
- 목록을 필터링할 때는 AllowDenyPatterns를 사용해야 합니다. 패턴은 항상 entity의 완전한 이름에 적용되어야 합니다. 이러한 구성은 `*_pattern`으로 명명되어야 합니다. 예: `table_pattern`.
- `profile_table_level` 및 `profile_column_level`을 선호하여 `profile_table_level_only`와 같은 `*_only` 구성을 피합니다. `include_tables` 및 `include_views`가 좋은 예입니다.

#### 내용

- 모든 구성에는 설명이 있어야 합니다.
- 상속 또는 믹스인 클래스를 사용할 때 필드와 문서가 기본 클래스에 적용 가능한지 확인합니다. `bigquery_temp_table_schema` 필드가 모든 source의 프로파일링 구성에 나타나서는 안 됩니다!
- 합리적인 기본값을 설정하세요!
  - 구성에는 기본으로 내장되어야 한다고 합리적으로 예상되는 기본값이 포함되어서는 안 됩니다. **나쁜** 예로 Postgres source의 `schema_pattern`에 `information_schema`를 포함하는 기본 거부 패턴이 있습니다. 이는 사용자가 schema_pattern을 재정의하면 거부 패턴에 information_schema를 수동으로 추가해야 한다는 것을 의미합니다. 이는 좋지 않으며, 필터링은 구성에서 런타임에 추가되는 것이 아니라 source 구현에서 자동으로 처리되어야 합니다.

#### 코딩

- 검증할 항목당 하나의 pydantic 유효성 검사기를 사용합니다 - 50줄짜리 유효성 검사 메서드는 피해야 합니다.
- 비밀번호, 인증 토큰 등에는 `SecretStr`를 사용합니다.
- 단순한 필드 이름 변경의 경우 `pydantic_renamed_field` 헬퍼를 사용합니다.
- 필드 deprecated 처리 시 `pydantic_removed_field` 헬퍼를 사용합니다.
- 유효성 검사 메서드는 ValueError, TypeError 또는 AssertionError만 던져야 합니다. 유효성 검사기에서 ConfigurationError를 던지지 마세요.
- 내부 전용 구성 플래그에는 `hidden_from_docs`를 설정합니다. 그러나 이가 자주 필요하다는 것은 코드 구조에 더 큰 문제가 있다는 것을 나타냅니다. 숨겨진 필드는 아마 해당 source의 클래스 속성이나 인스턴스 변수여야 합니다.

## 테스트

```shell
# 위의 표준 소스에서 설치 절차를 따르세요.

# 모든 dev 및 테스트 요구 사항 설치.
../gradlew :metadata-ingestion:installDevTest

# 전체 테스트 스위트 실행
pytest -vv

# 단위 테스트 실행.
pytest -m 'not integration'

# Docker 기반 통합 테스트 실행.
pytest -m 'integration'

# gradle 빌드를 통해서도 이 단계를 실행할 수 있습니다:
../gradlew :metadata-ingestion:lint
../gradlew :metadata-ingestion:lintFix
../gradlew :metadata-ingestion:testQuick
../gradlew :metadata-ingestion:testFull
../gradlew :metadata-ingestion:check
# 단일 파일의 모든 테스트 실행
../gradlew :metadata-ingestion:testSingle -PtestFile=tests/unit/test_bigquery_source.py
# tests/unit 아래의 모든 테스트 실행
../gradlew :metadata-ingestion:testSingle -PtestFile=tests/unit
```

### 골든 테스트 파일 업데이트하기

특정 ingestion source 테스트에 사용되는 새 "golden" 데이터 파일을 생성해야 하는 변경 사항을 만든 경우 다음을 실행하여 재생성할 수 있습니다:

```shell
pytest tests/integration/<source>/<source>.py --update-golden-files
```

예를 들어:

```shell
pytest tests/integration/dbt/test_dbt.py --update-golden-files
```

### Airflow 플러그인 테스트하기

Airflow 플러그인의 경우 여러 의존성 세트를 테스트하기 위해 `tox`를 사용합니다.

```sh
cd metadata-ingestion-modules/airflow-plugin

# 모든 테스트 실행.
tox

# 특정 환경 실행.
# 이들은 `tox.ini` 파일에 정의되어 있습니다
tox -e py310-airflow26

# 특정 테스트 실행.
tox -e py310-airflow26 -- tests/integration/test_plugin.py

# 모든 골든 파일 업데이트.
tox -- --update-golden-files

# 특정 환경의 골든 파일 업데이트.
tox -e py310-airflow26 -- --update-golden-files
```
