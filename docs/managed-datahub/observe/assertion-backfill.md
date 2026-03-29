---
description: 이 페이지에서는 Assertion 보정(과거 데이터 부트스트래핑)에 대한 개요를 제공합니다
---

import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Assertion 이력 보정

<FeatureAvailability saasOnly />

> **Assertion 이력 보정** 기능은 DataHub Cloud의 **DataHub Cloud Observe** 모듈의 일부로 제공됩니다.
> **DataHub Cloud Observe**에 대해 더 알아보거나 체험해 보고 싶다면 [웹사이트를 방문](https://datahub.com/products/data-observability/)하세요.

<div align="center"><iframe width="640" height="444" src="https://www.loom.com/embed/61a201aea8464f58826c965fdbfbe255" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>

## 소개

새로운 [Smart Assertion](./smart-assertions.md)을 생성할 때 정확한 예측을 시작하기 전에 "정상"이 어떤 모습인지 학습하기 위한 과거 데이터가 필요합니다. 과거 컨텍스트 없이는 assertion의 AI 모델이 학습할 내용이 없어 이상을 안정적으로 감지하기 전에 실시간 평가를 며칠 또는 몇 주 동안 축적해야 합니다.

**Assertion 이력 보정**은 생성 시 과거 데이터에 대해 assertion을 실행하여 이 문제를 해결합니다. 예약된 평가를 통해 모델이 충분한 데이터 포인트를 축적할 때까지 기다리는 대신, 시스템이 과거 데이터를 위해 웨어하우스에 쿼리하고 한 번에 assertion의 지표 이력을 채웁니다. 이는 데이터의 일별, 주별, 월별 계절성을 완전히 인식하여 첫날부터 정확한 이상 탐지 임계값을 얻을 수 있음을 의미합니다.

보정은 다음 assertion 유형에 사용할 수 있습니다:

| Assertion 유형                    | 보정 지원                                                                                                  |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Smart Volume Assertion**        | 예 ([시계열 버킷팅](./volume-assertions.md#time-series-bucketing) 필요)                              |
| **Smart Column Metric Assertion** | 예 ([시계열 버킷팅](./column-assertions.md#time-series-bucketing-for-column-metric-assertions) 필요) |
| **Freshness Assertion**           | 아니오                                                                                                                |
| **Schema Assertion**              | 아니오                                                                                                                |
| **Custom SQL Assertion**          | 아니오                                                                                                                |

## 보정 작동 방식

보정이 활성화된 버킷팅된 assertion을 생성하면 다음 프로세스가 발생합니다:

1. **작업 생성**: 보정 작업이 `PENDING` 상태로 생성되고 실행 대기열에 추가됩니다.
2. **작업 예약**: 백그라운드 페처가 몇 분마다 실행되어 대기 중인 보정 작업을 가져와 실행을 위해 제출합니다. 웨어하우스 과부하를 방지하기 위해 최대 4개의 보정 작업이 동시에 실행됩니다.
3. **청크 실행**: 보정은 효율적인 `GROUP BY` 쿼리를 사용하여 청크 단위(데이터 약 1개월 분량)로 웨어하우스에 쿼리합니다. 이는 쿼리 비용과 복원력 사이의 균형을 맞춥니다 - 단일 청크가 실패해도 전체 보정이 아닌 해당 청크만 재시도하면 됩니다.
4. **진행 추적**: 각 청크가 완료된 후 진행 상황이 기록됩니다(완료율 및 마지막으로 평가된 버킷). 작업이 중단되면 중단된 지점에서 재개됩니다.
5. **완료**: 모든 과거 버킷이 채워지면 assertion의 AI 모델이 보정된 데이터를 기반으로 학습하여 예측 생성을 시작합니다.

### 보정 제한

과거 데이터를 보정할 수 있는 최대량은 버킷 간격에 따라 다릅니다:

| 버킷 간격 | 최대 되돌아보기    |
| --------------- | ------------------- |
| **일별**       | 365일(1년)   |
| **주별**      | 156주(3년) |

이 되돌아보기 윈도우는 assertion 생성 날짜를 기준으로 합니다.

### 보정 상태

assertion 상세 페이지에서 보정 진행 상황을 추적할 수 있습니다. 보정 작업은 다음 상태 중 하나에 있습니다:

- **Pending**: 보정 작업이 대기열에 있으며 실행기에 의해 처리되기를 기다리고 있습니다.
- **Submitted**: 작업이 시작하려고 합니다.
- **Running**: 보정 쿼리가 활발하게 실행 중입니다.
- **Complete**: 보정이 성공적으로 완료되었습니다.
- **Failed**: 보정에 오류가 발생했습니다. 보정을 재시도할 수 있습니다(아래 참조).
- **Rejected**: 적격성 요건을 충족하지 못했거나(예: assertion 유형이 보정을 지원하지 않음) 보정이 비활성화되어 보정이 시도되지 않았습니다.

:::info
대용량 테이블(1TB 초과)을 보정하는 것은 웨어하우스 컴퓨팅 측면에서 비용이 많이 들 수 있습니다. 더 짧은 되돌아보기 기간으로 시작하여 필요에 따라 확장하는 것을 고려하세요.
:::

## 보정 구성

### UI를 통한 구성

[시계열 버킷팅](./volume-assertions.md#time-series-bucketing)이 활성화된 새 smart assertion을 생성할 때:

1. **Backfill historical data**를 켜기로 전환합니다(smart assertions에서 버킷팅이 활성화된 경우 기본적으로 켜기로 설정됨).
2. 날짜 선택기를 사용하여 **보정 시작 날짜**를 선택합니다. 날짜 선택기는 최대 되돌아보기 제약(일별의 경우 365일, 주별 버킷팅의 경우 156주)을 적용합니다.
3. 나머지 assertion 구성을 완료하고 **Save**를 클릭합니다.

<p align="left">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/observe/bucketing/backfill.png"/>
</p>

생성 후 보정 시작 날짜를 업데이트할 수 있지만 버킷팅 구성(타임스탬프 컬럼, 버킷 간격, 시간대)은 변경할 수 없습니다.

### Python SDK를 통한 구성

`sync_smart_volume_assertion` 및 `sync_smart_column_metric_assertion` 메서드에서 `backfill_config` 파라미터를 사용하여 보정을 구성할 수 있습니다.

```python
from datahub.sdk import DataHubClient
from datahub.metadata.urns import DatasetUrn

client = DataHubClient(server="<your_server>", token="<your_token>")
dataset_urn = DatasetUrn.from_string(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,database.schema.table,PROD)"
)

# 일별 버킷팅과 6개월 보정을 사용한 smart volume assertion
assertion = client.assertions.sync_smart_volume_assertion(
    dataset_urn=dataset_urn,
    display_name="Daily Volume Anomaly Monitor",
    detection_mechanism="information_schema",
    sensitivity="medium",
    time_bucketing_strategy={
        "timestamp_field_path": "created_at",
        "bucket_interval": {"unit": "DAY", "multiple": 1},
        "timezone": "America/Los_Angeles",
    },
    backfill_config={
        "backfill_start_date_ms": 1688169600000,  # 2023-07-01T00:00:00Z
    },
    tags=["automated", "volume"],
    enabled=True,
)
```

`backfill_config` 파라미터는 다음을 허용합니다:

- `backfill_start_date_ms`(에포크 밀리초)가 있는 dict
- `BackfillConfig` Pydantic 모델(`datetime` 오브젝트 지원)
- 원시 `AssertionMonitorBootstrapConfigClass` GMS 모델

```python
from datetime import datetime
from acryl_datahub_cloud.sdk import BackfillConfig

# datetime 오브젝트가 있는 BackfillConfig 사용
backfill = BackfillConfig(backfill_start_date_ms=datetime(2024, 1, 1))

assertion = client.assertions.sync_smart_column_metric_assertion(
    dataset_urn=dataset_urn,
    column_name="user_id",
    metric_type="null_count",
    display_name="Smart Null Count - user_id",
    detection_mechanism="all_rows_query_datahub_dataset_profile",
    sensitivity="medium",
    time_bucketing_strategy={
        "timestamp_field_path": "created_at",
        "bucket_interval": {"unit": "WEEK", "multiple": 1},
    },
    backfill_config=backfill,
    enabled=True,
)
```

:::note
`backfill_config`는 `time_bucketing_strategy`도 설정되어 있어야 합니다. column metric assertion에서 `time_bucketing_strategy` 없이 `backfill_config`를 제공하면 구성이 거부되고 assertion이 생성되지 않습니다.
:::

## 실패한 보정 재시도

보정이 실패한 경우(웨어하우스 타임아웃, 네트워크 오류 등으로 인해), assertion 상세 페이지에서 재시도할 수 있습니다. 두 가지 재시도 모드가 있습니다:

- **소프트 재시도** (기본값): 마지막으로 성공적으로 평가된 버킷에서 보정을 재개합니다. 남은 간격만 채웁니다.
- **하드 리셋**: 처음부터 보정을 재시작하여 모든 버킷을 재평가하고 이전에 수집된 지표를 덮어씁니다. 기존 보정 데이터가 올바르지 않다고 의심되는 경우 사용하세요. 현재 GraphQL API를 통해서만 사용 가능합니다.

### UI를 통한 재시도

assertion 상세 페이지로 이동합니다. 보정 상태가 페이지 상단 근처에 발생한 오류와 함께 표시됩니다. **Retry**를 클릭합니다.

### GraphQL을 통한 재시도

```graphql
mutation retryMonitorBackfill {
  retryMonitorBackfill(
    input: { monitorUrn: "urn:li:monitor:your-monitor-id", hardReset: false }
  )
}
```

처음부터 전체 재보정을 수행하려면 `hardReset: true`로 설정합니다. 최근 항목을 추가/업데이트하고 백데이트한 작업을 실행한 경우 유용합니다.

## 사전 요구 사항

- **Remote Executor**: 보정에는 버전 **v0.3.17-acryl** 이상의 Remote Executor가 필요합니다.
- **웨어하우스 연결**: **Integrations** 탭에서 데이터 플랫폼(Snowflake, BigQuery, Redshift 또는 Databricks)에 대한 수집 소스가 구성되어 있어야 합니다.
- **권한**: 액터는 대상 dataset에 대해 `Edit Assertions` 및 `Edit Monitors` 권한이 있어야 합니다.

## FAQ

**Q: 보정 시 웨어하우스에 쿼리가 실행되나요?**
예. 버킷팅된 assertions의 경우 보정 프로세스는 과거 지표를 계산하기 위해 웨어하우스에 `GROUP BY` 쿼리를 실행합니다. 비용과 복원력 사이의 균형을 맞추기 위해 쿼리는 청크 단위(약 28일 분량)로 일괄 처리됩니다.

**Q: 생성 후 보정 시작 날짜를 변경할 수 있나요?**
예. 보정 시작 날짜는 생성 후 업데이트할 수 있습니다. 그러나 해당 버킷팅 파라미터(타임스탬프 컬럼, 버킷 간격, 시간대)는 assertion을 재생성하지 않고는 변경할 수 없습니다.

**Q: 보정 중 웨어하우스가 다운되면 어떻게 되나요?**
보정이 실패하며 재시도할 수 있습니다. 진행 상황이 청크별로 추적되므로 소프트 재시도는 처음부터 시작하는 대신 마지막으로 성공한 청크에서 재개됩니다.

**Q: 보정이 예약된 assertion 평가에 영향을 미치나요?**
아니오. 보정 실행은 일반적인 assertion 평가 스케줄을 방해하지 않습니다.
