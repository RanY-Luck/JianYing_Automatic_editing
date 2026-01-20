"""
模板 API 路由
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from backend.app.template.schema.template import (
    TemplateApply,
    TemplateCreate,
    TemplateDetail,
    TemplateUpdate,
)
from backend.app.template.service.template_service import template_service
from backend.common.response import ResponseSchemaModel, response_base
from backend.core.deps import CurrentSession

router = APIRouter()


@router.post(
    "",
    summary="创建模板"
)
async def create_template(
    db: CurrentSession,
    obj_in: TemplateCreate
) -> ResponseSchemaModel[TemplateDetail]:
    """
    创建剪辑模板
    
    :param db: 数据库会话
    :param obj_in: 创建参数
    :return: 模板详情
    """
    template = await template_service.create(db, obj_in)
    return response_base.success(data=template)


@router.get(
    "",
    summary="获取模板列表"
)
async def get_template_list(
    db: CurrentSession,
    template_type: Annotated[Optional[str], Query(description="模板类型过滤")] = None,
    tag: Annotated[Optional[str], Query(description="标签过滤")] = None,
    is_public: Annotated[Optional[bool], Query(description="是否公开")] = None,
    skip: Annotated[int, Query(ge=0, description="跳过数量")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="限制数量")] = 20
) -> ResponseSchemaModel[list[TemplateDetail]]:
    """
    获取模板列表
    
    :param db: 数据库会话
    :param template_type: 模板类型过滤
    :param tag: 标签过滤
    :param is_public: 是否公开
    :param skip: 跳过数量
    :param limit: 限制数量
    :return: 模板列表
    """
    templates = await template_service.get_list(
        db,
        template_type=template_type,
        tag=tag,
        is_public=is_public,
        skip=skip,
        limit=limit
    )
    return response_base.success(data=templates)


@router.get(
    "/{pk}",
    summary="获取模板详情"
)
async def get_template(
    db: CurrentSession,
    pk: int
) -> ResponseSchemaModel[TemplateDetail]:
    """
    获取模板详情
    
    :param db: 数据库会话
    :param pk: 模板 ID
    :return: 模板详情
    """
    template = await template_service.get(db, pk)
    return response_base.success(data=template)


@router.put(
    "/{pk}",
    summary="更新模板"
)
async def update_template(
    db: CurrentSession,
    pk: int,
    obj_in: TemplateUpdate
) -> ResponseSchemaModel[TemplateDetail]:
    """
    更新模板信息
    
    :param db: 数据库会话
    :param pk: 模板 ID
    :param obj_in: 更新参数
    :return: 模板详情
    """
    template = await template_service.update(db, pk, obj_in)
    return response_base.success(data=template)


@router.delete(
    "/{pk}",
    summary="删除模板"
)
async def delete_template(
    db: CurrentSession,
    pk: int
) -> ResponseSchemaModel:
    """
    删除模板
    
    :param db: 数据库会话
    :param pk: 模板 ID
    :return: 成功响应
    """
    await template_service.delete(db, pk)
    return response_base.success()


@router.post(
    "/from-draft/{draft_id}",
    summary="从草稿创建模板"
)
async def create_template_from_draft(
    db: CurrentSession,
    draft_id: int,
    name: Annotated[str, Query(description="模板名称")],
    description: Annotated[str, Query(description="模板描述")] = ""
) -> ResponseSchemaModel[TemplateDetail]:
    """
    从草稿创建模板
    
    :param db: 数据库会话
    :param draft_id: 草稿 ID
    :param name: 模板名称
    :param description: 模板描述
    :return: 模板详情
    """
    template = await template_service.create_from_draft(db, draft_id, name, description)
    return response_base.success(data=template)


@router.post(
    "/{pk}/apply",
    summary="应用模板到草稿"
)
async def apply_template(
    db: CurrentSession,
    pk: int,
    obj_in: TemplateApply
) -> ResponseSchemaModel:
    """
    应用模板到草稿
    
    :param db: 数据库会话
    :param pk: 模板 ID
    :param obj_in: 应用参数
    :return: 成功响应
    """
    await template_service.apply_to_draft(
        db,
        pk,
        obj_in.draft_id,
        obj_in.materials_mapping
    )
    return response_base.success(msg="应用模板成功")
