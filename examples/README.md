# MX Printer SDK 示例程序

本目录包含了 MX Printer SDK 的各种语言示例程序，演示如何使用 SDK 的核心功能。

## 目录结构

```
examples/
├── README.md                    # 本文档
├── CMakeLists.txt              # CMake 构建配置
├── c/
│   └── basic_usage.c           # C 语言基础使用示例
├── cpp/
│   └── printer_manager.cpp     # C++ 面向对象示例
└── python/
    └── mx_printer_demo.py       # Python 语言示例
```

## 示例说明

### C 语言示例 (`c/basic_usage.c`)

演示了 MX Printer SDK C API 的基本使用方法：

- **SDK 初始化和清理**：`mx_init()` 和 `mx_cleanup()`
- **设备扫描**：`mx_scan_devices()` 扫描可用设备
- **设备连接管理**：`mx_connect_device()` 和 `mx_disconnect_device()`
- **数据传输**：`mx_send_data()` 和 `mx_receive_data()`
- **图像处理**：`mx_process_image()` 和 `mx_get_image_info()`
- **错误处理**：`mx_get_error_string()` 获取错误描述

**特点**：
- 纯 C 语言实现
- 直接调用底层 API
- 详细的错误处理和日志输出
- 适合嵌入式和系统级开发

### C++ 语言示例 (`cpp/printer_manager.cpp`)

提供了面向对象的 MX Printer SDK 封装：

- **MXPrinterManager 类**：封装了所有 SDK 功能
- **DeviceInfo 结构体**：设备信息的 C++ 表示
- **ImageParams 结构体**：图像处理参数的 C++ 封装
- **RAII 资源管理**：自动初始化和清理
- **STL 容器支持**：使用 `std::vector`、`std::string` 等
- **异常安全**：完善的异常处理机制

**特点**：
- 现代 C++ 设计（C++17）
- 面向对象封装
- 类型安全和内存安全
- 适合桌面应用和高级系统开发

### Python 语言示例 (`python/mx_printer_demo.py`)

展示了 Python SDK 的使用方式：

- **MXPrinterManager 类**：Python 风格的设备管理器
- **DeviceInfo 数据类**：使用 `@dataclass` 装饰器
- **类型提示**：完整的类型注解支持
- **日志系统**：集成 Python `logging` 模块
- **异步支持**：为未来异步操作预留接口
- **枚举类型**：使用 SDK 提供的枚举类型

**特点**：
- Pythonic 设计风格
- 完整的类型提示
- 详细的文档字符串
- 适合快速原型开发和脚本应用

## 构建和运行

### 前置条件

1. **安装 MX Printer SDK**：
   ```bash
   # 构建并安装 SDK
   mkdir build && cd build
   cmake ..
   make
   sudo make install
   ```

2. **安装依赖**：
   - C/C++ 编译器（GCC 7+ 或 Clang 6+）
   - CMake 3.16+
   - Python 3.7+（用于 Python 示例）

### 构建 C/C++ 示例

```bash
# 在 examples 目录下
mkdir build && cd build
cmake ..
make

# 运行示例
./bin/mx_basic_usage_c
./bin/mx_printer_manager_cpp
```

### 使用 CMake 目标

```bash
# 构建所有示例
make

# 运行特定示例
make run_c_example
make run_cpp_example
make run_python_example

# 运行所有示例
make run_all_examples
```

### 运行 Python 示例

```bash
# 确保 Python SDK 在路径中
export PYTHONPATH=/path/to/mx_printer_sdk/python:$PYTHONPATH

# 运行示例
cd python
python3 mx_printer_demo.py
```

## 示例功能演示

### 1. 设备管理

所有示例都演示了以下设备管理功能：

- **设备扫描**：自动发现可用的打印机设备
- **设备信息显示**：显示设备 ID、名称、类型、连接状态等
- **设备连接**：建立与特定设备的连接
- **数据传输**：发送命令和接收响应
- **连接管理**：正确断开设备连接

### 2. 图像处理

演示图像处理功能：

- **图像参数设置**：分辨率、颜色通道、亮度、对比度等
- **图像格式转换**：支持多种图像格式
- **图像信息获取**：读取图像的元数据信息
- **批量处理**：处理多个图像文件

### 3. 错误处理

展示完善的错误处理机制：

- **错误码检查**：检查所有 API 调用的返回值
- **错误信息获取**：使用 `mx_get_error_string()` 获取详细错误描述
- **异常处理**：C++ 和 Python 示例中的异常处理
- **资源清理**：确保在错误情况下正确清理资源

## 开发指南

### 添加新示例

1. **创建源文件**：在相应语言目录下创建新的示例文件
2. **更新 CMakeLists.txt**：添加新的构建目标
3. **更新文档**：在本 README 中添加示例说明
4. **测试验证**：确保示例能正确编译和运行

### 代码风格

- **C 语言**：遵循 C11 标准，使用 4 空格缩进
- **C++ 语言**：遵循 C++17 标准，使用现代 C++ 特性
- **Python 语言**：遵循 PEP 8 规范，使用类型提示
- **注释**：提供详细的中文注释和文档字符串

### 最佳实践

1. **资源管理**：
   - 使用 RAII（C++）或 `try-finally`（Python）
   - 确保 SDK 初始化后必须调用清理函数
   - 连接的设备必须正确断开

2. **错误处理**：
   - 检查所有 API 调用的返回值
   - 提供有意义的错误信息
   - 在错误情况下正确清理资源

3. **性能优化**：
   - 重用 SDK 句柄，避免频繁初始化
   - 批量处理多个操作
   - 合理设置超时时间

## 故障排除

### 常见问题

1. **SDK 未找到**：
   ```
   CMake Error: Could not find a package configuration file provided by "MXPrinter"
   ```
   **解决方案**：确保 SDK 已正确安装，或设置 `CMAKE_PREFIX_PATH`

2. **Python 导入错误**：
   ```
   ImportError: No module named 'mxSdk'
   ```
   **解决方案**：设置正确的 `PYTHONPATH` 或安装 Python SDK

3. **设备连接失败**：
   ```
   设备连接失败: MX_ERROR_DEVICE_NOT_FOUND
   ```
   **解决方案**：检查设备是否正确连接，驱动是否安装

4. **权限问题**：
   ```
   设备连接失败: MX_ERROR_ACCESS_DENIED
   ```
   **解决方案**：在 Linux/macOS 上可能需要 sudo 权限或添加用户到相应组

### 调试技巧

1. **启用详细日志**：
   - C/C++：编译时定义 `DEBUG` 宏
   - Python：设置日志级别为 `DEBUG`

2. **使用调试器**：
   - GDB（Linux/macOS）：`gdb ./mx_basic_usage_c`
   - LLDB（macOS）：`lldb ./mx_basic_usage_c`
   - Visual Studio（Windows）：F5 启动调试

3. **检查系统日志**：
   - Linux：`dmesg | grep usb`
   - macOS：`log show --predicate 'subsystem contains "usb"'`
   - Windows：事件查看器

## 许可证

本示例代码遵循与 MX Printer SDK 相同的许可证。详情请参阅项目根目录的 LICENSE 文件。

## 贡献

欢迎提交问题报告和改进建议！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支：`git checkout -b feature/new-example`
3. 提交更改：`git commit -am 'Add new example'`
4. 推送分支：`git push origin feature/new-example`
5. 创建 Pull Request

## 联系方式

- **作者**：RBQ
- **项目主页**：[MX Printer SDK](https://github.com/your-org/mx-printer-sdk)
- **问题报告**：[GitHub Issues](https://github.com/your-org/mx-printer-sdk/issues)