"""
数据爬取模块 - Member 1
功能：从多个新闻源抓取文章数据，并存储到PostgreSQL数据库
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from urllib.parse import urljoin
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.conn = None
        self.connect()
        self.create_table()
    
    def connect(self):
        """连接到PostgreSQL数据库"""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', '127.0.0.1'),
                database=os.getenv('DB_NAME', 'news_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '740918'),
                port=os.getenv('DB_PORT', '5432')
            )
            logger.info("成功连接到PostgreSQL数据库")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def create_table(self):
        """创建文章表（如果不存在）"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
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
            """)
            
            # 创建索引以提高查询性能
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_source 
                ON articles(source)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_published_date 
                ON articles(published_date)
            """)
            
            self.conn.commit()
            cursor.close()
            logger.info("数据库表创建/确认完成")
        except Exception as e:
            logger.error(f"创建表失败: {e}")
            self.conn.rollback()
    
    def insert_article(self, article: Dict) -> bool:
        """插入单篇文章到数据库"""
        try:
            cursor = self.conn.cursor()
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
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"插入文章失败: {e}")
            self.conn.rollback()
            return False
    
    def insert_articles_batch(self, articles: List[Dict]) -> int:
        """批量插入文章到数据库"""
        success_count = 0
        for article in articles:
            if self.insert_article(article):
                success_count += 1
        logger.info(f"成功插入 {success_count}/{len(articles)} 篇文章到数据库")
        return success_count
    
    def get_all_articles(self) -> List[Dict]:
        """从数据库获取所有文章"""
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, title, content, url, source, 
                       published_date, scraped_at, created_at
                FROM articles
                ORDER BY published_date DESC, created_at DESC
            """)
            articles = cursor.fetchall()
            cursor.close()
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
                       published_date, scraped_at, created_at
                FROM articles
                WHERE source = %s
                ORDER BY published_date DESC
            """, (source,))
            articles = cursor.fetchall()
            cursor.close()
            return [dict(article) for article in articles]
        except Exception as e:
            logger.error(f"获取文章失败: {e}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")


class NewsScraper:
    """新闻爬虫类"""
    
    def __init__(self, config_path: str = "config.json", use_database: bool = True):
        """初始化爬虫"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.scraper_config = self.config['scraper']
        self.headers = {
            'User-Agent': self.scraper_config['user_agent']
        }
        self.articles = []
        self.use_database = use_database
        
        # 初始化数据库管理器
        if self.use_database:
            try:
                self.db_manager = DatabaseManager()
                logger.info("数据库管理器初始化成功")
            except Exception as e:
                logger.warning(f"数据库初始化失败，将只保存到文件: {e}")
                self.use_database = False
                self.db_manager = None
        else:
            self.db_manager = None
    
    def scrape_generic_news(self, url: str, source_name: str) -> List[Dict]:
        """通用新闻抓取方法"""
        articles = []
        
        try:
            response = requests.get(
                url, 
                headers=self.headers,
                timeout=self.scraper_config['request_timeout']
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找文章链接（通用方法，适配多个新闻网站）
            article_links = []
            
            # 尝试多种常见的文章选择器
            for selector in ['article', '.article', '.story', '.post', 'h2 a', 'h3 a']:
                elements = soup.select(selector)
                if elements:
                    for element in elements[:self.scraper_config['max_articles_per_source']]:
                        if element.name == 'a':
                            link = element.get('href')
                        else:
                            link_tag = element.find('a')
                            link = link_tag.get('href') if link_tag else None
                        
                        if link:
                            full_url = urljoin(url, link)
                            if full_url not in article_links:
                                article_links.append(full_url)
                    
                    if article_links:
                        break
            
            logger.info(f"从 {source_name} 找到 {len(article_links)} 个文章链接")
            
            # 抓取每篇文章的详细内容
            for idx, article_url in enumerate(article_links[:self.scraper_config['max_articles_per_source']]):
                try:
                    article_data = self.scrape_article(article_url, source_name)
                    if article_data:
                        articles.append(article_data)
                    
                    # 延迟以避免被封禁
                    time.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"抓取文章失败 {article_url}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"抓取 {source_name} 失败: {e}")
        
        return articles
    
    def scrape_article(self, url: str, source: str) -> Dict:
        """抓取单篇文章内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title = None
            for selector in ['h1', '.article-title', '.headline', 'title']:
                title_tag = soup.select_one(selector)
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    break
            
            if not title:
                title = soup.title.string if soup.title else "未知标题"
            
            # 提取内容
            content = ""
            for selector in ['article', '.article-body', '.story-body', '.content', 'main']:
                content_tag = soup.select_one(selector)
                if content_tag:
                    paragraphs = content_tag.find_all('p')
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    break
            
            if not content:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs[:10]])
            
            # 提取发布时间
            published_date = datetime.now().strftime("%Y-%m-%d")
            for selector in ['time', '.published-date', '.timestamp']:
                date_tag = soup.select_one(selector)
                if date_tag:
                    date_str = date_tag.get('datetime') or date_tag.get_text(strip=True)
                    try:
                        published_date = self.parse_date(date_str)
                    except:
                        pass
                    break
            
            return {
                'title': title,
                'content': content[:5000],  # 限制长度
                'url': url,
                'source': source,
                'published_date': published_date,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"解析文章失败 {url}: {e}")
            return None
    
    def parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        from dateutil import parser
        try:
            dt = parser.parse(date_str)
            return dt.strftime("%Y-%m-%d")
        except:
            return datetime.now().strftime("%Y-%m-%d")
    
    def scrape_all_sources(self) -> List[Dict]:
        """从所有配置的新闻源抓取数据"""
        all_articles = []
        
        for source in self.scraper_config['news_sources']:
            if not source['enabled']:
                continue
            
            logger.info(f"开始抓取: {source['name']}")
            articles = self.scrape_generic_news(source['url'], source['name'])
            all_articles.extend(articles)
            logger.info(f"从 {source['name']} 抓取了 {len(articles)} 篇文章")
            
            # 源之间的延迟
            time.sleep(3)
        
        return all_articles
    
    def save_to_file(self, articles: List[Dict], output_path: str = "data/raw_articles.json"):
        """保存抓取的数据到文件"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到 {output_path}，共 {len(articles)} 篇文章")
    
    def save_to_database(self, articles: List[Dict]) -> int:
        """保存抓取的数据到数据库"""
        if not self.use_database or not self.db_manager:
            logger.warning("数据库未启用，跳过数据库保存")
            return 0
        
        return self.db_manager.insert_articles_batch(articles)
    
    def save_articles(self, articles: List[Dict]):
        """保存文章（同时保存到文件和数据库）"""
        # 保存到文件
        self.save_to_file(articles)
        
        # 保存到数据库
        if self.use_database:
            db_count = self.save_to_database(articles)
            logger.info(f"总计: 文件 {len(articles)} 篇, 数据库 {db_count} 篇")
    
    def close(self):
        """关闭资源"""
        if self.db_manager:
            self.db_manager.close()


def main():
    """主函数"""
    scraper = NewsScraper(use_database=True)
    
    try:
        articles = scraper.scrape_all_sources()
        
        if articles:
            scraper.save_articles(articles)
            print(f"\n✓ 成功抓取 {len(articles)} 篇文章")
            print(f"✓ 数据已保存到文件和数据库")
        else:
            print("\n✗ 未能抓取到文章")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
