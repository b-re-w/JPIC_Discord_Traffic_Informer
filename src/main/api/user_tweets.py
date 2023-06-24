from snscrape.modules.twitter import TwitterUserScraper


class UserTweet(TwitterUserScraper):
    user_list = {}

    def __init__(self, user_id, user_tag, user_name, color, photo):
        super().__init__(user_tag)
        self.user_id = user_id
        self.user_tag = user_tag
        self.user_name = user_name
        self.color = color
        self.photo_url = photo
        self.user_list[user_tag] = self

    def lookup_tweets(self, max_tweets=100, since_tweet_id=None) -> tuple[list, dict]:
        tweet_list = []
        tweet_meta = {}
        for twt in self.get_items():
            if int(twt.id) <= int(since_tweet_id) or len(tweet_list) > max_tweets:
                break
            tweet_list.append(twt)
        if tweet_list:
            tweet_meta['user'] = tweet_list[0].user
            tweet_meta['newest_id'] = tweet_list[0].id
        return tweet_list, tweet_meta
