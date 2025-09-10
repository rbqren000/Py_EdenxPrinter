#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像旋转工具类

提供图像旋转、翻转、镜像等功能，专为PC端Python环境设计。

Author: RBQ
Date: 2024
"""

from typing import Tuple, Optional
import math

try:
    from PIL import Image, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    # 创建一个简单的Image类替代品用于类型提示
    class Image:
        class Image:
            def __init__(self, mode=None, size=None, color=None):
                self.mode = mode
                self.size = size
                self.width = size[0] if size else 0
                self.height = size[1] if size else 0
            
            def rotate(self, angle, expand=False, fillcolor=None):
                return self
            
            def convert(self, mode):
                return self


class ImageRotate:
    """
    图像旋转和翻转工具类，提供基本的图像处理功能
    注意：需要安装PIL/Pillow库才能使用图像处理功能
    """
    
    @staticmethod
    def _check_pil_available():
        """检查PIL是否可用"""
        if not PIL_AVAILABLE:
            raise ImportError("PIL/Pillow库未安装或不可用，请安装: pip install Pillow")
    
    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """
        将角度转换为弧度
        
        Args:
            degrees: 角度值
            
        Returns:
            弧度值
        """
        return degrees * math.pi / 180.0
    
    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        """
        将弧度转换为角度
        
        Args:
            radians: 弧度值
            
        Returns:
            角度值
        """
        return radians * 180.0 / math.pi
    

    
    @staticmethod
    def vertical_flip(image: Image.Image) -> Image.Image:
        """垂直翻转
        
        Args:
            image: PIL图像对象
            
        Returns:
            垂直翻转后的图像
        """
        ImageRotate._check_pil_available()
        return ImageOps.flip(image)
    
    @staticmethod
    def horizontal_flip(image: Image.Image) -> Image.Image:
        """水平翻转
        
        Args:
            image: PIL图像对象
            
        Returns:
            水平翻转后的图像
        """
        ImageRotate._check_pil_available()
        return ImageOps.mirror(image)
    
    @staticmethod
    def create_horizontal_mirrored_image(image: Image.Image) -> Image.Image:
        """创建左右镜像
        
        Args:
            image: 原始图像
            
        Returns:
            左右镜像图像
        """
        ImageRotate._check_pil_available()
        return ImageOps.mirror(image)
    
    @staticmethod
    def create_vertical_mirrored_image(image: Image.Image) -> Image.Image:
        """创建上下镜像
        
        Args:
            image: 原始图像
            
        Returns:
            上下镜像图像
        """
        ImageRotate._check_pil_available()
        return ImageOps.flip(image)
    
    @staticmethod
    def create_horizontal_and_vertical_mirrored_image(image: Image.Image) -> Image.Image:
        """创建左右上下镜像
        
        Args:
            image: 原始图像
            
        Returns:
            左右上下镜像图像
        """
        ImageRotate._check_pil_available()
        return ImageOps.flip(ImageOps.mirror(image))
    
    @staticmethod
    def rotate_by_degrees(image: Image.Image, degrees: float, expand: bool = True) -> Image.Image:
        """按角度旋转图片
        
        Args:
            image: PIL图像对象
            degrees: 旋转角度（度）
            expand: 是否扩展画布以容纳旋转后的图像
            
        Returns:
            旋转后的图像
        """
        ImageRotate._check_pil_available()
        return image.rotate(-degrees, expand=expand, fillcolor=(255, 255, 255, 0))
    
    @staticmethod
    def rotate_by_radians(image: Image.Image, radians: float, expand: bool = True) -> Image.Image:
        """按弧度旋转图片
        
        Args:
            image: PIL图像对象
            radians: 旋转弧度
            expand: 是否扩展画布以容纳旋转后的图像
            
        Returns:
            旋转后的图像
        """
        ImageRotate._check_pil_available()
        degrees = ImageRotate.radians_to_degrees(radians)
        return ImageRotate.rotate_by_degrees(image, degrees, expand)
    
    @staticmethod
    def get_rotated_size(width: int, height: int, radians: float) -> Tuple[int, int]:
        """计算旋转后的图像尺寸
        
        Args:
            width: 原始宽度
            height: 原始高度
            radians: 旋转弧度
            
        Returns:
            旋转后的(宽度, 高度)
        """
        cos_val = abs(math.cos(radians))
        sin_val = abs(math.sin(radians))
        
        new_width = int(width * cos_val + height * sin_val)
        new_height = int(width * sin_val + height * cos_val)
        
        return new_width, new_height
    
    @staticmethod
    def rotate_with_background(image: Image.Image, degrees: float, 
                             background_color: Tuple[int, int, int, int] = (255, 255, 255, 255)) -> Image.Image:
        """带背景色的旋转
        
        Args:
            image: PIL图像对象
            degrees: 旋转角度
            background_color: 背景色 (R, G, B, A)
            
        Returns:
            旋转后的图像
        """
        ImageRotate._check_pil_available()
        
        # 确保图像有alpha通道
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 计算旋转后的尺寸
        radians = ImageRotate.degrees_to_radians(degrees)
        new_width, new_height = ImageRotate.get_rotated_size(image.width, image.height, radians)
        
        # 创建新的背景图像
        rotated_image = Image.new('RGBA', (new_width, new_height), background_color)
        
        # 旋转原图像
        rotated_original = image.rotate(-degrees, expand=True, fillcolor=(0, 0, 0, 0))
        
        # 计算粘贴位置（居中）
        paste_x = (new_width - rotated_original.width) // 2
        paste_y = (new_height - rotated_original.height) // 2
        
        # 粘贴到背景上
        rotated_image.paste(rotated_original, (paste_x, paste_y), rotated_original)
        
        return rotated_image
    
    @staticmethod
    def normalize_angle(angle: float) -> float:
        """标准化角度到0-360度范围
        
        Args:
            angle: 输入角度
            
        Returns:
            标准化后的角度
        """
        while angle < 0:
            angle += 360
        while angle >= 360:
            angle -= 360
        return angle