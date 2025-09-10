#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
身份证扫描调试脚本
"""

import numpy as np
from PIL import Image, ImageDraw
import cv2
import sys
import os

# 添加路径以导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'sdk', 'python'))

from mxSdk.opencv.image_scanner import ImageScanner, IDCardConfig


def create_debug_id_card_image(size=(400, 250)):
    """创建调试用身份证图像"""
    img = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(img)
    
    # 绘制身份证轮廓
    draw.rectangle([10, 10, size[0]-10, size[1]-10], outline='black', width=3)
    
    # 绘制头像区域
    draw.rectangle([20, 30, 120, 150], fill='lightgray', outline='black', width=2)
    draw.text((50, 90), "头像", fill='black')
    
    # 绘制文字信息
    info_x = 140
    draw.text((info_x, 40), "姓名: 张三", fill='black')
    draw.text((info_x, 60), "性别: 男", fill='black')
    draw.text((info_x, 80), "民族: 汉", fill='black')
    draw.text((info_x, 100), "出生: 1990年1月1日", fill='black')
    draw.text((info_x, 120), "住址: 北京市朝阳区", fill='black')
    
    # 绘制身份证号码区域 - 创建明显的长条形区域
    number_y = size[1] - 50
    number_width = 300
    number_height = 25
    
    # 绘制号码背景
    draw.rectangle([30, number_y-12, 30+number_width, number_y+12], 
                  fill='white', outline='black', width=2)
    
    # 绘制号码文字
    draw.text((40, number_y-8), "公民身份号码", fill='black')
    draw.text((40, number_y+2), "110101199001011234", fill='black')
    
    return img


def debug_scan_process():
    """调试扫描过程"""
    print("🔍 开始调试身份证扫描过程...")
    
    # 创建测试图像
    test_image = create_debug_id_card_image()
    print(f"创建测试图像: {test_image.size}")
    
    # 创建扫描器
    scanner = ImageScanner()
    
    try:
        # 手动执行扫描步骤
        img_cv, gray = scanner._prepare_image(test_image)
        print(f"图像预处理完成: {gray.shape}")
        
        # 预处理
        cfg = scanner.id_card_config
        processed = scanner._preprocess_for_scanning(gray, cfg.gaussian_blur_kernel, cfg.gaussian_sigma)
        print(f"扫描预处理完成: {processed.shape}")
        
        # 自适应阈值
        binary = scanner._adaptive_threshold(processed, cfg)
        print(f"阈值处理完成: {binary.shape}, 唯一值: {np.unique(binary)}")
        
        # 形态学操作
        morphed = scanner._morphological_operations(binary, cfg)
        print(f"形态学操作完成: {morphed.shape}")
        
        # 轮廓检测
        contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(f"检测到轮廓数量: {len(contours)}")
        
        if contours:
            # 分析每个轮廓
            image_area = gray.shape[0] * gray.shape[1]
            print(f"图像总面积: {image_area}")
            
            for i, contour in enumerate(contours[:10]):  # 只分析前10个
                area = cv2.contourArea(contour)
                rect = cv2.boundingRect(contour)
                x, y, w, h = rect
                aspect_ratio = w / h if h > 0 else 0
                
                print(f"轮廓 {i}: 面积={area}, 边界框=({x},{y},{w},{h}), 宽高比={aspect_ratio:.2f}")
                
                # 检查是否符合条件
                meets_area = cfg.min_area <= area <= cfg.max_area
                meets_size = w >= cfg.min_width and h >= cfg.min_height
                meets_ratio = cfg.aspect_ratio_range[0] <= aspect_ratio <= cfg.aspect_ratio_range[1]
                
                print(f"  - 面积符合: {meets_area} ({cfg.min_area} <= {area} <= {cfg.max_area})")
                print(f"  - 尺寸符合: {meets_size} (w>={cfg.min_width}, h>={cfg.min_height})")
                print(f"  - 宽高比符合: {meets_ratio} ({cfg.aspect_ratio_range[0]} <= {aspect_ratio:.2f} <= {cfg.aspect_ratio_range[1]})")
                
                if meets_area and meets_size and meets_ratio:
                    confidence = scanner._calculate_id_card_confidence(contour, rect, area, image_area, cfg)
                    print(f"  - 置信度: {confidence:.3f}")
                    
                    if confidence > 0.1:
                        print(f"  ✅ 轮廓 {i} 符合所有条件！")
                    else:
                        print(f"  ❌ 轮廓 {i} 置信度过低")
                else:
                    print(f"  ❌ 轮廓 {i} 不符合基本条件")
        else:
            print("❌ 未检测到任何轮廓")
            
        # 尝试使用更宽松的配置
        print("\n🔧 尝试使用更宽松的配置...")
        loose_config = IDCardConfig(
            min_area=100,
            max_area=200000,
            aspect_ratio_range=(1.0, 15.0),
            min_width=20,
            min_height=5,
            threshold_value=150  # 使用固定阈值
        )
        
        # 重新处理
        binary2 = scanner._adaptive_threshold(processed, loose_config)
        morphed2 = scanner._morphological_operations(binary2, loose_config)
        contours2, _ = cv2.findContours(morphed2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        print(f"宽松配置检测到轮廓数量: {len(contours2)}")
        
        if contours2:
            filtered = scanner._filter_contours_for_id_card(contours2, loose_config, image_area)
            print(f"筛选后轮廓数量: {len(filtered)}")
            
            if filtered:
                best_contour, best_confidence = filtered[0]
                rect = cv2.boundingRect(best_contour)
                print(f"最佳候选: 边界框={rect}, 置信度={best_confidence:.3f}")
                
                # 尝试完整扫描
                try:
                    result = scanner.scan_id_card_number(test_image, config=loose_config)
                    if result:
                        print(f"✅ 扫描成功！区域: {result.bbox}, 置信度: {result.confidence:.3f}")
                    else:
                        print("❌ 扫描仍然失败")
                except Exception as e:
                    print(f"❌ 扫描异常: {e}")
        
    except Exception as e:
        print(f"❌ 调试过程出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_scan_process()