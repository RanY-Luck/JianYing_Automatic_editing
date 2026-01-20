from fastapi import APIRouter, Depends, Body
from typing import Dict, Any
from backend.app.task.service.editor_service import editor_service
from backend.common.response import response_base, ResponseSchemaModel
from backend.core.deps import CurrentSession

router = APIRouter()

@router.post("/draft/{draft_id}/add-music", summary="添加背景音乐")
async def add_music(
    draft_id: int,
    db: CurrentSession,
    music_path: str = Body(..., embed=True),
) -> ResponseSchemaModel:
    """
    为草稿添加背景音乐
    """
    await editor_service.add_music(db, draft_id, music_path)
    return response_base.success(msg="添加音乐成功")

@router.post("/draft/{draft_id}/deduplicate", summary="智能去重")
async def deduplicate(
    draft_id: int,
    db: CurrentSession,
    config: Dict[str, Any] = Body(default={}, embed=True),
) -> ResponseSchemaModel:
    """
    对草稿进行智能去重 (变速、镜像、裁剪等)
    config: {"speed": true, "mirror": true, "crop": true, "filter": true}
    """
    await editor_service.smart_deduplication(db, draft_id, config)
    return response_base.success(msg="去重处理成功")
