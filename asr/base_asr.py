"""ASR基类"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class BaseASR(ABC):
    """ASR基类"""
    
    def __init__(self, model_path: str, **kwargs):
        self.model_path = Path(model_path)
        self.model = None
        self.kwargs = kwargs
    
    @abstractmethod
    def load_model(self):
        """加载模型"""
        pass
    
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """语音识别
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            识别结果文本
        """
        pass
    
    @abstractmethod
    def transcribe_stream(self, audio_data: bytes) -> str:
        """流式语音识别
        
        Args:
            audio_data: 音频数据
            
        Returns:
            识别结果文本
        """
        pass
