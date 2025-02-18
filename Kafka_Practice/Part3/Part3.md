# Kafka 살펴보기
## Apache Kafka란?
- 오픈 소스 기반의  Event Streaming 플랫폼
- 여러 대의 분산 서버에서 대량의 데이터를 처리하는 분산 메시징 시스템
- 발행/ 구독 메시지 전달 패턴 사용
  - 발행자(발행하는 쪽)는 메시지(데이터)를 직접 수신자(구독하는 쪽)로 보내지 않음
  - 발행자는 어떤 형태로든 메시지를 분류해서 보내고, 수신자는 이렇게 분류된 메시지를 구독
  - 보통 발행된 메시지를 전달받고 중계해주는 중간 지점을 하는 브로커가 존재
  - TV 방속국과 TV의 관계와 비슷
  - 브로커가 없는 경우
    - ex) 프론트엔드 서버로 부터 app지표(사용자수, 클릭수 등)들을 모아 모니터링하는 지표 서버(구독자)
    - 모니터링을 시작하는 시점에는 발행자, 구독자가 직접 통신하도록 하느 간단한 해법
    - 만약 여러 서비스들로부터 여러 지표들을 모으도록 기능이 확장된다면 소프트웨어의 복잡도가 N*M 만큼 복잡해질 수 있음
      > N: 발행자 개수, M: 구독자 개수
    - 변경, 에러에 취약
  - 브로커가 있는 경우
    - 소프트웨어의 복잡도가 N*M 에서 N+M으로 감소
    - 발행자, 구독자가 서로에 대해 의존할 필요가 없음. 모두 브로커와만 접속하면 됨
    - 발해앚, 구독자가 추가, 제거 되더라도 기존 발행자, 구독자들은 영향을 받지 않음
      - 변경에 강함
  - 발행잔는 브로커에 메시지를 보내기만 할 뿐, 누가 메시지를 이용하는지 신경쓰지 않음
  - 발행자가 보내는 메시지는 브로커 내의 토픽에 등록됨
  - 구독자는 브로커 내의 토픽에서 자신이 관심 있는 것 만을 선택
  - 같은 토픽을 구독하느 여러 구독자에게는 동일한 메시지가 전달됨
- Apache Kafka의 주요 특징
  1. 높은 처리량으로 실시간 처리
  2. 확장성 : 처리하는 데이터 양에 따라 scale-out을 용이하게 함
  3. 영속성 : 수신한 데이터를 디스크에 유지하며, 임의의 시저멩 데이터를 읽을 수 있음
  4. 유연성 : 연계할 수 있는 시스템이 많아 여러 시스템들을 연결하는 허브 역할 가능
  5. 신뢰 : 메시지 전달 보증을 하므로 데이터 분실을 걱정할 필요가 없음
- Apache Kafka의 사용 분야
  1. 데이터 허브 : 여러 시스템 사이에서 데이터를 상호 교환
  2. 로그 수집 : BI도구를 이용한 리포팅, 머신러닝 분석을 위해 여러 서버에서 생성되는 로그들을 수집 및 축적
  3. 웹 활동 분석 : 실시간 대시보드와 이상치/ 부정 검출 등 웹에서의 사용자 활동을 실시간으로 추적
  4. 사물인터넷 : 센서 등 다양한 디바이스에서 보낸 데이터를 수신해 처리한 후 디바이스에 송신
  5. 이벤트 소싱 : 데이터에 대한 일련의 이벤트를 순차적으로 기록하고 CQRS 방식으로 대량의 이벤트르 유연하게 처리
- Kafka의 주요 구성 요소
  - Producer(발행자)
    - Connector가 붙어 있음(MySQL 같은 외부 시스템, API, 라이브러리 등)
  - Connect API를 통해 broker에 데이터를 전달
  - broker안 topic에 전달된 데이터는 Consumer(구독자)가 데이터를 읽어옴
  - cluster에 broker를 관리하는 Zookeeper가 있음

## Kafka 기본 개념
### Topic, Partitions, Offset
1. Topic
- kafka cluster 내의 어떤 특정 데이터 stream
- Database의 table과 유산한 개념
  - 차이점: table가 달리 어떤 제약조건 X, 데이터 검증을 따로 하지 않음
- 각각의 topic은 이름으로 구별
- json, avro, text, binary, protobuf 등 많은 메시지 포맷들을 지원
- topic에 직접적으로 쿼리를 날리수 없음
  - 대신 kafka producer를 사용해 데이터를 전송해야 함
  - kafka consumer를 사용해 데이터를 읽어야함

2. Partition
- Topic에 대한 대량의 메시지 입출력을 지원하기 위해, 각각의 Topic은 Partition이라는 단위로 분할됨
- 메시지가 한 번 partiton에 쓰이면, 변경도리 수 없음
- 한 partition 내에서 데이터의 순서는 보장됨(다른 Partition 간에는 X)
- 특정 메시지가 Topic 내 어느 Partition에 기록될지는 메시지 내의 Key 존재 여부에 따라 다름
  - Key가 없는 경우 : Round robin(순차적으로 돌아감, 공평함)
  - Key가 있는 경우 : Hash 기반(계산된 값에 따라 할당)
- Partiton Offset

3. Offset
- 각각의 Partition에서 수신한 메시지에는 일련 번호가 부여되어 있음
- Partition 단위로 메시지의 위치를 나타내는 Offset이라는 관리 정보를 이용해 Consumer가 어느 partiton가지 데이터를 읽었는지를 알 수 있게 함
- 종류
  - Log-End-Offset(LEO) : Partition 데이터의 끝
  - Curent Offset : Consumer가 어디까지 메시지를 읽었는지
  - Commit Offset : Consumer가 어디까지 커밋했는지
    - Consumer로 부터 여기까지 offset을 처리했다느 offset commit 요청을 계기로 업데이트
  - Commit이란
    - DB : 트랜잭션의 내용 업데이트를 영구적으로 확정
    - kafka : partition 내의 데이터를 처리하는 것
### Producer, Message
1. Producer
- topic에 메시지를 전달하는 역할
- Producer는 어느 Partition에 메시지를 전달해야 될지를 알고 있음(Partition: broker 내 저장)
- broker에 메시지를 전달하는데 실패했을 때, Producer는 자동으로 복구작업을 수행
- 메시지에 Key가 존재하는 경우
  - Key의 해시 값을 이용해 파티셔닝 - 동일한 Key를 가진 메시지는 동일 Partition에 기록
  - Partition간 데이터 편향이 발생할 수 있음
- 메시지에 Key가 존재하지 않는 경우
  - Round robin 방식 - 순서대로 파티션에 데이터를 집어넣음
- Ex) Partition 간 데이터 편향 
  - 특정 Producer에 전송하는 메시지의 Key종류 = A, B, C
  - Topic의 Partiton은 5개인 경우
  - Key가 있을 경우 Partition 2개는 항상 비어 있음
  - 리소스 낭비, 불균형 발생
2. Message format
- 기본적으로  Key, value는 모두 binary type
- 여러 타입을 byte형태로 직렬화(Serialization) 해야함
  - Message Serializer 존재
- 압축 포맷 지정 가능
### Consumer, Deserialization
1. Consumer
- topic에 저장되어있는 데이터를 읽어오는 역할(pull model 기반)
- Consumer는 어느 broker로부터 데이터를 읽어야 하는지 알고 있음
- broker에 문제가 있어 데이터 읽기에 실패했을 때 어떻게 복구해야하는지 알고 있음
- 각각의 Partition내에서 offset 기준으로 오름차순으로 데이터를 읽음
- pull model
  - Consumer가 데이터를 필요로 할 때 broker로부터 데이터를 읽음
  - push model의 반대
    - broker가 주체가 되어 Consumer에 데이터 전달
  - Kafka는 Consumer 단계에서 Pull model을 사용
  - Consumer가 고자이나 유지 보수로 정지했을 때, broker에 미치는 영향이 적다는 이점이 있음
    - push model이었으면 broker에서 대응 필요
  - Producer 단계에서는 push model 사용
2. Consumer Deserializer
- 데이터는 Partition 내에서 bytes 형태로 저장됨
- Consumer는 bytes 형태의 데이터르 String, int 등의 Object 형태로 변환(Deserialization: 역직렬화)
- Producer에서는 Serialization 방법과, Consumr에서의 Deserialization 방법은 반드시 같은 방식이어야함
- 데이터 타입을 바꾸고 싶다면, Partition내의 데이터는 불변이므로 새로운 topic을 생성해야함
### Consumer group, Consumer offsets
1. Consumer group
- 효율적인 분산 처리를 위해 도입
- consumer 들은 consumer group에 묶임
- group 내의 consumer들은 한 Topic내의 각기 다른 partition들을 읽음
- Consumer group내 Consumer가 너무 많은 경우
  - Partition 개수보다 Consumer group 내 Consumer개수가 많으면, ㅇ리부 Consumer는 비활성화 될 수 있음
- 한 개의 topic을 여러 Consumer group이 구독 가능
2. Consumer offset
- Kafka는 consumer group이 어느 partiition까지 읽었는지에 대한  offset정보를 저장
- offset 정보는 _consumer_offsets이라는 topic에 저자됨
- Offset이 커밋되는 방식
  - At least once(실무에서 가장 많이 사용)
    - 적어도 1회 전달, 메시지가 중복될 수 있지만 상실되지는 않음
    - 재전송 시도는 존재, 중복 삭제는 안될 수 있음
    - idempotent 이어야함(중복된 메시지를 처리하는 것이 시스템에 어떤 영향을 미치면 안됨->항상 같은 결과)
  - At most once
    - 1회는 전달을 시도해봄, 메시지는 중복되지 않지만 상실될 수 있음
    - 재전송 시도 X, 중복 삭제 X
  - Exactly once
    - 1회만 전달, 메시지 중복 X, 상실 X
    - 이산적으로 좋지만, 여러 개의 컴퓨터를 사용하는 분산환경에서는 여러 노드를 확인해야함
    - 그렇기에 성능이 좋지 않음
### Brokers
- Kafka cluster는 여러 개의 broker(=server)로 구성
- 각각의 broker는  id(interger)로 식별
- 각각의 broker는 특정한 topic partition들을 가지고 있음
- kafka client가 한 broker(=bootstrap broker)와만 연결되면, client는 전체 cluster내의 broker들과 연결될 수 있음
- 일반적으로 broker는 3개로 시작, 100개 이상으로 늘어날 수 있음
-  Ex)
  - broker = 3, Topic-A = 3 Partition, Topic-B = 2 Partition
  - 전체 cluster내의 3개의 server(broker)가 있음
  - Topic-A에 해당하는 partition들이 각각 다른 broker로 들어감
  - Topic-B에 해당하는 partition들은 2군데의 broker에 들어감
  - 각각의 topic끼리는 독립적임
- broker discovery
  - 각각의 broker는 bootstrap server가 될 수 있음
  - client는 한 broker와만 연결이 되면 전체 borker들과 연결이 가능
  - 각각의 broker는  cluster내의 모든 broker, partition, topic에 대해 알고 있음
### Replication
- Topic에 할당되는 파라미터 같은 것
- Topic들은 1 이상의 replication factor를 가져야함(factor 값이 N이란 건 Topic내 각 Partition을 N개의 broker에 복사)
- 프로덕션 환경에서는 반드시 2 이상으로 세팅(다른 broker에 1개 이상의 복제본이 있어야함)
- 만약 한 broker가 고장났더라도, 다른 broker까 데이터를 서빙할 수 있음
- 복제된 Partition 중 하나는 Leader로 선출됨
- 기본적으로 Producer는 Leader partition이 포함된 broker에 메시지를 전송
- 그 후에 broker는 나머지 partition들에 메시지를 복제
- Consumer도 Leader partition이 포함된 broker로부터 데이터를 읽음
  > kafka 2.4부터 leader가 아닌, 가장 가까운 broker로부터 데이터를 읽는 것이 가능
- Partition = 1 leader + (N-1) * ISR(In-sync Replicas)
- Producer Acknowlegment(Acks)
  - 처리가 잘되었다는 신호
  - acks = 0 
    - Producer는 메시지 송신 시 Ack를 기다리지 않고 다음 메시지를 송신
    - 데이터 손실 가능성 존재
  - acks = 1
    - Leader Replica에 데이터가 전달되면  Ack를 반환
    - 일반적으로 가장 많이 사용
  - acks = all
    - Leader + 모든 ISR들에 데이터가 복제되면 Ack를 반환
    - 가장 안전(데이터 손실 없음 보장) 하나 성능 이슈 존재
### Zookeeper, Kraft
1. Zookeeper
- Kafka broker들을 관리
- Partition 들간의 leader 선출 과정에 관여
- topic 추가 및 삭제, broker 추가 및 고장 등의 이벤트를 감지하고 Kafka에 전달
- Zooker도 Leader-follower 형태의 분산노드
2. Kraft
- Zookeepre라는 별도의 Framework(외부 서비스)를 이용해 관리하기에 시스템의 복잡도 증가
- Zookeeper는 cluster내 broker가 1000개 이상으로 많아질 때 성능상 병목이 될 수 있다고 함
- Confluent에서 Zookeeper없이 Kafka를 사용할 수 있는 Kraft를 도입
- zookeeper와 비교했을 때 성능이 좋다고 함
- 아직 production 환경에서는 zookeeper를 대체하지는 못하는 것 같음
