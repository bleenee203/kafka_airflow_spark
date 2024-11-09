from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType


def spark_streaming_job():
    # scala_version = '2.12' 
    # spark_version = '3.4.2'
    # packages = [
    #     f'org.apache.spark:spark-sql-kafka-0-10_{scala_version}:{spark_version}',
    #     'org.apache.kafka:kafka-clients:7.7.1'
    # ]
    spark = SparkSession.builder \
        .appName("KafkaSparkStreaming") \
        .master("spark://spark-master:7077") \
        .getOrCreate()

    schema = StructType([
        StructField("crash_date", StringType(), True),
        StructField("crash_time", StringType(), True),
        StructField("borough", StringType(), True),
        StructField("latitude", FloatType(), True),
        StructField("longitude", FloatType(), True),
        StructField("on_street_name", StringType(), True),
        StructField("off_street_name", StringType(), True),
        StructField("number_of_persons_injured", IntegerType(), True),
        StructField("number_of_persons_killed", IntegerType(), True),
        StructField("number_of_pedestrians_injured", IntegerType(), True),
        StructField("number_of_pedestrians_killed", IntegerType(), True),
        StructField("number_of_cyclist_injured", IntegerType(), True),
        StructField("number_of_cyclist_killed", IntegerType(), True),
        StructField("number_of_motorist_injured", IntegerType(), True),
        StructField("number_of_motorist_killed", IntegerType(), True),
        StructField("contributing_factor_vehicle_1", StringType(), True),
        StructField("contributing_factor_vehicle_2", StringType(), True),
        StructField("vehicle_type_code1", StringType(), True),
        StructField("vehicle_type_code2", StringType(), True),
        StructField("vehicle_type_code3", StringType(), True),
        StructField("vehicle_type_code4", StringType(), True),
        StructField("vehicle_type_code5", StringType(), True)
    ])

    # Kết nối tới Kafka
    #lastest: tieu thu du lieu moi duoc gui den
    #earliest: tieu thu tat ca du lieu co san trong topic va ca nhung du lieu moi duoc gui den
    #failOnDataLoss: false - khong fail khi xay ra mat du lieu
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "10.0.2.15:9092") \
        .option("subscribe", "raw_data") \
        .option("startingOffsets", "latest") \
        .option("failOnDataLoss", "false") \
        .load()

    # Chuyển đổi dữ liệu từ Kafka (JSON) thành các cột trong DataFrame
    json_df = df.selectExpr("CAST(value AS STRING) as json") \
        .select(from_json("json", schema).alias("data")) \
        .select("data.*")
    print('done')
    # Ghi dữ liệu vào HDFS
    query = json_df.writeStream \
        .format("parquet").outputMode("append") \
        .option("path", "hdfs://namenode:9000/raw_data") \
        .option("checkpointLocation", "hdfs://namenode:9000/spark_checkpoint") \
        .start()

    query.awaitTermination()
    #log ra console
    df1 = df.selectExpr("CAST(value AS STRING)").select(from_json(col("value"),schema).alias("data")).select("data.*")
    df1.printSchema()
    df1.writeStream \
    .outputMode("update") \
    .format("console") \
    .option("truncate", False) \
    .start() \
    .awaitTermination()
    

if __name__ == "__main__":
    spark_streaming_job()