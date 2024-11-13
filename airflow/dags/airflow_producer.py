# import airflow
# from airflow import DAG
# from airflow.operators.python import PythonOperator
# import os


# import random
# import time
# import json
# from datetime import datetime
# from kafka import KafkaProducer
# import logging
# from dotenv import load_dotenv
# import requests

# load_dotenv()

# def fetch_data_from_api():
#     url = "https://data.cityofnewyork.us/resource/h9gi-nx95.json"
#     params = {
#         "$order": "crash_date DESC",
#     }
    
#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()  
#         raw_data = response.json()  
#         logging.info(f"Fetched {len(raw_data)} records from API")
#         print('generating')
#         return raw_data
#     except requests.exceptions.RequestException as e:
#         logging.error(f"An error occurred while fetching data: {e}")
#         return []

# def stream_data():
#     kafka_host = os.environ.get('KAFKA_HOST', 'localhost')
#     producer = KafkaProducer(bootstrap_servers=['10.0.2.15:9092'], max_block_ms=5000,api_version=(0,11,5),
#               )

#     data = fetch_data_from_api()
#     if not data:
#         logging.error("No data fetched; exiting the stream.")
#         return
#     count=0
#     for res in data:
#         try:
#             producer.send('raw_data', json.dumps(res).encode('utf-8'))
#             producer.flush()
#             time.sleep(0.5)
#             count+=1
#         except Exception as e:
#             logging.error(f'An error occured: {e}')
#             continue
#     print(count)


    
# dag = DAG(
#     dag_id = "fetch_data",
#     default_args = {
#         "owner" : "Bich Ly",
#         "start_date" : airflow.utils.dates.days_ago(1),
#     },
#     schedule_interval = "@daily",
#     catchup = False
# )

# start = PythonOperator(
#     task_id = "start",
#     python_callable = lambda: print("Jobs Started"),
#     dag=dag
# )

# fetch_data_task = PythonOperator(
#     task_id="fetch_data_from_api",
#     python_callable=stream_data,
#     dag=dag
# )

# end = PythonOperator(
#     task_id="end",
#     python_callable = lambda: print("Jobs completed successfully"),
#     dag=dag
# )

# start >> fetch_data_task >> end


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

def fetch_data_from_api(offset=0, limit=100):
    url = "https://data.cityofnewyork.us/resource/h9gi-nx95.json"
    params = {
        "$order": "crash_date DESC",
        "$limit": limit,
        "$offset": offset
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        raw_data = response.json()
        if not raw_data:
            logging.info("No more data to fetch; exiting.")
            return []  # Indicate no more data
        logging.info(f"Fetched {len(raw_data)} records from API with offset {offset}")
        return raw_data
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching data: {e}")
        return []



def stream_data():
    kafka_host = os.environ.get('KAFKA_HOST', 'localhost')
    producer = KafkaProducer(
        bootstrap_servers=['10.0.2.15:9092'], 
        max_block_ms=5000,
        api_version=(0,11,5)
    )
    
    offset = 0
    limit = 100


    max_offset = 1000
    print(max_offset)
    while offset < max_offset:
        # Fetch data from API
        data = fetch_data_from_api(offset=offset, limit=limit)
        
        # Log the offset and number of records fetched
        logging.info(f"Offset: {offset}, Records fetched: {len(data)}")

        # Stop fetching if no data is returned
        if not data:
            logging.info("No more data to fetch; exiting loop.")
            break
        
        # Send each record to Kafka
        for record in data:
            try:
                producer.send('raw_data', json.dumps(record).encode('utf-8'))
                producer.flush()
            except Exception as e:
                logging.error(f"An error occurred while sending data to Kafka: {e}")
                continue

        logging.info(f"Streamed {len(data)} records in this batch.")
        
        # Stop fetching if the number of records is less than the limit
        if len(data) < limit:
            logging.info("Fetched last batch of data; exiting loop.")
            break
        
        # Increment offset for the next batch
        offset += limit
        time.sleep(5)  # Wait 5 seconds before fetching the next batch

    logging.info("Reached maximum offset or no more data; exiting.")



    
dag = DAG(
    dag_id = "fetch_data",
    default_args = {
        "owner" : "Bich Ly",
        "start_date" : airflow.utils.dates.days_ago(1),
    },
    schedule_interval = "@daily",
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
