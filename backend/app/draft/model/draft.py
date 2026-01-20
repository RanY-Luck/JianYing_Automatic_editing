"""
草稿数据模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class Draft(Base):
    """草稿模型"""
    
    __tablename__ = "drafts"
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="草稿 ID")
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="草稿名称")
    draft_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="剪映草稿 ID")
    draft_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="草稿文件路径")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="草稿描述")
    
    # 状态信息
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="editing", comment="草稿状态")
    
    # 媒体信息
    duration: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="总时长（秒）")
    resolution: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="分辨率")
    fps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="帧率")
    
    # 轨道信息
    tracks_info: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="轨道信息（JSON）")
    
    # 元数据
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="额外数据（JSON）")
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def __repr__(self) -> str:
        return f"<Draft(id={self.id}, name={self.name}, status={self.status})>"
