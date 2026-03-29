import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Tags

<FeatureAvailability/>

Tag는 검색 및 발견을 돕는 비공식적이고 느슨하게 관리되는 레이블입니다. dataset, dataset 스키마 또는 컨테이너에 추가하여 entity를 레이블링하거나 분류하는 쉬운 방법을 제공합니다 — 더 광범위한 business glossary나 어휘와 연결할 필요 없이 사용할 수 있습니다.

Tag는 다음과 같은 경우에 도움이 됩니다:

- 쿼리: 동료가 동일한 dataset을 쿼리하는 데 사용할 수 있는 문구로 dataset에 태그 지정
- 자산을 원하는 카테고리나 그룹에 매핑

## Tags 설정, 사전 조건 및 권한

Tag를 추가하려면 다음이 필요합니다:

- **Edit Tags** 메타데이터 권한: entity 수준에서 tag를 추가하기 위해 필요
- **Edit Dataset Column Tags**: 컬럼 수준에서 tag를 편집하기 위해 필요

새 [Metadata Policy](./authorization/policies.md)를 생성하여 이 권한을 부여할 수 있습니다.

## DataHub Tags 사용하기

### Tag 추가

dataset 또는 컨테이너 수준에서 tag를 추가하려면 해당 entity 페이지로 이동하여 **Add Tag** 버튼을 클릭합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/master/imgs/add-tag.png"/>
</p>

추가할 tag의 이름을 입력합니다. 새 tag를 추가하거나 이미 존재하는 tag를 추가할 수 있습니다(자동 완성으로 기존 tag가 표시됩니다).

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/master/imgs/add-tag-search.png"/>
</p>

"Add" 버튼을 클릭하면 tag가 추가된 것을 확인할 수 있습니다!

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/master/imgs/added-tag.png"/>
</p>

스키마 수준에서 tag를 추가하려면 스키마의 "Tags" 컬럼 위에 마우스를 올려 "Add Tag" 버튼이 나타날 때까지 기다린 다음, 위와 동일한 절차를 따릅니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/master/imgs/add-schema-tag.png"/>
</p>

### Tag 제거

tag를 제거하려면 해당 tag의 "X" 버튼을 클릭합니다. 그런 다음 tag 제거 확인 프롬프트에서 "Yes"를 클릭합니다.

### Tag로 검색

검색창에서 tag를 검색할 수 있으며, 특정 tag의 존재 여부로 entity를 필터링할 수도 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/master/imgs/search-tag.png"/>
</p>

## 추가 리소스

### 동영상

**CSV를 통해 DataHub에 Ownership, Tags, Terms 등을 추가하세요!**

<p align="center">
<iframe width="560" height="315" src="https://www.youtube.com/embed/BGt59KpH1Ds" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</p>

### GraphQL

- [addTag](../graphql/mutations.md#addtag)
- [addTags](../graphql/mutations.md#addtags)
- [batchAddTags](../graphql/mutations.md#batchaddtags)
- [removeTag](../graphql/mutations.md#removetag)
- [batchRemoveTags](../graphql/mutations.md#batchremovetags)
- [createTag](../graphql/mutations.md#createtag)
- [updateTag](../graphql/mutations.md#updatetag)
- [deleteTag](../graphql/mutations.md#deletetag)

**tags** 속성을 사용하여 주어진 URN으로 entity의 Tags를 쉽게 가져올 수 있습니다. 예시는 [메타데이터 Entity 작업하기](./api/graphql/how-to-set-up-graphql.md#querying-for-tags-of-an-asset)를 참고하세요.

### DataHub 블로그

- [Tags and Terms: Two Powerful DataHub Features, Used in Two Different Scenarios
  Managing PII in DataHub: A Practitioner's Guide](https://medium.com/datahub-project/tags-and-terms-two-powerful-datahub-features-used-in-two-different-scenarios-b5b4791e892e)

## FAQ 및 문제 해결

**DataHub Tags와 Glossary Terms의 차이점은 무엇인가요?**

DataHub Tags는 비공식적이고 느슨하게 관리되는 레이블인 반면, Terms는 선택적 계층 구조를 갖는 통제된 어휘의 일부입니다. Tags에는 공식적인 중앙 관리 요소가 없습니다.

사용법과 적용:

- 하나의 자산에 여러 tag를 가질 수 있습니다.
- Tags는 검색 및 발견을 위한 도구로 사용되는 반면, Terms는 일반적으로 거버넌스를 위해 리프 레벨 속성(예: 스키마 필드)의 유형을 표준화하는 데 사용됩니다. 예: (EMAIL_PLAINTEXT)

**DataHub Tags와 Domain의 차이점은 무엇인가요?**

Domain은 자산과 가장 관련성이 높은 비즈니스 단위/분야에 맞게 정렬된 최상위 카테고리 집합입니다. 중앙 또는 분산 관리에 의존합니다. 데이터 자산당 하나의 domain이 할당됩니다.

### 관련 기능

- [Glossary Terms](./glossary/business-glossary.md)
- [Domains](./domains.md)
