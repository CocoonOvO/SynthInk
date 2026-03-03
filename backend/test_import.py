"""测试导入"""
try:
    from app.main import app
    print("✅ Import successful")
    print(f"App title: {app.title}")
    print(f"App version: {app.version}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
