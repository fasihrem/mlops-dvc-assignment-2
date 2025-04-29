from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess

def run_get_data():
    subprocess.run(["python", "collectData.py"], check=True)

def run_process_data():
    subprocess.run(["python", "preprocessData.py"], check=True)

    
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'start_date': datetime(2025, 4, 30),  # Set the start date
}

# Instantiate the DAG
with DAG(
    'weather_data_pipeline',
    default_args=default_args,
    description='A simple pipeline to get and process weather data',
    schedule_interval=None,  # Set to None for manual triggering or define a cron expression
    catchup=False,  # Skip running past DAG runs
) as dag:

    # Task 1: Run get_data.py
    task_get_data = PythonOperator(
        task_id='get_data',
        python_callable=run_get_data,
    )

    # Task 2: Run process_data.py
    task_process_data = PythonOperator(
        task_id='process_data',
        python_callable=run_process_data,
    )

    # Set task dependencies
    task_get_data >> task_process_data  # Ensures get_data runs before process_data

