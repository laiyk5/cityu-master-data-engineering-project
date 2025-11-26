import feedparser
from abc import ABC, abstractmethod
from typing import Iterable
from datetime import datetime
from atss import logger

news_feeds = [
    "https://www.hongkongfp.com/feed/",
]

class News:
    def __init__(self, title: str, content: str, url: str, source: str, published_at: datetime):
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        self.published_at = published_at
        self.scraped_at = datetime.now().isoformat()

    def __repr__(self):
        return f"News(title={self.title}, source={self.source}, published_at={self.published_at})"
    
    def __str__(self):
        return f"Title: {self.title}\nSource: {self.source}\nPublished At: {self.published_at}\nURL: {self.url}\nContent: {self.content[:200]}...\n"

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "source": self.source,
            "published_at": self.published_at.isoformat(),
            "scraped_at": self.scraped_at
        }

class NewsSource(ABC):
    
    @abstractmethod
    def get_news(self) -> Iterable[News]:
        """获取新闻文章"""
        pass


class FileNewsSource(NewsSource):
    def __init__(self, file_path: str):
        self._file_path = file_path
    
    def get_news(self) -> Iterable[News]:
        import json
        with open(self._file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            articles = data.get('articles', [])
            scraped_at = data.get('scraped_at', datetime.now().isoformat())
            for item in articles:
                title = item.get('title', '')
                content = item.get('content', '')
                url = item.get('url', '')
                source = item.get('source', 'Unknown Source')
                published_at_str = item.get('published_at', '')
                try:
                    published_at = datetime.fromisoformat(published_at_str)
                except:
                    published_at = datetime.now()
                
                news = News(
                    title=title,
                    content=content,
                    url=url,
                    source=source,
                    published_at=published_at
                )
                news.scraped_at = scraped_at
                yield news


# RSS News Scraper
class RssNewsSource(NewsSource):

    def __init__(self, url):
        self._url = url
        self._feed = feedparser.parse(self._url)
        self._source = self._feed.feed.get('title', 'Unknown Source')
    
    def get_news(self) -> Iterable[News]:
        logger.info(f"Fetching news from RSS feed: {self._source}")
        for entry in self._feed.entries:
            # create a news object
            try:
                title = str(entry.get('title', ''))
                url = str(entry.get('link', ''))
                content = str(entry.content[0].value) if 'content' in entry else str(entry.get('summary', ''))
                published_at = datetime(*entry.published_parsed[:6])

                news = News(
                    title=title,
                    content=content,
                    url=url,
                    source=self._source,
                    published_at=published_at
                )
            except Exception as e:
                print(f"Error parsing entry: {e}")
                continue
            yield news

class MetaNewsSource(NewsSource):
    def __init__(self, sources: Iterable[NewsSource]):
        self._sources = sources
    
    def get_news(self) -> Iterable[News]:
        for source in self._sources:
            yield from source.get_news()


class RssMetaNewsSource(NewsSource):
    """
    Load a opml file string containing multiple RSS feed URLs, and aggregate them as a MetaNewsSource.
    More Opml files can be found at https://github.com/plenaryapp/awesome-rss-feeds
    """
    def __init__(self, opml_str: str):
        import listparser
        result = listparser.parse(opml_str)
        self._rss_urls = [feed.url for feed in result.feeds if feed.url.endswith('.xml') or 'rss' in feed.url]


        self._source = MetaNewsSource([RssNewsSource(url) for url in self._rss_urls])
    
    def get_news(self) -> Iterable[News]:
        return self._source.get_news()


def _topic_search(news_source: NewsSource, topic: str) -> Iterable[News]:
    """根据主题搜索新闻文章"""
    
    for news in news_source.get_news():
        if topic.lower() in news.title.lower() or topic.lower() in news.content.lower():
            yield news

if __name__ == "__main__":
    # 测试 RSS 新闻源
    with open("config/rss/HongKong SAR.opml", "r", encoding="utf-8") as f:
        opml_content = f.read()
    news_source = RssMetaNewsSource(opml_content)
    articles = _topic_search(news_source, "National Games")
    for article in articles:
        print(article)