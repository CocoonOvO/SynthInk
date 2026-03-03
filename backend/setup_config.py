"""配置配置库 - 设置数据库连接等必要配置"""
import asyncio
import os
import sys

# 禁用SSL用于本地开发
os.environ["POSTGRES_DISABLE_SSL"] = "true"

from app.config_db import config_db_manager, DatabaseConfig, DatabaseType, SystemConfig

async def setup():
    """初始化并配置配置库"""
    print("=" * 60)
    print("🐱 喵娘配置助手 - 配置库设置")
    print("=" * 60)
    
    # 初始化配置库
    await config_db_manager.initialize()
    print("✅ 配置库初始化完成")
    
    # 检查现有数据库配置
    existing_config = config_db_manager.get_active_database_config()
    
    if existing_config:
        print(f"\n📋 发现现有数据库配置:")
        print(f"   名称: {existing_config.name}")
        print(f"   类型: {existing_config.db_type.value}")
        print(f"   主机: {existing_config.host}:{existing_config.port}")
        print(f"   数据库: {existing_config.database}")
        print(f"   模式: {getattr(existing_config, 'schema', 'public')}")
        print(f"   用户: {existing_config.username}")
        print(f"   URL: {existing_config.url}")
        
        # 检查是否需要更新
        expected_url = "postgresql+asyncpg://postgres:heat1423@localhost:5432/synthink_test"
        expected_schema = "custom_schema"
        
        needs_update = False
        
        if existing_config.url != expected_url:
            print(f"\n⚠️ 数据库URL不匹配，需要更新")
            print(f"   当前: {existing_config.url}")
            print(f"   期望: {expected_url}")
            needs_update = True
            
        current_schema = getattr(existing_config, 'schema', 'public')
        if current_schema != expected_schema:
            print(f"\n⚠️ 数据库Schema不匹配，需要更新")
            print(f"   当前: {current_schema}")
            print(f"   期望: {expected_schema}")
            needs_update = True
        
        if not needs_update:
            print("\n✅ 数据库配置已是最新，无需更新")
            return
        
        print("\n🔄 正在更新数据库配置...")
    else:
        print("\n⚠️ 未找到数据库配置，正在创建...")
    
    # 创建/更新数据库配置
    db_config = DatabaseConfig(
        name="default",
        db_type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        database="synthink_test",
        schema="custom_schema",  # 使用custom_schema模式
        username="postgres",
        password="heat1423",
        url="postgresql+asyncpg://postgres:heat1423@localhost:5432/synthink_test",
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        is_active=True
    )
    
    config_id = config_db_manager.save_database_config(db_config)
    print(f"✅ 数据库配置已保存 (ID: {config_id})")
    
    # 设置database_url系统配置（用于兼容旧代码）
    db_url_config = SystemConfig(
        key="database_url",
        value="postgresql+asyncpg://postgres:heat1423@localhost:5432/synthink_test",
        value_type="string",
        description="业务数据库连接URL",
        category="database",
        is_editable=True,
        is_secret=True
    )
    config_db_manager.set_system_config(db_url_config)
    print("✅ database_url 系统配置已设置")
    
    # 设置database_schema系统配置
    db_schema_config = SystemConfig(
        key="database_schema",
        value="custom_schema",
        value_type="string",
        description="PostgreSQL数据库Schema名称",
        category="database",
        is_editable=True,
        is_secret=False
    )
    config_db_manager.set_system_config(db_schema_config)
    print("✅ database_schema 系统配置已设置")
    
    # 验证配置
    print("\n📋 验证配置:")
    active_config = config_db_manager.get_active_database_config()
    if active_config:
        print(f"   ✅ 数据库配置: {active_config.name}")
        print(f"   ✅ Schema: {getattr(active_config, 'schema', 'public')}")
    
    db_url = config_db_manager.get_system_config_value("database_url")
    print(f"   ✅ database_url: {db_url}")
    
    db_schema = config_db_manager.get_system_config_value("database_schema")
    print(f"   ✅ database_schema: {db_schema}")
    
    print("\n" + "=" * 60)
    print("🎉 配置库设置完成！喵~")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(setup())
