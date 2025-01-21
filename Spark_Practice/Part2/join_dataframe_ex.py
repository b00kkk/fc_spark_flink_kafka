from pyspark.sql import SparkSession
from pyspark.sql.types import *


def load_user_visits(ss: SparkSession):
    schema = StructType([
        StructField("user_id", IntegerType(), False),
        StructField("visits", IntegerType(), False),
    ])

    data = [
        (1, 10),
        (2, 27),
        (3, 2),
        (4, 5),
        (5, 88),
        (6, 1),
        (7, 5)
    ]

    return ss.createDataFrame(data, schema)


def load_user_names(ss: SparkSession):
    schema = StructType([
        StructField("user_id", IntegerType(), False),
        StructField("name", StringType(), False),
    ])

    data = [
        (1, "Andrew"),
        (2, "Chris"),
        (3, "John"),
        (4, "Bob"),
        (6, "Ryan"),
        (7, "Mali"),
        (8, "Tony"),
    ]

    return ss.createDataFrame(data, schema)


if __name__ == "__main__":
    ss: SparkSession = SparkSession.builder \
        .master("local") \
        .appName("dataframe join ex") \
        .getOrCreate()

    user_visits_df = load_user_visits(ss)
    user_names_df = load_user_names(ss)

    # 1) 컬럼 지정 X : cartesian join  (row : M x N 생성) -> Not good!!!
    # user_names_df.join(user_visits_df).show()

    # 2) inner join
    #user_names_df.join(user_visits_df, on="user_id").show()
    # user_names_df.join(user_visits_df, on="user_id", how="inner").show()
    # -> how를 넣나 안넣나 기본값이 inner이기에 같음

    # 3) left outer join
    user_names_df.join(user_visits_df, on="user_id", how="left").show()
    # user_names_df 의 내용이 없어도 user_visits_df 의 내용도 같이 나

    # 4) right outer join
    user_names_df.join(user_visits_df, on="user_id", how="right").show()
    # user_visits_df의 내용이 없어도 user_names_df의 내용이 나

    # 5) full outer join
    user_names_df.join(user_visits_df, on="user_id", how="outer").show()
    # 양 테이블에 없더라도 다 나옴
    # .explain() -> Physical Plan 확인.
