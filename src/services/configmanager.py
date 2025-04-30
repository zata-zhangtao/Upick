import os
import yaml
import time
from pathlib import Path
from src.log import get_logger
logger = get_logger("services.configmanager")


class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._init_config()
        return cls._instance
    
    def _init_config(self):
        self.ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.yaml_path = os.path.join(self.ROOT_DIR, "config.yaml")
        self.last_modified_time = 0
        self.config_data = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.yaml_path, "r", encoding="utf-8") as file:
                self.config_data = yaml.safe_load(file)
            self.last_modified_time = os.path.getmtime(self.yaml_path)
            return True
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return False
    
    def get_config(self, auto_reload=True):
        """获取配置，可选择是否自动检测文件变化并重新加载"""
        if auto_reload and self._is_config_modified():
            self.load_config()
        return self.config_data
    
    def _is_config_modified(self):
        """检查配置文件是否被修改"""
        try:
            current_mtime = os.path.getmtime(self.yaml_path)
            if current_mtime > self.last_modified_time:
                return True
            return False
        except Exception:
            return False
    
    def force_reload(self):
        """强制重新加载配置"""
        return self.load_config()
