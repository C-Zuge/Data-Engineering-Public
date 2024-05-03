## Astro Airflow | Soda | DBT | GCP | Metabase | Docker 

This project will cover some gaps on how to use soda and dbt (w/ Astronomer Cosmos) orchestrated by airflow (astronomer) and visualization on metabase, all over docker and integrated to Google Cloud Platform to store the data on GC storage and Big Query. This project will create a pipeline following the steps: 
- Acquire Data
- Store in Google Cloud Storage
- Create Dataset
- Load Dataset to Bigquery
- Check load (Soda)
- Transform de Data (DBT)
- Check Transformation (Soda)
- Create report table (DBT)
- Check Report (Soda)