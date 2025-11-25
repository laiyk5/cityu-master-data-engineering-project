"""
数据库工具 - 从数据库读取数据
功能：提供从PostgreSQL数据库读取文章数据的工具函数
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict
from datetime import datetime, timedelta

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_db_config() -> Dict:
    """获取数据库配置"""
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "database": os.getenv("DB_NAME", "news_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "admin"),
        "port": os.getenv("DB_PORT", "5433"),
    }

def _psycopg2_connect(db_config):
    """使用psycopg2连接数据库
    
    This method is intended to avoid type inference issues with psycopg2.connect
    """
    return psycopg2.connect(
        host=db_config.get("host"),
        database=db_config.get("database"),
        user=db_config.get("user"),
        password=db_config.get("password"),
        port=db_config.get("port"),
    )

class NewsDatabase:
    """This class manages the PostgreSQL database connection and setup.
    it maintain a single connection instance for reuse.
    """
    _conn = None
    _db_config = _get_db_config()
    _db_name = _db_config.get("database")
    _admin_conn = None

    @classmethod
    def get_connection(cls, reset=False):
        if reset:
            cls.close_connection()
            cls._drop_database()
        if cls._conn is None:
            if not cls._if_database_exists():
                cls._create_database()
            cls._connect()
        if cls._conn is None:
            raise Exception("✗ Database connection is not established.")
        return cls._conn
    
    @classmethod
    def get_admin_connection(cls):
        if cls._admin_conn is None:
            try:
                cls._admin_conn = _psycopg2_connect(
                    cls._db_config | {"database": "postgres"}
                )
                logger.info("Successfully connected to the admin database.")
            except Exception as e:
                logger.error(f"Failed to connect to the admin database: {e}")
                raise
        return cls._admin_conn

    @classmethod
    def close_connection(cls):
        if cls._conn:
            cls._conn.close()
            cls._conn = None

    @classmethod
    def close_admin_connection(cls):
        if cls._admin_conn:
            cls._admin_conn.close()
            cls._admin_conn = None

    @classmethod
    def _connect(cls):
        """Connect to the PostgreSQL database, creating it if it doesn't exist."""

        cls._db_config = _get_db_config()
        cls._db_name = cls._db_config.pop("database")

        try:
            cls._conn = _psycopg2_connect(cls._db_config | {"database": cls._db_name})
            logger.info("Successfully connected to the database.")
        except Exception as e:
            logger.error(f"Failed to connect to the database: {e}")
            raise

    @classmethod
    def _if_database_exists(cls):
        try:
            # 连接到默认的postgres数据库
            conn = _psycopg2_connect(cls._db_config | {"database": "postgres"})
            cursor = conn.cursor()

            # 检查数据库是否存在
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (cls._db_name,)
            )
            exists = cursor.fetchone() is not None

            cursor.close()
            conn.close()

            return exists

        except Exception as e:
            logger.error(f"✗ Failed to check if database exists: {e}")
            raise

    @classmethod
    def _create_database(cls):
        try:
            # 连接到默认的postgres数据库
            conn = cls.get_admin_connection()
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE {cls._db_name}")
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"✗ Failed to create database: {e}")
            raise

    @classmethod
    def _drop_database(cls):
        try:
            # 连接到默认的postgres数据库
            conn = cls.get_admin_connection()
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS {cls._db_name}")
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"✗ Failed to drop database: {e}")
            raise

class ArticleStorage:
    """数据库读取类"""

    def __init__(self, reset=False):
        self._create_tables()
        self._conn = NewsDatabase.get_connection(reset=reset)

    def _create_tables(self):
        """创建表结构"""
        try:
            conn = NewsDatabase.get_admin_connection()
            cursor = conn.cursor()

            # 创建文章表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS articles (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT,
                    url TEXT UNIQUE NOT NULL,
                    source VARCHAR(255),
                    published_date DATE,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            print("✓ 表 articles 创建成功")

            # 创建索引
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_articles_source 
                ON articles(source)
            """
            )
            print("✓ 索引 idx_articles_source 创建成功")

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_articles_published_date 
                ON articles(published_date)
            """
            )
            print("✓ 索引 idx_articles_published_date 创建成功")

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_articles_created_at 
                ON articles(created_at)
            """
            )
            print("✓ 索引 idx_articles_created_at 创建成功")

            conn.commit()
            cursor.close()
            NewsDatabase.close_admin_connection()

            print("\n✓ 所有表和索引创建完成")

        except Exception as e:
            print(f"✗ 创建表失败: {e}")
            raise

    def _insert_article(self, article: Dict) -> bool:
        """插入单篇文章到数据库"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO articles (title, content, url, source, published_date, scraped_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE SET
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    source = EXCLUDED.source,
                    published_date = EXCLUDED.published_date,
                    scraped_at = EXCLUDED.scraped_at
            """, (
                article['title'],
                article['content'],
                article['url'],
                article['source'],
                article['published_date'],
                article['scraped_at']
            ))
            self._conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"插入文章失败: {e}")
            self._conn.rollback()
            return False
    
    def insert_articles_batch(self, articles: List[Dict]) -> int:
        """批量插入文章到数据库"""
        success_count = 0
        for article in articles:
            if self._insert_article(article):
                success_count += 1
        logger.info(f"成功插入 {success_count}/{len(articles)} 篇文章到数据库")
        return success_count

    def get_all_articles(self, limit: int | None = None) -> List[Dict]:
        """获取所有文章"""
        try:
            cursor = self._conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT id, title, content, url, source, 
                       published_date::text as published_date, 
                       scraped_at::text as scraped_at
                FROM articles
                ORDER BY published_date DESC, created_at DESC
            """
            if limit is not None:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            articles = cursor.fetchall()
            cursor.close()
            logger.info(f"从数据库获取了 {len(articles)} 篇文章")
            return [dict(article) for article in articles]
        except Exception as e:
            logger.error(f"获取文章失败: {e}")
            return []

    def get_articles_by_date_range(self, days: int = 7) -> List[Dict]:
        """获取指定天数内的文章"""
        try:
            cursor = self._conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT id, title, content, url, source, 
                       published_date::text as published_date, 
                       scraped_at::text as scraped_at
                FROM articles
                WHERE published_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY published_date DESC
            """,
                (days,),
            )
            articles = cursor.fetchall()
            cursor.close()
            logger.info(f"从数据库获取了最近{days}天的 {len(articles)} 篇文章")
            return [dict(article) for article in articles]
        except Exception as e:
            logger.error(f"获取文章失败: {e}")
            return []

    def get_articles_by_source(self, source: str) -> List[Dict]:
        """根据来源获取文章"""
        try:
            cursor = self._conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT id, title, content, url, source, 
                       published_date::text as published_date, 
                       scraped_at::text as scraped_at
                FROM articles
                WHERE source = %s
                ORDER BY published_date DESC
            """,
                (source,),
            )
            articles = cursor.fetchall()
            cursor.close()
            logger.info(f"从数据库获取了来源为 {source} 的 {len(articles)} 篇文章")
            return [dict(article) for article in articles]
        except Exception as e:
            logger.error(f"获取文章失败: {e}")
            return []

    def get_article_count(self) -> int:
        """获取文章总数"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM articles")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            logger.error(f"获取文章数量失败: {e}")
            return 0

    def get_sources(self) -> List[str]:
        """获取所有新闻源"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT DISTINCT source FROM articles ORDER BY source")
            sources = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return sources
        except Exception as e:
            logger.error(f"获取新闻源失败: {e}")
            return []

    def close(self):
        """关闭数据库连接"""
        if self._conn:
            NewsDatabase.close_connection()


if __name__ == "__main__":
    # 测试数据库读取
    print("测试数据库连接和读取...")

    reader = ArticleStorage()

    # 获取文章总数
    count = reader.get_article_count()
    print(f"\n数据库中共有 {count} 篇文章")

    # 获取所有新闻源
    sources = reader.get_sources()
    print(f"\n新闻源: {', '.join(sources)}")

    # 获取最新的5篇文章
    articles = reader.get_all_articles(limit=5)
    print(f"\n最新的 {len(articles)} 篇文章:")
    for i, article in enumerate(articles, 1):
        print(f"{i}. [{article['source']}] {article['title']}")

    reader.close()
