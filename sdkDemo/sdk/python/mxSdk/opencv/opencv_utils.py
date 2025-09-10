#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenCV图像处理工具类

作者: RBQ
创建时间: 2025
描述: 提供各种图像处理功能，包括背景清除、素描效果、颜色反转等
     这是Objective-C版本OpenCVUtils的Python重写版本
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List, Union
from PIL import Image
import logging
from dataclasses import dataclass, field


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


class OpenCVUtils:
    """
    OpenCV图像处理工具类
    
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
    
    @staticmethod
    def _convert_pil_to_opencv(image: Image.Image) -> np.ndarray:
        """
        统一的PIL到OpenCV转换
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            OpenCV格式的图像数组
        """
        img_array = np.array(image)
        if len(img_array.shape) == 2:  # 灰度图
            return img_array
        elif img_array.shape[2] == 4:  # RGBA
            return cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        else:  # RGB
            return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def _prepare_grayscale(img_cv: np.ndarray) -> np.ndarray:
        """
        统一的灰度预处理
        
        Args:
            img_cv: OpenCV格式的图像数组
            
        Returns:
            归一化的浮点数灰度图像
        """
        if len(img_cv.shape) == 3:
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_cv.copy()
        
        # 转换为浮点数类型并归一化
        return gray.astype(np.float32) / 255.0
    
    @staticmethod
    def _calculate_adaptive_kernel_size(image: np.ndarray, base_size: int = 101) -> int:
        """
        计算自适应滤波核大小
        
        Args:
            image: 输入图像
            base_size: 基础核大小
            
        Returns:
            优化后的核大小
        """
        height, width = image.shape[:2]
        # 根据图像尺寸动态调整
        scale_factor = min(width, height) / 1000.0
        adaptive_size = int(base_size * max(0.5, min(2.0, scale_factor)))
        # 确保为奇数
        return adaptive_size if adaptive_size % 2 == 1 else adaptive_size + 1
    
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
        dst2 = OpenCVUtils._image_sharp(dst2, amount=100)
        
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
            img_cv = OpenCVUtils._convert_pil_to_opencv(image)
            
            # 灰度预处理
            gray_float = OpenCVUtils._prepare_grayscale(img_cv)
            
            # 背景减少算法
            dst = OpenCVUtils._enhanced_reduce_background_algorithm(gray_float, config)
            
            # 颜色渐变
            dst3 = OpenCVUtils._enhanced_color_gradation(dst, config)
            
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
            img_cv = OpenCVUtils._convert_pil_to_opencv(image)
            
            # 灰度预处理
            gray_float = OpenCVUtils._prepare_grayscale(img_cv)
            
            # 背景减少算法
            dst = OpenCVUtils._enhanced_reduce_background_algorithm(gray_float, config)
            
            # 颜色渐变
            dst3 = OpenCVUtils._enhanced_color_gradation(dst, config)
            
            # 二值化处理
            ts = OpenCVUtils._enhanced_binarization(dst3, config)
            
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
            img_cv = OpenCVUtils._convert_pil_to_opencv(image)
            
            # 创建红色掩码
            mask_img = OpenCVUtils._create_adaptive_red_mask(img_cv, config)
            
            # 图像修复
            result = OpenCVUtils._adaptive_inpaint(img_cv, mask_img, config)
            
            # 灰度预处理
            gray_float = OpenCVUtils._prepare_grayscale(result)
            
            # 背景减少算法
            dst = OpenCVUtils._enhanced_reduce_background_algorithm(gray_float, config)
            
            # 颜色渐变
            dst3 = OpenCVUtils._enhanced_color_gradation(dst, config)
            
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
            img_cv = OpenCVUtils._convert_pil_to_opencv(image)
            
            # 创建红色掩码
            mask_img = OpenCVUtils._create_adaptive_red_mask(img_cv, config)
            
            # 图像修复
            result = OpenCVUtils._adaptive_inpaint(img_cv, mask_img, config)
            
            # 灰度预处理
            gray_float = OpenCVUtils._prepare_grayscale(result)
            
            # 背景减少算法
            dst = OpenCVUtils._enhanced_reduce_background_algorithm(gray_float, config)
            
            # 颜色渐变
            dst3 = OpenCVUtils._enhanced_color_gradation(dst, config)
            
            # 二值化处理
            ts = OpenCVUtils._enhanced_binarization(dst3, config)
            
            # 转换回PIL格式
            return Image.fromarray(ts)
            
        except Exception as e:
            logging.error(f"深度红色背景清除失败: {e}")
            return None
    
    @staticmethod
    def process_image_for_text_detail(image: Image.Image) -> Optional[Image.Image]:
        """
        处理图像以增强文字细节
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()
            
            # 自适应阈值二值化
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 10
            )
            
            # 形态学操作增强文字清晰度
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # 转换回PIL格式
            result_image = Image.fromarray(morph)
            return result_image
            
        except Exception as e:
            logging.error(f"文字细节处理失败: {e}")
            return None
    
    @staticmethod
    def sketch_image(image: Image.Image) -> Optional[Image.Image]:
        """
        图像素描处理
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()
            
            # 高斯模糊
            blur = cv2.GaussianBlur(gray, (5, 5), 1.5)
            
            # Canny边缘检测
            edge = cv2.Canny(blur, 30, 90)
            
            # 形态学闭运算
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morph = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, kernel)
            
            # 反转图像
            sketch = cv2.bitwise_not(morph)
            
            # 拉普拉斯锐化
            laplace = cv2.Laplacian(sketch, cv2.CV_8U, ksize=3)
            sharp = cv2.addWeighted(sketch, 1.0, laplace, -0.5, 0)
            
            # 转换回PIL格式
            result_image = Image.fromarray(sharp)
            return result_image
            
        except Exception as e:
            logging.error(f"素描处理失败: {e}")
            return None
    
    @staticmethod
    def sketch_effect(image: Image.Image) -> Optional[Image.Image]:
        """
        素描效果处理
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()
            
            # 高斯模糊
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Sobel梯度
            gradient_x = cv2.Sobel(blurred, cv2.CV_16S, 1, 0)
            gradient_y = cv2.Sobel(blurred, cv2.CV_16S, 0, 1)
            
            # 转换为绝对值
            abs_gradient_x = cv2.convertScaleAbs(gradient_x)
            abs_gradient_y = cv2.convertScaleAbs(gradient_y)
            
            # 合并梯度
            sketch = cv2.addWeighted(abs_gradient_x, 0.5, abs_gradient_y, 0.5, 0)
            
            # 反转图像获得白底素描效果
            sketch = cv2.bitwise_not(sketch)
            
            # 转换回PIL格式
            result_image = Image.fromarray(sketch)
            return result_image
            
        except Exception as e:
            logging.error(f"素描效果处理失败: {e}")
            return None
    
    @staticmethod
    def invert_color(image: Image.Image) -> Optional[Image.Image]:
        """
        颜色反转（保持透明度）
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            
            # 检查通道数
            if len(img_array.shape) < 3:
                # 灰度图直接反转
                inverted = cv2.bitwise_not(img_array)
                result_image = Image.fromarray(inverted)
                return result_image
                
            # 获取通道数
            channels = img_array.shape[2]
            
            if channels == 4:  # RGBA图像
                # 分离通道
                r, g, b, a = cv2.split(cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGRA))
                
                # 反转RGB通道
                b = cv2.bitwise_not(b)
                g = cv2.bitwise_not(g)
                r = cv2.bitwise_not(r)
                
                # 合并通道
                inverted = cv2.merge([b, g, r, a])
                result_image = Image.fromarray(cv2.cvtColor(inverted, cv2.COLOR_BGRA2RGBA))
                
            else:  # RGB图像
                # 转换为BGR
                bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                # 反转
                inverted = cv2.bitwise_not(bgr)
                # 转换回RGB
                rgb_inverted = cv2.cvtColor(inverted, cv2.COLOR_BGR2RGB)
                result_image = Image.fromarray(rgb_inverted)
                
            return result_image
            
        except Exception as e:
            logging.error(f"颜色反转失败: {e}")
            return None
    
    @staticmethod
    def invert_colors(image: Image.Image) -> Optional[Image.Image]:
        """
        颜色反转（处理Alpha通道）
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            
            # 分离Alpha通道
            alpha_channel = None
            if len(img_array.shape) == 3 and img_array.shape[2] == 4:
                alpha_channel = img_array[:, :, 3]
                src = img_array[:, :, :3]
                # 转换RGB为BGR
                src = cv2.cvtColor(src, cv2.COLOR_RGB2BGR)
                has_alpha = True
            else:
                if len(img_array.shape) == 3:
                    # RGB转BGR
                    src = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                else:
                    src = img_array.copy()
                has_alpha = False
            
            # 反色处理
            inverted = cv2.bitwise_not(src)
            
            # 转换回PIL格式
            if has_alpha:
                # BGR转RGB
                inverted_rgb = cv2.cvtColor(inverted, cv2.COLOR_BGR2RGB)
                # 重新合并Alpha通道
                result_array = np.dstack((inverted_rgb, alpha_channel))
                result_image = Image.fromarray(result_array)
            else:
                if len(inverted.shape) == 3:
                    # BGR转RGB
                    result_image = Image.fromarray(cv2.cvtColor(inverted, cv2.COLOR_BGR2RGB))
                else:
                    result_image = Image.fromarray(inverted)
            
            return result_image
            
        except Exception as e:
            logging.error(f"颜色反转失败: {e}")
            return None
    
    @staticmethod
    def clear_foreground(image: Image.Image) -> Optional[Image.Image]:
        """
        清除前景文字
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()
            
            # 高斯模糊
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Canny边缘检测
            edges = cv2.Canny(blurred, 50, 150)
            
            # 膨胀操作
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            dilated = cv2.dilate(edges, kernel)
            
            # 图像修复
            repaired = cv2.inpaint(img_cv, dilated, 3, cv2.INPAINT_TELEA)
            
            # 转换回PIL格式
            if len(img_array.shape) == 3 and img_array.shape[2] == 4:  # 保持透明通道
                # 提取原始透明通道
                alpha = img_array[:, :, 3]
                # 将修复后的BGR转换为RGB
                rgb = cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB)
                # 创建RGBA图像
                rgba = np.dstack((rgb, alpha))
                result_image = Image.fromarray(rgba)
            else:
                result_image = Image.fromarray(cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB))
            
            return result_image
            
        except Exception as e:
            logging.error(f"前景清除失败: {e}")
            return None
    
    @staticmethod
    def apply_sobel_edge_detection(image: Image.Image) -> Optional[Image.Image]:
        """
        应用Sobel边缘检测
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()
            
            # Sobel边缘检测
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # 计算梯度幅值
            sobel = np.sqrt(sobel_x**2 + sobel_y**2)
            sobel = np.uint8(np.clip(sobel, 0, 255))
            
            # 转换回PIL格式
            result_image = Image.fromarray(sobel)
            
            return result_image
            
        except Exception as e:
            logging.error(f"Sobel边缘检测失败: {e}")
            return None
    
    @staticmethod
    def apply_canny_edge_detection(image: Image.Image) -> Optional[Image.Image]:
        """
        应用Canny边缘检测
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()
            
            # Canny边缘检测
            edges = cv2.Canny(gray, 50, 150)
            
            # 转换回PIL格式
            result_image = Image.fromarray(edges)
            
            return result_image
            
        except Exception as e:
            logging.error(f"Canny边缘检测失败: {e}")
            return None
    
    @staticmethod
    def equalize_histogram(image: Image.Image) -> Optional[Image.Image]:
        """
        直方图均衡化
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    # 保存透明通道
                    alpha = img_array[:, :, 3]
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                    has_alpha = True
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    has_alpha = False
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()
                has_alpha = False
            
            # 直方图均衡化
            equalized = cv2.equalizeHist(gray)
            
            # 转换回PIL格式
            if has_alpha:
                # 创建RGBA图像
                result_image = Image.fromarray(np.dstack((equalized, equalized, equalized, alpha)))
            else:
                result_image = Image.fromarray(equalized)
            
            return result_image
            
        except Exception as e:
            logging.error(f"直方图均衡化失败: {e}")
            return None
    
    @staticmethod
    def laplacian_sharpening(image: Image.Image) -> Optional[Image.Image]:
        """
        拉普拉斯算子锐化
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    # 保存透明通道
                    alpha = img_array[:, :, 3]
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                    has_alpha = True
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    has_alpha = False
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()
                has_alpha = False
            
            # 拉普拉斯算子
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            
            # 锐化
            sharpened = gray - laplacian
            sharpened = np.uint8(np.clip(sharpened, 0, 255))
            
            # 转换回PIL格式
            if has_alpha:
                # 创建RGBA图像
                result_image = Image.fromarray(np.dstack((sharpened, sharpened, sharpened, alpha)))
            else:
                result_image = Image.fromarray(sharpened)
            
            return result_image
            
        except Exception as e:
            logging.error(f"拉普拉斯锐化失败: {e}")
            return None
    
    @staticmethod
    def log_transformation(image: Image.Image) -> Optional[Image.Image]:
        """
        对数变换
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    # 保存透明通道
                    alpha = img_array[:, :, 3]
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                    has_alpha = True
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    has_alpha = False
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()
                has_alpha = False
            
            # 对数变换
            c = 255 / np.log(1 + np.max(gray))
            log_transformed = c * np.log(1 + gray.astype(np.float32))
            log_transformed = np.uint8(log_transformed)
            
            # 转换回PIL格式
            if has_alpha:
                # 创建RGBA图像
                result_image = Image.fromarray(np.dstack((log_transformed, log_transformed, log_transformed, alpha)))
            else:
                result_image = Image.fromarray(log_transformed)
            
            return result_image
            
        except Exception as e:
            logging.error(f"对数变换失败: {e}")
            return None
    
    @staticmethod
    def gamma_correction(image: Image.Image, gamma: float = 1.0) -> Optional[Image.Image]:
        """
        伽马校正
        
        Args:
            image: 输入PIL图像对象
            gamma: 伽马值
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空或伽马值无效时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
        if gamma <= 0:
            raise ValueError("伽马值必须大于0")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    # 保存透明通道
                    alpha = img_array[:, :, 3]
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                    has_alpha = True
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    has_alpha = False
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()
                has_alpha = False
            
            # 伽马校正
            gamma_corrected = np.power(gray / 255.0, gamma) * 255.0
            gamma_corrected = np.uint8(np.clip(gamma_corrected, 0, 255))
            
            # 转换回PIL格式
            if has_alpha:
                # 创建RGBA图像
                result_image = Image.fromarray(np.dstack((gamma_corrected, gamma_corrected, gamma_corrected, alpha)))
            else:
                result_image = Image.fromarray(gamma_corrected)
            
            return result_image
            
        except Exception as e:
            logging.error(f"伽马校正失败: {e}")
            return None
    
    @staticmethod
    def create_multi_img_to_one(base_image: Image.Image, images: list) -> Optional[Image.Image]:
        """
        将多个图像合并到一个基础图像上
        
        Args:
            base_image: 基础PIL图像对象
            images: 要合并的PIL图像对象列表
            
        Returns:
            合并后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if base_image is None:
            raise ValueError("基础图像不能为空")
            
        try:
            # 获取基础图像尺寸
            width, height = base_image.size
            result = base_image.copy()
            
            for img in images:
                if img is not None:
                    # 调整图像大小以匹配基础图像
                    resized = img.resize((width, height), Image.LANCZOS)
                    result = resized.copy()
            
            return result
            
        except Exception as e:
            logging.error(f"图像合并失败: {e}")
            return None
    
    @staticmethod
    def rectify_image(image: Image.Image) -> Optional[Image.Image]:
        """
        图像矫正（透视变换）
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            矫正后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    # 保存透明通道
                    alpha = img_array[:, :, 3]
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                    has_alpha = True
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    has_alpha = False
            else:
                img_cv = img_array.copy()
                has_alpha = False
                
            # 缩小图像以提高处理速度
            height, width = img_cv.shape[:2]
            shrink_count = width // 500
            multi = 2
            
            shrink_pic = img_cv.copy()
            if shrink_count > 1:
                shrink_count = shrink_count // 2
                multi = 2 ** (shrink_count + 1)
                for _ in range(shrink_count + 1):
                    shrink_pic = cv2.pyrDown(shrink_pic)
            else:
                shrink_pic = cv2.pyrDown(shrink_pic)
            
            # 转换为灰度图
            if len(shrink_pic.shape) == 3:
                gray = cv2.cvtColor(shrink_pic, cv2.COLOR_BGR2GRAY)
            else:
                gray = shrink_pic.copy()
            
            # Sobel边缘检测
            grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
            grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
            sobel = cv2.subtract(grad_x, grad_y)
            sobel = cv2.convertScaleAbs(sobel)
            
            # 形态学操作增强对比度
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
            enhanced = cv2.morphologyEx(sobel, cv2.MORPH_CLOSE, kernel)
            
            # 去除噪声
            blurred = cv2.blur(sobel, (5, 5))
            _, thresh = cv2.threshold(blurred, 30, 255, cv2.THRESH_BINARY)
            
            # 找轮廓
            contours, _ = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            
            # 找最大的矩形轮廓
            max_rect = None
            max_area = 0
            
            for contour in contours:
                rect = cv2.minAreaRect(contour)
                area = rect[1][0] * rect[1][1]
                if area > max_area:
                    max_area = area
                    max_rect = rect
            
            if max_rect is None:
                return None
            
            # 获取矩形的四个角点
            box = cv2.boxPoints(max_rect)
            box = box.astype(int)
            
            # 恢复到原图坐标
            box = box * multi
            
            # 定义目标矩形
            target_size = (500, 40)
            target_points = np.array([
                [0, 0],
                [target_size[0], 0],
                [target_size[0], target_size[1]],
                [0, target_size[1]]
            ], dtype=np.float32)
            
            # 排序角点
            box = box.astype(np.float32)
            # 按x坐标排序
            sorted_points = box[np.argsort(box[:, 0])]
            
            # 左侧两点按y坐标排序
            left_points = sorted_points[:2]
            left_points = left_points[np.argsort(left_points[:, 1])]
            
            # 右侧两点按y坐标排序
            right_points = sorted_points[2:]
            right_points = right_points[np.argsort(right_points[:, 1])]
            
            # 重新排列角点
            corners = np.array([
                left_points[0],   # 左上
                right_points[0],  # 右上
                right_points[1],  # 右下
                left_points[1]    # 左下
            ], dtype=np.float32)
            
            # 透视变换
            transform_matrix = cv2.getPerspectiveTransform(corners, target_points)
            result = cv2.warpPerspective(img_cv, transform_matrix, target_size)
            
            # 转换回PIL格式
            if has_alpha:
                # 创建RGBA图像（注意：透视变换后的图像可能不保留原始alpha通道，这里使用新的透明度）
                result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                # 创建全透明的alpha通道
                new_alpha = np.ones(result.shape[:2], dtype=np.uint8) * 255
                result_image = Image.fromarray(np.dstack((result_rgb, new_alpha)))
            else:
                result_image = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
            
            return result_image
            
        except Exception as e:
            logging.error(f"图像矫正失败: {e}")
            return None
    
    @staticmethod
    def amend_image_by_outline(image: Image.Image) -> Optional[Image.Image]:
        """
        通过轮廓修正图像
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            修正后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    # 保存透明通道
                    alpha = img_array[:, :, 3]
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                    has_alpha = True
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    has_alpha = False
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                img_cv = img_array.copy()
                gray = img_array.copy()
                has_alpha = False
            
            # 二值化
            _, binary = cv2.threshold(gray, 100, 200, cv2.THRESH_BINARY)
            
            # 找轮廓（只检索外框）
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            
            for contour in contours:
                # 获取最小外接矩形
                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)
                
                # 计算矩形的两条边长
                line1 = np.linalg.norm(box[1] - box[0])
                line2 = np.linalg.norm(box[3] - box[0])
                
                # 面积太小的直接跳过
                if line1 * line2 < 600:
                    continue
                
                # 计算旋转角度
                angle = rect[2]
                if line1 > line2:
                    angle = 90 + angle
                
                # 创建ROI图像
                roi_img = np.zeros_like(img_cv)
                
                # 填充轮廓
                cv2.fillPoly(binary, [contour], 255)
                
                # 抠图到ROI
                roi_img = cv2.bitwise_and(img_cv, img_cv, mask=binary)
                
                # 旋转图像
                center = tuple(map(int, rect[0]))
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(roi_img, rotation_matrix, (img_cv.shape[1], img_cv.shape[0]))
                
                # 转换为灰度图进行第二次轮廓检测
                if len(rotated.shape) == 3:
                    rotated_gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
                else:
                    rotated_gray = rotated.copy()
                
                _, rotated_binary = cv2.threshold(rotated_gray, 80, 200, cv2.THRESH_BINARY)
                contours2, _ = cv2.findContours(rotated_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                
                for contour2 in contours2:
                    # 获取边界矩形
                    x, y, w, h = cv2.boundingRect(contour2)
                    
                    # 面积太小的跳过
                    if w * h < 600:
                        continue
                    
                    # 提取矩形区域
                    result = rotated[y:y+h, x:x+w]
                    
                    # 转换回PIL格式
                    if has_alpha:
                        # 创建RGBA图像（注意：旋转后的图像可能不保留原始alpha通道）
                        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                        # 创建全透明的alpha通道
                        new_alpha = np.ones(result.shape[:2], dtype=np.uint8) * 255
                        result_image = Image.fromarray(np.dstack((result_rgb, new_alpha)))
                    else:
                        result_image = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
                    
                    return result_image
            
            return None
            
        except Exception as e:
            logging.error(f"轮廓修正失败: {e}")
            return None
    
    @staticmethod
    def resize_bitmap(image: Image.Image, width: int, height: int) -> Optional[Image.Image]:
        """
        调整图像大小
        
        Args:
            image: 输入PIL图像对象
            width: 目标宽度
            height: 目标高度
            
        Returns:
            调整大小后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空或尺寸无效时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        if width <= 0 or height <= 0:
            raise ValueError("目标尺寸必须大于0")
            
        try:
            # 使用PIL的resize方法
            resized_image = image.resize((width, height), Image.LANCZOS)
            return resized_image
            
        except Exception as e:
            logging.error(f"调整图像大小失败: {e}")
            return None
    
    @staticmethod
    def crop_image(image: Image.Image, x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
        """
        从图像中裁剪子图像
        
        Args:
            image: 输入PIL图像对象
            x: 左上角x坐标
            y: 左上角y坐标
            width: 裁剪宽度
            height: 裁剪高度
            
        Returns:
            裁剪后的PIL子图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空或裁剪参数无效时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            raise ValueError("裁剪参数无效")
            
        try:
            img_width, img_height = image.size
            
            # 确保裁剪区域在图像范围内
            if x + width > img_width or y + height > img_height:
                raise ValueError("裁剪区域超出图像范围")
                
            # 裁剪子图像
            sub_img = image.crop((x, y, x + width, y + height))
            return sub_img
            
        except Exception as e:
            logging.error(f"裁剪子图像失败: {e}")
            return None
            
    @staticmethod
    def sub_image(image1: Image.Image, image2: Image.Image) -> Optional[Image.Image]:
        """
        图像替换（将image2复制到image1上）
        
        Args:
            image1: 目标PIL图像对象
            image2: 源PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image1 is None:
            raise ValueError("目标图像不能为空")
        if image2 is None:
            raise ValueError("源图像不能为空")
            
        try:
            # 调整image2的大小以匹配image1
            if image2.size != image1.size:
                image2_resized = image2.resize(image1.size, Image.LANCZOS)
            else:
                image2_resized = image2
                
            # 返回调整大小后的image2副本
            return image2_resized.copy()
            
        except Exception as e:
            logging.error(f"图像替换失败: {e}")
            return None
    
    @staticmethod
    def opencv_scan_card(image: Image.Image) -> Optional[Image.Image]:
        """
        扫描身份证图片，定位号码区域
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            号码区域PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if img_array.shape[2] == 4:  # RGBA
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
            else:  # RGB
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # 转换为灰度图
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # 二值化
            _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
            
            # 腐蚀操作
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (26, 26))
            eroded = cv2.erode(binary, kernel)
            
            # 轮廓检测
            contours, _ = cv2.findContours(eroded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # 找到最可能的身份证号码区域
            number_rect = None
            max_width = 0
            
            for contour in contours:
                rect = cv2.boundingRect(contour)
                # 身份证号码区域通常是宽度大于高度5倍的矩形
                if rect[2] > rect[3] * 5 and rect[2] > max_width:
                    max_width = rect[2]
                    number_rect = rect
            
            # 定位失败
            if number_rect is None or number_rect[2] == 0 or number_rect[3] == 0:
                return None
            
            # 从原图截取号码区域
            x, y, w, h = number_rect
            number_region = img_cv[y:y+h, x:x+w]
            
            # 转换为灰度图并二值化
            number_gray = cv2.cvtColor(number_region, cv2.COLOR_BGR2GRAY)
            _, number_binary = cv2.threshold(number_gray, 80, 255, cv2.THRESH_BINARY)
            
            # 转换回PIL格式
            result_image = Image.fromarray(number_binary)
            return result_image
            
        except Exception as e:
            logging.error(f"身份证扫描失败: {e}")
            return None
    
    @staticmethod
    def laplacian_sharpening_enhanced(image: Image.Image) -> Optional[Image.Image]:
        """
        增强版拉普拉斯锐化
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            锐化后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    # 保存透明通道
                    alpha = img_array[:, :, 3]
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                    has_alpha = True
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    has_alpha = False
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()
                has_alpha = False
            
            # 拉普拉斯算子
            laplacian = cv2.Laplacian(gray, cv2.CV_8U, ksize=1)
            
            # 增强锐化（权重为1.0）
            sharpened = gray.astype(np.float32) - 1.0 * laplacian.astype(np.float32)
            sharpened = np.uint8(np.clip(sharpened, 0, 255))
            
            # 转换回PIL格式
            if has_alpha:
                # 创建RGBA图像
                result_image = Image.fromarray(np.dstack((sharpened, sharpened, sharpened, alpha)))
            else:
                result_image = Image.fromarray(sharpened)
            
            return result_image
            
        except Exception as e:
            logging.error(f"增强拉普拉斯锐化失败: {e}")
            return None
    
    @staticmethod
    def laplacian_sharpening_with_bilateral_filter(image: Image.Image) -> Optional[Image.Image]:
        """
        带双边滤波的拉普拉斯锐化
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            处理后的PIL图像对象，失败返回None
            
        Raises:
            ValueError: 当输入图像为空时
        """
        if image is None:
            raise ValueError("输入图像不能为空")
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    # 保存透明通道
                    alpha = img_array[:, :, 3]
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                    has_alpha = True
                else:  # RGB
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    has_alpha = False
                # 转换为灰度图
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()
                has_alpha = False
            
            # 拉普拉斯算子
            laplacian = cv2.Laplacian(gray, cv2.CV_8U, ksize=1)
            
            # 锐化（权重为0.5）
            sharpened = gray.astype(np.float32) - 0.5 * laplacian.astype(np.float32)
            sharpened = np.uint8(np.clip(sharpened, 0, 255))
            
            # 应用双边滤波器进行抗锯齿
            bilateral = cv2.bilateralFilter(sharpened, 9, 75, 75)
            
            # 转换回PIL格式
            if has_alpha:
                # 创建RGBA图像
                result_image = Image.fromarray(np.dstack((bilateral, bilateral, bilateral, alpha)))
            else:
                result_image = Image.fromarray(bilateral)
            
            return result_image
            
        except Exception as e:
            logging.error(f"双边滤波拉普拉斯锐化失败: {e}")
            return None
    
    @staticmethod
    def _color_gradation(src: np.ndarray) -> np.ndarray:
        """
        颜色渐变处理（内部方法）
        
        Args:
            src: 输入图像数组（浮点数类型）
            
        Returns:
            处理后的图像数组
        """
        highlight = 255
        shadow = 120
        diff = highlight - shadow
        
        # 减去阴影值
        r_diff = src - shadow
        
        # 缩放到0-255范围
        temp1 = r_diff * (255.0 / diff)
        
        # 转换为8位无符号整数
        dst = np.uint8(np.clip(temp1, 0, 255))
        
        return dst
    
    @staticmethod
    def _reduce_background_algorithm(src: np.ndarray) -> np.ndarray:
        """
        背景减少算法（内部方法）
        
        Args:
            src: 输入图像数组（浮点数类型）
            
        Returns:
            处理后的图像数组
        """
        # 均值滤波
        gauss = cv2.blur(src, (101, 101))
        
        # 除法运算增强对比度
        dst2 = cv2.divide(src, gauss)
        
        # 图像锐化
        dst2 = OpenCVUtils._image_sharp(dst2, amount=101)
        
        # 转换为8位无符号整数
        dst3 = np.uint8(dst2 * 255)
        
        return dst3
    
    @staticmethod
    def _four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
        """
        四点透视变换
        
        Args:
            image: 输入OpenCV格式图像数组
            pts: 四个点的坐标数组
            
        Returns:
            透视变换后的OpenCV格式图像数组
        """
        # 获取矩形的四个角点
        rect = np.zeros((4, 2), dtype="float32")
        
        # 计算左上、右上、右下、左下四个点
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # 左上
        rect[2] = pts[np.argmax(s)]  # 右下
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # 右上
        rect[3] = pts[np.argmax(diff)]  # 左下
        
        # 计算新图像的宽度和高度
        widthA = np.sqrt(((rect[2][0] - rect[3][0]) ** 2) + ((rect[2][1] - rect[3][1]) ** 2))
        widthB = np.sqrt(((rect[1][0] - rect[0][0]) ** 2) + ((rect[1][1] - rect[0][1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.sqrt(((rect[1][0] - rect[2][0]) ** 2) + ((rect[1][1] - rect[2][1]) ** 2))
        heightB = np.sqrt(((rect[0][0] - rect[3][0]) ** 2) + ((rect[0][1] - rect[3][1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        # 设置目标点
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")
        
        # 计算透视变换矩阵
        M = cv2.getPerspectiveTransform(rect, dst)
        
        # 应用透视变换
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        
        return warped
    
    @staticmethod
    def _image_sharp(src: np.ndarray, amount: int = 100) -> np.ndarray:
        """
        图像锐化（内部方法）
        
        Args:
            src: 输入图像数组
            amount: 锐化强度
            
        Returns:
            锐化后的图像数组
        """
        # 高斯模糊
        blurred = cv2.GaussianBlur(src, (0, 0), 2.0)
        
        # 计算锐化掩码
        mask = src - blurred
        
        # 应用锐化
        sharpened = src + (amount / 100.0) * mask
        
        return np.clip(sharpened, 0, 1)