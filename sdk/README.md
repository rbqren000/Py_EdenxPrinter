# MX Printer SDK

一个跨平台的打印机设备通信和图像处理SDK，支持多种连接方式和图像格式。

## 主要特性

- 🌐 **跨平台支持**: Windows、macOS、Linux、iOS、Android
- 🔌 **多种连接方式**: USB、串口、网络
- 🖼️ **图像处理**: 自动调整、格式转换、优化处理
- 🔧 **多语言绑定**: C/C++、Python，更多语言支持计划中
- 📱 **移动端支持**: iOS和Android平台
- 🛠️ **易于集成**: 简单的API设计，详细的文档和示例

## 项目结构

```
sdk/
├── README.md              # 项目说明文档
├── __init__.py            # Python包初始化文件
├── docs/                  # 文档目录
│   └── architecture.md   # 架构设计文档
├── examples/              # 示例代码
│   ├── cpp/              # C++示例
│   ├── java/             # Java示例
│   └── python/           # Python示例
├── include/               # C/C++头文件目录
│   ├── common/           # 通用头文件
│   └── mx_printer.h      # 主头文件
├── src/                  # C/C++源码实现
│   └── mx_printer.c      # 核心实现
├── platforms/            # 平台特定文件和构建脚本
│   ├── linux/           # Linux平台
│   ├── macos/           # macOS平台
│   ├── mobile/          # 移动平台
│   └── windows/         # Windows平台
├── python/              # Python SDK
│   ├── __init__.py     # Python包初始化
│   └── mxSdk/          # 核心Python模块
│       ├── connection/ # 连接管理模块
│       ├── core/       # 核心功能模块
│       ├── data/       # 数据类型模块
│       ├── enums/      # 枚举定义模块
│       ├── factories/  # 工厂类模块
│       ├── opencv/     # 图像处理模块
│       ├── packets/    # 数据包模块
│       └── utils/      # 工具类模块
└── tools/               # 构建和开发工具
    └── build_sdk.py    # SDK构建脚本
```

## 快速开始

### 构建SDK

#### 使用平台特定脚本

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

#### 使用CMake（推荐）

```bash
mkdir build && cd build
cmake ..
cmake --build . --config Release
cmake --install .
```

### C/C++ API

```c
#include "mx_printer.h"

int main() {
    // 初始化SDK
    mx_handle_t handle = mx_init();
    if (!handle) {
        printf("SDK初始化失败\n");
        return -1;
    }
    
    // 扫描设备
    mx_device_info_t devices[10];
    size_t device_count;
    mx_error_t result = mx_scan_devices(handle, devices, 10, &device_count);
    
    if (result == MX_SUCCESS) {
        printf("找到 %zu 个设备\n", device_count);
    }
    
    // 清理资源
    mx_cleanup(handle);
    return 0;
}
```

### Python API

```python
from mxSdk.connection import ConnectionStrategyFactory
from mxSdk.enums import ConnType, ConnectionStatus
from mxSdk.data import LogoData
from mxSdk.utils import RBQLog

# 初始化日志
logger = RBQLog()

# 创建连接策略
factory = ConnectionStrategyFactory()
usb_strategy = factory.create_strategy(ConnType.USB)

# 连接设备
if usb_strategy.connect():
    logger.info("设备连接成功")
    
    # 发送数据
    data = b"Hello, Printer!"
    usb_strategy.write_data(data)
    
    # 断开连接
    usb_strategy.disconnect()
else:
    logger.error("设备连接失败")
```

## 安装和构建

### 预编译库使用

1. 下载对应平台的预编译库
2. 将 `include` 目录添加到编译器包含路径
3. 链接对应平台的库文件

### 从源码构建

```bash
# 使用构建脚本
python3 sdk/tools/build_sdk.py

# 构建特定平台
python3 sdk/tools/build_sdk.py --platform macos/arm64

# 构建所有平台
python3 sdk/tools/build_sdk.py --all
```

## 支持的平台

| 操作系统 | 架构 | 状态 |
|---------|------|------|
| Windows | x86, x64, ARM64 | ✅ 支持 |
| macOS | x86_64, ARM64 | ✅ 支持 |
| Linux | x86_64, ARM64, ARMv7 | ✅ 支持 |
| iOS | ARM64 | 🚧 开发中 |
| Android | ARM64, ARMv7 | 🚧 开发中 |

## API 概览

### 核心功能

- **设备管理**: 扫描、连接、断开设备
- **数据通信**: 发送和接收数据
- **图像处理**: 格式转换、尺寸调整、优化
- **错误处理**: 详细的错误码和描述

### C API

```c
// 初始化和清理
edenx_handle_t edenx_init(void);
void edenx_cleanup(edenx_handle_t handle);

// 设备管理
edenx_error_t edenx_scan_devices(...);
edenx_error_t edenx_connect_device(...);
edenx_error_t edenx_disconnect_device(...);

// 数据通信
edenx_error_t edenx_send_data(...);
edenx_error_t edenx_receive_data(...);

// 图像处理
edenx_error_t edenx_process_image(...);
```

## 核心模块

### C/C++ API (mx_printer.h)
提供跨平台的C/C++接口，包括：
- 设备扫描和连接管理
- 数据收发功能
- 图像处理接口
- 错误处理机制

### Python API (mxSdk)
核心Python模块，提供完整的设备通信和图像处理功能。

## 依赖管理

项目使用vcpkg进行C/C++依赖管理，支持以下可选功能：
- `image-processing`: 图像处理功能（OpenCV、libjpeg等）
- `usb-support`: USB设备支持（libusb）
- `serial-support`: 串口设备支持（boost-asio）
- `network-support`: 网络设备支持（curl、openssl）
- `testing`: 测试框架（gtest、gmock）

## 持续集成

项目配置了GitHub Actions自动构建，支持：
- Windows (x64, x86, ARM64)
- macOS (x86_64, ARM64)
- Linux (x86_64)
- Android (armeabi-v7a, arm64-v8a, x86, x86_64)

每次推送和PR都会触发自动构建和测试。

## 文档

- [快速入门](docs/quick_start.md) - 快速上手指南
- [架构设计](docs/architecture.md) - 系统架构说明
- [API参考](docs/api_reference.md) - 完整API文档
- [最佳实践](docs/best_practices.md) - 开发最佳实践
- [迁移指南](docs/migration_guide.md) - 版本迁移指南

## 版本历史

### v1.0.0 (2024)
- 🎉 首次发布
- ✅ 支持Windows、macOS、Linux平台
- ✅ Python和C/C++绑定
- ✅ 基本设备通信功能
- ✅ 图像处理功能

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 [MIT许可证](LICENSE)。

## 技术支持

- **作者**: RBQ
- **问题反馈**: [GitHub Issues]
- **邮箱**: [联系邮箱]
- **文档**: [在线文档地址]

## 致谢

感谢所有为这个项目做出贡献的开发者和用户。

---

**注意**: 这是一个活跃开发的项目，API可能会有变化。建议在生产环境使用前仔细测试。