"""
数据库初始化脚本
功能：创建数据库和表结构
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """创建数据库（如果不存在）"""
    try:
        # 连接到默认的postgres数据库
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            database='postgres',  # 连接到默认数据库
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '740918'),
            port=os.getenv('DB_PORT', '5432')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        db_name = os.getenv('DB_NAME', 'news_db')
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✓ 数据库 {db_name} 创建成功")
        else:
            print(f"✓ 数据库 {db_name} 已存在")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ 创建数据库失败: {e}")
        raise

def create_tables():
    """创建表结构"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            database=os.getenv('DB_NAME', 'news_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '740918'),
            port=os.getenv('DB_PORT', '5432')
        )
        
        cursor = conn.cursor()
        
        # 创建文章表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                url TEXT UNIQUE NOT NULL,
                source VARCHAR(255),
                published_date DATE,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 表 articles 创建成功")
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_source 
            ON articles(source)
        """)
        print("✓ 索引 idx_articles_source 创建成功")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_published_date 
            ON articles(published_date)
        """)
        print("✓ 索引 idx_articles_published_date 创建成功")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_created_at 
            ON articles(created_at)
        """)
        print("✓ 索引 idx_articles_created_at 创建成功")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ 所有表和索引创建完成")
        
    except Exception as e:
        print(f"✗ 创建表失败: {e}")
        raise

def main():
    """主函数"""
    print("=" * 60)
    print("PostgreSQL 数据库初始化")
    print("=" * 60)
    print()
    
    # 显示配置信息
    print("数据库配置:")
    print(f"  主机: {os.getenv('DB_HOST', '127.0.0.1')}")
    print(f"  端口: {os.getenv('DB_PORT', '5432')}")
    print(f"  数据库: {os.getenv('DB_NAME', 'news_db')}")
    print(f"  用户: {os.getenv('DB_USER', 'postgres')}")
    print()
    
    try:
        # 步骤1: 创建数据库
        print("步骤1: 创建数据库...")
        create_database()
        print()
        
        # 步骤2: 创建表
        print("步骤2: 创建表和索引...")
        create_tables()
        print()
        
        print("=" * 60)
        print("✓ 数据库初始化完成！")
        print("=" * 60)
        print()
        print("现在可以运行以下命令:")
        print("  python scraper.py         # 爬取数据并保存到数据库")
        print("  python db_utils.py        # 查看数据库中的数据")
        print("  python main.py            # 运行完整的数据处理管道")
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ 数据库初始化失败")
        print("=" * 60)
        print()
        print("请检查:")
        print("  1. PostgreSQL服务是否已启动")
        print("  2. .env文件中的数据库配置是否正确")
        print("  3. 数据库用户是否有足够的权限")

if __name__ == "__main__":
    main()
