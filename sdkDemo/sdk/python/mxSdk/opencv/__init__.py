#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenCV图像处理模块

作者: RBQ
创建时间: 2025
描述: OpenCV图像处理功能模块的统一入口
"""

# 导入配置类
from .background_cleaner import BackgroundCleanConfig

# 导入各个功能模块
from .base_utils import BaseUtils
from .background_cleaner import BackgroundCleaner
from .image_effects import ImageEffects
from .image_analysis import ImageAnalysis
from .image_geometry import ImageGeometry
from .image_scanner import ImageScanner

# 导入主工具类
from .opencv_utils import OpenCVUtils

# 导入模块化版本（可选）
from .opencv_utils_modular import OpenCVUtils as OpenCVUtilsModular

__all__ = [
    'BackgroundCleanConfig',
    'BaseUtils',
    'BackgroundCleaner',
    'ImageEffects',
    'ImageAnalysis',
    'ImageGeometry',
    'ImageScanner',
    'OpenCVUtils',
    'OpenCVUtilsModular'
]