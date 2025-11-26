from . import logger
import dotenv
from .path_config import ENV_FILE

dotenv.load_dotenv(ENV_FILE)  # Load from parent directory

from openai import OpenAI


#!NOTE: should be configurable to use different LLM providers

class OpenAIClient:
    """OpenAI 客户端封装类"""
    
    def __init__(self):
        """初始化客户端"""
        self.api_key = dotenv.get_key(ENV_FILE, "DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 DEEPSEEK_API_KEY，请在 .env 文件中配置")
    
    def __enter__(self):
        """进入上下文管理器"""
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        return self.client
    
    def __exit__(self, exc_type, exc_value, traceback):
        """退出上下文管理器"""
        self.client.close()

def test_openai_client():
    try:
        with OpenAIClient() as client:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Please introduce yourself in one sentence."}
            ],
            max_tokens=100
        )
        print(response.choices[0].message.content)
        logger.info("DeepSeek API connection successful.")
    except Exception as e:
        logger.error(f"DeepSeek API connection failed: {e}")
        raise e


if __name__ == "__main__":
    test_openai_client()