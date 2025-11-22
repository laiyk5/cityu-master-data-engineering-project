"""
实体提取模块 - Member 3
功能：使用NLP技术识别关键实体（人物、组织、地点等）
"""

import json
from typing import List, Dict, Counter
from collections import Counter
import logging
import re
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('config/.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EntityExtractor:
    """实体提取类"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化实体提取器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.entity_config = self.config['entity_extraction']
        self.min_frequency = self.entity_config['min_entity_frequency']
        
        # 检查是否启用LLM提取（默认启用）
        self.use_llm = self.entity_config.get('use_llm', True)
        self.llm_provider = self.config.get('summarization', {}).get('llm_provider', 'deepseek')
        
        # 初始化LLM客户端
        if self.use_llm:
            self.llm_client = self._init_llm_client()
        else:
            self.llm_client = None
        
        # 只有在未启用LLM或LLM初始化失败时才尝试加载spaCy
        self.nlp = None
        if not self.use_llm or not self.llm_client:
            try:
                import spacy
                model_name = self.entity_config['spacy_model']
                try:
                    self.nlp = spacy.load(model_name)
                    logger.info(f"成功加载spaCy模型: {model_name}")
                except:
                    logger.warning(f"未找到模型 {model_name}，尝试下载...")
                    import os
                    os.system(f"python -m spacy download {model_name}")
                    self.nlp = spacy.load(model_name)
            except Exception as e:
                logger.warning(f"无法加载spaCy: {e}")
                logger.info("将使用基于规则的简单实体提取作为后备方案")
        else:
            logger.info("使用DeepSeek LLM提取实体，跳过spaCy加载")
    
    def _init_llm_client(self):
        """初始化LLM客户端用于实体提取"""
        try:
            if self.llm_provider == 'deepseek':
                from openai import OpenAI
                api_key = os.getenv('DEEPSEEK_API_KEY')
                if not api_key:
                    logger.warning("未找到DEEPSEEK_API_KEY，将使用传统提取方法")
                    return None
                base_url = self.config.get('summarization', {}).get('base_url', 'https://api.deepseek.com')
                client = OpenAI(api_key=api_key, base_url=base_url)
                logger.info("DeepSeek API客户端初始化成功（实体提取）")
                return client
            elif self.llm_provider == 'openai':
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    logger.warning("未找到OPENAI_API_KEY，将使用传统提取方法")
                    return None
                return OpenAI(api_key=api_key)
        except Exception as e:
            logger.error(f"初始化LLM客户端失败: {e}")
            return None
    
    def extract_entities_llm(self, text: str) -> Dict[str, List[str]]:
        """使用LLM API提取实体"""
        if not self.llm_client:
            return self.extract_entities_spacy(text)
        
        try:
            # 截取文本长度
            text_sample = text[:2000]
            
            prompt = f"""请从以下新闻文本中提取关键实体，返回JSON格式。
要求：
1. people: 人物名字列表（政治家、企业家、专家等）
2. organizations: 组织机构列表（公司、政府机构、国际组织等）
3. locations: 地点列表（国家、城市、地区等）
4. dates: 日期列表（重要时间点）

文本：
{text_sample}

请直接返回JSON格式，不要其他说明：
{{"people": [], "organizations": [], "locations": [], "dates": []}}"""
            
            response = self.llm_client.chat.completions.create(
                model=self.config['summarization']['model'],
                messages=[
                    {"role": "system", "content": "你是一个专业的命名实体识别助手，擅长从新闻文本中提取关键实体。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 尝试解析JSON - 处理可能的markdown代码块包裹
            import json
            
            # 打印原始响应用于调试
            logger.debug(f"LLM返回的原始文本: {result_text}")
            
            # 移除可能的markdown代码块标记
            if result_text.startswith('```'):
                # 找到第一个换行符后的内容，到最后一个```之前
                lines = result_text.split('\n')
                result_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else result_text
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            entities = json.loads(result_text)
            logger.info(f"成功解析LLM返回的实体: {len(entities.get('people', []))} 人物, {len(entities.get('organizations', []))} 组织, {len(entities.get('locations', []))} 地点")
            
            # 确保返回正确的格式
            return {
                'people': entities.get('people', []),
                'organizations': entities.get('organizations', []),
                'locations': entities.get('locations', []),
                'dates': entities.get('dates', []),
                'misc': []
            }
            
        except Exception as e:
            logger.error(f"LLM实体提取失败: {e}，切换到spaCy方法")
            return self.extract_entities_spacy(text)
    
    def extract_entities_spacy(self, text: str) -> Dict[str, List[str]]:
        """使用spaCy提取实体"""
        if not self.nlp:
            return self.extract_entities_simple(text)
        
        doc = self.nlp(text[:100000])  # 限制长度避免内存问题
        
        entities = {
            'people': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'misc': []
        }
        
        for ent in doc.ents:
            entity_text = ent.text.strip()
            
            if ent.label_ == 'PERSON':
                entities['people'].append(entity_text)
            elif ent.label_ in ['ORG', 'ORGANIZATION']:
                entities['organizations'].append(entity_text)
            elif ent.label_ in ['GPE', 'LOC', 'LOCATION']:
                entities['locations'].append(entity_text)
            elif ent.label_ == 'DATE':
                entities['dates'].append(entity_text)
            else:
                entities['misc'].append(entity_text)
        
        return entities
    
    def extract_entities_simple(self, text: str) -> Dict[str, List[str]]:
        """简单的基于规则的实体提取（备用方法）"""
        entities = {
            'people': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'misc': []
        }
        
        # 简单的大写词组识别（可能是实体）
        # 匹配连续的大写单词
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'
        matches = re.findall(pattern, text)
        
        for match in matches:
            # 简单分类逻辑
            if any(title in match for title in ['Mr.', 'Mrs.', 'Dr.', 'President', 'Minister']):
                entities['people'].append(match)
            elif any(word in match for word in ['Company', 'Inc.', 'Corp.', 'Organization', 'Association']):
                entities['organizations'].append(match)
            elif any(word in match for word in ['City', 'Country', 'State', 'Province']):
                entities['locations'].append(match)
            else:
                entities['misc'].append(match)
        
        # 日期模式
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        dates = re.findall(date_pattern, text)
        entities['dates'].extend(dates)
        
        return entities
    
    def extract_from_articles(self, articles: List[Dict]) -> Dict[str, List[str]]:
        """从文章列表中提取所有实体"""
        all_entities = {
            'people': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'misc': []
        }
        
        for idx, article in enumerate(articles):
            try:
                # 从标题和内容中提取
                text = f"{article.get('title', '')} {article.get('content', '')}"
                
                # 根据配置选择提取方法
                if self.use_llm and self.llm_client:
                    entities = self.extract_entities_llm(text)
                else:
                    entities = self.extract_entities_spacy(text)
                
                # 合并到总列表
                for category, items in entities.items():
                    all_entities[category].extend(items)
                
                if (idx + 1) % 10 == 0:
                    logger.info(f"已处理 {idx + 1}/{len(articles)} 篇文章")
                    
            except Exception as e:
                logger.error(f"提取文章 {idx} 的实体时出错: {e}")
                continue
        
        return all_entities
    
    def rank_entities(self, entities: Dict[str, List[str]]) -> Dict[str, List[Dict]]:
        """统计并排序实体"""
        ranked = {}
        
        for category, items in entities.items():
            # 统计频率
            counter = Counter(items)
            
            # 过滤低频实体
            filtered = {k: v for k, v in counter.items() if v >= self.min_frequency}
            
            # 排序
            sorted_entities = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
            
            # 转换为字典格式
            ranked[category] = [
                {'name': name, 'count': count}
                for name, count in sorted_entities[:50]  # 只保留前50个
            ]
            
            logger.info(f"{category}: 找到 {len(ranked[category])} 个高频实体")
        
        return ranked
    
    def extract_and_rank(self, articles: List[Dict]) -> Dict:
        """提取并排序实体"""
        logger.info(f"开始从 {len(articles)} 篇文章中提取实体")
        
        # 提取实体
        entities = self.extract_from_articles(articles)
        
        # 统计排序
        ranked_entities = self.rank_entities(entities)
        
        # 生成摘要
        summary = {
            'total_people': len(ranked_entities.get('people', [])),
            'total_organizations': len(ranked_entities.get('organizations', [])),
            'total_locations': len(ranked_entities.get('locations', [])),
            'total_dates': len(ranked_entities.get('dates', []))
        }
        
        return {
            'entities': ranked_entities,
            'summary': summary
        }
    
    def save_entities(self, entities_data: Dict, output_path: str = "data/entities.json"):
        """保存实体数据"""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(entities_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"实体数据已保存到 {output_path}")


def main():
    """主函数"""
    # 读取去重后的数据
    with open('data/deduplicated_articles.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # 提取实体
    extractor = EntityExtractor()
    entities_data = extractor.extract_and_rank(articles)
    
    # 保存结果
    extractor.save_entities(entities_data)
    
    print(f"\n✓ 实体提取完成:")
    print(f"  - 人物: {entities_data['summary']['total_people']}")
    print(f"  - 组织: {entities_data['summary']['total_organizations']}")
    print(f"  - 地点: {entities_data['summary']['total_locations']}")


if __name__ == "__main__":
    main()
