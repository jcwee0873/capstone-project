import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

NAVER_API_URL = "https://openapi.naver.com/v1/search/{div}.json"
NAVER_HEADERS = {
    "X-Naver-Client-Id": os.environ.get('NAVER_CLIENT_ID'),
    "X-Naver-Client-Secret": os.environ.get('NAVER_CLIENT_SECRET'),
}


def naver_api_call(
    keyword: str,
    start: int,
    display: int,
    div:str = 'blog',
    sort: str = "sim"
) -> list:
    """
    Parameters
    ----------
    kyword: str
        Search Keyword
    start: int
        Search result start from
    display: int
        Search result size
    div: str
        Search div [blog, news, cafearticle]
    sort: str
        Sorting criterion [sim, date]
    
    Returns
    -------
    list
    """
    params = {
        "query": keyword,
        "display": display,
        "start": min(1000, start),
        "sort": sort
    }
    url = NAVER_API_URL.format(div=div)
    res = requests.get(url, params=params, headers=NAVER_HEADERS)
    return json.loads(res.text).get('items', [])


def blog_url_load(
    keyword: str,
    size: int = 1000,
    div:str = 'blog',
    sort: str = "sim"
):
    """
    Parameters
    ----------
    keyword: str
        Search Keyword
    size: int
        Result size, size <= 1000
    div: str
        Search div [blog, news, cafearticle]
    sort: str
        Sorting criterion [sim, date]
    """
    size = min(size, 1000)
    result = []
    for i in range(size // 100):
        result += naver_api_call(
            keyword=keyword, 
            start=(i*100) + 1, 
            display=100,
            div=div,
            sort=sort
        )
    
    return result