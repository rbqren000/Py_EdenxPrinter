#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实图片背景清除测试脚本
测试优化后的背景清除功能在实际图片上的效果
"""

import os
import sys
import time
from PIL import Image
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sdk.python.mxSdk.opencv.opencv_utils import OpenCVUtils, BackgroundCleanConfig
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保项目路径正确")
    sys.exit(1)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_real_images():
    """测试真实图片的背景清除效果"""
    
    print("🖼️ 真实图片背景清除测试开始")
    print("=" * 60)
    
    # 测试图片目录
    test_dir = "testimage"
    output_dir = "output_results"
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取测试图片列表
    if not os.path.exists(test_dir):
        print(f"❌ 测试目录不存在: {test_dir}")
        return
    
    image_files = [f for f in os.listdir(test_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    
    if not image_files:
        print(f"❌ 在 {test_dir} 中没有找到图片文件")
        return
    
    print(f"📁 找到 {len(image_files)} 张测试图片")
    
    # 测试配置（优化版 - 移除效果不佳的固定配置）
    configs = {
        "默认配置": BackgroundCleanConfig(),  # 日常推荐使用
        "红色优化配置": BackgroundCleanConfig(
            adaptive_processing=True,
            red_hue_ranges=[(0, 15), (165, 180)]  # 扩大红色检测范围
        ),
        "高质量配置": BackgroundCleanConfig(
            adaptive_processing=True,
            kernel_size=None,  # 完全自适应
            inpaint_radius=3   # 更大的修复半径，更好效果
        )
    }
    
    # 测试方法
    methods = {
        "轻度背景清除": OpenCVUtils.light_clear_background,
        "深度背景清除": OpenCVUtils.deep_clear_background,
        "轻度红色背景清除": OpenCVUtils.light_clear_red_background,
        "深度红色背景清除": OpenCVUtils.deep_clear_red_background
    }
    
    results = {}
    
    # 对每张图片进行测试
    for image_file in image_files:
        print(f"\n🖼️ 测试图片: {image_file}")
        print("-" * 40)
        
        image_path = os.path.join(test_dir, image_file)
        
        try:
            # 加载图片
            original_image = Image.open(image_path)
            print(f"  📏 原始尺寸: {original_image.size}")
            print(f"  🎨 颜色模式: {original_image.mode}")
            
            # 转换为RGB模式（如果需要）
            if original_image.mode != 'RGB':
                original_image = original_image.convert('RGB')
                print(f"  🔄 已转换为RGB模式")
            
            image_results = {}
            
            # 测试每种配置和方法的组合
            for config_name, config in configs.items():
                print(f"\n  📋 配置: {config_name}")
                
                for method_name, method_func in methods.items():
                    print(f"    🔄 {method_name}...", end=" ")
                    
                    try:
                        start_time = time.time()
                        result_image = method_func(original_image, config)
                        end_time = time.time()
                        
                        if result_image is not None:
                            # 保存结果图片
                            base_name = os.path.splitext(image_file)[0]
                            output_filename = f"{base_name}_{config_name}_{method_name}.jpg"
                            output_path = os.path.join(output_dir, output_filename)
                            result_image.save(output_path, "JPEG", quality=95)
                            
                            processing_time = end_time - start_time
                            print(f"✅ 成功 ({processing_time:.3f}s)")
                            
                            # 记录结果
                            key = f"{config_name}_{method_name}"
                            image_results[key] = {
                                "success": True,
                                "time": processing_time,
                                "output_size": result_image.size,
                                "output_path": output_path
                            }
                        else:
                            print("❌ 失败")
                            image_results[f"{config_name}_{method_name}"] = {
                                "success": False,
                                "time": 0,
                                "error": "返回None"
                            }
                            
                    except Exception as e:
                        print(f"❌ 异常: {str(e)[:50]}...")
                        image_results[f"{config_name}_{method_name}"] = {
                            "success": False,
                            "time": 0,
                            "error": str(e)
                        }
            
            results[image_file] = image_results
            
        except Exception as e:
            print(f"  ❌ 加载图片失败: {e}")
            results[image_file] = {"error": f"加载失败: {e}"}
    
    # 生成测试报告
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    total_tests = 0
    successful_tests = 0
    total_time = 0
    
    for image_file, image_results in results.items():
        if "error" in image_results:
            print(f"\n❌ {image_file}: {image_results['error']}")
            continue
            
        print(f"\n📸 {image_file}:")
        
        # 按方法分组显示结果
        for method_name in methods.keys():
            print(f"  🔧 {method_name}:")
            method_success = 0
            method_total = 0
            method_time = 0
            
            for config_name in configs.keys():
                key = f"{config_name}_{method_name}"
                if key in image_results:
                    result = image_results[key]
                    method_total += 1
                    total_tests += 1
                    
                    if result["success"]:
                        method_success += 1
                        successful_tests += 1
                        method_time += result["time"]
                        total_time += result["time"]
                        print(f"    ✅ {config_name}: {result['time']:.3f}s")
                    else:
                        print(f"    ❌ {config_name}: {result.get('error', '未知错误')}")
            
            if method_total > 0:
                success_rate = (method_success / method_total) * 100
                avg_time = method_time / method_success if method_success > 0 else 0
                print(f"    📊 成功率: {method_success}/{method_total} ({success_rate:.1f}%) 平均耗时: {avg_time:.3f}s")
    
    # 总体统计
    print(f"\n🎯 总体统计:")
    print(f"  📊 总测试数: {total_tests}")
    print(f"  ✅ 成功数: {successful_tests}")
    print(f"  📈 成功率: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "  📈 成功率: 0%")
    print(f"  ⏱️ 总耗时: {total_time:.3f}s")
    print(f"  ⚡ 平均耗时: {(total_time/successful_tests):.3f}s" if successful_tests > 0 else "  ⚡ 平均耗时: 0s")
    
    # 性能分析（优化版配置）
    print(f"\n⚡ 性能分析:")
    method_stats = {}
    config_stats = {}
    
    for image_file, image_results in results.items():
        if "error" in image_results:
            continue
            
        for key, result in image_results.items():
            if result["success"]:
                parts = key.split("_", 1)
                config_name = parts[0]
                method = parts[1] if len(parts) > 1 else key
                
                # 按方法统计
                if method not in method_stats:
                    method_stats[method] = []
                method_stats[method].append(result["time"])
                
                # 按配置统计
                if config_name not in config_stats:
                    config_stats[config_name] = []
                config_stats[config_name].append(result["time"])
    
    print("  📊 按处理方法统计:")
    for method, times in method_stats.items():
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            print(f"    🔧 {method}:")
            print(f"      平均: {avg_time:.3f}s, 最快: {min_time:.3f}s, 最慢: {max_time:.3f}s")
    
    print("\n  📊 按配置类型统计:")
    for config_name, times in config_stats.items():
        if times:
            avg_time = sum(times) / len(times)
            print(f"    ⚙️ {config_name}: 平均 {avg_time:.3f}s ({len(times)}次测试)")
    
    print(f"\n📁 处理结果已保存到: {output_dir}/")
    print("🎉 真实图片测试完成！")

def analyze_image_characteristics():
    """分析测试图片的特征"""
    print("\n🔍 图片特征分析")
    print("-" * 40)
    
    test_dir = "testimage"
    
    for image_file in os.listdir(test_dir):
        if image_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_path = os.path.join(test_dir, image_file)
            
            try:
                with Image.open(image_path) as img:
                    print(f"\n📸 {image_file}:")
                    print(f"  📏 尺寸: {img.size[0]} x {img.size[1]}")
                    print(f"  🎨 模式: {img.mode}")
                    print(f"  📊 文件大小: {os.path.getsize(image_path) / 1024:.1f} KB")
                    
                    # 简单的颜色分析
                    if img.mode == 'RGB':
                        # 转换为RGB数组进行分析
                        import numpy as np
                        img_array = np.array(img)
                        
                        # 计算平均颜色
                        avg_color = np.mean(img_array, axis=(0, 1))
                        print(f"  🌈 平均RGB: ({avg_color[0]:.0f}, {avg_color[1]:.0f}, {avg_color[2]:.0f})")
                        
                        # 检测是否可能包含红色
                        red_pixels = np.sum((img_array[:,:,0] > 150) & (img_array[:,:,1] < 100) & (img_array[:,:,2] < 100))
                        total_pixels = img_array.shape[0] * img_array.shape[1]
                        red_ratio = red_pixels / total_pixels * 100
                        
                        if red_ratio > 1:
                            print(f"  🔴 可能包含红色背景 ({red_ratio:.1f}%)")
                        
            except Exception as e:
                print(f"  ❌ 分析失败: {e}")

if __name__ == "__main__":
    try:
        # 分析图片特征
        analyze_image_characteristics()
        
        # 运行真实图片测试
        test_real_images()
        
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()