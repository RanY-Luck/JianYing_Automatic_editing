"""
素材数据模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.enums import MaterialType
from backend.core.database import Base


class Material(Base):
    """素材模型"""
    
    __tablename__ = "materials"
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="素材 ID")
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="素材名称")
    type: Mapped[str] = mapped_column(String(50), nullable=False, comment="素材类型")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="素材描述")
    
    # 文件信息
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="文件路径")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, comment="文件大小（字节）")
    file_format: Mapped[str] = mapped_column(String(50), nullable=False, comment="文件格式")
    
    # 媒体信息
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="时长（秒）")
    resolution: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="分辨率")
    fps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="帧率")
    
    # 元数据
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="标签（JSON）")
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="额外数据（JSON）")
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def __repr__(self) -> str:
        return f"<Material(id={self.id}, name={self.name}, type={self.type})>"
