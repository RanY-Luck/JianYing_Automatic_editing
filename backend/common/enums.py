"""
枚举类型定义
"""
from enum import Enum


class MaterialType(str, Enum):
    """素材类型"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"


class DraftStatus(str, Enum):
    """草稿状态"""
    EDITING = "editing"  # 编辑中
    COMPLETED = "completed"  # 已完成
    EXPORTED = "exported"  # 已导出
    DELETED = "deleted"  # 已删除


class TaskType(str, Enum):
    """任务类型"""
    AUTO_EDIT = "auto_edit"  # 自动剪辑
    BATCH_PROCESS = "batch_process"  # 批量处理
    TEMPLATE_APPLY = "template_apply"  # 模板应用


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"  # 待执行
    RUNNING = "running"  # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


class ExportStatus(str, Enum):
    """导出状态"""
    QUEUED = "queued"  # 队列中
    EXPORTING = "exporting"  # 导出中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


class TrackType(str, Enum):
    """轨道类型"""
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    EFFECT = "effect"
    FILTER = "filter"
    STICKER = "sticker"
