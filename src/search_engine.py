from abc import ABC, abstractmethod
from typing import Iterable
from news_source import NewsSource, News

class SearchEngine(ABC):
    @abstractmethod
    def search(self, query: str) -> Iterable[News]:
        """根据查询返回搜索结果"""
        pass


class SimpleSearchEngine(SearchEngine):

    def __init__(self, news_stream: NewsSource):
        self.news_stream = news_stream

    def search(self, query: str):
        for news in self.news_stream.get_news():
            if query.lower() in news.title.lower() or query.lower() in news.content.lower():
                yield news
