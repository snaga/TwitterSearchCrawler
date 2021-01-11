#!/usr/bin/python3

import json
import os
import time

from twitter_search_crawler import TwitterSearchCrawler
from local_to_dlk import local_to_dlk


API_KEY = os.environ['API_KEY']
API_KEY_SECRET = os.environ['API_KEY_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
KEYWORD = os.environ['KEYWORD']
YYYYMMDDHH = os.environ['YYYYMMDDHH']

S3_AWS_ACCESS_KEY_ID = os.environ['S3_AWS_ACCESS_KEY_ID']
S3_AWS_SECRET_ACCESS_KEY = os.environ['S3_AWS_SECRET_ACCESS_KEY']
BUCKET_NAME = os.environ['BUCKET_NAME']
OBJECT_KEY_PREFIX = os.environ['OBJECT_KEY_PREFIX']

# Now - 59-min in JST.
YYYYMMDDHH = time.strftime('%Y%m%d%H', time.gmtime(time.time() - 59*60 + 9*60*60))


def lambda_handler(event=None, context=None):
    print(os.environ)
    print(event)
    print(context)

    tw = TwitterSearchCrawler(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
                              KEYWORD, YYYYMMDDHH)

    local_files = tw.run(outputdir='/tmp')

    s3_files = local_to_dlk(local_files, BUCKET_NAME, OBJECT_KEY_PREFIX,
                            S3_AWS_ACCESS_KEY_ID, S3_AWS_SECRET_ACCESS_KEY)

    return {
        'statusCode': 200,
        'body': json.dumps(s3_files)
    }


if __name__ == '__main__':
    lambda_handler()
