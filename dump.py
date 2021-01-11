#!/usr/bin/python3

import json
import sys

for a in sys.argv[1:]:
    data = []
    with open(a) as f:
        data = json.loads(f.read())

    for tw in data['statuses']:
        if 'retweeted_status' in tw:
            continue
        print("[{}] [{}] {}".format(tw['created_at'], tw['id'], tw['text'].replace('\n', ' ')))
