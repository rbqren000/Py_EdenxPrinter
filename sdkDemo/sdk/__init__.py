#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edenx Printer SDK

作者: RBQ
描述: 跨平台打印机设备通信和图像处理SDK
"""

try:
    from .python import mxSdk
except ImportError as e:
    print(f"警告: 无法导入SDK模块 - {e}")
    mxSdk = None

__version__ = "1.0.0"
__author__ = "RBQ"
__description__ = "Edenx Printer SDK - 跨平台打印机设备通信和图像处理"

__all__ = ["mxSdk"]
