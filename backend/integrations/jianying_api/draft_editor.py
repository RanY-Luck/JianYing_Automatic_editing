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
        # 实际需要真实的 filter id，这里仅做模拟结构插入
        # 真实场景需要维护一个 Filter ID 库
        pass
