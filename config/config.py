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


def is_int_or_parseable(x):
    if isinstance(x, int):
        return True
    try:
        int(x)
        return True
    except ValueError:
        return False


def merge_dicts(d_into: dict, d_from: dict):
    for d in d_from:
        if d not in d_into:
            d_into[d] = d_from[d]
        if isinstance(d_from[d], dict):
            merge_dicts(d_into[d], d_from[d])
    return d_into


def init_settings_for_guild(guild: int):
    global settings, defaults
    sett = settings[str(guild)] if str(guild) in settings else {}
    sett = merge_dicts(d_into=sett, d_from=defaults)
    replace_settings_for_guild(guild, sett)


@dataclass
class SettingValidation:
    setting: Any
    replace: Callable[[Any], Any]
    test: Callable[[Any], bool] = lambda x: True
    iterate: bool = False


def validate_settings(sett: dict):
    # Anything validated here should also be defined in default_settings.json to avoid any key errors
    validations = [
        SettingValidation(setting=sett['prefix'], replace=lambda x: '!', test=lambda x: x is not None and len(x) > 0),
        SettingValidation(setting=sett['automod']['saved_messages'],
                          replace=lambda x: int(x) if is_int_or_parseable(x) else 0,
                          test=lambda x: not is_int_or_parseable(x))
    ]

    for valid in validations:
        if not valid.iterate:
            valid.setting = [valid.setting]
        else:
            for i in range(len(valid.setting)):
                val = valid.setting[i]
                if not valid.test(val):
                    valid.setting[i] = valid.replace(val.setting)


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
    validate_settings(update)
    settings[str(guild)] = update
    dump_settings()


def dump_settings():
    global settings
    with open(JSON_DUMP_PATH, 'w') as f:
        json.dump(settings, f, sort_keys=True, indent=4)
