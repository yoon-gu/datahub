---
description: 이 페이지에서는 Assertion Notes 사용 방법에 대한 개요를 제공합니다
---

import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Assertion Notes

<FeatureAvailability saasOnly />

> **Assertion Notes** 기능은 DataHub Cloud의 **DataHub Cloud Observe** 모듈의 일부로 제공됩니다.
> **DataHub Cloud Observe**에 대해 더 알아보거나 체험해 보고 싶다면 [웹사이트를 방문](https://datahub.com/products/data-observability/)하세요.

## 소개

Assertion Notes 기능은 두 가지 핵심 사용 사례를 해결하는 것을 목표로 합니다:

1. 엔지니어가 데이터 품질 실패를 해결하는 데 유용한 팁 제공
2. 특정 검사의 목적 및 실패 시 영향 문서화; 예를 들어 일부 검사는 파이프라인을 차단할 수 있습니다.

### 문제 해결을 위한 용도

대규모 데이터 환경에서 데이터 품질 커버리지를 확장할 때, assertion 실패를 해결하는 엔지니어가 검사를 생성한 사람과 다른 경우가 종종 있습니다.
검사가 실패했을 때 문제를 해결하는 방법에 대한 지침이나 컨텍스트가 있는 메모를 제공하는 것이 유용한 경우가 많습니다.

- 검사가 수동으로 설정된 경우, 생성자가 향후 온콜 엔지니어를 위해 메모를 추가하는 것이 가치 있을 수 있습니다
- AI 검사였다면, 실패를 처음 조사한 사람이 수정 방법을 문서화하고 싶을 수 있습니다.

### 문서화를 위한 용도

Assertions에 메모를 추가하는 것은 Assertions를 문서화하는 데 유용합니다. 이는 특히 쿼리 구문에서 논리를 이해하기 어려울 수 있는 Custom SQL 검사에 특히 관련이 있습니다. notes 탭에 문서를 추가하면 다른 사람들이 무엇이 모니터링되고 있는지, 실패 시 문제를 해결하는 방법을 정확히 이해할 수 있습니다.

<iframe width="516" height="342" src="https://www.loom.com/embed/a6cb07d33e8440acafacea381912f904?sid=32918cd5-9ebf-4aa0-90bc-37fae84d1841" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>
