"""
模板 CRUD 层
"""
from typing import Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.template.model.template import Template
from backend.app.template.schema.template import TemplateCreate, TemplateUpdate


class CRUDTemplate:
    """
    模板 CRUD 操作
    
    NOTE: 提供模板的基础 CRUD 操作
    """
    
    def __init__(self):
        self.model = Template
    
    async def create(self, db: AsyncSession, obj_in: TemplateCreate) -> Template:
        """
        创建模板
        
        :param db: 数据库会话
        :param obj_in: 创建参数
        :return: 模板对象
        """
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, pk: int) -> Optional[Template]:
        """
        根据 ID 获取模板
        
        :param db: 数据库会话
        :param pk: 模板 ID
        :return: 模板对象
        """
        stmt = select(self.model).where(self.model.id == pk)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[Template]:
        """
        获取模板列表
        
        :param db: 数据库会话
        :param skip: 跳过数量
        :param limit: 限制数量
        :return: 模板列表
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, db: AsyncSession, pk: int, obj_in: TemplateUpdate) -> Template:
        """
        更新模板
        
        :param db: 数据库会话
        :param pk: 模板 ID
        :param obj_in: 更新参数
        :return: 模板对象
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        stmt = (
            update(self.model)
            .where(self.model.id == pk)
            .values(**update_data)
        )
        await db.execute(stmt)
        await db.flush()
        
        # 重新查询更新后的对象
        return await self.get(db, pk)
    
    async def delete(self, db: AsyncSession, pk: int) -> bool:
        """
        删除模板
        
        :param db: 数据库会话
        :param pk: 模板 ID
        :return: 是否成功
        """
        stmt = delete(self.model).where(self.model.id == pk)
        await db.execute(stmt)
        await db.flush()
        return True
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Template]:
        """
        根据名称获取模板
        
        :param db: 数据库会话
        :param name: 模板名称
        :return: 模板对象
        """
        stmt = select(self.model).where(self.model.name == name)
        result = await db.execute(stmt)
        return result.scalars().first()
    
    async def get_by_type(
        self,
        db: AsyncSession,
        template_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Template]:
        """
        根据类型获取模板列表
        
        :param db: 数据库会话
        :param template_type: 模板类型
        :param skip: 跳过数量
        :param limit: 限制数量
        :return: 模板列表
        """
        stmt = (
            select(self.model)
            .where(self.model.template_type == template_type)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_tag(
        self,
        db: AsyncSession,
        tag: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Template]:
        """
        根据标签获取模板列表
        
        :param db: 数据库会话
        :param tag: 标签
        :param skip: 跳过数量
        :param limit: 限制数量
        :return: 模板列表
        """
        # NOTE: 使用 JSON 包含查询
        stmt = (
            select(self.model)
            .where(self.model.tags.contains([tag]))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_public_templates(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[Template]:
        """
        获取公开模板列表
        
        :param db: 数据库会话
        :param skip: 跳过数量
        :param limit: 限制数量
        :return: 模板列表
        """
        stmt = (
            select(self.model)
            .where(self.model.is_public == True)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


# 单例实例
crud_template = CRUDTemplate()
