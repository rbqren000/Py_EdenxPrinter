#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Models Package - 基础数据模型包

该包包含SDK的基础数据模型，包括数据对象、指令对象及其相关的回调和上下文类。
这些是数据传输和指令处理的核心模型。

作者: RBQ
日期: 2025
"""

from .data_obj import DataObj
from .command import Command
from .data_obj_callback import (
    DataObj,
    DataObjCallback,
    DataObjProtocol
)
from .command_callback import (
    Command,
    CommandCallback,
    CommandProtocol
)
from .data_obj_context import DataObjContext
from .command_context import CommandContext
from .device_info import DeviceInfo

__all__ = [
    # 基础模型
    'DataObj',
    'Command',
    # 回调接口
    'DataObjCallback',
    'DataObjProtocol',
    'CommandCallback', 
    'CommandProtocol',
    # 上下文
    'DataObjContext',
    'CommandContext',
    # 设备信息
    'DeviceInfo'
]