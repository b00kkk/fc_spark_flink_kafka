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
  
## 스파크 메모리 관리
### Executor 메모리 구조
- Ex)
    - memory=8GB, cores=4 라면, default Memory overhead: 800MB
    - JVM Heap = 8GB(memory overhead는 이의 0.1배여서 800MB로 가정)
- overhead 영역의 JVM heap 영역이 꽉차있을 때 추가로 담을 수 있는 버퍼 공간이라 생각하면 됨
- JVM Heap
  - Reserved Memory
    - 스파크 엔진이 고정적으로 점유하는 영역(변경 불가)
  - Spark Memory(Reserved Memory를 제외하고 40%)
    - Dataframe 연산(transformation, map, filter, action, count 등)에 사용
    - Dataframe이 RDD로 컴파일 되더라도 User Memory를 사용하지는 않음
  - User Memory(Reserved Memory를 제외하고 60%)
    - spark Memory를 할당하고 남는 영역
      - User-defined
      - Spark 내부 메타데이터
      - UDF 함수
      - RDD conversion 연산
      - RDD 계보, 의존 관계
- Spark Memory
  - Storage Memory Pool(50%)
    - 캐싱된 데이터가 저장되는 영역
  - Executor Memory Pool(50%)
    - 데이터프레임 연산을 위한 Buffer
- Slot
  - 각각의 CPU Slot은 process가 아닌 Thread 단위로 만들어짐
  - Executor 당 1개의 JVM 존재
  - 각 slot이 Executor Memory pool을 공평하게 차지
  - Spark 1.6 까지는 기본 설정
- unified memory manager
  - 활성화된 task를 기준으로 공평하게 자원을 분배
  - 4개의 슬롯 중 2개의 슬롯만 활성화된다면?
    - 비활성화된 슬롯은 Executor memory pool에 할당하지 않고, 할성화된 slot만 할당
    - 만약 Executor memory pool이 꽉 차면, Storage memory pool영역도 사용이 가능
    - 반대로 캐싱해야할 데이터가 많아 Storage Memory pool이 꽉 차면 Executor momory pool 영역도 사용 가능
- 메모리 사용 시나리오
  - Dataframe을 캐싱하여 storage memory pool이 꽉 찬 상태
  - 더 캐싱해야 한다면 Executor memory pool의 남는 영역을 사용
  - Task가 실행된다면 Executor Memory Pool에 CPU Slot을 할당
  - Executor Memory Pool도 꽉 찬다면 캐시데이터는 Disk로 Spill, 남는 영역은 Slot이 차지
  - Executor Memory Pool은 원래 Slot이 차지해야하는 영역이기 때문
  - EXeuctor Memory가 더 필요하다면 Memory manager는 필요 없는 데이터들을 disk로 spill 시도
  - 만약 Spill이 안되면 OOM(Out Of Memory)이 발생
- 메모리 관련 Spark 파라미터 정리
  - spark.executor.memoryOverhed
  - spark.executor.memory(=total JVM Heap size)
  - spark.memory.fraction(=JVM Heap 중, reserved 영역을 제외하고 Dataframe 연산에 사용하게 될 영역의 비율)
  - spark.memory.storageFraction(=DataFrame 영역 중 캐시 영역의 비율)
  - spark.executor.cores(=한 executor 내에서 최대로 사용 가능한 스레드의 개수)
    - 너무 작게 세팅하면, 리소스를 온전히 사용하지 못함
    - 너무 크게 세팅하면, 스레드간 경합 발생
    - 권장 : 2~4
- Off Heap
  - 대부분의 스파크 연산, 데이터 캐싱은 JVM Heap 내에서 발생
  - heap 메모리를 사용할 때 효율적인 경우가 많으나 JVM heap은 garbage collection이 발생함
    - Exector의 heap 메모리에 많은 양의 데이터를 할당할 때, GC delay가 크게 발생할 수 있음
  - Spark 3.0+ 에서는 off-heap 메모리에서 몇몇 연산을 수행하는 것이 최적화
  - 연산 수행시 큰 메모리 사이즈를 요구할 때, on-heap, off-heap을 섞는 것이 GC delay를 줄이는데 도움이 됨
  - 기본 설정은 off-heap을 사용하지 않음
  - Off heap size 설정
    - 기존 JVM heap 내의 Storage Memory Pool, Executor Memory pool이, off-heap 영역에도 일부 할당될 수 있음
- pyspark memory
  - Scala, Java가 아닌 pyspark 사용시, Python worker가 추가로 필요할 수 있음
  - python worker는 JVM Heap memory를 직접 사용하지 못함
    - off-heap, overhead memory를 사용해야함
  - 두 memory 외에 추가로 memory가 필요할 때, spark.executor.pyspark.memory 파라미터를 세팅
  - 기본 세팅은 spark.executor.pyspark.memory를 사용하지 않는 것
    - 대부분의 pyspark application의 경우, 외부 python 라이브러리를 필요로 하지 않음

## Partitioning 개요 및 중요성
- Partition
  - 스파크에서 partiton은, 데이터를 논리적인 연산 단위인 chunk로 나눈 것을 의미
  - chunk로 나눌 때, 데이터의 분포는 완전히 랜덤일 수도 있고, 특정한 규칙이 있을 수 있음
  - 기본적으로 1개의 Partition에 대한 연산은, 1개의 task에서 수행
    - Partiton과 task는 1:1 관계
  - Partition을 스파크 프레임워크의 병렬 처리의 단위라고 볼 수 있음
- Partitioning
  - Partiton을 만드는 방법
  - 이 과정에서는 두 가지를 고려해야함
    - Partition의 개수
    - Partition의 개수가 주어졌을 때 데이터가 어떻게 분배되는지
  - Spark에서 기본으로 제공하는 partitioning 방법
    - Hash Partitoning
      - 데이터의 각 행을 대표하는 Key(Scala, Java의 Pari RDD에서의 key 등)을 hash function에 넣어 나온 hashcode를 기반으로 partitioning
    - Range Partitioning
      - 각 partition마다 특정 범위를 가지고 있고, 그 범위는 정렬가능한 Key값들을 전체 데이터에서 일부를 샘플링해서 결정함
      - 항상 같은 값들로 샘플리 하지 않으므로, 항상 같은 범위임을 보장하기 어려움
    - 범위가 정해지면, 나머지 값들을 범위에 맞게 Partitioning
  - Partitioning in RDD
    - 다양한 input data source(parquet file, HDFS, RDBMS, HIVE table 등)
    - 미리 정의된 rule에 따라 input data가 RDD의 Partition으로 변환됨
    - input data와 partition이 꼭 1:1로 대응되어아 하는 것은 아님
    - rule이 어떠한 partitioner를 사용할 것인가를 확인
    - RDD의 경우 HashPartitoner, RangePartitoner 외에, 데이터의 특성에 더 맞는 Custom partitoner를 구현 가능
      - Scala, Java의 경우 추상클래스인 Partitioner를 상속 받아 구현되지만 Pyspark에서는 지원 X
      - Pyspark에서는 특정 더미 컬럼을 만들고, 더미컬럼의 키값을 기준으로 파티셔닝함
    - RDD 타입의 변수 A가 있다고 하면, A.partitioner()식으로 가져올 수 있음
    - A와 B가 같은 partitoner를 사용해 partitioning 되어있다면, narrow transformation이 될 수 있음
      - Shuffle이 발생하지 않음
    - Partitoner 정보가 None이 아닌 input RDD에서 transformation 수행시 partition 정보는 항상보존 되는 것은 아님
      - 예시로 java,scala에서 PariRDD의 mapTopar 연산이 있음
      - mapToPari 연산을 한다는 것은 Key값 자체가 달라질 수 있는 가능성이 존재
      - Key값이 하나라도 변한다면 spark의 partitoner가 보장했던 데이터 분포의 일관성을 깨뜨림
      - Pyspark에서는 map 함수도 비슷함
    - Dataframe은 RDD와 비슷하지만, 차이점은 존재
      - DataFrame, Dataset에서는 custom partitioner를 생성할 수 없음
      - 대신 partitoning에 사용할 column들을 지정해줄 수는 있음
- Partitoning의 중요성
  - 병렬 처리 성능
    - partitoning을 어떻게 했는지에 따라, 동일한 input data에 대해서도 stage별 lead time이 크게 달라짐
      - Partitioning을 어떻게 했는지의 따라 병렬 처리의 능률이 달라짐
      - 무조건 파티션을 늘리는게 좋은 것은 아님(small file problem)
  - 장애 회복
    - 스파크에서 잡 실패는 partiton level로 관리
    - row 1개 연산이 실패하면, 그 row가 포함된 전체 partition을 재연산해야함
      - partition 사이즈가 너무 크다면, 재연산의 오버헤드가 커질 수 있음
  - Data Shuffling
    - input과 output 데이터 상태는 Partitioning 과정 자체에 영향을 미침
    - output partition 수 보다 input partition 수기 매우 작을 때
      - Shuffle 연산을 시작하는 시점에 과부하가 발생
      - input partition1개당 사이즈가 더 크기 때문
    - output partition 수 보다 Input partition 수가 매우 클 때
      - Shuffle 완료 후에, 완료된 데이터를 가져오는 과정에서 부하 발생
      - output partition 1개당 사이즈가 더 크기 때문
    - 두 케이스 모두 shuffle 연산에서 지연이나 에러를 발생할 수 있음
  - 연산의 효율성 증가
    - join, aggregation연산 수행시, 대상이 되는 데이터들의 partitioner가 동일
        - wide transformation이 아닌 narrow transformation 수행 -> shuffle 연산 방지
  - Data skew 문제
    - partition 간의 데이터 사이즈 차이가 큰 경우
    - 병렬 처리 애플리케이션에서 data skew는 큰 성능 저하의 원인이 될 수 있음
      - 크기가 작은 partition들의 연산이 아무리 빨리 수행되었을더라도, skew된 partition에서의 연산이 끝나지 않으면 다음 stage로 넘어갈 수 없음
    - file 형태로 데이터를 쓸 때도, File 간  skew 문제가 발생할 수 있음

## Repartition, Calesce에 대한 이해
- Repartition
  - Wide dependency transformation -> Shuffle 동반
  - RDD
    - repartiton(numPartitions)
  - DataFrame
    - repartition(numPartitions, *cols)
      - Hash 기반의 partitioning
    - repartitionByRange(numPartitons,*cols)
      - 값들의 범위를 기반으로 하는 partitioning
      - partitioning의 범위를 정하기 위해, 데이터 샘플링 작업을 수행
      - 아웃풋이 항상 똑같지 않을 수 있음
  - output partiton 개수
    - 기본적으로 파라미터로 넘겨준numPartitons
    - 만약 numPartitons를 넘기지 않았다면, spark.sql.shuffle.partitions 값을 사용
      - default = 200
  - Repartition은 Shuffle을 동반하기 때문에 함부로 사용하면 안됨
    - 사용 전, 후 성능이 어떻게 변하는지 모니터링
    - 사용하면 좋은 경우
      - DataFrame reuse and repeated column filters
        - 이 때는 filter로 사용되는 column에 대해 DF를 repartition 해놓으면 좋음
      - DataFrame/RDD의  partition이  skewd 되어 있을 때
        - size가 큰 일부 partition 떄문에 전체 stage를 처리하는 시간이 증가
      - DataFrame/RDD의 partiton 개수가 너무 작을 때
        - 각 partition 크기가 너무 크면 spark의 병렬성을 제대로 활용하지 못함
    - Partiton의 개수를 줄이는 목적으로 사용하는 것은 일반적으로 좋지 않음
      - 줄일 때는 Repartition이 아닌 Calesce를 사용하는 것이 좋음
- Coalesce
  - Narrow dependency transformation -> Shuffle 발생하지 않음
  - RDD
    - coalesce(numPartitons)
  - DataFrame
    - coalesce(numPartitons)
  - Coalesce는 shuffle/sort가 발생하지 않기 때문에 partition isze를 줄이는데는 일반적으로 repartition보다 좋음
  - lacla(같은  Executor)내의 partition들을 결합하기만 함
  - Coalesce는 partition의 개수를 증가시키지 않음
  - Coalesce는 skewed partition을 생성할 수 있음
  - Narrow transformation이기 때문에, coalesce()가 속한  stage내에서, 병렬성을 안좋게 할 수 있음
  - coalesce를 하지 않았다면, where,sleect transformation이 repartiiton의  task를 수행했을 것임

## Caching, Persisitence에 대한 이해
- 동일한 RDD나, Dataframe의 transformation 연산을 중복으로 하지 않기 위해 사용
  - transformation 연산이 lazy evaluation, 즉 action이 실행될 때 실제로 transformation 연산이 수행된다는 것을 인지해야함
- cache()는 내줍적으로 Persistence를 호출
  - 메모리에만 데이터를 캐싱
- persisit()는 다양한 StorageLevel에 데이터를 캐싱할 수 있음
  - MEMORY_ONLY
  - DISK_ONLY(MEMORY_ONLY 대비 더 큰 사이즈의 데이터 캐싱 가능, 속도가 느림)
  - MEMORY_ONLY_2(캐싱을 두 번 함, 더 안전함)
  - OFF_HEAP
- Caching 유무 비교
  - 캐싱을 하는 데에도 리소스가 필요하기 때문에, 처음에는 오래걸림
  - 다음 스테이션에서부터는 캐싱 적용시 더 빨라짐
- 캐싱된 RDD, Dataframe의 경우 UI에서 초록색으로 표시됨
- Caching, Persistence를 사용
  - 좋은 경우
    - 큰 RDD, DataFrame에 반복적으로 접근해야 되는 경우
      - 머신러닝 학습 등
  - 사용하면 안되는 경우
    - DataFrame이 메모리에 들어가기는 너무 큰 경우
    - 크기에 상관없이, 자주 쓰지 않는 dataFrame에 대해 비용이 크지 않은 transformation 수행
  - 메모리에만 cahce()의 경우, 직렬화, 비직렬화 과정이 동반되기 때문에 주