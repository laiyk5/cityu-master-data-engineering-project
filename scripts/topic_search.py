"""
交互式主题搜索爬虫
功能：根据用户输入的主题关键词，使用 DeepSeek API 智能查找相关新闻源并爬取
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from urllib.parse import urljoin, quote
import os
import sys
from dotenv import load_dotenv

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TopicScraper:
    """基于主题的新闻爬虫"""
    
    def __init__(self, topic: str, config_path: str = "config/config.json"):
        """
        初始化爬虫
        
        Args:
            topic: 搜索主题/关键词
        """
        self.topic = topic
        self.articles = []
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.scraper_config = self.config['scraper']
        self.headers = {
            'User-Agent': self.scraper_config['user_agent']
        }
        
        # 初始化数据库（如果可用）
        self.use_database = True
        try:
            from scraper import DatabaseManager
            self.db_manager = DatabaseManager()
            logger.info("数据库管理器初始化成功")
        except Exception as e:
            logger.warning(f"数据库初始化失败，将只保存到文件: {e}")
            self.use_database = False
            self.db_manager = None
        
        # 初始化智能源查找器（根据配置决定是否启用）
        topic_search_config = self.config.get('topic_search', {})
        self.use_intelligent_finder = topic_search_config.get('use_intelligent_finder', False)
        
        if self.use_intelligent_finder:
            try:
                from intelligent_source_finder import IntelligentSourceFinder
                self.source_finder = IntelligentSourceFinder()
                logger.info("智能新闻源查找器初始化成功")
            except Exception as e:
                logger.warning(f"智能源查找器初始化失败，将使用传统搜索: {e}")
                self.use_intelligent_finder = False
                self.source_finder = None
        else:
            logger.info("配置为使用传统搜索引擎方法（Bing News RSS）")
            self.source_finder = None
    
    def search_baidu_news(self, max_results: int = 100) -> List[Dict]:
        """
        搜索百度新闻
        """
        articles = []
        search_url = f"https://www.baidu.com/s?tn=news&rtt=1&bsst=1&cl=2&wd={quote(self.topic)}"
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找新闻条目
            news_items = soup.find_all('div', class_='result', limit=max_results)
            
            for item in news_items:
                try:
                    # 提取标题和链接
                    title_tag = item.find('h3') or item.find('a')
                    if title_tag:
                        link_tag = title_tag if title_tag.name == 'a' else title_tag.find('a')
                        if link_tag:
                            title = link_tag.get_text(strip=True)
                            url = link_tag.get('href', '')
                            
                            # 提取来源
                            source_tag = item.find('span', class_='c-color-gray')
                            source = source_tag.get_text(strip=True) if source_tag else '百度新闻'
                            
                            # 提取时间
                            time_tag = item.find('time')
                            published_date = datetime.now().strftime("%Y-%m-%d")
                            if time_tag and time_tag.get('datetime'):
                                try:
                                    published_date = time_tag.get('datetime').split('T')[0]
                                except:
                                    pass
                            
                            articles.append({
                                'title': title,
                                'url': url,
                                'source': source,
                                'published_date': published_date,
                                'content': '',  # 需要进一步爬取
                                'topic': self.topic,
                                'scraped_at': datetime.now().isoformat()
                            })
                except Exception as e:
                    logger.warning(f"解析新闻项失败: {e}")
                    continue
            
            logger.info(f"从百度新闻搜索到 {len(articles)} 篇关于 '{self.topic}' 的文章")
            
        except Exception as e:
            logger.error(f"搜索百度新闻失败: {e}")
        
        return articles
    
    def search_bing_news(self, max_results: int = 100) -> List[Dict]:
        """使用Bing新闻搜索（RSS + 网页版分页）"""
        articles = []
        seen_urls = set()
        
        # 先尝试RSS获取最新的
        search_url = f"https://www.bing.com/news/search?q={quote(self.topic)}&format=rss"
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            
            for item in items:
                try:
                    title = item.find('title').get_text(strip=True) if item.find('title') else ''
                    url = item.find('link').get_text(strip=True) if item.find('link') else ''
                    description = item.find('description').get_text(strip=True) if item.find('description') else ''
                    
                    pub_date = item.find('pubDate')
                    published_date = datetime.now().strftime("%Y-%m-%d")
                    if pub_date:
                        try:
                            from dateutil import parser
                            dt = parser.parse(pub_date.get_text())
                            published_date = dt.strftime("%Y-%m-%d")
                        except:
                            pass
                    
                    # 提取来源
                    source_tag = item.find('source')
                    source = source_tag.get_text(strip=True) if source_tag else 'Bing News'
                    
                    if url not in seen_urls:
                        seen_urls.add(url)
                        articles.append({
                            'title': title,
                            'url': url,
                            'source': source,
                            'published_date': published_date,
                            'content': description,
                            'topic': self.topic,
                            'scraped_at': datetime.now().isoformat()
                        })
                except Exception as e:
                    logger.warning(f"解析Bing新闻项失败: {e}")
                    continue
            
            logger.info(f"从Bing News RSS获取 {len(articles)} 篇文章")
            
        except Exception as e:
            logger.error(f"搜索Bing News RSS失败: {e}")
        
        # 如果需要更多结果，使用网页版分页搜索
        if len(articles) < max_results:
            logger.info(f"RSS结果不足，尝试网页版获取更多（目标: {max_results}篇）")
            page = 1
            max_pages = min(10, (max_results // 10) + 1)  # 每页约10条结果
            
            while len(articles) < max_results and page <= max_pages:
                try:
                    # Bing新闻网页版URL，first参数控制分页
                    first_param = (page - 1) * 10 + 1
                    web_url = f"https://www.bing.com/news/search?q={quote(self.topic)}&first={first_param}"
                    
                    response = requests.get(web_url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 查找新闻卡片
                    news_cards = soup.find_all('div', class_='news-card')
                    if not news_cards:
                        # 尝试其他可能的选择器
                        news_cards = soup.find_all('article')
                    
                    if not news_cards:
                        logger.warning(f"第{page}页未找到新闻卡片，停止分页")
                        break
                    
                    page_articles = 0
                    for card in news_cards:
                        try:
                            # 提取标题和链接
                            title_tag = card.find('a', class_='title')
                            if not title_tag:
                                title_tag = card.find('a')
                            
                            if not title_tag:
                                continue
                            
                            title = title_tag.get_text(strip=True)
                            url = title_tag.get('href', '')
                            
                            # 跳过已存在的URL
                            if url in seen_urls or not url:
                                continue
                            
                            # 提取描述
                            desc_tag = card.find('div', class_='snippet') or card.find('p')
                            description = desc_tag.get_text(strip=True) if desc_tag else ''
                            
                            # 提取来源
                            source_tag = card.find('span', class_='source')
                            source = source_tag.get_text(strip=True) if source_tag else 'Bing News'
                            
                            # 提取日期
                            date_tag = card.find('span', class_='time')
                            published_date = datetime.now().strftime("%Y-%m-%d")
                            if date_tag:
                                date_text = date_tag.get_text(strip=True)
                                # 简单处理日期（今天、昨天等）
                                if '小时' in date_text or '分钟' in date_text or '刚刚' in date_text:
                                    published_date = datetime.now().strftime("%Y-%m-%d")
                                elif '昨天' in date_text:
                                    published_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                            
                            seen_urls.add(url)
                            articles.append({
                                'title': title,
                                'url': url,
                                'source': source,
                                'published_date': published_date,
                                'content': description,
                                'topic': self.topic,
                                'scraped_at': datetime.now().isoformat()
                            })
                            page_articles += 1
                            
                            if len(articles) >= max_results:
                                break
                        
                        except Exception as e:
                            logger.warning(f"解析网页新闻卡片失败: {e}")
                            continue
                    
                    logger.info(f"第{page}页获取 {page_articles} 篇文章，累计 {len(articles)} 篇")
                    
                    if page_articles == 0:
                        logger.warning(f"第{page}页无新文章，停止分页")
                        break
                    
                    page += 1
                    time.sleep(1)  # 避免请求过快
                
                except Exception as e:
                    logger.error(f"搜索Bing News网页版第{page}页失败: {e}")
                    break
            
            logger.info(f"从Bing News共获取 {len(articles)} 篇关于 '{self.topic}' 的文章")
        
        return articles[:max_results]
    
    def scrape_article_content(self, url: str) -> str:
        """爬取文章详细内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
            
            return content[:5000]  # 限制长度
            
        except Exception as e:
            logger.warning(f"爬取文章内容失败 {url}: {e}")
            return ""
    
    def search_with_intelligent_finder(self, max_results: int = 100) -> List[Dict]:
        """使用智能源查找器搜索新闻"""
        logger.info(f"使用 DeepSeek API 智能查找主题: '{self.topic}' 的新闻源")
        
        all_articles = []
        
        try:
            # 1. 获取推荐的新闻源
            sources = self.source_finder.find_news_sources(self.topic, max_sources=5)
            logger.info(f"DeepSeek 推荐了 {len(sources)} 个新闻源")
            
            for source in sources:
                print(f"\n✓ 推荐源: {source['name']} - {source.get('description', '')}")
                print(f"  URL: {source['url']}")
            
            # 2. 从每个推荐的源爬取新闻
            for source in sources:
                try:
                    logger.info(f"正在从 {source['name']} 爬取新闻...")
                    
                    # 尝试从源的主页爬取
                    articles = self.scrape_from_source(
                        source['url'], 
                        source['name'],
                        max_articles=max_results // len(sources)
                    )
                    
                    all_articles.extend(articles)
                    logger.info(f"从 {source['name']} 获取了 {len(articles)} 篇文章")
                    
                    time.sleep(2)  # 延迟避免过快请求
                    
                except Exception as e:
                    logger.error(f"从 {source['name']} 爬取失败: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"智能源查找失败: {e}")
            # 回退到传统搜索
            logger.info("回退到传统搜索方法...")
            return self.search_topic_traditional(max_results)
        
        # 去重
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        logger.info(f"去重后共 {len(unique_articles)} 篇文章")
        self.articles = unique_articles
        return unique_articles
    
    def scrape_from_source(self, source_url: str, source_name: str, max_articles: int = 5) -> List[Dict]:
        """从指定新闻源爬取文章"""
        articles = []
        
        try:
            response = requests.get(source_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找文章链接（通用方法）
            article_links = []
            
            # 方法1: 查找包含主题关键词的链接
            for a_tag in soup.find_all('a', href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag.get('href')
                
                # 检查是否相关
                if title and len(title) > 10 and self.topic.lower() in title.lower():
                    full_url = urljoin(source_url, href)
                    if full_url.startswith('http'):
                        article_links.append({
                            'title': title,
                            'url': full_url,
                            'source': source_name
                        })
                        
                        if len(article_links) >= max_articles:
                            break
            
            # 方法2: 如果没找到，尝试爬取最新文章
            if not article_links:
                logger.info(f"未找到包含关键词的文章，爬取 {source_name} 最新文章...")
                for a_tag in soup.find_all('a', href=True, limit=max_articles * 2):
                    title = a_tag.get_text(strip=True)
                    href = a_tag.get('href')
                    
                    if title and len(title) > 20 and len(title) < 200:
                        full_url = urljoin(source_url, href)
                        if full_url.startswith('http') and 'article' in full_url or 'news' in full_url:
                            article_links.append({
                                'title': title,
                                'url': full_url,
                                'source': source_name
                            })
                            
                            if len(article_links) >= max_articles:
                                break
            
            # 爬取文章内容
            for article_info in article_links[:max_articles]:
                try:
                    time.sleep(1)
                    content = self.scrape_article_content(article_info['url'])
                    
                    articles.append({
                        'title': article_info['title'],
                        'url': article_info['url'],
                        'source': article_info['source'],
                        'published_date': datetime.now().strftime("%Y-%m-%d"),
                        'content': content,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.warning(f"爬取文章失败 {article_info['url']}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"从 {source_url} 爬取失败: {e}")
        
        return articles
    
    def search_topic_traditional(self, max_results: int = 100) -> List[Dict]:
        """传统搜索方法（使用 Bing/Google）"""
        logger.info(f"使用传统方法搜索主题: '{self.topic}'")
        
        all_articles = []
        
        # 尝试多个搜索源
        sources = [
            ('Bing News', self.search_bing_news),
            # 百度新闻有反爬虫验证，暂时禁用
            # ('百度新闻', self.search_baidu_news)
        ]
        
        for source_name, search_func in sources:
            try:
                logger.info(f"从 {source_name} 搜索...")
                articles = search_func(max_results=max_results // len(sources))
                
                # 爬取文章详细内容
                for article in articles:
                    if not article.get('content'):
                        time.sleep(1)
                        article['content'] = self.scrape_article_content(article['url'])
                
                all_articles.extend(articles)
                logger.info(f"从 {source_name} 获取了 {len(articles)} 篇文章")
                
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"从 {source_name} 搜索失败: {e}")
                continue
        
        # 去重
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        logger.info(f"去重后共 {len(unique_articles)} 篇文章")
        self.articles = unique_articles
        return unique_articles
    
    def search_topic(self, max_results: int = 100) -> List[Dict]:
        """搜索特定主题的新闻（智能选择方法）"""
        if self.use_intelligent_finder and self.source_finder:
            return self.search_with_intelligent_finder(max_results)
        else:
            return self.search_topic_traditional(max_results)
        return unique_articles
    
    def save_to_file(self, output_path: str = None):
        """保存到文件"""
        if output_path is None:
            # 使用主题名称创建文件名
            safe_topic = "".join(c for c in self.topic if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_topic = safe_topic.replace(' ', '_')
            output_path = f"data/topic_{safe_topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        data = {
            'topic': self.topic,
            'article_count': len(self.articles),
            'scraped_at': datetime.now().isoformat(),
            'articles': self.articles
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到 {output_path}")
        return output_path
    
    def save_to_database(self):
        """保存到数据库"""
        if not self.use_database or not self.db_manager:
            logger.warning("数据库未启用")
            return 0
        
        return self.db_manager.insert_articles_batch(self.articles)
    
    def close(self):
        """关闭资源"""
        if self.db_manager:
            self.db_manager.close()


def interactive_search():
    """交互式搜索界面"""
    print("""
╔════════════════════════════════════════════════════════╗
║         主题新闻搜索系统                               ║
║         Topic News Search System                       ║
╚════════════════════════════════════════════════════════╝
    """)
    
    # 获取用户输入
    print("请输入您想搜索的主题或事件（例如：人工智能、气候变化、科技新闻等）")
    topic = input("\n🔍 搜索主题: ").strip()
    
    if not topic:
        print("❌ 主题不能为空！")
        return
    
    print(f"\n✓ 搜索主题: {topic}")
    
    # 询问搜索数量
    try:
        max_results = input("\n📊 需要搜索多少篇文章？(默认100): ").strip()
        max_results = int(max_results) if max_results else 100
    except:
        max_results = 100
    
    print(f"✓ 搜索数量: {max_results}")
    
    # 询问是否爬取详细内容
    crawl_content = input("\n📰 是否爬取文章详细内容？(y/n, 默认n，耗时较长): ").strip().lower()
    crawl_content = crawl_content == 'y'
    
    print("\n" + "=" * 60)
    print("开始搜索...")
    print("=" * 60 + "\n")
    
    # 执行搜索
    scraper = TopicScraper(topic)
    
    try:
        articles = scraper.search_topic(max_results=max_results)
        
        if not articles:
            print("\n❌ 未找到相关文章")
            return
        
        print(f"\n✓ 找到 {len(articles)} 篇相关文章\n")
        
        # 显示前5篇
        print("=" * 60)
        print("文章预览（前5篇）:")
        print("=" * 60)
        for i, article in enumerate(articles[:5], 1):
            print(f"\n{i}. 【{article['source']}】{article['title']}")
            print(f"   URL: {article['url'][:80]}...")
            print(f"   日期: {article['published_date']}")
        
        # 保存选项
        print("\n" + "=" * 60)
        save_option = input("\n💾 保存选项:\n  1. 仅保存到文件\n  2. 保存到文件和数据库\n  3. 不保存\n\n请选择 (1/2/3, 默认1): ").strip()
        
        if save_option == '3':
            print("\n✓ 数据未保存")
        else:
            # 保存到文件
            file_path = scraper.save_to_file()
            print(f"\n✓ 已保存到文件: {file_path}")
            
            # 保存到数据库
            if save_option == '2':
                db_count = scraper.save_to_database()
                print(f"✓ 已保存到数据库: {db_count} 篇文章")
        
        # 询问是否继续处理
        print("\n" + "=" * 60)
        continue_process = input("\n是否继续处理这些数据（生成摘要、实体提取等）？(y/n, 默认n): ").strip().lower()
        
        if continue_process == 'y':
            # 将数据保存为标准格式供后续处理
            standard_file = "data/raw_articles.json"
            with open(standard_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ 数据已准备完成")
            print("\n现在可以运行以下命令继续处理:")
            print("  python main.py        # 运行完整的处理管道")
            print("  python demo.py        # 运行演示程序")
        
    finally:
        scraper.close()
    
    print("\n" + "=" * 60)
    print("搜索完成！")
    print("=" * 60)


if __name__ == "__main__":
    interactive_search()
