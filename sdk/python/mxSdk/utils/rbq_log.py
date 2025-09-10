#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RBQLog模块提供了一个简单而强大的日志记录工具。
这是对Objective-C RBQLog的Python重新实现，提供了相似的功能，
但采用了更符合Python风格的API设计。
"""

import os
import sys
import logging
import functools
from typing import Any, Optional, Callable, TypeVar, cast, ContextManager
from dataclasses import dataclass
from contextlib import contextmanager
try:
    from .log_level import LogLevel
except ImportError:
    from log_level import LogLevel
from contextlib import contextmanager

F = TypeVar('F', bound=Callable[..., Any])

class SingletonMeta(type):
    """单例元类，确保类只有一个实例"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

@dataclass
class LogContext:
    """日志上下文信息"""
    filename: str
    function: str
    line_number: int
    level: LogLevel
    message: str

class RBQLogFormatter(logging.Formatter):
    """自定义日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        # 优先使用extra中的上下文信息
        context = getattr(record, 'context', None)
        if context and isinstance(context, LogContext):
            record.filename = context.filename
            record.funcName = context.function
            record.lineno = context.line_number
            
        return super().format(record)

class RBQLog(metaclass=SingletonMeta):
    """
    RBQLog提供了一个统一的日志记录接口。
    
    特性:
    - 单例模式确保全局统一的日志配置
    - 支持多种日志级别(DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - 自动记录调用者信息(文件名、函数名、行号)
    - 支持日志文件输出
    - 支持格式化字符串
    - 支持启用/禁用日志输出
    
    使用示例:
    # >>> from rbq_log import RBQLog
    >>> log = RBQLog()
    >>> log.debug("测试消息")
    >>> log.info("用户 %s 登录", "张三")
    
    也可以作为上下文管理器使用:
    >>> with RBQLog().temp_level(LogLevel.ERROR):
    ...     log.debug("这条不会显示")
    ...     log.error("这条会显示")
    """
    
    def __init__(self) -> None:
        """初始化RBQLog"""
        self._enabled: bool = True
        self._logger: Optional[logging.Logger] = None
        self._level: LogLevel = LogLevel.DEBUG
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """配置日志记录器"""
        self._logger = logging.getLogger('RBQLog')
        self._logger.setLevel(logging.DEBUG)  # logger始终使用DEBUG级别
        
        # 清除所有现有的处理器
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)
            handler.close()
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self._level.value)  # handler控制实际的过滤级别
        
        # 设置日志格式
        # formatter = RBQLogFormatter(
        #     'RBQLog: %(asctime)s [%(levelname)s]\n'
        #     '[文件名:%(filename)s]\n'
        #     '[函数名:%(funcName)s]\n'
        #     '[行号:%(lineno)d]\n'
        #     '%(message)s\n'
        # )
        formatter = RBQLogFormatter('RBQLog: %(asctime)s [%(levelname)s] %(message)s')
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # 禁止向上传播到根logger
        self._logger.propagate = False
    
    def _get_caller_context(self, depth: int = 2) -> LogContext:
        """获取调用者信息"""
        frame = sys._getframe(depth)
        try:
            return LogContext(
                filename=os.path.basename(frame.f_code.co_filename),
                function=frame.f_code.co_name,
                line_number=frame.f_lineno,
                level=self._level,
                message=""
            )
        finally:
            del frame  # 显式清理frame引用
    
    def _log(self, level: LogLevel, message: str, *args: Any) -> None:
        """通用日志记录方法"""
        if not self._enabled or not self._logger:
            return
            
        # 检查消息级别是否应该被记录
        if level.value < self._level.value:
            return
            
        try:
            # 获取调用者信息
            context = self._get_caller_context(3)  # 跳过_log和具体的日志方法
            context.level = level
            context.message = message % args if args else message
            
            # 记录日志
            getattr(self._logger, level.name.lower())(
                context.message,
                extra={'context': context}
            )
        except Exception as e:
            # 处理格式化错误
            error_msg = f"格式化消息失败: {message} {args} ({str(e)})"
            getattr(self._logger, LogLevel.ERROR.name.lower())(
                error_msg,
                extra={'context': self._get_caller_context(3)}
            )
    
    def add_file_handler(self, filepath: str) -> None:
        """添加文件输出处理器
        
        Args:
            filepath: 日志文件路径
        """
        if not self._logger:
            return
            
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(filepath, encoding='utf-8')
        file_handler.setLevel(self._level.value)
        
        # 使用相同的格式化器
        # formatter = RBQLogFormatter(
        #     '%(asctime)s [%(levelname)s] '
        #     '[文件名:%(filename)s] '
        #     '[函数名:%(funcName)s] '
        #     '[行号:%(lineno)d] '
        #     '%(message)s'
        # )
        formatter = RBQLogFormatter('%(asctime)s [%(levelname)s] %(message)s')
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
    
    @property
    def enabled(self) -> bool:
        """获取日志是否启用"""
        return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool) -> None:
        """设置是否启用日志"""
        self._enabled = value
    
    @property
    def level(self) -> LogLevel:
        """获取当前日志级别"""
        return self._level
    
    @level.setter
    def level(self, value: LogLevel) -> None:
        """设置日志级别"""
        if value == self._level:
            return
            
        self._level = value
        if self._logger:
            # 先保存当前的处理器
            current_handlers = self._logger.handlers[:]
            # 移除所有处理器
            for handler in current_handlers:
                self._logger.removeHandler(handler)
            # 重新添加处理器并设置正确的级别
            for handler in current_handlers:
                handler.setLevel(value.value)
                self._logger.addHandler(handler)
    
    # 便捷日志方法（实例方法）
    def debug(self, message: str, *args: Any) -> None:
        """记录DEBUG级别日志"""
        self._log(LogLevel.DEBUG, message, *args)
    
    def info(self, message: str, *args: Any) -> None:
        """记录INFO级别日志"""
        self._log(LogLevel.INFO, message, *args)
    
    def warning(self, message: str, *args: Any) -> None:
        """记录WARNING级别日志"""
        self._log(LogLevel.WARNING, message, *args)
    
    def error(self, message: str, *args: Any) -> None:
        """记录ERROR级别日志"""
        self._log(LogLevel.ERROR, message, *args)
    
    def critical(self, message: str, *args: Any) -> None:
        """记录CRITICAL级别日志"""
        self._log(LogLevel.CRITICAL, message, *args)

    # 为保持向后兼容的类方法
    @classmethod
    def set_enable_log(cls, enable: bool) -> None:
        """设置是否启用日志（兼容性方法）"""
        cls().enabled = enable
    
    @classmethod
    def set_level(cls, level: LogLevel) -> None:
        """设置日志级别（兼容性方法）"""
        cls().level = level
        
    @classmethod
    def get_level(cls) -> LogLevel:
        """获取当前日志级别（兼容性方法）"""
        return cls().level
    
    @classmethod
    def set_file_output(cls, filepath: str) -> None:
        """设置文件输出（兼容性方法）"""
        cls().add_file_handler(filepath)
    
    # 静态日志方法，可以直接通过类调用
    @classmethod
    def log_debug(cls, message: str, *args: Any) -> None:
        """静态方法：记录DEBUG级别日志"""
        cls().debug(message, *args)
    
    @classmethod
    def log_info(cls, message: str, *args: Any) -> None:
        """静态方法：记录INFO级别日志"""
        cls().info(message, *args)
    
    @classmethod
    def log_warning(cls, message: str, *args: Any) -> None:
        """静态方法：记录WARNING级别日志"""
        cls().warning(message, *args)
    
    @classmethod
    def log_error(cls, message: str, *args: Any) -> None:
        """静态方法：记录ERROR级别日志"""
        cls().error(message, *args)
    
    @classmethod
    def log_critical(cls, message: str, *args: Any) -> None:
        """静态方法：记录CRITICAL级别日志"""
        cls().critical(message, *args)
    
    @classmethod
    def log(cls, message: str, *args: Any) -> None:
        """静态方法：记录INFO级别日志（兼容性方法）"""
        cls().info(message, *args)
    
    @contextmanager
    def temp_level(self, level: LogLevel):
        """临时改变日志级别的上下文管理器
        
        Args:
            level: 临时的日志级别
            
        Example:
            >>> with log.temp_level(LogLevel.ERROR):
            ...     log.debug("这条不会显示")
            ...     log.error("这条会显示")
        """
        old_level = self._level
        self.level = level  # 这会同时更新 self._level 和所有处理器的级别
        try:
            yield
        finally:
            self.level = old_level  # 恢复时也会更新所有处理器的级别