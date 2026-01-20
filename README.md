# 剪映自动剪辑系统

基于 **JianYingApi** 和 **PyJianying** 的自动化视频剪辑系统，支持剪映 6.0.1 版本。

## 📋 项目简介

本项目旨在通过编程方式自动化剪映视频编辑流程，实现从素材管理、草稿创建、自动剪辑到批量导出的完整工作流。

### 核心功能

- 🎬 **素材管理**：上传、存储、分类、搜索视频/音频/图片素材
- 📝 **草稿管理**：创建、编辑、版本管理剪映草稿
- 🎨 **模板管理**：创建、应用剪辑模板，快速批量生产
- ⚙️ **自动剪辑**：基于模板和规则自动化剪辑视频
- 📤 **批量导出**：使用 UI 自动化批量导出视频（支持剪映 6.0.1）

## 🛠️ 技术栈

- **后端框架**: FastAPI (Python 3.10+)
- **数据库**: PostgreSQL / MySQL (SQLAlchemy AsyncIO)
- **核心库**:
  - `PyJianying` - 草稿文件操作
  - `JianYingApi` - 高级编辑操作
  - `uiautomation` - Windows UI 自动化（批量导出）
- **其他**: Loguru, Pydantic, Uvicorn

## 📦 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd JianYing_Automatic_editing
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
copy .env.example .env
```

**重要配置项**：

```ini
# 数据库连接
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/jianying_auto

# 剪映路径（根据实际情况修改）
JIANYING_INSTALL_PATH=C:/Program Files/JianyingPro
JIANYING_DRAFT_PATH=C:/Users/冉勇/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft
```

### 5. 初始化数据库

```bash
python scripts/init_db.py
```

## 🚀 运行

### 开发模式

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

访问 API 文档：http://localhost:8000/docs

## 📁 项目结构

```
JianYing_Automatic_editing/
├── backend/                    # 后端核心代码
│   ├── app/                    # 应用模块
│   │   ├── material/           # 素材管理
│   │   ├── draft/              # 草稿管理
│   │   ├── template/           # 模板管理
│   │   ├── task/               # 剪辑任务
│   │   └── export/             # 导出管理
│   ├── core/                   # 核心配置
│   ├── common/                 # 公共模块
│   ├── utils/                  # 工具类
│   └── integrations/           # 第三方库集成
│       ├── jianying_api/       # JianYingApi 封装
│       └── py_jianying/        # PyJianying 封装
├── config/                     # 配置文件
├── storage/                    # 存储目录
├── logs/                       # 日志目录
├── scripts/                    # 脚本工具
├── tests/                      # 测试目录
├── main.py                     # 应用入口
└── requirements.txt            # 依赖列表
```

## ⚠️ 重要说明

### 剪映 6.0.1 版本兼容性

> **注意**: 剪映 6.0.1 版本对 `draft_content.json` 进行了加密，导致无法直接通过 PyJianying 读写草稿内容。

**当前解决方案**：

1. **草稿管理**：只能读取草稿元数据（`draft_info.json`），无法直接编辑草稿内容
2. **批量导出**：使用 `uiautomation` 库实现 UI 自动化导出
3. **高级编辑**：优先使用 JianYingApi 进行视频编辑操作

**替代方案**（推荐）：

- 使用剪映 5.9 版本（最后一个未加密版本）
- 研究剪映 6.0.1 的加密算法（可能违反 ToS）
- 完全基于 UI 自动化操作剪映界面

### UI 自动化注意事项

- 批量导出功能仅支持 **Windows** 系统
- 导出过程中**不要操作剪映窗口**
- 建议在**专用机器**上运行导出任务
- 导出前确保有足够的**磁盘空间**

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行指定模块测试
pytest tests/test_material/

# 生成覆盖率报告
pytest --cov=backend --cov-report=html
```

## 📝 开发计划

详见 [项目结构设计方案](./docs/project_structure_design.md)

- [x] Phase 1: 基础设施搭建
- [ ] Phase 2: 第三方库集成
- [ ] Phase 3: 核心业务模块
- [ ] Phase 4: 测试与优化

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📧 联系方式

如有问题，请联系：[your-email@example.com]

---

**注意**: 本项目仅供学习和研究使用，请遵守剪映的服务条款。