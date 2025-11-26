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
pip install uv
uv sync

# 2. 配置 API（复制并编辑 .env）
Copy-Item config/.env.example .env
# 在 .env 中添加: DEEPSEEK_API_KEY=your-key
```

**或直接运行:**
```bash
python run.py
```

## 📁 项目结构（仓库概览）

```
cityu-master-data-engineering-project-main/
├── pyproject.toml               # 项目元信息与依赖（如果使用 Poetry/PEP 517）
├── README.md                    # 项目说明（当前文件）
├── LICENSE                      # 许可（如存在）
├── .env.example                 # 示例环境变量
├── config/                      # 配置（JSON、站点地图、RSS 等）
│   ├── config.json
│   ├── rss/
│   │   ├── HongKong SAR.opml
│   │   └── United States.opml
│   └── sitemaps/
│       ├── baidu_news.sitemap.json
│       └── google_news.sitemap.json
├── data/                        # 数据目录（爬取、清洗、去重、实体、摘要等中间/输出文件）
├── examples/                    # 示例主题与数据（供查看/演示）
│   ├── NationalGames/
│   ├── NvidiaH20GPU/
│   └── Trump&Epstein/
├── output/                      # 最终输出（HTML 页面、报告）
├── scripts/                     # 可直接运行的脚本/工具
│   ├── main.py                  # 主管道（执行爬取到页面生成）
│   ├── start.py                 # 运行/配置向导脚本
│   ├── topic_search.py          # 交互式主题搜索工具
│   ├── search_cli.py            # 命令行主题搜索工具
│   ├── test_deepseek.py         # DeepSeek API 测试脚本
│   ├── web_app.py               # 本地化前端/演示页面入口
│   └── score.py                 # 评分/评估相关脚本
├── src/                         # 源码包
│   └── atss/                    # 应用核心模块
│       ├── __init__.py
│       ├── ai.py                           # 
│       ├── config.py                       # 
│       ├── data_cleaner.py                 # 数据清洗模块
│       ├── db_utils.py                     # 数据库工具
│       ├── deduplicator.py                 # 去重模块
│       ├── entity_extractor.py             # 实体提取模块
│       ├── html_generator.py               # HTML生成模块
│       ├── init_database.py                # 数据库初始化
│       ├── intelligent_source_finder.py    # 
│       ├── news_source.py                  # 
│       ├── path_config.py                  # 
│       ├── scraper.py                      # 数据爬取模块
│       ├── summarizer.py                   # 摘要生成模块
│       ├── timeline_generator.py           # 时间线生成模块
│       └── search_engine/                  # 
│           ├── fts.py
│           └── webscraper.py
├── static/                      # 静态资源（页面样式/脚本）
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── col_resize.js
├── templates/                   # HTML 模板
│   └── articles.html
└── uv.lock                      # (uv 环境锁文件，如果使用 uv) 
```

## 快速开始

### 1. 安装依赖

```bash
pip install uv
uv venv & uv sync
```

### 2. 配置环境

复制配置文件：
```bash
Copy-Item .env.example .env
```

编辑 `.env` 添加 API 密钥：
```env
DEEPSEEK_API_KEY=your-api-key-here
```

### 3. 运行项目

**运行完整管道**
```bash
python scripts/main.py
```
**虚拟环境运行**
```bash
uv run scripts/main.py
```

‼️ATTENTION: 请使用英文字符搜索，暂时不支持中文字符搜索

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
