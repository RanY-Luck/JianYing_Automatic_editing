"""
任务数据模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.enums import TaskStatus, TaskType
from backend.core.database import Base


class Task(Base):
    """任务模型"""
    
    __tablename__ = "tasks"
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="任务 ID")
    
    # 任务标识
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, comment="任务 UUID")
    
    # 任务信息
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="任务名称")
    type: Mapped[str] = mapped_column(String(50), nullable=False, default=TaskType.AUTO_EDIT, comment="任务类型")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=TaskStatus.PENDING, comment="任务状态")
    
    # 任务参数与结果
    params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="任务参数（JSON）")
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="任务结果（JSON）")
    error_msg: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="错误信息")
    
    # 进度
    progress: Mapped[int] = mapped_column(Integer, default=0, comment="进度（0-100）")
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now, comment="更新时间")
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True, comment="开始时间")
    finished_at: Mapped[Optional[datetime]] = mapped_column(nullable=True, comment="完成时间")
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, name={self.name}, status={self.status})>"
