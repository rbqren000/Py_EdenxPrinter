#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
背景清除功能模块

作者: RBQ
创建时间: 2025
描述: 提供各种背景清除功能，包括轻度/深度背景清除和红色背景清除
"""

import cv2
import numpy as np
from PIL import Image
import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass, field
from .base_utils import BaseUtils


@dataclass
class BackgroundCleanConfig:
    """背景清除配置类"""
    # 核心参数
    adaptive_processing: bool = True
    kernel_size: Optional[int] = None  # None表示自动计算
    
    # 红色检测参数
    red_hue_ranges: List[Tuple[int, int]] = field(default_factory=lambda: [(0, 10), (170, 180)])
    red_saturation_min: int = 50
    red_value_min: int = 50
    
    # 修复参数
    inpaint_radius: int = 2
    
    # 形态学参数
    dilate_size: int = 5


class BackgroundCleaner:
    """背景清除处理类"""
    
    @staticmethod
    def _enhanced_reduce_background_algorithm(src: np.ndarray, config: BackgroundCleanConfig) -> np.ndarray:
        """
        优化的背景减少算法
        
        Args:
            src: 输入图像数组（浮点数类型）
            config: 配置参数
            
        Returns:
            处理后的图像数组
        """
        # 计算核大小
        if config.adaptive_processing and config.kernel_size is None:
            height, width = src.shape[:2]
            kernel_size = min(max(min(width, height) // 10, 51), 151)
            # 确保为奇数
            kernel_size = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        else:
            kernel_size = config.kernel_size or 101
        
        # 单一背景估计（避免多尺度计算）
        background = cv2.blur(src, (kernel_size, kernel_size))
        
        # 避免除零
        background = np.maximum(background, 0.01)
        
        # 除法运算增强对比度
        dst2 = cv2.divide(src, background)
        
        # 简单锐化
        dst2 = BaseUtils.image_sharp(dst2, amount=100)
        
        # 转换为8位无符号整数
        dst3 = np.uint8(np.clip(dst2 * 255, 0, 255))
        
        return dst3
    
    @staticmethod
    def _enhanced_color_gradation(src: np.ndarray, config: BackgroundCleanConfig) -> np.ndarray:
        """
        优化的颜色渐变处理
        
        Args:
            src: 输入图像数组
            config: 配置参数
            
        Returns:
            处理后的图像数组
        """
        if config.adaptive_processing:
            # 自适应阈值计算
            shadow = np.percentile(src, 5.0)
            highlight = np.percentile(src, 95.0)
            
            # 防止范围过小
            if highlight - shadow < 50:
                shadow = 120
                highlight = 255
        else:
            shadow = 120
            highlight = 255
        
        diff = highlight - shadow
        if diff <= 0:
            return src
        
        # 减去阴影值并缩放
        r_diff = np.maximum(src - shadow, 0)
        temp1 = r_diff * (255.0 / diff)
        
        return np.uint8(np.clip(temp1, 0, 255))
    
    @staticmethod
    def _create_adaptive_red_mask(img_cv: np.ndarray, config: BackgroundCleanConfig) -> np.ndarray:
        """
        创建红色掩码
        
        Args:
            img_cv: OpenCV格式的图像
            config: 配置参数
            
        Returns:
            红色区域掩码
        """
        # 转换为HSV格式
        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        
        # 创建红色掩码
        masks = []
        for hue_range in config.red_hue_ranges:
            lower = np.array([hue_range[0], config.red_saturation_min, config.red_value_min])
            upper = np.array([hue_range[1], 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
            masks.append(mask)
        
        # 合并掩码
        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # 简单膨胀处理
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (config.dilate_size, config.dilate_size))
        processed_mask = cv2.dilate(combined_mask, kernel)
        
        return processed_mask
    
    @staticmethod
    def _adaptive_inpaint(img_cv: np.ndarray, mask: np.ndarray, config: BackgroundCleanConfig) -> np.ndarray:
        """
        图像修复
        
        Args:
            img_cv: 输入图像
            mask: 修复掩码
            config: 配置参数
            
        Returns:
            修复后的图像
        """
        # 简单的自适应半径计算
        if config.adaptive_processing:
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                max_area = max([cv2.contourArea(c) for c in contours])
                radius = min(max(int(np.sqrt(max_area) * 0.1), 2), 8)
            else:
                radius = config.inpaint_radius
        else:
            radius = config.inpaint_radius
        
        # 使用单一修复方法（NS方法通常效果更好）
        return cv2.inpaint(img_cv, mask, radius, cv2.INPAINT_NS)
    
    @staticmethod
    def _enhanced_binarization(image: np.ndarray, config: BackgroundCleanConfig) -> np.ndarray:
        """
        二值化处理
        
        Args:
            image: 输入图像
            config: 配置参数
            
        Returns:
            二值化后的图像
        """
        if config.adaptive_processing:
            # 预处理：轻度降噪和对比度增强
            denoised = cv2.medianBlur(image, 3)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # 使用OTSU自适应阈值
            _, result = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            # 简单OTSU二值化
            _, result = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return result
    
    @staticmethod
    def light_clear_background(image: Image.Image, config: Optional[BackgroundCleanConfig] = None) -> Optional[Image.Image]:
        """
        轻度背景清除
        
        Args:
            image: 输入PIL图像对象
            config: 配置参数，为None时使用默认配置
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
        
        if config is None:
            config = BackgroundCleanConfig()
            
        try:
            # 格式转换
            img_cv = BaseUtils.convert_pil_to_opencv(image)
            
            # 灰度预处理
            gray_float = BaseUtils.prepare_grayscale(img_cv)
            
            # 背景减少算法
            dst = BackgroundCleaner._enhanced_reduce_background_algorithm(gray_float, config)
            
            # 颜色渐变
            dst3 = BackgroundCleaner._enhanced_color_gradation(dst, config)
            
            # 转换回PIL格式
            return Image.fromarray(dst3)
            
        except Exception as e:
            logging.error(f"轻度背景清除失败: {e}")
            return None
    
    @staticmethod
    def deep_clear_background(image: Image.Image, config: Optional[BackgroundCleanConfig] = None) -> Optional[Image.Image]:
        """
        深度背景清除
        
        Args:
            image: 输入PIL图像对象
            config: 配置参数，为None时使用默认配置
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
        
        if config is None:
            config = BackgroundCleanConfig()
            
        try:
            # 格式转换
            img_cv = BaseUtils.convert_pil_to_opencv(image)
            
            # 灰度预处理
            gray_float = BaseUtils.prepare_grayscale(img_cv)
            
            # 背景减少算法
            dst = BackgroundCleaner._enhanced_reduce_background_algorithm(gray_float, config)
            
            # 颜色渐变
            dst3 = BackgroundCleaner._enhanced_color_gradation(dst, config)
            
            # 二值化处理
            ts = BackgroundCleaner._enhanced_binarization(dst3, config)
            
            # 转换回PIL格式
            return Image.fromarray(ts)
            
        except Exception as e:
            logging.error(f"深度背景清除失败: {e}")
            return None
    
    @staticmethod
    def light_clear_red_background(image: Image.Image, config: Optional[BackgroundCleanConfig] = None) -> Optional[Image.Image]:
        """
        轻度红色背景清除（优化版）
        
        Args:
            image: 输入PIL图像对象
            config: 配置参数，为None时使用默认配置
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
        
        if config is None:
            config = BackgroundCleanConfig()
            
        try:
            # 格式转换
            img_cv = BaseUtils.convert_pil_to_opencv(image)
            
            # 创建红色掩码
            mask_img = BackgroundCleaner._create_adaptive_red_mask(img_cv, config)
            
            # 图像修复
            result = BackgroundCleaner._adaptive_inpaint(img_cv, mask_img, config)
            
            # 灰度预处理
            gray_float = BaseUtils.prepare_grayscale(result)
            
            # 背景减少算法
            dst = BackgroundCleaner._enhanced_reduce_background_algorithm(gray_float, config)
            
            # 颜色渐变
            dst3 = BackgroundCleaner._enhanced_color_gradation(dst, config)
            
            # 转换回PIL格式
            return Image.fromarray(dst3)
            
        except Exception as e:
            logging.error(f"轻度红色背景清除失败: {e}")
            return None
    
    @staticmethod
    def deep_clear_red_background(image: Image.Image, config: Optional[BackgroundCleanConfig] = None) -> Optional[Image.Image]:
        """
        深度红色背景清除（优化版）
        
        Args:
            image: 输入PIL图像对象
            config: 配置参数，为None时使用默认配置
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
        
        if config is None:
            config = BackgroundCleanConfig()
            
        try:
            # 格式转换
            img_cv = BaseUtils.convert_pil_to_opencv(image)
            
            # 创建红色掩码
            mask_img = BackgroundCleaner._create_adaptive_red_mask(img_cv, config)
            
            # 图像修复
            result = BackgroundCleaner._adaptive_inpaint(img_cv, mask_img, config)
            
            # 灰度预处理
            gray_float = BaseUtils.prepare_grayscale(result)
            
            # 背景减少算法
            dst = BackgroundCleaner._enhanced_reduce_background_algorithm(gray_float, config)
            
            # 颜色渐变
            dst3 = BackgroundCleaner._enhanced_color_gradation(dst, config)
            
            # 二值化处理
            ts = BackgroundCleaner._enhanced_binarization(dst3, config)
            
            # 转换回PIL格式
            return Image.fromarray(ts)
            
        except Exception as e:
            logging.error(f"深度红色背景清除失败: {e}")
            return None