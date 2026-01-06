"""主程序入口"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    from app import app
    import uvicorn
    from utils.config_loader import config
    
    uvicorn.run(
        app,
        host=config.get("server.host", "0.0.0.0"),
        port=config.get("server.port", 8000),
        reload=False
    )
