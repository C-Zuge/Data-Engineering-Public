FROM apache/airflow:latest

RUN pip install apache-airflow-providers-docker

RUN python -m venv soda_venv && source soda_venv/bin/activate && \
    pip install --no-cache-dir soda-core-scientific --user && deactivate

RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-bigquery==1.5.3 --user && dbt deps --project-dir /usr/local/airflow/include/dbt/ && deactivate