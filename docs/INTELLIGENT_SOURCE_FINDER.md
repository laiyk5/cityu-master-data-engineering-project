# 智能新闻源查找功能

## 🤖 功能简介

项目现在使用 **DeepSeek API** 智能查找与主题相关的新闻源，而不是固定使用 Bing/Google 搜索。

### ✨ 主要特点

1. **智能推荐** - 根据主题自动推荐最相关的权威新闻网站
2. **多样化来源** - 覆盖国内外主流媒体
3. **主题相关** - 精准匹配主题特点（科技、商业、国际等）
4. **自动回退** - API 失败时自动使用传统搜索方法

## 🚀 使用方法

### 方式 1: 交互式搜索（推荐）

```bash
python scripts/topic_search.py
```

输入主题后，系统会：
1. 使用 DeepSeek API 查找 5 个最相关的新闻源
2. 显示推荐的新闻源和理由
3. 自动从这些源爬取相关新闻

### 方式 2: 命令行搜索

```bash
python scripts/search_cli.py --topic "人工智能" --max 20
```

### 方式 3: 启动向导

```bash
python scripts/start.py
# 选择 "2. 主题搜索"
```

## 📊 示例

### 输入主题: "artificial intelligence"

**DeepSeek 推荐的新闻源:**

1. **MIT Technology Review**
   - URL: https://www.technologyreview.com
   - 说明: 深度报道AI技术发展与伦理

2. **Wired**
   - URL: https://www.wired.com
   - 说明: 科技前沿媒体，专注AI创新应用

3. **The Verge**
   - URL: https://www.theverge.com
   - 说明: 报道AI产品与行业动态

4. **Reuters Technology**
   - URL: https://www.reuters.com/technology
   - 说明: 权威国际媒体AI政策与商业新闻

5. **澎湃新闻科技**
   - URL: https://www.thepaper.cn/channel_25951
   - 说明: 中国主流媒体AI政策与产业报道

## 🔧 技术实现

### 核心模块

**`src/intelligent_source_finder.py`**
- 使用 DeepSeek API 进行智能推荐
- 支持主题关键词分析
- 提供备用新闻源列表

### 工作流程

```
1. 用户输入主题
   ↓
2. DeepSeek API 分析主题特点
   ↓
3. 推荐 5 个最相关的新闻源
   ↓
4. 从每个源爬取文章
   ↓
5. 汇总、去重、生成摘要
```

## ⚙️ 配置

### 环境变量 (.env)

```env
DEEPSEEK_API_KEY=your-api-key-here
```

### API 参数

在 `src/intelligent_source_finder.py` 中可调整：

```python
# 推荐源数量
max_sources = 5

# 温度参数（越低越确定）
temperature = 0.3

# 最大 tokens
max_tokens = 1500
```

## 🆚 对比传统方法

| 特性 | 智能查找 (DeepSeek) | 传统方法 (Bing/Google) |
|------|---------------------|------------------------|
| 来源相关性 | ⭐⭐⭐⭐⭐ 精准匹配 | ⭐⭐⭐ 通用搜索 |
| 权威性 | ⭐⭐⭐⭐⭐ 主流媒体 | ⭐⭐⭐⭐ 混合结果 |
| 多样性 | ⭐⭐⭐⭐⭐ 国内外覆盖 | ⭐⭐⭐ 主要英文 |
| 速度 | ⭐⭐⭐⭐ 快速 API | ⭐⭐⭐ 依赖爬虫 |
| 灵活性 | ⭐⭐⭐⭐⭐ 动态适应 | ⭐⭐ 固定逻辑 |

## 🔄 回退机制

如果 DeepSeek API 失败，系统会自动：

1. **智能回退** - 根据主题关键词选择预设的备用源
2. **传统搜索** - 使用 Bing/Google News 搜索
3. **保证可用** - 确保功能始终可用

### 备用源分类

- **科技类**: TechCrunch, The Verge, Wired
- **商业类**: Bloomberg, Financial Times, CNBC
- **国际类**: BBC, Reuters, Al Jazeera
- **通用类**: CNN, The Guardian, AP News

## 💰 成本估算

基于 DeepSeek 定价：

- **单次查询**: ~500 tokens
- **成本**: < ¥0.001 / 次
- **每月 1000 次**: < ¥1

非常经济实惠！

## 📝 测试

### 快速测试

```bash
python test_intelligent_finder.py
```

### 测试不同主题

```python
from intelligent_source_finder import IntelligentSourceFinder

finder = IntelligentSourceFinder()

# 测试科技主题
sources = finder.find_news_sources("artificial intelligence", 5)

# 测试商业主题
sources = finder.find_news_sources("stock market", 5)

# 测试国际主题
sources = finder.find_news_sources("Ukraine war", 5)
```

## 🎯 最佳实践

1. **清晰主题** - 使用具体的主题关键词
2. **合理数量** - 推荐 3-5 个新闻源最佳
3. **验证结果** - 检查推荐源是否真实可访问
4. **监控成本** - 定期查看 API 使用情况

## 🐛 故障排查

### 问题 1: API 密钥错误

```
ValueError: 未找到 DEEPSEEK_API_KEY
```

**解决**: 在 .env 文件中添加 API 密钥

### 问题 2: JSON 解析失败

```
ERROR - 使用 DeepSeek API 查找新闻源失败
```

**解决**: 系统会自动回退到备用源，功能继续可用

### 问题 3: 推荐源无法访问

**解决**: 系统会跳过无法访问的源，继续处理其他源

## 📚 相关文档

- **DeepSeek API 文档**: [docs/DEEPSEEK_INTEGRATION.md](../docs/DEEPSEEK_INTEGRATION.md)
- **主题搜索指南**: [docs/TOPIC_SEARCH_GUIDE.md](../docs/TOPIC_SEARCH_GUIDE.md)
- **快速参考**: [docs/TOPIC_SEARCH_QUICKREF.md](../docs/TOPIC_SEARCH_QUICKREF.md)

## 🎉 总结

使用 DeepSeek API 进行智能新闻源查找：

✅ **更精准** - 根据主题推荐最相关的源  
✅ **更权威** - 推荐主流媒体  
✅ **更灵活** - 动态适应不同主题  
✅ **更经济** - 成本极低  
✅ **更可靠** - 自动回退机制  

---

**更新日期**: 2025-11-20  
**功能版本**: 2.1 (智能源查找)
