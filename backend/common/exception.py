"""
自定义异常类
"""


class BaseAPIException(Exception):
    """API 异常基类"""
    
    def __init__(
        self,
        message: str = "服务器内部错误",
        code: int = 500,
        data: dict | None = None
    ):
        self.message = message
        self.code = code
        self.data = data or {}
        super().__init__(self.message)


class NotFoundError(BaseAPIException):
    """资源未找到异常"""
    
    def __init__(self, message: str = "资源未找到", data: dict | None = None):
        super().__init__(message=message, code=404, data=data)


class BadRequestError(BaseAPIException):
    """请求参数错误异常"""
    
    def __init__(self, message: str = "请求参数错误", data: dict | None = None):
        super().__init__(message=message, code=400, data=data)


class UnauthorizedError(BaseAPIException):
    """未授权异常"""
    
    def __init__(self, message: str = "未授权访问", data: dict | None = None):
        super().__init__(message=message, code=401, data=data)


class ForbiddenError(BaseAPIException):
    """权限不足异常"""
    
    def __init__(self, message: str = "权限不足", data: dict | None = None):
        super().__init__(message=message, code=403, data=data)


class ConflictError(BaseAPIException):
    """资源冲突异常"""
    
    def __init__(self, message: str = "资源冲突", data: dict | None = None):
        super().__init__(message=message, code=409, data=data)


class ValidationError(BaseAPIException):
    """数据验证错误异常"""
    
    def __init__(self, message: str = "数据验证失败", data: dict | None = None):
        super().__init__(message=message, code=422, data=data)


class InternalServerError(BaseAPIException):
    """服务器内部错误异常"""
    
    def __init__(self, message: str = "服务器内部错误", data: dict | None = None):
        super().__init__(message=message, code=500, data=data)


class ServiceUnavailableError(BaseAPIException):
    """服务不可用异常"""
    
    def __init__(self, message: str = "服务暂时不可用", data: dict | None = None):
        super().__init__(message=message, code=503, data=data)


# ==================== 业务异常 ====================

class MaterialNotFoundError(NotFoundError):
    """素材未找到异常"""
    
    def __init__(self, material_id: int | str):
        super().__init__(message=f"素材 {material_id} 未找到")


class DraftNotFoundError(NotFoundError):
    """草稿未找到异常"""
    
    def __init__(self, draft_id: int | str):
        super().__init__(message=f"草稿 {draft_id} 未找到")


class TemplateNotFoundError(NotFoundError):
    """模板未找到异常"""
    
    def __init__(self, template_id: int | str):
        super().__init__(message=f"模板 {template_id} 未找到")


class TaskNotFoundError(NotFoundError):
    """任务未找到异常"""
    
    def __init__(self, task_id: int | str):
        super().__init__(message=f"任务 {task_id} 未找到")


class ExportNotFoundError(NotFoundError):
    """导出任务未找到异常"""
    
    def __init__(self, export_id: int | str):
        super().__init__(message=f"导出任务 {export_id} 未找到")


class FileFormatError(BadRequestError):
    """文件格式错误异常"""
    
    def __init__(self, file_format: str, allowed_formats: list[str]):
        super().__init__(
            message=f"不支持的文件格式 {file_format}，允许的格式：{', '.join(allowed_formats)}"
        )


class FileSizeError(BadRequestError):
    """文件大小超限异常"""
    
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            message=f"文件大小 {file_size} 字节超过限制 {max_size} 字节"
        )


class TaskExecutionError(InternalServerError):
    """任务执行错误异常"""
    
    def __init__(self, task_id: int | str, error_message: str):
        super().__init__(
            message=f"任务 {task_id} 执行失败：{error_message}"
        )


class ExportExecutionError(InternalServerError):
    """导出执行错误异常"""
    
    def __init__(self, export_id: int | str, error_message: str):
        super().__init__(
            message=f"导出任务 {export_id} 执行失败：{error_message}"
        )
