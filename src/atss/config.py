from .path_config import CONFIG_FILE

def get_config():
    """加载配置文件"""
    import json
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config