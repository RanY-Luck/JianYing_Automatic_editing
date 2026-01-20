"""
日志配置模块
"""
import sys
from pathlib import Path

from loguru import logger

from backend.core.conf import settings


def setup_logger():
    """配置 Loguru 日志"""
    
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    
    # 确保日志目录存在
    log_path = Path(settings.log_path)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # INFO 级别日志文件
    logger.add(
        log_path / "info_{time:YYYY-MM-DD}.log",
        level="INFO",
        rotation="00:00",  # 每天午夜轮转
        retention=f"{settings.log_retention_days} days",
        compression="zip",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
    )
    
    # ERROR 级别日志文件
    logger.add(
        log_path / "error_{time:YYYY-MM-DD}.log",
        level="ERROR",
        rotation="00:00",
        retention="90 days",  # 错误日志保留更长时间
        compression="zip",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}\n{exception}",
    )
    
    # DEBUG 级别日志文件（仅在开发模式）
    if settings.log_level == "DEBUG":
        logger.add(
            log_path / "debug_{time:YYYY-MM-DD}.log",
            level="DEBUG",
            rotation="100 MB",  # 按大小轮转
            retention="7 days",
            compression="zip",
            encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        )
    
    logger.info("日志系统初始化完成")


# 初始化日志
setup_logger()
