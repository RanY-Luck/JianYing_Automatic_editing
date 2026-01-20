"""
任务 CRUD 操作
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.task.model.task import Task
from backend.app.task.schema.task import TaskCreate, TaskUpdate


class CRUDTask(CRUDPlus[Task]):
    """任务 CRUD 类"""
    
    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> Task | None:
        """
        根据 UUID 获取任务
        :param db: 数据库会话
        :param uuid: 任务 UUID
        :return: 任务对象
        """
        stmt = select(Task).where(Task.uuid == uuid)
        result = await db.execute(stmt)
        return result.scalars().first()


task_dao = CRUDTask(Task)
