#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataObjCallback - 数据对象回调类

这是从Objective-C DataObjCallback类移植到Python的实现，采用Protocol协议模式。
用于处理数据对象的回调事件，包括成功、错误和超时回调。

Author: RBQ
Date: 2024
"""

from typing import Callable, Optional, Protocol, runtime_checkable
from .data_obj import DataObj


@runtime_checkable
class DataObjProtocol(Protocol):
    """
    数据对象回调委托协议
    
    定义了数据对象回调的接口方法
    """
    
    def on_data_obj_write_success(self, data_obj: DataObj, obj: Optional[object] = None) -> None:
        """
        数据对象写入成功回调
        
        Args:
            data_obj (DataObj): 数据对象
            obj (Optional[object]): 附加对象
        """
        pass
    
    def on_data_obj_write_error(self, data_obj: Optional[DataObj], error_msg: str) -> None:
        """
        数据对象写入错误回调
        
        Args:
            data_obj (Optional[DataObj]): 数据对象
            error_msg (str): 错误消息
        """
        pass
    
    def on_data_obj_write_timeout(self, data_obj: DataObj, error_msg: str) -> None:
        """
        数据对象写入超时回调
        
        Args:
            data_obj (DataObj): 数据对象
            error_msg (str): 错误消息
        """
        pass


class DataObjCallback:
    """
    数据对象回调类

    用于处理数据对象的各种回调事件，采用Protocol协议模式实现

    通过指定实现DataObjProtocol协议的处理器对象来接收回调事件。

    Attributes:
        _handler (Optional[DataObjProtocol]): 回调处理器对象，实现DataObjProtocol协议
    """

    def __init__(self, handler: Optional[DataObjProtocol] = None):
        """
        初始化DataObjCallback对象

        Args:
            handler (Optional[DataObjProtocol]): 回调处理器对象

        Raises:
            TypeError: 如果提供的handler不实现DataObjProtocol协议
        """
        if handler is not None and not isinstance(handler, DataObjProtocol):
            raise TypeError("handler must implement DataObjProtocol")
        self._handler = handler

    def _trigger_success(self, data_obj: DataObj, obj: Optional[object] = None) -> None:
        """
        触发成功回调

        Args:
            data_obj (DataObj): 数据对象
            obj (Optional[object]): 附加对象
        """
        if self._handler:
            self._handler.on_data_obj_write_success(data_obj, obj)

    def _trigger_error(self, data_obj: Optional[DataObj], error_msg: str) -> None:
        """
        触发错误回调

        Args:
            data_obj (Optional[DataObj]): 数据对象
            error_msg (str): 错误消息
        """
        if self._handler:
            self._handler.on_data_obj_write_error(data_obj, error_msg)

    def _trigger_timeout(self, data_obj: DataObj, error_msg: str) -> None:
        """
        触发超时回调

        Args:
            data_obj (DataObj): 数据对象
            error_msg (str): 错误消息
        """
        if self._handler:
            self._handler.on_data_obj_write_timeout(data_obj, error_msg)

    def __str__(self) -> str:
        """
        返回对象的字符串表示

        Returns:
            str: 对象的字符串表示
        """
        has_handler = bool(self._handler)
        return f"DataObjCallback(has_handler={has_handler})"

    def __repr__(self) -> str:
        """
        返回对象的详细字符串表示

        Returns:
            str: 对象的详细字符串表示
        """
        return self.__str__()