from enum import IntEnum

class ConnectionStatus(IntEnum):
    """连接状态枚举类（整数型）

    定义了连接过程中可能的状态。
    
    Attributes:
        DISCONNECTED: 已断开连接或未连接，默认为该状态
        CONNECTING: 正在连接
        CONNECTED: 已连接
        DISCONNECTING: 正在断开连接
    """
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    DISCONNECTING = 3
    CONNECT_FAIL = 4
