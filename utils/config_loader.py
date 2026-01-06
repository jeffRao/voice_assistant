"""配置加载工具"""
import yaml
from pathlib import Path
from typing import Dict, Any
import os


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        # 获取项目根目录（配置文件所在目录）
        self.root_dir = self.config_path.parent.absolute() if self.config_path.is_absolute() else Path.cwd()
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value
    
    def get_abs_path(self, relative_path: str) -> str:
        """将相对路径转换为绝对路径
        
        Args:
            relative_path: 相对于项目根目录的路径
            
        Returns:
            绝对路径字符串
        """
        path = Path(relative_path)
        if path.is_absolute():
            return str(path)
        else:
            return str(self.root_dir / path)


# 全局配置实例
config = ConfigLoader()
