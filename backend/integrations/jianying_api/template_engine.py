"""
模板应用引擎

支持:
1. 模板参数化
2. 批量应用模板到素材
3. 模板配置管理
"""

import json
import os
from typing import Dict, List, Any, Optional
from loguru import logger
from backend.integrations.jianying_api.draft_editor import DraftEditor


class TemplateEngine:
    """模板应用引擎"""
    
    def __init__(self):
        pass
    
    def apply_template(
        self,
        draft_content: Dict,
        template_config: Dict[str, Any]
    ) -> Dict:
        """
        应用模板到草稿
        
        :param draft_content: 草稿内容
        :param template_config: 模板配置
        :return: 应用模板后的草稿内容
        """
        try:
            editor = DraftEditor(draft_content)
            
            # 应用滤镜
            if "filter" in template_config:
                filter_config = template_config["filter"]
                editor.add_filter(
                    filter_config.get("name", "vivid"),
                    filter_config.get("intensity", 0.8)
                )
            
            # 应用转场
            if "transition" in template_config:
                transition_config = template_config["transition"]
                editor.add_transition(
                    transition_config.get("name", "fade"),
                    transition_config.get("duration", 0.5)
                )
            
            # 添加字幕
            if "subtitles" in template_config:
                for subtitle in template_config["subtitles"]:
                    editor.add_text(
                        subtitle.get("text", ""),
                        subtitle.get("start_time", 0.0),
                        subtitle.get("duration", 3.0),
                        subtitle.get("font_size", 48),
                        subtitle.get("font_color", "#FFFFFF"),
                        subtitle.get("position_x", 0.5),
                        subtitle.get("position_y", 0.9)
                    )
            
            # 调整颜色
            if "color_adjustments" in template_config:
                adjustments = template_config["color_adjustments"]
                # 应用到所有视频片段
                for track in editor.tracks:
                    if track.get("type") == "video":
                        for segment in track.get("segments", []):
                            segment_id = segment.get("id")
                            if "brightness" in adjustments:
                                editor.adjust_brightness(segment_id, adjustments["brightness"])
                            if "contrast" in adjustments:
                                editor.adjust_contrast(segment_id, adjustments["contrast"])
                            if "saturation" in adjustments:
                                editor.adjust_saturation(segment_id, adjustments["saturation"])
            
            # 应用智能去重
            if template_config.get("smart_dedup", False):
                dedup_config = template_config.get("dedup_config", {})
                editor.deduplicate(dedup_config)
            
            logger.info("模板应用成功")
            return editor.get_content()
            
        except Exception as e:
            logger.error(f"应用模板失败: {e}")
            return draft_content
    
    def batch_apply_template(
        self,
        draft_paths: List[str],
        template_config: Dict[str, Any],
        output_dir: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        批量应用模板到多个草稿
        
        :param draft_paths: 草稿路径列表
        :param template_config: 模板配置
        :param output_dir: 输出目录
        :return: 处理结果列表
        """
        results = []
        
        for draft_path in draft_paths:
            try:
                # 读取草稿内容
                content_path = os.path.join(draft_path, "draft_content.json")
                if not os.path.exists(content_path):
                    results.append({
                        "draft_path": draft_path,
                        "success": False,
                        "error": "草稿内容文件不存在"
                    })
                    continue
                
                with open(content_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                
                # 应用模板
                new_content = self.apply_template(content, template_config)
                
                # 保存结果
                if output_dir:
                    # 保存到输出目录
                    draft_name = os.path.basename(draft_path)
                    output_path = os.path.join(output_dir, draft_name)
                    os.makedirs(output_path, exist_ok=True)
                    
                    output_content_path = os.path.join(output_path, "draft_content.json")
                else:
                    # 备份并覆盖原文件
                    import shutil
                    shutil.copy(content_path, content_path + ".bak")
                    output_content_path = content_path
                
                with open(output_content_path, "w", encoding="utf-8") as f:
                    json.dump(new_content, f, ensure_ascii=False, indent=2)
                
                results.append({
                    "draft_path": draft_path,
                    "success": True,
                    "output_path": output_content_path
                })
                
                logger.info(f"批量应用模板成功: {draft_path}")
                
            except Exception as e:
                logger.error(f"批量应用模板失败 {draft_path}: {e}")
                results.append({
                    "draft_path": draft_path,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def create_template_from_draft(
        self,
        draft_content: Dict,
        template_name: str
    ) -> Dict[str, Any]:
        """
        从草稿创建模板配置
        
        :param draft_content: 草稿内容
        :param template_name: 模板名称
        :return: 模板配置
        """
        template_config = {
            "name": template_name,
            "version": "1.0",
            "description": f"从草稿自动生成的模板: {template_name}"
        }
        
        try:
            materials = draft_content.get("materials", {})
            
            # 提取滤镜配置
            if materials.get("filters"):
                first_filter = materials["filters"][0]
                template_config["filter"] = {
                    "name": first_filter.get("name", "vivid"),
                    "intensity": first_filter.get("intensity", 0.8)
                }
            
            # 提取转场配置
            if materials.get("transitions"):
                first_transition = materials["transitions"][0]
                template_config["transition"] = {
                    "name": first_transition.get("name", "fade"),
                    "duration": first_transition.get("duration", 500000) / 1000000.0
                }
            
            # 提取字幕配置
            subtitles = []
            for track in draft_content.get("tracks", []):
                if track.get("type") == "text":
                    for segment in track.get("segments", []):
                        material_id = segment.get("material_id")
                        # 查找对应的文本素材
                        for text_material in materials.get("texts", []):
                            if text_material.get("id") == material_id:
                                subtitles.append({
                                    "text": text_material.get("content", ""),
                                    "start_time": segment.get("target_timerange", {}).get("start", 0) / 1000000.0,
                                    "duration": segment.get("target_timerange", {}).get("duration", 0) / 1000000.0,
                                    "font_size": text_material.get("font_size", 48),
                                    "font_color": text_material.get("font_color", "#FFFFFF")
                                })
            
            if subtitles:
                template_config["subtitles"] = subtitles
            
            logger.info(f"创建模板配置成功: {template_name}")
            return template_config
            
        except Exception as e:
            logger.error(f"创建模板配置失败: {e}")
            return template_config


# 单例实例
template_engine = TemplateEngine()
