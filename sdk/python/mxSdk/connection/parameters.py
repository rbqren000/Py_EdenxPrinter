# -*- coding: utf-8 -*-
"""
连接参数类

定义了不同连接类型的参数类，用于传递连接所需的配置信息。

作者: RBQ
版本: 1.0.0
创建时间: 2025
Python版本: 3.9+
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class BaseConnectionParameters:
    """连接参数基类

    所有连接参数类的基类，包含通用参数。

    Attributes:
        timeout: 连接超时时间（秒）
        auto_reconnect: 是否自动重连
        extra_params: 额外参数字典
    """
    timeout: float = 5.0
    auto_reconnect: bool = False
    extra_params: Dict[str, Any] = field(default_factory=dict)

# 经典蓝牙
@dataclass
class ClassicBluetoothConnectionParameters(BaseConnectionParameters):
    """经典蓝牙连接参数

    经典蓝牙连接特有的参数。

    Attributes:
        address: 蓝牙地址
        port: 端口
        channel: 通道
        uuid: 服务UUID
    """
    address: Optional[str] = None
    port: int = 1
    channel: int = 1
    uuid: Optional[str] = None

# BLE连接
@dataclass
class BleConnectionParameters(BaseConnectionParameters):
    """BLE连接参数

    蓝牙低功耗连接特有的参数。

    Attributes:
        address_type: 地址类型
        service_uuid: 服务UUID
        char_uuid: 特征UUID
        mtu: 最大传输单元
        scan_timeout: 扫描超时时间（秒）
    """
    address_type: str = 'public'  # public, random
    service_uuid: Optional[str] = None
    char_uuid: Optional[str] = None
    mtu: int = 512
    scan_timeout: float = 10.0

# WIFI连接
@dataclass
class WifiConnectionParameters(BaseConnectionParameters):
    """WIFI连接参数

    WIFI连接特有的参数。

    Attributes:
        ssid: 网络名称
        password: 网络密码
    """
    ssid: Optional[str] = None
    password: Optional[str] = None

# AP连接
@dataclass
class ApConnectionParameters(BaseConnectionParameters):
    """AP连接参数

    AP连接特有的参数。

    Attributes:
        ssid: 网络名称
        password: 网络密码
    """
    ssid: Optional[str] = None
    password: Optional[str] = None

@dataclass
class SerialConnectionParameters(BaseConnectionParameters):
    """串口连接参数

    串口连接特有的参数。

    Attributes:
        port: 串口名称
        baudrate: 波特率
        bytesize: 数据位
        parity: 校验位
        stopbits: 停止位
        xonxoff: 是否启用软件流控
        rtscts: 是否启用RTS/CTS流控
        dsrdtr: 是否启用DSR/DTR流控
        read_timeout: 读取超时时间（秒）
        write_timeout: 写入超时时间（秒）
    """
    port: Optional[str] = None
    baudrate: int = 115200
    bytesize: int = 8
    parity: str = 'N'  # N-无校验，E-偶校验，O-奇校验，M-标记，S-空格
    stopbits: float = 1
    xonxoff: bool = False
    rtscts: bool = False
    dsrdtr: bool = False
    read_timeout: float = 1.0
    write_timeout: float = 1.0

@dataclass
class UsbConnectionParameters(BaseConnectionParameters):
    """USB连接参数

    USB连接特有的参数。

    Attributes:
        vendor_id: 厂商ID
        product_id: 产品ID
        interface_number: 接口号
        endpoint_in: 输入端点
        endpoint_out: 输出端点
        read_timeout: 读取超时时间（毫秒）
        write_timeout: 写入超时时间（毫秒）
    """
    vendor_id: Optional[int] = None
    product_id: Optional[int] = None
    interface_number: Optional[int] = None
    endpoint_in: Optional[int] = None
    endpoint_out: Optional[int] = None
    read_timeout: int = 1000
    write_timeout: int = 1000


@dataclass
class BleConnectionParameters(BaseConnectionParameters):
    """BLE连接参数

    蓝牙低功耗连接特有的参数。

    Attributes:
        address_type: 地址类型
        service_uuid: 服务UUID
        char_uuid: 特征UUID
        mtu: 最大传输单元
        scan_timeout: 扫描超时时间（秒）
    """
    address_type: str = 'public'  # public, random
    service_uuid: Optional[str] = None
    char_uuid: Optional[str] = None
    mtu: int = 512
    scan_timeout: float = 10.0


# 类型别名，用于向后兼容
ConnectionParameters = BaseConnectionParameters