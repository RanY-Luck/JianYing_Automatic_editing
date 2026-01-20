"""
滤镜库 - 剪映内置滤镜 ID 映射

NOTE: 滤镜 ID 需要从剪映实际草稿中提取
可以手动在剪映中应用滤镜,然后导出草稿分析 draft_content.json 获取真实 ID
"""

from typing import Dict, List, Optional
from enum import Enum


class FilterCategory(str, Enum):
    """滤镜分类"""
    BASIC = "basic"  # 基础滤镜
    FILM = "film"  # 电影滤镜
    VINTAGE = "vintage"  # 复古滤镜
    PORTRAIT = "portrait"  # 人像滤镜
    LANDSCAPE = "landscape"  # 风景滤镜
    FOOD = "food"  # 美食滤镜


class FilterLibrary:
    """滤镜库"""
    
    # 基础滤镜映射
    # NOTE: 这些是示例 ID,实际使用时需要替换为真实的剪映滤镜 ID
    FILTERS: Dict[str, Dict[str, str]] = {
        # 基础滤镜
        "black_white": {
            "id": "filter_black_white_001",
            "name": "黑白",
            "category": FilterCategory.BASIC,
            "description": "经典黑白滤镜"
        },
        "sepia": {
            "id": "filter_sepia_001",
            "name": "怀旧",
            "category": FilterCategory.BASIC,
            "description": "怀旧棕褐色调"
        },
        "warm": {
            "id": "filter_warm_001",
            "name": "暖色",
            "category": FilterCategory.BASIC,
            "description": "温暖色调"
        },
        "cool": {
            "id": "filter_cool_001",
            "name": "冷色",
            "category": FilterCategory.BASIC,
            "description": "清冷色调"
        },
        "vivid": {
            "id": "filter_vivid_001",
            "name": "鲜艳",
            "category": FilterCategory.BASIC,
            "description": "增强饱和度"
        },
        "soft": {
            "id": "filter_soft_001",
            "name": "柔和",
            "category": FilterCategory.BASIC,
            "description": "柔和朦胧效果"
        },
        
        # 电影滤镜
        "film_classic": {
            "id": "filter_film_classic_001",
            "name": "经典电影",
            "category": FilterCategory.FILM,
            "description": "经典电影胶片效果"
        },
        "film_noir": {
            "id": "filter_film_noir_001",
            "name": "黑色电影",
            "category": FilterCategory.FILM,
            "description": "黑色电影风格"
        },
        
        # 复古滤镜
        "vintage_1980": {
            "id": "filter_vintage_1980_001",
            "name": "80年代",
            "category": FilterCategory.VINTAGE,
            "description": "80年代复古风格"
        },
        "vintage_polaroid": {
            "id": "filter_vintage_polaroid_001",
            "name": "宝丽来",
            "category": FilterCategory.VINTAGE,
            "description": "宝丽来拍立得效果"
        },
        
        # 人像滤镜
        "portrait_natural": {
            "id": "filter_portrait_natural_001",
            "name": "自然人像",
            "category": FilterCategory.PORTRAIT,
            "description": "自然肤色增强"
        },
        "portrait_beauty": {
            "id": "filter_portrait_beauty_001",
            "name": "美颜",
            "category": FilterCategory.PORTRAIT,
            "description": "美颜效果"
        },
        
        # 风景滤镜
        "landscape_vibrant": {
            "id": "filter_landscape_vibrant_001",
            "name": "鲜艳风景",
            "category": FilterCategory.LANDSCAPE,
            "description": "增强风景色彩"
        },
        "landscape_sunset": {
            "id": "filter_landscape_sunset_001",
            "name": "日落",
            "category": FilterCategory.LANDSCAPE,
            "description": "日落暖色调"
        },
        
        # 美食滤镜
        "food_delicious": {
            "id": "filter_food_delicious_001",
            "name": "美味",
            "category": FilterCategory.FOOD,
            "description": "增强食物色彩"
        },
    }
    
    @classmethod
    def get_filter_id(cls, filter_name: str) -> Optional[str]:
        """
        获取滤镜 ID
        
        :param filter_name: 滤镜名称
        :return: 滤镜 ID
        """
        filter_info = cls.FILTERS.get(filter_name)
        return filter_info["id"] if filter_info else None
    
    @classmethod
    def get_filter_info(cls, filter_name: str) -> Optional[Dict]:
        """
        获取滤镜信息
        
        :param filter_name: 滤镜名称
        :return: 滤镜信息字典
        """
        return cls.FILTERS.get(filter_name)
    
    @classmethod
    def list_filters(cls, category: Optional[FilterCategory] = None) -> List[Dict]:
        """
        列出滤镜
        
        :param category: 滤镜分类过滤
        :return: 滤镜列表
        """
        filters = []
        for name, info in cls.FILTERS.items():
            if category is None or info["category"] == category:
                filters.append({
                    "name": name,
                    **info
                })
        return filters
    
    @classmethod
    def get_random_filter(cls, category: Optional[FilterCategory] = None) -> Optional[str]:
        """
        获取随机滤镜名称
        
        :param category: 滤镜分类过滤
        :return: 随机滤镜名称
        """
        import random
        filters = cls.list_filters(category)
        if filters:
            return random.choice(filters)["name"]
        return None


# 导出常用滤镜名称常量
class FilterPresets:
    """滤镜预设"""
    BLACK_WHITE = "black_white"
    SEPIA = "sepia"
    WARM = "warm"
    COOL = "cool"
    VIVID = "vivid"
    SOFT = "soft"
    FILM_CLASSIC = "film_classic"
    FILM_NOIR = "film_noir"
    VINTAGE_1980 = "vintage_1980"
    VINTAGE_POLAROID = "vintage_polaroid"
    PORTRAIT_NATURAL = "portrait_natural"
    PORTRAIT_BEAUTY = "portrait_beauty"
    LANDSCAPE_VIBRANT = "landscape_vibrant"
    LANDSCAPE_SUNSET = "landscape_sunset"
    FOOD_DELICIOUS = "food_delicious"
