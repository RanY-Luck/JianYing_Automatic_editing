"""
草稿业务逻辑服务
"""
import uuid
from typing import Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.draft.crud.crud_draft import crud_draft
from backend.app.draft.schema.draft import (
    DraftCreateParam,
    DraftListSchema,
    DraftQueryParam,
    DraftSchema,
    DraftUpdateParam,
)
from backend.common.enums import DraftStatus
from backend.common.exception import DraftNotFoundError
from backend.integrations.py_jianying.draft_manager import draft_manager


class DraftService:
    """草稿业务逻辑服务"""
    
    async def create(
        self,
        db: AsyncSession,
        param: DraftCreateParam
    ) -> DraftSchema:
        """
        创建草稿
        
        :param db: 数据库会话
        :param param: 创建参数
        :return: 草稿信息
        """
        # 生成唯一的草稿 ID
        draft_id = str(uuid.uuid4())
        
        # 创建草稿文件夹
        draft_path = draft_manager.create_draft_folder(param.name)
        
        # 创建草稿记录
        draft_data = {
            'name': param.name,
            'draft_id': draft_id,
            'draft_path': draft_path,
            'description': param.description,
            'status': DraftStatus.EDITING.value,
            'duration': 0.0,
            'resolution': param.resolution,
            'fps': param.fps,
        }
        
        draft = await crud_draft.create(db, draft_data)
        logger.info(f"创建草稿成功: {draft.id} - {draft.name}")
        
        return DraftSchema.model_validate(draft)
    
    async def get(self, db: AsyncSession, pk: int) -> DraftSchema:
        """
        获取草稿详情
        
        :param db: 数据库会话
        :param pk: 草稿 ID
        :return: 草稿信息
        """
        draft = await crud_draft.get(db, pk)
        if not draft:
            raise DraftNotFoundError(pk)
        
        return DraftSchema.model_validate(draft)
    
    async def update(
        self,
        db: AsyncSession,
        pk: int,
        param: DraftUpdateParam
    ) -> DraftSchema:
        """
        更新草稿信息
        
        :param db: 数据库会话
        :param pk: 草稿 ID
        :param param: 更新参数
        :return: 草稿信息
        """
        # 检查草稿是否存在
        draft = await crud_draft.get(db, pk)
        if not draft:
            raise DraftNotFoundError(pk)
        
        # 更新数据
        update_data = {}
        if param.name is not None:
            update_data['name'] = param.name
        if param.description is not None:
            update_data['description'] = param.description
        if param.status is not None:
            update_data['status'] = param.status.value
        
        draft = await crud_draft.update(db, pk, update_data)
        logger.info(f"更新草稿成功: {pk}")
        
        return DraftSchema.model_validate(draft)
    
    async def delete(self, db: AsyncSession, pk: int) -> bool:
        """
        删除草稿
        
        :param db: 数据库会话
        :param pk: 草稿 ID
        :return: 是否成功
        """
        # 检查草稿是否存在
        draft = await crud_draft.get(db, pk)
        if not draft:
            raise DraftNotFoundError(pk)
        
        # 删除草稿文件夹
        draft_manager.delete_draft_folder(draft.draft_path)
        
        # 删除数据库记录
        await crud_draft.delete(db, pk)
        
        logger.info(f"删除草稿成功: {pk}")
        return True
    
    async def get_list(
        self,
        db: AsyncSession,
        param: DraftQueryParam
    ) -> DraftListSchema:
        """
        获取草稿列表（分页）
        
        :param db: 数据库会话
        :param param: 查询参数
        :return: 草稿列表
        """
        items, total = await crud_draft.get_paginated(
            db=db,
            page=param.page,
            page_size=param.page_size,
            status=param.status,
            name=param.name
        )
        
        return DraftListSchema(
            total=total,
            items=[DraftSchema.model_validate(item) for item in items],
            page=param.page,
            page_size=param.page_size
        )
    
    async def import_from_jianying(
        self,
        db: AsyncSession,
        jianying_draft_id: str,
        name: str
    ) -> DraftSchema:
        """
        从剪映草稿箱导入草稿
        
        :param db: 数据库会话
        :param jianying_draft_id: 剪映草稿 ID
        :param name: 草稿名称
        :return: 草稿信息
        """
        # 获取剪映草稿信息
        draft_info = draft_manager.get_draft_info(jianying_draft_id)
        if not draft_info:
            raise DraftNotFoundError(jianying_draft_id)
        
        # 复制草稿到存储目录
        target_path = draft_manager.copy_draft_to_storage(jianying_draft_id, name)
        if not target_path:
            raise Exception("复制草稿失败")
        
        # 创建草稿记录
        draft_data = {
            'name': name,
            'draft_id': jianying_draft_id,
            'draft_path': target_path,
            'status': DraftStatus.EDITING.value,
            'duration': draft_info.get('duration', 0.0),
        }
        
        draft = await crud_draft.create(db, draft_data)
        logger.info(f"导入草稿成功: {draft.id} - {draft.name}")
        
        return DraftSchema.model_validate(draft)


# 单例实例
draft_service = DraftService()
