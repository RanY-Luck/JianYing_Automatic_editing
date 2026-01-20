"""
剪映自动剪辑系统 - 主应用入口
"""
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from backend.common.exception import BaseAPIException
from backend.common.response import response_base
from backend.core.conf import app_config, settings
from backend.core.database import close_db, create_tables, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动中...")

    # 初始化数据库
    await init_db()
    logger.info("数据库连接初始化完成")

    # 创建数据库表
    await create_tables()
    logger.info("数据库表创建完成")

    yield

    # 关闭时执行
    logger.info("应用关闭中...")
    await close_db()
    logger.info("数据库连接已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=app_config.get('app.name', '剪映自动剪辑系统'),
    version=app_config.get('app.version', '1.0.0'),
    description=app_config.get('app.description', '基于 JianYingApi 和 PyJianying 的自动化视频剪辑系统'),
    lifespan=lifespan,
)

# CORS 中间件
cors_config = app_config.get('security.cors', {})
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.get('allow_origins', ["*"]),
    allow_credentials=cors_config.get('allow_credentials', True),
    allow_methods=cors_config.get('allow_methods', ["*"]),
    allow_headers=cors_config.get('allow_headers', ["*"]),
)


# 全局异常处理
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """处理自定义 API 异常"""
    logger.error(f"API 异常: {exc.message}")
    return JSONResponse(
        status_code=exc.code,
        content=response_base.error(
            message=exc.message,
            code=exc.code,
            data=exc.data
        ).model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理全局异常"""
    logger.exception(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": None,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )


# 健康检查
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return response_base.success(data={"status": "healthy"})


# 根路径
@app.get("/", tags=["系统"])
async def root():
    """根路径"""
    return response_base.success(
        data={
            "name": app_config.get('app.name'),
            "version": app_config.get('app.version'),
            "description": app_config.get('app.description'),
        }
    )


# 注册路由
from backend.app.material.api.v1 import material as material_router
from backend.app.draft.api.v1 import draft as draft_router
from backend.app.template.api.v1 import template as template_router
from backend.app.task.api.v1 import task as task_router

app.include_router(material_router.router, prefix="/api/v1", tags=["素材管理"])
app.include_router(draft_router.router, prefix="/api/v1", tags=["草稿管理"])
app.include_router(template_router.router, prefix="/api/v1/templates", tags=["模板管理"])
app.include_router(task_router.router, prefix="/api/v1", tags=["任务管理"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=app_config.get('server.reload', True),
        log_level=settings.log_level.lower(),
    )
