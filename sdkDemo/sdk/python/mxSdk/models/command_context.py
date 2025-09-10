#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CommandContext - 指令上下文类

这是从Objective-C CommandContext类移植到Python的实现。
用于将指令对象和其回调函数组合在一起，提供完整的指令处理上下文。

Author: RBQ
Date: 2024
"""

from .command import Command
from .command_callback import CommandCallback


class CommandContext:
    """
    指令上下文类
    
    将指令对象和其回调函数组合在一起，提供完整的指令处理上下文
    
    Attributes:
        command (Command): 指令对象
        command_callback (CommandCallback): 指令回调
    """
    
    def __init__(self, command: Command, command_callback: CommandCallback):
        """
        初始化CommandContext对象
        
        Args:
            command (Command): 指令对象
            command_callback (CommandCallback): 指令回调
        """
        self.command = command
        self.command_callback = command_callback
    
    @classmethod
    def create_context(cls, command: Command, command_callback: CommandCallback) -> 'CommandContext':
        """
        创建指令上下文
        
        Args:
            command (Command): 指令对象
            command_callback (CommandCallback): 指令回调
            
        Returns:
            CommandContext: 新创建的CommandContext对象
        """
        return cls(command, command_callback)
    
    def is_ready_to_send(self) -> bool:
        """
        检查指令是否准备好发送
        
        Returns:
            bool: 如果指令准备好发送返回True，否则返回False
        """
        return self.command.is_ready_to_send()
    
    def get_remaining_delay_time(self) -> float:
        """
        获取剩余的延时时间
        
        Returns:
            float: 剩余的延时时间（秒），如果已经可以发送则返回0
        """
        return self.command.get_remaining_delay_time()
    
    def __str__(self) -> str:
        """
        返回对象的字符串表示
        
        Returns:
            str: 对象的字符串表示
        """
        return f"CommandContext(command={self.command}, callback={self.command_callback})"
    
    def __repr__(self) -> str:
        """
        返回对象的详细字符串表示
        
        Returns:
            str: 对象的详细字符串表示
        """
        return self.__str__()