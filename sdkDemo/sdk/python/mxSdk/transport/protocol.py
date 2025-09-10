"""传输协议常量定义

这个模块定义了数据包传输中使用的协议常量，包括帧头类型和控制字符。
"""

# 帧头常量
SOH = 0x18      # Start of Header - 指令码 128byte
STX = 0x19      # Start of Text - 指令码 512byte
STX_A = 0x1A    # Start of Text A - 指令码 1k
STX_B = 0x1B    # Start of Text B - 指令码 2k
STX_C = 0x1C    # Start of Text C - 指令码 5k
STX_D = 0x1D    # Start of Text D - 指令码 10k
STX_E = 0x1E    # Start of Text E - 指令码 预留 124byte

# 控制字符常量
C = 0x4E        # 'N' - 请求数据相关指令
NAK = 0x52      # 'R' - 重传当前数据包请求命令
EOT = 0x44      # 'D' - 接收完毕，结束发送

# 数据包常量
PACKET_HEAD_LEN = 1         # 数据包头长度
PACKET_HEAD_XOR_LEN = 1     # 数据包头异或长度
CRC_LEN = 2                 # CRC校验长度
MAX_ERRORS = 10             # 最大错误（无应答）包数