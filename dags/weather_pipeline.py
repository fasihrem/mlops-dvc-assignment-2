from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2024, 1, 1),
    'catchup': False
}

with DAG('weather_pipeline', schedule_interval=None, default_args=default_args, tags=["dvc"]) as dag:

    collect_task = BashOperator(
        task_id='collect_weather',
        bash_command='python3 fetch_weather.py'
    )

    preprocess_task = BashOperator(
        task_id='preprocess_data',
        bash_command='python3 preprocess_data.py'
    )

    collect_task >> preprocess_task