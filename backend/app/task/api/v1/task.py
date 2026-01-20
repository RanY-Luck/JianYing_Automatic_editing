"""
任务 API 路由
"""
from typing import List

from fastapi import APIRouter, BackgroundTasks

from backend.app.task.schema.task import TaskCreate, TaskInfo, TaskUpdate
from backend.app.task.service.task_service import task_service
from backend.common.response import ResponseSchemaModel, response_base
from backend.core.deps import CurrentSession

router = APIRouter()


@router.post("/tasks", summary="创建任务")
async def create_task(
    db: CurrentSession,
    obj_in: TaskCreate
) -> ResponseSchemaModel[TaskInfo]:
    """
    创建任务
    :param db: 数据库会话
    :param obj_in: 任务参数
    :return: 任务信息
    """
    task = await task_service.create_task(db, obj_in)
    return response_base.success(data=task, message="任务创建成功")


@router.get("/tasks/{pk}", summary="获取任务详情")
async def get_task(
    db: CurrentSession,
    pk: int
) -> ResponseSchemaModel[TaskInfo]:
    """
    获取任务详情
    :param db: 数据库会话
    :param pk: 任务 ID
    :return: 任务信息
    """
    task = await task_service.get_task(db, pk)
    return response_base.success(data=task)


@router.get("/tasks", summary="获取任务列表")
async def list_tasks(
    db: CurrentSession
) -> ResponseSchemaModel[List[TaskInfo]]:
    """
    获取任务列表
    :param db: 数据库会话
    :return: 任务列表
    """
    tasks = await task_service.list_tasks(db)
    return response_base.success(data=tasks)


@router.post("/tasks/{pk}/execute", summary="执行任务")
async def execute_task(
    db: CurrentSession,
    pk: int,
    background_tasks: BackgroundTasks
) -> ResponseSchemaModel[bool]:
    """
    执行任务
    :param db: 数据库会话
    :param pk: 任务 ID
    :param background_tasks: 后台任务
    :return: 是否提交成功
    """
    # 检查任务是否存在
    await task_service.get_task(db, pk)
    
    # 注意: 这里为了简单演示，直接使用当前的 db session
    # 在实际生产环境中，应该在后台任务中创建新的 session，或者使用任务队列(如 Celery)
    # 因为 CurrentSession 依赖于请求上下文，请求结束后可能会关闭
    # 但在此处，由于 task_service.execute_task 是 async 的，还是会直接 await 执行
    # 如果想真正的后台执行，需要处理 session 问题
    # 这里我们选择直接 await 执行演示效果
    
    await task_service.execute_task(db, pk)
    
    return response_base.success(data=True, message="任务已开始执行")
