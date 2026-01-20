"""
素材管理 API 路由
"""
from fastapi import APIRouter, UploadFile, File, Form
from loguru import logger

from backend.app.material.schema.material import (
    MaterialCreateParam,
    MaterialListSchema,
    MaterialQueryParam,
    MaterialSchema,
    MaterialUpdateParam,
)
from backend.app.material.service.material_service import material_service
from backend.common.enums import MaterialType
from backend.common.response import ResponseSchemaModel, response_base
from backend.core.deps import CurrentSession
from backend.utils.file_utils import ensure_dir, get_unique_filename
from backend.core.conf import settings
import os
import shutil

router = APIRouter()


@router.post("/materials/upload", summary="上传素材")
async def upload_material(
    db: CurrentSession,
    file: UploadFile = File(...),
    name: str = Form(...),
    type: MaterialType = Form(...),
    description: str = Form(None),
    tags: str = Form(None),  # JSON 字符串
) -> ResponseSchemaModel[MaterialSchema]:
    """
    上传素材文件
    
    :param db: 数据库会话
    :param file: 上传的文件
    :param name: 素材名称
    :param type: 素材类型
    :param description: 素材描述
    :param tags: 标签（JSON 字符串）
    :return: 素材信息
    """
    # 确定存储目录
    type_dir_map = {
        MaterialType.VIDEO: "videos",
        MaterialType.AUDIO: "audios",
        MaterialType.IMAGE: "images",
        MaterialType.TEXT: "texts",
    }
    storage_dir = os.path.join(
        settings.material_path,
        type_dir_map.get(type, "others")
    )
    ensure_dir(storage_dir)
    
    # 生成唯一文件名
    unique_filename = get_unique_filename(storage_dir, file.filename)
    file_path = os.path.join(storage_dir, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 获取文件信息
    file_size = os.path.getsize(file_path)
    file_format = os.path.splitext(file.filename)[1]
    
    # 解析标签
    import json
    tags_list = None
    if tags:
        try:
            tags_list = json.loads(tags)
        except:
            tags_list = [tags]
    
    # 创建素材记录
    param = MaterialCreateParam(
        name=name,
        type=type,
        description=description,
        file_path=file_path,
        file_size=file_size,
        file_format=file_format,
        tags=tags_list,
    )
    
    material = await material_service.create(db, param)
    
    logger.info(f"上传素材成功: {material.name}")
    return response_base.success(data=material, message="上传成功")


@router.get("/materials", summary="获取素材列表")
async def get_materials(
    db: CurrentSession,
    type: MaterialType = None,
    name: str = None,
    page: int = 1,
    page_size: int = 20,
) -> ResponseSchemaModel[MaterialListSchema]:
    """
    获取素材列表（分页）
    
    :param db: 数据库会话
    :param type: 素材类型过滤
    :param name: 名称模糊搜索
    :param page: 页码
    :param page_size: 每页数量
    :return: 素材列表
    """
    param = MaterialQueryParam(
        type=type,
        name=name,
        page=page,
        page_size=page_size
    )
    
    result = await material_service.get_list(db, param)
    return response_base.success(data=result)


@router.get("/materials/{pk}", summary="获取素材详情")
async def get_material(
    db: CurrentSession,
    pk: int
) -> ResponseSchemaModel[MaterialSchema]:
    """
    获取素材详情
    
    :param db: 数据库会话
    :param pk: 素材 ID
    :return: 素材信息
    """
    material = await material_service.get(db, pk)
    return response_base.success(data=material)


@router.put("/materials/{pk}", summary="更新素材信息")
async def update_material(
    db: CurrentSession,
    pk: int,
    param: MaterialUpdateParam
) -> ResponseSchemaModel[MaterialSchema]:
    """
    更新素材信息
    
    :param db: 数据库会话
    :param pk: 素材 ID
    :param param: 更新参数
    :return: 素材信息
    """
    material = await material_service.update(db, pk, param)
    return response_base.success(data=material, message="更新成功")


@router.delete("/materials/{pk}", summary="删除素材")
async def delete_material(
    db: CurrentSession,
    pk: int
) -> ResponseSchemaModel[bool]:
    """
    删除素材
    
    :param db: 数据库会话
    :param pk: 素材 ID
    :return: 是否成功
    """
    result = await material_service.delete(db, pk)
    return response_base.success(data=result, message="删除成功")


@router.get("/materials/statistics/summary", summary="获取素材统计")
async def get_material_statistics(
    db: CurrentSession
) -> ResponseSchemaModel[dict]:
    """
    获取素材统计信息
    
    :param db: 数据库会话
    :return: 统计信息
    """
    stats = await material_service.get_statistics(db)
    return response_base.success(data=stats)
