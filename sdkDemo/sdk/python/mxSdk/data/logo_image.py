#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LogoImage - Logo图像数据类

对应Objective-C中的LogoImage类，用于表示Logo图像数据。
包含图像路径信息。

作者: RBQ
日期: 2025
"""

from typing import Optional


class LogoImage:
    """
    Logo图像数据类
    
    用于表示Logo图像的基本信息，包括图像路径。
    这是一个简单的数据容器类，主要用于存储Logo图像的路径信息。
    
    Attributes:
        image_path (str): Logo图像的路径
    """
    
    def __init__(self, image_path: Optional[str] = None):
        """
        初始化Logo图像对象
        
        Args:
            image_path (Optional[str], optional): 图像文件路径，默认为None
        """
        self._image_path = image_path
    
    @property
    def image_path(self) -> Optional[str]:
        """
        获取图像文件路径
        
        Returns:
            Optional[str]: 图像文件路径
        """
        return self._image_path
    
    @image_path.setter
    def image_path(self, value: Optional[str]) -> None:
        """
        设置图像文件路径
        
        Args:
            value (Optional[str]): 新的图像文件路径
        """
        self._image_path = value
    
    def __str__(self) -> str:
        """
        返回对象的字符串表示
        
        Returns:
            str: 对象的字符串描述
        """
        return f"LogoImage(image_path='{self.image_path}')"
    
    def __repr__(self) -> str:
        """
        返回对象的详细字符串表示
        
        Returns:
            str: 对象的详细字符串描述
        """
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        """
        比较两个LogoImage对象是否相等
        
        Args:
            other: 要比较的对象
            
        Returns:
            bool: 如果相等返回True，否则返回False
        """
        if not isinstance(other, LogoImage):
            return False
        
        return self.image_path == other.image_path
    
    def __hash__(self) -> int:
        """
        返回对象的哈希值
        
        Returns:
            int: 对象的哈希值
        """
        return hash(self.image_path)