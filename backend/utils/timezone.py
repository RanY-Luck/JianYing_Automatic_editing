"""
时间处理工具
"""
from datetime import datetime, timezone
from typing import Optional

import pytz


# 默认时区（中国标准时间）
DEFAULT_TIMEZONE = pytz.timezone('Asia/Shanghai')


def now(tz: Optional[pytz.BaseTzInfo] = None) -> datetime:
    """
    获取当前时间
    
    :param tz: 时区，默认为 Asia/Shanghai
    :return: 当前时间
    """
    if tz is None:
        tz = DEFAULT_TIMEZONE
    return datetime.now(tz)


def utc_now() -> datetime:
    """
    获取当前 UTC 时间
    
    :return: 当前 UTC 时间
    """
    return datetime.now(timezone.utc)


def to_timestamp(dt: datetime) -> int:
    """
    将 datetime 转换为时间戳（秒）
    
    :param dt: datetime 对象
    :return: 时间戳
    """
    return int(dt.timestamp())


def from_timestamp(timestamp: int, tz: Optional[pytz.BaseTzInfo] = None) -> datetime:
    """
    将时间戳转换为 datetime
    
    :param timestamp: 时间戳（秒）
    :param tz: 时区，默认为 Asia/Shanghai
    :return: datetime 对象
    """
    if tz is None:
        tz = DEFAULT_TIMEZONE
    return datetime.fromtimestamp(timestamp, tz)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化 datetime
    
    :param dt: datetime 对象
    :param fmt: 格式化字符串
    :return: 格式化后的字符串
    """
    return dt.strftime(fmt)


def parse_datetime(dt_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    解析时间字符串
    
    :param dt_str: 时间字符串
    :param fmt: 格式化字符串
    :return: datetime 对象
    """
    return datetime.strptime(dt_str, fmt)
