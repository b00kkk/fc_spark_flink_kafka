import requests
import json


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

    original_data = get_original_data(query="베스트셀러")

    print(original_data)