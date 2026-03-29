# Data Contracts

## Data Contract이란

Data Contract는 **데이터 자산의 생산자와 소비자 간의 합의**로, 데이터 품질에 대한 약속입니다.
데이터의 schema, freshness, 데이터 품질에 관한 [assertions](assertions.md)을 포함하는 경우가 많습니다.

Data Contract의 주요 특성:

- **검증 가능**: 메타데이터가 아닌 실제 물리적 데이터 자산을 기반으로 합니다(예: schema 검사, 컬럼 수준 데이터 검사, 운영 SLA - 문서, 소유권, 태그는 해당 안 됨).
- **assertions 집합**: 계약 상태를 결정하기 위해 물리적 자산에 대한 실제 검사(schema, freshness, volume, custom, column)
- **생산자 지향**: 물리적 데이터 자산당 하나의 계약, 생산자 소유.

<details>
<summary>소비자 지향 Data contracts</summary>
관리 가능한 계약 수를 유지하고 소비자들이 특정 물리적 자산의 계약에서 많은 부분이 겹치기를 원한다고 예상하기 때문에 생산자 지향 계약을 선택했습니다. 하지만 소비자 지향 data contracts가 생산자 지향 계약으로는 충족할 수 없는 특정 요구를 충족한다는 피드백을 들었습니다. 예를 들어, 같은 물리적 데이터 자산에서 소비자별로 하나의 계약이 있으면 각 소비자가 자신이 관심 있는 assertions가 위반될 때만 알림을 받을 수 있습니다. 슬랙에서 이에 대한 피드백을 환영합니다!
</details>

아래는 DataHub의 Data Contracts UI 스크린샷입니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/data_contracts/validated-data-contracts-ui.png"/>
</p>

## Data Contract과 Assertions

data contracts에 대한 비전을 다른 방식으로 표현하면 **물리적 데이터 자산에 대한 공개 생산자 약속을 나타내는 검증 가능한 assertions의 묶음**입니다.
이는 자산에 대한 모든 assertions이거나 소비자에게 공개적으로 약속하려는 하위 집합일 수 있습니다. Data Contracts를 사용하면 **선택한 assertions 그룹을 공개 약속으로 승격**할 수 있습니다: 이 assertions 하위 집합이 충족되지 않으면 Data Contract가 실패합니다.

assertions 유형 및 생성 및 실행 방법에 대한 자세한 내용은 [assertions](/docs/managed-datahub/observe/assertions.md) 문서를 참조하세요.

:::note 소유권
물리적 데이터 자산의 소유자는 계약의 소유자이기도 하며 제안된 변경 사항을 수락하고 계약을 직접 변경할 수 있습니다.
:::

## Data Contracts 생성 방법

Data Contracts는 DataHub API 또는 UI를 통해 생성할 수 있습니다.

### UI

1. 계약을 생성할 dataset의 Dataset 프로필로 이동합니다
2. **Quality** > **Data Contracts** 탭에서 **Create**를 클릭합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/data_contracts/create-data-contract-ui.png"/>
</p>

3. Data Contract에 포함할 assertions를 선택합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/data_contracts/select-assertions.png"/>
</p>

:::note UI를 통한 Data Contracts 생성
UI를 통해 Data Contract를 생성할 때 Freshness, Schema, 데이터 품질 assertions를 먼저 생성해야 합니다.
:::

4. 이제 UI에서 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/data_contracts/contracts-created.png"/>
</p>

### API

_data contract 생성에 관한 API 가이드가 곧 제공될 예정입니다!_

## Data Contracts 실행 방법

Data Contracts 실행은 계약의 assertions를 실행하고 DataHub에서 결과를 얻는 것에 달려 있습니다. DataHub Cloud Observe(SAAS에서 사용 가능)를 사용하면 DataHub 자체에서 assertions를 예약할 수 있습니다. 그렇지 않으면 DataHub 외부에서 assertions를 실행하고 결과를 DataHub에 다시 게시할 수 있습니다.

DataHub는 아래에 설명된 것처럼 DBT Test 및 Great Expectations와 잘 통합됩니다. 다른 서드파티 assertion 실행기의 경우 API를 사용하여 assertion 결과를 플랫폼에 다시 게시해야 합니다.

### DBT Test

DBT 수집 중 dbt `run_results` 파일을 가져와 dbt 테스트 실행 결과를 assertion 실행으로 변환합니다. [자세한 내용은 여기를 참조하세요.](/docs/generated/ingestion/sources/dbt.md#module-dbt)

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/data_contracts/dbt-test.png"/>
</p>

### Great Expectations

Great Expectations의 경우 **DataHubValidationAction**을 Great Expectations Checkpoint에 직접 통합하여 assertion(일명 expectation) 결과를 DataHub에 전송할 수 있습니다. [가이드는 여기를 참조하세요](../../../metadata-ingestion/integration_docs/great-expectations.md).

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/data_contracts/gx-test.png"/>
</p>
