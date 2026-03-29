import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Lineage 영향 분석

<FeatureAvailability/>

Lineage 영향 분석은 Dataset, Dashboard, Chart 및 기타 많은 DataHub Entity의 upstream 및 downstream 의존성 전체 집합을 이해하기 위한 강력한 워크플로입니다.

이를 통해 데이터 실무자들은 schema 변경 또는 데이터 파이프라인 실패가 downstream 의존성에 미치는 영향을 사전에 파악하고, 예상치 못한 데이터 품질 문제를 야기한 upstream 의존성을 신속하게 발견할 수 있습니다.

Lineage 영향 분석은 DataHub UI와 GraphQL 엔드포인트를 통해 사용 가능하며, 수동 및 자동화된 워크플로를 모두 지원합니다.

## Lineage 영향 분석 설정, 사전 요구사항 및 권한

Lineage 영향 분석은 다른 Entity와 Lineage 관계가 있는 모든 Entity에 대해 활성화되며 추가 설정이 필요하지 않습니다.

"View Entity Page" 권한이 있는 DataHub 사용자는 누구나 DataHub UI에서 upstream 또는 downstream Entity의 전체 집합을 조회하고 결과를 CSV로 내보낼 수 있습니다.

## Lineage 영향 분석 사용하기

다음의 간단한 단계를 통해 데이터 entity의 전체 의존성 체인을 파악할 수 있습니다.

1. 특정 Entity 페이지에서 **Lineage** 탭을 선택합니다

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/impact-analysis-lineage-tab.png"/>
</p>

2. **Upstream** 및 **Downstream** 의존성 사이를 쉽게 전환합니다

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/impact-analysis-choose-upstream-downstream.png"/>
</p>

3. 관심 있는 **의존성 차수**를 선택합니다. 프로세서 집약적인 쿼리를 최소화하기 위해 기본 필터는 "1차 의존성"으로 설정되어 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/impact-analysis-filter-dependencies.png"/>
</p>

4. Entity 타입, 플랫폼, 소유자 등으로 결과 목록을 분류하여 관련 의존성을 추출합니다

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/impact-analysis-apply-filters.png"/>
</p>

5. 전체 의존성 목록을 CSV로 내보냅니다

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/impact-analysis-export-full-list.png"/>
</p>

6. 할당된 소유권, 도메인, 태그, 용어 및 DataHub 내 해당 entity로 빠르게 돌아갈 수 있는 링크가 포함된 상세 정보와 함께 CSV로 필터링된 의존성 집합을 확인합니다

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/impact-analysis-view-export-results.png"/>
</p>

### 알려진 이슈

영향 분석은 시스템에 상당한 부하를 줄 수 있는 강력한 기능입니다. 대규모 결과 집합을 처리할 때 높은 성능을 유지하기 위해 결과를 더 빠르게 제공하는 대체 처리 경로인 "Lightning Cache"를 구현했습니다. 기본적으로 이 캐시는 결과 집합에 300개 이상의 자산이 있는 단순 쿼리에서 활성화됩니다. GMS 파드의 환경 변수 `CACHE_SEARCH_LINEAGE_LIGHTNING_THRESHOLD`를 설정하여 이 임계값을 사용자 정의할 수 있습니다.

그러나 Lightning Cache에는 한 가지 제한 사항이 있습니다: 소프트 삭제되었거나 DataHub 데이터베이스에 더 이상 존재하지 않는 자산이 포함될 수 있습니다. 이는 lineage 참조에 "유령 entity"(연관된 데이터가 없는 URN)가 포함될 수 있기 때문입니다.

영향 분석 결과를 다운로드할 때 시스템은 이러한 소프트 삭제 및 존재하지 않는 자산을 적절히 필터링합니다. 따라서 UI에 표시되는 내용과 다운로드한 결과 간에 차이가 있을 수 있습니다.

## 추가 리소스

### 동영상

**DataHub 201: 영향 분석**

<p align="center">
<iframe width="560" height="315" src="https://www.youtube.com/embed/BHG_kzpQ_aQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</p>

### GraphQL

- [searchAcrossLineage](../../graphql/queries.md#searchacrosslineage)
- [searchAcrossLineageInput](../../graphql/inputObjects.md#searchacrosslineageinput)

`searchAcrossLineage`를 사용하여 데이터 lineage를 읽는 예시를 찾고 계신가요? [여기](../api/tutorials/lineage.md#read-lineage)를 확인하세요.

### DataHub 블로그

- [의존성 영향 분석, 데이터 검증 결과 및 그 외 - DataHub v0.8.27 & v.0.8.28 주요 사항](https://medium.com/datahub-project/dependency-impact-analysis-data-validation-outcomes-and-more-1302604da233)

### FAQ 및 문제 해결

**Lineage 탭이 비활성화되어 있어 클릭할 수 없는 이유가 무엇인가요?**

해당 entity에 대한 Lineage 메타데이터를 아직 수집하지 않았음을 의미합니다. 시작하려면 Lineage 가이드를 참조하세요.

**내보낸 의존성 목록이 불완전한 이유가 무엇인가요?**

현재 의존성 목록을 10,000개 레코드로 제한하고 있습니다. 이 한도에 도달하면 필터를 적용하여 결과 집합을 좁히는 것을 권장합니다.

### 관련 기능

- [DataHub Lineage](../features/feature-guides/lineage.md)
