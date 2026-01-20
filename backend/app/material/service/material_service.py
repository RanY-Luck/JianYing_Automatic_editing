"""
素材业务逻辑服务
"""
import os
from pathlib import Path
from typing import List, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.material.crud.crud_material import crud_material
from backend.app.material.model.material import Material
from backend.app.material.schema.material import (
    MaterialCreateParam,
    MaterialListSchema,
    MaterialQueryParam,
    MaterialSchema,
    MaterialUpdateParam,
)
from backend.common.enums import MaterialType
from backend.common.exception import (
    FileSizeError,
    FileFormatError,
    MaterialNotFoundError,
)
from backend.core.conf import settings
from backend.utils.file_utils import (
    ensure_dir,
    get_file_size,
    get_unique_filename,
    validate_file_format,
    validate_file_path,
    validate_file_size,
)


class MaterialService:
    """素材业务逻辑服务"""
    
    async def create(
        self,
        db: AsyncSession,
        param: MaterialCreateParam
    ) -> MaterialSchema:
        """
        创建素材
        
        :param db: 数据库会话
        :param param: 创建参数
        :return: 素材信息
        """
        # 验证文件路径
        if not validate_file_path(param.file_path):
            raise FileFormatError("文件路径不合法", [])
        
        # 验证文件格式
        allowed_formats = self._get_allowed_formats(param.type)
        if not validate_file_format(param.file_path, allowed_formats):
            raise FileFormatError(
                Path(param.file_path).suffix,
                allowed_formats
            )
        
        # 验证文件大小
        if not validate_file_size(param.file_path, settings.max_file_size):
            raise FileSizeError(
                get_file_size(param.file_path),
                settings.max_file_size
            )
        
        # 创建素材记录
        material_data = {
            'name': param.name,
            'type': param.type.value,
            'description': param.description,
            'file_path': param.file_path,
            'file_size': param.file_size,
            'file_format': param.file_format,
            'duration': param.duration,
            'resolution': param.resolution,
            'fps': param.fps,
            'tags': {'tags': param.tags} if param.tags else None,
        }
        
        material = await crud_material.create(db, material_data)
        logger.info(f"创建素材成功: {material.id} - {material.name}")
        
        return MaterialSchema.model_validate(material)
    
    async def get(self, db: AsyncSession, pk: int) -> MaterialSchema:
        """
        获取素材详情
        
        :param db: 数据库会话
        :param pk: 素材 ID
        :return: 素材信息
        """
        material = await crud_material.get(db, pk)
        if not material:
            raise MaterialNotFoundError(pk)
        
        return MaterialSchema.model_validate(material)
    
    async def update(
        self,
        db: AsyncSession,
        pk: int,
        param: MaterialUpdateParam
    ) -> MaterialSchema:
        """
        更新素材信息
        
        :param db: 数据库会话
        :param pk: 素材 ID
        :param param: 更新参数
        :return: 素材信息
        """
        # 检查素材是否存在
        material = await crud_material.get(db, pk)
        if not material:
            raise MaterialNotFoundError(pk)
        
        # 更新数据
        update_data = {}
        if param.name is not None:
            update_data['name'] = param.name
        if param.description is not None:
            update_data['description'] = param.description
        if param.tags is not None:
            update_data['tags'] = {'tags': param.tags}
        
        material = await crud_material.update(db, pk, update_data)
        logger.info(f"更新素材成功: {pk}")
        
        return MaterialSchema.model_validate(material)
    
    async def delete(self, db: AsyncSession, pk: int) -> bool:
        """
        删除素材
        
        :param db: 数据库会话
        :param pk: 素材 ID
        :return: 是否成功
        """
        # 检查素材是否存在
        material = await crud_material.get(db, pk)
        if not material:
            raise MaterialNotFoundError(pk)
        
        # 删除数据库记录
        await crud_material.delete(db, pk)
        
        # TODO: 删除文件（可选，根据业务需求决定）
        # if os.path.exists(material.file_path):
        #     os.remove(material.file_path)
        
        logger.info(f"删除素材成功: {pk}")
        return True
    
    async def get_list(
        self,
        db: AsyncSession,
        param: MaterialQueryParam
    ) -> MaterialListSchema:
        """
        获取素材列表（分页）
        
        :param db: 数据库会话
        :param param: 查询参数
        :return: 素材列表
        """
        items, total = await crud_material.get_paginated(
            db=db,
            page=param.page,
            page_size=param.page_size,
            material_type=param.type,
            name=param.name
        )
        
        return MaterialListSchema(
            total=total,
            items=[MaterialSchema.model_validate(item) for item in items],
            page=param.page,
            page_size=param.page_size
        )
    
    async def get_statistics(self, db: AsyncSession) -> dict:
        """
        获取素材统计信息
        
        :param db: 数据库会话
        :return: 统计信息
        """
        total = await crud_material.get_count_by_type(db)
        video_count = await crud_material.get_count_by_type(db, MaterialType.VIDEO)
        audio_count = await crud_material.get_count_by_type(db, MaterialType.AUDIO)
        image_count = await crud_material.get_count_by_type(db, MaterialType.IMAGE)
        text_count = await crud_material.get_count_by_type(db, MaterialType.TEXT)
        
        return {
            'total': total,
            'video': video_count,
            'audio': audio_count,
            'image': image_count,
            'text': text_count,
        }
    
    def _get_allowed_formats(self, material_type: MaterialType) -> List[str]:
        """
        获取允许的文件格式
        
        :param material_type: 素材类型
        :return: 允许的格式列表
        """
        if material_type == MaterialType.VIDEO:
            return settings.allowed_video_formats_list
        elif material_type == MaterialType.AUDIO:
            return settings.allowed_audio_formats_list
        elif material_type == MaterialType.IMAGE:
            return settings.allowed_image_formats_list
        else:
            return []


# 单例实例
material_service = MaterialService()
