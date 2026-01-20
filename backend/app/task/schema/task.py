"""
任务 Schema 定义
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.common.enums import TaskStatus, TaskType


class TaskSchemaBase(BaseModel):
    """任务基础 Schema"""
    name: str = Field(..., description="任务名称")
    type: TaskType = Field(default=TaskType.AUTO_EDIT, description="任务类型")
    params: Optional[dict] = Field(default=None, description="任务参数")


class TaskCreate(TaskSchemaBase):
    """创建任务 Schema"""
    pass


class TaskUpdate(BaseModel):
    """更新任务 Schema"""
    name: Optional[str] = Field(None, description="任务名称")
    status: Optional[TaskStatus] = Field(None, description="任务状态")
    result: Optional[dict] = Field(None, description="任务结果")
    error_msg: Optional[str] = Field(None, description="错误信息")
    progress: Optional[int] = Field(None, ge=0, le=100, description="进度")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    finished_at: Optional[datetime] = Field(None, description="完成时间")


class TaskInfo(TaskSchemaBase):
    """任务信息 Schema"""
    id: int = Field(..., description="任务 ID")
    uuid: str = Field(..., description="任务 UUID")
    status: TaskStatus = Field(..., description="任务状态")
    result: Optional[dict] = Field(None, description="任务结果")
    error_msg: Optional[str] = Field(None, description="错误信息")
    progress: int = Field(0, description="进度")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    finished_at: Optional[datetime] = Field(None, description="完成时间")

    class Config:
        from_attributes = True
