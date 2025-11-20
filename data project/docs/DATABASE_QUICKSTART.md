# 数据库集成快速参考

## 🚀 快速开始

### 1. 安装数据库依赖
```powershell
pip install psycopg2-binary sqlalchemy python-dotenv
```

### 2. 初始化数据库
```powershell
python init_database.py
```

### 3. 运行爬虫（自动存储到数据库）
```powershell
python scraper.py
```

### 4. 查看数据库数据
```powershell
python db_utils.py
```

## 📊 数据库结构

**数据库名:** news_db

**表名:** articles

| 字段 | 类型 | 说明 |
|-----|------|-----|
| id | SERIAL | 主键 |
| title | TEXT | 标题 |
| content | TEXT | 内容 |
| url | TEXT (UNIQUE) | 链接 |
| source | VARCHAR(255) | 来源 |
| published_date | DATE | 发布日期 |
| scraped_at | TIMESTAMP | 爬取时间 |
| created_at | TIMESTAMP | 创建时间 |

## 💻 使用示例

### Python代码

```python
from db_utils import DatabaseReader, load_articles_from_database

# 方法1: 使用DatabaseReader
reader = DatabaseReader()
articles = reader.get_all_articles()
count = reader.get_article_count()
sources = reader.get_sources()
reader.close()

# 方法2: 使用便捷函数
articles = load_articles_from_database(limit=100)
recent = load_articles_from_database(days=7)
```

### SQL查询

```sql
-- 连接数据库
psql -h 127.0.0.1 -U postgres -d news_db

-- 查看所有文章
SELECT * FROM articles ORDER BY published_date DESC;

-- 统计来源
SELECT source, COUNT(*) FROM articles GROUP BY source;

-- 最近文章
SELECT * FROM articles 
WHERE published_date >= CURRENT_DATE - INTERVAL '7 days';
```

## 🔧 常用命令

| 命令 | 说明 |
|-----|------|
| `python init_database.py` | 初始化数据库 |
| `python scraper.py` | 爬取并存储数据 |
| `python db_utils.py` | 查看数据库统计 |
| `python main.py` | 运行完整管道 |

## ⚙️ 配置文件

**.env 文件配置:**
```env
DB_HOST=127.0.0.1
DB_NAME=news_db
DB_USER=postgres
DB_PASSWORD=740918
DB_PORT=5432
```

## 🎯 特性

✅ 自动去重（URL唯一）
✅ 自动更新已存在的文章
✅ 索引优化查询性能
✅ 容错机制（数据库失败降级到文件）
✅ 批量插入支持
✅ 日期范围查询
✅ 按来源筛选

## 📝 注意事项

1. 确保PostgreSQL服务已启动
2. 数据库配置正确（.env文件）
3. 用户有足够的权限
4. 首次使用前运行 `init_database.py`

## 🔍 故障排除

**连接失败？**
- 检查PostgreSQL服务状态
- 验证.env配置
- 测试: `psql -h 127.0.0.1 -U postgres`

**权限问题？**
```sql
GRANT ALL PRIVILEGES ON DATABASE news_db TO postgres;
```

**重置数据库？**
```sql
DROP DATABASE news_db;
```
然后重新运行 `python init_database.py`

---

详细文档请参考 `DATABASE_README.md`
