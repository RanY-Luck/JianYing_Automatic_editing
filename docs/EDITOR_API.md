# 智能剪辑功能 API 文档

## 📋 概述

剪映自动剪辑系统提供了完整的智能编辑 API,支持滤镜、转场、字幕、视频编辑等功能。

**基础 URL**: `http://localhost:8000/api/v1/editor`

---

## 🎨 滤镜接口

### 添加滤镜

**接口**: `POST /draft/{draft_id}/filter`

**参数**:
```json
{
  "filter_name": "vintage_1980",
  "intensity": 0.8,
  "segment_id": null
}
```

**可用滤镜**:
- 基础: `black_white`, `sepia`, `warm`, `cool`, `vivid`, `soft`
- 电影: `film_classic`, `film_noir`
- 复古: `vintage_1980`, `vintage_polaroid`
- 人像: `portrait_natural`, `portrait_beauty`
- 风景: `landscape_vibrant`, `landscape_sunset`
- 美食: `food_delicious`

---

## 🎬 转场接口

### 添加转场

**接口**: `POST /draft/{draft_id}/transition`

**参数**:
```json
{
  "transition_name": "fade",
  "duration": 0.5,
  "from_segment_id": null,
  "to_segment_id": null
}
```

**可用转场**:
- 基础: `fade`, `dissolve`, `wipe_left`, `wipe_right`, `wipe_up`, `wipe_down`
- 动态: `slide_left`, `slide_right`, `zoom_in`, `zoom_out`, `rotate_clockwise`, `rotate_counterclockwise`
- 创意: `blur`, `flash`, `circle`
- 故障: `glitch`, `rgb_split`

---

## 📝 字幕接口

### 添加字幕

**接口**: `POST /draft/{draft_id}/subtitle`

**参数**:
```json
{
  "text": "这是一段字幕",
  "start_time": 0.0,
  "duration": 3.0,
  "style": {
    "font_size": 48,
    "font_color": "#FFFFFF",
    "position_x": 0.5,
    "position_y": 0.9
  }
}
```

---

## ✂️ 视频编辑接口

### 分割视频

**接口**: `POST /draft/{draft_id}/split`

**参数**:
```json
{
  "segment_id": "SEGMENT_ID",
  "split_time": 5.0
}
```

### 裁剪视频

**接口**: `POST /draft/{draft_id}/trim`

**参数**:
```json
{
  "segment_id": "SEGMENT_ID",
  "start_time": 2.0,
  "end_time": 8.0
}
```

---

## 🎨 颜色调整接口

### 调整颜色

**接口**: `POST /draft/{draft_id}/adjust-color`

**参数**:
```json
{
  "segment_id": "SEGMENT_ID",
  "adjustments": {
    "brightness": 0.3,
    "contrast": 0.2,
    "saturation": -0.1
  }
}
```

---

## 🏷️ 贴纸/水印接口

### 添加贴纸

**接口**: `POST /draft/{draft_id}/sticker`

**参数**:
```json
{
  "sticker_path": "/path/to/watermark.png",
  "start_time": 0.0,
  "duration": 10.0,
  "position": {
    "x": 0.9,
    "y": 0.1
  },
  "scale": 0.2
}
```

---

## 🎵 音乐接口

### 添加背景音乐

**接口**: `POST /draft/{draft_id}/add-music`

**参数**:
```json
{
  "music_path": "/path/to/music.mp3"
}
```

---

## 🔄 智能去重接口

### 智能去重

**接口**: `POST /draft/{draft_id}/deduplicate`

**参数**:
```json
{
  "speed": true,
  "mirror": true,
  "crop": true,
  "filter": true
}
```

---

## 📊 完整功能列表

| 功能 | 接口 | 状态 |
|------|------|------|
| 添加滤镜 | `/filter` | ✅ |
| 添加转场 | `/transition` | ✅ |
| 添加字幕 | `/subtitle` | ✅ |
| 分割视频 | `/split` | ✅ |
| 裁剪视频 | `/trim` | ✅ |
| 调整颜色 | `/adjust-color` | ✅ |
| 添加贴纸 | `/sticker` | ✅ |
| 添加音乐 | `/add-music` | ✅ |
| 智能去重 | `/deduplicate` | ✅ |

---

## 🚀 快速开始

1. 启动应用:
```bash
python main.py
```

2. 访问 API 文档:
```
http://localhost:8000/docs
```

3. 测试接口:
使用 Swagger UI 或 Postman 测试各个接口

---

## ⚠️ 注意事项

1. **滤镜和转场 ID**: 当前为示例 ID,需要从实际剪映草稿中提取真实 ID
2. **文件备份**: 所有编辑操作会自动创建 `.bak` 备份文件
3. **剪映版本**: 仅支持剪映 5.9 版本(未加密)
