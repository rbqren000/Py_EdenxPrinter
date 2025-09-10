#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenCV图像处理工具类（模块化版本）

作者: RBQ
创建时间: 2025
描述: 提供各种图像处理功能，包括背景清除、素描效果、颜色反转等
     这是模块化重构版本，保持与原版本的完全兼容性
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List, Union
from PIL import Image
import logging

# 导入各个功能模块
from .background_cleaner import BackgroundCleanConfig
from .base_utils import BaseUtils
from .background_cleaner import BackgroundCleaner
from .image_effects import ImageEffects
from .image_analysis import ImageAnalysis
from .image_geometry import ImageGeometry
from .image_scanner import ImageScanner


class OpenCVUtils:
    """
    OpenCV图像处理工具类（模块化版本）
    
    提供各种图像处理功能，包括：
    - 背景清除（轻度/深度）
    - 红色背景清除
    - 素描效果
    - 颜色反转
    - 前景清除
    - 边缘检测
    - 直方图均衡化
    - 图像锐化
    - 对数变换
    - 伽马校正
    """
    
    # ==================== 背景清除功能 ====================
    
    @staticmethod
    def light_clear_background(image: Image.Image, config: Optional[BackgroundCleanConfig] = None) -> Optional[Image.Image]:
        """轻度背景清除"""
        return BackgroundCleaner.light_clear_background(image, config)
    
    @staticmethod
    def deep_clear_background(image: Image.Image, config: Optional[BackgroundCleanConfig] = None) -> Optional[Image.Image]:
        """深度背景清除"""
        return BackgroundCleaner.deep_clear_background(image, config)
    
    @staticmethod
    def light_clear_red_background(image: Image.Image, config: Optional[BackgroundCleanConfig] = None) -> Optional[Image.Image]:
        """轻度红色背景清除"""
        return BackgroundCleaner.light_clear_red_background(image, config)
    
    @staticmethod
    def deep_clear_red_background(image: Image.Image, config: Optional[BackgroundCleanConfig] = None) -> Optional[Image.Image]:
        """深度红色背景清除"""
        return BackgroundCleaner.deep_clear_red_background(image, config)
    
    # ==================== 图像效果处理 ====================
    
    @staticmethod
    def process_image_for_text_detail(image: Image.Image) -> Optional[Image.Image]:
        """处理图像以增强文字细节"""
        return ImageEffects.process_image_for_text_detail(image)
    
    @staticmethod
    def sketch_image(image: Image.Image) -> Optional[Image.Image]:
        """图像素描处理"""
        return ImageEffects.sketch_image(image)
    
    @staticmethod
    def sketch_effect(image: Image.Image) -> Optional[Image.Image]:
        """素描效果处理"""
        return ImageEffects.sketch_effect(image)
    
    @staticmethod
    def invert_color(image: Image.Image) -> Optional[Image.Image]:
        """颜色反转（保持透明度）"""
        return ImageEffects.invert_color(image)
    
    @staticmethod
    def invert_colors(image: Image.Image) -> Optional[Image.Image]:
        """颜色反转（处理Alpha通道）"""
        return ImageEffects.invert_colors(image)
    
    @staticmethod
    def clear_foreground(image: Image.Image) -> Optional[Image.Image]:
        """清除前景文字"""
        return ImageEffects.clear_foreground(image)
    
    # ==================== 图像分析和变换 ====================
    
    @staticmethod
    def apply_sobel_edge_detection(image: Image.Image) -> Optional[Image.Image]:
        """应用Sobel边缘检测"""
        return ImageAnalysis.apply_sobel_edge_detection(image)
    
    @staticmethod
    def apply_canny_edge_detection(image: Image.Image) -> Optional[Image.Image]:
        """应用Canny边缘检测"""
        return ImageAnalysis.apply_canny_edge_detection(image)
    
    @staticmethod
    def equalize_histogram(image: Image.Image) -> Optional[Image.Image]:
        """直方图均衡化"""
        return ImageAnalysis.equalize_histogram(image)
    
    @staticmethod
    def laplacian_sharpening(image: Image.Image) -> Optional[Image.Image]:
        """拉普拉斯算子锐化"""
        return ImageAnalysis.laplacian_sharpening(image)
    
    @staticmethod
    def log_transformation(image: Image.Image) -> Optional[Image.Image]:
        """对数变换"""
        return ImageAnalysis.log_transformation(image)
    
    @staticmethod
    def gamma_correction(image: Image.Image, gamma: float = 1.0) -> Optional[Image.Image]:
        """伽马校正"""
        return ImageAnalysis.gamma_correction(image, gamma)
    
    @staticmethod
    def laplacian_sharpening_enhanced(image: Image.Image) -> Optional[Image.Image]:
        """增强版拉普拉斯锐化
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            锐化后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        return ImageAnalysis.laplacian_sharpening_enhanced(image)
    
    @staticmethod
    def laplacian_sharpening_with_bilateral_filter(image: Image.Image) -> Optional[Image.Image]:
        """带双边滤波的拉普拉斯锐化"""
        return ImageAnalysis.laplacian_sharpening_with_bilateral_filter(image)
    
    # ==================== 图像几何变换 ====================
    
    @staticmethod
    def create_multi_img_to_one(base_image: Image.Image, images: list) -> Optional[Image.Image]:
        """将多个图像合并到一个基础图像上"""
        return ImageGeometry.create_multi_img_to_one(base_image, images)
    
    @staticmethod
    def rectify_image(image: Image.Image) -> Optional[Image.Image]:
        """图像矫正（透视变换）"""
        return ImageGeometry.rectify_image(image)
    
    @staticmethod
    def amend_image_by_outline(image: Image.Image) -> Optional[Image.Image]:
        """通过轮廓修正图像"""
        return ImageGeometry.amend_image_by_outline(image)
    
    @staticmethod
    def resize_bitmap(image: Image.Image, width: int, height: int) -> Optional[Image.Image]:
        """调整图像大小"""
        return ImageGeometry.resize_bitmap(image, width, height)
    
    @staticmethod
    def crop_image(image: Image.Image, x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
        """从图像中裁剪子图像"""
        return ImageGeometry.crop_image(image, x, y, width, height)
    
    @staticmethod
    def sub_image(image1: Image.Image, image2: Image.Image) -> Optional[Image.Image]:
        """图像替换（将image2复制到image1上）"""
        return ImageGeometry.sub_image(image1, image2)
    
    # ==================== 图像扫描功能 ====================
    
    @staticmethod
    def opencv_scan_card(image: Image.Image) -> Optional[Image.Image]:
        """扫描身份证图片，定位号码区域"""
        return ImageScanner.opencv_scan_card(image)
    
    # ==================== 内部工具方法（保持兼容性） ====================
    
    @staticmethod
    def _convert_pil_to_opencv(image: Image.Image) -> np.ndarray:
        """统一的PIL到OpenCV转换"""
        return BaseUtils.convert_pil_to_opencv(image)
    
    @staticmethod
    def _prepare_grayscale(img_cv: np.ndarray) -> np.ndarray:
        """统一的灰度预处理"""
        return BaseUtils.prepare_grayscale(img_cv)
    
    @staticmethod
    def _calculate_adaptive_kernel_size(image: np.ndarray, base_size: int = 101) -> int:
        """计算自适应滤波核大小"""
        return BaseUtils.calculate_adaptive_kernel_size(image, base_size)
    
    @staticmethod
    def _color_gradation(src: np.ndarray) -> np.ndarray:
        """颜色渐变处理（内部方法）"""
        return BaseUtils.color_gradation(src)
    
    @staticmethod
    def _reduce_background_algorithm(src: np.ndarray) -> np.ndarray:
        """背景减少算法（内部方法）"""
        return BaseUtils.reduce_background_algorithm(src)
    
    @staticmethod
    def _four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
        """四点透视变换"""
        return BaseUtils.four_point_transform(image, pts)
    
    @staticmethod
    def _image_sharp(src: np.ndarray, amount: int = 100) -> np.ndarray:
        """图像锐化（内部方法）"""
        return BaseUtils.image_sharp(src, amount)