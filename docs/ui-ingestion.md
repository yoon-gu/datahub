import FeatureAvailability from '@site/src/components/FeatureAvailability';

# 메타데이터 Ingestion

<FeatureAvailability/>

DataHub는 데이터 소스에 대한 정보를 자동으로 수집하여 조직의 데이터를 탐색하고 이해하는 데 도움을 줍니다. 이 과정을 **메타데이터 ingestion**이라고 하며, DataHub가 자동으로 다음을 가져올 수 있습니다:

- 데이터베이스의 **테이블 및 컬럼 이름**
- 시스템 간 정보 흐름을 보여주는 **에셋 Lineage**
- 어떤 dataset이 가장 많이 사용되는지를 알려주는 **사용 통계**
- 최신성 및 완전성을 포함한 **데이터 품질 정보**
- 소유권 및 문서화와 같은 **비즈니스 컨텍스트**

이를 통해 Snowflake, BigQuery, dbt 등 인기 있는 플랫폼에 쉽게 연결하고, 자동 업데이트를 예약하며, 자격 증명을 안전하게 관리할 수 있습니다.

## 사전 요구 사항 및 권한

DataHub에서 메타데이터 ingestion을 관리하려면 적절한 권한이 필요합니다.

:::note Ask DataHub for Ingestion (공개 베타 - DataHub Cloud)
**Ask DataHub** (공개 베타)는 DataHub Cloud 배포를 위한 ingestion 생성 및 문제 해결 워크플로우 내에서 사용할 수 있습니다. 설정, 필터링, 문제 해결 및 모범 사례에 대한 AI 기반 지원을 워크플로우 내에서 바로 받을 수 있습니다.
:::

### 옵션 1: 관리자 수준 접근

사용자에게 모든 ingestion 소스에 대한 완전한 관리 접근 권한을 부여하는 다음 권한을 허용할 수 있습니다:

- **`Manage Metadata Ingestion`** - 모든 ingestion 소스의 생성, 편집, 실행 및 삭제에 대한 완전한 접근 권한 제공
- **`Manage Secrets`** - ingestion 설정에 사용되는 암호화된 자격 증명의 생성 및 관리 허용

이러한 권한은 두 가지 방법으로 부여할 수 있습니다:

1. **관리자 역할 할당** - **Admin Role**에 할당된 사용자는 기본적으로 이러한 권한을 받음
2. **플랫폼 권한이 있는 커스텀 정책** - 특정 사용자 또는 그룹에게 `Manage Metadata Ingestion` 및 `Manage Secrets` 플랫폼 권한을 부여하는 [커스텀 정책](authorization/policies.md) 생성

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion-privileges.png"/>
</p>

### 옵션 2: 리소스별 정책

더 세밀한 제어를 위해 관리자는 **Ingestion Sources**에 특별히 적용되는 [커스텀 정책](authorization/policies.md)을 생성하여 다른 사용자가 다른 수준의 접근 권한을 가질 수 있도록 할 수 있습니다:

- **보기** - ingestion 소스 설정 및 실행 내역 보기
- **편집** - ingestion 소스 설정 수정
- **삭제** - ingestion 소스 제거
- **실행** - 요청에 따라 ingestion 소스 실행

**사전 요구 사항:**

- **DataHub Core**: `VIEW_INGESTION_SOURCE_PRIVILEGES_ENABLED` 기능 플래그 활성화
- **DataHub Cloud**: 고객 성공 팀에 문의하여 기능 활성화

:::caution
**중요**: 이 기능 플래그가 활성화되면 "전체" 리소스 타입에 적용되는 모든 정책이 이제 Ingestion Sources를 포함하게 됩니다. 기본 읽기 전용 정책도 포함됩니다. 이렇게 하면 적용된 권한에 따라 Ingestion 탭이 보이고 잠재적으로 작동 가능해집니다. 데이터 소스 페이지를 노출하지 않아야 하는 보기 전용 정책이 있는 경우 주의하여 구현하세요.
:::

## Ingestion 소스 생성하기

적절한 권한이 있으면 DataHub의 **Ingestion** 탭으로 이동합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion-tab.png"/>
</p>

이 페이지에서는 활성 **Ingestion Sources** 목록을 볼 수 있습니다. Ingestion Source는 DataHub가 메타데이터를 추출하는 외부 데이터 시스템에 대한 설정된 연결을 나타냅니다.

처음 시작하는 경우 설정된 소스가 없습니다. 다음 섹션에서 첫 번째 ingestion 소스를 생성하는 방법을 안내합니다.

### 1단계: 데이터 소스 선택

**+ Create source**를 클릭하여 ingestion 소스 생성 프로세스를 시작합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/create-new-ingestion-source-button.png"/>
</p>

다음으로, 연결할 데이터 소스 타입을 선택합니다. DataHub는 다음을 포함한 인기 있는 플랫폼에 대한 사전 구축된 템플릿을 제공합니다:

- **데이터 웨어하우스**: Snowflake, BigQuery, Redshift, Databricks
- **데이터베이스**: MySQL, PostgreSQL, SQL Server, Oracle
- **비즈니스 인텔리전스**: Looker, Tableau, PowerBI
- **스트리밍**: Kafka, Pulsar
- **그 외 많은 것들...**

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/select-platform-template.png"/>
</p>

데이터 소스에 맞는 템플릿을 선택하세요. 특정 플랫폼이 목록에 없는 경우 **Custom**을 선택하여 수동으로 소스를 구성할 수 있지만, 더 많은 기술적 지식이 필요합니다.

### 2단계: 연결 세부 정보 설정

데이터 소스 템플릿을 선택한 후, DataHub가 소스에 연결하고 메타데이터를 추출하는 방법을 설정합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion/ingestion-connection-ask-datahub.png"/>
</p>

_Ask DataHub (공개 베타 - Cloud 전용)는 ingestion 설정 프로세스 전반에 걸쳐 상황에 맞는 도움을 제공합니다_

**이름 및 소유자**: 먼저 나중에 본인과 팀이 식별하는 데 도움이 되는 ingestion 소스의 설명적인 이름을 제공합니다. 이 ingestion 소스의 소유자로 **사용자** 및/또는 **그룹**을 할당할 수 있습니다. 기본적으로 생성자(본인)가 소유자로 할당되지만, 생성 후 언제든지 추가 소유자를 추가하거나 변경할 수 있습니다.

**연결 정보**: 다음으로 사용자 친화적인 양식을 사용하여 연결 세부 정보를 설정합니다. 정확한 필드는 선택한 플랫폼에 따라 다르지만 일반적으로 다음을 포함합니다:

- 호스트/서버 주소 및 포트
- 데이터베이스 또는 프로젝트 이름
- 인증 자격 증명

**에셋 필터**: 추출할 메타데이터를 설정합니다:

- 포함할 데이터베이스, 스키마 또는 테이블
- 특정 데이터를 제외하기 위한 필터링 옵션

**Ingestion 설정**: 프로파일링, 오래된 메타데이터 처리 및 기타 운영 설정을 포함한 ingestion 동작을 설정합니다. 기본값은 대부분의 사용 사례에 대한 모범 사례를 나타냅니다.

:::note Ask DataHub for Configuration Help (공개 베타)
**Ask DataHub** (공개 베타)는 각 설정 옵션의 동작과 선택지를 이해하는 데 도움을 줄 수 있습니다. 데이터 소스와 사용 사례에 맞는 맞춤형 권장 사항을 받을 수 있습니다.
:::

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion/ingestion-configuration-ask-datahub-2.png"/>
</p>

_Ask DataHub (공개 베타 - Cloud 전용)는 설정 옵션을 이해하고 데이터 소스에 맞는 맞춤형 권장 사항을 제공하는 데 도움을 줍니다_

#### Secrets를 사용한 민감한 정보 관리

프로덕션 환경에서는 비밀번호 및 API 키와 같은 민감한 정보를 DataHub의 **Secrets** 기능을 사용하여 안전하게 저장해야 합니다.

시크릿을 생성하려면:

1. Ingestion 인터페이스의 **Secrets** 탭으로 이동
2. **Create new secret** 클릭
3. 설명적인 이름 제공 (예: `BIGQUERY_PRIVATE_KEY`)
4. 민감한 값 입력
5. 선택적으로 설명 추가
6. **Create** 클릭

생성된 시크릿은 자격 증명 필드에 제공된 드롭다운 메뉴를 사용하여 ingestion 설정 양식에서 참조할 수 있습니다.

:::caution 보안 참고 사항
`Manage Secrets` 권한이 있는 사용자는 DataHub의 GraphQL API를 통해 평문 시크릿 값을 검색할 수 있습니다. 시크릿에는 신뢰할 수 있는 관리자만 접근할 수 있도록 하세요.
:::

#### 연결 테스트

진행하기 전에 DataHub가 데이터 소스에 성공적으로 연결할 수 있는지 확인하는 것이 중요합니다. 대부분의 ingestion 소스 양식에는 다음을 검증하는 **Test Connection** 버튼이 있습니다:

- 데이터 소스에 대한 네트워크 연결
- 인증 자격 증명
- 메타데이터 추출에 필요한 권한

<p align="center">
  <img width="70%" alt="Test BigQuery connection" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/guides/bigquery/bigquery-test-connection.png"/>
</p>

연결 테스트가 실패하면 설정을 검토하고 다음을 확인하세요:

- DataHub와 데이터 소스 간의 네트워크 접근이 가능한지
- 자격 증명이 올바르고 충분한 권한이 있는지
- 방화벽 규칙이 연결을 허용하는지

#### 고급 설정

추가적인 제어가 필요한 사용자를 위해 DataHub는 고급 설정 섹션에서 접근 가능한 고급 설정 옵션을 제공합니다:

- **CLI 버전:** ingestion 실행을 위한 DataHub CLI의 특정 버전 지정
- **환경 변수:** ingestion 프로세스를 위한 커스텀 환경 변수 설정
- **Executor ID:** 필요한 경우 원격 실행 설정
- **디버그 모드:** 문제 해결을 위한 상세 로깅 활성화

### 3단계: 동기화 스케줄

DataHub가 소스에서 메타데이터를 동기화하는 빈도를 설정합니다. 토글을 사용하여 예약 실행을 활성화 또는 비활성화할 수 있습니다 (권장: 활성화). 이를 통해 수동 개입 없이 메타데이터를 최신 상태로 유지할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/schedule-ingestion.png"/>
</p>

수동으로 또는 임시로 ingestion을 실행하려면 스케줄링 단계를 완전히 건너뛸 수 있습니다.

### 4단계: 검토 및 저장

모든 설정이 올바른지 확인하기 위해 설정을 검토합니다. 준비가 되면 두 가지 옵션이 있습니다:

- **저장**: 즉시 실행하지 않고 ingestion 소스 설정 저장
- **저장 및 실행**: 저장하고 즉시 첫 번째 ingestion 실행 시작

설정에 만족하면 원하는 저장 옵션을 클릭하여 소스를 완료합니다.

## Ingestion 실행 및 모니터링

### Ingestion 소스 실행

Ingestion Source를 생성한 후 '실행' 버튼을 클릭하여 실행할 수 있습니다. 잠시 후 ingestion 소스의 '마지막 상태' 열이 `Running`으로 변경되어 DataHub가 ingestion 작업을 성공적으로 대기열에 추가했음을 나타냅니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion/running.png"/>
</p>

ingestion이 성공적으로 완료되면 상태가 녹색의 `Success`로 표시됩니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion/success-run.png"/>
</p>

### 실행 내역 보기

**Run History** 탭에는 모든 ingestion 실행의 완전한 내역이 표시됩니다. 여기서 다음을 수행할 수 있습니다:

- **모든 실행 보기**: 모든 소스의 모든 ingestion 실행 보기
- **최근 활동 확인**: 실행 목록에서 가장 최근 것이 상단에 표시
- **소스별 필터링**: 드롭다운을 사용하여 특정 ingestion 소스의 실행 보기
- **소스 탭에서 접근**: 소스의 **Last Run** 상태를 클릭하거나 소스 메뉴에서 **View Run History** 선택

이를 통해 ingestion 성능을 추적하고 시간이 지남에 따라 발생하는 문제를 쉽게 해결할 수 있습니다.

<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion/run-history-tab.png"/>
</p>

### Ingestion 결과 보기

성공적인 ingestion 후에 추출된 내용에 대한 자세한 정보를 볼 수 있습니다:

1. 완료된 ingestion 실행의 **Success** 상태 버튼 클릭
2. **View All**을 선택하여 수집된 엔티티 목록 보기
3. 개별 엔티티를 클릭하여 추출된 메타데이터 검증

<p align="center">
  <img width="75%" alt="ingestion_details_view_all" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion/ingestion-run-summary.png"/>
</p>

### 실행 중인 Ingestion 취소

ingestion 실행이 너무 오래 걸리거나 멈춘 것처럼 보이면 실행 중인 작업의 '정지' 버튼을 클릭하여 취소할 수 있습니다.

<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion/cancelled-run.png"/>
</p>

다음과 같은 문제가 발생할 때 유용합니다:

- 네트워크 타임아웃
- Ingestion 소스 버그
- 리소스 제약

## 실패한 Ingestion 문제 해결

### 일반적인 실패 원인

ingestion 실행이 실패하면 소스 목록에 실패 상태 표시기가 나타납니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion/failed-source.png"/>
</p>

ingestion 실패의 일반적인 원인은 다음과 같습니다:

1. **설정 오류**: 잘못된 연결 세부 정보, 누락된 필수 필드 또는 잘못된 매개변수 값
2. **인증 문제**: 잘못된 자격 증명, 만료된 토큰 또는 불충분한 권한
3. **네트워크 연결**: DNS 확인 실패, 방화벽 차단 또는 접근 불가능한 데이터 소스
4. **시크릿 확인 문제**: 존재하지 않거나 이름이 잘못된 참조된 시크릿
5. **리소스 제약**: 메모리 제한, 타임아웃 또는 처리 용량 문제

### 자세한 로그 보기

ingestion 실패를 진단하려면 실행 내역 상태 (Failed, Aborted) 값을 클릭하여 포괄적인 ingestion 실행 로그를 보고 다운로드하세요.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion/ingestion-run-log.png"/>
</p>

로그는 다음에 대한 자세한 정보를 제공합니다:

- 연결 시도 및 오류
- 인증 실패
- 데이터 추출 진행 상황
- 오류 메시지 및 스택 추적

### 보안된 DataHub 인스턴스에 대한 인증

DataHub 인스턴스에 [메타데이터 서비스 인증](authentication/introducing-metadata-service-authentication.md)이 활성화된 경우 설정에 개인 액세스 토큰을 제공해야 합니다.

<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ingestion-with-token.png"/>
</p>

## YAML을 사용한 고급 설정

UI 기반 양식이 대부분의 일반적인 ingestion 시나리오를 처리하지만, 고급 사용자는 다음과 같은 경우에 YAML 설정에 직접 접근해야 할 수 있습니다:

- UI에서 사용할 수 없는 커스텀 ingestion 소스
- 복잡한 변환 파이프라인
- 고급 필터링 및 처리 로직
- 외부 시스템과의 통합

이러한 고급 사용 사례를 위해 DataHub는 직접 YAML 레시피 설정을 지원합니다. YAML 기반 설정에 대한 자세한 내용(문법 및 예시 포함)은 [레시피 개요 가이드](metadata-ingestion/recipe_overview.md)를 참고하세요.

### 레시피 배포 (CLI)

[ingestion 레시피 업로드에 대한 CLI 문서](./cli.md#ingest-deploy)에 언급된 대로 CLI를 사용하여 레시피를 배포할 수 있습니다.

```bash
datahub ingest deploy --name "My Test Ingestion Source" --schedule "5 * * * *" --time-zone "UTC" -c recipe.yaml
```

### 레시피 배포 (GraphQL)

**createIngestionSource** mutation 엔드포인트를 사용하여 [DataHub의 GraphQL API](./api/graphql/overview.md)를 통해 ingestion 소스를 생성합니다.

```graphql
mutation {
  createIngestionSource(
    input: {
      name: "My Test Ingestion Source"
      type: "mysql"
      description: "My ingestion source description"
      schedule: { interval: "*/5 * * * *", timezone: "UTC" }
      config: {
        recipe: "{\"source\":{\"type\":\"mysql\",\"config\":{\"include_tables\":true,\"database\":null,\"password\":\"${MYSQL_PASSWORD}\",\"profiling\":{\"enabled\":false},\"host_port\":null,\"include_views\":true,\"username\":\"${MYSQL_USERNAME}\"}},\"pipeline_name\":\"urn:li:dataHubIngestionSource:f38bd060-4ea8-459c-8f24-a773286a2927\"}"
        version: "0.8.18"
        executorId: "mytestexecutor"
      }
    }
  )
}
```

**참고**: GraphQL 사용 시 레시피는 큰따옴표 이스케이프 처리가 필요합니다.

## 자주 묻는 질문

### Docker 환경에서 '연결 실패' 오류로 ingestion이 실패하는 이유는 무엇인가요?

`datahub docker quickstart`를 사용하여 DataHub를 실행 중이고 연결 실패를 경험하는 경우, 네트워크 설정 문제일 수 있습니다. Ingestion executor가 DataHub의 백엔드 서비스에 접근하지 못할 수 있습니다.

Docker 내부 DNS 이름을 사용하도록 ingestion 설정을 업데이트해 보세요:

<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/quickstart-ingestion-config.png"/>
</p>

### 대시 표시(-) 상태는 무엇을 의미하고 어떻게 수정하나요?

ingestion 소스가 대시 표시(-) 상태를 표시하고 'Running'으로 변경되지 않는 경우, 다음을 의미할 수 있습니다:

1. **소스가 실행되도록 트리거된 적이 없음** - "실행" 버튼을 클릭하여 소스를 실행해 보세요
2. **DataHub actions executor가 실행 중이지 않거나 정상이 아님** (DataHub Core 사용자만 해당)

"실행"을 클릭해도 문제가 해결되지 않으면 DataHub Core 사용자는 actions 컨테이너를 진단해야 합니다:

1. `docker ps`로 컨테이너 상태 확인
2. `docker logs <container-id>`로 executor 로그 보기
3. 필요한 경우 actions 컨테이너 재시작

### 언제 UI ingestion 대신 CLI/YAML을 사용해야 하나요?

다음과 같은 경우 CLI 기반 ingestion을 사용하는 것을 고려하세요:

- DataHub의 네트워크에서 데이터 소스에 접근할 수 없는 경우 (DataHub Cloud의 경우 [원격 executors](managed-datahub/operator-guide/setting-up-remote-ingestion-executor.md) 사용)
- UI 템플릿에서 사용할 수 없는 커스텀 ingestion 로직이 필요한 경우
- Ingestion에 로컬 파일 시스템 접근이 필요한 경우
- 여러 환경에 걸쳐 ingestion을 분산시키고 싶은 경우
- 복잡한 변환이나 커스텀 메타데이터 처리가 필요한 경우

## 추가 리소스

- **데모 비디오**: [전체 UI ingestion 워크스루 보기](https://www.youtube.com/watch?v=EyMyLcaw_74)
- **빠른 시작 가이드**: 인기 있는 데이터 소스에 대한 단계별 설정 안내
- **레시피 문서**: [포괄적인 YAML 설정 레퍼런스](metadata-ingestion/recipe_overview.md)
- **통합 카탈로그**: [지원되는 모든 데이터 소스 및 기능 탐색](https://docs.datahub.com/integrations)
