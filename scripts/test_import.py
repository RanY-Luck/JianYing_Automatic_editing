"""测试应用启动"""
import sys
import traceback

try:
    print("1. 测试导入 logger...")
    from backend.utils.logger import setup_logger
    print("✓ Logger OK")
    
    print("\n2. 测试导入 database...")
    from backend.core.database import init_db
    print("✓ Database OK")
    
    print("\n3. 测试导入 Material model...")
    from backend.app.material.model.material import Material
    print("✓ Material model OK")
    
    print("\n4. 测试导入 Draft model...")
    from backend.app.draft.model.draft import Draft
    print("✓ Draft model OK")
    
    print("\n5. 测试导入 main app...")
    from main import app
    print("✓ App OK")
    
    print("\n✅ 所有模块导入成功！")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    print("\n详细错误信息:")
    traceback.print_exc()
    sys.exit(1)
