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


class DatabaseReader:
    """数据库读取类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.conn = None
        self.connect()
    
    def connect(self):
        """连接到PostgreSQL数据库"""
        try:
            self.conn = psycopg2.connect(
                host='127.0.0.1',
                database='postgres',
                user='postgres',
                password='admin',
                port='5432'
            )
            logger.info("成功连接到PostgreSQL数据库")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def get_all_articles(self, limit: int = None) -> List[Dict]:
        """获取所有文章"""
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            # allow optional ordering via safe column names and direction
            # default ordering
            query = """
                SELECT id, title, content, url, source, 
                       published_date::text as published_date, 
                       scraped_at::text as scraped_at
                FROM articles
            """
            if limit:
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
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, title, content, url, source, 
                       published_date::text as published_date, 
                       scraped_at::text as scraped_at
                FROM articles
                WHERE published_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY published_date DESC
            """, (days,))
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
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, title, content, url, source, 
                       published_date::text as published_date, 
                       scraped_at::text as scraped_at
                FROM articles
                WHERE source = %s
                ORDER BY published_date DESC
            """, (source,))
            articles = cursor.fetchall()
            cursor.close()
            logger.info(f"从数据库获取了来源为 {source} 的 {len(articles)} 篇文章")
            return [dict(article) for article in articles]
        except Exception as e:
            logger.error(f"获取文章失败: {e}")
            return []

    def get_articles_by_query(self, query_text: str, limit: int = 100) -> List[Dict]:
        """根据文本查询文章（title/content/source）使用 ILIKE（不区分大小写）

        Args:
            query_text: 要搜索的文本
            limit: 最多返回多少条记录

        Returns:
            文章列表
        """
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            # 使用参数化查询以防注入；将查询用%%包裹表示模糊匹配
            pattern = f"%{query_text}%"
            cursor.execute("""
                SELECT id, title, content, url, source,
                       published_date::text as published_date,
                       scraped_at::text as scraped_at
                FROM articles
                WHERE title ILIKE %s OR content ILIKE %s OR source ILIKE %s
                ORDER BY published_date DESC
                LIMIT %s
            """, (pattern, pattern, pattern, limit))
            articles = cursor.fetchall()
            cursor.close()
            logger.info(f"通过查询 '{query_text}' 找到 {len(articles)} 篇文章")
            return [dict(article) for article in articles]
        except Exception as e:
            logger.error(f"查询文章失败: {e}")
            return []

    def get_articles_by_query_with_sort(self, query_text: str, limit: int = 100, offset: int = 0, sort_by: str = 'published_date', sort_dir: str = 'desc') -> List[Dict]:
        """Server-side search with secure ordering

        Args:
            query_text: the search string
            limit: max rows
            sort_by: allowed column name to sort by
            sort_dir: 'asc' or 'desc'
        """
        # sanitize sort_by and sort_dir to prevent SQL injection (no parameterization for column names)
        allowed_cols = {'id', 'title', 'source', 'published_date', 'scraped_at', 'created_at'}
        if sort_by not in allowed_cols:
            sort_by = 'published_date'

        sort_dir = 'ASC' if str(sort_dir).lower() == 'asc' else 'DESC'

        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            pattern = f"%{query_text}%"
            sql = f"""
                SELECT id, title, content, url, source,
                       published_date::text as published_date,
                       scraped_at::text as scraped_at
                FROM articles
                WHERE title ILIKE %s OR content ILIKE %s OR source ILIKE %s
                ORDER BY {sort_by} {sort_dir}
                LIMIT %s
                OFFSET %s
            """
            cursor.execute(sql, (pattern, pattern, pattern, limit, offset))
            articles = cursor.fetchall()
            cursor.close()
            logger.info(f"通过查询 '{query_text}' 找到 {len(articles)} 篇文章 (排序: {sort_by} {sort_dir})")
            return [dict(article) for article in articles]
        except Exception as e:
            logger.error(f"查询文章失败: {e}")
            return []

    def get_all_articles_with_sort(self, limit: int = None, sort_by: str = 'published_date', sort_dir: str = 'desc') -> List[Dict]:
        """Return all articles with optional ordering. Uses whitelist for sort_by and sort_dir."""
        allowed_cols = {'id', 'title', 'source', 'published_date', 'scraped_at', 'created_at'}
        if sort_by not in allowed_cols:
            sort_by = 'published_date'

        sort_dir = 'ASC' if str(sort_dir).lower() == 'asc' else 'DESC'

        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            sql = f"""
                SELECT id, title, content, url, source,
                       published_date::text as published_date,
                       scraped_at::text as scraped_at
                FROM articles
                ORDER BY {sort_by} {sort_dir}
            """
            if limit is not None:
                # limit may be provided as per_page; if offset is required we'll use a separate path
                sql += f" LIMIT %s"
                cursor.execute(sql, (limit,))
            else:
                cursor.execute(sql)

            articles = cursor.fetchall()
            cursor.close()
            logger.info(f"从数据库获取了 {len(articles)} 篇文章 (排序: {sort_by} {sort_dir})")
            return [dict(article) for article in articles]
        except Exception as e:
            logger.error(f"获取文章失败: {e}")
            return []

    def get_all_articles_with_sort_and_offset(self, limit: int = None, offset: int = 0, sort_by: str = 'published_date', sort_dir: str = 'desc') -> List[Dict]:
        """Return articles with ordering, limit and offset for pagination."""
        allowed_cols = {'id', 'title', 'source', 'published_date', 'scraped_at', 'created_at'}
        if sort_by not in allowed_cols:
            sort_by = 'published_date'

        sort_dir = 'ASC' if str(sort_dir).lower() == 'asc' else 'DESC'

        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            sql = f"""
                SELECT id, title, content, url, source,
                       published_date::text as published_date,
                       scraped_at::text as scraped_at
                FROM articles
                ORDER BY {sort_by} {sort_dir}
            """
            if limit is not None:
                sql += " LIMIT %s OFFSET %s"
                cursor.execute(sql, (limit, offset))
            else:
                cursor.execute(sql)

            articles = cursor.fetchall()
            cursor.close()
            logger.info(f"从数据库获取了 {len(articles)} 篇文章 (排序: {sort_by} {sort_dir}, offset={offset})")
            return [dict(article) for article in articles]
        except Exception as e:
            logger.error(f"获取文章失败: {e}")
            return []

    def get_article_count_by_query(self, query_text: str) -> int:
        """Count articles matching a query_text across title/content/source."""
        try:
            cursor = self.conn.cursor()
            pattern = f"%{query_text}%"
            cursor.execute("""
                SELECT COUNT(*) FROM articles
                WHERE title ILIKE %s OR content ILIKE %s OR source ILIKE %s
            """, (pattern, pattern, pattern))
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            logger.error(f"查询计数失败: {e}")
            return 0
    
    def get_article_count(self) -> int:
        """获取文章总数"""
        try:
            cursor = self.conn.cursor()
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
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT source FROM articles ORDER BY source")
            sources = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return sources
        except Exception as e:
            logger.error(f"获取新闻源失败: {e}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")


def load_articles_from_database(limit: int = None, days: int = None) -> List[Dict]:
    """
    从数据库加载文章的便捷函数
    
    Args:
        limit: 限制返回的文章数量
        days: 只返回最近N天的文章
    
    Returns:
        文章列表
    """
    try:
        reader = DatabaseReader()
        
        if days:
            articles = reader.get_articles_by_date_range(days)
        else:
            articles = reader.get_all_articles(limit)
        
        reader.close()
        return articles
    except Exception as e:
        logger.error(f"从数据库加载文章失败: {e}")
        # 如果数据库读取失败，尝试从文件读取
        logger.info("尝试从文件读取数据...")
        try:
            import json
            with open('data/raw_articles.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []


if __name__ == "__main__":
    # 测试数据库读取
    print("测试数据库连接和读取...")
    
    reader = DatabaseReader()
    
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
