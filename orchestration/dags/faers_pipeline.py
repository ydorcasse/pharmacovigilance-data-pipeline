from airflow.sdk import dag, Param
from airflow.providers.standard.operators.bash import BashOperator
from pendulum import datetime

@dag(
    start_date=datetime(2025, 1, 1),
    schedule="0 6 15 2,5,8,11 *",    # trimestriel (quand la FDA publie)
    catchup=False,  # ne pas rattraper les intervalles passés
    tags=["faers"],
    params={
        "year": Param(None, type=["null", "integer"]),
        "quarter": Param(None, type=["null", "integer"]),
    },
)

def faers_pipeline():
    
    download = BashOperator(
        task_id="download_faers",
        bash_command=(
            "cd /usr/local/airflow && "
            "python -m src.ingestion.download_faers "
            "--year {{ params.year or (logical_date.year if logical_date.month > 3 else logical_date.year - 1) }} "
            "--quarter {{ params.quarter or (((logical_date.month - 1) // 3) or 4) }}"
        ),
    )
    
    unzip = BashOperator(
        task_id="unzip_faers",
        bash_command=(
            "cd /usr/local/airflow && "
            "python -m src.ingestion.unzip_faers "
            "--year {{ params.year or (logical_date.year if logical_date.month > 3 else logical_date.year - 1) }} "
            "--quarter {{ params.quarter or (((logical_date.month - 1) // 3) or 4) }}"
        ),
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