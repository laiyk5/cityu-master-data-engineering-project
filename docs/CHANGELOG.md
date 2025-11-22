# 版本更新日志

## v2.1 - AI智能源推荐版 (2025-11-20)

### 🎉 新增功能

#### AI智能新闻源查找
- 使用 DeepSeek API 智能分析主题特征
- 自动推荐最相关的新闻源（替代固定的 Bing/Google 搜索）
- 支持国际主流媒体和中文权威源
- 每个推荐源包含相关性说明

### 📝 技术细节

#### 新增模块
- `src/intelligent_source_finder.py` - 智能源查找核心模块
  - `IntelligentSourceFinder` 类
  - `find_news_sources()` - 使用 DeepSeek API 查找源
  - `find_specific_urls()` - 查找特定源的 URL
  - 三级回退机制：DeepSeek API → 关键词匹配 → 默认源

#### 修改模块
- `scripts/topic_search.py` - 增强主题搜索功能
  - 新增 `search_with_intelligent_finder()` - AI智能源搜索
  - 新增 `scrape_from_source()` - 从推荐源爬取
  - 重命名 `search_topic_traditional()` - 传统搜索方法
  - 更新 `search_topic()` - 智能路由选择最佳方法

#### 文档更新
- `docs/INTELLIGENT_SOURCE_FINDER.md` - 新功能详细文档
- `docs/README.md` - 更新功能列表
- `docs/TOPIC_SEARCH_GUIDE.md` - 更新使用指南
- `docs/项目状态总结.md` - 更新为 v2.1

### 🧪 测试验证

#### 测试1: AI源推荐
```
主题: artificial intelligence
推荐源:
✓ MIT Technology Review
✓ Wired
✓ The Verge
✓ Reuters Technology
✓ 澎湃新闻科技
状态: 通过 ✅
```

#### 测试2: 完整搜索流程
```
主题: climate change
推荐源:
✓ The Guardian - Environment
✓ BBC News - Climate & Environment
✓ Reuters - Environment
✓ National Geographic - Environment
✓ 新华网 - 环保频道
爬取结果: 2 篇文章
状态: 通过 ✅
```

### 🎯 使用示例

```python
from intelligent_source_finder import IntelligentSourceFinder

finder = IntelligentSourceFinder()
sources = finder.find_news_sources("人工智能")

for source in sources:
    print(f"{source['name']}: {source['url']}")
    print(f"  相关性: {source['relevance']}")
```

### 💡 优势对比

#### v2.0（旧版）
- 固定使用 Bing/Google 搜索
- 所有主题使用相同的搜索引擎
- 结果质量依赖搜索引擎

#### v2.1（新版）
- ✅ AI智能分析主题特征
- ✅ 每个主题推荐最相关的专业源
- ✅ 涵盖国际和中文权威媒体
- ✅ 更高的内容质量和相关性

### 🔄 回退机制

1. **首选**: DeepSeek API智能推荐
2. **备选**: 基于关键词的源匹配
3. **兜底**: 传统 Bing/Google 搜索

---

## v2.0 - DeepSeek集成版 (2025-11-19)

### 新增功能
- DeepSeek API 集成用于摘要生成
- DeepSeek API 集成用于实体提取
- 主题搜索功能（交互式 + CLI）
- PostgreSQL 数据库集成

### 核心模块
- `src/summarizer.py` - LLM摘要生成
- `src/entity_extractor.py` - LLM实体提取
- `scripts/topic_search.py` - 主题搜索
- `src/db_utils.py` - 数据库工具

---

## v1.0 - 基础版本 (2025-11-18)

### 核心功能
- 多源数据爬取
- 数据清洗和验证
- 智能去重（TF-IDF）
- spaCy 实体识别
- 基础摘要生成
- 时间线生成
- HTML 报告生成

### 初始模块
- `src/scraper.py`
- `src/data_cleaner.py`
- `src/deduplicator.py`
- `src/entity_extractor.py`
- `src/summarizer.py`
- `src/timeline_generator.py`
- `src/html_generator.py`
- `scripts/main.py`
