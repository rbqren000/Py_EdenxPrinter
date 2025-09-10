#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BaseUtils修复验证测试

测试修复后的BaseUtils类是否正常工作
"""

import numpy as np
import cv2
from PIL import Image
import sys
import os

# 添加SDK路径
sys.path.append('sdk/python')

try:
    from mxSdk.opencv.base_utils import BaseUtils
    print("✅ 成功导入BaseUtils")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def test_convert_pil_to_opencv():
    """测试PIL到OpenCV转换"""
    print("\n🧪 测试PIL到OpenCV转换...")
    
    try:
        # 创建测试图像
        test_image = Image.new('RGB', (100, 100), color='red')
        
        # 测试转换
        cv_image = BaseUtils.convert_pil_to_opencv(test_image)
        
        assert cv_image.shape == (100, 100, 3), f"形状错误: {cv_image.shape}"
        assert cv_image.dtype == np.uint8, f"数据类型错误: {cv_image.dtype}"
        
        print("✅ PIL到OpenCV转换测试通过")
        
        # 测试错误处理
        try:
            BaseUtils.convert_pil_to_opencv(None)
            print("❌ 错误处理测试失败")
        except ValueError:
            print("✅ 错误处理测试通过")
            
    except Exception as e:
        print(f"❌ PIL到OpenCV转换测试失败: {e}")

def test_prepare_grayscale():
    """测试灰度预处理"""
    print("\n🧪 测试灰度预处理...")
    
    try:
        # 创建测试图像
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # 测试归一化
        gray_norm = BaseUtils.prepare_grayscale(test_image, normalize=True)
        assert gray_norm.dtype == np.float32, f"归一化数据类型错误: {gray_norm.dtype}"
        assert 0 <= np.min(gray_norm) and np.max(gray_norm) <= 1, "归一化范围错误"
        
        # 测试不归一化
        gray_raw = BaseUtils.prepare_grayscale(test_image, normalize=False)
        assert gray_raw.dtype == np.uint8, f"原始数据类型错误: {gray_raw.dtype}"
        
        # 测试灰度图输入
        gray_input = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        gray_output = BaseUtils.prepare_grayscale(gray_input, normalize=True)
        assert gray_output.shape == (100, 100), f"灰度图形状错误: {gray_output.shape}"
        
        print("✅ 灰度预处理测试通过")
        
    except Exception as e:
        print(f"❌ 灰度预处理测试失败: {e}")

def test_adaptive_kernel_size():
    """测试自适应核大小计算"""
    print("\n🧪 测试自适应核大小计算...")
    
    try:
        # 创建不同尺寸的测试图像
        small_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        large_image = np.random.randint(0, 255, (2000, 2000), dtype=np.uint8)
        
        small_kernel = BaseUtils.calculate_adaptive_kernel_size(small_image)
        large_kernel = BaseUtils.calculate_adaptive_kernel_size(large_image)
        
        # 验证核大小是奇数
        assert small_kernel % 2 == 1, f"小图像核大小不是奇数: {small_kernel}"
        assert large_kernel % 2 == 1, f"大图像核大小不是奇数: {large_kernel}"
        
        # 验证大图像的核应该更大
        assert large_kernel >= small_kernel, f"大图像核大小应该更大: {large_kernel} vs {small_kernel}"
        
        print(f"✅ 自适应核大小测试通过 (小图: {small_kernel}, 大图: {large_kernel})")
        
    except Exception as e:
        print(f"❌ 自适应核大小测试失败: {e}")

def test_image_sharp():
    """测试图像锐化"""
    print("\n🧪 测试图像锐化...")
    
    try:
        # 测试float32输入
        test_image_float = np.random.rand(100, 100).astype(np.float32)
        sharpened_float = BaseUtils.image_sharp(test_image_float, amount=100)
        
        assert sharpened_float.dtype == np.float32, f"float32输出类型错误: {sharpened_float.dtype}"
        assert 0 <= np.min(sharpened_float) and np.max(sharpened_float) <= 1, "float32输出范围错误"
        
        # 测试uint8输入
        test_image_uint8 = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        sharpened_uint8 = BaseUtils.image_sharp(test_image_uint8, amount=100)
        
        assert sharpened_uint8.dtype == np.uint8, f"uint8输出类型错误: {sharpened_uint8.dtype}"
        assert 0 <= np.min(sharpened_uint8) and np.max(sharpened_uint8) <= 255, "uint8输出范围错误"
        
        print("✅ 图像锐化测试通过")
        
    except Exception as e:
        print(f"❌ 图像锐化测试失败: {e}")

def test_color_gradation():
    """测试颜色渐变处理"""
    print("\n🧪 测试颜色渐变处理...")
    
    try:
        # 测试float32输入
        test_image_float = np.random.rand(100, 100).astype(np.float32)
        result_float = BaseUtils.color_gradation(test_image_float)
        
        assert result_float.dtype == np.uint8, f"float32输入输出类型错误: {result_float.dtype}"
        
        # 测试uint8输入
        test_image_uint8 = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        result_uint8 = BaseUtils.color_gradation(test_image_uint8)
        
        assert result_uint8.dtype == np.uint8, f"uint8输入输出类型错误: {result_uint8.dtype}"
        
        print("✅ 颜色渐变处理测试通过")
        
    except Exception as e:
        print(f"❌ 颜色渐变处理测试失败: {e}")

def test_four_point_transform():
    """测试四点透视变换"""
    print("\n🧪 测试四点透视变换...")
    
    try:
        # 创建测试图像
        test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        
        # 定义四个点（矩形）
        pts = np.array([
            [50, 50],   # 左上
            [150, 50],  # 右上
            [150, 150], # 右下
            [50, 150]   # 左下
        ], dtype=np.float32)
        
        # 测试透视变换
        warped = BaseUtils.four_point_transform(test_image, pts)
        
        assert warped.shape[2] == 3, f"输出通道数错误: {warped.shape[2]}"
        assert warped.dtype == test_image.dtype, f"输出数据类型错误: {warped.dtype}"
        
        # 测试指定输出尺寸
        warped_sized = BaseUtils.four_point_transform(test_image, pts, output_size=(100, 100))
        assert warped_sized.shape[:2] == (100, 100), f"指定尺寸输出错误: {warped_sized.shape[:2]}"
        
        print("✅ 四点透视变换测试通过")
        
    except Exception as e:
        print(f"❌ 四点透视变换测试失败: {e}")

def test_validate_image():
    """测试图像验证"""
    print("\n🧪 测试图像验证...")
    
    try:
        # 有效图像
        valid_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        assert BaseUtils.validate_image(valid_image) == True, "有效图像验证失败"
        
        # 无效图像
        assert BaseUtils.validate_image(None) == False, "None图像验证失败"
        assert BaseUtils.validate_image(np.array([])) == False, "空数组验证失败"
        
        # 包含NaN的图像
        nan_image = np.random.rand(100, 100).astype(np.float32)
        nan_image[0, 0] = np.nan
        assert BaseUtils.validate_image(nan_image) == False, "NaN图像验证失败"
        
        print("✅ 图像验证测试通过")
        
    except Exception as e:
        print(f"❌ 图像验证测试失败: {e}")

def test_memory_usage():
    """测试内存使用计算"""
    print("\n🧪 测试内存使用计算...")
    
    try:
        # 创建已知大小的图像
        test_image = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
        expected_mb = (1000 * 1000 * 3) / (1024 * 1024)  # 约2.86MB
        
        actual_mb = BaseUtils.get_memory_usage_mb(test_image)
        
        assert abs(actual_mb - expected_mb) < 0.1, f"内存计算错误: {actual_mb} vs {expected_mb}"
        
        # 测试空图像
        assert BaseUtils.get_memory_usage_mb(None) == 0.0, "空图像内存计算错误"
        
        print(f"✅ 内存使用计算测试通过 ({actual_mb:.2f}MB)")
        
    except Exception as e:
        print(f"❌ 内存使用计算测试失败: {e}")

def main():
    """运行所有测试"""
    print("🚀 开始BaseUtils修复验证测试...")
    
    test_convert_pil_to_opencv()
    test_prepare_grayscale()
    test_adaptive_kernel_size()
    test_image_sharp()
    test_color_gradation()
    test_four_point_transform()
    test_validate_image()
    test_memory_usage()
    
    print("\n🎉 所有测试完成！")

if __name__ == "__main__":
    main()