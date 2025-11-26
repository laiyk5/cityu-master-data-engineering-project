"""
主管道程序 - Member 6
功能：整合所有模块，执行完整的数据处理流程
"""

import json
import os
import logging
from datetime import datetime
import sys


# 添加 src 目录到路径
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)  # ../../src

# 配置日志
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")  # ../../logs
os.makedirs(log_dir, exist_ok=True)

# 配置文件处理器（UTF-8编码）
file_handler = logging.FileHandler(
    os.path.join(log_dir, "pipeline.log"), encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

# 配置控制台处理器（UTF-8编码）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
# 设置控制台输出编码为UTF-8
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "ignore")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "ignore")

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logger = logging.getLogger(__name__)


class Pipeline:
    """主管道类"""

    def __init__(self, config_path: str | None = None):
        """初始化管道"""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "config", "config.json"
            )  # ../../config/config.json
        self.config_path = config_path
        self.load_config()
        self.create_directories()

    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            logger.info("配置文件加载成功")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            sys.exit(1)

    def create_directories(self):
        """创建必要的目录"""
        directories = [
            self.config["output"]["data_dir"],
            self.config["output"]["temp_dir"],
            os.path.dirname(self.config["output"]["html_file"]),
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"目录已创建/确认: {directory}")

    def step0_topic_acquisition(self):
        """Gain topic from user input"""

        self.topic = input(
            "Please enter the topic or event you want to search for: "
        ).strip()

        logger.info(f"✓ 步骤0完成: 主题已获取 - {self.topic}")
        return True

    def step1_data_acquisition(self):
        """步骤1: 爬取数据"""
        logger.info("=" * 50)
        logger.info("步骤1: 开始爬取数据")
        logger.info("=" * 50)

        scraper = None
        try:
            # # 检查是否存在 topic 搜索结果
            # import glob
            # topic_files = glob.glob(os.path.join(self.config['output']['data_dir'], 'topic_*.json'))

            # if topic_files:
            #     # 使用最新的 topic 搜索结果
            #     latest_topic_file = max(topic_files, key=os.path.getmtime)
            #     logger.info(f"发现主题搜索结果: {os.path.basename(latest_topic_file)}")
            #     logger.info(f"将使用该文件的数据，跳过默认源爬取")

            #     with open(latest_topic_file, 'r', encoding='utf-8') as f:
            #         data = json.load(f)
            #         # topic文件可能有两种格式：列表或包装对象
            #         if isinstance(data, list):
            #             articles = data
            #         elif isinstance(data, dict) and 'articles' in data:
            #             articles = data['articles']
            #         else:
            #             articles = data

            # # 保存到 raw_articles.json 供后续步骤使用
            # raw_path = os.path.join(self.config['output']['data_dir'], 'raw_articles.json')
            # with open(raw_path, 'w', encoding='utf-8') as f:
            #     json.dump(articles, f, ensure_ascii=False, indent=2)

            # logger.info(f"✓ 步骤1完成: 使用了 {len(articles)} 篇主题搜索文章")
            # return True

            # 如果没有 topic 文件，按原来的方式爬取
            # from scraper import MyNewsScraper

            # scraper = MyNewsScraper(self.config_path, use_database=True)
            # articles = scraper.scrape_all_sources()

            # if not articles:
            #     logger.warning("未爬取到任何文章，使用示例数据")
            #     articles = self._create_sample_data()

            # # 保存到文件和数据库
            # scraper.save_articles(articles)

            from atss.news_source import RssMetaNewsSource, MetaNewsSource, News

            def news_to_article(news: News):
                article = news.to_dict()
                article["published_date"] = article.pop("published_at", "")
                return article

            def acuire_news_from_rss():
                from atss.search_engine.fts import FTSSearchEngine
                from atss.db_utils import ArticleStorage

                # load opml file
                opml_config = self.config["datasource"]["rss"]["opml"]
                opml_paths = []
                for c in opml_config:
                    if c["enabled"]:
                        opml_path = c["file"]
                        opml_paths.append(opml_path)

                news_sources = []
                for opml_path in opml_paths:
                    with open(opml_path, "r", encoding="utf-8") as f:
                        opml_content = f.read()
                    news_source = RssMetaNewsSource(opml_content)
                    news_sources.append(news_source)

                news_source = MetaNewsSource(news_sources)

                storage = ArticleStorage(reset=False)
                # storage the news from RSS
                storage.save_articles(
                    list(
                        map(lambda news: news_to_article(news), news_source.get_news())
                    )
                )

                # search the news by topic
                search_engine = FTSSearchEngine()
                news = list(search_engine.search(self.topic))
                return news

            def acuire_news_from_websearch():
                from atss.search_engine.webscraper import WebScraperSearchEngine
                from atss.config import get_config

                webscraper_config = get_config()["search_engine"]["webscraper"]

                # search the news using web search

                search_engines = {
                    name: WebScraperSearchEngine(cfg["sitemap"], limit=10)
                    for name, cfg in webscraper_config.items()
                    if cfg["enabled"]
                }

                all_news = []
                for name, search_engine in search_engines.items():
                    logger.info(f"Searching news with Web Search Engine {name}...")
                    all_news.extend(list(search_engine.search(self.topic)))
                return all_news

            rss_news = acuire_news_from_rss()
            websearch_news = acuire_news_from_websearch()

            news = rss_news + websearch_news

            # Save articles to files # !NOTE: just for compatibility

            from atss.scraper import MyNewsScraper

            scraper = MyNewsScraper(self.config_path, use_database=True)
            articles = [news_to_article(n) for n in news]
            scraper._save_to_file(articles)

            logger.info(f"✓ 步骤1完成: 爬取了 {len(articles)} 篇文章")
            return True

        except Exception as e:
            logger.error(f"✗ 步骤1失败: {e}", stack_info=True)
            # 创建示例数据以便继续流程
            articles = self._create_sample_data()
            from atss.scraper import MyNewsScraper

            scraper_fallback = MyNewsScraper(self.config_path, use_database=False)
            scraper_fallback._save_to_file(articles)
            logger.info("使用示例数据继续")
            return True
        finally:
            if scraper:
                scraper.close()

    def step2_clean_data(self):
        """步骤2: 清洗数据"""
        logger.info("=" * 50)
        logger.info("步骤2: 开始清洗数据")
        logger.info("=" * 50)

        try:
            from atss.data_cleaner import DataCleaner

            # 读取原始数据
            with open("data/raw_articles.json", "r", encoding="utf-8") as f:
                raw_articles = json.load(f)

            cleaner = DataCleaner()
            cleaned_articles = cleaner.clean_dataset(raw_articles)
            cleaner.save_cleaned_data(cleaned_articles)

            logger.info(f"✓ 步骤2完成: 清洗了 {len(cleaned_articles)} 篇文章")
            return True

        except Exception as e:
            logger.error(f"✗ 步骤2失败: {e}")
            return False

    def step3_deduplicate(self):
        """步骤3: 去重"""
        logger.info("=" * 50)
        logger.info("步骤3: 开始去重")
        logger.info("=" * 50)

        try:
            from atss.deduplicator import Deduplicator

            with open("data/cleaned_articles.json", "r", encoding="utf-8") as f:
                cleaned_articles = json.load(f)

            deduplicator = Deduplicator(
                similarity_threshold=self.config["deduplication"][
                    "similarity_threshold"
                ]
            )
            deduplicated_articles = deduplicator.deduplicate(cleaned_articles)
            deduplicator.save_deduplicated_data(deduplicated_articles)

            logger.info(f"✓ 步骤3完成: 去重后剩余 {len(deduplicated_articles)} 篇文章")
            return True

        except Exception as e:
            logger.error(f"✗ 步骤3失败: {e}")
            return False

    def step4_extract_entities(self):
        """步骤4: 提取实体"""
        logger.info("=" * 50)
        logger.info("步骤4: 开始提取实体")
        logger.info("=" * 50)

        try:
            from atss.entity_extractor import EntityExtractor

            with open("data/deduplicated_articles.json", "r", encoding="utf-8") as f:
                articles = json.load(f)

            extractor = EntityExtractor(self.config_path)
            entities_data = extractor.extract_and_rank(articles)
            extractor.save_entities(entities_data)

            logger.info(f"✓ 步骤4完成: 提取了实体")
            return True

        except Exception as e:
            logger.error(f"✗ 步骤4失败: {e}")
            return False

    def step5_generate_summary(self):
        """步骤5: 生成摘要"""
        logger.info("=" * 50)
        logger.info("步骤5: 开始生成摘要")
        logger.info("=" * 50)

        try:
            from atss.summarizer import Summarizer

            with open("data/deduplicated_articles.json", "r", encoding="utf-8") as f:
                articles = json.load(f)

            summarizer = Summarizer(self.config_path)
            summary = summarizer.generate_summary(articles)
            summarizer.save_summary(summary)

            logger.info(f"✓ 步骤5完成: 生成了摘要")
            return True

        except Exception as e:
            logger.error(f"✗ 步骤5失败: {e}")
            return False

    def step6_generate_timeline(self):
        """步骤6: 生成时间线"""
        logger.info("=" * 50)
        logger.info("步骤6: 开始生成时间线")
        logger.info("=" * 50)

        try:
            from atss.timeline_generator import TimelineGenerator

            with open("data/deduplicated_articles.json", "r", encoding="utf-8") as f:
                articles = json.load(f)

            generator = TimelineGenerator()
            timeline = generator.create_timeline(articles)
            generator.save_timeline(timeline)

            logger.info(f"✓ 步骤6完成: 生成了 {len(timeline)} 个时间节点")
            return True

        except Exception as e:
            logger.error(f"✗ 步骤6失败: {e}")
            return False

    def step7_generate_html(self):
        """步骤7: 生成HTML页面"""
        logger.info("=" * 50)
        logger.info("步骤7: 开始生成HTML页面")
        logger.info("=" * 50)

        try:
            from atss.html_generator import HTMLGenerator

            # # 获取主题名称（从topic文件名或摘要中提取）
            # topic_name = None
            # import glob
            # topic_files = glob.glob(os.path.join(self.config['output']['data_dir'], 'topic_*.json'))
            # if topic_files:
            #     latest_topic_file = max(topic_files, key=os.path.getmtime)
            #     # 从文件名提取主题：topic_主题名_时间戳.json
            #     filename = os.path.basename(latest_topic_file)
            #     parts = filename.replace('.json', '').split('_')
            #     if len(parts) >= 2:
            #         topic_name = '_'.join(parts[1:-1])  # 去掉'topic'和时间戳
            topic_name = self.topic

            generator = HTMLGenerator(self.config_path)
            data = generator.load_data()
            html_content = generator.generate_html(data)
            actual_file = generator.save_html(html_content, topic_name=topic_name)

            # 保存实际生成的文件路径供后续使用
            self.generated_html_file = actual_file

            logger.info(f"✓ 步骤7完成: HTML页面已生成")
            return True

        except Exception as e:
            logger.error(f"✗ 步骤7失败: {e}")
            return False

    def _create_sample_data(self):
        """创建示例数据"""
        sample_articles = [
            {
                "title": "AI Technology Breakthrough in Natural Language Processing",
                "content": "Researchers have announced a major breakthrough in natural language processing technology. The new model shows unprecedented accuracy in understanding context and generating human-like responses. This development is expected to revolutionize various industries including customer service, content creation, and education. The team behind this achievement includes leading scientists from multiple institutions.",
                "url": "https://example.com/article1",
                "source": "Tech News",
                "published_date": "2025-11-15",
                "scraped_at": datetime.now().isoformat(),
            },
            {
                "title": "New Climate Agreement Reached at International Summit",
                "content": "World leaders have reached a historic climate agreement at the international summit. The agreement includes commitments to reduce carbon emissions by 50% by 2030. Major countries including the United States, China, and European nations have pledged significant investments in renewable energy. Environmental organizations have praised the agreement as a crucial step forward.",
                "url": "https://example.com/article2",
                "source": "World News",
                "published_date": "2025-11-16",
                "scraped_at": datetime.now().isoformat(),
            },
            {
                "title": "Tech Giant Announces Revolutionary Quantum Computer",
                "content": "A major technology company has unveiled its latest quantum computer, claiming it can solve complex problems thousands of times faster than traditional computers. The breakthrough has implications for drug discovery, financial modeling, and cryptography. Industry experts believe this marks the beginning of the quantum computing era.",
                "url": "https://example.com/article3",
                "source": "Innovation Daily",
                "published_date": "2025-11-17",
                "scraped_at": datetime.now().isoformat(),
            },
        ]

        logger.info("已创建示例数据用于演示")
        return sample_articles

    def run(self):
        """运行完整管道"""
        logger.info("\n" + "=" * 60)
        logger.info("开始执行自动化主题摘要生成管道")
        logger.info("=" * 60 + "\n")

        start_time = datetime.now()

        steps = [
            ("获取topic", self.step0_topic_acquisition),
            ("爬取数据", self.step1_data_acquisition),
            ("清洗数据", self.step2_clean_data),
            ("去重处理", self.step3_deduplicate),
            ("提取实体", self.step4_extract_entities),
            ("生成摘要", self.step5_generate_summary),
            ("生成时间线", self.step6_generate_timeline),
            ("生成HTML", self.step7_generate_html),
        ]

        results = []
        for step_name, step_func in steps:
            try:
                success = step_func()
                results.append((step_name, success))

                if not success:
                    logger.warning(f"步骤 '{step_name}' 失败，但继续执行")

            except Exception as e:
                logger.error(f"步骤 '{step_name}' 发生异常: {e}")
                results.append((step_name, False))

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 打印总结
        logger.info("\n" + "=" * 60)
        logger.info("管道执行完成")
        logger.info("=" * 60)
        logger.info(f"总耗时: {duration:.2f} 秒")
        logger.info("\n执行结果:")

        for step_name, success in results:
            status = "✓" if success else "✗"
            logger.info(f"  {status} {step_name}")

        # 统计
        success_count = sum(1 for _, success in results if success)
        logger.info(f"\n成功: {success_count}/{len(results)} 个步骤")

        if success_count == len(results):
            logger.info("\n🎉 所有步骤成功完成！")
            # 显示实际生成的HTML文件路径
            html_file = getattr(
                self, "generated_html_file", self.config["output"]["html_file"]
            )
            logger.info(f"📄 HTML报告已生成: {html_file}")
        else:
            logger.warning("\n⚠️  部分步骤失败，请查看日志")


def main():
    """主函数"""
    print(
        """
    ╔════════════════════════════════════════════════════════╗
    ║     自动化主题摘要页面生成系统                         ║
    ║     Automated Topic Summary Page Generation            ║
    ╚════════════════════════════════════════════════════════╝
    """
    )

    pipeline = Pipeline()
    pipeline.run()

    print("\n" + "=" * 60)
    print("感谢使用！")
    print("=" * 60)


if __name__ == "__main__":
    main()
