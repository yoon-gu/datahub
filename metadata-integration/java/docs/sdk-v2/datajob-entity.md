# DataJob Entity

DataJob entity는 데이터 처리 파이프라인 내의 작업 단위를 나타냅니다 (예: Airflow 태스크, dbt 모델, Spark job). DataJob은 DataFlow(파이프라인)에 속하며 dataset 및 다른 DataJob과 lineage를 가질 수 있습니다. 이 가이드는 SDK V2에서의 포괄적인 DataJob 작업을 다룹니다.

## DataJob 생성

### 최소 DataJob

orchestrator, flowId, jobId가 필수입니다:

```java
DataJob dataJob = DataJob.builder()
    .orchestrator("airflow")
    .flowId("my_dag")
    .jobId("my_task")
    .build();
```

### 클러스터 지정

클러스터 지정 (기본값은 "prod"):

```java
DataJob dataJob = DataJob.builder()
    .orchestrator("airflow")
    .flowId("analytics_pipeline")
    .cluster("staging")
    .jobId("transform_data")
    .build();
// URN: urn:li:dataJob:(urn:li:dataFlow:(airflow,analytics_pipeline,staging),transform_data)
```

### 메타데이터와 함께 생성

생성 시 설명과 이름 추가 (name과 type 모두 필요):

```java
DataJob dataJob = DataJob.builder()
    .orchestrator("dagster")
    .flowId("customer_etl")
    .cluster("prod")
    .jobId("load_customers")
    .description("Loads customer data from PostgreSQL to Snowflake")
    .name("Load Customers to DWH")
    .type("BATCH")
    .build();
```

### 사용자 정의 속성과 함께 생성

빌더에 사용자 정의 속성 포함 (customProperties 사용 시 name과 type 필요):

```java
Map<String, String> props = new HashMap<>();
props.put("schedule", "0 2 * * *");
props.put("retries", "3");
props.put("timeout", "3600");

DataJob dataJob = DataJob.builder()
    .orchestrator("airflow")
    .flowId("daily_pipeline")
    .jobId("my_task")
    .name("My Daily Task")
    .type("BATCH")
    .customProperties(props)
    .build();
```

## URN 구성

DataJob URN은 다음 패턴을 따릅니다:

```
urn:li:dataJob:(urn:li:dataFlow:({orchestrator},{flowId},{cluster}),{jobId})
```

**자동 URN 생성:**

```java
DataJob dataJob = DataJob.builder()
    .orchestrator("airflow")
    .flowId("finance_reporting")
    .cluster("prod")
    .jobId("aggregate_transactions")
    .build();

DataJobUrn urn = dataJob.getDataJobUrn();
// urn:li:dataJob:(urn:li:dataFlow:(airflow,finance_reporting,prod),aggregate_transactions)
```

## 설명 작업

### 설명 설정

```java
dataJob.setDescription("Processes daily customer transactions");
```

### 설명 읽기

DataJobInfo에서 지연 로딩으로 설명 가져오기:

```java
String description = dataJob.getDescription();
```

## 표시 이름 작업

### 이름 설정

```java
dataJob.setName("Process Customer Transactions");
```

### 이름 읽기

```java
String name = dataJob.getName();
```

## 태그

### 태그 추가

```java
// 간단한 태그 이름 (자동 접두사 추가)
dataJob.addTag("critical");
// 생성됨: urn:li:tag:critical

// 전체 태그 URN
dataJob.addTag("urn:li:tag:etl");
```

### 태그 제거

```java
dataJob.removeTag("critical");
dataJob.removeTag("urn:li:tag:etl");
```

### 태그 체이닝

```java
dataJob.addTag("critical")
       .addTag("pii")
       .addTag("production");
```

## 소유자

### 소유자 추가

```java
import com.linkedin.common.OwnershipType;

// 기술 소유자
dataJob.addOwner(
    "urn:li:corpuser:data_team",
    OwnershipType.TECHNICAL_OWNER
);

// 데이터 스튜어드
dataJob.addOwner(
    "urn:li:corpuser:compliance",
    OwnershipType.DATA_STEWARD
);

// 비즈니스 소유자
dataJob.addOwner(
    "urn:li:corpuser:product_team",
    OwnershipType.BUSINESS_OWNER
);
```

### 소유자 제거

```java
dataJob.removeOwner("urn:li:corpuser:data_team");
```

### 소유권 타입

사용 가능한 소유권 타입:

- `TECHNICAL_OWNER` - 기술적 구현을 유지 관리하는 사람
- `BUSINESS_OWNER` - 비즈니스 이해관계자
- `DATA_STEWARD` - 데이터 품질 및 컴플라이언스 관리자
- `DATAOWNER` - 일반 데이터 소유자
- `DEVELOPER` - 소프트웨어 개발자
- `PRODUCER` - 데이터 생산자
- `CONSUMER` - 데이터 소비자
- `STAKEHOLDER` - 기타 이해관계자

## 용어 (Glossary Terms)

### 용어 추가

```java
dataJob.addTerm("urn:li:glossaryTerm:DataProcessing");
dataJob.addTerm("urn:li:glossaryTerm:ETL");
```

### 용어 제거

```java
dataJob.removeTerm("urn:li:glossaryTerm:DataProcessing");
```

### 용어 체이닝

```java
dataJob.addTerm("urn:li:glossaryTerm:DataProcessing")
       .addTerm("urn:li:glossaryTerm:ETL")
       .addTerm("urn:li:glossaryTerm:FinancialReporting");
```

## 도메인

### 도메인 설정

```java
dataJob.setDomain("urn:li:domain:Engineering");
```

### 도메인 제거

```java
dataJob.removeDomain();
```

## 사용자 정의 속성

### 개별 속성 추가

```java
dataJob.addCustomProperty("schedule", "0 2 * * *");
dataJob.addCustomProperty("retries", "3");
dataJob.addCustomProperty("timeout", "3600");
```

### 모든 속성 설정

모든 사용자 정의 속성 대체:

```java
Map<String, String> properties = new HashMap<>();
properties.put("schedule", "0 2 * * *");
properties.put("retries", "3");
properties.put("timeout", "3600");
properties.put("priority", "high");

dataJob.setCustomProperties(properties);
```

### 속성 제거

```java
dataJob.removeCustomProperty("timeout");
```

## Lineage 작업

DataJob lineage는 데이터 job과 그것이 작동하는 dataset 간의 관계를 정의합니다. Lineage는 영향 분석, 데이터 출처 추적, 파이프라인을 통한 데이터 흐름 이해를 가능하게 합니다.

DataJob SDK는 네 가지 유형의 lineage를 지원합니다:

1. **dataset 수준 lineage** - job이 읽고 쓰는 dataset 추적
2. **DataJob 의존성** - 다른 job에 의존하는 job 추적 (태스크 의존성)
3. **필드 수준 lineage** - 소비 및 생성되는 특정 컬럼 추적
4. **세밀한 lineage** - 컬럼 간 변환 추적

### 입력 및 출력 Dataset 이해

**입력 Dataset** - job이 읽는 dataset:

- job의 소스 데이터를 나타냅니다
- upstream lineage 생성: Dataset → DataJob

**출력 Dataset** - job이 쓰는 dataset:

- job의 결과 데이터를 나타냅니다
- downstream lineage 생성: DataJob → Dataset

### 입력 Dataset

#### 단일 입력 추가

```java
// 문자열 URN 사용
dataJob.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.transactions,PROD)");

// 타입 안전성을 위해 DatasetUrn 객체 사용
DatasetUrn datasetUrn = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.transactions,PROD)"
);
dataJob.addInputDataset(datasetUrn);
```

#### 여러 입력 추가

```java
// 여러 호출 체이닝
dataJob.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.transactions,PROD)")
       .addInputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.customers,PROD)")
       .addInputDataset("urn:li:dataset:(urn:li:dataPlatform:kafka,events.purchases,PROD)");
```

#### 모든 입력 한 번에 설정

```java
List<String> inletUrns = Arrays.asList(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders,PROD)",
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.customers,PROD)",
    "urn:li:dataset:(urn:li:dataPlatform:kafka,events.clicks,PROD)"
);
dataJob.setInputDatasets(inletUrns);
```

#### 입력 제거

```java
// 단일 입력 제거
dataJob.removeInputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.transactions,PROD)");

// 또는 DatasetUrn 사용
DatasetUrn datasetUrn = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.transactions,PROD)"
);
dataJob.removeInputDataset(datasetUrn);
```

#### 입력 읽기

```java
// 모든 입력 가져오기 (지연 로딩)
List<DatasetUrn> inlets = dataJob.getInputDatasets();
for (DatasetUrn inlet : inlets) {
    System.out.println("Input: " + inlet);
}
```

### 출력 Dataset

#### 단일 출력 추가

```java
// 문자열 URN 사용
dataJob.addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.sales_summary,PROD)");

// DatasetUrn 객체 사용
DatasetUrn datasetUrn = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.sales_summary,PROD)"
);
dataJob.addOutputDataset(datasetUrn);
```

#### 여러 출력 추가

```java
dataJob.addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.daily_summary,PROD)")
       .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.monthly_summary,PROD)")
       .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:s3,reports/summary.parquet,PROD)");
```

#### 모든 출력 한 번에 설정

```java
List<String> outletUrns = Arrays.asList(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.customer_metrics,PROD)",
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.product_metrics,PROD)"
);
dataJob.setOutputDatasets(outletUrns);
```

#### 출력 제거

```java
// 단일 출력 제거
dataJob.removeOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.sales_summary,PROD)");

// 또는 DatasetUrn 사용
DatasetUrn datasetUrn = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.sales_summary,PROD)"
);
dataJob.removeOutputDataset(datasetUrn);
```

#### 출력 읽기

```java
// 모든 출력 가져오기 (지연 로딩)
List<DatasetUrn> outlets = dataJob.getOutputDatasets();
for (DatasetUrn outlet : outlets) {
    System.out.println("Output: " + outlet);
}
```

### DataJob 의존성

DataJob 의존성은 워크플로 내의 태스크 간 관계를 모델링합니다. 이를 통해 DataHub는 어떤 job이 다른 job의 완료를 기다려야 하는지 추적할 수 있습니다.

**사용 사례:**

- Airflow 태스크 의존성 (태스크 A → 태스크 B → 태스크 C)
- 크로스 DAG 의존성 (서로 다른 파이프라인의 job)
- 워크플로 오케스트레이션 시각화

#### job 의존성 추가

```java
// 문자열 URN 사용
dataJob.addInputDataJob("urn:li:dataJob:(urn:li:dataFlow:(airflow,pipeline,prod),upstream_task)");

// 타입 안전성을 위해 DataJobUrn 객체 사용
DataJobUrn upstreamJob = DataJobUrn.createFromString(
    "urn:li:dataJob:(urn:li:dataFlow:(airflow,pipeline,prod),upstream_task)"
);
dataJob.addInputDataJob(upstreamJob);
```

#### job 의존성 체이닝

```java
// 여러 의존성 (모두 완료 후 태스크 실행)
dataJob.addInputDataJob("urn:li:dataJob:(urn:li:dataFlow:(airflow,pipeline,prod),task_1)")
       .addInputDataJob("urn:li:dataJob:(urn:li:dataFlow:(airflow,pipeline,prod),task_2)")
       .addInputDataJob("urn:li:dataJob:(urn:li:dataFlow:(dagster,other_pipeline,prod),external_task)");
```

#### job 의존성 제거

```java
// 단일 의존성 제거
dataJob.removeInputDataJob("urn:li:dataJob:(urn:li:dataFlow:(airflow,pipeline,prod),task_1)");

// 또는 DataJobUrn 사용
DataJobUrn jobUrn = DataJobUrn.createFromString(
    "urn:li:dataJob:(urn:li:dataFlow:(airflow,pipeline,prod),task_1)"
);
dataJob.removeInputDataJob(jobUrn);
```

#### job 의존성 읽기

```java
// 모든 upstream job 의존성 가져오기 (지연 로딩)
List<DataJobUrn> dependencies = dataJob.getInputDataJobs();
for (DataJobUrn dependency : dependencies) {
    System.out.println("Depends on: " + dependency);
}
```

#### 예시: Airflow 태스크 의존성

```java
// 일반적인 Airflow DAG 태스크 체인 모델링
DataJob extractTask = DataJob.builder()
    .orchestrator("airflow")
    .flowId("etl_pipeline")
    .jobId("extract_data")
    .build();

DataJob validateTask = DataJob.builder()
    .orchestrator("airflow")
    .flowId("etl_pipeline")
    .jobId("validate_data")
    .build();

// validate_data는 extract_data에 의존
validateTask.addInputDataJob(extractTask.getUrn().toString());

DataJob transformTask = DataJob.builder()
    .orchestrator("airflow")
    .flowId("etl_pipeline")
    .jobId("transform_data")
    .build();

// transform_data는 validate_data에 의존
transformTask.addInputDataJob(validateTask.getUrn().toString());

// 모든 태스크 저장
client.entities().upsert(extractTask);
client.entities().upsert(validateTask);
client.entities().upsert(transformTask);

// 결과: extract_data → validate_data → transform_data
```

### 필드 수준 Lineage

필드 수준 lineage는 job이 소비하고 생성하는 특정 컬럼(필드)을 추적합니다. dataset 수준 lineage보다 더 세밀한 정보를 제공합니다.

**사용 사례:**

- 변환에서 읽고 쓰는 컬럼 추적
- 필드 수준 의존성 이해
- job이 필요한 컬럼에만 접근하는지 검증

**필드 URN 형식:**

```
urn:li:schemaField:(DATASET_URN,COLUMN_NAME)
```

#### 입력 필드 추가

```java
// job이 읽는 컬럼 추적
dataJob.addInputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,db.orders,PROD),order_id)");
dataJob.addInputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,db.orders,PROD),customer_id)");
dataJob.addInputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,db.orders,PROD),total_amount)");
```

#### 출력 필드 추가

```java
// job이 쓰는 컬럼 추적
dataJob.addOutputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.sales,PROD),order_id)");
dataJob.addOutputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.sales,PROD),customer_id)");
dataJob.addOutputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.sales,PROD),revenue)");
```

#### 필드 제거

```java
// 필드 lineage 제거
dataJob.removeInputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,db.orders,PROD),order_id)");
dataJob.removeOutputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.sales,PROD),revenue)");
```

#### 필드 읽기

```java
// 모든 입력 필드 가져오기 (지연 로딩)
List<Urn> inputFields = dataJob.getInputFields();
for (Urn field : inputFields) {
    System.out.println("Reads field: " + field);
}

// 모든 출력 필드 가져오기 (지연 로딩)
List<Urn> outputFields = dataJob.getOutputFields();
for (Urn field : outputFields) {
    System.out.println("Writes field: " + field);
}
```

#### 예시: 컬럼 수준 추적

```java
DataJob aggregateJob = DataJob.builder()
    .orchestrator("airflow")
    .flowId("analytics")
    .jobId("aggregate_sales")
    .description("Aggregates sales data by customer")
    .name("Aggregate Sales by Customer")
    .type("BATCH")
    .build();

// dataset 수준 lineage
aggregateJob.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.transactions,PROD)");
aggregateJob.addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.customer_sales,PROD)");

// 필드 수준 lineage - 사용하는 정확한 컬럼 지정
aggregateJob.addInputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.transactions,PROD),customer_id)");
aggregateJob.addInputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.transactions,PROD),amount)");
aggregateJob.addInputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.transactions,PROD),transaction_date)");

aggregateJob.addOutputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.customer_sales,PROD),customer_id)");
aggregateJob.addOutputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.customer_sales,PROD),total_sales)");
aggregateJob.addOutputField("urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.customer_sales,PROD),transaction_count)");

client.entities().upsert(aggregateJob);
```

### 세밀한 Lineage

세밀한 lineage는 컬럼 간 변환을 캡처하여 어떤 입력 컬럼이 어떤 출력 컬럼을 생성하는지, 그리고 어떻게 변환되는지를 정확히 보여줍니다.

**사용 사례:**

- 변환 로직 문서화 (예: "SUM(amount)")
- 컬럼 수준 영향 분석 추적
- 데이터 파생 이해
- 컴플라이언스 및 감사 추적

#### 세밀한 Lineage 추가

```java
// 기본 변환 (신뢰도 점수 없음)
dataJob.addFineGrainedLineage(
    "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders,PROD),customer_id)",
    "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.sales,PROD),customer_id)",
    "IDENTITY",
    null
);

// 신뢰도 점수가 있는 변환 (0.0~1.0)
dataJob.addFineGrainedLineage(
    "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders,PROD),amount)",
    "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.sales,PROD),revenue)",
    "SUM",
    1.0f  // 높은 신뢰도
);
```

#### 일반적인 변환 타입

```java
// IDENTITY - 직접 복사
dataJob.addFineGrainedLineage(upstream, downstream, "IDENTITY", 1.0f);

// 집계 함수
dataJob.addFineGrainedLineage(upstream, downstream, "SUM", 1.0f);
dataJob.addFineGrainedLineage(upstream, downstream, "COUNT", 1.0f);
dataJob.addFineGrainedLineage(upstream, downstream, "AVG", 1.0f);
dataJob.addFineGrainedLineage(upstream, downstream, "MAX", 1.0f);
dataJob.addFineGrainedLineage(upstream, downstream, "MIN", 1.0f);

// 문자열 연산
dataJob.addFineGrainedLineage(upstream, downstream, "CONCAT", 0.9f);
dataJob.addFineGrainedLineage(upstream, downstream, "UPPER", 1.0f);
dataJob.addFineGrainedLineage(upstream, downstream, "SUBSTRING", 0.95f);

// 날짜 연산
dataJob.addFineGrainedLineage(upstream, downstream, "DATE_TRUNC", 1.0f);
dataJob.addFineGrainedLineage(upstream, downstream, "EXTRACT", 1.0f);

// 사용자 정의 변환
dataJob.addFineGrainedLineage(upstream, downstream, "CUSTOM_FUNCTION", 0.8f);
```

#### 세밀한 Lineage 제거

```java
// 특정 변환 제거
dataJob.removeFineGrainedLineage(
    "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.orders,PROD),amount)",
    "urn:li:schemaField:(urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.sales,PROD),revenue)",
    "SUM",
    null  // queryUrn (선택 사항)
);
```

#### 세밀한 Lineage 읽기

```java
// 모든 세밀한 lineage 가져오기 (지연 로딩)
List<FineGrainedLineage> lineages = dataJob.getFineGrainedLineages();
for (FineGrainedLineage lineage : lineages) {
    System.out.println("Upstreams: " + lineage.getUpstreams());
    System.out.println("Downstreams: " + lineage.getDownstreams());
    System.out.println("Transformation: " + lineage.getTransformOperation());
    System.out.println("Confidence: " + lineage.getConfidenceScore());
}
```

#### 예시: 복잡한 집계

```java
DataJob salesAggregation = DataJob.builder()
    .orchestrator("airflow")
    .flowId("analytics")
    .jobId("daily_sales_summary")
    .name("Daily Sales Summary")
    .type("BATCH")
    .build();

// dataset 수준 lineage
salesAggregation.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:postgres,sales.transactions,PROD)");
salesAggregation.addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.daily_summary,PROD)");

// 세밀한 변환
String inputDataset = "urn:li:dataset:(urn:li:dataPlatform:postgres,sales.transactions,PROD)";
String outputDataset = "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.daily_summary,PROD)";

// 날짜는 직접 복사
salesAggregation.addFineGrainedLineage(
    "urn:li:schemaField:(" + inputDataset + ",transaction_date)",
    "urn:li:schemaField:(" + outputDataset + ",date)",
    "IDENTITY",
    1.0f
);

// 매출은 금액의 합계
salesAggregation.addFineGrainedLineage(
    "urn:li:schemaField:(" + inputDataset + ",amount)",
    "urn:li:schemaField:(" + outputDataset + ",total_revenue)",
    "SUM",
    1.0f
);

// 거래 건수
salesAggregation.addFineGrainedLineage(
    "urn:li:schemaField:(" + inputDataset + ",transaction_id)",
    "urn:li:schemaField:(" + outputDataset + ",transaction_count)",
    "COUNT",
    1.0f
);

// 평균 주문 금액
salesAggregation.addFineGrainedLineage(
    "urn:li:schemaField:(" + inputDataset + ",amount)",
    "urn:li:schemaField:(" + outputDataset + ",avg_order_value)",
    "AVG",
    1.0f
);

client.entities().upsert(salesAggregation);
```

#### 예시: 다중 컬럼 파생

```java
// 여러 입력 컬럼에 의존하는 출력을 모델링
DataJob enrichmentJob = DataJob.builder()
    .orchestrator("airflow")
    .flowId("enrichment")
    .jobId("enrich_customer_data")
    .build();

String inputDataset = "urn:li:dataset:(urn:li:dataPlatform:postgres,crm.customers,PROD)";
String outputDataset = "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.customers_enriched,PROD)";

// full_name = CONCAT(first_name, ' ', last_name)
// first_name과 last_name 모두 full_name에 기여
enrichmentJob.addFineGrainedLineage(
    "urn:li:schemaField:(" + inputDataset + ",first_name)",
    "urn:li:schemaField:(" + outputDataset + ",full_name)",
    "CONCAT",
    1.0f
);

enrichmentJob.addFineGrainedLineage(
    "urn:li:schemaField:(" + inputDataset + ",last_name)",
    "urn:li:schemaField:(" + outputDataset + ",full_name)",
    "CONCAT",
    1.0f
);

// email_domain = SUBSTRING(email, POSITION('@', email) + 1)
enrichmentJob.addFineGrainedLineage(
    "urn:li:schemaField:(" + inputDataset + ",email)",
    "urn:li:schemaField:(" + outputDataset + ",email_domain)",
    "SUBSTRING",
    1.0f
);

client.entities().upsert(enrichmentJob);
```

#### 신뢰도 점수

신뢰도 점수(0.0~1.0)는 변환에 대한 확신 정도를 나타냅니다:

- **1.0** - 정확하고 결정론적인 변환 (예: IDENTITY, SUM)
- **0.9-0.99** - 높은 신뢰도 (예: 단순 문자열 연산)
- **0.7-0.89** - 중간 신뢰도 (예: 일부 불확실성이 있는 복잡한 변환)
- **0.5-0.69** - 낮은 신뢰도 (예: ML 기반 lineage, 휴리스틱 기반)
- **< 0.5** - 매우 불확실함 (일반적으로 권장하지 않음)

```java
// 높은 신뢰도 - 정확한 변환이 알려져 있음
dataJob.addFineGrainedLineage(source, target, "UPPER", 1.0f);

// 중간 신뢰도 - SQL 파싱에서 추론됨
dataJob.addFineGrainedLineage(source, target, "CASE_WHEN", 0.85f);

// 낮은 신뢰도 - ML로 예측된 변환
dataJob.addFineGrainedLineage(source, target, "INFERRED", 0.6f);
```

### 완전한 Lineage 예시

이 예시는 네 가지 유형의 lineage가 함께 동작하는 방식을 보여줍니다:

```java
// upstream 검증 job 생성
DataJob validateJob = DataJob.builder()
    .orchestrator("airflow")
    .flowId("analytics_pipeline")
    .cluster("prod")
    .jobId("validate_transactions")
    .name("Validate Transaction Data")
    .type("BATCH")
    .build();

validateJob.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.transactions,PROD)")
           .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,validated.transactions,PROD)");

client.entities().upsert(validateJob);

// 포괄적인 lineage를 가진 주요 변환 job 생성
DataJob transformJob = DataJob.builder()
    .orchestrator("airflow")
    .flowId("analytics_pipeline")
    .cluster("prod")
    .jobId("aggregate_sales")
    .description("Aggregates daily sales data from multiple validated sources")
    .name("Aggregate Daily Sales")
    .type("BATCH")
    .build();

// 1. dataset 수준 lineage - 어떤 테이블을 읽고 쓰는지
transformJob.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,validated.transactions,PROD)")
            .addInputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.customers,PROD)")
            .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.daily_sales,PROD)");

// 2. DataJob 의존성 - 이 job은 검증 job에 의존
transformJob.addInputDataJob(validateJob.getUrn().toString());

// 3. 필드 수준 lineage - 어떤 특정 컬럼에 접근하는지
String transactionsDataset = "urn:li:dataset:(urn:li:dataPlatform:snowflake,validated.transactions,PROD)";
String customersDataset = "urn:li:dataset:(urn:li:dataPlatform:snowflake,raw.customers,PROD)";
String outputDataset = "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.daily_sales,PROD)";

// 입력 필드
transformJob.addInputField("urn:li:schemaField:(" + transactionsDataset + ",transaction_id)")
            .addInputField("urn:li:schemaField:(" + transactionsDataset + ",customer_id)")
            .addInputField("urn:li:schemaField:(" + transactionsDataset + ",amount)")
            .addInputField("urn:li:schemaField:(" + transactionsDataset + ",transaction_date)")
            .addInputField("urn:li:schemaField:(" + customersDataset + ",customer_id)")
            .addInputField("urn:li:schemaField:(" + customersDataset + ",customer_name)");

// 출력 필드
transformJob.addOutputField("urn:li:schemaField:(" + outputDataset + ",date)")
            .addOutputField("urn:li:schemaField:(" + outputDataset + ",customer_name)")
            .addOutputField("urn:li:schemaField:(" + outputDataset + ",total_revenue)")
            .addOutputField("urn:li:schemaField:(" + outputDataset + ",transaction_count)");

// 4. 세밀한 lineage - 특정 컬럼 간 변환
// 날짜 컬럼 (identity 변환)
transformJob.addFineGrainedLineage(
    "urn:li:schemaField:(" + transactionsDataset + ",transaction_date)",
    "urn:li:schemaField:(" + outputDataset + ",date)",
    "IDENTITY",
    1.0f
);

// 고객 이름 (join + identity)
transformJob.addFineGrainedLineage(
    "urn:li:schemaField:(" + customersDataset + ",customer_name)",
    "urn:li:schemaField:(" + outputDataset + ",customer_name)",
    "IDENTITY",
    1.0f
);

// 총 매출 (집계)
transformJob.addFineGrainedLineage(
    "urn:li:schemaField:(" + transactionsDataset + ",amount)",
    "urn:li:schemaField:(" + outputDataset + ",total_revenue)",
    "SUM",
    1.0f
);

// 거래 건수 (집계)
transformJob.addFineGrainedLineage(
    "urn:li:schemaField:(" + transactionsDataset + ",transaction_id)",
    "urn:li:schemaField:(" + outputDataset + ",transaction_count)",
    "COUNT",
    1.0f
);

// 기타 메타데이터 추가
transformJob.addTag("critical")
            .addOwner("urn:li:corpuser:data_team", OwnershipType.TECHNICAL_OWNER);

// DataHub에 저장
client.entities().upsert(transformJob);

// 결과: 다음을 보여주는 포괄적인 lineage 생성:
// - job 의존성: validate_transactions → aggregate_sales
// - dataset 흐름: raw.transactions → validated.transactions → analytics.daily_sales
//                 raw.customers → analytics.daily_sales
// - 컬럼 수준: transaction_date → date (IDENTITY)
//                 amount → total_revenue (SUM)
//                 transaction_id → transaction_count (COUNT)
//                 customer_name → customer_name (IDENTITY via JOIN)
```

### Lineage 흐름 시각화

위의 포괄적인 lineage 예시는 다음과 같은 다단계 lineage 그래프를 생성합니다:

```
Job-to-Job 수준:
┌────────────────────────┐         ┌──────────────────────┐
│ Validate Transactions  │────────→│  Aggregate Sales Job │
└────────────────────────┘         └──────────────────────┘

Dataset 수준:
┌─────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│ raw.transactions    │───→│ validated.transactions  │───→│                         │
└─────────────────────┘    └─────────────────────────┘    │  analytics.daily_sales  │
                                                           │                         │
┌─────────────────────┐                                   │                         │
│ raw.customers       │──────────────────────────────────→│                         │
└─────────────────────┘                                   └─────────────────────────┘

컬럼 수준 (세밀한):
validated.transactions.transaction_date ──[IDENTITY]──→ daily_sales.date
validated.transactions.amount           ──[SUM]──────→ daily_sales.total_revenue
validated.transactions.transaction_id   ──[COUNT]────→ daily_sales.transaction_count
raw.customers.customer_name             ──[IDENTITY]──→ daily_sales.customer_name
```

### ETL 파이프라인 예시

완전한 Extract-Transform-Load 파이프라인 모델링:

```java
// Extract job
DataJob extractJob = DataJob.builder()
    .orchestrator("airflow")
    .flowId("etl_pipeline")
    .jobId("extract")
    .build();

extractJob.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:mysql,prod.orders,PROD)")
          .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:s3,staging/orders_raw,PROD)");

client.entities().upsert(extractJob);

// Transform job
DataJob transformJob = DataJob.builder()
    .orchestrator("airflow")
    .flowId("etl_pipeline")
    .jobId("transform")
    .build();

transformJob.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:s3,staging/orders_raw,PROD)")
            .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:s3,staging/orders_clean,PROD)");

client.entities().upsert(transformJob);

// Load job
DataJob loadJob = DataJob.builder()
    .orchestrator("airflow")
    .flowId("etl_pipeline")
    .jobId("load")
    .build();

loadJob.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:s3,staging/orders_clean,PROD)")
       .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.orders,PROD)");

client.entities().upsert(loadJob);

// 엔드투엔드 lineage 생성:
// mysql.orders → [Extract] → s3.raw → [Transform] → s3.clean → [Load] → snowflake.analytics
```

### Lineage 업데이트

```java
// 기존 job 로드
DataJobUrn urn = DataJobUrn.createFromString(
    "urn:li:dataJob:(urn:li:dataFlow:(airflow,my_pipeline,prod),my_task)"
);
DataJob dataJob = client.entities().get(urn);

// 새 입력 추가 (예: 요구사항 변경)
dataJob.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:kafka,events.new_source,PROD)");

// 이전 출력 제거 (예: 더 이상 사용하지 않는 테이블)
dataJob.removeOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,old.deprecated_table,PROD)");

// 변경 사항 적용
client.entities().update(dataJob);
```

### Lineage 모범 사례

1. **완전하게 정의** - 정확한 lineage를 위해 입력과 출력 모두 정의
2. **올바른 URN 사용** - dataset URN이 DataHub의 기존 dataset과 일치하는지 확인
3. **변경 시 업데이트** - 파이프라인 변경에 따라 lineage를 최신 상태로 유지
4. **변환 문서화** - 설명을 사용하여 job이 수행하는 작업 설명
5. **모든 job 모델링** - 완전한 lineage를 위해 파이프라인의 모든 단계 포함
6. **타입 있는 URN 사용** - 컴파일 타임 안전성을 위해 문자열 대신 DatasetUrn/DataJobUrn 객체 선호
7. **lineage 계층화** - dataset 수준부터 시작하여 필요에 따라 필드 수준과 세밀한 lineage 추가
8. **의존성 추적** - DataJob 의존성을 사용하여 태스크 오케스트레이션 모델링
9. **변환 정밀도** - 세밀한 lineage에서 정확한 변환 타입 사용
10. **신뢰도 점수 설정** - lineage 품질을 나타내는 적절한 신뢰도 점수 사용

### 일반적인 패턴

#### 여러 소스에서 단일 대상으로

```java
// 데이터 집계 job
dataJob.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:postgres,sales.orders,PROD)")
       .addInputDataset("urn:li:dataset:(urn:li:dataPlatform:postgres,sales.customers,PROD)")
       .addInputDataset("urn:li:dataset:(urn:li:dataPlatform:postgres,sales.products,PROD)")
       .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.sales_summary,PROD)");
```

#### 단일 소스에서 여러 대상으로

```java
// 데이터 팬아웃 job
dataJob.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:kafka,events.raw,PROD)")
       .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:s3,archive/events,PROD)")
       .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,events.processed,PROD)")
       .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:elasticsearch,events.searchable,PROD)");
```

#### 크로스 플랫폼 Lineage

```java
// 서로 다른 플랫폼에 걸친 ETL
dataJob.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:mysql,production.transactions,PROD)")
       .addInputDataset("urn:li:dataset:(urn:li:dataPlatform:kafka,events.user_activity,PROD)")
       .addInputDataset("urn:li:dataset:(urn:li:dataPlatform:s3,raw/reference_data,PROD)")
       .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.customer_360,PROD)")
       .addOutputDataset("urn:li:dataset:(urn:li:dataPlatform:bigquery,reporting.customer_metrics,PROD)");
```

## 전체 예시

```java
import datahub.client.v2.DataHubClientV2;
import datahub.client.v2.entity.DataJob;
import com.linkedin.common.OwnershipType;
import java.io.IOException;
import java.util.concurrent.ExecutionException;

public class DataJobExample {
    public static void main(String[] args) {
        // 클라이언트 생성
        DataHubClientV2 client = DataHubClientV2.builder()
            .server("http://localhost:8080")
            .build();

        try {
            // 모든 메타데이터를 포함한 data job 빌드
            DataJob dataJob = DataJob.builder()
                .orchestrator("airflow")
                .flowId("customer_analytics")
                .cluster("prod")
                .jobId("process_events")
                .description("Processes customer events from Kafka to warehouse")
                .name("Process Customer Events")
                .type("BATCH")
                .build();

            // 태그 추가
            dataJob.addTag("critical")
                   .addTag("etl")
                   .addTag("pii");

            // 소유자 추가
            dataJob.addOwner("urn:li:corpuser:data_team", OwnershipType.TECHNICAL_OWNER)
                   .addOwner("urn:li:corpuser:product_team", OwnershipType.BUSINESS_OWNER);

            // 용어 추가
            dataJob.addTerm("urn:li:glossaryTerm:DataProcessing")
                   .addTerm("urn:li:glossaryTerm:CustomerData");

            // 도메인 설정
            dataJob.setDomain("urn:li:domain:Analytics");

            // 사용자 정의 속성 추가
            dataJob.addCustomProperty("schedule", "0 2 * * *")
                   .addCustomProperty("retries", "3")
                   .addCustomProperty("timeout", "7200");

            // DataHub에 upsert
            client.entities().upsert(dataJob);

            System.out.println("Successfully created data job: " + dataJob.getUrn());

        } catch (IOException | ExecutionException | InterruptedException e) {
            e.printStackTrace();
        } finally {
            try {
                client.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
```

## 기존 DataJob 업데이트

### 로드 및 수정

```java
// 기존 data job 로드
DataJobUrn urn = DataJobUrn.createFromString(
    "urn:li:dataJob:(urn:li:dataFlow:(airflow,my_dag,prod),my_task)"
);
DataJob dataJob = client.entities().get(urn);

// 새 메타데이터 추가 (패치 생성)
dataJob.addTag("new-tag")
       .addOwner("urn:li:corpuser:new_owner", OwnershipType.TECHNICAL_OWNER);

// 패치 적용
client.entities().update(dataJob);
```

### 점진적 업데이트

```java
// 필요한 것만 추가
dataJob.addTag("critical");
client.entities().update(dataJob);

// 나중에 더 추가
dataJob.addCustomProperty("priority", "high");
client.entities().update(dataJob);
```

## 빌더 옵션 참조

| 메서드                  | 필수 여부 | 설명                                                                                                                  |
| ----------------------- | --------- | --------------------------------------------------------------------------------------------------------------------- |
| `orchestrator(String)`  | ✅ 필수   | 오케스트레이터 (예: "airflow", "dagster")                                                                             |
| `flowId(String)`        | ✅ 필수   | Flow/DAG 식별자                                                                                                       |
| `jobId(String)`         | ✅ 필수   | Job/태스크 식별자                                                                                                     |
| `cluster(String)`       | 선택      | 클러스터 이름 (예: "prod", "dev"). 기본값: "prod"                                                                    |
| `description(String)`   | 선택      | Job 설명. **`name()`과 `type()` 모두 설정 필요**                                                                      |
| `name(String)`          | 선택      | UI에 표시되는 이름. **`description()`, `type()`, 또는 `customProperties()` 사용 시 필수**                             |
| `type(String)`          | 선택      | Job 타입 (예: "BATCH", "STREAMING"). **`description()`, `name()`, 또는 `customProperties()` 사용 시 필수**            |
| `customProperties(Map)` | 선택      | 사용자 정의 키-값 속성 맵. **`name()`과 `type()` 모두 설정 필요**                                                    |

**중요:** DataJobInfo aspect는 `name`과 `type` 필드를 모두 필요로 합니다. 빌더에서 `description`, `name`, `type`, `customProperties` 중 하나라도 제공하면 `name`과 `type` 모두 제공해야 합니다. 그렇지 않으면 빌드 시 `IllegalArgumentException`이 발생합니다.

## 일반적인 패턴

### 여러 DataJob 생성

```java
String[] tasks = {"extract", "transform", "load"};
for (String taskName : tasks) {
    DataJob dataJob = DataJob.builder()
        .orchestrator("airflow")
        .flowId("etl_pipeline")
        .cluster("prod")
        .jobId(taskName)
        .build();

    dataJob.addTag("etl")
           .addCustomProperty("team", "data-engineering");

    client.entities().upsert(dataJob);
}
```

### 배치 메타데이터 추가

```java
DataJob dataJob = DataJob.builder()
    .orchestrator("airflow")
    .flowId("my_dag")
    .jobId("my_task")
    .build();

List<String> tags = Arrays.asList("critical", "production", "etl");
tags.forEach(dataJob::addTag);

client.entities().upsert(dataJob);  // 모든 태그를 한 번에 emit
```

### 조건부 메타데이터

```java
if (isCritical(dataJob)) {
    dataJob.addTag("critical")
           .addTerm("urn:li:glossaryTerm:BusinessCritical");
}

if (processesFinancialData(dataJob)) {
    dataJob.addTag("financial")
           .addOwner("urn:li:corpuser:compliance_team", OwnershipType.DATA_STEWARD);
}
```

## DataJob vs DataFlow

**DataFlow**는 파이프라인 또는 DAG를 나타냅니다 (예: Airflow DAG):

- URN: `urn:li:dataFlow:(orchestrator,flowId,cluster)`
- 여러 DataJob을 포함합니다

**DataJob**은 파이프라인 내의 태스크를 나타냅니다:

- URN: `urn:li:dataJob:(flowUrn,jobId)`
- 하나의 DataFlow에 속합니다
- dataset 및 다른 DataJob과 lineage를 가질 수 있습니다

예시 계층 구조:

```
DataFlow: urn:li:dataFlow:(airflow,customer_pipeline,prod)
├── DataJob: urn:li:dataJob:(urn:li:dataFlow:(airflow,customer_pipeline,prod),extract)
├── DataJob: urn:li:dataJob:(urn:li:dataFlow:(airflow,customer_pipeline,prod),transform)
└── DataJob: urn:li:dataJob:(urn:li:dataFlow:(airflow,customer_pipeline,prod),load)
```
