import platform
import subprocess
import logging
from pathlib import Path

def get_config():
    """Linux平台配置"""
    try:
        # 架构检测
        machine = platform.machine().lower()
        is_arm = 'aarch64' in machine or 'arm' in machine
        
        # 检查OpenCV
        try:
            opencv_ver = subprocess.check_output(['pkg-config', '--modversion', 'opencv4'], 
                                              stderr=subprocess.DEVNULL).decode().strip()
        except:
            opencv_ver = None
            logging.warning("未检测到OpenCV4开发包")

        # 编译参数
        compile_args = [
            '-fPIC',
            '-O3',
            '-fopenmp'
        ]
        
        # 只在x86_64架构添加AVX支持
        if machine in ['x86_64', 'amd64'] and not is_arm:
            compile_args.append('-mavx2')
        
        # 链接参数
        link_args = [
            '-fopenmp',
            '-Wl,--as-needed'
        ]
        
        return {
            'include_dirs': ['/usr/local/include/opencv4'] if opencv_ver else [],
            'extra_compile_args': [arg for arg in compile_args if arg],
            'extra_link_args': link_args,
            'libraries': ['opencv_core', 'opencv_highgui'] if opencv_ver else [],
            'library_dirs': ['/usr/local/lib']
        }
    except Exception as e:
        logging.error(f"Linux配置错误: {str(e)}")
        return {
            'include_dirs': [],
            'extra_compile_args': ['-fPIC'],
            'extra_link_args': [],
            'libraries': [],
            'library_dirs': []
        }