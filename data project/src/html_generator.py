"""
HTML页面生成模块 - Member 5
功能：生成美观的静态HTML摘要页面
"""

import json
from typing import Dict, List
from datetime import datetime
import os
import logging
from jinja2 import Template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTMLGenerator:
    """HTML生成器类"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化HTML生成器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.output_path = self.config['output']['html_file']
    
    def load_data(self) -> Dict:
        """加载所有生成的数据"""
        data = {}
        
        try:
            # 加载文章
            with open('data/deduplicated_articles.json', 'r', encoding='utf-8') as f:
                data['articles'] = json.load(f)
        except Exception as e:
            logger.warning(f"加载文章数据失败: {e}")
            data['articles'] = []
        
        try:
            # 加载摘要
            with open('data/summary.json', 'r', encoding='utf-8') as f:
                data['summary'] = json.load(f)
        except Exception as e:
            logger.warning(f"加载摘要数据失败: {e}")
            data['summary'] = {'summary': '暂无摘要'}
        
        try:
            # 加载实体
            with open('data/entities.json', 'r', encoding='utf-8') as f:
                data['entities'] = json.load(f)
        except Exception as e:
            logger.warning(f"加载实体数据失败: {e}")
            data['entities'] = {'entities': {}}
        
        try:
            # 加载时间线
            with open('data/timeline.json', 'r', encoding='utf-8') as f:
                data['timeline'] = json.load(f)
        except Exception as e:
            logger.warning(f"加载时间线数据失败: {e}")
            data['timeline'] = {'timeline': []}
        
        return data
    
    def generate_html(self, data: Dict) -> str:
        """生成HTML内容"""
        template_str = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>主题摘要页面</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section-title {
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        
        .summary-box {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            line-height: 1.8;
        }
        
        .entity-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .entity-category {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-top: 3px solid #667eea;
        }
        
        .entity-category h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .entity-list {
            list-style: none;
        }
        
        .entity-item {
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .entity-name {
            font-weight: 500;
        }
        
        .entity-count {
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.85em;
        }
        
        .timeline {
            position: relative;
            padding-left: 30px;
        }
        
        .timeline::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: #667eea;
        }
        
        .timeline-item {
            position: relative;
            margin-bottom: 30px;
            padding-left: 20px;
        }
        
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -35px;
            top: 5px;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background: #667eea;
            border: 3px solid white;
            box-shadow: 0 0 0 3px #667eea;
        }
        
        .timeline-date {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .timeline-event {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }
        
        .articles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .article-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            transition: transform 0.3s, box-shadow 0.3s;
            border-top: 3px solid #667eea;
        }
        
        .article-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .article-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .article-meta {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }
        
        .article-source {
            color: #667eea;
            font-weight: 500;
        }
        
        .article-link {
            display: inline-block;
            margin-top: 10px;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .article-link:hover {
            text-decoration: underline;
        }
        
        .footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
            flex-wrap: wrap;
        }
        
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 40px;
            border-radius: 10px;
            text-align: center;
            min-width: 150px;
            margin: 10px;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 主题摘要页面</h1>
            <p class="subtitle">自动生成的新闻汇总与分析</p>
            <p class="subtitle">生成时间: {{ generated_time }}</p>
        </div>
        
        <div class="content">
            <!-- 统计信息 -->
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">{{ article_count }}</div>
                    <div class="stat-label">文章总数</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{{ entity_count }}</div>
                    <div class="stat-label">关键实体</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{{ timeline_count }}</div>
                    <div class="stat-label">时间节点</div>
                </div>
            </div>
            
            <!-- 主要摘要 -->
            <div class="section">
                <h2 class="section-title">📋 主要摘要</h2>
                <div class="summary-box">
                    {{ summary_text }}
                </div>
            </div>
            
            <!-- 关键实体 -->
            <div class="section">
                <h2 class="section-title">👥 关键实体</h2>
                <div class="entity-grid">
                    {% if entities.people %}
                    <div class="entity-category">
                        <h3>👤 人物</h3>
                        <ul class="entity-list">
                            {% for entity in entities.people[:10] %}
                            <li class="entity-item">
                                <span class="entity-name">{{ entity.name }}</span>
                                <span class="entity-count">{{ entity.count }}</span>
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                    
                    {% if entities.organizations %}
                    <div class="entity-category">
                        <h3>🏢 组织</h3>
                        <ul class="entity-list">
                            {% for entity in entities.organizations[:10] %}
                            <li class="entity-item">
                                <span class="entity-name">{{ entity.name }}</span>
                                <span class="entity-count">{{ entity.count }}</span>
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                    
                    {% if entities.locations %}
                    <div class="entity-category">
                        <h3>📍 地点</h3>
                        <ul class="entity-list">
                            {% for entity in entities.locations[:10] %}
                            <li class="entity-item">
                                <span class="entity-name">{{ entity.name }}</span>
                                <span class="entity-count">{{ entity.count }}</span>
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- 时间线 -->
            <div class="section">
                <h2 class="section-title">📅 事件时间线</h2>
                <div class="timeline">
                    {% for item in timeline[:10] %}
                    <div class="timeline-item">
                        <div class="timeline-date">{{ item.date }}</div>
                        <div class="timeline-event">
                            <strong>{{ item.main_event }}</strong>
                            {% if item.event_count > 1 %}
                            <p style="color: #666; margin-top: 5px;">（共 {{ item.event_count }} 个相关事件）</p>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <!-- 原始文章 -->
            <div class="section">
                <h2 class="section-title">📰 原始文章链接</h2>
                <div class="articles-grid">
                    {% for article in articles[:20] %}
                    <div class="article-card">
                        <div class="article-title">{{ article.title }}</div>
                        <div class="article-meta">
                            <span class="article-source">{{ article.source }}</span> • 
                            <span>{{ article.published_date }}</span>
                        </div>
                        <a href="{{ article.url }}" target="_blank" class="article-link">阅读原文 →</a>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>由自动化主题摘要系统生成 | © 2025</p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        
        # 准备模板数据
        template_data = {
            'generated_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'article_count': len(data.get('articles', [])),
            'entity_count': sum([
                len(data.get('entities', {}).get('entities', {}).get('people', [])),
                len(data.get('entities', {}).get('entities', {}).get('organizations', [])),
                len(data.get('entities', {}).get('entities', {}).get('locations', []))
            ]),
            'timeline_count': len(data.get('timeline', {}).get('timeline', [])),
            'summary_text': data.get('summary', {}).get('summary', '暂无摘要'),
            'entities': data.get('entities', {}).get('entities', {}),
            'timeline': data.get('timeline', {}).get('timeline', []),
            'articles': data.get('articles', [])
        }
        
        html_content = template.render(**template_data)
        return html_content
    
    def save_html(self, html_content: str, topic_name: str = None):
        """保存HTML文件"""
        # 如果提供了主题名称，使用主题名称作为文件名
        if topic_name:
            output_dir = os.path.dirname(self.output_path)
            # 清理主题名称，只保留安全字符
            safe_topic = "".join(c for c in topic_name if c.isalnum() or c in (' ', '-', '_', '（', '）', '(', ')'))
            safe_topic = safe_topic.strip().replace(' ', '_')
            output_file = os.path.join(output_dir, f"{safe_topic}_摘要.html")
        else:
            output_file = self.output_path
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML页面已保存到 {output_file}")
        
        # 返回实际保存的文件路径
        return output_file


def main():
    """主函数"""
    generator = HTMLGenerator()
    
    # 加载数据
    data = generator.load_data()
    
    # 生成HTML
    html_content = generator.generate_html(data)
    
    # 保存文件
    generator.save_html(html_content)
    
    print(f"\n✓ HTML页面生成完成: {generator.output_path}")


if __name__ == "__main__":
    main()
