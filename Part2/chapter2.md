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
## RDD 실습
[로그 집계 파이프라인 만들기](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch02_batch/join_rdd_ex.py)
