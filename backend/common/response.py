"""
统一响应格式
"""
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar('T')


class ResponseSchemaModel(BaseModel, Generic[T]):
    """统一响应模型"""
    
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="success", description="响应消息")
    data: T | None = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }


class ResponseBase:
    """响应工具类"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        code: int = 200
    ) -> ResponseSchemaModel:
        """成功响应"""
        return ResponseSchemaModel(
            code=code,
            message=message,
            data=data
        )
    
    @staticmethod
    def error(
        message: str = "操作失败",
        code: int = 500,
        data: Any = None
    ) -> ResponseSchemaModel:
        """错误响应"""
        return ResponseSchemaModel(
            code=code,
            message=message,
            data=data
        )
    
    @staticmethod
    def not_found(
        message: str = "资源未找到",
        data: Any = None
    ) -> ResponseSchemaModel:
        """资源未找到响应"""
        return ResponseSchemaModel(
            code=404,
            message=message,
            data=data
        )
    
    @staticmethod
    def bad_request(
        message: str = "请求参数错误",
        data: Any = None
    ) -> ResponseSchemaModel:
        """请求参数错误响应"""
        return ResponseSchemaModel(
            code=400,
            message=message,
            data=data
        )
    
    @staticmethod
    def unauthorized(
        message: str = "未授权访问",
        data: Any = None
    ) -> ResponseSchemaModel:
        """未授权响应"""
        return ResponseSchemaModel(
            code=401,
            message=message,
            data=data
        )
    
    @staticmethod
    def forbidden(
        message: str = "权限不足",
        data: Any = None
    ) -> ResponseSchemaModel:
        """权限不足响应"""
        return ResponseSchemaModel(
            code=403,
            message=message,
            data=data
        )


# 全局响应实例
response_base = ResponseBase()
