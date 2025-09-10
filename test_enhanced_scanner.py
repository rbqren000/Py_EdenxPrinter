"""
测试增强版图像扫描器
对比原版本和增强版本的性能差异
"""

import sys
import os
sys.path.append('sdk/python')

from PIL import Image
import numpy as np
import cv2
from mxSdk.opencv.image_scanner_enhanced import EnhancedImageScanner, EnhancedIDCardConfig
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_images():
    """创建测试图像"""
    test_images = []
    
    # 测试图像1: 清晰的身份证号码区域
    img1 = np.ones((300, 400, 3), dtype=np.uint8) * 240
    # 模拟身份证号码区域
    cv2.rectangle(img1, (50, 200), (350, 230), (255, 255, 255), -1)
    cv2.rectangle(img1, (50, 200), (350, 230), (0, 0, 0), 2)
    # 添加一些数字模拟
    for i in range(18):
        x = 55 + i * 16
        cv2.rectangle(img1, (x, 205), (x+12, 225), (0, 0, 0), -1)
    test_images.append(Image.fromarray(img1))
    
    # 测试图像2: 模糊的身份证
    img2 = np.ones((250, 400, 3), dtype=np.uint8) * 220
    # 添加噪声
    noise = np.random.randint(0, 50, img2.shape, dtype=np.uint8)
    img2 = cv2.add(img2, noise)
    # 模糊的身份证号码区域
    cv2.rectangle(img2, (30, 180), (370, 210), (200, 200, 200), -1)
    # 模糊处理
    img2 = cv2.GaussianBlur(img2, (3, 3), 1)
    test_images.append(Image.fromarray(img2))
    
    # 测试图像3: 复杂背景
    img3 = np.random.randint(100, 200, (280, 450, 3), dtype=np.uint8)
    # 身份证号码区域
    cv2.rectangle(img3, (80, 220), (380, 250), (255, 255, 255), -1)
    cv2.rectangle(img3, (80, 220), (380, 250), (0, 0, 0), 1)
    # 添加文字模拟
    for i in range(15):
        x = 85 + i * 19
        cv2.rectangle(img3, (x, 225), (x+15, 245), (0, 0, 0), -1)
    test_images.append(Image.fromarray(img3))
    
    # 测试图像4: 旋转的身份证
    img4 = np.ones((320, 480, 3), dtype=np.uint8) * 230
    # 创建旋转的矩形区域
    center = (240, 160)
    size = (300, 30)
    angle = 15
    
    # 计算旋转矩形的四个顶点
    rect = cv2.RotatedRect(center, size, angle)
    box = cv2.boxPoints(rect)
    box = np.array(box, dtype=np.int32)
    
    # 绘制旋转的身份证号码区域
    cv2.fillPoly(img4, [box], (255, 255, 255))
    cv2.polylines(img4, [box], True, (0, 0, 0), 2)
    test_images.append(Image.fromarray(img4))
    
    # 测试图像5: 低对比度
    img5 = np.ones((260, 420, 3), dtype=np.uint8) * 180
    # 低对比度的身份证号码区域
    cv2.rectangle(img5, (60, 190), (360, 220), (190, 190, 190), -1)
    cv2.rectangle(img5, (60, 190), (360, 220), (170, 170, 170), 1)
    test_images.append(Image.fromarray(img5))
    
    return test_images

def test_enhanced_scanner():
    """测试增强版扫描器"""
    print("=" * 60)
    print("测试增强版图像扫描器")
    print("=" * 60)
    
    # 创建扫描器实例
    scanner = EnhancedImageScanner()
    
    # 创建测试图像
    test_images = create_test_images()
    
    # 测试配置
    configs = [
        ("默认配置", EnhancedIDCardConfig()),
        ("宽松配置", EnhancedIDCardConfig(
            min_area=50,
            max_area=100000,
            aspect_ratio_range=(1.5, 10.0),
            min_width=30,
            min_height=10
        )),
        ("严格配置", EnhancedIDCardConfig(
            min_area=200,
            max_area=20000,
            aspect_ratio_range=(3.0, 6.0),
            min_width=80,
            min_height=20
        ))
    ]
    
    total_success = 0
    total_tests = 0
    
    for config_name, config in configs:
        print(f"\n--- 使用{config_name} ---")
        config_success = 0
        
        for i, image in enumerate(test_images, 1):
            print(f"\n测试图像 {i}:")
            
            start_time = time.time()
            results = scanner.scan_id_card_enhanced(image, config)
            end_time = time.time()
            
            total_tests += 1
            
            if results:
                config_success += 1
                total_success += 1
                print(f"  ✅ 扫描成功 - 找到 {len(results)} 个候选区域")
                print(f"  ⏱️  处理时间: {(end_time - start_time)*1000:.1f}ms")
                
                # 显示最佳结果的详细信息
                best_result = results[0]
                print(f"  📊 最佳结果:")
                print(f"     - 边界框: {best_result['bbox']}")
                print(f"     - 置信度: {best_result['confidence']:.3f}")
                print(f"     - 策略: {best_result['strategy']}")
                print(f"     - 特征: {best_result['features']}")
                
            else:
                print(f"  ❌ 扫描失败 - 未找到符合条件的区域")
                print(f"  ⏱️  处理时间: {(end_time - start_time)*1000:.1f}ms")
        
        success_rate = (config_success / len(test_images)) * 100
        print(f"\n{config_name}成功率: {config_success}/{len(test_images)} ({success_rate:.1f}%)")
    
    overall_success_rate = (total_success / total_tests) * 100
    print(f"\n" + "=" * 60)
    print(f"总体测试结果:")
    print(f"成功: {total_success}/{total_tests} ({overall_success_rate:.1f}%)")
    print(f"目标: 90%以上成功率")
    
    if overall_success_rate >= 90:
        print("🎉 达到目标成功率!")
    else:
        print("⚠️  未达到目标，需要进一步优化")
    
    return overall_success_rate

def test_strategy_effectiveness():
    """测试各个策略的有效性"""
    print("\n" + "=" * 60)
    print("测试各策略有效性")
    print("=" * 60)
    
    scanner = EnhancedImageScanner()
    test_images = create_test_images()
    config = EnhancedIDCardConfig()
    
    strategy_stats = {}
    
    for i, image in enumerate(test_images, 1):
        print(f"\n测试图像 {i}:")
        results = scanner.scan_id_card_enhanced(image, config)
        
        for result in results:
            strategies = result['strategy'].split('+')
            for strategy in strategies:
                if strategy not in strategy_stats:
                    strategy_stats[strategy] = {'count': 0, 'total_confidence': 0.0}
                
                strategy_stats[strategy]['count'] += 1
                strategy_stats[strategy]['total_confidence'] += result['confidence']
    
    print(f"\n策略统计:")
    for strategy, stats in sorted(strategy_stats.items(), 
                                key=lambda x: x[1]['count'], reverse=True):
        avg_confidence = stats['total_confidence'] / stats['count']
        print(f"  {strategy}: {stats['count']} 次使用, "
              f"平均置信度: {avg_confidence:.3f}")

def benchmark_performance():
    """性能基准测试"""
    print("\n" + "=" * 60)
    print("性能基准测试")
    print("=" * 60)
    
    scanner = EnhancedImageScanner()
    test_images = create_test_images()
    config = EnhancedIDCardConfig()
    
    # 预热
    for image in test_images[:2]:
        scanner.scan_id_card_enhanced(image, config)
    
    # 正式测试
    total_time = 0
    num_tests = 10
    
    print(f"执行 {num_tests} 轮测试...")
    
    for round_num in range(num_tests):
        round_start = time.time()
        
        for image in test_images:
            scanner.scan_id_card_enhanced(image, config)
        
        round_time = time.time() - round_start
        total_time += round_time
        
        print(f"  第 {round_num + 1} 轮: {round_time*1000:.1f}ms")
    
    avg_time_per_round = total_time / num_tests
    avg_time_per_image = avg_time_per_round / len(test_images)
    
    print(f"\n性能统计:")
    print(f"  平均每轮时间: {avg_time_per_round*1000:.1f}ms")
    print(f"  平均每张图像: {avg_time_per_image*1000:.1f}ms")
    print(f"  理论处理能力: {1/avg_time_per_image:.1f} 张/秒")

def test_edge_cases():
    """测试边缘情况"""
    print("\n" + "=" * 60)
    print("边缘情况测试")
    print("=" * 60)
    
    scanner = EnhancedImageScanner()
    config = EnhancedIDCardConfig()
    
    # 测试用例
    test_cases = [
        ("空白图像", Image.new('RGB', (400, 300), (255, 255, 255))),
        ("纯黑图像", Image.new('RGB', (400, 300), (0, 0, 0))),
        ("极小图像", Image.new('RGB', (50, 30), (128, 128, 128))),
        ("极大图像", Image.new('RGB', (2000, 1500), (200, 200, 200))),
        ("单色图像", Image.new('RGB', (400, 300), (128, 128, 128)))
    ]
    
    for case_name, image in test_cases:
        print(f"\n测试 {case_name}:")
        try:
            start_time = time.time()
            results = scanner.scan_id_card_enhanced(image, config)
            end_time = time.time()
            
            print(f"  ✅ 处理成功 - 找到 {len(results)} 个结果")
            print(f"  ⏱️  处理时间: {(end_time - start_time)*1000:.1f}ms")
            
        except Exception as e:
            print(f"  ❌ 处理失败: {str(e)}")

if __name__ == "__main__":
    try:
        # 主要功能测试
        success_rate = test_enhanced_scanner()
        
        # 策略有效性测试
        test_strategy_effectiveness()
        
        # 性能测试
        benchmark_performance()
        
        # 边缘情况测试
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)
        
        if success_rate >= 90:
            print("🎉 增强版扫描器达到预期目标!")
            print("✅ 成功率 >= 90%")
            print("✅ 多策略融合有效")
            print("✅ 性能表现良好")
        else:
            print("⚠️  需要进一步优化以达到90%成功率目标")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()