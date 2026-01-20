"""
智能剪辑算法模块

包含:
1. 静音片段检测与删除
2. 智能高光片段识别
3. 音频分析工具
"""

import os
import json
from typing import List, Dict, Tuple, Optional
from loguru import logger


class AudioAnalyzer:
    """音频分析器"""
    
    @staticmethod
    def detect_silence(
        audio_path: str,
        silence_threshold: float = -40.0,
        min_silence_duration: float = 0.5
    ) -> List[Tuple[float, float]]:
        """
        检测音频中的静音片段
        
        :param audio_path: 音频文件路径
        :param silence_threshold: 静音阈值 (dB)
        :param min_silence_duration: 最小静音时长(秒)
        :return: 静音片段列表 [(start_time, end_time), ...]
        """
        try:
            # NOTE: 需要安装 pydub 和 ffmpeg
            from pydub import AudioSegment
            from pydub.silence import detect_silence as pydub_detect_silence
            
            # 加载音频
            audio = AudioSegment.from_file(audio_path)
            
            # 检测静音片段 (返回毫秒)
            silence_ranges = pydub_detect_silence(
                audio,
                min_silence_len=int(min_silence_duration * 1000),
                silence_thresh=silence_threshold
            )
            
            # 转换为秒
            silence_ranges_sec = [
                (start / 1000.0, end / 1000.0) 
                for start, end in silence_ranges
            ]
            
            logger.info(f"检测到 {len(silence_ranges_sec)} 个静音片段")
            return silence_ranges_sec
            
        except ImportError:
            logger.error("需要安装 pydub: pip install pydub")
            return []
        except Exception as e:
            logger.error(f"静音检测失败: {e}")
            return []
    
    @staticmethod
    def detect_highlights(
        audio_path: str,
        threshold_percentile: float = 80.0,
        min_highlight_duration: float = 2.0
    ) -> List[Tuple[float, float]]:
        """
        检测音频中的高光片段(音量峰值)
        
        :param audio_path: 音频文件路径
        :param threshold_percentile: 音量阈值百分位 (0-100)
        :param min_highlight_duration: 最小高光时长(秒)
        :return: 高光片段列表 [(start_time, end_time), ...]
        """
        try:
            from pydub import AudioSegment
            import numpy as np
            
            # 加载音频
            audio = AudioSegment.from_file(audio_path)
            
            # 获取音频数据
            samples = np.array(audio.get_array_of_samples())
            
            # 计算每秒的平均音量
            sample_rate = audio.frame_rate
            chunk_size = sample_rate  # 1秒
            
            volumes = []
            for i in range(0, len(samples), chunk_size):
                chunk = samples[i:i + chunk_size]
                if len(chunk) > 0:
                    volume = np.abs(chunk).mean()
                    volumes.append(volume)
            
            # 计算阈值
            threshold = np.percentile(volumes, threshold_percentile)
            
            # 查找高光片段
            highlights = []
            start_idx = None
            
            for i, volume in enumerate(volumes):
                if volume >= threshold:
                    if start_idx is None:
                        start_idx = i
                else:
                    if start_idx is not None:
                        duration = (i - start_idx)
                        if duration >= min_highlight_duration:
                            highlights.append((
                                start_idx,
                                i
                            ))
                        start_idx = None
            
            # 处理最后一个片段
            if start_idx is not None:
                duration = (len(volumes) - start_idx)
                if duration >= min_highlight_duration:
                    highlights.append((start_idx, len(volumes)))
            
            logger.info(f"检测到 {len(highlights)} 个高光片段")
            return highlights
            
        except ImportError:
            logger.error("需要安装 pydub 和 numpy: pip install pydub numpy")
            return []
        except Exception as e:
            logger.error(f"高光检测失败: {e}")
            return []


class SmartEditor:
    """智能编辑器"""
    
    def __init__(self):
        self.audio_analyzer = AudioAnalyzer()
    
    def remove_silence(
        self,
        draft_content: Dict,
        silence_threshold: float = -40.0,
        min_silence_duration: float = 0.5
    ) -> Dict:
        """
        删除草稿中的静音片段
        
        :param draft_content: 草稿内容
        :param silence_threshold: 静音阈值 (dB)
        :param min_silence_duration: 最小静音时长(秒)
        :return: 处理后的草稿内容
        """
        try:
            tracks = draft_content.get("tracks", [])
            materials = draft_content.get("materials", {})
            
            for track in tracks:
                if track.get("type") != "video":
                    continue
                
                new_segments = []
                
                for segment in track.get("segments", []):
                    material_id = segment.get("material_id")
                    
                    # 查找对应的素材
                    material = None
                    for video in materials.get("videos", []):
                        if video.get("id") == material_id:
                            material = video
                            break
                    
                    if not material:
                        new_segments.append(segment)
                        continue
                    
                    # 获取音频路径
                    video_path = material.get("path")
                    if not video_path or not os.path.exists(video_path):
                        new_segments.append(segment)
                        continue
                    
                    # 检测静音片段
                    silence_ranges = self.audio_analyzer.detect_silence(
                        video_path,
                        silence_threshold,
                        min_silence_duration
                    )
                    
                    if not silence_ranges:
                        new_segments.append(segment)
                        continue
                    
                    # 分割片段,移除静音部分
                    source_range = segment.get("source_timerange", {})
                    source_start = source_range.get("start", 0) / 1000000.0  # 转为秒
                    source_duration = source_range.get("duration", 0) / 1000000.0
                    source_end = source_start + source_duration
                    
                    # 计算非静音片段
                    non_silence_ranges = []
                    current_start = source_start
                    
                    for silence_start, silence_end in silence_ranges:
                        # 检查静音片段是否在当前片段范围内
                        if silence_end <= source_start or silence_start >= source_end:
                            continue
                        
                        # 调整静音范围到片段范围内
                        silence_start = max(silence_start, source_start)
                        silence_end = min(silence_end, source_end)
                        
                        # 添加静音前的片段
                        if current_start < silence_start:
                            non_silence_ranges.append((current_start, silence_start))
                        
                        current_start = silence_end
                    
                    # 添加最后一个片段
                    if current_start < source_end:
                        non_silence_ranges.append((current_start, source_end))
                    
                    # 创建新片段
                    target_start = segment.get("target_timerange", {}).get("start", 0)
                    
                    for ns_start, ns_end in non_silence_ranges:
                        import copy
                        new_segment = copy.deepcopy(segment)
                        
                        duration_us = int((ns_end - ns_start) * 1000000)
                        
                        new_segment["source_timerange"]["start"] = int(ns_start * 1000000)
                        new_segment["source_timerange"]["duration"] = duration_us
                        new_segment["target_timerange"]["start"] = target_start
                        new_segment["target_timerange"]["duration"] = duration_us
                        
                        new_segments.append(new_segment)
                        target_start += duration_us
                
                track["segments"] = new_segments
            
            logger.info("静音片段删除完成")
            return draft_content
            
        except Exception as e:
            logger.error(f"删除静音片段失败: {e}")
            return draft_content
    
    def extract_highlights(
        self,
        draft_content: Dict,
        threshold_percentile: float = 80.0,
        min_highlight_duration: float = 2.0
    ) -> List[Dict]:
        """
        提取草稿中的高光片段信息
        
        :param draft_content: 草稿内容
        :param threshold_percentile: 音量阈值百分位
        :param min_highlight_duration: 最小高光时长(秒)
        :return: 高光片段信息列表
        """
        try:
            tracks = draft_content.get("tracks", [])
            materials = draft_content.get("materials", {})
            
            highlights = []
            
            for track in tracks:
                if track.get("type") != "video":
                    continue
                
                for segment in track.get("segments", []):
                    material_id = segment.get("material_id")
                    
                    # 查找对应的素材
                    material = None
                    for video in materials.get("videos", []):
                        if video.get("id") == material_id:
                            material = video
                            break
                    
                    if not material:
                        continue
                    
                    # 获取视频路径
                    video_path = material.get("path")
                    if not video_path or not os.path.exists(video_path):
                        continue
                    
                    # 检测高光片段
                    highlight_ranges = self.audio_analyzer.detect_highlights(
                        video_path,
                        threshold_percentile,
                        min_highlight_duration
                    )
                    
                    for start_sec, end_sec in highlight_ranges:
                        highlights.append({
                            "segment_id": segment.get("id"),
                            "material_id": material_id,
                            "start_time": start_sec,
                            "end_time": end_sec,
                            "duration": end_sec - start_sec
                        })
            
            logger.info(f"提取到 {len(highlights)} 个高光片段")
            return highlights
            
        except Exception as e:
            logger.error(f"提取高光片段失败: {e}")
            return []


# 单例实例
smart_editor = SmartEditor()
