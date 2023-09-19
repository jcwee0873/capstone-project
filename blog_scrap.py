import time
import json
import datetime
import argparse
from blog_fake_review.url_loader import blog_url_load
from blog_fake_review.webdriver import CustomWebDriver


def main(**kargs):
    blog_datas = blog_url_load(
        kargs.get('keyword', ''),
        size=kargs.get('size', 1000),
        div=kargs.get('div', 'blog'),
        sort=kargs.get('sort', 'sim')
    )

    driver = CustomWebDriver(
        headless=kargs.get('headless', False)
    )

    result = []

    for data in blog_datas:
        url = data['link']
        ok = driver.get(url)
        time.sleep(1)
        if not ok: continue
        
        driver.switch_to_frame("mainFrame")
            
        source = driver.get_page_source(to_soup=False)


        result.append({
            "title": data["title"],
            "url": url,
            "blog_name": data["bloggername"],
            "date": data["postdate"],
            "origin_source": source
        })

    today = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    with open(
        "./data/origin/{keyword}.json".format(
            keyword=kargs["keyword"],
            today=today
        ),"w", encoding='utf-8'
    ) as f:
        json.dump(result, f, ensure_ascii=False)


def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keyword', type=str)
    parser.add_argument('--size', type=int, default=100)
    parser.add_argument('--div', type=str, default="blog")
    parser.add_argument('--sort', type=str, default="sim")
    parser.add_argument('--headless', type=bool, default=False)

    return parser.parse_args()


if __name__ == "__main__":
    args = vars(load_args())
    main(**args)