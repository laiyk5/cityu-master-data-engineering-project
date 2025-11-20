"""
去重模块 - Member 2
功能：检测和去除重复文章
"""

import json
from typing import List, Dict, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Deduplicator:
    """文章去重类"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        初始化去重器
        
        Args:
            similarity_threshold: 相似度阈值，超过此值认为是重复
        """
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算两段文本的相似度"""
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except:
            return 0.0
    
    def find_duplicates(self, articles: List[Dict]) -> List[Set[int]]:
        """
        找出重复文章组
        
        Returns:
            List[Set[int]]: 每个集合包含一组重复文章的索引
        """
        if not articles:
            return []
        
        # 准备文本数据（使用标题+内容前500字符）
        texts = []
        for article in articles:
            text = f"{article.get('title', '')} {article.get('content', '')[:500]}"
            texts.append(text)
        
        # 计算TF-IDF矩阵
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
        except Exception as e:
            logger.error(f"TF-IDF计算失败: {e}")
            return []
        
        # 计算相似度矩阵
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # 找出重复组
        duplicate_groups = []
        processed = set()
        
        for i in range(len(articles)):
            if i in processed:
                continue
            
            # 找出与当前文章相似的所有文章
            similar_indices = set([i])
            for j in range(i + 1, len(articles)):
                if j in processed:
                    continue
                
                if similarity_matrix[i][j] >= self.similarity_threshold:
                    similar_indices.add(j)
                    processed.add(j)
            
            if len(similar_indices) > 1:
                duplicate_groups.append(similar_indices)
                logger.info(f"发现重复组: {len(similar_indices)} 篇相似文章")
            
            processed.add(i)
        
        return duplicate_groups
    
    def merge_duplicates(self, articles: List[Dict], duplicate_groups: List[Set[int]]) -> Dict:
        """
        合并重复文章
        
        Args:
            articles: 文章列表
            duplicate_groups: 重复组列表
        
        Returns:
            合并后的文章
        """
        merged = {}
        
        for group in duplicate_groups:
            indices = list(group)
            
            # 选择内容最长的作为主文章
            main_idx = max(indices, key=lambda i: len(articles[i].get('content', '')))
            main_article = articles[main_idx].copy()
            
            # 收集所有来源
            sources = set([articles[i]['source'] for i in indices if 'source' in articles[i]])
            main_article['sources'] = list(sources)
            
            # 收集所有URL
            urls = [articles[i]['url'] for i in indices if 'url' in articles[i]]
            main_article['source_urls'] = urls
            
            # 使用最早的发布日期
            dates = [articles[i].get('published_date', '') for i in indices]
            main_article['published_date'] = min(dates) if dates else main_article.get('published_date', '')
            
            # 标记为合并文章
            main_article['is_merged'] = True
            main_article['merged_count'] = len(indices)
            
            merged[main_idx] = main_article
        
        return merged
    
    def deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """
        执行去重操作
        
        Returns:
            去重后的文章列表
        """
        if not articles:
            return []
        
        logger.info(f"开始去重，原始文章数: {len(articles)}")
        
        # 找出重复文章
        duplicate_groups = self.find_duplicates(articles)
        
        if not duplicate_groups:
            logger.info("未发现重复文章")
            return articles
        
        # 合并重复文章
        merged_articles = self.merge_duplicates(articles, duplicate_groups)
        
        # 收集所有需要保留的文章
        all_duplicate_indices = set()
        for group in duplicate_groups:
            all_duplicate_indices.update(group)
        
        # 构建最终列表
        final_articles = []
        for i, article in enumerate(articles):
            if i in merged_articles:
                # 使用合并后的文章
                final_articles.append(merged_articles[i])
            elif i not in all_duplicate_indices:
                # 非重复文章直接保留
                final_articles.append(article)
        
        logger.info(f"去重完成，剩余文章数: {len(final_articles)}")
        logger.info(f"去除/合并了 {len(articles) - len(final_articles)} 篇重复文章")
        
        return final_articles
    
    def save_deduplicated_data(self, articles: List[Dict], output_path: str = "data/deduplicated_articles.json"):
        """保存去重后的数据"""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"去重后的数据已保存到 {output_path}")


def main():
    """主函数"""
    # 读取清洗后的数据
    with open('data/cleaned_articles.json', 'r', encoding='utf-8') as f:
        cleaned_articles = json.load(f)
    
    # 去重
    deduplicator = Deduplicator(similarity_threshold=0.85)
    deduplicated_articles = deduplicator.deduplicate(cleaned_articles)
    
    # 保存结果
    deduplicator.save_deduplicated_data(deduplicated_articles)
    
    print(f"\n✓ 去重完成: 从 {len(cleaned_articles)} 篇减少到 {len(deduplicated_articles)} 篇")


if __name__ == "__main__":
    main()
