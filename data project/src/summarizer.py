"""
摘要生成模块 - Member 4
功能：使用LLM API生成文章摘要
"""

import json
from typing import List, Dict
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Summarizer:
    """摘要生成类"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化摘要生成器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.summary_config = self.config['summarization']
        self.provider = self.summary_config['llm_provider']
        
        # 加载API密钥
        from dotenv import load_dotenv
        load_dotenv()
        
        # 初始化LLM客户端
        self.client = self._init_llm_client()
    
    def _init_llm_client(self):
        """初始化LLM客户端"""
        try:
            if self.provider == 'deepseek':
                from openai import OpenAI
                api_key = os.getenv('DEEPSEEK_API_KEY')
                if not api_key:
                    logger.warning("未找到DEEPSEEK_API_KEY，将使用模拟模式")
                    return None
                base_url = self.summary_config.get('base_url', 'https://api.deepseek.com')
                client = OpenAI(api_key=api_key, base_url=base_url)
                logger.info("DeepSeek API客户端初始化成功")
                return client
            
            elif self.provider == 'openai':
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    logger.warning("未找到OPENAI_API_KEY，将使用模拟模式")
                    return None
                client = OpenAI(api_key=api_key)
                return client
            
            elif self.provider == 'anthropic':
                from anthropic import Anthropic
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    logger.warning("未找到ANTHROPIC_API_KEY，将使用模拟模式")
                    return None
                return Anthropic(api_key=api_key)
            
        except Exception as e:
            logger.error(f"初始化LLM客户端失败: {e}")
            return None
    
    def generate_summary_deepseek(self, articles: List[Dict]) -> str:
        """使用DeepSeek生成摘要"""
        if not self.client:
            return self.generate_summary_fallback(articles)
        
        try:
            # 准备文章内容
            articles_text = "\n\n".join([
                f"标题: {article.get('title', '')}\n内容: {article.get('content', '')[:500]}"
                for article in articles[:10]  # 限制文章数量
            ])
            
            prompt = f"""请基于以下新闻文章，生成一个全面的主题摘要。摘要应该：
1. 涵盖主要事件和发展
2. 突出关键人物和组织
3. 保持客观和中立
4. 长度约200-300字

文章内容：
{articles_text}

请生成摘要："""
            
            response = self.client.chat.completions.create(
                model=self.summary_config['model'],
                messages=[
                    {"role": "system", "content": "你是一个专业的新闻摘要生成助手。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.summary_config['max_tokens'],
                temperature=self.summary_config['temperature']
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info("DeepSeek API调用成功，摘要已生成")
            return summary
            
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            return self.generate_summary_fallback(articles)
    
    def generate_summary_openai(self, articles: List[Dict]) -> str:
        """使用OpenAI生成摘要"""
        if not self.client:
            return self.generate_summary_fallback(articles)
        
        try:
            # 准备文章内容
            articles_text = "\n\n".join([
                f"标题: {article.get('title', '')}\n内容: {article.get('content', '')[:500]}"
                for article in articles[:10]  # 限制文章数量
            ])
            
            prompt = f"""请基于以下新闻文章，生成一个全面的主题摘要。摘要应该：
1. 涵盖主要事件和发展
2. 突出关键人物和组织
3. 保持客观和中立
4. 长度约200-300字

文章内容：
{articles_text}

请生成摘要："""
            
            response = self.client.chat.completions.create(
                model=self.summary_config['model'],
                messages=[
                    {"role": "system", "content": "你是一个专业的新闻摘要生成助手。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.summary_config['max_tokens'],
                temperature=self.summary_config['temperature']
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            return self.generate_summary_fallback(articles)
    
    def generate_summary_anthropic(self, articles: List[Dict]) -> str:
        """使用Anthropic Claude生成摘要"""
        if not self.client:
            return self.generate_summary_fallback(articles)
        
        try:
            articles_text = "\n\n".join([
                f"标题: {article.get('title', '')}\n内容: {article.get('content', '')[:500]}"
                for article in articles[:10]
            ])
            
            prompt = f"""请基于以下新闻文章，生成一个全面的主题摘要。摘要应该：
1. 涵盖主要事件和发展
2. 突出关键人物和组织
3. 保持客观和中立
4. 长度约200-300字

文章内容：
{articles_text}

请生成摘要："""
            
            message = self.client.messages.create(
                model=self.summary_config['model'],
                max_tokens=self.summary_config['max_tokens'],
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            summary = message.content[0].text.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Anthropic API调用失败: {e}")
            return self.generate_summary_fallback(articles)
    
    def generate_summary_fallback(self, articles: List[Dict]) -> str:
        """备用摘要生成方法（简单拼接）"""
        logger.info("使用备用摘要生成方法")
        
        # 提取所有标题
        titles = [article.get('title', '') for article in articles[:10]]
        
        # 生成简单摘要
        summary = "本次主题涵盖以下主要新闻：\n\n"
        summary += "\n".join([f"• {title}" for title in titles if title])
        
        return summary
    
    def generate_summary(self, articles: List[Dict]) -> str:
        """生成摘要（根据配置选择提供商）"""
        logger.info(f"使用 {self.provider} 生成摘要")
        
        if self.provider == 'deepseek':
            return self.generate_summary_deepseek(articles)
        elif self.provider == 'openai':
            return self.generate_summary_openai(articles)
        elif self.provider == 'anthropic':
            return self.generate_summary_anthropic(articles)
        else:
            return self.generate_summary_fallback(articles)
    
    def save_summary(self, summary: str, output_path: str = "data/summary.json"):
        """保存摘要"""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        data = {
            'summary': summary,
            'generated_at': datetime.now().isoformat(),
            'provider': self.provider
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"摘要已保存到 {output_path}")


def main():
    """主函数"""
    # 读取去重后的文章
    with open('data/deduplicated_articles.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # 生成摘要
    summarizer = Summarizer()
    summary = summarizer.generate_summary(articles)
    
    # 保存结果
    summarizer.save_summary(summary)
    
    print(f"\n✓ 摘要生成完成")
    print(f"\n{summary[:200]}...")


if __name__ == "__main__":
    main()
