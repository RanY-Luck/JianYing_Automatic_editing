"""
素材 CRUD 操作
"""
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.material.model.material import Material
from backend.common.enums import MaterialType


class CRUDMaterial:
    """素材 CRUD 操作类"""
    
    def __init__(self):
        self.model = Material
    
    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> Material:
        """
        创建素材
        
        :param db: 数据库会话
        :param obj_in: 创建数据
        :return: 素材对象
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, pk: int) -> Optional[Material]:
        """
        根据 ID 获取素材
        
        :param db: 数据库会话
        :param pk: 素材 ID
        :return: 素材对象
        """
        stmt = select(self.model).where(self.model.id == pk)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update(self, db: AsyncSession, pk: int, obj_in: Dict[str, Any]) -> Material:
        """
        更新素材
        
        :param db: 数据库会话
        :param pk: 素材 ID
        :param obj_in: 更新数据
        :return: 素材对象
        """
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
        """
        删除素材
        
        :param db: 数据库会话
        :param pk: 素材 ID
        :return: 是否成功
        """
        stmt = delete(self.model).where(self.model.id == pk)
        await db.execute(stmt)
        await db.flush()
        return True
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Material]:
        """
        根据名称获取素材
        
        :param db: 数据库会话
        :param name: 素材名称
        :return: 素材对象
        """
        stmt = select(self.model).where(self.model.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_type(
        self,
        db: AsyncSession,
        material_type: MaterialType,
        skip: int = 0,
        limit: int = 100
    ) -> List[Material]:
        """
        根据类型获取素材列表
        
        :param db: 数据库会话
        :param material_type: 素材类型
        :param skip: 跳过数量
        :param limit: 限制数量
        :return: 素材列表
        """
        stmt = (
            select(self.model)
            .where(self.model.type == material_type.value)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def search_by_name(
        self,
        db: AsyncSession,
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Material]:
        """
        根据名称模糊搜索素材
        
        :param db: 数据库会话
        :param name: 素材名称（模糊匹配）
        :param skip: 跳过数量
        :param limit: 限制数量
        :return: 素材列表
        """
        stmt = (
            select(self.model)
            .where(self.model.name.like(f"%{name}%"))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_count_by_type(
        self,
        db: AsyncSession,
        material_type: Optional[MaterialType] = None
    ) -> int:
        """
        获取指定类型的素材数量
        
        :param db: 数据库会话
        :param material_type: 素材类型（None 表示所有类型）
        :return: 素材数量
        """
        stmt = select(func.count(self.model.id))
        if material_type:
            stmt = stmt.where(self.model.type == material_type.value)
        result = await db.execute(stmt)
        return result.scalar_one()
    
    async def get_paginated(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        material_type: Optional[MaterialType] = None,
        name: Optional[str] = None
    ) -> tuple[List[Material], int]:
        """
        分页获取素材列表
        
        :param db: 数据库会话
        :param page: 页码
        :param page_size: 每页数量
        :param material_type: 素材类型过滤
        :param name: 名称模糊搜索
        :return: (素材列表, 总数)
        """
        # 构建查询条件
        conditions = []
        if material_type:
            conditions.append(self.model.type == material_type.value)
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
crud_material = CRUDMaterial()
