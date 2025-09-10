"""
日志级别枚举定义
"""
from enum import IntEnum

class LogLevel(IntEnum):
    """
    日志级别枚举类，定义了不同的日志级别
    """
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    def __str__(self) -> str:
        """返回日志级别的字符串表示"""
        return self.name

    def __repr__(self) -> str:
        """返回日志级别的程序表示"""
        return f"{self.__class__.__name__}.{self.name}"
