import requests
import json

import proto.book_data_pb2 as pb2

class NaverException(Exception):
    pass

def get_original_data(query: str) -> dict:
    client_id = "aWsoy_HBYJRTV5kqYTDy"
    client_secret = "nZ06EPYKtQ"
    url = "https://openapi.naver.com/v1/search/book.json"

    res = requests.get(
        url=url,
        headers={
            "X-Naver-Client-Id" : client_id,
            "X-Naver-Client-Secret" : client_secret
        },
        params={
            "query": "query",
            "display": 100,
            "start": 1,
        }
    )

    if  res.status_code >= 400:
        raise NaverException(res.content)

    return json.loads(res.text)



if __name__ == '__main__':

    original_data = get_original_data(query="베스트셀러")

    print(original_data)