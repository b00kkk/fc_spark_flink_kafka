from pyspark.sql import SparkSession

if __name__ == '__main__':
    ss: SparkSession = SparkSession.builder\
        .master("local")\
        .appName("spark_jobs_ex")\
        .getOrCreate()

    # 성별(Sex)이 남자 승객의 생존 여부(Survived),
    # 객실 등급(Pclass) 별 평균 운임 비용(Fare) 계산

    df = ss.read.option("header","true")\
        .option("inferSchema","true")\
        .csv("data/titanic_data.csv")

    df = df.repartition(5).where("Sex ='male'")\
        .select("Survived","Pclass","Fare")\
        .groupby("Survived","Pclass")\
        .mean()

    print(f"result ==> {df.collect()}")

    df.explain(mode="extended")

    while True:
        pass

    # Action : Job을 나누는 기준
    # read(), collect()

    # Wide transformation: Stage를 나누는 기준
    # repartition(), groupby()

    # Narrow transformation
    # where(), select()

    # Job2 의 Logical Plan
    # repartition -> where -> select -> group by -> mean

    # Logical plan 기준으로 Stage 구성
    # stage1 : repartition
    # stage2 : where -> select -> group by
    # stage3 : mean

    # Logical Plan 기준 Stage - Deep DIve
    # stage1 에서 1개의 partition을 가지고 있는 데이터가 5개의 partition으로 나뉘어짐
    # 나뉘어진 데이터는 Write Exchange라는 Buffer에 한 번 쓰여지게 됨
    # Write Exchange가 다음 Stage의 input이 됨
    # stage2 에서는 Write Exchange를 읽어 Read Exchange라는 버퍼에 둠
    # 이 부분에서 Executor간에 발생하는 Shuffle/Sort의 과정임
    # 파티션 개수에 해당하는 태스크가 만들어짐
    # 각각의 태스크 내에서 narrow trasformation이 병렬로 실행됨
    # gropu by로 Write Exchange 버퍼로 쓰여지고 다음 stage의 Read Exchange에 input이 됨
    # 그 과정에서 Shuffle/Sort가 됨
    # Read Exchange에서 데이터를 읽어오면 또 다른 transformation연산을 실행하게 됨

    # Job
    # Spark는 각 action을 기준으로 1개의 Job을 생성
    # 1개의 job에는 여러 개의 transformation이 존재할 수 있는데, 스파크 엔진은 이 transformation들을 바탕으로 logical plan을 생성함

    # Stage
    # 만들어진 logical plan을 바탕으로 job을 wide dependency transformation단위로 쪼개 Stage를 생성
    # 만약 wide가 없다면, Job은 1개의 stage만 가지게 뙴
    # N개의 wide transformation이 있다면, Stage는 N+1개가 됨

    # Shuffle/Sort
    # Stage간의 데이터는 Shuffle/sort연산을 통해 복사 후 전달됨

    # Task
    # Spark Job에서 가장 작은 작업 단위
    # 각 stage는 1개 이상의 병렬 task로 수행
    # 만들어지는 task의 개수는 그 stage에 사용되는 Partiton의 개수와 동일
    # task의 개수가 어떻게 세팅되냐에 따라 stage의 처리 시간이 크게 차이나기 떄문에 매우 중요함
    # task의 개수가 작으면 spark의 병렬 처리 능력을 사용하지 못하고, 크면 task들 간의 통신하는 overhead가 커짐
    # 특정 task를 통해 executor에 할당하는 것을 driver의 역할이고, 할당 후에는 각 executor에서 task의 수행을 담당

    # slot
    # 각 Executor에 할당된 core의 개수 만큼 방이 만들어진다는 의미
    # CPU가 4 core 라면  4개의 SLOT이 생성됨
    # task가 slot의 개수보다 크다면 slot수 만큼 우선 처리 후 남은 task는 slot이 비는 것을 기다렸다가 slot이 비면 할당됨

    # Action - collect
    # collect() action 수행시,  executor의 각 task는 Driver로 데이터를 전송
    # 모든 task가 성공했을 때 driver는 이 job이 성공했다고 여김
    # 만약 특정 task가 실패했다면, driver는 그 task를 재시도(그 task를 다른 executor에서 실행할 수도 있음)
    # retry도 실패한다면, driver는 exception을 발생시키고 job은 실패
