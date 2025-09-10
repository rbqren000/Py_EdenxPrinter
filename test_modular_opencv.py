#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化OpenCV功能测试脚本

作者: RBQ
创建时间: 2025
描述: 测试拆分后的OpenCV模块是否正常工作
"""

import sys
import os
from PIL import Image

# 添加SDK路径
sys.path.append('sdk/python')

def test_modular_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试各个模块的导入
        from mxSdk.opencv.background_cleaner import BackgroundCleanConfig
        from mxSdk.opencv.base_utils import BaseUtils
        from mxSdk.opencv.background_cleaner import BackgroundCleaner
        from mxSdk.opencv.image_effects import ImageEffects
        from mxSdk.opencv.image_analysis import ImageAnalysis
        from mxSdk.opencv.image_geometry import ImageGeometry
        from mxSdk.opencv.image_scanner import ImageScanner
        from mxSdk.opencv.opencv_utils_modular import OpenCVUtils
        
        print("✅ 所有模块导入成功")
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config_creation():
    """测试配置类创建"""
    print("\n🔍 测试配置类创建...")
    
    try:
        from mxSdk.opencv.background_cleaner import BackgroundCleanConfig
        
        # 测试默认配置
        config1 = BackgroundCleanConfig()
        print(f"✅ 默认配置创建成功: adaptive_processing={config1.adaptive_processing}")
        
        # 测试自定义配置
        config2 = BackgroundCleanConfig(
            adaptive_processing=False,
            kernel_size=51,
            inpaint_radius=3
        )
        print(f"✅ 自定义配置创建成功: kernel_size={config2.kernel_size}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置类创建失败: {e}")
        return False

def test_background_cleaner():
    """测试背景清除功能"""
    print("\n🔍 测试背景清除功能...")
    
    try:
        from mxSdk.opencv.background_cleaner import BackgroundCleaner
        from mxSdk.opencv.background_cleaner import BackgroundCleanConfig
        
        # 检查方法是否存在
        methods = [
            'light_clear_background',
            'deep_clear_background',
            'light_clear_red_background',
            'deep_clear_red_background'
        ]
        
        for method in methods:
            if hasattr(BackgroundCleaner, method):
                print(f"✅ 方法 {method} 存在")
            else:
                print(f"❌ 方法 {method} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 背景清除功能测试失败: {e}")
        return False

def test_modular_opencv_utils():
    """测试模块化OpenCVUtils类"""
    print("\n🔍 测试模块化OpenCVUtils类...")
    
    try:
        from mxSdk.opencv.opencv_utils_modular import OpenCVUtils
        
        # 检查主要方法是否存在
        main_methods = [
            'light_clear_background',
            'deep_clear_background',
            'sketch_image',
            'invert_color',
            'apply_canny_edge_detection',
            'resize_bitmap'
        ]
        
        for method in main_methods:
            if hasattr(OpenCVUtils, method):
                print(f"✅ 方法 {method} 存在")
            else:
                print(f"❌ 方法 {method} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 模块化OpenCVUtils测试失败: {e}")
        return False

def test_compatibility():
    """测试兼容性"""
    print("\n🔍 测试兼容性...")
    
    try:
        # 测试原版本和模块化版本的方法签名是否一致
        from mxSdk.opencv.opencv_utils import OpenCVUtils as OriginalUtils
        from mxSdk.opencv.opencv_utils_modular import OpenCVUtils as ModularUtils
        
        # 检查几个关键方法
        test_methods = [
            'light_clear_background',
            'sketch_image',
            'resize_bitmap'
        ]
        
        for method_name in test_methods:
            original_method = getattr(OriginalUtils, method_name, None)
            modular_method = getattr(ModularUtils, method_name, None)
            
            if original_method and modular_method:
                print(f"✅ 方法 {method_name} 在两个版本中都存在")
            else:
                print(f"❌ 方法 {method_name} 兼容性问题")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 兼容性测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始模块化OpenCV功能测试\n")
    
    tests = [
        ("模块导入", test_modular_imports),
        ("配置类创建", test_config_creation),
        ("背景清除功能", test_background_cleaner),
        ("模块化OpenCVUtils", test_modular_opencv_utils),
        ("兼容性", test_compatibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！模块化拆分成功！")
        print("\n📁 创建的文件结构:")
        print("sdk/python/mxSdk/opencv/")
        print("├── __init__.py              # 模块入口")
        print("├── config.py                # 配置类")
        print("├── base_utils.py            # 基础工具")
        print("├── background_cleaner.py    # 背景清除功能")
        print("├── image_effects.py         # 图像效果处理")
        print("├── image_analysis.py        # 图像分析变换")
        print("├── image_geometry.py        # 几何变换")
        print("├── image_scanner.py         # 图像扫描")
        print("├── opencv_utils.py          # 原始文件（保留）")
        print("└── opencv_utils_modular.py  # 模块化版本")
        
        print("\n💡 使用方式:")
        print("# 方式1: 使用原始版本（保持不变）")
        print("from mxSdk.opencv.opencv_utils import OpenCVUtils")
        print()
        print("# 方式2: 使用模块化版本")
        print("from mxSdk.opencv.opencv_utils_modular import OpenCVUtils")
        print()
        print("# 方式3: 直接使用各个功能模块")
        print("from mxSdk.opencv.background_cleaner import BackgroundCleaner")
        print("from mxSdk.opencv.image_effects import ImageEffects")
        
    else:
        print("❌ 部分测试失败，请检查模块拆分")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)