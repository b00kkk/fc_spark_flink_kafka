import random

from pyspark.sql import SparkSession
from pyspark.sql.functions import asc

if __name__ == '__main__':
    ss: SparkSession = SparkSession.builder\
        .master("local")\
        .appName("sort_merge_join_ex")\
        .config("spark.sql.join.preferSortMergeJoin", True)\
        .config("spark.sql.autoBroadcastJoinThreshold", -1)\
        .config("spark.sql.defaultSizeInBytes", 100000) \
        .config("spark.sql.shuffle.partitions", 16)\
        .config("spark.sql.adaptive.enabled", False)\
        .getOrCreate()
    # config에 설정을 넣어줌
    # SortMergeJoin을 True로 설정
    # BroadcastJoin이 발생하지 않도록 -1로 설정
    # defaultsize를 100000byte로 설정
    # shuffle 할 때의 기본 partition의 개수를 16개로 설정
    # adaptive.enabled를 False로 설정.
    # 만약 True라면, adaptive query 가 활성화됨(다음에 자세히 다룸)

    states = {
        0: "AZ",
        1: "CO",
        2: "CA",
        3: "TX",
        4: "NY",
        5: "MI",
    }

    items = {
        0: "SKU-0",
        1: "SKU-1",
        2: "SKU-2",
        3: "SKU-3",
        4: "SKU-4",
        5: "SKU-5",
    }

    users_df = ss.createDataFrame([[uid,
                                   f"user_{uid}",
                                   f"user_{uid}@fastcampus.com",
                                   states[random.randint(0,5)]]
                                  for uid in range(100000)]) \
        .toDF("uid", "login", "email", "user_state")

    orders_df = ss.createDataFrame([[tid,
                                    random.randint(1,5000),
                                    random.randint(1,10000),
                                    states[random.randint(0,5)],
                                    items[random.randint(0,5)]]
                                   for tid in range(100000)]) \
        .toDF("transaction_id", "login", "uid", "email", "user_state")

    joined_df = orders_df.join(users_df, on="uid")
    joined_df.explain(mode="extended")
    # trigger action
    joined_df.count()

    # while True:
    #     pass

    # SparkUI 에서 SQL/DataFrame  확인
    # 두 개의 데이터 셋(user datafame, order datafame)을 확인할 수 있음
    # Exchange 에서 shuffle을 하고, Sort를 하고, SortMergeJoin을 수행함
    # 두 개의 데이터셋이 같은 방식으로 정렬되어 있지 않아 Sort과정이 들어가게 되는 것임(약간의 시간 소요)
    # 같은 방식으로 데이터의 분포가 되어 있지 않아 shuffle이 발생하는 것도 확인할 수 있음
    # Join과정을 최적화하고 싶다면 과정을 추가해줘야함

    # join 과정을 최적화
    # 최적화 방법
    # 1. uid 키로 사전 정렬
    # 2. 데이터를 저장할 때 uid bucketing - 데이터를 키의 분포에 따라 미리 파티셔닝을 하는 것

    users_df.orderBy(asc("uid")).write.format("parquet")\
        .bucketBy(8, "uid").mode("overwrite").saveAsTable("UsersTbl")

    orders_df.orderBy(asc("uid")).write.format("parquet") \
        .bucketBy(8, "uid").mode("overwrite").saveAsTable("OrdersTbl")

    ss.sql("CACHE TABLE UsersTbl")
    ss.sql("CACHE TABLE OrdersTbl")

    users_bucket_df = ss.table("UsersTbl")
    orders_bucket_df = ss.table("OrdersTbl")

    joined_bucket_df = users_bucket_df.join(orders_bucket_df, on="uid")

    # trigger action
    while True:
        pass

    # SparkUI보면 저장된 테이블을 볼 수 있음
    # Exchange가 없고 데이터를 그대로 가져온 것을 볼 수 있음
    # Sort는 발생하지 시간을 보아 발생하지 않은 것을 볼 수 있음
    # 바로  SortMergeJoin을 수행하게 됨
    # join 연산과 사전정렬 버케팅은 상황에 따라 무거운 것이 달라 잘 선택해야함

