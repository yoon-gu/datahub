import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# DataHub와 AI/ML 프레임워크 통합

## AI/ML 시스템을 DataHub와 통합하는 이유

데이터 실무자로서 AI 실험, 모델, 그리고 이들 간의 관계를 추적하는 것은 어려운 일입니다.
DataHub는 AI 자산을 체계적으로 정리하고 추적할 수 있는 중앙 집중식 공간을 제공하여 이 과정을 더 쉽게 만들어 줍니다.

이 가이드에서는 AI 워크플로를 DataHub와 통합하는 방법을 안내합니다.
MLflow 및 Amazon SageMaker 같은 인기 있는 ML 플랫폼과의 통합을 통해, DataHub는 조직 전체에서 AI 모델을 쉽게 찾고 공유하고, 모델이 시간에 따라 어떻게 발전하는지 추적하며, 각 모델과 학습 데이터 간의 연결을 이해할 수 있도록 합니다.
무엇보다 중요한 것은, 모든 것을 검색 가능하고 연결된 상태로 만들어 AI 프로젝트에서의 원활한 협업을 가능하게 한다는 점입니다.

## 이 가이드의 목표

이 가이드에서는 다음 내용을 배웁니다:

- 기본 AI 구성 요소(모델, 실험, 실행) 생성하기
- 이 구성 요소들을 연결하여 완전한 AI 시스템 구축하기
- 모델, 데이터, 실험 간의 관계 추적하기

## 핵심 AI 개념

DataHub의 핵심 구성 요소에 대해 알아야 할 내용은 다음과 같습니다:

- **Experiments**는 동일한 프로젝트에 대한 학습 실행의 모음으로, 예를 들어 이탈 예측기를 구축하기 위한 모든 시도를 포함합니다.
- **Training Runs**는 experiment 내에서 모델을 학습시키는 시도로, 파라미터와 결과를 기록합니다.
- **Model Groups**는 관련 모델들을 함께 구성하며, 예를 들어 이탈 예측기의 모든 버전을 포함합니다.
- **Models**는 프로덕션 사용을 위해 등록된 성공적인 학습 실행입니다.

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/concept-diagram-dh-term.png"/>
</p>

계층 구조는 다음과 같습니다:

1. 모든 실행은 experiment에 속합니다.
2. 성공적인 실행은 모델로 등록될 수 있습니다.
3. 모델은 model group에 속합니다.
4. 모든 실행이 모델이 되는 것은 아닙니다.

:::note 용어 매핑
각 AI 플랫폼(MLflow, Amazon SageMaker)은 고유한 용어를 사용합니다.
일관성을 유지하기 위해 이 가이드 전체에서 DataHub의 용어를 사용합니다.
DataHub 용어가 각 플랫폼의 용어에 어떻게 대응되는지는 아래 표를 참고하세요:

| DataHub         | 설명                                | MLflow        | SageMaker     |
| --------------- | ----------------------------------- | ------------- | ------------- |
| ML Model Group  | 관련 모델의 모음                    | Model         | Model Group   |
| ML Model        | model group 내의 버전화된 아티팩트  | Model Version | Model Version |
| ML Training Run | 단일 학습 시도                      | Run           | Training Job  |
| ML Experiment   | 학습 실행의 모음                    | Experiment    | Experiment    |

:::

플랫폼별 자세한 내용은 [MLflow](/docs/generated/ingestion/sources/mlflow.md) 및 [Amazon SageMaker](/docs/generated/ingestion/sources/sagemaker.md) 통합 가이드를 참조하세요.

## 기본 설정

이 튜토리얼을 진행하려면 DataHub Quickstart가 로컬에 배포되어 있어야 합니다.
자세한 단계는 [DataHub Quickstart 가이드](/docs/quickstart.md)를 참조하세요.

다음으로, [여기](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/examples/ai/dh_ai_client.py)에 정의된 `DatahubAIClient`를 사용하여 DataHub용 Python 클라이언트를 설정합니다.

DataHub UI에서 토큰을 생성하고 `<your_token>`을 해당 토큰으로 교체하세요:

```python
from dh_ai_client import DatahubAIClient

client = DatahubAIClient(token="<your_token>", server_url="http://localhost:9002")
```

:::note GraphQL로 확인하기
이 가이드 전반에 걸쳐 GraphQL 쿼리를 사용하여 변경 사항을 확인하는 방법을 안내합니다.
이 쿼리는 DataHub UI의 `https://localhost:9002/api/graphiql`에서 실행할 수 있습니다.
:::

## AI 자산 생성

ML 시스템의 기본 구성 요소를 만들어 보겠습니다. 이 구성 요소들은 AI 작업을 체계적으로 정리하고 팀이 쉽게 검색할 수 있도록 도와줍니다.

### Model Group 생성

model group은 유사한 모델의 다양한 버전을 포함합니다. 예를 들어, "Customer Churn Predictor"의 모든 버전은 하나의 그룹에 속합니다.

<Tabs>
<TabItem value="basic" label="Basic">
식별자만으로 기본 model group을 생성합니다:

```python
model_group = MLModelGroup(
    id="airline_forecast_models_group",
    platform="mlflow",
)

client._emit_mcps(model_group.as_mcps())
```

</TabItem>
<TabItem value="advanced" label="Advanced">
설명, 생성 타임스탬프, 팀 정보 등 풍부한 메타데이터를 추가합니다:

```python
model_group = MLModelGroup(
    id="airline_forecast_models_group",
    platform="mlflow",
    name="Airline Forecast Models Group",
    description="Group of models for airline passenger forecasting",
    created=datetime.now(),
    last_modified=datetime.now(),
    owners=[CorpUserUrn("urn:li:corpuser:datahub")],
    external_url="https://www.linkedin.com/in/datahub",
    tags=["urn:li:tag:forecasting", "urn:li:tag:arima"],
    terms=["urn:li:glossaryTerm:forecasting"],
    custom_properties={"team": "forecasting"},
)

client._emit_mcps(model_group.as_mcps())
```

</TabItem>
</Tabs>

model group이 생성되었는지 확인해 보겠습니다:

<Tabs>
<TabItem value="UI" label="UI">
DataHub UI에서 새로 생성된 model group을 확인합니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/model-group-empty.png"/>
</p>
</TabItem>

<TabItem value="graphql" label="GraphQL">
model group의 속성을 확인하기 위해 쿼리합니다:

```graphql
query {
  mlModelGroup(
    urn: "urn:li:mlModelGroup:(urn:li:dataPlatform:mlflow,airline_forecast_models_group,PROD)"
  ) {
    properties {
      name
      description
      created {
        time
      }
    }
  }
}
```

응답에서 model group의 상세 정보를 확인할 수 있습니다:

```json
{
  "data": {
    "mlModelGroup": {
      "properties": {
        "name": "Airline Forecast Models Group",
        "description": "Group of models for airline passenger forecasting",
        "created": {
          "time": 1744356062485
        }
      }
    }
  },
  "extensions": {}
}
```

</TabItem>
</Tabs>

### Model 생성

다음으로, 배포 준비가 완료된 학습된 모델을 나타내는 특정 모델 버전을 생성해 보겠습니다.

<Tabs>
<TabItem value="basic" label="Basic">
필수 버전만으로 모델을 생성합니다:

```python
model = MLModel(
    id="arima_model",
    platform="mlflow",
)

client._emit_mcps(model.as_mcps())
```

</TabItem>
<TabItem value="advanced" label="Advanced">
프로덕션 사용을 위해 지표, 파라미터, 메타데이터를 포함합니다:

```python
model = MLModel(
    id="arima_model",
    platform="mlflow",
    name="ARIMA Model",
    description="ARIMA model for airline passenger forecasting",
    created=datetime.now(),
    last_modified=datetime.now(),
    owners=[CorpUserUrn("urn:li:corpuser:datahub")],
    external_url="https://www.linkedin.com/in/datahub",
    tags=["urn:li:tag:forecasting", "urn:li:tag:arima"],
    terms=["urn:li:glossaryTerm:forecasting"],
    custom_properties={"team": "forecasting"},
    version="1",
    aliases=["champion"],
    hyper_params={"learning_rate": "0.01"},
    training_metrics={"accuracy": "0.9"},
)

client._emit_mcps(model.as_mcps())
```

</TabItem>
</Tabs>

모델을 확인해 보겠습니다:

<Tabs>
<TabItem value="UI" label="UI">
DataHub UI에서 모델의 상세 정보를 확인합니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/model-empty.png"/>
</p>
</TabItem>

<TabItem value="graphql" label="GraphQL">
모델 정보를 쿼리합니다:

```graphql
query {
  mlModel(urn: "urn:li:mlModel:(urn:li:dataPlatform:mlflow,arima_model,PROD)") {
    properties {
      name
      description
    }
    versionProperties {
      version {
        versionTag
      }
    }
  }
}
```

응답에서 모델의 상세 정보를 확인할 수 있습니다:

```json
{
  "data": {
    "mlModel": {
      "properties": {
        "name": "ARIMA Model",
        "description": "ARIMA model for airline passenger forecasting"
      },
      "versionProperties": {
        "version": {
          "versionTag": "1"
        }
      }
    }
  },
  "extensions": {}
}
```

</TabItem>
</Tabs>

### Experiment 생성

experiment는 특정 프로젝트에 대한 여러 학습 실행을 체계적으로 정리하는 데 도움이 됩니다.

<Tabs>
<TabItem value="basic" label="Basic">
기본 experiment를 생성합니다:

```python
experiment = Container(
    container_key=ContainerKey(
        platform="mlflow",
        name="airline_forecast_experiment"
    ),
    display_name="Airline Forecast Experiment"
)

client._emit_mcps(experiment.as_mcps())
```

</TabItem>
<TabItem value="advanced" label="Advanced">
컨텍스트와 메타데이터를 추가합니다:

```python
experiment = Container(
    container_key=ContainerKey(
        platform="mlflow",
        name="airline_forecast_experiment"
    ),
    display_name="Airline Forecast Experiment",
    description="Experiment to forecast airline passenger numbers",
    extra_properties={"team": "forecasting"},
    created=datetime(2025, 4, 9, 22, 30),
    last_modified=datetime(2025, 4, 9, 22, 30),
    subtype=MLAssetSubTypes.MLFLOW_EXPERIMENT,
)

client._emit_mcps(experiment.as_mcps())
```

</TabItem>
</Tabs>

experiment를 확인합니다:

<Tabs>
<TabItem value="UI" label="UI">
UI에서 experiment의 상세 정보를 확인합니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/experiment-empty.png"/>
</p>
</TabItem>

<TabItem value="graphql" label="GraphQL">
experiment 정보를 쿼리합니다:

```graphql
query {
  container(urn: "urn:li:container:airline_forecast_experiment") {
    properties {
      name
      description
    }
  }
}
```

응답을 확인합니다:

```json
{
  "data": {
    "container": {
      "properties": {
        "name": "Airline Forecast Experiment",
        "description": "Experiment to forecast airline passenger numbers"
      }
    }
  },
  "extensions": {}
}
```

</TabItem>
</Tabs>

### Training Run 생성

training run은 특정 모델 학습 시도에 관한 모든 세부 정보를 기록합니다.

<Tabs>
<TabItem value="basic" label="Basic">
기본 training run을 생성합니다:

```python
client.create_training_run(
    run_id="simple_training_run",
)
```

</TabItem>
<TabItem value="advanced" label="Advanced">
지표, 파라미터 및 기타 중요한 메타데이터를 포함합니다:

```python
client.create_training_run(
    run_id="simple_training_run",
    properties=DataProcessInstancePropertiesClass(
        name="Simple Training Run",
        created=AuditStampClass(
            time=1628580000000, actor="urn:li:corpuser:datahub"
        ),
        customProperties={"team": "forecasting"},
    ),
    training_run_properties=MLTrainingRunPropertiesClass(
        id="simple_training_run",
        outputUrls=["s3://my-bucket/output"],
        trainingMetrics=[MLMetricClass(name="accuracy", value="0.9")],
        hyperParams=[MLHyperParamClass(name="learning_rate", value="0.01")],
        externalUrl="https:localhost:5000",
    ),
    run_result=RunResultType.FAILURE,
    start_timestamp=1628580000000,
    end_timestamp=1628580001000,
)
```

</TabItem>
</Tabs>

training run을 확인합니다:

<Tabs>
<TabItem value="UI" label="UI">
UI에서 실행 상세 정보를 확인합니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/run-empty.png"/>
</p>
</TabItem>

<TabItem value="graphql" label="GraphQL">
training run을 쿼리합니다:

```graphql
query {
  dataProcessInstance(urn: "urn:li:dataProcessInstance:simple_training_run") {
    name
    created {
      time
    }
    properties {
      customProperties
    }
  }
}
```

응답을 확인합니다:

```json
{
  "data": {
    "dataProcessInstance": {
      "name": "Simple Training Run",
      "created": {
        "time": 1628580000000
      },
      "properties": {
        "customProperties": {
          "team": "forecasting"
        }
      }
    }
  }
}
```

</TabItem>
</Tabs>

### Dataset 생성

dataset은 ML 시스템의 핵심 구성 요소로, training run의 입력 및 출력 역할을 합니다. DataHub에 dataset을 생성하면 데이터 lineage를 추적하고 ML pipeline을 통해 데이터가 어떻게 흐르는지 파악할 수 있습니다.

<Tabs>
<TabItem value="basic" label="Basic">
최소한의 정보로 기본 dataset을 생성합니다:

```python
input_dataset = Dataset(
    platform="snowflake",
    name="iris_input",
)
client._emit_mcps(input_dataset.as_mcps())
```

</TabItem>
<TabItem value="advanced" label="Advanced">

보다 자세한 정보로 dataset을 생성합니다:

```python
input_dataset = Dataset(
    platform="snowflake",
    name="iris_input",
    description="Raw Iris dataset used for training ML models",
    schema=[("id", "number"), ("name", "string"), ("species", "string")],
    display_name="Iris Training Input Data",
    tags=["urn:li:tag:ml_data", "urn:li:tag:iris"],
    terms=["urn:li:glossaryTerm:raw_data"],
    owners=[CorpUserUrn("urn:li:corpuser:datahub")],
    custom_properties={
        "data_source": "UCI Repository",
        "records": "150",
        "features": "4",
    },
)
client._emit_mcps(input_dataset.as_mcps())

output_dataset = Dataset(
    platform="snowflake",
    name="iris_output",
    description="Processed Iris dataset with model predictions",
    schema=[("id", "number"), ("name", "string"), ("species", "string")],
    display_name="Iris Model Output Data",
    tags=["urn:li:tag:ml_data", "urn:li:tag:predictions"],
    terms=["urn:li:glossaryTerm:model_output"],
    owners=[CorpUserUrn("urn:li:corpuser:datahub")],
    custom_properties={
        "model_version": "1.0",
        "records": "150",
        "accuracy": "0.95",
    },
)
client._emit_mcps(output_dataset.as_mcps())
```

</TabItem>
</Tabs>

dataset을 확인합니다:

<Tabs>
<TabItem value="UI" label="UI"> DataHub UI에서 dataset 상세 정보를 확인합니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/dataset.png"/>
</p>

</TabItem>
<TabItem value="graphql" label="GraphQL">

dataset 정보를 쿼리합니다:

```graphql
query {
  dataset(
    urn: "urn:li:dataset:(urn:li:dataPlatform:snowflake,iris_input,PROD)"
  ) {
    name
    properties {
      customProperties
    }
  }
}
```

응답을 확인합니다:

```graphql
{
  "data": {
    "dataset": {
      "name": "iris_input",
      "properties": {
        "customProperties": {
          "data_source": "UCI Repository",
          "records": "150",
          "features": "4"
        }
      }
    }
  }
}
```

</TabItem>
</Tabs>

DataHub의 dataset은 schema 정보, 데이터 품질 지표, lineage 세부 정보도 포함할 수 있으며, 이는 모델 성능에 데이터 특성을 이해하는 것이 중요한 ML 워크플로에서 특히 유용합니다.

## 관계 정의

이제 이 구성 요소들을 연결하여 종합적인 ML 시스템을 구축해 보겠습니다. 이러한 연결을 통해 모델 lineage 추적, 모델 발전 모니터링, 의존성 파악, ML 자산 전반에 걸친 효과적인 검색이 가능해집니다.

### Model을 Model Group에 추가

모델을 해당 그룹에 연결합니다:

```python
model.add_group(model_group.urn)

client._emit_mcps(model.as_mcps())
```

<Tabs>
<TabItem value="UI" label="UI">

**Models** 섹션의 **Model Group** 아래에서 모델 버전을 확인합니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/model-group-with-model.png"/>
</p>

**Model** 페이지의 **Group** 탭에서 그룹 정보를 확인합니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/model-with-model-group.png"/>
</p>
</TabItem>

<TabItem value="graphql" label="GraphQL">
모델-그룹 관계를 쿼리합니다:

```graphql
query {
  mlModel(urn: "urn:li:mlModel:(urn:li:dataPlatform:mlflow,arima_model,PROD)") {
    name
    properties {
      groups {
        urn
        properties {
          name
        }
      }
    }
  }
}
```

응답을 확인합니다:

```json
{
  "data": {
    "mlModel": {
      "name": "ARIMA Model",
      "properties": {
        "groups": [
          {
            "urn": "urn:li:mlModelGroup:(urn:li:dataPlatform:mlflow,airline_forecast_models_group)",
            "properties": {
              "name": "Airline Forecast Models Group"
            }
          }
        ]
      }
    }
  }
}
```

</TabItem>
</Tabs>

### Run을 Experiment에 추가

training run을 해당 experiment에 연결합니다:

```python
client.add_run_to_experiment(run_urn=run_urn, experiment_urn=experiment_urn)
```

<Tabs>
<TabItem value="UI" label="UI">

**Experiment** 페이지의 **Entities** 탭에서 실행을 확인합니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/experiment-with-run.png"/>
</p>

**Run** 페이지에서 experiment 상세 정보를 확인합니다:

<p align="center">
  <img width="40%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/run-with-experiment.png"/>
</p>
</TabItem>

<TabItem value="graphql" label="GraphQL">
실행-experiment 관계를 쿼리합니다:

```graphql
query {
  dataProcessInstance(urn: "urn:li:dataProcessInstance:simple_training_run") {
    name
    parentContainers {
      containers {
        urn
        properties {
          name
        }
      }
    }
  }
}
```

관계 상세 정보를 확인합니다:

```json
{
  "data": {
    "dataProcessInstance": {
      "name": "Simple Training Run",
      "parentContainers": {
        "containers": [
          {
            "urn": "urn:li:container:airline_forecast_experiment",
            "properties": {
              "name": "Airline Forecast Experiment"
            }
          }
        ]
      }
    }
  }
}
```

</TabItem>
</Tabs>

### Run을 Model에 추가

training run을 결과 모델에 연결합니다:

```python
model.add_training_job(DataProcessInstanceUrn(run_id))

client._emit_mcps(model.as_mcps())
```

이 관계를 통해 다음이 가능합니다:

- 각 모델을 생성한 실행 추적
- 모델 출처 파악
- 모델 문제 디버깅
- 모델 발전 모니터링

<Tabs>
<TabItem value="UI" label="UI">

**Model** 페이지의 **Summary** 탭에서 소스 실행을 확인합니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/model-with-source-run.png"/>
</p>

**Run** 페이지의 **Lineage** 탭에서 관련 모델을 확인합니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/run-lineage-model.png"/>
</p>
<p align="center">
  <img width="50%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/run-lineage-model-graph.png"/>
</p>

</TabItem>

<TabItem value="graphql" label="GraphQL">
모델의 training job을 쿼리합니다:

```graphql
query {
  mlModel(urn: "urn:li:mlModel:(urn:li:dataPlatform:mlflow,arima_model,PROD)") {
    name
    properties {
      mlModelLineageInfo {
        trainingJobs
      }
    }
  }
}
```

관계를 확인합니다:

```json
{
  "data": {
    "mlModel": {
      "name": "ARIMA Model",
      "properties": {
        "mlModelLineageInfo": {
          "trainingJobs": ["urn:li:dataProcessInstance:simple_training_run"]
        }
      }
    }
  }
}
```

</TabItem>
</Tabs>

### Run을 Model Group에 추가

실행과 model group 사이에 직접 연결을 생성합니다:

```python
model_group.add_training_job(DataProcessInstanceUrn(run_id))

client._emit_mcps(model_group.as_mcps())
```

이 연결을 통해 다음이 가능합니다:

- 실행의 lineage에서 model group 확인
- 그룹 수준에서 training job 쿼리
- 모델 패밀리의 학습 이력 추적

<Tabs>
<TabItem value="UI" label="UI">

**Run** 페이지의 **Lineage** 탭에서 model group을 확인합니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/run-lineage-model-group.png"/>
</p>
<p align="center">
  <img width="50%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/run-lineage-model-group-graph.png"/>
</p>
</TabItem>

<TabItem value="graphql" label="GraphQL">
model group의 training job을 쿼리합니다:

```graphql
query {
  mlModelGroup(
    urn: "urn:li:mlModelGroup:(urn:li:dataPlatform:mlflow,airline_forecast_models_group)"
  ) {
    name
    properties {
      mlModelLineageInfo {
        trainingJobs
      }
    }
  }
}
```

관계를 확인합니다:

```json
{
  "data": {
    "mlModelGroup": {
      "name": "Airline Forecast Models Group",
      "properties": {
        "mlModelLineageInfo": {
          "trainingJobs": ["urn:li:dataProcessInstance:simple_training_run"]
        }
      }
    }
  }
}
```

</TabItem>
</Tabs>

### Dataset을 Run에 추가

training run의 입력 및 출력 dataset을 추적합니다:

```python
client.add_input_datasets_to_run(
    run_urn=run_urn,
    dataset_urns=[str(input_dataset_urn)]
)

client.add_output_datasets_to_run(
    run_urn=run_urn,
    dataset_urns=[str(output_dataset_urn)]
)
```

이러한 연결은 다음에 도움이 됩니다:

- 데이터 lineage 추적
- 데이터 의존성 파악
- 재현성 보장
- 데이터 품질 영향 모니터링

dataset 관계는 **Dataset** 또는 **Run** 페이지의 **Lineage** 탭에서 확인할 수 있습니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/run-lineage-dataset-graph.png"/>
</p>

## 속성 업데이트

### Model Group 속성 업데이트

model group에 추가 정보를 업데이트할 수 있습니다:

```python
# Update description
model_group.set_description("Updated description for airline forecast models")

# Add tags and terms
model_group.add_tag(TagUrn("production"))
model_group.add_term(GlossaryTermUrn("time-series"))

# Update custom properties
model_group.set_custom_properties({
    "team": "forecasting",
    "business_unit": "operations",
    "status": "active"
})

# Save the changes
client._emit_mcps(model_group.as_mcps())
```

이러한 업데이트를 통해 다음이 가능합니다:

- 상세한 설명으로 문서화 개선
- 태그와 용어로 일관된 비즈니스 컨텍스트 적용
- 조직 소유권 및 상태 추적

### Model 속성 업데이트

모델이 발전함에 따라 추가 정보를 업데이트할 수 있습니다:

```python
# Update model version
model.set_version("2")

# Add tags and terms
model.add_tag(TagUrn("marketing"))
model.add_term(GlossaryTermUrn("marketing"))

# Add version alias
model.add_version_alias("challenger")

# Save the changes
client._emit_mcps(model.as_mcps())
```

이러한 업데이트를 통해 다음이 가능합니다:

- 버전 관리를 통한 모델 반복 추적
- 태그와 용어로 비즈니스 컨텍스트 적용
- "champion"과 "challenger" 같은 배포 별칭 관리

### Experiment 속성 업데이트

프로젝트가 발전함에 따라 experiment에 추가 메타데이터를 업데이트할 수 있습니다:

```python
# Create a container object for the existing experiment
existing_experiment = Container(
    container_key=ContainerKey(
        platform="mlflow",
        name="airline_forecast_experiment"
    ),
)

# Update properties
existing_experiment.set_description("Updated experiment for forecasting passenger numbers")
existing_experiment.add_tag(TagUrn("time-series"))
existing_experiment.add_term(GlossaryTermUrn("forecasting"))
existing_experiment.set_custom_properties({
    "team": "forecasting",
    "priority": "high",
    "status": "active"
})

# Save the changes
client._emit_mcps(existing_experiment.as_mcps())
```

이러한 업데이트는 다음에 도움이 됩니다:

- 변화하는 experiment 목표 문서화
- 일관된 태그로 experiment 분류
- experiment 상태 및 우선순위 추적

## 전체 개요

모든 구성 요소가 연결된 완전한 ML 시스템입니다:

<p align="center">
  <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/apis/tutorials/ml/lineage-full.png"/>
</p>

이제 학습 데이터부터 실행을 거쳐 프로덕션 모델에 이르는 ML 자산의 완전한 lineage 뷰를 갖추게 되었습니다!

이 튜토리얼의 전체 코드는 [여기](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/examples/ai/dh_ai_client_sample.py)에서 확인할 수 있습니다.

## 다음 단계

이 통합들을 실제로 확인하려면:

- MLflow 통합을 시연하는 [타운홀 데모](https://youtu.be/_WUoVqkF2Zo?feature=shared&t=1932)를 시청하세요.
- 상세 문서를 참조하세요:
  - [MLflow 통합 가이드](/docs/generated/ingestion/sources/mlflow.md)
  - [Amazon SageMaker 통합 가이드](/docs/generated/ingestion/sources/sagemaker.md)
