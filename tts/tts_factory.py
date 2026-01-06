"""TTS工厂类"""
from typing import Dict, Any
from .base_tts import BaseTTS
from .edge_tts import EdgeTTS
from .cosyvoice_tts import CosyVoiceTTS


class TTSFactory:
    """TTS工厂"""
    
    _tts_classes = {
        "edgetts": EdgeTTS,
        "cosyvoice": CosyVoiceTTS
    }
    
    @classmethod
    def create_tts(cls, tts_type: str, config: Dict[str, Any]) -> BaseTTS:
        """创建TTS实例
        
        Args:
            tts_type: TTS类型 (edgetts, cosyvoice)
            config: 配置参数
            
        Returns:
            TTS实例
        """
        if tts_type not in cls._tts_classes:
            raise ValueError(f"不支持的TTS类型: {tts_type}")
        
        tts_class = cls._tts_classes[tts_type]
        return tts_class(**config)
