import os
import json
import threading
from io import BytesIO
from dotenv import load_dotenv

import requests
import pandas as pd
from glob import glob
from tqdm import tqdm
from PIL import Image
from minio import Minio
from minio.error import S3Error

load_dotenv()

CLIENT = Minio(
    os.environ.get('S3_ENDPOINTS'),
    access_key=os.environ.get('S3_ACCESS_KEY'),
    secret_key=os.environ.get('S3_SECRET_KEY'),
    secure=False
)
BUCKET_NAME = 'jcwee.study'
FILE_PATH = 'skku/capstone/fake_review_detect/data/photo/{target}/{article_id}/{no}.png'


def load_img(url: str):
    res = requests.get(url)
    img = Image.open(BytesIO(res.content))
    
    return img


def save_bucket(
    url,
    article_id,
    no,
    target
):
    img = load_img(url)
    img_byte = BytesIO()
    img.save(img_byte, format='PNG')
    img_byte = img_byte.getvalue()

    CLIENT.put_object(
        BUCKET_NAME,
        FILE_PATH.format(article_id=article_id, target=target, no=no),
        data=BytesIO(img_byte),
        length=len(img_byte),
        content_type='image/png'
    )



def worker(article_batch, target):
    for article in article_batch:
        article_id = '.'.join(article['url'].split('/')[-2:])
        
        for p in article['contents']:
            if p['info'] in ['img', 'gif']:
                try:
                    save_bucket(
                        p['content'],
                        article_id=article_id,
                        no=p['no'],
                        target=target
                    )
                    
                except Exception as e:
                    print(e)
        
        print(target, article_id)


def main():
    parsed_list = glob("./data/semi-structured/*.json")
    
    for path in parsed_list:
        print(path)

        with open(path, 'r', encoding='utf-8') as f:
            blog = json.load(f)
        

        num_threads = 20
        step = len(blog) // num_threads  # calculate the step
        threads = []

        for i in range(0, len(blog), step):
            # create threads
            t = threading.Thread(target=worker, args=(blog[i:i + step], path.split('/')[-1].split('.')[0].replace(' ', ''),))
            threads.append(t)
            t.start()

        # wait for all threads to finish
        for t in threads:
            t.join()


if __name__ == "__main__":
    main()
        