"""
异步任务队列系统

支持:
1. 异步任务处理
2. 任务进度跟踪
3. 任务状态管理
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from loguru import logger
from pydantic import BaseModel


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"  # 等待中
    RUNNING = "running"  # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


class TaskType(str, Enum):
    """任务类型"""
    APPLY_TEMPLATE = "apply_template"  # 应用模板
    REMOVE_SILENCE = "remove_silence"  # 删除静音
    EXTRACT_HIGHLIGHTS = "extract_highlights"  # 提取高光
    BATCH_EXPORT = "batch_export"  # 批量导出
    CUSTOM = "custom"  # 自定义任务


class Task(BaseModel):
    """任务模型"""
    id: str
    type: TaskType
    status: TaskStatus
    progress: float = 0.0  # 0.0 - 1.0
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    params: Dict[str, Any] = {}
    result: Optional[Any] = None
    error: Optional[str] = None
    
    class Config:
        use_enum_values = True


class TaskQueue:
    """任务队列"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.max_concurrent_tasks = 3
    
    def create_task(
        self,
        task_type: TaskType,
        params: Dict[str, Any]
    ) -> str:
        """
        创建任务
        
        :param task_type: 任务类型
        :param params: 任务参数
        :return: 任务 ID
        """
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            type=task_type,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            params=params
        )
        
        self.tasks[task_id] = task
        logger.info(f"创建任务: {task_id} ({task_type})")
        
        return task_id
    
    async def execute_task(
        self,
        task_id: str,
        executor: Callable
    ):
        """
        执行任务
        
        :param task_id: 任务 ID
        :param executor: 执行函数
        """
        task = self.tasks.get(task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return
        
        try:
            # 更新状态为运行中
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            logger.info(f"开始执行任务: {task_id}")
            
            # 执行任务
            result = await executor(task.params, self._update_progress_callback(task_id))
            
            # 更新状态为完成
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            task.progress = 1.0
            logger.info(f"任务完成: {task_id}")
            
        except Exception as e:
            # 更新状态为失败
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error = str(e)
            logger.error(f"任务失败: {task_id} - {e}")
        
        finally:
            # 从运行任务中移除
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    def _update_progress_callback(self, task_id: str):
        """创建进度更新回调函数"""
        def update_progress(progress: float):
            task = self.tasks.get(task_id)
            if task:
                task.progress = min(1.0, max(0.0, progress))
        return update_progress
    
    async def start_task(
        self,
        task_id: str,
        executor: Callable
    ):
        """
        启动任务
        
        :param task_id: 任务 ID
        :param executor: 执行函数
        """
        # 检查并发任务数量
        while len(self.running_tasks) >= self.max_concurrent_tasks:
            await asyncio.sleep(0.5)
        
        # 创建异步任务
        async_task = asyncio.create_task(self.execute_task(task_id, executor))
        self.running_tasks[task_id] = async_task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务信息
        
        :param task_id: 任务 ID
        :return: 任务对象
        """
        return self.tasks.get(task_id)
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None
    ) -> List[Task]:
        """
        列出任务
        
        :param status: 状态过滤
        :param task_type: 类型过滤
        :return: 任务列表
        """
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if task_type:
            tasks = [t for t in tasks if t.type == task_type]
        
        return tasks
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        :param task_id: 任务 ID
        :return: 是否成功
        """
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status == TaskStatus.RUNNING:
            # 取消运行中的任务
            async_task = self.running_tasks.get(task_id)
            if async_task:
                async_task.cancel()
                del self.running_tasks[task_id]
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        logger.info(f"任务已取消: {task_id}")
        
        return True
    
    def clear_completed_tasks(self):
        """清理已完成的任务"""
        completed_ids = [
            task_id for task_id, task in self.tasks.items()
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
        ]
        
        for task_id in completed_ids:
            del self.tasks[task_id]
        
        logger.info(f"清理了 {len(completed_ids)} 个已完成任务")


# 全局任务队列实例
task_queue = TaskQueue()
