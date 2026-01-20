"""
模板数据模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class Template(Base):
    """
    剪辑模板模型
    
    NOTE: 用于存储剪辑模板,支持模板化批量剪辑
    """
    
    __tablename__ = "templates"
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="模板 ID")
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="模板名称")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="模板描述")
    template_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="模板类型 (video/audio/text/mixed)")
    
    # 模板数据
    template_data: Mapped[dict] = mapped_column(JSON, nullable=False, comment="模板配置 (JSON)")
    thumbnail: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="缩略图路径")
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="标签")
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否公开")
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def __repr__(self) -> str:
        return f"<Template(id={self.id}, name={self.name}, type={self.template_type})>"

