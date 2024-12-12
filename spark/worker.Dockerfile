FROM bitnami/spark:3.4.1

USER root

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install textblob pyspark requests

# Download TextBlob corpora
RUN python -m textblob.download_corpora

WORKDIR /app