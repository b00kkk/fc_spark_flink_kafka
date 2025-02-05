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
