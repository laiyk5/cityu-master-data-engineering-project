# 自动化主题摘要页面生成系统

## 项目简介

这是一个自动化数据管道项目，能够从多个新闻源爬取特定主题的文章，进行数据清洗、去重、实体提取和摘要生成，最终生成一个美观的HTML摘要页面。

## 功能特点

✨ **多源数据爬取** - 从多个新闻网站自动抓取文章
🔍 **智能主题搜索** - 支持手动输入特定事件或主题关键词，使用AI智能查找最相关的新闻源
🤖 **AI新闻源推荐** - 使用DeepSeek API自动分析主题并推荐最佳新闻源
🗄️ **数据库集成** - PostgreSQL数据库存储，支持高效查询
🧹 **智能数据清洗** - 去除HTML标签、广告和无用内容
🔄 **智能去重** - 基于内容相似度检测并合并重复文章
👥 **实体识别** - 自动提取人物、组织、地点等关键实体
📝 **AI摘要生成** - 使用LLM生成高质量摘要
📅 **时间线展示** - 按时间顺序组织事件
🎨 **精美HTML页面** - 生成响应式的摘要展示页面

## 项目结构

```
data-project/
├── main.py                    # 主管道程序
├── scraper.py                 # 数据爬取模块
├── data_cleaner.py            # 数据清洗模块
├── deduplicator.py            # 去重模块
├── entity_extractor.py        # 实体提取模块
├── summarizer.py              # 摘要生成模块
├── timeline_generator.py      # 时间线生成模块
├── html_generator.py          # HTML生成模块
├── config.json                # 配置文件
├── requirements.txt           # 依赖包列表
├── .env.example              # 环境变量示例
├── PROJECT_PLAN.md           # 项目分工文档
└── README.md                 # 本文件
```

## 安装指南

### 1. 克隆或下载项目

```bash
cd "c:\Users\17714\Desktop\data project"
```

### 2. 创建虚拟环境（推荐）

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```powershell
pip install -r requirements.txt
```

### 4. 下载spaCy模型

```powershell
python -m spacy download en_core_web_sm
```

### 5. 配置数据库（可选）

安装 PostgreSQL 并创建数据库（详见 DATABASE_README.md）：

```bash
python init_database.py
```

### 6. 配置 API 密钥

复制 `.env.example` 为 `.env`：

```powershell
Copy-Item .env.example .env
```

编辑 `.env` 文件，填入配置：

```env
# DeepSeek API（推荐，性价比高）
DEEPSEEK_API_KEY=your-deepseek-api-key

# 或者使用 OpenAI
OPENAI_API_KEY=your_openai_api_key

# 或者使用 Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key

# PostgreSQL 数据库配置
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=news_db
DB_USER=postgres
DB_PASSWORD=your_password
```

在 `config.json` 中选择 LLM 提供商：

```json
{
  "summarization": {
    "llm_provider": "deepseek",  // 可选: deepseek, openai, anthropic
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com"
  }
}
```

## 使用方法

### 方式1: 主题搜索（推荐）

**交互式搜索特定主题的新闻：**

```powershell
python topic_search.py
```

然后按照提示：
1. 输入您想搜索的主题（如：人工智能、气候变化等）
2. 设置搜索数量
3. 选择保存选项
4. 可选：继续处理数据生成摘要

### 方式2: 运行完整管道

**自动从配置的新闻源爬取：**

```powershell
python main.py
```

这将执行所有步骤并生成最终的HTML页面。

### 方式3: 单独运行各模块

```powershell
# 固定源爬取
python scraper.py

# 主题搜索
python topic_search.py

# 查看数据库数据
python db_utils.py

# 只清洗数据
python data_cleaner.py

# 只去重
python deduplicator.py

# 只提取实体
python entity_extractor.py

# 只生成摘要
python summarizer.py

# 只生成时间线
python timeline_generator.py

# 只生成HTML
python html_generator.py
```

## 配置说明

编辑 `config.json` 文件可以自定义：

- **新闻源列表** - 添加或删除新闻网站
- **爬取数量** - 每个源抓取的文章数量
- **去重阈值** - 相似度阈值（0-1）
- **实体提取设置** - NLP模型和最小频率
- **LLM设置** - API提供商、模型、参数
- **输出路径** - 数据和HTML文件保存位置

## 输出文件

运行完成后，会生成以下文件：

```
data/
├── raw_articles.json          # 原始爬取的文章
├── cleaned_articles.json      # 清洗后的文章
├── deduplicated_articles.json # 去重后的文章
├── entities.json              # 提取的实体
├── summary.json               # 生成的摘要
└── timeline.json              # 时间线数据

output/
└── topic_summary.html         # 最终生成的HTML页面
```

## 技术栈

- **Python 3.8+**
- **BeautifulSoup4** - 网页解析
- **Requests** - HTTP请求
- **Pandas** - 数据处理
- **PostgreSQL** - 数据库存储
- **spaCy** - 自然语言处理（可选）
- **scikit-learn** - 相似度计算
- **DeepSeek/OpenAI/Anthropic API** - LLM 摘要生成
- **Jinja2** - HTML模板

## 常见问题

### Q: 没有API密钥怎么办？

A: 系统会自动使用备用方法生成简单摘要，不影响其他功能。

### Q: 推荐使用哪个 LLM 提供商？

A: 推荐使用 **DeepSeek API**：
- ✅ 性价比最高（约 0.14 元/百万 tokens）
- ✅ 支持中英文
- ✅ API 兼容 OpenAI 格式
- ✅ 响应速度快

详见 `DEEPSEEK_INTEGRATION.md` 了解配置详情。

### Q: 爬虫无法访问某些网站？

A: 某些网站有反爬虫措施，可以：
- 调整请求延迟
- 使用代理
- 更换User-Agent
- 使用 Selenium（需额外配置）
- 使用主题搜索功能通过搜索引擎获取数据

### Q: spaCy模型下载失败？

A: spaCy 是可选的：
- 系统已启用 LLM 实体提取（更准确）
- 如需要 spaCy：`python -m spacy download en_core_web_sm`
- 或使用基于规则的简单提取

### Q: 内存不足？

A: 可以在配置文件中减少 `max_articles_per_source`。

### Q: 数据库连接失败？

A: 系统会自动回退到文件存储，不影响功能。详见 `DATABASE_README.md`。

## 6人小组分工

详见 `PROJECT_PLAN.md` 文件，包含完整的任务分配和时间规划。

## 示例输出

生成的HTML页面包含：
- 📊 统计信息卡片
- 📋 主要摘要
- 👥 关键实体（人物、组织、地点）
- 📅 事件时间线
- 📰 原始文章链接

## 扩展功能

可选的高级功能：
- 情感分析
- 主题建模
- 关键词云
- 数据可视化图表
- 定时自动更新
- Web服务部署

## 许可证

MIT License

## 作者

6人小组项目

## 更新日志

### v1.2.0 (2025-11-20)
- 🚀 集成 DeepSeek API 用于摘要生成和实体提取
- 📝 添加 LLM 实体提取功能
- 📄 新增 DEEPSEEK_INTEGRATION.md 文档
- 🔧 改进 JSON 解析和错误处理

### v1.1.0 (2025-11-19)
- 🔍 添加主题搜索功能
- 🗄️ 集成 PostgreSQL 数据库
- 📚 添加数据库相关文档
- 🛠️ 新增 CLI 搜索工具

### v1.0.0 (2025-11-18)
- ✨ 初始版本发布
- ✅ 实现全部核心功能
- 📚 完整文档

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目仓库: [GitHub链接]
- 邮箱: [联系邮箱]

---

**祝使用愉快！** 🎉
