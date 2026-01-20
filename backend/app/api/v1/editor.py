from fastapi import APIRouter, Depends, Body
from typing import Dict, Any, Optional
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

@router.post("/draft/{draft_id}/filter", summary="添加滤镜")
async def add_filter(
    draft_id: int,
    db: CurrentSession,
    filter_name: str = Body(..., description="滤镜名称"),
    intensity: float = Body(1.0, description="滤镜强度 (0.0-1.0)"),
    segment_id: Optional[str] = Body(None, description="片段ID,为空则应用到所有视频片段"),
) -> ResponseSchemaModel:
    """
    添加滤镜到草稿
    
    可用滤镜: black_white, sepia, warm, cool, vivid, soft, 
             film_classic, film_noir, vintage_1980, vintage_polaroid,
             portrait_natural, portrait_beauty, landscape_vibrant, 
             landscape_sunset, food_delicious
    """
    await editor_service.add_filter(db, draft_id, filter_name, intensity, segment_id)
    return response_base.success(msg=f"添加滤镜成功: {filter_name}")

@router.post("/draft/{draft_id}/transition", summary="添加转场")
async def add_transition(
    draft_id: int,
    db: CurrentSession,
    transition_name: str = Body(..., description="转场名称"),
    duration: float = Body(0.5, description="转场时长(秒)"),
    from_segment_id: Optional[str] = Body(None, description="起始片段ID"),
    to_segment_id: Optional[str] = Body(None, description="结束片段ID"),
) -> ResponseSchemaModel:
    """
    添加转场效果
    
    可用转场: fade, dissolve, wipe_left, wipe_right, wipe_up, wipe_down,
             slide_left, slide_right, zoom_in, zoom_out, 
             rotate_clockwise, rotate_counterclockwise,
             blur, flash, circle, glitch, rgb_split
    """
    await editor_service.add_transition(db, draft_id, transition_name, duration, from_segment_id, to_segment_id)
    return response_base.success(msg=f"添加转场成功: {transition_name}")

@router.post("/draft/{draft_id}/subtitle", summary="添加字幕")
async def add_subtitle(
    draft_id: int,
    db: CurrentSession,
    text: str = Body(..., description="字幕文本"),
    start_time: float = Body(..., description="开始时间(秒)"),
    duration: float = Body(..., description="持续时长(秒)"),
    style: Optional[Dict[str, Any]] = Body(None, description="字幕样式"),
) -> ResponseSchemaModel:
    """
    添加字幕
    
    style 参数示例:
    {
        "font_size": 48,
        "font_color": "#FFFFFF",
        "position_x": 0.5,
        "position_y": 0.9
    }
    """
    await editor_service.add_subtitle(db, draft_id, text, start_time, duration, style)
    return response_base.success(msg="添加字幕成功")

@router.post("/draft/{draft_id}/split", summary="分割视频片段")
async def split_video(
    draft_id: int,
    db: CurrentSession,
    segment_id: str = Body(..., description="片段ID"),
    split_time: float = Body(..., description="分割时间点(秒,相对于片段开始)"),
) -> ResponseSchemaModel:
    """
    在指定时间点分割视频片段
    """
    await editor_service.split_video(db, draft_id, segment_id, split_time)
    return response_base.success(msg="分割视频成功")

@router.post("/draft/{draft_id}/trim", summary="裁剪视频片段")
async def trim_video(
    draft_id: int,
    db: CurrentSession,
    segment_id: str = Body(..., description="片段ID"),
    start_time: float = Body(..., description="起始时间(秒)"),
    end_time: float = Body(..., description="结束时间(秒)"),
) -> ResponseSchemaModel:
    """
    裁剪视频片段时间范围
    """
    await editor_service.trim_video(db, draft_id, segment_id, start_time, end_time)
    return response_base.success(msg="裁剪视频成功")

@router.post("/draft/{draft_id}/adjust-color", summary="调整视频颜色")
async def adjust_color(
    draft_id: int,
    db: CurrentSession,
    segment_id: str = Body(..., description="片段ID"),
    adjustments: Dict[str, float] = Body(..., description="调整参数"),
) -> ResponseSchemaModel:
    """
    调整视频颜色属性
    
    adjustments 参数示例:
    {
        "brightness": 0.5,   # 亮度 (-1.0 到 1.0)
        "contrast": 0.3,     # 对比度 (-1.0 到 1.0)
        "saturation": -0.2   # 饱和度 (-1.0 到 1.0)
    }
    """
    await editor_service.adjust_color(db, draft_id, segment_id, adjustments)
    return response_base.success(msg="调整颜色成功")

@router.post("/draft/{draft_id}/sticker", summary="添加贴纸/水印")
async def add_sticker(
    draft_id: int,
    db: CurrentSession,
    sticker_path: str = Body(..., description="贴纸文件路径"),
    start_time: float = Body(..., description="开始时间(秒)"),
    duration: float = Body(..., description="持续时长(秒)"),
    position: Optional[Dict[str, float]] = Body(None, description="位置"),
    scale: float = Body(1.0, description="缩放比例"),
) -> ResponseSchemaModel:
    """
    添加贴纸/水印
    
    position 参数示例:
    {
        "x": 0.9,  # X 位置 (0.0-1.0)
        "y": 0.1   # Y 位置 (0.0-1.0)
    }
    """
    await editor_service.add_sticker(db, draft_id, sticker_path, start_time, duration, position, scale)
    return response_base.success(msg="添加贴纸成功")

