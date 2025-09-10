# -*- coding: utf-8 -*-
"""
LogoDataFactory - Logo数据工厂类

对应Objective-C中的LogoDataFactory类，用于将LogoImage转换为LogoData。
提供图像处理、二值化、数据转换等功能。

作者: RBQ
日期: 2025
"""

import threading
from typing import Optional, Callable
import numpy as np
from PIL import Image
from sdk.python.mxSdk.utils.dispatch_main_event import DispatchMainEvent
from ..data.logo_image import LogoImage
from ..data.logo_data import LogoData
from ..utils.mx_file_manager import FileManager
from ..utils.mx_image_utils import MxImageUtils
from ..utils.rbq_log import RBQLog
from ..utils.dispatch_main_event import DispatchMainEvent

class LogoDataFactory:
    """
    Logo数据工厂类
    
    用于将LogoImage转换为LogoData，提供图像处理、二值化、数据转换等功能。
    支持异步和同步两种处理方式。
    
    主要功能:
    - 将Logo图像转换为打印数据
    - 图像预处理（缩放、居中、背景填充）
    - 灰度转换和Floyd-Steinberg抖动
    - 二值化处理
    - 数据格式转换
    """
    
    # 目标图像尺寸常量
    TARGET_WIDTH = 2000
    TARGET_HEIGHT = 552
    
    @classmethod
    def logo_image_to_data_async(
        cls,
        logo_image: LogoImage,
        threshold: int,
        on_start: Optional[Callable[[], None]] = None,
        on_complete: Optional[Callable[[LogoData], None]] = None,
        on_error: Optional[Callable[[], None]] = None
    ) -> None:
        """
        异步将LogoImage转换为LogoData
        
        Args:
            logo_image: Logo图像对象
            threshold: 二值化阈值 (0-255)
            on_start: 开始处理时的回调函数
            on_complete: 处理完成时的回调函数，参数为生成的LogoData
            on_error: 处理出错时的回调函数
        """
        def process_task():
            try:
                # 调用开始回调
                if on_start:
                    DispatchMainEvent.post(on_start)
                
                # 执行转换
                logo_data = cls.logo_image_to_data(logo_image, threshold)
                
                if not logo_data:
                    if on_error:
                        DispatchMainEvent.post(on_error)
                    return
                
                # 调用完成回调
                if on_complete:
                    DispatchMainEvent.post(on_complete, logo_data)
                    
            except Exception as e:
                RBQLog.log_error(f"LogoDataFactory异步处理出错: {e}")
                if on_error:
                    DispatchMainEvent.post(on_error)
        
        # 在后台线程中执行处理
        thread = threading.Thread(target=process_task)
        thread.start()
    
    @classmethod
    def logo_image_to_data(cls, logo_image: LogoImage, threshold: int) -> Optional[LogoData]:
        """
        同步将LogoImage转换为LogoData
        
        Args:
            logo_image: Logo图像对象
            threshold: 二值化阈值 (0-255)
            
        Returns:
            转换后的LogoData对象，失败时返回None
        """
        if not logo_image or not logo_image.image_path:
            RBQLog.log_error("LogoImage或图像路径为空")
            return None
        
        try:
            # 加载图像
            image = FileManager.load_image(logo_image.image_path)
            if not image:
                RBQLog.log_error(f"无法加载图像: {logo_image.image_path}")
                return None
            
            width, height = image.size
            RBQLog.log_debug(f"原始图像尺寸: {width}x{height}")
            
            # 如果图像尺寸不是目标尺寸，进行预处理
            if width != cls.TARGET_WIDTH or height != cls.TARGET_HEIGHT:
                image = cls._process_image(image)
                width, height = image.size
                RBQLog.log_debug(f"处理后图像尺寸: {width}x{height}")
            
            # 转换为像素数组
            pixels = np.array(image.convert("RGBA"), dtype=np.uint8)
            
            # 转换为灰度
            gray_pixels:np.ndarray = np.zeros(width * height, dtype=np.int32)
            MxImageUtils.convert_ndarray_rgb_to_gray(pixels, gray_pixels)
            
            initial_errors: np.ndarray = None
            last_row_errors: np.ndarray = None
            # Floyd-Steinberg抖动
            MxImageUtils.format_gray_to_floyd_dithering(gray_pixels, width, height, threshold, initial_errors, last_row_errors)
            
            # 灰度转二值化
            binary_pixels:np.ndarray = np.zeros(width * height, dtype=np.int32)
            MxImageUtils.gray_to_binary(
                    gray_pixels, binary_pixels, width, height, threshold
            )
            
            data72:np.ndarray = np.zeros(width*72, dtype=np.uint8)
            # 转换为72字节数据格式
            MxImageUtils.format_binary_69_to_data_72_by_col(
                binary_pixels,data72, width, height
            )
            
            # 保存数据到缓存文件
            data_path = FileManager.save_data_to_cache(data72)
            
            # 生成模拟图像（保存处理后的图像到临时文件）
            simulation_image:Image.Image = MxImageUtils.image_simulation_by_binary(
                binary_pixels, width, height
            )
            RBQLog.log_debug(f"模拟图像尺寸: {simulation_image.size}")
            image_path = FileManager.save_image_to_cache(simulation_image)
            
            # 创建LogoData对象
            logo_data = LogoData(
                data_path=data_path,
                data_length=len(data72),
                image_path=image_path
            )
            
            return logo_data
            
        except Exception as e:
            RBQLog.log_error(f"LogoImage转换为LogoData失败: {e}")
            return None
    
    @classmethod
    def merge_logo_image_to_data_async(
        cls,
        logo_image: LogoImage,
        threshold: int,
        on_start: Optional[Callable[[], None]] = None,
        on_complete: Optional[Callable[[LogoData], None]] = None,
        on_error: Optional[Callable[[], None]] = None
    ) -> None:
        """
        异步将LogoImage转换为LogoData（合并模式）
        
        Args:
            logo_image: Logo图像对象
            threshold: 二值化阈值 (0-255)
            on_start: 开始处理时的回调函数
            on_complete: 处理完成时的回调函数，参数为生成的LogoData
            on_error: 处理出错时的回调函数
        """
        
        def process_task():
            try:
                # 调用开始回调
                if on_start:
                    DispatchMainEvent.post(on_start)
                
                # 执行转换
                logo_data = cls.merge_logo_image_to_data(logo_image, threshold)
                
                if not logo_data:
                    if on_error:
                        DispatchMainEvent.post(on_error)
                    return
                
                # 调用完成回调
                if on_complete:
                    DispatchMainEvent.post(on_complete, logo_data)
                    
            except Exception as e:
                RBQLog.log_error(f"LogoDataFactory合并模式异步处理出错: {e}")
                if on_error:
                    DispatchMainEvent.post(on_error)
        
        # 在后台线程中执行处理
        thread = threading.Thread(target=process_task)
        thread.start()
    
    @classmethod
    def merge_logo_image_to_data(cls, logo_image: LogoImage, threshold: int) -> Optional[LogoData]:
        """
        同步将LogoImage转换为LogoData（合并模式）
        
        使用合并的位图处理方式，一次性完成灰度转换、抖动和二值化。
        
        Args:
            logo_image: Logo图像对象
            threshold: 二值化阈值 (0-255)
            
        Returns:
            转换后的LogoData对象，失败时返回None
        """
        if not logo_image or not logo_image.image_path:
            RBQLog.log_error("LogoImage或图像路径为空")
            return None
        
        try:
            # 加载图像
            image:Image.Image = FileManager.load_image(logo_image.image_path)
            if image is None:
                RBQLog.log_error(f"无法加载图像: {logo_image.image_path}")
                return None
            
            width, height = image.size
            RBQLog.log_debug(f"原始图像尺寸: {width}x{height}")
            
            # 如果图像尺寸不是目标尺寸，进行预处理
            if width != cls.TARGET_WIDTH or height != cls.TARGET_HEIGHT:
                image = cls._process_image(image)
                width, height = image.size
                RBQLog.log_debug(f"处理后图像尺寸: {width}x{height}")
            
            # 转换为像素数组
            pixels = np.array(image.convert('RGBA'), dtype=np.uint8)
            
            # 使用合并的位图处理方式
            binary:np.ndarray = np.zeros(width * height, dtype=np.int32)
            MxImageUtils.merge_bitmap_to_gray_floyd_dithering_binary(
                pixels,binary, width, height, threshold, dithering=True, compress=False
            )
            
            # 格式化为72字节数据
            data72:np.ndarray = np.zeros(width*72, dtype=np.uint8)
            MxImageUtils.format_binary_69_to_data_72_by_col(binary,data72, width, height)
            
            # 保存数据到缓存文件
            data_path = FileManager.save_data_to_cache(data72)
            
            # 生成模拟图像（保存处理后的图像到临时文件）
            simulation_image:Image.Image = MxImageUtils.image_simulation_by_binary(
                binary, width, height
            )
            image_path = FileManager.save_image_to_cache(simulation_image)
            
            # 创建LogoData对象
            logo_data:LogoData = LogoData(
                data_path=data_path,
                data_length=len(data72),
                image_path=image_path
            )
            
            return logo_data
            
        except Exception as e:
            RBQLog.log_error(f"LogoImage合并模式转换为LogoData失败: {e}")
            return None
    
    @classmethod
    def _process_image(cls, input_image: Image.Image) -> Image.Image:
        """
        处理图像到目标尺寸
        
        将输入图像处理为2000x552的目标尺寸，保持纵横比并居中显示。
        如果图像小于目标尺寸，直接居中；如果大于目标尺寸，等比缩放后居中。
        
        Args:
            input_image: 输入的PIL图像对象
            
        Returns:
            处理后的PIL图像对象
        """
        target_width = cls.TARGET_WIDTH
        target_height = cls.TARGET_HEIGHT
        
        # 创建白色背景
        output_image:Image.Image = Image.new('RGB', (target_width, target_height), 'white')
        
        input_width, input_height = input_image.size
        
        if input_width <= target_width and input_height <= target_height:
            # 图像比目标尺寸小，直接居中显示
            scaled_image = input_image
            scaled_width = input_width
            scaled_height = input_height
        else:
            # 图像比目标尺寸大，进行等比缩放
            width_ratio = target_width / input_width
            height_ratio = target_height / input_height
            scale = min(width_ratio, height_ratio)  # 保持纵横比
            
            scaled_width = round(input_width * scale)
            scaled_height = round(input_height * scale)
            
            # 缩放图像
            scaled_image = input_image.resize(
                (scaled_width, scaled_height),
                Image.Resampling.LANCZOS
            )
        
        # 计算居中位置
        left = (target_width - scaled_width) // 2
        top = (target_height - scaled_height) // 2
        
        # 将缩放后的图像粘贴到白色背景的中心位置
        if scaled_image.mode != 'RGB':
            scaled_image = scaled_image.convert('RGB')
        
        output_image.paste(scaled_image, (left, top))
        
        return output_image