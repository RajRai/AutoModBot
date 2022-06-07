import json
from types import SimpleNamespace
import os

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(script_dir, 'data', 'dev.db')
json_file = open(os.path.join(script_dir, 'config', 'settings.json'))

# Parse JSON into an object with attributes corresponding to dict keys.
settings = json.loads(json_file.read(), object_hook=lambda d: SimpleNamespace(**d))


def settings_for_guild(guild: int):
    for set in settings:
        if set.guild == guild:
            return set

def dump_settings():
    with open(os.path.join(script_dir, 'config', 'settings.json'), 'w') as f:
        json.dumps(settings, default=lambda o: o.__dict__, sort_keys=True, indent=4)
