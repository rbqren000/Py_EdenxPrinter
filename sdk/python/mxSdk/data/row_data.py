#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RowData - 行数据类

对应Objective-C中的RowData类，用于表示单行图像的数据信息。
包含数据长度、数据路径和压缩标志等属性。

作者: RBQ
日期: 2025
"""

from typing import Optional
from ..utils.mx_file_manager import FileManager
from ..utils.rbq_log import RBQLog


class RowData:
    """
    行数据类
    
    用于表示单行图像的数据信息，包括数据长度、文件路径和压缩状态。
    提供数据包计算和数据读取功能。
    
    Attributes:
        data_length (int): 数据长度
        row_data_path (str): 行数据文件路径
        compress (bool): 是否压缩数据
    """
    
    def __init__(self, data_length: int = 0, row_data_path: Optional[str] = None, compress: bool = True):
        """
        初始化行数据对象
        
        Args:
            data_length (int, optional): 数据长度，默认为0
            row_data_path (Optional[str], optional): 行数据文件路径，默认为None
            compress (bool, optional): 是否压缩，默认为True
        """
        self._data_length = data_length
        self._row_data_path = row_data_path
        self._compress = compress
    
    @property
    def data_length(self) -> int:
        """
        获取数据长度
        
        Returns:
            int: 数据长度
        """
        return self._data_length
    
    @data_length.setter
    def data_length(self, value: int) -> None:
        """
        设置数据长度
        
        Args:
            value (int): 新的数据长度
        """
        self._data_length = value
    
    @property
    def row_data_path(self) -> Optional[str]:
        """
        获取行数据文件路径
        
        Returns:
            Optional[str]: 行数据文件路径
        """
        return self._row_data_path
    
    @row_data_path.setter
    def row_data_path(self, value: Optional[str]) -> None:
        """
        设置行数据文件路径
        
        Args:
            value (Optional[str]): 新的行数据文件路径
        """
        self._row_data_path = value
    
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
    
    def total_packet_count(self, useful_data_len: int) -> int:
        """
        计算总数据包数量
        
        根据有用数据长度计算需要多少个数据包来传输所有数据。
        
        Args:
            useful_data_len (int): 每个数据包中有用数据的长度
            
        Returns:
            int: 总数据包数量
            
        Raises:
            ValueError: 当useful_data_len小于等于0时抛出异常
        """
        if useful_data_len <= 0:
            raise ValueError("useful_data_len must be greater than 0")
        
        if self._data_length == 0:
            return 0
        
        # 计算数据包数量：如果能整除则直接除法，否则需要额外一个包
        if self._data_length % useful_data_len == 0:
            return self._data_length // useful_data_len
        else:
            return self._data_length // useful_data_len + 1
    
    @property
    def data(self) -> Optional[bytes]:
        """
        获取数据内容
        
        从文件路径读取数据内容。
        
        Returns:
            Optional[bytes]: 数据内容，如果文件不存在或读取失败返回None
        """
        if not self._row_data_path:
            return None
        
        RBQLog.log_debug(f"获取的数据的文件路径为: {self._row_data_path}")
        return FileManager.load_data(self._row_data_path)
    
    def __str__(self) -> str:
        """
        返回对象的字符串表示
        
        Returns:
            str: 对象的字符串描述
        """
        return (f"RowData(data_length={self.data_length}, "
                f"row_data_path='{self.row_data_path}', "
                f"compress={self.compress})")
    
    def __repr__(self) -> str:
        """
        返回对象的详细字符串表示
        
        Returns:
            str: 对象的详细字符串描述
        """
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        """
        比较两个RowData对象是否相等
        
        Args:
            other: 要比较的对象
            
        Returns:
            bool: 如果相等返回True，否则返回False
        """
        if not isinstance(other, RowData):
            return False
        
        return (self.data_length == other.data_length and
                self.row_data_path == other.row_data_path and
                self.compress == other.compress)