# Assertions

:::note 지원 데이터 플랫폼
현재 DataHub Cloud Observe의 일환으로 Snowflake, Redshift, BigQuery, Databricks의 데이터 모니터링을 지원합니다.
DataHub Cloud Observe는 [수집된 통계](/metadata-ingestion/docs/dev_guides/sql_profiles.md)를 활용하여 dataset 지표(행 수, 컬럼 null 여부 등) 및 dataset freshness에 대한 assertion을 다른 데이터 플랫폼에서도 모니터링할 수 있습니다.
:::

assertion은 **지정된 규칙을 위반하는 데이터를 찾아내는 데이터 품질 테스트**입니다.
assertion은 [Data Contracts](/docs/managed-datahub/observe/data-contract.md)의 구성 요소 역할을 하며, 계약이 충족되는지 검증하는 수단입니다.

## Assertion 생성 및 실행 방법

데이터 품질 테스트(즉, assertion)는 DataHub Cloud에서 생성 및 실행하거나 서드파티 도구에서 수집할 수 있습니다.

### DataHub Cloud Assertions

DataHub 제공 assertion 실행기의 경우, 소스와 DataHub에 접근하기 위한 에이전트를 사용자 환경에 배포할 수 있습니다. DataHub Cloud Observe는 다음 종류의 assertion을 기본 제공합니다:

- [Freshness](/docs/managed-datahub/observe/freshness-assertions.md) (SLA)
- [Volume](/docs/managed-datahub/observe/volume-assertions.md)
- [Custom SQL](/docs/managed-datahub/observe/custom-sql-assertions.md)
- [Column](/docs/managed-datahub/observe/column-assertions.md)
- [Schema](/docs/managed-datahub/observe/schema-assertions.md)

#### 모니터링 규칙 — 대규모 Assertions

[모니터링 규칙](/docs/managed-datahub/observe/data-health-dashboard.md#monitoring-rules)을 사용하면 데이터 환경 전반에 [Smart Assertions](/docs/managed-datahub/observe/smart-assertions.md)(AI 이상 탐지 모니터)를 자동으로 적용할 수 있습니다. DataHub 도메인, 데이터 플랫폼, schema 등의 검색 조건을 정의하면 DataHub가 일치하는 모든 dataset에 Freshness, Volume, Schema 이상 탐지 모니터를 생성합니다. 데이터 환경이 변화함에 따라 조건에 부합하는 새 dataset은 자동으로 모니터링되고, 더 이상 일치하지 않는 dataset은 모니터가 제거됩니다.

[데이터 상태 대시보드](/docs/managed-datahub/observe/data-health-dashboard.md)에서 모니터링 규칙을 생성하고 관리할 수 있습니다.

단일 dataset의 여러 컬럼에 대해 컬럼 지표 이상 탐지 모니터를 생성하려면 [Column Assertions](https://docs.datahub.com/docs/managed-datahub/observe/column-assertions#anomaly-detection-with-smart-assertions-)의 **이상 탐지** 섹션을 참조하세요.

### 대규모 데이터 환경에서 이상 탐지

어떤 assertion에 적합한 규칙을 파악할 시간이 부족하거나, 엄격한 규칙만으로는 데이터 검증 요구를 충족하기 어려운 경우가 많습니다. 전통적인 규칙 기반 assertion은 복잡한 데이터 패턴이나 대규모 운영 환경에서 부적절해질 수 있습니다.

**일반적인 시나리오**

수동 assertion 규칙이 부족한 대표적인 상황:

- **계절적 데이터 패턴** - 행 수 변화가 주간 계절성을 보이는 테이블의 경우 요일별로 서로 다른 assertion이 필요할 수 있어 정적 규칙 유지가 비현실적입니다.

- **대규모 dataset의 통계적 복잡성** - 각 컬럼의 예상 표준편차를 파악하는 것은 수백 개의 테이블에 걸쳐 매우 시간이 많이 소요되며, 테이블마다 고유한 특성이 있을 때는 더욱 어렵습니다.

- **동적 데이터 환경** - 데이터 패턴이 시간에 따라 변화할 때, assertion 규칙을 수동으로 업데이트하는 것은 유지 부담이 되어 오탐 또는 이상 탐지 누락으로 이어질 수 있습니다.

### AI Smart Assertion 솔루션

이러한 시나리오에서는 [Smart Assertion](./smart-assertions.md) 생성을 고려하여 머신러닝이 데이터의 정상 패턴을 자동으로 감지하고 이상이 발생했을 때 알림을 받을 수 있습니다. 이 접근 방식은 수동 규칙 유지 부담 없이 보다 유연하고 적응적인 데이터 품질 모니터링을 가능하게 합니다.

전통적인 assertion과 smart assertion 모두 DataHub API 또는 UI를 통해 정의할 수 있습니다.

### 시계열 버킷팅 및 과거 데이터 보정

특정 시간 세분성(예: 일별 또는 주별)으로 데이터를 평가해야 하는 assertion의 경우, [Volume](/docs/managed-datahub/observe/volume-assertions.md#time-series-bucketing) 및 [Column Metric](/docs/managed-datahub/observe/column-assertions.md#time-series-bucketing-for-column-metric-assertions) assertion에서 **시계열 버킷팅**을 활성화할 수 있습니다. 이 기능은 타임스탬프 컬럼을 사용하여 데이터를 시간 버킷으로 분할하고 각 버킷을 독립적으로 평가합니다.

버킷팅이 활성화된 Smart Assertions의 경우, AI 모델이 첫날부터 정확한 예측을 시작할 수 있도록 assertion의 지표 이력을 즉시 채우는 **과거 데이터 보정**도 구성할 수 있습니다. 자세한 내용은 [Assertion 이력 보정](/docs/managed-datahub/observe/assertion-backfill.md)을 참조하세요.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/assertions/assertion-ui.png"/>
</p>

### 서드파티 도구 연동

서드파티 도구는 다음과 같이 연동할 수 있습니다:

- [DBT Test](/docs/generated/ingestion/sources/dbt.md#integrating-with-dbt-test)
- [Great Expectations](../../../metadata-ingestion/integration_docs/great-expectations.md)
- [Custom Assertions](../../api/tutorials/custom-assertions.md)

서드파티 도구를 사용할 경우, DataHub에 저장된 Data Contract 사양에 따라 assertion이 실행되도록 직접 관리해야 합니다. 서드파티 실행기를 사용하는 경우, [DataHub Actions Framework](/docs/actions/README.md)를 통해 Kafka 토픽을 구독하여 Assertion 변경 이벤트를 수신할 수 있습니다.

## 알림

DataHub UI의 물리적 자산 페이지와 DataHub API 호출 결과에서 assertion 검사 결과(및 이력)를 확인할 수 있을 뿐만 아니라, assertion 실행 이벤트 [구독](https://youtu.be/VNNZpkjHG_I?t=79)이나 [인시던트](../../incidents/incidents.md) 발생 또는 해결 시 [Slack 메시지](/docs/managed-datahub/slack/saas-slack-setup.md)(DM 또는 팀 채널)로 알림을 받을 수도 있습니다. 향후에는 계약에 직접 구독하는 기능도 제공할 예정입니다.

DataHub Cloud Observe를 통해 [AWS EventBridge](/docs/managed-datahub/operator-guide/setting-up-events-api-on-aws-eventbridge.md)를 통한 API 이벤트를 수신하여 Assertion 실행 이벤트에 반응할 수 있습니다(각 솔루션의 가용성과 설정 편의성은 현재 DataHub Cloud 구성에 따라 다름 - 자세한 내용은 DataHub Cloud 담당자에게 문의).

## 노이즈 필터링 및 데이터 상태 보고

때로는 알림이 너무 많아져서 어떤 것이 중요한지 Slack 알림에서 파악하기 어려울 수 있습니다. 또한 팀이 소유한 어떤 테이블에 데이터 품질 검사가 실행되고 있는지 파악해야 할 때도 있습니다.
[데이터 상태 대시보드](./data-health-dashboard.md)는 데이터 환경의 상태를 전체적으로 조망할 수 있는 뷰를 제공합니다. 데이터를 슬라이스하고 다이스하여 원하는 정확한 답을 찾을 수 있습니다.

## 비용

assertion을 실행하는 다양한 방법을 제공하여 사용 사례에 따라 가장 저렴하고/또는 가장 정확한 방법을 사용할 수 있도록 합니다. 예를 들어, Freshness (SLA) assertion의 경우 감사 로그 또는 정보 스키마를 활용하면 비교적 저렴하게 freshness 검사를 실행할 수 있으며, Last Modified Column, High Watermark Column, DataHub Operation도 지원합니다([자세한 내용은 문서 참조](/docs/managed-datahub/observe/freshness-assertions.md#3-change-source)).

## 실행 세부 정보 - 위치 및 방법

DataHub Cloud assertion을 실행하는 방법은 여러 가지가 있습니다:

1. 소스 시스템 직접 쿼리:
   a. `Information Schema` 테이블은 테이블 freshness 또는 행 수에 대한 저렴하고 빠른 검사를 제공하는 기본 수단으로 사용됩니다.
   b. `Audit log` 또는 `Operation log` 테이블을 사용하여 테이블 작업을 세밀하게 모니터링할 수 있습니다.
   c. 테이블 자체를 직접 쿼리할 수도 있습니다. 이는 `last_updated` 컬럼을 참조하는 freshness 검사, 데이터 일부를 대상으로 하는 행 수 검사, 컬럼 값 검사에 유용합니다. 이러한 검사의 쿼리 비용을 줄이기 위한 여러 최적화를 제공합니다.
2. DataHub 메타데이터 참조
   a. 수집 또는 SDK를 통해 보고된 [Operations](/docs/api/tutorials/operations.md)을 사용하여 테이블 freshness 모니터링을 지원할 수 있습니다.
   b. SDK를 통해 수집되거나 보고된 `DatasetProfile` 및 `SchemaFieldProfile`을 사용하여 테이블 지표 및 컬럼 지표 모니터링을 지원할 수 있습니다.

### 프라이버시: 네트워크 내부 실행으로 데이터 외부 노출 방지

DataHub Cloud의 일환으로 [Remote Executor](/docs/managed-datahub/operator-guide/setting-up-remote-ingestion-executor.md) 배포 모델을 제공합니다. 이 모델을 사용하면 assertion이 사용자 네트워크 내에서 실행되고 결과만 DataHub Cloud로 전송됩니다. 실제 자격 증명이나 소스 데이터는 네트워크 밖으로 나가지 않습니다.

### 소스 시스템 선택

Assertion은 테이블을 처음 수집하는 데 사용된 것과 동일한 소스 시스템을 사용하여 쿼리를 실행합니다.
예를 들어 BigQuery 테이블에 대해 여러 수집 소스가 있는 경우, 기본적으로 실행기는 테이블의 `DatasetProperties`를 수집하는 데 사용된 수집 소스를 사용합니다. 이 동작은 고객 성공 담당자를 통해 변경할 수 있습니다.
