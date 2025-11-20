"""
智能主题新闻源发现模块
使用 DeepSeek API 智能查找和推荐相关新闻源
"""

import os
import json
import logging
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class IntelligentSourceFinder:
    """智能新闻源查找器"""
    
    def __init__(self):
        """初始化查找器"""
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        
        if not self.api_key:
            raise ValueError("未找到 DEEPSEEK_API_KEY，请在 .env 文件中配置")
        
        # 初始化 DeepSeek 客户端
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            logger.info("DeepSeek API 客户端初始化成功")
        except Exception as e:
            logger.error(f"初始化 DeepSeek 客户端失败: {e}")
            raise
    
    def find_news_sources(self, topic: str, max_sources: int = 5) -> List[Dict]:
        """
        使用 DeepSeek API 查找与主题相关的新闻源
        
        Args:
            topic: 搜索主题
            max_sources: 最多返回的新闻源数量
            
        Returns:
            新闻源列表，每个源包含 name, url, description
        """
        prompt = f"""请为主题"{topic}"推荐{max_sources}个最相关的新闻网站来源。

要求：
1. 推荐权威、可信的新闻媒体网站
2. 网站应该经常报道与"{topic}"相关的内容
3. 包含国内外主流媒体
4. 每个网站包含：名称、网址、简短描述

请直接返回JSON格式，格式如下：
{{
  "sources": [
    {{
      "name": "网站名称",
      "url": "完整网址（https://开头）",
      "description": "为什么这个网站适合此主题（20字内）"
    }}
  ]
}}

只返回JSON，不要其他解释。"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的新闻媒体推荐专家，擅长根据主题推荐最相关的新闻来源。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            logger.debug(f"API 返回: {result_text}")
            
            # 解析 JSON
            result_text = self._clean_json_response(result_text)
            sources_data = json.loads(result_text)
            
            sources = sources_data.get('sources', [])
            logger.info(f"成功获取 {len(sources)} 个新闻源推荐")
            
            return sources[:max_sources]
            
        except Exception as e:
            logger.error(f"使用 DeepSeek API 查找新闻源失败: {e}")
            # 返回备用新闻源
            return self._get_fallback_sources(topic)
    
    def find_specific_urls(self, topic: str, source_name: str = None, max_urls: int = 3) -> List[str]:
        """
        使用 DeepSeek API 查找特定主题的具体文章URL
        
        Args:
            topic: 搜索主题
            source_name: 指定新闻源名称（可选）
            max_urls: 最多返回的URL数量
            
        Returns:
            推荐的文章URL列表
        """
        source_info = f"来自{source_name}网站的" if source_name else ""
        
        prompt = f"""请推荐{max_urls}个关于"{topic}"主题的{source_info}新闻文章URL。

要求：
1. URL必须是真实存在的新闻文章页面
2. 文章应该与"{topic}"高度相关
3. 优先推荐最近发布的文章
4. URL格式正确且可访问

请直接返回JSON格式：
{{
  "urls": [
    {{
      "url": "完整文章URL",
      "title": "文章标题",
      "relevance": "相关性说明（15字内）"
    }}
  ]
}}

只返回JSON，不要其他解释。"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的新闻搜索专家，擅长查找相关新闻文章。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            result_text = self._clean_json_response(result_text)
            urls_data = json.loads(result_text)
            
            urls = [item['url'] for item in urls_data.get('urls', [])]
            logger.info(f"成功获取 {len(urls)} 个文章URL推荐")
            
            return urls[:max_urls]
            
        except Exception as e:
            logger.error(f"使用 DeepSeek API 查找文章URL失败: {e}")
            return []
    
    def _clean_json_response(self, text: str) -> str:
        """清理 API 返回的文本，提取 JSON"""
        # 移除 markdown 代码块标记
        if text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1]) if len(lines) > 2 else text
            text = text.replace('```json', '').replace('```', '').strip()
        
        return text
    
    def _get_fallback_sources(self, topic: str) -> List[Dict]:
        """返回备用新闻源（当API调用失败时）"""
        logger.info("使用备用新闻源列表")
        
        # 根据主题关键词智能选择备用源
        topic_lower = topic.lower()
        
        fallback_sources = []
        
        # 技术类主题
        if any(word in topic_lower for word in ['ai', 'tech', 'technology', '科技', '人工智能', 'blockchain', '区块链']):
            fallback_sources.extend([
                {"name": "TechCrunch", "url": "https://techcrunch.com", "description": "领先的科技新闻媒体"},
                {"name": "The Verge", "url": "https://www.theverge.com", "description": "科技和文化新闻"},
                {"name": "Wired", "url": "https://www.wired.com", "description": "科技、商业和文化"}
            ])
        
        # 商业财经类
        if any(word in topic_lower for word in ['business', 'economy', '经济', '商业', 'finance', '金融']):
            fallback_sources.extend([
                {"name": "Bloomberg", "url": "https://www.bloomberg.com", "description": "全球商业和金融新闻"},
                {"name": "Financial Times", "url": "https://www.ft.com", "description": "国际商业新闻"},
                {"name": "CNBC", "url": "https://www.cnbc.com", "description": "商业和金融新闻"}
            ])
        
        # 国际新闻
        if any(word in topic_lower for word in ['world', 'international', '国际', 'global', 'war', '战争']):
            fallback_sources.extend([
                {"name": "BBC News", "url": "https://www.bbc.com/news", "description": "国际新闻报道"},
                {"name": "Reuters", "url": "https://www.reuters.com", "description": "全球新闻通讯社"},
                {"name": "Al Jazeera", "url": "https://www.aljazeera.com", "description": "中东和国际新闻"}
            ])
        
        # 通用新闻（默认）
        if not fallback_sources:
            fallback_sources = [
                {"name": "BBC News", "url": "https://www.bbc.com/news", "description": "权威国际新闻"},
                {"name": "CNN", "url": "https://www.cnn.com", "description": "全球新闻网络"},
                {"name": "The Guardian", "url": "https://www.theguardian.com", "description": "英国主流媒体"},
                {"name": "New York Times", "url": "https://www.nytimes.com", "description": "美国主流报纸"},
                {"name": "Associated Press", "url": "https://apnews.com", "description": "全球新闻通讯社"}
            ]
        
        return fallback_sources[:5]


def main():
    """测试功能"""
    print("=" * 70)
    print("智能新闻源查找测试")
    print("=" * 70)
    
    finder = IntelligentSourceFinder()
    
    # 测试1: 查找新闻源
    topic = input("\n请输入主题: ").strip() or "人工智能"
    print(f"\n正在为主题 '{topic}' 查找新闻源...")
    
    sources = finder.find_news_sources(topic, max_sources=5)
    
    print(f"\n找到 {len(sources)} 个相关新闻源:")
    for i, source in enumerate(sources, 1):
        print(f"\n{i}. {source['name']}")
        print(f"   URL: {source['url']}")
        print(f"   说明: {source.get('description', 'N/A')}")
    
    # 测试2: 查找具体URL（可选）
    if sources and input("\n是否查找具体文章URL? (y/n): ").lower() == 'y':
        source_name = sources[0]['name']
        print(f"\n正在查找 {source_name} 关于 '{topic}' 的文章...")
        
        urls = finder.find_specific_urls(topic, source_name, max_urls=3)
        
        print(f"\n找到 {len(urls)} 个相关文章:")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")


if __name__ == "__main__":
    main()
