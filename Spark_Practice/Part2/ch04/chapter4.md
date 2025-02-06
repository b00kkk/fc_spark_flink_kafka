# Spark 심화 개념

## 스파크 클러스터, 아키텍처에 대한 이해
- Spark cluster
    - spark application을 구동하기 위한 분산 클러스터
    - ex)
        - 10개의 worker done
        - 각 worker node 당 capacity
            - 8 CPU cores
            - 32 GB RAM
        - cluster의 capacity
            - 80 CPU cores
            - 320GB RAM
- 런타임 아키텍처
    - worker node의 스펙이 Yarn RM이 할당한 스펙보다 크거나 같아야함
    - Application Master(AM) container
        - AM container 내에는 main()이 존재
        - Pyspark에서는 Python wrapper는 Py4J라는 라이버러리로 JVM내의 Java wrapper를 호출
        - 그 후 JVM 내의 Scala application이 실행됨
            > 스파크의 코드 구조
            > Python Wrapper -> Java Wrapper -> Scalacore
        - Application Driver는 실제 데이터를 분산 처리 하지 않음
        - 실제 데이터는 Excutor Node에서 처리됨
    - AM container + Yarn RM + Executor Container
        - Python에서 Py4J 라이브러리를 통해 JVM의 main() 호출
        - JVM(Application Driver)는 Yarn RM에 Executor container생성 요청
        - Executor Container 생성
        - 각 워커노드에 JVM 하나씩 만들어냄
        - 만들어 낸 후, Driver가 각 Executor 에 작업 할당
    - Pyspark에 포함되지 않은 라이브러리 및 UDF 사용시
        - 각 Executor 별로 Python worker가 추가로 생성
        - JVM내에서 작업 수행을 위해 Java 코드로 변환됨
        - Pyspark만 사용시에는 필요 없음
    
## Depoy mode - cluster, clinet mode
1. Deploy mode
- 크게 cluster mode, clinet mode 존재
- Cluster mode
    - 명령어 : spark -submit --master yarn --deploy-mode cluster
- Client mode
    - 명령어 : spark-submit --master yarn --deploy-mode client
2. Cluster mode
- 실행과정
   - client machine에서 client가 spark submit 명령어를 통해 Yarn RM에 잡을 제출
   - Yarn RM은 AM컨테이너에서 spark Driver를 구동하도록 함
   - Driver는 Yarn RM에 Executor container를 위한 자원 요청
   - Yarn RM은 executor container들을 실행하고, Driver에 executor 관리를 위임
- Cluster mode에서는 AM, Executor container 모두 Spark cluster의  worker node 에서 실행
- 즉, 한 번 client가 잡을 제출하면, clinet machine에서는 Spark 구동에 대해서 관여를 하지않음
3. Clinet mode
- 실행과정
    - client machine에 있는 client가 spark submit 명령어를 입력
    - client는 잡을 Yarn RM이 아닌, client machine에 있는 driver JVM에 제출
    - Driver는 Yarn RM에  executor container를 위한 자원을 요청
    - Yarn RM은 executor container들을 실행하고, Driver에 executor 관리를 위임
4. Cluster mode와 Clinet mode 비교
- 가장 큰 차이점은 Driver application의 위치
    - Cluster mode : Driver가 Spark cluster의 worker node에 위치
    - Client mode : Driver가 spark cluster가 아닌 client machine에 위치
- 두 모드에서 executor는 모두 spark cluster에 위치
- production 환경에서는 거의 무조건 cluster mode를 사용
    - Driver, Executor, Yarn RM 모두 Spark cluster에 위치하기 떄문에, client 머신과의 의존 관계 없음
    - 성능적인 면에서 client 대비 driver,executor가 network상에서 가까이 있을 가능성이 높음
        - network latency 감소
- Client mode를 사용하는 경우
    - interative workload
        - driver가 local에 있기 떄문에, 커뮤니케이션이 쉬움
    - spark 잡의 로그를 쉽게 보고자 할 때 사용

## Spark - action, stage, shuffle, task, slot 확인 실습
[원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch04_advanced/spark_jobs_ex.py)

## JOIN의 종류

- Join
    - RDD나 Dataframe의 형태로 되어 있는 두 데이터를 공통적으로 일치하는 키를 기준으로 병합하는 연산
    - Join 연산들은 Executor 사이의 방대한 데이터 이동이 발생할 수 있음
    - 그렇기에 데이터 이동(셔플)을 최소화하는 것이 Spark 성능의 핵심 요소
- Join의 종류
    - Broadcast Hash Join (BJH)
        - map-side only join 이라고도 함
        - 큰 데이터셋과, 작은 데이터셋을 join 할 때 사용
        - Broadcat 변수를 이용해서 더 작은 쪽의 데이터는 Spark Driver에 의해 모든 Executor에 복사가 됨
        - 각각의 Executor에 나뉘어 있는 나뉘어 있는 큰 데이터 파티션과 각각 join의 연산이 수행됨
        - 데이터 교환, 즉 Shuffle이 거의 발생하지 않아 효율적
        - 작은 데이터가 너무 크면 문제가 발생할 수도 있음
        - 관련 파라미터
            - spark.sql.autoBroadcastJoinThreshold (default:10MB)
            - 데이터 셋의 크기가 이 파라미터에서 정의한 Threshold 이하라면 자동으로 BHJ를 수행
    - Sort Merge Join (SMH)
        - 정렬 가능하고 겹치지 않으면서, 공통의 파티션에 저장이 가능한 공통의 키를 기반으로 큰 두 종류의 데이터셋을 합칠 수 있는 방법
        - 두 데이터가 모두 클 때 사용하는 Join
        - 해시 가능한 공통 키를 가지면서, 공통 파티션에 존재하는 두 가지의 데이터셋을 사용
            - 두 개의 데이터셋에 Join하려는 동일 키를 가진 데이터셋의 모든 row가 동일 executor의 동일 파티션에 존재하도록 Shuffle 작업이 필요
            - 데이터 저장 방식, 파티셔닝 방법 등에 따라 생략될 수 있음
        - Sort, Merge 두 단계 
            - Sort
              - 각 데이터 셋을 join 연산에 사용한 키를 기준으로 정렬
            - Merge
              - 각 데이터 셋에서 키 순서대로 데이터를 순회하며, 키가 일치하는 Row끼리 병합
        - 관련 파라미터
          - spark.sql.join.preferSortMergeJoin
    - Shuffle Hash Join (SHJ)
    - Broadcast Nested Loop Join (BNLJ)
    - Catersian Product Join
    - 일반적으로 가장 효율 적인 Join은 BJH와 SMH 임

### Broadcast Hash Join (BHJ) 실습
[원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch04_advanced/join_broadcast_hash_join_ex.py)

### Sort Merge Join (SMH) 실습
[원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch04_advanced/join_sort_merge_join_ex.py)

## 스파크에서의 메모리 할당
- Driver 메모리 할당
  - 관련 파라미터
    1. JVM memory(spark.driver.memory) - default = 1GB
    2. Overhead(spark.driver.memoryOverhead) - default = 0.1 (10% or 384MB)
    - Overhead란, JVM head이 아닌 공간으로 JVM이 아닌 프로세스를 처리하는데 사용됨
- Executor 메모리 할당
    - 관련 파라미터
      1. Heap Memory(spark.executor.memory)
      2. Overhead Memory(spark.executor.memoryOverhead)
        - Non-JVM 프로세스들이 처리되는 공간
        - ex) 셔플 데이터 교
      3. Offheap Memory(spark.memory.offHeap.size)
      4. Pyspark Memory(spark.executor.pyspark.memory)
        - Scala나 Java를 사용하는 경우 고려할 필요강 없음
        - Pyspark를 사용할 때, 파라미터를 따로 지정하지 않으면 파이썬의 메모리를 얼마나 쓰는지 제한하지 않음
        - 파이썬외의 다른 non-JVM 프로세스와 공유하는 오베헤드 메모리 공간을 초과하지 않도록 하는 것이 spark application의 역할
    - Offheap, PysparkMemory가 양수 값으로 세팅이 된다면 Overhead 영역에 포함됨
  