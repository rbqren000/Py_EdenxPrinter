#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transport Package - 传输协议包

该包包含数据传输协议相关的常量和工具，负责定义数据包传输中使用的协议规范。

作者: RBQ
日期: 2025
"""

from .protocol import *

__all__ = [
    # 帧头常量
    'SOH',
    'STX', 
    'STX_A',
    'STX_B',
    'STX_C',
    'STX_D',
    'STX_E',
    # 控制字符常量
    'C',
    'NAK',
    'EOT',
    # 数据包常量
    'PACKET_HEAD_LEN',
    'PACKET_HEAD_XOR_LEN',
    'CRC_LEN',
    'MAX_ERRORS'
]