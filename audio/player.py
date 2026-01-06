"""音频播放模块"""
import queue
import threading
import numpy as np
import wave
from pathlib import Path
from typing import Optional
import pygame


class AudioPlayer:
    """音频播放器"""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self.play_queue = queue.Queue()
        self.ordered_queue = {}  # {序号: 音频路径}
        self.next_play_index = 1  # 下一个要播放的序号
        self.queue_lock = threading.Lock()
        self.is_playing = False
        self.player_thread = None
        self._stop_flag = False
        self._reset_event = threading.Event()  # 重置事件，用于唤醒等待的线程
        
        # 初始化pygame mixer
        pygame.mixer.init(frequency=sample_rate, channels=1)
    
    def start(self):
        """启动播放器线程"""
        if self.player_thread is None or not self.player_thread.is_alive():
            self._stop_flag = False
            self.player_thread = threading.Thread(target=self._play_loop, daemon=True)
            self.player_thread.start()
            print("音频播放器已启动")
    
    def stop(self):
        """停止播放器"""
        self._stop_flag = True
        if self.player_thread and self.player_thread.is_alive():
            self.player_thread.join(timeout=2.0)
        pygame.mixer.quit()
        print("音频播放器已停止")
    
    def add_to_queue(self, audio_path: str, index: int = None):
        """添加音频到播放队列
        
        Args:
            audio_path: 音频文件路径
            index: 播放顺序序号（可选，如果提供则按序号播放）
        """
        if not Path(audio_path).exists():
            print(f"音频文件不存在: {audio_path}")
            return
            
        if index is not None:
            # 有序队列模式
            with self.queue_lock:
                self.ordered_queue[index] = audio_path
                print(f"已添加到有序队列[{index}]: {audio_path}")
                # 检查是否可以播放下一个
                self._check_and_queue_next()
        else:
            # 普通队列模式
            self.play_queue.put(audio_path)
            print(f"已添加到播放队列: {audio_path}")
    
    def _check_and_queue_next(self):
        """检查并将下一个有序音频加入播放队列"""
        while self.next_play_index in self.ordered_queue:
            audio_path = self.ordered_queue.pop(self.next_play_index)
            self.play_queue.put(audio_path)
            print(f"[{self.next_play_index}] 加入播放队列: {audio_path}")
            self.next_play_index += 1
    
    def _play_loop(self):
        """播放循环"""
        while not self._stop_flag:
            try:
                # 从队列获取音频文件，超时1秒
                audio_path = self.play_queue.get(timeout=1.0)
                self._play_audio(audio_path)
                self.play_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"播放循环错误: {e}")
    
    def _play_audio(self, audio_path: str):
        """播放单个音频文件
        
        Args:
            audio_path: 音频文件路径
        """
        try:
            self.is_playing = True
            print(f"正在播放: {audio_path}")
            
            # 加载并播放音频
            sound = pygame.mixer.Sound(audio_path)  # 这里可以识别 MP3
            sound.play()

            # 等待结束
            while pygame.mixer.get_busy() and not self._stop_flag:
                pygame.time.Clock().tick(10)
            # pygame.mixer.music.load(audio_path)
            # pygame.mixer.music.play()
            #
            # # 等待播放完成
            # while pygame.mixer.music.get_busy() and not self._stop_flag:
            #     pygame.time.Clock().tick(10)
            
            self.is_playing = False
            print(f"播放完成: {audio_path}")
            
        except Exception as e:
            print(f"播放音频失败: {e}")
            self.is_playing = False
    
    def clear_queue(self):
        """清空播放队列"""
        while not self.play_queue.empty():
            try:
                self.play_queue.get_nowait()
                self.play_queue.task_done()
            except queue.Empty:
                break
        with self.queue_lock:
            self.ordered_queue.clear()
            self.next_play_index = 1
        print("播放队列已清空")
    
    def reset_order(self):
        """重置有序队列的序号计数器"""
        with self.queue_lock:
            self.ordered_queue.clear()
            self.next_play_index = 1
        print("有序队列已重置")
    
    def generate_silent_audio(self, output_path: str, duration: float = 0.5):
        """生成静音音频文件作为占位
        
        Args:
            output_path: 输出文件路径
            duration: 静音时长（秒），默认0.5秒
        """
        try:
            # 生成静音数据
            num_samples = int(self.sample_rate * duration)
            silent_data = np.zeros(num_samples, dtype=np.int16)
            
            # 写入WAV文件
            with wave.open(output_path, 'w') as wav_file:
                wav_file.setnchannels(1)  # 单声道
                wav_file.setsampwidth(2)  # 16位
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(silent_data.tobytes())
            
            print(f"已生成静音占位文件: {output_path}")
            return True
        except Exception as e:
            print(f"生成静音文件失败: {e}")
            return False
    
    def wait_until_done(self):
        """等待播放队列完成"""
        self.play_queue.join()
