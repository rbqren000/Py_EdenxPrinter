#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据压缩工具类
提供与 Objective-C Compress.h/m 完全一致的功能
"""
from typing import List, Union, Optional
import numpy as np
from numpy.typing import NDArray

class Compress:

    @staticmethod
    def compress_row_data(data72: np.ndarray) -> np.ndarray:
        """
        压缩单拼数据

        Args:
            data72: 72 字节数据

        Returns:
            压缩后的 72 字节数据
        """
        total_bytes: int = data72.size
        width: int = total_bytes // 72
        c_width: int = (width + 1) // 2

        c72: np.ndarray = np.zeros(c_width * 72, dtype=np.uint8)

        for c in range(c_width):
            col0 = data72[(c * 2) * 72 : (c * 2 + 1) * 72]
            if (c * 2 + 1) < width:
                col1 = data72[(c * 2 + 1) * 72 : (c * 2 + 2) * 72]
                c72[c * 72 : (c + 1) * 72] = col0 | col1
            else:
                c72[c * 72 : (c + 1) * 72] = col0
        return c72

    @staticmethod
    def uncompress_row_data(c72: np.ndarray, width: int) -> np.ndarray:
        """
        解压缩单拼数据

        Args:
            c72: 压缩后的数据
            width: 原始宽度

        Returns:
            解压缩后的数据
        """
        if c72.size == 0 or width <= 0:
            return np.array([], dtype=np.uint8)

        d72: np.ndarray = np.zeros(width * 72, dtype=np.uint8)
        c_width: int = (width + 1) // 2

        for c in range(c_width):
            col = c72[c * 72 : (c + 1) * 72]
            r0 = (c * 2) * 72
            d72[r0 : r0 + 72] = col

            if c * 2 + 1 < width:
                r1 = (c * 2 + 1) * 72
                d72[r1 : r1 + 72] = col

        return d72

    @staticmethod
    def simulation_compress_with_uncompress(
        binary: np.ndarray,
        uncompress: np.ndarray,
        width: int,
        height: int
    ) -> None:
        """
        模拟压缩并解压图像。

        Args:
            binary: 原始图像像素数据 (uint32)，尺寸 width * height。
            uncompress: 解压结果缓冲区（需预分配 width * height 大小）。
            width: 图像宽度。
            height: 图像高度。
        """
        if width <= 0 or height <= 0:
            return

        c_width: int = (width + 1) // 2
        c72: np.ndarray = np.zeros(c_width * height, dtype=np.uint32)

        for r in range(height):
            for cw in range(c_width):
                bt_0 = binary[r * width + (cw * 2)]
                bt_1 = binary[r * width + (cw * 2 + 1)] if cw < c_width - 1 else 255
                c72[r * c_width + cw] = 255 if bt_0 == 255 or bt_1 == 255 else 0

        for r in range(height):
            for cw in range(c_width):
                color = c72[r * c_width + cw]
                uncompress[r * width + (cw * 2)] = color
                if cw < c_width - 1:
                    uncompress[r * width + (cw * 2 + 1)] = color


    @staticmethod
    def merge_simulation_compress_with_uncompress(
        binary: np.ndarray,
        uncompress: np.ndarray,
        width: int,
        height: int
    ) -> None:
        """
        Args:
            binary: 输入原始图像数据，shape=(height, width)
            uncompress: 输出解压数据，shape=(height, width)，必须提前分配好
            width: 图像宽度
            height: 图像高度
        
        Returns:
            c72: 压缩后的图像数据，shape=(height, (width+1)//2)
        """
        if width <= 0 or height <= 0:
            return None

        c_width: int = (width + 1) // 2
        c72:np.ndarray = np.zeros(c_width * height, dtype=np.uint32)

        for r in range(height):
            for cw in range(c_width):
                
                bt_0 = binary[r * width + (cw * 2)]
                bt_1 = binary[r * width + (cw * 2 + 1)] if (cw * 2 + 1) < width else 255

                # 压缩
                compressedValue = 255 if bt_0 == 255 or bt_1 == 255 else 0
                c72[r * c_width + cw] = compressedValue

                # 解压
                uncompress[r * width + (cw * 2)] = compressedValue
                if cw < c_width - 1:
                    uncompress[r * width + (cw * 2 + 1)] = compressedValue
