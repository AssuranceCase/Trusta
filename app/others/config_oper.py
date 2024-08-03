import json


class Config:
    def set_config(self, key, value):
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        config[key] = value

        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    
    def get_all_config(self):
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    
    def get_config(self, key):
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get(key, '')