# MLModel Entity

## 개요

`MLModel` entity는 DataHub에서 머신러닝 모델을 나타냅니다. ML 모델은 데이터를 학습하여 프로덕션 환경에 배포되며, 학습 지표, 하이퍼파라미터, model group, training job, downstream job, 배포 정보 등 종합적인 메타데이터를 포함합니다.

## URN 구조

MLModel URN은 다음 패턴을 따릅니다:

```
urn:li:mlModel:(urn:li:dataPlatform:{platform},{model_name},{environment})
```

**구성 요소:**

- `platform`: ML 플랫폼 (예: tensorflow, pytorch, sklearn, sagemaker)
- `model_name`: 모델의 고유 식별자
- `environment`: 환경 유형 (PROD, DEV, STAGING, TEST 등)

**예시:**

```
urn:li:mlModel:(urn:li:dataPlatform:tensorflow,user_churn_predictor,PROD)
urn:li:mlModel:(urn:li:dataPlatform:pytorch,recommendation_model_v2,STAGING)
urn:li:mlModel:(urn:li:dataPlatform:sklearn,fraud_detector,PROD)
```

## ML 관련 개념

### Training Metrics

모델 학습 중 수집되어 성능을 측정하는 지표:

- 분류: accuracy, precision, recall, f1_score, auc_roc, auc_pr
- 회귀: mse, mae, rmse, r2_score
- 손실 지표: log_loss, cross_entropy
- 커스텀 지표: training_time, validation_accuracy

### Hyperparameters

모델 학습 시 사용되는 설정 파라미터:

- 학습 설정: learning_rate, batch_size, epochs
- 아키텍처: hidden_layers, hidden_units, dropout_rate
- 최적화: optimizer, learning_rate_decay, momentum
- 정규화: l1_regularization, l2_regularization

### Model Groups

관련 모델들의 모음 (예: 동일한 모델 패밀리의 다양한 버전). 모델은 하나의 그룹에 속할 수 있으며, 버전 추적 및 A/B 테스트 시나리오를 지원합니다.

### Training Jobs

이 모델을 생성한 데이터 처리 job 또는 pipeline. 학습 데이터에서 모델까지의 lineage를 생성합니다.

### Downstream Jobs

추론, 스코어링 또는 예측을 위해 이 모델을 사용하거나 소비하는 job. 모델에서 downstream 애플리케이션까지의 lineage를 생성합니다.

### Deployments

모델이 배포된 프로덕션 환경 (예: SageMaker 엔드포인트, Kubernetes 서비스, REST API).

## ML Model 생성

### 기본 예시

```java
MLModel model = MLModel.builder()
    .platform("tensorflow")
    .name("user_churn_predictor")
    .env("PROD")
    .displayName("User Churn Prediction Model")
    .description("XGBoost model predicting user churn probability")
    .build();

// Add training metrics
model.addTrainingMetric("accuracy", "0.94")
     .addTrainingMetric("f1_score", "0.92")
     .addTrainingMetric("auc_roc", "0.96");

// Add hyperparameters
model.addHyperParam("learning_rate", "0.01")
     .addHyperParam("max_depth", "6")
     .addHyperParam("n_estimators", "100");

// Add standard metadata
model.addTag("production")
     .addOwner("urn:li:corpuser:ml_team", OwnershipType.TECHNICAL_OWNER)
     .setDomain("urn:li:domain:MachineLearning");

// Save to DataHub
client.entities().upsert(model);
```

### Builder 옵션

```java
MLModel model = MLModel.builder()
    .platform("pytorch")              // Required: ML platform
    .name("recommendation_model")     // Required: Model identifier
    .env("PROD")                      // Optional: Default is PROD
    .displayName("Product Recommender") // Optional: Human-readable name
    .description("Collaborative filtering model") // Optional
    .externalUrl("https://mlflow.company.com/models/123") // Optional
    .build();
```

## ML 관련 작업

### Training Metrics

```java
// Add individual metrics
model.addTrainingMetric("accuracy", "0.947")
     .addTrainingMetric("precision", "0.934")
     .addTrainingMetric("recall", "0.921");

// Set all metrics at once
MLMetric metric1 = new MLMetric();
metric1.setName("f1_score");
metric1.setValue("0.927");

MLMetric metric2 = new MLMetric();
metric2.setName("auc_roc");
metric2.setValue("0.965");

model.setTrainingMetrics(List.of(metric1, metric2));

// Get metrics
List<MLMetric> metrics = model.getTrainingMetrics();
```

### Hyperparameters

```java
// Add individual hyperparameters
model.addHyperParam("learning_rate", "0.001")
     .addHyperParam("batch_size", "64")
     .addHyperParam("epochs", "100");

// Set all hyperparameters at once
MLHyperParam param1 = new MLHyperParam();
param1.setName("dropout_rate");
param1.setValue("0.3");

MLHyperParam param2 = new MLHyperParam();
param2.setName("optimizer");
param2.setValue("adam");

model.setHyperParams(List.of(param1, param2));

// Get hyperparameters
List<MLHyperParam> params = model.getHyperParams();
```

### Model Groups

```java
// Set model group (creates relationship)
model.setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:tensorflow,churn_models,PROD)");

// Get model group
String group = model.getModelGroup();
```

### Training Jobs (Lineage)

```java
// Add training jobs
model.addTrainingJob("urn:li:dataJob:(urn:li:dataFlow:(airflow,ml_training_dag,prod),train_model)")
     .addTrainingJob("urn:li:dataProcessInstance:(urn:li:dataFlow:(airflow,ml_training_dag,prod),2025-10-15T08:00:00Z)");

// Remove training job
model.removeTrainingJob("urn:li:dataJob:(urn:li:dataFlow:(airflow,ml_training_dag,prod),train_model)");

// Get training jobs
List<String> jobs = model.getTrainingJobs();
```

### Downstream Jobs (Lineage)

```java
// Add downstream jobs
model.addDownstreamJob("urn:li:dataJob:(urn:li:dataFlow:(airflow,scoring_dag,prod),score_customers)")
     .addDownstreamJob("urn:li:dataJob:(urn:li:dataFlow:(airflow,inference_dag,prod),predict)");

// Remove downstream job
model.removeDownstreamJob("urn:li:dataJob:(urn:li:dataFlow:(airflow,scoring_dag,prod),score_customers)");

// Get downstream jobs
List<String> jobs = model.getDownstreamJobs();
```

### Deployments

```java
// Add deployments
model.addDeployment("urn:li:mlModelDeployment:(urn:li:dataPlatform:sagemaker,model-staging)")
     .addDeployment("urn:li:mlModelDeployment:(urn:li:dataPlatform:sagemaker,model-production)");

// Remove deployment
model.removeDeployment("urn:li:mlModelDeployment:(urn:li:dataPlatform:sagemaker,model-staging)");

// Get deployments
List<String> deployments = model.getDeployments();
```

## 표준 속성 작업

### 표시 이름과 설명

```java
// Set display name
model.setDisplayName("Customer Lifetime Value Model");

// Set description
model.setDescription("Deep learning model predicting CLV based on purchase history");

// Set external URL
model.setExternalUrl("https://mlflow.company.com/experiments/42/runs/abc123");

// Get properties
String name = model.getDisplayName();
String desc = model.getDescription();
String url = model.getExternalUrl();
```

### Custom Properties

```java
// Add individual properties
model.addCustomProperty("framework", "TensorFlow 2.14")
     .addCustomProperty("model_version", "2.1.0")
     .addCustomProperty("training_date", "2025-10-15");

// Set all properties at once
Map<String, String> props = new HashMap<>();
props.put("deployment_date", "2025-10-20");
props.put("inference_latency_ms", "15");
model.setCustomProperties(props);

// Get properties
Map<String, String> customProps = model.getCustomProperties();
```

## 표준 메타데이터 작업

### Tags

```java
// Add tags (with or without urn:li:tag: prefix)
model.addTag("production")
     .addTag("urn:li:tag:ml-model")
     .addTag("deep-learning");

// Remove tag
model.removeTag("production");
```

### Owners

```java
// Add owners with different types
model.addOwner("urn:li:corpuser:ml_platform_team", OwnershipType.TECHNICAL_OWNER)
     .addOwner("urn:li:corpuser:data_science_team", OwnershipType.DATA_STEWARD);

// Remove owner
model.removeOwner("urn:li:corpuser:ml_platform_team");
```

### Glossary Terms

```java
// Add glossary terms
model.addTerm("urn:li:glossaryTerm:MachineLearning.Model")
     .addTerm("urn:li:glossaryTerm:CustomerAnalytics.Prediction");

// Remove term
model.removeTerm("urn:li:glossaryTerm:MachineLearning.Model");
```

### Domain

```java
// Set domain
model.setDomain("urn:li:domain:MachineLearning");

// Remove specific domain
model.removeDomain("urn:li:domain:MachineLearning");

// Or clear all domains
model.clearDomains();
```

## 공통 패턴

### 완전한 ML Model 워크플로

```java
// 1. Create model with basic metadata
MLModel model = MLModel.builder()
    .platform("tensorflow")
    .name("customer_ltv_predictor")
    .env("PROD")
    .displayName("Customer Lifetime Value Prediction Model")
    .description("Deep learning model predicting customer lifetime value")
    .externalUrl("https://mlflow.company.com/experiments/42")
    .build();

// 2. Add comprehensive training metrics
model.addTrainingMetric("accuracy", "0.947")
     .addTrainingMetric("precision", "0.934")
     .addTrainingMetric("recall", "0.921")
     .addTrainingMetric("f1_score", "0.927")
     .addTrainingMetric("auc_roc", "0.965")
     .addTrainingMetric("training_time_minutes", "142.5");

// 3. Add comprehensive hyperparameters
model.addHyperParam("learning_rate", "0.001")
     .addHyperParam("batch_size", "64")
     .addHyperParam("epochs", "100")
     .addHyperParam("optimizer", "adam")
     .addHyperParam("dropout_rate", "0.3")
     .addHyperParam("hidden_layers", "3");

// 4. Set model group for version tracking
model.setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:tensorflow,ltv_models,PROD)");

// 5. Add training lineage
model.addTrainingJob("urn:li:dataJob:(urn:li:dataFlow:(airflow,ml_training_dag,prod),train_ltv)")
     .addTrainingJob("urn:li:dataProcessInstance:(urn:li:dataFlow:(airflow,ml_training_dag,prod),2025-10-15T08:00:00Z)");

// 6. Add downstream lineage
model.addDownstreamJob("urn:li:dataJob:(urn:li:dataFlow:(airflow,customer_scoring,prod),score)")
     .addDownstreamJob("urn:li:dataJob:(urn:li:dataFlow:(airflow,campaign_targeting,prod),target)");

// 7. Add deployment information
model.addDeployment("urn:li:mlModelDeployment:(urn:li:dataPlatform:sagemaker,ltv-staging)")
     .addDeployment("urn:li:mlModelDeployment:(urn:li:dataPlatform:sagemaker,ltv-production)");

// 8. Add organizational metadata
model.addTag("production")
     .addTag("deep-learning")
     .addTag("business-critical")
     .addOwner("urn:li:corpuser:ml_platform", OwnershipType.TECHNICAL_OWNER)
     .addOwner("urn:li:corpuser:data_science", OwnershipType.DATA_STEWARD)
     .addTerm("urn:li:glossaryTerm:MachineLearning.Model")
     .setDomain("urn:li:domain:MachineLearning");

// 9. Add custom properties
model.addCustomProperty("framework", "TensorFlow 2.14")
     .addCustomProperty("model_version", "2.1.0")
     .addCustomProperty("training_date", "2025-10-15")
     .addCustomProperty("deployment_date", "2025-10-20")
     .addCustomProperty("inference_latency_ms", "15");

// 10. Save to DataHub
client.entities().upsert(model);
```

### 모델 학습에서 배포까지의 흐름

```java
// Step 1: Create model after training
MLModel model = MLModel.builder()
    .platform("pytorch")
    .name("fraud_detector_v2")
    .env("DEV")
    .build();

// Step 2: Add training results
model.addTrainingMetric("accuracy", "0.97")
     .addTrainingMetric("precision", "0.95")
     .addHyperParam("learning_rate", "0.001")
     .addHyperParam("batch_size", "128")
     .setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:pytorch,fraud_models,DEV)");

client.entities().upsert(model);

// Step 3: Promote to staging
MLModel stagingModel = MLModel.builder()
    .platform("pytorch")
    .name("fraud_detector_v2")
    .env("STAGING")
    .build();

stagingModel.setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:pytorch,fraud_models,STAGING)")
            .addDeployment("urn:li:mlModelDeployment:(urn:li:dataPlatform:sagemaker,fraud-staging)");

client.entities().upsert(stagingModel);

// Step 4: Deploy to production
MLModel prodModel = MLModel.builder()
    .platform("pytorch")
    .name("fraud_detector_v2")
    .env("PROD")
    .build();

prodModel.setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:pytorch,fraud_models,PROD)")
         .addDeployment("urn:li:mlModelDeployment:(urn:li:dataPlatform:sagemaker,fraud-production)")
         .addTag("production")
         .addOwner("urn:li:corpuser:fraud_ml_team", OwnershipType.TECHNICAL_OWNER)
         .setDomain("urn:li:domain:FraudPrevention");

client.entities().upsert(prodModel);
```

### A/B 테스트 시나리오

```java
// Model A (current champion)
MLModel modelA = MLModel.builder()
    .platform("tensorflow")
    .name("recommendation_model_a")
    .env("PROD")
    .displayName("Recommendation Model A (Champion)")
    .build();

modelA.addTrainingMetric("accuracy", "0.92")
      .setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:tensorflow,recommendation_models,PROD)")
      .addDeployment("urn:li:mlModelDeployment:(urn:li:dataPlatform:sagemaker,recommend-prod-80pct)")
      .addCustomProperty("traffic_percentage", "80");

// Model B (challenger)
MLModel modelB = MLModel.builder()
    .platform("tensorflow")
    .name("recommendation_model_b")
    .env("PROD")
    .displayName("Recommendation Model B (Challenger)")
    .build();

modelB.addTrainingMetric("accuracy", "0.94")
      .setModelGroup("urn:li:mlModelGroup:(urn:li:dataPlatform:tensorflow,recommendation_models,PROD)")
      .addDeployment("urn:li:mlModelDeployment:(urn:li:dataPlatform:sagemaker,recommend-prod-20pct)")
      .addCustomProperty("traffic_percentage", "20")
      .addCustomProperty("experiment_id", "ab_test_2025_10");

client.entities().upsert(modelA);
client.entities().upsert(modelB);
```

## 모범 사례

1. **서술적인 이름 사용**: 모델 이름은 목적을 명확히 나타내야 합니다 (예: `user_churn_predictor_v2`, `fraud_detection_xgboost`)

2. **종합적인 지표 추적**: 투명성을 위해 학습 및 검증 지표를 모두 포함하세요.

3. **하이퍼파라미터 문서화**: 재현성을 위해 사용된 모든 하이퍼파라미터를 기록하세요.

4. **Lineage 유지**: 항상 training job과 downstream 소비자를 연결하세요.

5. **Model group 활용**: 관련 모델을 함께 그룹화하여 더 쉬운 버전 관리를 지원하세요.

6. **적절한 태그 사용**: `production`, `experimental`, `deprecated` 같은 태그를 사용하세요.

7. **소유권 설정**: 기술 담당자(ML 엔지니어)와 데이터 청지기를 지정하세요.

8. **배포 정보 추가**: 운영 모니터링을 위해 모델이 배포된 위치를 추적하세요.

9. **Custom properties 활용**: 프레임워크 버전, 학습 날짜, 성능 벤치마크를 저장하세요.

10. **외부 시스템 연결**: `externalUrl`을 사용하여 MLflow, SageMaker 또는 다른 ML 플랫폼에 연결하세요.

## 참고 항목

- [Dataset Entity](dataset-entity.md) - 학습 데이터 lineage
- [DataJob Entity](datajob-entity.md) - Training job 메타데이터
- [SDK V2 개요](README.md) - 일반 SDK 개념
