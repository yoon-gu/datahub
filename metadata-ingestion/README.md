# 메타데이터 수집 소개

:::tip 통합 source 찾기
수집 source를 탐색하고 기능별로 필터링하려면 **[통합 페이지](https://docs.datahub.com/integrations)**를 참조하세요.
:::

## 통합 방법

DataHub는 데이터 수집을 위한 세 가지 방법을 제공합니다:

- [UI Ingestion](../docs/ui-ingestion.md) : UI를 통해 메타데이터 ingestion pipeline을 쉽게 구성하고 실행합니다.
- [CLI Ingestion 가이드](cli-ingestion.md) : YAML을 사용하여 ingestion pipeline을 구성하고 CLI를 통해 실행합니다.
- SDK 기반 수집 : [Python Emitter](./as-a-library.md) 또는 [Java emitter](../metadata-integration/java/as-a-library.md)를 사용하여 ingestion pipeline을 프로그래밍 방식으로 제어합니다.

## 통합 유형

통합은 방법에 따라 두 가지 개념으로 나눌 수 있습니다:

### Push 기반 통합

Push 기반 통합을 사용하면 메타데이터가 변경될 때 데이터 시스템에서 직접 메타데이터를 내보낼 수 있습니다.
Push 기반 통합의 예로는 [Airflow](../docs/lineage/airflow.md), [Spark](../metadata-integration/java/acryl-spark-lineage/README.md), [Great Expectations](./integration_docs/great-expectations.md), [Protobuf Schemas](../metadata-integration/java/datahub-protobuf/README.md) 등이 있습니다. 이를 통해 데이터 에코시스템의 "능동적인" 에이전트로부터 낮은 지연 시간으로 메타데이터를 통합할 수 있습니다.

### Pull 기반 통합

Pull 기반 통합을 사용하면 데이터 시스템에 연결하고 배치 또는 증분 배치 방식으로 메타데이터를 추출하여 데이터 시스템을 "크롤링"하거나 "수집"할 수 있습니다.
Pull 기반 통합의 예로는 BigQuery, Snowflake, Looker, Tableau 등 다양한 서비스가 있습니다.

## 핵심 개념

다음은 ingestion과 관련된 핵심 개념입니다:

- [Sources](source_overview.md): 메타데이터를 추출하는 데이터 시스템 (예: BigQuery, MySQL)
- [Sinks](sink_overview.md): 메타데이터의 목적지 (예: 파일, DataHub)
- [Recipe](recipe_overview.md): .yaml 파일 형태의 ingestion 주요 구성

고급 가이드는 다음을 참조하세요:

- [메타데이터 수집 개발하기](./developing.md)
- [메타데이터 수집 source 추가하기](./adding-source.md)
- [Transformer 사용하기](./docs/transformer/intro.md)
