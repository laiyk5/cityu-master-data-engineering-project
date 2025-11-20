# 主题搜索功能使用指南

## 🔍 智能主题搜索功能

支持手动输入特定事件或主题关键词，使用 **DeepSeek AI** 智能分析主题并自动推荐最相关的新闻源，然后爬取相关新闻。

### ✨ 核心优势

- 🤖 **AI驱动** - 使用DeepSeek API智能分析主题特征
- 🎯 **精准推荐** - 自动推荐最相关的新闻源（非固定搜索引擎）
- 🌐 **多源覆盖** - 支持国际主流媒体和中文权威源
- 📊 **质量保证** - 推荐的源都包含相关性说明

## 快速开始

### 运行主题搜索

```powershell
python topic_search.py
```

### 交互式界面

程序会引导您完成以下步骤：

#### 1. 输入搜索主题

```
🔍 搜索主题: 人工智能
```

**AI自动分析主题**：输入后，DeepSeek API 会自动：
- 分析主题的核心概念和关键特征
- 识别最相关的新闻源类型
- 推荐5个最佳新闻源（包括国际和中文媒体）
- 为每个源提供相关性说明

支持的主题示例：
- 人工智能 → 推荐：MIT Tech Review, Wired, The Verge等
- Climate Change → 推荐：The Guardian Environment, BBC Climate等
- 比特币 → 推荐：CoinDesk, Bloomberg Crypto等
- 太空探索 → 推荐：NASA News, Space.com等
- 新能源汽车 → 推荐：Electrek, CleanTechnica等
- 任何您感兴趣的主题

#### 2. 设置搜索数量

```
📊 需要搜索多少篇文章？(默认20): 30
```

建议：10-50篇文章

#### 3. 选择是否爬取详细内容

```
📰 是否爬取文章详细内容？(y/n, 默认n): n
```

注意：爬取详细内容耗时较长

#### 4. 选择保存选项

```
💾 保存选项:
  1. 仅保存到文件
  2. 保存到文件和数据库
  3. 不保存

请选择 (1/2/3, 默认1): 2
```

#### 5. 可选：继续处理数据

```
是否继续处理这些数据（生成摘要、实体提取等）？(y/n): y
```

选择 y 后可以运行 `python main.py` 继续处理

## 使用示例

### 示例1: 搜索"人工智能"主题（AI智能推荐源）

```powershell
python topic_search.py

# 输入
🔍 搜索主题: 人工智能
📊 需要搜索多少篇文章？: 20
💾 保存选项: 2

# AI自动推荐新闻源
✓ 推荐源: MIT Technology Review - AI与机器学习深度报道
  URL: https://www.technologyreview.com
✓ 推荐源: Wired - 前沿科技趋势分析
  URL: https://www.wired.com
✓ 推荐源: The Verge - 科技产品与AI应用
  URL: https://www.theverge.com
✓ 推荐源: Reuters Technology - 全球AI产业新闻
  URL: https://www.reuters.com/technology
✓ 推荐源: 澎湃新闻科技 - 中国AI政策与产业
  URL: https://www.thepaper.cn/channel_25951

# 输出
✓ 找到 20 篇相关文章
✓ 已保存到文件: data/topic_人工智能_20251120_153045.json
✓ 已保存到数据库: 20 篇文章
```

### 示例2: 搜索并继续处理

```powershell
python topic_search.py

# 输入主题
🔍 搜索主题: Climate Change

# ... 搜索完成后
是否继续处理这些数据？: y

# 然后运行
python main.py
```

## 搜索源

目前支持以下搜索源：

1. **Bing News** - 必应新闻搜索
2. **Google News** - 谷歌新闻搜索

## 输出文件

### 文件格式

保存的JSON文件包含：

```json
{
  "topic": "人工智能",
  "article_count": 20,
  "scraped_at": "2025-11-20T15:30:45",
  "articles": [
    {
      "title": "文章标题",
      "url": "文章链接",
      "source": "新闻来源",
      "published_date": "2025-11-20",
      "content": "文章内容",
      "topic": "人工智能",
      "scraped_at": "2025-11-20T15:30:45"
    }
  ]
}
```

### 文件位置

```
data/topic_主题名_日期时间.json
```

例如：
- `data/topic_人工智能_20251120_153045.json`
- `data/topic_AI_Technology_20251120_154030.json`

## 数据库存储

选择保存到数据库时，文章会存储到PostgreSQL的`articles`表中，包含`topic`字段标记主题。

### 查询特定主题的文章

```python
from db_utils import DatabaseReader

reader = DatabaseReader()
# 注意：需要添加按topic查询的方法
articles = reader.get_all_articles()
reader.close()
```

## 与主管道集成

### 搜索后继续处理

1. 运行主题搜索：
```powershell
python topic_search.py
```

2. 选择"是"继续处理

3. 运行主管道：
```powershell
python main.py
```

主管道会：
- 读取搜索到的文章
- 清洗和去重
- 提取实体
- 生成摘要和时间线
- 生成HTML页面

## 高级用法

### 在代码中使用

```python
from topic_search import TopicScraper

# 创建搜索器
scraper = TopicScraper(topic="人工智能")

# 搜索文章
articles = scraper.search_topic(max_results=20)

# 保存到文件
file_path = scraper.save_to_file()

# 保存到数据库
db_count = scraper.save_to_database()

# 关闭
scraper.close()

print(f"找到 {len(articles)} 篇文章")
print(f"保存到: {file_path}")
```

### 批量搜索多个主题

```python
topics = ["人工智能", "区块链", "新能源"]

for topic in topics:
    scraper = TopicScraper(topic=topic)
    articles = scraper.search_topic(max_results=10)
    scraper.save_to_file()
    scraper.save_to_database()
    scraper.close()
    print(f"完成主题: {topic}")
```

## 注意事项

1. **搜索限制** - 某些搜索引擎可能有访问频率限制
2. **内容爬取** - 爬取详细内容会大幅增加时间
3. **去重** - 自动基于URL去重
4. **语言** - 支持中英文主题搜索
5. **延迟** - 自动添加请求延迟避免被封禁

## 故障排除

### 问题1: 搜索无结果

**原因：**
- 主题关键词太具体
- 网络连接问题
- 搜索源不可用

**解决：**
- 使用更通用的关键词
- 检查网络连接
- 尝试不同的主题

### 问题2: 爬取速度慢

**原因：**
- 选择了爬取详细内容
- 网络速度慢
- 文章数量太多

**解决：**
- 减少搜索数量
- 不爬取详细内容
- 分批搜索

### 问题3: 数据库保存失败

**原因：**
- 数据库未初始化
- 连接配置错误

**解决：**
```powershell
python init_database.py
```

## 完整工作流程

```
1. 主题搜索
   ↓
   python topic_search.py
   输入主题 → 搜索文章 → 保存数据
   ↓
2. 数据处理
   ↓
   python main.py
   清洗 → 去重 → 提取实体 → 生成摘要
   ↓
3. 查看结果
   ↓
   打开 output/topic_summary.html
```

---

更多信息请参考 `README.md`
