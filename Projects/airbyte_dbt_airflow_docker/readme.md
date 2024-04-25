### Airbyte | DBT | Airflow | Docker
This project will cover some gaps on how to use dbt and airbyte with airflow all over docker. In this case we have to instance a dbt project at first but only orquestrate with airflow (including process dbt_run inside airflow and get the response of success or failure).

This is not the best way once we dont have an clear view of dbt proccess and each time we have to manage by docker cli using airflow, the next step should be increment using Astronomer Cosmos that will handle the render and abstract some layers.
