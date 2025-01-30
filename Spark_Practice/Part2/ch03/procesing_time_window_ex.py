from pyspark.sql import SparkSession
import pyspark.sql.functions as F

if __name__ == '__main__':
    ss: SparkSession = SparkSession.builder\
        .master("local[2]")\
        .appName("Event time windows ex")\
        .getOrCreate()

    def aggregate_by_processing_time():
        lines_char_count_by_window_df = ss.readStream \
            .format("socket")\
            .option("host", "localhost")\
            .option("port", 12345).load()\
            .select(F.col("value"),
                    F.current_timestamp().alias("processingTime"))\
            .groupby(F.window(F.col("processingTime"), "5 seconds").alias("window"))\
            .agg(F.sum(F.length(F.col("value"))).alias("charCount")) \
            .select(F.col("window").getField("start").alias("strat"),
                    F.col("window").getField("end").alias("end"),
                    F.col("charCount"))

        lines_char_count_by_window_df.writeStream\
            .format("console")\
            .outputMode("complete")\
            .start()\
            .awaitTermination()

    aggregate_by_processing_time()
    # spark에서 처리되는 시간에 따라 집계되는 것을 확인할 수 있음