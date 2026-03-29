# 메타데이터 aspect란 무엇인가?

메타데이터 aspect는 구조화된 문서, 보다 정확히는 [PDL](https://linkedin.github.io/rest.li/pdl_schema)의 `record`로서,
특정 종류의 메타데이터(예: 소유권, schema, 통계, 업스트림)를 표현합니다.
메타데이터 aspect는 그 자체만으로는 의미가 없으며(예: 무엇에 대한 소유권인지?), 특정 entity와 반드시 연결되어야 합니다(예: PageViewEvent에 대한 소유권).
각 aspect는 서로 크게 다를 것으로 예상되므로, 메타데이터 aspect에 어떠한 모델 요건도 강요하지 않는 것을 원칙으로 합니다.

메타데이터 aspect는 설계상 불변(immutable)입니다. 즉, 특정 aspect에 대한 모든 변경은 [새 버전](../advanced/aspect-versioning.md) 생성으로 이어집니다.
각 업데이트 후 가장 최근 X개의 버전만 보유하도록 선택적 보존 정책을 적용할 수 있습니다.
X를 1로 설정하면 메타데이터 aspect는 사실상 버전 관리가 없는 상태가 됩니다.
시간 기반 보존 정책을 적용하는 것도 가능합니다. 예를 들어, 최근 30일간의 메타데이터 변경 내역만 보유할 수 있습니다.

메타데이터 aspect는 여러 단계의 중첩 구조를 가진 임의로 복잡한 문서가 될 수 있지만, 때로는 단일 대형 aspect를 더 작고 독립적인 여러 aspect로 분리하는 것이 바람직합니다.
이렇게 하면 다음과 같은 이점이 있습니다:

1. **읽기/쓰기 속도 향상**: 메타데이터 aspect는 불변이므로, 모든 "업데이트"는 대형 aspect 전체를 기반 데이터 저장소에 다시 쓰는 작업을 수반합니다.
   마찬가지로, 읽기 측도 일부분만 필요하더라도 aspect 전체를 가져와야 합니다.
2. **서로 다른 aspect를 독립적으로 버전 관리**: 예를 들어, dataset에 대한 "schema 메타데이터" 변경과 무관하게 "소유권 메타데이터"의 변경 이력만 조회하는 것이 가능합니다.
3. **rest.li 엔드포인트 모델링 지원**: rest.li 엔드포인트와 메타데이터 aspect 간의 1:1 매핑이 필수는 아니지만, 이 패턴을 따르는 것이 자연스러우며, 결과적으로 거대한 단일 엔드포인트 대신 더 작고 모듈화된 엔드포인트를 갖게 됩니다.

다음은 메타데이터 aspect의 예시입니다. `admin` 및 `members` 필드가 `Group` entity와 `User` entity 간의 관계를 암묵적으로 표현하고 있음에 주목하세요.
이러한 관계를 메타데이터 aspect 내에 URN으로 저장하는 것은 매우 자연스럽습니다.
[relationship](relationship.md) 섹션에서는 이 관계를 명시적으로 추출하고 모델링하는 방법을 설명합니다.

```
namespace com.linkedin.group

import com.linkedin.common.AuditStamp
import com.linkedin.common.CorpuserUrn

/**
 * The membership metadata for a group
 */
record Membership {

  /** Audit stamp for the last change */
  auditStamp: AuditStamp

  /** Admin of the group */
  admin: CorpuserUrn

  /** Members of the group, ordered in descending importance */
  members: array[CorpuserUrn]
}
```
