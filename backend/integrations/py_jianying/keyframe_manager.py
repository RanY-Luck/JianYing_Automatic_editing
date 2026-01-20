"""
关键帧管理器 - 基于 PyJianying

NOTE: 此模块用于管理剪映草稿中的关键帧动画
支持位置、缩放、旋转、透明度等关键帧的添加和管理
"""
import json
import os
from typing import Dict, List, Optional, Any

from loguru import logger

from backend.core.conf import settings


class KeyframeProperty:
    """关键帧属性枚举"""
    POSITION_X = "position_x"
    POSITION_Y = "position_y"
    SCALE = "scale"
    ROTATION = "rotation"
    OPACITY = "opacity"
    VOLUME = "volume"


class EasingType:
    """缓动函数类型"""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    CUBIC_BEZIER = "cubic_bezier"


class KeyframeManager:
    """
    关键帧管理器
    
    NOTE: 用于管理剪映草稿中的关键帧动画
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
    
    def _find_segment(self, content: dict, track_id: str, segment_id: str) -> Optional[dict]:
        """
        查找片段
        
        :param content: 草稿内容
        :param track_id: 轨道 ID
        :param segment_id: 片段 ID
        :return: 片段对象
        """
        if 'tracks' not in content:
            return None
        
        for track in content['tracks']:
            if track.get('id') == track_id:
                for segment in track.get('segments', []):
                    if segment.get('id') == segment_id:
                        return segment
        
        return None
    
    def add_keyframe(
        self,
        draft_path: str,
        track_id: str,
        segment_id: str,
        time: float,
        property_name: str,
        value: float,
        easing: str = EasingType.LINEAR
    ) -> bool:
        """
        添加关键帧
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param segment_id: 片段 ID
        :param time: 关键帧时间(秒,相对于片段开始时间)
        :param property_name: 属性名称
        :param value: 属性值
        :param easing: 缓动函数类型
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
            
            # 确保 keyframes 字段存在
            if 'keyframes' not in segment:
                segment['keyframes'] = {}
            
            # 确保属性的关键帧数组存在
            if property_name not in segment['keyframes']:
                segment['keyframes'][property_name] = []
            
            # 添加关键帧
            keyframe = {
                "time": int(time * 1000000),  # 转换为微秒
                "value": value,
                "easing": easing
            }
            
            # 按时间顺序插入
            keyframes = segment['keyframes'][property_name]
            inserted = False
            for i, kf in enumerate(keyframes):
                if kf['time'] > keyframe['time']:
                    keyframes.insert(i, keyframe)
                    inserted = True
                    break
            
            if not inserted:
                keyframes.append(keyframe)
            
            if self._save_draft_content(draft_path, content):
                logger.info(f"添加关键帧成功: {property_name} at {time}s = {value}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"添加关键帧失败: {e}")
            return False
    
    def remove_keyframe(
        self,
        draft_path: str,
        track_id: str,
        segment_id: str,
        property_name: str,
        time: float
    ) -> bool:
        """
        删除关键帧
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param segment_id: 片段 ID
        :param property_name: 属性名称
        :param time: 关键帧时间(秒)
        :return: 是否成功
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content:
                return False
            
            segment = self._find_segment(content, track_id, segment_id)
            if not segment or 'keyframes' not in segment:
                return False
            
            if property_name not in segment['keyframes']:
                return False
            
            time_us = int(time * 1000000)
            keyframes = segment['keyframes'][property_name]
            original_count = len(keyframes)
            
            # 删除指定时间的关键帧
            segment['keyframes'][property_name] = [
                kf for kf in keyframes if kf['time'] != time_us
            ]
            
            if len(segment['keyframes'][property_name]) == original_count:
                logger.warning(f"关键帧不存在: {property_name} at {time}s")
                return False
            
            if self._save_draft_content(draft_path, content):
                logger.info(f"删除关键帧成功: {property_name} at {time}s")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"删除关键帧失败: {e}")
            return False
    
    def add_fade_in_animation(
        self,
        draft_path: str,
        track_id: str,
        segment_id: str,
        duration: float = 1.0
    ) -> bool:
        """
        添加淡入动画
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param segment_id: 片段 ID
        :param duration: 淡入时长(秒)
        :return: 是否成功
        """
        try:
            # 在开始时透明度为 0
            if not self.add_keyframe(draft_path, track_id, segment_id, 0.0, KeyframeProperty.OPACITY, 0.0, EasingType.EASE_OUT):
                return False
            
            # 在 duration 时透明度为 1
            if not self.add_keyframe(draft_path, track_id, segment_id, duration, KeyframeProperty.OPACITY, 1.0, EasingType.EASE_OUT):
                return False
            
            logger.info(f"添加淡入动画成功: duration={duration}s")
            return True
        
        except Exception as e:
            logger.error(f"添加淡入动画失败: {e}")
            return False
    
    def add_fade_out_animation(
        self,
        draft_path: str,
        track_id: str,
        segment_id: str,
        start_time: float,
        duration: float = 1.0
    ) -> bool:
        """
        添加淡出动画
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param segment_id: 片段 ID
        :param start_time: 淡出开始时间(秒,相对于片段开始)
        :param duration: 淡出时长(秒)
        :return: 是否成功
        """
        try:
            # 在 start_time 时透明度为 1
            if not self.add_keyframe(draft_path, track_id, segment_id, start_time, KeyframeProperty.OPACITY, 1.0, EasingType.EASE_IN):
                return False
            
            # 在 start_time + duration 时透明度为 0
            if not self.add_keyframe(draft_path, track_id, segment_id, start_time + duration, KeyframeProperty.OPACITY, 0.0, EasingType.EASE_IN):
                return False
            
            logger.info(f"添加淡出动画成功: start={start_time}s, duration={duration}s")
            return True
        
        except Exception as e:
            logger.error(f"添加淡出动画失败: {e}")
            return False
    
    def add_zoom_animation(
        self,
        draft_path: str,
        track_id: str,
        segment_id: str,
        start_time: float,
        duration: float,
        from_scale: float = 1.0,
        to_scale: float = 1.5
    ) -> bool:
        """
        添加缩放动画
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param segment_id: 片段 ID
        :param start_time: 动画开始时间(秒)
        :param duration: 动画时长(秒)
        :param from_scale: 起始缩放比例
        :param to_scale: 结束缩放比例
        :return: 是否成功
        """
        try:
            # 起始关键帧
            if not self.add_keyframe(draft_path, track_id, segment_id, start_time, KeyframeProperty.SCALE, from_scale, EasingType.EASE_IN_OUT):
                return False
            
            # 结束关键帧
            if not self.add_keyframe(draft_path, track_id, segment_id, start_time + duration, KeyframeProperty.SCALE, to_scale, EasingType.EASE_IN_OUT):
                return False
            
            logger.info(f"添加缩放动画成功: {from_scale} -> {to_scale}")
            return True
        
        except Exception as e:
            logger.error(f"添加缩放动画失败: {e}")
            return False
    
    def add_move_animation(
        self,
        draft_path: str,
        track_id: str,
        segment_id: str,
        start_time: float,
        duration: float,
        from_x: float,
        from_y: float,
        to_x: float,
        to_y: float
    ) -> bool:
        """
        添加移动动画
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param segment_id: 片段 ID
        :param start_time: 动画开始时间(秒)
        :param duration: 动画时长(秒)
        :param from_x: 起始 X 位置
        :param from_y: 起始 Y 位置
        :param to_x: 结束 X 位置
        :param to_y: 结束 Y 位置
        :return: 是否成功
        """
        try:
            # X 轴动画
            if not self.add_keyframe(draft_path, track_id, segment_id, start_time, KeyframeProperty.POSITION_X, from_x, EasingType.EASE_IN_OUT):
                return False
            if not self.add_keyframe(draft_path, track_id, segment_id, start_time + duration, KeyframeProperty.POSITION_X, to_x, EasingType.EASE_IN_OUT):
                return False
            
            # Y 轴动画
            if not self.add_keyframe(draft_path, track_id, segment_id, start_time, KeyframeProperty.POSITION_Y, from_y, EasingType.EASE_IN_OUT):
                return False
            if not self.add_keyframe(draft_path, track_id, segment_id, start_time + duration, KeyframeProperty.POSITION_Y, to_y, EasingType.EASE_IN_OUT):
                return False
            
            logger.info(f"添加移动动画成功: ({from_x}, {from_y}) -> ({to_x}, {to_y})")
            return True
        
        except Exception as e:
            logger.error(f"添加移动动画失败: {e}")
            return False
    
    def add_rotation_animation(
        self,
        draft_path: str,
        track_id: str,
        segment_id: str,
        start_time: float,
        duration: float,
        from_rotation: float = 0.0,
        to_rotation: float = 360.0
    ) -> bool:
        """
        添加旋转动画
        
        :param draft_path: 草稿路径
        :param track_id: 轨道 ID
        :param segment_id: 片段 ID
        :param start_time: 动画开始时间(秒)
        :param duration: 动画时长(秒)
        :param from_rotation: 起始旋转角度
        :param to_rotation: 结束旋转角度
        :return: 是否成功
        """
        try:
            # 起始关键帧
            if not self.add_keyframe(draft_path, track_id, segment_id, start_time, KeyframeProperty.ROTATION, from_rotation, EasingType.LINEAR):
                return False
            
            # 结束关键帧
            if not self.add_keyframe(draft_path, track_id, segment_id, start_time + duration, KeyframeProperty.ROTATION, to_rotation, EasingType.LINEAR):
                return False
            
            logger.info(f"添加旋转动画成功: {from_rotation}° -> {to_rotation}°")
            return True
        
        except Exception as e:
            logger.error(f"添加旋转动画失败: {e}")
            return False


# 单例实例
keyframe_manager = KeyframeManager()
