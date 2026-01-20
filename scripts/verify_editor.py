"""
验证智能剪辑功能模块导入
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试所有新增模块的导入"""
    print("=" * 60)
    print("测试智能剪辑功能模块导入")
    print("=" * 60)
    
    try:
        # 测试滤镜库
        print("\n[1/5] 测试滤镜库导入...")
        from backend.integrations.jianying_api.filter_library import FilterLibrary, FilterCategory, FilterPresets
        print("✅ 滤镜库导入成功")
        print(f"   - 可用滤镜数量: {len(FilterLibrary.FILTERS)}")
        print(f"   - 滤镜分类: {[c.value for c in FilterCategory]}")
        
        # 测试转场库
        print("\n[2/5] 测试转场库导入...")
        from backend.integrations.jianying_api.transition_library import TransitionLibrary, TransitionCategory, TransitionPresets
        print("✅ 转场库导入成功")
        print(f"   - 可用转场数量: {len(TransitionLibrary.TRANSITIONS)}")
        print(f"   - 转场分类: {[c.value for c in TransitionCategory]}")
        
        # 测试 DraftEditor
        print("\n[3/5] 测试 DraftEditor 导入...")
        from backend.integrations.jianying_api.draft_editor import DraftEditor
        print("✅ DraftEditor 导入成功")
        
        # 检查新增方法
        methods = [
            'add_filter', 'add_transition', 'split_segment', 
            'trim_segment', 'adjust_brightness', 'adjust_contrast', 
            'adjust_saturation', 'add_text'
        ]
        for method in methods:
            if hasattr(DraftEditor, method):
                print(f"   ✓ {method}")
            else:
                print(f"   ✗ {method} 未找到")
        
        # 测试 EditorService
        print("\n[4/5] 测试 EditorService 导入...")
        from backend.app.task.service.editor_service import editor_service
        print("✅ EditorService 导入成功")
        
        # 检查新增方法
        service_methods = [
            'add_filter', 'add_transition', 'add_subtitle',
            'split_video', 'trim_video', 'adjust_color', 'add_sticker'
        ]
        for method in service_methods:
            if hasattr(editor_service, method):
                print(f"   ✓ {method}")
            else:
                print(f"   ✗ {method} 未找到")
        
        # 测试 API 路由
        print("\n[5/5] 测试 API 路由导入...")
        from backend.app.api.v1.editor import router
        print("✅ API 路由导入成功")
        print(f"   - 路由数量: {len(router.routes)}")
        
        # 列出所有路由
        print("\n   可用接口:")
        for route in router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods_str = ', '.join(route.methods)
                print(f"   - {methods_str:6} {route.path}")
        
        print("\n" + "=" * 60)
        print("✅ 所有模块导入测试通过!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_filter_library():
    """测试滤镜库功能"""
    print("\n" + "=" * 60)
    print("测试滤镜库功能")
    print("=" * 60)
    
    from backend.integrations.jianying_api.filter_library import FilterLibrary, FilterCategory
    
    # 测试获取滤镜 ID
    filter_id = FilterLibrary.get_filter_id("black_white")
    print(f"\n黑白滤镜 ID: {filter_id}")
    
    # 测试获取滤镜信息
    filter_info = FilterLibrary.get_filter_info("vintage_1980")
    print(f"\n80年代滤镜信息: {filter_info}")
    
    # 测试列出滤镜
    basic_filters = FilterLibrary.list_filters(FilterCategory.BASIC)
    print(f"\n基础滤镜 ({len(basic_filters)} 个):")
    for f in basic_filters:
        print(f"  - {f['name']}: {f['description']}")
    
    # 测试随机滤镜
    random_filter = FilterLibrary.get_random_filter()
    print(f"\n随机滤镜: {random_filter}")


def test_transition_library():
    """测试转场库功能"""
    print("\n" + "=" * 60)
    print("测试转场库功能")
    print("=" * 60)
    
    from backend.integrations.jianying_api.transition_library import TransitionLibrary, TransitionCategory
    
    # 测试获取转场 ID
    transition_id = TransitionLibrary.get_transition_id("fade")
    print(f"\n淡入淡出转场 ID: {transition_id}")
    
    # 测试获取转场信息
    transition_info = TransitionLibrary.get_transition_info("zoom_in")
    print(f"\n放大转场信息: {transition_info}")
    
    # 测试列出转场
    dynamic_transitions = TransitionLibrary.list_transitions(TransitionCategory.DYNAMIC)
    print(f"\n动态转场 ({len(dynamic_transitions)} 个):")
    for t in dynamic_transitions:
        print(f"  - {t['name']}: {t['description']} (默认时长: {t['default_duration']}s)")
    
    # 测试随机转场
    random_transition = TransitionLibrary.get_random_transition()
    print(f"\n随机转场: {random_transition}")


if __name__ == "__main__":
    # 运行所有测试
    success = test_imports()
    
    if success:
        test_filter_library()
        test_transition_library()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成!")
        print("=" * 60)
        print("\n提示:")
        print("1. 启动应用: python main.py")
        print("2. 访问 API 文档: http://localhost:8000/docs")
        print("3. 测试新增的智能剪辑接口")
    else:
        print("\n❌ 测试失败,请检查错误信息")
        sys.exit(1)
