import json
import os
from attrdict import AttrDict

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(script_dir, 'data', 'dev.db')
JSON_PATH = os.path.join(script_dir, 'config', 'settings.json')
JSON_DUMP_PATH = JSON_PATH
# JSON_DUMP_PATH = os.path.join(script_dir, 'config', 'settings_dump.json')
# JSON_PATH = JSON_DUMP_PATH
json_file = open(JSON_PATH)
settings = json.load(json_file)
json_file.close()


def prefix(bot, message):
    return settings[str(message.guild.id)]['prefix']


def settings_for_guild(guild: int):
    global settings
    return AttrDict(settings[str(guild)])


def settings_for_guild_dict(guild: int):
    global settings
    return settings[str(guild)] if str(guild) in settings else {}


def replace_settings_for_guild(guild: int, update: dict):
    global settings
    settings[str(guild)] = update
    dump_settings(settings)


def dump_settings(settings):
    with open(JSON_DUMP_PATH, 'w') as f:
        json.dump(settings, f, sort_keys=True, indent=4)
