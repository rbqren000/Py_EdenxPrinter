#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenCV基础工具类

作者: RBQ
创建时间: 2025
描述: 提供OpenCV图像处理的基础工具方法，包括格式转换、预处理等
版本: 2.0 - 性能优化版
"""

import cv2
import numpy as np
from PIL import Image
import logging
from typing import Optional, Union, Tuple


class BaseUtils:
    """OpenCV基础工具类 - 性能优化版"""
    
    # 配置常量
    DEFAULT_BLUR_KERNEL_BASE = 101
    DEFAULT_SHARPEN_AMOUNT = 100
    DEFAULT_SHADOW_VALUE = 120
    DEFAULT_HIGHLIGHT_VALUE = 255
    MIN_KERNEL_SIZE = 5
    MAX_KERNEL_SIZE = 201
    
    @staticmethod
    def convert_pil_to_opencv(image: Image.Image) -> np.ndarray:
        """
        统一的PIL到OpenCV转换（优化版）
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            OpenCV格式的图像数组
            
        Raises:
            ValueError: 当输入图像无效时
        """
        if image is None:
            raise ValueError("输入图像不能为None")
        
        try:
            img_array = np.array(image)
            
            if img_array.size == 0:
                raise ValueError("输入图像为空")
            
            if len(img_array.shape) == 2:  # 灰度图
                return img_array
            elif len(img_array.shape) == 3:
                if img_array.shape[2] == 4:  # RGBA
                    return cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                elif img_array.shape[2] == 3:  # RGB
                    return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                else:
                    raise ValueError(f"不支持的通道数: {img_array.shape[2]}")
            else:
                raise ValueError(f"不支持的图像维度: {len(img_array.shape)}")
                
        except Exception as e:
            logging.error(f"PIL到OpenCV转换失败: {e}")
            raise
    
    @staticmethod
    def prepare_grayscale(img_cv: np.ndarray, normalize: bool = True) -> np.ndarray:
        """
        统一的灰度预处理（修复版）
        
        Args:
            img_cv: OpenCV格式的图像数组
            normalize: 是否归一化到[0,1]范围
            
        Returns:
            处理后的灰度图像
            
        Raises:
            ValueError: 当输入图像无效时
        """
        if img_cv is None or img_cv.size == 0:
            raise ValueError("输入图像不能为空")
        
        if not isinstance(img_cv, np.ndarray):
            raise ValueError("输入必须是numpy数组")
        
        try:
            # 修复：确保不修改原始数据
            if len(img_cv.shape) == 3:
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                # 修复：创建副本避免修改原始数据
                gray = img_cv.copy() if normalize else img_cv
            
            if normalize:
                # 确保输入是uint8类型再归一化
                if gray.dtype != np.uint8:
                    gray = np.clip(gray, 0, 255).astype(np.uint8)
                return gray.astype(np.float32) / 255.0
            else:
                return gray
                
        except Exception as e:
            logging.error(f"灰度预处理失败: {e}")
            raise
    
    @staticmethod
    def calculate_adaptive_kernel_size(
        image: np.ndarray, 
        base_size: int = None,
        min_size: int = None,
        max_size: int = None
    ) -> int:
        """
        计算自适应滤波核大小（修复版）
        
        Args:
            image: 输入图像
            base_size: 基础核大小，默认使用类常量
            min_size: 最小核大小，默认使用类常量
            max_size: 最大核大小，默认使用类常量
            
        Returns:
            优化后的核大小
            
        Raises:
            ValueError: 当输入参数无效时
        """
        if image is None or image.size == 0:
            raise ValueError("输入图像不能为空")
        
        if not isinstance(image, np.ndarray):
            raise ValueError("输入必须是numpy数组")
        
        # 使用默认值
        if base_size is None:
            base_size = BaseUtils.DEFAULT_BLUR_KERNEL_BASE
        if min_size is None:
            min_size = BaseUtils.MIN_KERNEL_SIZE
        if max_size is None:
            max_size = BaseUtils.MAX_KERNEL_SIZE
        
        # 修复：验证参数范围
        if base_size < 1 or min_size < 1 or max_size < 1:
            raise ValueError("核大小必须为正数")
        if min_size > max_size:
            raise ValueError("最小核大小不能大于最大核大小")
        
        try:
            height, width = image.shape[:2]
            
            # 优化：使用更精确的缩放策略
            image_diagonal = np.sqrt(width * width + height * height)
            reference_diagonal = 1414.0  # sqrt(1000*1000 + 1000*1000)
            
            scale_factor = image_diagonal / reference_diagonal
            adaptive_size = int(base_size * np.clip(scale_factor, 0.3, 3.0))
            
            # 确保在合理范围内且为奇数
            adaptive_size = np.clip(adaptive_size, min_size, max_size)
            return adaptive_size if adaptive_size % 2 == 1 else adaptive_size + 1
            
        except Exception as e:
            logging.error(f"自适应核大小计算失败: {e}")
            # 修复：确保返回值有效
            fallback_size = base_size if base_size is not None else BaseUtils.DEFAULT_BLUR_KERNEL_BASE
            return fallback_size if fallback_size % 2 == 1 else fallback_size + 1
    
    @staticmethod
    def image_sharp(
        src: np.ndarray, 
        amount: int = None,
        sigma: float = 2.0
    ) -> np.ndarray:
        """
        图像锐化（修复版）
        
        Args:
            src: 输入图像数组（浮点数类型，范围[0,1]）
            amount: 锐化强度，默认使用类常量
            sigma: 高斯模糊标准差
            
        Returns:
            锐化后的图像数组（保持输入数据类型和范围）
            
        Raises:
            ValueError: 当输入参数无效时
        """
        if src is None or src.size == 0:
            raise ValueError("输入图像不能为空")
        
        if not isinstance(src, np.ndarray):
            raise ValueError("输入必须是numpy数组")
        
        if amount is None:
            amount = BaseUtils.DEFAULT_SHARPEN_AMOUNT
        
        if not (0 <= amount <= 500):
            raise ValueError("锐化强度应在0-500范围内")
        
        if sigma <= 0:
            raise ValueError("高斯模糊标准差必须为正数")
        
        try:
            # 修复：确保输入数据范围正确
            if src.dtype == np.uint8:
                # 如果输入是uint8，转换为float32进行处理
                src_float = src.astype(np.float32) / 255.0
                return_uint8 = True
            else:
                # 假设输入已经是[0,1]范围的float
                src_float = src
                return_uint8 = False
            
            # 验证数据范围
            if np.any(src_float < 0) or np.any(src_float > 1):
                logging.warning("输入图像数据超出[0,1]范围，将进行裁剪")
                src_float = np.clip(src_float, 0.0, 1.0)
            
            # 高斯模糊
            blurred = cv2.GaussianBlur(src_float, (0, 0), sigma)
            
            # 计算锐化掩码
            mask = src_float - blurred
            
            # 应用锐化
            amount_factor = amount * 0.01
            sharpened = src_float + amount_factor * mask
            
            # 裁剪到有效范围
            sharpened = np.clip(sharpened, 0.0, 1.0)
            
            # 修复：保持输入数据类型
            if return_uint8:
                return (sharpened * 255).astype(np.uint8)
            else:
                return sharpened
            
        except Exception as e:
            logging.error(f"图像锐化失败: {e}")
            return src
    
    @staticmethod
    def color_gradation(
        src: np.ndarray,
        shadow: int = None,
        highlight: int = None
    ) -> np.ndarray:
        """
        颜色渐变处理（修复版）
        
        Args:
            src: 输入图像数组（支持uint8或float32类型）
            shadow: 阴影值（0-255范围），默认使用类常量
            highlight: 高光值（0-255范围），默认使用类常量
            
        Returns:
            处理后的图像数组（uint8类型）
            
        Raises:
            ValueError: 当输入参数无效时
        """
        if src is None or src.size == 0:
            raise ValueError("输入图像不能为空")
        
        if not isinstance(src, np.ndarray):
            raise ValueError("输入必须是numpy数组")
        
        if shadow is None:
            shadow = BaseUtils.DEFAULT_SHADOW_VALUE
        if highlight is None:
            highlight = BaseUtils.DEFAULT_HIGHLIGHT_VALUE
        
        if shadow >= highlight:
            raise ValueError("阴影值必须小于高光值")
        
        if not (0 <= shadow <= 255) or not (0 <= highlight <= 255):
            raise ValueError("阴影值和高光值必须在0-255范围内")
        
        try:
            # 修复：统一处理不同输入类型
            if src.dtype == np.uint8:
                src_255 = src.astype(np.float32)
            elif src.dtype in [np.float32, np.float64]:
                # 检查数据范围
                if np.max(src) <= 1.0:
                    # 输入是[0,1]范围
                    src_255 = src * 255.0
                else:
                    # 输入可能已经是[0,255]范围
                    src_255 = src
            else:
                # 其他类型转换为float32
                src_255 = src.astype(np.float32)
                if np.max(src_255) <= 1.0:
                    src_255 *= 255.0
            
            # 预计算常量
            diff = highlight - shadow
            scale_factor = 255.0 / diff
            
            # 减去阴影值并缩放
            adjusted = (src_255 - shadow) * scale_factor
            
            # 转换为8位无符号整数
            return np.clip(adjusted, 0, 255).astype(np.uint8)
            
        except Exception as e:
            logging.error(f"颜色渐变处理失败: {e}")
            # 修复：更安全的fallback
            if src.dtype == np.uint8:
                return src
            else:
                return np.clip(src * 255 if np.max(src) <= 1.0 else src, 0, 255).astype(np.uint8)
    
    @staticmethod
    def reduce_background_algorithm(
        src: np.ndarray,
        kernel_size: int = None,
        sharpen_amount: int = None,
        use_gaussian: bool = True
    ) -> np.ndarray:
        """
        背景减少算法（优化版）
        
        Args:
            src: 输入图像数组（浮点数类型，范围[0,1]）
            kernel_size: 滤波核大小，None表示自动计算
            sharpen_amount: 锐化强度，默认使用类常量
            use_gaussian: 是否使用高斯滤波（更高效）
            
        Returns:
            处理后的图像数组（uint8类型）
            
        Raises:
            ValueError: 当输入参数无效时
        """
        if src is None or src.size == 0:
            raise ValueError("输入图像不能为空")
        
        try:
            # 自适应计算核大小
            if kernel_size is None:
                kernel_size = BaseUtils.calculate_adaptive_kernel_size(src)
            
            if sharpen_amount is None:
                sharpen_amount = BaseUtils.DEFAULT_SHARPEN_AMOUNT + 1  # 101
            
            # 优化：使用更高效的滤波方法
            if use_gaussian:
                # 高斯滤波比均值滤波更高效且效果更好
                sigma = kernel_size / 6.0  # 经验公式
                background = cv2.GaussianBlur(src, (kernel_size, kernel_size), sigma)
            else:
                # 保持原有的均值滤波选项
                background = cv2.blur(src, (kernel_size, kernel_size))
            
            # 防止除零错误
            background = np.maximum(background, 1e-7)
            
            # 除法运算增强对比度
            enhanced = cv2.divide(src, background)
            
            # 图像锐化
            sharpened = BaseUtils.image_sharp(enhanced, amount=sharpen_amount)
            
            # 转换为8位无符号整数
            result = np.clip(sharpened * 255, 0, 255).astype(np.uint8)
            
            return result
            
        except Exception as e:
            logging.error(f"背景减少算法失败: {e}")
            return (src * 255).astype(np.uint8)
    
    @staticmethod
    def four_point_transform(
        image: np.ndarray, 
        pts: np.ndarray,
        output_size: Optional[Tuple[int, int]] = None
    ) -> np.ndarray:
        """
        四点透视变换（修复版）
        
        Args:
            image: 输入OpenCV格式图像数组
            pts: 四个点的坐标数组 (4, 2)
            output_size: 输出图像尺寸 (width, height)，None表示自动计算
            
        Returns:
            透视变换后的OpenCV格式图像数组
            
        Raises:
            ValueError: 当输入参数无效时
        """
        if image is None or image.size == 0:
            raise ValueError("输入图像不能为空")
        
        if not isinstance(image, np.ndarray):
            raise ValueError("输入必须是numpy数组")
        
        if pts is None or pts.shape != (4, 2):
            raise ValueError("需要提供4个点的坐标")
        
        # 验证点坐标是否有效
        if np.any(np.isnan(pts)) or np.any(np.isinf(pts)):
            raise ValueError("点坐标包含无效值")
        
        try:
            # 修复：使用更可靠的四点排序算法
            pts = pts.astype(np.float32)
            
            # 计算质心
            center = np.mean(pts, axis=0)
            
            # 计算每个点相对于质心的角度
            angles = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])
            
            # 按角度排序：左上、右上、右下、左下
            sorted_indices = np.argsort(angles)
            
            # 重新排列点：从左上开始顺时针
            rect = np.zeros((4, 2), dtype=np.float32)
            
            # 找到最左上的点作为起始点
            top_left_idx = sorted_indices[np.argmin(pts[sorted_indices, 0] + pts[sorted_indices, 1])]
            start_idx = np.where(sorted_indices == top_left_idx)[0][0]
            
            # 按顺时针顺序排列
            for i in range(4):
                rect[i] = pts[sorted_indices[(start_idx + i) % 4]]
            
            if output_size is None:
                # 计算新图像的宽度和高度
                width_top = np.linalg.norm(rect[1] - rect[0])
                width_bottom = np.linalg.norm(rect[2] - rect[3])
                max_width = max(int(width_top), int(width_bottom))
                
                height_left = np.linalg.norm(rect[3] - rect[0])
                height_right = np.linalg.norm(rect[2] - rect[1])
                max_height = max(int(height_left), int(height_right))
                
                # 修复：确保尺寸合理
                max_width = max(max_width, 1)
                max_height = max(max_height, 1)
            else:
                max_width, max_height = output_size
                if max_width <= 0 or max_height <= 0:
                    raise ValueError("输出尺寸必须为正数")
            
            # 验证输出尺寸是否过大（防止内存溢出）
            max_pixels = 50 * 1024 * 1024  # 50M像素限制
            if max_width * max_height > max_pixels:
                raise ValueError(f"输出图像过大: {max_width}x{max_height}")
            
            # 设置目标点
            dst = np.array([
                [0, 0],
                [max_width - 1, 0],
                [max_width - 1, max_height - 1],
                [0, max_height - 1]
            ], dtype=np.float32)
            
            # 计算透视变换矩阵
            M = cv2.getPerspectiveTransform(rect, dst)
            
            # 检查变换矩阵是否有效
            if np.any(np.isnan(M)) or np.any(np.isinf(M)):
                raise ValueError("透视变换矩阵无效")
            
            # 应用透视变换
            warped = cv2.warpPerspective(
                image, M, (max_width, max_height),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=0
            )
            
            return warped
            
        except cv2.error as e:
            logging.error(f"OpenCV透视变换失败: {e}")
            raise ValueError(f"透视变换失败: {e}")
        except Exception as e:
            logging.error(f"四点透视变换失败: {e}")
            raise
    
    @staticmethod
    def validate_image(image: np.ndarray, min_size: int = 1) -> bool:
        """
        验证图像是否有效（增强版）
        
        Args:
            image: 输入图像数组
            min_size: 最小尺寸要求
            
        Returns:
            是否为有效图像
        """
        if image is None:
            return False
        
        if not isinstance(image, np.ndarray):
            return False
        
        if image.size == 0:
            return False
        
        if len(image.shape) not in [2, 3]:
            return False
        
        # 修复：添加更多验证
        try:
            height, width = image.shape[:2]
            
            if height < min_size or width < min_size:
                return False
            
            # 检查数据类型是否支持
            if image.dtype not in [np.uint8, np.uint16, np.float32, np.float64]:
                return False
            
            # 检查是否包含无效值
            if np.any(np.isnan(image)) or np.any(np.isinf(image)):
                return False
            
            # 检查3通道图像的通道数
            if len(image.shape) == 3 and image.shape[2] not in [1, 3, 4]:
                return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def get_memory_usage_mb(image: np.ndarray) -> float:
        """
        计算图像内存占用（MB）
        
        Args:
            image: 输入图像数组
            
        Returns:
            内存占用大小（MB）
        """
        if image is None or image.size == 0:
            return 0.0
        
        return image.nbytes / (1024 * 1024)