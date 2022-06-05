import json
from types import SimpleNamespace
import os

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(script_dir, 'data', 'dev.db')
json_file = open(os.path.join(script_dir, 'config', 'settings.json'))

# Parse JSON into an object with attributes corresponding to dict keys.
settings = json.loads(json_file.read(), object_hook=lambda d: SimpleNamespace(**d))
