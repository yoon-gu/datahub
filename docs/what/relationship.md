# relationship란 무엇인가?

relationship는 정확히 두 [entity](entity.md) 간의 명명된 연관 관계로, 출발지(source)와 목적지(destination)로 구성됩니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/metadata-modeling.png"/>
</p>

위 그래프에서 `Group` entity는 `HasMember` relationship을 통해 `User` entity와 연결될 수 있습니다.
relationship 이름은 방향을 반영한다는 점, 즉 `Group`에서 `User`를 가리킨다는 점에 유의하세요.
이는 해당 정보를 담고 있는 실제 메타데이터 aspect가 User가 아닌 `Group`과 연관되어 있기 때문입니다.
방향이 반대였다면 relationship 이름은 `IsMemberOf`가 되었을 것입니다.
relationship 방향성에 대한 추가 논의는 [relationship의 방향](#direction-of-relationships)을 참조하세요.
relationship의 특정 인스턴스, 예를 들어 `urn:li:corpGroup:group1`이 `urn:li:corpuser:user1`을 멤버로 갖는다는 사실은
메타데이터 그래프에서 하나의 엣지(edge)에 해당합니다.

relationship은 "entity에 중립적"이어야 합니다. 다시 말해, `Dataset`을 `User`에 연결하거나 `Dashboard`를 `User`에 연결할 때 동일한 `OwnedBy` relationship을 사용하는 것을 기대합니다.
Pegasus는 URN이 본질적으로 모두 문자열이기 때문에 여러 URN 타입으로 필드를 타입 지정하는 것을 허용하지 않으므로,
source와 destination에 일반 URN 타입을 사용합니다.
허용되는 source 및 destination URN 타입을 제한하기 위해
`@Relationship` [어노테이션](../modeling/extending-the-metadata-model.md/#relationship)을 도입하였습니다.

relationship을 rest.li의 [association 리소스](https://linkedin.github.io/rest.li/modeling/modeling#association)로 모델링하는 것도 가능하며, 이 경우 매핑 테이블로 저장되는 경우가 많습니다. 그러나 메타데이터 aspect의 "외래 키" 필드로 모델링하는 것이 훨씬 더 일반적입니다. 예를 들어, `Ownership` aspect에는 소유자의 corpUser URN 배열이 포함될 가능성이 높습니다.

다음은 PDL에서 relationship을 모델링하는 방법의 예시입니다. 참고 사항:

1. 이 aspect인 `nativeGroupMembership`은 `corpUser`와 연관됩니다.
2. `corpUser`의 aspect는 `corpGroup` 타입의 하나 이상의 상위 entity를 가리킵니다.

```
namespace com.linkedin.identity

import com.linkedin.common.Urn

/**
 * Carries information about the native CorpGroups a user is in.
 */
@Aspect = {
  "name": "nativeGroupMembership"
}
record NativeGroupMembership {
  @Relationship = {
    "/*": {
      "name": "IsMemberOfNativeGroup",
      "entityTypes": [ "corpGroup" ]
    }
  }
  nativeGroups: array[Urn]
}
```

## relationship의 방향 {#direction-of-relationships}

relationship은 노드 간의 방향성 있는 엣지로 모델링되기 때문에, 어느 방향을 가리켜야 하는지, 혹은 양방향 엣지가 필요한지 묻는 것은 자연스러운 질문입니다.
답은 "사실 크게 상관없다"입니다. 이는 기술적인 선택이라기보다는 미적인 선택에 가깝습니다.

우선, 실제 방향은 그래프 쿼리 실행에 크게 영향을 미치지 않습니다. 대부분의 그래프 DB는 역방향으로 엣지를 효율적으로 탐색할 수 있습니다.

그렇기는 하지만, 일반적으로 relationship 방향을 지정하는 데 더 "자연스러운 방식"이 존재하며, 이는 메타데이터가 저장되는 방식과 밀접하게 관련됩니다. 예를 들어, LDAP 그룹의 멤버십 정보는 일반적으로 그룹 메타데이터에 목록 형태로 저장됩니다. 그 결과, 멤버에서 그룹으로 향하는 `IsMemberOf` relationship 대신, 그룹에서 멤버로 향하는 `HasMember` relationship을 모델링하는 것이 더 자연스럽습니다.

## 고카디널리티 relationship

고카디널리티 relationship을 최적으로 모델링하는 방법에 대한 제안은 [이 문서](../advanced/high-cardinality.md)를 참조하세요.
