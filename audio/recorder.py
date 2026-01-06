"""音频录制模块"""
import wave
import pyaudio
from pathlib import Path
from typing import Optional


class AudioRecorder:
    """音频录制器"""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        audio_format: int = pyaudio.paInt16
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio_format = audio_format
        
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.frames = []
        self.is_recording = False
    
    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            print("已经在录音中")
            return
        
        self.frames = []
        self.is_recording = True
        
        try:
            self.stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            print("开始录音...")
        except Exception as e:
            print(f"启动录音失败: {e}")
            self.is_recording = False
            raise
    
    def stop_recording(self) -> bytes:
        """停止录音并返回音频数据
        
        Returns:
            音频数据
        """
        if not self.is_recording:
            print("当前未在录音")
            return b""
        
        self.is_recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        print("录音已停止")
        return b"".join(self.frames)
    
    def record_chunk(self):
        """录制一帧音频数据"""
        if self.is_recording and self.stream:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"录音出错: {e}")
    
    def save_to_file(self, output_path: str, audio_data: Optional[bytes] = None):
        """保存音频到文件
        
        Args:
            output_path: 输出文件路径
            audio_data: 音频数据，如果为None则使用当前录制的数据
        """
        if audio_data is None:
            audio_data = b"".join(self.frames)
        
        if not audio_data:
            print("没有可保存的音频数据")
            return
        
        try:
            with wave.open(output_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data)
            print(f"音频已保存到: {output_path}")
        except Exception as e:
            print(f"保存音频失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        print("音频录制器已清理")
