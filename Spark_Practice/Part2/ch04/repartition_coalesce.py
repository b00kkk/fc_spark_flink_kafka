from pyspark.sql import SparkSession

if __name__ == '__main__':
    ss: SparkSession = SparkSession.builder \
        .master("local")\
        .appName("spark_jobs_ex")\
        .getOrCreate()

    df = ss.read.option("header","true") \
        .option("inferSchema", "true") \
        .csv("data/titanic_data.csv")

    # 1. repartition ex)
    # df = df.repartition(10)
    # df = df.repartition(10, "Age")

    # df.cache()


    df=df.repartition(20).where("Pclass=1")\
        .select("PassengerId","Survived")\
        .coalesce(5)\
        .where("Age>=20")

    df.count()

    while True:
        pass


    # SparkUI의 Storage에서 캐싱된 데이터를 확인할 수 있음
    # RDD를 보면 거의 대부분이 균일하게 들어간 것을 볼 수 있음
    # 컬럼을 지정하고 돌려보면 RDD에서 균일하게 들어가 있지 않음
    # 컬럼을 지정했을 때는 컬럼의 값의 분포에 따라 균일하게 되지않을 가능성이 높음

    # coalesce를 넣지 않고 실행시키면 job을 봤을 때 중간 연산에서 20개의 task로 진행됨
    # coalesce를 넣으면 task의 개수가 5개로 됨
