"""
测试任务模块
"""
import sys
import os
import asyncio
import logging

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger

from backend.core.database import create_tables, init_db, async_session_maker
from backend.app.task.model.task import Task
from backend.app.task.schema.task import TaskCreate, TaskUpdate
from backend.app.task.service.task_service import task_service
from backend.common.enums import TaskType, TaskStatus


async def main():
    """测试任务模块功能"""
    logger.info("开始测试任务模块...")
    
    # 1. 初始化数据库
    await init_db()
    
    # 2. 确保表存在
    # 必须先导入 Task 模型，create_tables 才能识别
    await create_tables()
    logger.info("数据库表已确认")
    
    async with async_session_maker() as session:
        try:
            # 3. 创建任务
            logger.info("正在创建测试任务...")
            task_in = TaskCreate(
                name="测试自动剪辑任务",
                type=TaskType.AUTO_EDIT,
                params={"template_id": 1, "video_source": "test.mp4"}
            )
            task = await task_service.create_task(session, task_in)
            logger.info(f"任务创建成功: {task.id} - {task.uuid}")
            
            # 4. 获取任务
            fetched_task = await task_service.get_task(session, task.id)
            logger.info(f"获取任务详情: {fetched_task.name}, 状态: {fetched_task.status}")
            assert fetched_task.id == task.id
            
            # 5. 更新任务
            logger.info("正在更新任务状态...")
            await task_service.execute_task(session, task.id)
            
            # execute_task 在当前实现中是全同步等待 sleep 的，所以这里应该已经是 COMPLETED 或 FAILED
            # 如果是异步后台，这里可能是 RUNNING
            
            final_task = await task_service.get_task(session, task.id)
            logger.info(f"任务执行后状态: {final_task.status}")
            logger.info(f"任务结果: {final_task.result}")
            logger.info(f"错误信息: {final_task.error_msg}")
            
            # 手动清理测试数据
            logger.info("清理测试数据...")
            from backend.app.task.crud.task import task_dao
            await task_dao.delete(session, task.id)
            logger.info("测试数据已清理")
            
            logger.info("✓ 所有测试通过!")
            
        except Exception as e:
            logger.error(f"测试失败: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    # 配置 logger
    logger.configure(handlers=[{"sink": sys.stdout, "level": "INFO"}])
    asyncio.run(main())
