#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiRowData - 多行数据类

对应Objective-C中的MultiRowData类，用于管理多行数据。
包含行数据列表、图像路径、缩略图路径、压缩标志和排布方向等属性。

作者: RBQ
日期: 2025
"""

from typing import List, Optional
from .row_data import RowData
from ..enums.row_layout_direction import RowLayoutDirection


class MultiRowData:
    """
    多行数据类
    
    用于管理多行数据，包括行数据列表、预览图地址、缩略图路径等信息。
    提供数据统计和访问功能。
    
    Attributes:
        row_data_arr (List[RowData]): 行数据列表
        image_paths (Optional[List[str]]): 预览图的地址列表，每一行包含一个预览图
        thumb_path (str): 缩略图路径
        compress (bool): 是否压缩数据，默认为压缩数据
        row_layout_direction (RowLayoutDirection): 切图排布方向
    """
    
    def __init__(self,
                 row_data_arr: Optional[List[RowData]] = None,
                 image_paths: Optional[List[str]] = None,
                 thumb_path: Optional[str] = None,
                 compress: bool = True,
                 row_layout_direction: RowLayoutDirection = RowLayoutDirection.VERTICAL):
        """
        初始化多行数据对象
        
        Args:
            row_data_arr (Optional[List[RowData]], optional): 行数据列表，默认为None
            image_paths (Optional[List[str]], optional): 预览图的地址列表，默认为None
            thumb_path (Optional[str], optional): 缩略图路径，默认为None
            compress (bool, optional): 是否压缩数据，默认为True
            row_layout_direction (RowLayoutDirection, optional): 切图排布方向，默认为垂直方向
        """
        self._row_data_arr = row_data_arr if row_data_arr is not None else []
        self._image_paths = image_paths
        self._thumb_path = thumb_path if thumb_path is not None else ""
        self._compress = compress
        self._row_layout_direction = row_layout_direction
    
    @property
    def row_data_arr(self) -> List[RowData]:
        """
        获取行数据列表
        
        Returns:
            List[RowData]: 行数据列表
        """
        return self._row_data_arr
    
    @row_data_arr.setter
    def row_data_arr(self, value: List[RowData]) -> None:
        """
        设置行数据列表
        
        Args:
            value (List[RowData]): 新的行数据列表
        """
        self._row_data_arr = value if value is not None else []
    
    @property
    def row_data_list(self) -> List[RowData]:
        """
        获取行数据列表（row_data_arr的别名，用于向后兼容）
        
        Returns:
            List[RowData]: 行数据列表
        """
        return self._row_data_arr
    
    @row_data_list.setter
    def row_data_list(self, value: List[RowData]) -> None:
        """
        设置行数据列表（row_data_arr的别名，用于向后兼容）
        
        Args:
            value (List[RowData]): 新的行数据列表
        """
        self._row_data_arr = value if value is not None else []
    
    @property
    def image_paths(self) -> Optional[List[str]]:
        """
        获取预览图的地址列表
        
        Returns:
            Optional[List[str]]: 预览图的地址列表
        """
        return self._image_paths
    
    @image_paths.setter
    def image_paths(self, value: Optional[List[str]]) -> None:
        """
        设置预览图的地址列表
        
        Args:
            value (Optional[List[str]]): 新的预览图地址列表
        """
        self._image_paths = value
    
    @property
    def thumb_path(self) -> str:
        """
        获取缩略图路径
        
        Returns:
            str: 缩略图路径
        """
        return self._thumb_path
    
    @thumb_path.setter
    def thumb_path(self, value: str) -> None:
        """
        设置缩略图路径
        
        Args:
            value (str): 新的缩略图路径
        """
        self._thumb_path = value if value is not None else ""
    
    @property
    def compress(self) -> bool:
        """
        获取压缩标志
        
        Returns:
            bool: 是否压缩数据
        """
        return self._compress
    
    @compress.setter
    def compress(self, value: bool) -> None:
        """
        设置压缩标志
        
        Args:
            value (bool): 新的压缩标志
        """
        self._compress = value
    
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
    
    def total_data_length(self) -> int:
        """
        计算总数据长度
        
        Returns:
            int: 所有行数据的总长度
        """
        total_length = 0
        if not self._row_data_arr:
            return total_length
        
        for row_data in self._row_data_arr:
            total_length += row_data.data_length
        
        return total_length
    
    def total_packet_count(self, useful_data_len: int) -> int:
        """
        计算总数据包数量
        
        Args:
            useful_data_len (int): 每个数据包中有用数据的长度
            
        Returns:
            int: 总数据包数量
            
        Raises:
            ValueError: 当useful_data_len小于等于0时抛出异常
        """
        if useful_data_len <= 0:
            raise ValueError("useful_data_len must be greater than 0")
        
        total_packet_count = 0
        if not self._row_data_arr:
            return total_packet_count
        
        for row_data in self._row_data_arr:
            total_packet_count += row_data.total_packet_count(useful_data_len)
        
        return total_packet_count
    
    def has_data(self) -> bool:
        """
        检查是否有数据
        
        Returns:
            bool: 如果总数据长度大于0返回True，否则返回False
        """
        return self.total_data_length() > 0
    
    def total_row_count(self) -> int:
        """
        获取总行数
        
        Returns:
            int: 行数据的总数量
        """
        if not self._row_data_arr:
            return 0
        return len(self._row_data_arr)
    
    def row_data_with_row_index(self, row_index: int) -> Optional[RowData]:
        """
        根据行索引获取行数据
        
        Args:
            row_index (int): 行索引
            
        Returns:
            Optional[RowData]: 行数据对象，如果索引无效返回None
        """
        if not self._row_data_arr:
            return None
        
        try:
            return self._row_data_arr[row_index]
        except IndexError:
            return None
    
    def compress_value(self) -> int:
        """
        获取压缩值
        
        Returns:
            int: 压缩时返回1，不压缩时返回0
        """
        return 1 if self._compress else 0
    
    def add_row_data(self, row_data: RowData) -> None:
        """
        添加行数据
        
        Args:
            row_data (RowData): 要添加的行数据
        """
        if row_data is not None:
            self._row_data_arr.append(row_data)
    
    def remove_row_data(self, row_data: RowData) -> bool:
        """
        移除指定的行数据
        
        Args:
            row_data (RowData): 要移除的行数据对象
            
        Returns:
            bool: 移除成功返回True，未找到返回False
        """
        if row_data is None:
            return False
        try:
            self._row_data_arr.remove(row_data)
            return True
        except ValueError:
            return False
    
    def clear_row_data(self) -> None:
        """
        清空所有行数据
        """
        self._row_data_arr.clear()
    
    def __str__(self) -> str:
        """
        返回对象的字符串表示
        
        Returns:
            str: 对象的字符串描述
        """
        return (f"MultiRowData(row_count={len(self._row_data_arr)}, "
                f"total_data_length={self.total_data_length()}, "
                f"thumb_path='{self.thumb_path}', "
                f"compress={self.compress}, "
                f"row_layout_direction={self.row_layout_direction.name})")
    
    def __repr__(self) -> str:
        """
        返回对象的详细字符串表示
        
        Returns:
            str: 对象的详细字符串描述
        """
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        """
        比较两个MultiRowData对象是否相等
        
        Args:
            other: 要比较的对象
            
        Returns:
            bool: 如果相等返回True，否则返回False
        """
        if not isinstance(other, MultiRowData):
            return False
        
        return (self.row_data_arr == other.row_data_arr and
                self.image_paths == other.image_paths and
                self.thumb_path == other.thumb_path and
                self.compress == other.compress and
                self.row_layout_direction == other.row_layout_direction)
    
    def __len__(self) -> int:
        """
        返回行数据数量
        
        Returns:
            int: 行数据数量
        """
        return len(self._row_data_arr)
    
    def __getitem__(self, index: int) -> RowData:
        """
        通过索引获取行数据
        
        Args:
            index (int): 行数据索引
            
        Returns:
            RowData: 行数据对象
            
        Raises:
            IndexError: 当索引超出范围时抛出异常
        """
        return self._row_data_arr[index]
    
    def __setitem__(self, index: int, value: RowData) -> None:
        """
        通过索引设置行数据
        
        Args:
            index (int): 行数据索引
            value (RowData): 新的行数据对象
            
        Raises:
            IndexError: 当索引超出范围时抛出异常
        """
        self._row_data_arr[index] = value
    
    def __iter__(self):
        """
        返回行数据列表的迭代器
        
        Returns:
            Iterator: 行数据列表的迭代器
        """
        return iter(self._row_data_arr)