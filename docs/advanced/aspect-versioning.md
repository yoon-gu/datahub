# Aspect 버전 관리

[메타데이터 aspect](../what/aspect.md)의 각 버전은 불변이므로, 기존 aspect를 업데이트하면 새 버전이 생성됩니다. 일반적으로 버전 번호는 최신 버전이 가장 큰 버전 번호를 가지도록 순차적으로 증가할 것으로 예상됩니다. 즉, `v1`(가장 오래됨), `v2`(두 번째로 오래됨), ..., `vN`(최신). 그러나 이 방식은 rest.li 모델링과 트랜잭션 격리 모두에서 주요 과제를 야기하므로 재고가 필요합니다.

## Rest.li 모델링

특정 aspect에 대한 전용 rest.li 서브 리소스(예: `/datasets/{datasetKey}/ownership`)를 생성하는 것이 일반적이므로, 버전의 개념은 흥미로운 모델링 질문이 됩니다. 서브 리소스가 [Simple](https://linkedin.github.io/rest.li/modeling/modeling#simple) 타입이어야 할까요, 아니면 [Collection](https://linkedin.github.io/rest.li/modeling/modeling#collection) 타입이어야 할까요?

Simple인 경우, [GET](https://linkedin.github.io/rest.li/user_guide/restli_server#get) 메서드는 최신 버전을 반환할 것으로 예상되고, 최신 버전이 아닌 버전을 검색하는 유일한 방법은 커스텀 [ACTION](https://linkedin.github.io/rest.li/user_guide/restli_server#action) 메서드를 통해서인데, 이는 [REST](https://en.wikipedia.org/wiki/Representational_state_transfer) 원칙에 위배됩니다. 따라서 Simple 서브 리소스는 좋은 선택이 아닌 것 같습니다.

Collection인 경우, 버전 번호가 자연스럽게 키가 되어 일반적인 GET 메서드를 사용하여 특정 버전 번호를 쉽게 검색할 수 있습니다. 표준 [GET_ALL](https://linkedin.github.io/rest.li/user_guide/restli_server#get_all) 메서드를 사용하여 모든 버전을 나열하거나 [BATCH_GET](https://linkedin.github.io/rest.li/user_guide/restli_server#batch_get)을 통해 여러 버전을 가져오는 것도 쉽습니다. 그러나 Collection 리소스는 최신/가장 큰 키를 직접 가져오는 간단한 방법을 지원하지 않습니다. 이를 달성하려면 다음 중 하나를 수행해야 합니다:

- 페이지 크기가 1인 GET_ALL (내림차순 키 순서 가정)
- 특별한 매개변수와 페이지 크기 1의 [FINDER](https://linkedin.github.io/rest.li/user_guide/restli_server#finder)
- 다시 커스텀 ACTION 메서드

이러한 옵션 중 어느 것도 가장 일반적인 사용 사례 중 하나인 aspect의 최신 버전을 요청하는 자연스러운 방법처럼 보이지 않습니다.

## 트랜잭션 격리

[트랜잭션 격리](<https://en.wikipedia.org/wiki/Isolation_(database_systems)>)는 복잡한 주제이므로 먼저 기본 사항을 숙지하세요.

메타데이터 aspect의 동시 업데이트를 지원하기 위해 다음 의사 DB 작업이 단일 트랜잭션에서 실행되어야 합니다:

```
1. 현재 최대 버전(Vmax) 검색
2. 새 값을 (Vmax + 1)로 쓰기
```

위의 작업 1은 [Phantom Reads](<https://en.wikipedia.org/wiki/Isolation_(database_systems)#Phantom_reads>)에 쉽게 영향을 받을 수 있습니다. 이로 인해 작업 2가 잘못된 버전을 계산하여 새 버전을 생성하는 대신 기존 버전을 덮어쓸 수 있습니다.

이를 해결하는 한 가지 방법은 [성능 비용](https://logicalread.com/optimize-mysql-perf-part-2-mc13/#.XjxSRSlKh1N)으로 DB에서 [직렬화 가능(Serializable)](<https://en.wikipedia.org/wiki/Isolation_(database_systems)#Serializable>) 격리 수준을 강제하는 것입니다. 실제로 특히 분산 문서 저장소에서는 이 수준의 격리를 지원하는 DB가 거의 없습니다. [Repeatable Reads](<https://en.wikipedia.org/wiki/Isolation_(database_systems)#Repeatable_reads>) 또는 [Read Committed](<https://en.wikipedia.org/wiki/Isolation_(database_systems)#Read_committed>) 격리 수준을 지원하는 것이 더 일반적인데, 안타깝게도 이 경우에는 도움이 되지 않습니다.

또 다른 가능한 해결책은 `select`를 통해 계산할 필요 없이 별도의 테이블에서 `Vmax`를 트랜잭션 방식으로 추적하는 것입니다(Phantom Reads 방지). 그러나 교차 테이블/문서/entity 트랜잭션은 모든 분산 문서 저장소에서 지원하는 기능이 아니므로 일반화된 솔루션으로 적합하지 않습니다.

## 해결책: 버전 0

두 가지 도전에 대한 해결책은 놀랍도록 간단합니다. 최신 버전을 나타내기 위해 "부동" 버전 번호를 사용하는 대신 "고정/센티넬" 버전 번호를 사용할 수 있습니다. 이 경우 최신 버전 이외의 모든 버전이 여전히 순차적으로 증가하도록 버전 0을 선택합니다. 즉, `v0`(최신), `v1`(가장 오래됨), `v2`(두 번째로 오래됨) 등이 됩니다. 또는 단순히 모든 비-0 버전을 감사 추적으로 볼 수도 있습니다.

버전 0이 앞서 언급한 도전을 어떻게 해결할 수 있는지 살펴보겠습니다.

### Rest.li 모델링

버전 0을 사용하면 최신 버전을 얻는 것이 결정론적 키로 Collection aspect 특정 서브 리소스의 GET 메서드를 호출하는 것이 됩니다(예: `/datasets/{datasetkey}/ownership/0`). 이는 GET_ALL이나 FINDER를 사용하는 것보다 훨씬 자연스럽습니다.

### 트랜잭션 격리

버전 0의 경우 의사 DB 작업이 다음 트랜잭션 블록으로 변경됩니다:

```
1. aspect의 v0 검색
2. 현재 최대 버전(Vmax) 검색
3. 이전 값을 (Vmax + 1)로 다시 쓰기
4. 새 값을 v0으로 다시 쓰기
```

작업 2가 여전히 잠재적인 Phantom Reads의 영향을 받을 수 있고, 따라서 작업 3에서 기존 버전을 손상시킬 수 있지만, Repeatable Reads 격리 수준은 작업 4에서 감지된 [Lost Update](https://codingsight.com/the-lost-update-problem-in-concurrent-transactions/)로 인해 트랜잭션이 실패하도록 보장합니다. 이것은 MySQL의 InnoDB에 대한 [기본 격리 수준](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)이기도 합니다.
