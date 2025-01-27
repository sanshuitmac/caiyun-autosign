import yaml

class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        print(f"Loading config from: {self.config_file}")
        self.config = {}
        self.load_config()

    def get(self, key, default=None):
        if not isinstance(key, str):
            raise TypeError(f"The key must be a string, received key: {key}")
        
        current = self.config
        parts = key.split('.')
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def set(self, key, value):
        if not isinstance(key, str):
            raise TypeError(f"The key must be a string, received key: {key}")
        
        current = self.config
        parts = key.split('.')
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
        self.save_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                loaded = yaml.safe_load(f)
                self.config = loaded if loaded is not None else {}
        except FileNotFoundError:
            self.config = {}

    def save_config(self):
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f)

config = Config('./config.yaml')