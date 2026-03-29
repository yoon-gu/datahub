## 개요

dbt는 분석 또는 운영 데이터를 저장하고 쿼리하는 데 사용되는 데이터 플랫폼입니다. 자세한 내용은 [공식 dbt 문서](https://www.getdbt.com/)를 참조하세요.

DataHub의 dbt 통합은 dataset/테이블/뷰, schema 필드, 컨테이너와 같은 핵심 메타데이터 entity를 다룹니다. 모듈 기능에 따라 lineage, 사용량, 프로파일링, 소유권, 태그 및 stateful 삭제 감지와 같은 기능도 캡처할 수 있습니다.

:::info lineage를 위해 dbt와 데이터 웨어하우스 ingestion 모두 실행하기

1. **dbt와 데이터 웨어하우스(대상 플랫폼) 모두에 대해 ingestion을 실행**해야 합니다. 어떤 순서로든 실행할 수 있습니다.
2. `dbt` 노드 간(예: 모델/스냅샷이 dbt source 또는 임시 모델에 의존할 때) 열 lineage뿐만 아니라 `dbt` 노드와 기본 대상 플랫폼 노드 간의 lineage(예: BigQuery 테이블 -> dbt source, dbt 모델 -> BigQuery 테이블/뷰)도 생성합니다.
3. dbt 노드와 대상/데이터 웨어하우스 노드 간의 "sibling" 관계를 자동으로 생성합니다. 이러한 노드는 두 플랫폼 로고와 함께 UI에 표시됩니다.
4. dbt meta에 정의된 속성을 기반으로 자동화된 액션(예: 태그, 용어 또는 소유자 추가)도 지원합니다.
   :::

## Concept Mapping

| Source 개념 | DataHub 개념                                                        | 참고                   |
| -------------- | ---------------------------------------------------------------------- | ----------------------- |
| Source         | [Dataset](../../metamodel/entities/dataset.md)                         | 서브타입 `Source`        |
| Seed           | [Dataset](../../metamodel/entities/dataset.md)                         | 서브타입 `Seed`          |
| Model          | [Dataset](../../metamodel/entities/dataset.md)                         | 서브타입 `Model`         |
| Snapshot       | [Dataset](../../metamodel/entities/dataset.md)                         | 서브타입 `Snapshot`      |
| Semantic View  | [Dataset](../../metamodel/entities/dataset.md)                         | 서브타입 `Semantic View` |
| Test           | [Assertion](../../metamodel/entities/assertion.md)                     |                         |
| Test Result    | [Assertion Run Result](../../metamodel/entities/assertion.md)          |                         |
| Model Runs     | [DataProcessInstance](../../metamodel/entities/dataProcessInstance.md) |                         |
