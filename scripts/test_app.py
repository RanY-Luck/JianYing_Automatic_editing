"""
测试应用导入和路由注册
"""
import sys

try:
    print("正在导入应用...")
    from main import app
    print("✓ 应用导入成功")
    
    print(f"\n已注册路由数量: {len(app.routes)}")
    
    print("\n路由列表:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ','.join(route.methods) if route.methods else 'N/A'
            print(f"  {methods:10} {route.path}")
    
    print("\n✓ 所有检查通过!")
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
