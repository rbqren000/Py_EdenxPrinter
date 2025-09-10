# -*- coding: utf-8 -*-
"""
Connection module for mxSdk

连接模块，提供设备连接策略和工厂类。
支持USB、串口等多种连接方式。

作者: RBQ
版本: 1.0.0
创建时间: 2025
Python版本: 3.9+
"""

from .usb import UsbConnectionStrategy
from .serial import SerialConnectionStrategy
from .factory import ConnectionStrategyFactory
from .strategy import ConnectionStrategy, DeviceInfo, ConnectionStatus
from .manager import ConnectManager, ManagedConnection
from .gcd_style_timer import GCDStyleTimer
from .gcd_timer_manager import GCDTimerManager

from .parameters import (
    BaseConnectionParameters,
    UsbConnectionParameters,
    SerialConnectionParameters,
    ClassicBluetoothConnectionParameters
)

__all__ = [
    'ConnectionStrategy',
    'DeviceInfo',
    'ConnectionStatus',
    'ConnectionStrategyFactory',
    'ConnectManager',
    'ManagedConnection',
    'UsbConnectionStrategy',
    'SerialConnectionStrategy',
    'BaseConnectionParameters',
    'UsbConnectionParameters',
    'SerialConnectionParameters',
    'ClassicBluetoothConnectionParameters',
    'GCDStyleTimer',
    'GCDTimerManager',
]

__version__ = "1.0.0"
__author__ = "RBQ"