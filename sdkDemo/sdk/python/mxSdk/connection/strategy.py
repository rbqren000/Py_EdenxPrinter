# -*- coding: utf-8 -*-
"""
连接策略基类

定义了所有连接策略必须实现的接口，采用策略模式设计。
每种连接类型（USB、串口、蓝牙等）都有自己的连接策略实现。

作者: RBQ
版本: 1.0.0
创建时间: 2025
Python版本: 3.9+
"""
# 这里增加下边这句可以在协议中方法中引入ConnectionStrategy本身，不过这里暂时不返回ConnectionStrategy了，且这个语句必须放到文件开头
# from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple, Callable, Protocol
from dataclasses import dataclass
from ..enums import ConnType
from ..enums.connection_status import ConnectionStatus
from ..models.device_info import DeviceInfo
from ..models.command_context import CommandContext
from ..models.data_obj_context import DataObjContext
from ..enums.conn_type import ConnType

# 设备发现协议
class DiscoveryProtocol(Protocol):
    """设备发现事件协议
    
    定义设备发现过程中的所有回调方法。
    实现此协议的类必须提供所有方法的实现。
    """
    
    def on_discover_start(self) -> None:
        """设备发现开始时调用
        
        当开始扫描设备时触发此方法。
        Args:
            strategy: 连接策略
        """
        ...
    
    def on_discover_found(self, device: DeviceInfo) -> None:
        """发现单个设备时调用
        
        Args:
            device: 发现的设备信息
            strategy: 连接策略
        """
        ...
    
    def on_discover_stop(self) -> None:
        """设备发现停止时调用
        
        当扫描结束时触发此方法。
        
        Args:
            strategy: 连接策略
        """
        ...


# 数据读取协议
class DataReadProtocol(Protocol):
    """数据读取事件协议
    
    定义数据读取过程中的回调方法。
    """
    
    def on_data_read(self, data: bytes) -> None:
        """接收到数据时调用
        
        Args:
            data: 接收到的原始字节流数据
            strategy: 连接策略
        """
        ...


# 数据写入协议
class DataWriteProtocol(Protocol):
    """数据写入事件协议
    
    定义数据写入过程中的所有回调方法。
    """
    
    def on_data_write_progress(self, index: int, tag: int, data_chunk: bytes, 
                              total_length: int, written_length: int, progress: int) -> None:
        """数据写入进度更新时调用
        
        Args:
            index: 写入操作的序号或数据块索引
            tag: 数据标志位，用于标识当前传输上下文
            data_chunk: 当前正在写入的数据片段（一个分包）
            total_length: 总数据长度（整个数据包的目标字节数）
            written_length: 当前已写入的总字节数
            progress: 当前写入进度百分比（0~100）
            strategy: 连接策略
        """
        ...
    
    def on_data_write_success(self, index: int, tag: int, data: bytes, 
                             total_length: int) -> None:
        """数据写入成功时调用
        
        Args:
            index: 写入操作的序号或标识索引
            tag: 数据块标志位，用于区分业务上下文
            data: 实际写入的数据内容（一个完整数据包）
            total_length: 此次应写入的总数据长度（单位: 字节）
            success: 写入是否成功
            strategy: 连接策略
        """
        ...
    
    def on_data_write_failure(self, index: int, tag: int, data: bytes, 
                             error_code: int, error_message: str) -> None:
        """数据写入失败时调用
        
        Args:
            index: 写入操作的序号或标识索引
            tag: 数据块标志位，用于区分业务上下文
            data: 实际写入的数据内容（一个完整数据包）
            error_code: 错误码，标识具体的写入失败原因
            error_message: 错误描述信息，详细说明写入失败的原因
            strategy: 连接策略
        """
        ...

# 连接状态协议
class ConnectionStatusProtocol(Protocol):
    """连接状态事件协议
    
    定义连接状态变更过程中的回调方法。
    """
    
    def on_connection_status_changed(self, status: ConnectionStatus) -> None:
        """连接状态变更时调用
        
        Args:
            status: 新的连接状态
            strategy: 连接策略
        """
        ...


class ConnectionStrategy(ABC):
    """连接策略抽象基类

    定义了所有连接策略必须实现的接口。
    采用策略模式设计，允许在运行时选择不同的连接方式。

    Attributes:
        _status: 当前连接状态
        _device: 当前连接的设备信息
    """

    def __init__(self):
        """初始化连接策略"""

        self._conn_status = ConnectionStatus.DISCONNECTED
        self._device = None
        self._is_discovering = False  # 是否正在扫描设备

        # 写数据标识，默认为-1
        self._tag = -1
        self._command_context: Optional[CommandContext] = None
        self._data_obj_context: Optional[DataObjContext] = None

        # 事件处理器
        self._discovery_handler: Optional[DiscoveryProtocol] = None
        self._data_read_handler: Optional[DataReadProtocol] = None
        self._data_write_handler: Optional[DataWriteProtocol] = None
        self._connection_status_handler: Optional[ConnectionStatusProtocol] = None

    #返回连接状态
    @property
    def conn_status(self) -> ConnectionStatus:
        """获取当前连接状态

        Returns:
            ConnectionStatus: 当前连接状态
        """
        return self._conn_status

    #通过方法来获取连接状态
    def get_conn_status(self) -> ConnectionStatus:
        """获取当前连接状态

        Returns:
            ConnectionStatus: 当前连接状态
        """
        return self._conn_status

    @property
    def device_info(self) -> Optional[DeviceInfo]:
        """获取当前连接的设备信息

        Returns:
            Optional[DeviceInfo]: 当前连接的设备信息，未连接时返回None
        """
        return self._device

    @property
    def is_discovering(self) -> bool:
        """获取是否正在扫描设备

        Returns:
            bool: 正在扫描返回True，否则返回False
        """
        return self._is_discovering

    @property
    @abstractmethod
    def connection_type(self) -> ConnType:
        """获取连接类型

        Returns:
            ConnType: 连接类型
        """
        pass

    # 设置Protocol事件处理器
    def set_discovery_handler(self, handler: DiscoveryProtocol) -> None:
        """设置设备发现事件处理器
        
        Args:
            handler: 实现DiscoveryProtocol的事件处理器对象
        """
        self._discovery_handler = handler
    
    def set_data_read_handler(self, handler: DataReadProtocol) -> None:
        """设置数据读取事件处理器
        
        Args:
            handler: 实现DataReadProtocol的事件处理器对象
        """
        self._data_read_handler = handler
    
    def set_data_write_handler(self, handler: DataWriteProtocol) -> None:
        """设置数据写入事件处理器
        
        Args:
            handler: 实现DataWriteProtocol的事件处理器对象
        """
        self._data_write_handler = handler
    
    def set_connection_status_handler(self, handler: ConnectionStatusProtocol) -> None:
        """设置连接状态事件处理器
        
        Args:
            handler: 实现ConnectionStatusProtocol的事件处理器对象
        """
        self._connection_status_handler = handler

    @abstractmethod
    def discover_devices(self, timeout: float = 5.0) -> None:
        """发现可用设备

        Args:
            timeout: 发现超时时间（秒）

        Returns:
            List[DeviceInfo]: 发现的设备列表
        """
        pass

    @abstractmethod
    def cancel_discover_devices(self) -> None:
        """取消设备发现
        
        停止当前正在进行的设备发现操作。
        如果没有正在进行的发现操作，此方法应该安全地返回。
        """
        pass

    @abstractmethod
    def connect(self, device_info: DeviceInfo) -> None:
        """
        连接到设备

        Args:
            device_info: 设备信息对象，包含连接所需的所有参数
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """断开当前连接"""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """检查是否已连接

        Returns:
            bool: 已连接返回True，未连接返回False
        """
        pass
    
    @abstractmethod
    def write_data(self, tag: int, data: bytes) -> None:
        """发送数据

        Args:
            tag: 数据块标志位，用于区分业务上下文
            data: 要发送的数据

        Returns:
            Tuple[bool, int]: (是否成功, 发送的字节数)
        """
        pass

    def _trigger_command_error(self, command_context: CommandContext, error_msg: str) -> None:
        """触发错误回调

        Args:
            command: 触发错误的命令
            error_msg: 错误消息
        """
        if command_context.command_callback:
            command_context.command_callback._trigger_error(command_context.command, error_msg)

    def _trigger_command_success(self, command_context: CommandContext) -> None:
        """触发成功回调

        Args:
            command_context: 触发成功的命令
        """
        if command_context.command_callback:
            command_context.command_callback._trigger_success(command_context.command)

    @abstractmethod
    def write_CommandContext(self, command_context: CommandContext) -> None:
        """发送CommandContext

        Args:
            command_context: 要发送的CommandContext对象
        """
        pass

    def _trigger_obj_error(self, data_obj_context: DataObjContext, error_msg: str) -> None:
        """触发错误回调

        Args:
            data_obj_context: 触发错误的DataObjContext
            error_msg: 错误消息
        """
        if data_obj_context.data_obj_callback:
            data_obj_context.data_obj_callback._trigger_error(data_obj_context.data_obj.data, error_msg)

    def _trigger_obj_success(self, data_obj_context: DataObjContext) -> None:
        """触发成功回调

        Args:
            data_obj_context: 触发成功的DataObjContext
        """
        if data_obj_context.data_obj_callback:
            data_obj_context.data_obj_callback._trigger_success(data_obj_context.data_obj)

    @abstractmethod
    def write_DataObjContext(self, data_obj_context: DataObjContext) -> None:
        """发送DataObjContext

        Args:
            data_obj_context: 要发送的DataObjContext对象
        """
        pass

    def _trigger_connection_status_changed(self, status: ConnectionStatus) -> None:
        """触发连接状态变更事件
        Args:
            status: 新的连接状态
        """
        if self._connection_status_handler:
            self._connection_status_handler.on_connection_status_changed(status)

    def _update_connect_status(self, status: ConnectionStatus) -> None:
        """更新连接状态
        Args:
            conn_status: 新状态
        """
        if status != self._conn_status:
            self._conn_status = status
            # 触发状态变化事件
            self._trigger_connection_status_changed(status)
    
    # Protocol事件触发方法
    def _trigger_discover_start(self) -> None:
        """触发设备发现开始事件"""
        self._is_discovering = True
        if self._discovery_handler:
            self._discovery_handler.on_discover_start()
    
    def _trigger_discover_found(self, device: DeviceInfo) -> None:
        """触发发现单个设备事件
        Args:
            device: 发现的设备信息
        """
        if self._discovery_handler:
            self._discovery_handler.on_discover_found(device)
    
    def _trigger_discover_stop(self) -> None:
        """触发设备发现停止事件"""
        self._is_discovering = False
        if self._discovery_handler:
            self._discovery_handler.on_discover_stop()
    
    def _trigger_data_read(self, data: bytes) -> None:
        """触发数据读取事件
        Args:
            data: 接收到的数据
        """
        if self._data_read_handler:
            self._data_read_handler.on_data_read(data)
    
    def _trigger_data_write_progress(self, index: int, tag: int, data: bytes, 
                                   written_length: int, total_length: int, progress: int) -> None:
        """触发数据写入进度事件
        Args:
            index: 数据索引
            tag: 数据标签
            data: 写入的数据
            written_length: 已写入数据长度
            total_length: 总数据长度
            progress: 写入进度百分比
        """
        if self._data_write_handler:
            self._data_write_handler.on_data_write_progress(
                index, tag, data, total_length, written_length, progress
            )
    
    def _trigger_data_write_success(self, index: int, tag: int, data: bytes, 
                                  total_length: int) -> None:
        """触发数据写入成功事件
        Args:
            index: 数据索引
            tag: 数据标签
            data: 写入的数据
            total_length: 总数据长度
            success: 写入是否成功
        """
        if self._data_write_handler:
            self._data_write_handler.on_data_write_success(index, tag, data, total_length)
    
    def _trigger_data_write_failure(self, index: int, tag: int, data: bytes, 
                                  error_code: int, error_message: str) -> None:
        """触发数据写入失败事件
        Args:
            index: 数据索引
            tag: 数据标签
            data: 写入的数据
            error_code: 错误码
            error_message: 错误信息
        """
        if self._data_write_handler:
            self._data_write_handler.on_data_write_failure(index, tag, data, error_code, error_message)
    

    
    # 给继承该类的子类来调用，并自动调用相应的事件
    def _update_data_write_progress(self, index: int, tag: int, data: bytes, 
                                  written_length: int, total_length: int, progress: int) -> None:
        """更新分包写入进度（向后兼容方法）"""
        self._trigger_data_write_progress(index, tag, data, written_length, total_length, progress)
    
    def _update_data_write_success(self, index: int, tag: int, data: bytes, 
                                 total_length: int) -> None:
        """更新数据写入成功状态（向后兼容方法）"""
        self._trigger_data_write_success(index, tag, data, total_length)
    
    def _update_data_write_failure(self, index: int, tag: int, data: bytes, 
                                 error_code: int, error_message: str) -> None:
        """更新数据写入失败状态（向后兼容方法）"""
        self._trigger_data_write_failure(index, tag, data, error_code, error_message)
