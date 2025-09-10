#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轮廓筛选调试脚本
"""

import numpy as np
from PIL import Image, ImageDraw
import cv2
import sys
import os

# 添加路径以导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'sdk', 'python'))

from mxSdk.opencv.image_scanner import ImageScanner, IDCardConfig


def create_realistic_id_card(size=(400, 250)):
    """创建更真实的身份证图像"""
    img = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(img)
    
    # 绘制身份证边框
    draw.rectangle([5, 5, size[0]-5, size[1]-5], outline='black', width=2)
    
    # 绘制头像区域
    draw.rectangle([20, 30, 120, 150], fill='lightgray', outline='black', width=1)
    
    # 绘制文字信息区域
    info_x = 140
    draw.rectangle([info_x, 30, size[0]-20, 150], outline='gray', width=1)
    
    # 绘制身份证号码区域 - 这是我们要检测的目标
    number_x = 50
    number_y = size[1] - 60
    number_w = 300
    number_h = 25
    
    # 绘制号码背景（稍微突出）
    draw.rectangle([number_x, number_y, number_x + number_w, number_y + number_h], 
                  fill='#f0f0f0', outline='black', width=1)
    
    # 绘制号码文字
    draw.text((number_x + 5, number_y + 5), "公民身份号码 110101199001011234", fill='black')
    
    return img


def debug_contour_filtering():
    """调试轮廓筛选过程"""
    print("🔍 调试轮廓筛选过程...")
    
    # 创建测试图像
    test_image = create_realistic_id_card()
    print(f"创建测试图像: {test_image.size}")
    
    # 创建扫描器
    scanner = ImageScanner()
    
    # 预处理图像
    img_cv, gray = scanner._prepare_image(test_image)
    print(f"图像预处理: {gray.shape}")
    
    # 使用标准配置
    cfg = scanner.id_card_config
    
    # 预处理
    processed = scanner._preprocess_for_scanning(
        gray, cfg.gaussian_blur_kernel, cfg.gaussian_sigma
    )
    
    # 阈值处理
    binary = scanner._adaptive_threshold(processed, cfg)
    
    # 形态学操作
    morphed = scanner._morphological_operations(binary, cfg)
    
    # 轮廓检测
    contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"检测到轮廓数量: {len(contours)}")
    
    if contours:
        image_area = gray.shape[0] * gray.shape[1]
        print(f"图像总面积: {image_area}")
        
        # 手动执行筛选逻辑
        print("\n🔍 手动执行筛选逻辑...")
        
        filtered = []
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            rect = cv2.boundingRect(contour)
            x, y, w, h = rect
            aspect_ratio = w / h if h > 0 else 0
            
            print(f"\n轮廓 {i}:")
            print(f"  面积: {area}")
            print(f"  边界框: ({x}, {y}, {w}, {h})")
            print(f"  宽高比: {aspect_ratio:.2f}")
            
            # 动态调整参数基于图像大小
            dynamic_min_area = max(cfg.min_area, image_area * 0.001)
            dynamic_max_area = min(cfg.max_area, image_area * 0.95)
            
            print(f"  动态面积范围: {dynamic_min_area} - {dynamic_max_area}")
            
            # 面积检查
            area_ok = dynamic_min_area <= area <= dynamic_max_area
            print(f"  面积检查: {area_ok}")
            
            if not area_ok:
                print(f"  ❌ 面积不符合要求")
                continue
            
            # 尺寸检查
            import math
            image_width = int(math.sqrt(image_area * 1.6))
            image_height = int(image_area / image_width)
            
            min_w = max(cfg.min_width, image_width * 0.05)
            min_h = max(cfg.min_height, image_height * 0.02)
            
            print(f"  动态最小尺寸: {min_w} x {min_h}")
            
            size_ok = w >= min_w and h >= min_h
            print(f"  尺寸检查: {size_ok}")
            
            if not size_ok:
                print(f"  ❌ 尺寸不符合要求")
                continue
            
            # 宽高比检查
            loose_range = (0.8, 20.0)
            ratio_ok = loose_range[0] <= aspect_ratio <= loose_range[1]
            print(f"  宽高比检查: {ratio_ok} (范围: {loose_range})")
            
            if not ratio_ok:
                print(f"  ❌ 宽高比不符合要求")
                continue
            
            # 计算置信度
            confidence = scanner._calculate_id_card_confidence(contour, rect, area, image_area, cfg)
            print(f"  置信度: {confidence:.3f}")
            
            if confidence > 0.05:
                print(f"  ✅ 轮廓 {i} 通过所有检查！")
                filtered.append((contour, confidence))
            else:
                print(f"  ❌ 置信度过低")
        
        print(f"\n筛选结果: {len(filtered)} 个候选")
        
        # 测试实际的筛选方法
        print("\n🧪 测试实际的筛选方法...")
        actual_filtered = scanner._filter_contours_for_id_card(contours, cfg, image_area)
        print(f"实际筛选结果: {len(actual_filtered)} 个候选")
        
        if actual_filtered:
            for i, (contour, confidence) in enumerate(actual_filtered):
                rect = cv2.boundingRect(contour)
                print(f"  候选 {i}: 边界框={rect}, 置信度={confidence:.3f}")
        
    else:
        print("❌ 未检测到任何轮廓")


if __name__ == "__main__":
    debug_contour_filtering()