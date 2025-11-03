import json
import hashlib
import base64

def load_db():
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except UnicodeDecodeError:
        # Если не UTF-8, пробуем другие кодировки
        try:
            with open('users.json', 'r', encoding='cp1251') as f:
                return json.load(f)
        except:
            with open('users.json', 'r', encoding='latin-1') as f:
                return json.load(f)

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"admin_ids": []}
    except UnicodeDecodeError:
        try:
            with open('config.json', 'r', encoding='cp1251') as f:
                return json.load(f)
        except:
            with open('config.json', 'r', encoding='latin-1') as f:
                return json.load(f)

def save_db(data):
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)