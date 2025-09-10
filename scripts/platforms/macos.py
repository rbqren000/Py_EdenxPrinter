import platform
import sys
import logging
import subprocess
from pathlib import Path

def get_config():
    """macOS平台配置"""
    try:
        # 系统检测
        is_universal = sys.platform == 'darwin'
        machine = platform.machine().lower()
        os_version = subprocess.check_output(['sw_vers', '-productVersion']).decode().strip()
        
        # 检查Metal支持
        metal_support = Path('/System/Library/Frameworks/Metal.framework').exists()
        
        # 编译参数
        compile_args = [
            '-O3',
            '-flto',
            '-mmacosx-version-min=11.0',
            '-fobjc-arc',
            '-fmodules'
        ]
        if metal_support:
            compile_args.append('-DMETAL_ENABLED')
        
        # 链接参数
        link_args = [
            '-arch', 'arm64',
            '-arch', 'x86_64',
            '-rpath', '@loader_path',
            '-framework', 'CoreFoundation'
        ]
        if metal_support:
            link_args.extend(['-framework', 'Metal'])
        
        # OpenCV检测 - 支持多种安装方式
        opencv_path = None
        opencv_paths = [
            '/opt/homebrew/opt/opencv',  # Apple Silicon Homebrew
            '/usr/local/opt/opencv',     # Intel Homebrew
            '/opt/local/lib',            # MacPorts
            os.environ.get('OPENCV_DIR', '') if os.environ.get('OPENCV_DIR') else None
        ]
        
        # 首先尝试brew命令
        try:
            opencv_path = subprocess.check_output(['brew', '--prefix', 'opencv'], 
                                                stderr=subprocess.DEVNULL).decode().strip()
        except:
            # 如果brew失败，尝试预定义路径
            for path in opencv_paths:
                if path and Path(path).exists():
                    opencv_path = path
                    break
        
        if not opencv_path:
            logging.warning("未检测到OpenCV，将使用pip安装的opencv-python")
        
        return {
            'include_dirs': [f'{opencv_path}/include'] if opencv_path else [],
            'extra_compile_args': compile_args,
            'extra_link_args': link_args,
            'libraries': ['opencv2'] if opencv_path else [],
            'library_dirs': [f'{opencv_path}/lib'] if opencv_path else [],
            'frameworks': ['CoreVideo', 'CoreImage']
        }
    except Exception as e:
        logging.error(f"macOS配置错误: {str(e)}")
        return {
            'include_dirs': [],
            'extra_compile_args': ['-O2'],
            'extra_link_args': [],
            'libraries': [],
            'library_dirs': []
        }