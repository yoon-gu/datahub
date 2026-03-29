# Chart Entity

Chart entity는 BI 도구(예: Looker, Tableau, Superset)의 시각화 및 보고서를 나타냅니다. 이 가이드는 SDK V2의 chart 작업을 다룹니다.

## Chart 생성

### 최소 Chart

tool과 id만 필수입니다:

```java
Chart chart = Chart.builder()
    .tool("looker")
    .id("my_sales_chart")
    .build();
```

### 메타데이터 포함

제목, 설명 및 커스텀 속성 추가:

```java
Chart chart = Chart.builder()
    .tool("tableau")
    .id("sales_dashboard_chart_1")
    .title("Sales Performance by Region")
    .description("Monthly sales broken down by geographic region")
    .build();
```

### 커스텀 속성 포함

```java
Map<String, String> properties = new HashMap<>();
properties.put("dashboard", "executive_dashboard");
properties.put("refresh_schedule", "hourly");

Chart chart = Chart.builder()
    .tool("looker")
    .id("revenue_chart")
    .title("Revenue Trends")
    .customProperties(properties)
    .build();
```

## URN 구성

Chart URN은 다음 패턴을 따릅니다:

```
urn:li:chart:({tool},{id})
```

**예제:**

```java
Chart chart = Chart.builder()
    .tool("looker")
    .id("my_chart")
    .build();

ChartUrn urn = chart.getChartUrn();
// urn:li:chart:(looker,my_chart)
```

## 지원되는 BI 도구

일반적인 도구 식별자:

- `looker` - Looker
- `tableau` - Tableau
- `superset` - Apache Superset
- `powerbi` - Power BI
- `metabase` - Metabase
- `redash` - Redash
- `mode` - Mode Analytics

## Chart 작업

### 태그 추가

chart를 분류하고 분류하기 위한 태그 추가:

```java
// Simple tag (automatically adds "urn:li:tag:" prefix)
chart.addTag("pii");
chart.addTag("financial");

// Or use full URN
chart.addTag("urn:li:tag:production");
```

### 소유자 관리

다양한 소유권 타입으로 소유자 추가:

```java
import com.linkedin.common.OwnershipType;

// Add technical owner
chart.addOwner("urn:li:corpuser:data_team", OwnershipType.TECHNICAL_OWNER);

// Add business owner
chart.addOwner("urn:li:corpuser:sales_team", OwnershipType.BUSINESS_OWNER);

// Add data steward
chart.addOwner("urn:li:corpuser:compliance_team", OwnershipType.DATA_STEWARD);

// Remove an owner
chart.removeOwner("urn:li:corpuser:old_owner");
```

### Glossary Terms 추가

chart를 비즈니스 glossary 용어와 연결:

```java
chart.addTerm("urn:li:glossaryTerm:SalesMetrics");
chart.addTerm("urn:li:glossaryTerm:QuarterlyReporting");

// Remove a term
chart.removeTerm("urn:li:glossaryTerm:OldTerm");
```

### 도메인 설정

chart를 도메인으로 구성:

```java
// Set domain
chart.setDomain("urn:li:domain:Sales");

// Remove domain
chart.setDomain(null);
// or
chart.removeDomain();
```

### 설명 및 제목 설정

patch 기반 업데이트를 사용하여 chart 설명 및 제목 업데이트:

```java
chart.setDescription("Updated chart description");
chart.setTitle("New Chart Title");
```

### 커스텀 속성 관리

커스텀 속성 추가, 업데이트 또는 제거:

```java
// Add individual properties
chart.addCustomProperty("refresh_schedule", "hourly");
chart.addCustomProperty("chart_type", "bar");

// Set all properties at once (replaces existing)
Map<String, String> props = new HashMap<>();
props.put("dashboard_url", "https://dashboard.example.com");
props.put("author", "data_team");
chart.setCustomProperties(props);

// Remove a property
chart.removeCustomProperty("old_property");
```

## Lineage 작업

Chart lineage는 chart와 chart가 소비하는 dataset 사이의 데이터 흐름 관계를 정의합니다. 이는 영향 분석, 데이터 거버넌스 및 데이터 의존성 이해에 필수적입니다.

### 입력 Dataset 설정

chart가 소비하는 dataset 정의:

```java
import com.linkedin.common.urn.DatasetUrn;
import java.util.Arrays;

// Create dataset URNs
DatasetUrn salesDataset = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,sales.transactions,PROD)");
DatasetUrn customerDataset = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,sales.customers,PROD)");

// Set all input datasets at once (replaces existing)
chart.setInputDatasets(Arrays.asList(salesDataset, customerDataset));
```

### 개별 입력 Dataset 추가

Dataset을 점진적으로 추가:

```java
// Add datasets one at a time
chart.addInputDataset(salesDataset);
chart.addInputDataset(customerDataset);

// This pattern is useful when:
// - Building lineage incrementally
// - Discovering datasets during chart analysis
// - Adding new data sources to existing chart
```

### 입력 Dataset 제거

더 이상 소비되지 않는 dataset 제거:

```java
DatasetUrn legacyDataset = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:postgres,legacy.old_table,PROD)");

// Remove specific dataset from lineage
chart.removeInputDataset(legacyDataset);
```

### 입력 Dataset 검색

chart가 소비하는 dataset 목록 가져오기:

```java
// Load chart from DataHub
ChartUrn chartUrn = new ChartUrn("looker", "my_chart");
Chart chart = client.entities().get(chartUrn);

// Get all input datasets
List<DatasetUrn> inputDatasets = chart.getInputDatasets();
System.out.println("Chart consumes " + inputDatasets.size() + " datasets:");
for (DatasetUrn dataset : inputDatasets) {
    System.out.println("  - " + dataset);
}
```

### 완전한 Lineage 예제

```java
// Create chart with comprehensive lineage
Chart salesChart = Chart.builder()
    .tool("tableau")
    .id("sales_dashboard_chart")
    .title("Sales Performance")
    .build();

// Define input datasets
DatasetUrn transactions = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,sales.transactions,PROD)");
DatasetUrn customers = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,sales.customers,PROD)");
DatasetUrn products = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,sales.products,PROD)");

// Set lineage
salesChart.setInputDatasets(Arrays.asList(transactions, customers, products));

// Add metadata
salesChart.addTag("sales")
         .addOwner("urn:li:corpuser:data_team", OwnershipType.TECHNICAL_OWNER)
         .setDomain("urn:li:domain:Sales");

// Save to DataHub
client.entities().upsert(salesChart);
```

## Chart별 속성

Chart에는 기본 메타데이터를 넘어선 여러 전문화된 속성이 있습니다:

### Chart 타입

시각화 타입 설정:

```java
// Available types: BAR, LINE, PIE, TABLE, TEXT, BOXPLOT, AREA, SCATTER
chart.setChartType("BAR");

// Get chart type
String chartType = chart.getChartType();
```

### 접근 수준

Chart 가시성 제어:

```java
// Available levels: PUBLIC, PRIVATE
chart.setAccess("PUBLIC");

// Get access level
String access = chart.getAccess();
```

### 외부 및 Chart URL

Chart에 접근하기 위한 URL 설정:

```java
// External URL - link to view chart in source BI tool
chart.setExternalUrl("https://looker.company.com/dashboards/123");

// Chart URL - direct URL to chart (may be different from external URL)
chart.setChartUrl("https://looker.company.com/embed/charts/456");

// Get URLs
String externalUrl = chart.getExternalUrl();
String chartUrl = chart.getChartUrl();
```

### 마지막 새로 고침 타임스탬프

Chart 데이터가 마지막으로 업데이트된 시간 추적:

```java
// Set timestamp (milliseconds since epoch)
long currentTime = System.currentTimeMillis();
chart.setLastRefreshed(currentTime);

// Or use a specific time
long specificTime = Instant.parse("2025-10-29T10:00:00Z").toEpochMilli();
chart.setLastRefreshed(specificTime);

// Get last refreshed time
Long lastRefreshed = chart.getLastRefreshed();
if (lastRefreshed != null) {
    Instant refreshTime = Instant.ofEpochMilli(lastRefreshed);
    System.out.println("Last refreshed: " + refreshTime);
}
```

### 완전한 속성 예제

```java
import java.time.Instant;

Chart chart = Chart.builder()
    .tool("looker")
    .id("sales_performance")
    .title("Sales Performance Dashboard")
    .build();

// Set all chart-specific properties
chart.setChartType("BAR")
     .setAccess("PUBLIC")
     .setExternalUrl("https://looker.company.com/dashboards/sales")
     .setChartUrl("https://looker.company.com/embed/charts/sales_performance")
     .setLastRefreshed(System.currentTimeMillis());

// Set lineage
DatasetUrn salesDataset = DatasetUrn.createFromString(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,sales.transactions,PROD)");
chart.addInputDataset(salesDataset);

// Add metadata
chart.addTag("sales")
     .setDomain("urn:li:domain:Sales");

client.entities().upsert(chart);
```

## 완전한 예제

다음은 모든 chart 작업을 보여주는 포괄적인 예제입니다:

```java
import com.linkedin.common.OwnershipType;
import datahub.client.v2.DataHubClientV2;
import datahub.client.v2.entity.Chart;
import java.io.IOException;
import java.util.concurrent.ExecutionException;

public class ChartExample {
    public static void main(String[] args)
        throws IOException, ExecutionException, InterruptedException {
        // Create client
        DataHubClientV2 client = DataHubClientV2.builder()
            .server("http://localhost:8080")
            .build();

        try {
            // Create chart with basic metadata
            Chart chart = Chart.builder()
                .tool("looker")
                .id("regional_sales_chart")
                .title("Regional Sales Performance")
                .description("Quarterly sales broken down by region and product category")
                .build();

            // Add tags for categorization
            chart.addTag("sales")
                 .addTag("executive")
                 .addTag("quarterly-review");

            // Add owners
            chart.addOwner("urn:li:corpuser:sales_team", OwnershipType.TECHNICAL_OWNER)
                 .addOwner("urn:li:corpuser:bi_team", OwnershipType.DATA_STEWARD);

            // Add glossary terms
            chart.addTerm("urn:li:glossaryTerm:SalesMetrics")
                 .addTerm("urn:li:glossaryTerm:QuarterlyReporting");

            // Set domain
            chart.setDomain("urn:li:domain:Sales");

            // Add custom properties
            chart.addCustomProperty("dashboard", "executive_overview")
                 .addCustomProperty("chart_type", "bar")
                 .addCustomProperty("data_source", "snowflake")
                 .addCustomProperty("refresh_schedule", "hourly");

            // Upsert to DataHub (emits all accumulated patches)
            client.entities().upsert(chart);

            System.out.println("Successfully created chart: " + chart.getUrn());
            System.out.println("Total patches: " + chart.getPendingPatches().size());

        } finally {
            client.close();
        }
    }
}
```

## 빌더 옵션 참조

| 메서드                  | 필수 여부 | 설명                                    |
| ----------------------- | -------- | ---------------------------------------------- |
| `tool(String)`          | ✅ 예   | BI 도구 식별자 (예: "looker", "tableau") |
| `id(String)`            | ✅ 예   | 도구 내 chart 식별자               |
| `title(String)`         | 아니요       | Chart 제목                                    |
| `description(String)`   | 아니요       | Chart 설명                              |
| `customProperties(Map)` | 아니요       | 커스텀 키-값 속성의 맵             |

## Patch 기반 작업

Chart entity는 이제 Dataset과 유사한 patch 기반 작업을 지원합니다. 모든 변경 (addTag, addOwner 등)은 save()가 호출될 때까지 축적되는 patch MCP를 생성합니다. 이를 통해:

- **효율적인 배칭**: 단일 네트워크 호출로 여러 작업
- **점진적 업데이트**: 수정된 필드만 서버로 전송
- **플루언트 체이닝**: 읽기 쉬운 방식으로 복잡한 메타데이터 구축

사용 가능한 patch 작업:

| 작업                           | 설명                        |
| ----------------------------------- | ---------------------------------- |
| `addTag(String)`                    | chart에 태그 추가             |
| `removeTag(String)`                 | chart에서 태그 제거        |
| `addOwner(String, OwnershipType)`   | 소유권 타입으로 소유자 추가   |
| `removeOwner(String)`               | chart에서 소유자 제거     |
| `addTerm(String)`                   | chart에 glossary term 추가   |
| `removeTerm(String)`                | glossary term 제거             |
| `setDomain(String)`                 | chart의 도메인 설정       |
| `removeDomain()`                    | chart에서 도메인 제거   |
| `setDescription(String)`            | Chart 설명 업데이트           |
| `setTitle(String)`                  | Chart 제목 업데이트                 |
| `addCustomProperty(String, String)` | 커스텀 속성 추가 또는 업데이트    |
| `removeCustomProperty(String)`      | 커스텀 속성 제거           |
| `setCustomProperties(Map)`          | 모든 커스텀 속성 교체      |
| `setInputDatasets(List)`            | 입력 dataset 설정 (lineage)       |
| `addInputDataset(DatasetUrn)`       | 입력 dataset 추가 (lineage)     |
| `removeInputDataset(DatasetUrn)`    | 입력 dataset 제거 (lineage)  |
| `setExternalUrl(String)`            | chart의 외부 URL 설정     |
| `setChartUrl(String)`               | chart URL 설정                      |
| `setLastRefreshed(long)`            | 마지막 새로 고침 타임스탬프 설정       |
| `setChartType(String)`              | chart 타입 설정 (BAR, LINE 등)   |
| `setAccess(String)`                 | 접근 수준 설정 (PUBLIC, PRIVATE) |

patch 기반 업데이트 작동 방식에 대한 자세한 내용은 [Patch 작업 가이드](./patch-operations.md)를 참조하세요.

## 공통 패턴

### 여러 Chart 생성

```java
List<String> chartIds = Arrays.asList("chart1", "chart2", "chart3");

for (String chartId : chartIds) {
    Chart chart = Chart.builder()
        .tool("looker")
        .id(chartId)
        .title("Chart " + chartId)
        .build();

    client.entities().upsert(chart);
}
```

### Chart를 Dashboard와 연결

커스텀 속성을 사용하여 관계 추적:

```java
Chart chart = Chart.builder()
    .tool("tableau")
    .id("sales_chart")
    .build();

Map<String, String> props = new HashMap<>();
props.put("dashboard_id", "executive_dashboard");
props.put("position", "top_left");

chart.setCustomProperties(props);
client.entities().upsert(chart);
```

## Chart 업데이트

### 로드 및 수정

```java
// Load existing chart
ChartUrn urn = new ChartUrn("looker", "my_chart");
Chart chart = client.entities().get(urn);

// Modify
chart.setDescription("Updated description");

// Save changes
client.entities().update(chart);
```

## 다음 단계

- **[Dataset Entity 가이드](./dataset-entity.md)** - 포괄적인 dataset 작업
- **[Entities 개요](./entities-overview.md)** - entity 전체의 공통 패턴
- **[Patch 작업](./patch-operations.md)** - 점진적 업데이트 이해

## 예제

### 기본 Chart 생성

```java
{{ inline /metadata-integration/java/examples/src/main/java/io/datahubproject/examples/v2/ChartCreateExample.java show_path_as_comment }}
```

### 메타데이터 및 Lineage가 있는 포괄적인 Chart

```java
{{ inline /metadata-integration/java/examples/src/main/java/io/datahubproject/examples/v2/ChartFullExample.java show_path_as_comment }}
```

### Chart Lineage 작업

```java
{{ inline /metadata-integration/java/examples/src/main/java/io/datahubproject/examples/v2/ChartLineageExample.java show_path_as_comment }}
```
