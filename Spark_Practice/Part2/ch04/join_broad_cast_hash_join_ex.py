import random

from pyspark.sql import SparkSession
from pyspark.sql.functions import broadcast

if __name__ == '__main__':
    ss: SparkSession = SparkSession.builder \
        .master("local") \
        .appName("broadcast_hasy_join_ex") \
        .getOrCreate()

    # big
    big_list = [[random.randint(1,10)] for _ in range(1000000)]
    big_df = ss.createDataFrame(big_list).toDF("id")

    # small
    small_list = [[1,"A"], [2,"B"], [3,"C"]]
    small_df = ss.createDataFrame(small_list).toDF("id","name")

    joined_df = big_df.join(broadcast(small_df), on="id")

    joined_df.show()

    while True:
        pass

    # SparkUI 확인
    # SQL/DataFrame 확인
    # Row 가 3인 작은 데이터셋
    # Broadcast Exchange, 즉 driver에서 executor로 데이터가 복사되는 과정을 통해 Exchange가 발생
    # 큰 데이터셋은 작은 데이터셋이 broadcast 변수가 되어 BroadcastHashJoin을 수행하게 됨
    # BroadcastExchange가 발생하고 Shuffle이 발생하지 않는 것을 UI에서 확인할 수 있음

    