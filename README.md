# 自动化主题摘要页面生成系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)](STATUS)

> 从多源爬取新闻，使用 LLM 生成智能摘要，创建精美的主题汇总页面

## ✨ 功能特性

- 🔍 **多源数据爬取** - BBC, CNN, Reuters + Bing/Google 搜索
- 🤖 **LLM 智能分析** - DeepSeek API 驱动的摘要和实体提取
- 🗄️ **数据库集成** - PostgreSQL 存储，自动回退文件系统
- 🎨 **精美输出** - 响应式 HTML 页面，包含摘要、实体、时间线
- 🔄 **智能去重** - TF-IDF + 余弦相似度算法
- 📊 **完整管道** - 爬取 → 清洗 → 去重 → 提取 → 摘要 → 展示

## 🚀 快速开始（3步）

[安装UV](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)

```bash
# 1. 安装依赖
uv sync

# 2. 配置 API（复制并编辑 .env）
Copy-Item config/.env.example .env
# 在 .env 中添加: DEEPSEEK_API_KEY=your-key

# 3. 运行启动向导
python scripts/start.py
```

**或直接运行:**
```bash
python run.py
```

## 📁 项目结构

```
data-project/
├── src/                          # 源代码模块
│   ├── scraper.py               # 数据爬取模块
│   ├── data_cleaner.py          # 数据清洗模块
│   ├── deduplicator.py          # 去重模块
│   ├── entity_extractor.py      # 实体提取模块
│   ├── summarizer.py            # 摘要生成模块
│   ├── timeline_generator.py    # 时间线生成模块
│   ├── html_generator.py        # HTML生成模块
│   ├── db_utils.py              # 数据库工具
│   └── init_database.py         # 数据库初始化
│
├── scripts/                      # 可执行脚本
│   ├── main.py                  # 主管道程序
│   ├── start.py                 # 启动向导
│   ├── topic_search.py          # 主题搜索（交互式）
│   ├── search_cli.py            # 主题搜索（命令行）
│   ├── test_deepseek.py         # DeepSeek API 测试
│   └── demo.py                  # 演示脚本
│
├── docs/                         # 文档
│   ├── README.md                # 主文档
│   ├── 文档索引.md              # 文档索引
│   ├── 项目状态总结.md          # 项目状态
│   ├── PROJECT_PLAN.md          # 项目规划
│   ├── QUICKSTART_DEEPSEEK.md   # DeepSeek 快速开始
│   ├── DEEPSEEK_INTEGRATION.md  # DeepSeek 集成文档
│   ├── DATABASE_QUICKSTART.md   # 数据库快速开始
│   ├── DATABASE_README.md       # 数据库文档
│   ├── TOPIC_SEARCH_QUICKREF.md # 主题搜索速查
│   └── TOPIC_SEARCH_GUIDE.md    # 主题搜索指南
│
├── config/                       # 配置文件
│   ├── config.json              # 主配置文件
│   └── .env.example             # 环境变量模板
│
├── data/                         # 数据文件
│   ├── raw_articles.json
│   ├── cleaned_articles.json
│   ├── deduplicated_articles.json
│   ├── entities.json
│   ├── summary.json
│   └── timeline.json
│
├── output/                       # 输出文件
│   └── topic_summary.html       # 生成的HTML页面
│
├── logs/                         # 日志文件
│   ├── pipeline.log
│   └── pipeline_with_evaluation.log
│
├── temp/                         # 临时文件
├── tests/                        # 测试文件
│
├── .env                          # 环境变量（不提交到git）
├── .gitignore                    # Git忽略文件
├── requirements.txt              # Python依赖
└── run.py                        # 主启动文件
```

## 快速开始

### 1. 安装依赖

```bash
uv venv & uv sync
```

### 2. 配置环境

复制配置文件：
```bash
Copy-Item config/.env.example .env
```

编辑 `.env` 添加 API 密钥：
```env
DEEPSEEK_API_KEY=your-api-key-here
```

### 3. 运行项目

**方式1: 使用启动向导**
```bash
python scripts/start.py
```

**方式2: 运行完整管道**
```bash
python run.py
```

**方式3: 主题搜索**
```bash
python scripts/topic_search.py
```

## 文档

所有文档位于 `docs/` 目录：
- 📖 [完整文档索引](docs/文档索引.md)
- 🚀 [快速开始指南](docs/QUICKSTART_DEEPSEEK.md)
- 📊 [项目状态总结](docs/项目状态总结.md)

## 功能特性

✨ **核心功能**
- 多源数据爬取
- 智能去重处理
- LLM 实体提取（DeepSeek）
- LLM 摘要生成（DeepSeek）
- 时间线生成
- 精美 HTML 页面

🗄️ **数据库**
- PostgreSQL 集成
- 自动回退到文件存储

🔍 **主题搜索**
- 交互式搜索
- CLI 命令行工具
- Bing/Google News 集成

## 许可证

MIT License

## 作者

6人小组项目 - 2025
