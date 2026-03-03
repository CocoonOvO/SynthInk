#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复PostgreSQL认证方式以兼容Navicat"""

import os
import subprocess
import shutil
from datetime import datetime

def find_postgres_config():
    """查找PostgreSQL配置文件"""
    # 常见安装路径
    possible_paths = [
        r"C:\Program Files\PostgreSQL\18\data",
        r"C:\Program Files\PostgreSQL\17\data",
        r"C:\Program Files\PostgreSQL\16\data",
        r"C:\Program Files\PostgreSQL\15\data",
        r"C:\Program Files\PostgreSQL\14\data",
        r"C:\ProgramData\PostgreSQL\18\data",
        r"C:\ProgramData\PostgreSQL\17\data",
    ]
    
    for path in possible_paths:
        pg_hba = os.path.join(path, "pg_hba.conf")
        postgresql_conf = os.path.join(path, "postgresql.conf")
        if os.path.exists(pg_hba) and os.path.exists(postgresql_conf):
            return path
    
    # 尝试通过注册表查找
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\postgresql-x64-18")
        image_path, _ = winreg.QueryValueEx(key, "ImagePath")
        winreg.CloseKey(key)
        # 从服务路径推断数据目录
        if "-D" in image_path:
            data_dir = image_path.split("-D")[1].strip().strip('"')
            # 清理可能的多余字符
            data_dir = data_dir.split('"')[0].strip()
            return data_dir
    except:
        pass
    
    return None

def backup_config(data_dir):
    """备份配置文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    pg_hba = os.path.join(data_dir, "pg_hba.conf")
    postgresql_conf = os.path.join(data_dir, "postgresql.conf")
    
    # 备份pg_hba.conf
    if os.path.exists(pg_hba):
        backup_hba = os.path.join(data_dir, f"pg_hba.conf.backup_{timestamp}")
        shutil.copy2(pg_hba, backup_hba)
        print(f"✅ 已备份 pg_hba.conf -> {backup_hba}")
    
    # 备份postgresql.conf
    if os.path.exists(postgresql_conf):
        backup_conf = os.path.join(data_dir, f"postgresql.conf.backup_{timestamp}")
        shutil.copy2(postgresql_conf, backup_conf)
        print(f"✅ 已备份 postgresql.conf -> {backup_conf}")

def fix_pg_hba_conf(data_dir):
    """修改pg_hba.conf使用md5认证"""
    pg_hba_path = os.path.join(data_dir, "pg_hba.conf")
    
    with open(pg_hba_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换 scram-sha-256 为 md5
    new_content = content.replace('scram-sha-256', 'md5')
    
    # 确保本地连接使用md5
    lines = new_content.split('\n')
    new_lines = []
    
    for line in lines:
        # 跳过注释和空行
        if line.strip().startswith('#') or not line.strip():
            new_lines.append(line)
            continue
        
        # 修改IPv4和IPv6连接
        if 'host' in line and 'all' in line:
            parts = line.split()
            if len(parts) >= 4:
                # 替换认证方式为md5
                if 'scram-sha-256' in line:
                    line = line.replace('scram-sha-256', 'md5')
                elif 'trust' not in line and 'reject' not in line:
                    # 如果行中没有指定认证方式，添加md5
                    parts = line.split()
                    if len(parts) >= 4 and parts[0] == 'host':
                        line = line.replace(parts[-1], 'md5') if parts[-1] in ['scram-sha-256', 'password'] else line + ' md5'
        
        new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    
    with open(pg_hba_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 已修改 pg_hba.conf，将认证方式改为 md5")

def fix_postgresql_conf(data_dir):
    """修改postgresql.conf监听配置"""
    conf_path = os.path.join(data_dir, "postgresql.conf")
    
    with open(conf_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 确保监听所有地址
    if "#listen_addresses = 'localhost'" in content:
        content = content.replace("#listen_addresses = 'localhost'", "listen_addresses = '*'")
        print("✅ 已启用监听所有地址")
    
    with open(conf_path, 'w', encoding='utf-8') as f:
        f.write(content)

def restart_postgres():
    """重启PostgreSQL服务"""
    print("\n🔄 正在重启PostgreSQL服务...")
    
    # 尝试停止服务
    try:
        subprocess.run(["net", "stop", "postgresql-x64-18"], check=False, capture_output=True)
    except:
        pass
    
    # 尝试启动服务
    try:
        result = subprocess.run(["net", "start", "postgresql-x64-18"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL服务已重启")
            return True
        else:
            print(f"⚠️ 服务启动失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠️ 重启服务失败: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 PostgreSQL Navicat兼容修复工具")
    print("=" * 60)
    
    # 查找配置目录
    data_dir = find_postgres_config()
    if not data_dir:
        print("❌ 无法找到PostgreSQL数据目录")
        print("请手动检查以下位置:")
        print("  - C:\\Program Files\\PostgreSQL\\18\\data")
        print("  - C:\\ProgramData\\PostgreSQL\\18\\data")
        return
    
    print(f"📁 找到PostgreSQL数据目录: {data_dir}")
    
    # 备份配置
    print("\n📋 正在备份配置文件...")
    backup_config(data_dir)
    
    # 修改配置
    print("\n🔧 正在修改认证配置...")
    fix_pg_hba_conf(data_dir)
    fix_postgresql_conf(data_dir)
    
    # 重启服务
    restart_postgres()
    
    print("\n" + "=" * 60)
    print("✅ 修复完成！")
    print("=" * 60)
    print("\n💡 现在可以使用Navicat连接了：")
    print("   主机: localhost")
    print("   端口: 5432")
    print("   数据库: postgres")
    print("   用户名: postgres")
    print("   密码: heat1423")
    print("\n⚠️ 注意：修改认证方式会降低安全性，建议仅在开发环境使用")

if __name__ == "__main__":
    main()
