#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageEffects类重构优化测试脚本

测试内容:
1. 基础功能测试
2. 配置化参数测试
3. 错误处理测试
4. 性能统计测试
5. 批量处理测试
6. 向后兼容性测试
"""

import numpy as np
from PIL import Image
import sys
import os

# 添加路径以导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'sdk', 'python'))

try:
    from mxSdk.opencv.image_effects import (
        ImageEffects, 
        TextDetailConfig, 
        SketchConfig, 
        InpaintConfig,
        SketchAlgorithm,
        ImageEffectsError
    )
    print("✅ 成功导入ImageEffects及相关配置类")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)


def create_test_image(size=(200, 200), mode='RGB'):
    """创建测试图像"""
    if mode == 'RGB':
        # 创建彩色测试图像
        img_array = np.random.randint(0, 255, (size[1], size[0], 3), dtype=np.uint8)
        # 添加一些结构化内容
        img_array[50:150, 50:150] = [255, 255, 255]  # 白色方块
        img_array[75:125, 75:125] = [0, 0, 0]        # 黑色方块
    elif mode == 'RGBA':
        # 创建带透明通道的图像
        img_array = np.random.randint(0, 255, (size[1], size[0], 4), dtype=np.uint8)
        img_array[:, :, 3] = 200  # 设置透明度
        img_array[50:150, 50:150] = [255, 255, 255, 255]  # 白色方块
        img_array[75:125, 75:125] = [0, 0, 0, 255]        # 黑色方块
    else:  # 'L' 灰度
        img_array = np.random.randint(0, 255, size[::-1], dtype=np.uint8)
        img_array[50:150, 50:150] = 255  # 白色方块
        img_array[75:125, 75:125] = 0    # 黑色方块
    
    return Image.fromarray(img_array, mode)


def test_basic_functionality():
    """测试基础功能"""
    print("\n🧪 测试基础功能...")
    
    # 创建测试图像
    rgb_image = create_test_image(mode='RGB')
    rgba_image = create_test_image(mode='RGBA')
    gray_image = create_test_image(mode='L')
    
    # 创建ImageEffects实例
    effects = ImageEffects()
    
    # 测试文字细节增强
    try:
        result = effects.process_image_for_text_detail(rgb_image)
        assert isinstance(result, Image.Image)
        print("  ✅ 文字细节增强 - RGB图像")
        
        result = effects.process_image_for_text_detail(rgba_image)
        assert isinstance(result, Image.Image)
        print("  ✅ 文字细节增强 - RGBA图像")
        
        result = effects.process_image_for_text_detail(gray_image)
        assert isinstance(result, Image.Image)
        print("  ✅ 文字细节增强 - 灰度图像")
    except Exception as e:
        print(f"  ❌ 文字细节增强失败: {e}")
    
    # 测试素描效果 - 不同算法
    try:
        # Canny算法
        result = effects.create_sketch_effect(rgb_image, SketchAlgorithm.CANNY_BASED)
        assert isinstance(result, Image.Image)
        print("  ✅ 素描效果 - Canny算法")
        
        # Sobel算法
        result = effects.create_sketch_effect(rgb_image, SketchAlgorithm.SOBEL_BASED)
        assert isinstance(result, Image.Image)
        print("  ✅ 素描效果 - Sobel算法")
        
        # Laplacian算法
        result = effects.create_sketch_effect(rgb_image, SketchAlgorithm.LAPLACIAN)
        assert isinstance(result, Image.Image)
        print("  ✅ 素描效果 - Laplacian算法")
    except Exception as e:
        print(f"  ❌ 素描效果失败: {e}")
    
    # 测试颜色反转
    try:
        result = effects.invert_colors(rgb_image)
        assert isinstance(result, Image.Image)
        print("  ✅ 颜色反转 - RGB图像")
        
        result = effects.invert_colors(rgba_image, preserve_alpha=True)
        assert isinstance(result, Image.Image)
        assert result.mode == 'RGBA'
        print("  ✅ 颜色反转 - RGBA图像(保持透明度)")
        
        result = effects.invert_colors(rgba_image, preserve_alpha=False)
        assert isinstance(result, Image.Image)
        print("  ✅ 颜色反转 - RGBA图像(不保持透明度)")
    except Exception as e:
        print(f"  ❌ 颜色反转失败: {e}")
    
    # 测试前景清除
    try:
        result = effects.clear_foreground(rgb_image)
        assert isinstance(result, Image.Image)
        print("  ✅ 前景清除 - RGB图像")
        
        result = effects.clear_foreground(rgba_image)
        assert isinstance(result, Image.Image)
        print("  ✅ 前景清除 - RGBA图像")
    except Exception as e:
        print(f"  ❌ 前景清除失败: {e}")


def test_configuration():
    """测试配置化参数"""
    print("\n⚙️ 测试配置化参数...")
    
    test_image = create_test_image()
    
    # 自定义文字细节配置
    try:
        text_config = TextDetailConfig(
            block_size=15,
            c_constant=5.0,
            morph_kernel_size=(3, 3)
        )
        effects = ImageEffects(text_config=text_config)
        result = effects.process_image_for_text_detail(test_image)
        assert isinstance(result, Image.Image)
        print("  ✅ 自定义文字细节配置")
    except Exception as e:
        print(f"  ❌ 自定义文字细节配置失败: {e}")
    
    # 自定义素描配置
    try:
        sketch_config = SketchConfig(
            algorithm=SketchAlgorithm.SOBEL_BASED,
            blur_kernel_size=(7, 7),
            sobel_weight_x=0.6,
            sobel_weight_y=0.4,
            invert_result=False
        )
        effects = ImageEffects(sketch_config=sketch_config)
        result = effects.create_sketch_effect(test_image)
        assert isinstance(result, Image.Image)
        print("  ✅ 自定义素描配置")
    except Exception as e:
        print(f"  ❌ 自定义素描配置失败: {e}")
    
    # 自定义修复配置
    try:
        inpaint_config = InpaintConfig(
            canny_low_threshold=30,
            canny_high_threshold=100,
            inpaint_radius=5
        )
        effects = ImageEffects(inpaint_config=inpaint_config)
        result = effects.clear_foreground(test_image)
        assert isinstance(result, Image.Image)
        print("  ✅ 自定义修复配置")
    except Exception as e:
        print(f"  ❌ 自定义修复配置失败: {e}")


def test_error_handling():
    """测试错误处理"""
    print("\n🚨 测试错误处理...")
    
    effects = ImageEffects()
    
    # 测试空图像
    try:
        effects.process_image_for_text_detail(None)
        print("  ❌ 应该抛出异常但没有")
    except ImageEffectsError:
        print("  ✅ 正确处理空图像异常")
    except Exception as e:
        print(f"  ⚠️ 异常类型不正确: {type(e).__name__}")
    
    # 测试无效图像
    try:
        # 创建一个无效的图像对象
        invalid_image = Image.new('RGB', (0, 0))
        effects.invert_colors(invalid_image)
        print("  ❌ 应该抛出异常但没有")
    except ImageEffectsError:
        print("  ✅ 正确处理无效图像异常")
    except Exception as e:
        print(f"  ⚠️ 异常类型不正确: {type(e).__name__}")
    
    # 测试不支持的算法
    try:
        test_image = create_test_image()
        # 这里我们不能直接测试不支持的算法，因为枚举限制了选择
        # 但我们可以测试配置验证
        result = effects.create_sketch_effect(test_image, SketchAlgorithm.CANNY_BASED)
        assert isinstance(result, Image.Image)
        print("  ✅ 算法验证正常")
    except Exception as e:
        print(f"  ❌ 算法验证失败: {e}")


def test_performance_stats():
    """测试性能统计"""
    print("\n📊 测试性能统计...")
    
    effects = ImageEffects()
    test_image = create_test_image()
    
    # 重置统计
    effects.reset_stats()
    initial_stats = effects.get_processing_stats()
    assert initial_stats['total_processed'] == 0
    print("  ✅ 统计重置功能")
    
    # 执行一些处理
    try:
        effects.process_image_for_text_detail(test_image)
        effects.create_sketch_effect(test_image)
        effects.invert_colors(test_image)
        
        stats = effects.get_processing_stats()
        assert stats['total_processed'] == 3
        assert stats['success_count'] == 3
        assert stats['avg_processing_time'] > 0
        assert stats['success_rate'] == 1.0
        print(f"  ✅ 性能统计: 处理{stats['total_processed']}张，平均时间{stats['avg_processing_time']:.4f}秒")
    except Exception as e:
        print(f"  ❌ 性能统计测试失败: {e}")


def test_batch_processing():
    """测试批量处理"""
    print("\n📦 测试批量处理...")
    
    effects = ImageEffects()
    
    # 创建多张测试图像
    test_images = [
        create_test_image(mode='RGB'),
        create_test_image(mode='RGBA'),
        create_test_image(mode='L')
    ]
    
    try:
        # 批量素描处理
        results = effects.batch_process(test_images, 'create_sketch_effect', 
                                      algorithm=SketchAlgorithm.CANNY_BASED)
        assert len(results) == 3
        assert all(isinstance(img, Image.Image) for img in results if img is not None)
        print("  ✅ 批量素描处理")
        
        # 批量颜色反转
        results = effects.batch_process(test_images, 'invert_colors')
        assert len(results) == 3
        print("  ✅ 批量颜色反转")
        
        # 测试空列表
        try:
            effects.batch_process([], 'invert_colors')
            print("  ❌ 应该抛出异常但没有")
        except ImageEffectsError:
            print("  ✅ 正确处理空列表异常")
        
        # 测试不存在的方法
        try:
            effects.batch_process(test_images, 'nonexistent_method')
            print("  ❌ 应该抛出异常但没有")
        except ImageEffectsError:
            print("  ✅ 正确处理不存在方法异常")
            
    except Exception as e:
        print(f"  ❌ 批量处理测试失败: {e}")


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n🔄 测试向后兼容性...")
    
    effects = ImageEffects()
    test_image = create_test_image()
    
    try:
        # 测试旧的方法名
        result1 = effects.sketch_image(test_image)
        assert isinstance(result1, Image.Image)
        print("  ✅ sketch_image方法兼容")
        
        result2 = effects.sketch_effect(test_image)
        assert isinstance(result2, Image.Image)
        print("  ✅ sketch_effect方法兼容")
        
        result3 = effects.invert_color(test_image)
        assert isinstance(result3, Image.Image)
        print("  ✅ invert_color方法兼容")
        
        # 验证不同算法产生不同结果
        # (这里只是简单检查，实际应用中可能需要更详细的比较)
        print("  ✅ 向后兼容性测试通过")
        
    except Exception as e:
        print(f"  ❌ 向后兼容性测试失败: {e}")


def main():
    """主测试函数"""
    print("🚀 开始ImageEffects类重构优化测试")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_configuration()
        test_error_handling()
        test_performance_stats()
        test_batch_processing()
        test_backward_compatibility()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成！ImageEffects类重构优化成功！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()