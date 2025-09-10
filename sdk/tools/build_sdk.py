#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MX Printer SDK构建脚本

作者: RBQ
描述: 用于构建不同平台的SDK库文件
"""

import os
import sys
import platform
import subprocess
import argparse
from pathlib import Path


class SDKBuilder:
    """
    SDK构建器类
    """
    
    def __init__(self):
        """
        初始化构建器
        """
        self.sdk_root = Path(__file__).parent.parent
        self.project_root = self.sdk_root.parent
        self.build_dir = self.sdk_root / "build"
        self.platforms_dir = self.sdk_root / "platforms"
        
    def detect_platform(self):
        """
        检测当前构建平台
        
        Returns:
            str: 平台标识
        """
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == "windows":
            if machine in ["amd64", "x86_64"]:
                return "windows/x64"
            elif machine == "i386":
                return "windows/x86"
            elif machine in ["arm64", "aarch64"]:
                return "windows/arm64"
        elif system == "darwin":  # macOS
            if machine in ["arm64", "aarch64"]:
                return "macos/arm64"
            else:
                return "macos/x86_64"
        elif system == "linux":
            if machine in ["x86_64", "amd64"]:
                return "linux/x86_64"
            elif machine in ["arm64", "aarch64"]:
                return "linux/arm64"
            elif machine.startswith("arm"):
                return "linux/armv7"
        
        return "unknown"
    
    def create_build_dirs(self):
        """
        创建构建目录
        """
        self.build_dir.mkdir(exist_ok=True)
        print(f"创建构建目录: {self.build_dir}")
    
    def build_native_library(self, target_platform=None):
        """
        构建原生库
        
        Args:
            target_platform (str): 目标平台，None表示当前平台
        """
        if target_platform is None:
            target_platform = self.detect_platform()
        
        print(f"开始构建平台: {target_platform}")
        
        # 创建平台特定的构建目录
        platform_build_dir = self.build_dir / target_platform
        platform_build_dir.mkdir(parents=True, exist_ok=True)
        
        # 这里应该包含实际的编译逻辑
        # 例如调用CMake、Make或其他构建系统
        
        # 示例：使用CMake构建（需要根据实际情况调整）
        cmake_file = self.create_cmake_file(platform_build_dir)
        
        try:
            # 配置CMake
            subprocess.run([
                "cmake",
                "-S", str(self.project_root),
                "-B", str(platform_build_dir),
                f"-DTARGET_PLATFORM={target_platform}"
            ], check=True)
            
            # 构建
            subprocess.run([
                "cmake",
                "--build", str(platform_build_dir),
                "--config", "Release"
            ], check=True)
            
            print(f"平台 {target_platform} 构建成功")
            
        except subprocess.CalledProcessError as e:
            print(f"构建失败: {e}")
            return False
        except FileNotFoundError:
            print("CMake未找到，请确保已安装CMake")
            return False
        
        return True
    
    def create_cmake_file(self, build_dir):
        """
        创建CMakeLists.txt文件
        
        Args:
            build_dir (Path): 构建目录
        """
        cmake_content = '''
cmake_minimum_required(VERSION 3.16)
project(MXPrinterSDK)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_C_STANDARD 11)

# 设置输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# 包含头文件目录
include_directories(${CMAKE_SOURCE_DIR}/sdk/include)

# 源文件
set(SDK_SOURCES
    ${CMAKE_SOURCE_DIR}/sdk/src/mx_printer.c
    # 添加其他源文件...
)

# 创建共享库
add_library(mx_printer SHARED ${SDK_SOURCES})

# 创建静态库
add_library(edenx_printer_static STATIC ${SDK_SOURCES})

# 设置库的输出名称
set_target_properties(edenx_printer_static PROPERTIES OUTPUT_NAME edenx_printer)

# 链接库（根据需要添加）
# target_link_libraries(edenx_printer ${REQUIRED_LIBRARIES})

# 安装规则
install(TARGETS edenx_printer edenx_printer_static
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin)

install(DIRECTORY ${CMAKE_SOURCE_DIR}/sdk/include/
    DESTINATION include
    FILES_MATCHING PATTERN "*.h")
'''
        
        cmake_file = build_dir / "CMakeLists.txt"
        with open(cmake_file, 'w', encoding='utf-8') as f:
            f.write(cmake_content)
        
        return cmake_file
    
    def copy_libraries(self, target_platform):
        """
        复制构建好的库文件到对应平台目录
        
        Args:
            target_platform (str): 目标平台
        """
        platform_build_dir = self.build_dir / target_platform
        platform_output_dir = self.platforms_dir / target_platform
        platform_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 查找并复制库文件
        lib_extensions = {
            'windows': ['.dll', '.lib'],
            'macos': ['.dylib', '.a'],
            'linux': ['.so', '.a']
        }
        
        system = target_platform.split('/')[0]
        extensions = lib_extensions.get(system, ['.so', '.a'])
        
        for ext in extensions:
            for lib_file in platform_build_dir.rglob(f"*edenx_printer*{ext}"):
                dest_file = platform_output_dir / lib_file.name
                print(f"复制库文件: {lib_file} -> {dest_file}")
                # 这里应该实际复制文件
                # shutil.copy2(lib_file, dest_file)
    
    def build_all_platforms(self):
        """
        构建所有支持的平台
        """
        platforms = [
            "windows/x86",
            "windows/x64",
            "windows/arm64",
            "macos/x86_64",
            "macos/arm64",
            "linux/x86_64",
            "linux/arm64",
            "linux/armv7"
        ]
        
        current_platform = self.detect_platform()
        print(f"当前平台: {current_platform}")
        
        for platform in platforms:
            if platform == current_platform:
                print(f"\n构建当前平台: {platform}")
                self.build_native_library(platform)
                self.copy_libraries(platform)
            else:
                print(f"\n跳过交叉编译平台: {platform} (需要交叉编译工具链)")


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='Edenx Printer SDK构建脚本')
    parser.add_argument('--platform', help='目标平台 (例如: macos/arm64)')
    parser.add_argument('--all', action='store_true', help='构建所有平台')
    parser.add_argument('--clean', action='store_true', help='清理构建目录')
    
    args = parser.parse_args()
    
    builder = SDKBuilder()
    
    if args.clean:
        print("清理构建目录...")
        import shutil
        if builder.build_dir.exists():
            shutil.rmtree(builder.build_dir)
        print("清理完成")
        return
    
    builder.create_build_dirs()
    
    if args.all:
        builder.build_all_platforms()
    elif args.platform:
        builder.build_native_library(args.platform)
        builder.copy_libraries(args.platform)
    else:
        # 构建当前平台
        current_platform = builder.detect_platform()
        builder.build_native_library(current_platform)
        builder.copy_libraries(current_platform)
    
    print("\n构建完成！")


if __name__ == "__main__":
    main()