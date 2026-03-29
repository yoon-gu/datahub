# Sources

Source는 **메타데이터를 추출하는 데이터 시스템입니다.**

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/sources-sinks.png"/>
</p>

일반적으로 source는 아래와 같이 [recipe](./recipe_overview.md)의 상단에 정의됩니다.

```yaml
#my_recipe.yml
source:
  type: <source_name>
  config:
    option_1: <value>
    ...
```

## Source 유형

사이드바 왼쪽의 `Sources` 탭에서 메타데이터를 수집할 수 있는 모든 source를 확인할 수 있습니다. 예를 들어 [BigQuery](https://docs.datahub.com/docs/generated/ingestion/sources/bigquery), [Looker](https://docs.datahub.com/docs/generated/ingestion/sources/looker), [Tableau](https://docs.datahub.com/docs/generated/ingestion/sources/tableau) 등의 source가 있습니다.

:::tip 통합 source 찾기
전체 **[통합 목록](https://docs.datahub.com/integrations)**을 확인하고 기능별로 필터링하세요.
:::

## 메타데이터 수집 Source 상태

각 메타데이터 Source에 지원 상태를 적용하여 통합의 신뢰성을 한눈에 파악할 수 있도록 합니다.

![Certified](https://img.shields.io/badge/support%20status-certified-brightgreen): Certified Source는 DataHub 커뮤니티에서 충분히 테스트되고 널리 채택된 source입니다. 통합이 안정적이며 사용자 측면의 문제가 거의 없을 것으로 기대합니다.

![Incubating](https://img.shields.io/badge/support%20status-incubating-blue): Incubating Source는 DataHub 커뮤니티에서 사용할 준비가 되었지만 다양한 엣지 케이스에 대해 충분히 테스트되지 않았습니다. 커넥터를 강화하기 위해 커뮤니티의 피드백을 적극적으로 수렴하며, 향후 릴리스에서 마이너 버전 변경이 있을 수 있습니다.

![Testing](https://img.shields.io/badge/support%20status-testing-lightgrey): Testing Source는 DataHub 커뮤니티 멤버가 실험적으로 사용할 수 있지만 예고 없이 변경될 수 있습니다.
