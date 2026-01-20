"""
剪映草稿编辑器 - 提供高级编辑功能
"""
import uuid
import random
import copy
from typing import Dict, List, Optional, Union, Tuple
from loguru import logger

class DraftEditor:
    """
    剪映草稿编辑器
    用于对草稿内容(draft_content.json)进行高级编辑
    """

    def __init__(self, content: Dict):
        """
        初始化编辑器
        :param content: 草稿内容的字典对象 (draft_content.json)
        """
        self.content = content
        self.tracks = self.content.get("tracks", [])
        self.materials = self.content.get("materials", {})
        
        # 确保 materials 结构存在
        topic_types = ["videos", "audios", "stickers", "effects", "transitions", "filters"]
        for topic in topic_types:
            if topic not in self.materials:
                self.materials[topic] = []

    def get_content(self) -> Dict:
        """获取编辑后的内容"""
        return self.content

    def _generate_id(self) -> str:
        """生成唯一 ID"""
        return str(uuid.uuid4()).upper()

    def _get_track_max_duration(self) -> int:
        """获取所有轨道的最大时长 (微秒)"""
        max_duration = 0
        for track in self.tracks:
            track_duration = 0
            for segment in track.get("segments", []):
                # 累加时长 (注意：Segments 可能是重叠的或者有空隙，这里简单处理为最后一个 Segment 的结束时间)
                # 更准确的计算应该是 max(target_timerange.start + target_timerange.duration)
                target_timerange = segment.get("target_timerange", {})
                start = target_timerange.get("start", 0)
                duration = target_timerange.get("duration", 0)
                end = start + duration
                if end > track_duration:
                    track_duration = end
            if track_duration > max_duration:
                max_duration = track_duration
        return max_duration

    def add_audio(self, file_path: str, start_time: int = 0, duration: int = -1, volume: float = 1.0) -> bool:
        """
        添加背景音乐
        :param file_path: 音频文件绝对路径
        :param start_time: 插入起始时间 (微秒)
        :param duration: 持续时长 (微秒)，-1 表示使用音频全长或对齐视频长度
        :param volume: 音量 (0.0 - 1.0)
        :return: 是否成功
        """
        try:
            audio_id = self._generate_id()
            
            # 1. 添加到 materials.audios
            audio_material = {
                "app_id": 0,
                "category_id": "",
                "category_name": "local",
                "check_flag": 1,
                "content": {
                    "check_flag": 1,
                    "keyword": "",
                    "level": 0,
                    "phrase": "",
                    "query": "",
                    "tag": ""
                },
                "cropper": {
                    "lower_left_x": 0.0,
                    "lower_left_y": 1.0,
                    "lower_right_x": 1.0,
                    "lower_right_y": 1.0,
                    "upper_left_x": 0.0,
                    "upper_left_y": 0.0,
                    "upper_right_x": 1.0,
                    "upper_right_y": 0.0
                },
                "duration": 10000000, # 默认 10s，后面应该读取真实文件时长，这里简化
                "effect_id": audio_id,
                "extra_info": "",
                "formula_id": "",
                "id": audio_id,
                "intensifies_path": "",
                "local_material_id": audio_id,
                "music_id": audio_id,
                "name": "Background Music",
                "path": file_path,
                "resource_id": "",
                "source_platform": 0,
                "team_id": "",
                "text_id": "",
                "tone_category_id": "",
                "tone_category_name": "",
                "tone_effect_id": "",
                "tone_effect_name": "",
                "tone_maker": "",
                "tone_maker_id": "",
                "tone_type": "",
                "type": "audio",
                "update_time": 0,
                "version": 0
            }
            self.materials["audios"].append(audio_material)

            # 2. 计算时长
            # 如果 duration 为 -1，则尝试对齐视频最大时长
            if duration == -1:
                duration = self._get_track_max_duration()
                if duration == 0:
                    duration = 10000000 # 默认 10s

            # 3. 添加到 tracks
            # 查找现有的音频轨道，或者新建
            target_track = None
            for track in self.tracks:
                if track.get("type") == "audio":
                    target_track = track
                    break
            
            if not target_track:
                target_track = {
                    "attribute": 0,
                    "flag": 0,
                    "id": self._generate_id(),
                    "segments": [],
                    "type": "audio"
                }
                self.tracks.append(target_track)

            segment_id = self._generate_id()
            segment = {
                "carton": False,
                "clip": {
                    "alpha": 1.0,
                    "flip": {"horizontal": False, "vertical": False},
                    "rotation": 0.0,
                    "scale": {"x": 1.0, "y": 1.0},
                    "transform": {"x": 0.0, "y": 0.0}
                },
                "common_attribute": {"size": 0},
                "enable_adjust": False,
                "enable_color_curves": True,
                "enable_color_wheels": True,
                "enable_lut": True,
                "enable_smart_color_adjust": False,
                "extra_material_refs": [audio_id],
                "group_id": "",
                "hdr_settings": {"intensity": 1.0, "mode": 1, "nits": 1000},
                "id": segment_id,
                "intensifies_audio_path": "",
                "is_placeholder": False,
                "is_tone_modify": False,
                "keyframe_refs": [],
                "material_id": audio_id,
                "render_index": 0,
                "reverse": False,
                "source_timerange": {"duration": duration, "start": 0},
                "speed": 1.0,
                "target_timerange": {"duration": duration, "start": start_time},
                "template_id": "",
                "template_scene": "default",
                "track_attribute": 0,
                "track_render_index": 0,
                "visible": True,
                "volume": volume
            }
            
            target_track["segments"].append(segment)
            logger.info(f"已添加背景音乐: {file_path}")
            return True

        except Exception as e:
            logger.error(f"添加背景音乐失败: {e}")
            return False

    def deduplicate(self, config: Dict = None) -> bool:
        """
        智能去重
        :param config: 配置字典，支持 speed, mirror, crop, filter
        :return: 是否成功
        """
        if config is None:
            config = {
                "speed": True, 
                "mirror": True, 
                "crop": True, 
                "filter": True
            }
            
        try:
            # 遍历所有视频轨道的主视频片段
            for track in self.tracks:
                if track.get("type") == "video":
                    for segment in track.get("segments", []):
                        if config.get("speed"):
                            self._apply_speed(segment)
                        if config.get("mirror"):
                            self._apply_mirror(segment)
                        if config.get("crop"):
                            self._apply_crop(segment)
            
            if config.get("filter"):
                self._apply_random_filter()
                
            logger.info("去重处理完成")
            return True
            
        except Exception as e:
            logger.error(f"去重处理失败: {e}")
            return False

    def _apply_speed(self, segment: Dict):
        """应用微变变速"""
        # 随机 0.95 - 1.05 之间
        speed_factor = 1.0 + (random.random() * 0.1 - 0.05)
        segment["speed"] = speed_factor
        # 注意：变速后需要调整 target_timerange 的 duration
        # duration / speed = new_duration (视觉时长变了)
        # 但在剪映 JSON 中，target_timerange.duration 通常是显示的长度
        # 如果 speed 变了，source_timerange 不变，target_timerange 应该变化
        # 这里简化处理，暂只修改 speed 参数
        
    def _apply_mirror(self, segment: Dict):
        """应用随机镜像"""
        if random.random() > 0.5:
            # 查找或创建 clip 属性
            if "clip" not in segment:
                segment["clip"] = {}
            if "flip" not in segment["clip"]:
                segment["clip"]["flip"] = {"horizontal": False, "vertical": False}
            
            segment["clip"]["flip"]["horizontal"] = True

    def _apply_crop(self, segment: Dict):
        """应用随机轻微裁剪 (Zoom in)"""
        # scale 1.02 - 1.05
        scale_factor = 1.02 + random.random() * 0.03
        if "clip" not in segment:
            segment["clip"] = {}
        if "scale" not in segment["clip"]:
            segment["clip"]["scale"] = {"x": 1.0, "y": 1.0}
            
        # 保持原有 scale 比例
        segment["clip"]["scale"]["x"] *= scale_factor
        segment["clip"]["scale"]["y"] *= scale_factor

    def _apply_random_filter(self):
        """添加随机滤镜"""
        from .filter_library import FilterLibrary
        
        # 获取随机滤镜
        filter_name = FilterLibrary.get_random_filter()
        if not filter_name:
            return
        
        filter_id = FilterLibrary.get_filter_id(filter_name)
        if not filter_id:
            return
        
        # 遍历所有视频轨道的片段
        for track in self.tracks:
            if track.get("type") == "video":
                for segment in track.get("segments", []):
                    # 添加滤镜到片段
                    if "extra_material_refs" not in segment:
                        segment["extra_material_refs"] = []
                    
                    # 添加滤镜引用
                    segment["extra_material_refs"].append(filter_id)
                    
                    # 添加滤镜到 materials.filters (如果需要)
                    if "filters" not in self.materials:
                        self.materials["filters"] = []
                    
                    # 检查滤镜是否已存在
                    filter_exists = any(f.get("id") == filter_id for f in self.materials["filters"])
                    if not filter_exists:
                        filter_material = {
                            "id": filter_id,
                            "name": filter_name,
                            "type": "filter",
                            "intensity": 0.5 + random.random() * 0.5,  # 0.5-1.0 随机强度
                        }
                        self.materials["filters"].append(filter_material)
    
    def add_filter(self, filter_name: str, intensity: float = 1.0, segment_id: Optional[str] = None) -> bool:
        """
        添加滤镜到指定片段或所有视频片段
        
        :param filter_name: 滤镜名称
        :param intensity: 滤镜强度 (0.0-1.0)
        :param segment_id: 片段 ID,为 None 则应用到所有视频片段
        :return: 是否成功
        """
        from .filter_library import FilterLibrary
        
        try:
            filter_id = FilterLibrary.get_filter_id(filter_name)
            if not filter_id:
                logger.error(f"未找到滤镜: {filter_name}")
                return False
            
            # 添加滤镜到 materials
            if "filters" not in self.materials:
                self.materials["filters"] = []
            
            filter_exists = any(f.get("id") == filter_id for f in self.materials["filters"])
            if not filter_exists:
                filter_material = {
                    "id": filter_id,
                    "name": filter_name,
                    "type": "filter",
                    "intensity": max(0.0, min(1.0, intensity)),
                }
                self.materials["filters"].append(filter_material)
            
            # 应用到片段
            applied = False
            for track in self.tracks:
                if track.get("type") == "video":
                    for segment in track.get("segments", []):
                        # 如果指定了 segment_id,只应用到该片段
                        if segment_id and segment.get("id") != segment_id:
                            continue
                        
                        if "extra_material_refs" not in segment:
                            segment["extra_material_refs"] = []
                        
                        # 避免重复添加
                        if filter_id not in segment["extra_material_refs"]:
                            segment["extra_material_refs"].append(filter_id)
                            applied = True
            
            if applied:
                logger.info(f"已添加滤镜: {filter_name}")
                return True
            else:
                logger.warning(f"未找到可应用滤镜的片段")
                return False
                
        except Exception as e:
            logger.error(f"添加滤镜失败: {e}")
            return False
    
    def add_transition(self, transition_name: str, duration: float = 0.5, 
                      from_segment_id: Optional[str] = None, 
                      to_segment_id: Optional[str] = None) -> bool:
        """
        在两个片段之间添加转场效果
        
        :param transition_name: 转场名称
        :param duration: 转场时长(秒)
        :param from_segment_id: 起始片段 ID
        :param to_segment_id: 结束片段 ID
        :return: 是否成功
        """
        from .transition_library import TransitionLibrary
        
        try:
            transition_id = TransitionLibrary.get_transition_id(transition_name)
            if not transition_id:
                logger.error(f"未找到转场: {transition_name}")
                return False
            
            # 转换秒为微秒
            duration_us = int(duration * 1000000)
            
            # 添加转场到 materials
            if "transitions" not in self.materials:
                self.materials["transitions"] = []
            
            transition_material = {
                "id": transition_id,
                "name": transition_name,
                "type": "transition",
                "duration": duration_us,
            }
            self.materials["transitions"].append(transition_material)
            
            # 查找视频轨道
            for track in self.tracks:
                if track.get("type") == "video":
                    segments = track.get("segments", [])
                    
                    # 如果没有指定片段,自动在相邻片段间添加转场
                    if not from_segment_id and not to_segment_id:
                        for i in range(len(segments) - 1):
                            self._add_transition_between_segments(
                                segments[i], segments[i + 1], transition_id, duration_us
                            )
                    else:
                        # 查找指定的片段
                        from_seg = None
                        to_seg = None
                        for seg in segments:
                            if seg.get("id") == from_segment_id:
                                from_seg = seg
                            if seg.get("id") == to_segment_id:
                                to_seg = seg
                        
                        if from_seg and to_seg:
                            self._add_transition_between_segments(
                                from_seg, to_seg, transition_id, duration_us
                            )
            
            logger.info(f"已添加转场: {transition_name}")
            return True
            
        except Exception as e:
            logger.error(f"添加转场失败: {e}")
            return False
    
    def _add_transition_between_segments(self, from_segment: Dict, to_segment: Dict, 
                                        transition_id: str, duration_us: int):
        """在两个片段之间添加转场"""
        # 在 to_segment 上添加转场引用
        if "transition" not in to_segment:
            to_segment["transition"] = {
                "id": transition_id,
                "duration": duration_us,
            }
    
    def split_segment(self, segment_id: str, split_time: float) -> bool:
        """
        在指定时间点分割片段
        
        :param segment_id: 片段 ID
        :param split_time: 分割时间点(秒,相对于片段开始时间)
        :return: 是否成功
        """
        try:
            split_time_us = int(split_time * 1000000)
            
            for track in self.tracks:
                for i, segment in enumerate(track.get("segments", [])):
                    if segment.get("id") == segment_id:
                        # 获取原片段的时间范围
                        source_range = segment.get("source_timerange", {})
                        target_range = segment.get("target_timerange", {})
                        
                        source_start = source_range.get("start", 0)
                        source_duration = source_range.get("duration", 0)
                        target_start = target_range.get("start", 0)
                        target_duration = target_range.get("duration", 0)
                        
                        # 检查分割点是否有效
                        if split_time_us <= 0 or split_time_us >= target_duration:
                            logger.error(f"分割时间点无效: {split_time}秒")
                            return False
                        
                        # 创建第二个片段
                        new_segment = copy.deepcopy(segment)
                        new_segment["id"] = self._generate_id()
                        
                        # 调整第一个片段的时间范围
                        segment["source_timerange"]["duration"] = split_time_us
                        segment["target_timerange"]["duration"] = split_time_us
                        
                        # 调整第二个片段的时间范围
                        new_segment["source_timerange"]["start"] = source_start + split_time_us
                        new_segment["source_timerange"]["duration"] = source_duration - split_time_us
                        new_segment["target_timerange"]["start"] = target_start + split_time_us
                        new_segment["target_timerange"]["duration"] = target_duration - split_time_us
                        
                        # 插入新片段
                        track["segments"].insert(i + 1, new_segment)
                        
                        logger.info(f"已分割片段: {segment_id} 在 {split_time}秒")
                        return True
            
            logger.error(f"未找到片段: {segment_id}")
            return False
            
        except Exception as e:
            logger.error(f"分割片段失败: {e}")
            return False
    
    def trim_segment(self, segment_id: str, start_time: float, end_time: float) -> bool:
        """
        裁剪片段时间范围
        
        :param segment_id: 片段 ID
        :param start_time: 起始时间(秒,相对于片段开始)
        :param end_time: 结束时间(秒,相对于片段开始)
        :return: 是否成功
        """
        try:
            start_time_us = int(start_time * 1000000)
            end_time_us = int(end_time * 1000000)
            
            for track in self.tracks:
                for segment in track.get("segments", []):
                    if segment.get("id") == segment_id:
                        source_range = segment.get("source_timerange", {})
                        target_range = segment.get("target_timerange", {})
                        
                        source_start = source_range.get("start", 0)
                        target_start = target_range.get("start", 0)
                        
                        new_duration = end_time_us - start_time_us
                        if new_duration <= 0:
                            logger.error(f"裁剪时间范围无效")
                            return False
                        
                        # 更新时间范围
                        segment["source_timerange"]["start"] = source_start + start_time_us
                        segment["source_timerange"]["duration"] = new_duration
                        segment["target_timerange"]["duration"] = new_duration
                        
                        logger.info(f"已裁剪片段: {segment_id}")
                        return True
            
            logger.error(f"未找到片段: {segment_id}")
            return False
            
        except Exception as e:
            logger.error(f"裁剪片段失败: {e}")
            return False
    
    def adjust_brightness(self, segment_id: str, value: float) -> bool:
        """
        调整片段亮度
        
        :param segment_id: 片段 ID
        :param value: 亮度值 (-1.0 到 1.0, 0 为原始亮度)
        :return: 是否成功
        """
        return self._adjust_color_property(segment_id, "brightness", value)
    
    def adjust_contrast(self, segment_id: str, value: float) -> bool:
        """
        调整片段对比度
        
        :param segment_id: 片段 ID
        :param value: 对比度值 (-1.0 到 1.0, 0 为原始对比度)
        :return: 是否成功
        """
        return self._adjust_color_property(segment_id, "contrast", value)
    
    def adjust_saturation(self, segment_id: str, value: float) -> bool:
        """
        调整片段饱和度
        
        :param segment_id: 片段 ID
        :param value: 饱和度值 (-1.0 到 1.0, 0 为原始饱和度)
        :return: 是否成功
        """
        return self._adjust_color_property(segment_id, "saturation", value)
    
    def _adjust_color_property(self, segment_id: str, property_name: str, value: float) -> bool:
        """
        调整颜色属性
        
        :param segment_id: 片段 ID
        :param property_name: 属性名称
        :param value: 属性值
        :return: 是否成功
        """
        try:
            value = max(-1.0, min(1.0, value))
            
            for track in self.tracks:
                for segment in track.get("segments", []):
                    if segment.get("id") == segment_id:
                        # 创建或更新颜色调整属性
                        if "color_adjust" not in segment:
                            segment["color_adjust"] = {}
                        
                        segment["color_adjust"][property_name] = value
                        segment["enable_adjust"] = True
                        
                        logger.info(f"已调整{property_name}: {segment_id} = {value}")
                        return True
            
            logger.error(f"未找到片段: {segment_id}")
            return False
            
        except Exception as e:
            logger.error(f"调整{property_name}失败: {e}")
            return False
    
    def add_text(self, text: str, start_time: float, duration: float, 
                font_size: int = 48, font_color: str = "#FFFFFF",
                position_x: float = 0.5, position_y: float = 0.9) -> bool:
        """
        添加文本/字幕
        
        :param text: 文本内容
        :param start_time: 开始时间(秒)
        :param duration: 持续时长(秒)
        :param font_size: 字体大小
        :param font_color: 字体颜色
        :param position_x: X 位置 (0.0-1.0)
        :param position_y: Y 位置 (0.0-1.0)
        :return: 是否成功
        """
        try:
            text_id = self._generate_id()
            start_time_us = int(start_time * 1000000)
            duration_us = int(duration * 1000000)
            
            # 添加到 materials.texts
            if "texts" not in self.materials:
                self.materials["texts"] = []
            
            text_material = {
                "id": text_id,
                "type": "text",
                "content": text,
                "font_size": font_size,
                "font_color": font_color,
            }
            self.materials["texts"].append(text_material)
            
            # 查找或创建文本轨道
            text_track = None
            for track in self.tracks:
                if track.get("type") == "text":
                    text_track = track
                    break
            
            if not text_track:
                text_track = {
                    "attribute": 0,
                    "flag": 0,
                    "id": self._generate_id(),
                    "segments": [],
                    "type": "text"
                }
                self.tracks.append(text_track)
            
            # 创建文本片段
            segment_id = self._generate_id()
            segment = {
                "id": segment_id,
                "material_id": text_id,
                "target_timerange": {
                    "start": start_time_us,
                    "duration": duration_us
                },
                "source_timerange": {
                    "start": 0,
                    "duration": duration_us
                },
                "clip": {
                    "alpha": 1.0,
                    "transform": {
                        "x": position_x,
                        "y": position_y
                    },
                    "scale": {"x": 1.0, "y": 1.0}
                },
                "visible": True,
            }
            
            text_track["segments"].append(segment)
            logger.info(f"已添加文本: {text}")
            return True
            
        except Exception as e:
            logger.error(f"添加文本失败: {e}")
            return False
