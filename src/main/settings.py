# -*- coding: utf-8 -*-
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
### Alias : settings & Last Modded : 2022.05.31. ###
Coded with Python 3.10 Grammar by irack000
Description : Application Main
Reference : ?
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import json

json_settings = json.loads(open('env.json', encoding='utf-8').read())


class DiscordEnv(object):
    token: str = json_settings['discord']['bot_token']
    channel_id: int = json_settings['discord']['channel_id']
    log_channel_id: int = json_settings['discord']['log_channel_id']
