"""TTS基类"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class BaseTTS(ABC):
    """TTS基类"""
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    
    @abstractmethod
    async def synthesize(self, text: str, output_path: str) -> bool:
        """异步语音合成
        
        Args:
            text: 待合成文本
            output_path: 输出音频文件路径
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def synthesize_sync(self, text: str, output_path: str) -> bool:
        """同步语音合成
        
        Args:
            text: 待合成文本
            output_path: 输出音频文件路径
            
        Returns:
            是否成功
        """
        pass
