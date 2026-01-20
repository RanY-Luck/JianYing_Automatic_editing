"""
转场库 - 剪映内置转场效果 ID 映射

NOTE: 转场 ID 需要从剪映实际草稿中提取
可以手动在剪映中应用转场,然后导出草稿分析 draft_content.json 获取真实 ID
"""

from typing import Dict, List, Optional
from enum import Enum


class TransitionCategory(str, Enum):
    """转场分类"""
    BASIC = "basic"  # 基础转场
    CREATIVE = "creative"  # 创意转场
    DYNAMIC = "dynamic"  # 动态转场
    GLITCH = "glitch"  # 故障转场


class TransitionLibrary:
    """转场库"""
    
    # 转场效果映射
    # NOTE: 这些是示例 ID,实际使用时需要替换为真实的剪映转场 ID
    TRANSITIONS: Dict[str, Dict[str, str]] = {
        # 基础转场
        "fade": {
            "id": "transition_fade_001",
            "name": "淡入淡出",
            "category": TransitionCategory.BASIC,
            "description": "经典淡入淡出效果",
            "default_duration": 0.5  # 默认时长(秒)
        },
        "dissolve": {
            "id": "transition_dissolve_001",
            "name": "溶解",
            "category": TransitionCategory.BASIC,
            "description": "溶解过渡效果",
            "default_duration": 0.8
        },
        "wipe_left": {
            "id": "transition_wipe_left_001",
            "name": "左擦除",
            "category": TransitionCategory.BASIC,
            "description": "从左向右擦除",
            "default_duration": 0.6
        },
        "wipe_right": {
            "id": "transition_wipe_right_001",
            "name": "右擦除",
            "category": TransitionCategory.BASIC,
            "description": "从右向左擦除",
            "default_duration": 0.6
        },
        "wipe_up": {
            "id": "transition_wipe_up_001",
            "name": "上擦除",
            "category": TransitionCategory.BASIC,
            "description": "从下向上擦除",
            "default_duration": 0.6
        },
        "wipe_down": {
            "id": "transition_wipe_down_001",
            "name": "下擦除",
            "category": TransitionCategory.BASIC,
            "description": "从上向下擦除",
            "default_duration": 0.6
        },
        
        # 动态转场
        "slide_left": {
            "id": "transition_slide_left_001",
            "name": "左滑动",
            "category": TransitionCategory.DYNAMIC,
            "description": "向左滑动切换",
            "default_duration": 0.5
        },
        "slide_right": {
            "id": "transition_slide_right_001",
            "name": "右滑动",
            "category": TransitionCategory.DYNAMIC,
            "description": "向右滑动切换",
            "default_duration": 0.5
        },
        "zoom_in": {
            "id": "transition_zoom_in_001",
            "name": "放大",
            "category": TransitionCategory.DYNAMIC,
            "description": "放大过渡",
            "default_duration": 0.7
        },
        "zoom_out": {
            "id": "transition_zoom_out_001",
            "name": "缩小",
            "category": TransitionCategory.DYNAMIC,
            "description": "缩小过渡",
            "default_duration": 0.7
        },
        "rotate_clockwise": {
            "id": "transition_rotate_cw_001",
            "name": "顺时针旋转",
            "category": TransitionCategory.DYNAMIC,
            "description": "顺时针旋转切换",
            "default_duration": 0.8
        },
        "rotate_counterclockwise": {
            "id": "transition_rotate_ccw_001",
            "name": "逆时针旋转",
            "category": TransitionCategory.DYNAMIC,
            "description": "逆时针旋转切换",
            "default_duration": 0.8
        },
        
        # 创意转场
        "blur": {
            "id": "transition_blur_001",
            "name": "模糊",
            "category": TransitionCategory.CREATIVE,
            "description": "模糊过渡效果",
            "default_duration": 0.6
        },
        "flash": {
            "id": "transition_flash_001",
            "name": "闪白",
            "category": TransitionCategory.CREATIVE,
            "description": "闪白过渡",
            "default_duration": 0.3
        },
        "circle": {
            "id": "transition_circle_001",
            "name": "圆形",
            "category": TransitionCategory.CREATIVE,
            "description": "圆形扩散",
            "default_duration": 0.7
        },
        
        # 故障转场
        "glitch": {
            "id": "transition_glitch_001",
            "name": "故障",
            "category": TransitionCategory.GLITCH,
            "description": "故障效果",
            "default_duration": 0.4
        },
        "rgb_split": {
            "id": "transition_rgb_split_001",
            "name": "RGB分离",
            "category": TransitionCategory.GLITCH,
            "description": "RGB色彩分离",
            "default_duration": 0.5
        },
    }
    
    @classmethod
    def get_transition_id(cls, transition_name: str) -> Optional[str]:
        """
        获取转场 ID
        
        :param transition_name: 转场名称
        :return: 转场 ID
        """
        transition_info = cls.TRANSITIONS.get(transition_name)
        return transition_info["id"] if transition_info else None
    
    @classmethod
    def get_transition_info(cls, transition_name: str) -> Optional[Dict]:
        """
        获取转场信息
        
        :param transition_name: 转场名称
        :return: 转场信息字典
        """
        return cls.TRANSITIONS.get(transition_name)
    
    @classmethod
    def list_transitions(cls, category: Optional[TransitionCategory] = None) -> List[Dict]:
        """
        列出转场
        
        :param category: 转场分类过滤
        :return: 转场列表
        """
        transitions = []
        for name, info in cls.TRANSITIONS.items():
            if category is None or info["category"] == category:
                transitions.append({
                    "name": name,
                    **info
                })
        return transitions
    
    @classmethod
    def get_random_transition(cls, category: Optional[TransitionCategory] = None) -> Optional[str]:
        """
        获取随机转场名称
        
        :param category: 转场分类过滤
        :return: 随机转场名称
        """
        import random
        transitions = cls.list_transitions(category)
        if transitions:
            return random.choice(transitions)["name"]
        return None


# 导出常用转场名称常量
class TransitionPresets:
    """转场预设"""
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    WIPE_UP = "wipe_up"
    WIPE_DOWN = "wipe_down"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    ROTATE_CLOCKWISE = "rotate_clockwise"
    ROTATE_COUNTERCLOCKWISE = "rotate_counterclockwise"
    BLUR = "blur"
    FLASH = "flash"
    CIRCLE = "circle"
    GLITCH = "glitch"
    RGB_SPLIT = "rgb_split"
