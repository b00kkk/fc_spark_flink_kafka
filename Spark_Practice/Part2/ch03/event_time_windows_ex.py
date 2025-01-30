from pyspark.sql import SparkSession
from pyspark.sql.window import Window
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, IntegralType

if __name__ == '__main__':
    ss: SparkSession = SparkSession.builder\
        .master("local[2]")\
        .appName("Event time windows ex")\
        .getOrCreate()

    domain_traffic_schema = StructType([
        StructField("id", StringType(), False),
        StructField("domain", StringType(), False),
        StructField("count", IntegerType(), False),
        StructField("time", TimestampType(), False),
    ])

    def read_traffics_from_socket():
        return ss.readStream\
            .format("socket")\
            .option("host", "localhost")\
            .option("port", 12345).load()\
            .select(F.from_json(F.col("value"),
                                domain_traffic_schema)
                    .alias("traffic")).selectExpr("traffic.*")

    # Q) sliding window를 사용해서 트래픽 카운트들을 집계

    def aggregate_traffic_counts_by_sliding_window():
        traffics_df = read_traffics_from_socket()

        window_by_hours =\
            traffics_df.groupby(F.window(
                F.col("time"),
                windowDuration="2 hours",
                slideDuration="1 hour").alias("time"))\
                .agg(F.sum("count").alias("total_count"))\
                .select(
                    F.col("time").getField("start").alias("start"),
                    F.col("time").getField("end").alias("end"),
                    F.col("total_count")
            ).orderBy(F.col("start"))
        # Duration 2시간, Interval 1시간으로 지정

        window_by_hours.writeStream.format("console")\
            .outputMode("complete").start().awaitTermination()

    def aggregate_traffic_counts_by_tumbling_window():
        traffics_df = read_traffics_from_socket()

        window_by_hours = \
            traffics_df.groupby(F.window(
                F.col("time"), "1 hour").alias("time")) \
                .agg(F.sum("count").alias("total_count")) \
                .select(
                F.col("time").getField("start").alias("start"),
                F.col("time").getField("end").alias("end"),
                F.col("total_count")
            ).orderBy(F.col("start"))

        window_by_hours.writeStream.format("console") \
            .outputMode("complete").start().awaitTermination()

    # aggregate_traffic_counts_by_sliding_window()
    # aggregate_traffic_counts_by_tumbling_window()

    """
    매 시간 마다, traffic 이 가장 만은 도메인을 출력
    """

    def read_traffics_from_file():
        return ss.readStream.schema(domain_traffic_schema)\
            .json("data/traffics")

    def find_largest_traffic_domain_per_hour():
        traffics_df = read_traffics_from_file()

        largest_traffic_domain = \
            traffics_df.groupby(F.col("domain"), F.window(
                F.col("time"), "1 hour").alias("hour")) \
                .agg(F.sum("count").alias("total_count")) \
                .select(
                F.col("hour").getField("start").alias("start"),
                F.col("hour").getField("end").alias("end"),
                F.col("domain"),
                F.col("total_count")
            ).orderBy(F.col("total_count"))

        largest_traffic_domain.writeStream.format("console") \
            .outputMode("complete").start().awaitTermination()

    find_largest_traffic_domain_per_hour()