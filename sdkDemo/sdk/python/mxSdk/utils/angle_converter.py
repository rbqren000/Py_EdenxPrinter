#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角度转换工具类

提供弧度和角度之间的相互转换功能。所有方法都是静态方法,无需实例化即可使用。

Example:
    >>> from pyMxSdk.utils.angle_converter import AngleConverter
    >>> degree = AngleConverter.convert_radian_to_degree(3.14159)
    >>> print(f"{degree:.2f}")  # 180.00
    >>> radian = AngleConverter.convert_degree_to_radian(180)
    >>> print(f"{radian:.5f}")  # 3.14159
"""

import math


class AngleConverter:
    """角度转换工具类

    提供弧度(radian)和角度(degree)之间的转换功能:
    - 弧度转角度: radian * 180 / π
    - 角度转弧度: degree * π / 180
    """

    @staticmethod
    def convert_radian_to_degree(radian: float) -> float:
        """将弧度转换为角度

        将输入的弧度值转换为对应的角度值。结果范围在 -180° 到 180° 之间。

        Args:
            radian: 要转换的弧度值

        Returns:
            float: 转换后的角度值
        """
        # 将弧度值限制在 -π 到 π 之间
        radian = math.fmod(radian, 2 * math.pi)
        # 将弧度转换为角度
        return radian * 180 / math.pi

    @staticmethod 
    def convert_degree_to_radian(degree: float) -> float:
        """将角度转换为弧度

        将输入的角度值转换为对应的弧度值。结果范围在 -π 到 π 之间。

        Args:
            degree: 要转换的角度值

        Returns:
            float: 转换后的弧度值
        """
        # 将角度值限制在 0 到 360 度之间
        degree = math.fmod(degree, 360)
        # 将角度转换为弧度
        return degree * math.pi / 180
