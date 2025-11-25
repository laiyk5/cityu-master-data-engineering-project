from atss.db_utils import ArticleStorage
from atss.news_source import NewsSource, News
from datetime import datetime

from . import SearchEngine

def article_to_news(article: dict) -> News:
    return News(
        title=article['title'],
        content=article['content'],
        url=article['url'],
        published_at=datetime.strptime(article['published_date'], "%Y-%m-%d"),
        source=article['source']
    )

class FTSSearchEngine(SearchEngine):

    def __init__(self):
        self._storage = ArticleStorage()

    def search(self, query: str):
        articles = self._storage.search_article(query)

        # convert article to News objects
        #!NOTE: just for compatibility
        for article in articles:
            article_obj = article_to_news(article)
            yield article_obj



if __name__ == "__main__":
    # 测试FTS搜索引擎
    fts_earch_engine = FTSSearchEngine()
    query = "Trump & Epstein"
    search_results = list(fts_earch_engine.search(query))
    print(f"\n搜索关键词 '{query}'，找到 {len(search_results)} 篇相关文章:")
    for i, article in enumerate(search_results, 1):
        print(f"{i}. [{article.published_at}] [{article.source}] {article.title}")
        