import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
import json
from datetime import datetime

from kafka import KafkaConsumer

    
dag = DAG(
    dag_id = "sensor_data_consumer",
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

spark_task  = SparkSubmitOperator(
    task_id="sensor_data_consumer",
    application="/opt/airflow/dags/spark_streaming_job.py",
    conn_id="spark_default",
    name="KafkaSparkHDFS",
    verbose=False,
    dag=dag,
    env_vars={'HADOOP_CONF_DIR': '/opt/hadoop-3.2.1/etc/hadoop'},
    packages="org.apache.spark:spark-streaming-kafka-0-10_2.12:3.4.2,org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.2,org.apache.hadoop:hadoop-client:3.2.1",

)

end = PythonOperator(
    task_id="end",
    python_callable = lambda: print("Jobs completed successfully"),
    dag=dag
)

start >> spark_task >> end