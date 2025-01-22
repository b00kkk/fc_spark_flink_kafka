# 스트림 프로세싱

## Structured Streaming
Batch Processing은 고정된 Dataset에 대해 한 번만 연산을 하는 거 였다면, 
Stram Processing은 끝없이 들어오는 데이터의 흐름을 연속적, 준 실시간으로 처리
- 두 가지 방법론이 존재 함
    - 레코드 단위 처리 모델
        - 각 노드는 지속적으로 한 번에 한 개의 레코드를 받게 됨
        - 그 레코드를 처리하여 생성된 다른 레코드는 그래프상의 다음 노드로 보냄
        - 장점 : 응답시간이 매우 짧음
        - 단점 : 높은 처리량을 달성하기 어렵고, 특정 노드에 장애 발생시 복구가 어려움
    - 마이크로 배치 스트림 처리 모델
        - Spark Straming 에서 기본적으로 취하는 방법
        - Stream procesiing을, 아주 작은 Batch Processing을 처리하는 방식으로 생각
          - 마이크로 배치 단위로 입력데이터를 구분
          - 입력 데이터를 각 노드에서 태스크 단위로 처리
          - ㄷ마이크로 배치 단위로 구분된 데이터가 출력
        - 장점 : 높은 처리량
        - 단점 : 느린 반응 속도
        - 대부분의 파이프라인에서 ms 단위의 반응속도가 필요하지 않고, 다른 곳에서 지연이 발생할 가능성이 있어 채택함
- Spark 에서는 Batch와 Stream을 다루는 코드가 비슷함
    - Dstream
        - Batch의 RDD API 기반으로 작성
        - RDD API와 마찬가지로, 개발자들이 작성한 코드와 동일한 순서로 연산을 수행
            - 카탈라스트 옵티마이저에 의한 자동 최적화 발생x
        - Event time window 지원 부족(Processing time window만 지)
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