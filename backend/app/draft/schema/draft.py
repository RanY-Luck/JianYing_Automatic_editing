"""
草稿 Pydantic Schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.common.enums import DraftStatus


# ==================== 请求 Schema ====================

class DraftCreateParam(BaseModel):
    """创建草稿参数"""
    
    name: str = Field(..., description="草稿名称", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="草稿描述")
    resolution: Optional[str] = Field("1920x1080", description="分辨率")
    fps: Optional[int] = Field(30, description="帧率", ge=1)


class DraftUpdateParam(BaseModel):
    """更新草稿参数"""
    
    name: Optional[str] = Field(None, description="草稿名称", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="草稿描述")
    status: Optional[DraftStatus] = Field(None, description="草稿状态")


class DraftQueryParam(BaseModel):
    """查询草稿参数"""
    
    status: Optional[DraftStatus] = Field(None, description="草稿状态")
    name: Optional[str] = Field(None, description="草稿名称（模糊搜索）")
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(20, description="每页数量", ge=1, le=100)


# ==================== 响应 Schema ====================

class DraftSchema(BaseModel):
    """草稿响应 Schema"""
    
    id: int
    name: str
    draft_id: str
    draft_path: str
    description: Optional[str]
    status: str
    duration: float
    resolution: Optional[str]
    fps: Optional[int]
    tracks_info: Optional[dict]
    extra_data: Optional[dict]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DraftListSchema(BaseModel):
    """草稿列表响应 Schema"""
    
    total: int = Field(..., description="总数")
    items: list[DraftSchema] = Field(..., description="草稿列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
