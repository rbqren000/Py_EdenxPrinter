"""Logo数据包处理类

这个模块实现了Logo数据的分包传输功能，支持数据分割、进度跟踪和数据包格式化。

作者: RBQ
日期: 2025-06-18
"""

import time
from typing import Optional

from ..data.logo_data import LogoData
from .base_packet import BasePacket
from ..transport.protocol import SOH, STX, STX_A, STX_B, STX_C, STX_D, STX_E, PACKET_HEAD_LEN, PACKET_HEAD_XOR_LEN, CRC_LEN
from ..utils.crc16 import CRC16
from .base_packet import BasePacket

class LogoDataPacket(BasePacket):
    """
    Logo数据包处理类

    这个类用于处理Logo数据的分包传输，支持不同帧头类型的数据包封装。
    """

    def __init__(self):
        super().__init__()
        self.data: Optional[bytes] = None              # 原始数据
        self.fh: int = SOH                             # 当前帧头标志

        self.total_data_len: int = 0                   # 原始数据总长度（字节）
        self.total_packet_count: int = 0               # 总分包数量
        self.index: int = -1                           # 当前包序号

        self.useful_packet_data_length: int = 124      # 每包有效载荷长度（不含帧头等开销）
        self.full_packet_data_len: int = 0             # 每个完整包的总长度（含头部、校验等）

        self.progress: float = 0.0                     # 当前进度（百分比）
        self.progress_precision: int = 2               # 进度显示的小数位数

        self.start_time: float = 0.0                   # 起始时间戳
        self.current_time: float = 0.0                 # 当前时间戳
        self.last_invalidate_progress_time: float = 0.0  # 上次刷新进度时间

    def set(self, logo_data: LogoData, fh: int = STX_E) -> None:
        """
        设置 logo 数据及帧头类型，初始化分包计算。
        """
        self.clear()
        self.data = logo_data.data
        self.fh = fh

        # 不同帧头对应不同包长 & 显示精度
        self.useful_packet_data_length, self.progress_precision = {
            SOH: (128, 2),
            STX: (512, 1),
            STX_A: (1024, 0),
            STX_B: (2048, 0),
            STX_C: (5120, 0),
            STX_D: (10240, 0),
            STX_E: (124, 2),
        }.get(fh, (124, 2))

        self.full_packet_data_len = (
            self.useful_packet_data_length
            + PACKET_HEAD_LEN
            + PACKET_HEAD_XOR_LEN
            + CRC_LEN
        )

        self.total_data_len = logo_data.data_length
        self.total_packet_count = (
            self.total_data_len // self.useful_packet_data_length
            + (1 if self.total_data_len % self.useful_packet_data_length else 0)
        )

        self.index = -1
        self.progress = 0.0
        self.start_time = 0.0
        self.current_time = 0.0

    def clear(self) -> None:
        """
        清除内部状态和数据
        """
        super().clear()
        self.data = None
        self.fh = SOH
        self.total_data_len = 0
        self.total_packet_count = 0
        self.index = -1
        self.useful_packet_data_length = 124
        self.full_packet_data_len = 0
        self.progress = 0.0
        self.start_time = 0.0
        self.current_time = 0.0
        self.last_invalidate_progress_time = 0.0

    def has_data(self) -> bool:
        """当前是否加载了待发送数据"""
        return bool(self.data and len(self.data) > 0)

    def has_next_packet(self) -> bool:
        """是否还有下一包可发送"""
        return self.data is not None and self.index + 1 < self.total_packet_count

    def get_current_packet(self) -> Optional[bytes]:
        """获取当前索引位置的数据包（未前进）"""
        if self.data is None or self.index < 0:
            return None
        return self._make_packet_at(self.index)

    def get_next_packet(self) -> Optional[bytes]:
        """获取下一包数据（索引自增）"""
        if not self.has_next_packet():
            return None
        self.index += 1
        return self._make_packet_at(self.index)

    def _make_packet_at(self, index: int) -> bytes:
        """
        构造指定索引位置的包，末包不足自动补 0x1A
        """
        offset = index * self.useful_packet_data_length
        end = min(offset + self.useful_packet_data_length, self.total_data_len)
        chunk = self.data[offset:end]
        if len(chunk) < self.useful_packet_data_length:
            chunk += bytes([0x1A] * (self.useful_packet_data_length - len(chunk)))
        return chunk

    def packet_format(self, data: bytes) -> bytes:
        """
        将数据封装成完整传输包：帧头 + 异或字节 + 数据 + CRC
        """
        buf = bytearray(self.full_packet_data_len)
        pos = 0
        buf[pos] = self.fh
        pos += 1
        buf[pos] = (~self.fh) & 0xFF
        pos += 1
        buf[pos : pos + len(data)] = data
        pos += len(data)
        crc = CRC16.crc16_calc(buf[:pos])
        buf[pos] = (crc >> 8) & 0xFF
        buf[pos + 1] = crc & 0xFF
        return bytes(buf)

    def invalidate_progress(self) -> bool:
        """
        计算当前进度是否发生变化或超过 1 秒未刷新
        返回 True 表示需要更新 UI
        """
        if self.total_packet_count == 0:
            return False

        multiplier = 10 ** self.progress_precision
        raw = (self.index / self.total_packet_count) * 100
        new_progress = round(raw * multiplier) / multiplier
        now = time.time()

        if new_progress != self.progress or (now - self.last_invalidate_progress_time) >= 1.0:
            self.progress = new_progress
            self.last_invalidate_progress_time = now
            return True
        return False

    def get_progress(self) -> int:
        """获取整数进度百分比（向下取整）"""
        return int(self.progress)
