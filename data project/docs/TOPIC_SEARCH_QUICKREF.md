# 主题搜索快速参考

## 🚀 三种使用方式

### 1. 命令行模式（推荐）

```powershell
# 基本用法
python search_cli.py --topic "人工智能" --max 20

# 保存到数据库
python search_cli.py -t "AI Technology" -m 15 -s both

# 搜索并继续处理
python search_cli.py -t "Climate Change" --continue
```

### 2. 交互式模式

```powershell
python topic_search.py
```

然后按照提示输入。

### 3. 代码中使用

```python
from topic_search import TopicScraper

scraper = TopicScraper(topic="人工智能")
articles = scraper.search_topic(max_results=20)
scraper.save_to_file()
scraper.save_to_database()
scraper.close()
```

## 📋 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|-----|------|------|--------|
| `--topic` | `-t` | 搜索主题（必需） | - |
| `--max` | `-m` | 最大文章数 | 20 |
| `--save` | `-s` | 保存选项 | file |
| `--continue` | `-c` | 继续处理 | False |
| `--output` | `-o` | 输出路径 | 自动 |

### 保存选项

- `file` - 仅保存到文件
- `db` - 仅保存到数据库
- `both` - 保存到文件和数据库
- `none` - 不保存

## 💡 使用示例

### 示例1: 快速搜索

```powershell
python search_cli.py -t "人工智能" -m 10
```

### 示例2: 搜索并保存到数据库

```powershell
python search_cli.py -t "区块链" -m 20 -s both
```

### 示例3: 搜索并生成摘要

```powershell
# 步骤1: 搜索
python search_cli.py -t "气候变化" -m 30 --continue

# 步骤2: 生成摘要
python main.py
```

### 示例4: 批量搜索

```powershell
# 搜索多个主题
python search_cli.py -t "人工智能" -s db
python search_cli.py -t "区块链" -s db
python search_cli.py -t "新能源" -s db
```

## 📊 输出

### 文件输出

```
data/topic_主题名_时间戳.json
```

例如：`data/topic_Artificial_Intelligence_20251120_113043.json`

### 数据库输出

存储到 PostgreSQL 的 `articles` 表

### 屏幕输出

```
======================================================================
主题新闻搜索工具
======================================================================
搜索主题: Artificial Intelligence
文章数量: 10

✓ 找到 5 篇相关文章

文章预览（前5篇）:
1. [Bing News] 标题...
2. [Bing News] 标题...
...

✓ 已保存到文件: data/topic_xxx.json
✓ 已保存到数据库: 5 篇文章
✓ 搜索完成！
```

## 🔗 与其他模块集成

### 完整工作流

```powershell
# 1. 搜索主题
python search_cli.py -t "AI" -m 30 --continue

# 2. 处理数据
python main.py

# 3. 查看结果
start output/topic_summary.html
```

### 只查看数据库

```powershell
python db_utils.py
```

## ⚙️ 配置

修改 `.env` 文件设置数据库连接：

```env
DB_HOST=127.0.0.1
DB_NAME=news_db
DB_USER=postgres
DB_PASSWORD=740918
DB_PORT=5432
```

## 🎯 支持的主题示例

中文：
- 人工智能
- 区块链技术
- 气候变化
- 新能源汽车
- 太空探索
- 量子计算

英文：
- Artificial Intelligence
- Climate Change
- Blockchain Technology
- Space Exploration
- Renewable Energy
- Quantum Computing

## 📝 注意事项

1. **首次使用** - 确保已初始化数据库：`python init_database.py`
2. **搜索限制** - 某些搜索源可能有频率限制
3. **中文支持** - 完全支持中文主题搜索
4. **自动去重** - 基于URL自动去除重复文章
5. **延迟设置** - 自动添加延迟避免被封禁

## 🆘 帮助

```powershell
# 查看帮助
python search_cli.py --help

# 查看版本
python search_cli.py --version
```

---

完整文档请参考 `TOPIC_SEARCH_GUIDE.md`
