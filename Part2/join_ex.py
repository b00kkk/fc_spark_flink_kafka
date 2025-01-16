from pyspark import SparkContext
from pyspark.sql import SparkSession

def load_data(from_file: bool, sc: SparkContext):
    if (from_file):
        return load_data_from_file(sc)
    return load_data_from_in_memory(sc)

def load_data_from_file(sc: SparkContext):
    return sc.textFile("data/user_visits.txt").map(lambda v: v.split(",")),\
        sc.textFile("data/user_names.txt").map(lambda v: v.split(","))

def load_data_from_in_memory(sc: SparkContext):

    #[user_id, visits]
    user_visits = [
        (1, 10),
        (2, 27),
        (3, 2),
        (4, 5),
        (5, 88),
        (6, 1),
        (7,5)
    ]
    # [userid, name]
    user_names = [
        (1, "Andrew"),
        (2, "Chris"),
        (3, "John"),
        (4, "Bob"),
        (6, "Ryan"),
        (7, "Mali"),
        (8, "Tony"),
    ]

    return sc.parallelize(user_visits), sc.parallelize(user_names)


if __name__ == '__main__':
    ss : SparkSession = SparkSession.builder\
        .master("local")\
        .appName("rdd examples ver")\
        .getOrCreate()
    sc: SparkContext = ss.sparkContext

    user_visits_rdd, user_names_rdd = load_data(True, sc)

    # print(user_visits_rdd.take(5))
    # print(user_names_rdd.take(5))

    # a) Chris의 방문 횟수를 출력
    joined_rdd = user_names_rdd.join(user_visits_rdd).sortByKey()
    # print(joined_rdd.take(5))

    result = joined_rdd.filter(lambda row: row[1][0] == 'Chris').collect()
    #print(result)

    # inner, left outer join, right outer join, full outer join
    inner = user_names_rdd.join(user_visits_rdd).sortByKey()
    print(inner.collect())
    # inner 동시에 존재하는 경우만 출력됨(5,8 이 없음)

    left_outer= user_names_rdd.leftOuterJoin(user_visits_rdd).sortByKey()
    print(f"left ==> {left_outer.collect()}")
    # 좌측에 있는 것만 결과에 나옴

    right_outer = user_names_rdd.rightOuterJoin(user_visits_rdd).sortByKey()
    print(f"right ==> {right_outer.collect()}")
    # 우측에 있는 것만 결과에 나옴

    full_outer = user_names_rdd.fullOuterJoin(user_visits_rdd).sortByKey()
    print(f"full==> {full_outer.collect()}")
    # 어느 한 쪽에 존재하면 일단 결과를 보여줌

    
