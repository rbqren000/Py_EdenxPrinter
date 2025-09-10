"""
平台特定编译配置模块
"""
import sys
from importlib import import_module

def get_platform_config():
    """动态加载当前平台的配置"""
    platform_name = {
        'darwin': 'macos',
        'win32': 'windows',
        'linux': 'linux'
    }.get(sys.platform, 'default')
    
    try:
        module = import_module(f'.{platform_name}', __package__)
        return module.get_config()
    except ImportError:
        try:
            from .default import get_config
            return get_config()
        except ImportError:
            # 返回默认配置
            return {
                'include_dirs': [],
                'extra_compile_args': ['-O2'],
                'extra_link_args': [],
                'libraries': [],
                'library_dirs': []
            }