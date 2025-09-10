#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BasePacket - 基础数据包类
描述: 数据包处理的基础类，提供通用的数据包解析功能

作者: RBQ
日期: 2025-06-18
"""

from ..transport.protocol import C, NAK, EOT


class BasePacket:
    def __init__(self):
        self.start = False

    def clear(self) -> None:
        self.start = False

    def is_request_data(self, data: bytes) -> bool:
        if not data or not self.start:
            return False

        if len(data) == 1 and data[0] == C:
            return True

        try:
            if data.decode('utf-8').strip().lower() == 'c':
                return True
        except UnicodeDecodeError:
            pass

        has_c = False
        for byte in data:
            if byte == C:
                has_c = True
            elif byte == NAK or byte == EOT:
                return False
        return has_c

    def is_nak(self, data: bytes) -> bool:
        if not data or not self.start:
            return False

        if len(data) == 1 and data[0] == NAK:
            return True

        try:
            if data.decode('utf-8').strip().lower() == 'r':
                return True
        except UnicodeDecodeError:
            pass

        has_nak = False
        for byte in data:
            if byte == EOT:
                return False
            if byte == NAK:
                has_nak = True
        return has_nak

    def is_eot(self, data: bytes) -> bool:
        if not data or not self.start:
            return False

        if len(data) == 1 and data[0] == EOT:
            return True

        try:
            if data.decode('utf-8').strip().lower() == 'd':
                return True
        except UnicodeDecodeError:
            pass

        return EOT in data
