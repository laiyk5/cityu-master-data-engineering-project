"""This module implements a web scraper-based search engine.

Web Scraper (https://webscraper.io/) is a powerful web scraping tool that can easily extract data from
websites based on user-defined sitemaps.

The sitemap defines how to navigate and extract data from a specific website structure. It is generated
by the Web Scraper tool and saved as a JSON file.

If the scraper does not function, update the corresponding sitemap. Don't forget to replace the query
text in the sitemap's start URL with {query} to make this module function.
"""

import datetime
from re import S
from typing import Iterable

import dateparser
from regex import F
import selenium

from atss.news_source import News
from . import SearchEngine
import json


from bs4 import BeautifulSoup

from atss import logger


class Parser:
    def __init__(
        self,
        id,
        selector,
        type_: str,
        multiple: bool = False,
        parent: "Parser | None" = None,
    ):
        self.id = id
        self.selector = selector
        self.type_ = type_
        self.children: list[Parser] = []
        self.parent = parent
        self.multiple = multiple
        parent.add_child(self) if parent else None

    def add_child(self, child_parser):
        self.children.append(child_parser)

    def parse(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.select(self.selector)

        if self.children:
            results = []
            for element in elements:
                result = {}
                for child in self.children:
                    child_result = {child.id: child.parse(str(element))}
                    result.update(child_result)
                results.append(result)
        else:
            if self.type_ == "SelectorText":
                results = [e.get_text(strip=True) for e in elements]
            elif self.type_ == "SelectorLink":
                results = [e.get("href") for e in elements]
            else:
                results = [e.get_text(strip=True) for e in elements]
        return results if self.multiple else results[0] if results else None


class WebScraperSearchEngine(SearchEngine):
    def __init__(self, sitemap_path, limit: int = 10, go_detail=False):
        self.limit = limit
        self.go_detail = go_detail
        # load site map
        with open(sitemap_path, "r", encoding="utf-8") as f:
            self._sitemap = json.load(f)

        from selenium.webdriver import ChromeOptions, Chrome
        chrome_options = ChromeOptions()
        # chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = Chrome(options=chrome_options)

        self._init_parser()

    def _init_parser(self):
        parsers: dict[str, Parser] = {}
        parsers["_root"] = Parser("_root", "", type_="Root")
        # build parser tree with self.sitemap
        for s in self._sitemap["selectors"]:
            # print(s)
            # print(type(s))
            id = s["id"]
            selector_ = s["selector"]
            parent = parsers[s["parentSelectors"][0]]
            multiple = s["multiple"]
            type_ = s["type"]
            parsers[id] = Parser(
                id, selector_, type_=type_, multiple=multiple, parent=parent
            )  # find parent parser

        # search for the root selector (i.e., the one)
        self.root_parser = parsers["record_wrapper"]


    def _get_page_source(self, url: str):
        self.driver.get(url)
        import time

        time.sleep(2)  # wait for page to load
        return self.driver.page_source

    def search(self, query: str):
        from urllib.parse import quote

        search_url = self._sitemap["startUrl"][0].replace("{query}", quote(query))
        logger.info(f"Searching URL: {search_url}")

        html = self._get_page_source(search_url)
        # if response.status_code != 200:
        #     logger.error(f"Failed to fetch search results: {response.status_code}")
        #     return

        # html = response.text
        # print(html)
        records: list[dict] = self.root_parser.parse(html)

        for record in records[:self.limit]:
            url = record.get("url", "")
            if url.startswith("./"):
                url = "https://news.google.com" + url[1:]
            record["url"] = url
            published_at = record.get("published_at", "")
            if published_at:
                published_at = dateparser.parse(published_at)  # parse human readable strings like "2 hours ago"
            if not published_at:
                raise ValueError("No published_at found")
            else:
                published_at = published_at.date()
            news = News(
                title=record.get("title", "No Title"),
                content=record.get("content", "No Content"),
                url=url,
                published_at=published_at,
                source=record.get("source", "Unkown"),
            )

            # try get the content from the url if content is empty
            if self.go_detail and (not news.content or news.content == "No Content"):
                try:
                    news.content = self._fetch_article_content(news.url)
                except Exception as e:
                    logger.error(
                        f"Failed to fetch article content from {news.url}: {e}"
                    )

            yield news

    def _fetch_article_content(self, url: str) -> str:
        from bs4 import BeautifulSoup

        import time
        time.sleep(2)  # 避免过快请求

        import requests
        response = requests.get(url, allow_redirects=True, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch article content: {response.status_code}")
            return "No Content"

        html = response.text


        # html = self._get_page_source(url)
        logger.debug(f"Fetched HTML content from {url[:50]}..., length: {len(html)}")
        soup = BeautifulSoup(html, "html.parser")

        # Try to extract main article content
        paragraphs = soup.select("p")
        logger.debug("Number of paragraphs found: " + str(len(paragraphs)))
        content = "\n".join([p.get_text(strip=True) for p in paragraphs])


        logger.debug(content)

        return content if content else "No Content"



if __name__ == "__main__":
    from atss.config import get_config

    webscraper_config = get_config()["search_engine"]["webscraper"]

    # 测试Google News搜索引擎
    google_search_engine = WebScraperSearchEngine(webscraper_config["Google News"]["sitemap"], limit=1, go_detail=True)
    query = "Japan Tiwan"
    search_results = list(google_search_engine.search(query))
    logger.info(f"\n搜索关键词 '{query}'，找到 {len(search_results)} 篇相关文章:")
    for i, article in enumerate(search_results, 1):
        logger.info(f"{i}. {article}")

    # 测试Baidu News搜索引擎
    baidu_search_engine = WebScraperSearchEngine(webscraper_config["Baidu News"]["sitemap"], limit=10)
    query = "日本 台湾"
    search_results = list(baidu_search_engine.search(query))
    logger.info(f"\n搜索关键词 '{query}'，找到 {len(search_results)} 篇相关文章:")
    for i, article in enumerate(search_results, 1):
        logger.info(f"{i}. {article}")