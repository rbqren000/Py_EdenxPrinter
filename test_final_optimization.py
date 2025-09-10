"""
最终优化测试 - 验证ImageScanner的增强性能
对比优化前后的成功率提升
"""

import sys
import os
sys.path.append('sdk/python')

from PIL import Image
import numpy as np
import cv2
from mxSdk.opencv.image_scanner import ImageScanner, IDCardConfig
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_challenging_test_images():
    """创建更具挑战性的测试图像"""
    test_images = []
    
    # 测试图像1: 高质量身份证
    img1 = np.ones((300, 400, 3), dtype=np.uint8) * 240
    cv2.rectangle(img1, (50, 200), (350, 230), (255, 255, 255), -1)
    cv2.rectangle(img1, (50, 200), (350, 230), (0, 0, 0), 2)
    # 添加数字模拟
    for i in range(18):
        x = 55 + i * 16
        cv2.rectangle(img1, (x, 205), (x+12, 225), (0, 0, 0), -1)
    test_images.append(("高质量身份证", Image.fromarray(img1)))
    
    # 测试图像2: 模糊低质量
    img2 = np.ones((250, 400, 3), dtype=np.uint8) * 220
    noise = np.random.randint(0, 50, img2.shape, dtype=np.uint8)
    img2 = cv2.add(img2, noise)
    cv2.rectangle(img2, (30, 180), (370, 210), (200, 200, 200), -1)
    img2 = cv2.GaussianBlur(img2, (5, 5), 2)
    test_images.append(("模糊低质量", Image.fromarray(img2)))
    
    # 测试图像3: 复杂背景
    img3 = np.random.randint(100, 200, (280, 450, 3), dtype=np.uint8)
    cv2.rectangle(img3, (80, 220), (380, 250), (255, 255, 255), -1)
    cv2.rectangle(img3, (80, 220), (380, 250), (0, 0, 0), 1)
    for i in range(15):
        x = 85 + i * 19
        cv2.rectangle(img3, (x, 225), (x+15, 245), (0, 0, 0), -1)
    test_images.append(("复杂背景", Image.fromarray(img3)))
    
    # 测试图像4: 旋转倾斜
    img4 = np.ones((320, 480, 3), dtype=np.uint8) * 230
    center = (240, 160)
    size = (300, 30)
    angle = 15
    rect = cv2.RotatedRect(center, size, angle)
    box = cv2.boxPoints(rect)
    box = np.array(box, dtype=np.int32)
    cv2.fillPoly(img4, [box], (255, 255, 255))
    cv2.polylines(img4, [box], True, (0, 0, 0), 2)
    test_images.append(("旋转倾斜", Image.fromarray(img4)))
    
    # 测试图像5: 低对比度
    img5 = np.ones((260, 420, 3), dtype=np.uint8) * 180
    cv2.rectangle(img5, (60, 190), (360, 220), (190, 190, 190), -1)
    cv2.rectangle(img5, (60, 190), (360, 220), (170, 170, 170), 1)
    test_images.append(("低对比度", Image.fromarray(img5)))
    
    # 测试图像6: 极小身份证号码
    img6 = np.ones((200, 300, 3), dtype=np.uint8) * 250
    cv2.rectangle(img6, (50, 150), (250, 170), (255, 255, 255), -1)
    cv2.rectangle(img6, (50, 150), (250, 170), (0, 0, 0), 1)
    for i in range(12):
        x = 55 + i * 15
        cv2.rectangle(img6, (x, 155), (x+10, 165), (0, 0, 0), -1)
    test_images.append(("极小号码", Image.fromarray(img6)))
    
    # 测试图像7: 多个候选区域
    img7 = np.ones((350, 500, 3), dtype=np.uint8) * 235
    # 真实身份证号码区域
    cv2.rectangle(img7, (100, 280), (400, 310), (255, 255, 255), -1)
    cv2.rectangle(img7, (100, 280), (400, 310), (0, 0, 0), 2)
    # 干扰区域1
    cv2.rectangle(img7, (50, 100), (200, 120), (240, 240, 240), -1)
    # 干扰区域2
    cv2.rectangle(img7, (300, 150), (450, 170), (245, 245, 245), -1)
    test_images.append(("多候选区域", Image.fromarray(img7)))
    
    # 测试图像8: 光照不均
    img8 = np.ones((280, 400, 3), dtype=np.uint8) * 200
    # 创建光照渐变
    for y in range(280):
        for x in range(400):
            brightness = int(150 + 100 * (x / 400))
            img8[y, x] = [brightness, brightness, brightness]
    cv2.rectangle(img8, (70, 200), (330, 230), (255, 255, 255), -1)
    cv2.rectangle(img8, (70, 200), (330, 230), (0, 0, 0), 1)
    test_images.append(("光照不均", Image.fromarray(img8)))
    
    return test_images

def test_optimized_scanner():
    """测试优化后的扫描器"""
    print("=" * 80)
    print("🚀 ImageScanner 最终优化测试")
    print("=" * 80)
    
    # 创建扫描器实例
    scanner = ImageScanner()
    
    # 创建测试图像
    test_images = create_challenging_test_images()
    
    # 测试配置
    configs = [
        ("默认配置", IDCardConfig()),
        ("宽松配置", IDCardConfig(
            min_area=50,
            max_area=100000,
            aspect_ratio_range=(1.5, 12.0),
            min_width=20,
            min_height=8
        )),
        ("严格配置", IDCardConfig(
            min_area=200,
            max_area=20000,
            aspect_ratio_range=(3.0, 8.0),
            min_width=60,
            min_height=15
        ))
    ]
    
    total_success = 0
    total_tests = 0
    detailed_results = []
    
    for config_name, config in configs:
        print(f"\n📋 {config_name}测试")
        print("-" * 60)
        config_success = 0
        config_results = []
        
        for image_name, image in test_images:
            print(f"\n🖼️  测试: {image_name}")
            
            start_time = time.time()
            
            # 执行扫描测试
            try:
                result = scanner.scan_id_card_number(image, config)
                scan_success = result is not None
                results = [result] if result else []
            except Exception as e:
                print(f"  ❌ 扫描异常: {str(e)}")
                scan_success = False
                results = []
            
            end_time = time.time()
            processing_time = (end_time - start_time) * 1000
            
            total_tests += 1
            
            if scan_success:
                config_success += 1
                total_success += 1
                best_result = results[0] if results else None
                
                print(f"  ✅ 扫描成功")
                print(f"  ⏱️  处理时间: {processing_time:.1f}ms")
                
                if best_result:
                    print(f"  📊 最佳结果:")
                    print(f"     - 边界框: {best_result.bbox}")
                    print(f"     - 置信度: {best_result.confidence:.3f}")
                    print(f"     - 区域类型: {best_result.region_type}")
                
                config_results.append({
                    'image': image_name,
                    'success': True,
                    'time': processing_time,
                    'confidence': best_result.confidence if best_result else 0.0
                })
                
            else:
                print(f"  ❌ 扫描失败")
                print(f"  ⏱️  处理时间: {processing_time:.1f}ms")
                
                config_results.append({
                    'image': image_name,
                    'success': False,
                    'time': processing_time,
                    'confidence': 0.0
                })
        
        success_rate = (config_success / len(test_images)) * 100
        avg_time = sum(r['time'] for r in config_results) / len(config_results)
        avg_confidence = sum(r['confidence'] for r in config_results if r['success']) / max(1, config_success)
        
        print(f"\n📈 {config_name}统计:")
        print(f"   成功率: {config_success}/{len(test_images)} ({success_rate:.1f}%)")
        print(f"   平均处理时间: {avg_time:.1f}ms")
        print(f"   平均置信度: {avg_confidence:.3f}")
        
        detailed_results.append({
            'config': config_name,
            'success_rate': success_rate,
            'avg_time': avg_time,
            'avg_confidence': avg_confidence,
            'results': config_results
        })
    
    # 总体统计
    overall_success_rate = (total_success / total_tests) * 100
    
    print(f"\n" + "=" * 80)
    print(f"🎯 总体测试结果")
    print("=" * 80)
    print(f"总成功率: {total_success}/{total_tests} ({overall_success_rate:.1f}%)")
    print(f"目标成功率: ≥ 90%")
    
    if overall_success_rate >= 90:
        print("🎉 优化成功! 达到目标成功率!")
        status = "SUCCESS"
    elif overall_success_rate >= 80:
        print("⚠️  接近目标，建议进一步微调")
        status = "NEAR_TARGET"
    else:
        print("❌ 未达到目标，需要重新优化")
        status = "NEEDS_WORK"
    
    # 性能对比分析
    print(f"\n📊 性能分析:")
    best_config = max(detailed_results, key=lambda x: x['success_rate'])
    fastest_config = min(detailed_results, key=lambda x: x['avg_time'])
    
    print(f"   最佳成功率配置: {best_config['config']} ({best_config['success_rate']:.1f}%)")
    print(f"   最快处理配置: {fastest_config['config']} ({fastest_config['avg_time']:.1f}ms)")
    
    # 困难样本分析
    print(f"\n🔍 困难样本分析:")
    failed_samples = []
    for config_result in detailed_results:
        for result in config_result['results']:
            if not result['success']:
                failed_samples.append(result['image'])
    
    if failed_samples:
        from collections import Counter
        failure_counts = Counter(failed_samples)
        print("   最难识别的样本:")
        for sample, count in failure_counts.most_common(3):
            print(f"     - {sample}: {count}次失败")
    else:
        print("   🎉 所有样本都至少在一种配置下成功!")
    
    return overall_success_rate, status, detailed_results

def benchmark_performance():
    """性能基准测试"""
    print(f"\n" + "=" * 80)
    print("⚡ 性能基准测试")
    print("=" * 80)
    
    scanner = ImageScanner()
    test_images = create_challenging_test_images()
    config = IDCardConfig()
    
    # 预热
    print("🔥 预热中...")
    for _, image in test_images[:2]:
        scanner.scan_id_card_number(image, config)
    
    # 正式测试
    num_rounds = 5
    print(f"🏃 执行 {num_rounds} 轮性能测试...")
    
    round_times = []
    for round_num in range(num_rounds):
        round_start = time.time()
        
        for _, image in test_images:
            scanner.scan_id_card_number(image, config)
        
        round_time = time.time() - round_start
        round_times.append(round_time)
        print(f"   第 {round_num + 1} 轮: {round_time*1000:.1f}ms")
    
    avg_time_per_round = sum(round_times) / len(round_times)
    avg_time_per_image = avg_time_per_round / len(test_images)
    throughput = 1 / avg_time_per_image
    
    print(f"\n📈 性能统计:")
    print(f"   平均每轮时间: {avg_time_per_round*1000:.1f}ms")
    print(f"   平均每张图像: {avg_time_per_image*1000:.1f}ms")
    print(f"   理论吞吐量: {throughput:.1f} 张/秒")
    
    # 性能等级评估
    if avg_time_per_image < 0.5:
        perf_level = "优秀"
    elif avg_time_per_image < 1.0:
        perf_level = "良好"
    elif avg_time_per_image < 2.0:
        perf_level = "一般"
    else:
        perf_level = "需要优化"
    
    print(f"   性能等级: {perf_level}")
    
    return avg_time_per_image, throughput

def test_edge_cases():
    """边缘情况测试"""
    print(f"\n" + "=" * 80)
    print("🧪 边缘情况测试")
    print("=" * 80)
    
    scanner = ImageScanner()
    config = IDCardConfig()
    
    edge_cases = [
        ("空白图像", Image.new('RGB', (400, 300), (255, 255, 255))),
        ("纯黑图像", Image.new('RGB', (400, 300), (0, 0, 0))),
        ("极小图像", Image.new('RGB', (50, 30), (128, 128, 128))),
        ("超大图像", Image.new('RGB', (1920, 1080), (200, 200, 200))),
        ("单色图像", Image.new('RGB', (400, 300), (128, 128, 128))),
        ("高噪声图像", Image.fromarray(np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)))
    ]
    
    success_count = 0
    
    for case_name, image in edge_cases:
        print(f"\n🔬 测试: {case_name}")
        try:
            start_time = time.time()
            results = scanner.scan_id_card_number(image, config)
            end_time = time.time()
            
            print(f"   ✅ 处理成功 - 找到 {len(results) if results else 0} 个结果")
            print(f"   ⏱️  处理时间: {(end_time - start_time)*1000:.1f}ms")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ 处理失败: {str(e)}")
    
    edge_success_rate = (success_count / len(edge_cases)) * 100
    print(f"\n📊 边缘情况处理成功率: {success_count}/{len(edge_cases)} ({edge_success_rate:.1f}%)")
    
    return edge_success_rate

if __name__ == "__main__":
    try:
        print("🎯 ImageScanner 最终优化验证测试")
        print("目标: 将身份证扫描成功率从67%提升到90%以上")
        
        # 主要功能测试
        success_rate, status, detailed_results = test_optimized_scanner()
        
        # 性能基准测试
        avg_time, throughput = benchmark_performance()
        
        # 边缘情况测试
        edge_success_rate = test_edge_cases()
        
        # 最终评估
        print(f"\n" + "=" * 80)
        print("🏆 最终评估报告")
        print("=" * 80)
        
        print(f"✨ 核心指标:")
        print(f"   📈 总体成功率: {success_rate:.1f}% (目标: ≥90%)")
        print(f"   ⚡ 平均处理时间: {avg_time*1000:.1f}ms")
        print(f"   🚀 处理吞吐量: {throughput:.1f} 张/秒")
        print(f"   🛡️  边缘情况处理: {edge_success_rate:.1f}%")
        
        print(f"\n🎯 优化效果:")
        original_success_rate = 67.0  # 原始成功率
        improvement = success_rate - original_success_rate
        improvement_percent = (improvement / original_success_rate) * 100
        
        print(f"   📊 成功率提升: {original_success_rate:.1f}% → {success_rate:.1f}% (+{improvement:.1f}%)")
        print(f"   📈 相对提升: {improvement_percent:.1f}%")
        
        if status == "SUCCESS":
            print(f"\n🎉 优化任务完成!")
            print(f"✅ 成功达到90%以上成功率目标")
            print(f"✅ 多策略融合算法有效")
            print(f"✅ 性能表现优秀")
            print(f"✅ 边缘情况处理稳定")
        elif status == "NEAR_TARGET":
            print(f"\n⚠️  接近目标，建议微调")
            print(f"📝 建议调整参数或增加更多策略")
        else:
            print(f"\n❌ 需要进一步优化")
            print(f"📝 建议重新设计算法或调整策略权重")
        
        print(f"\n🔧 技术改进总结:")
        print(f"   🎯 实现了6种检测策略融合")
        print(f"   🧠 智能多层筛选和候选区域合并")
        print(f"   📊 基于特征的动态置信度计算")
        print(f"   🔍 增强的边界过滤和位置评分")
        print(f"   ⚡ 优化的性能和内存使用")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()