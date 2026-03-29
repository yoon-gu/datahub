import FeatureAvailability from '@site/src/components/FeatureAvailability';

# DataHub Lineage 소개

<FeatureAvailability />

데이터 lineage는 **조직 내에서 데이터가 어떻게 흐르는지를 보여주는 지도입니다.** 데이터가 어디서 시작되어 어떻게 이동하고 최종적으로 어디에 도달하는지를 상세하게 보여줍니다.
이는 단일 시스템 내에서 발생할 수도 있고(예: Snowflake 테이블 간 데이터 이동), 다양한 플랫폼에 걸쳐 발생할 수도 있습니다.

데이터 lineage를 활용하면 다음이 가능합니다:

- 데이터 무결성 유지
- 복잡한 관계를 단순화하고 정제
- [lineage 영향 분석](../../act-on-metadata/impact-analysis.md) 수행
- lineage를 통한 메타데이터 전파 (예: [문서](../../automations/docs-propagation.md))

## Lineage 조회

**Lineage** 탭에서 _Explorer_ 시각화 또는 _Impact Analysis_ 도구를 통해 lineage를 확인할 수 있습니다.
entity 사이드바에서 간단하게 자산의 영향 분석을 살펴볼 수도 있습니다.

<p align="center">
<img width="80%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/lineage-tab-v3.png" />
</p>

UI는 기본적으로 lineage의 최신 버전을 표시합니다. 타임피커를 사용하면 최신 버전 내의 엣지 중 지정된 시간 범위 밖에서 마지막으로 업데이트된 엣지를 필터링하여 제외할 수 있습니다. 과거 시간 범위를 선택해도 과거 lineage 이력을 보여주지 않습니다. 이 기능은 최신 lineage 버전의 뷰를 필터링하는 용도로만 사용됩니다.

<p align="center">
<img width="80%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/lineage-view-v3.png" />
</p>

이 예시에서 데이터는 dbt로 오케스트레이션된 서로 다른 Snowflake 테이블 사이를 흘러 Looker 뷰와 탐색으로 이어집니다.

### 컬럼 수준 Lineage

컬럼 수준 lineage는 **각 특정 데이터 컬럼의 변경 및 이동을 추적합니다.** 이 방식은 테이블 수준에서 lineage를 지정하는 테이블 수준 lineage와 대비되는 경우가 많습니다. 컬럼 lineage는 테이블 수준 lineage를 조회하면서 테이블의 컬럼을 펼치고 lineage가 있는 컬럼 위에 마우스를 올리거나 클릭하는 방식으로 시각화할 수 있습니다.

<p align="center">
<img width="80%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/column-level-lineage-v3.png" />
</p>

숨겨진 자산에 대한 컬럼 수준 lineage가 있거나 테이블 수준 뷰가 너무 복잡해진 경우,
컬럼의 브레드크럼을 클릭하면 단일 컬럼에 집중된 lineage를 시각화할 수 있습니다:

<p align="center">
<img width="80%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/schema-field-level-lineage-link.png" />
</p>

<p align="center">
<img width="80%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/schema-field-level-lineage.png" />
</p>

### 데이터 파이프라인 Lineage

DataHub는 데이터 lineage와 함께 데이터 파이프라인의 태스크 관계를 시각화하는 기능도 지원합니다. 데이터 파이프라인의 entity 페이지에서 **Lineage** 탭으로 이동하면 시각화 화면이 열립니다. 중앙에는 데이터 파이프라인 노드가 위치하며, 모든 구성 태스크를 포함하는 박스로 표현됩니다. 박스 내에서 각 태스크를 클릭하고 드래그하여 이동할 수 있으며, 데이터 파이프라인 박스 자체도 클릭하여 드래그할 수 있습니다.

<p align="center">
<img width="80%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/dataflow-lineage-tab.png" />
</p>

또한 DataHub의 크로스 플랫폼 lineage를 활용하여 각 태스크의 upstream과 downstream을 조회할 수 있습니다.
lineage 확장 버튼의 숫자는 해당 태스크가 가진 데이터 의존성 upstream / downstream의 수를 나타냅니다.
확장 후에는 표준 lineage 탐색기처럼 계속해서 lineage를 더 확장할 수 있습니다.

<p align="center">
<img width="80%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/dataflow-lineage-expand.png" />
</p>

시각화를 단순하게 유지하기 위해 한 번에 하나의 태스크의 upstream과 하나의 태스크의 downstream만 확장할 수 있습니다.

<p align="center">
<img width="80%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/dataflow-lineage-expand-2.png" />
</p>

## Lineage 추가

### Ingestion 소스

Lineage 추출을 지원하는 ingestion 소스(예: **테이블 Lineage 기능**)를 사용하는 경우 lineage 정보를 자동으로 추출할 수 있습니다. 자동 lineage 추출을 지원하는 소스 목록은
[여기](../../generated/lineage/automatic-lineage-extraction.md)에서 확인할 수 있습니다.
자세한 지침은 사용 중인 소스의 [소스 문서](https://docs.datahub.com/integrations)를 참조하세요.

### UI

`v0.9.5`부터 DataHub는 entity 간의 lineage 수동 편집을 지원합니다. 데이터 전문가들은 Lineage 시각화 화면과 entity 페이지의 Lineage 탭 모두에서 upstream 및 downstream lineage 엣지를 자유롭게 추가하거나 제거할 수 있습니다. 이 기능을 사용하여 자동 lineage 추출을 보완하거나, 자동 추출을 지원하지 않는 소스에서 중요한 entity 관계를 설정하세요. 수동 lineage 편집은 Dataset, Chart, Dashboard, Data Job에서 지원됩니다.
자세한 내용은 [Lineage에 관한 UI 가이드](./ui-lineage.md)를 참조하세요.

:::caution UI 기반 lineage 사용 시 권장 사항

수동으로 추가한 lineage와 프로그래밍 방식으로 추가한 lineage가 충돌하여 원치 않는 덮어쓰기가 발생할 수 있습니다.
lineage 정보가 자동화된 방식(예: ingestion 소스 실행)으로도 추출되지 않는 경우에만 lineage를 수동으로 편집하는 것을 강력히 권장합니다. lineage가 자동으로 수집되는 entity에 대해 수동으로 lineage를 편집하려는 경우, 해당 ingestion 소스가 `incremental_lineage`를 지원하는지 확인하고 지원한다면 해당 설정 플래그를 활성화하는 것을 고려하세요. 이 플래그를 설정하면 기존에 존재하던 lineage 엣지가 제거되지 않으므로, 현재 lineage를 정확하게 파악하려면 시간 기반 필터링을 사용해야 할 수도 있습니다.

:::

### API

Lineage를 지원하는 ingestion 소스를 사용하지 않는 경우, API를 통해 entity 간의 lineage 엣지를 프로그래밍 방식으로 emit할 수 있습니다.
자세한 내용은 [Lineage에 관한 API 가이드](../../api/tutorials/lineage.md)를 참조하세요.
