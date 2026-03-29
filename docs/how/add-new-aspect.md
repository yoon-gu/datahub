# 새로운 메타데이터 aspect를 추가하는 방법

새로운 메타데이터 [aspect](../what/aspect.md)를 추가하는 것은 기존 [entity](../what/entity.md)를 확장하는 가장 일반적인 방법 중 하나입니다.
여기서는 CorpUserEditableInfo를 예시로 사용하겠습니다.

1. 해당 네임스페이스(예: [`com.linkedin.identity`](https://github.com/datahub-project/datahub/tree/master/metadata-models/src/main/pegasus/com/linkedin/identity))에 aspect 모델을 추가합니다.

2. entity의 aspect union을 확장하여 새 aspect를 포함합니다.

3. 프로젝트 루트에서 다음 명령을 실행하여 rest.li [IDL 및 snapshot](https://linkedin.github.io/rest.li/modeling/compatibility_check)을 재빌드합니다.

```
./gradlew :metadata-service:restli-servlet-impl:build -Prest.model.compatibility=ignore
```

4. 최상위 [리소스 엔드포인트](https://linkedin.github.io/rest.li/user_guide/restli_server#writing-resources)에 새 aspect를 노출하려면, 선택적 필드로 리소스 데이터 모델을 확장하세요. 또한 최상위 리소스(예: [`CorpUsers`](https://github.com/datahub-project/datahub/blob/master/gms/impl/src/main/java/com/linkedin/metadata/resources/identity/CorpUsers.java))의 `toValue` 및 `toSnapshot` 메서드를 확장하여 snapshot 및 value 모델 간에 변환해야 합니다.

5. (선택 사항) MCE 대신(또는 추가로) API를 통해 aspect를 업데이트해야 하는 경우, 새 aspect에 대한 [서브 리소스](https://linkedin.github.io/rest.li/user_guide/restli_server#sub-resources) 엔드포인트(예: `CorpUsersEditableInfoResource`)를 추가합니다. 서브 리소스 엔드포인트를 사용하면 이전 버전의 aspect와 감사 스탬프와 같은 추가 메타데이터도 검색할 수 있습니다.

6. gms, [mce-consumer-job](https://github.com/datahub-project/datahub/tree/master/metadata-jobs/mce-consumer-job), [mae-consumer-job](https://github.com/datahub-project/datahub/tree/master/metadata-jobs/mae-consumer-job)을 재빌드하고 재시작한 후에
   새 aspect로 [MCE](../what/mxe.md)를 내보내기 시작하면 자동으로 DB에 수집 및 저장됩니다.
