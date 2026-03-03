#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查PostgreSQL安装和数据库状态"""

import subprocess
import sys

def check_psycopg2():
    """检查psycopg2是否安装"""
    try:
        import psycopg2
        print("✅ psycopg2已安装")
        return True
    except ImportError:
        print("❌ psycopg2未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        print("✅ psycopg2安装完成")
        return True

def check_postgres_connection():
    """检查PostgreSQL连接"""
    try:
        import psycopg2
        # 使用主人提供的密码连接
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="heat1423",
            database="postgres"
        )
        print("✅ 成功连接到PostgreSQL")
        
        # 获取版本信息
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"📦 PostgreSQL版本: {version}")
        
        # 获取所有数据库
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cur.fetchall()
        print(f"\n📚 现有数据库列表 ({len(databases)}个):")
        for db in databases:
            print(f"   • {db[0]}")
        
        # 获取所有用户
        cur.execute("SELECT usename FROM pg_user;")
        users = cur.fetchall()
        print(f"\n👤 现有用户列表 ({len(users)}个):")
        for user in users:
            print(f"   • {user[0]}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def main():
    print("=" * 50)
    print("🔍 PostgreSQL 安装检查报告")
    print("=" * 50)
    
    check_psycopg2()
    print()
    check_postgres_connection()
    
    print("\n" + "=" * 50)
    print("检查完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
