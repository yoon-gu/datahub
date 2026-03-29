---
title: Remote Executor 모니터링
description: Remote Executor 상태와 성능을 모니터링하고 관찰하는 방법 알아보기
---

import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Remote Executor 모니터링

<FeatureAvailability saasOnly />

## 개요

이 가이드는 Remote Executor 배포를 모니터링하는 모든 측면을 다룹니다:

1. 파일 기반 상태 확인
2. UI 기반 상태 모니터링
3. 고급 Prometheus 메트릭 구성

## 상태 확인

### 파일 기반 상태 확인

Remote Executor는 컨테이너 플랫폼에서 모니터링할 수 있는 파일 기반 상태 확인을 사용합니다:

- Liveness: `/tmp/worker_liveness_heartbeat`
- Readiness: `/tmp/worker_readiness_heartbeat`

이 파일들은 Remote Executor가 자동으로 관리하며 Kubernetes liveness/readiness probe 또는 ECS 상태 확인에 사용할 수 있습니다.

### UI 기반 상태 모니터링

DataHub UI에서 직접 Remote Executor 상태를 모니터링하세요:

1. **Data Sources > Executors**로 이동합니다.
2. 각 Pool에 대한 상태 정보를 확인합니다:
   - 활성 Remote Executor 인스턴스
   - 각 executor의 마지막 보고 시간
   - 상태 (Active/Stale)
   - 현재 실행 중인 Ingestion 작업 및 세부 정보

<p align="center">
  <img width="90%"  src="https://github.com/datahub-project/static-assets/blob/main/imgs/remote-executor/remote-executor-view-running-tasks.png?raw=true"/>
</p>

## 고급: Prometheus 메트릭

Remote Executor는 Prometheus/OpenMetrics 형식으로 포트 `9087/tcp`에서 메트릭을 노출합니다. 메트릭은 Prometheus 스택 또는 DataDog과 같은 호환 에이전트를 통해 수집할 수 있습니다.

### 메트릭 카테고리

1. **Ingestion 메트릭**

   - `datahub_executor_worker_ingestion_requests` - 총 수신된 작업 수
   - `datahub_executor_worker_ingestion_errors` - 실패한 작업 수 (v0.3.9+)

2. **리소스 메트릭** (v0.3.9+)
   - 메모리: `datahub_executor_memory_*`
   - CPU: `datahub_executor_cpu_*`
   - 디스크: `datahub_executor_disk_*`
   - 네트워크: `datahub_executor_net_*`

### Prometheus 구성

Prometheus에서 Remote Executor 메트릭 수집을 허용하는 ServiceMonitor 리소스 예시:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
  name: datahub-remote-executor
spec:
  endpoints:
    - port: metrics
  selector:
    matchLabels:
      app.kubernetes.io/name: datahub-remote-executor
```

### 사용 가능한 메트릭 확인

1. 메트릭 엔드포인트를 직접 확인합니다:

   ```bash
   curl http://your-executor:9087/metrics
   ```

2. Prometheus UI에서 주석 읽기
3. 모니터링 시스템에서 `datahub_executor_*` 검색

:::note
플랫폼별 메트릭(예: 컨테이너 재시작)은 네이티브 도구를 통해 모니터링해야 합니다(ECS의 경우 CloudWatch, K8s의 경우 Kubernetes 메트릭).
:::
