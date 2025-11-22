"""
DeepSeek API 功能测试脚本
用于验证 API 集成和功能正常工作
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

def test_deepseek_connection():
    """测试 DeepSeek API 连接"""
    print("=" * 60)
    print("测试 DeepSeek API 连接")
    print("=" * 60)
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ 未找到 DEEPSEEK_API_KEY")
        return False
    
    print(f"✓ API Key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # 简单测试
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个有用的助手。"},
                {"role": "user", "content": "请用一句话介绍你自己。"}
            ],
            max_tokens=100
        )
        
        result = response.choices[0].message.content
        print(f"\n✓ API 响应成功")
        print(f"回答: {result}")
        return True
        
    except Exception as e:
        print(f"❌ API 调用失败: {e}")
        return False

def test_summarization():
    """测试摘要生成"""
    print("\n" + "=" * 60)
    print("测试摘要生成功能")
    print("=" * 60)
    
    from summarizer import Summarizer
    
    # 测试文章
    test_articles = [
        {
            "title": "AI Technology Advances",
            "content": "Artificial intelligence has made significant progress this year. "
                      "Major tech companies are investing heavily in AI research and development."
        },
        {
            "title": "Climate Change Summit",
            "content": "World leaders gathered to discuss climate change action plans. "
                      "New commitments were made to reduce carbon emissions by 2030."
        }
    ]
    
    try:
        summarizer = Summarizer()
        summary = summarizer.generate_summary(test_articles)
        
        print(f"\n✓ 摘要生成成功")
        print(f"摘要内容:\n{summary}")
        return True
        
    except Exception as e:
        print(f"❌ 摘要生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_entity_extraction():
    """测试实体提取"""
    print("\n" + "=" * 60)
    print("测试实体提取功能")
    print("=" * 60)
    
    from entity_extractor import EntityExtractor
    
    # 测试文章
    test_articles = [
        {
            "title": "President Biden Visits London",
            "content": "President Joe Biden arrived in London yesterday to meet with "
                      "Prime Minister Rishi Sunak at 10 Downing Street. They discussed "
                      "NATO cooperation and trade agreements between the United States and "
                      "the United Kingdom."
        }
    ]
    
    try:
        extractor = EntityExtractor()
        entities_data = extractor.extract_and_rank(test_articles)
        
        print(f"\n✓ 实体提取成功")
        print(f"提取的实体:")
        print(f"  - 人物: {len(entities_data['entities']['people'])}")
        print(f"  - 组织: {len(entities_data['entities']['organizations'])}")
        print(f"  - 地点: {len(entities_data['entities']['locations'])}")
        
        # 显示具体实体
        if entities_data['entities']['people']:
            print(f"\n人物列表:")
            for entity in entities_data['entities']['people'][:5]:
                print(f"    • {entity['name']} (出现{entity['count']}次)")
        
        if entities_data['entities']['locations']:
            print(f"\n地点列表:")
            for entity in entities_data['entities']['locations'][:5]:
                print(f"    • {entity['name']} (出现{entity['count']}次)")
        
        return True
        
    except Exception as e:
        print(f"❌ 实体提取失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 16 + "DeepSeek API 功能测试" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝\n")
    
    results = []
    
    # 测试1: API连接
    results.append(("API连接", test_deepseek_connection()))
    
    # 测试2: 摘要生成
    results.append(("摘要生成", test_summarization()))
    
    # 测试3: 实体提取
    results.append(("实体提取", test_entity_extraction()))
    
    # 显示测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{status:8} - {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\n总计: {total_passed}/{total_tests} 测试通过")
    
    if total_passed == total_tests:
        print("\n🎉 所有测试通过！DeepSeek API 集成正常工作。")
    else:
        print("\n⚠️ 部分测试失败，请检查配置和日志。")

if __name__ == "__main__":
    main()
