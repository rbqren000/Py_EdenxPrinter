#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RowImage - 行图像数据类

对应Objective-C中的RowImage类，用于表示单行图像数据。
包含图像路径和用于抖动算法的边界距离信息。

作者: RBQ
日期: 2025
"""

from typing import Optional


class RowImage:
    """
    行图像数据类
    
    用于表示单行图像的基本信息，包括图像路径和边界距离。
    边界距离用于抖动算法时消除不同行拼接时的缝隙。
    
    Attributes:
        image_path (str): 行图的路径
        top_beyond_distance (int): 顶部保留的超出距离
        bottom_beyond_distance (int): 底部保留的超出距离
    """
    
    def __init__(self, image_path: Optional[str] = None, top_beyond_distance: int = 0, bottom_beyond_distance: int = 0):
        """
        初始化行图像对象
        
        Args:
            image_path (Optional[str], optional): 图像文件路径，默认为None
            top_beyond_distance (int, optional): 顶部超出距离，默认为0
            bottom_beyond_distance (int, optional): 底部超出距离，默认为0
        """
        self._image_path = image_path
        self._top_beyond_distance = top_beyond_distance
        self._bottom_beyond_distance = bottom_beyond_distance
    
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
    
    @property
    def top_beyond_distance(self) -> int:
        """
        获取顶部保留的超出距离
        
        Returns:
            int: 顶部保留的超出距离
        """
        return self._top_beyond_distance
    
    @top_beyond_distance.setter
    def top_beyond_distance(self, value: int) -> None:
        """
        设置顶部保留的超出距离
        
        Args:
            value (int): 新的顶部超出距离
        """
        self._top_beyond_distance = value
    
    @property
    def bottom_beyond_distance(self) -> int:
        """
        获取底部保留的超出距离
        
        Returns:
            int: 底部保留的超出距离
        """
        return self._bottom_beyond_distance
    
    @bottom_beyond_distance.setter
    def bottom_beyond_distance(self, value: int) -> None:
        """
        设置底部保留的超出距离
        
        Args:
            value (int): 新的底部超出距离
        """
        self._bottom_beyond_distance = value
    
    def __str__(self) -> str:
        """
        返回对象的字符串表示
        
        Returns:
            str: 对象的字符串描述
        """
        return (f"RowImage(image_path='{self.image_path}', "
                f"top_beyond_distance={self.top_beyond_distance}, "
                f"bottom_beyond_distance={self.bottom_beyond_distance})")
    
    def __repr__(self) -> str:
        """
        返回对象的详细字符串表示
        
        Returns:
            str: 对象的详细字符串描述
        """
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        """
        比较两个RowImage对象是否相等
        
        Args:
            other: 要比较的对象
            
        Returns:
            bool: 如果相等返回True，否则返回False
        """
        if not isinstance(other, RowImage):
            return False
        
        return (self.image_path == other.image_path and
                self.top_beyond_distance == other.top_beyond_distance and
                self.bottom_beyond_distance == other.bottom_beyond_distance)