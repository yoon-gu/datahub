# MLModelGroup Entity

## 개요

`MLModelGroup` entity는 DataHub에서 버전화된 ML 모델들의 모음을 나타냅니다. ML Model Group은 동일한 모델 패밀리에 속하는 관련 모델들을 정리하고 추적하는 방법을 제공하며, 버전 관리, A/B 테스트 시나리오, 모델 학습 및 배포 pipeline 전반에 걸친 종합적인 lineage 추적을 지원합니다.

## URN 구조

MLModelGroup URN은 다음 패턴을 따릅니다:

```
urn:li:mlModelGroup:(urn:li:dataPlatform:{platform},{group_name},{environment})
```

**구성 요소:**

- `platform`: ML 플랫폼 (예: mlflow, sagemaker, vertexai, tensorflow)
- `group_name`: model group의 고유 식별자
- `environment`: 환경 유형 (PROD, DEV, STAGING, TEST 등)

**예시:**

```
urn:li:mlModelGroup:(urn:li:dataPlatform:mlflow,recommendation_models,PROD)
urn:li:mlModelGroup:(urn:li:dataPlatform:sagemaker,fraud_detection_family,PROD)
urn:li:mlModelGroup:(urn:li:dataPlatform:vertexai,churn_prediction_models,STAGING)
```

## ML Model Group 개념

### 모델 패밀리

model group은 관련 모델들의 패밀리를 나타내며, 일반적으로 동일한 모델의 다양한 버전을 포함합니다:

- **버전 발전**: 시간에 따라 모델이 어떻게 발전하는지 추적 (v1.0, v1.1, v2.0)
- **A/B 테스트**: champion과 challenger 모델을 그룹화하여 비교
- **다중 환경**: DEV, STAGING, PROD 환경 전반에 걸친 동일한 모델 패밀리
- **프레임워크 변형**: 동일한 비즈니스 로직의 다양한 구현

### MLModel과의 관계

- **일대다**: 하나의 model group에 많은 모델 포함
- **버전 관리**: 개별 모델은 그룹 내의 특정 버전을 나타냄
- **공유 메타데이터**: 목적, 비즈니스 컨텍스트, 팀 소유권 등 공통 속성
- **Lineage 집계**: 학습 및 downstream job을 그룹 수준에서 추적 가능

### Training Jobs

이 그룹의 모델을 학습시키는 데이터 처리 job 또는 pipeline. Training job은 학습 데이터에서 model group까지의 lineage를 생성하여 모델의 모든 버전을 구축하는 데 사용된 데이터 소스를 보여줍니다.

### Downstream Jobs

추론, 스코어링 또는 예측을 위해 이 그룹의 모델을 사용하거나 소비하는 job. Downstream job은 model group에서 애플리케이션까지의 lineage를 생성하여 이 모델들이 어디에서 사용되는지 보여줍니다.

## ML Model Group 생성

### 기본 예시

```java
MLModelGroup modelGroup = MLModelGroup.builder()
    .platform("mlflow")
    .groupId("recommendation_models")
    .env("PROD")
    .name("Product Recommendation Model Family")
    .description("Collection of product recommendation models trained on user behavior data")
    .build();

// Add standard metadata
modelGroup.addTag("recommendation")
          .addTag("production")
          .addOwner("urn:li:corpuser:ml_team", OwnershipType.TECHNICAL_OWNER)
          .setDomain("urn:li:domain:MachineLearning");

// Add training job references
modelGroup.addTrainingJob("urn:li:dataProcessInstance:training_pipeline_2025_01");

// Save to DataHub
client.entities().upsert(modelGroup);
```

### Builder 옵션

```java
MLModelGroup modelGroup = MLModelGroup.builder()
    .platform("sagemaker")                  // Required: ML platform
    .groupId("churn_prediction_models")     // Required: Model group identifier
    .env("PROD")                            // Optional: Default is PROD
    .name("Customer Churn Prediction Models") // Optional: Human-readable name
    .description("Models predicting customer churn") // Optional
    .externalUrl("https://mlflow.company.com/groups/123") // Optional
    .build();
```

## ML Model Group 작업

### 표시 이름과 설명

```java
// Name is typically set in builder and read-only after creation
String name = modelGroup.getName();

// Description can be updated using patch operations
modelGroup.setDescription("Updated description for customer churn model family");

// Get properties
String description = modelGroup.getDescription();
```

### External URL

```java
// External URL is typically set in builder
MLModelGroup modelGroup = MLModelGroup.builder()
    .platform("mlflow")
    .groupId("fraud_models")
    .externalUrl("https://mlflow.company.com/experiments/fraud-detection")
    .build();

// Get external URL
String url = modelGroup.getExternalUrl();
```

### Custom Properties

```java
// Custom properties are set in builder
Map<String, String> customProps = new HashMap<>();
customProps.put("model_family", "transformer");
customProps.put("framework", "pytorch");
customProps.put("use_case", "fraud_detection");
customProps.put("model_type", "classification");

MLModelGroup modelGroup = MLModelGroup.builder()
    .platform("vertexai")
    .groupId("fraud_models")
    .customProperties(customProps)
    .build();

// Get custom properties
Map<String, String> props = modelGroup.getCustomProperties();
```

### 타임스탬프

```java
import com.linkedin.common.TimeStamp;

// Set creation and modification timestamps
TimeStamp created = new TimeStamp().setTime(System.currentTimeMillis());
TimeStamp lastModified = new TimeStamp().setTime(System.currentTimeMillis());

MLModelGroup modelGroup = MLModelGroup.builder()
    .platform("mlflow")
    .groupId("recommendation_models")
    .created(created)
    .lastModified(lastModified)
    .build();

// Get timestamps
TimeStamp createdTime = modelGroup.getCreated();
TimeStamp modifiedTime = modelGroup.getLastModified();
```

### Training Jobs (Lineage)

```java
// Add training jobs one at a time
modelGroup.addTrainingJob("urn:li:dataProcessInstance:training_pipeline_v1_2025_01")
          .addTrainingJob("urn:li:dataProcessInstance:training_pipeline_v2_2025_03");

// Set all training jobs at once (replaces existing)
List<String> trainingJobs = Arrays.asList(
    "urn:li:dataProcessInstance:training_pipeline_v1_2025_01",
    "urn:li:dataProcessInstance:training_pipeline_v2_2025_03",
    "urn:li:dataProcessInstance:training_pipeline_v3_2025_06"
);
modelGroup.setTrainingJobs(trainingJobs);

// Remove a training job
modelGroup.removeTrainingJob("urn:li:dataProcessInstance:training_pipeline_v1_2025_01");

// Get training jobs
List<String> jobs = modelGroup.getTrainingJobs();
```

### Downstream Jobs (Lineage)

```java
// Add downstream jobs one at a time
modelGroup.addDownstreamJob("urn:li:dataProcessInstance:prediction_service")
          .addDownstreamJob("urn:li:dataProcessInstance:batch_scoring_job");

// Set all downstream jobs at once (replaces existing)
List<String> downstreamJobs = Arrays.asList(
    "urn:li:dataProcessInstance:prediction_service",
    "urn:li:dataProcessInstance:batch_scoring_job",
    "urn:li:dataProcessInstance:real_time_inference_api"
);
modelGroup.setDownstreamJobs(downstreamJobs);

// Remove a downstream job
modelGroup.removeDownstreamJob("urn:li:dataProcessInstance:prediction_service");

// Get downstream jobs
List<String> jobs = modelGroup.getDownstreamJobs();
```

## 표준 메타데이터 작업

### Tags

```java
// Add tags (with or without urn:li:tag: prefix)
modelGroup.addTag("production")
          .addTag("urn:li:tag:ml-model-group")
          .addTag("high-priority");

// Remove tag
modelGroup.removeTag("production");
```

### Owners

```java
// Add owners with different types
modelGroup.addOwner("urn:li:corpuser:ml_platform_team", OwnershipType.TECHNICAL_OWNER)
          .addOwner("urn:li:corpuser:data_science_lead", OwnershipType.TECHNICAL_OWNER)
          .addOwner("urn:li:corpuser:product_team", OwnershipType.BUSINESS_OWNER);

// Remove owner
modelGroup.removeOwner("urn:li:corpuser:ml_platform_team");
```

### Glossary Terms

```java
// Add glossary terms
modelGroup.addTerm("urn:li:glossaryTerm:MachineLearning.ModelGroup")
          .addTerm("urn:li:glossaryTerm:CustomerAnalytics.Prediction");

// Remove term
modelGroup.removeTerm("urn:li:glossaryTerm:MachineLearning.ModelGroup");
```

### Domain

```java
// Set domain
modelGroup.setDomain("urn:li:domain:MachineLearning");

// Remove domain
modelGroup.removeDomain();
```

## 공통 패턴

### 완전한 Model Group 워크플로

```java
// 1. Create model group with comprehensive metadata
Map<String, String> customProperties = new HashMap<>();
customProperties.put("model_family", "transformer");
customProperties.put("framework", "pytorch");
customProperties.put("use_case", "customer_churn_prediction");
customProperties.put("model_type", "classification");
customProperties.put("deployment_status", "production");

MLModelGroup modelGroup = MLModelGroup.builder()
    .platform("sagemaker")
    .groupId("customer_churn_predictor")
    .env("PROD")
    .name("Customer Churn Prediction Model Family")
    .description(
        "Collection of customer churn prediction models trained on historical customer " +
        "behavior, subscription data, and engagement metrics. Models are retrained " +
        "monthly and deployed across all customer touchpoints.")
    .externalUrl("https://ml-platform.example.com/models/churn-predictor")
    .customProperties(customProperties)
    .build();

// 2. Add organizational metadata
modelGroup.addTag("churn-prediction")
          .addTag("classification")
          .addTag("production")
          .addTag("customer-analytics")
          .addOwner("urn:li:corpuser:ml_team", OwnershipType.TECHNICAL_OWNER)
          .addOwner("urn:li:corpuser:product_team", OwnershipType.BUSINESS_OWNER)
          .addTerm("urn:li:glossaryTerm:MachineLearning.Classification")
          .addTerm("urn:li:glossaryTerm:CustomerAnalytics.ChurnPrediction")
          .setDomain("urn:li:domain:MachineLearning");

// 3. Add training job lineage
modelGroup.addTrainingJob("urn:li:dataProcessInstance:training_pipeline_v1_2025_01")
          .addTrainingJob("urn:li:dataProcessInstance:training_pipeline_v2_2025_03")
          .addTrainingJob("urn:li:dataProcessInstance:training_pipeline_v3_2025_06");

// 4. Add downstream job lineage
modelGroup.addDownstreamJob("urn:li:dataProcessInstance:prediction_service_deployment")
          .addDownstreamJob("urn:li:dataProcessInstance:batch_scoring_job")
          .addDownstreamJob("urn:li:dataProcessInstance:real_time_inference_api");

// 5. Save to DataHub
client.entities().upsert(modelGroup);
```

### 버전화된 모델 패밀리 패턴

```java
// Step 1: Create the model group
MLModelGroup modelGroup = MLModelGroup.builder()
    .platform("tensorflow")
    .groupId("fraud_detection_models")
    .env("PROD")
    .name("Fraud Detection Model Family")
    .description("Collection of fraud detection models across versions and environments")
    .build();

modelGroup.addTag("fraud-detection")
          .addOwner("urn:li:corpuser:fraud_ml_team", OwnershipType.TECHNICAL_OWNER)
          .setDomain("urn:li:domain:FraudPrevention");

client.entities().upsert(modelGroup);

// Step 2: Create individual model versions in the group
MLModel modelV1 = MLModel.builder()
    .platform("tensorflow")
    .name("fraud_detector_v1_0")
    .env("PROD")
    .displayName("Fraud Detector v1.0")
    .build();

modelV1.setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:tensorflow,fraud_detection_models,PROD)")
       .addTrainingMetric("accuracy", "0.92")
       .addCustomProperty("version", "1.0")
       .addCustomProperty("release_date", "2025-01-15");

client.entities().upsert(modelV1);

MLModel modelV2 = MLModel.builder()
    .platform("tensorflow")
    .name("fraud_detector_v2_0")
    .env("PROD")
    .displayName("Fraud Detector v2.0")
    .build();

modelV2.setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:tensorflow,fraud_detection_models,PROD)")
       .addTrainingMetric("accuracy", "0.95")
       .addCustomProperty("version", "2.0")
       .addCustomProperty("release_date", "2025-06-15")
       .addCustomProperty("improvements", "New feature engineering and ensemble methods");

client.entities().upsert(modelV2);
```

### 다중 환경 Model Group 패턴

```java
// Create model groups for each environment
MLModelGroup devGroup = MLModelGroup.builder()
    .platform("mlflow")
    .groupId("recommendation_models")
    .env("DEV")
    .name("Recommendation Models - Development")
    .description("Development versions of recommendation models")
    .build();

devGroup.addTag("development")
        .addOwner("urn:li:corpuser:ml_dev_team", OwnershipType.TECHNICAL_OWNER);

client.entities().upsert(devGroup);

MLModelGroup stagingGroup = MLModelGroup.builder()
    .platform("mlflow")
    .groupId("recommendation_models")
    .env("STAGING")
    .name("Recommendation Models - Staging")
    .description("Staging versions of recommendation models for testing")
    .build();

stagingGroup.addTag("staging")
            .addOwner("urn:li:corpuser:ml_qa_team", OwnershipType.TECHNICAL_OWNER);

client.entities().upsert(stagingGroup);

MLModelGroup prodGroup = MLModelGroup.builder()
    .platform("mlflow")
    .groupId("recommendation_models")
    .env("PROD")
    .name("Recommendation Models - Production")
    .description("Production recommendation models serving live traffic")
    .build();

prodGroup.addTag("production")
         .addTag("business-critical")
         .addOwner("urn:li:corpuser:ml_prod_team", OwnershipType.TECHNICAL_OWNER)
         .addOwner("urn:li:corpuser:product_team", OwnershipType.BUSINESS_OWNER)
         .setDomain("urn:li:domain:ProductRecommendations");

client.entities().upsert(prodGroup);
```

### A/B 테스트 Model Group 패턴

```java
// Create a model group for A/B testing
MLModelGroup abTestGroup = MLModelGroup.builder()
    .platform("sagemaker")
    .groupId("product_ranking_ab_test")
    .env("PROD")
    .name("Product Ranking A/B Test Models")
    .description("Model group for A/B testing different product ranking algorithms")
    .build();

Map<String, String> abTestProps = new HashMap<>();
abTestProps.put("test_type", "ab_test");
abTestProps.put("test_id", "ranking_experiment_2025_10");
abTestProps.put("start_date", "2025-10-01");
abTestProps.put("expected_end_date", "2025-11-01");

MLModelGroup groupWithProps = MLModelGroup.builder()
    .platform("sagemaker")
    .groupId("product_ranking_ab_test")
    .env("PROD")
    .customProperties(abTestProps)
    .build();

abTestGroup.addTag("ab-test")
           .addTag("experiment")
           .addOwner("urn:li:corpuser:growth_team", OwnershipType.BUSINESS_OWNER)
           .addOwner("urn:li:corpuser:ml_team", OwnershipType.TECHNICAL_OWNER);

client.entities().upsert(abTestGroup);

// Champion model (80% traffic)
MLModel championModel = MLModel.builder()
    .platform("sagemaker")
    .name("ranking_champion_collaborative_filter")
    .env("PROD")
    .displayName("Champion: Collaborative Filtering")
    .build();

championModel.setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:sagemaker,product_ranking_ab_test,PROD)")
             .addCustomProperty("traffic_percentage", "80")
             .addCustomProperty("model_role", "champion")
             .addTrainingMetric("ndcg", "0.82");

client.entities().upsert(championModel);

// Challenger model (20% traffic)
MLModel challengerModel = MLModel.builder()
    .platform("sagemaker")
    .name("ranking_challenger_neural_network")
    .env("PROD")
    .displayName("Challenger: Neural Network")
    .build();

challengerModel.setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:sagemaker,product_ranking_ab_test,PROD)")
               .addCustomProperty("traffic_percentage", "20")
               .addCustomProperty("model_role", "challenger")
               .addTrainingMetric("ndcg", "0.85");

client.entities().upsert(challengerModel);
```

### 완전한 Lineage 패턴

```java
// Create a model group with full lineage tracking
MLModelGroup modelGroup = MLModelGroup.builder()
    .platform("vertexai")
    .groupId("customer_ltv_models")
    .env("PROD")
    .name("Customer Lifetime Value Models")
    .description("Models predicting customer lifetime value for marketing campaigns")
    .build();

// Add training job lineage (showing data sources)
modelGroup.addTrainingJob("urn:li:dataProcessInstance:customer_data_etl_2025_01")
          .addTrainingJob("urn:li:dataProcessInstance:feature_engineering_pipeline_2025_01")
          .addTrainingJob("urn:li:dataProcessInstance:model_training_pipeline_2025_01");

// Add downstream job lineage (showing consumers)
modelGroup.addDownstreamJob("urn:li:dataProcessInstance:ltv_scoring_batch_job")
          .addDownstreamJob("urn:li:dataProcessInstance:marketing_campaign_targeting")
          .addDownstreamJob("urn:li:dataProcessInstance:customer_segmentation_pipeline")
          .addDownstreamJob("urn:li:dataProcessInstance:retention_prediction_service");

modelGroup.addTag("ltv-prediction")
          .addTag("marketing-analytics")
          .addOwner("urn:li:corpuser:marketing_analytics_team", OwnershipType.BUSINESS_OWNER)
          .addOwner("urn:li:corpuser:ml_platform_team", OwnershipType.TECHNICAL_OWNER)
          .setDomain("urn:li:domain:Marketing");

client.entities().upsert(modelGroup);
```

## 모범 사례

1. **서술적인 그룹 ID 사용**: 그룹 ID는 모델 패밀리의 목적을 명확히 나타내야 합니다 (예: `customer_churn_models`, `fraud_detection_family`)

2. **일관된 명명 체계 유지**: 환경 전반에 걸쳐 일관된 명명 체계를 사용하세요 (예: DEV, STAGING, PROD에서 `recommendation_models`)

3. **그룹 수준에서 lineage 추적**: 모델 패밀리의 완전한 데이터 흐름을 보여주기 위해 학습 및 downstream job을 추가하세요.

4. **관련 버전 그룹화**: 동일한 비즈니스 모델의 모든 버전은 동일한 그룹에 속해야 합니다.

5. **환경 적절히 사용**: 승격 워크플로를 추적하기 위해 환경별로 model group을 분리하세요 (DEV, STAGING, PROD).

6. **모델 발전 문서화**: custom properties를 사용하여 중요한 이정표, 개선 사항, 아키텍처 변경 사항을 추적하세요.

7. **체계적인 태그 사용**: `production`, `experimental`, `deprecated`, `ab-test` 같은 태그로 model group을 분류하세요.

8. **소유권 명확히 설정**: 기술 담당자(ML 엔지니어)와 비즈니스 담당자(제품 관리자)를 지정하세요.

9. **외부 시스템 연결**: `externalUrl`을 사용하여 MLflow, SageMaker 또는 다른 ML 플랫폼 대시보드에 연결하세요.

10. **Custom properties 활용**: `framework`, `model_family`, `use_case`, `deployment_status` 같은 메타데이터를 저장하세요.

## Model Group vs 개별 Model

### Model Group을 사용해야 하는 경우

- **버전 관리**: 동일한 모델의 여러 버전 추적
- **A/B 테스트**: champion과 challenger 모델을 함께 그룹화
- **환경 승격**: DEV, STAGING, PROD 전반에 걸쳐 동일한 모델 패밀리 추적
- **집계 lineage**: 패밀리 수준에서 학습 및 downstream job 표시
- **팀 조직**: 특정 팀이 유지 관리하는 모든 모델 그룹화

### 개별 Model을 사용해야 하는 경우

- **특정 모델 버전**: 특정 지표와 하이퍼파라미터를 가진 특정 학습된 모델 표현
- **배포 추적**: 특정 모델 버전이 배포된 위치 추적
- **성능 지표**: 특정 모델에 대한 학습 및 검증 지표 저장
- **상세 메타데이터**: 하이퍼파라미터, 학습 설정, 모델 아티팩트 캡처

### 관계 모범 사례

```java
// 1. Create the model group first
MLModelGroup group = MLModelGroup.builder()
    .platform("tensorflow")
    .groupId("churn_models")
    .env("PROD")
    .name("Customer Churn Model Family")
    .build();
client.entities().upsert(group);

// 2. Create individual models that reference the group
MLModel modelV1 = MLModel.builder()
    .platform("tensorflow")
    .name("churn_predictor_v1")
    .env("PROD")
    .build();

// Link model to group
modelV1.setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:tensorflow,churn_models,PROD)");
client.entities().upsert(modelV1);

// 3. Repeat for other versions
MLModel modelV2 = MLModel.builder()
    .platform("tensorflow")
    .name("churn_predictor_v2")
    .env("PROD")
    .build();

modelV2.setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:tensorflow,churn_models,PROD)");
client.entities().upsert(modelV2);
```

## 참고 항목

- [MLModel Entity](mlmodel-entity.md) - 개별 모델 메타데이터 및 지표
- [Dataset Entity](dataset-entity.md) - 학습 데이터 lineage
- [DataJob Entity](datajob-entity.md) - 학습 및 추론 job 메타데이터
- [SDK V2 개요](README.md) - 일반 SDK 개념
