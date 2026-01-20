"""
模板管理器 - 基于 PyJianying

NOTE: 此模块用于管理剪映草稿模板
支持从草稿创建模板、应用模板到草稿、替换素材等功能
"""
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any

from loguru import logger

from backend.core.conf import settings


class TemplateManager:
    """
    模板管理器
    
    NOTE: 用于管理剪映草稿模板
    支持剪映 5.9 版本(未加密的 draft_content.json)
    """
    
    def __init__(self):
        self.storage_draft_path = settings.draft_path
        self.template_path = os.path.join(settings.storage_root, "templates")
        os.makedirs(self.template_path, exist_ok=True)
    
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
                shutil.copy2(content_file, backup_file)
            
            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存草稿内容成功: {content_file}")
            return True
        
        except Exception as e:
            logger.error(f"保存草稿内容失败: {e}")
            return False
    
    def create_template_from_draft(
        self,
        draft_path: str,
        template_name: str,
        description: str = ""
    ) -> Optional[str]:
        """
        从草稿创建模板
        
        :param draft_path: 草稿路径
        :param template_name: 模板名称
        :param description: 模板描述
        :return: 模板路径
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content:
                return None
            
            # 创建模板目录
            template_dir = os.path.join(self.template_path, template_name)
            os.makedirs(template_dir, exist_ok=True)
            
            # 提取模板数据
            template_data = {
                "name": template_name,
                "description": description,
                "canvas_config": content.get("canvas_config", {}),
                "tracks": content.get("tracks", []),
                "materials_mapping": self._extract_materials_mapping(content),
                "version": "1.0"
            }
            
            # 保存模板
            template_file = os.path.join(template_dir, "template.json")
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"创建模板成功: {template_name}")
            return template_dir
        
        except Exception as e:
            logger.error(f"创建模板失败: {e}")
            return None
    
    def _extract_materials_mapping(self, content: dict) -> Dict[str, dict]:
        """
        提取素材映射关系
        
        :param content: 草稿内容
        :return: 素材映射 {material_id: {type, path, ...}}
        """
        materials_mapping = {}
        
        # 从 tracks 中提取素材引用
        for track in content.get('tracks', []):
            for segment in track.get('segments', []):
                material_id = segment.get('material_id')
                if material_id:
                    materials_mapping[material_id] = {
                        "type": track.get('type'),
                        "placeholder": True  # 标记为占位符,需要替换
                    }
        
        return materials_mapping
    
    def save_template(self, template_data: dict, template_path: str) -> bool:
        """
        保存模板到文件
        
        :param template_data: 模板数据
        :param template_path: 模板路径
        :return: 是否成功
        """
        try:
            os.makedirs(os.path.dirname(template_path), exist_ok=True)
            
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存模板成功: {template_path}")
            return True
        
        except Exception as e:
            logger.error(f"保存模板失败: {e}")
            return False
    
    def load_template(self, template_path: str) -> Optional[dict]:
        """
        加载模板
        
        :param template_path: 模板路径
        :return: 模板数据
        """
        try:
            if not os.path.exists(template_path):
                logger.error(f"模板文件不存在: {template_path}")
                return None
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            return template_data
        
        except Exception as e:
            logger.error(f"加载模板失败: {e}")
            return None
    
    def apply_template(
        self,
        draft_path: str,
        template_path: str,
        materials_mapping: Dict[str, str]
    ) -> bool:
        """
        应用模板到草稿
        
        :param draft_path: 草稿路径
        :param template_path: 模板路径
        :param materials_mapping: 素材映射 {template_material_id: new_material_id}
        :return: 是否成功
        """
        try:
            # 加载模板
            template_data = self.load_template(template_path)
            if not template_data:
                return False
            
            # 加载草稿
            content = self._load_draft_content(draft_path)
            if not content:
                return False
            
            # 应用画布配置
            if 'canvas_config' in template_data:
                content['canvas_config'] = template_data['canvas_config']
            
            # 应用轨道(替换素材 ID)
            if 'tracks' in template_data:
                new_tracks = self._replace_materials_in_tracks(
                    template_data['tracks'],
                    materials_mapping
                )
                content['tracks'] = new_tracks
            
            # 保存草稿
            if self._save_draft_content(draft_path, content):
                logger.info(f"应用模板成功: {template_path}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"应用模板失败: {e}")
            return False
    
    def _replace_materials_in_tracks(
        self,
        tracks: List[dict],
        materials_mapping: Dict[str, str]
    ) -> List[dict]:
        """
        替换轨道中的素材 ID
        
        :param tracks: 轨道列表
        :param materials_mapping: 素材映射
        :return: 新的轨道列表
        """
        import copy
        new_tracks = copy.deepcopy(tracks)
        
        for track in new_tracks:
            for segment in track.get('segments', []):
                old_material_id = segment.get('material_id')
                if old_material_id and old_material_id in materials_mapping:
                    segment['material_id'] = materials_mapping[old_material_id]
        
        return new_tracks
    
    def replace_materials(
        self,
        draft_path: str,
        old_material_id: str,
        new_material_id: str
    ) -> bool:
        """
        替换草稿中的素材
        
        :param draft_path: 草稿路径
        :param old_material_id: 旧素材 ID
        :param new_material_id: 新素材 ID
        :return: 是否成功
        """
        try:
            content = self._load_draft_content(draft_path)
            if not content:
                return False
            
            # 替换所有轨道中的素材 ID
            replaced_count = 0
            for track in content.get('tracks', []):
                for segment in track.get('segments', []):
                    if segment.get('material_id') == old_material_id:
                        segment['material_id'] = new_material_id
                        replaced_count += 1
            
            if replaced_count == 0:
                logger.warning(f"未找到素材: {old_material_id}")
                return False
            
            if self._save_draft_content(draft_path, content):
                logger.info(f"替换素材成功: {old_material_id} -> {new_material_id}, 共 {replaced_count} 处")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"替换素材失败: {e}")
            return False
    
    def validate_template(self, template_data: dict) -> bool:
        """
        验证模板格式
        
        :param template_data: 模板数据
        :return: 是否有效
        """
        try:
            # 检查必需字段
            required_fields = ['name', 'tracks', 'materials_mapping']
            for field in required_fields:
                if field not in template_data:
                    logger.error(f"模板缺少必需字段: {field}")
                    return False
            
            # 检查轨道格式
            if not isinstance(template_data['tracks'], list):
                logger.error("模板 tracks 字段必须是数组")
                return False
            
            # 检查素材映射格式
            if not isinstance(template_data['materials_mapping'], dict):
                logger.error("模板 materials_mapping 字段必须是对象")
                return False
            
            logger.info("模板验证通过")
            return True
        
        except Exception as e:
            logger.error(f"模板验证失败: {e}")
            return False
    
    def check_materials_compatibility(
        self,
        template_data: dict,
        materials: List[dict]
    ) -> bool:
        """
        检查素材兼容性
        
        :param template_data: 模板数据
        :param materials: 素材列表
        :return: 是否兼容
        """
        try:
            template_materials = template_data.get('materials_mapping', {})
            
            # 检查素材数量
            if len(materials) < len(template_materials):
                logger.warning(f"素材数量不足: 需要 {len(template_materials)}, 提供 {len(materials)}")
                return False
            
            # TODO: 检查素材类型匹配
            
            logger.info("素材兼容性检查通过")
            return True
        
        except Exception as e:
            logger.error(f"素材兼容性检查失败: {e}")
            return False


# 单例实例
template_manager = TemplateManager()
