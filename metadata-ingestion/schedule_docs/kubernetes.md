# Kubernetes 사용하기

공식 [helm charts](https://github.com/acryldata/datahub-helm)를 사용하여 DataHub를 배포한 경우,
datahub ingestion cron 서브차트를 사용하여 ingestion을 예약할 수 있습니다.

**values.yaml**에서 해당 구성이 어떻게 보이는지 예시입니다:

```yaml
datahub-ingestion-cron:
  enabled: true
  crons:
    mysql:
      schedule: "0 * * * *" # 매 시간
      recipe:
        configmapName: recipe-config
        fileName: mysql_recipe.yml
```

이는 cron 작업이 실행될 동일한 네임스페이스에 예약된 모든 recipe를 담고 있는 Kubernetes ConfigMap이 미리 존재한다고 가정합니다.

예시:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: recipe-config
data:
  mysql_recipe.yml: |-
    source:
      type: mysql
      config:
        # 연결 정보
        host_port: <MYSQL HOST>:3306
        database: dbname

        # 자격 증명
        username: root
        password: example

    sink:
      type: datahub-rest
      config:
        server: http://<GMS_HOST>:8080
```

자세한 내용은 이 서브차트의 [문서](https://github.com/acryldata/datahub-helm/tree/master/charts/datahub/subcharts/datahub-ingestion-cron)를 참조하세요.
