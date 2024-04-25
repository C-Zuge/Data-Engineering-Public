from datetime import datetime
from airflow import DAG
from docker.types import Mount
from airflow.utils.dates import days_ago
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from airflow.providers.docker.operators.docker import DockerOperator
import subprocess

CONN_ID = ''

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

with DAG(
    'elt_and_dbt',
    default_args=default_args,
    description='An ELT workflow with dbt',
    start_date=datetime(2023, 10, 3),
    catchup=False,
) as dag:

    t1 = AirbyteTriggerSyncOperator(
        task_id='airbyte_postgres-to_postgres',
        airbyte_conn_id='airbyte',
        connection_id=CONN_ID,
        asynchronous=False,
        timeout=3600,
        wait_seconds=3
    )

    t2 = DockerOperator(
        task_id='dbt_run',
        image='ghcr.io/dbt-labs/dbt-postgres:1.4.7',
        command=[
            "run",
            "--profiles-dir",
            "/root",
            "--project-dir",
            "/dbt",
            "--full-refresh"
        ],
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        mounts=[
            Mount(source='<Insert_path>',
                target='/dbt', type='bind'),
            Mount(source='/home/cesar/.dbt', target='/root', type='bind'),
        ],
        extra_hosts={"host.docker.internal":"host-gateway"}
    )

    t1 >> t2