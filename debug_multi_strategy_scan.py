#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多策略身份证扫描调试脚本
"""

import numpy as np
from PIL import Image, ImageDraw
import cv2
import sys
import os

# 添加路径以导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'sdk', 'python'))

from mxSdk.opencv.image_scanner import ImageScanner, IDCardConfig


def create_simple_test_image(size=(300, 200)):
    """创建简单的测试图像"""
    img = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(img)
    
    # 绘制一个简单的矩形
    rect_x = 50
    rect_y = 150
    rect_w = 200
    rect_h = 30
    
    draw.rectangle([rect_x, rect_y, rect_x + rect_w, rect_y + rect_h], 
                  fill='lightgray', outline='black', width=2)
    draw.text((rect_x + 10, rect_y + 8), "123456789012345678", fill='black')
    
    return img


def debug_each_strategy():
    """调试每个策略的执行过程"""
    print("🔍 开始调试多策略身份证扫描...")
    
    # 创建测试图像
    test_image = create_simple_test_image()
    print(f"创建测试图像: {test_image.size}")
    
    # 创建扫描器
    scanner = ImageScanner()
    
    # 手动测试每个策略
    strategies = [
        ("标准配置", scanner._scan_with_standard_config),
        ("宽松配置", scanner._scan_with_loose_config),
        ("自适应配置", scanner._scan_with_adaptive_config),
        ("兜底配置", scanner._scan_with_fallback_config)
    ]
    
    for strategy_name, strategy_func in strategies:
        print(f"\n🧪 测试策略: {strategy_name}")
        try:
            results = strategy_func(test_image, scanner.id_card_config)
            if results:
                print(f"  ✅ 成功找到 {len(results)} 个候选区域")
                for i, result in enumerate(results):
                    print(f"    候选 {i+1}: 区域={result.bbox}, 置信度={result.confidence:.3f}")
            else:
                print(f"  ❌ 未找到任何候选区域")
                
                # 深入调试这个策略
                print(f"  🔧 深入调试 {strategy_name}...")
                debug_strategy_details(test_image, scanner, strategy_name)
                
        except Exception as e:
            print(f"  ❌ 策略执行异常: {e}")
            import traceback
            traceback.print_exc()


def debug_strategy_details(image, scanner, strategy_name):
    """深入调试策略细节"""
    try:
        # 预处理图像
        img_cv, gray = scanner._prepare_image(image)
        print(f"    图像预处理: {gray.shape}")
        
        # 根据策略名称选择配置
        if strategy_name == "标准配置":
            cfg = scanner.id_card_config
        elif strategy_name == "宽松配置":
            cfg = IDCardConfig(
                min_area=100,
                max_area=scanner.id_card_config.max_area * 2,
                aspect_ratio_range=(0.8, 20.0),
                min_width=15,
                min_height=5,
                adaptive_block_size=15,
                adaptive_c=3.0
            )
        elif strategy_name == "自适应配置":
            image_area = gray.shape[0] * gray.shape[1]
            import math
            cfg = IDCardConfig(
                min_area=max(50, int(image_area * 0.001)),
                max_area=min(scanner.id_card_config.max_area, int(image_area * 0.8)),
                aspect_ratio_range=(1.0, 15.0),
                min_width=max(10, int(math.sqrt(image_area) * 0.05)),
                min_height=max(5, int(math.sqrt(image_area) * 0.02)),
                adaptive_block_size=max(3, min(21, int(math.sqrt(image_area) * 0.02))),
                adaptive_c=2.5
            )
        else:  # 兜底配置
            cfg = IDCardConfig(
                min_area=50,
                max_area=999999,
                aspect_ratio_range=(0.5, 50.0),
                min_width=8,
                min_height=3,
                threshold_value=120,
                adaptive_block_size=21,
                adaptive_c=5.0
            )
        
        print(f"    配置参数: min_area={cfg.min_area}, max_area={cfg.max_area}")
        print(f"    宽高比范围: {cfg.aspect_ratio_range}")
        print(f"    最小尺寸: {cfg.min_width}x{cfg.min_height}")
        
        # 预处理
        processed = scanner._preprocess_for_scanning(
            gray, cfg.gaussian_blur_kernel, cfg.gaussian_sigma
        )
        print(f"    预处理完成: {processed.shape}")
        
        # 阈值处理
        binary = scanner._adaptive_threshold(processed, cfg)
        print(f"    阈值处理: {binary.shape}, 唯一值: {np.unique(binary)}")
        
        # 形态学操作
        morphed = scanner._morphological_operations(binary, cfg)
        print(f"    形态学操作: {morphed.shape}")
        
        # 轮廓检测
        contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(f"    检测到轮廓: {len(contours)}")
        
        if contours:
            image_area = gray.shape[0] * gray.shape[1]
            print(f"    图像面积: {image_area}")
            
            # 分析前5个轮廓
            for i, contour in enumerate(contours[:5]):
                area = cv2.contourArea(contour)
                rect = cv2.boundingRect(contour)
                x, y, w, h = rect
                aspect_ratio = w / h if h > 0 else 0
                
                print(f"    轮廓 {i}: 面积={area}, 边界框=({x},{y},{w},{h}), 宽高比={aspect_ratio:.2f}")
                
                # 检查筛选条件
                area_ok = cfg.min_area <= area <= cfg.max_area
                size_ok = w >= cfg.min_width and h >= cfg.min_height
                ratio_ok = cfg.aspect_ratio_range[0] <= aspect_ratio <= cfg.aspect_ratio_range[1]
                
                print(f"      面积检查: {area_ok} ({cfg.min_area} <= {area} <= {cfg.max_area})")
                print(f"      尺寸检查: {size_ok} (w>={cfg.min_width}, h>={cfg.min_height})")
                print(f"      宽高比检查: {ratio_ok} ({cfg.aspect_ratio_range[0]} <= {aspect_ratio:.2f} <= {cfg.aspect_ratio_range[1]})")
                
                if area_ok and size_ok and ratio_ok:
                    confidence = scanner._calculate_id_card_confidence(contour, rect, area, image_area, cfg)
                    print(f"      置信度: {confidence:.3f}")
                    
                    if confidence > 0.05:
                        print(f"      ✅ 轮廓 {i} 通过所有检查！")
                    else:
                        print(f"      ❌ 轮廓 {i} 置信度过低")
                else:
                    print(f"      ❌ 轮廓 {i} 未通过基本检查")
        else:
            print("    ❌ 未检测到任何轮廓")
            
            # 尝试更简单的处理
            print("    🔧 尝试更简单的处理...")
            simple_binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
            simple_contours, _ = cv2.findContours(simple_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            print(f"    简单阈值检测到轮廓: {len(simple_contours)}")
            
            if simple_contours:
                for i, contour in enumerate(simple_contours[:3]):
                    area = cv2.contourArea(contour)
                    rect = cv2.boundingRect(contour)
                    print(f"      简单轮廓 {i}: 面积={area}, 边界框={rect}")
        
    except Exception as e:
        print(f"    ❌ 调试异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_each_strategy()