"""
数据清洗模块 - Member 2
功能：清洗和标准化爬取的数据
"""

import json
import re
from typing import List, Dict
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清洗类"""
    
    def __init__(self):
        """初始化数据清洗器"""
        self.cleaned_articles = []
    
    def clean_html(self, text: str) -> str:
        """去除HTML标签"""
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text()
    
    def remove_special_chars(self, text: str) -> str:
        """去除特殊字符但保留基本标点"""
        # 保留字母、数字、空格和基本标点
        text = re.sub(r'[^\w\s.,!?;:()\-\'\"]+', ' ', text)
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def remove_ads_and_boilerplate(self, text: str) -> str:
        """去除广告和样板文字"""
        # 常见的广告和样板文字模式
        ad_patterns = [
            r'subscribe to our newsletter',
            r'click here to',
            r'advertisement',
            r'sign up for',
            r'follow us on',
            r'share this article',
            r'read more:',
        ]
        
        text_lower = text.lower()
        for pattern in ad_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def standardize_date(self, date_str: str) -> str:
        """标准化日期格式为 YYYY-MM-DD"""
        try:
            # 尝试多种日期格式
            formats = [
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%d-%m-%Y",
                "%d/%m/%Y",
                "%B %d, %Y",
                "%b %d, %Y",
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%d")
                except:
                    continue
            
            # 如果都失败，返回原始字符串
            return date_str
            
        except Exception as e:
            logger.warning(f"日期标准化失败: {date_str}")
            return date_str
    
    def clean_article(self, article: Dict) -> Dict:
        """清洗单篇文章"""
        cleaned = article.copy()
        
        # 清洗标题
        if 'title' in cleaned:
            cleaned['title'] = self.clean_html(cleaned['title'])
            cleaned['title'] = self.remove_special_chars(cleaned['title'])
            cleaned['title'] = cleaned['title'][:200]  # 限制长度
        
        # 清洗内容
        if 'content' in cleaned:
            cleaned['content'] = self.clean_html(cleaned['content'])
            cleaned['content'] = self.remove_ads_and_boilerplate(cleaned['content'])
            cleaned['content'] = self.remove_special_chars(cleaned['content'])
            
            # 去除过短的内容
            if len(cleaned['content']) < 100:
                logger.warning(f"文章内容过短，可能质量不高: {cleaned.get('title', 'Unknown')}")
        
        # 标准化日期
        if 'published_date' in cleaned:
            cleaned['published_date'] = self.standardize_date(cleaned['published_date'])
        
        # 确保URL存在
        if 'url' not in cleaned or not cleaned['url']:
            cleaned['url'] = ''
        
        # 确保source存在
        if 'source' not in cleaned or not cleaned['source']:
            cleaned['source'] = 'Unknown'
        
        return cleaned
    
    def validate_article(self, article: Dict) -> bool:
        """验证文章数据质量"""
        # 必须有标题
        if not article.get('title'):
            return False
        
        # 必须有内容且长度合理
        content = article.get('content', '')
        if len(content) < 100:
            return False
        
        # 必须有URL
        if not article.get('url'):
            return False
        
        return True
    
    def clean_dataset(self, articles: List[Dict]) -> List[Dict]:
        """清洗整个数据集"""
        cleaned_articles = []
        
        for idx, article in enumerate(articles):
            try:
                cleaned = self.clean_article(article)
                
                # 验证清洗后的文章
                if self.validate_article(cleaned):
                    cleaned_articles.append(cleaned)
                else:
                    logger.warning(f"文章 {idx} 未通过验证，已跳过")
                    
            except Exception as e:
                logger.error(f"清洗文章 {idx} 时出错: {e}")
                continue
        
        logger.info(f"清洗完成: {len(cleaned_articles)}/{len(articles)} 篇文章通过验证")
        return cleaned_articles
    
    def save_cleaned_data(self, articles: List[Dict], output_path: str = "data/cleaned_articles.json"):
        """保存清洗后的数据"""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"清洗后的数据已保存到 {output_path}")


def main():
    """主函数"""
    # 读取原始数据
    with open('data/raw_articles.json', 'r', encoding='utf-8') as f:
        raw_articles = json.load(f)
    
    # 清洗数据
    cleaner = DataCleaner()
    cleaned_articles = cleaner.clean_dataset(raw_articles)
    
    # 保存结果
    cleaner.save_cleaned_data(cleaned_articles)
    
    print(f"\n✓ 数据清洗完成: {len(cleaned_articles)} 篇文章")


if __name__ == "__main__":
    main()
