#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像几何变换模块

作者: RBQ
创建时间: 2025
描述: 提供图像几何变换功能，包括矫正、裁剪、调整大小、透视变换等
"""

import cv2
import numpy as np
from PIL import Image
import logging
from typing import Optional, List
from .base_utils import BaseUtils


class ImageGeometry:
    """图像几何变换处理类"""
    
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