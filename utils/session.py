"""会话管理工具"""
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional


class SessionManager:
    """会话管理器"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_session(self) -> str:
        """创建新会话并返回会话ID"""
        session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        session_dir = self.output_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_id
    
    def get_session_dir(self, session_id: str) -> Path:
        """获取会话目录"""
        session_dir = self.output_dir / session_id
        if not session_dir.exists():
            session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
    
    def get_audio_path(self, session_id: str, filename: str) -> Path:
        """获取音频文件路径"""
        return self.get_session_dir(session_id) / filename
