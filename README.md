Lấy địa chỉ IP của máy host: hostname -I | awk '{print $1}'

Sau đó vào file .env của cả 2 folder, thay thế địa chỉ IP bằng địa chỉ IP của máy mình

Cd vào thư mục kafka: docker compose up (Bị lỗi broker is unhealthy -> chỉ cần compose up lại)

Chạy xong thì tạo topic

Tạo 1 topic: docker compose exec broker kafka-topics --create --topic <ten-topic> --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092

Xóa 1 topic: docker compose exec broker kafka-topics --delete --topic <ten-topic> --bootstrap-server localhost:9092

Mở localhost ở port 9021(Control Center) để xem các thông tin: bấm vào broker đang có -> topic..v.v

Cd vào thư mục airflow: docker compose up

Nếu gặp lỗi Hadoop NameNode is in safe mode

Vào container namenode bằng cách: docker exec -it namenode /bin/bash

Tắt safe mode: hdfs dfsadmin -safemode leave

Khi webUI của airflow start: Vào Admin -> Connection tạo 1 connection

Conn_id: spark_default

Port:7077

Connection Type: Spark

Host: spark://spark-master

Sau đó unpause dag producer lên: nó sẽ tự động chạy và gửi dữ liệu đến kafka mỗi 3 phút lần (dữ liệu t đang tạo random)

Start dag consumer lên(cái này chạy tay, chạy đến khi nào muốn dừng thì thôi): nó sẽ lấy dữ liệu từ kafka liên tục và đưa vào hdfs

Xem tình trạng spark job đang chạy ở localhost port 9090

Xem các thư mục, dữ liệu trong hdfs(yarn) ở localhost port 9870



Lưu ý: 

SPARK_WORKER_CORES: 1

SPARK_WORKER_MEMORY: 1g

Muốn chạy song song nhiều job thì tăng 2 tham số này lên

Hiện tại chỉ chạy được 1 job 1 lúc

Muốn chạy job bằng spark-shell: docker exec -it airflow-spark-master-1 /opt/bitnami/spark/bin/spark-shell --master spark://spark-master:7077

Code kiểm tra dữ liệu trong hdfs ở spark-shell

val df = spark.read.parquet("hdfs://namenode:9000/raw_data")

df.show()


![image](https://github.com/user-attachments/assets/1ea055da-9e03-4593-b3d9-50b50c5da54b)


Pull git lên bị lỗi: xác thực -> git remote set-url origin git@github.com:bleenee203/kafka_airflow_spark
