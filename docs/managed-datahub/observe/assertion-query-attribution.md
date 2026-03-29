---
description: 비용을 더 잘 추적하기 위해 DataHub Cloud Observe에 쿼리를 귀속시키는 방법을 알아보세요
---

import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Assertion 쿼리 귀속

<FeatureAvailability saasOnly />

Freshness 및 Volume과 같은 특정 Assertions의 경우 DataHub는 해당 assertion이 통과했는지 실패했는지 결정하기 위해 데이터 웨어하우스(예: Snowflake)에 쿼리를 실행합니다. 설정한 assertions의 수에 따라 매일 웨어하우스에 많은 추가 쿼리가 발생할 수 있습니다. DataHub Cloud Observe에서 들어오는 모든 쿼리를 추적하고 이해하기 위해 발행된 쿼리에 태깅이 추가되었습니다.

## SQL 주석

모든 플랫폼에서, 쿼리 소스가 DataHub임을 나타내고 쿼리를 발행한 assertion의 URN을 포함하는 SQL 주석이 모든 쿼리 상단에 추가됩니다. 예:

```sql
/* query_source=datahub_observe assertion_urn=urn:li:assertion:507e3dec-8fed-4809-9cdd-cf2a4a06a249 */
SELECT *
FROM users
```

## Snowflake 쿼리 태그

Snowflake에 대해 발행된 쿼리의 경우 SQL 구문에 [Snowflake Query Tag](https://select.dev/posts/snowflake-query-tags)가 추가됩니다.

```sql
ALTER SESSION SET query_tag='{"query_source": "datahub_observe", "assertion_urn": "urn:li:assertion:507e3dec-8fed-4809-9cdd-cf2a4a06a249"}'
```

## BigQuery 작업 레이블

BigQuery는 청구 데이터에 자동으로 포함되는 [작업 레이블](https://docs.cloud.google.com/bigquery/docs/adding-labels#job-label)을 통해 귀속을 지원합니다. 안타깝게도 레이블의 길이 및 문자 제한으로 인해 assertion URN은 작업 레이블에 포함되지 않습니다.

```python
labels = {"datahub_observe": "true"}
```
