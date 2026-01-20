"""
编辑器服务层 - 衔接 API 与 DraftEditor
"""
import os
import json
from typing import Dict, Any, Optional, List
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.draft.crud.crud_draft import crud_draft
from backend.common.exception import NotFoundError, BadRequestError
from backend.integrations.jianying_api.draft_editor import DraftEditor
from backend.integrations.py_jianying.effect_manager import effect_manager
from backend.integrations.py_jianying.track_manager import track_manager

class EditorService:
    """编辑器服务"""

    async def add_music(
        self,
        db: AsyncSession,
        draft_id: int,
        music_path: str,
        start_time: int = 0,
        duration: int = -1,
        volume: float = 1.0
    ) -> bool:
        """
        为草稿添加背景音乐
        """
        draft = await crud_draft.get(db, draft_id)
        if not draft:
            raise NotFoundError()

        content_path = os.path.join(draft.draft_path, "draft_content.json")
        if not os.path.exists(content_path):
            raise BadRequestError(message="草稿内容文件不存在，可能是新版本草稿(加密)")

        try:
            with open(content_path, "r", encoding="utf-8") as f:
                content = json.load(f)

            editor = DraftEditor(content)
            if editor.add_audio(music_path, start_time, duration, volume):
                # 保存回文件
                new_content = editor.get_content()
                # 备份
                import shutil
                shutil.copy(content_path, content_path + ".bak")
                
                with open(content_path, "w", encoding="utf-8") as f:
                    json.dump(new_content, f, ensure_ascii=False, indent=2)
                
                logger.info(f"添加音乐成功: {draft_id}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"编辑草稿失败: {e}")
            raise BadRequestError(message=f"编辑失败: {str(e)}")

    async def smart_deduplication(
        self,
        db: AsyncSession,
        draft_id: int,
        config: Dict[str, Any] = None
    ) -> bool:
        """
        对草稿进行智能去重
        """
        draft = await crud_draft.get(db, draft_id)
        if not draft:
            raise NotFoundError()

        content_path = os.path.join(draft.draft_path, "draft_content.json")
        if not os.path.exists(content_path):
            raise BadRequestError(message="草稿内容文件不存在")

        try:
            with open(content_path, "r", encoding="utf-8") as f:
                content = json.load(f)

            editor = DraftEditor(content)
            if editor.deduplicate(config):
                # 保存
                new_content = editor.get_content()
                import shutil
                shutil.copy(content_path, content_path + ".bak")

                with open(content_path, "w", encoding="utf-8") as f:
                    json.dump(new_content, f, ensure_ascii=False, indent=2)
                
                logger.info(f"去重成功: {draft_id}")
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"去重失败: {e}")
            raise BadRequestError(message=str(e))
    
    async def add_filter(
        self,
        db: AsyncSession,
        draft_id: int,
        filter_name: str,
        intensity: float = 1.0,
        segment_id: Optional[str] = None
    ) -> bool:
        """
        添加滤镜到草稿
        
        :param db: 数据库会话
        :param draft_id: 草稿 ID
        :param filter_name: 滤镜名称
        :param intensity: 滤镜强度 (0.0-1.0)
        :param segment_id: 片段 ID,为 None 则应用到所有视频片段
        :return: 是否成功
        """
        draft = await crud_draft.get(db, draft_id)
        if not draft:
            raise NotFoundError()

        content_path = os.path.join(draft.draft_path, "draft_content.json")
        if not os.path.exists(content_path):
            raise BadRequestError(message="草稿内容文件不存在")

        try:
            with open(content_path, "r", encoding="utf-8") as f:
                content = json.load(f)

            editor = DraftEditor(content)
            if editor.add_filter(filter_name, intensity, segment_id):
                self._save_draft_content(content_path, editor.get_content())
                logger.info(f"添加滤镜成功: {draft_id} - {filter_name}")
                return True
            return False

        except Exception as e:
            logger.error(f"添加滤镜失败: {e}")
            raise BadRequestError(message=f"添加滤镜失败: {str(e)}")
    
    async def add_transition(
        self,
        db: AsyncSession,
        draft_id: int,
        transition_name: str,
        duration: float = 0.5,
        from_segment_id: Optional[str] = None,
        to_segment_id: Optional[str] = None
    ) -> bool:
        """
        添加转场效果
        
        :param db: 数据库会话
        :param draft_id: 草稿 ID
        :param transition_name: 转场名称
        :param duration: 转场时长(秒)
        :param from_segment_id: 起始片段 ID
        :param to_segment_id: 结束片段 ID
        :return: 是否成功
        """
        draft = await crud_draft.get(db, draft_id)
        if not draft:
            raise NotFoundError()

        content_path = os.path.join(draft.draft_path, "draft_content.json")
        if not os.path.exists(content_path):
            raise BadRequestError(message="草稿内容文件不存在")

        try:
            with open(content_path, "r", encoding="utf-8") as f:
                content = json.load(f)

            editor = DraftEditor(content)
            if editor.add_transition(transition_name, duration, from_segment_id, to_segment_id):
                self._save_draft_content(content_path, editor.get_content())
                logger.info(f"添加转场成功: {draft_id} - {transition_name}")
                return True
            return False

        except Exception as e:
            logger.error(f"添加转场失败: {e}")
            raise BadRequestError(message=f"添加转场失败: {str(e)}")
    
    async def add_subtitle(
        self,
        db: AsyncSession,
        draft_id: int,
        text: str,
        start_time: float,
        duration: float,
        style: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        添加字幕
        
        :param db: 数据库会话
        :param draft_id: 草稿 ID
        :param text: 字幕文本
        :param start_time: 开始时间(秒)
        :param duration: 持续时长(秒)
        :param style: 字幕样式配置
        :return: 是否成功
        """
        draft = await crud_draft.get(db, draft_id)
        if not draft:
            raise NotFoundError()

        content_path = os.path.join(draft.draft_path, "draft_content.json")
        if not os.path.exists(content_path):
            raise BadRequestError(message="草稿内容文件不存在")

        try:
            with open(content_path, "r", encoding="utf-8") as f:
                content = json.load(f)

            editor = DraftEditor(content)
            
            # 解析样式配置
            if style is None:
                style = {}
            
            font_size = style.get("font_size", 48)
            font_color = style.get("font_color", "#FFFFFF")
            position_x = style.get("position_x", 0.5)
            position_y = style.get("position_y", 0.9)
            
            if editor.add_text(text, start_time, duration, font_size, font_color, position_x, position_y):
                self._save_draft_content(content_path, editor.get_content())
                logger.info(f"添加字幕成功: {draft_id} - {text}")
                return True
            return False

        except Exception as e:
            logger.error(f"添加字幕失败: {e}")
            raise BadRequestError(message=f"添加字幕失败: {str(e)}")
    
    async def split_video(
        self,
        db: AsyncSession,
        draft_id: int,
        segment_id: str,
        split_time: float
    ) -> bool:
        """
        分割视频片段
        
        :param db: 数据库会话
        :param draft_id: 草稿 ID
        :param segment_id: 片段 ID
        :param split_time: 分割时间点(秒)
        :return: 是否成功
        """
        draft = await crud_draft.get(db, draft_id)
        if not draft:
            raise NotFoundError()

        content_path = os.path.join(draft.draft_path, "draft_content.json")
        if not os.path.exists(content_path):
            raise BadRequestError(message="草稿内容文件不存在")

        try:
            with open(content_path, "r", encoding="utf-8") as f:
                content = json.load(f)

            editor = DraftEditor(content)
            if editor.split_segment(segment_id, split_time):
                self._save_draft_content(content_path, editor.get_content())
                logger.info(f"分割视频成功: {draft_id} - {segment_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"分割视频失败: {e}")
            raise BadRequestError(message=f"分割视频失败: {str(e)}")
    
    async def trim_video(
        self,
        db: AsyncSession,
        draft_id: int,
        segment_id: str,
        start_time: float,
        end_time: float
    ) -> bool:
        """
        裁剪视频片段
        
        :param db: 数据库会话
        :param draft_id: 草稿 ID
        :param segment_id: 片段 ID
        :param start_time: 起始时间(秒)
        :param end_time: 结束时间(秒)
        :return: 是否成功
        """
        draft = await crud_draft.get(db, draft_id)
        if not draft:
            raise NotFoundError()

        content_path = os.path.join(draft.draft_path, "draft_content.json")
        if not os.path.exists(content_path):
            raise BadRequestError(message="草稿内容文件不存在")

        try:
            with open(content_path, "r", encoding="utf-8") as f:
                content = json.load(f)

            editor = DraftEditor(content)
            if editor.trim_segment(segment_id, start_time, end_time):
                self._save_draft_content(content_path, editor.get_content())
                logger.info(f"裁剪视频成功: {draft_id} - {segment_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"裁剪视频失败: {e}")
            raise BadRequestError(message=f"裁剪视频失败: {str(e)}")
    
    async def adjust_color(
        self,
        db: AsyncSession,
        draft_id: int,
        segment_id: str,
        adjustments: Dict[str, float]
    ) -> bool:
        """
        调整视频颜色属性
        
        :param db: 数据库会话
        :param draft_id: 草稿 ID
        :param segment_id: 片段 ID
        :param adjustments: 调整参数 {"brightness": 0.5, "contrast": 0.3, "saturation": -0.2}
        :return: 是否成功
        """
        draft = await crud_draft.get(db, draft_id)
        if not draft:
            raise NotFoundError()

        content_path = os.path.join(draft.draft_path, "draft_content.json")
        if not os.path.exists(content_path):
            raise BadRequestError(message="草稿内容文件不存在")

        try:
            with open(content_path, "r", encoding="utf-8") as f:
                content = json.load(f)

            editor = DraftEditor(content)
            
            # 应用各种调整
            success = True
            if "brightness" in adjustments:
                success = success and editor.adjust_brightness(segment_id, adjustments["brightness"])
            if "contrast" in adjustments:
                success = success and editor.adjust_contrast(segment_id, adjustments["contrast"])
            if "saturation" in adjustments:
                success = success and editor.adjust_saturation(segment_id, adjustments["saturation"])
            
            if success:
                self._save_draft_content(content_path, editor.get_content())
                logger.info(f"调整颜色成功: {draft_id} - {segment_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"调整颜色失败: {e}")
            raise BadRequestError(message=f"调整颜色失败: {str(e)}")
    
    async def add_sticker(
        self,
        db: AsyncSession,
        draft_id: int,
        sticker_path: str,
        start_time: float,
        duration: float,
        position: Optional[Dict[str, float]] = None,
        scale: float = 1.0
    ) -> bool:
        """
        添加贴纸/水印
        
        :param db: 数据库会话
        :param draft_id: 草稿 ID
        :param sticker_path: 贴纸文件路径
        :param start_time: 开始时间(秒)
        :param duration: 持续时长(秒)
        :param position: 位置 {"x": 0.9, "y": 0.1}
        :param scale: 缩放比例
        :return: 是否成功
        """
        draft = await crud_draft.get(db, draft_id)
        if not draft:
            raise NotFoundError()

        try:
            # 使用 effect_manager 添加贴纸
            if position is None:
                position = {"x": 0.5, "y": 0.5}
            
            success = effect_manager.add_sticker(
                draft.draft_path,
                sticker_path,
                start_time,
                duration,
                position.get("x", 0.5),
                position.get("y", 0.5),
                scale
            )
            
            if success:
                logger.info(f"添加贴纸成功: {draft_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"添加贴纸失败: {e}")
            raise BadRequestError(message=f"添加贴纸失败: {str(e)}")
    
    def _save_draft_content(self, content_path: str, content: Dict):
        """
        保存草稿内容并备份
        
        :param content_path: 草稿内容文件路径
        :param content: 草稿内容
        """
        import shutil
        # 备份
        shutil.copy(content_path, content_path + ".bak")
        # 保存
        with open(content_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)

editor_service = EditorService()

