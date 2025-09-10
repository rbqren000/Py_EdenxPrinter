#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataObj - 数据对象类

这是从Objective-C DataObj类移植到Python的实现。
用于封装数据传输中的基本数据对象。

Author: RBQ
Date: 2024
"""

from typing import Optional


class DataObj:
    """
    数据对象类，用于封装数据传输中的基本数据对象
    
    Attributes:
        index (int): 指令号，一般为随机数
        data (Optional[bytes]): 数据内容
        tag (int): 标签
    """
    
    def __init__(self, data: Optional[bytes] = None, index: int = -1, tag: int = -1):
        """
        初始化DataObj对象
        
        Args:
            data (Optional[bytes]): 数据内容
            index (int): 指令号，默认为-1
            tag (int): 标签，默认为-1
        """
        self.index = index
        self.data = data
        self.tag = tag
    
    @classmethod
    def create_with_data(cls, data: bytes) -> 'DataObj':
        """
        使用数据创建DataObj对象
        
        Args:
            data (bytes): 数据内容
            
        Returns:
            DataObj: 新创建的DataObj对象
        """
        return cls(data=data)
    
    @classmethod
    def create_with_data_and_tag(cls, data: bytes, tag: int) -> 'DataObj':
        """
        使用数据和标签创建DataObj对象
        
        Args:
            data (bytes): 数据内容
            tag (int): 标签
            
        Returns:
            DataObj: 新创建的DataObj对象
        """
        return cls(data=data, tag=tag)
    
    @classmethod
    def create_with_data_index_and_tag(cls, data: bytes, index: int, tag: int) -> 'DataObj':
        """
        使用数据、索引和标签创建DataObj对象
        
        Args:
            data (bytes): 数据内容
            index (int): 指令号
            tag (int): 标签
            
        Returns:
            DataObj: 新创建的DataObj对象
        """
        return cls(data=data, index=index, tag=tag)
    
    def __str__(self) -> str:
        """
        返回对象的字符串表示
        
        Returns:
            str: 对象的字符串表示
        """
        data_len = len(self.data) if self.data else 0
        return f"DataObj(index={self.index}, data_length={data_len}, tag={self.tag})"
    
    def __repr__(self) -> str:
        """
        返回对象的详细字符串表示
        
        Returns:
            str: 对象的详细字符串表示
        """
        return self.__str__()