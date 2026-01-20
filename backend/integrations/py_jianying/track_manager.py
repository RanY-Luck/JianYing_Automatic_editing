"""
轨道管理器 - 基于 PyJianying

NOTE: 此模块用于管理剪映草稿中的轨道和片段
支持视频、音频、文本等轨道的添加、删除和修改操作
"""
import json
import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any

from loguru import logger

from backend.core.conf import settings


class TrackType:
    """轨道类型枚举"""
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    EFFECT = "effect"
    STICKER = "sticker"
    FILTER = "filter"


class TrackManager:
    """
    轨道管理器
    
    NOTE: 用于管理剪映草稿中的轨道和片段
    支持剪映 5.9 版本(未加密的 draft_content.json)
    """
    
    def __init__(self):
        self.storage_draft_path = settings.draft_path
    
    def _load_draft_content(self, draft_path: str) -> Optional[dict]:
        """
        加载草稿内容
        
        :param draft_path: 草稿路径
        :return: 草稿内容
        """
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
        """
        保存草稿内容
        
        :param draft_path: 草稿路径
        :param content: 草稿内容
        :return: 是否成功
        """
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
    
    def add_video_track(
        self,
        draft_path: str,
        material_id: str,
        material_path: str,
        start_time: float = 0.0,
        duration: Optional[float] = None,
        volume: float = 1.0,
        speed: float = 1.0
    ) -> Optional[str]:
        """
        添加视频轨道
        
        :param draft_path: 草稿路径
        :param material_id: 素材 ID
        :param material_path: 素材文件路径
        :param start_time: 开始时间(微秒)
        :param duration: 时长(微秒),None 表示使用素材原始时长
        :param volume: 音量 (0.0-1.0)
        :param speed: 速度 (0.1-10.0)
        :return: 轨道 ID
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content:
                return None
            
            # 确保 tracks 数组存在
            if 'tracks' not in content:
                content['tracks'] = []
            
            # 创建视频轨道
            track_id = self._generate_id()
            segment_id = self._generate_id()
            
            # NOTE: 剪映使用微秒作为时间单位
            track = {
                "id": track_id,
                "type": TrackType.VIDEO,
                "segments": [
                    {
                        "id": segment_id,
                        "material_id": material_id,
                        "target_timerange": {
                            "start": int(start_time * 1000000),  # 转换为微秒
                            "duration": int(duration * 1000000) if duration else None
                        },
                        "source_timerange": {
                            "start": 0,
                            "duration": int(duration * 1000000) if duration else None
                        },
                        "volume": volume,
                        "speed": speed,
                        "enable_adjust": True,
                        "enable_color_curves": True,
                        "enable_color_match_adjust": False,
                        "enable_color_wheels": True,
                        "enable_lut": False,
                        "enable_smart_color_adjust": False
                    }
                ]
            }
            
            # 添加到 tracks
            content['tracks'].append(track)
            
            # 保存草稿
            if self._save_draft_content(draft_path, content):
                logger.info(f"添加视频轨道成功: {track_id}")
                return track_id
            
            return None
        
        except Exception as e:
            logger.error(f"添加视频轨道失败: {e}")
            return None
    
    def add_audio_track(
        self,
        draft_path: str,
        material_id: str,
        material_path: str,
        start_time: float = 0.0,
        duration: Optional[float] = None,
        volume: float = 1.0,
        fade_in: float = 0.0,
        fade_out: float = 0.0
    ) -> Optional[str]:
        """
        添加音频轨道
        
        :param draft_path: 草稿路径
        :param material_id: 素材 ID
        :param material_path: 素材文件路径
        :param start_time: 开始时间(秒)
        :param duration: 时长(秒)
        :param volume: 音量 (0.0-1.0)
        :param fade_in: 淡入时长(秒)
        :param fade_out: 淡出时长(秒)
        :return: 轨道 ID
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content:
                return None
            
            if 'tracks' not in content:
                content['tracks'] = []
            
            track_id = self._generate_id()
            segment_id = self._generate_id()
            
            track = {
                "id": track_id,
                "type": TrackType.AUDIO,
                "segments": [
                    {
                        "id": segment_id,
                        "material_id": material_id,
                        "target_timerange": {
                            "start": int(start_time * 1000000),
                            "duration": int(duration * 1000000) if duration else None
                        },
                        "source_timerange": {
                            "start": 0,
                            "duration": int(duration * 1000000) if duration else None
                        },
                        "volume": volume,
                        "fade_in_duration": int(fade_in * 1000000),
                        "fade_out_duration": int(fade_out * 1000000)
                    }
                ]
            }
            
            content['tracks'].append(track)
            
            if self._save_draft_content(draft_path, content):
                logger.info(f"添加音频轨道成功: {track_id}")
                return track_id
            
            return None
        
        except Exception as e:
            logger.error(f"添加音频轨道失败: {e}")
            return None
    
    def add_text_track(
        self,
        draft_path: str,
        text_content: str,
        start_time: float = 0.0,
        duration: float = 3.0,
        font_size: int = 48,
        font_color: str = "#FFFFFF",
        position_x: float = 0.5,
        position_y: float = 0.5
    ) -> Optional[str]:
        """
        添加文本轨道
        
        :param draft_path: 草稿路径
        :param text_content: 文本内容
        :param start_time: 开始时间(秒)
        :param duration: 时长(秒)
        :param font_size: 字体大小
        :param font_color: 字体颜色 (十六进制)
        :param position_x: X 位置 (0.0-1.0, 相对于画布宽度)
        :param position_y: Y 位置 (0.0-1.0, 相对于画布高度)
        :return: 轨道 ID
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content:
                return None
            
            if 'tracks' not in content:
                content['tracks'] = []
            
            track_id = self._generate_id()
            segment_id = self._generate_id()
            
            track = {
                "id": track_id,
                "type": TrackType.TEXT,
                "segments": [
                    {
                        "id": segment_id,
                        "target_timerange": {
                            "start": int(start_time * 1000000),
                            "duration": int(duration * 1000000)
                        },
                        "content": text_content,
                        "style": {
                            "font_size": font_size,
                            "font_color": font_color,
                            "position": {
                                "x": position_x,
                                "y": position_y
                            },
                            "alignment": "center"
                        }
                    }
                ]
            }
            
            content['tracks'].append(track)
            
            if self._save_draft_content(draft_path, content):
                logger.info(f"添加文本轨道成功: {track_id}")
                return track_id
            
            return None
        
        except Exception as e:
            logger.error(f"添加文本轨道失败: {e}")
            return None
    
    def remove_track(self, draft_path: str, track_id: str) -> bool:
        """
        删除轨道
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :return: 是否成功
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content or 'tracks' not in content:
                return False
            
            # 查找并删除轨道
            original_count = len(content['tracks'])
            content['tracks'] = [t for t in content['tracks'] if t.get('id') != track_id]
            
            if len(content['tracks']) == original_count:
                logger.warning(f"轨道不存在: {track_id}")
                return False
            
            if self._save_draft_content(draft_path, content):
                logger.info(f"删除轨道成功: {track_id}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"删除轨道失败: {e}")
            return False
    
    def get_tracks(self, draft_path: str, track_type: Optional[str] = None) -> List[dict]:
        """
        获取轨道列表
        
        :param draft_path: 草稿路径
        :param track_type: 轨道类型过滤
        :return: 轨道列表
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content or 'tracks' not in content:
                return []
            
            tracks = content['tracks']
            
            if track_type:
                tracks = [t for t in tracks if t.get('type') == track_type]
            
            return tracks
        
        except Exception as e:
            logger.error(f"获取轨道列表失败: {e}")
            return []
    
    def update_track_volume(self, draft_path: str, track_id: str, volume: float) -> bool:
        """
        更新轨道音量
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param volume: 音量 (0.0-1.0)
        :return: 是否成功
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content or 'tracks' not in content:
                return False
            
            # 查找轨道
            for track in content['tracks']:
                if track.get('id') == track_id:
                    # 更新所有片段的音量
                    for segment in track.get('segments', []):
                        segment['volume'] = volume
                    
                    if self._save_draft_content(draft_path, content):
                        logger.info(f"更新轨道音量成功: {track_id}, volume={volume}")
                        return True
                    break
            
            return False
        
        except Exception as e:
            logger.error(f"更新轨道音量失败: {e}")
            return False
    
    def update_track_speed(self, draft_path: str, track_id: str, speed: float) -> bool:
        """
        更新轨道速度
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param speed: 速度 (0.1-10.0)
        :return: 是否成功
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content or 'tracks' not in content:
                return False
            
            for track in content['tracks']:
                if track.get('id') == track_id:
                    for segment in track.get('segments', []):
                        segment['speed'] = speed
                        # NOTE: 速度改变会影响时长
                        if 'target_timerange' in segment and 'duration' in segment['target_timerange']:
                            original_duration = segment['target_timerange']['duration']
                            segment['target_timerange']['duration'] = int(original_duration / speed)
                    
                    if self._save_draft_content(draft_path, content):
                        logger.info(f"更新轨道速度成功: {track_id}, speed={speed}")
                        return True
                    break
            
            return False
        
        except Exception as e:
            logger.error(f"更新轨道速度失败: {e}")
            return False


# 单例实例
track_manager = TrackManager()
