from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions \
    import col, to_timestamp, max, min, mean, date_trunc, collect_set, \
    hour, minute, count


def load_data(ss: SparkSession, from_file, schema):
    if from_file:
        return ss.read.schema(schema).csv("data/log.csv")

    log_data_inmemory = [
        ["130.31.184.234", "2023-02-26 04:15:21", "PATCH", "/users", "400", 61],
        ["28.252.170.12", "2023-02-26 04:15:21", "GET", "/events", "401", 73],
        ["180.97.92.48", "2023-02-26 04:15:22", "POST", "/parsers", "503", 17],
        ["73.218.61.17", "2023-02-26 04:16:22", "DELETE", "/lists", "201", 91],
        ["24.15.193.50", "2023-02-26 04:17:23", "PUT", "/auth", "400", 24],
    ]

    return ss.createDataFrame(log_data_inmemory, schema)


if __name__ == "__main__":
    ss: SparkSession = SparkSession.builder \
        .master("local") \
        .appName("log dataframe ex") \
        .getOrCreate()

    # define schema
    fields = StructType([
        StructField("ip", StringType(), False), #False: null값을 허용하지 않음
        StructField("timestamp", StringType(), False),
        StructField("method", StringType(), False),
        StructField("endpoint", StringType(), False),
        StructField("status_code", StringType(), False),
        StructField("latency", IntegerType(), False),  # 단위 : milliseconds
    ])

    from_file = True

    df = load_data(ss, from_file, fields)

    # 데이터 확인
    #df.show()
    # 스키마 확인
    #df.printSchema()

    # a) 컬럼 변환
    # a-1) 현재 latency 컬럼의 단위는 milliseconds인데, seconds 단위인
    # latency_seconds 컬럼을 새로 만들기

    def milliseconds_to_seconds(n):
        return n/1000

    df = df.withColumn("latency_seconds",
                       milliseconds_to_seconds(df.latency))

    #df.show()

    # a-2) StringType 로 받은 timestamp 컬럼을 TimestampType으로 변경

    df= df.withColumn("timestamp", to_timestamp(col("timestamp")))
    # df.show()
    # df.printSchema()


    # b) filter
    # b-1) status_code = 400, endpoint = '/users'인 row만 필터링
    # df = df.filter((df.status_code == "400") & (df.endpoint == "/users"))
    # df.show()

    # c) group by
    # c-1) method, endpoint별 latency의 최댓값, 최솟값, 평균값
    group_cols = ["method", "endpoint"]

    # df.groupby(group_cols)\
    #     .agg(max("latency").alias("max_latency"),
    #          min("latency").alias("min_latency"),
    #          mean("latency").alias("mean_latency")).show()

    # c-2) 분 단위의, 중복을 제거한 ip 리스트, 개수 뽑기
    group_cols = ["hour", "minute"]
    df.withColumn(
        "hour", hour(date_trunc("hour", col("timestamp")))
    ).withColumn(
        "minute", minute(date_trunc("minute", col("timestamp")))
    ).groupby(group_cols).agg(
        collect_set("ip").alias("ip_list"),
        count("ip").alias("ip_count")
    ).sort(group_cols).show()
    # explain을 넣고 돌리면 Physical Plan을 볼 수 있음
    # 밑에서 부터 위로 올라가면서 해석하면 됨
    # extended=True를 넣으면 처음 Logical Plan 부터 쭉 확인할 수 있음

    while True:
        pass

    # http://localhost:4040/jobs/ 접속
    # Stages 접속해 확인해보면 RDD로 출력되는 걸 볼 수 있음
    # Environment 도 RDD로 확인이 됨
    # SQL/DataFrame은  SparkSQL을 사용했기에 나오는데 Plan을 확인할 수 있음
    # Exchange가 셔플이 발생했다는 의미
    # Details에서 extended를 볼 수 있음
    # RDD는 이런 식의 최적화가 되어있지 않음
    # 그렇기에 RDD보다는 DataFrame이나 SQL을 사용하는 것이 좋음
