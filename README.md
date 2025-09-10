# EdenxPrinter - MX Printer SDK

一个跨平台的打印机设备软件开发工具包，支持多种连接方式和图像处理功能。

## 项目概述

EdenxPrinter 是一个功能完整的打印机设备管理和控制库，提供了统一的 API 接口来支持不同类型的打印机设备。SDK 采用模块化设计，支持多种编程语言，并提供了丰富的功能特性。

### 主要特性

- **跨平台支持**：Windows、macOS、Linux
- **多架构支持**：x86、x64、ARM、ARM64
- **多语言绑定**：C/C++、Python
- **多种连接方式**：USB、串口、网络、蓝牙
- **图像处理**：格式转换、尺寸调整、亮度对比度调节、背景清理
- **设备管理**：自动发现、连接管理、状态监控
- **错误处理**：完善的错误码和错误信息
- **现代构建系统**：CMake + vcpkg 依赖管理
- **持续集成**：GitHub Actions 多平台自动构建
- **图形界面**：基于PyQt5的上位机应用程序

## 项目结构

```
EdenxPrinter/
├── README.md                   # 项目说明文档
├── LICENSE                     # 许可证文件
├── CMakeLists.txt             # 主构建配置
├── vcpkg.json                 # 依赖管理配置
├── main.py                    # 主程序入口
├── .github/
│   └── workflows/
│       └── build.yml          # CI/CD 工作流
├── cmake/
│   └── MXPrinterConfig.cmake.in  # CMake 配置模板
├── sdk/
│   ├── README.md              # SDK 说明文档
│   ├── src/
│   │   └── mx_printer.c       # C/C++ 源代码
│   ├── python/
│   │   └── mxSdk/             # Python SDK 模块
│   │       ├── __init__.py
│   │       ├── models/        # 数据模型
│   │       ├── connection/    # 连接相关模块
│   │       ├── enums/         # 枚举类型
│   │       ├── factories/     # 工厂类
│   │       ├── opencv/        # OpenCV图像处理
│   │       ├── packets/       # 数据包处理
│   │       ├── transport/     # 传输协议
│   │       └── utils/         # 工具类
│   └── tools/
│       └── build_sdk.py       # SDK 构建脚本
├── mxSdk/                     # Objective-C 原始SDK
├── pages/                     # PyQt5页面组件
├── dialogs/                   # 对话框组件
├── menus/                     # 菜单组件
├── helper/                    # 辅助工具
├── style/                     # 样式定义
├── utils/                     # 通用工具
├── examples/                  # 示例代码
│   ├── README.md
│   ├── c/                     # C语言示例
│   ├── cpp/                   # C++示例
│   └── python/                # Python示例
├── scripts/                   # 构建脚本
├── docs/                      # 文档
├── tests/                     # 测试代码
└── venv/                      # Python虚拟环境
```

## 快速开始

### 系统要求

- **操作系统**：Windows 10+、macOS 10.15+、Linux (Ubuntu 18.04+)
- **编译器**：GCC 7+、Clang 6+、MSVC 2019+
- **CMake**：3.16 或更高版本
- **Python**：3.9+ (用于 Python 绑定和应用程序)
- **vcpkg**：用于依赖管理（可选）
- **Qt5**：用于图形界面应用程序

### 构建安装

#### 1. 克隆项目

```bash
git clone https://github.com/rbqren000/Py_EdenxPrinter.git
cd EdenxPrinter
```

#### 2. 设置Python环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 使用 CMake 构建

```bash
# 创建构建目录
mkdir build && cd build

# 配置项目
cmake .. -DCMAKE_BUILD_TYPE=Release

# 构建
cmake --build .

# 安装（可选）
sudo cmake --install .
```

#### 4. 构建Python SDK

```bash
# 构建Python SDK
cd sdk/tools
python3 build_sdk.py
```

#### 5. 运行应用程序

```bash
# 返回项目根目录
cd ../../

# 运行主程序
python3 main.py
```

#### 6. 构建选项

```bash
# 构建示例程序
cmake .. -DBUILD_EXAMPLES=ON

# 构建测试套件
cmake .. -DBUILD_TESTS=ON

# 启用所有功能
cmake .. -DBUILD_EXAMPLES=ON -DBUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Debug
```

### 使用示例

#### Python SDK 示例

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdenxPrinter SDK 使用示例

作者: RBQ
版本: 1.0.1
Python版本: 3.9+
"""

import sys
import os

# 添加SDK路径到Python路径
sdk_path = os.path.join(os.path.dirname(__file__), 'sdk', 'python')
if sdk_path not in sys.path:
    sys.path.insert(0, sdk_path)

from mxSdk import (
    DataObj, Command, DataObjCallback, CommandCallback,
    ConnectionStrategyFactory, ConnectManager, ConnType
)

def main():
    """主函数 - 演示SDK基本用法"""
    
    # 创建连接管理器
    manager = ConnectManager()
    
    # 扫描可用设备
    print("正在扫描设备...")
    devices = manager.scan_devices()
    
    if not devices:
        print("未找到可用设备")
        return
    
    print(f"找到 {len(devices)} 个设备:")
    for i, device in enumerate(devices):
        print(f"  {i+1}. {device.name} ({device.connection_type})")
    
    # 选择第一个设备进行连接
    selected_device = devices[0]
    print(f"\n正在连接设备: {selected_device.name}")
    
    # 创建连接策略
    if selected_device.connection_type == ConnType.USB:
        strategy = ConnectionStrategyFactory.create_usb_strategy()
    elif selected_device.connection_type == ConnType.SERIAL:
        strategy = ConnectionStrategyFactory.create_serial_strategy()
    else:
        print(f"不支持的连接类型: {selected_device.connection_type}")
        return
    
    # 连接设备
    if manager.connect_device(selected_device, strategy):
        print("设备连接成功")
        
        # 创建数据对象
        data_obj = DataObj()
        
        # 创建命令
        command = Command()
        command.op_code = OpCode.GET_DEVICE_INFO
        
        # 发送命令
        print("发送设备信息查询命令...")
        response = manager.send_command(command)
        
        if response:
            print("收到设备响应")
            # 处理响应数据
        else:
            print("未收到设备响应")
        
        # 断开连接
        manager.disconnect_device()
        print("设备已断开连接")
    else:
        print("设备连接失败")

if __name__ == "__main__":
    main()
```

#### C 语言示例

```c
#include <stdio.h>
#include <stdlib.h>
#include "mx_printer.h"

int main() {
    // 初始化 SDK
    mx_handle_t handle = mx_init();
    if (!handle) {
        printf("SDK 初始化失败\n");
        return 1;
    }
    
    printf("EdenxPrinter SDK 版本: %s\n", mx_get_version());
    
    // 扫描设备
    mx_device_info_t devices[10];
    size_t device_count = 0;
    
    mx_error_t result = mx_scan_devices(handle, devices, 10, &device_count);
    if (result == MX_SUCCESS) {
        printf("找到 %zu 个设备\n", device_count);
        
        for (size_t i = 0; i < device_count; i++) {
            printf("设备 %zu: %s\n", i + 1, devices[i].device_name);
        }
        
        if (device_count > 0) {
            // 连接第一个设备
            result = mx_connect_device(handle, &devices[0]);
            if (result == MX_SUCCESS) {
                printf("设备连接成功\n");
                
                // 获取设备信息
                mx_device_info_t info;
                result = mx_get_device_info(handle, &info);
                if (result == MX_SUCCESS) {
                    printf("设备信息:\n");
                    printf("  名称: %s\n", info.device_name);
                    printf("  序列号: %s\n", info.serial_number);
                }
                
                // 断开连接
                mx_disconnect_device(handle);
                printf("设备已断开连接\n");
            } else {
                printf("设备连接失败: %s\n", mx_get_error_string(result));
            }
        }
    } else {
        printf("扫描设备失败: %s\n", mx_get_error_string(result));
    }
    
    // 清理资源
    mx_cleanup(handle);
    return 0;
}
```

#### 图形界面应用程序

项目包含一个基于PyQt5的图形界面应用程序，可以通过以下方式启动：

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行主程序
python3 main.py
```

图形界面提供以下功能：
- 设备扫描和连接
- 图像处理和预览
- 打印参数设置
- 实时状态监控
- 日志查看

## API 文档

### Python SDK API

#### 核心模块

##### mxSdk.models

数据模型模块，提供基础数据结构。

- `DataObj` - 数据对象基类
- `Command` - 命令对象
- `DataObjCallback` - 数据对象回调
- `CommandCallback` - 命令回调
- `DataObjContext` - 数据对象上下文
- `CommandContext` - 命令上下文

##### mxSdk.connection

连接管理模块，提供设备连接功能。

- `ConnectManager` - 连接管理器
- `ConnectionStrategy` - 连接策略基类
- `DeviceInfo` - 设备信息
- `ConnectionStatus` - 连接状态
- `UsbConnectionStrategy` - USB连接策略
- `SerialConnectionStrategy` - 串口连接策略
- `ConnectionStrategyFactory` - 连接策略工厂

##### mxSdk.enums

枚举类型模块，定义各种枚举值。

- `ConnType` - 连接类型
- `ConnectionStatus` - 连接状态
- `DataSendType` - 数据发送类型
- `FirmwareType` - 固件类型
- `OpCode` - 操作码
- `PaperType` - 纸张类型
- `RowLayoutDirection` - 行布局方向

##### mxSdk.factories

工厂类模块，提供对象创建功能。

- `DataFactory` - 数据对象工厂
- `PacketFactory` - 数据包工厂

##### mxSdk.opencv

OpenCV图像处理模块。

- `OpenCVUtils` - OpenCV工具类
- `ImageProcessor` - 图像处理器
- `ImageScanner` - 图像扫描器
- `ImageAnalysis` - 图像分析
- `ImageEffects` - 图像效果
- `BackgroundCleaner` - 背景清理器

#### 使用示例

```python
from mxSdk import (
    ConnectManager, ConnectionStrategyFactory, 
    DataObj, Command, OpCode, ConnType
)

# 创建连接管理器
manager = ConnectManager()

# 扫描设备
devices = manager.scan_devices()

# 创建USB连接策略
usb_strategy = ConnectionStrategyFactory.create_usb_strategy()

# 连接设备
if devices and manager.connect_device(devices[0], usb_strategy):
    # 创建命令
    cmd = Command()
    cmd.op_code = OpCode.GET_DEVICE_INFO
    
    # 发送命令
    response = manager.send_command(cmd)
    
    # 处理响应
    if response:
        print("命令执行成功")
    
    # 断开连接
    manager.disconnect_device()
```

### C API

#### 初始化和清理

- `mx_handle_t mx_init()` - 初始化 SDK
- `void mx_cleanup(mx_handle_t handle)` - 清理 SDK 资源
- `const char* mx_get_version()` - 获取 SDK 版本

#### 设备管理

- `mx_error_t mx_scan_devices(mx_handle_t handle, mx_device_info_t* devices, size_t max_devices, size_t* device_count)` - 扫描可用设备
- `mx_error_t mx_connect_device(mx_handle_t handle, const mx_device_info_t* device)` - 连接设备
- `mx_error_t mx_disconnect_device(mx_handle_t handle)` - 断开设备连接
- `mx_error_t mx_get_device_info(mx_handle_t handle, mx_device_info_t* info)` - 获取设备信息

#### 数据传输

- `mx_error_t mx_send_command(mx_handle_t handle, const mx_command_t* command)` - 发送命令到设备
- `mx_error_t mx_receive_response(mx_handle_t handle, mx_response_t* response)` - 从设备接收响应
- `mx_error_t mx_send_data(mx_handle_t handle, const uint8_t* data, size_t size)` - 发送数据到设备
- `mx_error_t mx_receive_data(mx_handle_t handle, uint8_t* buffer, size_t buffer_size, size_t* received_size)` - 从设备接收数据

#### 图像处理

- `mx_error_t mx_process_image(mx_handle_t handle, const char* image_path, mx_image_params_t* params)` - 处理图像文件
- `mx_error_t mx_get_image_info(mx_handle_t handle, const char* image_path, mx_image_info_t* info)` - 获取图像信息

#### 错误处理

- `const char* mx_get_error_string(mx_error_t error)` - 获取错误描述

### 数据结构

#### 设备信息 (C)

```c
typedef struct {
    char device_id[64];
    char device_name[128];
    char serial_number[64];
    mx_device_type_t type;
    uint16_t vendor_id;
    uint16_t product_id;
    bool is_connected;
} mx_device_info_t;
```

#### 图像参数 (C)

```c
typedef struct {
    uint32_t width;
    uint32_t height;
    uint8_t channels;
    uint8_t bit_depth;
    bool auto_resize;
    bool auto_contrast;
    float brightness;
    float contrast;
    bool background_clean;
} mx_image_params_t;
```

#### 错误码 (C)

```c
typedef enum {
    MX_SUCCESS = 0,
    MX_ERROR_INVALID_PARAMETER,
    MX_ERROR_OUT_OF_MEMORY,
    MX_ERROR_DEVICE_NOT_FOUND,
    MX_ERROR_DEVICE_BUSY,
    MX_ERROR_CONNECTION_FAILED,
    MX_ERROR_TIMEOUT,
    MX_ERROR_IO_ERROR,
    MX_ERROR_NOT_SUPPORTED,
    MX_ERROR_UNKNOWN
} mx_error_t;
```

## 开发指南

### 添加新功能

1. **更新Python SDK**：
   - 在 `sdk/python/mxSdk/` 相应模块中添加新功能
   - 更新 `__init__.py` 中的导出列表
   - 添加相应的单元测试

2. **更新C SDK**：
   - 在 `sdk/src/mx_printer.c` 中实现新功能
   - 更新头文件（如果有）
   - 添加相应的单元测试

3. **更新图形界面**：
   - 在 `pages/` 目录下添加新的页面组件
   - 在 `dialogs/` 目录下添加新的对话框
   - 更新 `main.py` 中的主窗口逻辑

4. **更新文档**：
   - 更新 API 文档
   - 添加示例代码
   - 更新 README.md

### 代码规范

- **Python 代码**：
  - 遵循 PEP 8 规范
  - 使用类型提示
  - 添加详细的文档字符串
  - 函数和类命名使用驼峰命名法

- **C 代码**：
  - 遵循 C11 标准
  - 使用 4 空格缩进
  - 添加详细的注释
  - 函数命名使用下划线分隔法

- **命名规范**：
  - Python: `className`, `methodName`, `variable_name`
  - C: `mx_function_name`, `MX_CONSTANT_NAME`, `mx_type_name_t`

### 测试

```bash
# 运行Python测试
python3 -m pytest tests/

# 运行特定测试
python3 -m pytest tests/test_specific_module.py

# 生成覆盖率报告
python3 -m pytest --cov=mxSdk tests/

# 构建并运行C测试
cmake .. -DBUILD_TESTS=ON
make
ctest

# 运行特定C测试
./bin/tests/mx_printer_tests --gtest_filter="MXPrinterBasicTest.*"
```

### 性能分析

```bash
# Python性能分析
python3 -m cProfile -s cumulative main.py

# 内存检查
python3 -m tracemalloc main.py

# C内存检查
make memcheck

# C静态分析
make static_analysis
```

### 调试技巧

1. **Python调试**：
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   # 或使用pdb
   import pdb; pdb.set_trace()
   ```

2. **C调试**：
   ```bash
   gdb ./your_program
   (gdb) run
   ```

3. **内存检查**：
   ```bash
   valgrind --leak-check=full ./your_program
   ```

## 部署

### 发布流程

1. **版本控制**：
   ```bash
   # 创建发布标签
   git tag -a v1.0.0 -m "版本 1.0.0 发布"
   
   # 推送标签
   git push origin v1.0.0
   ```

2. **GitHub Actions自动构建**：
   - 提交代码后，GitHub Actions会自动构建和测试
   - 构建成功后，会自动创建发布包
   - 发布包包括Python SDK、C SDK和图形界面应用程序

3. **发布到PyPI**：
   ```bash
   # 构建Python包
   cd sdk/python
   python3 -m build
   
   # 上传到PyPI
   python3 -m twine upload dist/*
   ```

4. **发布二进制包**：
   - macOS: 创建DMG安装包
   - Windows: 创建MSI安装包
   - Linux: 创建DEB/RPM包

### 持续集成/持续部署 (CI/CD)

项目使用GitHub Actions进行CI/CD，包括：

1. **代码质量检查**：
   - 代码风格检查
   - 静态代码分析
   - 单元测试
   - 集成测试

2. **构建流程**：
   - 多平台构建（macOS、Windows、Linux）
   - 多架构构建（x86_64、arm64）
   - 自动化测试
   - 代码覆盖率报告

3. **部署流程**：
   - 自动创建GitHub Release
   - 自动发布到PyPI
   - 自动生成文档
   - 自动发送通知

### 环境配置

1. **开发环境**：
   ```bash
   # 克隆仓库
   git clone https://github.com/rbqren000/Py_EdenxPrinter.git
   cd Py_EdenxPrinter
   
   # 创建虚拟环境
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或 venv\Scripts\activate  # Windows
   
   # 安装依赖
   pip install -r requirements.txt
   ```

2. **生产环境**：
   ```bash
   # 安装EdenxPrinter SDK
   pip install edenxprinter
   
   # 或从源码安装
   git clone https://github.com/rbqren000/Py_EdenxPrinter.git
   cd Py_EdenxPrinter
   pip install .
   ```

3. **Docker环境**：
   ```dockerfile
   FROM python:3.9-slim
   
   # 安装系统依赖
   RUN apt-get update && apt-get install -y \
       libopencv-dev \
       python3-opencv \
       && rm -rf /var/lib/apt/lists/*
   
   # 安装EdenxPrinter SDK
   RUN pip install edenxprinter
   
   # 设置工作目录
   WORKDIR /app
   
   # 复制应用程序代码
   COPY . .
   
   # 运行应用程序
   CMD ["python3", "main.py"]
   ```

### 监控与日志

1. **日志配置**：
   ```python
   import logging
   from mxSdk.utils import RBQLog
   
   # 配置日志
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('edenxprinter.log'),
           logging.StreamHandler()
       ]
   )
   
   # 使用SDK日志
   logger = RBQLog.get_logger("EdenxPrinter")
   logger.info("应用程序启动")
   ```

2. **性能监控**：
   ```python
   import time
   import psutil
   from mxSdk.utils import RBQLog
   
   # 监控系统资源
   def monitor_resources():
       cpu_percent = psutil.cpu_percent()
       memory_percent = psutil.virtual_memory().percent
       disk_percent = psutil.disk_usage('/').percent
       
       RBQLog.info(f"CPU使用率: {cpu_percent}%")
       RBQLog.info(f"内存使用率: {memory_percent}%")
       RBQLog.info(f"磁盘使用率: {disk_percent}%")
   ```

3. **错误追踪**：
   ```python
   import traceback
   from mxSdk.utils import RBQLog
   
   def handle_error(error):
       error_msg = f"发生错误: {str(error)}"
       stack_trace = traceback.format_exc()
       
       RBQLog.error(error_msg)
       RBQLog.error(stack_trace)
       
       # 发送错误报告
       send_error_report(error_msg, stack_trace)
   ```

## 故障排除

### 常见问题

1. **编译错误**：
   - 检查编译器版本是否满足要求
   - 确保所有依赖已正确安装
   - 查看详细的编译日志
   - 确保Python版本为3.9+
   - 检查Qt5是否正确安装

2. **链接错误**：
   - 检查库文件路径是否正确
   - 确保目标架构匹配
   - 验证依赖库版本兼容性
   - 检查OpenCV库是否正确链接

3. **运行时错误**：
   - 检查设备驱动是否安装
   - 验证设备权限设置
   - 查看系统日志获取详细信息
   - 确保虚拟环境已激活

4. **Python导入错误**：
   - 检查Python路径是否正确设置
   - 确保所有依赖包已安装
   - 验证SDK构建是否成功
   - 检查`__init__.py`文件是否存在

5. **图形界面问题**：
   - 确保PyQt5已正确安装
   - 检查Qt5环境变量设置
   - 验证显示设置（Linux系统）
   - 查看GUI日志获取详细信息

### 调试技巧

1. **启用调试日志**：
   ```python
   import logging
   from mxSdk.utils import RBQLog
   
   # 配置调试日志
   logging.basicConfig(level=logging.DEBUG)
   logger = RBQLog.get_logger("EdenxPrinter")
   logger.setLevel(logging.DEBUG)
   ```

2. **使用Python调试器**：
   ```python
   import pdb
   
   # 在需要调试的位置插入断点
   pdb.set_trace()
   ```

3. **使用C调试器**：
   ```bash
   gdb ./your_program
   (gdb) run
   ```

4. **内存检查**：
   ```bash
   # Python内存检查
   python3 -m tracemalloc main.py
   
   # C内存检查
   valgrind --leak-check=full ./your_program
   ```

5. **性能分析**：
   ```bash
   # Python性能分析
   python3 -m cProfile -s cumulative main.py
   
   # 系统资源监控
   htop  # Linux
   top   # macOS
   ```

### 日志分析

1. **查看应用程序日志**：
   ```bash
   # 查看最近的日志
   tail -f edenxprinter.log
   
   # 查看错误日志
   grep "ERROR" edenxprinter.log
   
   # 查看特定时间段的日志
   sed -n '/2024-01-01 10:00/,/2024-01-01 11:00/p' edenxprinter.log
   ```

2. **系统日志**：
   ```bash
   # macOS系统日志
   log show --last 1h --predicate 'process == "python3"'
   
   # Linux系统日志
   journalctl -u your-service-name -f
   ```

3. **设备连接日志**：
   ```bash
   # macOS设备连接日志
   log show --predicate 'subsystem == "com.apple.usb"'
   
   # Linux设备连接日志
   dmesg | grep usb
   ```

### 常见解决方案

1. **设备无法连接**：
   - 检查设备是否正确连接
   - 验证设备驱动是否安装
   - 尝试使用不同的USB端口
   - 检查设备权限（Linux系统可能需要sudo）

2. **图像处理失败**：
   - 检查OpenCV是否正确安装
   - 验证图像格式是否支持
   - 检查图像文件路径是否正确
   - 确保有足够的内存处理大图像

3. **性能问题**：
   - 减少图像处理分辨率
   - 使用多线程处理
   - 优化算法实现
   - 增加系统内存

4. **依赖问题**：
   ```bash
   # 重新安装所有依赖
   pip install -r requirements.txt --force-reinstall
   
   # 更新所有包
   pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
   ```

## 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. **Fork 项目**
2. **创建特性分支**：`git checkout -b feature/amazing-feature`
3. **提交更改**：`git commit -m 'Add amazing feature'`
4. **推送分支**：`git push origin feature/amazing-feature`
5. **创建 Pull Request**

### 贡献类型

- 🐛 Bug 修复
- ✨ 新功能
- 📚 文档改进
- 🎨 代码优化
- 🧪 测试增强
- 🔧 构建改进
- 🌐 国际化支持
- 📦 包管理改进

### 代码审查

所有 Pull Request 都需要经过代码审查：

- 代码风格检查
- 功能测试验证
- 性能影响评估
- 文档完整性检查
- 安全性评估

### 开发流程

1. **设置开发环境**：
   ```bash
   # 克隆仓库
   git clone https://github.com/your-username/Py_EdenxPrinter.git
   cd Py_EdenxPrinter
   
   # 添加上游仓库
   git remote add upstream https://github.com/rbqren000/Py_EdenxPrinter.git
   
   # 创建开发分支
   git checkout -b dev
   ```

2. **同步上游代码**：
   ```bash
   # 获取上游更改
   git fetch upstream
   
   # 合并到本地分支
   git merge upstream/main
   ```

3. **创建功能分支**：
   ```bash
   # 从dev分支创建新功能分支
   git checkout -b feature/your-feature-name dev
   ```

4. **提交规范**：
   - 提交信息应清晰描述更改内容
   - 使用以下前缀：
     - `feat:` 新功能
     - `fix:` Bug修复
     - `docs:` 文档更改
     - `style:` 代码格式更改
     - `refactor:` 代码重构
     - `test:` 测试相关更改
     - `chore:` 构建或辅助工具更改

   示例：
   ```bash
   git commit -m "feat: 添加USB设备自动检测功能"
   git commit -m "fix: 修复图像处理内存泄漏问题"
   git commit -m "docs: 更新API文档"
   ```

5. **测试要求**：
   - 所有新功能必须包含单元测试
   - 测试覆盖率应不低于80%
   - 所有现有测试必须通过
   - 性能测试应显示无明显性能下降

### 报告问题

1. **Bug报告**：
   - 使用GitHub Issues提交Bug报告
   - 提供详细的重现步骤
   - 包含系统环境信息
   - 附上相关的日志和截图

2. **功能请求**：
   - 描述所需功能的详细需求
   - 解释使用场景和预期行为
   - 提供可能的实现建议

### 社区准则

- 尊重所有贡献者
- 提供建设性的反馈
- 遵循项目的代码风格
- 及时响应审查意见
- 保持代码和文档的同步更新

### 发布流程

1. **版本号规范**：
   - 遵循语义化版本控制 (SemVer)
   - 格式：MAJOR.MINOR.PATCH
   - MAJOR: 不兼容的API更改
   - MINOR: 向后兼容的功能新增
   - PATCH: 向后兼容的问题修复

2. **发布检查清单**：
   - [ ] 所有测试通过
   - [ ] 文档已更新
   - [ ] 更新日志已更新
   - [ ] 版本号已更新
   - [ ] 构建和部署流程已验证

3. **发布步骤**：
   ```bash
   # 更新版本号
   # 更新CHANGELOG.md
   git add .
   git commit -m "chore: 准备发布v1.0.0"
   
   # 创建标签
   git tag -a v1.0.0 -m "版本 1.0.0 发布"
   
   # 推送更改和标签
   git push upstream main
   git push upstream v1.0.0
   ```

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

### 许可证摘要

- **商业使用**：允许
- **修改**：允许
- **分发**：允许
- **私有使用**：允许
- **责任担保**：不提供
- **专利使用**：不授予

### 第三方许可证

本项目使用了以下第三方库，它们各自有自己的许可证：

- **OpenCV**：BSD 3-Clause许可证
- **PyQt5**：GPL v3或商业许可证
- **NumPy**：BSD许可证
- **Pillow**：PIL许可证

## 联系方式

- **作者**：RBQ
- **邮箱**：rbq@example.com
- **项目主页**：https://github.com/rbqren000/Py_EdenxPrinter
- **问题报告**：https://github.com/rbqren000/Py_EdenxPrinter/issues
- **讨论区**：https://github.com/rbqren000/Py_EdenxPrinter/discussions
- **文档**：https://rbqren000.github.io/Py_EdenxPrinter/

### 社区资源

- **官方论坛**：https://forum.edenxprinter.com
- **Stack Overflow**：使用[edenxprinter]标签提问
- **Discord频道**：https://discord.gg/edenxprinter
- **Reddit社区**：https://reddit.com/r/edenxprinter

### 支持与咨询

- **技术支持**：support@edenxprinter.com
- **商务合作**：business@edenxprinter.com
- **安全报告**：security@edenxprinter.com

## 致谢

感谢以下开源项目和贡献者：

### 核心依赖

- [Python](https://www.python.org/) - 编程语言
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - Python GUI框架
- [OpenCV](https://opencv.org/) - 计算机视觉库
- [NumPy](https://numpy.org/) - 科学计算库
- [Pillow](https://python-pillow.org/) - 图像处理库

### 开发工具

- [CMake](https://cmake.org/) - 跨平台构建系统
- [GitHub Actions](https://github.com/features/actions) - CI/CD 平台
- [pytest](https://pytest.org/) - Python测试框架
- [Black](https://black.readthedocs.io/) - Python代码格式化工具

### 特别感谢

- 感谢所有为项目贡献代码的开发者
- 感谢提供反馈和建议的用户
- 感谢参与测试和文档编写的社区成员

## 更新日志

### v1.0.0 (2025-01-01)

- 🎉 首次发布
- ✨ 支持 USB、串口、网络连接
- ✨ 图像处理功能
- ✨ 跨平台支持（Windows、macOS、Linux）
- ✨ 多语言绑定（C/C++、Python）
- ✨ 基于PyQt5的图形界面应用程序
- 📚 完整的文档和示例
- 🧪 全面的测试套件
- 🔧 现代化的构建系统
- 🚀 GitHub Actions CI/CD集成

### 计划中的功能

- 🔄 支持更多打印机型号
- 🔄 增强图像处理算法
- 🔄 添加更多连接方式
- 🔄 支持移动平台（iOS/Android）
- 🔄 云服务集成

---

**EdenxPrinter - MX Printer SDK** - 让打印机设备开发变得简单高效！