from typing import List
from datetime import datetime
from pyspark import SparkContext, RDD
from pyspark.sql import SparkSession

if __name__ == '__main__':
    ss : SparkSession = SparkSession.builder\ # 스파크 애플리케이션의 시작점
        .master("local")\ #local 모드에서 실행
        .appName("rdd examples ver")\
        .getOrCreate()

    sc: SparkContext = ss.sparkContext #RDD 기반 작업을 위해 사

    log_rdd: RDD[str] = sc.textFile("data/log.txt")

    #check count
    #print(f"count of RDD ==> {log_rdd.count()}")

    #print each row
    #log_rdd.foreach(lambda v: print(v))

    # a) map
    # a-1) log.txt의 각 행을 LIst[str]로 받아오기
    def parse_line(row: str):
        return row.strip().split(" | ")

    parsed_log_rdd: RDD[List[str]]=log_rdd.map(parse_line)

    #parsed_log_rdd.foreach(print)

    # b) filter
    # b-1) status code가 404인 log만 필터링

    def get_only_404(row: List[str]) -> bool:
        status_code = row[-1]
        return status_code == '404'

    rdd_404 = parsed_log_rdd.filter(get_only_404)
    #rdd_404.foreach(print)

    # b-2) status code가 정상인 경우(2xx)인 log만 필터링
    def get_only_2xx(row: List[str]) -> bool:
        status_code = row[-1]
        return status_code.startswith("2")

    rdd_normal = parsed_log_rdd.filter(get_only_2xx)
    #rdd_normal.foreach(print)

    # b-3) post 요청이고 /playbooks api인 로그만 필터링
    def get_post_request_and_playbooks_api(row: List[str]):
        log = row[2].replace("\"","")
        return log.startswith("POST") and "/playbooks" in log

    rdd_post_playbooks = parsed_log_rdd\
        .filter(get_post_request_and_playbooks_api)
    #rdd_post_playbooks.foreach(print)

    # c) reduce
    # c-1) API method (POST/GET/PUT/PATCH/DELETE) 별 개수를 출력
    def extract_api_method(row: List[str]):
        log = row[2].replace("\"", "")
        api_method = log.split(" ")[0]
        return api_method, 1
        
    # reduceByKey() : 집계함수
    rdd_count_by_api_method = parsed_log_rdd.map(extract_api_method)\
        .reduceByKey(lambda c1, c2: c1 + c2).sortByKey()

    #rdd_count_by_api_method.foreach(print)

    # c-2) 분 단위 별 요청 횟수를 출력

    def extract_hour_and_minute(row: List[str]) -> tuple[str, int]:
        timestamp = row[1].replace("[","").replace("]","")
        date_format = "%d/%b/%Y:%H:%M:%S"
        date_time_obj = datetime.strptime(timestamp, date_format)
        return f"{date_time_obj.hour}:{date_time_obj.minute}",1
        
    rdd_count_by_hour_and_minute = parsed_log_rdd.map(extract_hour_and_minute)\
        .reduceByKey(lambda c1, c2: c1 + c2)\
        .sortByKey()

    #rdd_count_by_hour_and_minute.foreach(print)

    # d) group by
    # d-1) status code api method 별 ip 리스트

    def extract_cols(row: List[str]) -> tuple[str, str, str]:
        ip = row[0]
        status_code=row[-1]
        api_method=row[2].replace("\"","").split(" ")[0]

        return status_code, api_method, ip

    result = parsed_log_rdd.map(extract_cols)\
        .map(lambda x: ((x[0], x[1]), x[2]))\
        .groupByKey().mapValues(list)

    #result.foreach(print)

    # reduceBYKey

    result2 = parsed_log_rdd.map(extract_cols) \
        .map(lambda x: ((x[0], x[1]), x[2]))\
        .reduceByKey(lambda i1, i2: f"{i1},{i2}")\
        .map(lambda  row: (row[0], row[1].split(",")))

    result2.collect()

    # group by 가 reduceByKey 보다 가독성이 좋다.
    # 하지만 성능은 reduceByKey가 더 좋음

    while True:
        pass

    # localhost:4040/jobs/를 들어가 Spark UI 확인
    # Jobs는 action 연산에 의해 구분이 됨
    # action이 collect 하나만 있기에 현재 action도 1개
    # 위치를 보면 108번 째 줄에 action이 있다는 것을 확인할 수 있음
    # 들어가 보면 두 개의 stage로 나누어져 있는 것을 확인할 수 있음
    # 첫 번째 stage는 File을 읽어오는 부분, 두 번째 stage에서 데이터 교환이 발생함
    # 첫 번째와 두 번째를 가르는 부분이 103번 줄이라는 것을 확인할 수 있음
    # reduceByKey가 narrow transformation이 아닌 wide transformation임
    # 여기서 실행기(executor)간에 데이터 교환이 발생함
    # 이것을 "셔플"이라고 부름
    # 스테이지를 가르는 기준이 셔플의 발생 여부이다.
    # Event Timeline을 보면 언제 Executor가 추가되고 연산이 얼마나 걸렸는지 확인이 가능함
    # details를 클릭해 코드 실행 로그를 확인할 수 있음
    # Storage는 현재 나오지 않지만, Spark의 중간 결과를 캐싱하는 경우 나타남
    # Environment는 Spark의 Config들이 나타남
    # Executors에서는 각각의 로그를 확인해 볼 수 있음
    # SparkSQL을 사용하면 UI에서 SQL탭을 확인할 수 있음
