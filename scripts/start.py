"""
自动化主题摘要页面生成系统 - 启动向导
帮助用户快速开始使用项目
"""

import os
import sys
from pathlib import Path

def print_banner():
    """打印欢迎横幅"""
    print("\n" + "=" * 70)
    print("     自动化主题摘要页面生成系统 - 启动向导")
    print("     Automated Topic Summary Page Generation - Launcher")
    print("=" * 70 + "\n")

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...\n")
    
    issues = []
    
    # 检查 .env 文件
    if not Path('.env').exists():
        issues.append("❌ 未找到 .env 文件")
        print("   建议: 复制 .env.example 为 .env 并配置 API 密钥")
    else:
        print("✓ .env 文件存在")
        
        # 检查 API 密钥
        from dotenv import load_dotenv
        load_dotenv()
        
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if deepseek_key:
            print(f"✓ DeepSeek API Key: {deepseek_key[:10]}...{deepseek_key[-4:]}")
        elif openai_key:
            print(f"✓ OpenAI API Key: {openai_key[:10]}...{openai_key[-4:]}")
        elif anthropic_key:
            print(f"✓ Anthropic API Key: {anthropic_key[:10]}...{anthropic_key[-4:]}")
        else:
            issues.append("⚠️ 未配置任何 LLM API 密钥")
            print("   建议: 在 .env 中添加 DEEPSEEK_API_KEY")
    
    # 检查 config.json
    config_path = Path('config') / 'config.json'
    if not config_path.exists():
        issues.append("❌ 未找到 config/config.json 文件")
    else:
        print("✓ config/config.json 文件存在")
    
    # 检查必要的目录
    for dir_name in ['data', 'output', 'temp']:
        if not Path(dir_name).exists():
            Path(dir_name).mkdir(exist_ok=True)
            print(f"✓ 创建目录: {dir_name}")
        else:
            print(f"✓ 目录存在: {dir_name}")
    
    return issues

def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 70)
    print("请选择操作:")
    print("=" * 70)
    print()
    print("1. 🚀 运行完整管道（从配置的新闻源爬取）")
    print("2. 🔍 主题搜索（搜索特定主题的新闻）")
    print("3. 🧪 测试 DeepSeek API（验证配置）")
    print("4. 🗄️  初始化数据库")
    print("5. 📊 查看数据库数据")
    print("6. 📚 查看文档索引")
    print("7. ⚙️  配置向导")
    print("0. 退出")
    print()
    
    choice = input("请输入选项 (0-7): ").strip()
    return choice

def run_full_pipeline():
    """运行完整管道"""
    print("\n" + "=" * 70)
    print("运行完整管道")
    print("=" * 70 + "\n")
    
    import subprocess
    result = subprocess.run(['python', 'scripts/main.py'], 
                          capture_output=False, 
                          text=True)
    
    if result.returncode == 0:
        print("\n✅ 管道运行成功！")
        print("📄 查看结果: output/topic_summary.html")
    else:
        print("\n❌ 管道运行失败，请查看错误信息")

def run_topic_search():
    """运行主题搜索"""
    print("\n" + "=" * 70)
    print("主题搜索")
    print("=" * 70 + "\n")
    
    import subprocess
    subprocess.run(['python', 'scripts/topic_search.py'])

def test_deepseek():
    """测试 DeepSeek API"""
    print("\n" + "=" * 70)
    print("测试 DeepSeek API")
    print("=" * 70 + "\n")
    
    import subprocess
    subprocess.run(['python', 'scripts/test_deepseek.py'])

def init_database():
    """初始化数据库"""
    print("\n" + "=" * 70)
    print("初始化数据库")
    print("=" * 70 + "\n")
    
    import subprocess
    subprocess.run(['python', 'scripts/init_database.py'])

def view_database():
    """查看数据库数据"""
    print("\n" + "=" * 70)
    print("查看数据库数据")
    print("=" * 70 + "\n")
    
    import subprocess
    subprocess.run(['python', 'scripts/db_utils.py'])

def view_docs():
    """查看文档索引"""
    print("\n" + "=" * 70)
    print("文档索引")
    print("=" * 70 + "\n")
    
    docs = {
        '1': ('README.md', '项目总览和安装指南'),
        '2': ('QUICKSTART_DEEPSEEK.md', 'DeepSeek API 快速开始'),
        '3': ('DATABASE_QUICKSTART.md', '数据库快速配置'),
        '4': ('TOPIC_SEARCH_QUICKREF.md', '主题搜索速查表'),
        '5': ('DEEPSEEK_INTEGRATION.md', 'DeepSeek 完整文档'),
        '6': ('DATABASE_README.md', '数据库完整文档'),
        '7': ('TOPIC_SEARCH_GUIDE.md', '主题搜索指南'),
        '8': ('PROJECT_PLAN.md', '项目规划和分工'),
        '9': ('项目状态总结.md', '项目状态总结'),
        '0': ('文档索引.md', '完整文档索引'),
    }
    
    print("可用文档:")
    for key, (filename, desc) in docs.items():
        print(f"{key}. {filename:30} - {desc}")
    
    print("\n提示: 使用 Markdown 编辑器打开文档以获得最佳阅读体验")
    input("\n按回车键继续...")

def configuration_wizard():
    """配置向导"""
    print("\n" + "=" * 70)
    print("配置向导")
    print("=" * 70 + "\n")
    
    print("1. API 密钥配置")
    print("-" * 70)
    print("编辑 .env 文件并添加以下内容:")
    print()
    print("DEEPSEEK_API_KEY=your-api-key-here")
    print()
    print("获取 DeepSeek API 密钥: https://platform.deepseek.com/")
    print()
    
    print("2. 数据库配置（可选）")
    print("-" * 70)
    print("在 .env 文件中配置 PostgreSQL:")
    print()
    print("DB_HOST=127.0.0.1")
    print("DB_PORT=5432")
    print("DB_NAME=news_db")
    print("DB_USER=postgres")
    print("DB_PASSWORD=your-password")
    print()
    
    print("3. LLM 提供商选择")
    print("-" * 70)
    print("编辑 config.json 中的 llm_provider:")
    print("  - deepseek (推荐)")
    print("  - openai")
    print("  - anthropic")
    print()
    
    input("按回车键继续...")

def main():
    """主函数"""
    print_banner()
    
    # 检查环境
    issues = check_environment()
    
    if issues:
        print("\n⚠️ 发现以下问题:")
        for issue in issues:
            print(f"  {issue}")
        print("\n建议先解决这些问题，或选择配置向导(选项 7)")
    else:
        print("\n✅ 环境检查通过！")
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            run_full_pipeline()
        elif choice == '2':
            run_topic_search()
        elif choice == '3':
            test_deepseek()
        elif choice == '4':
            init_database()
        elif choice == '5':
            view_database()
        elif choice == '6':
            view_docs()
        elif choice == '7':
            configuration_wizard()
        elif choice == '0':
            print("\n感谢使用！再见！👋\n")
            break
        else:
            print("\n❌ 无效的选项，请重新选择")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已中断，再见！👋\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
