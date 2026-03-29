import FeatureAvailability from '@site/src/components/FeatureAvailability';

# 커스텀 Ownership 유형

<FeatureAvailability/>

**🤝 버전 호환성**

> DataHub Core: **0.10.4** | DataHub Cloud: **0.2.8**

## 커스텀 Ownership 유형이란?

커스텀 Ownership 유형은 DataHub 내에서 사용자와 그들이 관리하는 데이터 자산 간의 ownership 관계를 설정하는 방식을 개선한 기능입니다.

## 커스텀 Ownership 유형이 필요한 이유

DataHub는 ownership 관계에 대해 사전 정의된 견해를 제공합니다. 그러나 이것이 항상 필요에 정확히 부합하지 않을 수 있다는 것을 알고 있습니다. 이 기능을 통해 이해관계자들이 사용하는 용어에 더 잘 맞도록 수정할 수 있습니다.

## 커스텀 Ownership 유형의 장점

커스텀 ownership 유형을 사용하면 조직의 ownership 명명 규칙을 DataHub에 직접 적용할 수 있습니다. 이를 통해 이해관계자들은 조직에서 이미 사용 중인 언어로 entity의 owner가 어떤 관계를 가지는지 파악할 수 있습니다.

## 커스텀 Ownership 유형 사용 방법

커스텀 Ownership 유형은 DataHub의 메타데이터 모델에서 완전히 새로운 entity로 구현되어 있어, entity 관련 API를 모두 사용할 수 있습니다. 또한 DataHub의 관리자 UI를 통해 관리할 수 있으며, 기존 ownership 유형과 동일한 방식으로 시스템 전체에서 ownership에 사용할 수 있습니다.

## 커스텀 Ownership 유형 설정, 사전 조건 및 권한

Ownership 유형을 생성하고 추가하려면 다음이 필요합니다:

- **Manage Ownership Types** 메타데이터 권한: 플랫폼 수준에서 Ownership 유형을 생성/삭제/수정하기 위해 필요합니다. [Platform Policy](./../authorization/policies.md#platform-policies)를 통해 부여할 수 있습니다.
- **Edit Owners** 메타데이터 권한: 특정 entity에 커스텀 ownership 유형과 연결된 owner를 추가하거나 제거하기 위해 필요합니다.

새 [Metadata Policy](./../authorization/policies.md#metadata-policies)를 생성하여 이 권한을 부여할 수 있습니다.

## 커스텀 Ownership 유형 사용하기

커스텀 Ownership 유형은 UI, GraphQL 명령어 또는 소프트웨어 엔지니어링(GitOps) 방식으로 관리할 수 있는 MCP ingestion을 통해 관리할 수 있습니다.

### 커스텀 Ownership 유형 관리 (UI)

커스텀 Ownership 유형을 관리하려면 먼저 DataHub 관리자 페이지로 이동합니다:

<p></p>

<p align="center">
    <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ownership/manage-view.png" />
</p>

그런 다음 `Management` 섹션 아래의 `Ownership Types` 탭으로 이동합니다.

새 유형을 만들려면 '+ Create new Ownership Type'을 클릭합니다.

그러면 Ownership 유형을 구성할 수 있는 새 모달이 열립니다.

폼 안에서 Ownership 유형의 이름을 선택할 수 있습니다. 다른 사용자들이 의미를 더 쉽게 이해할 수 있도록 ownership 유형에 대한 설명을 추가할 수도 있습니다.

걱정하지 마세요, 나중에 변경할 수 있습니다.

<p align="center">
    <img width="70%" src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ownership/ownership-type-create.png" />
</p>

이름과 설명을 선택한 후 'Save'를 클릭하여 새 Ownership 유형을 생성합니다.

관리 뷰에서 변경/삭제하려는 유형의 줄임표를 클릭하여 유형을 편집하거나 삭제할 수도 있습니다.

### 커스텀 Ownership 유형 관리 (CLI)

다른 모든 DataHub 메타데이터 entity와 마찬가지로, DataHub는 커스텀 Ownership 유형을 코드로 정의하고 관리하기 위한 JSON 기반의 커스텀 ownership 유형 스펙을 제공합니다.

다음은 "Architect"라는 이름의 커스텀 ownership 유형 예시입니다:

```json
{{ inline /metadata-ingestion/examples/ownership/ownership_type.json show_path_as_comment }}
```

이 파일을 DataHub에 업로드하려면 파일 기반 레시피를 사용하여 `ingest` 명령어 그룹을 통해 `datahub` CLI를 사용합니다:

```yaml
# see https://docs.datahub.com/docs/generated/ingestion/sources/file for complete documentation
source:
  type: "file"
  config:
    # path to json file
    path: "metadata-ingestion/examples/ownership/ownership_type.json"

# see https://docs.datahub.com/docs/metadata-ingestion/sink_docs/datahub for complete documentation
sink:
  type: "datahub-rest"
  config:
    server: "http://localhost:9002/api/gms"
```

마지막으로 다음을 실행합니다

```shell
datahub ingest -c recipe.yaml
```

업데이트가 필요한 경우 json 파일을 수정하고 CLI를 통해 다시 ingest하면 됩니다.

Ownership 유형을 삭제하려면 해당 ownership 유형의 URN에 대해 [삭제 명령어](../how/delete-metadata.md#soft-delete-the-default)를 실행합니다. 이 경우 `urn:li:ownershipType:architect`가 됩니다.

### 커스텀 Ownership 유형 관리 (GraphQL)

DataHub의 내장 [`GraphiQL` 에디터](../api/graphql/how-to-set-up-graphql.md#graphql-explorer-graphiql)를 사용하여 커스텀 ownership 유형을 생성/수정/삭제할 수도 있습니다:

```json
mutation {
  createOwnershipType(
    input: {
      name: "Architect"
      description: "Technical person responsible for the asset"
    }
  ) {
    urn
    type
    info {
      name
    	description
    }
  }
}
```

다음 응답이 표시되면 작업이 성공한 것입니다:

```json
{
  "data": {
    "createOwnershipType": {
      "urn": "urn:li:ownershipType:ccf9aa80-e3f3-4620-93a1-8d4a2ceaf5de",
      "type": "CUSTOM_OWNERSHIP_TYPE",
      "status": null,
      "info": {
        "name": "Architect",
        "description": "Technical person responsible for the asset",
        "created": null,
        "lastModified": null
      }
    }
  },
  "extensions": {}
}
```

CRUD 작업을 위한 `updateOwnershipType`, `deleteOwnershipType`, `listOwnershipTypes` 엔드포인트도 있습니다.

이 엔드포인트에 대한 [GraphQL 참조 문서](../api/graphql/overview.md)를 자유롭게 읽어보세요.

### Entity에 커스텀 Ownership 유형 할당 (UI)

Entity 페이지를 시작점으로 하여 커스텀 ownership 유형과 함께 entity에 owner를 할당할 수 있습니다.

Entity의 프로필 페이지에서 오른쪽 사이드바를 사용하여 Owners 섹션을 찾습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ownership/ownership-type-set-part1.png" />
</p>

'Add Owners'를 클릭하고 원하는 owner를 선택한 다음 이 자산을 추가할 커스텀 Ownership 유형을 검색합니다. 완료되면 'Add'를 클릭합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/ownership/ownership-type-set-part2.png" />
</p>

자산에서 ownership을 제거하려면 Owner 레이블의 'x' 아이콘을 클릭합니다.

> 주의: 자산에 Owner를 추가하거나 제거하려면 `Edit Owners` 메타데이터 권한이 필요하며, 이는
> [Policy](./../authorization/policies.md)를 통해 부여할 수 있습니다.
