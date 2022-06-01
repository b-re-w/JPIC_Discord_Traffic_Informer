# -*- coding: utf-8 -*-
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
### Alias : app & Last Modded : 2022.05.31. ###
Coded with Python 3.10 Grammar by irack000
Description : Application Main
Reference : [twitter] https://hleecaster.com/python-twitter-api/
                      https://velog.io/@kjyeon1101/%ED%8A%B8%EC%9C%84%ED%84%B0-API-%ED%81%AC%EB%A1%A4%EB%A7%81%ED%95%98%EA%B8%B0
            [twitter api 2.0] https://github.com/twitterdev/Twitter-API-v2-sample-code
            [discord] https://luran.me/521
                      https://cosmosproject.tistory.com/482
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
from datetime import datetime

from settings import TwitterEnv, DiscordEnv

from api.user_tweets import UserTweet
from discord.ext import commands, tasks

bot = commands.Bot(command_prefix='!')
channel = None
log_channel = None
latest_log_msg = {}

key_words = ['시위', '집회', '행진']

initial_with_index = True


def init_twitter_api():
    """ Initialize user id must be twitter user number.
        user number can be found at https://tweeterid.com/ by user name.
    """
    # @seoultopis => 124409615
    UserTweet(124409615, "seoultopis", "서울시 교통정보과", 0x62c1cc, TwitterEnv.bearer_token,
              "https://pbs.twimg.com/profile_images/1544937894/php0GXgQC_400x400")
    # @poltraffic02 => 1449898601899986946
    UserTweet(1449898601899986946, "poltraffic02", "서울경찰청 종합교통정보센터", 0x5cc4e8, TwitterEnv.bearer_token,
              "https://pbs.twimg.com/profile_images/1451428633164193802/qV1vNOSe_400x400.jpg")


init_twitter_api()


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

    # Get Channels
    global channel, log_channel
    channel = bot.get_channel(DiscordEnv.channel_id)
    log_channel = bot.get_channel(DiscordEnv.log_channel_id)
    if not channel or not log_channel:
        raise Exception("Channels not found.")

    # Check Log Channel history
    global latest_log_msg
    async for message in log_channel.history(limit=200):
        if message.author == bot.user:
            latest_log_msg = message
            break
    if not latest_log_msg:
        print("Log channel history not found. Initializing...")
        if initial_with_index:
            for tag, t_user in UserTweet.user_list.items():
                latest_log_msg[tag] = input(f"Please enter initial tweet index for {t_user.name} : ")
        else:  # auto initialization
            await log_channel.send("Initializing...")
    else:
        # ex: seoultopis=1531766718456274947,poltraffic02=1531766718456274947
        print("Log channel history found.")
        print("Latest log message content : " + latest_log_msg.content)
        try:
            latest_log_msg = {log_msg.split('=')[0]: log_msg.split('=')[1] for log_msg in latest_log_msg.content.split(',')}
        except IndexError:
            latest_log_msg = {}

    send_traffic_info.start()


@tasks.loop(minutes=1)
async def send_traffic_info():
    send_list = {}
    log_string = []
    for tag, t_user in UserTweet.user_list.items():
        since_id = latest_log_msg.get(tag, None)
        if since_id:
            since_id = f"{int(since_id) + 1}"
        params = t_user.get_params(max_tweets=100, since_id=since_id)
        try:
            meta, datas = t_user.connect_to_endpoint(params)
            print(f"[{datetime.now()}] <{tag}> ", meta)
        except KeyError:
            print(f"[{datetime.now()}] <{tag}> Nothing to update.")
            continue
        for data in datas:
            key_word_found = False
            for key_word in key_words:
                if key_word in data.text:
                    key_word_found = True
                    break
            if key_word_found:
                while True:
                    if tag in send_list:
                        tag = tag + '_'
                    else:
                        break
                send_list[data.created_at] = data.to_discord_embed
                break
        log_string.append(meta.to_log_msg)
        latest_log_msg[tag] = meta.newest_id
    for _, send_msg in sorted(send_list.items()):
        await channel.send(embed=send_msg)
    if log_string:
        await log_channel.send(",".join(log_string))


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


if __name__ == '__main__':
    bot.run(DiscordEnv.token)
