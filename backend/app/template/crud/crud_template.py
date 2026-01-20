"""
模板 CRUD 层
"""
from typing import Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.template.model.template import Template


class CRUDTemplate(CRUDPlus[Template]):
    """
    模板 CRUD 操作
    
    NOTE: 继承 CRUDPlus,提供基础 CRUD 操作
    """
    
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
crud_template = CRUDTemplate(Template)
