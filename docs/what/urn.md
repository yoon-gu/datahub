# URN이란 무엇인가?

URN([Uniform Resource Name](https://en.wikipedia.org/wiki/Uniform_Resource_Name))은 DataHub에서 모든 리소스를 고유하게 정의하기 위해 선택된 [URI](https://en.wikipedia.org/wiki/Uniform_Resource_Identifier) 체계입니다. 다음과 같은 형식을 가집니다.

```
urn:<Namespace>:<Entity Type>:<ID>
```

[GMA](gma.md)에 [새 entity를 온보딩](../modeling/metadata-model.md)하려면 해당 entity에 특화된 URN을 모델링하는 것부터 시작합니다.
기존 [URN 모델](../../li-utils/src/main/javaPegasus/com/linkedin/common/urn)을 참고용으로 활용할 수 있습니다.

## 네임스페이스

DataHub에서 사용 가능한 모든 URN은 `li`를 네임스페이스로 사용합니다.
DataHub를 포크(fork)한다면 조직에 맞는 다른 네임스페이스로 쉽게 변경할 수 있습니다.

## Entity 타입

URN의 entity 타입은 GMA 문맥에서의 [entity](entity.md)와는 다릅니다. 각 인스턴스마다 고유 식별자가 필요한 리소스의 객체 타입으로 생각하면 됩니다. `dataset` entity 타입을 가진 [DatasetUrn]처럼 GMA entity에 대한 URN을 생성할 수도 있지만, [DataPlatformUrn]처럼 데이터 플랫폼에 대한 URN을 정의할 수도 있습니다.

## ID

ID는 URN의 고유 식별자 부분입니다. 특정 네임스페이스 내에서 특정 entity 타입에 대해 고유합니다.
ID는 단일 필드를 포함하거나, 복잡한 URN의 경우 여러 필드를 포함할 수 있습니다. 복잡한 URN은 ID 필드로 다른 URN을 포함할 수도 있습니다. 이런 유형의 URN을 중첩 URN이라고도 합니다. URN이 아닌 ID 필드의 경우 값은 문자열, 숫자, 또는 [Pegasus Enum](https://linkedin.github.io/rest.li/pdl_schema#enum-type)이 될 수 있습니다.

다음은 단일 ID 필드를 가진 URN의 예시입니다:

```
urn:li:dataPlatform:kafka
urn:li:corpuser:jdoe
```

[DatasetUrn](../../li-utils/src/main/javaPegasus/com/linkedin/common/urn/DatasetUrn.java)은 복잡한 중첩 URN의 예시입니다. `platform`, `name`, `fabric` 세 개의 ID 필드를 포함하며, `platform`은 또 다른 [URN](../../li-utils/src/main/javaPegasus/com/linkedin/common/urn/DataPlatformUrn.java)입니다. 다음은 예시입니다.

```
urn:li:dataset:(urn:li:dataPlatform:kafka,PageViewEvent,PROD)
urn:li:dataset:(urn:li:dataPlatform:hdfs,PageViewEvent,EI)
```

## 제한 사항

URN을 생성할 때 몇 가지 제한 사항이 있습니다:

URN 어디에서도 다음 문자는 허용되지 않습니다.

1. 소괄호는 URN 필드의 예약 문자입니다: `(` 또는 `)`
2. "단위 구분자" 유니코드 문자 `␟` (U+241F)

URN 튜플 내에서는 다음 문자가 허용되지 않습니다.

1. 쉼표는 URN 튜플의 예약 문자입니다: `,`

예시: `urn:li:dashboard:(looker,dashboards.thelook)`은 유효한 URN이지만, `urn:li:dashboard:(looker,dashboards.the,look)`은 유효하지 않습니다.

URN을 생성하거나 생성할 때 이러한 문자를 사용하지 마세요. 한 가지 방법은 해당 문자에 URL 인코딩을 사용하는 것입니다.
