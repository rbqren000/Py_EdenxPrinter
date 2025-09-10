#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
仿射变换转换工具类

提供从仿射变换矩阵中提取旋转角度的功能。所有方法都是静态方法,无需实例化即可使用。

Example:
    >>> from pyMxSdk.utils.affine_transform_converter import AffineTransformConverter
    >>> # 创建一个旋转45度的仿射变换矩阵
    >>> import math
    >>> cos45 = math.cos(math.radians(45))
    >>> sin45 = math.sin(math.radians(45))
    >>> matrix = [[cos45, -sin45, 0], [sin45, cos45, 0]]
    >>> radian = AffineTransformConverter.cg_affine_transform_to_radian(matrix)
    >>> degree = math.degrees(radian)
    >>> print(f"{degree:.1f}")  # 45.0
    >>> print(f"{radian:.5f}")  # 0.78540
"""

import math
from typing import Union, Tuple, List


class AffineTransformConverter:
    """
    仿射变换转换器
    
    这个类提供了仿射变换矩阵的转换功能，主要用于处理2D图形变换。
    专为PC端Python环境设计的2D图形变换工具。
    
    主要功能:
    - 创建各种类型的仿射变换矩阵
    - 矩阵运算和组合
    - 点和矩形的变换
    - 变换参数的提取和分析
    """

    @staticmethod
    def cg_affine_transform_to_radian(transform: Union[List[List[float]], Tuple[Tuple[float, ...], ...]]) -> float:
        """将仿射变换矩阵转换为弧度

        从仿射变换矩阵中提取旋转角度，并返回弧度值。结果范围在 0 到 2π 之间。

        Args:
            transform: 仿射变换矩阵，可以是numpy数组、列表或元组
                      格式为 [[a, c, tx], [b, d, ty]] 或 [[a, c], [b, d]]

        Returns:
            float: 转换后的弧度值
        """
        # 提取a和b元素
        a = transform[0][0]
        b = transform[1][0]
        
        # 计算弧度
        radian = math.atan2(b, a)
        
        # 处理负弧度，使结果范围在0到2π之间
        if radian < 0:
            radian = 2 * math.pi + radian
            
        return radian

    @staticmethod
    def cg_affine_transform_to_degree(transform: Union[List[List[float]], Tuple[Tuple[float, ...], ...]]) -> float:
        """将仿射变换矩阵转换为角度

        从仿射变换矩阵中提取旋转角度，并返回角度值。结果范围在 0° 到 360° 之间。

        Args:
            transform: 仿射变换矩阵，可以是numpy数组、列表或元组
                      格式为 [[a, c, tx], [b, d, ty]] 或 [[a, c], [b, d]]

        Returns:
            float: 转换后的角度值
        """
        # 获取弧度值
        radian = AffineTransformConverter.cg_affine_transform_to_radian(transform)
        
        # 将弧度转换为角度
        return radian * 180 / math.pi