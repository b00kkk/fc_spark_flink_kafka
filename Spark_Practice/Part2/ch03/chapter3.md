# 스트림 프로세싱

## Structured Streaming
Batch Processing은 고정된 Dataset에 대해 한 번만 연산을 하는 거 였다면, \
Stream Processing은 끝없이 들어오는 데이터의 흐름을 연속적, 준 실시간으로 처리
- 두 가지 방법론이 존재 함
    - 레코드 단위 처리 모델
        - 각 노드는 지속적으로 한 번에 한 개의 레코드를 받게 됨
        - 그 레코드를 처리하여 생성된 다른 레코드는 그래프 상의 다음 노드로 보냄
        - 장점 : 응답시간이 매우 짧음
        - 단점 : 높은 처리량을 달성하기 어렵고, 특정 노드에 장애 발생시 복구가 어려움
    - 마이크로 배치 스트림 처리 모델
        - Spark Straming 에서 기본적으로 취하는 방법
        - Stream procesiing을 아주 작은 Batch Processing을 처리하는 방식으로 생각
          - 마이크로 배치 단위로 입력 데이터를 구분
          - 입력 데이터를 각 노드에서 태스크 단위로 처리
          - 마이크로 배치 단위로 구분된 데이터가 출력
        - 장점 : 높은 처리량
        - 단점 : 느린 반응 속도
        - 대부분의 파이프라인에서 ms 단위의 반응속도가 필요하지 않고, 다른 곳에서 지연이 발생할 가능성이 있어 채택함
- Spark에서는 Batch와 Stream을 다루는 코드가 비슷함
    - Dstream
        - Batch의 RDD API 기반으로 작성
        - RDD API와 마찬가지로, 개발자들이 작성한 코드와 동일한 순서로 연산을 수행
            - 카탈스트 옵티마이저에 의한 자동 최적화 발생x
        - Event time window 지원 부족(Processing time window만 지원)
            - Event time은 스트림의 이벤트가 발생한 시간을 말함
            - Processing time은 만들어진 이벤트가 스파크 스트리밍에 들어온 시점을 말함
    - Spark Structured Streaming
        - Dataframe API 기반으로 작성
        - Dstream의 단점을 극복
        - Streaming processing 코드 작성이 Batch Processing 만큼 쉬어야한다는 원칙을 가지고 설계함
    - 데이터의 Stream을 무한하게 연속적으로 추가되는 데이터의 테이블 개념으로 간주
    - 매번 결과 테이블이 갱신될 때 마다 세 가지 기능을 제공
        - append 모드 : 지난 트리거 이후로 결과 테이블에 새로 추가된 행만 외부 저장소에 기록
        - update 모드 : 지난 트리거 이후에 결과 테이블에 갱신된 행들만 외부 저장소에 기록
        - complete 모드 : 갱신된 전체 테이블을 외부 저장소에 기록

## Structured Streaming 실습 
### 실시간 로그 집계 파이프라인 만들기
- [원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch03_streaming/streaming_dataframes_ex.py)
- [내가 정리한 코드](https://github.com/b00kkk/fc_spark_flink_kafka/blob/main/Spark_Practice/Part2/ch03/streaming_dataframe_ex.py)

### Join
- [원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch03_streaming/streaming_dataframes_join_ex.py)
- [내가 정리한 코드](https://github.com/b00kkk/fc_spark_flink_kafka/blob/main/Spark_Practice/Part2/ch03/streaming_dataframe_join_ex.py)

## Dstream 실습 
### read, write
- [원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch03_streaming/dstream_ex.py)
- [내가 정리한 코드](https://github.com/b00kkk/fc_spark_flink_kafka/blob/main/Spark_Practice/Part2/ch03/dstream_ex.py)

### transforamtions
- [원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch03_streaming/dstream_transformations_ex.py)
- [내가 정리한 코드](https://github.com/b00kkk/fc_spark_flink_kafka/blob/main/Spark_Practice/Part2/ch03/dstream_transformation_ex.py)

## Event Time windows, Processing Time windows
### window function
- 데이터의 특정한 범이를 설정하고, 그 범위 내에서 집계 함수 등을 적용
- spark streaming에서는 time-based window만을 사용(다른 기반의 window 사용시 에러 발생)
- window duration : window의 크기
- window sliding interval : window의 간의 간격
- 크게 세 가지 방식의 window가 존재
    - sliding window
        - 각 window의 크기는 고정
        - window 간의 겹치는 구간 존재
        - duration과 interval의 크기가 달라 겹치는 구간이 발생
    - tumbling window
        - 고정 크기의 window
        - 겹치는 window가 없음
        - interval과 duration이 같음
    - session window
        - 동적으로 달라짐
        - 처음 window가 만들어진 후, record/event가 설정한 gap duration내에 들어는 한 확장
        - gap duration내에 event/record가 들어오지 않는다면 window가 끝나고, 새로운 window를 생성
### Event time windows
- event time을 기준으로 input record를 처리
    > event time: record/event가 실제로 생성된 시점(spark streaming application에 들어온 시간과는 다름)
- 일반적으로 event time은 input record의 column으로 제공됨
- Dstream에서는 event time을 기준으로 작업하는데 한계가 있음
- Structured streaming 에서는 window function을 제공함
### Processing time windows
- Processing time을 기준으로 input record를 처리
    > Processing time : spark streaming application에 들어온 시간
- 일반적으로 processing time은 spark에서 처리리하는 시간이라 input record에는 포함되어 있지 않음
- current_timestamp 메서드를 통해 생성
### event + window
- output mode = COMPLETE
    - 이전에 쓰여 있던 테이블의 결과를 모두 가져옴
- output mode = UPDATE
    - 업데이트가 된 window에 대해서만 사용함
- output mode = APPEND
    - 추가된 이벤트에 대해서만 테이블로 사용됨

## Event TIme windows, Processing Time windows 실습
### Event Time windows
- [원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch03_streaming/event_time_windows_ex.py)
- [내가 정리한 코드](https://github.com/b00kkk/fc_spark_flink_kafka/blob/main/Spark_Practice/Part2/ch03/event_time_windows_ex.py)
### Processing Time windows
- [원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch03_streaming/processing_time_windows_ex.py)
- [내가 정리한 코드](https://github.com/b00kkk/fc_spark_flink_kafka/blob/main/Spark_Practice/Part2/ch03/procesing_time_window_ex.py)

## Watermark
- 처리된 데이터에서 쿼리에 의해 검색된 event time의 최댓값보다 뒤쳐지는 동적인 임계값
- 이 임계값 이전에 event time을 가지는 event는 쿼리 집계 대상에서 제외됨
- 이 Watermark를 사용하면, spark 쿼리의 결과를 계산하고 유지해야하는 상태 정보의 양을 줄일 수 있음
    - 일부 데이터를 포함하지 않기 때문
### Watermark 실습
[원본](https://github.com/startFromBottom/fc-spark-streaming/blob/main/part02/ch03_streaming/watermarks_ex.py)
[내가 정리한 코드](https://github.com/b00kkk/fc_spark_flink_kafka/blob/main/Spark_Practice/Part2/ch03/watermark_ex.py)
