#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LogoData - Logo数据类

对应Objective-C中的LogoData类，用于表示Logo数据信息。
包含数据路径、数据长度和图像路径等属性。

作者: RBQ
日期: 2025
"""

from typing import Optional
from ..utils.mx_file_manager import FileManager
from ..utils.rbq_log import RBQLog


class LogoData:
    """
    Logo数据类
    
    用于表示Logo数据的信息，包括数据路径、数据长度和图像路径。
    提供数据包计算和数据读取功能。
    
    Attributes:
        data_path (str): 数据文件路径
        data_length (int): 数据长度
        image_path (str): 图像文件路径
    """
    
    def __init__(self, data_path: Optional[str] = None, data_length: int = 0, image_path: Optional[str] = None):
        """
        初始化Logo数据对象
        
        Args:
            data_path (Optional[str], optional): 数据文件路径，默认为None
            data_length (int, optional): 数据长度，默认为0
            image_path (Optional[str], optional): 图像文件路径，默认为None
        """
        self._data_path = data_path
        self._data_length = data_length
        self._image_path = image_path
    
    @property
    def data_path(self) -> Optional[str]:
        """
        获取数据文件路径
        
        Returns:
            Optional[str]: 数据文件路径
        """
        return self._data_path
    
    @data_path.setter
    def data_path(self, value: Optional[str]) -> None:
        """
        设置数据文件路径
        
        Args:
            value (Optional[str]): 新的数据文件路径
        """
        self._data_path = value
    
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
    
    def total_packet_count(self, useful_data_len: int) -> int:
        """
        计算总数据包数量
        
        根据有用数据长度计算需要多少个数据包来传输所有数据。
        
        Args:
            useful_data_len (int): 每个数据包中有用数据的长度
            
        Returns:
            int: 总数据包数量
        """
        if self._data_length % useful_data_len == 0:
            return self._data_length // useful_data_len
        else:
            return self._data_length // useful_data_len + 1
    
    def packet_count(self, useful_data_len: int) -> int:
        """
        计算数据包数量（别名方法）
        
        这是total_packet_count方法的别名，为了兼容测试代码。
        
        Args:
            useful_data_len (int): 每个数据包中有用数据的长度
            
        Returns:
            int: 数据包数量
            
        Raises:
            ValueError: 当useful_data_len小于等于0时抛出异常
        """
        if useful_data_len <= 0:
            raise ValueError("useful_data_len must be greater than 0")
        
        if self._data_length <= 0:
            return 0
        
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
        if not self._data_path:
            return None
        
        RBQLog.log_debug(f"获取的数据的文件路径为: {self._data_path}")
        return FileManager.load_data(self._data_path)
    
    def __str__(self) -> str:
        """
        返回对象的字符串表示
        
        Returns:
            str: 对象的字符串描述
        """
        return (f"LogoData(data_path='{self.data_path}', "
                f"data_length={self.data_length}, "
                f"image_path='{self.image_path}')")
    
    def __repr__(self) -> str:
        """
        返回对象的详细字符串表示
        
        Returns:
            str: 对象的详细字符串描述
        """
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        """
        比较两个LogoData对象是否相等
        
        Args:
            other: 要比较的对象
            
        Returns:
            bool: 如果相等返回True，否则返回False
        """
        if not isinstance(other, LogoData):
            return False
        
        return (self.data_path == other.data_path and
                self.data_length == other.data_length and
                self.image_path == other.image_path)
    
    def __hash__(self) -> int:
        """
        返回对象的哈希值
        
        Returns:
            int: 对象的哈希值
        """
        return hash((self.data_path, self.data_length, self.image_path))