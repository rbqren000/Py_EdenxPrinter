"""PyMxSdk - Python版本的MxSdk库

这是从Objective-C重写的Python版本，提供了完整的数据处理、图像处理和通信协议功能。

作者: RBQ
版本: 1.0.1
Python版本: 3.9+
"""

# 版本信息
__version__ = "1.0.1"
__author__ = "RBQ"

# 导入基础模型
from .models import (
    DataObj,
    Command,
    DataObjCallback,
    CommandCallback,
    DataObjContext,
    CommandContext
)

# 导入连接管理器和工厂
from .connection.factory import ConnectionStrategyFactory
from .connection.strategy import ConnectionStrategy, DeviceInfo, ConnectionStatus
from .connection.usb import UsbConnectionStrategy
from .connection.serial import SerialConnectionStrategy
from .connection.manager import ConnectManager
from .connection.parameters import *
from .packets import *
from .enums import *

__all__ = [
    'ConnectionStrategyFactory',
    'ConnectionStrategy',
    'DeviceInfo',
    'ConnectionStatus',
    'ConnectManager',
    'UsbConnectionStrategy',
    'SerialConnectionStrategy',
    # 枚举
    'ConnType',
    'ConnectionStatus',
    'DataSendType',
    'FirmwareType',
    'OpCode',
    'PaperType',
    'RowLayoutDirection',
    # 数据类型
    'MultiRowData',
    'LogoData',
    'OtaData',
    'PrintData',
    # 工厂类
    'DataFactory',
    'PacketFactory',
    # 工具类
    'RBQLog',
    'DataUtils',
    'ImageUtils',
    'FileUtils',
    # OpenCV工具
    'OpenCVUtils',
    'ImageProcessor',
    # 数据包
    'BasePacket',
    'CommandPacket',
    'DataPacket',
    'ResponsePacket'
]