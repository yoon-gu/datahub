# Sinks

Sink는 **메타데이터의 목적지입니다.**

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/sources-sinks.png"/>
</p>

일반적으로 sink는 아래와 같이 [recipe](./recipe_overview.md)에서 [source](./source-docs-template.md) 다음에 정의됩니다.

```yaml
source: ...

sink:
  type: <sink_type>
  config: ...
```

## Sink 유형

DataHub의 ingestion을 구성할 때, 일반적으로 다음 중 하나를 통해 메타데이터를 DataHub로 전송합니다.

- [REST (datahub-rest)](sink_docs/datahub.md#datahub-rest)
- [Kafka (datahub-kafka)](sink_docs/datahub.md#datahub-kafka)

디버깅이나 문제 해결 목적으로는 다음 sink가 유용할 수 있습니다:

- [메타데이터 파일](sink_docs/metadata-file.md)
- [콘솔](sink_docs/console.md)

## 기본 Sink

`acryl-datahub` 버전 `>=0.8.33.2`부터 기본 sink는 `datahub-rest` 엔드포인트로 간주됩니다.
