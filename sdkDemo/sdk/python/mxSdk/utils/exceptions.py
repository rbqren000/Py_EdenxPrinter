#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常类定义

定义了SDK中使用的各种异常类。

作者: RBQ
版本: 1.0.0
创建时间: 2025
Python版本: 3.9+
"""


class ConnectionException(Exception):
    """连接异常
    
    当设备连接出现问题时抛出此异常。
    """
    
    def __init__(self, message: str = "连接异常", error_code: int = None):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
    
    def __str__(self):
        if self.error_code:
            return f"ConnectionException({self.error_code}): {self.message}"
        return f"ConnectionException: {self.message}"


class TimeoutException(Exception):
    """超时异常
    
    当操作超时时抛出此异常。
    """
    
    def __init__(self, message: str = "操作超时", timeout_seconds: float = None):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds
        self.message = message
    
    def __str__(self):
        if self.timeout_seconds:
            return f"TimeoutException({self.timeout_seconds}s): {self.message}"
        return f"TimeoutException: {self.message}"


class DataTransmissionException(Exception):
    """数据传输异常
    
    当数据传输出现问题时抛出此异常。
    """
    
    def __init__(self, message: str = "数据传输异常", data_type: str = None):
        super().__init__(message)
        self.data_type = data_type
        self.message = message
    
    def __str__(self):
        if self.data_type:
            return f"DataTransmissionException({self.data_type}): {self.message}"
        return f"DataTransmissionException: {self.message}"


class DeviceNotFoundException(ConnectionException):
    """设备未找到异常
    
    当无法找到指定设备时抛出此异常。
    """
    
    def __init__(self, message: str = "设备未找到", device_id: str = None):
        super().__init__(message)
        self.device_id = device_id
    
    def __str__(self):
        if self.device_id:
            return f"DeviceNotFoundException({self.device_id}): {self.message}"
        return f"DeviceNotFoundException: {self.message}"


class InvalidParameterException(Exception):
    """无效参数异常
    
    当传入的参数无效时抛出此异常。
    """
    
    def __init__(self, message: str = "无效参数", parameter_name: str = None):
        super().__init__(message)
        self.parameter_name = parameter_name
        self.message = message
    
    def __str__(self):
        if self.parameter_name:
            return f"InvalidParameterException({self.parameter_name}): {self.message}"
        return f"InvalidParameterException: {self.message}"