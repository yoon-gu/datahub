# Cron 사용하기

머신에 recipe 파일 `/home/ubuntu/datahub_ingest/mysql_to_datahub.yml`이 있다고 가정합니다.

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

[DataHub CLI](../../docs/cli.md)를 사용하여 crontab으로 매일 자정 5분 후에 ingestion이 실행되도록 예약할 수 있습니다.

```
5 0 * * * datahub ingest -c /home/ubuntu/datahub_ingest/mysql_to_datahub.yml
```

스케줄링과 관련된 더 많은 옵션은 [crontab 문서](https://man7.org/linux/man-pages/man5/crontab.5.html)를 참조하세요.
