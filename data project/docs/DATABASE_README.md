# 数据库配置说明

## PostgreSQL 数据库集成

本项目已集成PostgreSQL数据库，用于存储爬取的新闻文章数据。

### 数据库配置

数据库连接信息配置在 `.env` 文件中：

```env
DB_HOST=127.0.0.1
DB_NAME=news_db
DB_USER=postgres
DB_PASSWORD=740918
DB_PORT=5432
```

### 数据库表结构

#### articles 表

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | SERIAL | 主键，自增 |
| title | TEXT | 文章标题 |
| content | TEXT | 文章内容 |
| url | TEXT | 文章URL（唯一） |
| source | VARCHAR(255) | 新闻来源 |
| published_date | DATE | 发布日期 |
| scraped_at | TIMESTAMP | 爬取时间 |
| created_at | TIMESTAMP | 创建时间 |

**索引：**
- `idx_articles_source` - 按来源查询优化
- `idx_articles_published_date` - 按日期查询优化
- `idx_articles_created_at` - 按创建时间查询优化

### 安装步骤

#### 1. 安装依赖

```powershell
pip install psycopg2-binary sqlalchemy
```

#### 2. 确保PostgreSQL已安装并运行

检查PostgreSQL服务状态：

```powershell
# Windows
Get-Service postgresql*

# 或者
pg_isready -h 127.0.0.1 -p 5432
```

#### 3. 初始化数据库

运行初始化脚本：

```powershell
python init_database.py
```

这将：
- 创建 `news_db` 数据库（如果不存在）
- 创建 `articles` 表
- 创建必要的索引

### 使用方法

#### 1. 爬取数据并存储到数据库

```powershell
# 直接运行爬虫（会自动保存到数据库和文件）
python scraper.py

# 或运行完整管道
python main.py
```

#### 2. 从数据库读取数据

```python
from db_utils import DatabaseReader

# 创建数据库读取器
reader = DatabaseReader()

# 获取所有文章
articles = reader.get_all_articles()

# 获取最近7天的文章
recent_articles = reader.get_articles_by_date_range(days=7)

# 获取特定来源的文章
bbc_articles = reader.get_articles_by_source('BBC News')

# 获取文章总数
count = reader.get_article_count()

# 关闭连接
reader.close()
```

#### 3. 便捷函数

```python
from db_utils import load_articles_from_database

# 加载所有文章
articles = load_articles_from_database()

# 加载最多100篇文章
articles = load_articles_from_database(limit=100)

# 加载最近7天的文章
articles = load_articles_from_database(days=7)
```

### 数据库查询示例

```powershell
# 使用psql连接
psql -h 127.0.0.1 -U postgres -d news_db

# 查看所有文章
SELECT id, title, source, published_date FROM articles ORDER BY published_date DESC;

# 统计各来源的文章数
SELECT source, COUNT(*) as count FROM articles GROUP BY source;

# 查找最近的文章
SELECT * FROM articles WHERE published_date >= CURRENT_DATE - INTERVAL '7 days';
```

### 测试数据库连接

```powershell
python db_utils.py
```

这将显示：
- 数据库连接状态
- 文章总数
- 所有新闻源
- 最新的5篇文章

### 特性

✅ **自动去重** - URL字段设置为UNIQUE，自动防止重复文章
✅ **更新支持** - 使用 `ON CONFLICT` 更新已存在的文章
✅ **索引优化** - 为常用查询字段创建索引
✅ **日期追踪** - 记录发布时间和爬取时间
✅ **容错机制** - 数据库失败时自动降级到文件存储

### 故障排除

#### 问题1: 数据库连接失败

**解决方案：**
1. 确认PostgreSQL服务已启动
2. 检查 `.env` 文件中的配置是否正确
3. 确认数据库用户有足够权限

```powershell
# 检查服务
Get-Service postgresql*

# 测试连接
psql -h 127.0.0.1 -U postgres
```

#### 问题2: 权限不足

**解决方案：**
```sql
-- 在psql中执行
GRANT ALL PRIVILEGES ON DATABASE news_db TO postgres;
```

#### 问题3: 数据库不存在

**解决方案：**
```powershell
python init_database.py
```

### 数据迁移

#### 从文件导入到数据库

```python
import json
from scraper import DatabaseManager

# 读取JSON文件
with open('data/raw_articles.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)

# 导入到数据库
db = DatabaseManager()
count = db.insert_articles_batch(articles)
print(f"导入了 {count} 篇文章")
db.close()
```

#### 从数据库导出到文件

```python
from db_utils import DatabaseReader
import json

reader = DatabaseReader()
articles = reader.get_all_articles()

with open('export.json', 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

reader.close()
print(f"导出了 {len(articles)} 篇文章")
```

### 性能优化建议

1. **定期清理旧数据**
```sql
DELETE FROM articles WHERE scraped_at < CURRENT_DATE - INTERVAL '30 days';
```

2. **分析查询性能**
```sql
EXPLAIN ANALYZE SELECT * FROM articles WHERE source = 'BBC News';
```

3. **重建索引**
```sql
REINDEX TABLE articles;
```

### 备份与恢复

#### 备份数据库

```powershell
pg_dump -h 127.0.0.1 -U postgres -d news_db > backup.sql
```

#### 恢复数据库

```powershell
psql -h 127.0.0.1 -U postgres -d news_db < backup.sql
```

---

更多信息请参考 PostgreSQL 官方文档：https://www.postgresql.org/docs/
