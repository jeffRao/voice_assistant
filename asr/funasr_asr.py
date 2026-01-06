"""FunASR实现"""
from pathlib import Path
from typing import Optional
from .base_asr import BaseASR


class FunASR(BaseASR):
    """FunASR语音识别"""
    
    def __init__(self, model_path: str, language: str = "zh", device: str = "cpu", **kwargs):
        super().__init__(model_path, **kwargs)
        self.language = language
        self.device = device
        self.load_model()
    
    def load_model(self):
        """加载FunASR模型"""
        try:
            from funasr import AutoModel
            import os
            
            # 检查模型路径是否存在
            if os.path.exists(self.model_path):
                # 本地模型加载
                print(f"从本地加载FunASR模型: {self.model_path}")
                self.model = AutoModel(
                    model=str(self.model_path),
                    device=self.device,
                    disable_pbar=True,
                    disable_log=True
                )
            else:
                # 如果本地不存在，使用ModelScope下载
                print("本地模型不存在，将从ModelScope下载")
                model_name = "damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
                self.model = AutoModel(
                    model=model_name,
                    device=self.device,
                    disable_pbar=True,
                    disable_log=True,
                    hub="ms"
                )
            
            print(f"FunASR模型加载成功")
        except Exception as e:
            print(f"FunASR模型加载失败: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def transcribe(self, audio_path: str) -> str:
        """语音识别"""
        if self.model is None:
            raise RuntimeError("模型未加载")
        
        try:
            result = self.model.generate(
                input=audio_path,
                batch_size_s=300
            )
            
            if result and len(result) > 0:
                text = result[0].get("text", "")
                return text.strip()
            return ""
        except Exception as e:
            print(f"语音识别失败: {e}")
            return ""
    
    def transcribe_stream(self, audio_data: bytes) -> str:
        """流式语音识别"""
        import tempfile, soundfile as sf, numpy as np
        import os

        # with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        #     tmp_file.write(audio_data)
        #     tmp_path = tmp_file.name

        pcm = np.frombuffer(audio_data, dtype='<i2')  # bytes -> int16
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sf.write(tmp.name, pcm, 16000, subtype='PCM_16')
            tmp_path = tmp.name
        
        try:
            result = self.transcribe(tmp_path)
            return result
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
