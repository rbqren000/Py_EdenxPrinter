import os
import platform
import sys
import logging
from pathlib import Path

def get_config():
    """Windows平台配置"""
    try:
        # 架构检测
        is_64bit = platform.architecture()[0] == '64bit'
        python_version = f"{sys.version_info.major}{sys.version_info.minor}"
        
        # OpenCV路径检测 - 支持多种安装方式
        opencv_paths = [
            Path("C:/opencv/build/x64" if is_64bit else "C:/opencv/build/x86"),
            Path("C:/vcpkg/installed/x64-windows" if is_64bit else "C:/vcpkg/installed/x86-windows"),
            Path(os.environ.get('OPENCV_DIR', '')) if os.environ.get('OPENCV_DIR') else None
        ]
        
        opencv_path = None
        for path in opencv_paths:
            if path and path.exists():
                opencv_path = path
                break
        
        if not opencv_path:
            logging.warning("未找到本地OpenCV安装路径，将依赖pip安装的opencv-python。")
            # 当使用pip的opencv-python时，通常不需要手动指定include和lib目录
            return {
                'include_dirs': [],
                'extra_compile_args': ['/Ox', '/GL', '/MP'],
                'extra_link_args': ['/LTCG', '/DLL'],
                'libraries': [],
                'library_dirs': []
            }
        
        # 编译参数
        compile_args = [
            '/Ox', '/GL', '/MP',  # 优化和多核编译
            f'/DPYTHON_VERSION={python_version}'
        ]
        
        # 链接参数
        link_args = [
            '/LTCG',  # 链接时代码生成
            '/DLL'    # 生成DLL
        ]
        
        return {
            'include_dirs': [str(opencv_path / "include")],
            'extra_compile_args': compile_args,
            'extra_link_args': link_args,
            'libraries': ['opencv_world455'], # 注意：版本号可能需要根据实际情况调整
            'library_dirs': [str(opencv_path / "lib")]
        }
    except Exception as e:
        logging.error(f"Windows配置时发生未知错误: {str(e)}", exc_info=True)
        # 返回一个安全的默认值
        return {
            'include_dirs': [],
            'extra_compile_args': ['/Ox', '/GL', '/MP'],
            'extra_link_args': ['/LTCG', '/DLL'],
            'libraries': [],
            'library_dirs': []
        }