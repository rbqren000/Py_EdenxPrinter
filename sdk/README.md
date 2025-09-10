# Edenx Printer SDK

一个专为Edenx打印机设计的Python SDK，提供设备通信、图像处理和数据管理功能。

## 主要特性

- 🔌 **多种连接方式**: 支持USB和串口连接
- 🖼️ **图像处理**: 基于OpenCV的图像扫描、分析和处理
- 📦 **数据管理**: 完整的数据包、命令和响应处理
- 🏭 **工厂模式**: 使用工厂模式创建连接策略和数据对象
- 🔄 **异步通信**: 支持异步数据传输和回调处理
- 🛠️ **易于集成**: 简单的API设计，详细的模块化结构

## 项目结构

```
sdk/
├── README.md              # 项目说明文档
├── __init__.py            # Python包初始化文件
├── docs/                  # 文档目录
├── examples/              # 示例代码
│   └── python/           # Python示例
├── python/              # Python SDK
│   ├── __init__.py     # Python包初始化
│   ├── mxSdk/          # 核心Python模块
│   │   ├── __init__.py # 模块初始化
│   │   ├── connection/ # 连接管理模块
│   │   │   ├── factory.py      # 连接策略工厂
│   │   │   ├── strategy.py    # 连接策略基类
│   │   │   ├── usb.py         # USB连接实现
│   │   │   └── serial.py      # 串口连接实现
│   │   ├── data/       # 数据类型模块
│   │   │   ├── logo_data.py       # 标志数据
│   │   │   ├── logo_image.py      # 标志图像
│   │   │   ├── row_data.py        # 行数据
│   │   │   ├── row_image.py       # 行图像
│   │   │   ├── multi_row_data.py  # 多行数据
│   │   │   └── multi_row_image.py # 多行图像
│   │   ├── enums/      # 枚举定义模块
│   │   │   ├── conn_type.py           # 连接类型
│   │   │   ├── connection_status.py   # 连接状态
│   │   │   ├── data_send_type.py      # 数据发送类型
│   │   │   ├── event_type.py          # 事件类型
│   │   │   ├── firmware_type.py       # 固件类型
│   │   │   ├── op_code.py             # 操作码
│   │   │   ├── paper_type.py          # 纸张类型
│   │   │   └── row_layout_direction.py # 行布局方向
│   │   ├── factories/  # 工厂类模块
│   │   │   ├── logo_data_factory.py      # 标志数据工厂
│   │   │   └── multi_row_data_factory.py # 多行数据工厂
│   │   ├── models/     # 模型类模块
│   │   │   ├── command.py         # 命令模型
│   │   │   ├── command_callback.py # 命令回调
│   │   │   ├── command_context.py # 命令上下文
│   │   │   ├── data_obj.py        # 数据对象
│   │   │   ├── data_obj_callback.py # 数据对象回调
│   │   │   └── data_obj_context.py # 数据对象上下文
│   │   ├── opencv/     # 图像处理模块
│   │   │   ├── base_utils.py         # 基础工具
│   │   │   ├── background_cleaner.py # 背景清理
│   │   │   ├── image_analysis.py     # 图像分析
│   │   │   ├── image_effects.py      # 图像效果
│   │   │   ├── image_geometry.py     # 图像几何
│   │   │   ├── image_scanner.py      # 图像扫描
│   │   │   └── opencv_utils.py       # OpenCV工具
│   │   ├── packets/    # 数据包模块
│   │   ├── transport/  # 传输模块
│   │   └── utils/      # 工具类模块
│   └── mxSdk_bin/      # 编译后的二进制模块
├── src/                  # C/C++源码实现
│   └── mx_printer.c     # 核心实现
└── tools/               # 构建和开发工具
    └── build_sdk.py     # SDK构建脚本
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

```python
from sdk.python import mxSdk
from mxSdk.connection.factory import ConnectionStrategyFactory
from mxSdk.enums import ConnType, ConnectionStatus
from mxSdk.data import LogoData

# 创建连接策略工厂
factory = ConnectionStrategyFactory()

# 创建USB连接策略
usb_strategy = factory.create_strategy(ConnType.USB)

# 连接设备
if usb_strategy.connect():
    print("设备连接成功")
    
    # 创建数据对象
    logo_data = LogoData()
    
    # 发送数据
    usb_strategy.write_data(logo_data.to_bytes())
    
    # 断开连接
    usb_strategy.disconnect()
else:
    print("设备连接失败")
```

### 图像处理

```python
from mxSdk.opencv import ImageScanner, ImageProcessor

# 创建图像扫描器
scanner = ImageScanner()

# 扫描图像
image = scanner.scan_image("path/to/image.jpg")

# 创建图像处理器
processor = ImageProcessor()

# 处理图像
processed_image = processor.process_image(image)
```

## API 概览

### 核心模块

#### 连接管理 (connection)
- `ConnectionStrategyFactory`: 创建连接策略的工厂类
- `ConnectionStrategy`: 连接策略基类
- `UsbConnectionStrategy`: USB连接实现
- `SerialConnectionStrategy`: 串口连接实现

#### 数据类型 (data)
- `LogoData`: 打印机默认打印，既logo数据类
- `LogoImage`: 打印机默认打印，既logo图像类
- `RowData`: 单行数据类
- `RowImage`: 单行图像类
- `MultiRowData`: 多行数据类
- `MultiRowImage`: 多行图像类

#### 枚举定义 (enums)
- `ConnType`: 连接类型枚举
- `ConnectionStatus`: 连接状态枚举
- `DataSendType`: 数据发送类型枚举
- `FirmwareType`: 固件类型枚举
- `OpCode`: 操作码枚举
- `PaperType`: 纸张类型枚举
- `RowLayoutDirection`: 行布局方向枚举

#### 工厂类 (factories)
- `LogoDataFactory`: 标志数据工厂类
- `MultiRowDataFactory`: 多行数据工厂类

#### 模型类 (models)
- `Command`: 命令模型类
- `CommandCallback`: 命令回调类
- `CommandContext`: 命令上下文类
- `DataObj`: 数据对象类
- `DataObjCallback`: 数据对象回调类
- `DataObjContext`: 数据对象上下文类

#### 图像处理 (opencv)
- `ImageScanner`: 图像扫描器
- `ImageProcessor`: 图像处理器
- `BaseUtils`: 基础工具类
- `BackgroundCleaner`: 背景清理器
- `ImageAnalysis`: 图像分析工具
- `ImageEffects`: 图像效果工具
- `ImageGeometry`: 图像几何工具

## 构建SDK

### 使用构建脚本

```bash
# 构建当前平台
python3 sdk/tools/build_sdk.py

# 构建特定平台
python3 sdk/tools/build_sdk.py --platform macos/arm64

# 构建所有平台
python3 sdk/tools/build_sdk.py --all
```

### 编译Python模块为二进制

```bash
# 使用项目提供的脚本
python3 scripts/build_py_to_bin.py
```

## 支持的平台

| 操作系统 | 架构 | 状态 |
|---------|------|------|
| macOS | x86_64, ARM64 | ✅ 支持 |
| Linux | x86_64, ARM64 | ✅ 支持 |
| Windows | x64, x86 | ✅ 支持 |

## 依赖管理

项目使用requirements.txt管理Python依赖，主要依赖包括：
- PyQt5: GUI框架
- Pillow: 图像处理
- pyserial: 串口通信
- opencv-python: 图像处理
- numpy: 数值计算
- cython: Python到C的编译器

## 持续集成

项目配置了GitHub Actions自动构建，支持：
- macOS (x86_64, ARM64)
- Linux (x86_64)

每次推送和PR都会触发自动构建和测试。

## 版本历史

### v1.0.0 (2025)
- 🎉 首次发布
- ✅ 支持macOS和Linux平台
- ✅ Python绑定
- ✅ USB和串口通信功能
- ✅ 图像处理功能
- ✅ 数据包处理

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
- **项目创建时间**: 2025
- **Python版本**: 3.9

---

**注意**: 这是一个活跃开发的项目，API可能会有变化。建议在生产环境使用前仔细测试。