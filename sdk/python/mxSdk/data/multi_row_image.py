#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiRowImage - 多行图像数据类

对应Objective-C中的MultiRowImage类，用于管理多行图像数据。
包含行图像列表、缩略图路径、排布方向和裁切标志等属性。

作者: RBQ
日期: 2025
"""

from typing import List, Optional
from .row_image import RowImage
from ..enums.row_layout_direction import RowLayoutDirection


class MultiRowImage:
    """
    多行图像数据类
    
    用于管理多行图像数据，包括行图像列表、缩略图路径、排布方向等信息。
    支持连续图片裁切的特殊处理以减少抖动算法引起的缝隙问题。
    
    Attributes:
        row_images (List[RowImage]): 行图像列表
        thumb_path (Optional[str]): 缩略图路径
        row_layout_direction (RowLayoutDirection): 切图排布方向
        is_contiguous_cropped_images (bool): 图片是否为一张图片裁切而来
    """
    
    def __init__(self, 
                 row_images: Optional[List[RowImage]] = None,
                 thumb_path: Optional[str] = None,
                 row_layout_direction: RowLayoutDirection = RowLayoutDirection.VERTICAL,
                 is_contiguous_cropped_images: bool = False):
        """
        初始化多行图像对象
        
        Args:
            row_images (Optional[List[RowImage]], optional): 行图像列表，默认为None
            thumb_path (Optional[str], optional): 缩略图路径，默认为None
            row_layout_direction (RowLayoutDirection, optional): 切图排布方向，默认为垂直方向
            is_contiguous_cropped_images (bool, optional): 图片是否为一张图片裁切而来，默认为False
            
        Note:
            如果is_contiguous_cropped_images为True，表示rowImages中的图片是连续一张图裁切而来，
            会进行裁切图衔接位置处理，以尽可能减少计算过程中抖动算法引起的缝隙问题。
        """
        self._row_images = row_images if row_images is not None else []
        self._thumb_path = thumb_path
        self._row_layout_direction = row_layout_direction
        self._is_contiguous_cropped_images = is_contiguous_cropped_images
    
    @property
    def row_images(self) -> List[RowImage]:
        """
        获取行图像列表
        
        Returns:
            List[RowImage]: 行图像列表
        """
        return self._row_images
    
    @row_images.setter
    def row_images(self, value: List[RowImage]) -> None:
        """
        设置行图像列表
        
        Args:
            value (List[RowImage]): 新的行图像列表
        """
        self._row_images = value if value is not None else []
    
    @property
    def thumb_path(self) -> Optional[str]:
        """
        获取缩略图路径
        
        Returns:
            Optional[str]: 缩略图路径
        """
        return self._thumb_path
    
    @thumb_path.setter
    def thumb_path(self, value: Optional[str]) -> None:
        """
        设置缩略图路径
        
        Args:
            value (Optional[str]): 新的缩略图路径
        """
        self._thumb_path = value
    
    @property
    def row_layout_direction(self) -> RowLayoutDirection:
        """
        获取切图排布方向
        
        Returns:
            RowLayoutDirection: 切图排布方向
        """
        return self._row_layout_direction
    
    @row_layout_direction.setter
    def row_layout_direction(self, value: RowLayoutDirection) -> None:
        """
        设置切图排布方向
        
        Args:
            value (RowLayoutDirection): 新的切图排布方向
        """
        self._row_layout_direction = value
    
    @property
    def is_contiguous_cropped_images(self) -> bool:
        """
        获取图片是否为一张图片裁切而来的标志
        
        Returns:
            bool: 图片是否为一张图片裁切而来
        """
        return self._is_contiguous_cropped_images

    @is_contiguous_cropped_images.setter
    def is_contiguous_cropped_images(self, value: bool) -> None:
        """
        设置图片是否为一张图片裁切而来的标志
        
        Args:
            value (bool): 新的裁切标志
        """
        self._is_contiguous_cropped_images = value

    def add_row_image(self, row_image: RowImage) -> None:
        """
        添加行图像
        
        Args:
            row_image (RowImage): 要添加的行图像
        """
        self._row_images.append(row_image)
    
    def remove_row_image(self, index: int) -> bool:
        """
        移除指定索引的行图像
        
        Args:
            index (int): 要移除的行图像索引
            
        Returns:
            bool: 移除成功返回True，索引无效返回False
        """
        if 0 <= index < len(self._row_images):
            del self._row_images[index]
            return True
        return False
    
    def get_row_image(self, index: int) -> Optional[RowImage]:
        """
        获取指定索引的行图像
        
        Args:
            index (int): 行图像索引
            
        Returns:
            Optional[RowImage]: 行图像对象，如果索引无效返回None
        """
        if 0 <= index < len(self._row_images):
            return self._row_images[index]
        return None
    
    def get_row_count(self) -> int:
        """
        获取行图像数量
        
        Returns:
            int: 行图像数量
        """
        return len(self._row_images)
    
    def clear_row_images(self) -> None:
        """
        清空所有行图像
        """
        self._row_images.clear()
    
    def __str__(self) -> str:
        """
        返回对象的字符串表示
        
        Returns:
            str: 对象的字符串描述
        """
        return (f"MultiRowImage(row_count={len(self._row_images)}, "
                f"thumb_path='{self.thumb_path}', "
                f"row_layout_direction={self.row_layout_direction.name}, "
                f"is_contiguous_cropped_images={self.is_contiguous_cropped_images})")

    def __repr__(self) -> str:
        """
        返回对象的详细字符串表示
        
        Returns:
            str: 对象的详细字符串描述
        """
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        """
        比较两个MultiRowImage对象是否相等
        
        Args:
            other: 要比较的对象
            
        Returns:
            bool: 如果相等返回True，否则返回False
        """
        if not isinstance(other, MultiRowImage):
            return False
        
        return (self.row_images == other.row_images and
                self.thumb_path == other.thumb_path and
                self.row_layout_direction == other.row_layout_direction and
                self.is_contiguous_cropped_images == other.is_contiguous_cropped_images)

    def __len__(self) -> int:
        """
        返回行图像数量
        
        Returns:
            int: 行图像数量
        """
        return len(self._row_images)
    
    def __getitem__(self, index: int) -> RowImage:
        """
        通过索引获取行图像
        
        Args:
            index (int): 行图像索引
            
        Returns:
            RowImage: 行图像对象
            
        Raises:
            IndexError: 当索引超出范围时抛出异常
        """
        return self._row_images[index]
    
    def __setitem__(self, index: int, value: RowImage) -> None:
        """
        通过索引设置行图像
        
        Args:
            index (int): 行图像索引
            value (RowImage): 新的行图像对象
            
        Raises:
            IndexError: 当索引超出范围时抛出异常
        """
        self._row_images[index] = value
    
    def __iter__(self):
        """
        返回行图像列表的迭代器
        
        Returns:
            Iterator: 行图像列表的迭代器
        """
        return iter(self._row_images)