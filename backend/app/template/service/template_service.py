"""
模板 Service 层
"""
import os
from typing import Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.draft.crud.crud_draft import crud_draft
from backend.app.material.crud.crud_material import crud_material
from backend.app.template.crud.crud_template import crud_template
from backend.app.template.model.template import Template
from backend.app.template.schema.template import TemplateCreate, TemplateUpdate
from backend.common.exception import NotFoundError, BadRequestError
from backend.integrations.py_jianying import template_manager as py_template_manager


class TemplateService:
    """
    模板服务层
    
    NOTE: 处理模板相关的业务逻辑
    """
    
    async def create(self, db: AsyncSession, obj_in: TemplateCreate) -> Template:
        """
        创建模板
        
        :param db: 数据库会话
        :param obj_in: 创建参数
        :return: 模板对象
        """
        # 检查模板名称是否已存在
        existing = await crud_template.get_by_name(db, obj_in.name)
        if existing:
            raise BadRequestError(message=f"模板名称已存在: {obj_in.name}")
        
        # 验证模板数据
        if not py_template_manager.validate_template(obj_in.template_data):
            raise BadRequestError(message="模板数据格式无效")
        
        # 创建模板
        template = await crud_template.create(db, obj_in)
        logger.info(f"创建模板成功: {template.name} (ID: {template.id})")
        
        return template
    
    async def get(self, db: AsyncSession, pk: int) -> Template:
        """
        获取模板详情
        
        :param db: 数据库会话
        :param pk: 模板 ID
        :return: 模板对象
        """
        template = await crud_template.get(db, pk)
        if not template:
            raise NotFoundError()
        
        return template
    
    async def get_list(
        self,
        db: AsyncSession,
        template_type: Optional[str] = None,
        tag: Optional[str] = None,
        is_public: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Template]:
        """
        获取模板列表
        
        :param db: 数据库会话
        :param template_type: 模板类型过滤
        :param tag: 标签过滤
        :param is_public: 是否公开过滤
        :param skip: 跳过数量
        :param limit: 限制数量
        :return: 模板列表
        """
        if template_type:
            return await crud_template.get_by_type(db, template_type, skip, limit)
        elif tag:
            return await crud_template.get_by_tag(db, tag, skip, limit)
        elif is_public:
            return await crud_template.get_public_templates(db, skip, limit)
        else:
            return await crud_template.get_multi(db, skip=skip, limit=limit)
    
    async def update(self, db: AsyncSession, pk: int, obj_in: TemplateUpdate) -> Template:
        """
        更新模板
        
        :param db: 数据库会话
        :param pk: 模板 ID
        :param obj_in: 更新参数
        :return: 模板对象
        """
        template = await self.get(db, pk)
        
        # 如果更新模板数据,验证格式
        if obj_in.template_data:
            if not py_template_manager.validate_template(obj_in.template_data):
                raise BadRequestError(message="模板数据格式无效")
        
        # 更新模板
        updated_template = await crud_template.update(db, pk, obj_in)
        logger.info(f"更新模板成功: {template.name} (ID: {pk})")
        
        return updated_template
    
    async def delete(self, db: AsyncSession, pk: int) -> None:
        """
        删除模板
        
        :param db: 数据库会话
        :param pk: 模板 ID
        """
        template = await self.get(db, pk)
        
        await crud_template.delete(db, pk)
        logger.info(f"删除模板成功: {template.name} (ID: {pk})")
    
    async def create_from_draft(
        self,
        db: AsyncSession,
        draft_id: int,
        template_name: str,
        description: str = ""
    ) -> Template:
        """
        从草稿创建模板
        
        :param db: 数据库会话
        :param draft_id: 草稿 ID
        :param template_name: 模板名称
        :param description: 模板描述
        :return: 模板对象
        """
        # 获取草稿
        draft = await crud_draft.get(db, draft_id)
        if not draft:
            raise NotFoundError(msg=f"草稿不存在: {draft_id}")
        
        # 从草稿创建模板
        template_dir = py_template_manager.create_template_from_draft(
            draft.draft_path,
            template_name,
            description
        )
        
        if not template_dir:
            raise BadRequestError(message="从草稿创建模板失败")
        
        # 加载模板数据
        template_file = os.path.join(template_dir, "template.json")
        template_data = py_template_manager.load_template(template_file)
        
        if not template_data:
            raise BadRequestError(message="加载模板数据失败")
        
        # 保存到数据库
        obj_in = TemplateCreate(
            name=template_name,
            description=description,
            template_type="mixed",  # TODO: 根据草稿内容自动判断类型
            template_data=template_data,
            is_public=False
        )
        
        template = await self.create(db, obj_in)
        logger.info(f"从草稿创建模板成功: {template_name} (草稿 ID: {draft_id})")
        
        return template
    
    async def apply_to_draft(
        self,
        db: AsyncSession,
        template_id: int,
        draft_id: int,
        materials_mapping: dict[str, int]
    ) -> bool:
        """
        应用模板到草稿
        
        :param db: 数据库会话
        :param template_id: 模板 ID
        :param draft_id: 草稿 ID
        :param materials_mapping: 素材映射 {template_material_id: material_id}
        :return: 是否成功
        """
        # 获取模板
        template = await self.get(db, template_id)
        
        # 获取草稿
        draft = await crud_draft.get(db, draft_id)
        if not draft:
            raise NotFoundError(msg=f"草稿不存在: {draft_id}")
        
        # 验证素材映射
        for material_id in materials_mapping.values():
            material = await crud_material.get(db, material_id)
            if not material:
                raise NotFoundError(msg=f"素材不存在: {material_id}")
        
        # 检查素材兼容性
        materials = [await crud_material.get(db, mid) for mid in materials_mapping.values()]
        if not py_template_manager.check_materials_compatibility(template.template_data, materials):
            raise BadRequestError(message="素材与模板不兼容")
        
        # 保存模板到临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            import json
            json.dump(template.template_data, f, ensure_ascii=False, indent=2)
            temp_template_path = f.name
        
        try:
            # 转换素材映射 (int -> str)
            str_materials_mapping = {k: str(v) for k, v in materials_mapping.items()}
            
            # 应用模板
            success = py_template_manager.apply_template(
                draft.draft_path,
                temp_template_path,
                str_materials_mapping
            )
            
            if not success:
                raise BadRequestError(message="应用模板失败")
            
            logger.info(f"应用模板成功: 模板 {template.name} -> 草稿 {draft.name}")
            return True
        
        finally:
            # 删除临时文件
            if os.path.exists(temp_template_path):
                os.remove(temp_template_path)


# 单例实例
template_service = TemplateService()
