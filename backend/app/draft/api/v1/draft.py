"""
草稿管理 API 路由
"""
from fastapi import APIRouter
from backend.app.draft.schema.draft import (
    DraftCreateParam,
    DraftListSchema,
    DraftQueryParam,
    DraftSchema,
    DraftUpdateParam,
)
from backend.app.draft.service.draft_service import draft_service
from backend.common.enums import DraftStatus
from backend.common.response import ResponseSchemaModel, response_base
from backend.core.deps import CurrentSession

router = APIRouter()


@router.post("/drafts", summary="创建草稿")
async def create_draft(
        db: CurrentSession,
        param: DraftCreateParam
) -> ResponseSchemaModel[DraftSchema]:
    """
    创建草稿
    
    :param db: 数据库会话
    :param param: 创建参数
    :return: 草稿信息
    """
    draft = await draft_service.create(db, param)
    return response_base.success(data=draft, message="创建成功")


@router.get("/drafts", summary="获取草稿列表")
async def get_drafts(
        db: CurrentSession,
        status: DraftStatus = None,
        name: str = None,
        page: int = 1,
        page_size: int = 20,
) -> ResponseSchemaModel[DraftListSchema]:
    """
    获取草稿列表（分页）
    
    :param db: 数据库会话
    :param status: 草稿状态过滤
    :param name: 名称模糊搜索
    :param page: 页码
    :param page_size: 每页数量
    :return: 草稿列表
    """
    param = DraftQueryParam(
        status=status,
        name=name,
        page=page,
        page_size=page_size
    )

    result = await draft_service.get_list(db, param)
    return response_base.success(data=result)


@router.get("/drafts/{pk}", summary="获取草稿详情")
async def get_draft(
        db: CurrentSession,
        pk: int
) -> ResponseSchemaModel[DraftSchema]:
    """
    获取草稿详情
    
    :param db: 数据库会话
    :param pk: 草稿 ID
    :return: 草稿信息
    """
    draft = await draft_service.get(db, pk)
    return response_base.success(data=draft)


@router.put("/drafts/{pk}", summary="更新草稿信息")
async def update_draft(
        db: CurrentSession,
        pk: int,
        param: DraftUpdateParam
) -> ResponseSchemaModel[DraftSchema]:
    """
    更新草稿信息
    
    :param db: 数据库会话
    :param pk: 草稿 ID
    :param param: 更新参数
    :return: 草稿信息
    """
    draft = await draft_service.update(db, pk, param)
    return response_base.success(data=draft, message="更新成功")


@router.delete("/drafts/{pk}", summary="删除草稿")
async def delete_draft(
        db: CurrentSession,
        pk: int
) -> ResponseSchemaModel[bool]:
    """
    删除草稿
    
    :param db: 数据库会话
    :param pk: 草稿 ID
    :return: 是否成功
    """
    result = await draft_service.delete(db, pk)
    return response_base.success(data=result, message="删除成功")


@router.post("/drafts/import/{jianying_draft_id}", summary="从剪映导入草稿")
async def import_draft_from_jianying(
        db: CurrentSession,
        jianying_draft_id: str,
        name: str
) -> ResponseSchemaModel[DraftSchema]:
    """
    从剪映草稿箱导入草稿
    
    :param db: 数据库会话
    :param jianying_draft_id: 剪映草稿 ID
    :param name: 草稿名称
    :return: 草稿信息
    """
    draft = await draft_service.import_from_jianying(db, jianying_draft_id, name)
    return response_base.success(data=draft, message="导入成功")
