#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Factories Package - 工厂类包

该包包含各种数据工厂类，用于创建和处理不同类型的数据对象。

作者: RBQ
日期: 2025
"""

from .logo_data_factory import LogoDataFactory
from .multi_row_data_factory import MultiRowDataFactory
# from .ota_data_factory import OtaDataFactory

__all__ = [
    'LogoDataFactory',
    'MultiRowDataFactory',
    # 'OtaDataFactory'
]