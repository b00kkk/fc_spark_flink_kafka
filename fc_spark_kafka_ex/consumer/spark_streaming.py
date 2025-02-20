from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.protobuf.functions import from_protobuf


if __name__ == '__main__':
    ss: SparkSession = SparkSession.builder\
        .master("local")\
        .appName("book_ex")\
        .getOrCreate()

    proto_desc_path = "/home/boo/PycharmProjects/fc_spark_flink_kafka/fc_spark_kafka_ex/proto/book_data.desc"

    df = ss.readStream\
        .format("kafka")\
        .option("startingOffset", "earliest")\
        .option("subscribe", "book")\
        .option("kafka.bootstrap.servers", "localhost:29092")\
        .load()\
        .select(from_protobuf("value", "Book", proto_desc_path).alias("book"))\
        .withColumn("title", F.column("book.title")) \
        .withColumn("author", F.column("book.author")) \
        .withColumn("publisher", F.column("book.publisher")) \
        .withColumn("price", F.column("book.price")) \
        .withColumn("publication_date", F.column("book.publication_date")) \
        .withColumn("source", F.column("book.source"))\
        .withColumn("processing_time", F.current_timestamp())\
        .select("title", "author", "publisher", "price", "publication_date", "source", "processing_time")

    price_stat_df = df.groupby(F.window(F.col("processing_time"), "1 minute"), "source").agg(
        F.max("price").alias("max_price"),
        F.min("price").alias("min_price"),
        F.mean("price").alias("mean_price"),
    )

    price_stat_df.writeStream\
        .format("console")\
        .outputMode("complete")\
        .option("truncate", "false")\
        .start()\
        .awaitTermination()