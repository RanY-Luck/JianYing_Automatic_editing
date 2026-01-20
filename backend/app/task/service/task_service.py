"""
任务服务层
"""
import uuid
import asyncio
from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.task.crud.task import task_dao
from backend.app.task.model.task import Task
from backend.app.task.schema.task import TaskCreate, TaskUpdate, TaskInfo
from backend.common.enums import TaskStatus, TaskType
from backend.common.exception import NotFoundError


class TaskService:
    """任务服务类"""
    
    async def create_task(self, db: AsyncSession, obj_in: TaskCreate) -> Task:
        """
        创建任务
        :param db: 数据库会话
        :param obj_in: 创建参数
        :return: 任务对象
        """
        # 生成 UUID
        task_uuid = str(uuid.uuid4())
        
        # 创建任务
        task = await task_dao.create(db, obj_in, uuid=task_uuid)
        return task

    async def get_task(self, db: AsyncSession, task_id: int) -> Task:
        """
        获取任务
        :param db: 数据库会话
        :param task_id: 任务 ID
        :return: 任务对象
        """
        task = await task_dao.get(db, task_id)
        if not task:
            raise NotFoundError(msg="任务不存在")
        return task

    async def list_tasks(self, db: AsyncSession) -> List[Task]:
        """
        获取任务列表
        :param db: 数据库会话
        :return: 任务列表
        """
        return await task_dao.get_all(db)

    async def execute_task(self, db: AsyncSession, task_id: int):
        """
        执行任务 (异步)
        :param db: 数据库会话
        :param task_id: 任务 ID
        """
        task = await self.get_task(db, task_id)
        
        # 更新状态为运行中
        await task_dao.update(db, task_id, TaskUpdate(status=TaskStatus.RUNNING, started_at=datetime.now()))
        
        try:
            # TODO: 根据任务类型调用相应的处理逻辑
            # 目前仅做模拟
            if task.type == TaskType.AUTO_EDIT:
                await self._process_auto_edit(task)
            
            # 更新状态为完成
            await task_dao.update(db, task_id, TaskUpdate(
                status=TaskStatus.COMPLETED, 
                progress=100, 
                finished_at=datetime.now()
            ))
            
        except Exception as e:
            # 更新状态为失败
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            await task_dao.update(db, task_id, TaskUpdate(
                status=TaskStatus.FAILED, 
                error_msg=error_msg,
                finished_at=datetime.now()
            ))

    async def _process_auto_edit(self, task: Task):
        """
        处理自动剪辑任务
        """
        try:
            # 模拟参数解析，实际应该从 task.params 中获取
            # 假设 params 结构: {"draft_id": 123, "actions": [{"type": "deduplicate", "config": {...}}]}
            params = task.params if task.params else {}
            draft_id = params.get("draft_id")
            
            if not draft_id:
                logger.warning(f"任务 {task.id} 缺少 draft_id")
                return

            # 使用 editor_service
            from backend.app.task.service.editor_service import editor_service
            
            # 示例：执行去重
            if params.get("deduplicate"):
                # 注意：这里需要 session，但 _process_auto_edit 目前设计是在 execute_task 中调用
                # execute_task 已经有了 db session，但需要传递进来
                # 由于这是异步任务，可能需要独立的 session 或者从调用方传递
                # 这里假设调用方逻辑会优化，或者临时创建 session
                # 简单起见，仅记录日志，等待后续完善任务调度逻辑
                logger.info(f"正在为草稿 {draft_id} 执行去重...")
                # await editor_service.smart_deduplication(db, draft_id) 
                pass
                
        except Exception as e:
            logger.error(f"自动剪辑处理失败: {e}")
            raise


task_service = TaskService()
