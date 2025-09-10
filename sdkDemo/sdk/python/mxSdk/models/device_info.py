from dataclasses import dataclass, asdict
from typing import Optional, Set
import hashlib
import json
from ..enums.conn_type import ConnType

@dataclass
class DeviceInfo:

    name: str                                   # 设备名称（显示用）
    conn_type: ConnType                         # 保存当前连接类型
    supported_conn_types: int = 0               #支持的全部类型
    device_id: Optional[str] = None             # 设备 ID

    # USB 设备参数'
    usb_manufacturer: Optional[str] = None      # USB厂商名称（来自设备描述符）
    usb_product: Optional[str] = None           # USB产品名称（来自设备描述符）
    usb_path: Optional[str] = None              # USB设备系统路径（如 /dev/ttyUSB0）
    usb_serial_number: Optional[str] = None     # USB 序列号（来自设备描述符）
    vendor_id: Optional[int] = None            # 厂商 ID
    product_id: Optional[int] = None           # 产品 ID
    is_virtual: bool = False                   # 是否为虚拟设备（如虚拟串口）
    # USB 连接参数
    interface_number: Optional[int] = None     # USB接口号，默认使用第一个接口
    endpoint_in: Optional[int] = None          # 输入端点，默认自动查找
    endpoint_out: Optional[int] = None         # 输出端点，默认自动查找
    usb_read_timeout: Optional[int] = 1000     # USB读取超时时间（毫秒），默认1秒
    usb_write_timeout: Optional[int] = 1000    # USB写入超时时间（毫秒），默认1秒
    # USB 拓展信息（高级）
    usb_bus_number: Optional[int] = None               # USB总线号（如Bus 001），用于物理定位设备
    usb_device_address: Optional[int] = None           # 设备地址（如Device 002），配合bus号唯一标识设备
    usb_interface_class: Optional[int] = None          # USB接口类（如0x07表示打印机，0x03表示HID）
    usb_interface_subclass: Optional[int] = None       # USB接口子类，用于进一步分类设备类型
    usb_interface_protocol: Optional[int] = None       # USB协议号（配合类/子类判断具体设备）
    usb_configuration_value: Optional[int] = None      # 当前激活的USB配置编号（多配置设备常见）
    usb_driver: Optional[str] = None                   # 系统驱动名称（如usbserial、cdc_acm等）
    usb_speed: Optional[str] = None                    # USB通信速度：low, full, high, super（1.1~3.0+）
    #usb附加属性
    device_class: Optional[int] = None            # 设备类
    device_subclass: Optional[int] = None         # 设备子类
    device_protocol: Optional[int] = None         # 设备协议

    # 串口参数
    is_usb_serial: bool = False                 # 是否为USB串口
    serial_port_path: Optional[str] = None      # 串口路径，如 /dev/ttyUSB0、COM3
    serial_number: Optional[str] = None         # 串口设备的序列号（如果系统提供）
    baudrate: Optional[int] = 115200            # 波特率，默认115200
    data_bits: Optional[int] = 8                # 数据位，默认8位
    stop_bits: Optional[float] = 1.0            # 停止位，默认1位
    parity: Optional[str] = 'N'                 # 校验位：'N'(无), 'E'(偶), 'O'(奇), 'M'(标记), 'S'(空格)
    # 串口流控参数（一般使用默认值）
    xonxoff: Optional[bool] = False             # 软件流控，默认关闭
    rtscts: Optional[bool] = False              # RTS/CTS硬件流控，默认关闭
    dsrdtr: Optional[bool] = False              # DSR/DTR硬件流控，默认关闭
    # 串口超时参数
    read_timeout: Optional[float] = 1.0         # 读取超时时间（秒），默认1秒
    write_timeout: Optional[float] = 1.0        # 写入超时时间（秒），默认1秒
    inter_byte_timeout: Optional[float] = None  # 字符间隔超时时间（秒），默认None（不使用）
    exclusive: Optional[bool] = None            # 是否独占访问，默认False（不独占）

    # BLE / 经典蓝牙参数
    mac_address: Optional[str] = None           # 蓝牙 MAC 地址
    rssi: Optional[int] = None                  # 蓝牙信号强度（RSSI）
    ble_name: Optional[str] = None              # BLE 广播设备名称
    ble_services: Optional[Set[str]] = None     # GATT 服务 UUID 集合
    pairing_required: Optional[bool] = None     # 是否需要配对

    # Wi-Fi / AP 相关
    ip_address: Optional[str] = None            # IP 地址（Wi-Fi / AP 模式）
    port: Optional[int] = None                  # 端口号（默认80）
    ssid: Optional[str] = None                  # Wi-Fi 网络名称
    password: Optional[str] = None              # Wi-Fi 网络密码

    # 固件信息
    firmware_version: Optional[str] = None
    battery_level: Optional[int] = None

    #打印相关的设置参数
    horizontalDirection: Optional[int] = None
    verticalDirection: Optional[int] = None

    oldHorizontalDirection: Optional[int] = None
    oldVerticalDirection: Optional[int] = None

    def __post_init__(self):
        if not self.device_id:
            self.device_id = self._generate_device_id(
                self.conn_type,
                usb_path=self.usb_path,
                usb_serial_number=self.usb_serial_number,
                vendor_id=self.vendor_id,
                product_id=self.product_id,
                serial_port_path=self.serial_port_path,
                serial_number=self.serial_number,
                mac_address=self.mac_address,
                ip_address=self.ip_address
            )
        if not self.name:
            self.name = self._get_name(
                conn_type=self.conn_type,
                usb_product=self.usb_product,
                vendor_id=self.vendor_id,
                product_id=self.product_id,
                serial_port_path=self.serial_port_path,
                ble_name=self.ble_name,
                ip_address=self.ip_address,
                ssid=self.ssid
            )

    @staticmethod
    def _generate_device_id(conn_type: ConnType,
                            usb_path: Optional[str] = None,
                            usb_serial_number: Optional[str] = None,
                            vendor_id: Optional[int] = None,
                            product_id: Optional[int] = None,
                            serial_port_path: Optional[str] = None,
                            serial_number: Optional[str] = None,
                            mac_address: Optional[str] = None,
                            ip_address: Optional[str] = None) -> str:
        prefix = str(conn_type)

        # BLE / CLASSIC 蓝牙
        if ConnType.BLE in conn_type or ConnType.CLASSIC in conn_type:
            if mac_address:
                return f"{prefix}:{mac_address}"

        # USB
        if ConnType.USB in conn_type:
            if vendor_id and product_id and usb_serial_number:
                return f"{prefix}:{vendor_id:04X}-{product_id:04X}-{usb_serial_number}"
            elif usb_path:
                return f"{prefix}:{usb_path}"

        # 串口
        if ConnType.SERIAL in conn_type:
            if serial_port_path:
                return f"{prefix}:{serial_port_path}"
            elif serial_number:
                return f"{prefix}:{serial_number}"

        # Wi-Fi 或 AP
        if (ConnType.WIFI in conn_type or ConnType.AP in conn_type) and ip_address:
            return f"{prefix}:{ip_address}"

        # 默认兜底
        fingerprint = f"{prefix}:{mac_address or usb_serial_number or serial_number or usb_path or serial_port_path or ip_address or ''}"
        digest = hashlib.md5(fingerprint.encode()).hexdigest()[:8]
        return f"{prefix}:anon-{digest}"

    @staticmethod
    def _get_name(conn_type: ConnType,
                usb_product: Optional[str] = None,
                vendor_id: Optional[int] = None,
                product_id: Optional[int] = None,
                serial_port_path: Optional[str] = None,
                ble_name: Optional[str] = None,
                ip_address: Optional[str] = None,
                ssid: Optional[str] = None) -> str:
        """获取设备名称"""
        if conn_type == ConnType.USB:
            return usb_product or f"USB-{vendor_id:04X}-{product_id:04X}" if vendor_id and product_id else "USB设备"
        if conn_type == ConnType.SERIAL:
            return serial_port_path or "串口设备"
        if conn_type == ConnType.BLE or conn_type == ConnType.CLASSIC:
            return ble_name or "蓝牙设备"
        if conn_type == ConnType.WIFI or conn_type == ConnType.AP:
            return ip_address or ssid or "网络设备"
        return "未知设备"


    #判断设备相等
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeviceInfo):
            return False
        return self.device_id == other.device_id

    #获取设备哈希值
    def __hash__(self) -> int:
        return hash(self.device_id)
    
    #返回设备信息字符串 各属性用","隔开
    def __repr__(self) -> str:
        """返回设备信息字符串"""
        return json.dumps(asdict(self), ensure_ascii=False)