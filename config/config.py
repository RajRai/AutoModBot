import json
import os
from typing import Any, Callable

from attrdict import AttrDict
from dataclasses import dataclass

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(script_dir, 'data', 'dev.db')
JSON_PATH = os.path.join(script_dir, 'data', 'settings.json')
DEFAULTS_PATH = os.path.join(script_dir, 'config', 'default_settings.json')
JSON_DUMP_PATH = JSON_PATH
# JSON_DUMP_PATH = os.path.join(script_dir, 'config', 'settings_dump.json')
# JSON_PATH = JSON_DUMP_PATH
json_file = open(JSON_PATH)
settings = json.load(json_file)
json_file.close()

defaults_file = open(DEFAULTS_PATH)
defaults = json.load(defaults_file)
defaults_file.close()

seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


def merge_defaults(d_into: dict, d_from: dict):
    for d in d_from:
        if d not in d_into:
            d_into[d] = d_from[d]
        if isinstance(d_from[d], dict):
            merge_defaults(d_into[d], d_from[d])
    return d_into


def init_settings_for_guild(guild: int):
    global settings, defaults
    sett = settings[str(guild)] if str(guild) in settings else {}
    sett = merge_defaults(d_into=sett, d_from=defaults)
    replace_settings_for_guild(guild, sett)


@dataclass
class SettingValidation:
    setting: Any
    replace: Callable[[Any], Any]
    test: Callable[[Any], bool] = lambda x: True
    iterate: bool = False


def validate_settings(sett: dict):
    # Anything validated anywhere in this function should also be defined in default_settings.json to avoid any key
    # errors.
    if sett['prefix'] is None or len(sett['prefix']) == 0:
        sett['prefix'] = '!'

    x = sett['automod']['saved_messages']
    if isinstance(x, str):
        sett['automod']['saved_messages'] = int(x) if x.isdigit() else 0

    for mode in ['mentions', 'repeat', 'spam']:
        for r in sett['automod'][mode]['rules']:
            if r['cutoff'][-1] not in seconds_per_unit or not r['cutoff'][:-1].isdigit():
                r['cutoff'] = r['cutoff'] + 's' if r['cutoff'].isdigit() else '0s'

    for t in sett['automod']['timeout']:
        for s in t['steps']:
            if s['cutoff'][-1] not in seconds_per_unit or not s['cutoff'][:-1].isdigit():
                s['cutoff'] = s['cutoff'] + 's' if s['cutoff'].isdigit() else '0s'
            if s['timeout'][-1] not in seconds_per_unit or not s['timeout'][:-1].isdigit():
                s['timeout'] = s['timeout'] + 's' if s['timeout'].isdigit() else '0s'

    return sett


def prefix(bot, message):
    global settings
    if str(message.guild.id) in settings:
        return settings[str(message.guild.id)]['prefix']
    return '!'


def settings_for_guild(guild: int):
    return AttrDict(settings_for_guild_dict(guild))


def settings_for_guild_dict(guild: int):
    global settings
    if str(guild) not in settings:
        init_settings_for_guild(guild)
    return settings[str(guild)]


def replace_settings_for_guild(guild: int, update: dict):
    global settings
    sett = validate_settings(update)
    settings[str(guild)] = sett
    dump_settings()


def dump_settings():
    global settings
    with open(JSON_DUMP_PATH, 'w') as f:
        json.dump(settings, f, sort_keys=True, indent=4)
        f.close()
