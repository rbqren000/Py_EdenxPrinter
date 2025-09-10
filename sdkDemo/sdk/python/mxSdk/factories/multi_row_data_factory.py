#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiRowDataFactory - 多行数据工厂类

该模块提供了将多行图像数据转换为打印机可用数据格式的功能。
支持三种不同的处理模式：标准模式、合并模式和优化合并模式。

作者: RBQ
日期: 2025
"""

import threading
import math
from typing import Optional, List, Callable, Any
from PIL import Image
import numpy as np
from numpy.typing import NDArray
from ..data.multi_row_data import MultiRowData
from ..data.multi_row_image import MultiRowImage
from ..data.row_data import RowData
from ..data.row_image import RowImage
from ..enums.row_layout_direction import RowLayoutDirection
from ..utils.mx_file_manager import FileManager
from ..utils.mx_image_utils import MxImageUtils
from ..opencv.opencv_utils_modular import OpenCVUtils
from ..utils.compress import Compress
from ..utils.rbq_log import RBQLog
from ..utils.dispatch_main_event import DispatchMainEvent

class MultiRowDataFactory:
    """
    多行数据工厂类
    
    提供将多行图像数据转换为打印机可用数据格式的功能。
    支持标准模式、合并模式和优化合并模式三种处理方式。
    """
    
    # 打印头宽度常量
    PRINT_HEAD_WIDTH = 552
    DATA_SUFFIX = ".data"
    
    @classmethod
    def bitmap_to_multi_row_data_async(
        cls,
        multi_row_image: MultiRowImage,
        threshold: int = 128,
        clear_background: bool = False,
        dithering: bool = True,
        compress: bool = True,
        flip_horizontally: bool = False,
        is_simulation: bool = False,
        thumb_to_simulation: bool = False,
        on_start: Optional[Callable[[], None]] = None,
        on_complete: Optional[Callable[[MultiRowData], None]] = None,
        on_error: Optional[Callable[[], None]] = None
    ) -> None:
        """
        异步将位图转换为多行数据（标准模式）
        
        Args:
            multi_row_image: 多行图像对象
            threshold: 二值化阈值 (0-255)
            clear_background: 是否清除背景
            dithering: 是否使用Floyd-Steinberg抖动
            compress: 是否压缩数据
            flip_horizontally: 是否水平翻转
            is_simulation: 是否生成模拟图像
            thumb_to_simulation: 是否对缩略图进行模拟
            on_start: 开始处理回调
            on_complete: 完成处理回调
            on_error: 错误处理回调
        """
        #打印传入的参数
        RBQLog.log(f"【bitmap_to_multi_row_data_async】收到参数->阈值: {threshold}, 背景清除: {clear_background}, 抖动: {dithering}, 压缩: {compress}, 水平翻转: {flip_horizontally}")

        if not multi_row_image:
            if on_error:
                DispatchMainEvent.post(on_error)
            return
        
        def process_task():
            try:
                if on_start:
                    DispatchMainEvent.post(on_start)
                
                result = cls.bitmap_to_multi_row_data(
                    multi_row_image=multi_row_image,
                    threshold=threshold,
                    clear_background=clear_background,
                    dithering=dithering,
                    compress=compress,
                    flip_horizontally=flip_horizontally,
                    is_simulation=is_simulation,
                    thumb_to_simulation=thumb_to_simulation
                )
                
                if result and on_complete:
                    DispatchMainEvent.post(on_complete, result)
                elif not result and on_error:
                    DispatchMainEvent.post(on_error)
                    
            except Exception as e:
                RBQLog.log_error(f"异步处理多行数据时发生错误: {e}")
                if on_error:
                    DispatchMainEvent.post(on_error)
        
        # 在线程池中执行处理任务
        thread = threading.Thread(target=process_task)
        thread.start()
    
    @classmethod
    def bitmap_to_multi_row_data(
        cls,
        multi_row_image: MultiRowImage,
        threshold: int = 128,
        clear_background: bool = False,
        dithering: bool = True,
        compress: bool = True,
        flip_horizontally: bool = False,
        is_simulation: bool = False,
        thumb_to_simulation: bool = False
    ) -> Optional[MultiRowData]:
        """
        将位图转换为多行数据（标准模式）
        
        Args:
            multi_row_image: 多行图像对象
            threshold: 二值化阈值 (0-255)
            clear_background: 是否清除背景
            dithering: 是否使用Floyd-Steinberg抖动
            compress: 是否压缩数据
            flip_horizontally: 是否水平翻转
            is_simulation: 是否生成模拟图像
            thumb_to_simulation: 是否对缩略图进行模拟
            
        Returns:
            MultiRowData对象，失败时返回None
        """
        if not multi_row_image:
            return None
        
        try:
            row_layout_direction = multi_row_image.row_layout_direction
            # 是否为裁剪所得的连续图
            is_contiguous_cropped_images = multi_row_image.is_contiguous_cropped_images
            row_data_arr: List[RowData] = []
            image_paths: List[str] = [] if is_simulation else None
            row_image_arr: List[RowImage] = multi_row_image.row_images

            # Floyd-Steinberg抖动的误差传递
            row_data_initial_errors: np.ndarray = None
            row_data_last_row_errors: np.ndarray = None
            # simulation_initial_errors: np.ndarray = None
            # simulation_last_row_errors: np.ndarray = None

            # 遍历每一行图像
            for sm, row_image in enumerate(row_image_arr):
                origin_path: str = row_image.image_path
                if not origin_path:
                    # 如果没有图像路径，跳过当前行
                    continue
                
                # 根据布局方向加载和旋转图像
                loaded_image: Image.Image = FileManager.load_image(origin_path)
                if not loaded_image:
                    # 如果加载图像失败，跳过当前行
                    continue
                
                # 水平翻转（如果需要）
                if flip_horizontally:
                    loaded_image = loaded_image.transpose(Image.FLIP_LEFT_RIGHT)
                
                if row_layout_direction == RowLayoutDirection.HORIZONTAL:
                    # image = MxImageUtils.rotated_image_with_graphics_by_radians(
                    #     loaded_image,
                    #     math.pi / 2
                    # )
                    image = loaded_image.rotate(90, expand=True)
                else:
                    image = loaded_image
                
                if not image:
                    #  如果加载图像失败，跳过当前行
                    continue
                
                top_beyond_distance = row_image.top_beyond_distance
                bottom_beyond_distance = row_image.bottom_beyond_distance
                
                width, height = image.size
                valid_height = height - top_beyond_distance - bottom_beyond_distance
                
                new_image: Image.Image = None
                # 如果有效高度不为552，则缩放到552
                if valid_height != cls.PRINT_HEAD_WIDTH:
                    scale = cls.PRINT_HEAD_WIDTH / valid_height
                    new_top_beyond_distance = top_beyond_distance * scale
                    new_bottom_beyond_distance = bottom_beyond_distance * scale
                    temp_width = math.floor(width * scale)
                    temp_height = cls.PRINT_HEAD_WIDTH + new_top_beyond_distance + new_bottom_beyond_distance
                    
                    new_image = image.resize((int(temp_width), int(temp_height)), Image.LANCZOS)
                    valid_height = cls.PRINT_HEAD_WIDTH
                    # new_width = temp_width
                    # new_height = temp_height
                else:
                    new_image = image
                    # new_width = math.floor(width)
                    # new_height = height
                    new_top_beyond_distance = top_beyond_distance
                    new_bottom_beyond_distance = bottom_beyond_distance
                
                RBQLog.log_debug(
                    f"[createRowData] 处理第{sm}行: "
                    f"rowLayoutDirection={row_layout_direction}, "
                    f"width={width}, height={height}, valid_height={valid_height}, "
                    f"topBeyondDistance={top_beyond_distance}, bottomBeyondDistance={bottom_beyond_distance}, "
                    f"new_topBeyondDistance={new_top_beyond_distance}, new_bottomBeyondDistance={new_bottom_beyond_distance}"
                )
                
                # 清除背景
                if clear_background:
                    new_image = OpenCVUtils.deep_clear_background(new_image)
                
                # 获取像素数据  一维数组
                # pixels: NDArray[np.uint32] = np.frombuffer(
                #     new_image.convert("RGBA").tobytes(), dtype=np.uint32
                # )

                # image_array = np.array(new_image, dtype=np.uint8)  # 将图片转为numpy数组
                # _height, _width, _channels = image_array.shape    # 添加 _ 前缀
                # for y in range(_height):
                #     for x in range(_width):
                #         pixel = image_array[y, x]
                #         if _channels == 1:
                #             # 灰度图（单通道）
                #             gray = pixel[0]
                #             RBQLog.log(f"像素 (y={y}, x={x}): 灰度={gray}")
                #         elif _channels == 3:
                #             # RGB（三通道）
                #             r, g, b = pixel
                #             RBQLog.log(f"像素 (y={y}, x={x}): R={r}, G={g}, B={b}")
                #         elif _channels == 4:
                #             # RGBA（四通道）
                #             r, g, b, a = pixel
                #             RBQLog.log(f"像素 (y={y}, x={x}): R={r}, G={g}, B={b}, A={a}")
                #         else:
                #             # 其他情况（如多通道特殊图像）
                #             RBQLog.log(f"像素 (y={y}, x={x}): 通道数据={pixel}")

                rgba_array:np.ndarray = np.array(new_image.convert("RGBA"), dtype=np.uint8)
                # 轮训打印rgba_array
                # _height, _width, _ = rgba_array.shape
                # for y in range(_height):
                #     row = rgba_array[y]  # shape: (width, 4)
                #     for x in range(_width):
                #         r, g, b, a = row[x]
                #         RBQLog.log(f"rgba_array (y={y}, x={x}): R={r}, G={g}, B={b}, A={a}")

                #计算有效范围
                start_row = int(new_top_beyond_distance)
                end_row = start_row + int(valid_height)
                # 有效像素区域
                valid_rgba_array: np.ndarray = rgba_array[start_row:end_row, :, :]
                _height, _width, _ = valid_rgba_array.shape
                RBQLog.log(f"valid_rgba_array shape: {_height}, {_width}, {_}")
                # 打印 valid_rgba_array里边的值
                # for y in range(valid_height):
                #     for x in range(new_width):
                #         r, g, b, a = valid_rgba_array[y, x]
                #         RBQLog.log(f"valid_rgba_array (y={y}, x={x}): R={r}, G={g}, B={b}, A={a}")

                # 如果是连续图像，则需要进行误差传递
                if is_contiguous_cropped_images and row_data_last_row_errors is not None:
                    row_data_initial_errors = row_data_last_row_errors
                else:
                    row_data_initial_errors = None
                # 为 row_data_initial_errors 赋值后重置row_data_last_row_errors
                row_data_last_row_errors = None

                gray_pixels:np.ndarray = np.zeros(_width * _height, dtype=np.int32)
                # 转换为灰度
                MxImageUtils.convert_ndarray_rgb_to_gray(
                    valid_rgba_array, gray_pixels
                )
                
                if dithering:
                    # 如果是连续图像，则需要进行误差传递，这个时候需要创建row_data_last_row_errors
                    if is_contiguous_cropped_images:
                        row_data_last_row_errors:np.ndarray = np.zeros(_width, dtype=np.int32)

                    MxImageUtils.format_gray_to_floyd_dithering(
                        gray_pixels, _width, _height, 
                        threshold, row_data_initial_errors, row_data_last_row_errors
                    )

                binary_pixels:np.ndarray = np.zeros(_width * _height, dtype=np.int32)
                # 转换为二值图像
                MxImageUtils.gray_to_binary(
                    gray_pixels, binary_pixels, _width, _height, threshold
                )
                # 遍历打印binary_pixels
                # for i in range(int(_width * _height)):
                #     RBQLog.log(f"binary_pixels[{i}] = {binary_pixels[i]}")

                d72:np.ndarray = np.zeros(_width*72, dtype=np.uint8)
                # 转换为72字节数据格式
                MxImageUtils.format_binary_69_to_data_72_by_col(
                    binary_pixels,d72, _width, _height
                )
                
                # 压缩数据
                if compress:
                    data72 = Compress.compress_row_data(d72)
                else:
                    data72 = d72

                # 保存数据到缓存文件
                data_path: str = FileManager.save_data_to_cache(data72)
                
                # 创建RowData对象
                row_data = RowData()
                row_data.row_data_path = data_path
                row_data.data_length = len(data72)
                row_data.compress = compress
                
                row_data_arr.append(row_data)
                
                # 生成模拟图像
                if is_simulation:
                    image_path = MxImageUtils.image_simulation_by_binary_with_save(
                        binary_pixels, _width, _height,
                        compress, row_layout_direction
                    )
                    image_paths.append(image_path)
                
                RBQLog.log_debug(
                    f"完成第{sm}行数据处理; 图片大小:{new_image.size}; "
                    f"图片路径:{image_path if is_simulation else 'None'}; "
                    f"dataLength:{row_data.data_length}"
                )
            
            # 处理缩略图模拟
            thumb_path = None
            if thumb_to_simulation and multi_row_image.thumb_path:
                origin_thumb: Optional[Image.Image] = FileManager.load_image(multi_row_image.thumb_path)
                if origin_thumb:
                    thumb_path = MxImageUtils.merge_simulate_image_by_image(
                        image=origin_thumb,
                        threshold=threshold,
                        clear_background=clear_background,
                        dithering=dithering,
                        compress=compress,
                        top_beyond_distance=0,
                        bottom_beyond_distance=0,
                        is_zoom_to_552=False,
                        initial_errors=None
                    )
            
            # 创建MultiRowData对象
            multi_row_data = MultiRowData(
                row_data_arr=row_data_arr,
                image_paths=image_paths,
                thumb_path=thumb_path,
                compress=compress,
                row_layout_direction=row_layout_direction
            )
            
            return multi_row_data
            
        except Exception as e:
            RBQLog.log_error(f"处理多行数据时发生错误: {e}")
            return None
    
    @classmethod
    def merge_bitmap_to_multi_row_data_async(
        cls,
        multi_row_image: MultiRowImage,
        threshold: int = 128,
        clear_background: bool = False,
        dithering: bool = True,
        compress: bool = True,
        flip_horizontally: bool = False,
        is_simulation: bool = False,
        thumb_to_simulation: bool = False,
        on_start: Optional[Callable[[], None]] = None,
        on_complete: Optional[Callable[[MultiRowData], None]] = None,
        on_error: Optional[Callable[[], None]] = None
    ) -> None:
        """
        异步将位图转换为多行数据（合并模式）
        
        Args:
            multi_row_image: 多行图像对象
            threshold: 二值化阈值 (0-255)
            clear_background: 是否清除背景
            dithering: 是否使用Floyd-Steinberg抖动
            compress: 是否压缩数据
            flip_horizontally: 是否水平翻转
            is_simulation: 是否生成模拟图像
            thumb_to_simulation: 是否对缩略图进行模拟
            on_start: 开始处理回调
            on_complete: 完成处理回调
            on_error: 错误处理回调
        """
        if not multi_row_image:
            if on_error:
                DispatchMainEvent.post(on_error)
            return
        
        def process_task():
            try:
                if on_start:
                    DispatchMainEvent.post(on_start)
                
                result = cls.merge_bitmap_to_multi_row_data(
                    multi_row_image=multi_row_image,
                    threshold=threshold,
                    clear_background=clear_background,
                    dithering=dithering,
                    compress=compress,
                    flip_horizontally=flip_horizontally,
                    is_simulation=is_simulation,
                    thumb_to_simulation=thumb_to_simulation
                )
                
                if result and on_complete:
                    DispatchMainEvent.post(on_complete, result)
                elif not result and on_error:
                    DispatchMainEvent.post(on_error)
                    
            except Exception as e:
                RBQLog.log_error(f"异步处理多行数据时发生错误: {e}")
                if on_error:
                    DispatchMainEvent.post(on_error)
        
        # 在线程池中执行处理任务
        thread = threading.Thread(target=process_task)
        thread.start()
    
    @classmethod
    def merge_bitmap_to_multi_row_data(
        cls,
        multi_row_image: MultiRowImage,
        threshold: int = 128,
        clear_background: bool = False,
        dithering: bool = True,
        compress: bool = True,
        flip_horizontally: bool = False,
        is_simulation: bool = False,
        thumb_to_simulation: bool = False
    ) -> Optional[MultiRowData]:
        """
        将位图转换为多行数据（合并模式）
        
        合并模式使用一步到位的处理方式，直接从位图转换为二值数据。
        
        Args:
            multi_row_image: 多行图像对象
            threshold: 二值化阈值 (0-255)
            clear_background: 是否清除背景
            dithering: 是否使用Floyd-Steinberg抖动
            compress: 是否压缩数据
            flip_horizontally: 是否水平翻转
            is_simulation: 是否生成模拟图像
            thumb_to_simulation: 是否对缩略图进行模拟
            
        Returns:
            MultiRowData对象，失败时返回None
        """
        if not multi_row_image:
            return None
        
        try:
            row_layout_direction: RowLayoutDirection = multi_row_image.row_layout_direction
            is_contiguous_cropped_images: bool = multi_row_image.is_contiguous_cropped_images
            row_data_arr: List[RowData] = []
            image_paths: List[str] = [] if is_simulation else None
            row_image_arr: List[RowImage] = multi_row_image.row_images
            
            # Floyd-Steinberg抖动的误差传递
            row_data_initial_errors: Optional[NDArray[np.int32]] = None
            row_data_last_row_errors: Optional[NDArray[np.int32]] = None
            # simulation_initial_errors: Optional[NDArray[np.int32]] = None
            # simulation_last_row_errors: Optional[NDArray[np.int32]] = None
            
            for sm, row_image in enumerate(row_image_arr):
                origin_path = row_image.image_path
                if not origin_path:
                    return None
                
                # 根据布局方向加载和旋转图像
                loaded_image: Image.Image = FileManager.load_image(origin_path)
                if not loaded_image:
                    # 如果加载图像失败，跳过当前行
                    continue
                
                # 水平翻转（如果需要）
                if flip_horizontally:
                    loaded_image = loaded_image.transpose(Image.FLIP_LEFT_RIGHT)
                
                if row_layout_direction == RowLayoutDirection.HORIZONTAL:
                    # image = MxImageUtils.rotated_image_with_graphics_by_radians(
                    #     loaded_image,
                    #     math.pi / 2
                    # )
                    image = loaded_image.rotate(90, expand=True)
                else:
                    image = loaded_image
                
                if not image:
                    #  如果加载图像失败，跳过当前行
                    continue
                
                top_beyond_distance = row_image.top_beyond_distance
                bottom_beyond_distance = row_image.bottom_beyond_distance
                
                width, height = image.size
                valid_height = height - top_beyond_distance - bottom_beyond_distance
                
                new_image: Image.Image = None
                # 如果有效高度不为552，则缩放到552
                if valid_height != cls.PRINT_HEAD_WIDTH:
                    scale = cls.PRINT_HEAD_WIDTH / valid_height
                    new_top_beyond_distance = top_beyond_distance * scale
                    new_bottom_beyond_distance = bottom_beyond_distance * scale
                    temp_width = math.floor(width * scale)
                    temp_height = cls.PRINT_HEAD_WIDTH + new_top_beyond_distance + new_bottom_beyond_distance
                    
                    new_image = image.resize((int(temp_width), int(temp_height)), Image.LANCZOS)
                    valid_height = cls.PRINT_HEAD_WIDTH
                    # new_width = temp_width
                    # new_height = temp_height
                else:
                    new_image = image
                    # new_width = math.floor(width)
                    # new_height = height
                    new_top_beyond_distance = top_beyond_distance
                    new_bottom_beyond_distance = bottom_beyond_distance
                
                RBQLog.log_debug(
                    f"[createRowData] 处理第{sm}行: "
                    f"rowLayoutDirection={row_layout_direction}, "
                    f"width={width}, height={height}, valid_height={valid_height}, "
                    f"topBeyondDistance={top_beyond_distance}, bottomBeyondDistance={bottom_beyond_distance}, "
                    f"new_topBeyondDistance={new_top_beyond_distance}, new_bottomBeyondDistance={new_bottom_beyond_distance}"
                )
                
                # 清除背景
                if clear_background:
                    new_image = OpenCVUtils.deep_clear_background(new_image)
                
                # 获取像素数据  一维数组
                # pixels: NDArray[np.uint32] = np.frombuffer(
                #     new_image.convert("RGBA").tobytes(), dtype=np.uint32
                # )

                # image_array = np.array(new_image, dtype=np.uint8)  # 将图片转为numpy数组
                # _height, _width, _channels = image_array.shape    # 添加 _ 前缀
                # for y in range(_height):
                #     for x in range(_width):
                #         pixel = image_array[y, x]
                #         if _channels == 1:
                #             # 灰度图（单通道）
                #             gray = pixel[0]
                #             RBQLog.log(f"像素 (y={y}, x={x}): 灰度={gray}")
                #         elif _channels == 3:
                #             # RGB（三通道）
                #             r, g, b = pixel
                #             RBQLog.log(f"像素 (y={y}, x={x}): R={r}, G={g}, B={b}")
                #         elif _channels == 4:
                #             # RGBA（四通道）
                #             r, g, b, a = pixel
                #             RBQLog.log(f"像素 (y={y}, x={x}): R={r}, G={g}, B={b}, A={a}")
                #         else:
                #             # 其他情况（如多通道特殊图像）
                #             RBQLog.log(f"像素 (y={y}, x={x}): 通道数据={pixel}")

                rgba_array:np.ndarray = np.array(new_image.convert("RGBA"), dtype=np.uint8)
                # 轮训打印rgba_array
                # _height, _width, _ = rgba_array.shape
                # for y in range(_height):
                #     row = rgba_array[y]  # shape: (width, 4)
                #     for x in range(_width):
                #         r, g, b, a = row[x]
                #         RBQLog.log(f"rgba_array (y={y}, x={x}): R={r}, G={g}, B={b}, A={a}")

                #计算有效范围
                start_row = int(new_top_beyond_distance)
                end_row = start_row + int(valid_height)
                # 有效像素区域
                valid_rgba_array: np.ndarray = rgba_array[start_row:end_row, :, :]
                _height, _width, _ = valid_rgba_array.shape
                RBQLog.log(f"valid_rgba_array shape: {_height}, {_width}, {_}")
                # 打印 valid_rgba_array里边的值
                # for y in range(valid_height):
                #     for x in range(new_width):
                #         r, g, b, a = valid_rgba_array[y, x]
                #         RBQLog.log(f"valid_rgba_array (y={y}, x={x}): R={r}, G={g}, B={b}, A={a}")
                
                # 如果是连续图像，则需要进行误差传递
                if row_data_last_row_errors is not None:
                    row_data_initial_errors = row_data_last_row_errors
                else:
                    row_data_initial_errors = None
                row_data_last_row_errors = None
                
                binary_pixels:np.ndarray = np.zeros(_width*_height, dtype=np.int32)

                if is_contiguous_cropped_images and row_data_last_row_errors is None:
                    row_data_last_row_errors = np.zeros(_width, dtype=np.int32) 
                MxImageUtils.merge_bitmap_to_gray_floyd_dithering_binary(
                    valid_rgba_array, binary_pixels, _width, _height, 
                    threshold, dithering, compress, row_data_initial_errors, row_data_last_row_errors
                )
                
                d72:np.ndarray = np.zeros(_width*72, dtype=np.uint8)
                MxImageUtils.format_binary_69_to_data_72_by_col(
                    binary_pixels, d72, _width, _height
                )
                
                # 压缩数据
                if compress:
                    data72:NDArray[np.uint8] = Compress.compress_row_data(d72)
                else:
                    data72 = d72
                
                # 保存数据到缓存文件
                data_path: str = FileManager.save_data_to_cache(data72)
                
                # 创建RowData对象
                row_data = RowData()
                row_data.row_data_path = data_path
                row_data.data_length = len(data72)
                row_data.compress = compress
                
                row_data_arr.append(row_data)
                
                # 处理模拟图像的误差传递
                # if is_contiguous_cropped_images:
                #     if simulation_last_row_errors is not None:
                #         simulation_initial_errors = simulation_last_row_errors
                #     simulation_last_row_errors = None
                
                # 生成模拟图像
                if is_simulation:
                    image_path = MxImageUtils.image_simulation_by_binary_with_save(
                        binary_pixels, _width, _height,
                        compress, row_layout_direction
                    )
                    image_paths.append(image_path)
                
                RBQLog.log_debug(
                    f"完成第{sm}行数据处理; 图片大小:{new_image.size}; "
                    f"图片路径:{image_path if is_simulation else 'None'}; "
                    f"dataLength:{row_data.data_length}"
                )
            
            # 处理缩略图模拟
            thumb_path:Optional[str] = None
            if thumb_to_simulation and multi_row_image.thumb_path:
                origin_thumb:Optional[Image] = FileManager.load_image(multi_row_image.thumb_path)
                if origin_thumb:
                    thumb_path = MxImageUtils.merge_simulate_image_by_image(
                        image=origin_thumb,
                        threshold=threshold,
                        clear_background=clear_background,
                        dithering=dithering,
                        compress=compress,
                        top_beyond_distance=0,
                        bottom_beyond_distance=0,
                        is_zoom_to_552=False,
                        initial_errors=None
                    )
            
            # 创建MultiRowData对象
            multi_row_data = MultiRowData(
                row_data_arr=row_data_arr,
                image_paths=image_paths,
                thumb_path=thumb_path,
                compress=compress,
                row_layout_direction=row_layout_direction
            )
            
            return multi_row_data
            
        except Exception as e:
            RBQLog.log_error(f"处理多行数据时发生错误: {e}")
            return None
    
    @classmethod
    def better_merge_bitmap_to_multi_row_data_async(
        cls,
        multi_row_image: MultiRowImage,
        threshold: int = 128,
        clear_background: bool = False,
        dithering: bool = True,
        compress: bool = True,
        flip_horizontally: bool = False,
        is_simulation: bool = False,
        thumb_to_simulation: bool = False,
        on_start: Optional[Callable[[], None]] = None,
        on_complete: Optional[Callable[[MultiRowData], None]] = None,
        on_error: Optional[Callable[[], None]] = None
    ) -> None:
        """
        异步将位图转换为多行数据（优化合并模式）
        
        Args:
            multi_row_image: 多行图像对象
            threshold: 二值化阈值 (0-255)
            clear_background: 是否清除背景
            dithering: 是否使用Floyd-Steinberg抖动
            compress: 是否压缩数据
            flip_horizontally: 是否水平翻转
            is_simulation: 是否生成模拟图像
            thumb_to_simulation: 是否对缩略图进行模拟
            on_start: 开始处理回调
            on_complete: 完成处理回调
            on_error: 错误处理回调
        """
        if not multi_row_image:
            if on_error:
                DispatchMainEvent.post(on_error)
            return
        
        def process_task():
            try:
                if on_start:
                    DispatchMainEvent.post(on_start)
                
                result = cls.better_merge_bitmap_to_multi_row_data(
                    multi_row_image=multi_row_image,
                    threshold=threshold,
                    clear_background=clear_background,
                    dithering=dithering,
                    compress=compress,
                    flip_horizontally=flip_horizontally,
                    is_simulation=is_simulation,
                    thumb_to_simulation=thumb_to_simulation
                )
                
                if result and on_complete:
                    DispatchMainEvent.post(on_complete, result)
                elif not result and on_error:
                    DispatchMainEvent.post(on_error)
                    
            except Exception as e:
                RBQLog.log_error(f"异步处理多行数据时发生错误: {e}")
                if on_error:
                    DispatchMainEvent.post(on_error)
        
        # 在线程池中执行处理任务
        thread = threading.Thread(target=process_task)
        thread.start()
    
    @classmethod
    def better_merge_bitmap_to_multi_row_data(
        cls,
        multi_row_image: MultiRowImage,
        threshold: int = 128,
        clear_background: bool = False,
        dithering: bool = True,
        compress: bool = True,
        flip_horizontally: bool = False,
        is_simulation: bool = False,
        thumb_to_simulation: bool = False
    ) -> Optional[MultiRowData]:
        """
        将位图转换为多行数据（优化合并模式）
        
        优化合并模式直接从位图转换为72字节数据格式，性能更优。
        
        Args:
            multi_row_image: 多行图像对象
            threshold: 二值化阈值 (0-255)
            clear_background: 是否清除背景
            dithering: 是否使用Floyd-Steinberg抖动
            compress: 是否压缩数据
            flip_horizontally: 是否水平翻转
            is_simulation: 是否生成模拟图像
            thumb_to_simulation: 是否对缩略图进行模拟
            
        Returns:
            MultiRowData对象，失败时返回None
        """
        if not multi_row_image or not multi_row_image.row_images:
            return None
        
        try:
            row_layout_direction: RowLayoutDirection = multi_row_image.row_layout_direction
            is_contiguous_cropped_images: bool = multi_row_image.is_contiguous_cropped_images
            row_data_arr: List[RowData] = []
            image_paths: List[str] = [] if is_simulation else None
            row_image_arr: List[RowImage] = multi_row_image.row_images
            
            # Floyd-Steinberg抖动的误差传递
            row_data_initial_errors: Optional[NDArray[np.int32]] = None
            row_data_last_row_errors: Optional[NDArray[np.int32]] = None
            # simulation_initial_errors: Optional[NDArray[np.int32]] = None
            # simulation_last_row_errors: Optional[NDArray[np.int32]] = None
            
            for sm, row_image in enumerate(row_image_arr):
                origin_path = row_image.image_path
                if not origin_path:
                    return None
                
                # 根据布局方向加载和旋转图像
                loaded_image: Image.Image = FileManager.load_image(origin_path)
                if not loaded_image:
                    # 如果加载图像失败，跳过当前行
                    continue
                
                # 水平翻转（如果需要）
                if flip_horizontally:
                    loaded_image = loaded_image.transpose(Image.FLIP_LEFT_RIGHT)
                
                if row_layout_direction == RowLayoutDirection.HORIZONTAL:
                    # image = MxImageUtils.rotated_image_with_graphics_by_radians(
                    #     loaded_image,
                    #     math.pi / 2
                    # )
                    image = loaded_image.rotate(90, expand=True)
                else:
                    image = loaded_image
                
                if not image:
                    #  如果加载图像失败，跳过当前行
                    continue
                
                top_beyond_distance = row_image.top_beyond_distance
                bottom_beyond_distance = row_image.bottom_beyond_distance
                
                width, height = image.size
                valid_height = height - top_beyond_distance - bottom_beyond_distance
                
                new_image: Image.Image = None
                # 如果有效高度不为552，则缩放到552
                if valid_height != cls.PRINT_HEAD_WIDTH:
                    scale = cls.PRINT_HEAD_WIDTH / valid_height
                    new_top_beyond_distance = top_beyond_distance * scale
                    new_bottom_beyond_distance = bottom_beyond_distance * scale
                    temp_width = math.floor(width * scale)
                    temp_height = cls.PRINT_HEAD_WIDTH + new_top_beyond_distance + new_bottom_beyond_distance
                    
                    new_image = image.resize((int(temp_width), int(temp_height)), Image.LANCZOS)
                    valid_height = cls.PRINT_HEAD_WIDTH
                    # new_width = temp_width
                    # new_height = temp_height
                else:
                    new_image = image
                    # new_width = math.floor(width)
                    # new_height = height
                    new_top_beyond_distance = top_beyond_distance
                    new_bottom_beyond_distance = bottom_beyond_distance
                
                RBQLog.log_debug(
                    f"[createRowData] 处理第{sm}行: "
                    f"rowLayoutDirection={row_layout_direction}, "
                    f"width={width}, height={height}, valid_height={valid_height}, "
                    f"topBeyondDistance={top_beyond_distance}, bottomBeyondDistance={bottom_beyond_distance}, "
                    f"new_topBeyondDistance={new_top_beyond_distance}, new_bottomBeyondDistance={new_bottom_beyond_distance}"
                )
                
                # 清除背景
                if clear_background:
                    new_image: Image.Image = OpenCVUtils.deep_clear_background(new_image)
                
                # 获取像素数据  一维数组
                # pixels: NDArray[np.uint32] = np.frombuffer(
                #     new_image.convert("RGBA").tobytes(), dtype=np.uint32
                # )

                # image_array = np.array(new_image, dtype=np.uint8)  # 将图片转为numpy数组
                # _height, _width, _channels = image_array.shape    # 添加 _ 前缀
                # for y in range(_height):
                #     for x in range(_width):
                #         pixel = image_array[y, x]
                #         if _channels == 1:
                #             # 灰度图（单通道）
                #             gray = pixel[0]
                #             RBQLog.log(f"像素 (y={y}, x={x}): 灰度={gray}")
                #         elif _channels == 3:
                #             # RGB（三通道）
                #             r, g, b = pixel
                #             RBQLog.log(f"像素 (y={y}, x={x}): R={r}, G={g}, B={b}")
                #         elif _channels == 4:
                #             # RGBA（四通道）
                #             r, g, b, a = pixel
                #             RBQLog.log(f"像素 (y={y}, x={x}): R={r}, G={g}, B={b}, A={a}")
                #         else:
                #             # 其他情况（如多通道特殊图像）
                #             RBQLog.log(f"像素 (y={y}, x={x}): 通道数据={pixel}")

                rgba_array:np.ndarray = np.array(new_image.convert("RGBA"), dtype=np.uint8)
                # 轮训打印rgba_array
                # _height, _width, _ = rgba_array.shape
                # for y in range(_height):
                #     row = rgba_array[y]  # shape: (width, 4)
                #     for x in range(_width):
                #         r, g, b, a = row[x]
                #         RBQLog.log(f"rgba_array (y={y}, x={x}): R={r}, G={g}, B={b}, A={a}")

                #计算有效范围
                start_row = int(new_top_beyond_distance)
                end_row = start_row + int(valid_height)
                # 有效像素区域
                valid_rgba_array: np.ndarray = rgba_array[start_row:end_row, :, :]
                _height, _width, _ = valid_rgba_array.shape
                RBQLog.log(f"valid_rgba_array shape: {_height}, {_width}, {_}")
                # 打印 valid_rgba_array里边的值
                # for y in range(valid_height):
                #     for x in range(new_width):
                #         r, g, b, a = valid_rgba_array[y, x]
                #         RBQLog.log(f"valid_rgba_array (y={y}, x={x}): R={r}, G={g}, B={b}, A={a}")
                
                # 如果是连续图像，则需要进行误差传递
                if row_data_last_row_errors is not None:
                    row_data_initial_errors = row_data_last_row_errors
                else:
                    row_data_initial_errors = None
                row_data_last_row_errors = None
                
                binary_pixels:np.ndarray = np.zeros(_width*_height, dtype=np.int32)
                d72:np.ndarray = np.zeros(_width*72, dtype=np.uint8)

                # 使用优化合并模式：直接从位图转换为72字节数据
                if is_contiguous_cropped_images and row_data_last_row_errors is None:
                    row_data_last_row_errors = np.zeros(_width*_height, dtype=np.int32)

                MxImageUtils.better_merge_bitmap_to_data72(
                    valid_rgba_array, binary_pixels, d72, _width, _height, 
                    threshold, dithering, compress, row_data_initial_errors, row_data_last_row_errors
                )
                
                # 压缩数据
                if compress:
                    data72 = Compress.compress_row_data(d72)
                else:
                    data72 = d72

                # 保存数据到缓存文件
                data_path = FileManager.save_data_to_cache(data72)
                
                # 创建RowData对象
                row_data = RowData()
                row_data.row_data_path = data_path
                row_data.data_length = len(data72)
                row_data.compress = compress
                
                row_data_arr.append(row_data)
                
                # 处理模拟图像的误差传递
                # if is_contiguous_cropped_images:
                #     if simulation_last_row_errors is not None:
                #         simulation_initial_errors = simulation_last_row_errors
                #     simulation_last_row_errors = None
                
                # 生成模拟图像
                if is_simulation:
                    image_path = MxImageUtils.image_simulation_by_binary_with_save(
                        binary_pixels, _width, _height,
                        compress, row_layout_direction
                    )
                    image_paths.append(image_path)
                
                RBQLog.log_debug(
                    f"完成第{sm}行数据处理; 图片大小:{new_image.size}; "
                    f"图片路径:{image_path if is_simulation else 'None'}; "
                    f"dataLength:{row_data.data_length}"
                )
            
            # 处理缩略图模拟
            thumb_path:Optional[str] = None
            if thumb_to_simulation and multi_row_image.thumb_path:
                origin_thumb:Optional[Image] = FileManager.load_image(multi_row_image.thumb_path)
                if origin_thumb:
                    thumb_path = MxImageUtils.merge_simulate_image_by_image(
                        image=origin_thumb,
                        threshold=threshold,
                        clear_background=clear_background,
                        dithering=dithering,
                        compress=compress,
                        top_beyond_distance=0,
                        bottom_beyond_distance=0,
                        is_zoom_to_552=False,
                        initial_errors=None
                    )
            
            # 创建MultiRowData对象
            multi_row_data = MultiRowData(
                row_data_arr=row_data_arr,
                image_paths=image_paths,
                thumb_path=thumb_path,
                compress=compress,
                row_layout_direction=row_layout_direction
            )
            
            return multi_row_data
            
        except Exception as e:
            RBQLog.log_error(f"处理多行数据时发生错误: {e}")
            return None