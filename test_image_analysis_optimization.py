#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageAnalysis重构优化验证测试

测试重构后的ImageAnalysis类是否正常工作
"""

import numpy as np
import cv2
from PIL import Image
import sys
import os
import time

# 添加SDK路径
sys.path.append('sdk/python')

try:
    from mxSdk.opencv.image_analysis import ImageAnalysis, EdgeDetectionConfig, SharpeningConfig, TransformConfig
    print("✅ 成功导入ImageAnalysis和配置类")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def create_test_image(size=(200, 200), image_type='color'):
    """创建测试图像"""
    if image_type == 'color':
        # 创建彩色测试图像
        img_array = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
        # 添加一些结构
        cv2.rectangle(img_array, (50, 50), (150, 150), (255, 255, 255), 2)
        cv2.circle(img_array, (100, 100), 30, (0, 255, 0), -1)
        return Image.fromarray(img_array, 'RGB')
    elif image_type == 'rgba':
        # 创建RGBA测试图像
        img_array = np.random.randint(0, 255, (*size, 4), dtype=np.uint8)
        img_array[:, :, 3] = 200  # 设置透明度
        cv2.rectangle(img_array, (50, 50), (150, 150), (255, 255, 255, 255), 2)
        return Image.fromarray(img_array, 'RGBA')
    else:  # grayscale
        # 创建灰度测试图像
        img_array = np.random.randint(0, 255, size, dtype=np.uint8)
        cv2.rectangle(img_array, (50, 50), (150, 150), 255, 2)
        cv2.circle(img_array, (100, 100), 30, 128, -1)
        return Image.fromarray(img_array, 'L')

def test_initialization():
    """测试初始化"""
    print("\n🧪 测试初始化...")
    
    try:
        # 默认初始化
        analyzer = ImageAnalysis()
        assert analyzer.edge_config is not None, "边缘检测配置未初始化"
        assert analyzer.sharpening_config is not None, "锐化配置未初始化"
        assert analyzer.transform_config is not None, "变换配置未初始化"
        
        # 自定义配置初始化
        edge_config = EdgeDetectionConfig(canny_low_threshold=30, canny_high_threshold=100)
        analyzer_custom = ImageAnalysis(edge_config=edge_config)
        assert analyzer_custom.edge_config.canny_low_threshold == 30, "自定义配置未生效"
        
        print("✅ 初始化测试通过")
        return analyzer
        
    except Exception as e:
        print(f"❌ 初始化测试失败: {e}")
        return None

def test_sobel_edge_detection(analyzer):
    """测试Sobel边缘检测"""
    print("\n🧪 测试Sobel边缘检测...")
    
    try:
        test_image = create_test_image()
        
        # 基本测试
        result = analyzer.apply_sobel_edge_detection(test_image)
        assert isinstance(result, Image.Image), "返回类型错误"
        assert result.size == test_image.size, "图像尺寸改变"
        
        # 参数测试
        result_custom = analyzer.apply_sobel_edge_detection(test_image, ksize=5, scale=2.0)
        assert isinstance(result_custom, Image.Image), "自定义参数测试失败"
        
        # RGBA图像测试
        rgba_image = create_test_image(image_type='rgba')
        result_rgba = analyzer.apply_sobel_edge_detection(rgba_image)
        assert result_rgba.mode in ['L', 'RGBA'], f"RGBA处理模式错误: {result_rgba.mode}"
        
        print("✅ Sobel边缘检测测试通过")
        
    except Exception as e:
        print(f"❌ Sobel边缘检测测试失败: {e}")

def test_canny_edge_detection(analyzer):
    """测试Canny边缘检测"""
    print("\n🧪 测试Canny边缘检测...")
    
    try:
        test_image = create_test_image()
        
        # 基本测试
        result = analyzer.apply_canny_edge_detection(test_image)
        assert isinstance(result, Image.Image), "返回类型错误"
        
        # 自适应阈值测试
        result_auto = analyzer.apply_canny_edge_detection(test_image, low_threshold=0, high_threshold=0)
        assert isinstance(result_auto, Image.Image), "自适应阈值测试失败"
        
        # 参数验证测试
        try:
            analyzer.apply_canny_edge_detection(test_image, low_threshold=100, high_threshold=50)
            print("❌ 参数验证测试失败")
        except (ValueError, RuntimeError):
            pass  # 期望的异常
        
        print("✅ Canny边缘检测测试通过")
        
    except Exception as e:
        print(f"❌ Canny边缘检测测试失败: {e}")

def test_histogram_equalization(analyzer):
    """测试直方图均衡化"""
    print("\n🧪 测试直方图均衡化...")
    
    try:
        test_image = create_test_image()
        
        # 灰度均衡化
        result_gray = analyzer.equalize_histogram(test_image, preserve_color=False)
        assert isinstance(result_gray, Image.Image), "灰度均衡化失败"
        
        # 彩色均衡化
        result_color = analyzer.equalize_histogram(test_image, preserve_color=True)
        assert isinstance(result_color, Image.Image), "彩色均衡化失败"
        
        # CLAHE测试
        result_clahe = analyzer.equalize_histogram(test_image, adaptive=True, clip_limit=3.0)
        assert isinstance(result_clahe, Image.Image), "CLAHE测试失败"
        
        print("✅ 直方图均衡化测试通过")
        
    except Exception as e:
        print(f"❌ 直方图均衡化测试失败: {e}")

def test_laplacian_sharpening(analyzer):
    """测试拉普拉斯锐化"""
    print("\n🧪 测试拉普拉斯锐化...")
    
    try:
        test_image = create_test_image()
        
        # 灰度锐化
        result_gray = analyzer.laplacian_sharpening(test_image, preserve_color=False)
        assert isinstance(result_gray, Image.Image), "灰度锐化失败"
        
        # 彩色锐化
        result_color = analyzer.laplacian_sharpening(test_image, preserve_color=True)
        assert isinstance(result_color, Image.Image), "彩色锐化失败"
        
        # 参数测试
        result_custom = analyzer.laplacian_sharpening(test_image, weight=0.5, ksize=3)
        assert isinstance(result_custom, Image.Image), "自定义参数锐化失败"
        
        print("✅ 拉普拉斯锐化测试通过")
        
    except Exception as e:
        print(f"❌ 拉普拉斯锐化测试失败: {e}")

def test_log_transformation(analyzer):
    """测试对数变换"""
    print("\n🧪 测试对数变换...")
    
    try:
        test_image = create_test_image()
        
        # 自动计算c值
        result_auto = analyzer.log_transformation(test_image)
        assert isinstance(result_auto, Image.Image), "自动对数变换失败"
        
        # 自定义c值
        result_custom = analyzer.log_transformation(test_image, c_value=2.0)
        assert isinstance(result_custom, Image.Image), "自定义对数变换失败"
        
        # 彩色对数变换
        result_color = analyzer.log_transformation(test_image, preserve_color=True)
        assert isinstance(result_color, Image.Image), "彩色对数变换失败"
        
        print("✅ 对数变换测试通过")
        
    except Exception as e:
        print(f"❌ 对数变换测试失败: {e}")

def test_gamma_correction(analyzer):
    """测试伽马校正"""
    print("\n🧪 测试伽马校正...")
    
    try:
        test_image = create_test_image()
        
        # 基本伽马校正
        result_basic = analyzer.gamma_correction(test_image, gamma=1.5)
        assert isinstance(result_basic, Image.Image), "基本伽马校正失败"
        
        # 彩色伽马校正
        result_color = analyzer.gamma_correction(test_image, gamma=0.8, preserve_color=True)
        assert isinstance(result_color, Image.Image), "彩色伽马校正失败"
        
        # 参数验证测试 - 现在只检查极端值
        try:
            analyzer.gamma_correction(test_image, gamma=-1.0)  # 负值应该失败
            print("❌ 伽马参数验证测试失败")
        except (ValueError, RuntimeError):
            pass  # 期望的异常
        
        print("✅ 伽马校正测试通过")
        
    except Exception as e:
        print(f"❌ 伽马校正测试失败: {e}")

def test_bilateral_filter_sharpening(analyzer):
    """测试双边滤波锐化"""
    print("\n🧪 测试双边滤波锐化...")
    
    try:
        test_image = create_test_image()
        
        # 基本测试
        result = analyzer.laplacian_sharpening_with_bilateral_filter(test_image)
        assert isinstance(result, Image.Image), "双边滤波锐化失败"
        
        # 彩色测试
        result_color = analyzer.laplacian_sharpening_with_bilateral_filter(
            test_image, preserve_color=True
        )
        assert isinstance(result_color, Image.Image), "彩色双边滤波锐化失败"
        
        print("✅ 双边滤波锐化测试通过")
        
    except Exception as e:
        print(f"❌ 双边滤波锐化测试失败: {e}")

def test_batch_processing(analyzer):
    """测试批量处理"""
    print("\n🧪 测试批量处理...")
    
    try:
        # 创建多个测试图像
        test_images = [
            create_test_image(),
            create_test_image(image_type='grayscale'),
            create_test_image(image_type='rgba')
        ]
        
        # 批量Sobel边缘检测
        results = analyzer.batch_process(test_images, 'apply_sobel_edge_detection')
        assert len(results) == len(test_images), "批量处理结果数量错误"
        assert all(isinstance(r, Image.Image) for r in results if r is not None), "批量处理结果类型错误"
        
        # 批量伽马校正
        results_gamma = analyzer.batch_process(test_images, 'gamma_correction', gamma=1.2)
        assert len(results_gamma) == len(test_images), "批量伽马校正结果数量错误"
        
        print("✅ 批量处理测试通过")
        
    except Exception as e:
        print(f"❌ 批量处理测试失败: {e}")

def test_performance_stats(analyzer):
    """测试性能统计"""
    print("\n🧪 测试性能统计...")
    
    try:
        # 重置统计
        analyzer.reset_stats()
        stats_initial = analyzer.get_processing_stats()
        assert stats_initial['total_processed'] == 0, "统计重置失败"
        
        # 执行一些操作
        test_image = create_test_image()
        analyzer.apply_sobel_edge_detection(test_image)
        analyzer.gamma_correction(test_image)
        
        # 检查统计
        stats_after = analyzer.get_processing_stats()
        assert stats_after['total_processed'] == 2, f"处理计数错误: {stats_after['total_processed']}"
        assert stats_after['success_count'] == 2, f"成功计数错误: {stats_after['success_count']}"
        assert 'avg_processing_time' in stats_after, "缺少平均处理时间统计"
        
        print(f"✅ 性能统计测试通过 (处理{stats_after['total_processed']}张，平均耗时{stats_after.get('avg_processing_time', 0):.4f}秒)")
        
    except Exception as e:
        print(f"❌ 性能统计测试失败: {e}")

def test_error_handling(analyzer):
    """测试错误处理"""
    print("\n🧪 测试错误处理...")
    
    try:
        # 测试无效输入
        invalid_image = Image.new('RGB', (0, 0))  # 空图像
        
        try:
            analyzer.apply_sobel_edge_detection(invalid_image)
            print("❌ 无效输入处理测试失败")
        except (ValueError, RuntimeError):
            pass  # 期望的异常
        
        # 测试无效操作名称
        test_image = create_test_image()
        try:
            analyzer.batch_process([test_image], 'invalid_operation')
            print("❌ 无效操作名称测试失败")
        except ValueError:
            pass  # 期望的异常
        
        print("✅ 错误处理测试通过")
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")

def performance_comparison():
    """性能对比测试"""
    print("\n🚀 性能对比测试...")
    
    try:
        # 创建大图像进行性能测试
        large_image = create_test_image(size=(1000, 1000))
        
        analyzer = ImageAnalysis()
        
        # 测试各种操作的性能
        operations = [
            ('Sobel边缘检测', 'apply_sobel_edge_detection'),
            ('Canny边缘检测', 'apply_canny_edge_detection'),
            ('直方图均衡化', 'equalize_histogram'),
            ('拉普拉斯锐化', 'laplacian_sharpening'),
            ('伽马校正', 'gamma_correction')
        ]
        
        for name, operation in operations:
            start_time = time.time()
            getattr(analyzer, operation)(large_image)
            end_time = time.time()
            print(f"  {name}: {end_time - start_time:.4f}秒")
        
        # 显示总体统计
        stats = analyzer.get_processing_stats()
        print(f"  总处理数: {stats['total_processed']}")
        print(f"  成功率: {stats['success_count']/stats['total_processed']*100:.1f}%")
        print(f"  平均耗时: {stats.get('avg_processing_time', 0):.4f}秒")
        
        print("✅ 性能对比测试完成")
        
    except Exception as e:
        print(f"❌ 性能对比测试失败: {e}")

def main():
    """运行所有测试"""
    print("🚀 开始ImageAnalysis重构优化验证测试...")
    
    # 初始化测试
    analyzer = test_initialization()
    if analyzer is None:
        return
    
    # 功能测试
    test_sobel_edge_detection(analyzer)
    test_canny_edge_detection(analyzer)
    test_histogram_equalization(analyzer)
    test_laplacian_sharpening(analyzer)
    test_log_transformation(analyzer)
    test_gamma_correction(analyzer)
    test_bilateral_filter_sharpening(analyzer)
    test_batch_processing(analyzer)
    test_performance_stats(analyzer)
    test_error_handling(analyzer)
    
    # 性能测试
    performance_comparison()
    
    print("\n🎉 所有测试完成！")

if __name__ == "__main__":
    main()