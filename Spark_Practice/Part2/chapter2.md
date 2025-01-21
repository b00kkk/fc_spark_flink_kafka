# 배치 프로세싱(Spark SQL/ RDD/ Dataframe)
## Spark RDD
RDD : 스파크의 기본 추상화 객체
- 의존성 정보
  - 어떤 입력을 필요로 하고 현재의 RDD가 어떻게 만들어지는지 스파크에게 가르쳐줌
  - 새로운 결과를 만들어야 하는 경우, 스파크는 이 의존성 정보를 참고하고 연산을 재반복해 RDD를 재생성할 수 있음
- 파티션
  - 스파크에서 작업을 나눠 실행기들에 파티션별로 병렬 연산 할 수 있는 능력을 제공
- 연산 함수
  - Partition을 반복자 형태(Iterator)로 변환하는 함수를 내장하고 있음

## RDD 실습(로그 집계 파이프 라인 만들기)
[원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch02_batch/join_rdd_ex.py)
[내가 정리한 코드](https://github.com/b00kkk/fc_spark_flink_kafka/blob/main/Part2/log_rdd_ex.py)

## SparkSQL, Dataframe, Dataset
1. RDD API의 문제점
- 스파크가 RDD API 기반의 연산, 표현식을 검사하지 못해 최적화할 방법이 없음
  - RDD 기반 코드에서 어떤 일이 일어나는지 알 수 없음
  - Join, filter, groub by 등 여러 연산을 하더라도 람다 표현식으로 밖에 보지 못함
  - 특히 PySpark의 경우, 연산함수 Iterater[T] 데이터 타입을 제대로 인식하지 못함
- 스파크는 어떠한 데이터 압축 테크닉도 적용하지 못함
  - 타입 T에 대한 정보를 전혀 얻을 수 없음
  - 그 타입의 객체 안에서 어떤 타입의 컬럼에 접근한다 해도, 스파크는 알 수 없음
  - 바이트 뭉치로 직렬화해서 사용할 수 밖에 없음
  > -> 스파크가 연산 순서를 재정렬해 효과적인 질의 계획으로 바꿀 수 없음
2. SparkSQL
- 구조호된 데이터를 처리하기 위한 스파크 모듈
- DataFrame, Dataset이라 불리는 높은 차원의 추상화를 제공하고, 분산 SQL 쿼리 엔진의 역할도 수행
- RDD의 문제점을 모두 해결할 수 있음
- SQL 질의 수행
- 스파크 컴포넌트들을 통합하고, Dataframe, Dataset이 여러 프로그래밍 언어에서 정형화 데이터 관련 작업을 단순화할 수 있도록 추상화 해줌
  - RDD를 사용하면 여러 파일 포맷을 못 읽을 수 있음
- 정형화된 파일 포맷에서 스키마와 정형화 데이터를 읽고 쓰며, 데이터를 임시 테이블로 변환
- 빠른 데이터 탐색을 할 수 있도록 대화형 스파크 SQL 셀을 제공
- JDBC 커넥터를 통해 외부의 도구들과 연결할 수 있는 중간 역할 제공
  - 커넥터를 사용해 Tableau, PowerBI 등 여러 애플리케이션과 연동 가능
- 최종실행을 위해 최적화된 질의 계획과 JVM을 위한 최적화 코드 생성
- 장점
  - 성능
    - RDD와 달리, 연산, 표현식, 데이터 타입 정보를 모두 알 수 있음
    - 스파크는 연산 순서를 재정렬해, 더 효과적인 질의 계획으로 변경 가능
    - 카탈리스트 옵티 마이저
      - 연산 쿼리를 받아 실행 계획으로 변환(네 단계의 변환 과정을 거쳐 RDD 생성)
      >  1. 분석  2. 논리적 최적화  3. 물리 계획 수립  4. 코드 생성
  - 표현성
    - 예를 들면 RDD의 경우 람다 표현식을 계산해야 해 직관적으로 알기 어려움
    - SparkSQL은 Dataframe API를 사용하면 명확하게 보임(ex: group by)
  - 일관성
    - scala, python, java 등 프로그래밍 언어와 무관하게 일관성있는 코드를 보여줌
3. Dataframe API
- 구조, 포맷 등 몇몇 연산 등에 있어, 판다스 데이터 프레임에 영향을 많이 받음
- Spark Dataframe은 이름 있는 컬럼과 스키마를 가진 분산 인메모리 테이블처럼 동작
- 사람이 보는 형태로는 표의 형태를 보임
- 데이터 타입
  - 기본 타임
  > Byte, Short, Integer, Long, Float, Double, String, Boolean, Decimal
  - 정형화 타입
  > Binary, Timestamp, Date, Array, Map, Struct, StructField
  - 실제 데이터를 위한 스키마를 정의할 때 타입들이 어떻게 연계되는지를 아는 것지 중요
- 스키마
  - Dataframe을 위해 컬럼 이름과 연관된 데이터 타입을 정의한 것
  - 외부 데이터 소스에서 구조화된 데이터를 읽어 들일 때 사용
  - 스파크에서는 미리 스키마를 정의하지 않아도 됨
    - 데이터를 보고 스키마를 추론하게 됨
    - 일반적으로 스키마를 미리 정의하기는 함
    - 미리 스키마를 정의하면 스파크가 데이터 타입을 추측해야하는 책임을 덜어줌
    - 스파크가 스키마를 확정하기 위해, 파일의 많은 부분을 읽어 들이려고 별도의 잡을 만드는 것을 방지
    - 데이터가 스키마와 맞지 않는 경우, 조기에 문제 발견 가능
  - 정의 방법
    - 프로그래밍 스타일
    - DDL
4. Dataset API
- 원래는 분리가 되어있었는데 스파크 2.0에서 개발자들이 한 종류만 알면 되도록 Dataframe API, Dataset API를 하나로 합침
- Dataset은 정적 타입과 동적 타입을 모두 가짐
- 그렇기에 Java와 Scala에서만 사용 가능, Python과 R은 DataFrame만 사용 가
  - Java와 Scala는 타입 안전을 보장, Python과 R은 타입 안전을 보장하지 않음
- Scala에서는 case class, Java에서는 JavaBean 클래스를 사용해 Dataset이 쓸 스키마를 지정할 수 있음
- 트랜스포메이션, 액션 연산들도 사용 가능
- 사용되는 동안, 하부의 스파크 SQL엔진이 JVM 객체의 생성, 변환, 직렬화, 역직렬화를 담담
- Dataset Encoder의 도움을 받아 Off-heap 메모리 관리
- Dataset과 Dataframe의 가장 큰 차이는 오류가 발생되는 시점이다
  - Dataset은 타입 안전이 항상 보장되어 문법 오류와 분석 오류가 모두 컴파일 시점에 잡힘
  - Dataframe은 동적 API에 기반하기에 문법 오류는 컴파일 시점, 분석 오류는 런타임 시점에 잡을 수 있음
  - SQL 형태로 사용하면 모두 런타임 시점에 잡을 수 있음

## Dataframe API 실습(로그 집계 파이프라인 만들기)
[원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch02_batch/log_dataframe_ex.py)
[내가 정리한 코드](https://github.com/b00kkk/fc_spark_flink_kafka/blob/main/Spark_Practice/Part2/log_dataframe_ex.py)

## SQL API 실습(로그 집계 파이프라인 만들기)
[원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch02_batch/log_sql_ex.py)
[내가 정리한 코드[(https://github.com/b00kkk/fc_spark_flink_kafka/blob/main/Spark_Practice/Part2/log_sql_ex.py)
