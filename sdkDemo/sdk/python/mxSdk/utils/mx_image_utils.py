#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MxImageUtils - 图像处理工具类

这是从Objective-C MxImageUtils类移植到Python的实现。
提供图像处理的核心功能，包括：
- 位图转灰度
- 各种抖动算法（Floyd-Steinberg、Atkinson、Burkes）
- 灰度转二值化
- 二值图像数据格式转换
- 图像模拟和压缩处理

作者: RBQ
日期: 2025
"""

import numpy as np
from typing import Optional, Tuple, Callable, List
import math
from PIL import Image
from numpy.typing import NDArray
import numpy as np
from ..data.row_data import RowData
from ..utils.mx_file_manager import FileManager
from ..enums.row_layout_direction import RowLayoutDirection
from .compress import Compress
from .rbq_log import RBQLog
from ..opencv.opencv_utils import OpenCVUtils


class MxImageUtils:
    """图像处理工具类
    提供图像处理的核心功能，包括：
    - 位图转灰度
    - 各种抖动算法（Floyd-Steinberg、Atkinson、Burkes）
    - 灰度转二值化
    - 二值图像数据格式转换
    - 图像模拟和压缩处理
    """

    @staticmethod
    def rgb_to_int(r: int, g: int, b: int) -> int:
        """
        将RGB值转换为32位整型值。

        Args:
            r: 红色通道值 (0-255)
            g: 绿色通道值 (0-255)
            b: 蓝色通道值 (0-255)

        Returns:
            32位整型值，格式为0xAARRGGBB
        """
        return (255 << 24) | (r << 16) | (g << 8) | b

    @staticmethod
    def int_to_rgb(value: int) -> Tuple[int, int, int]:
        """
        将32位整型值转换为RGB值。

        Args:
            value: 32位整型值，格式为0xAARRGGBB

        Returns:
            包含红色、绿色和蓝色通道值的元组 (r, g, b)
        """
        r = (value >> 16) & 0xFF
        g = (value >> 8) & 0xFF
        b = value & 0xFF
        return r, g, b

    @staticmethod
    def rgba_to_int(r: int, g: int, b: int, a: int) -> int:
        """
        将RGBA值转换为32位整型值。

        Args:
            r: 红色通道值 (0-255)
            g: 绿色通道值 (0-255)
            b: 蓝色通道值 (0-255)
            a: 透明度通道值 (0-255)

        Returns:
            32位整型值，格式为0xAARRGGBB
        """
        return (a << 24) | (r << 16) | (g << 8) | b

    @staticmethod
    def int_to_rgba(value: int) -> Tuple[int, int, int, int]:
        """
        将32位整型值转换为RGBA值。

        Args:
            value: 32位整型值，格式为0xAARRGGBB

        Returns:
            包含红色、绿色、蓝色和透明度通道值的元组 (r, g, b, a)
        """
        a = (value >> 24) & 0xFF
        r = (value >> 16) & 0xFF
        g = (value >> 8) & 0xFF
        b = value & 0xFF
        return r, g, b, a

    @staticmethod
    def convert_ndarray_rgb_to_gray(pixels: np.ndarray,gray: np.ndarray) -> None:
        """
        数据示例
        pixels = np.array([
            [[255, 0,   0,   255], [0,   255, 0,   255]],  # 第1行：红色、绿色
            [[0,   0,   255, 255], [255, 255, 0,   255]],  # 第2行：蓝色、黄色
            [[0,   0,   0,   255], [255, 255, 255, 255]]   # 第3行：黑色、白色
        ], dtype=np.uint8)

        使用整数加权转换公式近似灰度值：
            gray = (R * 77 + G * 151 + B * 28) >> 8
        该公式性能优于浮点运算，同时保持较高视觉近似度。

        要求：
            - 输入图像为 RGB 或 RGBA 格式（即通道数为 3 或 4）
            - 输出灰度图以一维数组存储，顺序为按行展开（row-major）

        参数说明:
            pixels (np.ndarray): 输入三维图像数组，形状为 (height, width, channels)，其中 channels = 3 或 4
            gray (np.ndarray): 输出的一维灰度图数组，长度为 height * width，对应 pixels 展平后的像素序列
        """
        ndim = pixels.ndim
        if ndim != 3:
            return
        height, width, channels = pixels.shape
        if channels != 3 and channels != 4 and pixels.dtype != np.uint8:
            return
        # 打印上边信息
        RBQLog.log(f"height = {height}, width = {width}, channels = {channels}")
        for row in range(height):
            for col in range(width):
                r, g, b, _ = pixels[row][col]
                # RBQLog.log(f"r = {r}, g = {g}, b = {b}")
                gray[row * width + col] = (int(r) * 77 + int(g) * 151 + int(b) * 28) >> 8
                # RBQLog.log(f"gray[{row * width + col}] = {gray[row * width + col]}")


    @staticmethod
    def convert_flat_rgba_to_gray(pixels: np.ndarray, gray: np.ndarray, width: int, height: int) -> None:
        """
        从展平通道序列的一维像素数组中提取 RGB，计算灰度值并写入 gray。

        格式示例：
            pixels = [R0, G0, B0, A0, R1, G1, B1, A1, ..., RN, GN, BN, AN]
            gray[row * width + col] = 灰度值（整数加权法）

        Args:
            pixels (np.ndarray): 展平的一维像素数组，长度=width × height × channels
            gray (np.ndarray): 灰度输出数组（外部传入），长度=width × height
            width (int): 图像宽度
            height (int): 图像高度
        """

        ndim = pixels.ndim
        if ndim != 1 or pixels.dtype != np.uint8:
            return
        for row in range(height):
            for col in range(width):
                index = row * width + col
                r = pixels[index * 4 + 0]
                g = pixels[index * 4 + 1]
                b = pixels[index * 4 + 2]
                gray[row * width + col] = (r * 77 + g * 151 + b * 28) >> 8

    @staticmethod
    def convert_argb_int_array_to_gray(pixels: np.ndarray, gray: np.ndarray, width: int, height: int) -> None:
        """
        类似Android的ARGB整型数组
        格式示例：
            pixels = [0xAARRGGBB, 0xAARRGGBB, ...]
            每项为 uint32 整型颜色值，按 ARGB 排布
            gray[row * width + col] = 灰度值（整数加权法）

        Args:
            pixels (np.ndarray): 一维整型颜色数组，长度=width × height，dtype=uint32
            gray (np.ndarray): 灰度输出数组（外部传入），长度=width × height
            width (int): 图像宽度
            height (int): 图像高度
        """
        ndim = pixels.ndim
        if ndim != 1 or pixels.dtype != np.uint32:
            return
        for i in range(width * height):
            color = int(pixels[i])
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            gray[i] = (r * 77 + g * 151 + b * 28) >> 8


    @staticmethod
    def format_gray_to_floyd_dithering(
        gray: np.ndarray,
        width: int,
        height: int,
        threshold: int,
        initial_errors: np.ndarray,
        last_row_errors: np.ndarray
    ) -> None:
        """
        对灰度图应用 Floyd–Steinberg 抖动算法，并可选择传入首行误差与输出末行误差。

        Args:
            gray: 一维灰度图像数组（长度 width * height），原地处理。
            width: 图像宽度。
            height: 图像高度。
            threshold: 二值化阈值。
            initial_errors: 可选首行误差数组，长度为 width。
            last_row_errors: 可选输出末行误差数组（需提前分配），长度为 width。
        """

        for row in range(height):
            for col in range(width):

                index = row * width + col

                # 应用首行误差
                if row == 0 and initial_errors is not None:
                    gray[index] += initial_errors[col]

                old_pixel = gray[index]
                new_pixel = 255 if old_pixel > threshold else 0
                gray[index] = new_pixel

                error = old_pixel - new_pixel

                # 右侧误差扩散（7/16）
                if col + 1 < width:
                    gray[index + 1] += error * 7 // 16

                # 下一行扩散
                if row + 1 < height:
                    if col > 0:
                        gray[index + width - 1] += error * 3 // 16
                    gray[index + width] += error * 5 // 16
                    if col + 1 < width:
                        gray[index + width + 1] += error * 1 // 16

                # 记录最后一行误差
                if row == height - 1 and last_row_errors is not None:
                    if col > 0:
                        last_row_errors[col - 1] += error * 3 // 16
                    last_row_errors[col] += error * 5 // 16
                    if col + 1 < width:
                        last_row_errors[col + 1] += error * 1 // 16

    @staticmethod
    def format_gray_to_atkinson_dithering(
        gray: np.ndarray,
        width: int,
        height: int,
        threshold: int,
        initial_errors: np.ndarray = None,
        last_row_errors: np.ndarray = None
    ) -> None:
        """
        应用 Atkinson 抖动算法将灰度图像二值化，并进行误差扩散。
        支持首行误差注入及末行误差提取。

        Args:
            gray: 输入灰度图，长度 width * height，一维 int32 数组。
            width: 图像宽度。
            height: 图像高度。
            threshold: 二值化阈值。
            initial_errors: 可选首行误差数组（长度为 width）。
            last_row_errors: 可选输出的末行误差数组（长度为 width）。
        """

        for y in range(height):
            for x in range(width):
                index = y * width + x

                # 应用首行误差
                if y == 0 and initial_errors is not None:
                    gray[index] += initial_errors[x]

                old_pixel = gray[index]
                new_pixel = 255 if old_pixel > threshold else 0
                gray[index] = new_pixel
                error = old_pixel - new_pixel

                # 扩散到同一行
                if x + 1 < width:
                    gray[index + 1] += error * 1 // 8
                if x + 2 < width:
                    gray[index + 2] += error * 1 // 8

                # 下一行扩散
                if y + 1 < height:
                    row_down = (y + 1) * width
                    if x > 0:
                        gray[row_down + x - 1] += error * 1 // 8
                    gray[row_down + x] += error * 1 // 8
                    if x + 1 < width:
                        gray[row_down + x + 1] += error * 1 // 8

                # 再下一行（y+2）扩散
                if y + 2 < height:
                    gray[(y + 2) * width + x] += error * 1 // 8

                # 记录最后一行误差
                if y == height - 1 and last_row_errors is not None:
                    if x > 0:
                        last_row_errors[x - 1] += error * 1 // 8
                    last_row_errors[x] += error * 2 // 8
                    if x + 1 < width:
                        last_row_errors[x + 1] += error * 1 // 8


    @staticmethod
    def format_gray_to_burkes_dithering(
        gray: np.ndarray,
        width: int,
        height: int,
        threshold: int,
        initial_errors: np.ndarray = None,
        last_row_errors: np.ndarray = None
    ) -> None:
        """
        应用 Burkes 抖动算法将灰度图像二值化，并扩散误差至周围像素。
        支持首行误差注入与末行误差提取。

        Args:
            gray: 一维灰度图像数组，长度为 width * height，类型为 np.uint32。
            width: 图像宽度。
            height: 图像高度。
            threshold: 二值化阈值。
            initial_errors: 可选首行误差数组，长度为 width。
            last_row_errors: 可选末行误差缓冲区，长度为 width。
        """

        for row in range(height):
            for col in range(width):
                index = row * width + col

                # 注入首行误差（如提供）
                if row == 0 and initial_errors is not None:
                    gray[index] += initial_errors[col]

                old_pixel = gray[index]
                new_pixel = 255 if old_pixel > threshold else 0
                gray[index] = new_pixel
                error = old_pixel - new_pixel

                # 扩散至同一行右侧
                if col + 1 < width:
                    gray[index + 1] += error * 8 // 32
                if col + 2 < width:
                    gray[index + 2] += error * 4 // 32

                # 扩散至下一行像素
                if row + 1 < height:
                    next_row = (row + 1) * width
                    if col > 1:
                        gray[next_row + col - 2] += error * 2 // 32
                    if col > 0:
                        gray[next_row + col - 1] += error * 4 // 32
                    gray[next_row + col] += error * 8 // 32
                    if col + 1 < width:
                        gray[next_row + col + 1] += error * 4 // 32
                    if col + 2 < width:
                        gray[next_row + col + 2] += error * 2 // 32

                # 记录末行误差
                if row == height - 1 and last_row_errors is not None:
                    if col > 1:
                        last_row_errors[col - 2] += error * 2 // 32
                    if col > 0:
                        last_row_errors[col - 1] += error * 4 // 32
                    last_row_errors[col] += error * 8 // 32
                    if col + 1 < width:
                        last_row_errors[col + 1] += error * 4 // 32
                    if col + 2 < width:
                        last_row_errors[col + 2] += error * 2 // 32
    

    @staticmethod
    def gray_to_binary(gray: NDArray[np.int32],
                    binary: NDArray[np.int32],
                    width: int,
                    height: int,
                    threshold: int) -> None:
        """
        将灰度图像转换为二值图像，使用行偏移优化。

        Args:
            gray: 输入灰度图像数据，一维数组 (width * height)，值范围 0–255。
            binary: 输出二值图像数组，必须与 gray 同长度。
            width: 图像宽度。
            height: 图像高度。
            threshold: 二值化阈值。
        """
        for row in range(height):
            row_index = row * width
            for col in range(width):
                g = gray[row_index + col]
                # binary[row_index + col] = ~(g >= threshold) & 0xFF
                # RBQLog.log(f"g = {g}")
                binary[row_index + col] = 255 if g >= threshold else 0

    @staticmethod
    def gray_to_binary_index(gray: np.ndarray,
                            binary: np.ndarray,
                            width: int,
                            height: int,
                            threshold: int) -> None:
        """
        将灰度图像转换为二值图像，使用每像素全局索引处理。

        Args:
            gray: 输入灰度图像数据，一维数组 (width * height)，值范围 0–255。
            binary: 输出二值图像数组，必须与 gray 同长度。
            width: 图像宽度。
            height: 图像高度。
            threshold: 二值化阈值。
        """
        for row in range(height):
            for col in range(width):
                index = row * width + col
                g = gray[index]
                # binary[index] = ~(g >= threshold) & 0xFF
                binary[index] = 255 if g >= threshold else 0

    @staticmethod
    def format_binary_69_to_data_72_by_col(
        binary: np.ndarray,
        d72: np.ndarray,
        width: int,
        height: int
    ) -> None:
        """
        将二值图像按列压缩并转换为每列72字节的数据格式。

        Args:
            binary: 一维二值图像数据 (width * height)，每像素为 0 或 255。
            d72: 输出数组，大小为 width * 72 的 np.uint8。
            width: 图像宽度。
            height: 图像高度。
        """
        d69: np.ndarray = np.zeros(width * 69, dtype=np.uint8)

        cycle_offsets: np.ndarray = np.array([0, 48, 24, 60, 12, 36], dtype=np.int32)
        bit_shift_table: np.ndarray = np.array([0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01], dtype=np.uint8)

        for col in range(width):
            col69 = col * 69
            col72 = col * 72

            for row in range(height):
                index = col + row * width
                pixel = binary[index]

                # 将二值像素压缩进 d69 位图
                if pixel == 0:
                    byte_index = row // 8
                    bit_index = row % 8
                    d69[col69 + byte_index] |= bit_shift_table[bit_index]

                # 从 d69 映射到最终 d72 字节排列
                if d69[col69 + row // 8] & bit_shift_table[row % 8]:
                    cycle = row % 6
                    base_index = col72 + (row // 276) * 6
                    cycle_index = ((row % 276 - cycle) // 6) // 8
                    d_index = base_index + cycle_offsets[cycle] + cycle_index
                    bit_pos = ((row % 276) // 6) % 8
                    d72[d_index] |= bit_shift_table[bit_pos]


    @staticmethod
    def format_binary_69_to_data_72_by_row(
        binary: np.ndarray,
        d72: np.ndarray,
        width: int,
        height: int
    ) -> None:
        """
        按行遍历像素，将二值图像转换为72字节/列的压缩格式，适用于周期排列硬件格式。

        Args:
            binary: 一维二值图像数据，大小为 width * height，值为 0 或 255。
            d72: 输出数组，每列72字节，总长度为 width * 72。
            width: 图像宽度。
            height: 图像高度。
        """
        d69: np.ndarray = np.zeros(width * 69, dtype=np.uint8)
        
        cycle_offsets: np.ndarray = np.array([0, 48, 24, 60, 12, 36], dtype=np.int32)
        bit_shift_table: np.ndarray = np.array([0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01], dtype=np.uint8)

        for row in range(height):
            row_div8 = row // 8
            row_mod8 = row % 8
            cycle = row % 6
            row_mod276 = row % 276
            row_cycle_offset = (row_mod276 - cycle) // 6
            cycle_index = row_cycle_offset // 8
            bit_pos = (row_mod276 // 6) % 8

            for col in range(width):
                col69 = col * 69
                col72 = col * 72
                pixel = binary[col + row * width]

                if pixel == 0:
                    # 将像素压缩进 d69 每列位图
                    d69[col69 + row_div8] |= bit_shift_table[row_mod8]

                # 若该位在 d69 中为 1，则映射到 d72
                if d69[col69 + row_div8] & bit_shift_table[row_mod8]:
                    base_index = col72 + (row // 276) * 6
                    d_index = base_index + cycle_offsets[cycle] + cycle_index
                    d72[d_index] |= bit_shift_table[bit_pos]


    @staticmethod
    def merge_bitmap_to_gray_floyd_dithering_binary(
        pixels: np.ndarray, 
        binary: np.ndarray,
        width: int,
        height: int,
        threshold: int,
        dithering: bool,
        compress: bool,                     # Placeholder: no effect yet
        initial_errors: np.ndarray = None,
        last_row_errors: np.ndarray = None
    ) -> None:
        """
        将 RGBA 位图转换为二值图像，支持灰度转换、Floyd–Steinberg 抖动、首行误差注入与末行误差输出。

        Args:
            pixels: 输入 RGBA 图像，长度为 width * height，类型为 np.int32。
            binary: 输出图像（灰度/二值）缓冲区，类型为 np.int32。
            width: 图像宽度。
            height: 图像高度。
            threshold: 二值化阈值。
            dithering: 是否启用 Floyd–Steinberg 抖动。
            compress: 是否启用压缩（目前无效）。
            initial_errors: 首行误差注入，长度为 width。
            last_row_errors: 最后一行误差输出（需提前分配为 width）。
        """

        ndim = pixels.ndim
        if ndim != 3:
            return
        height, width, channels = pixels.shape
        if channels != 3 and channels != 4 and pixels.dtype != np.uint8:
            return

        current_row_errors: np.ndarray = np.zeros(width, dtype=np.int32)
        next_row_errors: np.ndarray = np.zeros(width, dtype=np.int32)
        right_error = 0

        for row in range(height):
            right_error = 0
            for col in range(width):

                index = row * width + col

                r, g, b, _ = pixels[row][col]

                gray = (r * 77 + g * 151 + b * 28) >> 8
                binary[index] = gray

                # 注入首行误差
                if row == 0 and initial_errors is not None:
                    binary[index] += initial_errors[col]

                if dithering:
                    old_pixel = binary[index] + right_error + current_row_errors[col]
                    new_pixel = 255 if old_pixel > threshold else 0
                    binary[index] = new_pixel

                    error = old_pixel - new_pixel
                    right_error = error * 7 // 16

                    if col > 0:
                        next_row_errors[col - 1] += error * 3 // 16
                    next_row_errors[col] += error * 5 // 16
                    if col + 1 < width:
                        next_row_errors[col + 1] += error * 1 // 16

                # 再次应用二值转换（即使非抖动，也会统一为黑白）
                # binary[index] = -(binary[index] >= threshold) & 0xFF
                binary[index] = 255 if binary[index] >= threshold else 0

            # 交换误差缓冲区
            current_row_errors[:] = next_row_errors
            next_row_errors.fill(0)

        # 输出最后一行误差
        if last_row_errors is not None:
            last_row_errors[:] = current_row_errors


    @staticmethod
    def better_merge_bitmap_to_data72(
        pixels: np.ndarray,
        binary: np.ndarray,
        d72: np.ndarray,
        width: int,
        height: int,
        threshold: int,
        dithering: bool,
        compress: bool, 
        initial_errors: np.ndarray = None,
        last_row_errors: np.ndarray = None
    ) -> None:
        """
        将 RGBA 位图转换为二值图，并压缩为每列72字节的 d72 格式。
        包含灰度转换、抖动、误差扩散、周期映射等。

        Args:
            pixels: 输入像素数组，打包 RGBA 每像素一个 np.int32。
            binary: 中间或输出二值图（与 pixels 等长）。
            d72: 输出压缩结果，每列 72 字节。
            width: 图像宽度。
            height: 图像高度。
            threshold: 二值化阈值。
            dithering: 是否启用 Floyd–Steinberg 抖动。
            compress: 是否启用后续压缩（未使用）。
            initial_errors: 可选首行误差数组。
            last_row_errors: 可选输出最后一行误差数组。
        """

        ndim = pixels.ndim
        if ndim != 3:
            return
        height, width, channels = pixels.shape
        if channels != 3 and channels != 4 and pixels.dtype != np.uint8:
            return

        d69: np.ndarray = np.zeros(width * 69, dtype=np.uint8)
        current_row_errors: np.ndarray = np.zeros(width, dtype=np.int32)
        next_row_errors: np.ndarray = np.zeros(width, dtype=np.int32)
        right_error = 0

        cycle_offsets = [0, 48, 24, 60, 12, 36]
        bit_shift_table = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]

        for row in range(height):
            right_error = 0

            for col in range(width):
                index = row * width + col

                r, g, b, _ = pixels[row][col]

                gray = (r * 77 + g * 151 + b * 28) >> 8

                binary[index] = gray

                if row == 0 and initial_errors is not None:
                    binary[index] += initial_errors[col]

                if dithering:
                    old_pixel = binary[index] + right_error + current_row_errors[col]
                    new_pixel = 255 if old_pixel > threshold else 0
                    binary[index] = new_pixel
                    error = old_pixel - new_pixel
                    right_error = error * 7 // 16
                    if col > 0:
                        next_row_errors[col - 1] += error * 3 // 16
                    next_row_errors[col] += error * 5 // 16
                    if col + 1 < width:
                        next_row_errors[col + 1] += error * 1 // 16

                # 二值化（无论是否抖动，统一转成黑白）
                # binary[index] = -(binary[index] >= threshold) & 0xFF
                binary[index] = 255 if binary[index] >= threshold else 0

                # d69压缩
                if binary[index] == 0:
                    row_div8 = row // 8
                    d69[col * 69 + row_div8] |= bit_shift_table[row % 8]

                # d69 → d72映射
                if d69[col * 69 + row // 8] & bit_shift_table[row % 8]:
                    cycle = row % 6
                    base_index = col * 72 + (row // 276) * 6
                    cycle_index = ((row % 276 - cycle) // 6) // 8
                    d_index = base_index + cycle_offsets[cycle] + cycle_index
                    bit_pos = ((row % 276) // 6) % 8
                    d72[d_index] |= bit_shift_table[bit_pos]

            current_row_errors[:] = next_row_errors
            next_row_errors.fill(0)

        if last_row_errors is not None:
            last_row_errors[:] = current_row_errors


    @staticmethod
    def create_row_data(
        pixels: np.ndarray,               # 每像素一个32位RGBA整数，小端排列
        width: int,
        height: int,
        threshold: int,
        dithering: bool,
        compress: bool,
        initial_errors: np.ndarray = None,
        last_row_errors: np.ndarray = None
    ) -> RowData:
        """
        完整图像处理流程，将 RGBA 数据转为压缩后的 d72 数据，返回 RowData。
        """

        gray: np.ndarray = np.zeros(width * height, dtype=np.int32)
        MxImageUtils.convert_ndarray_rgb_to_gray(pixels, gray, width, height)

        if dithering:
            MxImageUtils.format_gray_to_floyd_dithering(
                gray, width, height, threshold,
                initial_errors=initial_errors,
                last_row_errors=last_row_errors
            )

        binary: np.ndarray = np.zeros_like(gray)
        MxImageUtils.gray_to_binary(gray, binary, width, height, threshold)

        d72: np.ndarray = np.zeros(width * 72, dtype=np.uint8)
        MxImageUtils.format_binary_69_to_data_72_by_col(binary, d72, width, height)

        if compress:
            d72 = Compress.compress_row_data(d72)

        data_path = FileManager.save_data_to_cache(d72.tobytes())

        return RowData(
            data_length=len(d72),
            row_data_path=data_path,
            compress=compress
        )
    
    @staticmethod
    def merge_create_row_data(
        pixels: np.ndarray, 
        width: int,
        height: int,
        threshold: int,
        dithering: bool,
        compress: bool,
        initial_errors: np.ndarray = None,
        last_row_errors: np.ndarray = None
    ) -> RowData:
        """
        更强融合流程：RGBA → gray + dither → binary → data72 → compress → cache。
        """
        binary: np.ndarray = np.zeros(width * height, dtype=np.int32)
        MxImageUtils.merge_bitmap_to_gray_floyd_dithering_binary(
            pixels=pixels,
            binary=binary,
            width=width,
            height=height,
            threshold=threshold,
            dithering=dithering,
            compress=compress,
            initial_errors=initial_errors,
            last_row_errors=last_row_errors
        )

        d72: np.ndarray = np.zeros(width * 72, dtype=np.uint8)
        MxImageUtils.format_binary_69_to_data_72_by_col(binary, d72, width, height)

        if compress:
            d72 = Compress.compress_row_data(d72)

        data_path: str = FileManager.save_data_to_cache(d72.tobytes())

        return RowData(
            row_data_path=data_path,
            data_length=len(d72),
            compress=compress
        )

    @staticmethod
    def image_simulation_by_binary(
        binary: np.ndarray,
        width: int,
        height: int,
        compress: bool = False,
        row_layout_direction: RowLayoutDirection = RowLayoutDirection.VERTICAL
    ) -> Image.Image:
        if compress:
            uncompressed: np.ndarray = np.zeros(width * height, dtype=np.int32)
            Compress.merge_simulation_compress_with_uncompress(
                binary, uncompressed, width, height
            )
            pixel_data: np.ndarray = uncompressed
        else:
            pixel_data: np.ndarray = binary
        
        # 扩展为 RGBA 格式：R=G=B=pixel, A=255（不透明）
        rgba_array = np.zeros((height, width, 4), dtype=np.uint8)
        # rgba_array[:, :, 0] = pixel_data.reshape((height, width))  # Red
        # rgba_array[:, :, 1] = pixel_data.reshape((height, width))  # Green
        # rgba_array[:, :, 2] = pixel_data.reshape((height, width))  # Blue
        # rgba_array[:, :, 3] = 255 
        rgba_array[:, :, :3] = pixel_data.reshape((height, width))[:, :, None]
        rgba_array[:, :, 3] = 255

        image = Image.frombytes(
            mode="RGBA",
            size=(width, height),
            data=rgba_array,
            decoder_name="raw"
        )

        if row_layout_direction == RowLayoutDirection.HORIZONTAL:
            image = image.rotate(90, expand=True)

        return image

    @staticmethod
    def image_simulation_by_binary_with_save(
        binary: np.ndarray,
        width: int,
        height: int,
        compress: bool,
        row_layout_direction: RowLayoutDirection
    ) -> str:
        image: Image.Image = MxImageUtils.image_simulation_by_binary(
            binary=binary,
            width=width,
            height=height,
            compress=compress,
            row_layout_direction=row_layout_direction
        )
        image_path: str = FileManager.save_image_to_cache(image)
        return image_path

    @staticmethod
    def merge_image_simulation_by_pixels(
        pixels: np.ndarray,
        width: int,
        height: int,
        threshold: int,
        dithering: bool,
        compress: bool,
        row_layout_direction: RowLayoutDirection,
        initial_errors: np.ndarray = None,
        last_row_errors: np.ndarray = None
    ) -> Image.Image:

        binary: np.ndarray = np.zeros(width * height, dtype=np.int32)
        MxImageUtils.merge_bitmap_to_gray_floyd_dithering_binary(
            pixels=pixels,
            binary=binary,
            width=width,
            height=height,
            threshold=threshold,
            dithering=dithering,
            compress=compress,
            initial_errors=initial_errors,
            last_row_errors=last_row_errors
        )

        return MxImageUtils.image_simulation_by_binary(
            binary=binary,
            width=width,
            height=height,
            compress=compress,
            row_layout_direction=row_layout_direction
        )

    @staticmethod
    def merge_image_simulation_by_pixels_with_save(
        pixels: np.ndarray,
        width: int,
        height: int,
        threshold: int,
        dithering: bool,
        compress: bool,
        row_layout_direction: RowLayoutDirection,
        initial_errors: np.ndarray = None,
        last_row_errors: np.ndarray = None
    ) -> str:
        image: Image.Image = MxImageUtils.merge_image_simulation_by_pixels(
            pixels=pixels,
            width=width,
            height=height,
            threshold=threshold,
            dithering=dithering,
            compress=compress,
            row_layout_direction=row_layout_direction,
            initial_errors=initial_errors,
            last_row_errors=last_row_errors
        )
        image_path: str = FileManager.save_image_to_cache(image)
        return image_path


    
    @staticmethod
    def merge_simulate_image_by_image(
        image: Image.Image,
        threshold: int,
        clear_background: bool,
        dithering: bool,
        compress: bool,
        top_beyond_distance: int,
        bottom_beyond_distance: int,
        is_zoom_to_552: bool,
        row_layout_direction: RowLayoutDirection,
        initial_errors: np.ndarray = None,
        last_row_errors: np.ndarray = None
    ) -> Image.Image:

        width, height = image.size
        valid_height = height - top_beyond_distance - bottom_beyond_distance

        if valid_height != 552 and is_zoom_to_552:
            scale = 552 / valid_height
            new_top = int(top_beyond_distance * scale)
            new_bottom = int(bottom_beyond_distance * scale)
            new_width = int(width * scale)
            new_height = int(552 + new_top + new_bottom)
            image = image.resize((new_width, new_height), resample=Image.BICUBIC)
        else:
            new_width = int(width)
            new_height = int(height)
            new_top = top_beyond_distance
            new_bottom = bottom_beyond_distance

        if clear_background:
            image = OpenCVUtils.light_clear_background(image)

        rgba_array:np.ndarray = np.array(image.convert("RGBA"), dtype=np.uint8)
        # 轮训打印rgba_array
        # _height, _width, _ = rgba_array.shape
        # for y in range(_height):
        #     row = rgba_array[y]  # shape: (width, 4)
        #     for x in range(_width):
        #         r, g, b, a = row[x]
        #         RBQLog.log(f"rgba_array (y={y}, x={x}): R={r}, G={g}, B={b}, A={a}")

        #计算有效范围
        start_row = int(new_top)
        end_row = start_row + int(valid_height)
        # 有效像素区域
        valid_rgba_array: np.ndarray = rgba_array[start_row:end_row, :, :]
        _height, _width, _ = valid_rgba_array.shape
        RBQLog.log(f"valid_rgba_array shape: {_height}, {_width}, {_}")

        return MxImageUtils.merge_image_simulation_by_pixels(
            pixels=valid_rgba_array,
            width=new_width,
            height=(new_height - new_top - new_bottom),
            threshold=threshold,
            dithering=dithering,
            compress=compress,
            row_layout_direction=row_layout_direction,
            initial_errors=initial_errors,
            last_row_errors=last_row_errors
        )


    
    @staticmethod
    def merge_image_simulation_by_image_with_save(
        image: Image.Image,
        threshold: int,
        clear_background: bool,
        dithering: bool,
        compress: bool,
        top_beyond_distance: int,
        bottom_beyond_distance: int,
        is_zoom_to_552: bool,
        row_layout_direction: RowLayoutDirection,
        initial_errors: np.ndarray = None,
        last_row_errors: np.ndarray = None
    ) -> str:

        simulation_image = MxImageUtils.merge_simulate_image_by_image(
            image=image,
            threshold=threshold,
            clear_background=clear_background,
            dithering=dithering,
            compress=compress,
            top_beyond_distance=top_beyond_distance,
            bottom_beyond_distance=bottom_beyond_distance,
            is_zoom_to_552=is_zoom_to_552,
            row_layout_direction=row_layout_direction,
            initial_errors=initial_errors,
            last_row_errors=last_row_errors
        )

        simulation_path: str = FileManager.save_image_to_cache(simulation_image)
        return simulation_path

    @staticmethod
    def rotated_image_with_graphics_by_radians(image: Image.Image, radians: float) -> Optional[Image.Image]:
        """
        Args:
            image: PIL 的 Image 实例。
            radians: 旋转角度（单位为弧度）。

        Returns:
            新的旋转后的 Image 实例。
        """
        # 原图尺寸
        width, height = image.size
        # 打印原图尺寸
        RBQLog.log(f"【rotated_image_with_graphics_by_radians】原图尺寸: {width} x {height}")

        # 计算旋转后图像的新边界尺寸
        angle_degrees = math.degrees(radians)
        rotated_image: Image.Image = image.rotate(angle_degrees, resample=Image.BICUBIC, expand=True)

        return rotated_image
