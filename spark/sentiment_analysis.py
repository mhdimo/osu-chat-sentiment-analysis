# spark/sentiment_analysis.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, FloatType
from textblob import TextBlob
import json

def analyze_sentiment(message):
    try:
        blob = TextBlob(message)
        sentiment = blob.sentiment.polarity  # Returns a float between -1.0 to 1.0
        return float(sentiment)
    except Exception as e:
        return 0.0

def main():
    spark = SparkSession.builder \
        .appName("IRC Sentiment Analysis") \
        .getOrCreate()

    # Define UDF for sentiment analysis
    sentiment_udf = udf(analyze_sentiment, FloatType())

    # Read from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "irc-messages") \
        .option("startingOffsets", "earliest") \
        .load()

    # Convert the binary 'value' column to string
    df = df.selectExpr("CAST(value AS STRING) as json_str")

    # Parse JSON and extract fields
    df = df.selectExpr("json_tuple(json_str, 'username', 'message', 'timestamp', 'channel') as (username, message, timestamp, channel)")

    # Perform sentiment analysis
    df = df.withColumn("sentiment_score", sentiment_udf(df.message))

    # Prepare JSON for Kafka output
    def to_json(username, message, timestamp, channel, sentiment_score):
        return json.dumps({
            "username": username,
            "message": message,
            "timestamp": timestamp,
            "channel": channel,
            "sentiment_score": sentiment_score
        })

    to_json_udf = udf(to_json, StringType())

    df = df.withColumn("value", to_json_udf(df.username, df.message, df.timestamp, df.channel, df.sentiment_score))

    # Write to Kafka
    query = df.selectExpr("CAST(value AS STRING)") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("topic", "irc-messages-sentiment") \
        .option("checkpointLocation", "/tmp/spark_checkpoint") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()