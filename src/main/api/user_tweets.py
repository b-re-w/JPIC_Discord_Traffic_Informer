# https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/User-Tweet-Timeline/user_tweets.py
import requests
import json

import pytz
from datetime import datetime

import discord


class UserTweet(object):
    user_list = {}

    def __init__(self, user_id, user_tag, user_name, bearer_token):
        self.user_id = user_id
        self.user_tag = user_tag
        self.user_name = user_name
        self.photo_url = f"https://twitter.com/{user_tag}/photo"
        self.bearer_token = bearer_token
        self.user_list[user_tag] = self

    @property
    def url(self):
        return f"https://api.twitter.com/2/users/{self.user_id}/tweets"

    @staticmethod
    def get_params(next_token=None, max_tweets=None, since_id=None):
        # Tweet fields are adjustable.
        # Options include:
        # attachments, author_id, context_annotations,
        # conversation_id, created_at, entities, geo, id,
        # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
        # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
        # source, text, and withheld

        # param list
        # [id,since_id,until_id,max_results,pagination_token,exclude,start_time,end_time,expansions,
        #  tweet.fields,media.fields,poll.fields,place.fields,user.fields]

        # Ref: https://community.postman.com/t/how-can-i-get-more-than-100-tweets/20625/9
        params = {'tweet.fields': "created_at"}
        if next_token:
            params['pagination_token'] = next_token
        if max_tweets:  # default is 10
            params['max_results'] = max_tweets
        if since_id:
            params['since_id'] = since_id
            if 'max_results' in params:
                del params['max_results']
        return params

    def bearer_oauth(self, r):
        """ Method required by bearer token authentication. """
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2UserTweetsPython"
        return r

    def connect_to_endpoint(self, params):
        response = requests.request("GET", self.url, auth=self.bearer_oauth, params=params)
        if response.status_code != 200:
            raise Exception(f"Request returned an error: {response.status_code} {response.text}")
        json_response = response.json()
        result_meta = TweetMeta(json_response['meta'], self)
        result_data = []
        for data in json_response['data']:
            result_data.append(Tweet(data, self))
        return result_meta, result_data


class Tweet(dict):
    def __init__(self, tweet_json, user_tweets):
        super().__init__(tweet_json)
        self.user = user_tweets

    @property
    def created_at(self):
        return self['created_at']

    @property
    def id(self):
        return self['id']

    @property
    def text(self):
        return self['text']

    @property
    def original_url(self):
        return f"https://twitter.com/{self.user.user_tag}/status/{self.id}"

    @property
    def to_discord_embed(self):
        embed = discord.Embed(title=self.user.user_name, description=self.created_at,
                              timestamp=datetime.now(pytz.timezone('UTC')), color=0x00ff00)
        embed.add_field(name="Info", value=self.text, inline=False)
        embed.set_footer(text=self.original_url, icon_url=self.user.photo_url)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/955360993729449987/955392404280737812/99pk9saw36t7q8t3o0gt.jpg")
        return embed


class TweetMeta(dict):
    def __init__(self, meta_json, user_tweets):
        super().__init__(meta_json)
        self.user = user_tweets

    @property
    def next_token(self):
        return self['next_token']

    @property
    def result_count(self):
        return self['result_count']

    @property
    def newest_id(self):
        return self['newest_id']

    @property
    def oldest_id(self):
        return self['oldest_id']

    @property
    def to_log_msg(self):
        return f"{self.user.user_tag}={self.newest_id}"


if __name__ == "__main__":
    tweet_params = UserTweet.get_params(max_tweets=5)
    json_response = UserTweet("", "", "", "").connect_to_endpoint(tweet_params)
    print(json.dumps(json_response, indent=4, sort_keys=True))
