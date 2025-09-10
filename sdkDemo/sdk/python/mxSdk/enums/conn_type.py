from enum import IntFlag

class ConnType(IntFlag):
    """连接类型枚举类
    
    定义了连接过程中可能的连接类型。
    
    Attributes:
        NONE    : 无连接
        BLE     : 蓝牙低功耗
        CLASSIC : 经典蓝牙
        WIFI    : WiFi连接
        AP      : AP热点
        USB     : USB连接
        SERIAL  : 串口连接
    """
    NONE    = 0b00000000  # 无连接
    BLE     = 0b00000001  # 蓝牙低功耗
    CLASSIC = 0b00000010  # 经典蓝牙
    WIFI    = 0b00000100  # WiFi连接
    AP      = 0b00001000  # AP热点
    USB     = 0b00010000  # USB连接
    SERIAL  = 0b00100000  # 串口连接

    def __str__(self) -> str:
        if self == ConnType.BLE:
            return "BLE"
        elif self == ConnType.CLASSIC:
            return "经典蓝牙"
        elif self == ConnType.WIFI:
            return "WiFi"
        elif self == ConnType.AP:
            return "AP"
        elif self == ConnType.USB:
            return "USB"
        elif self == ConnType.SERIAL:
            return "串口"
        elif self == ConnType.NONE:
            return "None"
        else:
            return " | ".join(
                name for name, member in ConnType.__members__.items()
                if member in self and member != ConnType.NONE
            )

    def __repr__(self) -> str:
        return f"ConnType.{str(self)}"
