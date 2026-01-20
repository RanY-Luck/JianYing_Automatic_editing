"""
依赖注入模块
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db

# ==================== 数据库会话依赖 ====================
CurrentSession = Annotated[AsyncSession, Depends(get_db)]

# NOTE: 如果需要手动控制事务提交，使用以下依赖
# CurrentSessionTransaction = Annotated[AsyncSession, Depends(get_db_with_transaction)]
