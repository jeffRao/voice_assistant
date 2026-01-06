"""语音助手后端服务"""
import asyncio
import re
import subprocess
from io import BytesIO
from pathlib import Path
from typing import Optional, Dict, Any

import torchaudio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from asr.asr_factory import ASRFactory
from llm.llm_client import LLMClient
from tts.tts_factory import TTSFactory
from audio.player import AudioPlayer
from utils.config_loader import config
from utils.session import SessionManager

app = FastAPI(title="语音助手API")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 全局管理器
session_manager = SessionManager(config.get("output.dir", "output"))
audio_player = AudioPlayer()

# 句子分隔符
SENTENCE_DELIMITERS = config.get("sentence_delimiters", ["。", "！", "？", ".", "!", "?"])

cmd = [
    "ffmpeg", "-hide_banner", "-loglevel", "error",
    "-i", "pipe:0",             # 从 stdin 读
    "-f", "wav", "-ac", "1", "-ar", "16000", "-sample_fmt", "s16",
    "pipe:1"                    # 向 stdout 写
]


class VoiceAssistant:
    """语音助手核心类"""
    
    def __init__(self):
        self.asr_models: Dict[str, Any] = {}
        self.tts_models: Dict[str, Any] = {}
        self.llm_client: Optional[LLMClient] = None
        self.current_session: Optional[str] = None
        self.sentence_buffer = ""
        self.sentence_counter = 0
    
    def initialize_asr(self, asr_type: str):
        """初始化ASR模型"""
        if asr_type not in self.asr_models:
            asr_config = config.get(f"asr.models.{asr_type}", {})
            asr_config["device"] = "cpu"
            # 将相对路径转换为绝对路径
            if "model_path" in asr_config:
                asr_config["model_path"] = config.get_abs_path(asr_config["model_path"])
            self.asr_models[asr_type] = ASRFactory.create_asr(asr_type, asr_config)
    
    def initialize_tts(self, tts_type: str):
        """初始化TTS模型"""
        if tts_type not in self.tts_models:
            tts_config = config.get(f"tts.models.{tts_type}", {})
            if tts_type == "cosyvoice":
                tts_config["device"] = "cpu"
            # 将相对路径转换为绝对路径
            if "model_path" in tts_config:
                tts_config["model_path"] = config.get_abs_path(tts_config["model_path"])
            self.tts_models[tts_type] = TTSFactory.create_tts(tts_type, tts_config)
    
    def initialize_llm(self):
        """初始化大模型客户端"""
        if self.llm_client is None:
            llm_config = config.get("llm", {})
            self.llm_client = LLMClient(**llm_config)
    
    async def process_audio(self, audio_path: str, asr_type: str, tts_type: str):
        """处理音频文件的完整流程
        
        Args:
            audio_path: 音频文件路径
            asr_type: ASR类型
            tts_type: TTS类型
            
        Yields:
            处理结果
        """
        # 重置播放队列位置，开启新对话
        audio_player.clear_queue()
        
        # 1. ASR识别
        yield {"type": "status", "message": "正在识别语音..."}
        
        asr_model = self.asr_models.get(asr_type)
        if not asr_model:
            yield {"type": "error", "message": "ASR模型未初始化"}
            return
        
        user_text = asr_model.transcribe(audio_path)
        if not user_text:
            yield {"type": "error", "message": "语音识别失败"}
            return
        
        yield {"type": "asr_result", "text": user_text}
        
        # 2. 调用大模型
        yield {"type": "status", "message": "正在生成回答..."}
        
        self.sentence_buffer = ""
        self.sentence_counter = 0
        
        async for chunk in self._stream_llm_response(user_text, tts_type):
            yield chunk
    
    async def _stream_llm_response(self, user_text: str, tts_type: str):
        """流式处理大模型响应"""
        full_response = ""
        
        # 使用 asyncio 运行同步生成器，避免阻塞
        for chunk in self.llm_client.simple_chat(user_text):
            full_response += chunk
            self.sentence_buffer += chunk
            
            # 发送LLM片段
            yield {"type": "llm_chunk", "text": chunk}
            
            # 释放事件循环，允许其他异步任务运行
            await asyncio.sleep(0)
            
            # 检测完整句子
            for delimiter in SENTENCE_DELIMITERS:
                if delimiter in self.sentence_buffer:
                    # 找到句子分隔符
                    sentences = self.sentence_buffer.split(delimiter)
                    
                    # 处理除最后一个之外的所有句子（最后一个可能不完整）
                    for i in range(len(sentences) - 1):
                        sentence = sentences[i].strip() + delimiter
                        if sentence.strip():
                            # 先递增计数器并获取序号
                            self.sentence_counter += 1
                            sentence_index = self.sentence_counter
                            # 异步进行TTS转换，传递序号
                            asyncio.create_task(
                                self._convert_to_speech(sentence, tts_type, sentence_index)
                            )
                    
                    # 保留最后一个未完成的部分
                    self.sentence_buffer = sentences[-1]
                    break
        
        # 处理剩余的buffer
        if self.sentence_buffer.strip():
            self.sentence_counter += 1
            sentence_index = self.sentence_counter
            asyncio.create_task(
                self._convert_to_speech(self.sentence_buffer.strip(), tts_type, sentence_index)
            )
        
        yield {"type": "llm_complete", "text": full_response}
    
    async def _convert_to_speech(self, text: str, tts_type: str, index: int):
        """将文本转换为语音
        
        Args:
            text: 要转换的文本
            tts_type: TTS类型
            index: 句子序号，用于保证播放顺序
        """
        try:
            tts_model = self.tts_models.get(tts_type)
            if not tts_model:
                print(f"TTS模型未初始化: {tts_type}")
                return
            
            filename = f"response_{index:03d}.wav"
            output_path = str(session_manager.get_audio_path(self.current_session, filename))
            
            # 异步合成语音
            success = await tts_model.synthesize(text, output_path)
            
            if success:
                # 添加到播放队列，指定序号
                audio_player.add_to_queue(output_path, index)
                print(f"TTS完成: {filename}")
            else:
                # TTS失败，生成静音占位文件
                print(f"TTS失败，生成静音占位: {text}")
                if audio_player.generate_silent_audio(output_path, duration=0.3):
                    audio_player.add_to_queue(output_path, index)
                
        except Exception as e:
            print(f"TTS转换错误: {e}")
            # 发生异常也生成静音占位
            try:
                filename = f"response_{index:03d}.wav"
                output_path = str(session_manager.get_audio_path(self.current_session, filename))
                if audio_player.generate_silent_audio(output_path, duration=0.3):
                    audio_player.add_to_queue(output_path, index)
            except Exception as fallback_error:
                print(f"静音占位生成失败: {fallback_error}")


# 全局助手实例
assistant = VoiceAssistant()


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    audio_player.start()
    print("语音助手服务已启动")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    audio_player.stop()
    print("语音助手服务已关闭")


@app.get("/")
async def read_root():
    """返回前端页面"""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")


@app.post("/api/initialize")
async def initialize(asr_type: str = Form(...), tts_type: str = Form(...)):
    """初始化模型"""
    try:
        assistant.initialize_asr(asr_type)
        assistant.initialize_tts(tts_type)
        assistant.initialize_llm()
        
        # 创建新会话
        session_id = session_manager.create_session()
        assistant.current_session = session_id
        
        # 重置播放器的有序队列
        audio_player.clear_queue()
        
        return JSONResponse({
            "status": "success",
            "session_id": session_id,
            "message": "模型初始化成功"
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"初始化失败: {str(e)}"
        }, status_code=500)


@app.post("/api/process_audio")
async def process_audio_file(
    audio: UploadFile = File(...),
    asr_type: str = Form(...),
    tts_type: str = Form(...),
    session_id: str = Form(...)
):
    """处理上传的音频文件"""
    try:
        # 1. 先读到内存
        content = await audio.read()

        # 2. 用 torchaudio 直接解码（支持 webm/opus/m4a/mp3 等）
        wav_bytes, _ = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate(input=content)
        wav, orig_sr = torchaudio.load(BytesIO(wav_bytes))  # 此时已是 16 kHz 单通道 16-bit

        # 3. 统一转成 16 kHz 单通道 16-bit
        if wav.shape[0] > 1:  # 立体声 -> 单通道
            wav = wav.mean(dim=0, keepdim=True)
        if orig_sr != 16_000:
            wav = torchaudio.functional.resample(wav, orig_sr, 16_000)

        # 4. 落盘成标准 WAV
        audio_path = session_manager.get_audio_path(session_id, "user_input.wav")
        torchaudio.save(audio_path, wav, 16_000, encoding="PCM_S", bits_per_sample=16)

        assistant.current_session = session_id

        return JSONResponse({
            "status": "success",
            "audio_path": str(audio_path),
            "message": "音频已接收并转换为 WAV"
        })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"处理失败: {str(e)}"
        }, status_code=500)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接处理"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "process":
                audio_path = data["audio_path"]
                asr_type = data["asr_type"]
                tts_type = data["tts_type"]
                
                async for result in assistant.process_audio(audio_path, asr_type, tts_type):
                    await websocket.send_json(result)
                    
            elif data["type"] == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        print("WebSocket连接已断开")
    except Exception as e:
        print(f"WebSocket错误: {e}")
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config.get("server.host", "0.0.0.0"),
        port=config.get("server.port", 8000),
        reload=False
    )
