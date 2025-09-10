#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edenx Printer SDK Python绑定

作者: RBQ
描述: SDK的Python语言绑定模块
"""

try:
    from . import mxSdk
except ImportError as e:
    print(f"警告: 无法导入SDK模块 - {e}")
    mxSdk = None

__version__ = "1.0.0"
__author__ = "RBQ"
__description__ = "Edenx Printer SDK Python绑定"

__all__ = ["mxSdk"]