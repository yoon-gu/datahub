---
title: 비즈니스 Glossary
---

import FeatureAvailability from '@site/src/components/FeatureAvailability';

# 비즈니스 Glossary

<FeatureAvailability/>

## 소개

복잡한 데이터 생태계에서 작업할 때, 공유된 어휘를 사용하여 데이터 자산을 구성하는 것은 매우 유용합니다. DataHub의 비즈니스 Glossary 기능은 표준화된 데이터 개념 집합을 정의하는 프레임워크를 제공하고, 이를 데이터 생태계 내에 존재하는 물리적 자산과 연결함으로써 이를 가능하게 합니다.

이 문서에서는 DataHub의 비즈니스 Glossary 기능을 구성하는 핵심 개념을 소개하고, 조직에서 이를 활용하는 방법을 보여드립니다.

### Terms 및 Term Groups

비즈니스 Glossary는 두 가지 중요한 기본 요소로 구성됩니다: Terms와 Term Groups.

- **Terms**: 특정 비즈니스 정의가 할당된 단어나 구문.
- **Term Groups**: 폴더처럼 작동하며, Terms와 다른 Term Groups를 포함하여 중첩 구조를 허용합니다.

Terms와 Term Groups 모두 문서를 추가하고 고유한 owner를 지정할 수 있습니다.

Glossary Terms의 경우 **Related Terms** 탭에서 서로 다른 Terms 간의 관계를 설정할 수 있습니다. 여기서 Contains 및 Inherits 관계를 생성할 수 있습니다. 마지막으로 **Related Entities** 탭에서 특정 Term으로 태그된 모든 entity를 확인할 수 있습니다.

## Glossary에 접근하기

비즈니스 Glossary를 보려면 사용자에게 [Policy](../authorization/policies.md)를 생성하여 부여할 수 있는 `Manage Glossaries`라는 Platform Privilege가 있어야 합니다.

이 권한이 부여되면 페이지 상단의 **Govern** 드롭다운을 클릭한 다음 **Glossary**를 클릭하여 Glossary에 접근할 수 있습니다:

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/glossary/glossary-button.png"/>
</p>

이제 Glossary의 루트에 있으며, 상위 항목이 없는 모든 Terms와 Term Groups를 볼 수 있습니다. 왼쪽에 Glossary 구조를 쉽게 확인할 수 있는 계층 탐색기도 표시됩니다!

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/glossary/root-glossary.png"/>
</p>

## Term 또는 Term Group 생성

UI를 통해 Terms와 Term Groups를 생성하는 두 가지 방법이 있습니다. 먼저 Glossary 홈 페이지에서 오른쪽 상단의 메뉴 점을 클릭하고 원하는 옵션을 선택하여 직접 생성할 수 있습니다:

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/glossary/root-glossary-create.png"/>
</p>

Term Group 페이지에서 직접 Terms 또는 Term Groups를 생성할 수도 있습니다. 이를 위해 오른쪽 상단의 메뉴 점을 클릭하고 원하는 항목을 선택합니다:

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/glossary/create-from-node.png"/>
</p>

팝업되는 모달은 현재 위치한 Term Group을 자동으로 **Parent**로 설정합니다. 입력창을 선택하고 Glossary를 탐색하여 원하는 Term Group을 찾아 쉽게 변경할 수 있습니다. 또한 Term Group의 이름을 입력하기 시작하면 검색을 통해 나타나도록 할 수 있습니다. 상위 항목 없이 Term 또는 Term Group을 생성하려면 이 입력창을 비워두면 됩니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/glossary/create-modal.png"/>
</p>

## Term 또는 Term Group 편집

Term 또는 Term Group을 편집하려면 먼저 편집하고자 하는 Term 또는 Term Group 페이지로 이동합니다. 그런 다음 이름 옆의 편집 아이콘을 클릭하여 인라인 에디터를 엽니다. 텍스트를 변경하고 외부를 클릭하거나 Enter를 누르면 저장됩니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/glossary/edit-term.png"/>
</p>

## Term 또는 Term Group 이동

Term 또는 Term Group이 생성된 후, 다른 Term Group 하위로 이동할 수 있습니다. 이를 위해 entity의 오른쪽 상단 메뉴 점을 클릭하고 **Move**를 선택합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/glossary/move-term-button.png"/>
</p>

그러면 Glossary를 탐색하여 원하는 Term Group을 찾을 수 있는 모달이 열립니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/glossary/move-term-modal.png"/>
</p>

## Term 또는 Term Group 삭제

Term 또는 Term Group을 삭제하려면 삭제하려는 항목의 entity 페이지로 이동한 다음 오른쪽 상단의 메뉴 점을 클릭합니다. 여기서 **Delete**를 선택하고 별도의 모달에서 확인합니다. **참고**: 현재 자식 항목이 없는 Term Groups만 삭제할 수 있습니다. 계단식 삭제가 지원될 때까지 모든 자식 항목을 먼저 삭제한 다음 Term Group을 삭제해야 합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/glossary/delete-button.png"/>
</p>

## Entity에 Term 추가

Glossary를 정의한 후 데이터 자산에 terms를 첨부할 수 있습니다. 자산에 Glossary Term을 추가하려면 자산의 entity 페이지로 이동하여 오른쪽 사이드바에서 **Add Terms** 버튼을 찾습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/glossary/add-term-to-entity.png"/>
</p>

팝업되는 모달에서 두 가지 방법 중 하나로 원하는 Term을 선택할 수 있습니다:

- 입력창에서 이름으로 Term 검색
- 입력창을 클릭하면 나타나는 Glossary 드롭다운을 통해 탐색

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/glossary/add-term-modal.png"/>
</p>

## 권한

Glossary Terms와 Term Groups는 다른 entity와 마찬가지로 메타데이터 정책을 따릅니다. 그러나 비즈니스 Glossary 내에서 권한을 구성하기 위해 두 가지 특별한 권한이 제공됩니다.

- **Manage Direct Glossary Children**: 사용자가 Glossary Term Group에 이 권한을 가지고 있으면, 해당 권한이 있는 Term Group 바로 아래의 Terms와 Term Groups를 생성, 편집, 삭제할 수 있습니다.
- **Manage All Glossary Children**: 사용자가 Glossary Term Group에 이 권한을 가지고 있으면, 해당 권한이 있는 Term Group 아래 어디에나 있는 Term 또는 Term Group을 생성, 편집, 삭제할 수 있습니다. 이는 자식 Term Group의 자식에도 적용됩니다(그 이하도 마찬가지).

## Shift left — Glossary를 Git으로 관리

이 [Github Action](https://github.com/acryldata/business-glossary-sync-action)을 사용하여 비즈니스 Glossary를 git 저장소에 가져올 수 있습니다. 이는 git에서 glossary를 관리하는 시작점이 될 수 있습니다.

## Git으로 Glossary 관리

많은 경우 비즈니스 Glossary를 git과 같은 버전 관리 시스템에서 관리하는 것이 더 좋을 수 있습니다. 이를 통해 모든 변경 사항을 변경 관리 및 검토 프로세스를 통해 처리함으로써 팀 간의 변경 관리를 더 쉽게 할 수 있습니다.

Git을 사용하여 glossary를 관리하려면 파일 내에서 정의한 다음 변경이 발생할 때마다(예: `git commit` 훅에서) DataHub CLI를 사용하여 DataHub에 ingest할 수 있습니다. Glossary 파일의 형식과 DataHub에 ingest하는 방법에 대한 자세한 내용은 [비즈니스 Glossary](../generated/ingestion/sources/business-glossary.md) 소스 가이드를 확인하세요.

## Glossary Term 관계에 대하여

DataHub는 개별 Glossary Terms _간의_ 두 가지 다른 종류의 관계를 지원합니다: **Inherits From**과 **Contains**.

**Contains**는 하나의 Glossary Term이 다른 Term의 _상위 집합_이거나 _구성_ 요소일 때 두 Glossary Terms를 연결하는 데 사용할 수 있습니다.
예시: **Address** Term이 **Zip Code** Term, **Street** Term, **City** Term을 _Contains_합니다 (_Has-A_ 스타일 관계)

**Inherits**는 하나의 Glossary Term이 다른 Term의 _하위 유형_ 또는 _하위 카테고리_일 때 두 Glossary Terms를 연결하는 데 사용할 수 있습니다.
예시: **Email** Term이 **PII** Term에서 _Inherits From_합니다 (_Is-A_ 스타일 관계)

이러한 관계 유형을 통해 조직 내에 존재하는 개념들을 매핑할 수 있으며, 개별 데이터 자산 및 컬럼에 첨부된 Glossary Terms를 변경하지 않고도 배경에서 개념 간의 매핑을 변경할 수 있습니다.

예를 들어, 물리적 데이터 타입을 나타내는 `Email Address`와 같은 매우 구체적이고 구체적인 Glossary Term을 정의한 다음, `Inheritance` 관계를 통해 이를 상위 레벨 `PII` Glossary Term과 연결할 수 있습니다. 이를 통해 `PII`를 포함하거나 처리하는 모든 데이터 자산 집합을 쉽게 유지 관리할 수 있으면서도, 개별 데이터 자산이나 컬럼을 재주석 달지 않고도 `PII` 분류에 새 Terms를 쉽게 추가하고 제거할 수 있습니다.

## 데모

[데모 사이트](https://demo.datahub.com/glossary)에서 Glossary 예시와 작동 방식을 확인해보세요!

### GraphQL

- [addTerm](../../graphql/mutations.md#addterm)
- [addTerms](../../graphql/mutations.md#addterms)
- [batchAddTerms](../../graphql/mutations.md#batchaddterms)
- [removeTerm](../../graphql/mutations.md#removeterm)
- [batchRemoveTerms](../../graphql/mutations.md#batchremoveterms)
- [createGlossaryTerm](../../graphql/mutations.md#createglossaryterm)
- [createGlossaryNode](../../graphql/mutations.md#createglossarynode) (Term Group)

**glossaryTerms** 속성을 사용하여 주어진 URN으로 entity의 Glossary Terms를 쉽게 가져올 수 있습니다. 예시는 [메타데이터 Entity 작업하기](../api/graphql/how-to-set-up-graphql.md#querying-for-glossary-terms-of-an-asset)를 확인하세요.

## 리소스

- [Creating a Business Glossary and Putting it to use in DataHub](https://medium.com/datahub-project/creating-a-business-glossary-and-putting-it-to-use-in-datahub-43a088323c12)
- [Tags and Terms: Two Powerful DataHub Features, Used in Two Different Scenarios](https://medium.com/datahub-project/tags-and-terms-two-powerful-datahub-features-used-in-two-different-scenarios-b5b4791e892e)

## 피드백 / 질문 / 우려 사항

의견을 듣고 싶습니다! 피드백, 질문, 우려 사항 등 모든 문의 사항은 Slack을 통해 연락해주세요!
