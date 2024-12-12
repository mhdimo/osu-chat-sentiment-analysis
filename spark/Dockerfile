# spark/Dockerfile
FROM bitnami/spark:3.4.1

USER root

RUN install_packages wget

# Install Python dependencies
RUN pip install textblob pyspark requests

# Download TextBlob corpora
RUN python -m textblob.download_corpora

# Copy the sentiment analysis script
COPY sentiment_analysis.py /app/sentiment_analysis.py

WORKDIR /app

# Set the entrypoint to run the Spark application with required packages
CMD ["spark-submit", "--master", "spark://spark-master:7077", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1", "sentiment_analysis.py"]