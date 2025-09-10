#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FilesUtils - 文件操作工具类

提供文件属性获取、文件操作等功能的工具类。
这是从Objective-C FilesUtils类移植到Python的实现。
"""

import os
import stat
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class FilesUtils:
    """文件操作工具类
    
    提供文件属性获取、文件存在性检查等功能。
    """
    
    @staticmethod
    def get_file_attributes_at_path(file_path: str) -> Optional[Dict[str, Any]]:
        """获取指定路径文件的属性信息
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            Optional[Dict[str, Any]]: 文件属性字典，如果文件不存在或出错则返回None
                包含以下键值对：
                - 'size': 文件大小（字节）
                - 'creation_date': 创建时间
                - 'modification_date': 修改时间
                - 'access_date': 访问时间
                - 'is_directory': 是否为目录
                - 'is_file': 是否为文件
                - 'permissions': 文件权限（八进制字符串）
                - 'owner': 文件所有者ID
                - 'group': 文件组ID
        """
        try:
            if not os.path.exists(file_path):
                return None
                
            file_stat = os.stat(file_path)
            
            attributes = {
                'size': file_stat.st_size,
                'creation_date': datetime.fromtimestamp(file_stat.st_ctime),
                'modification_date': datetime.fromtimestamp(file_stat.st_mtime),
                'access_date': datetime.fromtimestamp(file_stat.st_atime),
                'is_directory': stat.S_ISDIR(file_stat.st_mode),
                'is_file': stat.S_ISREG(file_stat.st_mode),
                'permissions': oct(file_stat.st_mode)[-3:],  # 获取权限的后三位
                'owner': file_stat.st_uid,
                'group': file_stat.st_gid
            }
            
            return attributes
            
        except (OSError, IOError) as e:
            # 文件访问错误
            return None
    
    @staticmethod
    def file_exists_at_path(file_path: str) -> bool:
        """检查文件是否存在
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 文件存在返回True，否则返回False
        """
        return os.path.exists(file_path)
    
    @staticmethod
    def create_directory_at_path(dir_path: str, create_intermediate: bool = True) -> bool:
        """创建目录
        
        Args:
            dir_path (str): 目录路径
            create_intermediate (bool): 是否创建中间目录，默认为True
            
        Returns:
            bool: 创建成功返回True，否则返回False
        """
        try:
            if create_intermediate:
                os.makedirs(dir_path, exist_ok=True)
            else:
                os.mkdir(dir_path)
            return True
        except (OSError, IOError):
            return False
    
    @staticmethod
    def remove_file_at_path(file_path: str) -> bool:
        """删除文件
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                return True
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
                return True
            return False
        except (OSError, IOError):
            return False
    
    @staticmethod
    def get_file_size(file_path: str) -> Optional[int]:
        """获取文件大小
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            Optional[int]: 文件大小（字节），文件不存在返回None
        """
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            return None
        except (OSError, IOError):
            return None
    
    @staticmethod
    def is_directory(path: str) -> bool:
        """检查路径是否为目录
        
        Args:
            path (str): 路径
            
        Returns:
            bool: 是目录返回True，否则返回False
        """
        return os.path.isdir(path)
    
    @staticmethod
    def is_file(path: str) -> bool:
        """检查路径是否为文件
        
        Args:
            path (str): 路径
            
        Returns:
            bool: 是文件返回True，否则返回False
        """
        return os.path.isfile(path)
    
    @staticmethod
    def get_directory_contents(dir_path: str) -> Optional[list]:
        """获取目录内容列表
        
        Args:
            dir_path (str): 目录路径
            
        Returns:
            Optional[list]: 目录内容列表，目录不存在或出错返回None
        """
        try:
            if os.path.isdir(dir_path):
                return os.listdir(dir_path)
            return None
        except (OSError, IOError):
            return None
    
    @staticmethod
    def copy_file(source_path: str, destination_path: str) -> bool:
        """复制文件
        
        Args:
            source_path (str): 源文件路径
            destination_path (str): 目标文件路径
            
        Returns:
            bool: 复制成功返回True，否则返回False
        """
        try:
            import shutil
            shutil.copy2(source_path, destination_path)
            return True
        except (OSError, IOError, shutil.Error):
            return False
    
    @staticmethod
    def move_file(source_path: str, destination_path: str) -> bool:
        """移动文件
        
        Args:
            source_path (str): 源文件路径
            destination_path (str): 目标文件路径
            
        Returns:
            bool: 移动成功返回True，否则返回False
        """
        try:
            import shutil
            shutil.move(source_path, destination_path)
            return True
        except (OSError, IOError, shutil.Error):
            return False