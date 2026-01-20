"""
编辑器服务层 - 衔接 API 与 DraftEditor
"""
import os
import json
from typing import Dict, Any
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.draft.crud.crud_draft import crud_draft
from backend.common.exception import NotFoundError, BadRequestError
from backend.integrations.jianying_api.draft_editor import DraftEditor

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

editor_service = EditorService()
