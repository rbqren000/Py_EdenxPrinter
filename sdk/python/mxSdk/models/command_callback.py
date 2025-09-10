#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CommandCallback - 指令回调类

这是从Objective-C CommandCallback类移植到Python的实现。
用于处理指令的回调事件，包括成功、错误和超时回调。

Author: RBQ
Date: 2024
"""

from typing import Callable, Optional, Protocol, runtime_checkable
from .command import Command

@runtime_checkable
class CommandProtocol(Protocol):
    """指令协议（结构类型协议）"""
    
    def on_command_success(self, command: Command, obj: Optional[object] = None) -> None:
        ...
    
    def on_command_error(self, command: Command, error_msg: str) -> None:
        ...
    
    def on_command_timeout(self, command: Command, error_msg: str) -> None:
        ...

class CommandCallback:
    """
    协议委托容器（支持结构类型检查）
    
    通过__init__方法的类型验证实现协议强制约束
    """
    
    def __init__(self, handler: CommandProtocol):
        if not isinstance(handler, CommandProtocol):
            raise TypeError("处理器必须实现CommandProtocol协议")
        self._handler = handler

    def _trigger_success(self, command: Command, obj: Optional[object] = None) -> None:
        self._handler.on_command_success(command, obj)

    def _trigger_error(self, command: Command, error_msg: str) -> None:
        self._handler.on_command_error(command, error_msg)

    def _trigger_timeout(self, command: Command, error_msg: str) -> None:
        self._handler.on_command_timeout(command, error_msg)
    
    def __str__(self) -> str:
        """
        返回对象的字符串表示
        
        Returns:
            str: 对象的字符串表示，包含处理器是否存在的信息
        """
        has_handler = bool(self._handler)
        return f"CommandCallback(has_handler={has_handler})"
    
    def __repr__(self) -> str:
        """
        返回对象的详细字符串表示
        
        Returns:
            str: 对象的详细字符串表示
        """
        return self.__str__()