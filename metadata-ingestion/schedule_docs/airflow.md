# Airflow 사용하기

스케줄링에 Apache Airflow를 사용 중이라면 ingestion recipe 스케줄링에도 Airflow를 활용할 수 있습니다. Airflow 관련 질문은 [Airflow 문서](https://airflow.apache.org/docs/apache-airflow/stable/)를 참조하세요.

DAG를 구성하는 몇 가지 예시를 제공합니다:

- [`mysql_sample_dag`](../../metadata-ingestion-modules/airflow-plugin/src/datahub_airflow_plugin/example_dags/mysql_sample_dag.py)는 DAG 내에 전체 MySQL ingestion 구성을 포함합니다.

- [`snowflake_sample_dag`](../../metadata-ingestion-modules/airflow-plugin/src/datahub_airflow_plugin/example_dags/snowflake_sample_dag.py)는 recipe에 자격 증명을 포함하지 않고 Airflow의 [Connections](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection/index.html) 기능에서 가져옵니다. 이 방식을 사용하려면 Airflow에서 연결을 구성해야 합니다.

:::tip

이 예시 DAG들은 `PythonVirtualenvOperator`를 사용하여 ingestion을 실행합니다. 이는 DataHub와 나머지 Airflow 환경 사이에 충돌이 없음을 보장하므로 권장되는 방식입니다.

태스크를 구성할 때 source에 맞는 요구 사항을 지정하고 `system_site_packages` 옵션을 false로 설정하는 것이 중요합니다.

```py
ingestion_task = PythonVirtualenvOperator(
	task_id="ingestion_task",
	requirements=[
		"acryl-datahub[<your-source>]",
	],
	system_site_packages=False,
	python_callable=your_callable,
)
```

:::

<details>
<summary>고급: recipe 파일 로드하기</summary>

더 고급 사례에서는 ingestion recipe를 파일에 저장하고 태스크에서 로드하고 싶을 수 있습니다.

- recipe 파일이 Airflow 워커에서 접근 가능한 폴더에 있는지 확인합니다. Airflow가 설치된 머신의 절대 경로 또는 `AIRFLOW_HOME` 기준의 상대 경로를 지정할 수 있습니다.
- Airflow 환경에 [DataHub CLI](../../docs/cli.md)가 설치되어 있는지 확인합니다.
- DataHub ingestion recipe 파일을 읽고 실행하는 DAG 태스크를 생성합니다. 참고용 예시는 아래를 확인하세요.
- 스케줄링을 위해 DAG 파일을 Airflow에 배포합니다. 일반적으로 Airflow 인스턴스에서 접근 가능한 dags 폴더에 DAG 파일을 체크인하는 작업을 포함합니다.

예시: [`generic_recipe_sample_dag`](../../metadata-ingestion-modules/airflow-plugin/src/datahub_airflow_plugin/example_dags/generic_recipe_sample_dag.py)

</details>
