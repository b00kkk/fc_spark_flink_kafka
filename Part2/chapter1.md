# Apache Spark

## Apache Spark란
- 데이터 센터나 클라우드에서 대규모 분산 데이터 처리를 하기 위해 설계된 통합형 엔진

## Apache Spark의 주요 설계 철학
1. 속도
- 스파크 이전 하둡 맵리듀스가 주로 사용됨
- 하둡 맵리듀스는 디스크 I/O를 주로 사용하고, 스파크는 중간 결과를 메모리에 유지
- 스파크와 하둡의 성능을 벤치마킹한 자료를 봐도 스파크가 빠르다는 것을 확인할 수 있음
- 질의 연산을 방향성 비순환 그래프(DAG)로 구성
  - DAG의 스케쥴러와 쿼리 최적화 모듈은 효율적인 연산 그래프를 만들고 각각의 태스크 단위로 분해하여, 클러스터의 워커 노드 위에서 병령 실행될 수 있도록 함
- 텅스텐이란 물리적 코드로 실행을 위한 간결한 코드 생성
2. 사용 편리성
- 클라이언트 입장에서 추상화가 잘 되어 있음
- DataFrame, DataSet과 같은 고수준 RDD에서 단순성을 실현함
- 여러 프로그래밍 언어(Scala, Java, Python, R, Kotlin 등)을 제공
3. 모듈성
- 스파크에 내장된 다양한 컴포넌트를 사용해 다양한 타입의 워크로드에 적용가능
- 특정 워크로드를 처리하기 위해 하나의 통합된 처리 엔진을 가짐
  - 다른 워크로드와 연계하기 위해 하둡, Hive, Storm 등과 연동이 필요
  - 이들은 자신만의 API가 가지고 있어 모듈성이 떨어지고 배우기 어려움
  - 하지만, 하나의 프레임워크에서 다룰 수 있다는 장점이 있음
4.  확장성
-  스파크는 빠른 병렬 연산에 초점을 둠
-  수많은 데이터 소스(하둡, Hbase, mongo DB, hive, RDBMS, AWS 등)로부터 데이터를 읽어 들일 수 있음
-  여러 파일 포맷과 교환 가능

## 로컬 환경에 스파크 설치
1. 로컬 스파크 구축
- java 설치
  - 터미널 실행
  - java -version 으로 자바가 설치 되어있는지 확인
  - 자바가 설치되어있지 않다면 sudo apt-get instal openjdk-11-jdk 입력
  - java -version 으로 제대로 설치 되었는지 다시 확인
- PyCharm 설치
   - [Pycharm 다운로드 링크](https://www.jetbrains.com/pycharm/download/?section=linux#section=linux)
   - snap find pycharm 
   - sudo snap install pycharm--community --classic
   - 파이참이 잘 설치되었는지 학인하기
- Python 가상 환경 구성 및 pyspark 라이브러리 설치
  - New project 선택
  - virtualenv를 사용해 가상 환경 설정
  - 터미널에서 pip install pyspark를 입력해 pyspark 라이브러리 설치
