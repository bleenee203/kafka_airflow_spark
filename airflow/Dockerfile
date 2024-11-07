FROM ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.9.3-python3.11}

USER root
RUN apt-get update && \
    apt-get install -y gcc python3-dev openjdk-17-jdk && \
    apt-get clean

ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64
ENV PATH "$JAVA_HOME/bin:$PATH"

USER airflow

COPY ./requirements.txt . 
RUN pip install -r requirements.txt
