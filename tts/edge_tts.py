"""EdgeTTS实现"""
import asyncio
from pathlib import Path
from typing import Optional
from .base_tts import BaseTTS


class EdgeTTS(BaseTTS):
    """EdgeTTS语音合成"""
    
    def __init__(
        self,
        voice: str = "zh-CN-XiaoxiaoNeural",
        rate: str = "+0%",
        volume: str = "+0%",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.voice = voice
        self.rate = rate
        self.volume = volume
    
    async def synthesize(self, text: str, output_path: str) -> bool:
        """异步语音合成"""
        try:
            import edge_tts
            
            communicate = edge_tts.Communicate(
                text,
                voice=self.voice,
                rate=self.rate,
                volume=self.volume
            )
            
            await communicate.save(output_path)
            return True
            
        except Exception as e:
            print(f"EdgeTTS合成失败: {e}")
            return False
    
    def synthesize_sync(self, text: str, output_path: str) -> bool:
        """同步语音合成"""
        try:
            asyncio.run(self.synthesize(text, output_path))
            return True
        except Exception as e:
            print(f"EdgeTTS同步合成失败: {e}")
            return False
