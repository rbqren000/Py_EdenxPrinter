#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataObjContext - 数据对象上下文类

这是从Objective-C DataObjContext类移植到Python的实现。
用于将数据对象和其回调函数组合在一起，提供完整的数据处理上下文。

Author: RBQ
Date: 2024
"""

from .data_obj import DataObj
from .data_obj_callback import DataObjCallback
from .data_obj import DataObj

class DataObjContext:
    """
    数据对象上下文类
    
    将数据对象和其回调函数组合在一起，提供完整的数据处理上下文
    
    Attributes:
        data_obj (DataObj): 数据对象
        data_obj_callback (DataObjCallback): 数据对象回调
    """
    
    def __init__(self, data_obj: DataObj, data_obj_callback: DataObjCallback):
        """
        初始化DataObjContext对象
        
        Args:
            data_obj (DataObj): 数据对象
            data_obj_callback (DataObjCallback): 数据对象回调
        """
        self.data_obj = data_obj
        self.data_obj_callback = data_obj_callback
    
    @classmethod
    def create_context(cls, data_obj: DataObj, data_obj_callback: DataObjCallback) -> 'DataObjContext':
        """
        创建数据对象上下文
        
        Args:
            data_obj (DataObj): 数据对象
            data_obj_callback (DataObjCallback): 数据对象回调
            
        Returns:
            DataObjContext: 新创建的DataObjContext对象
        """
        return cls(data_obj, data_obj_callback)
    
    def __str__(self) -> str:
        """
        返回对象的字符串表示
        
        Returns:
            str: 对象的字符串表示
        """
        return f"DataObjContext(data_obj={self.data_obj}, callback={self.data_obj_callback})"
    
    def __repr__(self) -> str:
        """
        返回对象的详细字符串表示
        
        Returns:
            str: 对象的详细字符串表示
        """
        return self.__str__()