# -*- coding: utf-8 -*-
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
### Alias : app & Last Modded : 2023.06.24. ###
Coded with Python 3.10 Grammar by irack000
Description : Application Main
Reference : [twitter] https://hleecaster.com/python-twitter-api/
                      https://velog.io/@kjyeon1101/%ED%8A%B8%EC%9C%84%ED%84%B0-API-%ED%81%AC%EB%A1%A4%EB%A7%81%ED%95%98%EA%B8%B0
            [twitter api 2.0] https://github.com/twitterdev/Twitter-API-v2-sample-code
            [discord] https://luran.me/521
                      https://cosmosproject.tistory.com/482
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
from datetime import datetime
from flask import Flask
import pytz

import discord
from discord.ext import commands, tasks
intents = discord.Intents.default()
intents.typing = False
intents.presences = False

from settings import DiscordEnv
from api.user_tweets import UserTweet


bot = commands.Bot(command_prefix='!', intents=intents)
channel = None
log_channel = None
latest_log_msg = {}

key_words = ['시위', '집회', '행진']

initial_with_index = False


def init_twitter_api():
    """ Initialize user id must be twitter user number.
        user number can be found at https://tweeterid.com/ by user name.
    """
    # @seoultopis => 124409615
    UserTweet(124409615, "seoultopis", "서울시 교통정보과", 0x62c1cc,
              "https://pbs.twimg.com/profile_images/1544937894/php0GXgQC_400x400")
    # @poltraffic02 => 1449898601899986946
    UserTweet(1449898601899986946, "poltraffic02", "서울경찰청 종합교통정보센터", 0x718679,
              "https://pbs.twimg.com/profile_images/1451428633164193802/qV1vNOSe_400x400.jpg")


def to_discord_embed(user, twt_data):
    embed = discord.Embed(title="A New Traffic Information Received.",
                          description="* press embed profile to go original post.",
                          timestamp=twt_data.date, color=user.color)
    embed.add_field(name=twt_data.date, value=twt_data.rawContent, inline=False)
    embed.set_author(name=user.user_name, url=twt_data.url, icon_url=user.photo_url)
    embed.set_footer(text=twt_data.url, icon_url=user.photo_url)
    [embed.set_image(url=media.fullUrl) for media in twt_data.media]
    embed.set_thumbnail(url=twt_data.url)
    return embed


@bot.event
async def on_ready():
    global latest_log_msg

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
                latest_log_msg[tag] = \
                    f"{int(input(f'Please enter initial tweet index for {t_user.user_name} : '))-1}"
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
    global latest_log_msg
    current_log_msg = {key: val for key, val in latest_log_msg.items()}

    send_list = {}
    is_modified = False
    for tag, t_user in UserTweet.user_list.items():
        since_id = latest_log_msg.get(tag, None)
        if since_id:
            since_id = f"{int(since_id) + 1}"

        try:
            datas, meta = t_user.lookup_tweets(max_tweets=100, since_id=since_id)
            if datas:
                print(f"[{datetime.now()}] <{tag}> ", meta)
                for data in datas:
                    key_word_found = False
                    for key_word in key_words:
                        if key_word in data.rawContent:
                            key_word_found = True
                            print(data.rawContent)
                            break
                    if key_word_found:
                        while True:
                            if tag in send_list:
                                tag = tag + '_'
                            else:
                                break
                        send_list[data.date] = to_discord_embed(t_user, data)
                        break
                current_log_msg[tag] = meta['newest_id']
                is_modified = True
            else:
                print(f"[{datetime.now()}] <{tag}> Nothing to update.")
                continue
        except Exception as e:
            print(f"[{datetime.now()}]\n", e)
            return

    for _, send_msg in sorted(send_list.items()):
        await channel.send(embed=send_msg)
    if is_modified:
        if latest_log_msg != current_log_msg:
            await log_channel.send(",".join([f"{tag}={log}" for tag, log in current_log_msg.items()]))
            latest_log_msg = current_log_msg


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


init_twitter_api()
bot.run(DiscordEnv.token)
app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return "Hello World!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
