"""
时间线生成模块 - Member 4
功能：从文章中提取和组织时间线
"""

import json
from typing import List, Dict
from datetime import datetime
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimelineGenerator:
    """时间线生成类"""
    
    def __init__(self):
        """初始化时间线生成器"""
        pass
    
    def parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        try:
            # 尝试多种格式
            formats = [
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%d-%m-%Y",
                "%d/%m/%Y",
                "%Y-%m-%dT%H:%M:%S",
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
            
            # 默认返回当前日期
            return datetime.now()
            
        except:
            return datetime.now()
    
    def extract_timeline_events(self, articles: List[Dict]) -> List[Dict]:
        """从文章中提取时间线事件"""
        events_by_date = defaultdict(list)
        
        for article in articles:
            date_str = article.get('published_date', '')
            if not date_str:
                continue
            
            try:
                date = self.parse_date(date_str)
                date_key = date.strftime("%Y-%m-%d")
                
                event = {
                    'title': article.get('title', ''),
                    'source': article.get('source', ''),
                    'url': article.get('url', ''),
                    'content_snippet': article.get('content', '')[:150] + '...'
                }
                
                events_by_date[date_key].append(event)
                
            except Exception as e:
                logger.warning(f"解析日期失败: {date_str}")
                continue
        
        return events_by_date
    
    def create_timeline(self, articles: List[Dict]) -> List[Dict]:
        """创建时间线"""
        logger.info(f"从 {len(articles)} 篇文章创建时间线")
        
        # 提取事件
        events_by_date = self.extract_timeline_events(articles)
        
        # 按日期排序
        sorted_dates = sorted(events_by_date.keys())
        
        timeline = []
        for date in sorted_dates:
            events = events_by_date[date]
            
            # 为每个日期创建一个条目
            timeline_entry = {
                'date': date,
                'event_count': len(events),
                'main_event': events[0]['title'] if events else '',
                'events': events
            }
            
            timeline.append(timeline_entry)
        
        logger.info(f"时间线创建完成，共 {len(timeline)} 个时间点")
        return timeline
    
    def generate_timeline_summary(self, timeline: List[Dict]) -> str:
        """生成时间线摘要文本"""
        if not timeline:
            return "暂无时间线数据"
        
        summary = "事件时间线：\n\n"
        
        for entry in timeline:
            date = entry['date']
            main_event = entry['main_event']
            event_count = entry['event_count']
            
            summary += f"📅 {date}:\n"
            summary += f"  • {main_event}\n"
            if event_count > 1:
                summary += f"  （共 {event_count} 个相关事件）\n"
            summary += "\n"
        
        return summary
    
    def save_timeline(self, timeline: List[Dict], output_path: str = "data/timeline.json"):
        """保存时间线数据"""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        data = {
            'timeline': timeline,
            'generated_at': datetime.now().isoformat(),
            'total_events': sum(entry['event_count'] for entry in timeline)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"时间线已保存到 {output_path}")


def main():
    """主函数"""
    # 读取去重后的文章
    with open('data/deduplicated_articles.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # 生成时间线
    generator = TimelineGenerator()
    timeline = generator.create_timeline(articles)
    
    # 生成摘要
    summary = generator.generate_timeline_summary(timeline)
    
    # 保存结果
    generator.save_timeline(timeline)
    
    print(f"\n✓ 时间线生成完成，共 {len(timeline)} 个时间点")
    print(f"\n{summary[:300]}...")


if __name__ == "__main__":
    main()
