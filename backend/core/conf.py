"""
核心配置管理模块
"""
from functools import lru_cache
from pathlib import Path
from typing import List

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    # ==================== 数据库配置 ====================
    database_url: str = Field(
        default="sqlite+aiosqlite:///./jianying_auto.db",
        description="数据库连接 URL"
    )
    
    # ==================== 剪映配置 ====================
    jianying_install_path: str = Field(
        default="C:/Program Files/JianyingPro",
        description="剪映安装路径"
    )
    
    jianying_draft_path: str = Field(
        default="C:/Users/冉勇/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft",
        description="剪映草稿箱路径"
    )
    
    jianying_version: str = Field(
        default="5.9.0",
        description="剪映版本"
    )
    
    # ==================== JianYingApi 配置 ====================
    jianying_api_key: str = Field(
        default="",
        description="JianYingApi 密钥"
    )
    
    jianying_api_secret: str = Field(
        default="",
        description="JianYingApi 密钥"
    )
    
    # ==================== 存储配置 ====================
    storage_root: str = Field(
        default="./storage",
        description="存储根目录"
    )
    
    material_path: str = Field(
        default="./storage/materials",
        description="素材存储路径"
    )
    
    draft_path: str = Field(
        default="./storage/drafts",
        description="草稿存储路径"
    )
    
    template_path: str = Field(
        default="./storage/templates",
        description="模板存储路径"
    )
    
    export_path: str = Field(
        default="./storage/exports",
        description="导出视频存储路径"
    )
    
    # ==================== 日志配置 ====================
    log_level: str = Field(
        default="INFO",
        description="日志级别"
    )
    
    log_path: str = Field(
        default="./logs",
        description="日志文件路径"
    )
    
    log_retention_days: int = Field(
        default=30,
        description="日志保留天数"
    )
    
    # ==================== 导出配置 ====================
    default_resolution: str = Field(
        default="1920x1080",
        description="默认导出分辨率"
    )
    
    default_fps: int = Field(
        default=30,
        description="默认导出帧率"
    )
    
    max_concurrent_exports: int = Field(
        default=2,
        description="最大并发导出任务数"
    )
    
    export_timeout: int = Field(
        default=3600,
        description="导出超时时间（秒）"
    )
    
    # ==================== 任务配置 ====================
    max_concurrent_tasks: int = Field(
        default=5,
        description="最大并发任务数"
    )
    
    task_retry_times: int = Field(
        default=3,
        description="任务失败重试次数"
    )
    
    task_retry_delay: int = Field(
        default=5,
        description="任务重试延迟（秒）"
    )
    
    # ==================== 安全配置 ====================
    jwt_secret_key: str = Field(
        default="your-secret-key-change-this-in-production",
        description="JWT 密钥"
    )
    
    jwt_expire_hours: int = Field(
        default=24,
        description="JWT 过期时间（小时）"
    )
    
    # ==================== 文件上传限制 ====================
    max_file_size: int = Field(
        default=5368709120,  # 5GB
        description="最大文件大小（字节）"
    )
    
    allowed_video_formats: str = Field(
        default=".mp4,.mov,.avi,.mkv,.flv,.wmv",
        description="允许的视频格式"
    )
    
    allowed_audio_formats: str = Field(
        default=".mp3,.wav,.aac,.m4a,.flac",
        description="允许的音频格式"
    )
    
    allowed_image_formats: str = Field(
        default=".jpg,.jpeg,.png,.gif,.bmp,.webp",
        description="允许的图片格式"
    )
    
    # ==================== 服务器配置 ====================
    server_host: str = Field(
        default="0.0.0.0",
        description="服务器主机"
    )
    
    server_port: int = Field(
        default=8000,
        description="服务器端口"
    )
    
    server_workers: int = Field(
        default=4,
        description="工作进程数"
    )
    
    # ==================== Redis 配置（可选）====================
    redis_url: str = Field(
        default="",
        description="Redis 连接 URL"
    )
    
    @property
    def allowed_video_formats_list(self) -> List[str]:
        """获取允许的视频格式列表"""
        return [fmt.strip() for fmt in self.allowed_video_formats.split(',')]
    
    @property
    def allowed_audio_formats_list(self) -> List[str]:
        """获取允许的音频格式列表"""
        return [fmt.strip() for fmt in self.allowed_audio_formats.split(',')]
    
    @property
    def allowed_image_formats_list(self) -> List[str]:
        """获取允许的图片格式列表"""
        return [fmt.strip() for fmt in self.allowed_image_formats.split(',')]


class AppConfig:
    """应用配置加载器"""
    
    def __init__(self, config_file: str = "config/settings.yaml"):
        self.config_file = config_file
        self._config_data = None
    
    def load(self) -> dict:
        """加载 YAML 配置文件"""
        if self._config_data is None:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config_data = yaml.safe_load(f)
            else:
                self._config_data = {}
        return self._config_data
    
    def get(self, key: str, default=None):
        """获取配置项"""
        config = self.load()
        keys = key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


@lru_cache
def get_app_config() -> AppConfig:
    """获取应用配置单例"""
    return AppConfig()


# 全局配置实例
settings = get_settings()
app_config = get_app_config()
