"""
文件操作工具
"""
import os
import shutil
from pathlib import Path
from typing import List

from backend.common.exception import BadRequestError
from backend.core.conf import settings


def validate_file_path(file_path: str) -> bool:
    """
    验证文件路径，防止路径遍历攻击
    
    :param file_path: 文件路径
    :return: 是否合法
    """
    real_path = os.path.realpath(file_path)
    storage_root = os.path.realpath(settings.storage_root)
    return real_path.startswith(storage_root)


def validate_file_format(file_path: str, allowed_formats: List[str]) -> bool:
    """
    验证文件格式
    
    :param file_path: 文件路径
    :param allowed_formats: 允许的格式列表（如 ['.mp4', '.mov']）
    :return: 是否合法
    """
    file_ext = Path(file_path).suffix.lower()
    return file_ext in allowed_formats


def validate_file_size(file_path: str, max_size: int) -> bool:
    """
    验证文件大小
    
    :param file_path: 文件路径
    :param max_size: 最大文件大小（字节）
    :return: 是否合法
    """
    file_size = os.path.getsize(file_path)
    return file_size <= max_size


def get_file_size(file_path: str) -> int:
    """
    获取文件大小
    
    :param file_path: 文件路径
    :return: 文件大小（字节）
    """
    return os.path.getsize(file_path)


def ensure_dir(dir_path: str) -> None:
    """
    确保目录存在，不存在则创建
    
    :param dir_path: 目录路径
    """
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def delete_file(file_path: str) -> None:
    """
    删除文件
    
    :param file_path: 文件路径
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def delete_directory(dir_path: str) -> None:
    """
    删除目录及其内容
    
    :param dir_path: 目录路径
    """
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)


def copy_file(src: str, dst: str) -> None:
    """
    复制文件
    
    :param src: 源文件路径
    :param dst: 目标文件路径
    """
    ensure_dir(os.path.dirname(dst))
    shutil.copy2(src, dst)


def move_file(src: str, dst: str) -> None:
    """
    移动文件
    
    :param src: 源文件路径
    :param dst: 目标文件路径
    """
    ensure_dir(os.path.dirname(dst))
    shutil.move(src, dst)


def get_unique_filename(directory: str, filename: str) -> str:
    """
    获取唯一文件名（如果文件已存在，则添加数字后缀）
    
    :param directory: 目录路径
    :param filename: 文件名
    :return: 唯一文件名
    """
    file_path = Path(directory) / filename
    if not file_path.exists():
        return filename
    
    stem = file_path.stem
    suffix = file_path.suffix
    counter = 1
    
    while True:
        new_filename = f"{stem}_{counter}{suffix}"
        new_path = Path(directory) / new_filename
        if not new_path.exists():
            return new_filename
        counter += 1


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    :param size_bytes: 文件大小（字节）
    :return: 格式化后的字符串（如 "1.5 MB"）
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"
