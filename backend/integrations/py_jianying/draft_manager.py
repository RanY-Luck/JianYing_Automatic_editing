"""
草稿管理器 - 基于 PyJianying
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional

from loguru import logger

from backend.core.conf import settings


class DraftManager:
    """
    草稿管理器
    
    NOTE: 剪映 6.0.1 版本的 draft_content.json 已加密
    此管理器主要用于读取草稿元数据和管理草稿文件夹
    """
    
    def __init__(self):
        self.draft_root = settings.jianying_draft_path
        self.storage_draft_path = settings.draft_path
    
    def list_drafts(self) -> list[dict]:
        """
        列出剪映草稿箱中的所有草稿
        
        :return: 草稿列表
        """
        drafts = []
        
        if not os.path.exists(self.draft_root):
            logger.warning(f"剪映草稿箱路径不存在: {self.draft_root}")
            return drafts
        
        try:
            for draft_folder in os.listdir(self.draft_root):
                draft_path = os.path.join(self.draft_root, draft_folder)
                
                if not os.path.isdir(draft_path):
                    continue
                
                # 读取草稿信息
                draft_info = self._read_draft_info(draft_path)
                if draft_info:
                    drafts.append(draft_info)
        
        except Exception as e:
            logger.error(f"列出草稿失败: {e}")
        
        return drafts
    
    def _read_draft_info(self, draft_path: str) -> Optional[dict]:
        """
        读取草稿信息
        
        :param draft_path: 草稿路径
        :return: 草稿信息
        """
        try:
            # 读取 draft_info.json（未加密）
            info_file = os.path.join(draft_path, "draft_info.json")
            if not os.path.exists(info_file):
                return None
            
            with open(info_file, 'r', encoding='utf-8') as f:
                info_data = json.load(f)
            
            # NOTE: draft_content.json 在 6.0.1 版本中已加密，无法直接读取
            # 我们只能获取基本信息
            draft_id = os.path.basename(draft_path)
            
            return {
                'draft_id': draft_id,
                'draft_path': draft_path,
                'draft_name': info_data.get('draft_name', draft_id),
                'create_time': info_data.get('tm_draft_create', 0),
                'update_time': info_data.get('tm_draft_modified', 0),
                'duration': info_data.get('duration', 0),
                'is_encrypted': True,  # 6.0.1 版本草稿已加密
            }
        
        except Exception as e:
            logger.error(f"读取草稿信息失败 {draft_path}: {e}")
            return None
    
    def get_draft_info(self, draft_id: str) -> Optional[dict]:
        """
        获取指定草稿的信息
        
        :param draft_id: 草稿 ID
        :return: 草稿信息
        """
        draft_path = os.path.join(self.draft_root, draft_id)
        if not os.path.exists(draft_path):
            logger.warning(f"草稿不存在: {draft_id}")
            return None
        
        return self._read_draft_info(draft_path)
    
    def create_draft_folder(self, draft_name: str) -> str:
        """
        在存储目录创建草稿文件夹
        
        :param draft_name: 草稿名称
        :return: 草稿路径
        """
        # 生成唯一的草稿 ID
        import uuid
        draft_id = str(uuid.uuid4())
        
        draft_path = os.path.join(self.storage_draft_path, draft_id)
        os.makedirs(draft_path, exist_ok=True)
        
        logger.info(f"创建草稿文件夹: {draft_path}")
        return draft_path
    
    def copy_draft_to_storage(self, draft_id: str, target_name: str) -> Optional[str]:
        """
        将剪映草稿箱中的草稿复制到存储目录
        
        :param draft_id: 剪映草稿 ID
        :param target_name: 目标草稿名称
        :return: 目标草稿路径
        """
        import shutil
        
        source_path = os.path.join(self.draft_root, draft_id)
        if not os.path.exists(source_path):
            logger.error(f"源草稿不存在: {draft_id}")
            return None
        
        target_path = os.path.join(self.storage_draft_path, target_name)
        
        try:
            shutil.copytree(source_path, target_path, dirs_exist_ok=True)
            logger.info(f"复制草稿成功: {source_path} -> {target_path}")
            return target_path
        
        except Exception as e:
            logger.error(f"复制草稿失败: {e}")
            return None
    
    def delete_draft_folder(self, draft_path: str) -> bool:
        """
        删除草稿文件夹
        
        :param draft_path: 草稿路径
        :return: 是否成功
        """
        import shutil
        
        try:
            if os.path.exists(draft_path):
                shutil.rmtree(draft_path)
                logger.info(f"删除草稿文件夹: {draft_path}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"删除草稿文件夹失败: {e}")
            return False


# 单例实例
draft_manager = DraftManager()
