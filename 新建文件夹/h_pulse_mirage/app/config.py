import os
from dotenv import load_dotenv
from pydantic import BaseSettings, AnyHttpUrl
from typing import Optional, Dict, Any, List, Union

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/h_pulse_mirage")
    
    # 应用配置
    APP_NAME: str = "H-Pulse·Mirage"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "命运模拟与演出引擎"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # API配置
    API_PREFIX: str = "/api"
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # 部署配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    
    # 命理系统配置
    WUXING_WEIGHTS: Dict[str, float] = {
        "天干": 1.0,
        "地支": 0.8
    }
    
    # AI模拟配置
    SIMULATION_STEPS: int = 100
    PPO_EPOCHS: int = 20
    GAMMA: float = 0.99
    
    # 文件存储
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./storage")
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "h_pulse_mirage_secret_key_change_in_production")
    TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30分钟
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7天
    
    # 命运剧场配置 
    MAX_SCENES: int = 50
    DIALOGUE_MODE: str = "rule_based"  # rule_based, gpt (未来可接入LLM)
    
    # NFT系统配置
    NFT_HASH_ALGORITHM: str = "sha256"
    NFT_PREFIX: str = "fate-nft-"
    
    # WebSocket配置
    WS_MESSAGE_QUEUE_SIZE: int = 100
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置对象
settings = Settings()

# 导出简单配置变量以兼容现有代码
DB_URL = settings.DATABASE_URL 