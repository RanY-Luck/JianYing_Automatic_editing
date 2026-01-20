"""
素材 Pydantic Schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.common.enums import MaterialType


# ==================== 请求 Schema ====================

class MaterialCreateParam(BaseModel):
    """创建素材参数"""
    
    name: str = Field(..., description="素材名称", min_length=1, max_length=255)
    type: MaterialType = Field(..., description="素材类型")
    description: Optional[str] = Field(None, description="素材描述")
    file_path: str = Field(..., description="文件路径")
    file_size: int = Field(..., description="文件大小（字节）", gt=0)
    file_format: str = Field(..., description="文件格式")
    duration: Optional[float] = Field(None, description="时长（秒）", ge=0)
    resolution: Optional[str] = Field(None, description="分辨率")
    fps: Optional[int] = Field(None, description="帧率", ge=0)
    tags: Optional[list[str]] = Field(None, description="标签")


class MaterialUpdateParam(BaseModel):
    """更新素材参数"""
    
    name: Optional[str] = Field(None, description="素材名称", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="素材描述")
    tags: Optional[list[str]] = Field(None, description="标签")


class MaterialQueryParam(BaseModel):
    """查询素材参数"""
    
    type: Optional[MaterialType] = Field(None, description="素材类型")
    name: Optional[str] = Field(None, description="素材名称（模糊搜索）")
    tags: Optional[list[str]] = Field(None, description="标签")
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(20, description="每页数量", ge=1, le=100)


# ==================== 响应 Schema ====================

class MaterialSchema(BaseModel):
    """素材响应 Schema"""
    
    id: int
    name: str
    type: str
    description: Optional[str]
    file_path: str
    file_size: int
    file_format: str
    duration: Optional[float]
    resolution: Optional[str]
    fps: Optional[int]
    tags: Optional[dict]
    extra_data: Optional[dict]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MaterialListSchema(BaseModel):
    """素材列表响应 Schema"""
    
    total: int = Field(..., description="总数")
    items: list[MaterialSchema] = Field(..., description="素材列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
