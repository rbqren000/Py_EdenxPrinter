#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像处理模块

作者: RBQ
版本: 1.0.0
Python版本: 3.9+
"""

import os
from PIL import Image
from PyQt5.QtCore import QObject, pyqtSignal


class ImageProcessor(QObject):
    """图像处理器类
    
    负责处理图像相关的操作，包括获取图像信息、图像处理等功能。
    """
    
    # 定义信号
    processing_error = pyqtSignal(str)
    processing_success = pyqtSignal(dict)

    def __init__(self):
        """初始化图像处理器"""
        super().__init__()

    def get_image_info(self, file_path):
        """获取图片信息
        
        Args:
            file_path (str): 图片文件路径
            
        Returns:
            dict: 图片信息字典，包含文件路径、大小、尺寸、格式等信息
            None: 获取失败时返回None
        """
        try:
            if not file_path:
                raise ValueError("文件路径不能为空")
                
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"图片文件不存在: {file_path}")

            file_size = os.path.getsize(file_path)
            
            with Image.open(file_path) as img:
                info = {
                    "file_path": file_path,
                    "file_size": f"{file_size / 1024:.2f} KB",
                    "dimensions": f"{img.size[0]} x {img.size[1]}",
                    "format": img.format or "Unknown",
                    "mode": img.mode
                }
                self.processing_success.emit(info)
                return info
                
        except FileNotFoundError as e:
            error_msg = str(e)
            self.processing_error.emit(error_msg)
            return None
        except Exception as e:
            error_msg = f"获取图片信息失败: {str(e)}"
            self.processing_error.emit(error_msg)
            return None

    def process_image(self, image_path, operation=None, **kwargs):
        """处理图片
        
        Args:
            image_path (str): 图片文件路径
            operation (str, optional): 处理操作类型（如 'grayscale', 'rotate' 等）
            **kwargs: 其他处理参数
                auto_resize (bool): 是否自动调整大小
                max_width (int): 最大宽度
                max_height (int): 最大高度
                quality (int): 图像质量
                mode (str): 处理模式（'黑白', '灰度', '彩色'）
                dithering (str): 抖动算法
            
        Returns:
            PIL.Image: 处理后的图像对象
            None: 处理失败时返回None
        """
        try:
            if not image_path or not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
                
            with Image.open(image_path) as img:
                # 复制图像以避免修改原始文件
                processed_img = img.copy()
                
                # 如果有kwargs参数，使用新的处理逻辑
                if kwargs:
                    return self._process_image_advanced(processed_img, **kwargs)
                
                # 兼容旧的operation参数
                if operation == "grayscale":
                    return processed_img.convert('L')
                elif operation == "rotate":
                    return processed_img.rotate(90)
                elif operation == "resize":
                    # 示例：调整为固定尺寸
                    return processed_img.resize((800, 600))
                else:
                    # 默认返回原图
                    return processed_img
                    
        except Exception as e:
            error_msg = f"图片处理失败: {str(e)}"
            self.processing_error.emit(error_msg)
            return None
    
    def _process_image_advanced(self, img, auto_resize=True, max_width=384, max_height=384, 
                               quality=85, mode='黑白', dithering='Floyd-Steinberg', **kwargs):
        """高级图像处理
        
        Args:
            img (PIL.Image): 输入图像
            auto_resize (bool): 是否自动调整大小
            max_width (int): 最大宽度
            max_height (int): 最大高度
            quality (int): 图像质量
            mode (str): 处理模式
            dithering (str): 抖动算法
            
        Returns:
            PIL.Image: 处理后的图像
        """
        try:
            # 自动调整大小
            if auto_resize:
                img = self._resize_image(img, max_width, max_height)
            
            # 根据模式处理图像
            if mode == '黑白':
                img = self._convert_to_bw(img, dithering)
            elif mode == '灰度':
                img = img.convert('L')
            elif mode == '彩色':
                img = img.convert('RGB')
            
            return img
            
        except Exception as e:
            raise Exception(f"高级图像处理失败: {str(e)}")
    
    def _resize_image(self, img, max_width, max_height):
        """调整图像大小"""
        width, height = img.size
        
        # 计算缩放比例
        scale_w = max_width / width
        scale_h = max_height / height
        scale = min(scale_w, scale_h, 1.0)  # 不放大图像
        
        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img
    
    def _convert_to_bw(self, img, dithering='Floyd-Steinberg'):
        """转换为黑白图像"""
        # 先转换为灰度
        if img.mode != 'L':
            img = img.convert('L')
        
        # 应用抖动算法
        if dithering == 'Floyd-Steinberg':
            img = img.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
        elif dithering == 'None':
            img = img.convert('1', dither=Image.Dither.NONE)
        else:
            img = img.convert('1')
        
        return img

    def validate_image_file(self, file_path):
        """验证图像文件是否有效
        
        Args:
            file_path (str): 图片文件路径
            
        Returns:
            bool: 文件有效返回True，否则返回False
        """
        try:
            if not file_path or not os.path.exists(file_path):
                return False
                
            with Image.open(file_path) as img:
                # 尝试验证图像
                img.verify()
                return True
                
        except Exception:
            return False