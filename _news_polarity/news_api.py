import os
import json
import datetime
import requests
from dotenv import load_dotenv


BIGKINDS_NEWS_URL = "http://tools.kinds.or.kr:8888/search/news"

CURRENT_PATH = os.path.dirname(__file__)
load_dotenv(os.path.abspath(os.path.join(CURRENT_PATH, '../.env')))


def fetch_request_body(**kargs) -> dict:
    """
    Parameters
    ----------
    query: str
    start: str
        Format: YYYY-MM-DD, default: today
    end: str
        Format: YYYY-MM-DD, default: tomorrow
    return_from: int
        default: 0
    return_size: int
        default: 10000

    Returns
    -------
    dict
    """
    body = {
        "access_key": os.getenv('BIGKINDS_API_KEY'),
        "argument": {
            "query": kargs.get("query", ""),
            "published_at": {
                "from": kargs.get('start', datetime.datetime.now().strftime("%Y-%m-%d")),
                "until": kargs.get('end' , (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
            },
            "sort": {"date": "desc"},
            "return_from": kargs.get('return_from', 0),
            "return_size": kargs.get('return_size', 10000),
            "fields": [
                "news_id",
                "title",
                "content",
                "published_at",
                "enveloped_at",
                "dateline",
                "provider",
                "category",
                "category_incident",
                "publisher_code",
                "provider_link_page",
            ]
        }
    }

    return body


def api_call(**kargs) -> str | dict:
    """
    Parameters
    ----------
    query: str
    start: str
        Format: YYYY-MM-DD, default: today
    end: str
        Format: YYYY-MM-DD, default: tomorrow
    return_from: int
        default: 0
    return_size: int
        default: 10000
    to_json: bool
        default: False

    Returns
    -------
    str | dict
    """
    request_body = fetch_request_body(**{k:v for k, v in kargs.items() if v})
    response = requests.post(BIGKINDS_NEWS_URL, json=request_body)

    return json.loads(response.text)


def call_bigkinds_news(
    query: str = "",
    start: str | None = None,
    end: str | None = None,
    return_from: int = 0,
    return_size: int = -1
) -> str | dict:
    """
    Parameters
    ----------
    query: str
    start: str
        Format: YYYY-MM-DD, default: today
    end: str
        Format: YYYY-MM-DD, default: tomorrow
    return_from: int
        default: 0
    return_size: int
        default: -1 (Call all news)

    Returns
    -------
    str | dict
    """
    print(f"[BigkindsNews] '{query}' from {start} to {end}. ({return_size})")

    if (return_size == -1) or (return_size > 10000):
        total_size = return_size
        return_size = 10000

    result = []
    while True:
        response = api_call(
            query=query, 
            start=start, 
            end=end, 
            return_from=return_from, 
            return_size=return_size
        )

        total_hits = response.get('return_object', {}).get('total_hits', 0)

        if total_hits == 0: return []

        result += response['return_object']['documents']

        print(f"[BigkindsNews] {len(result)} / {total_hits}")

        if ((total_size == -1) \
            or (total_size > len(result))) \
            and (len(result) < total_hits):

            return_from = len(result)
            if return_from + return_size >= total_hits:
                return_size = total_hits - return_from
                
            continue

        return result
        

        



    