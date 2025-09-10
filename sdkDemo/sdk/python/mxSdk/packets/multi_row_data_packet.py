#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiRowDataPacket - 多行数据包类

对应Objective-C中的MultiRowDataPacket类，用于处理多行图像数据的分包传输。
支持按行分割数据、进度跟踪和数据包格式化。

作者: RBQ
日期: 2025-06-18
"""

import time
from typing import Optional, List

from ..data.multi_row_data import MultiRowData
from ..data.row_data import RowData
from .base_packet import BasePacket
from ..transport.protocol import SOH, STX, STX_A, STX_B, STX_C, STX_D, STX_E, PACKET_HEAD_LEN, PACKET_HEAD_XOR_LEN, CRC_LEN
from ..utils.crc16 import CRC16
from ..utils.rbq_log import RBQLog

class MultiRowDataPacket(BasePacket):
    """
    多行图像数据打包类

    支持逐行数据打包、跨行缓存、CRC 封装、进度管理等
    """

    def __init__(self):
        super().__init__()
        self.compress: int = 1  # 默认压缩
        self.fh: int = SOH

        self.multi_row_image_data: Optional[MultiRowData] = None
        self.current_single_row_image_data = None
        self.current_row_image_byte_data: Optional[bytes] = None

        self.total_data_len = 0
        self.total_packet_count = 0
        self.total_row_count = 0
        self.index = -1

        self.useful_packet_data_length = 124
        self.full_packet_data_len = 0

        self.progress = 0.0
        self.progress_precision = 2

        self.current_row = 0
        self.current_row_data_length = 0
        self.current_row_total_packet_count = 0
        self.index_in_current_row_packet = -1

        self.start_time = 0.0
        self.current_time = 0.0
        self.last_invalidate_progress_time = 0.0

    def set(self, multi_row_data: MultiRowData, fh: int = STX_E):
        """设置多行图像数据和帧头"""
        self.clear()
        self.multi_row_image_data = multi_row_data
        self.compress = multi_row_data.compress_value()
        self.fh = fh

        # 根据帧头类型设定 packet 大小与进度精度
        self.useful_packet_data_length, self.progress_precision = {
            SOH: (128, 2),
            STX: (512, 1),
            STX_A: (1024, 0),
            STX_B: (2048, 0),
            STX_C: (5120, 0),
            STX_D: (10240, 0),
            STX_E: (124, 2)
        }.get(fh, (124, 2))

        self.full_packet_data_len = self.useful_packet_data_length + PACKET_HEAD_LEN + PACKET_HEAD_XOR_LEN + CRC_LEN
        self.total_data_len = multi_row_data.total_data_length()
        self.total_packet_count = multi_row_data.total_packet_count(self.useful_packet_data_length)
        self.total_row_count = multi_row_data.total_row_count()

        self.index = -1
        self.progress = 0.0

        self.current_row = 0
        self.current_single_row_image_data:RowData = multi_row_data.row_data_with_row_index(self.current_row)
        self.current_row_image_byte_data = self.current_single_row_image_data.data
        self.current_row_data_length = self.current_single_row_image_data.data_length
        self.current_row_total_packet_count = self.current_single_row_image_data.total_packet_count(self.useful_packet_data_length)
        self.index_in_current_row_packet = -1

        self.start_time = 0.0
        self.current_time = 0.0

    def clear(self):
        """清空状态"""
        super().clear()
        self.compress = 1
        self.fh = SOH

        self.multi_row_image_data: Optional[MultiRowData] = None
        self.current_single_row_image_data = None
        self.current_row_image_byte_data = None

        self.total_data_len = 0
        self.total_packet_count = 0
        self.total_row_count = 0
        self.index = -1

        self.useful_packet_data_length = 124
        self.full_packet_data_len = 0
        self.progress = 0.0
        self.progress_precision = 2

        self.current_row = 0
        self.current_row_data_length = 0
        self.current_row_total_packet_count = 0
        self.index_in_current_row_packet = -1

        self.start_time = 0.0
        self.current_time = 0.0
        self.last_invalidate_progress_time = 0.0

    def has_data(self) -> bool:
        """判断是否包含可打包的数据"""
        return self.multi_row_image_data is not None and self.total_data_len > 0

    def get_current_row(self) -> int:
        """获取当前行索引"""
        return self.current_row

    def has_next_packet_with_current_row(self) -> bool:
        """当前行是否还有数据包"""
        return self.current_row_total_packet_count > 0 and (self.index_in_current_row_packet + 1) < self.current_row_total_packet_count

    def has_next_row(self) -> bool:
        """判断是否还有下一行"""
        return self.multi_row_image_data is not None and (self.current_row + 1) < self.total_row_count

    def cursor_move_to_next(self) -> bool:
        """移动游标到下一行"""
        if not self.has_next_row():
            return False

        self.current_row += 1
        self.current_single_row_image_data = self.multi_row_image_data.row_data_with_row_index(self.current_row)
        self.current_row_image_byte_data = self.current_single_row_image_data.data
        self.current_row_data_length = self.current_single_row_image_data.data_length
        self.current_row_total_packet_count = self.current_single_row_image_data.total_packet_count(self.useful_packet_data_length)
        self.index_in_current_row_packet = -1
        return True

    def get_current_packet(self) -> Optional[bytes]:
        """获取当前索引处数据包"""
        if self.current_row_image_byte_data is None:
            return None

        offset = self.index_in_current_row_packet * self.useful_packet_data_length
        end = offset + self.useful_packet_data_length
        chunk = self.current_row_image_byte_data[offset:end]

        if len(chunk) < self.useful_packet_data_length:
            chunk += bytes([0x1A] * (self.useful_packet_data_length - len(chunk)))

        return chunk

    def get_next_packet(self) -> Optional[bytes]:
        """索引推进，获取下一数据包（含填充）"""
        self.index += 1
        self.index_in_current_row_packet += 1

        return self.get_current_packet()

    def packet_format(self, data: bytes) -> bytes:

        hex_data = ' '.join([f'{byte:02X}' for byte in data])
        # RBQLog.log(f'数据包：{hex_data}')

        """数据封装为完整格式：帧头 + 异或 + 数据 + CRC"""
        buf = bytearray(self.full_packet_data_len)
        # 打印 full_packet_data_len长度和data长度
        # RBQLog.log(f'full_packet_data_len: {self.full_packet_data_len}, data长度: {len(data)}')
        pos = 0

        buf[pos] = self.fh
        pos += 1
        buf[pos] = (~self.fh) & 0xFF
        pos += 1
        buf[pos:pos + len(data)] = data
        pos += len(data)

        crc = CRC16.crc16_calc(buf[:pos])
        # 打印crc值
        high_byte = (crc >> 8) & 0xFF
        low_byte = crc & 0xFF
        # RBQLog.log(f'CRC16校验值：{crc:04X}, 高字节: {high_byte:02X}, 低字节: {low_byte:02X}')
        buf[pos] = high_byte
        buf[pos + 1] = low_byte

        # 打印buf长度
        # RBQLog.log(f'封装后的数据包长度：{len(buf)}')
        # 打印buf内容
        # hex_buf = ' '.join([f'{byte:02X}' for byte in buf])
        # RBQLog.log(f'封装后的数据包内容：{hex_buf}')

        # RBQLog.log(f"数据包长度: {len(data)}, 帧头: {self.fh:02X}, CRC: {crc:04X}, 格式化后数据长度: {len(buf)}, full_packet_data_len: {self.full_packet_data_len}")

        return bytes(buf)

    def invalidate_progress(self) -> bool:
        """更新进度状态，是否需要刷新"""
        if self.total_packet_count == 0:
            return False

        now = time.time()
        multiplier = 10 ** self.progress_precision
        raw = (self.index / self.total_packet_count) * 100
        current = round(raw * multiplier) / multiplier

        if current != self.progress or (now - self.last_invalidate_progress_time) >= 1.0:
            self.progress = current
            self.last_invalidate_progress_time = now
            return True

        return False

    def get_progress(self) -> int:
        """获取整数形式进度百分比"""
        return int(self.progress)
    # 可迭代
    def __iter__(self):
        """
        可迭代协议

        实现可迭代协议，使MultiRowDataPacket对象可以在for循环中使用。
        
        Returns:
            MultiRowDataPacket: 当前对象
        """
        return iter(self.multi_row_image_data)