# Great Expectations

이 가이드는 DataHub의 Python REST 에미터를 사용하여 assertions(기대값)와 그 결과를 DataHub로 전송하기 위해 Great Expectations에서 `DataHubValidationAction`을 설정하고 구성하는 방법을 안내합니다.

## 기능

`DataHubValidationAction`은 DataHub에 assertions 메타데이터를 푸시합니다. 여기에는 다음이 포함됩니다.

- **Assertion 세부 정보**: Dataset(테이블)에 설정된 assertions(기대값)의 세부 정보.
- **Assertion 결과**: 시간이 지남에 따라 추적되는 assertion의 평가 결과.

이 통합은 SqlAlchemyExecutionEngine과 SparkDFExecutionEngine을 사용하는 v3 API 데이터 소스를 지원합니다.

SparkDFExecutionEngine의 경우, DataHubValidationAction은 dataset URN을 구성할 때 GX의 **Data Asset**을 dataset의 엔티티 이름으로 매핑합니다.

## 제한 사항

이 통합은 다음을 지원하지 않습니다.

- SqlAlchemyDataset과 같은 v2 데이터 소스
- SqlAlchemyExecutionEngine, SparkDFExecutionEngine 이외의 실행 엔진(Pandas)을 사용하는 v3 데이터 소스
- 여러 테이블(> 1개)을 포함하는 크로스 dataset 기대값

## 호환성

- SparkDFExecutionEngine을 사용하는 DataHubValidationAction은 **Great Expectation >= 0.18.0, <1.0.0**에서만 테스트되었습니다. 다른 버전은 호환되지 않을 수 있습니다.

## 설정

1. Great Expectations 환경에 필요한 종속성을 설치합니다.

   ```shell
   pip install 'acryl-datahub-gx-plugin'
   ```

2. Great Expectations Checkpoint에 `DataHubValidationAction`을 추가하려면 Great Expectations `Checkpoint`의 action_list에 다음 설정을 추가하세요. action_list 설정에 대한 자세한 내용은 [Checkpoints and Actions](https://docs.greatexpectations.io/docs/reference/checkpoints_and_actions/)를 참고하세요.
   ```yml
   action_list:
     - name: datahub_action
       action:
         module_name: datahub_gx_plugin.action
         class_name: DataHubValidationAction
         server_url: http://localhost:8080 #datahub server url
   ```
   **설정 옵션:**
   - `server_url` (필수): DataHub GMS 엔드포인트의 URL
   - `env` (선택 사항, 기본값 "PROD"): dataset URN을 구성할 때 네임스페이스에 사용할 환경.
   - `exclude_dbname` (선택 사항): dataset URN을 구성할 때 dbname/카탈로그를 제외합니다. (카탈로그를 생략하려는 Trino/Presto에 매우 적용 가능, 예: `hive`)
   - `platform_alias` (선택 사항): dataset URN을 구성할 때의 플랫폼 별칭. 예: 주 데이터 플랫폼은 `presto-on-hive`이지만 테스트를 실행하는 데 `trino` 사용
   - `platform_instance_map` (선택 사항): dataset URN을 구성할 때 사용할 플랫폼 인스턴스 매핑. GX '데이터 소스' 이름을 DataHub의 플랫폼 인스턴스에 매핑합니다. 예: `platform_instance_map: { "datasource_name": "warehouse" }`
   - `graceful_exceptions` (기본값 true): true로 설정하면 lineage 백엔드의 대부분의 런타임 오류가 억제되어 전체 checkpoint가 실패하지 않습니다. 설정 문제는 여전히 예외를 발생시킵니다.
   - `token` (선택 사항): 인증에 사용되는 Bearer 토큰.
   - `timeout_sec` (선택 사항): HTTP 요청당 타임아웃.
   - `retry_status_codes` (선택 사항): 이 상태 코드에서도 HTTP 요청을 재시도합니다.
   - `retry_max_times` (선택 사항): HTTP 요청이 실패할 경우 최대 재시도 횟수. 재시도 간격은 지수적으로 증가합니다.
   - `extra_headers` (선택 사항): datahub 요청에 추가될 추가 헤더.
   - `parse_table_names_from_sql` (기본값 false): 통합은 SQL 파서를 사용하여 어설트되는 dataset을 파싱하려고 시도할 수 있습니다. 이 파싱은 기본적으로 비활성화되어 있지만 `parse_table_names_from_sql: True`로 설정하여 활성화할 수 있습니다. 파서는 [`sqllineage`](https://pypi.org/project/sqllineage/) 패키지를 기반으로 합니다.
   - `convert_urns_to_lowercase` (선택 사항): dataset URN을 소문자로 변환할지 여부.

## 디버깅

`DataHubValidationAction`에 대한 디버그 로깅을 활성화하려면 환경 변수 `DATAHUB_DEBUG` (기본값 `false`)를 `true`로 설정하세요.

## 더 알아보기

Great Expectations가 실제로 작동하는 것을 보려면 2022년 2월 타운홀에서의 [이 데모](https://www.loom.com/share/d781c9f0b270477fb5d6b0c26ef7f22d)를 확인하세요.
