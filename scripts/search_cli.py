"""
命令行主题搜索工具
功能：通过命令行参数进行主题搜索
"""

import argparse
import sys
from topic_search import TopicScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='主题新闻搜索工具 - 搜索特定主题的新闻文章',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 搜索"人工智能"主题的20篇文章
  python search_cli.py --topic "人工智能" --max 20 --save both
  
  # 搜索"气候变化"并保存到数据库
  python search_cli.py -t "Climate Change" -m 15 -s db
  
  # 搜索并继续处理
  python search_cli.py -t "AI Technology" --continue
        """
    )
    
    parser.add_argument(
        '-t', '--topic',
        required=True,
        help='搜索主题或关键词（必需）'
    )
    
    parser.add_argument(
        '-m', '--max',
        type=int,
        default=20,
        help='最大文章数量（默认：20）'
    )
    
    parser.add_argument(
        '-s', '--save',
        choices=['file', 'db', 'both', 'none'],
        default='file',
        help='保存选项：file=仅文件, db=仅数据库, both=两者, none=不保存（默认：file）'
    )
    
    parser.add_argument(
        '-c', '--continue',
        action='store_true',
        dest='continue_process',
        help='搜索后继续处理数据（生成摘要等）'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='指定输出文件路径（可选）'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("主题新闻搜索工具")
    print("=" * 70)
    print(f"搜索主题: {args.topic}")
    print(f"文章数量: {args.max}")
    print(f"保存选项: {args.save}")
    print("=" * 70)
    print()
    
    # 创建搜索器
    scraper = TopicScraper(args.topic)
    
    try:
        # 搜索文章
        print("正在搜索...")
        articles = scraper.search_topic(max_results=args.max)
        
        if not articles:
            print("\n❌ 未找到相关文章")
            return 1
        
        print(f"\n✓ 找到 {len(articles)} 篇相关文章\n")
        
        # 显示前5篇
        print("=" * 70)
        print("文章预览（前5篇）:")
        print("=" * 70)
        for i, article in enumerate(articles[:5], 1):
            print(f"\n{i}. [{article['source']}] {article['title']}")
            print(f"   日期: {article['published_date']}")
            print(f"   URL: {article['url'][:70]}...")
        
        print("\n" + "=" * 70)
        
        # 保存数据
        saved_files = []
        
        if args.save in ['file', 'both']:
            file_path = scraper.save_to_file(args.output)
            saved_files.append(file_path)
            print(f"✓ 已保存到文件: {file_path}")
        
        if args.save in ['db', 'both']:
            db_count = scraper.save_to_database()
            print(f"✓ 已保存到数据库: {db_count} 篇文章")
        
        if args.save == 'none':
            print("⚠️  数据未保存")
        
        # 继续处理
        if args.continue_process:
            import json
            standard_file = "data/raw_articles.json"
            with open(standard_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            print("\n" + "=" * 70)
            print("✓ 数据已准备完成，可以继续处理")
            print("\n运行以下命令继续:")
            print("  python main.py        # 运行完整的处理管道")
            print("=" * 70)
        
        print("\n✓ 搜索完成！")
        return 0
        
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return 1
        
    finally:
        scraper.close()


if __name__ == "__main__":
    sys.exit(main())
