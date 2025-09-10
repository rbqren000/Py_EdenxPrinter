#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileManager - 文件管理工具类

提供文件和数据的保存、加载、管理功能。
适用于PC端应用，不包含移动端特有的倍图概念。

作者: RBQ
日期: 2025
"""

import os
import tempfile
import shutil
from typing import Optional, List
from PIL import Image
import numpy as np
from numpy.typing import NDArray
import uuid
import time
from .rbq_log import RBQLog


class FileManager:
    """
    文件管理工具类
    
    提供文件和数据的保存、加载、管理功能。
    专为PC端应用设计，简化了移动端特有的功能。
    """
    
    # 缓存目录路径
    _cache_directory: Optional[str] = None
    _data_cache_directory: Optional[str] = None
    _image_cache_directory: Optional[str] = None
    _json_cache_directory: Optional[str] = None
    _docs_cache_directory: Optional[str] = None
    _docs_saved_directory: Optional[str] = None
    _mx_cache_files_directory: Optional[str] = None
    _font_saved_files_directory: Optional[str] = None
    _image_sqlite_directory: Optional[str] = None
    
    # 缓存文件名常量
    IMAGE_CACHE_FILE = ".imageCacheFile"
    IMAGE_SQLITE_FILE = ".imageSqliteFile"
    JSON_CACHE_FILE = ".JsonCacheFile"
    DATA_CACHE_FILE = ".dataCacheFile"
    DOCS_CACHE_FILE = ".docsCacheFile"
    DOCS_SAVED_FILE = ".docsSavedFile"
    MX_CACHE_FILES = ".mxCacheFiles"
    FONT_SAVED_FILES = ".fontSavedFiles"
    MX_MAIN_JSON_NAME = "mx_main_json.txt"
    
    @classmethod
    def get_cache_directory(cls) -> str:
        """获取缓存目录路径
        
        Returns:
            缓存目录路径
        """
        if cls._cache_directory is None:
            # 创建应用专用的缓存目录
            cache_root = tempfile.gettempdir()
            cls._cache_directory = os.path.join(cache_root, "pyMxSdk_cache")
            os.makedirs(cls._cache_directory, exist_ok=True)
        
        return cls._cache_directory
    
    @classmethod
    def get_data_cache_directory(cls) -> str:
        """获取数据缓存目录路径
        
        Returns:
            数据缓存目录路径
        """
        if cls._data_cache_directory is None:
            cls._data_cache_directory = os.path.join(cls.get_cache_directory(), "data")
            os.makedirs(cls._data_cache_directory, exist_ok=True)
        
        return cls._data_cache_directory
    
    @classmethod
    def get_image_cache_directory(cls) -> str:
        """获取图像缓存目录路径
        
        Returns:
            图像缓存目录路径
        """
        if cls._image_cache_directory is None:
            cls._image_cache_directory = os.path.join(cls.get_cache_directory(), "images")
            os.makedirs(cls._image_cache_directory, exist_ok=True)
        
        return cls._image_cache_directory
    
    @classmethod
    def get_json_cache_directory(cls) -> str:
        """获取JSON缓存目录路径
        
        Returns:
            JSON缓存目录路径
        """
        if cls._json_cache_directory is None:
            cls._json_cache_directory = os.path.join(cls.get_cache_directory(), "json")
            os.makedirs(cls._json_cache_directory, exist_ok=True)
        
        return cls._json_cache_directory
    
    @classmethod
    def get_docs_cache_directory(cls) -> str:
        """获取文档缓存目录路径
        
        Returns:
            文档缓存目录路径
        """
        if cls._docs_cache_directory is None:
            cls._docs_cache_directory = os.path.join(cls.get_cache_directory(), "docs_cache")
            os.makedirs(cls._docs_cache_directory, exist_ok=True)
        
        return cls._docs_cache_directory
    
    @classmethod
    def get_docs_saved_directory(cls) -> str:
        """获取文档保存目录路径
        
        Returns:
            文档保存目录路径
        """
        if cls._docs_saved_directory is None:
            cls._docs_saved_directory = os.path.join(cls.get_cache_directory(), "docs_saved")
            os.makedirs(cls._docs_saved_directory, exist_ok=True)
        
        return cls._docs_saved_directory
    
    @classmethod
    def get_mx_cache_files_directory(cls) -> str:
        """获取模版缓存文件目录路径
        所有模版将要保存的总的路径位置，它下边还有一个文件夹，每个模版一个文件夹
        
        Returns:
            模版缓存文件目录路径
        """
        if cls._mx_cache_files_directory is None:
            cls._mx_cache_files_directory = os.path.join(cls.get_cache_directory(), "mx_cache_files")
            os.makedirs(cls._mx_cache_files_directory, exist_ok=True)
        
        return cls._mx_cache_files_directory
    
    @classmethod
    def get_font_saved_files_directory(cls) -> str:
        """获取用户字体保存目录路径
        用来保存用户字体的位置
        
        Returns:
            字体保存目录路径
        """
        if cls._font_saved_files_directory is None:
            cls._font_saved_files_directory = os.path.join(cls.get_cache_directory(), "font_saved_files")
            os.makedirs(cls._font_saved_files_directory, exist_ok=True)
        
        return cls._font_saved_files_directory
    
    @classmethod
    def get_image_sqlite_directory(cls) -> str:
        """获取图像SQLite数据库目录路径
        
        Returns:
            图像SQLite数据库目录路径
        """
        if cls._image_sqlite_directory is None:
            cls._image_sqlite_directory = os.path.join(cls.get_cache_directory(), "image_sqlite")
            os.makedirs(cls._image_sqlite_directory, exist_ok=True)
        
        return cls._image_sqlite_directory
    
    @classmethod
    def save_data_to_cache(cls, data: NDArray[np.uint8]) -> str:
        """保存数据到缓存文件
        
        Args:
            data: 要保存的数据
            
        Returns:
            保存的文件路径
        """
        try:
            # 生成唯一文件名
            filename = f"data_{uuid.uuid4().hex}_{int(time.time())}.dat"
            file_path = os.path.join(cls.get_data_cache_directory(), filename)
            
            # 保存数据
            with open(file_path, 'wb') as f:
                f.write(data)
            
            RBQLog.log_debug(f"数据已保存到: {file_path}, 大小: {len(data)}字节")
            return file_path
            
        except Exception as e:
            RBQLog.log_error(f"保存数据到缓存文件失败: {e}")
            raise
    
    @classmethod
    def save_image_to_cache(cls, image: Image.Image, format: str = 'PNG') -> str:
        """保存图像到缓存
        
        Args:
            image: PIL图像对象
            format: 图像格式 (PNG, JPEG等)
            
        Returns:
            保存的文件路径
        """
        try:
            # 生成唯一文件名
            ext = format.lower()
            filename = f"image_{uuid.uuid4().hex}_{int(time.time())}.{ext}"
            file_path = os.path.join(cls.get_image_cache_directory(), filename)
            
            # 保存图像
            image.save(file_path, format=format)
            
            RBQLog.log_debug(f"图像已保存到: {file_path}, 格式: {format}")
            return file_path
            
        except Exception as e:
            RBQLog.log_error(f"保存图像到缓存失败: {e}")
            raise
    
    @classmethod
    def save_json_to_cache(cls, json_data: str, filename: Optional[str] = None) -> str:
        """保存JSON数据到缓存
        
        Args:
            json_data: JSON字符串数据
            filename: 可选的文件名，如果不提供则自动生成
            
        Returns:
            保存的文件路径
        """
        try:
            if filename is None:
                filename = f"json_{uuid.uuid4().hex}_{int(time.time())}.json"
            elif not filename.endswith('.json'):
                filename += '.json'
                
            file_path = os.path.join(cls.get_json_cache_directory(), filename)
            
            # 保存JSON数据
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            RBQLog.log_debug(f"JSON数据已保存到: {file_path}, 大小: {len(json_data)}字符")
            return file_path
            
        except Exception as e:
            RBQLog.log_error(f"保存JSON数据到缓存失败: {e}")
            raise
    
    @classmethod
    def save_docs_to_cache(cls, data: bytes, filename: Optional[str] = None) -> str:
        """保存文档到缓存目录
        
        Args:
            data: 文档数据
            filename: 可选的文件名，如果不提供则自动生成
            
        Returns:
            保存的文件路径
        """
        try:
            if filename is None:
                filename = f"doc_{uuid.uuid4().hex}_{int(time.time())}.dat"
                
            file_path = os.path.join(cls.get_docs_cache_directory(), filename)
            
            # 保存文档数据
            with open(file_path, 'wb') as f:
                f.write(data)
            
            RBQLog.log_debug(f"文档已保存到: {file_path}, 大小: {len(data)}字节")
            return file_path
            
        except Exception as e:
            RBQLog.log_error(f"保存文档到缓存失败: {e}")
            raise
    
    @classmethod
    def save_docs_to_saved_directory(cls, data: bytes, filename: Optional[str] = None) -> str:
        """保存文档到保存目录
        
        Args:
            data: 文档数据
            filename: 可选的文件名，如果不提供则自动生成
            
        Returns:
            保存的文件路径
        """
        try:
            if filename is None:
                filename = f"saved_doc_{uuid.uuid4().hex}_{int(time.time())}.dat"
                
            file_path = os.path.join(cls.get_docs_saved_directory(), filename)
            
            # 保存文档数据
            with open(file_path, 'wb') as f:
                f.write(data)
            
            RBQLog.log_debug(f"文档已保存到保存目录: {file_path}, 大小: {len(data)}字节")
            return file_path
            
        except Exception as e:
            RBQLog.log_error(f"保存文档到保存目录失败: {e}")
            raise
    
    @classmethod
    def save_font_file(cls, font_data: bytes, filename: Optional[str] = None) -> str:
        """保存字体文件
        
        Args:
            font_data: 字体文件数据
            filename: 可选的文件名，如果不提供则自动生成
            
        Returns:
            保存的文件路径
        """
        try:
            if filename is None:
                filename = f"font_{uuid.uuid4().hex}_{int(time.time())}.ttf"
            elif not any(filename.endswith(ext) for ext in ['.ttf', '.otf', '.woff', '.woff2']):
                filename += '.ttf'
                
            file_path = os.path.join(cls.get_font_saved_files_directory(), filename)
            
            # 保存字体数据
            with open(file_path, 'wb') as f:
                f.write(font_data)
            
            RBQLog.log_debug(f"字体文件已保存到: {file_path}, 大小: {len(font_data)}字节")
            return file_path
            
        except Exception as e:
            RBQLog.log_error(f"保存字体文件失败: {e}")
            raise
    
    @classmethod
    def save_mx_template(cls, template_id: str, json_data: str) -> str:
        """保存模版数据
        每个模版一个文件夹，在模版文件夹中保存主JSON文件
        
        Args:
            template_id: 模版ID
            json_data: 模版JSON数据
            
        Returns:
            保存的文件路径
        """
        try:
            # 创建模版专用目录
            template_dir = os.path.join(cls.get_mx_cache_files_directory(), template_id)
            os.makedirs(template_dir, exist_ok=True)
            
            # 保存主JSON文件
            file_path = os.path.join(template_dir, cls.MX_MAIN_JSON_NAME)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            RBQLog.log_debug(f"模版数据已保存到: {file_path}, 模版ID: {template_id}")
            return file_path
            
        except Exception as e:
            RBQLog.log_error(f"保存模版数据失败: {e}")
            raise
    
    @classmethod
    def load_data(cls, file_path: str) -> Optional[bytes]:
        """从文件加载数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件数据，如果加载失败返回None
        """
        try:
            if not os.path.exists(file_path):
                RBQLog.warning(f"文件不存在: {file_path}")
                return None
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            RBQLog.log_debug(f"从文件加载数据: {file_path}, 大小: {len(data)}字节")
            return data
            
        except Exception as e:
            RBQLog.log_error(f"从文件加载数据失败: {e}")
            return None
    
    @classmethod
    def load_image(cls, file_path: str) -> Optional[Image.Image]:
        """从文件加载图像
        
        Args:
            file_path: 图像文件路径
            
        Returns:
            PIL图像对象，如果加载失败返回None
        """
        try:
            if not os.path.exists(file_path):
                RBQLog.warning(f"图像文件不存在: {file_path}")
                return None
            
            image: Image.Image = Image.open(file_path)
            
            RBQLog.log_debug(f"从文件加载图像: {file_path}, 尺寸: {image.size}")
            return image
            
        except Exception as e:
            RBQLog.log_error(f"从文件加载图像失败: {e}")
            return None
    
    @classmethod
    def load_json(cls, file_path: str) -> Optional[str]:
        """从文件加载JSON数据
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            JSON字符串，如果加载失败返回None
        """
        try:
            if not os.path.exists(file_path):
                RBQLog.warning(f"JSON文件不存在: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = f.read()
            
            RBQLog.log_debug(f"从文件加载JSON数据: {file_path}, 大小: {len(json_data)}字符")
            return json_data
            
        except Exception as e:
            RBQLog.log_error(f"从文件加载JSON数据失败: {e}")
            return None
    
    @classmethod
    def load_docs(cls, file_path: str) -> Optional[bytes]:
        """从文件加载文档数据
        
        Args:
            file_path: 文档文件路径
            
        Returns:
            文档数据，如果加载失败返回None
        """
        try:
            if not os.path.exists(file_path):
                RBQLog.warning(f"文档文件不存在: {file_path}")
                return None
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            RBQLog.log_debug(f"从文件加载文档数据: {file_path}, 大小: {len(data)}字节")
            return data
            
        except Exception as e:
            RBQLog.log_error(f"从文件加载文档数据失败: {e}")
            return None
    
    @classmethod
    def load_font_file(cls, file_path: str) -> Optional[bytes]:
        """从文件加载字体文件数据
        
        Args:
            file_path: 字体文件路径
            
        Returns:
            字体文件数据，如果加载失败返回None
        """
        try:
            if not os.path.exists(file_path):
                RBQLog.warning(f"字体文件不存在: {file_path}")
                return None
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            RBQLog.log_debug(f"从文件加载字体数据: {file_path}, 大小: {len(data)}字节")
            return data
            
        except Exception as e:
            RBQLog.log_error(f"从文件加载字体数据失败: {e}")
            return None
    
    @classmethod
    def load_mx_template(cls, template_id: str) -> Optional[str]:
        """加载模版数据
        从模版文件夹中加载主JSON文件
        
        Args:
            template_id: 模版ID
            
        Returns:
            模版JSON数据，如果加载失败返回None
        """
        try:
            template_dir = os.path.join(cls.get_mx_cache_files_directory(), template_id)
            file_path = os.path.join(template_dir, cls.MX_MAIN_JSON_NAME)
            
            if not os.path.exists(file_path):
                RBQLog.warning(f"模版文件不存在: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = f.read()
            
            RBQLog.log_debug(f"从文件加载模版数据: {file_path}, 模版ID: {template_id}")
            return json_data
            
        except Exception as e:
            RBQLog.log_error(f"从文件加载模版数据失败: {e}")
            return None
    
    @classmethod
    def delete_file(cls, file_path: str) -> bool:
        """删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            删除成功返回True
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                RBQLog.log_debug(f"文件已删除: {file_path}")
                return True
            else:
                RBQLog.warning(f"要删除的文件不存在: {file_path}")
                return True  # 文件不存在也算删除成功
                
        except Exception as e:
            RBQLog.log_error(f"删除文件失败: {e}")
            return False
    
    @classmethod
    def clear_cache_directory(cls, directory_type: str = 'all') -> bool:
        """清理缓存目录
        
        Args:
            directory_type: 目录类型 ('all', 'data', 'images')
            
        Returns:
            清理成功返回True
        """
        try:
            directories_to_clear = []
            
            if directory_type == 'all':
                directories_to_clear = [
                    cls.get_data_cache_directory(),
                    cls.get_image_cache_directory()
                ]
            elif directory_type == 'data':
                directories_to_clear = [cls.get_data_cache_directory()]
            elif directory_type == 'images':
                directories_to_clear = [cls.get_image_cache_directory()]
            else:
                RBQLog.warning(f"未知的目录类型: {directory_type}")
                return False
            
            for directory in directories_to_clear:
                if os.path.exists(directory):
                    # 删除目录中的所有文件
                    for filename in os.listdir(directory):
                        file_path = os.path.join(directory, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    
                    RBQLog.log_debug(f"缓存目录已清理: {directory}")
            
            return True
            
        except Exception as e:
            RBQLog.log_error(f"清理缓存目录失败: {e}")
            return False
    
    @classmethod
    def get_cache_size(cls, directory_type: str = 'all') -> int:
        """获取缓存大小
        
        Args:
            directory_type: 目录类型 ('all', 'data', 'images')
            
        Returns:
            缓存大小（字节）
        """
        try:
            total_size = 0
            directories_to_check = []
            
            if directory_type == 'all':
                directories_to_check = [
                    cls.get_data_cache_directory(),
                    cls.get_image_cache_directory()
                ]
            elif directory_type == 'data':
                directories_to_check = [cls.get_data_cache_directory()]
            elif directory_type == 'images':
                directories_to_check = [cls.get_image_cache_directory()]
            else:
                return 0
            
            for directory in directories_to_check:
                if os.path.exists(directory):
                    for filename in os.listdir(directory):
                        file_path = os.path.join(directory, filename)
                        if os.path.isfile(file_path):
                            total_size += os.path.getsize(file_path)
            
            return total_size
            
        except Exception as e:
            RBQLog.log_error(f"获取缓存大小失败: {e}")
            return 0
    
    @classmethod
    def list_cache_files(cls, directory_type: str = 'all') -> List[str]:
        """列出缓存文件
        
        Args:
            directory_type: 目录类型 ('all', 'data', 'images')
            
        Returns:
            文件路径列表
        """
        try:
            files = []
            directories_to_check = []
            
            if directory_type == 'all':
                directories_to_check = [
                    cls.get_data_cache_directory(),
                    cls.get_image_cache_directory()
                ]
            elif directory_type == 'data':
                directories_to_check = [cls.get_data_cache_directory()]
            elif directory_type == 'images':
                directories_to_check = [cls.get_image_cache_directory()]
            
            for directory in directories_to_check:
                if os.path.exists(directory):
                    for filename in os.listdir(directory):
                        file_path = os.path.join(directory, filename)
                        if os.path.isfile(file_path):
                            files.append(file_path)
            
            return files
            
        except Exception as e:
            RBQLog.log_error(f"列出缓存文件失败: {e}")
            return []
    
    @classmethod
    def copy_file(cls, source_path: str, destination_path: str) -> bool:
        """复制文件
        
        Args:
            source_path: 源文件路径
            destination_path: 目标文件路径
            
        Returns:
            复制成功返回True
        """
        try:
            if not os.path.exists(source_path):
                RBQLog.warning(f"源文件不存在: {source_path}")
                return False
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # 复制文件
            shutil.copy2(source_path, destination_path)
            
            RBQLog.log_debug(f"文件已复制: {source_path} -> {destination_path}")
            return True
            
        except Exception as e:
            RBQLog.log_error(f"复制文件失败: {e}")
            return False
    
    @classmethod
    def move_file(cls, source_path: str, destination_path: str) -> bool:
        """移动文件
        
        Args:
            source_path: 源文件路径
            destination_path: 目标文件路径
            
        Returns:
            移动成功返回True
        """
        try:
            if not os.path.exists(source_path):
                RBQLog.warning(f"源文件不存在: {source_path}")
                return False
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # 移动文件
            shutil.move(source_path, destination_path)
            
            RBQLog.log_debug(f"文件已移动: {source_path} -> {destination_path}")
            return True
            
        except Exception as e:
            RBQLog.log_error(f"移动文件失败: {e}")
            return False
    
    @classmethod
    def get_file_info(cls, file_path: str) -> Optional[dict]:
        """获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文件信息的字典，如果文件不存在返回None
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            
            return {
                'path': file_path,
                'size': stat.st_size,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'accessed_time': stat.st_atime,
                'is_file': os.path.isfile(file_path),
                'is_directory': os.path.isdir(file_path)
            }
            
        except Exception as e:
            RBQLog.log_error(f"获取文件信息失败: {e}")
            return None