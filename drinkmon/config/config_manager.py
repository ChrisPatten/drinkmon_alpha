"""
Load/save configuration, config file handling, URL decoding.
Implements save_config, load_config, url_decode functions.
"""
import ujson as json

CONFIG_FILE = "config.json"

def save_config(ssid, pw, color):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'ssid':ssid, 'pw':pw, 'color':color}, f)

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def url_decode(s):
    s = s.replace('+', ' ')
    try:
        import ure as re
        s = re.sub('%([0-9a-fA-F][0-9a-fA-F])', lambda m: chr(int(m.group(1),16)), s)
    except ImportError:
        import re
        def pct_decode(match):
            return chr(int(match.group(1), 16))
        s = re.sub(r'%([0-9a-fA-F]{2})', pct_decode, s)
    return s
