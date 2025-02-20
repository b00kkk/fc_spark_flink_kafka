import requests
import json

from confluent_kafka import Producer
import fc_spark_kafka_ex.proto.book_data_pb2 as pb2
from fc_spark_kafka_ex.keywords import book_keywords


class KakaoException(Exception):
    pass

def get_original_data(query: str) -> dict:
    rest_api_key = "ff84c51d91a61382967f5baff8d5b9cd"
    url = "https://dapi.kakao.com/v3/search/book"

    res = requests.get(
        url=url,
        headers={
            "Authorization": f"KakaoAK {rest_api_key}"
        },
        params={
            "query": "query",
            "size": 50,
            "start": 1,
        }
    )

    if  res.status_code >= 400:
        raise KakaoException(res.content)

    return json.loads(res.text)



if __name__ == '__main__':

    # kafka configs
    conf = {
        'bootstrap.servers': 'localhost:29092',
    }

    producer = Producer(conf)
    topic = "book"



    for keyword in book_keywords:
        original_data = get_original_data(query=keyword)
        for item in original_data['documents']:
            book = pb2.Book()
            # dictionary -> protobuf
            book.title = item['title']
            book.author = ','.join(item['authors'])
            book.publisher = item['publisher']
            book.isbn = item['isbn']
            book.price = item['price']
            book.publication_date = item['datetime']
            book.source = 'kakao'

            print('----')
            print(book)
            print('----')
            producer.produce(topic=topic, value=book.SerializeToString())

            producer.flush()
            print("전송 완료")