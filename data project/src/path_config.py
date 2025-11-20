"""
配置文件路径帮助模块
提供统一的路径管理
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# 主要目录
SRC_DIR = PROJECT_ROOT / 'src'
SCRIPTS_DIR = PROJECT_ROOT / 'scripts'
DOCS_DIR = PROJECT_ROOT / 'docs'
CONFIG_DIR = PROJECT_ROOT / 'config'
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'output'
LOGS_DIR = PROJECT_ROOT / 'logs'
TEMP_DIR = PROJECT_ROOT / 'temp'

# 配置文件
CONFIG_FILE = CONFIG_DIR / 'config.json'
ENV_FILE = PROJECT_ROOT / '.env'
ENV_EXAMPLE = CONFIG_DIR / '.env.example'

# 数据文件
RAW_ARTICLES = DATA_DIR / 'raw_articles.json'
CLEANED_ARTICLES = DATA_DIR / 'cleaned_articles.json'
DEDUPLICATED_ARTICLES = DATA_DIR / 'deduplicated_articles.json'
ENTITIES_FILE = DATA_DIR / 'entities.json'
SUMMARY_FILE = DATA_DIR / 'summary.json'
TIMELINE_FILE = DATA_DIR / 'timeline.json'

# 输出文件
HTML_OUTPUT = OUTPUT_DIR / 'topic_summary.html'

# 日志文件
PIPELINE_LOG = LOGS_DIR / 'pipeline.log'

def ensure_directories():
    """确保所有必要的目录存在"""
    for directory in [DATA_DIR, OUTPUT_DIR, LOGS_DIR, TEMP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

def get_config_path():
    """获取配置文件路径"""
    return str(CONFIG_FILE)

def get_data_path(filename):
    """获取数据文件路径"""
    return str(DATA_DIR / filename)

def get_output_path(filename):
    """获取输出文件路径"""
    return str(OUTPUT_DIR / filename)

def get_log_path(filename):
    """获取日志文件路径"""
    return str(LOGS_DIR / filename)

if __name__ == "__main__":
    print("项目路径配置:")
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"源代码目录: {SRC_DIR}")
    print(f"脚本目录: {SCRIPTS_DIR}")
    print(f"文档目录: {DOCS_DIR}")
    print(f"配置目录: {CONFIG_DIR}")
    print(f"数据目录: {DATA_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"日志目录: {LOGS_DIR}")
    print(f"\n配置文件: {CONFIG_FILE}")
    print(f"环境文件: {ENV_FILE}")
