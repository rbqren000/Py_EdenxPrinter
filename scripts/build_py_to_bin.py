#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python代码编译为二进制文件脚本 (修复版)
将Python代码编译为二进制文件以保护代码
"""

import os
import sys
import shutil
import logging
import subprocess
import tempfile
import argparse
import sysconfig
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 尝试导入Cython，如果失败则提示安装
try:
    from setuptools import setup, Extension
    from Cython.Build import cythonize
    import numpy as np
except ImportError as e:
    logger.error(f"缺少必要模块: {e}")
    logger.error("请运行: pip install cython setuptools numpy")
    sys.exit(1)


def get_python_config():
    """获取Python配置信息，跨平台兼容"""
    try:
        # 使用sysconfig获取Python配置，更可靠
        include_dir = sysconfig.get_path('include')
        logger.info(f"Python头文件路径: {include_dir}")
        return include_dir
    except Exception as e:
        logger.error(f"获取Python配置失败: {e}")
        # 备用方案
        import distutils.sysconfig
        return distutils.sysconfig.get_python_inc()


def get_platform_config():
    """动态加载平台配置"""
    try:
        # 修复导入问题
        sys.path.insert(0, os.path.dirname(__file__))
        from platforms import get_platform_config as _get_config
        return _get_config()
    except ImportError as e:
        logger.warning(f"无法加载平台配置: {e}，使用默认配置")
        return {
            'include_dirs': [],
            'extra_compile_args': ['-O2'],
            'extra_link_args': [],
            'libraries': [],
            'library_dirs': []
        }


def compile_py_to_bin(src_dir, dst_dir, config):
    """
    将Python代码编译为二进制文件
    """
    logger.info(f"开始编译: {src_dir} -> {dst_dir}")
    
    # 获取Python配置
    python_include = get_python_config()
    platform_config = get_platform_config()
    
    # 创建目标目录
    dst_path = Path(dst_dir)
    dst_path.mkdir(parents=True, exist_ok=True)
    
    compiled_files = []
    
    src_path = Path(src_dir)
    package_root = src_path.parent
    error_count = 0
    
    for py_file in src_path.rglob('*.py'):
        # Module path relative to package root (e.g., mxSdk.data.utils)
        rel_path_for_module = py_file.relative_to(package_root)
        
        # Correctly determine module path for __init__.py files
        if py_file.name == '__init__.py':
            module_path = '.'.join(rel_path_for_module.parent.parts)
        else:
            module_path = '.'.join(rel_path_for_module.with_suffix('').parts)

        # Destination path relative to output directory (e.g., build/dist/mxSdk/data/utils.so)
        rel_path_for_dest = py_file.relative_to(package_root)
        dst_file = dst_path / rel_path_for_dest.with_suffix('')
        
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"处理文件: {py_file} as module {module_path}")
        
        try:
            success = compile_single_file(py_file, dst_file, python_include, platform_config, module_path, src_path)
            if success:
                compiled_files.append(str(dst_file))
            else:
                error_count += 1
        except Exception as e:
            logger.error(f"编译 {py_file} 失败: {e}", exc_info=True)
            error_count += 1
            continue

    if error_count > 0:
        logger.error(f"{error_count} 个文件编译失败。")
        sys.exit(1)

    logger.info(f"编译完成，成功编译 {len(compiled_files)} 个文件")
    return compiled_files


def compile_single_file(src_file, dst_file, python_include, platform_config, module_path, src_root):
    """编译单个Python文件"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Recreate the package structure inside the temp directory
        rel_path_for_copy = src_file.relative_to(src_root.parent)
        tmp_src_file = tmp_path / rel_path_for_copy
        tmp_src_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, tmp_src_file)

        # Prepare extension module
        ext_modules = [
            Extension(
                name=module_path,
                sources=[str(tmp_src_file)],
                include_dirs=[python_include, np.get_include()] + platform_config.get('include_dirs', []),
                libraries=platform_config.get('libraries', []),
                library_dirs=platform_config.get('library_dirs', []),
                extra_compile_args=platform_config.get('extra_compile_args', []),
                extra_link_args=platform_config.get('extra_link_args', []),
            )
        ]
        
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            setup(
                name="mxSdk_compiled",
                ext_modules=cythonize(
                    ext_modules,
                    compiler_directives={
                        'language_level': "3",
                        'embedsignature': True,
                        'binding': True,
                        'boundscheck': False,
                        'wraparound': False
                    }
                ),
                script_args=["build_ext"],
                zip_safe=False
            )
            
            # Find the generated binary file in the build/lib.* directory
            build_lib_dirs = list(Path('build').glob('lib.*'))
            if not build_lib_dirs:
                logger.error(f"编译后未找到 'build/lib.*' 目录: {src_file.name}")
                return False
            
            build_lib_dir = build_lib_dirs[0]
            bin_ext = '.pyd' if os.name == 'nt' else '.so'
            
            # 根据模块路径正确查找编译产物
            module_path_parts = module_path.split('.')
            expected_file_name = module_path_parts[-1] + bin_ext
            expected_file_path = build_lib_dir.joinpath(*module_path_parts[:-1]) / expected_file_name
            
            if expected_file_path.exists():
                compiled_file = expected_file_path
            else:
                # 备用方案：搜索匹配的文件
                found_files = list(build_lib_dir.rglob(f"*{bin_ext}"))
                if not found_files:
                    logger.error(f"在 {build_lib_dir} 中未找到编译产物: {src_file.name}")
                    return False
                compiled_file = found_files[0]
            
            # Correctly determine the target file path
            if src_file.name == '__init__.py':
                target_file = dst_file.parent / (dst_file.parent.name + bin_ext)
            else:
                target_file = dst_file.with_suffix(bin_ext)

            # Ensure the destination directory exists before moving the file
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(compiled_file), str(target_file))
            logger.info(f"编译成功: {src_file.name} -> {target_file}")
            
            generate_checksum(target_file)
            return True
                
        finally:
            os.chdir(original_cwd)
    
    return False


def generate_checksum(file_path):
    """生成文件校验和"""
    import hashlib
    
    with open(file_path, 'rb') as f:
        content = f.read()
        checksum = hashlib.sha256(content).hexdigest()
    
    checksum_file = file_path.with_suffix('.sha256')
    with open(checksum_file, 'w') as f:
        f.write(f"{checksum}  {file_path.name}\n")
    
    logger.info(f"生成校验和: {checksum_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Python代码编译工具')
    parser.add_argument('--src', default=None, help='源代码目录')
    parser.add_argument('--output', '--dst', default=None, help='输出目录')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 确定源目录和目标目录
        project_root = Path(__file__).parent.parent
        src_dir = Path(args.src) if args.src else project_root / 'sdk/python/mxSdk'
        dst_dir = Path(args.output) if args.output else project_root / 'sdk/python/mxSdk_bin'
        
        # 转换为绝对路径
        src_dir = src_dir.resolve()
        dst_dir = dst_dir.resolve()
        
        logger.info("=" * 60)
        logger.info(f"Python代码编译工具启动于 {datetime.now()}")
        logger.info(f"源代码目录: {src_dir}")
        logger.info(f"目标目录: {dst_dir}")
        logger.info(f"Python版本: {sys.version}")
        logger.info(f"平台: {sys.platform}")
        logger.info("=" * 60)
        
        if not src_dir.exists():
            logger.error(f"源目录不存在: {src_dir}")
            sys.exit(1)
        
        # 确保目标目录存在
        dst_dir.mkdir(parents=True, exist_ok=True)
        
        # 编译
        compiled_files = compile_py_to_bin(str(src_dir), str(dst_dir), {})
        
        logger.info("=" * 60)
        logger.info(f"编译完成，共处理 {len(compiled_files)} 个文件")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.warning("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()