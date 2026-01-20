"""
模板 Schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TemplateBase(BaseModel):
    """模板基础 Schema"""
    name: str = Field(..., description="模板名称", max_length=200)
    description: Optional[str] = Field(None, description="模板描述")
    template_type: str = Field(..., description="模板类型 (video/audio/text/mixed)")
    template_data: dict = Field(..., description="模板配置 (JSON)")
    thumbnail: Optional[str] = Field(None, description="缩略图路径", max_length=500)
    tags: Optional[list[str]] = Field(None, description="标签")
    is_public: bool = Field(False, description="是否公开")


class TemplateCreate(TemplateBase):
    """创建模板 Schema"""
    pass


class TemplateUpdate(BaseModel):
    """更新模板 Schema"""
    name: Optional[str] = Field(None, description="模板名称", max_length=200)
    description: Optional[str] = Field(None, description="模板描述")
    template_type: Optional[str] = Field(None, description="模板类型")
    template_data: Optional[dict] = Field(None, description="模板配置")
    thumbnail: Optional[str] = Field(None, description="缩略图路径")
    tags: Optional[list[str]] = Field(None, description="标签")
    is_public: Optional[bool] = Field(None, description="是否公开")


class TemplateDetail(TemplateBase):
    """模板详情 Schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TemplateApply(BaseModel):
    """应用模板 Schema"""
    draft_id: int = Field(..., description="草稿 ID")
    materials_mapping: dict[str, int] = Field(..., description="素材映射 {template_material_id: material_id}")
