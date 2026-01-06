"""ASR工厂类"""
from typing import Dict, Any
from .base_asr import BaseASR
from .sensevoice_asr import SenseVoiceASR
from .funasr_asr import FunASR


class ASRFactory:
    """ASR工厂"""
    
    _asr_classes = {
        "sensevoice": SenseVoiceASR,
        "funasr": FunASR
    }
    
    @classmethod
    def create_asr(cls, asr_type: str, config: Dict[str, Any]) -> BaseASR:
        """创建ASR实例
        
        Args:
            asr_type: ASR类型 (sensevoice, funasr)
            config: 配置参数
            
        Returns:
            ASR实例
        """
        if asr_type not in cls._asr_classes:
            raise ValueError(f"不支持的ASR类型: {asr_type}")
        
        asr_class = cls._asr_classes[asr_type]
        return asr_class(**config)
