---
title: "소개"
---

# Transformers

## Transformer란 무엇인가요?

우리는 종종 메타데이터가 ingestion sink에 도달하기 전에 수정하고 싶습니다 – 예를 들어 커스텀 태그, 소유권, 속성을 추가하거나 일부 필드를 patch하고 싶을 수 있습니다. Transformer는 정확히 이러한 작업을 수행할 수 있게 해줍니다.

게다가, transformer를 사용하면 ingestion 프레임워크의 코드를 직접 수정하지 않고도 ingestion되는 메타데이터에 대한 세밀한 제어가 가능합니다. 대신, 원하는 방식으로 메타데이터 이벤트를 변환할 수 있는 자체 모듈을 작성할 수 있습니다. transformer를 recipe에 포함시키려면 transformer의 이름과 transformer에 필요한 구성만 있으면 됩니다.

:::note

존재하지 않는 메타데이터에 대한 URN을 제공하면 예상치 못한 동작이 발생합니다. transformer에서 적용하려는 태그, 용어, 도메인 등의 URN이 DataHub 인스턴스에 이미 존재하는지 확인하세요.

예를 들어, transformer에서 dataset에 적용하기 위해 도메인 URN을 추가해도 해당 도메인 entity가 존재하지 않으면 생성되지 않습니다. 따라서 문서를 추가할 수 없고 고급 검색에 표시되지 않습니다. 이는 transformer에서 적용하는 모든 메타데이터에 해당됩니다.

:::

## 제공되는 transformer

자체 transformer를 작성하는 옵션(아래 참조) 외에도, 태그, glossary terms, 속성 및 소유권 정보를 추가하는 사용 사례를 위한 간단한 transformer를 제공합니다.

DataHub가 제공하는 dataset용 transformer는 다음과 같습니다:

- [Simple Add Dataset ownership](./dataset_transformer.md#simple-add-dataset-ownership)
- [Pattern Add Dataset ownership](./dataset_transformer.md#pattern-add-dataset-ownership)
- [Simple Remove Dataset ownership](./dataset_transformer.md#simple-remove-dataset-ownership)
- [Extract Ownership from Tags](./dataset_transformer.md#extract-ownership-from-tags)
- [Clean suffix prefix from Ownership](./dataset_transformer.md#clean-suffix-prefix-from-ownership)
- [Mark Dataset Status](./dataset_transformer.md#mark-dataset-status)
- [Simple Add Dataset globalTags](./dataset_transformer.md#simple-add-dataset-globaltags)
- [Pattern Add Dataset globalTags](./dataset_transformer.md#pattern-add-dataset-globaltags)
- [Add Dataset globalTags](./dataset_transformer.md#add-dataset-globaltags)
- [Set Dataset browsePath](./dataset_transformer.md#set-dataset-browsepath)
- [Simple Add Dataset glossaryTerms](./dataset_transformer.md#simple-add-dataset-glossaryterms)
- [Pattern Add Dataset glossaryTerms](./dataset_transformer.md#pattern-add-dataset-glossaryterms)
- [Add Dataset globalTags](./dataset_transformer.md#add-dataset-globaltags)
- [Pattern Add Dataset Schema Field glossaryTerms](./dataset_transformer.md#pattern-add-dataset-schema-field-glossaryterms)
- [Pattern Add Dataset Schema Field globalTags](./dataset_transformer.md#pattern-add-dataset-schema-field-globaltags)
- [Simple Add Dataset datasetProperties](./dataset_transformer.md#simple-add-dataset-datasetproperties)
- [Add Dataset datasetProperties](./dataset_transformer.md#add-dataset-datasetproperties)
- [Simple Add Dataset domains](./dataset_transformer.md#simple-add-dataset-domains)
- [Pattern Add Dataset domains](./dataset_transformer.md#pattern-add-dataset-domains)
- [Domain Mapping Based on Tags](./dataset_transformer.md#domain-mapping-based-on-tags)
- [Simple Add Dataset dataProduct ](./dataset_transformer.md#simple-add-dataset-dataproduct)
- [Pattern Add Dataset dataProduct](./dataset_transformer.md#pattern-add-dataset-dataproduct)
- [Add Dataset dataProduct](./dataset_transformer.md#add-dataset-dataproduct)
- [Set browsePaths](./universal_transformers.md#set-browsepaths)
