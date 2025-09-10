#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像效果处理模块 - 重构优化版本

作者: RBQ
创建时间: 2025
描述: 提供各种图像效果处理功能，包括素描效果、颜色反转、前景清除等
优化: 消除代码重复，集成BaseUtils，配置化参数，改进错误处理
"""

import cv2
import numpy as np
from PIL import Image
import logging
from typing import Optional, Union, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum
import time

# 直接导入BaseUtils类 - 去除不必要的try-except
from .base_utils import BaseUtils


class SketchAlgorithm(Enum):
    """素描算法类型"""
    CANNY_BASED = "canny"      # 基于Canny边缘检测的素描
    SOBEL_BASED = "sobel"      # 基于Sobel梯度的素描
    LAPLACIAN = "laplacian"    # 基于拉普拉斯算子的素描


@dataclass
class TextDetailConfig:
    """文字细节增强配置"""
    adaptive_method: int = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    threshold_type: int = cv2.THRESH_BINARY
    block_size: int = 11
    c_constant: float = 10.0
    morph_kernel_size: Tuple[int, int] = (2, 2)
    morph_operation: int = cv2.MORPH_CLOSE


@dataclass
class SketchConfig:
    """素描效果配置"""
    algorithm: SketchAlgorithm = SketchAlgorithm.CANNY_BASED
    blur_kernel_size: Tuple[int, int] = (5, 5)
    blur_sigma: float = 1.5
    canny_low_threshold: int = 30
    canny_high_threshold: int = 90
    morph_kernel_size: Tuple[int, int] = (3, 3)
    sobel_weight_x: float = 0.5
    sobel_weight_y: float = 0.5
    laplacian_weight: float = -0.5
    invert_result: bool = True


@dataclass
class InpaintConfig:
    """图像修复配置"""
    blur_kernel_size: Tuple[int, int] = (3, 3)
    canny_low_threshold: int = 50
    canny_high_threshold: int = 150
    dilate_kernel_size: Tuple[int, int] = (3, 3)
    inpaint_radius: int = 3
    inpaint_method: int = cv2.INPAINT_TELEA


class ImageEffectsError(Exception):
    """图像效果处理异常"""
    pass


class ImageEffects:
    """
    图像效果处理类 - 重构优化版本
    
    主要改进:
    1. 消除代码重复，提取公共方法
    2. 集成BaseUtils功能
    3. 配置化参数管理
    4. 改进错误处理机制
    5. 合并重复功能
    6. 添加性能监控
    """
    
    def __init__(self, 
                 text_config: Optional[TextDetailConfig] = None,
                 sketch_config: Optional[SketchConfig] = None,
                 inpaint_config: Optional[InpaintConfig] = None):
        """
        初始化图像效果处理器
        
        Args:
            text_config: 文字细节增强配置
            sketch_config: 素描效果配置
            inpaint_config: 图像修复配置
        """
        self.text_config = text_config or TextDetailConfig()
        self.sketch_config = sketch_config or SketchConfig()
        self.inpaint_config = inpaint_config or InpaintConfig()
        
        # 性能统计
        self._processing_stats = {
            'total_processed': 0,
            'total_time': 0.0,
            'success_count': 0,
            'error_count': 0
        }
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
    
    def _prepare_image(self, image: Image.Image) -> Tuple[np.ndarray, np.ndarray, bool]:
        """
        统一的图像预处理方法
        
        Args:
            image: 输入PIL图像
            
        Returns:
            Tuple[OpenCV图像, 原始数组, 是否有Alpha通道]
            
        Raises:
            ImageEffectsError: 图像验证失败时
        """
        # 输入验证 - 检查PIL图像
        if image is None:
            raise ImageEffectsError("输入图像不能为空")
        
        if not hasattr(image, 'size') or image.size[0] <= 0 or image.size[1] <= 0:
            raise ImageEffectsError("输入图像尺寸无效")
        
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            
            # 验证转换后的数组
            if img_array.size == 0:
                raise ImageEffectsError("图像数据为空")
            
            img_cv = BaseUtils.convert_pil_to_opencv(image)
            
            # 检查是否有Alpha通道
            has_alpha = len(img_array.shape) == 3 and img_array.shape[2] == 4
            
            return img_cv, img_array, has_alpha
            
        except Exception as e:
            raise ImageEffectsError(f"图像预处理失败: {e}")
    
    def _create_result_image(self, processed_cv: np.ndarray, 
                           original_array: np.ndarray, 
                           has_alpha: bool,
                           preserve_alpha: bool = True) -> Image.Image:
        """
        统一的结果图像创建方法
        
        Args:
            processed_cv: 处理后的OpenCV图像
            original_array: 原始PIL图像数组
            has_alpha: 是否有Alpha通道
            preserve_alpha: 是否保持Alpha通道
            
        Returns:
            PIL图像对象
        """
        try:
            # 处理灰度图像
            if len(processed_cv.shape) == 2:
                if has_alpha and preserve_alpha:
                    # 创建RGBA图像
                    alpha = original_array[:, :, 3]
                    rgba = np.dstack((processed_cv, processed_cv, processed_cv, alpha))
                    return Image.fromarray(rgba)
                else:
                    return Image.fromarray(processed_cv)
            
            # 处理彩色图像
            if has_alpha and preserve_alpha:
                # 保持原始Alpha通道
                alpha = original_array[:, :, 3]
                rgb = cv2.cvtColor(processed_cv, cv2.COLOR_BGR2RGB)
                rgba = np.dstack((rgb, alpha))
                return Image.fromarray(rgba)
            else:
                # 转换BGR到RGB
                rgb = cv2.cvtColor(processed_cv, cv2.COLOR_BGR2RGB)
                return Image.fromarray(rgb)
                
        except Exception as e:
            raise ImageEffectsError(f"结果图像创建失败: {e}")
    
    def _record_processing_time(self, start_time: float, success: bool):
        """记录处理时间和统计信息"""
        processing_time = time.time() - start_time
        self._processing_stats['total_processed'] += 1
        self._processing_stats['total_time'] += processing_time
        
        if success:
            self._processing_stats['success_count'] += 1
        else:
            self._processing_stats['error_count'] += 1
    
    def process_image_for_text_detail(self, 
                                    image: Image.Image,
                                    config: Optional[TextDetailConfig] = None) -> Image.Image:
        """
        处理图像以增强文字细节
        
        Args:
            image: 输入PIL图像对象
            config: 可选的配置参数，覆盖默认配置
            
        Returns:
            处理后的PIL图像对象
            
        Raises:
            ImageEffectsError: 处理失败时
        """
        start_time = time.time()
        
        try:
            # 使用传入的配置或默认配置
            cfg = config or self.text_config
            
            # 预处理图像
            img_cv, img_array, has_alpha = self._prepare_image(image)
            
            # 转换为灰度图
            gray = BaseUtils.prepare_grayscale(img_cv, normalize=False)
            
            # 确保数据类型为uint8
            if gray.dtype != np.uint8:
                gray = gray.astype(np.uint8)
            
            # 参数验证
            if cfg.block_size % 2 == 0:
                cfg.block_size += 1  # 确保为奇数
            
            # 自适应阈值二值化
            binary = cv2.adaptiveThreshold(
                gray, 255, cfg.adaptive_method, 
                cfg.threshold_type, cfg.block_size, cfg.c_constant
            )
            
            # 形态学操作增强文字清晰度
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, cfg.morph_kernel_size)
            morph = cv2.morphologyEx(binary, cfg.morph_operation, kernel)
            
            # 创建结果图像
            result = self._create_result_image(morph, img_array, has_alpha, preserve_alpha=False)
            
            self._record_processing_time(start_time, True)
            return result
            
        except Exception as e:
            self._record_processing_time(start_time, False)
            self.logger.error(f"文字细节处理失败: {e}")
            raise ImageEffectsError(f"文字细节处理失败: {e}")
    
    def create_sketch_effect(self, 
                           image: Image.Image,
                           algorithm: Optional[SketchAlgorithm] = None,
                           config: Optional[SketchConfig] = None) -> Image.Image:
        """
        创建素描效果 (合并了sketch_image和sketch_effect方法)
        
        Args:
            image: 输入PIL图像对象
            algorithm: 素描算法类型，覆盖配置中的算法
            config: 可选的配置参数，覆盖默认配置
            
        Returns:
            处理后的PIL图像对象
            
        Raises:
            ImageEffectsError: 处理失败时
        """
        start_time = time.time()
        
        try:
            # 使用传入的配置或默认配置
            cfg = config or self.sketch_config
            if algorithm:
                cfg.algorithm = algorithm
            
            # 预处理图像
            img_cv, img_array, has_alpha = self._prepare_image(image)
            
            # 转换为灰度图
            gray = BaseUtils.prepare_grayscale(img_cv, normalize=False)
            
            # 确保数据类型为uint8
            if gray.dtype != np.uint8:
                gray = gray.astype(np.uint8)
            
            # 根据算法类型处理
            if cfg.algorithm == SketchAlgorithm.CANNY_BASED:
                sketch = self._canny_sketch(gray, cfg)
            elif cfg.algorithm == SketchAlgorithm.SOBEL_BASED:
                sketch = self._sobel_sketch(gray, cfg)
            elif cfg.algorithm == SketchAlgorithm.LAPLACIAN:
                sketch = self._laplacian_sketch(gray, cfg)
            else:
                raise ImageEffectsError(f"不支持的素描算法: {cfg.algorithm}")
            
            # 可选的图像反转
            if cfg.invert_result:
                sketch = cv2.bitwise_not(sketch)
            
            # 创建结果图像
            result = self._create_result_image(sketch, img_array, has_alpha, preserve_alpha=False)
            
            self._record_processing_time(start_time, True)
            return result
            
        except Exception as e:
            self._record_processing_time(start_time, False)
            self.logger.error(f"素描效果处理失败: {e}")
            raise ImageEffectsError(f"素描效果处理失败: {e}")
    
    def _canny_sketch(self, gray: np.ndarray, config: SketchConfig) -> np.ndarray:
        """基于Canny边缘检测的素描算法"""
        # 高斯模糊
        blur = cv2.GaussianBlur(gray, config.blur_kernel_size, config.blur_sigma)
        
        # Canny边缘检测
        edge = cv2.Canny(blur, config.canny_low_threshold, config.canny_high_threshold)
        
        # 形态学闭运算
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, config.morph_kernel_size)
        morph = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, kernel)
        
        # 可选的拉普拉斯锐化
        if config.laplacian_weight != 0:
            laplace = cv2.Laplacian(morph, cv2.CV_8U, ksize=3)
            morph = cv2.addWeighted(morph, 1.0, laplace, config.laplacian_weight, 0)
        
        return morph
    
    def _sobel_sketch(self, gray: np.ndarray, config: SketchConfig) -> np.ndarray:
        """基于Sobel梯度的素描算法"""
        # 高斯模糊
        blurred = cv2.GaussianBlur(gray, config.blur_kernel_size, 0)
        
        # Sobel梯度
        gradient_x = cv2.Sobel(blurred, cv2.CV_16S, 1, 0)
        gradient_y = cv2.Sobel(blurred, cv2.CV_16S, 0, 1)
        
        # 转换为绝对值
        abs_gradient_x = cv2.convertScaleAbs(gradient_x)
        abs_gradient_y = cv2.convertScaleAbs(gradient_y)
        
        # 合并梯度
        sketch = cv2.addWeighted(
            abs_gradient_x, config.sobel_weight_x, 
            abs_gradient_y, config.sobel_weight_y, 0
        )
        
        return sketch
    
    def _laplacian_sketch(self, gray: np.ndarray, config: SketchConfig) -> np.ndarray:
        """基于拉普拉斯算子的素描算法"""
        # 高斯模糊
        blurred = cv2.GaussianBlur(gray, config.blur_kernel_size, config.blur_sigma)
        
        # 拉普拉斯边缘检测
        laplacian = cv2.Laplacian(blurred, cv2.CV_8U, ksize=3)
        
        # 形态学操作
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, config.morph_kernel_size)
        sketch = cv2.morphologyEx(laplacian, cv2.MORPH_CLOSE, kernel)
        
        return sketch
    
    def invert_colors(self, 
                     image: Image.Image,
                     preserve_alpha: bool = True) -> Image.Image:
        """
        颜色反转 (合并了invert_color和invert_colors方法)
        
        Args:
            image: 输入PIL图像对象
            preserve_alpha: 是否保持Alpha通道不变
            
        Returns:
            处理后的PIL图像对象
            
        Raises:
            ImageEffectsError: 处理失败时
        """
        start_time = time.time()
        
        try:
            # 预处理图像
            img_cv, img_array, has_alpha = self._prepare_image(image)
            
            # 处理灰度图像
            if len(img_array.shape) == 2:
                inverted = cv2.bitwise_not(img_array)
                result = Image.fromarray(inverted)
                self._record_processing_time(start_time, True)
                return result
            
            # 处理彩色图像
            if has_alpha and preserve_alpha:
                # 分离Alpha通道
                alpha = img_array[:, :, 3]
                rgb_part = img_array[:, :, :3]
                
                # 反转RGB部分
                inverted_rgb = cv2.bitwise_not(rgb_part)
                
                # 重新合并Alpha通道
                result_array = np.dstack((inverted_rgb, alpha))
                result = Image.fromarray(result_array)
            else:
                # 反转整个图像
                if len(img_array.shape) == 3:
                    inverted = cv2.bitwise_not(img_array)
                    result = Image.fromarray(inverted)
                else:
                    inverted = cv2.bitwise_not(img_array)
                    result = Image.fromarray(inverted)
            
            self._record_processing_time(start_time, True)
            return result
            
        except Exception as e:
            self._record_processing_time(start_time, False)
            self.logger.error(f"颜色反转失败: {e}")
            raise ImageEffectsError(f"颜色反转失败: {e}")
    
    def clear_foreground(self, 
                        image: Image.Image,
                        config: Optional[InpaintConfig] = None) -> Image.Image:
        """
        清除前景文字
        
        Args:
            image: 输入PIL图像对象
            config: 可选的配置参数，覆盖默认配置
            
        Returns:
            处理后的PIL图像对象
            
        Raises:
            ImageEffectsError: 处理失败时
        """
        start_time = time.time()
        
        try:
            # 使用传入的配置或默认配置
            cfg = config or self.inpaint_config
            
            # 预处理图像
            img_cv, img_array, has_alpha = self._prepare_image(image)
            
            # 转换为灰度图用于边缘检测
            gray = BaseUtils.prepare_grayscale(img_cv, normalize=False)
            
            # 确保数据类型为uint8
            if gray.dtype != np.uint8:
                gray = gray.astype(np.uint8)
            
            # 高斯模糊
            blurred = cv2.GaussianBlur(gray, cfg.blur_kernel_size, 0)
            
            # Canny边缘检测
            edges = cv2.Canny(blurred, cfg.canny_low_threshold, cfg.canny_high_threshold)
            
            # 膨胀操作
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, cfg.dilate_kernel_size)
            dilated = cv2.dilate(edges, kernel)
            
            # 图像修复
            repaired = cv2.inpaint(img_cv, dilated, cfg.inpaint_radius, cfg.inpaint_method)
            
            # 创建结果图像
            result = self._create_result_image(repaired, img_array, has_alpha, preserve_alpha=True)
            
            self._record_processing_time(start_time, True)
            return result
            
        except Exception as e:
            self._record_processing_time(start_time, False)
            self.logger.error(f"前景清除失败: {e}")
            raise ImageEffectsError(f"前景清除失败: {e}")
    
    def batch_process(self, 
                     images: list[Image.Image], 
                     effect_name: str,
                     **kwargs) -> list[Image.Image]:
        """
        批量处理图像
        
        Args:
            images: 图像列表
            effect_name: 效果方法名
            **kwargs: 传递给效果方法的参数
            
        Returns:
            处理后的图像列表
            
        Raises:
            ImageEffectsError: 批量处理失败时
        """
        if not images:
            raise ImageEffectsError("图像列表不能为空")
        
        # 获取效果方法
        if not hasattr(self, effect_name):
            raise ImageEffectsError(f"不支持的效果方法: {effect_name}")
        
        effect_method = getattr(self, effect_name)
        results = []
        failed_count = 0
        
        for i, image in enumerate(images):
            try:
                result = effect_method(image, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.warning(f"批量处理第{i+1}张图像失败: {e}")
                results.append(None)
                failed_count += 1
        
        if failed_count > 0:
            self.logger.warning(f"批量处理完成，{failed_count}/{len(images)}张图像处理失败")
        
        return results
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        获取处理统计信息
        
        Returns:
            包含统计信息的字典
        """
        stats = self._processing_stats.copy()
        if stats['total_processed'] > 0:
            stats['avg_processing_time'] = stats['total_time'] / stats['total_processed']
            stats['success_rate'] = stats['success_count'] / stats['total_processed']
        else:
            stats['avg_processing_time'] = 0.0
            stats['success_rate'] = 0.0
        
        return stats
    
    def reset_stats(self):
        """重置处理统计信息"""
        self._processing_stats = {
            'total_processed': 0,
            'total_time': 0.0,
            'success_count': 0,
            'error_count': 0
        }
    
    # 向后兼容的方法别名
    def sketch_image(self, image: Image.Image) -> Image.Image:
        """向后兼容的素描方法 (使用Canny算法)"""
        return self.create_sketch_effect(image, SketchAlgorithm.CANNY_BASED)
    
    def sketch_effect(self, image: Image.Image) -> Image.Image:
        """向后兼容的素描方法 (使用Sobel算法)"""
        return self.create_sketch_effect(image, SketchAlgorithm.SOBEL_BASED)
    
    def invert_color(self, image: Image.Image) -> Image.Image:
        """向后兼容的颜色反转方法"""
        return self.invert_colors(image, preserve_alpha=True)