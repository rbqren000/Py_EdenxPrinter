# -*- coding: utf-8 -*-
"""
DataSendType - 数据发送类型枚举

对应Objective-C中的DataSendType枚举，用于定义数据发送的类型。

作者: RBQ
日期: 2025
"""

from enum import Enum


class DataSendType(Enum):
    """
    数据发送类型枚举
    
    定义了不同的数据发送模式：
    - DATA_SEND_ONCE_CONTINUOUS: 一次性连续发送
    - DATA_SEND_COMPLETE_ONCE_WAIT_NEXT: 完成一次后等待下一次
    """
    
    # 一次性连续发送
    DATA_SEND_ONCE_CONTINUOUS = "DataSendOnceContinuous"
    
    # 完成一次后等待下一次
    DATA_SEND_COMPLETE_ONCE_WAIT_NEXT = "DataSendCompleteOnceWaitNext"
    
    def __str__(self) -> str:
        """返回枚举值的字符串表示"""
        return self.value
    
    def __repr__(self) -> str:
        """返回枚举的详细表示"""
        return f"DataSendType.{self.name}"