# spark/Dockerfile
FROM bitnami/spark:3.4.1

USER root

# Install wget
RUN install_packages wget

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install textblob pyspark requests

# Download TextBlob corpora
RUN python -m textblob.download_corpora

# Copy the sentiment analysis script
COPY sentiment_analysis.py /app/sentiment_analysis.py

WORKDIR /app

# Use the SPARK_MASTER_URL environment variable
CMD ["sh", "-c", "spark-submit --master ${SPARK_MASTER_URL} --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 sentiment_analysis.py"]