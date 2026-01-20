# 模板配置指南 (template_data)

## 📋 模板配置结构

模板配置是一个 JSON 对象,用于定义应用到草稿的各种编辑效果。以下是完整的配置说明:

---

## 🎨 完整模板示例

```json
{
  "name": "我的视频模板",
  "version": "1.0",
  "description": "适用于 Vlog 的模板",
  "filter": {
    "name": "vintage_1980",
    "intensity": 0.8
  },
  "transition": {
    "name": "fade",
    "duration": 0.5
  },
  "subtitles": [
    {
      "text": "开场标题",
      "start_time": 0.0,
      "duration": 3.0,
      "font_size": 60,
      "font_color": "#FFD700",
      "position_x": 0.5,
      "position_y": 0.1
    },
    {
      "text": "结尾感谢",
      "start_time": 58.0,
      "duration": 2.0,
      "font_size": 48,
      "font_color": "#FFFFFF",
      "position_x": 0.5,
      "position_y": 0.9
    }
  ],
  "color_adjustments": {
    "brightness": 0.2,
    "contrast": 0.1,
    "saturation": 0.3
  },
  "smart_dedup": true,
  "dedup_config": {
    "speed": true,
    "mirror": true,
    "crop": true,
    "filter": false
  }
}
```

---

## 📝 字段详细说明

### 1. 基础信息 (可选)

```json
{
  "name": "模板名称",           // 可选,模板的名称
  "version": "1.0",            // 可选,模板版本号
  "description": "模板描述"     // 可选,模板用途说明
}
```

### 2. 滤镜配置 (filter)

```json
{
  "filter": {
    "name": "滤镜名称",          // 必填,滤镜名称
    "intensity": 0.8            // 可选,滤镜强度 0.0-1.0,默认 1.0
  }
}
```

**可用滤镜名称**:

| 分类 | 滤镜名称 | 说明 |
|------|---------|------|
| 基础 | `black_white` | 黑白 |
| 基础 | `sepia` | 怀旧 |
| 基础 | `warm` | 暖色 |
| 基础 | `cool` | 冷色 |
| 基础 | `vivid` | 鲜艳 |
| 基础 | `soft` | 柔和 |
| 电影 | `film_classic` | 经典电影 |
| 电影 | `film_noir` | 黑色电影 |
| 复古 | `vintage_1980` | 80年代 |
| 复古 | `vintage_polaroid` | 宝丽来 |
| 人像 | `portrait_natural` | 自然人像 |
| 人像 | `portrait_beauty` | 美颜 |
| 风景 | `landscape_vibrant` | 鲜艳风景 |
| 风景 | `landscape_sunset` | 日落 |
| 美食 | `food_delicious` | 美味 |

### 3. 转场配置 (transition)

```json
{
  "transition": {
    "name": "转场名称",          // 必填,转场名称
    "duration": 0.5            // 可选,转场时长(秒),默认 0.5
  }
}
```

**可用转场名称**:

| 分类 | 转场名称 | 说明 |
|------|---------|------|
| 基础 | `fade` | 淡入淡出 |
| 基础 | `dissolve` | 溶解 |
| 基础 | `wipe_left` | 左擦除 |
| 基础 | `wipe_right` | 右擦除 |
| 基础 | `wipe_up` | 上擦除 |
| 基础 | `wipe_down` | 下擦除 |
| 动态 | `slide_left` | 左滑动 |
| 动态 | `slide_right` | 右滑动 |
| 动态 | `zoom_in` | 放大 |
| 动态 | `zoom_out` | 缩小 |
| 动态 | `rotate_clockwise` | 顺时针旋转 |
| 动态 | `rotate_counterclockwise` | 逆时针旋转 |
| 创意 | `blur` | 模糊 |
| 创意 | `flash` | 闪白 |
| 创意 | `circle` | 圆形扩散 |
| 故障 | `glitch` | 故障效果 |
| 故障 | `rgb_split` | RGB分离 |

### 4. 字幕配置 (subtitles)

```json
{
  "subtitles": [
    {
      "text": "字幕文本",         // 必填,字幕内容
      "start_time": 0.0,       // 必填,开始时间(秒)
      "duration": 3.0,         // 必填,持续时长(秒)
      "font_size": 48,         // 可选,字体大小,默认 48
      "font_color": "#FFFFFF", // 可选,字体颜色,默认白色
      "position_x": 0.5,       // 可选,X位置 0.0-1.0,默认 0.5(居中)
      "position_y": 0.9        // 可选,Y位置 0.0-1.0,默认 0.9(底部)
    }
  ]
}
```

**位置说明**:
- `position_x`: 0.0=左, 0.5=中, 1.0=右
- `position_y`: 0.0=上, 0.5=中, 1.0=下

**颜色格式**: 十六进制颜色码,如 `#FFFFFF`(白色), `#FFD700`(金色), `#FF0000`(红色)

### 5. 颜色调整 (color_adjustments)

```json
{
  "color_adjustments": {
    "brightness": 0.2,    // 可选,亮度调整 -1.0 到 1.0
    "contrast": 0.1,      // 可选,对比度调整 -1.0 到 1.0
    "saturation": 0.3     // 可选,饱和度调整 -1.0 到 1.0
  }
}
```

**数值说明**:
- `0.0`: 不调整
- 正值: 增强效果
- 负值: 减弱效果
- 范围: -1.0 到 1.0

### 6. 智能去重 (smart_dedup)

```json
{
  "smart_dedup": true,      // 是否启用智能去重
  "dedup_config": {
    "speed": true,          // 是否应用微变速
    "mirror": true,         // 是否应用随机镜像
    "crop": true,           // 是否应用随机裁剪
    "filter": false         // 是否应用随机滤镜
  }
}
```

---

## 🎯 常用模板示例

### 示例 1: 简单滤镜模板

```json
{
  "filter": {
    "name": "vivid",
    "intensity": 0.9
  }
}
```

### 示例 2: Vlog 模板

```json
{
  "filter": {
    "name": "warm",
    "intensity": 0.7
  },
  "transition": {
    "name": "fade",
    "duration": 0.5
  },
  "subtitles": [
    {
      "text": "我的 Vlog",
      "start_time": 0.0,
      "duration": 2.5,
      "font_size": 60,
      "font_color": "#FFD700"
    }
  ],
  "color_adjustments": {
    "brightness": 0.1,
    "saturation": 0.2
  }
}
```

### 示例 3: 复古电影模板

```json
{
  "filter": {
    "name": "film_classic",
    "intensity": 0.8
  },
  "transition": {
    "name": "dissolve",
    "duration": 0.8
  },
  "color_adjustments": {
    "contrast": 0.2,
    "saturation": -0.1
  }
}
```

### 示例 4: 快节奏短视频模板

```json
{
  "filter": {
    "name": "vivid",
    "intensity": 1.0
  },
  "transition": {
    "name": "flash",
    "duration": 0.3
  },
  "color_adjustments": {
    "brightness": 0.1,
    "contrast": 0.2,
    "saturation": 0.4
  },
  "smart_dedup": true,
  "dedup_config": {
    "speed": true,
    "mirror": true,
    "crop": true
  }
}
```

### 示例 5: 美食视频模板

```json
{
  "filter": {
    "name": "food_delicious",
    "intensity": 0.9
  },
  "transition": {
    "name": "zoom_in",
    "duration": 0.6
  },
  "subtitles": [
    {
      "text": "美食分享",
      "start_time": 0.0,
      "duration": 2.0,
      "font_size": 55,
      "font_color": "#FF6B6B",
      "position_y": 0.15
    }
  ],
  "color_adjustments": {
    "saturation": 0.3,
    "brightness": 0.1
  }
}
```

---

## 🔧 使用方法

### 方法 1: 通过 API 应用模板

```python
import requests

template_data = {
    "filter": {"name": "vintage_1980", "intensity": 0.8},
    "transition": {"name": "fade", "duration": 0.5}
}

response = requests.post(
    "http://localhost:8000/api/v1/editor/draft/1/apply-template",
    json={"template_config": template_data}
)
```

### 方法 2: 批量应用模板

```python
template_data = {
    "filter": {"name": "vivid", "intensity": 0.9},
    "color_adjustments": {
        "brightness": 0.2,
        "saturation": 0.3
    }
}

response = requests.post(
    "http://localhost:8000/api/v1/editor/batch/apply-template",
    json={
        "draft_ids": [1, 2, 3],
        "template_config": template_data
    }
)
```

---

## 💡 最佳实践

1. **从简单开始**: 先只配置滤镜或转场,测试效果后再添加其他配置

2. **保存常用模板**: 将常用的模板配置保存为 JSON 文件,方便复用

3. **渐进调整**: 颜色调整建议从小数值开始(如 0.1),避免过度调整

4. **字幕位置**: 
   - 标题建议放顶部: `position_y: 0.1`
   - 正文建议放底部: `position_y: 0.9`

5. **转场时长**: 
   - 快节奏视频: 0.3-0.5 秒
   - 慢节奏视频: 0.5-1.0 秒

---

## ⚠️ 注意事项

1. **滤镜和转场 ID**: 当前为示例 ID,实际使用需要从剪映草稿中提取真实 ID

2. **字段都是可选的**: 可以只配置需要的部分,不需要的可以省略

3. **时间单位**: 所有时间相关字段都使用**秒**作为单位

4. **颜色格式**: 必须使用十六进制格式,如 `#FFFFFF`

5. **数值范围**: 
   - intensity: 0.0-1.0
   - position: 0.0-1.0
   - color_adjustments: -1.0 到 1.0

---

## 📚 相关文档

- API 文档: `http://localhost:8000/docs`
- 滤镜库: `backend/integrations/jianying_api/filter_library.py`
- 转场库: `backend/integrations/jianying_api/transition_library.py`
- 模板引擎: `backend/integrations/jianying_api/template_engine.py`
