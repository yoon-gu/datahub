import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# MLModel & MLModelGroup

## MLModel과 MLModelGroup을 사용하는 이유

MLModel과 MLModelGroup entity는 메타데이터 생태계에서 머신러닝 모델과 관련 그룹을 표현하는 데 사용됩니다. 이를 통해 사용자는 머신러닝 모델의 버전, 설정, 성능 지표 등을 정의하고 관리하며 모니터링할 수 있습니다.

### 이 가이드의 목표

이 가이드에서는 다음 작업을 수행하는 방법을 안내합니다.

- MLModel 또는 MLModelGroup 생성하기.
- MLModel을 MLModelGroup과 연결하기.
- MLModel 및 MLModelGroup entity 읽기.

## 사전 요구 사항

이 튜토리얼을 진행하려면 DataHub Quickstart를 배포하고 샘플 데이터를 수집해야 합니다.
자세한 단계는 [DataHub Quickstart 가이드](/docs/quickstart.md)를 참조하세요.

## MLModelGroup 생성

이름, 플랫폼 등 필요한 속성을 제공하여 MLModelGroup을 생성할 수 있습니다.

```python
{{ inline /metadata-ingestion/examples/library/mlmodel_group_create.py show_path_as_comment }}
```

## MLModel 생성

이름, 플랫폼 등 필요한 속성을 제공하여 MLModel을 생성할 수 있습니다.

```python
{{ inline /metadata-ingestion/examples/library/mlmodel_create_full.py show_path_as_comment }}
```

MLModel을 생성할 때 그룹 URN을 제공하면 MLModel을 MLModelGroup과 연결할 수 있습니다.

아래와 같이 MLModel entity를 업데이트하여 나중에 MLModelGroup을 설정할 수도 있습니다.

```python
{{ inline /metadata-ingestion/examples/library/mlgroup_add_to_mlmodel.py show_path_as_comment }}
```

## MLModelGroup 읽기

그룹 URN을 제공하여 MLModelGroup을 읽을 수 있습니다.

```python
{{ inline /metadata-ingestion/examples/library/mlmodel_group_read.py show_path_as_comment }}
```

#### 예상 출력

```python
>> Model Group Name:  My Recommendations Model Group
>> Model Group Description:  A group for recommendations models
>> Model Group Custom Properties:  {'owner': 'John Doe', 'team': 'recommendations', 'domain': 'marketing'}
```

## MLModel 읽기

모델 URN을 제공하여 MLModel을 읽을 수 있습니다.

```python
{{ inline /metadata-ingestion/examples/library/mlmodel_read.py show_path_as_comment }}
```

#### 예상 출력

```python
>> Model Name:  My Recommendations Model
>> Model Description:  A model for recommending products to users
>> Model Group:  urn:li:mlModelGroup:(urn:li:dataPlatform:mlflow,my-recommendations-model,PROD)
>> Model Hyper Parameters:  [MLHyperParamClass({'name': 'learning_rate', 'description': None, 'value': '0.01', 'createdAt': None}), MLHyperParamClass({'name': 'num_epochs', 'description': None, 'value': '100', 'createdAt': None}), MLHyperParamClass({'name': 'batch_size', 'description': None, 'value': '32', 'createdAt': None})]
```
