"""
数据库初始化脚本
"""
import asyncio

from loguru import logger

from backend.core.database import create_tables, init_db


async def main():
    """初始化数据库"""
    logger.info("开始初始化数据库...")
    
    # 初始化数据库连接
    await init_db()
    logger.info("数据库连接初始化完成")
    
    # 创建所有表
    await create_tables()
    logger.info("数据库表创建完成")
    
    logger.info("数据库初始化完成！")


if __name__ == "__main__":
    asyncio.run(main())
