# Dashboard Entity

Dashboard entity는 BI 도구(예: Looker, Tableau, PowerBI)의 시각화 및 보고서 모음을 나타냅니다. 이 가이드는 SDK V2의 포괄적인 dashboard 작업을 다룹니다.

## Dashboard 생성

### 최소 Dashboard

tool과 id만 필수입니다:

```java
Dashboard dashboard = Dashboard.builder()
    .tool("looker")
    .id("my_sales_dashboard")
    .build();
```

### 메타데이터 포함

구성 시 제목과 설명 추가:

```java
Dashboard dashboard = Dashboard.builder()
    .tool("tableau")
    .id("executive_dashboard")
    .title("Executive KPI Dashboard")
    .description("Real-time executive dashboard showing key business metrics")
    .build();
```

### 커스텀 속성 포함

빌더에 커스텀 속성 포함:

```java
Map<String, String> props = new HashMap<>();
props.put("team", "business-intelligence");
props.put("refresh_schedule", "hourly");

Dashboard dashboard = Dashboard.builder()
    .tool("powerbi")
    .id("sales_dashboard")
    .title("Sales Performance")
    .customProperties(props)
    .build();
```

## URN 구성

Dashboard URN은 다음 패턴을 따릅니다:

```
urn:li:dashboard:({tool},{id})
```

**자동 URN 생성:**

```java
Dashboard dashboard = Dashboard.builder()
    .tool("looker")
    .id("regional_sales")
    .build();

DashboardUrn urn = dashboard.getDashboardUrn();
// urn:li:dashboard:(looker,regional_sales)
```

## 지원되는 BI 도구

일반적인 도구 식별자:

- `looker` - Looker
- `tableau` - Tableau
- `powerbi` - Power BI
- `superset` - Apache Superset
- `metabase` - Metabase
- `redash` - Redash
- `mode` - Mode Analytics
- `quicksight` - Amazon QuickSight
- `thoughtspot` - ThoughtSpot

## 태그

### 태그 추가

```java
// Simple tag name (auto-prefixed)
dashboard.addTag("executive");
// Creates: urn:li:tag:executive

// Full tag URN
dashboard.addTag("urn:li:tag:production");
```

### 태그 제거

```java
dashboard.removeTag("executive");
dashboard.removeTag("urn:li:tag:production");
```

### 태그 체이닝

```java
dashboard.addTag("executive")
         .addTag("real-time")
         .addTag("kpi");
```

## 소유자

### 소유자 추가

```java
import com.linkedin.common.OwnershipType;

// Business owner
dashboard.addOwner(
    "urn:li:corpuser:john_doe",
    OwnershipType.BUSINESS_OWNER
);

// Technical owner
dashboard.addOwner(
    "urn:li:corpuser:bi_team",
    OwnershipType.TECHNICAL_OWNER
);

// Data steward
dashboard.addOwner(
    "urn:li:corpuser:governance",
    OwnershipType.DATA_STEWARD
);
```

### 소유자 제거

```java
dashboard.removeOwner("urn:li:corpuser:john_doe");
```

### 소유권 타입

사용 가능한 소유권 타입:

- `BUSINESS_OWNER` - 비즈니스 이해관계자
- `TECHNICAL_OWNER` - 기술적 구현을 유지 관리
- `DATA_STEWARD` - 데이터 품질 및 규정 준수 관리
- `DATAOWNER` - 일반 데이터 소유자
- `DEVELOPER` - 소프트웨어 개발자
- `PRODUCER` - Dashboard 생산자/제작자
- `CONSUMER` - Dashboard 소비자
- `STAKEHOLDER` - 기타 이해관계자

## Glossary Terms

### 용어 추가

```java
dashboard.addTerm("urn:li:glossaryTerm:ExecutiveMetrics");
dashboard.addTerm("urn:li:glossaryTerm:BusinessIntelligence");
```

### 용어 제거

```java
dashboard.removeTerm("urn:li:glossaryTerm:ExecutiveMetrics");
```

### 용어 체이닝

```java
dashboard.addTerm("urn:li:glossaryTerm:KeyPerformanceIndicator")
         .addTerm("urn:li:glossaryTerm:SalesMetrics")
         .addTerm("urn:li:glossaryTerm:RealTimeData");
```

## 도메인

### 도메인 설정

```java
dashboard.setDomain("urn:li:domain:Sales");
```

### 도메인 제거

```java
// Remove a specific domain
dashboard.removeDomain("urn:li:domain:Sales");

// Or clear all domains
dashboard.clearDomains();
```

## 커스텀 속성

### 개별 속성 추가

```java
dashboard.addCustomProperty("team", "sales-operations");
dashboard.addCustomProperty("refresh_schedule", "hourly");
dashboard.addCustomProperty("data_source", "snowflake");
```

### 모든 속성 설정

모든 커스텀 속성 교체:

```java
Map<String, String> properties = new HashMap<>();
properties.put("team", "business-intelligence");
properties.put("refresh_schedule", "real-time");
properties.put("access_level", "executive");

dashboard.setCustomProperties(properties);
```

### 속성 제거

```java
dashboard.removeCustomProperty("refresh_schedule");
```

## Dashboard 메타데이터 읽기

### 제목 가져오기

```java
String title = dashboard.getTitle();
```

### 설명 가져오기

```java
String description = dashboard.getDescription();
```

## Lineage 작업

Dashboard lineage는 dashboard로 유입되는 데이터 소스(dataset)를 나타냅니다. 이를 통해 dashboard에서 소스 dataset으로의 업스트림 lineage 관계가 생성됩니다.

### 입력 Dataset 추가

Dataset을 하나씩 추가:

```java
// Using DatasetUrn
DatasetUrn dataset = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,sales.orders,PROD)"
);
dashboard.addInputDataset(dataset);

// Using string URN
dashboard.addInputDataset(
    "urn:li:dataset:(urn:li:dataPlatform:bigquery,marketing.campaigns,PROD)"
);
```

### 입력 Dataset 설정

모든 입력 dataset을 한 번에 교체:

```java
List<DatasetUrn> datasets = Arrays.asList(
    DatasetUrn.createFromString(
        "urn:li:dataset:(urn:li:dataPlatform:snowflake,sales.orders,PROD)"
    ),
    DatasetUrn.createFromString(
        "urn:li:dataset:(urn:li:dataPlatform:snowflake,sales.customers,PROD)"
    )
);

dashboard.setInputDatasets(datasets);
```

### 입력 Dataset 제거

```java
// Using DatasetUrn
DatasetUrn dataset = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,sales.orders,PROD)"
);
dashboard.removeInputDataset(dataset);

// Using string URN
dashboard.removeInputDataset(
    "urn:li:dataset:(urn:li:dataPlatform:bigquery,marketing.campaigns,PROD)"
);
```

### 입력 Dataset 가져오기

모든 입력 dataset 검색:

```java
List<DatasetUrn> inputDatasets = dashboard.getInputDatasets();
for (DatasetUrn dataset : inputDatasets) {
    System.out.println("Dataset: " + dataset);
}
```

### Lineage 체이닝

```java
dashboard.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,sales.orders,PROD)")
         .addInputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,sales.customers,PROD)")
         .addInputDataset("urn:li:dataset:(urn:li:dataPlatform:salesforce,Account,PROD)");
```

## Chart 관계

Chart 관계는 dashboard에 임베드된 시각화를 나타냅니다. 이를 통해 dashboard와 chart 사이에 "포함" 관계가 생성됩니다.

### Chart 추가

Chart를 하나씩 추가:

```java
// Using ChartUrn
ChartUrn chart = new ChartUrn("tableau", "revenue_chart");
dashboard.addChart(chart);

// Using string URN
dashboard.addChart("urn:li:chart:(looker,sales_performance_chart)");
```

### Chart 설정

모든 chart를 한 번에 교체:

```java
List<ChartUrn> charts = Arrays.asList(
    new ChartUrn("tableau", "revenue_chart"),
    new ChartUrn("tableau", "customer_satisfaction_chart"),
    new ChartUrn("tableau", "regional_breakdown_chart")
);

dashboard.setCharts(charts);
```

### Chart 제거

```java
// Using ChartUrn
ChartUrn chart = new ChartUrn("tableau", "revenue_chart");
dashboard.removeChart(chart);

// Using string URN
dashboard.removeChart("urn:li:chart:(looker,sales_performance_chart)");
```

### Chart 가져오기

모든 chart 검색:

```java
List<ChartUrn> charts = dashboard.getCharts();
for (ChartUrn chart : charts) {
    System.out.println("Chart: " + chart);
}
```

### Chart 체이닝

```java
dashboard.addChart(new ChartUrn("looker", "revenue_chart"))
         .addChart(new ChartUrn("looker", "customer_chart"))
         .addChart(new ChartUrn("looker", "product_chart"));
```

## Dashboard별 속성

### Dashboard URL

기본 BI 도구에서 dashboard에 대한 직접 링크 설정:

```java
// Set dashboard URL
dashboard.setDashboardUrl("https://tableau.company.com/views/sales-dashboard");

// Get dashboard URL
String url = dashboard.getDashboardUrl();
```

### 마지막 새로 고침

Dashboard 데이터가 마지막으로 업데이트된 시간 추적:

```java
// Set last refreshed timestamp (milliseconds since epoch)
long currentTime = System.currentTimeMillis();
dashboard.setLastRefreshed(currentTime);

// Get last refreshed timestamp
Long lastRefreshed = dashboard.getLastRefreshed();
if (lastRefreshed != null) {
    System.out.println("Last refreshed at: " + new Date(lastRefreshed));
}
```

### 결합된 Dashboard 속성

```java
dashboard.setDashboardUrl("https://looker.company.com/dashboards/executive")
         .setLastRefreshed(System.currentTimeMillis());
```

## 완전한 예제

```java
import datahub.client.v2.DataHubClientV2;
import datahub.client.v2.entity.Dashboard;
import com.linkedin.common.OwnershipType;
import java.io.IOException;
import java.util.concurrent.ExecutionException;

public class DashboardExample {
    public static void main(String[] args) {
        // Create client
        DataHubClientV2 client = DataHubClientV2.builder()
            .server("http://localhost:8080")
            .build();

        try {
            // Build dashboard with all metadata
            Dashboard dashboard = Dashboard.builder()
                .tool("looker")
                .id("sales_performance_dashboard")
                .title("Sales Performance Dashboard")
                .description("Executive dashboard showing key sales metrics and regional performance")
                .build();

            // Add tags
            dashboard.addTag("executive")
                     .addTag("sales")
                     .addTag("production");

            // Add owners
            dashboard.addOwner("urn:li:corpuser:sales_team", OwnershipType.BUSINESS_OWNER)
                     .addOwner("urn:li:corpuser:bi_team", OwnershipType.TECHNICAL_OWNER);

            // Add glossary terms
            dashboard.addTerm("urn:li:glossaryTerm:SalesMetrics")
                     .addTerm("urn:li:glossaryTerm:ExecutiveDashboard");

            // Set domain
            dashboard.setDomain("urn:li:domain:Sales");

            // Add custom properties
            dashboard.addCustomProperty("team", "sales-operations")
                     .addCustomProperty("refresh_schedule", "hourly")
                     .addCustomProperty("data_source", "snowflake");

            // Upsert to DataHub
            client.entities().upsert(dashboard);

            System.out.println("Successfully created dashboard: " + dashboard.getUrn());

        } catch (IOException | ExecutionException | InterruptedException e) {
            e.printStackTrace();
        } finally {
            try {
                client.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
```

## 기존 Dashboard 업데이트

### 로드 및 수정

```java
// Load existing dashboard
DashboardUrn urn = new DashboardUrn("looker", "my_dashboard");
Dashboard dashboard = client.entities().get(urn);

// Add new metadata (creates patches)
dashboard.addTag("new-tag")
         .addOwner("urn:li:corpuser:new_owner", OwnershipType.TECHNICAL_OWNER);

// Apply patches
client.entities().update(dashboard);
```

### 점진적 업데이트

```java
// Just add what you need
dashboard.addTag("real-time");
client.entities().update(dashboard);

// Later, add more
dashboard.addCustomProperty("updated_at", String.valueOf(System.currentTimeMillis()));
client.entities().update(dashboard);
```

## 빌더 옵션 참조

| 메서드                  | 필수 여부 | 설명                                    |
| ----------------------- | -------- | ---------------------------------------------- |
| `tool(String)`          | ✅ 예   | BI 도구 식별자 (예: "looker", "tableau") |
| `id(String)`            | ✅ 예   | 도구 내 dashboard 식별자           |
| `title(String)`         | 아니요       | Dashboard 제목                                |
| `description(String)`   | 아니요       | Dashboard 설명                          |
| `customProperties(Map)` | 아니요       | 커스텀 키-값 속성의 맵             |

## Patch 기반 작업

Dashboard는 메타데이터 작업에 patch 기반 업데이트를 사용합니다. `addTag()`, `addOwner()` 등의 모든 메서드는 `upsert()` 또는 `update()`가 호출될 때까지 축적되는 patches를 생성합니다.

**이점:**

- **효율적**: 여러 작업이 더 적은 API 호출로 배치됨
- **원자적**: 모든 변경 사항이 함께 성공하거나 실패
- **점진적**: 지정된 필드만 수정되고 나머지는 변경되지 않음

**예제:**

```java
Dashboard dashboard = Dashboard.builder()
    .tool("tableau")
    .id("sales_dashboard")
    .build();

// These create patches (no API calls yet)
dashboard.addTag("production");
dashboard.addOwner("urn:li:corpuser:owner", OwnershipType.BUSINESS_OWNER);
dashboard.setDomain("urn:li:domain:Sales");

// Single API call emits all patches
client.entities().upsert(dashboard);
```

## 공통 패턴

### 여러 Dashboard 생성

```java
List<String> dashboardIds = Arrays.asList("dashboard1", "dashboard2", "dashboard3");

for (String dashboardId : dashboardIds) {
    Dashboard dashboard = Dashboard.builder()
        .tool("looker")
        .id(dashboardId)
        .title("Dashboard " + dashboardId)
        .build();

    dashboard.addTag("auto-generated")
             .addCustomProperty("created_by", "sync_job");

    client.entities().upsert(dashboard);
}
```

### 배치 메타데이터 추가

```java
Dashboard dashboard = Dashboard.builder()
    .tool("tableau")
    .id("executive_dashboard")
    .build();

List<String> tags = Arrays.asList("executive", "kpi", "real-time", "production");
tags.forEach(dashboard::addTag);

client.entities().upsert(dashboard);  // Emits all tags in one call
```

### 조건부 메타데이터

```java
if (isExecutiveDashboard(dashboard)) {
    dashboard.addTag("executive")
             .addTerm("urn:li:glossaryTerm:ExecutiveMetrics");
}

if (requiresGovernance(dashboard)) {
    dashboard.addOwner("urn:li:corpuser:governance_team", OwnershipType.DATA_STEWARD);
}
```

### 전체 Lineage 컨텍스트를 가진 Dashboard

```java
// Create dashboard with rich metadata
Dashboard dashboard = Dashboard.builder()
    .tool("looker")
    .id("customer_360_dashboard")
    .title("Customer 360 Dashboard")
    .description("Comprehensive customer analytics dashboard")
    .build();

// Add business context
dashboard.addTerm("urn:li:glossaryTerm:CustomerAnalytics")
         .addTerm("urn:li:glossaryTerm:BusinessIntelligence")
         .setDomain("urn:li:domain:Customer");

// Add input datasets for lineage
dashboard.addInputDataset("urn:li:dataset:(urn:li:dataPlatform:snowflake,customer.profile,PROD)")
         .addInputDataset("urn:li:dataset:(urn:li:dataPlatform:salesforce,Account,PROD)")
         .addInputDataset("urn:li:dataset:(urn:li:dataPlatform:zendesk,Tickets,PROD)");

// Add embedded charts
dashboard.addChart(new ChartUrn("looker", "customer_segmentation_chart"))
         .addChart(new ChartUrn("looker", "lifetime_value_chart"))
         .addChart(new ChartUrn("looker", "support_tickets_chart"));

// Add operational metadata
dashboard.addCustomProperty("data_sources", "snowflake,salesforce,zendesk")
         .addCustomProperty("refresh_schedule", "every_15_minutes")
         .addCustomProperty("sla_tier", "tier1")
         .addCustomProperty("business_criticality", "high");

// Set dashboard properties
dashboard.setDashboardUrl("https://looker.company.com/dashboards/customer-360")
         .setLastRefreshed(System.currentTimeMillis());

// Add ownership and governance
dashboard.addOwner("urn:li:corpuser:product_team", OwnershipType.BUSINESS_OWNER)
         .addOwner("urn:li:corpuser:bi_team", OwnershipType.TECHNICAL_OWNER)
         .addTag("production")
         .addTag("customer-facing");

client.entities().upsert(dashboard);
```

## Chart Entity와의 비교

Dashboard와 Chart는 유사하지만 다른 목적을 가집니다:

| 기능          | Dashboard                     | Chart                     |
| ---------------- | ----------------------------- | ------------------------- |
| 목적          | 시각화 모음  | 단일 시각화      |
| URN 패턴      | `(tool,id)`                   | `(tool,id)`               |
| Patch 작업 | ✅ 완전 지원               | ✅ 완전 지원           |
| 일반적인 사용 사례 | 임원 대시보드, 보고서 | 개별 그래프, 차트 |

## 다음 단계

- **[Chart Entity 가이드](./chart-entity.md)** - chart entity 작업
- **[Dataset Entity 가이드](./dataset-entity.md)** - dataset entity 작업
- **[Patch 작업](./patch-operations.md)** - patches에 대한 심층 분석
- **[마이그레이션 가이드](./migration-from-v1.md)** - V1에서 업그레이드

## 예제

### 기본 Dashboard 생성

```java
{{ inline /metadata-integration/java/examples/src/main/java/io/datahubproject/examples/v2/DashboardCreateExample.java show_path_as_comment }}
```

### 메타데이터가 포함된 포괄적인 Dashboard

```java
{{ inline /metadata-integration/java/examples/src/main/java/io/datahubproject/examples/v2/DashboardFullExample.java show_path_as_comment }}
```

### Lineage 및 관계가 있는 Dashboard

```java
{{ inline /metadata-integration/java/examples/src/main/java/io/datahubproject/examples/v2/DashboardLineageExample.java show_path_as_comment }}
```
