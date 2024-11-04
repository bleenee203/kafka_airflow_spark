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


load_dotenv()

def fetch_data_from_api(id):
    #thay the bang code fetch data
    raw_data = {
        "sensor_id": id,
        "temperature": round(random.uniform(29.0, 30.0), 2),  # Random temperature between 20.0 and 30.0 degrees
        "humidity": round(random.uniform(50.0, 51.0), 2),     # Random humidity between 30.0% and 60.0%
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    print('generating')
    print(raw_data)
    return raw_data

def stream_data():
    kafka_host = os.environ.get('KAFKA_HOST', 'localhost')
    producer = KafkaProducer(bootstrap_servers=['10.0.2.15:9092'], max_block_ms=5000,api_version=(0,11,5),
              )
    curr_time = time.time()
    id = 0
    while True:
        if time.time() > curr_time + 60: 
            break
        try:
            id += 1
            res = fetch_data_from_api(id)
            if id >= 5:
                id = 0
            print(res, end="\r")
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