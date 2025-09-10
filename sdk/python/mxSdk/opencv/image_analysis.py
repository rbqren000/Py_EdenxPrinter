#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像分析和变换模块

作者: RBQ
创建时间: 2025
描述: 提供图像分析和变换功能，包括边缘检测、直方图均衡化、锐化、对数变换、伽马校正等
版本: 2.0 - 重构优化版
"""

import cv2
import numpy as np
from PIL import Image
import logging
from typing import Optional, Union, Tuple, Dict, Any
from dataclasses import dataclass, field
from .base_utils import BaseUtils


@dataclass
class EdgeDetectionConfig:
    """边缘检测配置"""
    # Sobel参数
    sobel_ksize: int = 3
    sobel_scale: float = 1.0
    sobel_delta: float = 0.0
    
    # Canny参数
    canny_low_threshold: int = 50
    canny_high_threshold: int = 150
    canny_aperture_size: int = 3
    canny_l2_gradient: bool = False


@dataclass
class SharpeningConfig:
    """锐化配置"""
    # 拉普拉斯锐化
    laplacian_ksize: int = 1
    laplacian_scale: float = 1.0
    laplacian_delta: float = 0.0
    sharpening_weight: float = 1.0
    
    # 双边滤波参数
    bilateral_d: int = 9
    bilateral_sigma_color: float = 75.0
    bilateral_sigma_space: float = 75.0


@dataclass
class TransformConfig:
    """变换配置"""
    # 伽马校正
    gamma_default: float = 1.0
    gamma_min: float = 0.1
    gamma_max: float = 3.0
    
    # 对数变换
    log_c_auto: bool = True
    log_c_value: float = 1.0


class ImageAnalysis:
    """图像分析和变换处理类 - 重构优化版"""
    
    def __init__(self, 
                 edge_config: Optional[EdgeDetectionConfig] = None,
                 sharpening_config: Optional[SharpeningConfig] = None,
                 transform_config: Optional[TransformConfig] = None):
        """
        初始化图像分析类
        
        Args:
            edge_config: 边缘检测配置
            sharpening_config: 锐化配置
            transform_config: 变换配置
        """
        self.edge_config = edge_config or EdgeDetectionConfig()
        self.sharpening_config = sharpening_config or SharpeningConfig()
        self.transform_config = transform_config or TransformConfig()
        
        # 性能统计
        self._processing_stats = {
            'total_processed': 0,
            'success_count': 0,
            'error_count': 0,
            'processing_times': []
        }
    
    def _prepare_image(self, image: Image.Image, preserve_color: bool = False) -> Tuple[np.ndarray, bool, Optional[np.ndarray]]:
        """
        统一的图像预处理（消除重复代码）
        
        Args:
            image: 输入PIL图像
            preserve_color: 是否保持彩色
            
        Returns:
            (处理后的图像数组, 是否有透明通道, 透明通道数组)
            
        Raises:
            ValueError: 输入图像无效时
        """
        if not BaseUtils.validate_image(np.array(image)):
            raise ValueError("输入图像无效")
        
        # 使用BaseUtils进行转换
        img_cv = BaseUtils.convert_pil_to_opencv(image)
        
        # 检查透明通道
        img_array = np.array(image)
        has_alpha = len(img_array.shape) == 3 and img_array.shape[2] == 4
        alpha_channel = img_array[:, :, 3] if has_alpha else None
        
        if preserve_color and len(img_cv.shape) == 3:
            # 保持彩色
            return img_cv, has_alpha, alpha_channel
        else:
            # 转换为灰度
            gray = BaseUtils.prepare_grayscale(img_cv, normalize=False)
            return gray, has_alpha, alpha_channel
    
    def _create_result_image(self, 
                           processed: np.ndarray, 
                           has_alpha: bool, 
                           alpha_channel: Optional[np.ndarray],
                           is_color: bool = False) -> Image.Image:
        """
        统一的结果图像创建
        
        Args:
            processed: 处理后的图像数组
            has_alpha: 是否有透明通道
            alpha_channel: 透明通道数组
            is_color: 是否为彩色图像
            
        Returns:
            PIL图像对象
        """
        if has_alpha and alpha_channel is not None:
            if is_color and len(processed.shape) == 3:
                # 彩色图像 + 透明通道
                result_array = np.dstack((processed, alpha_channel))
            else:
                # 灰度图像 + 透明通道
                if len(processed.shape) == 2:
                    result_array = np.dstack((processed, processed, processed, alpha_channel))
                else:
                    result_array = np.dstack((processed, alpha_channel))
            return Image.fromarray(result_array, 'RGBA')
        else:
            if is_color and len(processed.shape) == 3:
                # 彩色图像
                return Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB))
            else:
                # 灰度图像
                return Image.fromarray(processed, 'L')
    
    def _update_stats(self, success: bool, processing_time: float = 0.0):
        """更新处理统计"""
        self._processing_stats['total_processed'] += 1
        if success:
            self._processing_stats['success_count'] += 1
            self._processing_stats['processing_times'].append(processing_time)
        else:
            self._processing_stats['error_count'] += 1
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        stats = self._processing_stats.copy()
        if stats['processing_times']:
            stats['avg_processing_time'] = np.mean(stats['processing_times'])
            stats['max_processing_time'] = np.max(stats['processing_times'])
            stats['min_processing_time'] = np.min(stats['processing_times'])
        return stats
    
    def apply_sobel_edge_detection(self, 
                                 image: Image.Image,
                                 ksize: Optional[int] = None,
                                 scale: Optional[float] = None,
                                 delta: Optional[float] = None) -> Image.Image:
        """
        应用Sobel边缘检测（优化版）
        
        Args:
            image: 输入PIL图像对象
            ksize: Sobel算子大小，None使用配置值
            scale: 缩放因子，None使用配置值
            delta: 偏移值，None使用配置值
            
        Returns:
            处理后的PIL图像对象
            
        Raises:
            ValueError: 当输入图像无效时
            RuntimeError: 处理失败时
        """
        import time
        start_time = time.time()
        
        try:
            # 使用统一的图像预处理
            gray, has_alpha, alpha_channel = self._prepare_image(image, preserve_color=False)
            
            # 使用配置参数
            ksize = ksize or self.edge_config.sobel_ksize
            scale = scale or self.edge_config.sobel_scale
            delta = delta or self.edge_config.sobel_delta
            
            # 参数验证
            if ksize not in [1, 3, 5, 7]:
                raise ValueError("Sobel核大小必须是1, 3, 5, 7之一")
            
            # Sobel边缘检测
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize, scale=scale, delta=delta)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize, scale=scale, delta=delta)
            
            # 计算梯度幅值（优化计算）
            sobel = np.sqrt(sobel_x**2 + sobel_y**2)
            sobel = np.clip(sobel, 0, 255).astype(np.uint8)
            
            # 创建结果图像
            result_image = self._create_result_image(sobel, has_alpha, alpha_channel)
            
            # 更新统计
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            
            return result_image
            
        except Exception as e:
            self._update_stats(False)
            logging.error(f"Sobel边缘检测失败: {e}")
            raise RuntimeError(f"Sobel边缘检测处理失败: {e}")
    
    def apply_canny_edge_detection(self, 
                                 image: Image.Image,
                                 low_threshold: Optional[int] = None,
                                 high_threshold: Optional[int] = None,
                                 aperture_size: Optional[int] = None,
                                 l2_gradient: Optional[bool] = None) -> Image.Image:
        """
        应用Canny边缘检测（优化版）
        
        Args:
            image: 输入PIL图像对象
            low_threshold: 低阈值，None使用配置值
            high_threshold: 高阈值，None使用配置值
            aperture_size: Sobel算子大小，None使用配置值
            l2_gradient: 是否使用L2梯度，None使用配置值
            
        Returns:
            处理后的PIL图像对象
            
        Raises:
            ValueError: 当输入图像无效或参数无效时
            RuntimeError: 处理失败时
        """
        import time
        start_time = time.time()
        
        try:
            # 使用统一的图像预处理
            gray, has_alpha, alpha_channel = self._prepare_image(image, preserve_color=False)
            
            # 使用配置参数
            low_threshold = low_threshold or self.edge_config.canny_low_threshold
            high_threshold = high_threshold or self.edge_config.canny_high_threshold
            aperture_size = aperture_size or self.edge_config.canny_aperture_size
            l2_gradient = l2_gradient if l2_gradient is not None else self.edge_config.canny_l2_gradient
            
            # 自适应阈值调整（基于图像统计）
            if low_threshold == 0 and high_threshold == 0:
                # 自动计算阈值
                median = np.median(gray)
                low_threshold = int(max(0, 0.66 * median))
                high_threshold = int(min(255, 1.33 * median))
            
            # 参数验证（在自适应调整后）
            if low_threshold >= high_threshold:
                raise ValueError("低阈值必须小于高阈值")
            if aperture_size not in [3, 5, 7]:
                raise ValueError("Sobel算子大小必须是3, 5, 7之一")
            
            # Canny边缘检测
            edges = cv2.Canny(gray, low_threshold, high_threshold, 
                            apertureSize=aperture_size, L2gradient=l2_gradient)
            
            # 创建结果图像
            result_image = self._create_result_image(edges, has_alpha, alpha_channel)
            
            # 更新统计
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            
            return result_image
            
        except Exception as e:
            self._update_stats(False)
            logging.error(f"Canny边缘检测失败: {e}")
            raise RuntimeError(f"Canny边缘检测处理失败: {e}")
    
    def equalize_histogram(self, 
                         image: Image.Image,
                         preserve_color: bool = False,
                         adaptive: bool = False,
                         clip_limit: float = 2.0,
                         tile_grid_size: Tuple[int, int] = (8, 8)) -> Image.Image:
        """
        直方图均衡化（增强版）
        
        Args:
            image: 输入PIL图像对象
            preserve_color: 是否保持彩色（对彩色图像进行LAB空间均衡化）
            adaptive: 是否使用自适应直方图均衡化(CLAHE)
            clip_limit: CLAHE的对比度限制
            tile_grid_size: CLAHE的网格大小
            
        Returns:
            处理后的PIL图像对象
            
        Raises:
            ValueError: 当输入图像无效时
            RuntimeError: 处理失败时
        """
        import time
        start_time = time.time()
        
        try:
            # 使用统一的图像预处理
            img_cv, has_alpha, alpha_channel = self._prepare_image(image, preserve_color=preserve_color)
            
            if preserve_color and len(img_cv.shape) == 3:
                # 彩色图像：在LAB空间进行均衡化
                lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
                l_channel = lab[:, :, 0]
                
                if adaptive:
                    # 自适应直方图均衡化
                    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
                    l_channel = clahe.apply(l_channel)
                else:
                    # 标准直方图均衡化
                    l_channel = cv2.equalizeHist(l_channel)
                
                lab[:, :, 0] = l_channel
                equalized = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
                is_color = True
            else:
                # 灰度图像
                gray = img_cv if len(img_cv.shape) == 2 else cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                
                if adaptive:
                    # 自适应直方图均衡化
                    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
                    equalized = clahe.apply(gray)
                else:
                    # 标准直方图均衡化
                    equalized = cv2.equalizeHist(gray)
                is_color = False
            
            # 创建结果图像
            result_image = self._create_result_image(equalized, has_alpha, alpha_channel, is_color)
            
            # 更新统计
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            
            return result_image
            
        except Exception as e:
            self._update_stats(False)
            logging.error(f"直方图均衡化失败: {e}")
            raise RuntimeError(f"直方图均衡化处理失败: {e}")
    
    def laplacian_sharpening(self, 
                           image: Image.Image,
                           ksize: Optional[int] = None,
                           scale: Optional[float] = None,
                           delta: Optional[float] = None,
                           weight: Optional[float] = None,
                           preserve_color: bool = False) -> Image.Image:
        """
        拉普拉斯算子锐化（增强版）
        
        Args:
            image: 输入PIL图像对象
            ksize: 拉普拉斯算子大小，None使用配置值
            scale: 缩放因子，None使用配置值
            delta: 偏移值，None使用配置值
            weight: 锐化权重，None使用配置值
            preserve_color: 是否保持彩色
            
        Returns:
            处理后的PIL图像对象
            
        Raises:
            ValueError: 当输入图像无效时
            RuntimeError: 处理失败时
        """
        import time
        start_time = time.time()
        
        try:
            # 使用统一的图像预处理
            img_cv, has_alpha, alpha_channel = self._prepare_image(image, preserve_color=preserve_color)
            
            # 使用配置参数
            ksize = ksize or self.sharpening_config.laplacian_ksize
            scale = scale or self.sharpening_config.laplacian_scale
            delta = delta or self.sharpening_config.laplacian_delta
            weight = weight or self.sharpening_config.sharpening_weight
            
            if preserve_color and len(img_cv.shape) == 3:
                # 彩色图像：分别处理每个通道
                sharpened = np.zeros_like(img_cv)
                for i in range(3):
                    channel = img_cv[:, :, i]
                    laplacian = cv2.Laplacian(channel, cv2.CV_64F, ksize=ksize, scale=scale, delta=delta)
                    sharpened_channel = channel.astype(np.float64) - weight * laplacian
                    sharpened[:, :, i] = np.clip(sharpened_channel, 0, 255).astype(np.uint8)
                is_color = True
            else:
                # 灰度图像
                gray = img_cv if len(img_cv.shape) == 2 else cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=ksize, scale=scale, delta=delta)
                sharpened = gray.astype(np.float64) - weight * laplacian
                sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
                is_color = False
            
            # 创建结果图像
            result_image = self._create_result_image(sharpened, has_alpha, alpha_channel, is_color)
            
            # 更新统计
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            
            return result_image
            
        except Exception as e:
            self._update_stats(False)
            logging.error(f"拉普拉斯锐化失败: {e}")
            raise RuntimeError(f"拉普拉斯锐化处理失败: {e}")
    
    def log_transformation(self, 
                         image: Image.Image,
                         c_value: Optional[float] = None,
                         preserve_color: bool = False) -> Image.Image:
        """
        对数变换（增强版）
        
        Args:
            image: 输入PIL图像对象
            c_value: 对数变换常数，None表示自动计算
            preserve_color: 是否保持彩色
            
        Returns:
            处理后的PIL图像对象
            
        Raises:
            ValueError: 当输入图像无效时
            RuntimeError: 处理失败时
        """
        import time
        start_time = time.time()
        
        try:
            # 使用统一的图像预处理
            img_cv, has_alpha, alpha_channel = self._prepare_image(image, preserve_color=preserve_color)
            
            if preserve_color and len(img_cv.shape) == 3:
                # 彩色图像：分别处理每个通道
                transformed = np.zeros_like(img_cv, dtype=np.uint8)
                for i in range(3):
                    channel = img_cv[:, :, i].astype(np.float32)
                    if c_value is None or self.transform_config.log_c_auto:
                        c = 255.0 / np.log(1 + np.max(channel)) if np.max(channel) > 0 else 1.0
                    else:
                        c = c_value
                    
                    log_channel = c * np.log(1 + channel)
                    transformed[:, :, i] = np.clip(log_channel, 0, 255).astype(np.uint8)
                is_color = True
            else:
                # 灰度图像
                gray = img_cv if len(img_cv.shape) == 2 else cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                gray_float = gray.astype(np.float32)
                
                if c_value is None or self.transform_config.log_c_auto:
                    c = 255.0 / np.log(1 + np.max(gray_float)) if np.max(gray_float) > 0 else 1.0
                else:
                    c = c_value
                
                transformed = c * np.log(1 + gray_float)
                transformed = np.clip(transformed, 0, 255).astype(np.uint8)
                is_color = False
            
            # 创建结果图像
            result_image = self._create_result_image(transformed, has_alpha, alpha_channel, is_color)
            
            # 更新统计
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            
            return result_image
            
        except Exception as e:
            self._update_stats(False)
            logging.error(f"对数变换失败: {e}")
            raise RuntimeError(f"对数变换处理失败: {e}")
    
    def gamma_correction(self, 
                       image: Image.Image,
                       gamma: Optional[float] = None,
                       preserve_color: bool = True) -> Image.Image:
        """
        伽马校正（增强版）
        
        Args:
            image: 输入PIL图像对象
            gamma: 伽马值，None使用配置默认值
            preserve_color: 是否保持彩色
            
        Returns:
            处理后的PIL图像对象
            
        Raises:
            ValueError: 当输入图像无效或伽马值无效时
            RuntimeError: 处理失败时
        """
        import time
        start_time = time.time()
        
        try:
            # 参数验证
            if gamma is None:
                gamma = self.transform_config.gamma_default
            
            if gamma <= 0:
                raise ValueError("伽马值必须大于0")
            
            # 放宽伽马值范围检查，只在极端情况下警告
            if gamma < 0.1 or gamma > 10.0:
                logging.warning(f"伽马值{gamma}可能过于极端，建议使用0.1-10.0范围内的值")
            
            # 使用统一的图像预处理
            img_cv, has_alpha, alpha_channel = self._prepare_image(image, preserve_color=preserve_color)
            
            if preserve_color and len(img_cv.shape) == 3:
                # 彩色图像：分别处理每个通道
                corrected = np.zeros_like(img_cv, dtype=np.uint8)
                for i in range(3):
                    channel = img_cv[:, :, i].astype(np.float32) / 255.0
                    gamma_channel = np.power(channel, gamma) * 255.0
                    corrected[:, :, i] = np.clip(gamma_channel, 0, 255).astype(np.uint8)
                is_color = True
            else:
                # 灰度图像
                gray = img_cv if len(img_cv.shape) == 2 else cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                gray_normalized = gray.astype(np.float32) / 255.0
                corrected = np.power(gray_normalized, gamma) * 255.0
                corrected = np.clip(corrected, 0, 255).astype(np.uint8)
                is_color = False
            
            # 创建结果图像
            result_image = self._create_result_image(corrected, has_alpha, alpha_channel, is_color)
            
            # 更新统计
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            
            return result_image
            
        except Exception as e:
            self._update_stats(False)
            logging.error(f"伽马校正失败: {e}")
            raise RuntimeError(f"伽马校正处理失败: {e}")
    
    def laplacian_sharpening_with_bilateral_filter(self, 
                                                 image: Image.Image,
                                                 sharpening_weight: Optional[float] = None,
                                                 d: Optional[int] = None,
                                                 sigma_color: Optional[float] = None,
                                                 sigma_space: Optional[float] = None,
                                                 preserve_color: bool = False) -> Image.Image:
        """
        带双边滤波的拉普拉斯锐化（增强版）
        
        Args:
            image: 输入PIL图像对象
            sharpening_weight: 锐化权重，None使用配置值
            d: 双边滤波邻域直径，None使用配置值
            sigma_color: 颜色空间滤波器的sigma值，None使用配置值
            sigma_space: 坐标空间滤波器的sigma值，None使用配置值
            preserve_color: 是否保持彩色
            
        Returns:
            处理后的PIL图像对象
            
        Raises:
            ValueError: 当输入图像无效时
            RuntimeError: 处理失败时
        """
        import time
        start_time = time.time()
        
        try:
            # 使用配置参数
            weight = sharpening_weight or (self.sharpening_config.sharpening_weight * 0.5)
            d = d or self.sharpening_config.bilateral_d
            sigma_color = sigma_color or self.sharpening_config.bilateral_sigma_color
            sigma_space = sigma_space or self.sharpening_config.bilateral_sigma_space
            
            # 先进行拉普拉斯锐化
            sharpened_image = self.laplacian_sharpening(
                image, weight=weight, preserve_color=preserve_color
            )
            
            # 使用统一的图像预处理
            img_cv, has_alpha, alpha_channel = self._prepare_image(sharpened_image, preserve_color=preserve_color)
            
            if preserve_color and len(img_cv.shape) == 3:
                # 彩色图像：应用双边滤波
                bilateral = cv2.bilateralFilter(img_cv, d, sigma_color, sigma_space)
                is_color = True
            else:
                # 灰度图像
                gray = img_cv if len(img_cv.shape) == 2 else cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                bilateral = cv2.bilateralFilter(gray, d, sigma_color, sigma_space)
                is_color = False
            
            # 创建结果图像
            result_image = self._create_result_image(bilateral, has_alpha, alpha_channel, is_color)
            
            # 更新统计
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            
            return result_image
            
        except Exception as e:
            self._update_stats(False)
            logging.error(f"双边滤波拉普拉斯锐化失败: {e}")
            raise RuntimeError(f"双边滤波拉普拉斯锐化处理失败: {e}")
    
    def batch_process(self, 
                     images: list,
                     operation: str,
                     **kwargs) -> list:
        """
        批量处理图像
        
        Args:
            images: PIL图像列表
            operation: 操作名称
            **kwargs: 操作参数
            
        Returns:
            处理后的图像列表
            
        Raises:
            ValueError: 操作名称无效时
        """
        if not hasattr(self, operation):
            raise ValueError(f"不支持的操作: {operation}")
        
        results = []
        operation_func = getattr(self, operation)
        
        for i, image in enumerate(images):
            try:
                result = operation_func(image, **kwargs)
                results.append(result)
                logging.info(f"批量处理进度: {i+1}/{len(images)}")
            except Exception as e:
                logging.error(f"批量处理第{i+1}张图像失败: {e}")
                results.append(None)
        
        return results
    
    def laplacian_sharpening_enhanced(self, 
                                   image: Image.Image, 
                                   weight: float = 1.0) -> Image.Image:
        """
        增强型拉普拉斯锐化处理
        
        Args:
            image: 输入的PIL图像对象
            weight: 锐化权重，默认为1.0
            
        Returns:
            处理后的PIL图像对象
            
        Raises:
            RuntimeError: 当图像处理失败时抛出
        """
        import time
        start_time = time.time()
        
        try:
            # 将PIL图像转换为OpenCV格式
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2BGRA)
            
            # 分离透明通道（如果存在）
            if img_cv.shape[2] == 4:  # 检查是否有Alpha通道
                bgr = img_cv[:, :, :3]
                alpha = img_cv[:, :, 3]
                has_alpha = True
            else:
                bgr = img_cv
                has_alpha = False
            
            # 转换为灰度图进行拉普拉斯处理
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            
            # 应用拉普拉斯算子
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            
            # 应用锐化权重
            sharpened = gray.astype(np.float64) - weight * laplacian
            sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
            
            # 合并回彩色图像
            if len(bgr.shape) == 3 and bgr.shape[2] >= 3:
                # 保持原始彩色信息，仅增强对比度
                # 将锐化后的灰度图转换为3通道
                sharpened_bgr = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
                # 按权重混合原始图像和锐化图像
                result_bgr = cv2.addWeighted(bgr, 1.0, sharpened_bgr, weight, 0)
            else:
                result_bgr = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
            
            # 如果原图有透明通道，则重新合并
            if has_alpha:
                result_img = np.dstack([result_bgr, alpha])
            else:
                result_img = result_bgr
            
            # 转换回PIL格式
            if result_img.shape[2] == 4:
                result_image = Image.fromarray(cv2.cvtColor(result_img, cv2.COLOR_BGRA2RGBA))
            else:
                result_image = Image.fromarray(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
            
            # 更新统计
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            
            return result_image
            
        except Exception as e:
            self._update_stats(False)
            logging.error(f"增强型拉普拉斯锐化处理失败: {e}")
            raise RuntimeError(f"增强型拉普拉斯锐化处理失败: {e}")
    
    def reset_stats(self):
        """重置处理统计"""
        self._processing_stats = {
            'total_processed': 0,
            'success_count': 0,
            'error_count': 0,
            'processing_times': []
        }