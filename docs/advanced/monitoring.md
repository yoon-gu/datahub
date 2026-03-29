# DataHub 모니터링

## 개요

DataHub의 시스템 컴포넌트 모니터링은 운영 우수성 유지, 성능 문제 해결, 시스템 안정성 보장에 필수적입니다. 이 포괄적인 가이드는 추적(tracing) 및 메트릭을 통해 DataHub에서 관측 가능성을 구현하고 실행 중인 인스턴스에서 귀중한 인사이트를 추출하는 방법을 다룹니다.

## 왜 DataHub를 모니터링하는가?

효과적인 모니터링을 통해 다음을 수행할 수 있습니다:

- 성능 병목 현상 식별: 느린 쿼리 또는 API 엔드포인트 파악
- 더 빠른 문제 디버깅: 분산 컴포넌트 전반에 걸쳐 요청을 추적하여 장애 위치 파악
- SLA 충족: 핵심 성능 지표 추적 및 알림

## 관측 가능성 컴포넌트

DataHub의 관측 가능성 전략은 두 가지 보완적인 접근 방식으로 구성됩니다:

1. 메트릭 수집

   **목적:** 시간 경과에 따른 시스템 동작에 대한 집계 통계 데이터
   **기술:** DropWizard/JMX에서 Micrometer로 전환 중

   **현재 상태:** JMX를 통해 노출된 DropWizard 메트릭, Prometheus가 수집
   **향후 방향:** Spring 기반 메트릭을 위한 네이티브 Micrometer 통합
   **호환성:** 다른 메트릭 백엔드를 지원하는 Prometheus 호환 형식

   주요 메트릭 카테고리:

   - 성능 메트릭: 요청 지연 시간, 처리량, 오류율
   - 리소스 메트릭: CPU, 메모리 활용률
   - 애플리케이션 메트릭: 캐시 히트율, 큐 깊이, 처리 시간
   - 비즈니스 메트릭: entity 수, 수집율, 검색 성능

2. 분산 추적

   **목적:** 여러 서비스와 컴포넌트를 통해 흐르는 개별 요청 추적
   **기술:** OpenTelemetry 기반 계측

   - 요청 수명 주기의 종단 간 가시성 제공
   - 인기 라이브러리(Kafka, JDBC, Elasticsearch) 자동 계측
   - 여러 백엔드 시스템 지원(Jaeger, Zipkin 등)
   - 최소한의 코드 변경으로 커스텀 span 생성 가능

   주요 이점:

   - 마이크로서비스 전반의 요청 흐름 시각화
   - 지연 시간 핫스팟 식별
   - 서비스 의존성 이해
   - 복잡한 분산 트랜잭션 디버그

## GraphQL 계측 (Micrometer)

### 개요

DataHub는 Micrometer 메트릭을 통해 GraphQL API에 대한 포괄적인 계측을 제공하여 상세한 성능 모니터링 및 디버깅 기능을 제공합니다. 계측 시스템은 관측 가능성 깊이와 성능 오버헤드 사이의 균형을 맞추기 위한 유연한 설정 옵션을 제공합니다.

### 경로 수준 GraphQL 계측이 중요한 이유

전통적인 GraphQL 모니터링은 "검색 쿼리가 느립니다"라고만 말할 뿐 **왜** 그런지는 알려주지 않습니다. 경로 수준 계측 없이는 복잡한 중첩 쿼리에서 성능 병목 현상을 일으키는 특정 필드를 알 수 없습니다.

### 실제 예시

다음 GraphQL 쿼리를 고려하세요:

```graphql
query getSearchResults {
  search(input: { query: "sales data" }) {
    searchResults {
      entity {
        ... on Dataset {
          name
          owner {
            # Path: /search/searchResults/entity/owner
            corpUser {
              displayName
            }
          }
          lineage {
            # Path: /search/searchResults/entity/lineage
            upstreamCount
            downstreamCount
            upstreamEntities {
              urn
              name
            }
          }
          schemaMetadata {
            # Path: /search/searchResults/entity/schemaMetadata
            fields {
              fieldPath
              description
            }
          }
        }
      }
    }
  }
}
```

### 경로 수준 계측이 보여주는 것

경로 수준 메트릭으로 다음을 발견할 수 있습니다:

- `/search/searchResults/entity/owner` - 50ms (빠름, 잘 캐시됨)
- `/search/searchResults/entity/lineage` - 2500ms (느림! 그래프 데이터베이스 조회 중)
- `/search/searchResults/entity/schemaMetadata` - 150ms (수용 가능)

**경로 메트릭 없이**: "검색 쿼리에 3초 소요"
**경로 메트릭으로**: "Lineage 확인이 병목 현상"

### 주요 이점

#### 1. **정밀한 최적화**

추측 대신 어떤 resolver를 최적화해야 하는지 정확히 알 수 있습니다. lineage에 더 나은 캐싱이나 페이지네이션이 필요할 수 있습니다.

#### 2. **스마트 쿼리 패턴**

다음과 같은 비용이 많이 드는 패턴 식별:

```yaml
# 일관되게 느린 경로:
/*/lineage/upstreamEntities/*
/*/siblings/*/platform
# 조치: 필드 수준 캐싱이나 지연 로딩 추가
```

#### 3. **클라이언트별 디버깅**

다른 클라이언트는 다른 필드를 요청합니다. 경로 계측으로 다음을 확인:

- 웹 UI 요청이 느림(모든 것을 요청)
- API 통합 타임아웃(심층 lineage 요청)

#### 4. **N+1 쿼리 감지**

N+1 문제를 나타내는 resolver 패턴 발견:

```
/users/0/permissions - 10ms
/users/1/permissions - 10ms
/users/2/permissions - 10ms
... (100번 더)
```

### 설정 전략

오버헤드를 최소화하기 위해 대상을 좁게 설정하세요:

```yaml
# 알려진 느린 작업에 집중
fieldLevelOperations: "searchAcrossEntities,getDataset"

# 비용이 많이 드는 resolver 경로 대상
fieldLevelPaths: "/**/lineage/**,/**/relationships/**,/**/privileges"
```

### 아키텍처

GraphQL 계측은 GraphQL Java의 계측 프레임워크를 확장하는 `GraphQLTimingInstrumentation`을 통해 구현됩니다. 제공하는 기능:

- **요청 수준 메트릭**: 전체 쿼리 성능 및 오류 추적
- **필드 수준 메트릭**: 개별 필드 resolver에 대한 상세 타이밍
- **스마트 필터링**: 특정 작업 또는 필드 경로의 구성 가능한 타겟팅
- **낮은 오버헤드**: 효율적인 계측을 통한 최소한의 성능 영향

### 수집된 메트릭

#### 요청 수준 메트릭

**메트릭: `graphql.request.duration`**

- **타입**: 백분위수가 있는 타이머(p50, p95, p99)
- **태그**:
  - `operation`: 작업 이름(예: "getSearchResultsForMultiple")
  - `operation.type`: 쿼리, 뮤테이션 또는 구독
  - `success`: 오류 존재 여부에 따라 true/false
  - `field.filtering`: 적용된 필터링 모드(DISABLED, ALL_FIELDS, BY_OPERATION, BY_PATH, BY_BOTH)
- **사용 사례**: 전체 GraphQL 성능 모니터링, 느린 작업 식별

**메트릭: `graphql.request.errors`**

- **타입**: 카운터
- **태그**:
  - `operation`: 작업 이름
  - `operation.type`: 쿼리, 뮤테이션 또는 구독
- **사용 사례**: 작업별 오류율 추적

#### 필드 수준 메트릭

**메트릭: `graphql.field.duration`**

- **타입**: 백분위수가 있는 타이머(p50, p95, p99)
- **태그**:
  - `parent.type`: GraphQL 상위 타입(예: "Dataset", "User")
  - `field`: 확인 중인 필드 이름
  - `operation`: 작업 이름 컨텍스트
  - `success`: true/false
  - `path`: 필드 경로(선택 사항, `fieldLevelPathEnabled`로 제어)
- **사용 사례**: 느린 필드 resolver 식별, 데이터 페칭 최적화

**메트릭: `graphql.field.errors`**

- **타입**: 카운터
- **태그**: 필드 duration과 동일(success 태그 제외)
- **사용 사례**: 필드별 오류 패턴 추적

**메트릭: `graphql.fields.instrumented`**

- **타입**: 카운터
- **태그**:
  - `operation`: 작업 이름
  - `filtering.mode`: 활성 필터링 모드
- **사용 사례**: 계측 범위 및 오버헤드 모니터링

### 설정 가이드

#### 마스터 제어

```yaml
graphQL:
  metrics:
    # 모든 GraphQL 메트릭의 마스터 스위치
    enabled: ${GRAPHQL_METRICS_ENABLED:true}

    # 필드 수준 resolver 메트릭 활성화
    fieldLevelEnabled: ${GRAPHQL_METRICS_FIELD_LEVEL_ENABLED:false}
```

#### 선택적 필드 계측

필드 수준 메트릭은 복잡한 쿼리에 상당한 오버헤드를 추가할 수 있습니다. DataHub는 계측할 필드를 제어하기 위한 여러 전략을 제공합니다:

##### 1. **작업 기반 필터링**

느리거나 중요한 것으로 알려진 특정 GraphQL 작업 대상:

```yaml
fieldLevelOperations: "getSearchResultsForMultiple,searchAcrossLineageStructure"
```

##### 2. **경로 기반 필터링**

경로 패턴을 사용하여 스키마의 특정 부분 계측:

```yaml
fieldLevelPaths: "/search/results/**,/user/*/permissions,/**/lineage/*"
```

**경로 패턴 구문**:

- `/user` - user 필드의 정확한 일치
- `/user/*` - user의 직접 자녀(예: `/user/name`, `/user/email`)
- `/user/**` - 임의의 깊이에서 user 필드 및 모든 하위 항목
- `/*/comments/*` - 임의의 상위 아래 comments 필드

##### 3. **복합 필터링**

작업 및 경로 필터 모두 설정된 경우 두 기준에 모두 일치하는 필드만 계측됩니다:

```yaml
# 특정 작업 내에서 검색 결과만 계측
fieldLevelOperations: "searchAcrossEntities"
fieldLevelPaths: "/searchResults/**"
```

#### 고급 옵션

```yaml
# 필드 경로를 메트릭 태그로 포함(경고: 높은 카디널리티 위험)
fieldLevelPathEnabled: false

# 간단한 속성 접근에 대한 메트릭 포함
trivialDataFetchersEnabled: false
```

### 필터링 모드 설명

계측은 가장 효율적인 필터링 모드를 자동으로 결정합니다:

1. **DISABLED**: 필드 수준 메트릭 완전 비활성화
2. **ALL_FIELDS**: 필터링 없이 모든 필드 계측(최고 오버헤드)
3. **BY_OPERATION**: 지정된 작업 내의 필드만 계측
4. **BY_PATH**: 경로 패턴과 일치하는 필드만 계측
5. **BY_BOTH**: 가장 제한적 - 작업과 경로 모두 일치해야 함

### 성능 고려 사항

#### 영향 평가

필드 수준 계측 오버헤드는 다음에 따라 달라집니다:

- **쿼리 복잡도**: 필드가 많을수록 오버헤드가 큼
- **Resolver 성능**: 빠른 resolver는 상대적으로 오버헤드가 더 높음
- **필터링 효과성**: 더 나은 타겟팅 = 더 적은 오버헤드

#### 모범 사례

1. **보수적으로 시작**: 필드 수준 메트릭 비활성화로 시작

   ```yaml
   fieldLevelEnabled: false
   ```

2. **알려진 문제 대상**: 문제가 있는 작업에 선택적으로 활성화

   ```yaml
   fieldLevelEnabled: true
   fieldLevelOperations: "slowSearchQuery,complexLineageQuery"
   ```

3. **경로 패턴을 현명하게 사용**: 비용이 많이 드는 resolver 경로에 집중

   ```yaml
   fieldLevelPaths: "/search/**,/**/lineage/**"
   ```

4. **프로덕션에서 경로 태그 사용 금지**: 높은 카디널리티 위험

   ```yaml
   fieldLevelPathEnabled: false # 이것을 false로 유지
   ```

5. **계측 오버헤드 모니터링**: `graphql.fields.instrumented` 메트릭 추적

### 설정 예시

#### 개발 환경(완전한 가시성)

```yaml
graphQL:
  metrics:
    enabled: true
    fieldLevelEnabled: true
    fieldLevelOperations: "" # 모든 작업
    fieldLevelPathEnabled: true # 디버깅을 위한 경로 포함
    trivialDataFetchersEnabled: true
```

#### 프로덕션 - 대상 모니터링

```yaml
graphQL:
  metrics:
    enabled: true
    fieldLevelEnabled: true
    fieldLevelOperations: "getSearchResultsForMultiple,searchAcrossLineage"
    fieldLevelPaths: "/search/results/*,/lineage/upstream/**,/lineage/downstream/**"
    fieldLevelPathEnabled: false
    trivialDataFetchersEnabled: false
```

#### 프로덕션 - 최소 오버헤드

```yaml
graphQL:
  metrics:
    enabled: true
    fieldLevelEnabled: false # 요청 수준 메트릭만
```

### 느린 쿼리 디버깅

GraphQL 성능 문제를 조사할 때:

1. **먼저 요청 수준 메트릭 활성화**하여 느린 작업 식별
2. **느린 작업에 대해 일시적으로 필드 수준 메트릭 활성화**:
   ```yaml
   fieldLevelOperations: "problematicQuery"
   ```
3. **필드 duration 메트릭 분석**하여 병목 현상 찾기
4. **선택적으로 경로 태그 활성화**(일시적으로) 정밀 식별:
   ```yaml
   fieldLevelPathEnabled: true # 일시적으로만!
   ```
5. **식별된 resolver 최적화**하고 상세 계측 비활성화

### 모니터링 스택과의 통합

GraphQL 메트릭은 DataHub의 모니터링 인프라와 원활하게 통합됩니다:

- **Prometheus**: `/actuator/prometheus`에서 메트릭 노출
- **Grafana**: 다음을 보여주는 대시보드 생성:
  - 작업별 요청 비율 및 지연 시간
  - 오류율 및 타입
  - 필드 resolver 성능 히트맵
  - 상위 느린 작업 및 필드

Prometheus 쿼리 예시:

```promql
# 작업별 평균 요청 duration
rate(graphql_request_duration_seconds_sum[5m])
/ rate(graphql_request_duration_seconds_count[5m])

# 필드 resolver p99 지연 시간
histogram_quantile(0.99,
  rate(graphql_field_duration_seconds_bucket[5m])
)

# 작업별 오류율
rate(graphql_request_errors_total[5m])
```

## Kafka 컨슈머 계측 (Micrometer)

### 개요

DataHub는 Micrometer 메트릭을 통해 Kafka 메시지 소비에 대한 포괄적인 계측을 제공하여 메시지 큐 지연 시간 및 컨슈머 성능의 실시간 모니터링을 가능하게 합니다. 이 계측은 데이터 최신성 SLA를 유지하고 DataHub의 이벤트 기반 아키텍처 전반에 걸쳐 처리 병목 현상을 식별하는 데 중요합니다.

### Kafka 큐 시간 모니터링이 중요한 이유

전통적인 Kafka 지연(lag) 모니터링은 "10,000개 메시지 뒤처져 있습니다"라고만 알려줍니다.
큐 시간 메트릭 없이는 "5분 데이터 최신성 SLA를 충족하고 있는가?" 또는 "어떤 컨슈머 그룹이 지연을 경험하고 있는가?"와 같은 중요한 질문에 답할 수 없습니다.

#### 실제 영향

다음 시나리오를 고려하세요:

가변 생산율:

- 아침: 초당 100개 메시지 → 1000개 메시지 지연 = 10초 된 데이터
- 저녁: 초당 10개 메시지 → 1000개 메시지 지연 = 100초 된 데이터
- 동일한 지연 수, 비즈니스 영향은 매우 다릅니다!

버스트 트래픽 패턴:

- 대량 수집이 백만 개의 메시지 백로그 생성
- 이 메시지들이 지난 한 시간(복구 가능) 것인지 24시간(SLA 위반) 것인지?

컨슈머 그룹 성능:

- 실시간 프로세서는 1분 미만의 지연 시간 필요
- 분석 컨슈머는 1시간 지연 시간 허용 가능
- 다른 그룹은 다른 모니터링 임계값 필요

### 아키텍처

Kafka 큐 시간 계측은 모든 DataHub 컨슈머에 구현됩니다:

- MetadataChangeProposals (MCP) 프로세서 - SQL entity 업데이트
  - BatchMetadataChangeProposals (MCP) 프로세서 - 대량 SQL entity 업데이트
- MetadataChangeLog (MCL) 프로세서 및 훅 - Elasticsearch 및 다운스트림 aspect 작업
- DataHubUsageEventsProcessor - 사용량 분석 이벤트
- PlatformEventProcessor - 플랫폼 작업 및 외부 컨슈머

각 컨슈머는 메시지에 내장된 타임스탬프를 사용하여 자동으로 큐 시간 메트릭을 기록합니다.

### 수집된 메트릭

#### 핵심 메트릭

메트릭: `kafka.message.queue.time`

- 타입: 구성 가능한 백분위수 및 SLO 버킷이 있는 타이머
- 단위: 밀리초
- 태그:
  - topic: Kafka 토픽 이름(예: "MetadataChangeProposal_v1")
  - consumer.group: 컨슈머 그룹 ID(예: "generic-mce-consumer")
- 사용 사례: 메시지 생성부터 SQL 트랜잭션까지 종단 간 지연 시간 모니터링

#### 통계 분포

타이머는 자동으로 다음을 추적합니다:

- 수: 처리된 총 메시지 수
- 합계: 누적 큐 시간
- 최대: 관찰된 최고 큐 시간
- 백분위수: p50, p95, p99, p99.9(구성 가능)
- SLO 버킷: 지연 시간 목표를 충족하는 메시지의 비율

#### 설정 가이드

기본 설정:

```yaml
kafka:
  consumer:
    metrics:
      # 계산할 백분위수
      percentiles: "0.5,0.95,0.99,0.999"

      # 서비스 수준 목표 버킷(초)
      slo: "300,1800,3600,10800,21600,43200" # 5분,30분,1시간,3시간,6시간,12시간

      # 예상 최대 큐 시간
      maxExpectedValue: 86400 # 24시간(초)
```

#### 주요 모니터링 패턴

SLA 준수 모니터링:

```promql
# 5분 SLA 내에 처리된 메시지 비율
sum(rate(kafka_message_queue_time_seconds_bucket{le="300"}[5m])) by (topic)
/ sum(rate(kafka_message_queue_time_seconds_count[5m])) by (topic) * 100
```

컨슈머 그룹 비교:

```promql
# 컨슈머 그룹별 P99 큐 시간
histogram_quantile(0.99,
  sum by (consumer_group, le) (
    rate(kafka_message_queue_time_seconds_bucket[5m])
  )
)
```

#### 성능 고려 사항

메트릭 카디널리티:

계측은 낮은 카디널리티를 위해 설계되었습니다:

- 두 가지 태그만 사용: `topic` 및 `consumer.group`
- 파티션 수준 태그 없음(높은 파티션 수로 인한 폭발 방지)
- 메시지 특정 태그 없음

오버헤드 평가:

- CPU 영향: 최소 - 메시지당 단일 타임스탬프 계산
- 메모리 영향: 토픽/컨슈머-그룹 조합당 약 5KB
- 네트워크 영향: 무시할 수 있음 - 메트릭이 내보내기 전에 집계됨

#### 레거시 메트릭에서 마이그레이션

새로운 Micrometer 기반 큐 시간 메트릭은 레거시 DropWizard `kafkaLag` 히스토그램과 공존합니다:

- 레거시: JMX를 통한 `kafkaLag` 히스토그램
- 신규: Micrometer를 통한 `kafka.message.queue.time` 타이머
- 마이그레이션: 전환 기간 동안 두 메트릭 모두 수집
- 향후: 레거시 메트릭은 Micrometer를 위해 사용 중단될 예정

새로운 메트릭은 다음을 제공합니다:

- 더 나은 백분위수 정확도
- SLO 버킷 추적
- 멀티 백엔드 지원
- 차원 태그

## DataHub 요청 훅 지연 시간 계측 (Micrometer)

### 개요

DataHub는 초기 요청 제출부터 post-MCL(메타데이터 변경 로그) 훅 실행까지의 지연 시간을 측정하기 위한 포괄적인 계측을 제공합니다. 이 메트릭은 Kafka 큐에서 보낸 시간과 최종 훅까지 시스템을 통해 처리하는 데 걸린 시간을 모두 포함하여 메타데이터 변경의 종단 간 처리 시간을 이해하는 데 중요합니다.

### 훅 지연 시간 모니터링이 중요한 이유

전통적인 메트릭은 개별 컴포넌트 성능만 보여줍니다. 요청 훅 지연 시간은 메타데이터 변경이 DataHub의 파이프라인을 통해 완전히 처리되는 데 얼마나 걸리는지에 대한 전체 그림을 제공합니다:

- 요청 제출: 메타데이터 변경 요청이 처음 제출되는 시점
- 큐 시간: Kafka 토픽에서 소비 대기 중에 보낸 시간
- 처리 시간: 변경이 지속되고 처리되는 데 걸리는 시간
- 훅 실행: MCL 훅의 최종 실행

이 종단 간 뷰는 다음에 필수적입니다:

- 데이터 최신성 SLA 충족
- 메타데이터 파이프라인의 병목 현상 식별
- 시스템 부하가 처리 시간에 미치는 영향 이해
- 다운스트림 시스템에 대한 적시 업데이트 보장

### 설정

훅 지연 시간 메트릭은 특정 요구 사항에 따라 세부 조정을 허용하기 위해 Kafka 컨슈머 메트릭과 별도로 설정됩니다:

```yaml
datahub:
  metrics:
    # 요청에서 post-MCL 훅 실행까지의 시간을 측정합니다
    hookLatency:
      # 지연 시간 분포에 대해 계산할 백분위수
      percentiles: "0.5,0.95,0.99,0.999"

      # 서비스 수준 목표 버킷(초)
      # 추적하려는 지연 시간 목표를 정의합니다
      slo: "300,1800,3000,10800,21600,43200" # 5분, 30분, 1시간, 3시간, 6시간, 12시간

      # 예상 최대 지연 시간(초)
      # 이 값 이상은 이상치로 간주됩니다
      maxExpectedValue: 86000 # 24시간
```

### 수집된 메트릭

#### 핵심 메트릭

메트릭: `datahub.request.hook.queue.time`

- 타입: 구성 가능한 백분위수 및 SLO 버킷이 있는 타이머
- 단위: 밀리초
- 태그:
  - `hook`: 실행 중인 MCL 훅의 이름(예: "IngestionSchedulerHook", "SiblingsHook")
- 사용 사례: 요청 제출부터 훅 실행까지의 전체 지연 시간 모니터링

#### 주요 모니터링 패턴

훅별 SLA 준수:

훅이 지연 시간 SLA를 충족하고 있는지 모니터링:

```promql
# 훅별 5분 SLA 내에 처리된 요청 비율
sum(rate(datahub_request_hook_queue_time_seconds_bucket{le="300"}[5m])) by (hook)
/ sum(rate(datahub_request_hook_queue_time_seconds_count[5m])) by (hook) * 100
```

훅 성능 비교:

지연 시간이 가장 높은 훅 식별:

```promql
# 훅별 P99 지연 시간
histogram_quantile(0.99,
  sum by (hook, le) (
    rate(datahub_request_hook_queue_time_seconds_bucket[5m])
  )
)
```

지연 시간 추이:

시간 경과에 따른 훅 지연 시간 변화 추적:

```promql
# 평균 훅 지연 시간 추이
avg by (hook) (
  rate(datahub_request_hook_queue_time_seconds_sum[5m])
  / rate(datahub_request_hook_queue_time_seconds_count[5m])
)
```

#### 구현 세부 사항

훅 지연 시간 메트릭은 각 요청의 시스템 메타데이터에 내장된 trace ID를 활용합니다:

1. Trace ID 생성: 각 요청은 내장된 타임스탬프가 있는 고유한 trace ID를 생성합니다.
1. 전파: trace ID는 시스템 메타데이터를 통해 전체 처리 파이프라인 전반에 걸쳐 흐릅니다.
1. 측정: MCL 훅이 실행될 때 메트릭은 현재 시간과 trace ID 타임스탬프 간의 시간 차이를 계산합니다.
1. 기록: 지연 시간은 훅 이름을 태그로 하는 타이머 메트릭으로 기록됩니다.

#### 성능 고려 사항

- 오버헤드: 최소 - 훅 실행당 trace ID 추출 및 시간 계산만 필요
- 카디널리티: 낮음 - 하나의 태그(훅 이름)만 있으며 일반적으로 20개 미만의 고유 값
- 정확도: 높음 - 요청에서 훅 실행까지의 실제 벽시계 시간을 측정

#### Kafka 큐 시간 메트릭과의 관계

Kafka 큐 시간 메트릭(`kafka.message.queue.time`)이 메시지가 Kafka 토픽에서 보내는 시간을 측정하는 반면, 요청 훅 지연 시간 메트릭은 전체 그림을 제공합니다:

- Kafka 큐 시간: 메시지 생성부터 소비까지의 시간
- 훅 지연 시간: 초기 요청부터 최종 훅 실행까지의 시간

이 메트릭들을 함께 사용하면 지연이 발생하는 위치를 식별하는 데 도움이 됩니다:

- Kafka 큐 시간이 높지만 훅 지연 시간이 낮음: Kafka 소비의 병목 현상
- Kafka 큐 시간이 낮지만 훅 지연 시간이 높음: 처리 또는 지속성의 병목 현상
- 둘 다 높음: 시스템 전체 성능 문제

## Aspect 크기 유효성 검사 메트릭

모든 aspect 쓰기(REST, GraphQL, MCP)에 대해 방출되어 크기를 추적하고 크기가 큰 aspect를 감지합니다.

**메트릭:**

- `aspectSizeValidation.prePatch.sizeDistribution` - 기존 aspect의 크기 분포(태그: aspectName, sizeBucket)
- `aspectSizeValidation.postPatch.sizeDistribution` - 쓰여지는 aspect의 크기 분포(태그: aspectName, sizeBucket)
- `aspectSizeValidation.prePatch.oversized` - 데이터베이스에서 발견된 크기가 큰 aspect(태그: aspectName, remediation)
- `aspectSizeValidation.postPatch.oversized` - 쓰기 중 거부된 크기가 큰 aspect(태그: aspectName, remediation)
- `aspectSizeValidation.prePatch.warning` - 데이터베이스에서 제한에 근접한 aspect(태그: aspectName)
- `aspectSizeValidation.postPatch.warning` - 쓰기 중 제한에 근접한 aspect(태그: aspectName)

**설정:**

자세한 내용은 [Aspect 크기 유효성 검사](mcp-mcl.md#aspect-size-validation)를 참조하세요.

```yaml
datahub:
  validation:
    aspectSize:
      metrics:
        sizeBuckets: [1048576, 5242880, 10485760, 15728640]
```

기본 버킷(1MB, 5MB, 10MB, 15MB)은 범위를 생성합니다: 0-1MB, 1MB-5MB, 5MB-10MB, 10MB-15MB, 15MB+

## 캐시 모니터링 (Micrometer)

### 개요

Micrometer는 캐시 구현에 대한 자동 계측을 제공하여 캐시 성능과 효율성에 대한 깊은 인사이트를 제공합니다. 이 계측은 캐싱이 쿼리 성능과 시스템 부하에 크게 영향을 미치는 DataHub에서 매우 중요합니다.

### 자동 캐시 메트릭

캐시가 Micrometer에 등록되면, 코드 변경 없이 포괄적인 메트릭이 자동으로 수집됩니다:

#### 핵심 메트릭

- **`cache.size`** (게이지) - 캐시의 현재 항목 수
- **`cache.gets`** (카운터) - 다음으로 태그된 캐시 접근 시도:
  - `result=hit` - 성공적인 캐시 히트
  - `result=miss` - 백엔드 페칭이 필요한 캐시 미스
- **`cache.puts`** (카운터) - 캐시에 추가된 항목 수
- **`cache.evictions`** (카운터) - 제거된 항목 수
- **`cache.eviction.weight`** (카운터) - 제거된 항목의 총 가중치(크기 기반 제거의 경우)

#### 파생 메트릭

Prometheus 쿼리를 사용하여 핵심 성능 지표 계산:

```promql
# 캐시 히트율(핫 캐시의 경우 >80%여야 함)
sum(rate(cache_gets_total{result="hit"}[5m])) by (cache) /
sum(rate(cache_gets_total[5m])) by (cache)

# 캐시 미스율
1 - (cache_hit_rate)

# 제거율(캐시 압력 나타냄)
rate(cache_evictions_total[5m])
```

### DataHub 캐시 설정

DataHub는 각각 자동으로 계측되는 여러 캐시 레이어를 사용합니다:

#### 1. Entity 클라이언트 캐시

```yaml
cache.client.entityClient:
  enabled: true
  maxBytes: 104857600 # 100MB
  entityAspectTTLSeconds:
    corpuser:
      corpUserInfo: 20 # 자주 변경되는 데이터에 짧은 TTL
      corpUserKey: 300 # 안정적인 데이터에 더 긴 TTL
    structuredProperty:
      propertyDefinition: 300
      structuredPropertyKey: 86400 # 매우 안정적인 데이터에 1일
```

#### 2. 사용량 통계 캐시

```yaml
cache.client.usageClient:
  enabled: true
  maxBytes: 52428800 # 50MB
  defaultTTLSeconds: 86400 # 1일
  # 비용이 많이 드는 사용량 계산 캐시
```

#### 3. 검색 및 Lineage 캐시

```yaml
cache.search.lineage:
  ttlSeconds: 86400 # 1일
```

### 모니터링 모범 사례

#### 주요 관찰 지표

1. **캐시 타입별 히트율**

   ```promql
   # 히트율이 70% 아래로 떨어지면 알림
   cache_hit_rate < 0.7
   ```

2. **메모리 압력**
   ```promql
   # puts에 비해 높은 제거율
   rate(cache_evictions_total[5m]) / rate(cache_puts_total[5m]) > 0.1
   ```

## 스레드 풀 실행자 모니터링 (Micrometer)

### 개요

Micrometer는 Java `ThreadPoolExecutor` 인스턴스를 자동으로 계측하여 동시성 병목 현상과 리소스 활용률에 대한 중요한 가시성을 제공합니다. DataHub의 동시 작업에서 이 모니터링은 부하 하에서 성능을 유지하는 데 필수적입니다.

### 자동 실행자 메트릭

#### 풀 상태 메트릭

- **`executor.pool.size`** (게이지) - 풀의 현재 스레드 수
- **`executor.pool.core`** (게이지) - 핵심(최소) 풀 크기
- **`executor.pool.max`** (게이지) - 허용된 최대 풀 크기
- **`executor.active`** (게이지) - 태스크를 적극적으로 실행 중인 스레드

#### 큐 메트릭

- **`executor.queued`** (게이지) - 큐에서 대기 중인 태스크
- **`executor.queue.remaining`** (게이지) - 사용 가능한 큐 용량

#### 성능 메트릭

- **`executor.completed`** (카운터) - 완료된 총 태스크
- **`executor.seconds`** (타이머) - 태스크 실행 시간 분포
- **`executor.rejected`** (카운터) - 포화로 인해 거부된 태스크

### DataHub 실행자 설정

#### 1. GraphQL 쿼리 실행자

```yaml
graphQL.concurrency:
  separateThreadPool: true
  corePoolSize: 20 # 기본 스레드
  maxPoolSize: 200 # 부하 하에서 확장
  keepAlive: 60 # 유휴 스레드 제거 전 초
  # 복잡한 GraphQL 쿼리 해결 처리
```

#### 2. 배치 처리 실행자

```yaml
entityClient.restli:
  get:
    batchConcurrency: 2 # 병렬 배치 프로세서
    batchQueueSize: 500 # 태스크 버퍼
    batchThreadKeepAlive: 60
  ingest:
    batchConcurrency: 2
    batchQueueSize: 500
```

#### 3. 검색 및 분석 실행자

```yaml
timeseriesAspectService.query:
  concurrency: 10 # 병렬 쿼리 스레드
  queueSize: 500 # 버퍼링된 쿼리
```

### 중요한 모니터링 패턴

#### 포화 감지

```promql
# 스레드 풀 활용률(>0.8은 압력 나타냄)
executor_active / executor_pool_size > 0.8

# 큐 채워짐(>0.7은 백프레셔 나타냄)
executor_queued / (executor_queued + executor_queue_remaining) > 0.7
```

#### 거부 및 기아

```promql
# 태스크 거부(0이어야 함)
rate(executor_rejected_total[1m]) > 0

# 스레드 기아(모든 스레드가 장시간 바쁨)
avg_over_time(executor_active[5m]) >= executor_pool_core
```

#### 성능 분석

```promql
# 평균 태스크 실행 시간
rate(executor_seconds_sum[5m]) / rate(executor_seconds_count[5m])

# 실행자별 태스크 처리량
rate(executor_completed_total[5m])
```

### 조정 가이드라인

#### 증상 및 해결책

| 증상        | 메트릭 패턴                  | 해결책                          |
| ----------- | ---------------------------- | ------------------------------- |
| 높은 지연   | `executor_queued` 상승 중    | 풀 크기 증가                    |
| 거부         | `executor_rejected` > 0      | 큐 크기 또는 풀 최대값 증가     |
| 메모리 압력 | 유휴 스레드 많음             | `keepAlive` 시간 감소           |
| CPU 낭비    | 낮은 `executor_active`       | 코어 풀 크기 감소               |

#### 용량 계획

1. **기준 측정**: 정상 부하 하에서 모니터링
2. **스트레스 테스트**: 포화 지점 식별
3. **알림 설정**:
   - 70% 활용률에서 경고
   - 90% 활용률에서 위험
4. **자동 확장**: 큐 깊이를 기반으로 동적 풀 크기 조정 고려

## 분산 추적

추적(tracing)은 여러 컴포넌트에 걸쳐 요청의 수명을 추적할 수 있게 합니다. 각 추적(trace)은 수행 중인 작업에 대한 다양한 컨텍스트와 작업 완료에 걸린 시간을 포함하는 작업 단위인 여러 span으로 구성됩니다. 추적을 보면 성능 병목 현상을 더 쉽게 식별할 수 있습니다.

[OpenTelemetry java 계측 라이브러리](https://github.com/open-telemetry/opentelemetry-java-instrumentation)를 사용하여 추적을 활성화합니다.
이 프로젝트는 java 애플리케이션에 연결되는 Java 에이전트 JAR을 제공합니다. 에이전트는 인기 있는 라이브러리에서 원격 측정을 캡처하기 위해 바이트코드를 주입합니다.

에이전트를 사용하면 다음을 수행할 수 있습니다:

1. 사용자 설정에 따라 다른 추적 도구를 플러그 앤 플레이: Jaeger, Zipkin 또는 기타 도구
2. 추가 코드 없이 Kafka, JDBC, Elasticsearch에 대한 추적 가져오기
3. 간단한 `@WithSpan` 어노테이션으로 모든 함수의 추적 추적

GMS 및 MAE/MCE 컨슈머에 대해 환경 변수 `ENABLE_OTEL`을 `true`로 설정하여 에이전트를 활성화할 수 있습니다. 예시 [docker-compose](../../docker/monitoring/docker-compose.monitoring.yml)에서 환경 변수 `OTEL_TRACES_EXPORTER`를 `jaeger`로 설정하고 `OTEL_EXPORTER_JAEGER_ENDPOINT`를 `http://jaeger-all-in-one:14250`로 설정하여 메트릭을 로컬 Jaeger 인스턴스로 내보내지만, 올바른 환경 변수를 설정하여 이 동작을 쉽게 변경할 수 있습니다. 모든 설정에 대해서는 이 [문서](https://github.com/open-telemetry/opentelemetry-java/blob/main/sdk-extensions/autoconfigure/README.md)를 참조하세요.

위 설정이 완료되면 GMS에 요청이 전송될 때 상세한 추적을 볼 수 있어야 합니다. 추적을 더 읽기 쉽게 만들기 위해 여러 곳에 `@WithSpan` 어노테이션을 추가했습니다. 선택한 추적 수집기에서 추적을 보기 시작해야 합니다. 예시 [docker-compose](../../docker/monitoring/docker-compose.monitoring.yml)는 포트 16686에 Jaeger 인스턴스를 배포합니다. http://localhost:16686에서 추적을 볼 수 있어야 합니다.

### 설정 참고사항

`OTEL_EXPORTER_OTLP_PROTOCOL`을 사용하여 설정된 `grpc` 또는 `http/protobuf`를 사용하는 것을 권장합니다. 생성된 span의 크기로 인해 `http`는 예상대로 작동하지 않을 수 있으므로 사용을 피하세요.

## Micrometer

DataHub는 Micrometer를 기본 메트릭 프레임워크로 전환하고 있으며, 이는 관측 가능성 기능의 중요한 업그레이드를 나타냅니다. Micrometer는 가장 인기 있는 모니터링 시스템을 위한 간단하고 일관된 API를 제공하는 벤더 중립적인 애플리케이션 메트릭 파사드로, 벤더 종속 없이 JVM 기반 애플리케이션 코드를 계측할 수 있게 합니다.

### 왜 Micrometer인가?

1. 네이티브 Spring 통합

   DataHub는 Spring Boot를 사용하므로 Micrometer는 다음과 원활하게 통합됩니다:

   - 일반 메트릭의 자동 설정
   - HTTP 요청, JVM, 캐시 등에 대한 내장 메트릭
   - 메트릭 노출을 위한 Spring Boot Actuator 엔드포인트
   - Spring 컴포넌트의 자동 계측

2. 멀티 백엔드 지원

   주로 JMX를 대상으로 하는 레거시 DropWizard 방식과 달리, Micrometer는 네이티브로 다음을 지원합니다:

   - Prometheus(클라우드 네이티브 배포에 권장)
   - JMX(하위 호환성)
   - StatsD
   - CloudWatch
   - Datadog
   - New Relic
   - 더 많은 기타...

3. 차원 메트릭

   Micrometer는 **레이블/태그**를 사용하는 현대적인 차원 메트릭을 지원하여 다음을 가능하게 합니다:

   - 풍부한 쿼리 및 집계 기능
   - 더 나은 카디널리티 제어
   - 더 유연한 대시보드 및 알림
   - 클라우드 네이티브 모니터링 시스템과의 자연스러운 통합

## Micrometer 전환 계획

DataHub는 DropWizard 메트릭(JMX를 통해 노출)에서 현대적인 벤더 중립적인 메트릭 파사드인 Micrometer로의 전략적 전환을 진행 중입니다.
이 전환은 기존 모니터링 인프라에 대한 하위 호환성을 유지하면서 더 나은 클라우드 네이티브 모니터링 기능을 제공하는 것을 목표로 합니다.

### 현재 상태

현재 가지고 있는 것:

- 기본 시스템: JMX를 통해 노출된 DropWizard 메트릭
- 수집 방법: Prometheus-JMX 익스포터가 JMX 메트릭 수집
- 대시보드: JMX 소스 메트릭을 소비하는 Grafana 대시보드
- 코드 패턴: 카운터 및 타이머 생성을 위한 MetricUtils 클래스
- 통합: 수동 메트릭 생성과의 기본 Spring 통합

<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/0f6ae5ae889ee4e780504ca566670867acf975ff/imgs/advanced/monitoring/monitoring_current.svg"/>
</p>

제한 사항:

- JMX 중심 방식이 모니터링 백엔드 옵션을 제한함
- 통합된 관측 가능성 없음(메트릭 및 추적에 대한 별도 계측)
- 차원 메트릭 및 태그 지원 없음
- 대부분의 컴포넌트에 수동 계측 필요
- 적절한 태그 없는 레거시 명명 규칙

### 전환 상태

구축 중인 것:

- 기본 시스템: 네이티브 Prometheus 지원이 있는 Micrometer
- 수집 방법: /actuator/prometheus를 통한 직접 Prometheus 스크래핑
- 통합 텔레메트리: 메트릭 및 추적 모두를 위한 단일 계측 지점
- 현대적인 패턴: 풍부한 태그를 가진 차원 메트릭
- 멀티 백엔드: Prometheus, StatsD, CloudWatch, Datadog 등 지원
- 자동 계측: Spring 컴포넌트에 대한 자동 메트릭

<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/0f6ae5ae889ee4e780504ca566670867acf975ff/imgs/advanced/monitoring/monitoring_transition.svg"/>
</p>

주요 결정 및 근거:

1. 이중 레지스트리 방식

   **결정:** 태그 기반 라우팅을 통해 두 시스템을 병렬로 실행

   **근거:**

   - 다운타임이나 중단 없음
   - 컴포넌트 수준에서의 점진적 마이그레이션
   - 문제 발생 시 쉬운 롤백

2. Prometheus를 기본 대상으로

   **결정:** 새 메트릭에 Prometheus 집중

   **근거:**

   - 클라우드 네이티브 애플리케이션의 업계 표준
   - 풍부한 쿼리 언어 및 에코시스템
   - 차원 메트릭에 더 적합

3. Observation API 채택

   **결정:** 새로운 계측을 위한 Observation API 촉진

   **근거:**

   - 메트릭 + 추적을 위한 단일 계측
   - 감소된 코드 복잡성
   - 텔레메트리 타입 전반의 일관된 명명

### 미래 상태

<p align="center">
  <img width="80%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/0f6ae5ae889ee4e780504ca566670867acf975ff/imgs/advanced/monitoring/monitoring_future.svg"/>
</p>

Micrometer가 완전히 채택되면, DataHub의 관측 가능성을 별도 도구 모음에서 통합 플랫폼으로 변환할 것입니다.
이는 개발자들이 기능 구축에 집중하면서 "무료로" 포괄적인 텔레메트리를 얻을 수 있음을 의미합니다.

지능적이고 적응적인 모니터링

- 동적 계측: 코드 변경 없이 특정 entity 또는 작업에 대한 상세 메트릭을 온디맨드로 활성화
- 환경 인식 메트릭: Kubernetes에서는 Prometheus, AWS에서는 CloudWatch, Azure에서는 Azure Monitor로 자동 라우팅
- 내장 SLO 추적: 서비스 수준 목표를 선언적으로 정의하고 오류 예산을 자동 추적

개발자 및 운영자 경험

- 메서드에 @Observed를 추가하면 지연 시간 백분위수, 오류율 및 분산 추적 span이 자동으로 생성됩니다.
- 모든 서비스는 즉시 황금 신호(지연 시간, 트래픽, 오류, 포화)를 노출합니다.
- 비즈니스 메트릭(entity 수집율, 검색 성능)이 시스템 메트릭과 원활하게 상관됩니다.
- 메트릭, 추적, 로그가 일관된 운영 이야기를 전달하는 자체 문서화 텔레메트리.

## DropWizard & JMX

원래 JMX에 커스텀 메트릭을 내보내기 위해 [Dropwizard Metrics](https://metrics.dropwizard.io/4.2.0/)를 사용하고, 모든 JMX 메트릭을 Prometheus로 내보내기 위해 [Prometheus-JMX exporter](https://github.com/prometheus/jmx_exporter)를 사용하기로 결정했습니다. 이를 통해 코드 베이스가 메트릭 수집 도구와 독립적이 되어, 원하는 도구를 쉽게 사용할 수 있습니다. GMS 및 MAE/MCE 컨슈머에 대해 환경 변수 `ENABLE_PROMETHEUS`를 `true`로 설정하여 에이전트를 활성화할 수 있습니다. 변수 설정을 위한 예시 [docker-compose](../../docker/monitoring/docker-compose.monitoring.yml)를 참조하세요.

예시 [docker-compose](../../docker/monitoring/docker-compose.monitoring.yml)에서 메트릭을 내보내기 위해 JMX 익스포터가 사용하는 각 컨테이너의 4318 포트에서 스크래핑하도록 prometheus를 설정했습니다. 또한 prometheus를 수신하고 유용한 대시보드를 생성하도록 grafana를 설정했습니다. 기본적으로 두 가지 대시보드를 제공합니다: [JVM 대시보드](https://grafana.com/grafana/dashboards/14845)와 DataHub 대시보드.

JVM 대시보드에서 CPU/메모리/디스크 사용량과 같은 JVM 메트릭을 기반으로 한 자세한 차트를 찾을 수 있습니다. DataHub 대시보드에서 각 엔드포인트와 Kafka 토픽을 모니터링하는 차트를 찾을 수 있습니다. 예시 구현을 사용하여 http://localhost:3001로 이동하여 Grafana 대시보드를 찾으세요! (사용자명: admin, 비밀번호: admin)

코드 베이스 내에서 다양한 메트릭을 쉽게 추적하기 위해 MetricUtils 클래스를 만들었습니다. 이 유틸 클래스는 중앙 메트릭 레지스트리를 만들고, JMX 리포터를 설정하고, 카운터 및 타이머 설정을 위한 편리한 함수를 제공합니다. 다음을 실행하여 카운터를 만들고 증가시킬 수 있습니다.

```java
metricUtils.counter(this.getClass(),"metricName").increment();
```

코드 블록을 타이밍하려면 다음을 실행하세요.

```java
try(Timer.Context ignored=metricUtils.timer(this.getClass(),"timerName").timer()){
    ...block of code
    }
```

#### docker-compose를 통한 모니터링 활성화

이 [디렉토리](https://github.com/datahub-project/datahub/tree/master/docker/monitoring)에서 모니터링 활성화를 위한 몇 가지 예시 설정을 제공합니다. 기존 컨테이너에 필요한 환경 변수를 추가하고 새 컨테이너(Jaeger, Prometheus, Grafana)를 생성하는 docker-compose 파일을 살펴보세요.

docker-compose 명령을 실행할 때 `-f <<path-to-compose-file>>`을 사용하여 위의 docker-compose를 추가할 수 있습니다.
예를 들어:

```shell
docker-compose \
  -f quickstart/docker-compose.quickstart.yml \
  -f monitoring/docker-compose.monitoring.yml \
  pull && \
docker-compose -p datahub \
  -f quickstart/docker-compose.quickstart.yml \
  -f monitoring/docker-compose.monitoring.yml \
  up
```

MONITORING=true일 때 위의 docker-compose를 추가하도록 quickstart.sh, dev.sh, dev-without-neo4j.sh를 설정했습니다. 예를 들어 `MONITORING=true ./docker/quickstart.sh`는 추적 및 메트릭 수집을 시작하는 올바른 환경 변수를 추가하고 Jaeger, Prometheus, Grafana도 배포합니다. 곧 quickstart 시 플래그로 이를 지원할 예정입니다.

## 헬스 체크 엔드포인트

DataHub 서비스의 상태를 모니터링하기 위해 `/admin` 엔드포인트를 사용할 수 있습니다.
