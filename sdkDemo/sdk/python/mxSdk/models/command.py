#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command - 指令类

这是从Objective-C Command类移植到Python的实现。
用于封装指令数据，支持延时发送和超时控制。

Author: RBQ
Date: 2024
"""

import time
from typing import Optional


class Command:
    """
    指令类，用于封装指令数据和控制参数
    
    Attributes:
        index (int): 指令号，一般为随机数
        data (Optional[bytes]): 指令数据
        tag (int): 标签
        create_time (float): 指令生成时间，时间戳
        delay_time (float): 延时时间，秒。如果值为-1，则为立即发送，如果值大于0，则延时发送
        is_loss_on_timeout (bool): 超时时是否继续发送，默认False表示继续发送，当值为True时，则不再发送该指令
    """
    
    def __init__(self, 
                 data: Optional[bytes] = None, 
                 index: int = -1, 
                 tag: int = -1,
                 delay_time: float = -1,
                 create_time: float = -1,
                 is_loss_on_timeout: bool = False):
        """
        初始化Command对象
        
        Args:
            data (Optional[bytes]): 指令数据
            index (int): 指令号，默认为-1
            tag (int): 标签，默认为-1
            delay_time (float): 延时时间，默认为-1（立即发送）
            create_time (float): 指令生成时间，默认为-1（不设置时间）
            is_loss_on_timeout (bool): 超时时是否继续发送，默认为False
        """
        self.index = index
        self.data = data
        self.tag = tag
        self.create_time = create_time
        self.delay_time = delay_time
        self.is_loss_on_timeout = is_loss_on_timeout
    
    @classmethod
    def create_with_data(cls, data: bytes) -> 'Command':
        """
        使用数据创建Command对象
        
        Args:
            data (bytes): 指令数据
            
        Returns:
            Command: 新创建的Command对象
        """
        return cls(data=data)
    
    @classmethod
    def create_with_data_and_delay(cls, data: bytes, delay_time: float) -> 'Command':
        """
        使用数据和延时时间创建Command对象
        
        Args:
            data (bytes): 指令数据
            delay_time (float): 延时时间
            
        Returns:
            Command: 新创建的Command对象
        """
        create_time = time.time() if delay_time > 0 else -1
        return cls(data=data, delay_time=delay_time, create_time=create_time)
    
    @classmethod
    def create_with_data_delay_and_tag(cls, data: bytes, delay_time: float, tag: int) -> 'Command':
        """
        使用数据、延时时间和标签创建Command对象
        
        Args:
            data (bytes): 指令数据
            delay_time (float): 延时时间
            tag (int): 标签
            
        Returns:
            Command: 新创建的Command对象
        """
        create_time = time.time() if delay_time > 0 else -1
        return cls(data=data, delay_time=delay_time, tag=tag, create_time=create_time)
    
    @classmethod
    def create_with_data_and_tag(cls, data: bytes, tag: int) -> 'Command':
        """
        使用数据和标签创建Command对象
        
        Args:
            data (bytes): 指令数据
            tag (int): 标签
            
        Returns:
            Command: 新创建的Command对象
        """
        return cls(data=data, tag=tag)
    
    @classmethod
    def create_with_data_tag_and_delay(cls, data: bytes, tag: int, delay_time: float) -> 'Command':
        """
        使用数据、标签和延时时间创建Command对象
        
        Args:
            data (bytes): 指令数据
            tag (int): 标签
            delay_time (float): 延时时间
            
        Returns:
            Command: 新创建的Command对象
        """
        create_time = time.time() if delay_time > 0 else -1
        return cls(data=data, tag=tag, delay_time=delay_time, create_time=create_time)
    
    @classmethod
    def create_with_all_params(cls, data: bytes, index: int, tag: int, delay_time: float) -> 'Command':
        """
        使用所有参数创建Command对象
        
        Args:
            data (bytes): 指令数据
            index (int): 指令号
            tag (int): 标签
            delay_time (float): 延时时间
            
        Returns:
            Command: 新创建的Command对象
        """
        create_time = time.time() if delay_time > 0 else -1
        return cls(data=data, index=index, tag=tag, delay_time=delay_time, create_time=create_time)
    
    def is_ready_to_send(self) -> bool:
        """
        检查指令是否准备好发送
        
        Returns:
            bool: 如果指令准备好发送返回True，否则返回False
        """
        if self.delay_time <= 0:
            # 立即发送
            return True
        
        if self.create_time <= 0:
            # 没有设置创建时间，立即发送
            return True
        
        # 检查是否已经过了延时时间
        current_time = time.time()
        return (current_time - self.create_time) >= self.delay_time
    
    def get_remaining_delay_time(self) -> float:
        """
        获取剩余的延时时间
        
        Returns:
            float: 剩余的延时时间（秒），如果已经可以发送则返回0
        """
        if self.delay_time <= 0 or self.create_time <= 0:
            return 0.0
        
        current_time = time.time()
        elapsed_time = current_time - self.create_time
        remaining_time = self.delay_time - elapsed_time
        
        return max(0.0, remaining_time)
    
    def __str__(self) -> str:
        """
        返回对象的字符串表示
        
        Returns:
            str: 对象的字符串表示
        """
        data_len = len(self.data) if self.data else 0
        return (f"Command(index={self.index}, data_length={data_len}, tag={self.tag}, "
                f"delay_time={self.delay_time}, is_loss_on_timeout={self.is_loss_on_timeout})")
    
    def __repr__(self) -> str:
        """
        返回对象的详细字符串表示
        
        Returns:
            str: 对象的详细字符串表示
        """
        return self.__str__()