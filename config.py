import yaml
import os

class Config:
    def __init__(self):
        self.config = self.load_config()
        self.caiyun_token = self.config.get('139yun').get('token')
        self.phone = self.config.get('139yun').get('phone')

    def load_config(self):
        try:
            with open(f'./config.yaml', 'r') as file:
                config_data = yaml.safe_load(file)
                return config_data
        except FileNotFoundError:
            print("配置文件未找到，请检查路径是否正确。")
            return {}
        except yaml.YAMLError as exc:
            print(f"YAML格式错误: {exc}")
            return {}
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
config = Config()