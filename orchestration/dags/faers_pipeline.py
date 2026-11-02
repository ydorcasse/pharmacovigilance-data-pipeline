from airflow.sdk import dag
from airflow.providers.standard.operators.bash import BashOperator
from pendulum import datetime

@dag(
    start_date=datetime(2025, 1, 1),
    schedule="@quarterly",    # trimestriel (quand la FDA publie)
    catchup=False,  # ne pas rattraper les intervalles passés
    tags=["faers"],
)

def faers_pipeline():
    
    download = BashOperator(
        task_id="download_faers",
        bash_command="python /usr/local/airflow/src/ingestion/download_faers.py --year 2026 --quarter 2",
    )
    
    unzip = BashOperator(
        task_id="unzip_faers",
        bash_command="python /usr/local/airflow/src/ingestion/unzip_faers.py --year 2026 --quarter 2",
    )
    
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /usr/local/airflow/src/transformation/faers && dbt run",
    )
    
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /usr/local/airflow/src/transformation/faers && dbt test",
    )
    
    download >> unzip >> dbt_run >> dbt_test
    
faers_pipeline()