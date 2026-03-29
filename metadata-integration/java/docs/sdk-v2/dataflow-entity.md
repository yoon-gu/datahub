# DataFlow Entity

`DataFlow` entity는 DataHub에서 데이터 처리 파이프라인 또는 워크플로를 나타냅니다. Apache Airflow, Apache Spark, dbt, Apache Flink 및 기타 데이터 오케스트레이션 플랫폼의 오케스트레이션된 워크플로를 모델링합니다.

## 개요

DataFlow는 데이터 변환 또는 이동 목표를 달성하기 위해 함께 동작하는 데이터 처리 태스크의 논리적 그룹입니다. DataFlow는 일반적으로 다음과 같습니다:

- **스케줄 워크플로** (Airflow DAG)
- **배치 처리 job** (Spark 애플리케이션)
- **변환 프로젝트** (dbt 프로젝트)
- **스트리밍 파이프라인** (Flink job)

DataFlow는 `DataJob` entity의 부모 컨테이너 역할을 하며, 전체 파이프라인을 나타내는 반면 개별 job은 파이프라인 내의 특정 태스크를 나타냅니다.

## URN 구조

DataFlow URN은 다음 형식을 따릅니다:

```
urn:li:dataFlow:(orchestrator,flowId,cluster)
```

**구성 요소:**

- **orchestrator**: 워크플로를 실행하는 플랫폼 또는 도구 (예: "airflow", "spark", "dbt", "flink")
- **flowId**: 오케스트레이터 내에서 flow의 고유 식별자 (예: DAG ID, job 이름, 프로젝트 이름)
- **cluster**: flow가 실행되는 클러스터 또는 환경 (예: "prod", "prod-us-west-2", "emr-cluster")

**예시:**

```
urn:li:dataFlow:(airflow,customer_etl_daily,prod)
urn:li:dataFlow:(spark,ml_feature_generation,emr-prod-cluster)
urn:li:dataFlow:(dbt,marketing_analytics,prod)
```

## DataFlow 생성

### 기본 생성

```java
DataFlow dataflow = DataFlow.builder()
    .orchestrator("airflow")
    .flowId("my_dag_id")
    .cluster("prod")
    .displayName("My ETL Pipeline")
    .description("Daily ETL pipeline for customer data")
    .build();

client.entities().upsert(dataflow);
```

### 사용자 정의 속성과 함께 생성

```java
Map<String, String> properties = new HashMap<>();
properties.put("schedule", "0 2 * * *");
properties.put("team", "data-engineering");
properties.put("sla_hours", "4");

DataFlow dataflow = DataFlow.builder()
    .orchestrator("airflow")
    .flowId("customer_pipeline")
    .cluster("prod")
    .customProperties(properties)
    .build();
```

## 속성

### 핵심 속성

| 속성           | 타입   | 설명                              | 예시                            |
| -------------- | ------ | --------------------------------- | ------------------------------- |
| `orchestrator` | String | flow를 실행하는 플랫폼 (필수)     | "airflow", "spark", "dbt"       |
| `flowId`       | String | 고유 flow 식별자 (필수)           | "my_dag_id", "my_job_name"      |
| `cluster`      | String | 클러스터/환경 (필수)              | "prod", "dev", "prod-us-west-2" |
| `displayName`  | String | 사람이 읽을 수 있는 이름          | "Customer ETL Pipeline"         |
| `description`  | String | Flow 설명                         | "Processes customer data daily" |

### 추가 속성

| 속성               | 타입                | 설명                               |
| ------------------ | ------------------- | ---------------------------------- |
| `externalUrl`      | String              | 오케스트레이션 도구의 flow 링크    |
| `project`          | String              | 연관된 프로젝트 또는 네임스페이스  |
| `customProperties` | Map<String, String> | 키-값 메타데이터                   |
| `created`          | Long                | 생성 타임스탬프 (밀리초)           |
| `lastModified`     | Long                | 마지막 수정 타임스탬프 (밀리초)    |

## 작업

### 소유권

```java
// 소유자 추가
dataflow.addOwner("urn:li:corpuser:johndoe", OwnershipType.TECHNICAL_OWNER);
dataflow.addOwner("urn:li:corpuser:analytics_team", OwnershipType.BUSINESS_OWNER);

// 소유자 제거
dataflow.removeOwner("urn:li:corpuser:johndoe");
```

### 태그

```java
// 태그 추가 ("urn:li:tag:" 접두사 있음 또는 없음)
dataflow.addTag("etl");
dataflow.addTag("production");
dataflow.addTag("urn:li:tag:pii");

// 태그 제거
dataflow.removeTag("etl");
```

### 용어 (Glossary Terms)

```java
// 용어 추가
dataflow.addTerm("urn:li:glossaryTerm:ETL");
dataflow.addTerm("urn:li:glossaryTerm:DataPipeline");

// 용어 제거
dataflow.removeTerm("urn:li:glossaryTerm:ETL");
```

### 도메인

```java
// 도메인 설정
dataflow.setDomain("urn:li:domain:DataEngineering");

// 특정 도메인 제거
dataflow.removeDomain("urn:li:domain:DataEngineering");

// 또는 모든 도메인 초기화
dataflow.clearDomains();
```

### 사용자 정의 속성

```java
// 개별 속성 추가
dataflow.addCustomProperty("schedule", "0 2 * * *");
dataflow.addCustomProperty("team", "data-engineering");

// 속성 제거
dataflow.removeCustomProperty("schedule");

// 모든 속성 설정 (기존 속성 대체)
Map<String, String> props = new HashMap<>();
props.put("key1", "value1");
props.put("key2", "value2");
dataflow.setCustomProperties(props);
```

### 설명 및 표시 이름

```java
// 설명 설정
dataflow.setDescription("Daily ETL pipeline for customer data");

// 표시 이름 설정
dataflow.setDisplayName("Customer ETL Pipeline");

// 설명 가져오기
String description = dataflow.getDescription();

// 표시 이름 가져오기
String displayName = dataflow.getDisplayName();
```

### 타임스탬프 및 URL

```java
// 외부 URL 설정
dataflow.setExternalUrl("https://airflow.example.com/dags/my_dag");

// 프로젝트 설정
dataflow.setProject("customer_analytics");

// 타임스탬프 설정
dataflow.setCreated(System.currentTimeMillis() - 86400000L); // 1일 전
dataflow.setLastModified(System.currentTimeMillis());
```

## 오케스트레이터별 예시

### Apache Airflow

```java
DataFlow airflowFlow = DataFlow.builder()
    .orchestrator("airflow")
    .flowId("customer_etl_daily")
    .cluster("prod")
    .displayName("Customer ETL Pipeline")
    .description("Daily pipeline processing customer data from MySQL to Snowflake")
    .build();

airflowFlow
    .addTag("etl")
    .addTag("production")
    .addCustomProperty("schedule", "0 2 * * *")
    .addCustomProperty("catchup", "false")
    .addCustomProperty("max_active_runs", "1")
    .setExternalUrl("https://airflow.company.com/dags/customer_etl_daily");
```

### Apache Spark

```java
DataFlow sparkFlow = DataFlow.builder()
    .orchestrator("spark")
    .flowId("ml_feature_generation")
    .cluster("emr-prod-cluster")
    .displayName("ML Feature Generation Job")
    .description("Large-scale Spark job generating ML features")
    .build();

sparkFlow
    .addTag("spark")
    .addTag("machine-learning")
    .addCustomProperty("spark.executor.memory", "8g")
    .addCustomProperty("spark.driver.memory", "4g")
    .addCustomProperty("spark.executor.cores", "4")
    .setDomain("urn:li:domain:MachineLearning");
```

### dbt

```java
DataFlow dbtFlow = DataFlow.builder()
    .orchestrator("dbt")
    .flowId("marketing_analytics")
    .cluster("prod")
    .displayName("Marketing Analytics Models")
    .description("dbt transformations for marketing data")
    .build();

dbtFlow
    .addTag("dbt")
    .addTag("transformation")
    .addCustomProperty("dbt_version", "1.5.0")
    .addCustomProperty("target", "production")
    .addCustomProperty("models_count", "87")
    .setProject("marketing")
    .setExternalUrl("https://github.com/company/dbt-marketing");
```

### Apache Flink (스트리밍)

```java
DataFlow flinkFlow = DataFlow.builder()
    .orchestrator("flink")
    .flowId("real_time_fraud_detection")
    .cluster("prod-flink-cluster")
    .displayName("Real-time Fraud Detection")
    .description("Real-time streaming pipeline for fraud detection")
    .build();

flinkFlow
    .addTag("streaming")
    .addTag("real-time")
    .addTag("fraud-detection")
    .addCustomProperty("parallelism", "16")
    .addCustomProperty("checkpoint_interval", "60000")
    .setDomain("urn:li:domain:Security");
```

## 플루언트 API

모든 변경 메서드는 메서드 체이닝을 지원하기 위해 `this`를 반환합니다:

```java
DataFlow dataflow = DataFlow.builder()
    .orchestrator("airflow")
    .flowId("sales_pipeline")
    .cluster("prod")
    .build();

dataflow
    .addTag("etl")
    .addTag("production")
    .addOwner("urn:li:corpuser:owner1", OwnershipType.TECHNICAL_OWNER)
    .addOwner("urn:li:corpuser:owner2", OwnershipType.BUSINESS_OWNER)
    .addTerm("urn:li:glossaryTerm:Sales")
    .setDomain("urn:li:domain:Sales")
    .setDescription("Sales data pipeline")
    .addCustomProperty("schedule", "0 2 * * *")
    .addCustomProperty("team", "sales-analytics");

client.entities().upsert(dataflow);
```

## DataJob과의 관계

DataFlow는 DataJob의 부모 entity입니다. DataJob은 DataFlow 내의 특정 태스크 또는 단계를 나타냅니다:

```java
// 부모 DataFlow 생성
DataFlow dataflow = DataFlow.builder()
    .orchestrator("airflow")
    .flowId("customer_etl")
    .cluster("prod")
    .build();

client.entities().upsert(dataflow);

// 부모 flow를 참조하는 자식 DataJob 생성
DataJob extractJob = DataJob.builder()
    .flow(dataflow.getUrn())  // 부모 DataFlow 참조
    .jobId("extract_customers")
    .build();

DataJob transformJob = DataJob.builder()
    .flow(dataflow.getUrn())
    .jobId("transform_customers")
    .build();

client.entities().upsert(extractJob);
client.entities().upsert(transformJob);
```

이 계층 구조를 통해 다음이 가능합니다:

- 전체 파이프라인 모델링 (DataFlow)
- 파이프라인 내의 개별 태스크 모델링 (DataJob)
- 태스크 수준 lineage 및 의존성 추적
- 두 수준 모두에서 거버넌스 메타데이터 구성

## 모범 사례

1. **일관된 명명 사용**: 조직 전체에서 오케스트레이터 이름을 일관되게 유지하세요 (예: 항상 "airflow" 사용, "Airflow" 또는 "AIRFLOW" 혼용 금지)

2. **적절한 클러스터 선택**: 환경과 지역을 나타내는 의미 있는 클러스터 이름 사용 (예: "prod-us-west-2", "staging-eu-central-1")

3. **스케줄 정보 추가**: 배치 워크플로의 경우 사용자 정의 속성에 스케줄 표현식 포함

4. **소스 시스템 연결**: 오케스트레이션 도구의 UI로 다시 연결되도록 항상 `externalUrl` 설정

5. **소유권 초기 설정**: flow 생성 시 기술 소유자와 비즈니스 소유자 지정

6. **분류를 위한 태그 활용**: 타입(etl, streaming, ml), 환경(production, staging), 중요도별로 flow에 태그 지정

7. **SLA 문서화**: 사용자 정의 속성을 사용하여 SLA 요구사항 및 알림 채널 문서화

8. **버전 추적**: 버전이 있는 워크플로(예: dbt)의 경우 사용자 정의 속성에 버전 정보 포함

## 전체 예시

```java
// 클라이언트 초기화
DataHubClientConfigV2 config = DataHubClientConfigV2.builder()
    .server("http://localhost:8080")
    .token(System.getenv("DATAHUB_TOKEN"))
    .build();

try (DataHubClientV2 client = new DataHubClientV2(config)) {

    // 포괄적인 DataFlow 생성
    Map<String, String> customProps = new HashMap<>();
    customProps.put("schedule", "0 2 * * *");
    customProps.put("catchup", "false");
    customProps.put("team", "data-engineering");
    customProps.put("sla_hours", "4");
    customProps.put("alert_channel", "#data-alerts");

    DataFlow dataflow = DataFlow.builder()
        .orchestrator("airflow")
        .flowId("production_etl_pipeline")
        .cluster("prod-us-east-1")
        .displayName("Production ETL Pipeline")
        .description("Main ETL pipeline for customer data processing")
        .customProperties(customProps)
        .build();

    dataflow
        .addTag("etl")
        .addTag("production")
        .addTag("pii")
        .addOwner("urn:li:corpuser:data_eng_team", OwnershipType.TECHNICAL_OWNER)
        .addOwner("urn:li:corpuser:product_owner", OwnershipType.BUSINESS_OWNER)
        .addTerm("urn:li:glossaryTerm:ETL")
        .addTerm("urn:li:glossaryTerm:CustomerData")
        .setDomain("urn:li:domain:DataEngineering")
        .setProject("customer_analytics")
        .setExternalUrl("https://airflow.company.com/dags/production_etl_pipeline")
        .setCreated(System.currentTimeMillis() - 86400000L * 30)
        .setLastModified(System.currentTimeMillis());

    // DataHub에 upsert
    client.entities().upsert(dataflow);

    System.out.println("Created DataFlow: " + dataflow.getUrn());
}
```

## 참고 항목

- [DataJob Entity](datajob-entity.md) - DataFlow 내의 자식 태스크
- [Dataset Entity](dataset-entity.md) - DataFlow의 데이터 소스 및 대상
