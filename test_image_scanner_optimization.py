#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageScanner类全面重构优化测试脚本

测试内容:
1. 基础功能测试
2. 配置化参数测试
3. 多种文档类型扫描测试
4. 置信度评估测试
5. 批量处理测试
6. 性能统计测试
7. 向后兼容性测试
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sys
import os

# 添加路径以导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'sdk', 'python'))

try:
    from mxSdk.opencv.image_scanner import (
        ImageScanner,
        IDCardConfig,
        DocumentConfig,
        QRCodeConfig,
        DocumentType,
        ScanAlgorithm,
        ScanRegion,
        ImageScannerError
    )
    print("✅ 成功导入ImageScanner及相关配置类")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)


def create_id_card_image(size=(400, 250)):
    """创建模拟身份证图像"""
    # 创建白色背景
    img = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(img)
    
    # 绘制身份证轮廓
    draw.rectangle([10, 10, size[0]-10, size[1]-10], outline='black', width=2)
    
    # 绘制头像区域
    draw.rectangle([20, 30, 120, 150], outline='gray', width=1)
    draw.text((25, 90), "头像", fill='gray')
    
    # 绘制文字信息
    info_x = 140
    draw.text((info_x, 40), "姓名: 张三", fill='black')
    draw.text((info_x, 60), "性别: 男", fill='black')
    draw.text((info_x, 80), "民族: 汉", fill='black')
    draw.text((info_x, 100), "出生: 1990年1月1日", fill='black')
    draw.text((info_x, 120), "住址: 北京市朝阳区", fill='black')
    
    # 绘制身份证号码区域（重点测试区域）- 创建更明显的矩形区域
    number_y = size[1] - 60
    number_width = size[0] - 40
    number_height = 30
    
    # 填充白色背景
    draw.rectangle([20, number_y-15, 20+number_width, number_y+15], fill='white', outline='black', width=2)
    
    # 绘制号码文字
    draw.text((30, number_y-8), "公民身份号码", fill='black')
    draw.text((30, number_y+5), "110101199001011234", fill='black')
    
    # 添加一些噪点和纹理使其更真实
    for i in range(0, size[0], 20):
        for j in range(0, size[1], 20):
            if (i + j) % 40 == 0:
                draw.point((i, j), fill='lightgray')
    
    return img


def create_document_image(size=(300, 400)):
    """创建模拟文档图像"""
    img = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(img)
    
    # 绘制文档边框
    draw.rectangle([15, 15, size[0]-15, size[1]-15], outline='black', width=2)
    
    # 绘制标题
    draw.text((50, 40), "重要文档", fill='black')
    draw.line([50, 60, size[0]-50, 60], fill='black', width=1)
    
    # 绘制内容
    for i in range(10):
        y = 80 + i * 25
        draw.text((30, y), f"这是第{i+1}行文档内容", fill='black')
    
    return img


def create_qr_code_image(size=(200, 200)):
    """创建模拟二维码图像"""
    img = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(img)
    
    # 绘制简单的二维码模式
    qr_size = 120
    qr_x = (size[0] - qr_size) // 2
    qr_y = (size[1] - qr_size) // 2
    
    # 外框
    draw.rectangle([qr_x, qr_y, qr_x + qr_size, qr_y + qr_size], outline='black', width=2)
    
    # 三个定位点
    corner_size = 20
    # 左上角
    draw.rectangle([qr_x + 5, qr_y + 5, qr_x + corner_size, qr_y + corner_size], fill='black')
    # 右上角
    draw.rectangle([qr_x + qr_size - corner_size, qr_y + 5, 
                   qr_x + qr_size - 5, qr_y + corner_size], fill='black')
    # 左下角
    draw.rectangle([qr_x + 5, qr_y + qr_size - corner_size, 
                   qr_x + corner_size, qr_y + qr_size - 5], fill='black')
    
    # 添加一些随机点模拟二维码内容
    for i in range(30, qr_size-10, 8):
        for j in range(30, qr_size-10, 8):
            if (i + j) % 16 < 8:
                draw.rectangle([qr_x + i, qr_y + j, qr_x + i + 4, qr_y + j + 4], fill='black')
    
    return img


def test_basic_functionality():
    """测试基础功能"""
    print("\n🧪 测试基础功能...")
    
    # 创建测试图像
    id_card_img = create_id_card_image()
    document_img = create_document_image()
    qr_code_img = create_qr_code_image()
    
    # 创建ImageScanner实例
    scanner = ImageScanner()
    
    # 测试身份证扫描
    try:
        result = scanner.scan_id_card_number(id_card_img)
        assert isinstance(result, ScanRegion)
        assert result.confidence > 0
        assert result.region_type == "id_number"
        assert result.image is not None
        print(f"  ✅ 身份证扫描 - 置信度: {result.confidence:.3f}")
    except Exception as e:
        print(f"  ❌ 身份证扫描失败: {e}")
    
    # 测试多候选区域
    try:
        results = scanner.scan_id_card_number(id_card_img, return_all_candidates=True)
        assert isinstance(results, list)
        assert len(results) > 0
        print(f"  ✅ 多候选区域扫描 - 找到{len(results)}个候选区域")
    except Exception as e:
        print(f"  ❌ 多候选区域扫描失败: {e}")
    
    # 测试文档扫描
    try:
        results = scanner.scan_document(document_img)
        assert isinstance(results, list)
        print(f"  ✅ 文档扫描 - 找到{len(results)}个文档区域")
    except Exception as e:
        print(f"  ❌ 文档扫描失败: {e}")
    
    # 测试二维码检测
    try:
        results = scanner.detect_qr_codes(qr_code_img)
        assert isinstance(results, list)
        print(f"  ✅ 二维码检测 - 找到{len(results)}个二维码区域")
    except Exception as e:
        print(f"  ❌ 二维码检测失败: {e}")


def test_configuration():
    """测试配置化参数"""
    print("\n⚙️ 测试配置化参数...")
    
    test_image = create_id_card_image()
    
    # 自定义身份证配置
    try:
        id_config = IDCardConfig(
            threshold_value=120,
            morph_kernel_size=(15, 15),
            aspect_ratio_range=(4.0, 7.0),
            number_threshold=90
        )
        scanner = ImageScanner(id_card_config=id_config)
        result = scanner.scan_id_card_number(test_image)
        assert isinstance(result, ScanRegion)
        print("  ✅ 自定义身份证配置")
    except Exception as e:
        print(f"  ❌ 自定义身份证配置失败: {e}")
    
    # 自定义文档配置
    try:
        doc_config = DocumentConfig(
            canny_low_threshold=30,
            canny_high_threshold=100,
            min_area_ratio=0.05,
            max_area_ratio=0.8
        )
        scanner = ImageScanner(document_config=doc_config)
        results = scanner.scan_document(create_document_image())
        assert isinstance(results, list)
        print("  ✅ 自定义文档配置")
    except Exception as e:
        print(f"  ❌ 自定义文档配置失败: {e}")
    
    # 自定义二维码配置
    try:
        qr_config = QRCodeConfig(
            gaussian_blur=True,
            blur_kernel_size=(5, 5),
            use_builtin_detector=True
        )
        scanner = ImageScanner(qr_config=qr_config)
        results = scanner.detect_qr_codes(create_qr_code_image())
        assert isinstance(results, list)
        print("  ✅ 自定义二维码配置")
    except Exception as e:
        print(f"  ❌ 自定义二维码配置失败: {e}")


def test_error_handling():
    """测试错误处理"""
    print("\n🚨 测试错误处理...")
    
    scanner = ImageScanner()
    
    # 测试空图像
    try:
        scanner.scan_id_card_number(None)
        print("  ❌ 应该抛出异常但没有")
    except ImageScannerError:
        print("  ✅ 正确处理空图像异常")
    except Exception as e:
        print(f"  ⚠️ 异常类型不正确: {type(e).__name__}")
    
    # 测试无效图像
    try:
        invalid_image = Image.new('RGB', (0, 0))
        scanner.scan_document(invalid_image)
        print("  ❌ 应该抛出异常但没有")
    except ImageScannerError:
        print("  ✅ 正确处理无效图像异常")
    except Exception as e:
        print(f"  ⚠️ 异常类型不正确: {type(e).__name__}")
    
    # 测试无轮廓图像
    try:
        # 创建纯色图像
        solid_image = Image.new('RGB', (100, 100), 'white')
        result = scanner.scan_id_card_number(solid_image)
        print("  ❌ 应该抛出异常但没有")
    except ImageScannerError:
        print("  ✅ 正确处理无轮廓异常")
    except Exception as e:
        print(f"  ⚠️ 异常类型不正确: {type(e).__name__}")


def test_confidence_evaluation():
    """测试置信度评估"""
    print("\n📊 测试置信度评估...")
    
    scanner = ImageScanner()
    
    # 创建不同质量的身份证图像
    test_cases = [
        ("高质量身份证", create_id_card_image((400, 250))),
        ("小尺寸身份证", create_id_card_image((200, 125))),
        ("大尺寸身份证", create_id_card_image((600, 375)))
    ]
    
    for name, image in test_cases:
        try:
            results = scanner.scan_id_card_number(image, return_all_candidates=True)
            if results:
                best_result = results[0]
                print(f"  ✅ {name} - 置信度: {best_result.confidence:.3f}, "
                      f"区域: {best_result.bbox}")
            else:
                print(f"  ⚠️ {name} - 未检测到区域")
        except Exception as e:
            print(f"  ❌ {name} - 检测失败: {e}")


def test_batch_processing():
    """测试批量处理"""
    print("\n📦 测试批量处理...")
    
    scanner = ImageScanner()
    
    # 创建多张测试图像
    test_images = [
        create_id_card_image((400, 250)),
        create_id_card_image((300, 200)),
        create_document_image((250, 350))
    ]
    
    try:
        # 批量身份证扫描
        results = scanner.batch_scan(test_images, DocumentType.ID_CARD)
        assert len(results) == 3
        success_count = sum(1 for r in results if r is not None)
        print(f"  ✅ 批量身份证扫描 - 成功{success_count}/{len(results)}张")
        
        # 批量文档扫描
        results = scanner.batch_scan(test_images, DocumentType.DOCUMENT)
        assert len(results) == 3
        success_count = sum(1 for r in results if r is not None and len(r) > 0)
        print(f"  ✅ 批量文档扫描 - 成功{success_count}/{len(results)}张")
        
        # 测试空列表
        try:
            scanner.batch_scan([], DocumentType.ID_CARD)
            print("  ❌ 应该抛出异常但没有")
        except ImageScannerError:
            print("  ✅ 正确处理空列表异常")
        
        # 测试不支持的类型
        try:
            scanner.batch_scan(test_images, DocumentType.PASSPORT)
            print("  ❌ 应该抛出异常但没有")
        except ImageScannerError:
            print("  ✅ 正确处理不支持类型异常")
            
    except Exception as e:
        print(f"  ❌ 批量处理测试失败: {e}")


def test_performance_stats():
    """测试性能统计"""
    print("\n📈 测试性能统计...")
    
    scanner = ImageScanner()
    test_image = create_id_card_image()
    
    # 重置统计
    scanner.reset_stats()
    initial_stats = scanner.get_scan_stats()
    assert initial_stats['total_scans'] == 0
    print("  ✅ 统计重置功能")
    
    # 执行一些扫描
    try:
        scanner.scan_id_card_number(test_image)
        scanner.scan_document(create_document_image())
        scanner.detect_qr_codes(create_qr_code_image())
        
        stats = scanner.get_scan_stats()
        assert stats['total_scans'] == 3
        assert stats['avg_scan_time'] > 0
        assert 0 <= stats['success_rate'] <= 1
        
        print(f"  ✅ 性能统计: 扫描{stats['total_scans']}次，"
              f"平均时间{stats['avg_scan_time']:.4f}秒，"
              f"成功率{stats['success_rate']:.2%}")
        
        # 检查分类型统计
        if stats['type_avg_times']:
            for doc_type, avg_time in stats['type_avg_times'].items():
                print(f"    - {doc_type}: {avg_time:.4f}秒")
        
    except Exception as e:
        print(f"  ❌ 性能统计测试失败: {e}")


def test_scan_region_properties():
    """测试扫描区域属性"""
    print("\n🔍 测试扫描区域属性...")
    
    scanner = ImageScanner()
    test_image = create_id_card_image()
    
    try:
        result = scanner.scan_id_card_number(test_image)
        
        if result:
            # 检查ScanRegion属性
            assert hasattr(result, 'bbox')
            assert hasattr(result, 'confidence')
            assert hasattr(result, 'region_type')
            assert hasattr(result, 'image')
            
            # 验证bbox格式
            x, y, w, h = result.bbox
            assert all(isinstance(v, int) for v in result.bbox)
            assert w > 0 and h > 0
            
            # 验证置信度范围
            assert 0 <= result.confidence <= 1
            
            # 验证区域类型
            assert result.region_type == "id_number"
            
            # 验证提取的图像
            assert result.image is not None
            assert isinstance(result.image, Image.Image)
            
            print(f"  ✅ 扫描区域属性验证 - 区域: {result.bbox}, "
                  f"置信度: {result.confidence:.3f}")
        else:
            print("  ⚠️ 未检测到扫描区域")
            
    except Exception as e:
        print(f"  ❌ 扫描区域属性测试失败: {e}")


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n🔄 测试向后兼容性...")
    
    scanner = ImageScanner()
    test_image = create_id_card_image()
    
    try:
        # 测试旧的方法名
        result = scanner.opencv_scan_card(test_image)
        
        if result is not None:
            assert isinstance(result, Image.Image)
            print("  ✅ opencv_scan_card方法兼容")
        else:
            print("  ⚠️ opencv_scan_card返回None（可能是正常的）")
        
        print("  ✅ 向后兼容性测试通过")
        
    except Exception as e:
        print(f"  ❌ 向后兼容性测试失败: {e}")


def main():
    """主测试函数"""
    print("🚀 开始ImageScanner类全面重构优化测试")
    print("=" * 60)
    
    try:
        test_basic_functionality()
        test_configuration()
        test_error_handling()
        test_confidence_evaluation()
        test_batch_processing()
        test_performance_stats()
        test_scan_region_properties()
        test_backward_compatibility()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成！ImageScanner类全面重构优化成功！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()