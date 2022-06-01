# -*- coding: utf-8 -*-
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
### Alias : settings & Last Modded : 2022.05.31. ###
Coded with Python 3.10 Grammar by irack000
Description : Application Main
Reference : ?
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import json

json_settings = json.loads(open('env.json', encoding='utf-8').read())


class TwitterEnv(object):
    consumer_key: str = json_settings['twitter']['consumer_key']
    consumer_secret: str = json_settings['twitter']['consumer_secret']
    bearer_token: str = json_settings['twitter']['bearer_token']

    """ Belows are for Twitter API 1.0
    twitter_api = twitter.Api(consumer_key=consumer_key,
                              consumer_secret=consumer_secret,
                              access_token_key=access_token,
                              access_token_secret=access_secret)

    get_timeline_by_user = twitter_api.GetUserTimeline
    # account = "@USER_NAME"
    # statuses = twitter_api.GetUserTimeline(screen_name=account, count=200, include_rts=True, exclude_replies=False)
    # for status in statuses:
    #     print(status.text)
    get_search_results = twitter_api.GetSearch
    # query = "KEYWORD"
    # statuses = twitter_api.GetSearch(term=query, count=100)
    #
    # for status in statuses:
    #     print(status.text)
    get_filtered_stream = twitter_api.GetStreamFilter
    # query = ["KEYWORD"]
    # output_file_name = "stream_result.txt"
    # with open(output_file_name, 'w', encoding="utf-8") as output_file:
    # stream = twitter_api.GetStreamFilter(track=query)
    # while True:
    #     for tweets in stream:
    #         tweet = json.dumps(tweets, ensure_ascii=False)
    #         print(tweet, file=output_file, flush=True)
    """


class DiscordEnv(object):
    token: str = json_settings['discord']['bot_token']
    channel_id: int = json_settings['discord']['channel_id']
    log_channel_id: int = json_settings['discord']['log_channel_id']
