from pyspark import SparkContext, StorageLevel
from pyspark.sql import SparkSession

if __name__ == '__main__':
    ss: SparkSession = SparkSession.builder \
        .master("local") \
        .appName("cache_persistence_ex") \
        .getOrCreate()

    sc: SparkContext = ss.sparkContext

    data=[i for i in range(1, 10000000)]

    rdd = sc.parallelize(data).map(lambda v: [v, v**2, v**3])

    rdd.cache()
    rdd.count()
    rdd.count()
    rdd.count()

    while True:
        pass

    # SparkUI를 보면 Stage의 Duration을 확인할 수 있음
    # count가 3번 일어남
    # cache()를 추가하고 실행
    # 첫 번 째는 증가하지만, 두 번째, 세 번째 스테이지는 캐시가 되어 시간이 줄어듬
