# Spark

Spark를 DataHub와 통합하기 위해 Spark 애플리케이션 및 job 이벤트를 수신하고 메타데이터를 DataHub에 실시간으로 push하는 경량 Java 에이전트를 제공합니다. 에이전트는 애플리케이션 시작/종료 및 SQLExecution 시작/종료와 같은 이벤트를 수신하여 DataHub에 파이프라인(즉, DataFlow)과 태스크(즉, DataJob)를 생성하고, 읽기 및 쓰기가 수행되는 dataset에 대한 lineage를 함께 생성합니다. 다양한 Spark 시나리오에서 이를 구성하는 방법을 알아보세요.

## Spark 에이전트 구성

Spark 에이전트는 설정 파일 또는 Spark Session 생성 시 구성할 수 있습니다. Databricks에서 Spark를 사용하는 경우 [Databricks 구성 지침](#configuration-instructions-databricks)을 참조하세요.

### 시작하기 전에: 버전 및 릴리스 노트

jar 아티팩트의 버전 관리는 메인 [DataHub 저장소](https://github.com/datahub-project/datahub)의 시맨틱 버전 관리를 따르며, 릴리스 노트는
[여기](https://github.com/datahub-project/datahub/releases)에서 확인할 수 있습니다.
최신 릴리스 버전은 항상 [Maven 중앙 저장소](https://search.maven.org/search?q=a:acryl-spark-lineage)에서 확인하세요.

**참고**: 버전 0.2.18부터 서로 다른 Scala 버전에 대해 별도의 jar를 제공합니다:

- Scala 2.12의 경우: `io.acryl:acryl-spark-lineage_2.12:0.2.18`
- Scala 2.13의 경우: `io.acryl:acryl-spark-lineage_2.13:0.2.18`

### 구성 지침: spark-submit

spark-submit으로 job을 실행할 때 에이전트를 설정 파일에 구성해야 합니다.

```text
#Configuring DataHub spark agent jar
spark.jars.packages                          io.acryl:acryl-spark-lineage_2.12:0.2.18
spark.extraListeners                         datahub.spark.DatahubSparkListener
spark.datahub.rest.server                    http://localhost:8080
```

Scala 2.13의 경우:

```text
#Configuring DataHub spark agent jar for Scala 2.13
spark.jars.packages                          io.acryl:acryl-spark-lineage_2.13:0.2.18
spark.extraListeners                         datahub.spark.DatahubSparkListener
spark.datahub.rest.server                    http://localhost:8080
```

## spark-submit 커맨드라인

```sh
spark-submit --packages io.acryl:acryl-spark-lineage_2.12:0.2.18 --conf "spark.extraListeners=datahub.spark.DatahubSparkListener" my_spark_job_to_run.py
```

Scala 2.13의 경우:

```sh
spark-submit --packages io.acryl:acryl-spark-lineage_2.13:0.2.18 --conf "spark.extraListeners=datahub.spark.DatahubSparkListener" my_spark_job_to_run.py
```

### 구성 지침: Amazon EMR

[여기](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-configure.html)에 명시된 대로 다음 spark-defaults 설정 속성을 구성하세요.

```text
spark.jars.packages                          io.acryl:acryl-spark-lineage_2.12:0.2.18
spark.extraListeners                         datahub.spark.DatahubSparkListener
spark.datahub.rest.server                    https://your_datahub_host/gms
#If you have authentication set up then you also need to specify the Datahub access token
spark.datahub.rest.token                     yourtoken
```

### 구성 지침: 노트북

노트북에서 인터랙티브 job을 실행할 때 Spark Session을 빌드하면서 리스너를 구성할 수 있습니다.

```python
spark = SparkSession.builder
.master("spark://spark-master:7077")
.appName("test-application")
.config("spark.jars.packages", "io.acryl:acryl-spark-lineage_2.12:0.2.18")
.config("spark.extraListeners", "datahub.spark.DatahubSparkListener")
.config("spark.datahub.rest.server", "http://localhost:8080")
.enableHiveSupport()
.getOrCreate()
```

### 구성 지침: 독립형 Java 애플리케이션

독립형 Java 앱의 구성도 매우 유사합니다.

```java
spark =SparkSession.

builder()
        .

appName("test-application")
        .

config("spark.master","spark://spark-master:7077")
        .

config("spark.jars.packages","io.acryl:acryl-spark-lineage_2.12:0.2.18")
        .

config("spark.extraListeners","datahub.spark.DatahubSparkListener")
        .

config("spark.datahub.rest.server","http://localhost:8080")
        .

enableHiveSupport()
        .

getOrCreate();
```

### 구성 지침: Databricks

Spark 에이전트는 Databricks 클러스터 [Spark 설정](https://docs.databricks.com/clusters/configure.html#spark-configuration) 및 [Init 스크립트](https://docs.databricks.com/clusters/configure.html#init-scripts)를 사용하여 구성할 수 있습니다.

토큰과 같은 민감한 정보를 저장하기 위해 [Databricks Secrets](https://docs.databricks.com/security/secrets/secrets.html)를 활용할 수 있습니다.

- [Maven 중앙 저장소](https://s01.oss.sonatype.org/content/groups/public/io/acryl/acryl-spark-lineage/)에서 `datahub-spark-lineage` jar를 다운로드합니다.
- 아래 내용으로 `init.sh`를 생성합니다

  ```sh
  #!/bin/bash
  cp /dbfs/datahub/datahub-spark-lineage*.jar /databricks/jars
  ```

- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html)를 설치하고 구성합니다.
- Databricks CLI를 사용하여 jar와 init 스크립트를 Databricks 파일 시스템(DBFS)에 복사합니다.

  ```sh
  databricks fs mkdirs dbfs:/datahub
  databricks fs cp --overwrite datahub-spark-lineage*.jar dbfs:/datahub
  databricks fs cp --overwrite init.sh dbfs:/datahub
  ```

- Databricks 클러스터 구성 페이지를 엽니다. **Advanced Options** 토글을 클릭합니다. **Spark** 탭을 클릭합니다. `Spark Config` 아래에 다음 구성을 추가합니다.

  ```text
  spark.extraListeners                    datahub.spark.DatahubSparkListener
  spark.datahub.rest.server               http://localhost:8080
  spark.datahub.stage_metadata_coalescing true
  spark.datahub.databricks.cluster        cluster-name<any preferred cluster identifier>
  ```

- **Init Scripts** 탭을 클릭합니다. 클러스터 init 스크립트를 `dbfs:/datahub/init.sh`로 설정합니다.

- DataHub 인증 토큰 구성

  - 클러스터 spark 설정에 아래 구성을 추가합니다.

    ```text
    spark.datahub.rest.token <token>
    ```

  - 또는 Databricks secrets를 사용하여 토큰을 보안하게 관리할 수 있습니다.

    - Databricks CLI를 사용하여 secret을 생성합니다.

      ```sh
      databricks secrets create-scope --scope datahub --initial-manage-principal users
      databricks secrets put --scope datahub --key rest-token
      databricks secrets list --scope datahub &lt;&lt;Edit prompted file with token value&gt;&gt;
      ```

    - spark 설정에 추가합니다

      ```text
      spark.datahub.rest.token {{secrets/datahub/rest-token}}
      ```

## 구성 옵션

| 필드                                                             | 필수 여부 | 기본값                  | 설명                                                                                                                                                                                                                      |
| ---------------------------------------------------------------- | --------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| spark.jars.packages                                              | ✅        |                         | 최신/필요 버전으로 설정: io.acryl:acryl-spark-lineage_2.12:0.2.18 (또는 Scala 2.13의 경우 io.acryl:acryl-spark-lineage_2.13:0.2.18)                                                                                       |
| spark.extraListeners                                             | ✅        |                         | datahub.spark.DatahubSparkListener                                                                                                                                                                                        |
| spark.datahub.emitter                                            |           | rest                    | 메타데이터를 emit하는 방법을 지정합니다. 기본적으로 REST emitter를 사용하여 DataHub로 전송합니다. 유효한 옵션: rest, kafka 또는 file                                                                                       |
| spark.datahub.rest.server                                        |           | <http://localhost:8080> | Datahub 서버 URL. 예: <http://localhost:8080>                                                                                                                                                                             |
| spark.datahub.rest.token                                         |           |                         | 인증 토큰.                                                                                                                                                                                                                |
| spark.datahub.rest.disable_ssl_verification                      |           | false                   | SSL 인증서 검증 비활성화. 주의: 무엇을 하는지 알고 있는 경우에만 사용하세요!                                                                                                                                              |
| spark.datahub.rest.disable_chunked_encoding                      |           | false                   | 청크 전송 인코딩 비활성화. 일부 환경에서 청크 인코딩이 문제를 일으키는 경우 이 옵션으로 비활성화할 수 있습니다.                                                                                                           |
| spark.datahub.rest.max_retries                                   |           | 0                       | 실패 시 요청을 재시도하는 횟수                                                                                                                                                                                            |
| spark.datahub.rest.retry_interval                                |           | 10                      | 재시도 간 대기 시간(초)                                                                                                                                                                                                   |
| spark.datahub.file.filename                                      |           |                         | file emitter가 설정된 경우 메타데이터가 기록될 파일                                                                                                                                                                       |
| spark.datahub.kafka.bootstrap                                    |           |                         | Kafka emitter가 설정된 경우 사용할 Kafka 부트스트랩 서버 URL                                                                                                                                                              |
| spark.datahub.kafka.schema_registry_url                          |           |                         | Kafka emitter가 설정된 경우 사용할 Schema Registry URL                                                                                                                                                                    |
| spark.datahub.kafka.schema_registry_config.                      |           |                         | Schema Registry Client에 전달할 추가 설정                                                                                                                                                                                 |
| spark.datahub.kafka.producer_config.                             |           |                         | Kafka producer에 전달할 추가 설정. 예: `--conf "spark.datahub.kafka.producer_config.client.id=my_client_id"`                                                                                                              |
| spark.datahub.metadata.pipeline.platformInstance                 |           |                         | 파이프라인 수준 platform instance                                                                                                                                                                                         |
| spark.datahub.metadata.dataset.platformInstance                  |           |                         | dataset 수준 platform instance (다른 ingestion 소스로 생성된 dataset URN과 일치시킬 때 유용)                                                                                                                              |
| spark.datahub.metadata.dataset.env                               |           | PROD                    | [지원되는 값](https://docs.datahub.com/docs/graphql/enums#fabrictype). 그 외의 경우 PROD로 대체됩니다                                                                                                                     |
| spark.datahub.metadata.dataset.hivePlatformAlias                 |           | hive                    | 기본적으로 DataHub는 Hive 유사 테이블을 Hive 플랫폼에 할당합니다. Glue를 Hive 메타스토어로 사용하는 경우 이 설정 플래그를 `glue`로 설정하세요                                                                            |
| spark.datahub.metadata.include_scheme                            |           | true                    | 경로 URI의 스킴(예: hdfs://, s3://)을 dataset URN에 포함합니다. false로 설정하는 것을 권장하지만, 이전 버전과의 호환성을 위해 true로 설정되어 있습니다                                                                    |
| spark.datahub.metadata.remove_partition_pattern                  |           |                         | 파티션 패턴 제거 (예: /partition=\d+). database/table/partition=123을 database/table로 변경합니다                                                                                                                         |
| spark.datahub.coalesce_jobs                                      |           | true                    | Spark 애플리케이션의 모든 입력 및 출력 dataset을 포함하는 하나의 DataJob(태스크)만 emit됩니다                                                                                                                             |
| spark.datahub.parent.datajob_urn                                 |           |                         | 지정된 dataset이 생성된 DataJob의 upstream dataset으로 설정됩니다. spark.datahub.coalesce_jobs가 true로 설정된 경우에만 적용됩니다                                                                                        |
| spark.datahub.metadata.dataset.materialize                       |           | false                   | DataHub에서 dataset을 구체화합니다                                                                                                                                                                                        |
| spark.datahub.platform.s3.path_spec_list                         |           |                         | 플랫폼별 path spec 목록                                                                                                                                                                                                   |
| spark.datahub.metadata.dataset.include_schema_metadata           |           | false                   | Spark 실행을 기반으로 dataset schema 메타데이터를 emit합니다. 이 방법은 신뢰성이 떨어지므로 플랫폼 특화 DataHub 소스에서 schema 정보를 가져오는 것을 권장합니다                                                          |
| spark.datahub.flow_name                                          |           |                         | 설정된 경우 DataFlow 이름으로 사용됩니다. 설정되지 않은 경우 Spark 앱 이름을 flow_name으로 사용합니다                                                                                                                    |
| spark.datahub.file_partition_regexp                              |           |                         | 경로 끝이 지정된 정규식과 일치하는 경우 경로에서 파티션 부분을 제거합니다. 예: `year=.*/month=.*/day=.*`                                                                                                                  |
| spark.datahub.tags                                               |           |                         | DataFlow에 연결할 태그의 쉼표로 구분된 목록                                                                                                                                                                               |
| spark.datahub.domains                                            |           |                         | DataFlow에 연결할 도메인 URN의 쉼표로 구분된 목록                                                                                                                                                                        |
| spark.datahub.stage_metadata_coalescing                          |           | false                   | 일반적으로 메타데이터는 onApplicationEnd 이벤트에서 병합되어 전송되지만, 이 이벤트는 Databricks나 Glue에서 호출되지 않습니다. Databricks에서 병합된 실행을 원하는 경우 이를 활성화하세요.                                |
| spark.datahub.patch.enabled                                      |           | false                   | lineage를 패치로 전송하도록 true로 설정합니다. 이를 통해 기존 dataset lineage 엣지를 덮어쓰지 않고 추가합니다. 기본적으로 비활성화되어 있습니다.                                                                          |
| spark.datahub.metadata.dataset.lowerCaseUrns                     |           | false                   | dataset URN을 소문자로 변환하도록 true로 설정합니다. 기본적으로 비활성화되어 있습니다.                                                                                                                                    |
| spark.datahub.disableSymlinkResolution                           |           | false                   | Hive 테이블 대신 S3 위치를 사용하려는 경우 true로 설정합니다. 기본적으로 비활성화되어 있습니다.                                                                                                                          |
| spark.datahub.s3.bucket                                          |           |                         | s3 emitter가 설정된 경우 메타데이터가 기록될 버킷 이름                                                                                                                                                                    |
| spark.datahub.s3.prefix                                          |           |                         | s3 emitter가 설정된 경우 S3에서 메타데이터가 기록될 파일의 접두사                                                                                                                                                        |
| spark.datahub.s3.filename                                        |           |                         | s3 emitter가 설정된 경우 메타데이터가 기록될 파일 이름 (설정되지 않은 경우 랜덤 파일 이름 사용)                                                                                                                           |
| spark.datahub.log.mcps                                           |           | true                    | MCPS를 로그에 기록하려면 true로 설정합니다. 기본적으로 활성화되어 있습니다.                                                                                                                                               |
| spark.datahub.legacyLineageCleanup.enabled                       |           | false                   | 이전 Spark 플러그인 실행에서 남은 레거시 lineage를 제거하려면 true로 설정합니다. DataJob에 추가하는 dataset에서 해당 lineage를 제거합니다. 기본적으로 비활성화되어 있습니다.                                              |
| spark.datahub.captureColumnLevelLineage                          |           | true                    | 대규모 dataset에서 성능 향상을 위해 컬럼 수준 lineage 캡처를 비활성화하려면 false로 설정합니다.                                                                                                                           |
| spark.datahub.capture_spark_plan                                 |           | false                   | Spark 플랜을 캡처하려면 true로 설정합니다. 기본적으로 비활성화되어 있습니다.                                                                                                                                              |
| spark.datahub.metadata.dataset.enableEnhancedMergeIntoExtraction |           | false                   | Delta Lake MERGE INTO 명령에 대한 향상된 테이블 이름 추출을 활성화하려면 true로 설정합니다. job 이름에 대상 테이블 이름을 포함하여 lineage 추적을 개선합니다. 기본적으로 비활성화되어 있습니다.                           |

## 메타데이터 모델 예상 결과

현재 시점에서 Spark 에이전트는 Spark job, 태스크 및 dataset에 대한 lineage 엣지와 관련된 메타데이터를 생성합니다.

- Spark <master, appName>당 하나의 파이프라인이 생성됩니다.
- 앱 내의 각 고유한 Spark 쿼리 실행당 하나의 태스크가 생성됩니다.

Databricks의 Spark의 경우:

- 다음 항목당 하나의 파이프라인이 생성됩니다:
  - cluster_identifier: spark.datahub.databricks.cluster로 지정
  - applicationID: 클러스터 재시작 시마다 새로운 Spark applicationID가 생성됩니다.
- 각 고유한 Spark 쿼리 실행당 하나의 태스크가 생성됩니다.

### 사용자 정의 속성 및 Spark UI와의 연관성

파이프라인과 태스크의 다음 사용자 정의 속성은 Spark UI와 연관됩니다:

- 파이프라인의 appName과 appId를 사용하여 Spark 애플리케이션을 확인할 수 있습니다
- 파이프라인과 태스크의 기타 사용자 정의 속성은 실행 시작 및 종료 시간 등을 캡처합니다.

Databricks의 Spark의 경우, 파이프라인 시작 시간은 클러스터 시작 시간입니다.

### 컬럼 수준 Lineage 및 변환 타입

Spark 에이전트는 변환 타입을 포함한 컬럼 수준 lineage 등 세밀한 lineage 정보를 캡처합니다. 사용 가능한 경우 OpenLineage의 [변환 타입](https://openlineage.io/docs/spec/facets/dataset-facets/column_lineage_facet/#transformation-type)을 캡처하여 DataHub의 FinegrainedLineage `TransformOption`에 매핑하며, 컬럼 수준에서 데이터 변환이 어떻게 발생하는지에 대한 상세한 인사이트를 제공합니다.

### 지원되는 Spark 버전

Spark 3.x 시리즈를 지원합니다.

### 테스트된 환경

이 초기 릴리스는 다음 환경에서 테스트되었습니다:

- 로컬 및 원격 서버에 Python/Java 애플리케이션 spark-submit
- 독립형 Java 애플리케이션
- Databricks 독립형 클러스터
- EMR

Databricks 표준 및 고동시성 클러스터에서의 테스트는 아직 완료되지 않았습니다.

### HDFS 기반 dataset URN 구성

Spark는 dataset 간의 lineage를 emit합니다. URN 생성에 자체 로직을 사용합니다. Python 소스는 dataset의 메타데이터를 emit합니다. 이 두 가지를 연결하려면 양쪽에서 생성된 URN이 일치해야 합니다.
이 섹션은 다른 ingestion 소스의 URN과 일치시키는 데 도움을 드립니다.
기본적으로 URN은
`urn:li:dataset:(urn:li:dataPlatform:<$platform>,<platformInstance>.<name>,<env>)` 템플릿을 사용하여 생성됩니다. 원하는 URN을 생성하기 위해 이 4가지 항목을 구성할 수 있습니다.

**Platform**:
명시적으로 지원되는 HDFS 기반 플랫폼:

- AWS S3 (s3)
- Google Cloud Storage (gcs)
- Azure Storage:
  - Azure Blob Storage (abs) - wasb/wasbs 프로토콜 지원
  - Azure Data Lake Storage Gen2 (abs) - abfs/abfss 프로토콜 지원
- 로컬 파일 시스템 (file)
  기타 모든 플랫폼은 "hdfs"를 플랫폼으로 사용합니다.

**Name**:
기본적으로 이름은 전체 경로입니다. HDFS 기반 dataset의 경우 파티셔닝 및 샤딩 등 다양한 이유로 실제 파일 읽기 위치와 다른 경로 레벨에 테이블이 있을 수 있습니다. 'path_spec'은 이름을 변경하는 데 사용됩니다.
{table} 마커는 테이블 레벨을 지정하는 데 사용됩니다. 아래는 몇 가지 예시입니다. `path_spec_list`에 지정된 여러 경로에 대해 여러 path_spec을 지정할 수 있습니다. 각 실제 경로는 목록의 모든 path_spec에 대해 매칭됩니다. 처음 매칭되는 것이 URN 생성에 사용됩니다.

**path_spec 예시**

```
spark.datahub.platform.s3.path_spec_list=s3://my-bucket/foo/{table}/year=*/month=*/day=*/*,s3://my-other-bucket/foo/{table}/year=*/month=*/day=*/*"
```

| 절대 경로                            | path_spec                        | URN                                                                          |
| ------------------------------------ | -------------------------------- | ---------------------------------------------------------------------------- |
| s3://my-bucket/foo/tests/bar.avro    | 제공되지 않음                    | urn:li:dataset:(urn:li:dataPlatform:s3,my-bucket/foo/tests/bar.avro,PROD)    |
| s3://my-bucket/foo/tests/bar.avro    | s3://my-bucket/foo/{table}/\*    | urn:li:dataset:(urn:li:dataPlatform:s3,my-bucket/foo/tests,PROD)             |
| s3://my-bucket/foo/tests/bar.avro    | s3://my-bucket/foo/tests/{table} | urn:li:dataset:(urn:li:dataPlatform:s3,my-bucket/foo/tests/bar.avro,PROD)    |
| gs://my-bucket/foo/tests/bar.avro    | gs://my-bucket/{table}/_/_       | urn:li:dataset:(urn:li:dataPlatform:gcs,my-bucket/foo,PROD)                  |
| gs://my-bucket/foo/tests/bar.avro    | gs://my-bucket/{table}           | urn:li:dataset:(urn:li:dataPlatform:gcs,my-bucket/foo,PROD)                  |
| file:///my-bucket/foo/tests/bar.avro | file:///my-bucket/_/_/{table}    | urn:li:dataset:(urn:li:dataPlatform:local,my-bucket/foo/tests/bar.avro,PROD) |

**platform instance 및 env:**

env의 기본값은 'PROD'이고 platform instance는 None입니다. env와 platform instance는 'spark.datahub.metadata.dataset.env' 및 'spark.datahub.metadata.dataset.platformInstace' 설정을 사용하여 모든 dataset에 대해 설정할 수 있습니다.
Spark가 다른 env 또는 platform instance에 속하는 데이터를 처리하는 경우 `path_spec`별 값을 지정하기 위해 'path_alias'를 사용할 수 있습니다. 'path_alias'는 'path_spec_list', env, platform instance를 함께 그룹화합니다.

path_alias_list 예시:

아래 예시는 단일 Spark 애플리케이션에서 2개의 버킷 파일을 처리하는 경우 구성을 설명합니다. my-bucket의 파일은 platform instance로 "instance1"을 가져야 하고 env는 "PROD"이며, bucket2의 파일은 dataset URN에 env "DEV"를 가져야 합니다.

```
spark.datahub.platform.s3.path_alias_list :  path1,path2
spark.datahub.platform.s3.path1.env : PROD
spark.datahub.platform.s3.path1.path_spec_list: s3://my-bucket/*/*/{table}
spark.datahub.platform.s3.path1.platform_instance : instance-1
spark.datahub.platform.s3.path2.env: DEV
spark.datahub.platform.s3.path2.path_spec_list: s3://bucket2/*/{table}
```

### 사용 시 중요 참고사항

- appName을 적절히 사용하여 파이프라인에서 소스 코드로 lineage를 추적할 수 있도록 하는 것이 좋습니다.
- 동일한 appName을 가진 여러 앱이 동시에 실행되는 경우 dataset-lineage는 올바르게 캡처되지만
  app-id, SQLQueryId 등의 사용자 정의 속성은 신뢰할 수 없습니다. 이런 경우는 매우 드물 것으로 예상됩니다.
- Spark 실행이 실패하면 빈 파이프라인이 생성될 수 있으며 태스크가 없을 수도 있습니다.
- HDFS 소스의 경우 parquet/csv 형식의 일반적인 스토리지 방식에 맞추어 폴더(이름)를 dataset(이름)으로 간주합니다.

### Delta Lake MERGE INTO 명령

Delta Lake MERGE INTO 명령으로 작업할 때 기본 동작은 내부 Spark 태스크 이름을 기반으로 일반적인 job 이름을 생성합니다.
lineage 추적을 개선하려면 향상된 테이블 이름 추출 기능을 활성화할 수 있습니다:

```
spark.datahub.metadata.dataset.enableEnhancedMergeIntoExtraction=true
```

활성화하면 에이전트가 다음을 수행합니다:

1. Delta Lake MERGE INTO 명령을 감지합니다
2. SQL 쿼리, dataset 이름 또는 심링크에서 대상 테이블 이름을 추출합니다
3. job 이름에 테이블 이름을 포함하여 특정 테이블에 대한 작업을 쉽게 추적할 수 있게 합니다
4. DataHub에서 더 의미 있는 lineage를 생성합니다

예를 들어 `execute_merge_into_command_edge`라는 job 이름은 `execute_merge_into_command_edge.database_table_name`으로 향상되어 어떤 테이블이 수정되었는지 명확하게 표시됩니다.

### 디버깅

- 다음 정보 로그가 생성됩니다

Spark 컨텍스트 시작 시

```text
YY/MM/DD HH:mm:ss INFO DatahubSparkListener: DatahubSparkListener initialised.
YY/MM/DD HH:mm:ss INFO SparkContext: Registered listener datahub.spark.DatahubSparkListener
```

애플리케이션 시작 시

```text
YY/MM/DD HH:mm:ss INFO DatahubSparkListener: Application started: SparkListenerApplicationStart(AppName,Some(local-1644489736794),1644489735772,user,None,None)
YY/MM/DD HH:mm:ss INFO McpEmitter: REST Emitter Configuration: GMS url <rest.server>
YY/MM/DD HH:mm:ss INFO McpEmitter: REST Emitter Configuration: Token XXXXX
```

서버에 데이터 push 시

```text
YY/MM/DD HH:mm:ss INFO McpEmitter: MetadataWriteResponse(success=true, responseContent={"value":"<URN>"}, underlyingResponse=HTTP/1.1 200 OK [Date: day, DD month year HH:mm:ss GMT, Content-Type: application/json, X-RestLi-Protocol-Version: 2.0.0, Content-Length: 97, Server: Jetty(9.4.46.v20220331)] [Content-Length: 97,Chunked: false])
```

애플리케이션 종료 시

```text
YY/MM/DD HH:mm:ss INFO DatahubSparkListener: Application ended : AppName AppID
```

- 디버그 로그를 활성화하려면 log4j.properties 파일에 아래 설정을 추가하세요

```properties
log4j.logger.datahub.spark=DEBUG
log4j.logger.datahub.client.rest=DEBUG
```

## 빌드 방법

Java 8을 사용하여 프로젝트를 빌드합니다. 프로젝트는 Gradle을 빌드 도구로 사용합니다. 프로젝트를 빌드하려면 다음 명령을 실행하세요:

```shell
./gradlew -PjavaClassVersionDefault=8 :metadata-integration:java:acryl-spark-lineage:shadowJar
```

## 알려진 제한 사항

-

## 변경 이력

### 버전 0.2.18

- _변경 사항_:
  - OpenLineage 1.33.0 업그레이드
  - Spark 플랜 캡처를 위한 `spark.datahub.capture_spark_plan` 옵션 추가. 기본적으로 비활성화됩니다.
  - Spark Streaming 지원 추가
  - Delta 테이블이 Warehouse 위치 밖에 있을 때 플러그인이 경로만 캡처하고 테이블을 캡처하지 않는 문제 수정
  - Enhanced Merge Into Extraction 옵션 추가
  - lineage에서 map 변환을 올바르게 처리하도록 rdd map 감지 수정
  - **JAR 이름 변경**: 이 버전부터 서로 다른 Scala 버전에 대해 별도의 jar가 빌드됩니다:
    - Scala 2.12: `io.acryl:acryl-spark-lineage_2.12:0.2.18`
    - Scala 2.13: `io.acryl:acryl-spark-lineage_2.13:0.2.18`
  - **컬럼 수준 Lineage 향상**: [OpenLineage 컬럼 lineage 명세](https://openlineage.io/docs/spec/facets/dataset-facets/column_lineage_facet/#transformation-type)에 따라 OpenLineage의 변환 타입이 이제 캡처되어 DataHub의 FinegrainedLineage `TransformOption`에 매핑됩니다
  - **의존성 정리**: 사용자 애플리케이션과의 잠재적 충돌을 줄이기 위해 logback 의존성 제거
  - Spark 스트리밍용 FileStreamMicroBatchStream 및 foreachBatch 지원
  - MERGE INTO 작업이 이제 dataset 수준과 컬럼 수준 lineage 모두를 캡처합니다

### 버전 0.2.17

- _주요 변경 사항_:

  - 세밀한 lineage가 emit된 dataset이 아닌 DataJob에서 emit됩니다. 이전에 올바르지 않았던 올바른 동작입니다. 이로 인해 이전에 emit된 세밀한 lineage가 새로운 것으로 덮어쓰이지 않습니다.
    `spark.datahub.legacyLineageCleanup.enabled=true`를 설정하여 이전 lineage를 제거할 수 있습니다. 패치 지원이 활성화된 경우 최신 서버가 있는지 확인하세요. (0.2.17-rc5 이후에 도입됨)

- _변경 사항_:
  - OpenLineage 1.25.0 업그레이드
  - datahub rest 싱크에서 청크 인코딩 비활성화 옵션 추가 -> `spark.datahub.rest.disable_chunked_encoding`
  - datahub kafka 싱크의 mcp kafka 토픽 지정 옵션 추가 -> `spark.datahub.kafka.mcp_topic`
  - 이전 Spark 플러그인 실행에서 레거시 lineage 제거 옵션 추가. DataJob에 추가하는 dataset에서 해당 lineage를 제거합니다 -> `spark.datahub.legacyLineageCleanup.enabled`
- _수정 사항_:
  - lineage에서 map 변환 처리 수정. 이전에는 map 변환에 대해 잘못된 lineage를 생성했습니다.

### 버전 0.2.16

- DataHub 설정을 로그에 기록하지 않도록 변경

### 버전 0.2.15

- lineage를 kafka로 emit하는 Kafka emitter 추가
- lineage를 파일로 emit하는 File emitter 추가
- MCP를 S3에 저장하는 S3 emitter 추가
- OpenLineage를 1.19.0으로 업그레이드
- 프로젝트 이름을 acryl-datahub-spark-lineage로 변경
- OpenLineage 1.17+ glue 식별자 변경 지원
- facet이 없는 OpenLineage 입력/출력 처리 수정

### 버전 0.2.14

- Micrometer의 MeterFilter 경고 수정

### 버전 0.2.13

- lineage를 kafka로 emit하는 kafka emitter 추가

### 버전 0.2.12

- RddPathUtils의 불필요한 경고 메시지 제거

### 버전 0.2.11

- dataset URN을 소문자로 변환하는 옵션 추가
- `spark.datahub.platform.<platform_name>.env` 및 `spark.datahub.platform.<platform_name>.platform_instance` 설정 매개변수로 플랫폼별 platform instance 및/또는 env 설정 옵션 추가
- `spark.datahub.metadata.dataset.platformInstance` 설정 시 dataset의 platform instance 설정 수정
- 패치가 활성화된 경우 컬럼 수준 lineage 지원 수정
