import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
import os


import random
import time
import json
from datetime import datetime
from kafka import KafkaProducer
import logging
from dotenv import load_dotenv
import requests

load_dotenv()

def fetch_data_from_api():
    url = "https://data.cityofnewyork.us/resource/h9gi-nx95.json"
    params = {
        "$order": "crash_date DESC",
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  
        raw_data = response.json()  
        logging.info(f"Fetched {len(raw_data)} records from API")
        print('generating')
        print(raw_data)
        return raw_data
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching data: {e}")
        return []

def stream_data():
    kafka_host = os.environ.get('KAFKA_HOST', 'localhost')
    producer = KafkaProducer(bootstrap_servers=['10.0.2.15:9092'], max_block_ms=5000,api_version=(0,11,5),
              )
    curr_time = time.time()
    data = fetch_data_from_api()
    if not data:
        logging.error("No data fetched; exiting the stream.")
        return
    
    for res in data:
        if time.time() > curr_time + 60:
            break
        try:
            producer.send('raw_data', json.dumps(res).encode('utf-8'))
            producer.flush()
            time.sleep(1)
        except Exception as e:
            logging.error(f'An error occured: {e}')
            continue


    
dag = DAG(
    dag_id = "fetch_data",
    default_args = {
        "owner" : "Bich Ly",
        "start_date" : airflow.utils.dates.days_ago(1),
    },
    schedule_interval = "*/3 * * * *",
    catchup = False
)

start = PythonOperator(
    task_id = "start",
    python_callable = lambda: print("Jobs Started"),
    dag=dag
)

fetch_data_task = PythonOperator(
    task_id="fetch_data_from_api",
    python_callable=stream_data,
    dag=dag
)

end = PythonOperator(
    task_id="end",
    python_callable = lambda: print("Jobs completed successfully"),
    dag=dag
)

start >> fetch_data_task >> end