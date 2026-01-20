"""
特效管理器 - 基于 PyJianying

NOTE: 此模块用于管理剪映草稿中的特效、滤镜、转场等
支持常用特效的添加和管理
"""
import json
import os
import uuid
from typing import Dict, List, Optional, Any

from loguru import logger

from backend.core.conf import settings


class FilterType:
    """滤镜类型"""
    BLACK_WHITE = "black_white"
    VINTAGE = "vintage"
    FILM = "film"
    WARM = "warm"
    COOL = "cool"
    VIVID = "vivid"
    SOFT = "soft"


class TransitionType:
    """转场类型"""
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    SLIDE = "slide"
    ZOOM = "zoom"
    ROTATE = "rotate"


class EffectManager:
    """
    特效管理器
    
    NOTE: 用于管理剪映草稿中的特效、滤镜、转场等
    支持剪映 5.9 版本(未加密的 draft_content.json)
    """
    
    def __init__(self):
        self.storage_draft_path = settings.draft_path
    
    def _load_draft_content(self, draft_path: str) -> Optional[dict]:
        """加载草稿内容"""
        try:
            content_file = os.path.join(draft_path, "draft_content.json")
            if not os.path.exists(content_file):
                logger.error(f"草稿内容文件不存在: {content_file}")
                return None
            
            with open(content_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            return content
        
        except Exception as e:
            logger.error(f"加载草稿内容失败: {e}")
            return None
    
    def _save_draft_content(self, draft_path: str, content: dict) -> bool:
        """保存草稿内容"""
        try:
            content_file = os.path.join(draft_path, "draft_content.json")
            
            # 备份原文件
            if os.path.exists(content_file):
                backup_file = content_file + ".backup"
                import shutil
                shutil.copy2(content_file, backup_file)
            
            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存草稿内容成功: {content_file}")
            return True
        
        except Exception as e:
            logger.error(f"保存草稿内容失败: {e}")
            return False
    
    def _generate_id(self) -> str:
        """生成唯一 ID"""
        return str(uuid.uuid4()).replace('-', '')
    
    def _find_segment(self, content: dict, track_id: str, segment_id: str) -> Optional[dict]:
        """查找片段"""
        if 'tracks' not in content:
            return None
        
        for track in content['tracks']:
            if track.get('id') == track_id:
                for segment in track.get('segments', []):
                    if segment.get('id') == segment_id:
                        return segment
        
        return None
    
    def add_filter(
        self,
        draft_path: str,
        track_id: str,
        segment_id: str,
        filter_type: str,
        intensity: float = 1.0
    ) -> bool:
        """
        添加滤镜
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param segment_id: 片段 ID
        :param filter_type: 滤镜类型
        :param intensity: 强度 (0.0-1.0)
        :return: 是否成功
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content:
                return False
            
            segment = self._find_segment(content, track_id, segment_id)
            if not segment:
                logger.error(f"片段不存在: track_id={track_id}, segment_id={segment_id}")
                return False
            
            # 添加滤镜
            if 'effects' not in segment:
                segment['effects'] = []
            
            filter_effect = {
                "id": self._generate_id(),
                "type": "filter",
                "filter_type": filter_type,
                "intensity": intensity
            }
            
            segment['effects'].append(filter_effect)
            
            if self._save_draft_content(draft_path, content):
                logger.info(f"添加滤镜成功: {filter_type}, intensity={intensity}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"添加滤镜失败: {e}")
            return False
    
    def add_transition(
        self,
        draft_path: str,
        track_id: str,
        segment_id: str,
        transition_type: str,
        duration: float = 0.5
    ) -> bool:
        """
        添加转场
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param segment_id: 片段 ID
        :param transition_type: 转场类型
        :param duration: 转场时长(秒)
        :return: 是否成功
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content:
                return False
            
            segment = self._find_segment(content, track_id, segment_id)
            if not segment:
                logger.error(f"片段不存在: track_id={track_id}, segment_id={segment_id}")
                return False
            
            # 添加转场
            transition = {
                "id": self._generate_id(),
                "type": transition_type,
                "duration": int(duration * 1000000)  # 转换为微秒
            }
            
            segment['transition'] = transition
            
            if self._save_draft_content(draft_path, content):
                logger.info(f"添加转场成功: {transition_type}, duration={duration}s")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"添加转场失败: {e}")
            return False
    
    def add_sticker(
        self,
        draft_path: str,
        sticker_path: str,
        start_time: float,
        duration: float,
        position_x: float = 0.5,
        position_y: float = 0.5,
        scale: float = 1.0
    ) -> Optional[str]:
        """
        添加贴纸
        
        :param draft_path: 草稿路径
        :param sticker_path: 贴纸文件路径
        :param start_time: 开始时间(秒)
        :param duration: 时长(秒)
        :param position_x: X 位置 (0.0-1.0)
        :param position_y: Y 位置 (0.0-1.0)
        :param scale: 缩放比例
        :return: 贴纸轨道 ID
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content:
                return None
            
            if 'tracks' not in content:
                content['tracks'] = []
            
            track_id = self._generate_id()
            segment_id = self._generate_id()
            
            # 创建贴纸轨道
            track = {
                "id": track_id,
                "type": "sticker",
                "segments": [
                    {
                        "id": segment_id,
                        "sticker_path": sticker_path,
                        "target_timerange": {
                            "start": int(start_time * 1000000),
                            "duration": int(duration * 1000000)
                        },
                        "position": {
                            "x": position_x,
                            "y": position_y
                        },
                        "scale": scale
                    }
                ]
            }
            
            content['tracks'].append(track)
            
            if self._save_draft_content(draft_path, content):
                logger.info(f"添加贴纸成功: {sticker_path}")
                return track_id
            
            return None
        
        except Exception as e:
            logger.error(f"添加贴纸失败: {e}")
            return None
    
    def remove_filter(
        self,
        draft_path: str,
        track_id: str,
        segment_id: str,
        filter_id: str
    ) -> bool:
        """
        删除滤镜
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param segment_id: 片段 ID
        :param filter_id: 滤镜 ID
        :return: 是否成功
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content:
                return False
            
            segment = self._find_segment(content, track_id, segment_id)
            if not segment or 'effects' not in segment:
                return False
            
            original_count = len(segment['effects'])
            segment['effects'] = [e for e in segment['effects'] if e.get('id') != filter_id]
            
            if len(segment['effects']) == original_count:
                logger.warning(f"滤镜不存在: {filter_id}")
                return False
            
            if self._save_draft_content(draft_path, content):
                logger.info(f"删除滤镜成功: {filter_id}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"删除滤镜失败: {e}")
            return False
    
    def remove_transition(
        self,
        draft_path: str,
        track_id: str,
        segment_id: str
    ) -> bool:
        """
        删除转场
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param segment_id: 片段 ID
        :return: 是否成功
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content:
                return False
            
            segment = self._find_segment(content, track_id, segment_id)
            if not segment or 'transition' not in segment:
                return False
            
            del segment['transition']
            
            if self._save_draft_content(draft_path, content):
                logger.info(f"删除转场成功")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"删除转场失败: {e}")
            return False


# 单例实例
effect_manager = EffectManager()
