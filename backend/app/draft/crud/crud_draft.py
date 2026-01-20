"""
草稿 CRUD 操作
"""
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.draft.model.draft import Draft
from backend.common.enums import DraftStatus


class CRUDDraft:
    """草稿 CRUD 操作类"""
    
    def __init__(self):
        self.model = Draft
    
    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> Draft:
        """创建草稿"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, pk: int) -> Optional[Draft]:
        """根据 ID 获取草稿"""
        stmt = select(self.model).where(self.model.id == pk)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update(self, db: AsyncSession, pk: int, obj_in: Dict[str, Any]) -> Draft:
        """更新草稿"""
        stmt = (
            update(self.model)
            .where(self.model.id == pk)
            .values(**obj_in)
        )
        await db.execute(stmt)
        await db.flush()
        
        # 重新查询更新后的对象
        return await self.get(db, pk)
    
    async def delete(self, db: AsyncSession, pk: int) -> bool:
        """删除草稿"""
        stmt = delete(self.model).where(self.model.id == pk)
        await db.execute(stmt)
        await db.flush()
        return True
    
    async def get_by_draft_id(self, db: AsyncSession, draft_id: str) -> Optional[Draft]:
        """
        根据剪映草稿 ID 获取草稿
        
        :param db: 数据库会话
        :param draft_id: 剪映草稿 ID
        :return: 草稿对象
        """
        stmt = select(self.model).where(self.model.draft_id == draft_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_status(
        self,
        db: AsyncSession,
        status: DraftStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Draft]:
        """
        根据状态获取草稿列表
        
        :param db: 数据库会话
        :param status: 草稿状态
        :param skip: 跳过数量
        :param limit: 限制数量
        :return: 草稿列表
        """
        stmt = (
            select(self.model)
            .where(self.model.status == status.value)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_paginated(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        status: Optional[DraftStatus] = None,
        name: Optional[str] = None
    ) -> tuple[List[Draft], int]:
        """
        分页获取草稿列表
        
        :param db: 数据库会话
        :param page: 页码
        :param page_size: 每页数量
        :param status: 草稿状态过滤
        :param name: 名称模糊搜索
        :return: (草稿列表, 总数)
        """
        # 构建查询条件
        conditions = []
        if status:
            conditions.append(self.model.status == status.value)
        if name:
            conditions.append(self.model.name.like(f"%{name}%"))
        
        # 查询总数
        count_stmt = select(func.count(self.model.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar_one()
        
        # 查询数据
        stmt = select(self.model)
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        items = list(result.scalars().all())
        
        return items, total


# 单例实例
crud_draft = CRUDDraft()
