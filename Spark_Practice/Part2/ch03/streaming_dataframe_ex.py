from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

if __name__ == '__main__':
    ss: SparkSession = SparkSession.builder \
        .master("local[2]") \
        .appName("streaming dataframe example") \
        .getOrCreate()

    #define schema
    schemas = StructType([
        StructField("ip", StringType(), False),
        StructField("timestamp", StringType(), False),
        StructField("method", StringType(), False),
        StructField("endpoint", StringType(), False),
        StructField("status_code", StringType(), False),
        StructField("latency", IntegerType(), False),
    ])

    def hello_streaming():
        lines = ss.readStream\
            .format("socket")\
            .option("host","localhost")\
            .option("port",12345).load()
        # 우선 터미널에 nc -lk 12345 를 입력하여 포트를 열어야함
        # 실행 후 터미널에 데이터를 입력하면 특정 포트에 데이터가 들어올 때 마다 데이터 프레임이 만들어지는 것을 볼 수 있음

        lines.writeStream\
            .format("console")\
            .outputMode("append")\
            .trigger(processingTime="2 seconds")\
            .start()\
            .awaitTermination()
    # append 모드가 아닌 complete 모드이면 하나씩이 아닌 전부 추가되어 나옴

    def read_from_socket():
        lines = ss.readStream \
            .format("socket") \
            .option("host", "localhost") \
            .option("port", 12345).load()

        cols = ["ip", "timestamp", "method", "endpoint", "status_code", "latency"]

        df = lines.withColumn(cols[0], F.split(lines['value'], ",").getItem(0)) \
            .withColumn(cols[1], F.split(lines['value'], ",").getItem(1)) \
            .withColumn(cols[2], F.split(lines['value'], ",").getItem(2))\
            .withColumn(cols[3], F.split(lines['value'], ",").getItem(3))\
            .withColumn(cols[4], F.split(lines['value'], ",").getItem(4))\
            .withColumn(cols[5], F.split(lines['value'], ",").getItem(5))

        # filter : status_code = 400, endpoint = "/users"
        df = df.filter((df.status_code == "400") & (df.endpoint == "/users"))

        # group by : method, endpoint 별 latency의 최댓값, 최솟값, 평균값
        group_cols = ["method", "endpoint"]

        # df = df.groupby(group_cols)\
        #     .agg(F.max("latency").alias("max_latency"),
        #          F.min("latency").alias("min_latency"),
        #          F.mean("latency").alias("mean_latency"))
        # append output mode 는 watermark 없이 사용이 안됨
        # stream data가 무한한 데이터가 들어오는 전제
        # 특정한 시점에 대한 제약조건이 없다면 무한한 데이터를 집계해야할 수도 있음
        # 그래서 groupby는 watermark를 배운 후에 실


        df.writeStream \
            .format("console") \
            .outputMode("append") \
            .trigger(processingTime="2 seconds") \
            .start() \
            .awaitTermination()

    def read_from_files():
        logs_df = ss.readStream\
            .format("csv")\
            .option("header", "false").schema(schemas)\
            .load("data/logs/")

        logs_df.writeStream \
            .format("console") \
            .outputMode("append") \
            .trigger(processingTime="2 seconds") \
            .start() \
            .awaitTermination()

    # 만약 경로에 새로운 파일이 추가 된다면 새로운 csv 파일도 배치에 가져옴

    # read_from_socket()
    read_from_files()

