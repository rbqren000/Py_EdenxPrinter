#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像扫描模块

Created by RBQ on 2025/9/8
描述: 简化的图像扫描功能，专注核心功能，去除过度设计
"""

import cv2
import numpy as np
from PIL import Image
import logging
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass
from .base_utils import BaseUtils


@dataclass
class ScanResult:
    """扫描结果"""
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float                # 置信度 0-1
    image: Optional[Image.Image] = None  # 提取的区域图像


class ImageScannerError(Exception):
    """图像扫描异常"""
    pass


class ImageScanner:
    """
    图像扫描处理类
    
    专注核心功能：
    1. 身份证号码区域检测
    2. 通用文档检测
    3. 二维码检测
    """
    
    def __init__(self):
        """初始化图像扫描器"""
        self.logger = logging.getLogger(__name__)
        
        # 初始化QR码检测器
        self._qr_detector = None
        try:
            self._qr_detector = cv2.QRCodeDetector()
        except AttributeError:
            self.logger.warning("OpenCV版本不支持QRCodeDetector")
    
    def _prepare_image(self, image: Image.Image) -> Tuple[np.ndarray, np.ndarray]:
        """
        图像预处理
        
        Args:
            image: 输入PIL图像
            
        Returns:
            Tuple[OpenCV图像, 灰度图像]
        """
        if image is None or image.size[0] <= 0 or image.size[1] <= 0:
            raise ImageScannerError("输入图像无效")
        
        try:
            img_cv = BaseUtils.convert_pil_to_opencv(image)
            gray = BaseUtils.prepare_grayscale(img_cv, normalize=False)
            return img_cv, gray
        except Exception as e:
            raise ImageScannerError(f"图像预处理失败: {e}")
    
    def scan_id_card_number(self, image: Image.Image) -> Optional[ScanResult]:
        """
        扫描身份证号码区域
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            扫描结果或None
        """
        try:
            img_cv, gray = self._prepare_image(image)
            h, w = gray.shape
            
            # 预处理：高斯模糊 + 自适应阈值
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 形态学操作：连接断开的文字
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # 查找轮廓
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 筛选候选区域
            candidates = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 500:  # 过滤小区域
                    continue
                
                x, y, width, height = cv2.boundingRect(contour)
                
                # 基本筛选条件
                aspect_ratio = width / height if height > 0 else 0
                area_ratio = area / (w * h)
                
                # 身份证号码区域特征：
                # 1. 长宽比在3-15之间
                # 2. 面积占比0.5%-10%
                # 3. 位置在图像下半部分
                if (3.0 <= aspect_ratio <= 15.0 and 
                    0.005 <= area_ratio <= 0.1 and
                    y > h * 0.4):  # 下60%区域
                    
                    confidence = self._calculate_confidence(
                        aspect_ratio, area_ratio, y / h
                    )
                    
                    if confidence > 0.3:
                        candidates.append((x, y, width, height, confidence))
            
            if not candidates:
                return None
            
            # 选择置信度最高的候选
            candidates.sort(key=lambda x: x[4], reverse=True)
            x, y, width, height, confidence = candidates[0]
            
            # 提取区域图像
            region_img = img_cv[y:y+height, x:x+width]
            if len(region_img.shape) == 3:
                region_gray = cv2.cvtColor(region_img, cv2.COLOR_BGR2GRAY)
            else:
                region_gray = region_img
            
            # 二值化处理
            region_binary = cv2.adaptiveThreshold(
                region_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            region_pil = Image.fromarray(region_binary)
            
            return ScanResult(
                bbox=(x, y, width, height),
                confidence=confidence,
                image=region_pil
            )
            
        except Exception as e:
            self.logger.error(f"身份证扫描失败: {e}")
            raise ImageScannerError(f"身份证扫描失败: {e}")
    
    def _calculate_confidence(self, aspect_ratio: float, 
                            area_ratio: float, 
                            position_ratio: float) -> float:
        """
        计算置信度
        
        Args:
            aspect_ratio: 宽高比
            area_ratio: 面积比
            position_ratio: 位置比例
            
        Returns:
            置信度 (0-1)
        """
        confidence = 0.0
        
        # 宽高比评分 (理想值6.0)
        ratio_score = max(0, 0.4 - abs(aspect_ratio - 6.0) * 0.05)
        confidence += ratio_score
        
        # 面积评分 (理想值2%)
        area_score = max(0, 0.3 - abs(area_ratio - 0.02) * 10)
        confidence += area_score
        
        # 位置评分 (偏好下半部分)
        if position_ratio > 0.7:
            position_score = 0.3
        elif position_ratio > 0.5:
            position_score = 0.2
        else:
            position_score = 0.1
        confidence += position_score
        
        return min(1.0, confidence)
    
    def scan_document(self, image: Image.Image) -> List[ScanResult]:
        """
        通用文档扫描
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            检测到的文档区域列表
        """
        try:
            img_cv, gray = self._prepare_image(image)
            
            # Canny边缘检测
            edges = cv2.Canny(gray, 50, 150)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            results = []
            image_area = gray.shape[0] * gray.shape[1]
            
            for contour in contours:
                area = cv2.contourArea(contour)
                area_ratio = area / image_area
                
                # 文档区域筛选：面积占比10%-90%
                if 0.1 <= area_ratio <= 0.9:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # 合理的宽高比
                    if 0.5 <= aspect_ratio <= 3.0:
                        confidence = area_ratio * 0.5 + 0.3
                        
                        result = ScanResult(
                            bbox=(x, y, w, h),
                            confidence=min(1.0, confidence)
                        )
                        results.append(result)
            
            # 按置信度排序
            results.sort(key=lambda x: x.confidence, reverse=True)
            return results
            
        except Exception as e:
            self.logger.error(f"文档扫描失败: {e}")
            raise ImageScannerError(f"文档扫描失败: {e}")
    
    def detect_qr_codes(self, image: Image.Image) -> List[ScanResult]:
        """
        二维码检测
        
        Args:
            image: 输入PIL图像对象
            
        Returns:
            检测到的二维码区域列表
        """
        try:
            img_cv, gray = self._prepare_image(image)
            results = []
            
            # 使用内置检测器
            if self._qr_detector is not None:
                try:
                    retval, decoded_info, points, _ = self._qr_detector.detectAndDecodeMulti(gray)
                    
                    if retval and points is not None:
                        for point_set in points:
                            if point_set is not None and len(point_set) >= 4:
                                # 计算边界框
                                x_coords = point_set[:, 0]
                                y_coords = point_set[:, 1]
                                x, y = int(np.min(x_coords)), int(np.min(y_coords))
                                w = int(np.max(x_coords) - x)
                                h = int(np.max(y_coords) - y)
                                
                                result = ScanResult(
                                    bbox=(x, y, w, h),
                                    confidence=0.9
                                )
                                results.append(result)
                except Exception:
                    pass
            
            # 备用轮廓检测
            if not results:
                edges = cv2.Canny(gray, 50, 150)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 100 <= area <= 10000:
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = w / h if h > 0 else 0
                        
                        # 接近正方形
                        if abs(aspect_ratio - 1.0) <= 0.2:
                            result = ScanResult(
                                bbox=(x, y, w, h),
                                confidence=0.6
                            )
                            results.append(result)
            
            results.sort(key=lambda x: x.confidence, reverse=True)
            return results
            
        except Exception as e:
            self.logger.error(f"二维码检测失败: {e}")
            raise ImageScannerError(f"二维码检测失败: {e}")
    
    # 向后兼容方法
    def opencv_scan_card(self, image: Image.Image) -> Optional[Image.Image]:
        """向后兼容的身份证扫描方法"""
        try:
            result = self.scan_id_card_number(image)
            return result.image if result else None
        except Exception:
            return None