from enum import IntFlag

class FirmwareType(IntFlag):
    """固件类型枚举

    用来表示打印机上可升级的固件类型。使用位运算来表示不同的固件类型，
    每个位代表一种固件。这允许将多个固件类型组合在一起（使用位或运算）。

    Attributes:
        MCU (int): MCU芯片固件 (0x100)
        WIFI (int): WiFi芯片固件 (0x200)
    """
    MCU = 0b00000001 << 8   # 0x100
    WIFI = 0b00000001 << 9  # 0x200
    # 预留6位用于未来扩展

    def __str__(self) -> str:
        """返回格式化的固件类型描述"""
        if self == FirmwareType.MCU:
            return "MCU"
        elif self == FirmwareType.WIFI:
            return "WIFI"
        elif self == 0:
            return "None"
        else:
            return " | ".join(name for name, member in FirmwareType.__members__.items()
                            if member in self)

    def __repr__(self) -> str:
        """返回枚举值的程序表示形式"""
        return f"FirmwareType.{str(self)}"