# 剪映自动剪辑项目 - 快速开始指南

## 🚀 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
copy .env.example .env
```

**重要配置项**：

```ini
# 数据库连接（默认使用 SQLite）
DATABASE_URL=sqlite+aiosqlite:///./jianying_auto.db

# 剪映路径（根据实际情况修改）
JIANYING_INSTALL_PATH=C:/Program Files/JianyingPro
JIANYING_DRAFT_PATH=C:/Users/冉勇/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft
```

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 测试剪映集成

```bash
python scripts/test_jianying.py
```

### 5. 启动应用

```bash
python main.py
```

访问 API 文档：http://localhost:8000/docs

## 📚 API 文档

### 素材管理

- `POST /api/v1/materials/upload` - 上传素材
- `GET /api/v1/materials` - 获取素材列表
- `GET /api/v1/materials/{id}` - 获取素材详情
- `PUT /api/v1/materials/{id}` - 更新素材信息
- `DELETE /api/v1/materials/{id}` - 删除素材
- `GET /api/v1/materials/statistics/summary` - 获取素材统计

### 草稿管理

- `POST /api/v1/drafts` - 创建草稿
- `GET /api/v1/drafts` - 获取草稿列表
- `GET /api/v1/drafts/{id}` - 获取草稿详情
- `PUT /api/v1/drafts/{id}` - 更新草稿信息
- `DELETE /api/v1/drafts/{id}` - 删除草稿
- `POST /api/v1/drafts/import/{jianying_draft_id}` - 从剪映导入草稿

## 🧪 测试

### 测试剪映集成

```bash
python scripts/test_jianying.py
```

这将测试：
- 列出剪映草稿箱中的草稿
- 获取指定草稿的信息
- 创建草稿文件夹

### 测试 API

启动应用后，访问 http://localhost:8000/docs 使用 Swagger UI 测试 API。

## 📝 开发进度

- [x] Phase 1: 基础设施搭建
- [x] 素材管理模块（完整 CRUD + API）
- [x] 草稿管理模块（完整 CRUD + API）
- [x] PyJianying 集成（草稿管理器、导出管理器框架）
- [ ] 模板管理模块
- [ ] 剪辑任务模块
- [ ] 导出管理模块
- [ ] UI 自动化完善（需要根据剪映 6.0.1 UI 结构调整）

## ⚠️ 注意事项

### 剪映 6.0.1 版本限制

- 草稿文件已加密，无法直接编辑 `draft_content.json`
- 导出功能需要使用 UI 自动化（`uiautomation`）
- 建议在专用机器上运行导出任务

### 下一步工作

1. 完善 UI 自动化代码（需要使用 UIAutomation Inspector 查看剪映窗口控件结构）
2. 实现模板管理模块
3. 实现剪辑任务模块
4. 实现导出管理模块
5. 添加单元测试和集成测试

## 📧 问题反馈

如有问题，请查看日志文件：`logs/info_*.log` 和 `logs/error_*.log`
