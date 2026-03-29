# 메타데이터 수집 스케줄링 소개

recipe 파일 `/home/ubuntu/datahub_ingest/mysql_to_datahub.yml`이 주어진 경우.

```
source:
  type: mysql
  config:
    # 연결 정보
    host_port: localhost:3306
    database: dbname

    # 자격 증명
    username: root
    password: example

sink:
 type: datahub-rest
 config:
  server: http://localhost:8080
```

다음과 같이 [DataHub CLI](../../docs/cli.md)를 사용하여 메타데이터를 수집할 수 있습니다.

```
datahub ingest -c /home/ubuntu/datahub_ingest/mysql_to_datahub.yml
```

이는 recipe 파일에 구성된 `mysql` source에서 메타데이터를 한 번 수집합니다. source 시스템이 변경되면 DataHub에 변경 사항이 반영되기를 원할 것입니다. 이를 위해 누군가가 recipe 파일을 사용하여 ingestion 명령어를 다시 실행해야 합니다.

명령어를 수동으로 실행하는 대신, 정기적으로 실행되도록 ingestion을 예약할 수 있습니다. 이 섹션에서는 DataHub에 메타데이터 ingestion을 예약하는 방법에 대한 몇 가지 예를 제공합니다.
