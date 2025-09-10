#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConnectManager - 统一连接管理器

作者: RBQ
创建时间: 2025
描述: 提供统一的设备连接管理功能，支持USB和串口连接，实现Objective-C ConnectManager的Python版本
"""

# from __future__ import annotations
import threading
import time
import json
from typing import Dict, List, Optional, Callable, Any, Union, Protocol
from dataclasses import dataclass
from .factory import ConnectionStrategyFactory
from .strategy import DeviceInfo
from ..enums import ConnType, ConnectionStatus
from ..enums.op_code import OpCode
from ..enums.data_send_type import DataSendType
from ..transport.protocol import SOH, STX_A, STX_E
from ..utils.rbq_log import RBQLog
from ..packets import BasePacket
from ..packets import MultiRowDataPacket
from ..packets import LogoDataPacket
from ..packets import OtaDataPacket
from ..models.data_obj import DataObj
from ..models.data_obj_context import DataObjContext
from ..models.data_obj_callback import DataObjCallback,DataObjProtocol
from ..models.command import Command
from ..models import CommandContext
from ..models.command_callback import CommandCallback,CommandProtocol
from ..connection.strategy import ConnectionStrategy,DiscoveryProtocol, DataReadProtocol, DataWriteProtocol,ConnectionStatusProtocol
from ..utils.crc16 import CRC16
from ..data.multi_row_data import MultiRowData
from ..data.logo_data import LogoData
from .gcd_style_timer import GCDStyleTimer
from .Json_stream_assembler import JsonStreamAssembler

"""  
=== 设备发现相关事件协议 ===
"""
class DeviceDiscoveryProtocol(Protocol):
    """设备发现事件协议"""
    
    def on_device_discover_start(self) -> None:
        """设备开始发现事件"""
        ...
    
    def on_device_discover(self, device: DeviceInfo) -> None:
        """发现设备事件"""
        ...
    
    def on_device_discover_stop(self) -> None:
        """设备发现完成事件"""
        ...

"""  
=== 设备连接相关事件协议 ===
"""
class DeviceConnectionProtocol(Protocol):
    """设备连接事件协议"""
    
    def on_device_connect_start(self, device: DeviceInfo) -> None:
        """设备开始连接事件"""
        ...
    
    def on_device_connect_succeed(self, device: DeviceInfo) -> None:
        """设备连接成功事件"""
        ...
    
    def on_device_disconnect(self, device: DeviceInfo) -> None:
        """设备断开连接事件"""
        ...
    
    def on_device_connect_fail(self, device: DeviceInfo) -> None:
        """设备连接失败事件"""
        ...

"""  
=== 数据传输进度相关事件协议 ===
"""
class DeviceDataTransferProtocol(Protocol):
    """设备数据传输事件协议"""

    def on_device_data_transfer_start(self, device: DeviceInfo, size: float, startTime: int, currentTime: int) -> None:
        """设备数据传输开始事件"""
        ...
    
    def on_device_data_transfer_progress(self, device: DeviceInfo, size: float, progress: int, startTime: int, currentTime: int) -> None:
        """设备数据传输进度事件"""
        ...
    
    def on_device_data_transfer_success(self, device: DeviceInfo, size: float, startTime: int, currentTime: int) -> None:
        """设备数据传输成功事件"""
        ...
    
    def on_device_data_transfer_error(self, error_code: int, error_message: str) -> None:
        """设备数据传输错误事件"""
        ...

"""  
=== 设备读取属性事件协议 ===
"""
class DeviceReadProtocol(Protocol):
    """设备读取事件协议"""

    def on_device_read_data(self, device: DeviceInfo, data: bytes) -> None:
        """设备读取数据事件，这个无论啥数据都会返回，是未进行解析的数据"""
        ...
   
    def on_device_read_print_head_parameter(self, device: DeviceInfo, head_value: int, l_pix: int, p_pix: int, distance: int) -> None:
        """设备读取打印头参数事件"""
        ...
    def on_device_read_circulation_repeat_times(self, device: DeviceInfo, circulation_time: int, repeat_time: int) -> None:
        """设备读取重复次数事件"""
        ...
    
    def on_device_read_charging_state(self, device: DeviceInfo) -> None:
        """设备读取充电状态事件"""
        ...
    
    def on_device_read_print_direction_and_print_head_direction(self, device: DeviceInfo) -> None:
        """设备读取打印方向和打印头方向事件"""
        ...
    
    def on_device_read_print_head_id(self, device: DeviceInfo) -> None:
        """设备读取打印头ID事件"""
        ...
    
    def on_device_read_device_software_info(self, device: DeviceInfo, printer_head_id: str, name: str, mcu_version: str, mcu_date: str) -> None:
        """设备读取设备软件信息事件"""
        ...
    
    def on_device_read_cartridge_id(self, device: DeviceInfo, cartridge_id: str) -> None:
        """设备读取 cartridges ID 事件"""
        ...

    def on_device_read_print_head_temperature(self, device: DeviceInfo,temperature: int) -> None:
        """设备读取打印头温度事件"""
        ...
    
    def on_device_read_battery(self, device: DeviceInfo,battery_level: int) -> None:
        """设备读取电池信息事件"""
        ...

    def on_device_read_print_start(self, device: DeviceInfo, beginIndex: int, endIndex: int, currentIndex: int) -> None:
        """设备读取打印开始事件"""
        ...
    
    def on_device_read_print_completed(self, device: DeviceInfo, beginIndex: int, endIndex: int, currentIndex: int, cartridgeId: str) -> None:
        """设备读取打印完成事件"""
        ...
    def on_device_read_session_ready(self, device: DeviceInfo) -> None:
        """设备读取会话就绪事件"""
        ...
    def on_device_read_session_fail(self, device: DeviceInfo) -> None:
        """设备读取会话失败事件"""
        ...
    
    def on_device_read_silent_state(self, device: DeviceInfo,silent_state: bool) -> None:
        """设备读取静音状态事件"""
        ...
    
    def on_device_read_auto_power_off_state(self, device: DeviceInfo,auto_power_off_state: bool) -> None:
        """设备读取自动关机状态事件"""
        ...
    
    def on_device_read_write_print_start_command(self, device: DeviceInfo) -> None:
        """设备读取发送打印指令反馈事件"""
        ...

"""  
=== 打印任务相关事件协议 ===
"""
class DevicePrintTaskProtocol(Protocol):
    """设备打印任务事件协议"""
    
    def on_device_print_start(self, device: DeviceInfo) -> None:
        """设备打印开始事件"""
        ...
    
    def on_device_print_progress(self, device: DeviceInfo, current: int, total: int) -> None:
        """设备打印进度事件"""
        ...
    
    def on_device_print_finish(self, device: DeviceInfo) -> None:
        """设备打印完成事件"""
        ...

"""  
=== 命令写入相关事件协议 ===
"""
class DeviceCommandWriteProtocol(Protocol):
    """设备命令写入事件协议"""
    
    def on_device_command_write_success(self, device: DeviceInfo) -> None:
        """设备命令写入成功事件"""
        ...
    
    def on_device_command_write_error(self, device: DeviceInfo) -> None:
        """设备命令写入错误事件"""
        ...
"""  
=== 数据写入相关事件协议 ===
"""
class DeviceDataWriteProtocol(Protocol):
    """设备数据写入事件协议"""
    
    def on_device_data_write_start(self, device: DeviceInfo) -> None:
        """设备数据写入开始事件"""
        ...
    
    def on_device_data_write_progress(self, device: DeviceInfo, current: int, total: int) -> None:
        """设备数据写入进度事件"""
        ...
    
    def on_device_data_write_success(self, device: DeviceInfo) -> None:
        """设备数据写入成功事件"""
        ...
    
    def on_device_data_write_error(self, device: DeviceInfo) -> None:
        """设备数据写入错误事件"""
        ...

@dataclass
class ManagedConnection:
    """管理的连接信息"""
    device_info: DeviceInfo
    strategy: ConnectionStrategy
    auto_reconnect: bool = False
    last_activity: float = 0.0
    reconnect_attempts: int = 0
    max_reconnect_attempts: int = 3

class ConnectManager:
    """统一连接管理器
    
    提供设备发现、连接管理、数据传输等功能的统一接口。
    支持USB和串口连接方式，实现Objective-C ConnectManager的Python版本。
    """

    _COMMAND_INTERVAL = 0.05
    
    # 连接管理器实例
    _instance = None
    # 连接管理器实例锁
    _instance_lock = threading.Lock()
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def share(cls) -> 'ConnectManager':
        """获取单例对象
        
        Returns:
            ConnectManager实例
        """
        return cls()
    
    def __init__(self):
        """初始化连接管理器"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True

        #manager内部使用的其他事件
        self._discovery_handler = self.DiscoveryHandler(self)
        self._connection_status_handler = self.ConnectionStatusHandler(self)
        self._data_read_handler = self.DataReadHandler(self)
        self._data_write_handler = self.DataWriteHandler(self)
        self._command_handler = self.CommandHandler(self)
        self._data_obj_handler = self.DataObjHandler(self)

        self._command_call_back : CommandCallback = CommandCallback(self._command_handler)
        self._data_obj_call_back : DataObjCallback = DataObjCallback(self._data_obj_handler)

        self._sequence_number = 0

        self._factory: ConnectionStrategyFactory = ConnectionStrategyFactory()
        self._connections: Dict[str, ManagedConnection] = {}
        # 当前活跃的连接（替代原来的多个状态变量）
        self._current_connection: Optional[ManagedConnection] = None
        self._lock = threading.RLock()

        self._monitor_running = False
        
        # 设备发现状态
        self._is_discovering = False

        self._allow_send_data: bool = True
        self._is_syncing_data: bool = False
        
        self._n_index: int = 0
        # 数据包相关属性
        self._multi_row_data_packet: MultiRowDataPacket = MultiRowDataPacket() # 多行数据包
        self._logo_data_packet: LogoDataPacket = LogoDataPacket() # Logo数据包
        self._ota_data_packet: OtaDataPacket = OtaDataPacket() # OTA数据包
        # 存放packets的列表 存储所有数据包
        self._packets: List[BasePacket] = [self._multi_row_data_packet, self._logo_data_packet, self._ota_data_packet]
        # 主要处理传输过程中延时发送指令
        self._data_transfer_delay_command_timer: Optional[GCDStyleTimer] = None
        
        #等待数据传输响应重试计时
        self._wait_data_transfer_response_timer: Optional[GCDStyleTimer] = None

        self._command_queue: List[CommandContext] = []            # 命令队列
        self._command_queue_lock = threading.RLock()  # 指令队列锁
        self._command_queue_timer: Optional[GCDStyleTimer] = None
        
        self._sequence_number = 0           # 当前序列号
        self._sequence_lock = threading.RLock()  # 序列号锁
        self._last_send_command_time = 0     # 上次发送指令时间
        
        # 心跳监控系统
        self._is_syncing_data = False       # 是否正在同步数据
        self._heart_lose_times = 0          # 心跳丢失次数计数器
        self._max_lose_heart_times = 5      # 最大心跳丢失次数
        self._last_heart_response_time = 0  # 最后一次心跳响应时间
        self._n_index = 0                   # 当前数据包索引
        self._heart_timer: Optional[GCDStyleTimer] = None
        
        # 数据接收处理相关属性
        self._receive_lock = threading.RLock()
        #json接收器
        self._json_stream_assembler: JsonStreamAssembler = JsonStreamAssembler(self.on_json_complete)
        
        # 协议事件处理器管理 - 支持多事件注册
        self._protocol_handlers: Dict[str, List[Union[
            DeviceDiscoveryProtocol,
            DeviceConnectionProtocol, 
            DeviceDataTransferProtocol,
            DeviceReadProtocol,
            DevicePrintTaskProtocol,
            DeviceCommandWriteProtocol,
            DeviceDataWriteProtocol
        ]]] = {
            'device_discovery': [],
            'device_connection': [],
            'device_data_transfer': [],
            'device_read': [],
            'device_print_task': [],
            'device_command_write': [],
            'device_data_write': []
        }
        
        self._start_monitor()
    
    # ========== 注册发现设备事件 ==========
    def register_device_discovery_handler(self, handler: DeviceDiscoveryProtocol) -> None:
        """注册设备发现事件处理器"""
        with self._lock:
            if handler not in self._protocol_handlers['device_discovery']:
                self._protocol_handlers['device_discovery'].append(handler)
    
    # ========== 注销发现设备事件 ==========
    def unregister_device_discovery_handler(self, handler: DeviceDiscoveryProtocol) -> None:
        """注销设备发现事件处理器"""
        with self._lock:
            if handler in self._protocol_handlers['device_discovery']:
                self._protocol_handlers['device_discovery'].remove(handler)
    
    # ========== 注册连接设备事件 ==========
    def register_device_connection_handler(self, handler: DeviceConnectionProtocol) -> None:
        """注册设备连接事件处理器"""
        with self._lock:
            if handler not in self._protocol_handlers['device_connection']:
                self._protocol_handlers['device_connection'].append(handler)
    
    # ========== 注销连接设备事件 ==========
    def unregister_device_connection_handler(self, handler: DeviceConnectionProtocol) -> None:
        """注销设备连接事件处理器"""
        with self._lock:
            if handler in self._protocol_handlers['device_connection']:
                self._protocol_handlers['device_connection'].remove(handler)

    # ========== 注册数据传输事件 ==========
    def register_device_data_transfer_handler(self, handler: DeviceDataTransferProtocol) -> None:
        """注册数据传输事件处理器"""
        with self._lock:
            if handler not in self._protocol_handlers['device_data_transfer']:
                self._protocol_handlers['device_data_transfer'].append(handler)
    
    # ========== 注销数据传输事件 ==========
    def unregister_device_data_transfer_handler(self, handler: DeviceDataTransferProtocol) -> None:
        """注销数据传输事件处理器"""
        with self._lock:
            if handler in self._protocol_handlers['device_data_transfer']:
                self._protocol_handlers['device_data_transfer'].remove(handler)
    
    # ========== 注册读取设备事件 ==========
    def register_device_read_handler(self, handler: DeviceReadProtocol) -> None:
        """注册设备读取事件处理器"""
        with self._lock:
            if handler not in self._protocol_handlers['device_read']:
                self._protocol_handlers['device_read'].append(handler)
    
    # ========== 注销读取设备事件 ==========
    def unregister_device_read_handler(self, handler: DeviceReadProtocol) -> None:
        """注销设备读取事件处理器"""
        with self._lock:
            if handler in self._protocol_handlers['device_read']:
                self._protocol_handlers['device_read'].remove(handler)
    
    # ========== 注册打印任务事件 ==========
    def register_device_print_task_handler(self, handler: DevicePrintTaskProtocol) -> None:
        """注册打印任务事件处理器"""
        with self._lock:
            if handler not in self._protocol_handlers['device_print_task']:
                self._protocol_handlers['device_print_task'].append(handler)
    
    # ========== 注销打印任务事件 ==========
    def unregister_device_print_task_handler(self, handler: DevicePrintTaskProtocol) -> None:
        """注销打印任务事件处理器"""
        with self._lock:
            if handler in self._protocol_handlers['device_print_task']:
                self._protocol_handlers['device_print_task'].remove(handler)
    
    # ========== 注册命令写入事件 ==========
    def register_device_command_write_handler(self, handler: DeviceCommandWriteProtocol) -> None:
        """注册命令写入事件处理器"""
        with self._lock:
            if handler not in self._protocol_handlers['device_command_write']:
                self._protocol_handlers['device_command_write'].append(handler)
    
    # ========== 注销命令写入事件 ==========
    def unregister_device_command_write_handler(self, handler: DeviceCommandWriteProtocol) -> None:
        """注销命令写入事件处理器"""
        with self._lock:
            if handler in self._protocol_handlers['device_command_write']:
                self._protocol_handlers['device_command_write'].remove(handler)

    # ========== 注册数据写入事件 ==========
    def register_device_data_write_handler(self, handler: DeviceDataWriteProtocol) -> None:
        """注册数据写入事件处理器"""
        with self._lock:
            if handler not in self._protocol_handlers['device_data_write']:
                self._protocol_handlers['device_data_write'].append(handler)
    
    # ========== 注销数据写入事件 ==========
    def unregister_device_data_write_handler(self, handler: DeviceDataWriteProtocol) -> None:
        """注销数据写入事件处理器"""
        with self._lock:
            if handler in self._protocol_handlers['device_data_write']:
                self._protocol_handlers['device_data_write'].remove(handler)
    
    # ========== 触发发现设备事件 ==========
    def _trigger_device_discovery_handler_event(self, method_name: str, *args, **kwargs) -> None:
        """触发设备发现事件"""
        with self._lock:
            for handler in self._protocol_handlers['device_discovery']:
                try:
                    if hasattr(handler, method_name):
                        getattr(handler, method_name)(*args, **kwargs)
                except Exception as e:
                    RBQLog.log_error(f"设备发现事件处理器执行出错 [{method_name}]: {e}")
    
    # ========== 触发连接设备事件 ==========
    def _trigger_device_connection_handler_event(self, method_name: str, *args, **kwargs) -> None:
        """触发设备连接事件"""
        with self._lock:
            for handler in self._protocol_handlers['device_connection']:
                try:
                    if hasattr(handler, method_name):
                        getattr(handler, method_name)(*args, **kwargs)
                except Exception as e:
                    RBQLog.log_error(f"设备连接事件处理器执行出错 [{method_name}]: {e}")
    
    # ========== 触发数据传输事件 ==========
    def _trigger_device_data_transfer_handler_event(self, method_name: str, *args, **kwargs) -> None:
        """触发数据传输事件"""
        with self._lock:
            for handler in self._protocol_handlers['device_data_transfer']:
                try:
                    if hasattr(handler, method_name):
                        getattr(handler, method_name)(*args, **kwargs)
                except Exception as e:
                    RBQLog.log_error(f"数据传输事件处理器执行出错 [{method_name}]: {e}")
    
    # ========== 触发读取设备事件 ==========
    def _trigger_device_read_handler_event(self, method_name: str, *args, **kwargs) -> None:
        """触发设备读取事件"""
        with self._lock:
            for handler in self._protocol_handlers['device_read']:
                try:
                    if hasattr(handler, method_name):
                        getattr(handler, method_name)(*args, **kwargs)
                except Exception as e:
                    RBQLog.log_error(f"设备读取事件处理器执行出错 [{method_name}]: {e}")
    
    # ========== 触发打印任务事件 ==========
    def _trigger_device_print_task_handler_event(self, method_name: str, *args, **kwargs) -> None:
        """触发打印任务事件"""
        with self._lock:
            for handler in self._protocol_handlers['device_print_task']:
                try:
                    if hasattr(handler, method_name):
                        getattr(handler, method_name)(*args, **kwargs)
                except Exception as e:
                    RBQLog.log_error(f"打印任务事件处理器执行出错 [{method_name}]: {e}")
    
    # ========== 触发命令写入事件 ==========
    def _trigger_device_command_write_handler_event(self, method_name: str, *args, **kwargs) -> None:
        """触发命令写入事件"""
        with self._lock:
            for handler in self._protocol_handlers['device_command_write']:
                try:
                    if hasattr(handler, method_name):
                        getattr(handler, method_name)(*args, **kwargs)
                except Exception as e:
                    RBQLog.log_error(f"命令写入事件处理器执行出错 [{method_name}]: {e}")
    
    # ========== 触发数据写入事件 ==========
    def _trigger_device_data_write_handler_event(self, method_name: str, *args, **kwargs) -> None:
        """触发数据写入事件"""
        with self._lock:
            for handler in self._protocol_handlers['device_data_write']:
                try:
                    if hasattr(handler, method_name):
                        getattr(handler, method_name)(*args, **kwargs)
                except Exception as e:
                    RBQLog.log_error(f"数据写入事件处理器执行出错 [{method_name}]: {e}")
    
    # ========== 触发协议事件 ==========
    def _trigger_device_protocol_handler_event(self, protocol_category: str, method_name: str, *args, **kwargs) -> None:
        """同时触发协议事件"""
        if protocol_category == 'device_discovery':
            self._trigger_device_discovery_handler_event(method_name, *args, **kwargs)
        elif protocol_category == 'device_connection':
            self._trigger_device_connection_handler_event(method_name, *args, **kwargs)
        elif protocol_category == 'device_data_transfer':
            self._trigger_device_data_transfer_handler_event(method_name, *args, **kwargs)
        elif protocol_category == 'device_read':
            self._trigger_device_read_handler_event(method_name, *args, **kwargs)
        elif protocol_category == 'device_print_task':
            self._trigger_device_print_task_handler_event(method_name, *args, **kwargs)
        elif protocol_category == 'device_command_write':
            self._trigger_device_command_write_handler_event(method_name, *args, **kwargs)
        elif protocol_category == 'device_data_write':
            self._trigger_device_data_write_handler_event(method_name, *args, **kwargs)

    #通知开始设备发现通知on_device_discover_start
    def notify_device_discovery_start(self) -> None:
        """通知设备发现
        
        Args:
            device: 设备信息
        """
        self._trigger_device_discovery_handler_event('on_device_discover_start')

    #通知设备发现通知on_device_found
    def notify_device_discover(self, device: DeviceInfo) -> None:
        """通知设备发现结束
        
        Args:
            device: 设备信息
        """
        self._trigger_device_discovery_handler_event('on_device_discover', device)

    #通知设备发现on_device_discover_stop
    def notify_device_discover_stop(self) -> None:
        """通知设备发现结束
        
        Args:
            devices: 设备信息列表
        """
        self._trigger_device_discovery_handler_event('on_device_discover_stop')

    #通知设备连接开始通知on_device_connect_start
    def notify_device_connect_start(self, device: DeviceInfo) -> None:
        """通知设备连接开始
        
        Args:
            device: 设备信息
        """
        self._trigger_device_connection_handler_event('on_device_connect_start', device)

    #通知设备连接结束通知on_device_connect_succeed
    def notify_device_connect_succeed(self, device: DeviceInfo) -> None:
        """通知设备连接结束
        
        Args:
            device: 设备信息
        """
        self._trigger_device_connection_handler_event('on_device_connect_succeed', device)

    #通知设备连接断开通知on_device_disconnect
    def notify_device_disconnect(self, device: DeviceInfo) -> None:
        """通知设备连接断开
        
        Args:
            device: 设备信息
        """
        self._trigger_device_connection_handler_event('on_device_disconnect', device)

    #通知设备连接失败通知on_device_connect_fail
    def notify_device_connect_fail(self, device: DeviceInfo) -> None:
        """通知设备连接失败
        
        Args:
            device: 设备信息
        """
        self._trigger_device_connection_handler_event('on_device_connect_fail', device)

    def notify_device_data_transfer_start(self, device: DeviceInfo, size: float, startTime: int, currentTime: int) -> None:
        """通知设备数据传输开始
        
        Args:
            device: 设备信息
        """
        self._trigger_device_data_transfer_handler_event('on_device_data_transfer_start', device, size, startTime, currentTime)
    
    #通知数据传输进度通知on_device_data_transfer_progress
    def notify_device_data_transfer_progress(self, device: DeviceInfo, size: float, progress: int, startTime: int, currentTime: int) -> None:
        """通知设备数据传输进度
        
        Args:
            device: 设备信息
            size: 数据大小
            progress: 传输进度（0-100）
            startTime: 开始时间
            currentTime: 当前时间
        """
        self._trigger_device_data_transfer_handler_event('on_device_data_transfer_progress', device, size, progress, startTime, currentTime)
    
    #通知数据传输成功通知on_device_data_transfer_success
    def notify_device_data_transfer_success(self, device: DeviceInfo, size: float, startTime: int, currentTime: int) -> None:
        """通知设备数据传输成功
        
        Args:
            device: 设备信息
            size: 数据大小
            startTime: 开始时间
            currentTime: 当前时间
        """
        self._trigger_device_data_transfer_handler_event('on_device_data_transfer_success', device, size, startTime, currentTime)

    #通知数据传输错误on_device_data_transfer_error
    def notify_device_data_transfer_error(self, error_code: int, error_message: str) -> None:
        """通知设备数据传输错误
        
        Args:
            device: 设备信息
            error_code: 错误码
            error_message: 错误信息
        """
        self._trigger_device_data_transfer_handler_event('on_device_data_transfer_error', error_code, error_message)


    #通知读取到数据通知 on_device_read_data
    def notify_device_read_data(self, device: DeviceInfo, data: bytes) -> None:
        """通知设备读取数据
        
        Args:
            device: 设备信息
        """
        self._trigger_device_read_handler_event('on_device_read_data', device, data)
    
    #通知读取到充电状态通知on_device_read_charging_state
    def notify_device_read_charging_state(self, device: DeviceInfo) -> None:
        """通知设备读取充电状态
        
        Args:
            device: 设备信息
        """
        self._trigger_device_read_handler_event('on_device_read_charging_state', device)
    # 
    def notify_device_read_print_head_parameter(self, device: DeviceInfo, head_value: int, l_pix:int,p_pix, distance:int) -> None:
        """通知设备读取打印头参数
        
        Args:
            device: 设备信息
            head_value: 打印头参数
            l_pix: 打印头参数
            p_pix: 打印头参数
            distance: 打印头参数
        """
        self._trigger_device_read_handler_event('on_device_read_print_head_parameter', device,head_value,l_pix,p_pix,distance)

    def notify_device_read_circulation_repeat_times(self, device: DeviceInfo, circulation_time: int, repeat_time: int) -> None:
        """通知设备读取重复次数
        
        Args:
            device: 设备信息
            circulation_time: 循环次数
            repeat_time: 重复次数
        """
        self._trigger_device_read_handler_event('on_device_read_circulation_repeat_times', device,circulation_time,repeat_time)
    
    #通知读取到打印方向和打印头方向on_device_read_print_direction_and_print_head_direction
    def notify_device_read_print_direction_and_print_head_direction(self, device: DeviceInfo,horizontalDirection: int,verticalDirection: int,oldHorizontalDirection: int,oldVerticalDirection: int) -> None:
        """通知设备读取打印方向和打印头方向
        
        Args:
            device: 设备信息
        """
        self._trigger_device_read_handler_event('on_device_read_print_direction_and_print_head_direction', device,horizontalDirection,verticalDirection,oldHorizontalDirection,oldVerticalDirection)
    
    #读取到打印头IDon_device_read_print_head_id
    def notify_device_read_print_head_id(self, device: DeviceInfo) -> None:
        """通知设备读取打印头ID
        
        Args:
            device: 设备信息
        """
        self._trigger_device_read_handler_event('on_device_read_print_head_id', device)

    
    #通知读取到软件信息
    def notify_device_read_device_software_info(self, device: DeviceInfo, printer_head_id: str, name: str, mcu_version: str, mcu_date: str) -> None:
        """通知设备读取设备信息
        
        Args:
            device: 设备信息
            printer_head_id: 打印头ID
            name: 设备名称
            mcu_version: MCU版本
            mcu_date: MCU日期
        """
        self._trigger_device_read_handler_event('on_device_read_device_software_info', device,printer_head_id,name,mcu_version,mcu_date)

    #通知读取 cartridges ID
    def notify_device_read_cartridge_id(self,device:DeviceInfo, cartridge_id: str) -> None:
        """通知设备读取 cartridges ID
        
        Args:
            device: 设备信息
            cartridge_id: cartridges ID
        """
        self._trigger_device_read_handler_event('on_device_read_cartridge_id', device,cartridge_id)
    
    #通知读取到打印头温度on_device_read_print_head_temperature
    def notify_device_read_print_head_temperature(self, device: DeviceInfo,temperature: int) -> None:
        """通知设备读取打印头温度
        
        Args:
            device: 设备信息
            temperature: 打印头温度
        """
        self._trigger_device_read_handler_event('on_device_read_print_head_temperature', device,temperature)

    #通知读取到电量通知on_device_read_battery
    def notify_device_read_battery(self, device: DeviceInfo,battery_level: int) -> None:
        """通知设备读取电池信息
        
        Args:
            device: 设备信息
        """
        self._trigger_device_read_handler_event('on_device_read_battery', device,battery_level)

    def notify_device_read_print_start(self, device: DeviceInfo, beginIndex: int, endIndex: int, currentIndex: int) -> None:
        """通知设备读取打印开始
        
        Args:
            device: 设备信息
            beginIndex: 打印开始索引
            endIndex: 打印结束索引
            currentIndex: 当前打印索引
        """
        self._trigger_device_read_handler_event('on_device_read_print_start', device, beginIndex, endIndex, currentIndex)

    def notify_device_read_print_completed(self, device: DeviceInfo, beginIndex: int, endIndex: int, currentIndex: int, cartridgeId: str) -> None:
        """通知设备读取打印完成
        
        Args:
            device: 设备信息
            beginIndex: 打印开始索引
            endIndex: 打印结束索引
            currentIndex: 当前打印索引
            cartridgeId:  cartridges ID
        """

        self._trigger_device_read_handler_event('on_device_read_print_completed', device, beginIndex, endIndex, currentIndex, cartridgeId)
    
    def notify_session_ready(self, device:DeviceInfo) -> None:
        ...
    def notify_session_fail(self, device:DeviceInfo) -> None:
        ...

    #通知读取到静音状态on_device_read_silent_state
    def notify_device_read_silent_state(self, device: DeviceInfo,silent_state: bool) -> None:
        """通知设备读取静音状态
        
        Args:
            device: 设备信息
            silent_state: 静音状态
        """
        self._trigger_device_read_handler_event('on_device_read_silent_state', device,silent_state)
    
    #通知读取到自动关机状态on_device_read_auto_power_off_state
    def notify_device_read_auto_power_off_state(self, device: DeviceInfo,auto_power_off_state: bool) -> None:
        """通知设备读取自动关机状态
        
        Args:
            device: 设备信息
            auto_power_off_state: 自动关机状态
        """
        self._trigger_device_read_handler_event( 'on_device_read_auto_power_off_state', device,auto_power_off_state)

    def notify_device_read_write_print_start_command(self, device: DeviceInfo) -> None:
        """通知设备读取发送打印指令反馈
        
        Args:
            device: 设备信息
            write_print_start_command: 发送打印指令反馈
        """
        self._trigger_device_read_handler_event('on_device_read_write_print_start_command', device)
    
    

    #通知设备打印开始事件on_device_print_start
    def notify_device_print_start(self, device: DeviceInfo) -> None:
        """通知设备打印开始
        
        Args:
            device: 设备信息
        """
        self._trigger_device_print_task_handler_event('on_device_print_start', device)

    #通知打印进度事件on_device_print_progress
    def notify_device_print_progress(self, device: DeviceInfo, current: int, total: int) -> None:
        """通知设备打印进度
        
        Args:
            device: 设备信息
            current: 当前进度
            total: 总进度
        """
        self._trigger_device_print_task_handler_event('on_device_print_progress', device, current, total)
    
    #通知打印完成事件 on_device_print_finish
    def notify_device_print_finish(self, device: DeviceInfo) -> None:
        """通知设备打印完成
        
        Args:
            device: 设备信息
        """
        self._trigger_device_print_task_handler_event('on_device_print_finish', device)
    #通知指令写入事件 on_device_command_write_success
    def notify_device_command_write_success(self, device: DeviceInfo) -> None:
        """通知指令写入成功事件
        
        Args:
            device: 设备信息
        """
        self._trigger_device_command_write_handler_event('on_device_command_write_success', device)
    
    #通知指令写入错误事件 on_device_command_write_error
    def notify_device_command_write_error(self, device: DeviceInfo) -> None:
        """通知指令写入错误事件
        
        Args:
            device: 设备信息
        """
        self._trigger_device_command_write_handler_event('on_device_command_write_error', device)
    #数据写入开始事件on_device_data_write_start
    def notify_device_data_write_start(self, device: DeviceInfo) -> None:
        """通知数据写入开始事件
        
        Args:
            device: 设备信息
        """
        self._trigger_device_data_write_handler_event('on_device_data_write_start', device)

    #数据写入进度事件on_device_data_write_progress
    def notify_device_data_write_progress(self, device: DeviceInfo, current: int, total: int) -> None:
        """通知数据写入进度事件
        
        Args:
            device: 设备信息
            current: 当前进度
            total: 总进度
        """
        self._trigger_device_data_write_handler_event('on_device_data_write_progress', device, current, total)
    
    #数据写入成功事件on_device_data_write_success
    def notify_device_data_write_success(self, device: DeviceInfo) -> None:
        """通知数据写入成功事件
        
        Args:
            device: 设备信息
        """
        self._trigger_device_data_write_handler_event('on_device_data_write_success', device)
    
    #通知数据写入错误事件on_device_data_write_error
    def notify_device_data_write_error(self, device: DeviceInfo) -> None:
        """通知数据写入错误事件
        
        Args:
            device: 设备信息
        """
        self._trigger_device_data_write_handler_event('on_device_data_write_error', device)


    # 属性访问器
    @property
    def device(self) -> Optional[DeviceInfo]:
        """当前连接的设备"""
        return self._current_connection.device_info if self._current_connection else None

    def is_connected(self, device: Optional[DeviceInfo] = None) -> bool:
        """检查当前设备是否已连接"""
        # RBQLog.log("检查当前设备是否已连接，调用is_connected()方法")
        #打印当前连接设备
        # RBQLog.log(f"打印当前连接设备: {self._current_connection}")
        with self._lock:
            #如果没有指定设备，检查当前连接设备
            if device is None:
                return self._current_connection is not None and self._current_connection.strategy.is_connected()
            #如果指定了设备，检查指定设备是否已连接
            return device.device_id in self._connections and self._connections[device.device_id].strategy.is_connected()

    # 是否为ble连接
    def _is_ble_conn_type(self) -> bool:
        """是否为BLE连接类型"""
        if(self.device is not None):
            return self.device.conn_type == ConnType.BLE
        return False

    @property
    def is_ble_conn_type(self) -> bool:
        """是否为BLE连接类型"""
        return self._is_ble_conn_type()

    # 是否为经典蓝牙
    def _is_classic_conn_type(self) -> bool:
        """是否为经典蓝牙连接类型"""
        if(self.device is not None):
            return self.device.conn_type == ConnType.CLASSIC
        return False

    @property
    def is_classic_conn_type(self) -> bool:
        """是否为经典蓝牙连接类型"""
        return self._is_classic_conn_type()

    # 是否为WiFi连接
    def _is_wifi_conn_type(self) -> bool:
        """是否为WiFi连接类型"""
        if(self.device is not None):
            return self.device.conn_type == ConnType.WIFI
        return False
    
    @property
    def is_wifi_conn_type(self) -> bool:
        """是否为WiFi连接类型"""
        return self._is_wifi_conn_type()

    # 是否为AP连接
    def _is_ap_conn_type(self) -> bool:
        """是否为AP连接类型"""
        if(self.device is not None):
            return self.device.conn_type == ConnType.AP
        return False
    
    @property
    def is_ap_conn_type(self) -> bool:
        """是否为AP连接类型"""
        return self._is_ap_conn_type()

    def _is_ap_or_wifi_conn_type(self) -> bool:
        """是否为AP或WiFi连接类型
        
        注意：当前版本仅支持USB和串口连接，此方法始终返回False
        """
        if(self.device is not None):
            return self.device.conn_type == ConnType.WIFI or self.device.conn_type == ConnType.AP
        return False
    
    @property
    def is_ap_or_wifi_conn_type(self) -> bool:
        """是否为AP或WiFi连接类型"""
        return self._is_ap_or_wifi_conn_type()

    # 是否为USB连接
    def _is_usb_conn_type(self) -> bool:
        """是否为USB连接类型"""
        if(self.device is not None):
            return self.device.conn_type == ConnType.USB
        return False

    @property
    def is_usb_conn_type(self) -> bool:
        """是否为USB连接类型"""
        return self._is_usb_conn_type()
    
    # 是否为串口连接
    def _is_serial_conn_type(self) -> bool:
        """是否为串口连接类型"""
        if(self.device is not None):
            return self.device.conn_type == ConnType.SERIAL
        return False
    
    @property
    def is_serial_conn_type(self) -> bool:
        """是否为串口连接类型"""
        return self._is_serial_conn_type()

    def _is_syncing_data(self) -> bool:
        """是否正在同步数据"""
        return self._is_syncing_data
    
    @property
    def is_syncing_data(self) -> bool:
        """是否正在同步数据"""
        return self._is_syncing_data

    # 是否允许发送数据
    def _allow_send_data(self) -> bool:
        """是否允许发送数据"""
        return self._allow_send_data

    @property
    def allow_send_data(self) -> bool:
        """是否允许发送数据"""
        return self._allow_send_data
    
    
    # 析构函数，确保资源清理
    def __del__(self):
        """析构函数，确保资源清理"""
        self._shutdown()

    
    # =============================================
    # 设备发现事件处理区域
    # =============================================
    class DiscoveryHandler(DiscoveryProtocol):
        def __init__(self, manager: "ConnectManager") -> None:
            self._manager = manager

        def on_discover_start(self) -> None:
            self._manager.notify_device_discovery_start()

        def on_discover_found(self, device: DeviceInfo) -> None:
            self._manager.notify_device_discover(device)

        def on_discover_stop(self) -> None:
            self._manager.notify_device_discover_stop()

    # =============================================
    # 连接状态事件处理区域
    # =============================================
    class ConnectionStatusHandler(ConnectionStatusProtocol):
        def __init__(self, manager: "ConnectManager") -> None:
            self._manager = manager
        def on_connection_status_changed(self, status: ConnectionStatus) -> None:
            RBQLog.log(f"[ConnectManager]on_connection_status_changed() 连接状态改变: {status}")
            if status == ConnectionStatus.DISCONNECTED:
                if self._manager._current_connection.auto_reconnect:
                    self._manager._attempt_reconnect(self._manager._current_connection)
                else:
                     # 清理连接，释放资源并通知断开连接
                    self._manager._cleanup_connection(self._manager._current_connection.device_info)
                    self._manager.notify_device_disconnect(self._manager._current_connection.device_info)
            elif status == ConnectionStatus.CONNECTING:
                self._manager.notify_device_connect_start(self._manager._current_connection.device_info)
            elif status == ConnectionStatus.CONNECTED:
                self._manager.notify_device_connect_succeed(self._manager._current_connection.device_info)
            elif status == ConnectionStatus.DISCONNECTING:
                # 正在断开连接，不需要特殊处理
                pass
            else:
                self._manager.notify_device_connect_fail(self._manager._current_connection.device_info)

    # =============================================
    # 数据读取事件处理区域
    # =============================================
    class DataReadHandler(DataReadProtocol):
        def __init__(self, manager: "ConnectManager") -> None:
            self._manager = manager
        def on_data_read(self, data: bytes) -> None:
            # RBQLog.log(f"数据读取: {data}")
            self._manager._receiving(data)

    # =============================================
    # 数据写入事件处理区域
    # =============================================
    class DataWriteHandler(DataWriteProtocol):
        def __init__(self, manager: "ConnectManager") -> None:
            self._manager = manager
        def on_data_write_progress(self, index: int, tag: int, data_chunk: bytes, 
                                total_length: int, written_length: int, progress: int) -> None:
            RBQLog.log(f"数据写入进度: {progress}%")
        
        def on_data_write_success(self, index: int, tag: int, data: bytes, total_length: int) -> None:
            hex_data = ' '.join([f'{byte:02X}' for byte in data])
            RBQLog.log(f"数据写入成功: {hex_data}")

        def on_data_write_failure(self, index: int, tag: int, data: bytes, 
                                error_code: int, error_message: str) -> None:
            RBQLog.log(f"数据写入失败: {error_message}")

    #=============================================
    # 命令事件处理区域
    #=============================================
    class CommandHandler(CommandProtocol):
        def __init__(self, manager: "ConnectManager") -> None:
            self._manager = manager
        def on_command_success(self, command: Command, obj: Optional[object] = None) -> None:
            command_data: bytes = command.data
            # 转换为十六进制字符串
            hex_data = ' '.join([f'{byte:02X}' for byte in command_data])
            RBQLog.log(f"命令成功: {hex_data}")
        
        def on_command_error(self, command: Command, error_msg: str) -> None:
            RBQLog.log(f"命令错误: {error_msg}")
        
        def on_command_timeout(self, command: Command, error_msg: str) -> None:
            RBQLog.log(f"命令超时: {error_msg}")

    #=============================================
    # dataObj事件处理区域
    #=============================================
    class DataObjHandler(DataObjProtocol):
        def __init__(self, manager: "ConnectManager") -> None:
            self._manager = manager
        def on_data_obj_write_success(self, data_obj: DataObj, obj: Optional[object] = None) -> None:
            # data:bytes = data_obj.data
            # hex_data = ' '.join([f'{byte:02X}' for byte in data])
            # RBQLog.log(f"数据对象写入成功: {hex_data}")
            pass
        
        def on_data_obj_write_error(self, data_obj: Optional[DataObj], error_msg: str) -> None:
            RBQLog.log(f"数据对象写入错误: {error_msg}")
        
        def on_data_obj_write_timeout(self, data_obj: DataObj, error_msg: str) -> None:
            RBQLog.log(f"数据对象写入超时: {error_msg}")
    
    # 注意：BLE设备发现方法暂时未实现，当前版本仅支持USB和串口连接
    def discover_devices(self, conn_types: List[ConnType] = None, timeout: float = 5.0) -> None:
        """发现可用设备
        
        Args:
            conn_types: 要搜索的连接类型列表，默认搜索USB和串口
            timeout: 搜索超时时间（秒）
        """
        if conn_types is None:
            conn_types = [ConnType.USB, ConnType.SERIAL]
        
        self._is_discovering = True
        self.notify_device_discovery_start()
        
        for conn_type in conn_types:
                
            strategy = self._factory.create_strategy(conn_type)
            if strategy is None:
                RBQLog.log(f"无法创建 {conn_type} 连接策略")
                continue
            #打印当前strategy类名
            RBQLog.log(f"当前strategy类名: {strategy.__class__.__name__}")
            # 设置回调事件
            strategy.set_discovery_handler(self._discovery_handler)
            # 调用策略的设备发现事件
            strategy.discover_devices(timeout=timeout)

    # 取消设备发现
    def cancel_discovery(self, conn_types: List[ConnType] = None) -> None:
        """取消设备发现
        
        Args:
            conn_types: 要取消发现的连接类型列表，默认取消USB和串口发现
        """
        self._is_discovering = False
        if conn_types is None:
            conn_types = [ConnType.USB, ConnType.SERIAL]
        for conn_type in conn_types:
            strategy = self._factory.create_strategy(conn_type)
            if strategy is None:
                RBQLog.log(f"无法创建 {conn_type} 连接策略")
                continue
            strategy.cancel_discover_devices()
    
    def connect(self, device_info: DeviceInfo, auto_reconnect: bool = False) -> None:
        """连接设备
        
        Args:
            device_info: 设备信息
            auto_reconnect: 是否启用自动重连
        """
        #判断是否存在已连接设备
        if self._current_connection and self._current_connection.strategy.is_connected():
            RBQLog.log(f"当前已连接设备 {self._current_connection.device_info.device_id}，请先断开连接")
            self.disconnect()
            return
        # 打印将要连接设备
        RBQLog.log(f"将要连接设备: {device_info}")
        #根据策略连接设备
        strategy = self._factory.create_strategy(device_info.conn_type)
        if strategy is None:
            RBQLog.log(f"无法创建 {device_info.conn_type} 连接策略，连接失败")
            return
        #设置回调事件
        strategy.set_connection_status_handler(self._connection_status_handler)
        strategy.set_data_read_handler(self._data_read_handler)
        strategy.set_data_write_handler(self._data_write_handler)

        #存储当前连接
        self._current_connection = ManagedConnection(device_info, strategy, auto_reconnect)
        #添加到连接列表
        self._connections[device_info.device_id] = self._current_connection

        #连接设备
        strategy.connect(device_info)
        
    def disconnect(self, device: Optional[DeviceInfo] = None) -> None:
        """断开设备连接

        Args:
            device: 可选参数，指定要断开的设备，如果为None则断开所有设备连接
        """
        with self._lock:
            if not self.is_connected():
                RBQLog.log("没有设备连接，无法断开连接")
                return
            if device is None:
                # 断开所有连接
                for managed_conn in list(self._connections.values()):
                    managed_conn.auto_reconnect = False
                    if managed_conn.strategy.is_connected():
                        managed_conn.strategy.disconnect()
                        self._cleanup_connection(managed_conn)
                        RBQLog.log(f"已断开设备 {managed_conn.device_info.device_id}")
                self._current_connection = None
                self._connections.clear()
            else:
                # 断开指定设备连接
                device_id = device.device_id
                if device_id in self._connections:
                    managed_conn = self._connections[device_id]
                    managed_conn.auto_reconnect = False
                    if managed_conn.strategy.is_connected():
                        managed_conn.strategy.disconnect()
                        self._cleanup_connection(managed_conn)
                        RBQLog.log(f"已断开设备 {device_id}")
                    del self._connections[device_id]
                    if self._current_connection and self._current_connection.device_info.device_id == device_id:
                        self._current_connection = None
                else:
                    RBQLog.log(f"设备 {device_id} 未连接，无法断开连接")
    
    def write_command_context(self, command_context: CommandContext) -> None:
        """向当前连接的设备发送指令上下文
        
        Args:
            command_context: 指令上下文对象
        """
        #如果没连接，则无法发送
        if not self.is_connected():
            RBQLog.log("设备未连接，无法发送指令上下文")
            return
        #command_context 则也无法发送
        if command_context is None or command_context.command is None or command_context.command.data is None:
            RBQLog.log("指令对象或指令或指令数据为空，无法发送")
            return
        self._current_connection.strategy.write_CommandContext(command_context)
    
    def write_data_obj_context(self, data_obj_context: DataObjContext) -> None:
        """向当前连接的设备发送数据对象上下文
        
        Args:
            data_obj_context: 数据对象上下文对象
        """
        #如果没连接，则无法发送
        if not self.is_connected():
            RBQLog.log("设备未连接，无法发送数据对象上下文")
            return
        #data_obj_context 也无法发送
        if data_obj_context is None or data_obj_context.data_obj is None or data_obj_context.data_obj.data is None:
            RBQLog.log("数据对象或数据对象数据为空，无法发送")
            return
        self._current_connection.strategy.write_DataObjContext(data_obj_context)

    def write_data(self, device: Optional[DeviceInfo] = None, tag: int = 0, data: bytes = None) -> None:
        """向指定设备发送数据
        
        Args:
            device: 设备信息
            tag: 标签
            data: 要发送的数据
        """
        #如果没连接，则无法发送
        if not self.is_connected():
            RBQLog.log("设备未连接，无法发送数据")
            return

        with self._lock:
            if device is None:
                # 向所有已连接设备发送指令
                for managed_conn in self._connections.values():
                    if managed_conn.strategy.is_connected():
                        managed_conn.strategy.write_data(tag,data)
                return
            else:
                # 向指定设备发送指令
                if device.device_id in self._connections:
                    managed_conn = self._connections[device.device_id]
                if managed_conn.strategy.is_connected():
                    managed_conn.strategy.write_data(tag,data)
            return

    
    def write_data_to_devices(self, devices: List[DeviceInfo], data: bytes, tag: int) -> None:
        """向所有已连接设备发送数据
        
        Args:
            devices: 设备列表
            data: 要发送的数据
            tag: 标签
        """
        for device in devices:
            self.write_data(device, tag, data)

    def write_data_to_devices_by_conn_types(self, data: bytes, tag: int, conn_types: List[ConnType] = None) -> None:
        """向多个设备广播数据
        
        Args:
            data: 要发送的数据
            tag: 标签
            conn_types: 目标连接类型列表，None表示所有连接
        """
        
        with self._lock:
            for managed_conn in self._connections.values():
                if managed_conn.strategy.is_connected():
                    continue
                
                if conn_types and managed_conn.device_info.conn_type not in conn_types:
                    continue
                
                self.write_data(managed_conn.device_info, tag, data)

    
    def get_connection_status(self, device: DeviceInfo) -> Optional[ConnectionStatus]:
        """获取设备连接状态
        
        Args:
            device: 设备
            
        Returns:
            Optional[ConnectionStatus]: 连接状态，设备不存在时返回None
        """
        with self._lock:
            if device.device_id in self._connections:
                return self._connections[device.device_id].strategy.conn_status
            return None
    
    def get_connected_devices(self) -> List[DeviceInfo]:
        """获取已连接的设备列表
        
        Returns:
            List[DeviceInfo]: 已连接的设备信息列表
        """
        connected_devices = []
        
        with self._lock:
            for managed_conn in self._connections.values():
                if managed_conn.strategy.is_connected():
                    connected_devices.append(managed_conn.device_info)
        
        return connected_devices
    
    # 序列号生成
    def generate_sequence_number(self) -> int:
        """生成序列号
        
        Returns:
            int: 生成的序列号
        """
        with self._sequence_lock:
            self._sequence_number = (self._sequence_number + 1) % 256
            return self._sequence_number

    # 指令创建
    def create_command(self, opcode: int, params: Optional[bytes] = None) -> bytes:
        """创建指令数据包
        
        Args:
            opcode: 操作码
            params: 参数数据（可选，默认为空字节）
            
        Returns:
            bytes: 创建的指令数据包
        """
        prefix_len = 1
        packet_len_len = 2
        packet_xor_len_len = 2
        packet_ct_len = 4
        opcode_len = 2
        crc_len = 2
        params_len = len(params) if params else 0

        # 指令长度计算
        byte_len = prefix_len + packet_len_len + packet_xor_len_len + packet_ct_len + opcode_len + params_len + crc_len
        pack_len = packet_ct_len + opcode_len + params_len

        command = bytearray(byte_len)
        offset = 0

        # 前缀
        command[offset] = 0x17
        offset += 1

        # 包长度（小端）
        command[offset:offset+2] = pack_len.to_bytes(2, 'little')
        offset += 2

        # 包长度取反（小端）
        command[offset:offset+2] = (~pack_len & 0xFFFF).to_bytes(2, 'little')
        offset += 2

        # 帧序列号（4字节，小端）
        pack_ct = self.generate_sequence_number()
        command[offset:offset+4] = pack_ct.to_bytes(4, 'little')
        offset += 4

        # 操作码（2字节，小端）
        command[offset:offset+2] = opcode.to_bytes(2, 'little')
        offset += 2

        # 参数（如有）
        if params_len > 0:
            command[offset:offset+params_len] = params
            offset += params_len

        # 计算 CRC
        crc: int = CRC16.crc16_calc(command[:offset])
        command[offset:offset+2] = crc.to_bytes(2, 'big')
        offset += 2

        return bytes(command)
    
    def send_command(self, opcode: int, params: Optional[bytes] = None, tag: int = 0, delay_time: float = 0.0) -> None:
        """发送指令
        
        Args:
            opcode: 操作码
            params: 参数数据
            tag: 标签
            delay_time: 延迟时间（秒）
        """
        if not self.is_connected() or self.is_syncing_data:
            RBQLog.log(f"设备未连接或正在同步数据，不发送指令")
            return

        command_data: bytes = self.create_command(opcode, params)
        command: Command = Command.create_with_data_tag_and_delay(command_data, tag, delay_time)
        context = CommandContext.create_context(command, self._command_call_back)

        self.local_send_command(context)

    def _inner_send_command(self, opcode: int, params: Optional[bytes] = None, tag: int = -1, delay_time: float = 0.0) ->None:
        """内部发送指令
        
        Args:
            opcode: 操作码
            params: 参数数据
            tag: 标签
            delay_time: 延迟时间（秒）
        """
        if not self.is_connected():
            return
        command_data: bytes = self.create_command(opcode, params)
        command: Command = Command.create_with_data_tag_and_delay(command_data, tag, delay_time)
        context = CommandContext.create_context(command, self._command_call_back)
        self.local_send_command(context)

    def local_send_command(self, context: CommandContext) -> None:
        """本地发送指令
        
        Args:
            context: 指令上下文
        """
        with self._command_queue_lock:
            #获取当前时间
            current_time = time.time()
            off_set_time = current_time - self._last_send_command_time
            if off_set_time >= self._COMMAND_INTERVAL:
                self._last_send_command_time = current_time
                self.write_command_context(context)
            else:
                self._command_queue.append(context)
                if context.command.delay_time > 0:
                    self._clear_with__command_queue_timer()
                    self._command_queue_timer = GCDStyleTimer(
                        start=context.command.delay_time,
                        interval=0,
                        callback=self.send_queue_command,
                        repeats=False,
                        name="CommandQueueNext"
                    )
                    self._command_queue_timer.fire()

    def send_queue_command(self):
        if self._command_queue.count == 0:
            RBQLog.log("✅ 😊 commandQueue 中指令发送完毕 😊")
            return

        context = self.find_with_remove_command_context()
        self.write_command_context(context)

        if self._command_queue.count > 0:
            self._clear_with__command_queue_timer()
            self._command_queue_timer = GCDStyleTimer(
                start=self._COMMAND_INTERVAL,
                interval=0,
                callback=self.send_queue_command,
                repeats=False,
                name="CommandQueueNext"
            )
            self._command_queue_timer.fire()

    def is_current_send_command_context(context: CommandContext) -> bool:
        if context is None or context.command is None or context.command.data is None:
            return False

        command = context.command
        if command.delay_time == -1:
            return True

        current_time = time.time()
        offset = current_time - command.create_time

        # 目前忽略 is_loss_on_timeout 的处理
        if offset >= command.delay_time:
            return True
        return False
    
    # 从队列中查找并移除需要移除的指令上下文
    def find_with_remove_command_context(self):
        found_context = None
        current_time = time.time()
        for context in self._command_queue:
            command = context.command
            if command:
                if command.delay_time == -1:
                    found_context = context
                    break
                elif command.delay_time < current_time - command.create_time:
                    found_context = context
                    break
        if found_context:
            self._command_queue.remove(found_context)

        return found_context

    # 写入打印机参数
    def write_printer_parameters(self, printer_head: int, l_pix: int, p_pix: int, distance: int, tag: int = 0, delay_time: float = 0.0) -> None:
        """写入当前设备参数"""
        if self.is_connected():

            l_pix_0 = l_pix & 0xFF
            l_pix_1 = (l_pix >> 8) & 0xFF
            p_pix_0 = p_pix & 0xFF
            p_pix_1 = (p_pix >> 8) & 0xFF

            delayDistance0 = distance & 0xFF
            delayDistance1 = (distance >> 8) & 0xFF
            delayDistance2 = (distance >> 16) & 0xFF
            delayDistance3 = (distance >> 24) & 0xFF

            params = bytes([printer_head, p_pix_0, p_pix_1, l_pix_0, l_pix_1, delayDistance0, delayDistance1, delayDistance2, delayDistance3, 0, 0])
            self.send_command(OpCode.WRITE_PRINTER_PARAMETERS, params, tag, delay_time)

    # 读取打印头参数
    def read_printer_parameters(self, tag: int = 0, delay_time: float = 0.0) -> None:
        self.send_command(OpCode.READ_PRINTER_PARAMETERS, tag, delay_time)
    
    # 读取读取循环打印次数和重复打印次数
    def read_circulation_and_repeat_time(self, tag: int = 0, delay_time: float = 0.0) -> None:
        self.send_command(OpCode.READ_CIRCULATION_AND_REPEAT_TIMES, tag, delay_time)

    # 写入循环打印次数和重复打印次数
    def write_circulation_and_repeat_time(self, circulation: int, repeat: int, tag: int = 0, delay_time: float = 0.0) -> None:
        circulation0 =  circulation & 0xFF
        circulation1 = (circulation >> 8) & 0xFF
        repeat0 = repeat & 0xFF
        repeat1 = (repeat >> 8) & 0xFF
        params = bytes([circulation0, circulation1, repeat0, repeat1])
        self.send_command(OpCode.WRITE_CIRCULATION_AND_REPEAT_TIMES, params, tag, delay_time)
            

    # 读取打印方向
    def read_print_direction(self, tag: int = 0, delay_time: float = 0.0) -> None:
        self.send_command(OpCode.READ_PRINT_DIRECTION, tag, delay_time)

    # 写入打印方向
    def write_print_direction(self, horizontal_direction: int, vertical_direction: int, tag: int = 0, delay_time: float = 0.0) -> None:
        if horizontal_direction > 1 or horizontal_direction < 0 or vertical_direction > 1 or vertical_direction < 0:
            return
        params = bytes([horizontal_direction, vertical_direction])
        self.send_command(OpCode.WRITE_PRINT_DIRECTION, params, tag, delay_time)
    
    # 读取软件信息
    def read_software_info(self, tag: int = 0, delay_time: float = 0.0) -> None:
        self.send_command(OpCode.READ_SOFTWARE_INFO, tag, delay_time)

    # 读取电量
    def read_battery(self, tag: int = 0, delay_time: float = 0.0) -> None:
        """读取当前设备电池信息"""
        self.send_command(OpCode.READ_BATTERY, tag, delay_time)
    
    # 读取静音状态
    def read_silent_state(self, tag: int = 0, delay_time: float = 0.0) -> None:
        """读取当前设备静音状态"""
        self.send_command(OpCode.READ_SILENT_STATE, tag, delay_time)

    # 写入静音状态
    def write_silent_state(self, silent_state: bool, tag: int = 0, delay_time: float = 0.0) -> None:
        """写入当前设备静音状态"""
        state = 1 if silent_state else 0
        params = bytes([state])
        self.send_command(OpCode.WRITE_SILENT_STATE, params, tag, delay_time)
    
    # 读取自动关机状态
    def read_auto_power_off_state(self, tag: int = 0, delay_time: float = 0.0) -> None:
        """读取当前设备自动关机状态"""
        self.send_command(OpCode.READ_AUTO_POWER_OFF_STATE, tag, delay_time)

    # 写入自动关机状态
    def write_auto_power_off_state(self, auto_power_off_state: bool, tag: int = 0, delay_time: float = 0.0) -> None:
        """写入当前设备自动关机状态"""
        state = 1 if auto_power_off_state else 0
        params = bytes([state])
        self.send_command(OpCode.WRITE_AUTO_POWER_OFF_STATE, params, tag, delay_time)

    #写入开始打印指令
    def write_start_print(self, tag: int = 0, delay_time: float = 0.0) -> None:
        """写入当前设备开始打印指令"""
        self.send_command(OpCode.WRITE_PRINT_START_COMMAND, tag, delay_time)

    #读取墨盒id
    def read_printer_id(self, tag: int = 0, delay_time: float = 0.0) -> None:
        """读取当前设备墨盒id"""
        self.send_command(OpCode.READ_CARTRIDGE_ID, tag, delay_time)

    def write_connect_state_connected(self) -> None:
        """写入当前设备连接状态为已连接"""
        state = bytes([0x17,0x07,0x00, 0xF8, 0xFF,0x01,0x00,0x00,0x00,0x02,0x02,0x01, 0xE2,0x55])
        dataObj:DataObj = DataObj(state)
        context = DataObjContext(dataObj, self._data_obj_call_back)
        self.write_data_obj_context(context)

    #发送设备连接信号
    def write_connect_state_connected(self) -> None:
        """写入当前设备连接状态为已连接"""
        state = bytes([0x17,0x07,0x00, 0xF8, 0xFF,0x01,0x00,0x00,0x00,0x02,0x02,0x01, 0xE2,0x55])
        dataObj:DataObj = DataObj(state)
        context = DataObjContext(dataObj, self._data_obj_call_back)
        self.write_data_obj_context(context)

    #发送设备断开信号
    def write_connect_state_disconnected(self) -> None:
        """写入当前设备连接状态为已断开"""
        state = bytes([0x17,0x07,0x00, 0xF8, 0xFF,0x01,0x00,0x00,0x00,0x02,0x02,0x00,0x62,0x50])
        dataObj:DataObj = DataObj(state)
        context = DataObjContext(dataObj, self._data_obj_call_back)
        self.write_data_obj_context(context)
        
    #清除指令队列中的指令
    def _clear_command_queue(self) -> None:
        """清空指令队列"""
        with self._command_queue_lock:
            self._command_queue.clear()

    def _start_packet(self, packet):
        for _packet in self._packets:
            if packet != _packet:
                packet.start = False
        packet.start = True

    def _cancel_all_packet_start(self):
        for packet in self._packets:
            packet.start = False

    def _has_packet_start_sending(self) -> bool:
        """
        检查是否有数据包正在发送
        
        Returns:
            bool: 如果有数据包正在发送返回True，否则返回False
        """
        is_start = False
        for packet in self._packets:
            if packet.start:
                is_start = True
                break
        return is_start

    # ==================== MultiRowData 数据包方法系列 ====================
    def cancel_send_multi_row_data_packet(self) -> None:
        """取消发送多行数据包"""
        self._clear_wait_data_transfer_response_timer()
        self._multi_row_data_packet.clear()


    def set_with_send_multi_row_data_packet(self, multi_row_data: MultiRowData, fn: int = STX_E) -> None:
        """发送多行数据包
        Args:
            multi_row_data: 多行数据对象 (MultiRowData)
            fn: 协议类型（可选，默认协议类型为STX_E）
        """
        
        # 如果没有连接，则不发送
        if not self.is_connected():
            RBQLog.log_error("设备未连接，无法发送多行数据包")
            self.notify_device_data_transfer_error(1, "设备未连接，无法发送多行数据包")
            return
        
        # 检查指令队列是否为空
        if self._is_command_queue_empty():
            error_msg = "指令集中还存在指令正在处理，请稍等..."
            RBQLog.log_error(f"mxSdk错误，{error_msg}")
            self.notify_device_data_transfer_error(1, error_msg)
            return
        
        # 初始化发送状态
        self._n_index = 0
        
        # 设置多行数据包
        self._multi_row_data_packet.set(multi_row_data, fn)
        
        # 开始发送数据
        self._local_set_with_send_multi_row_data_packet()
        
        # 设置重试定时器
        self._clear_wait_data_transfer_response_timer()
        self._create_with_fire_wait_data_transfer_response_timer(3.0, self._local_set_with_send_multi_row_data_packet)

        RBQLog.log_info("----【send_multi_row_data_packet】发送多行数据包发送----")
    
    def _local_set_with_send_multi_row_data_packet(self) -> None:
        """发送多行数据包"""
        #如果没数据
        if not self._multi_row_data_packet.has_data():
            self.notify_device_data_transfer_error(1, "数据包没有数据")
            return
        self._json_stream_assembler.reset()
        self._start_packet(self._multi_row_data_packet)
        self._clear_command_queue()

        RBQLog.log(f"----是否已经启动packet数据发生----{self._has_packet_start_sending()}")

        currentRow: int = self._multi_row_data_packet.current_row
        arr_index_data_size: int = self._multi_row_data_packet.current_row_data_length

        dataSize0 = (arr_index_data_size & 0xFF)
        dataSize1 = ((arr_index_data_size >> 8) & 0xFF)
        dataSize2 = ((arr_index_data_size >> 16) & 0xFF)
        dataSize3 = ((arr_index_data_size >> 24) & 0xFF)
        compress = (self._multi_row_data_packet.compress & 0xFF)

        params: bytearray = bytearray([currentRow, dataSize0, dataSize1, dataSize2, dataSize3, compress])
        self._inner_send_command(OpCode.TRANSMIT_PICTURE_DATA, params)
        self._multi_row_data_packet.start_time = time.time()
        size: float = self._multi_row_data_packet.total_data_len / 1000.0
        # //发送进度更新事件
        self.notify_device_data_transfer_start(self._current_connection.device_info, size, self._multi_row_data_packet.start_time, time.time())

    def send_next_multi_row_data_packet(self) -> None:
        """发送下一个多行数据包"""
        if not self.is_connected():
            self.notify_device_data_transfer_error(1, "设备未连接，无法发送下一个多行数据包")
            return
        data: bytes = self._multi_row_data_packet.get_next_packet()
        self._multi_row_data_packet.current_time = time.time()

        updateProgress: bool = self._multi_row_data_packet.invalidate_progress()
        if updateProgress:
            progress: int = self._multi_row_data_packet.get_progress()
            size: float = self._multi_row_data_packet.total_data_len / 1000.0
            self.notify_device_data_transfer_progress(self._current_connection.device_info,size, progress, self._multi_row_data_packet.start_time, self._multi_row_data_packet.current_time)
        format_data: bytes = self._multi_row_data_packet.packet_format(data)
        data_obj = DataObj(format_data)
        data_obj_context = DataObjContext(data_obj, self._data_obj_call_back)
        self.write_data_obj_context(data_obj_context)
    
    def send_nak_multi_row_data_packet(self) -> None:
        """重传当前多行数据包（NAK响应）"""
        if not self.is_connected():
            self.notify_device_data_transfer_error(1, "设备未连接，无法发送NAK重传当前包")
            return
        data: bytes = self._multi_row_data_packet.get_current_packet()
        self._multi_row_data_packet.current_time = time.time()
        format_data: bytes = self._multi_row_data_packet.packet_format(data)
        data_obj = DataObj(format_data)
        data_obj_context = DataObjContext(data_obj, self._data_obj_call_back)
        self.write_data_obj_context(data_obj_context)

    # =============== ota ===============
    def cancel_send_ota_data_packet(self) -> None:
        """取消发送OTA数据包"""
        self._clear_wait_data_transfer_response_timer()
        self._ota_data_packet.clear()
    
    def set_with_send_ota_data_packet(self, data: bytes, fn: int = STX_E) -> None:
        """设置并发送OTA数据包
        
        Args:
            data: OTA数据包数据
            fn: 协议类型
        """
        # 如果没有连接，则不发送
        if not self.is_connected():
            RBQLog.log_error("设备未连接，无法发送多行数据包")
            self.notify_device_data_transfer_error(1, "设备未连接，无法发送多行数据包")
            return
        
        if self._is_command_queue_empty():
            error_msg = "指令集中还存在指令正在处理，请稍等..."
            RBQLog.log_error(f"mxSdk错误，{error_msg}")
            self.notify_device_data_transfer_error(1, error_msg)
            return
        self._ota_data_packet.set(data, fn)
        self._local_set_with_send_ota_data_packet()
        #重置定时器
        self._clear_wait_data_transfer_response_timer()
        self._create_with_fire_wait_data_transfer_response_timer(3.0, self._local_set_with_send_ota_data_packet)

        RBQLog.log_info("设置并发送OTA数据包")
    
    def _local_set_with_send_ota_data_packet(self) -> None:
        """本地设置并发送OTA数据包"""
        if not self._ota_data_packet.has_data():
            self.notify_device_data_transfer_error(1, "OTA数据包数据为空")
            return
        self._json_stream_assembler.reset()
        self._start_packet(self._ota_data_packet)
        self._clear_command_queue()

        dataLength: int = self._ota_data_packet.total_data_len
        dataSize0: int = dataLength & 0xFF
        dataSize1: int = (dataLength >> 8) & 0xFF
        dataSize2: int = (dataLength >> 16) & 0xFF
        dataSize3: int = (dataLength >> 24) & 0xFF

        RBQLog.log_info(f"OTA数据包数据长度：{dataLength}")

        params: bytearray = bytearray([dataSize0, dataSize1, dataSize2, dataSize3])
        self._inner_send_command(OpCode.UPDATE_MCU, params)

        size: float = dataLength / 1000.0
        self._ota_data_packet.start_time = time.time()
        self.notify_device_data_transfer_start(self._current_connection.device_info, size, self._ota_data_packet.start_time, time.time())

    def send_next_ota_packet(self) -> None:
        """设置并发送下一个OTA数据包"""
        if not self.is_connected():
            self.notify_device_data_transfer_error(1, "设备未连接，无法发送下一个OTA数据包")
            return
        data: bytes = self._ota_data_packet.get_next_packet()
        self._ota_data_packet.current_time = time.time()

        updateProgress: bool = self._ota_data_packet.invalidate_progress()
        if updateProgress:
            progress: int = self._ota_data_packet.get_progress()
            size: float = self._ota_data_packet.total_data_len / 1000.0
            self.notify_device_data_transfer_progress(self._current_connection.device_info,size, progress, self._ota_data_packet.start_time, self._ota_data_packet.current_time)
        format_data: bytes = self._ota_data_packet.packet_format(data)
        data_obj = DataObj(format_data)
        data_obj_context = DataObjContext(data_obj, self._data_obj_call_back)
        self.write_data_obj_context(data_obj_context)

    def send_nak_ota_packet(self) -> None:
        """重传当前OTA数据包（NAK响应）"""
        if not self.is_connected():
            self.notify_device_data_transfer_error(1, "设备未连接，无法发送NAK重传当前OTA数据包")
            return
        data: bytes = self._ota_data_packet.get_current_packet()
        self._ota_data_packet.current_time = time.time()
        format_data: bytes = self._ota_data_packet.packet_format(data)
        data_obj = DataObj(format_data)
        data_obj_context = DataObjContext(data_obj, self._data_obj_call_back)
        self.write_data_obj_context(data_obj_context)

    def cancel_send_logo_packet(self) -> None:
        """取消发送Logo数据包"""
        if not self.is_connected():
            self.notify_device_data_transfer_error(1, "设备未连接，无法取消发送Logo数据包")
            return
        self._clear_wait_data_transfer_response_timer()
        self._logo_data_packet.clear()

    # =============== LogoData 数据包方法系列===============
    def set_with_send_logo_packet(self, logo_data: LogoData, fn: int = STX_E) -> None:
        """设置并发送Logo数据包
        
        Args:
            logo_data: Logo数据包数据
            fn: 协议类型
        """
        if not self.is_connected():
            self.notify_device_data_transfer_error(1, "设备未连接，无法发送Logo数据包")
            return
        if self._is_command_queue_empty():
            error_msg = "指令集中还存在指令正在处理，请稍等..."
            RBQLog.log_error(f"mxSdk错误，{error_msg}")
            self.notify_device_data_transfer_error(1, error_msg)
            return
        self._logo_data_packet.set(logo_data, fn)
        self._local_set_with_send_logo_packet()
        #重置定时器
        self._clear_wait_data_transfer_response_timer()
        self._create_with_fire_wait_data_transfer_response_timer(3.0, self._local_set_with_send_logo_packet)

    def _local_set_with_send_logo_packet(self) -> None:
        """本地设置并发送Logo数据包"""
        if not self._logo_data_packet.has_data():
            self.notify_device_data_transfer_error(1, "Logo数据包数据为空")
            return
        self._json_stream_assembler.reset()
        self._start_packet(self._logo_data_packet)
        self._clear_command_queue()

        dataLength: int = self._logo_data_packet.total_data_len
        dataSize0: int = dataLength & 0xFF
        dataSize1: int = (dataLength >> 8) & 0xFF
        dataSize2: int = (dataLength >> 16) & 0xFF
        dataSize3: int = (dataLength >> 24) & 0xFF

        RBQLog.log(f"设置并发送Logo数据包，数据长度：{dataLength}")

        params: bytearray = bytearray([dataSize0, dataSize1, dataSize2, dataSize3])
        self._inner_send_command(OpCode.WRITE_LOGO_DATA, params)

        size: float =  self._logo_data_packet.total_data_len / 1000.0
        self._logo_data_packet.start_time = time.time()
        self.notify_device_data_transfer_start(self._current_connection.device_info, size, self._logo_data_packet.start_time, time.time())

    def send_next_logo_packet(self) -> None:
        """发送下一个Logo数据包"""
        if not self.is_connected():
            self.notify_device_data_transfer_error(1, "设备未连接，无法发送下一个Logo数据包")
            return
        data: bytes = self._logo_data_packet.get_next_packet()
        self._logo_data_packet.current_time = time.time()

        update_progress: bool = self._logo_data_packet.invalidate_progress()
        if update_progress:
            progress: int = self._logo_data_packet.get_progress()
            size: float = self._logo_data_packet.total_data_len / 1000.0
            self.notify_device_data_transfer_progress(self._current_connection.device_info,size, progress, self._logo_data_packet.start_time, self._logo_data_packet.current_time)

        format_data: bytes = self._logo_data_packet.packet_format(data)
        data_obj = DataObj(format_data)
        data_obj_context = DataObjContext(data_obj, self._data_obj_call_back)
        self.write_data_obj_context(data_obj_context)

    def send_nak_logo_packet(self) -> None:
        """重传当前Logo数据包（NAK响应）"""
        if not self.is_connected():
            self.notify_device_data_transfer_error(1, "设备未连接，无法发送NAK重传当前Logo数据包")
            return
        data: bytes = self._logo_data_packet.get_current_packet()
        self._logo_data_packet.current_time = time.time()
        format_data: bytes = self._logo_data_packet.packet_format(data)
        data_obj = DataObj(format_data)
        data_obj_context = DataObjContext(data_obj, self._data_obj_call_back)
        self.write_data_obj_context(data_obj_context)

    def _is_command_queue_empty(self) -> bool:
        """检查指令队列是否为空

        Returns:
            bool: 如果指令队列为空返回True，否则返回False
        """
        with self._command_queue_lock:
            return self._command_queue.count == 0

    #清除并重置数据延时指令定时器
    def _clear_data_transfer_delay_command_timer(self) -> None:
        """清除并重置数据延时指令定时器"""
        try:
            if self._data_transfer_delay_command_timer:
                self._data_transfer_delay_command_timer.clear()
                self._data_transfer_delay_command_timer = None
            RBQLog.log_debug("已清除数据延时指令定时器")
        except Exception as e:
            RBQLog.log_error(f"清除数据延时指令定时器失败: {str(e)}")

    def _create_with_fire_data_transfer_delay_command_timer(self, start: float, callback: Callable[[], None]) -> None:
        """设置数据延时指令定时器

        Args:
            start (float): 定时器启动时间（秒）
            callback (Callable[[], None]): 定时器回调函数
        """
        #先清除旧的指令队列计时器
        self._clear_data_transfer_delay_command_timer()
        #新建指令队列计时器并启动
        self._data_transfer_delay_command_timer = GCDStyleTimer(start, 0, callback, False, "DataTransferDelayCommandTimer")
        self._data_transfer_delay_command_timer.fire()

    # 清除并重置等待数据传输响应定时器
    def _clear_wait_data_transfer_response_timer(self) -> None:
        """清除并重置等待数据传输响应定时器"""
        try:
            if self._wait_data_transfer_response_timer:
                self._wait_data_transfer_response_timer.clear()
                self._wait_data_transfer_response_timer = None
                RBQLog.log_debug("已清除等待响应定时器")
        except Exception as e:
            RBQLog.log_error(f"清除定时器失败: {str(e)}")

    #创建并启动等待数据传输响应定时器
    def _create_with_fire_wait_data_transfer_response_timer(self, start: float, interval: float, callback: Callable[[], None]) -> None:
        """设置等待数据传输响应定时器

        Args:
            start (float): 定时器启动时间（秒）
            callback (Callable[[], None]): 定时器回调函数
        """
        #先清除旧的等待数据传输响应计时器
        self._clear_wait_data_transfer_response_timer()
        #新建数据传输响应计时器并启动
        self._wait_data_transfer_response_timer = GCDStyleTimer(start, interval, callback, False, "WaitDataTransferResponseTimer")
        self._wait_data_transfer_response_timer.fire()

    def _clear_with__command_queue_timer(self) -> None:
        """清除并重置指令队列定时器"""
        try:
            if self._command_queue_timer:
                self._command_queue_timer.clear()
                self._command_queue_timer = None
            RBQLog.log_debug("已清除指令队列定时器")
        except Exception as e:
            RBQLog.log_error(f"清除指令队列定时器失败: {str(e)}")

    def _create_with_fire_command_queue_timer(self, start: float, interval: float, callback: Callable[[], None]) -> None:
        """设置指令队列定时器

        Args:
            start (float): 定时器启动时间（秒）
            callback (Callable[[], None]): 定时器回调函数
        """
        #先清除旧的指令队列计时器
        self._clear_with__command_queue_timer()
        #新建指令队列计时器并启动
        self._command_queue_timer = GCDStyleTimer(start, interval, callback, False, "CommandQueueTimer")
        self._command_queue_timer.fire()

    #清除并重置心跳定时器
    def _clear_heart_timer(self) -> None:
        """清除并重置心跳定时器"""
        try:
            if self._heart_timer:
                self._heart_timer.clear()
                self._heart_timer = None
            RBQLog.log_debug("已清除心跳定时器")
        except Exception as e:
            RBQLog.log_error(f"清除心跳定时器失败: {str(e)}")

    def _create_with_fire_heart_timer(self, start: float, interval: float, callback: Callable[[], None]) -> None:
        """设置心跳定时器

        Args:
            start (float): 定时器启动时间（秒）
            callback (Callable[[], None]): 定时器回调函数
        """
        #先清除旧的心跳计时器
        self._clear_heart_timer()
        #新建心跳计时器并启动
        self._heart_timer = GCDStyleTimer(start, interval, callback, False, "HeartTimer")
        self._heart_timer.fire()

    # 开始启动心跳
    def _start_monitor_heart(self, start: int) -> None:
        pass
    
    #停止心跳
    def _stop_monitor_heart(self) -> None:
        pass
    
    def _shutdown(self):
        """关闭连接管理器，断开所有连接"""

        RBQLog.log_debug("调用[_shutdown]函数，开始关闭连接管理器")

        # 停止监控线程
        self._monitor_running = False

        # 清理所有定时器
        self._clear_heart_timer()
        self._clear_with__command_queue_timer()
        self._clear_wait_data_transfer_response_timer()
        
        # 断开所有连接
        with self._lock:
            device_ids = list(self._connections.keys())
            for device_id in device_ids:
                device: DeviceInfo = self._connections[device_id].device_info
                self.disconnect(device)
                self._cleanup_connection(device)
    
    def _start_monitor(self):
        """启动连接监控线程"""
        self._monitor_running = True
        monitor_thread = threading.Thread(
            target=self._monitor_connections,
            daemon=True,
            name='connection_monitor'
        )
        monitor_thread.start()
        RBQLog.log_debug("连接监控线程已启动")
    
    def _monitor_connections(self):
        """监控连接状态，处理自动重连"""
        while self._monitor_running:
            try:
                with self._lock:
                    for device_id, managed_conn in list(self._connections.items()):
                        # 检查连接状态
                        if managed_conn.strategy.conn_status == ConnectionStatus.CONNECTED:
                            if not managed_conn.strategy.is_connected():
                                managed_conn.strategy.conn_status = ConnectionStatus.DISCONNECTED
                                RBQLog.log(f"检测到设备 {device_id} 连接断开")
                                
                        # 处理自动重连
                        if (managed_conn.strategy.conn_status == ConnectionStatus.DISCONNECTED and 
                            managed_conn.auto_reconnect and 
                            managed_conn.reconnect_attempts < managed_conn.max_reconnect_attempts):
                            
                            self._attempt_reconnect(managed_conn)
                
                time.sleep(1.0)  # 每秒检查一次
                
            except Exception as e:
                RBQLog.log(f"连接监控异常: {str(e)}")
                time.sleep(5.0)  # 异常时等待更长时间
    
    def _attempt_reconnect(self, managed_conn: ManagedConnection) -> None:
        """尝试重连设备
        
        Args:
            managed_conn: 管理的连接对象
        """
        device_id = managed_conn.device_info.device_id
        managed_conn.reconnect_attempts += 1
        managed_conn.strategy.conn_status = ConnectionStatus.CONNECTING
        
        RBQLog.log(f"尝试重连设备 {device_id} (第 {managed_conn.reconnect_attempts} 次)")
        
        try:
            managed_conn.strategy.connect(device_info=managed_conn.device_info)
            # 连接结果将通过事件回调处理
            RBQLog.log(f"已发起设备 {device_id} 重连请求")
        except Exception as e:
            managed_conn.strategy.conn_status = ConnectionStatus.CONNECT_FAIL
            RBQLog.log(f"设备 {device_id} 重连异常: {str(e)}")
    
    def _cleanup_connection(self, device: DeviceInfo) -> None:
        """清理连接资源
        
        Args:
            device: 设备信息
        """
        RBQLog.log(f"调用[_cleanup_connection]函数，开始清理连接资源 清理设备->device: {device}")
        #查找并清理 device 对应的 managedConnection 并 断开连接
        for managed_conn in self._connections.values():
            if managed_conn.device_info == device:
                del self._connections[managed_conn.device_info.device_id]
                managed_conn.strategy.disconnect()
                break
        #清理指令队列定时器
        self._clear_with__command_queue_timer()
        #清理心跳定时器
        self._clear_heart_timer()
        #停止心跳
        self._stop_monitor_heart()
        #清理等待数据传输响应定时器
        self._clear_wait_data_transfer_response_timer()
        #清理指令队列 
        self._clear_command_queue()
    
    
    def _receiving(self, data: bytes) -> None:
        
        # 将字节数据解码为字符串后打印
        try:
            decoded_data: str = data.decode('utf-8')
        except UnicodeDecodeError:
            decoded_data = str(data)  # 解码失败时保留原始字节格式
        RBQLog.log(f" <-- 原始数据->decoded_data: {decoded_data} --")

        self.notify_device_read_data(self._current_connection.device_info,data)

        with self._receive_lock:
            try:
                if not self._has_packet_start_sending():
                    # 接收json
                    RBQLog.log(f" <-- [_receiving]接收json: {data}")
                    self._json_stream_assembler.feed(data)
                    return
                        
                # 处理二进制数据包
                self._dispatch_data_event(data)
                
            except Exception as e:
                RBQLog.log(f"数据接收处理异常: {str(e)}")

    def on_json_complete(self, json_str: str):
        self._dispatch_json_event(json_str)
    
    def _dispatch_json_event(self, json_str: str) -> None:
        """分发JSON事件
        
        解析JSON数据并根据命令类型分发相应的事件。
        
        Args:
            json_str: JSON字符串
        """
        RBQLog.log(f" <-- dispatchJsonEvent: {json_str} --")
        
        try:
            data_dict: dict = json.loads(json_str)
            code = data_dict.get('code', -1)
            
            if code == 0:

                cmd = data_dict.get('cmd', -1)
                
                if cmd == OpCode.READ_PRINTER_PARAMETERS.value:
                    self._handle_parameter_response(data_dict)
                elif cmd == OpCode.READ_CIRCULATION_AND_REPEAT_TIMES:
                    self._handle_circulation_and_repeat_times_response(data_dict)
                elif cmd == OpCode.READ_PRINT_DIRECTION.value:
                    self._handle_direction_response(data_dict)
                elif cmd == OpCode.READ_SOFTWARE_INFO.value:
                    self._handle_device_software_info_response(data_dict)
                elif cmd == OpCode.READ_CARTRIDGE_ID.value:
                    self._handle_cartridge_id_response(data_dict)
                elif cmd == OpCode.READ_PRINT_TEMPERATURE.value:
                    self._handle_temperature_response(data_dict)
                elif cmd == OpCode.READ_BATTERY.value:
                    self._handle_battery_response(data_dict)
                elif cmd == 4130:
                    #每5秒发一次低电提醒
                    RBQLog.log(f" <-- 低电量提醒 4130: {data_dict}")
                elif cmd == 4098:
                    # 4098开始清洗打印头
                    RBQLog.log(f" <-- 开始清洗打印头 4098: {data_dict}")
                elif cmd == 4099:
                    # 4099清洗完成
                    RBQLog.log(f" <-- 清洗完成 4099: {data_dict}")
                elif cmd == OpCode.PRINT_START.value:
                    # 4099清洗完成后，打印头开始打印
                    self._handle_print_start(data_dict)
                elif cmd == OpCode.PRINT_COMPLETED.value:
                    # 打印完成
                    self._handle_print_completed(data_dict)
                elif cmd == 514 and self.is_serial_conn_type():
                    # 514 表示通过串口和打印机连接成功
                    self._handle_session_even(data_dict)
                elif cmd == OpCode.READ_SILENT_STATE.value:
                    self._handle_silent_state_response(data_dict)
                elif cmd == OpCode.READ_AUTO_POWER_OFF_STATE.value:
                    self._handle_auto_power_off_response(data_dict)
                elif cmd == OpCode.WRITE_PRINT_START_COMMAND.value:
                    # 打印开始命令
                    self._handle_write_print_start_command(data_dict)
                else:
                    # 读取到一般指令
                    self._handle_general_command(data_dict)
            else:
                RBQLog.log(f"命令执行失败，错误码: {code}")
                
        except json.JSONDecodeError as e:
            RBQLog.log(f"JSON解析失败: {str(e)}")
        except Exception as e:
            RBQLog.log(f"JSON事件分发异常: {str(e)}")

    def _handle_parameter_response(self, data_dict: dict) -> None:
        """处理参数信息响应
        
        Args:
            data_dict: 响应数据字典
        """
        if not self.is_connected():
            return
        msg: str = data_dict.get('msg', '')
        parameters = msg.split(',')
        head_value = int(parameters[0])
        l_pix = int(parameters[1])
        p_pix = int(parameters[2])
        distance = int(parameters[3])

        RBQLog.log(f" <-- 参数响应: {head_value},{l_pix},{p_pix},{distance}")

        self.notify_device_read_print_head_parameter(self._current_connection.device_info,head_value,l_pix,p_pix,distance)
    
    def _handle_circulation_and_repeat_times_response(self, data_dict: dict) -> None:
        """处理循环和重复次数响应
        
        Args:
            data_dict: 响应数据字典
        """
        if not self.is_connected():
            return
        # 根据实际参数结构解析
        msg: str = data_dict.get('msg', '')
        parameters = msg.split(',')
        circulation_time = int(parameters[0])
        repeat_time = int(parameters[1])
        RBQLog.log(f" <-- 循环和重复次数响应: {circulation_time},{repeat_time}")
        self.notify_device_read_circulation_repeat_times(self._current_connection.device_info,circulation_time,repeat_time)

    def _handle_direction_response(self, data_dict: dict) -> None:
        """处理方向信息响应
        
        Args:
            data_dict: 响应数据字典
        """
        if not self.is_connected():
            return
        msg: str = data_dict.get('msg', '')
        parameters: list = msg.split(',')
        horizontalDirection: int = int(parameters[0])
        verticalDirection: int = int(parameters[1])

        oldHorizontalDirection = self._current_connection.device_info.horizontalDirection
        oldVerticalDirection = self._current_connection.device_info.verticalDirection
        
        RBQLog.log(f" <-- 打印方向: {horizontalDirection},{verticalDirection}; 旧打印方向: {oldHorizontalDirection},{oldVerticalDirection}")
        
        # 触发方向读取回调
        self.notify_device_read_print_direction_and_print_head_direction(self._current_connection.device_info ,horizontalDirection,verticalDirection,oldHorizontalDirection,oldVerticalDirection) 

    def _handle_device_software_info_response(self, data_dict: dict) -> None:
        """处理软件信息响应
        Args:
            data_dict: 响应数据字典
            printer_head_id: 打印头ID
            name: 软件名称
            mcu_ver: MCU版本
            date: 编译日期
        """
        if not self.is_connected():
            return
        printer_head_id: str = data_dict.get('id', '')
        name: str = data_dict.get('name', '')
        mcu_ver: str = data_dict.get('mcu_ver', '')
        date: str = data_dict.get('date', '')
        
        RBQLog.log(f" <-- deprinter_head_idviceId: {printer_head_id}; name: {name}; mcu_ver: {mcu_ver}; date: {date}")
        self.notify_device_read_device_software_info(self._current_connection.device_info,printer_head_id, name, mcu_ver, date)
    
    def _handle_cartridge_id_response(self, data_dict: dict) ->None:
        """处理墨盒ID cartridges ID 响应
        Args:
            data_dict: 响应数据字典
        """
        if not self.is_connected():
            return
        cartridge_id: str = data_dict.get('id', '')
        RBQLog.log(f" <-- cartridge_id: {cartridge_id}")
        self.notify_device_read_cartridge_id(self._current_connection.device_info,cartridge_id)

    def _handle_temperature_response(self, data_dict: dict) -> None:
        """处理温度信息响应
        
        Args:
            data_dict: 响应数据字典
        """
        if not self.is_connected():
            return
        temperature1: int = data_dict.get('temp_set', 0)
        temperature2: int = data_dict.get('temp_get', 0)
        temperature: int = temperature1 if temperature1 > 0 else temperature2
        RBQLog.log(f" <-- 打印头温度: {temperature}°C")
        self.notify_device_read_print_head_temperature(self._current_connection.device_info,temperature)

    def _handle_battery_response(self, data_dict: dict) -> None:
        """处理电池信息响应
        
        Args:
            data_dict: 响应数据字典
        """
        if not self.is_connected():
            return
        battery_level: int = data_dict.get('bat', 0)
        RBQLog.log(f" <-- 电池电量: {battery_level}%")
        self.notify_device_read_battery( self._current_connection.device_info, battery_level)
    
    def _handle_print_start(self, data_dict: dict) -> None:
        """处理打印开始响应
        
        Args:
            data_dict: 响应数据字典
        """
        if not self.is_connected():
            return
        msg: str = data_dict.get('msg', '')
        parameters: list = msg.split(',')
        beginIndex: int = int(parameters[0])
        endIndex: int = int(parameters[1])
        currentIndex: int = int(parameters[2])
        RBQLog.log(f" <-- 打印开始响应: {beginIndex},{endIndex},{currentIndex}")
        self.notify_device_read_print_start(self._current_connection.device_info, beginIndex, endIndex, currentIndex)

    def _handle_print_completed(self, data_dict: dict) -> None:
        """处理打印完成响应
        
        Args:
            data_dict: 响应数据字典
        """
        if not self.is_connected():
            return
        msg: str = data_dict.get('msg', '')
        parameters: list = msg.split(',')
        beginIndex: int = int(parameters[0])
        endIndex: int = int(parameters[1])
        currentIndex: int = int(parameters[2])
        cartridgeId: str = ''
        if len(parameters) > 3:
            cartridgeId = parameters[3]
        RBQLog.log(f" <-- 打印完成响应: {beginIndex},{endIndex},{currentIndex},{cartridgeId}")
        self.notify_device_read_print_completed(self._current_connection.device_info, beginIndex, endIndex, currentIndex, cartridgeId)

    def _handle_session_even(self, data_dict: dict) -> None:
        ...

    def _handle_session_ready(self, data_dict: dict) -> None:
        """处理连接成功响应
        
        Args:
            data_dict: 响应数据字典
        """
        RBQLog.log(f" <-- 连接成功响应: {data_dict}")
        # int pack = jsonObject.getInt("pack");

    def _handle_session_fail(self, data_dict: dict) -> None:
        """处理连接成功响应
        
        Args:
            data_dict: 响应数据字典
        """
        RBQLog.log(f" <-- 连接成功响应: {data_dict}")
    
    def _handle_silent_state_response(self, data_dict: dict) -> None:
        """处理静音状态响应
        
        Args:
            data_dict: 响应数据字典
        """
        silent_state: bool = data_dict.get('msg', False)
        RBQLog.i("读取到静音状态:" + str(silent_state))
        self.notify_device_read_silent_state(self._current_connection.device_info, silent_state)
    
    def _handle_auto_power_off_response(self, data_dict: dict) -> None:
        """处理自动关机状态响应
        
        Args:
            data_dict: 响应数据字典
        """
        auto_power_off_state: bool = data_dict.get('msg', False)
        RBQLog.log("读取到自动关机状态:" + str(auto_power_off_state))
        self.notify_device_read_auto_power_off_state(self._current_connection.device_info, auto_power_off_state)


    def _handle_write_print_start_command(self, data_dict: dict) -> None:
        """处理打印开始命令响应
        
        Args:
            data_dict: 响应数据字典
        """
        #这个只需要对比了指令，无需解析json
        RBQLog.log(f" <-- 读取到发送打印指令反馈: {data_dict}")
        self.notify_device_read_write_print_start_command( self._current_connection.device_info if self._current_connection else None, data_dict)

    def _handle_general_command(self, data_dict: dict) -> None:
        """处理一般指令响应
        
        Args:
            data_dict: 响应数据字典
        """
        code = data_dict.get('code', 0)
        if code == 0:
            RBQLog.log(f" <-- 一般指令响应: {data_dict}")
        else:
            RBQLog.log(f" <-- 一般指令响应失败: {data_dict}")

    
    def _dispatch_data_event(self, data: bytes) -> None:
        """分发二进制数据事件
        
        处理二进制数据包，包括多行数据、Logo数据和OTA数据。
        
        Args:
            data: 二进制数据
        """
        try:
            
            # RBQLog.log(f" <-- [_dispatch_data_event]分发数据事件: {data}")

            if self._multi_row_data_packet.start:
                self._dispatch_multi_row_data_event(data)
            elif self._logo_data_packet.start:
                self._dispatch_logo_data_event(data)
            elif self._ota_data_packet.start:
                self._dispatch_ota_data_event(data)
            else:
                # 触发普通数据回调
                RBQLog.log_error("没有正在进行的打印任务")
                
        except Exception as e:
            RBQLog.log_error(f"分发数据任务失败: {str(e)}")

    
    def _dispatch_multi_row_data_event(self, data: bytes) -> None:
        """处理多行数据事件响应
        
        Args:
            data: 接收到的响应数据
        """
        try:
            # 对数据解码打印，打印16进制字符串
            hex_data: str = ' '.join([f'{byte:02X}' for byte in data])
            RBQLog.log(f" <-- [_dispatch_multi_row_data_event]分发多行数据事件hex_data: {hex_data}")

            if not self._multi_row_data_packet.has_data():
                RBQLog.log_debug("[打印请求]没有多行数据")
                return
            if self._multi_row_data_packet.is_request_data(data):
                # RBQLog.log_debug("[打印请求]收到请求数据")
                self._clear_wait_data_transfer_response_timer()
                if self._multi_row_data_packet.has_next_packet_with_current_row():
                    self._n_index = self._n_index + 1
                    RBQLog.log_debug(f"[打印请求]请求数据，当前行: {self._n_index}")
                    self.send_next_multi_row_data_packet()
            elif self._multi_row_data_packet.is_nak(data):
                # RBQLog.log_debug("[打印请求]收到ACK")
                RBQLog.log_debug(f"[打印请求]收到ACK，当前行: {self._n_index}")
                self.send_nak_multi_row_data_packet()
            elif self._multi_row_data_packet.is_eot(data):
                RBQLog.log_debug("[打印请求]收到EOT")
                #判断是否还有下一行数据，如果有下一行数据则延时发送下一行打印指令
                if self._multi_row_data_packet.has_next_row():
                    #延时发送打印指令
                    self._clear_data_transfer_delay_command_timer()
                    self._create_with_fire_data_transfer_delay_command_timer(0.3, self.delay_begin_send_next_multi_row_data_packet)

                else:
                    self._clear_data_transfer_delay_command_timer()
                    self._create_with_fire_data_transfer_delay_command_timer(0.3, self.delay_send_print_command_with_notify_data_progress_success)

            
        except Exception as e:
            RBQLog.log_error(f"处理多行数据事件失败: {str(e)}")
            # 异常情况下清理状态
            self._cancel_all_packet_start()
            self._clear_wait_data_transfer_response_timer()
            self._clear_data_transfer_delay_command_timer()
            self.notify_device_data_transfer_error(1, str(e))

    def delay_begin_send_next_multi_row_data_packet(self) -> None:
        """延时发送下一行数据"""
        self._multi_row_data_packet.cursor_move_to_next()
        current_row: int = self._multi_row_data_packet.current_row & 0xFF

        arr_index_data_size: int = self._multi_row_data_packet.current_row_data_length
        data_size_0: int = arr_index_data_size & 0xFF
        data_size_1: int = (arr_index_data_size >> 8) & 0xFF
        data_size_2: int = (arr_index_data_size >> 16) & 0xFF
        data_size_3: int = (arr_index_data_size >> 24) & 0xFF
        compress: int = self._multi_row_data_packet.compress & 0xFF

        params: bytearray = bytearray([current_row, data_size_0, data_size_1, data_size_2, data_size_3, compress])
        self._inner_send_command(OpCode.TRANSMIT_PICTURE_DATA,params)

    def delay_send_print_command_with_notify_data_progress_success(self) -> None:
        """延时发送打印指令"""
        index:int = self._multi_row_data_packet.total_row_count & 0xFF
        params:bytearray = bytearray([0,index])
        self._inner_send_command(OpCode.PRINT_PICTURE,params)

        self._multi_row_data_packet.current_time = time.time()
        size: float = self._multi_row_data_packet.total_data_len / 1000.0
        self._cancel_all_packet_start()

        self.notify_device_data_transfer_success(self._current_connection.device_info, size, self._multi_row_data_packet.start_time, self._multi_row_data_packet.current_time)

    def _dispatch_logo_data_event(self, data: bytes) -> None:
        """处理Logo数据事件响应
        
        Args:
            data: 接收到的响应数据
        """
        try:

            # 对数据解码打印，打印16进制字符串
            hex_data: str = ' '.join([f'{byte:02X}' for byte in data])
            RBQLog.log(f" <-- [_dispatch_logo_data_event]分发多行数据事件hex_data: {hex_data}")

            if not self._logo_data_packet.has_data():
                RBQLog.log_debug("没有Logo数据")
                return
            if self._logo_data_packet.is_request_data(data):
                self._clear_wait_data_transfer_response_timer()
                if self._logo_data_packet.has_next_packet():
                    self._n_index = self._n_index + 1
                    self.send_next_logo_packet()
            elif self._logo_data_packet.is_nak(data):
                RBQLog.log_debug("收到ACK")
                self.send_nak_logo_packet()
            elif self._logo_data_packet.is_eot(data):
                RBQLog.log_debug("收到EOT")
                
                self._logo_data_packet.current_time = time.time()
                size: float = self._logo_data_packet.total_data_len / 1000.0
                self._cancel_all_packet_start()

                self.notify_device_data_transfer_success(self._current_connection.device_info, size, self._logo_data_packet.start_time, self._logo_data_packet.current_time)

        except Exception as e:
            RBQLog.log_error(f"处理Logo数据事件失败: {str(e)}")
            # 异常情况下清理状态
            self._cancel_all_packet_start()
            self._clear_wait_data_transfer_response_timer()
            self.notify_device_data_transfer_error(1, str(e))
    
    def _dispatch_ota_data_event(self, data: bytes) -> None:
        """处理OTA数据事件响应
        
        Args:
            data: 接收到的响应数据
        """
        try:

            # 对数据解码打印，打印16进制字符串
            hex_data: str = ' '.join([f'{byte:02X}' for byte in data])
            RBQLog.log(f" <-- [_dispatch_ota_data_event]分发多行数据事件hex_data: {hex_data}")

            if not self._ota_data_packet.has_data():
                RBQLog.log_debug("没有OTA数据")
                return
            if self._ota_data_packet.is_request_data(data):
                self._clear_wait_data_transfer_response_timer()
                if self._ota_data_packet.has_next_packet():
                    self._n_index = self._n_index + 1
                    self.send_next_ota_packet()
            elif self._ota_data_packet.is_nak(data):
                RBQLog.log_info(f"收到NAK，重传第 {self._n_index} 个OTA数据请求")
                self.send_nak_logo_packet()
            elif self._ota_data_packet.is_eot(data):
                RBQLog.log_info("收到OTA数据传输结束标志")
                self._ota_data_packet.current_time = time.time()
                size: float = self._ota_data_packet.total_data_len / 1000.0
                self._cancel_all_packet_start()
                self.notify_device_data_transfer_success(self._current_connection.device_info, size, self._ota_data_packet.start_time, self._ota_data_packet.current_time)
            
        except Exception as e:
            RBQLog.log_error(f"处理OTA数据事件失败: {str(e)}")
            self._cancel_all_packet_start()
            self._clear_wait_data_transfer_response_timer()
            self.notify_device_data_transfer_error(1, str(e))