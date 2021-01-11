#!/usr/bin/python3

import gzip
import json
import time
import uuid

from requests_oauthlib import OAuth1Session


class TwitterSession:
    def __init__(self, api_key, api_key_secret, access_token, access_token_secret):
        self.api_key = api_key
        self.api_key_secret = api_key_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        self.session = OAuth1Session(self.access_token,
                                     self.access_token_secret,
                                     self.api_key,
                                     self.api_key_secret)

    def rate_limit_status(self):
        resp = self.session.get('https://api.twitter.com/1.1/application/rate_limit_status.json')

        if resp.status_code == 200:
            res = json.loads(resp.text)
        else:
            print('status code: {}'.format(resp.status_code))
            self.session.close()
            raise Exception('Calling rate_limit_status failed.')
        self.session.close()

        return res


class TwitterSearch:
    def __init__(self, session):
        self.session = session

    def search_rate_limit_status(self):
        status = self.session.rate_limit_status()

        s = status['resources']['search']['/search/tweets']
        return status['resources']['search']['/search/tweets']

    def print_rate_limit_status(self):
        s = self.search_rate_limit_status()
        
        """
        limit: the rate limit ceiling for that given endpoint
        remaining: the number of requests left for the 15-minute window
        reset: the remaining window before the rate limit resets, in UTC epoch seconds

        ref: https://developer.twitter.com/en/docs/twitter-api/rate-limits
        """
        print('Rate limit:')
        print('  remaining {} calls'.format(s['remaining']))
        print('  reset on {} (local)'.format(time.strftime('%Y-%m-%d %H:%M:%S',
                                                           time.localtime(s['reset']))))

    # ref: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets
    def search_once(self, keyword, since=None, until=None, max_id=None):
        params = {'q': keyword, 'count': 100, 'result_type': 'mixed'}
        if since:
            params['since'] = since
        if until:
            params['until'] = until
        if max_id:
            params['max_id'] = max_id
        print(params)

        req = self.session.session.get('https://api.twitter.com/1.1/search/tweets.json', params=params)

        tweets_text = None
        if req.status_code == 200:
            tweets_text = req.text
        else:
            raise Exception('Calling search_tweets failed.')

        return tweets_text


class TwitterSearchCrawler:
    def __init__(self,
                 api_key, api_key_secret, access_token, access_token_secret,
                 keyword, yyyymmddhh):

        session = TwitterSession(api_key, api_key_secret, access_token, access_token_secret)
        self.search = TwitterSearch(session)

        print(self.search.search_rate_limit_status())
        self.search.print_rate_limit_status()

        self.keyword = keyword
        (self.since_s, self.until_s) = self.time_range_one_hour(yyyymmddhh)

    def time_range_one_hour(self, yyyymmddhh):
        since_t = time.strptime(yyyymmddhh, '%Y%m%d%H')
        until_t = time.localtime(time.mktime(since_t) + 60*60)

        # format: '2021-01-10_14:00:00_JST'
        return (time.strftime('%Y-%m-%d_%H:%M:%S_JST', since_t),
                time.strftime('%Y-%m-%d_%H:%M:%S_JST', until_t))

    def file_prefix(self):
        session_ts = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        session_id = str(uuid.uuid4()).split('-')[0]
        return '{}_{}'.format(session_ts, session_id)
    
    def write_to_local(self, filename, text, compress=False):
        if compress:
            fname = filename + '.gz'
            with gzip.open(fname, 'wt') as f:
                f.write(text)
        else:
            fname = filename
            with open(fname, 'wt') as f:
                f.write(text)
        print('written to {}.'.format(fname))
        return fname

    def run(self, outputdir=None):
        fileprefix = self.file_prefix()
        max_id = None
        written_files = []
        for i in range(0,999):
            tweets_text = self.search.search_once(self.keyword,
                                                  since=self.since_s, until=self.until_s,
                                                  max_id=max_id)

            # Write down to the raw file
            outfile = '{}_{}_tweets.json'.format(fileprefix, i)
            if outputdir:
                outfile = outputdir + '/' + outfile
            fname = self.write_to_local(outfile, tweets_text, compress=True)
            written_files.append(fname)
            
            r = json.loads(tweets_text)

            # Finish fetching.
            if not r['statuses']:
                print('no tweet left in the search result.')
                break

            # Get the oldest id for the continuous fetching. (direction: newer/larger -> older/smaller)
            print('max_id: {}, created_at: {}'.format(r['statuses'][-1]['id'],
                                                      r['statuses'][-1]['created_at']))
            max_id = r['statuses'][-1]['id'] - 1
            
            time.sleep(5)

        return written_files
