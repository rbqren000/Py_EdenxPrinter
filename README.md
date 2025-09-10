# MX Printer SDK

一个跨平台的打印机设备软件开发工具包，支持多种连接方式和图像处理功能。

## 项目概述

MX Printer SDK 是一个功能完整的打印机设备管理和控制库，提供了统一的 API 接口来支持不同类型的打印机设备。SDK 采用模块化设计，支持多种编程语言，并提供了丰富的功能特性。

### 主要特性

- **跨平台支持**：Windows、macOS、Linux、Android
- **多架构支持**：x86、x64、ARM、ARM64
- **多语言绑定**：C/C++、Python
- **多种连接方式**：USB、串口、网络、蓝牙
- **图像处理**：格式转换、尺寸调整、亮度对比度调节
- **设备管理**：自动发现、连接管理、状态监控
- **错误处理**：完善的错误码和错误信息
- **现代构建系统**：CMake + vcpkg 依赖管理
- **持续集成**：GitHub Actions 多平台自动构建

## 项目结构

```
MXPrinter/
├── README.md                   # 项目说明文档
├── LICENSE                     # 许可证文件
├── CMakeLists.txt             # 主构建配置
├── vcpkg.json                 # 依赖管理配置
├── build_sdk.py               # SDK 构建脚本
├── .github/
│   └── workflows/
│       └── build.yml          # CI/CD 工作流
├── cmake/
│   └── MXPrinterConfig.cmake.in  # CMake 配置模板
├── sdk/
│   ├── README.md              # SDK 说明文档
│   ├── include/
│   │   └── mx_printer.h       # C/C++ 头文件
│   ├── src/
│   │   └── mx_printer.c       # C/C++ 源代码
│   ├── python/
│   │   └── mxSdk/             # Python SDK 模块
│   │       ├── __init__.py
│   │       ├── core.py        # 核心功能
│   │       ├── enums.py      # 枚举类型
│   │       ├── connection/   # 连接相关模块
│   │       │   ├── __init__.py
│   │       │   ├── strategy.py      # 连接策略基类
│   │       │   ├── parameters.py    # 连接参数
│   │       │   ├── usb.py           # USB连接实现
│   │       │   ├── serial.py        # 串口连接实现
│   │       │   └── factory.py       # 连接策略工厂
│   └── platforms/
│       ├── windows/
│       │   └── build.bat      # Windows 构建脚本
│       ├── macos/
│       │   └── build.sh       # macOS 构建脚本
│       └── linux/
│           └── build.sh       # Linux 构建脚本
├── examples/
│   ├── README.md              # 示例说明文档
│   ├── CMakeLists.txt         # 示例构建配置
│   ├── c/
│   │   └── basic_usage.c      # C 语言示例
│   ├── cpp/
│   │   └── printer_manager.cpp # C++ 示例
│   └── python/
│       └── mx_printer_demo.py # Python 示例
└── tests/
    ├── CMakeLists.txt         # 测试构建配置
    ├── test_mx_printer_basic.cpp
    ├── test_mx_printer_devices.cpp
    ├── test_mx_printer_image.cpp
    └── test_mx_printer_errors.cpp
```

## 快速开始

### 系统要求

- **编译器**：GCC 7+、Clang 6+、MSVC 2019+
- **CMake**：3.16 或更高版本
- **Python**：3.7+ (用于 Python 绑定)
- **vcpkg**：用于依赖管理（可选）

### 构建安装

#### 1. 克隆项目

```bash
git clone https://github.com/your-org/mx-printer-sdk.git
cd mx-printer-sdk
```

#### 2. 使用 CMake 构建

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

#### 3. 使用平台脚本构建

**macOS:**
```bash
cd sdk/platforms/macos
./build.sh
```

**Linux:**
```bash
cd sdk/platforms/linux
./build.sh
```

**Windows:**
```cmd
cd sdk\platforms\windows
build.bat
```

#### 4. 构建选项

```bash
# 构建示例程序
cmake .. -DBUILD_EXAMPLES=ON

# 构建测试套件
cmake .. -DBUILD_TESTS=ON

# 启用所有功能
cmake .. -DBUILD_EXAMPLES=ON -DBUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Debug
```

### 使用示例

#### C 语言示例

```c
#include "mx_printer.h"
#include <stdio.h>

int main() {
    // 初始化 SDK
    mx_handle_t handle = mx_init();
    if (!handle) {
        printf("SDK 初始化失败\n");
        return 1;
    }
    
    printf("MX Printer SDK 版本: %s\n", mx_get_version());
    
    // 扫描设备
    mx_device_info_t devices[10];
    size_t device_count = 0;
    
    mx_error_t result = mx_scan_devices(handle, devices, 10, &device_count);
    if (result == MX_SUCCESS) {
        printf("找到 %zu 个设备\n", device_count);
        
        for (size_t i = 0; i < device_count; i++) {
            printf("设备 %zu: %s\n", i + 1, devices[i].device_name);
        }
    }
    
    // 清理资源
    mx_cleanup(handle);
    return 0;
}
```

#### Python 示例

```python
from mxSdk import DataObj, Command
from mxSdk.enums import ConnType, FirmwareType

# 创建设备管理器
manager = MXPrinterManager()

# 初始化 SDK
if manager.initialize():
    print("SDK 初始化成功")
    
    # 扫描设备
    devices = manager.scan_devices()
    print(f"找到 {len(devices)} 个设备")
    
    for device in devices:
        print(f"设备: {device.name}")
        print(f"类型: {device.connection_type}")
    
    # 清理资源
    manager.cleanup()
```

## API 文档

### 核心 API

#### 初始化和清理

- `mx_handle_t mx_init()` - 初始化 SDK
- `void mx_cleanup(mx_handle_t handle)` - 清理 SDK 资源
- `const char* mx_get_version()` - 获取 SDK 版本

#### 设备管理

- `mx_error_t mx_scan_devices()` - 扫描可用设备
- `mx_error_t mx_connect_device()` - 连接设备
- `mx_error_t mx_disconnect_device()` - 断开设备连接

#### 数据传输

- `mx_error_t mx_send_data()` - 发送数据到设备
- `mx_error_t mx_receive_data()` - 从设备接收数据

#### 图像处理

- `mx_error_t mx_process_image()` - 处理图像文件
- `mx_error_t mx_get_image_info()` - 获取图像信息

#### 错误处理

- `const char* mx_get_error_string(mx_error_t error)` - 获取错误描述

### 数据结构

#### 设备信息

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

#### 图像参数

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
} mx_image_params_t;
```

### 错误码

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

1. **更新头文件**：在 `sdk/include/mx_printer.h` 中添加新的 API 声明
2. **实现功能**：在 `sdk/src/mx_printer.c` 中实现具体功能
3. **添加测试**：在 `tests/` 目录下添加相应的单元测试
4. **更新文档**：更新 API 文档和示例代码
5. **更新绑定**：如果需要，更新 Python 绑定

### 代码规范

- **C 代码**：遵循 C11 标准，使用 4 空格缩进
- **C++ 代码**：遵循 C++17 标准，使用现代 C++ 特性
- **Python 代码**：遵循 PEP 8 规范，使用类型提示
- **命名规范**：
  - 函数：`mx_function_name`
  - 类型：`mx_type_name_t`
  - 常量：`MX_CONSTANT_NAME`
  - 宏：`MX_MACRO_NAME`

### 测试

```bash
# 构建并运行测试
cmake .. -DBUILD_TESTS=ON
make
ctest

# 运行特定测试
./bin/tests/mx_printer_tests --gtest_filter="MXPrinterBasicTest.*"

# 生成覆盖率报告（Debug 模式）
cmake .. -DCMAKE_BUILD_TYPE=Debug -DENABLE_COVERAGE=ON
make coverage
```

### 性能分析

```bash
# 内存检查
make memcheck

# 静态分析
make static_analysis

# 性能基准测试
cmake .. -DBUILD_PERFORMANCE_TESTS=ON
make
./bin/tests/mx_printer_benchmarks
```

## 部署

### 包管理

项目使用 vcpkg 进行依赖管理：

```bash
# 安装依赖
vcpkg install

# 更新依赖
vcpkg upgrade
```

### 发布

1. **更新版本号**：在 `CMakeLists.txt` 和相关文件中更新版本
2. **创建标签**：`git tag v1.0.0`
3. **推送标签**：`git push origin v1.0.0`
4. **GitHub Actions** 将自动构建并创建发布包

### 安装包

构建完成后，可以创建安装包：

```bash
# 创建 DEB 包（Linux）
cpack -G DEB

# 创建 RPM 包（Linux）
cpack -G RPM

# 创建 MSI 包（Windows）
cpack -G WIX

# 创建 DMG 包（macOS）
cpack -G DragNDrop
```

## 故障排除

### 常见问题

1. **编译错误**：
   - 检查编译器版本是否满足要求
   - 确保所有依赖已正确安装
   - 查看详细的编译日志

2. **链接错误**：
   - 检查库文件路径是否正确
   - 确保目标架构匹配
   - 验证依赖库版本兼容性

3. **运行时错误**：
   - 检查设备驱动是否安装
   - 验证设备权限设置
   - 查看系统日志获取详细信息

### 调试技巧

1. **启用调试日志**：
   ```c
   #define MX_DEBUG 1
   ```

2. **使用调试器**：
   ```bash
   gdb ./your_program
   (gdb) run
   ```

3. **内存检查**：
   ```bash
   valgrind --leak-check=full ./your_program
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

### 代码审查

所有 Pull Request 都需要经过代码审查：

- 代码风格检查
- 功能测试验证
- 性能影响评估
- 文档完整性检查

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

- **作者**：RBQ
- **邮箱**：rbq@example.com
- **项目主页**：https://github.com/your-org/mx-printer-sdk
- **问题报告**：https://github.com/your-org/mx-printer-sdk/issues
- **讨论区**：https://github.com/your-org/mx-printer-sdk/discussions

## 致谢

感谢以下开源项目和贡献者：

- [CMake](https://cmake.org/) - 跨平台构建系统
- [vcpkg](https://vcpkg.io/) - C++ 包管理器
- [Google Test](https://github.com/google/googletest) - 测试框架
- [GitHub Actions](https://github.com/features/actions) - CI/CD 平台

## 更新日志

### v1.0.0 (2024-XX-XX)

- 🎉 首次发布
- ✨ 支持 USB、串口、网络连接
- ✨ 图像处理功能
- ✨ 跨平台支持（Windows、macOS、Linux）
- ✨ 多语言绑定（C/C++、Python）
- 📚 完整的文档和示例
- 🧪 全面的测试套件
- 🔧 现代化的构建系统

---

**MX Printer SDK** - 让打印机设备开发变得简单高效！