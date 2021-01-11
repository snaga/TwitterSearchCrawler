#!/usr/bin/python3

import sys
import time

import boto3


def local_to_dlk(local_files, bucket_name, object_key_prefix,
                 aws_access_key_id, aws_secret_access_key):
    # current "yyyy/mm/dd hh" in JST (GMT+9).
    date_prefix = time.strftime('%Y/%m/%d/%H', time.gmtime(time.time() + 9*60*60))

    s3_client = boto3.client('s3',
                             aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key)
    uploaded = []
    for file_name in local_files:
        object_key = object_key_prefix + '/' + date_prefix + '/' + file_name.split('/')[-1]
        object_key = object_key.replace('//', '/')

        print('Uploading {} to s3://{}/{}.'.format(file_name, bucket_name, object_key))
        s3_client.upload_file(file_name, bucket_name, object_key)
        uploaded.append('s3://{}/{}'.format(bucket_name, object_key))

    return uploaded
