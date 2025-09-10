# -*- coding: utf-8 -*-
"""
串口连接策略

实现串口设备的发现、连接和数据传输功能。
使用pyserial库与串口设备通信。

作者: RBQ
版本: 1.0.0
创建时间: 2025
Python版本: 3.9+
"""

import time
import threading
import serial
import serial.tools.list_ports
from typing import List, Optional, Tuple
from .strategy import ConnectionStrategy
from .parameters import SerialConnectionParameters
from ..enums import ConnType
from ..enums.connection_status import ConnectionStatus
from ..models.device_info import DeviceInfo
from ..utils.rbq_log import RBQLog
from ..models.command_context import CommandContext
from ..models.data_obj_context import DataObjContext


class SerialConnectionStrategy(ConnectionStrategy):
    """串口连接策略类

    实现串口设备的发现、连接和数据传输功能。
    使用pyserial库与串口设备通信。

    Attributes:
        _serial: 串口对象
        _connection_params: 连接参数
        _read_thread: 数据读取线程
        _stop_reading: 停止读取标志
    """

    def __init__(self):
        """初始化串口连接策略"""
        super().__init__()
        self._serial: Optional[serial.Serial] = None
        self._connection_params: Optional[SerialConnectionParameters] = None
        self._read_thread: Optional[threading.Thread] = None
        self._stop_reading: bool = False
        self._cancel_discovery: bool = False  # 取消设备发现标志
        self._discover_devices_thread: Optional[threading.Thread] = None  # 设备发现线程
        self._disconnecting: bool = False  # 断开连接操作状态标志

    @property
    def connection_type(self) -> ConnType:
        """获取连接类型

        Returns:
            ConnType: 串口连接类型
        """
        return ConnType.SERIAL

    def discover_devices(self, timeout: float = 5.0) -> None:
        """发现串口设备

        搜索系统中所有可用的串口设备，并通过回调函数返回设备信息列表。
        对于串口设备，发现过程是即时的，但为了支持取消操作和统一接口，
        我们使用线程来执行发现过程。

        Args:
            timeout: 发现超时时间（秒），串口发现通常很快完成
        """
        # 如果已经在发现中，先取消之前的发现
        if self.is_discovering:
            self.cancel_discover_devices()
            
        # 重置取消标志
        self._cancel_discovery = False
        
        # 使用线程执行发现过程，支持超时和取消
        self._discover_devices_thread = threading.Thread(
            target=self._discover_devices_worker, 
            args=(timeout,), 
            daemon=True
        )
        self._discover_devices_thread.start()
        
    def _discover_devices_worker(self, timeout: float) -> None:
        """设备发现工作线程
        
        Args:
            timeout: 发现超时时间（秒）
        """
        # 触发发现开始回调
        self._trigger_discover_start()
        
        start_time = time.time()
        devices: List[DeviceInfo] = []
        
        try:
            # 获取所有串口
            ports = serial.tools.list_ports.comports()
            
            # 遍历串口并创建设备信息
            for port in ports:
                # 检查是否被取消
                if self._cancel_discovery:
                    RBQLog.log("设备发现已被取消")
                    break
                    
                # 检查超时
                if time.time() - start_time > timeout:
                    RBQLog.log(f"设备发现超时 ({timeout}秒)")
                    break
                    
                try:
                    # 判断是否为 USB 转串口设备
                    is_usb_serial = port.vid is not None and port.pid is not None

                    # 创建设备名称
                    name = port.description if port.description else f"Serial Port {port.device}"
                    
                    # 创建设备信息
                    device_info = DeviceInfo(
                        name=name,
                        conn_type=ConnType.SERIAL,
                        serial_port_path=port.device,
                        serial_number=port.serial_number,
                        # usb 转 串口 设备  识别 序列号
                        is_usb_serial=is_usb_serial,
                        usb_manufacturer=port.manufacturer,
                        usb_product=port.product,
                        vendor_id=port.vid if is_usb_serial else None,
                        product_id=port.pid if is_usb_serial else None,
                    )
                    
                    devices.append(device_info)
                    
                    # 发现单个设备时立即回调
                    self._trigger_discover_found(device_info)
                    
                    # 添加小延迟以支持取消操作
                    time.sleep(0.01)
                        
                except Exception as e:
                    RBQLog.log(f"获取串口设备信息时出错: {str(e)}")
                    continue
                    
            if not self._cancel_discovery:
                RBQLog.log(f"发现 {len(devices)} 个串口设备")
                # 循环打印出串口
                for device in devices:
                    RBQLog.log(f"发现串口设备: {device.name} ({device.serial_port_path})")
                
        except Exception as e:
            RBQLog.log(f"串口设备发现失败: {str(e)}")
            
        finally:
            # 触发发现停止回调
            self._trigger_discover_stop()

    def cancel_discover_devices(self) -> None:
        """取消设备发现
        
        停止当前正在进行的设备发现操作。
        对于串口设备发现，由于过程通常很快，取消操作主要用于中断长时间的扫描。
        """
        if self.is_discovering:
            RBQLog.log("正在取消串口设备发现...")
            self._cancel_discovery = True
            
            # 等待发现线程结束
            if self._discover_devices_thread and self._discover_devices_thread.is_alive():
                self._discover_devices_thread.join(timeout=2.0)
                
            RBQLog.log("串口设备发现已取消")
        else:
            RBQLog.log("当前没有正在进行的设备发现操作")

    def connect(self, device_info: DeviceInfo) -> None:
        """连接到串口设备

        Args:
            device_info: 设备信息，包含串口连接所需的所有参数
            
        Note:
            连接参数直接从 device_info 对象获取，包括：
            - port: 从 device_info.path 或 device_info.address 获取
            - baudrate: 波特率，默认115200
            - data_bits: 数据位，默认8
            - stop_bits: 停止位，默认1.0
            - parity: 校验位，默认'N'
            - 流控和超时参数使用设备默认值
        """
        # 重置断开标志，确保可以正常执行断开操作
        self._disconnecting = False
        
        try:
            # 打印device_info对象的属性
            RBQLog.log(f"[SerialConnectionStrategy]connect()传入的device_info对象的属性: {device_info.__dict__}")

            if self.is_connected():
                RBQLog.log("已经连接到串口设备，请先断开连接")
                return

            self._update_connect_status(ConnectionStatus.CONNECTING)
            
            # 初始化临时变量
            temp_serial = None

            # 获取串口名称
            port = device_info.serial_port_path

            if port is None:
                RBQLog.log("设备信息中未指定串口路径或地址")
                self._update_connect_status(ConnectionStatus.CONNECT_FAIL)
                return
                
            RBQLog.log(f"正在连接串口设备: {device_info.name}; prot:{port}")
            
            # 从设备信息中获取连接参数，使用默认值作为后备
            baudrate = device_info.baudrate or 115200
            bytesize = device_info.data_bits or 8
            parity = device_info.parity or 'N'
            stopbits = device_info.stop_bits or 1.0
            timeout = device_info.read_timeout or 1.0
            write_timeout = device_info.write_timeout or 1.0
            xonxoff = device_info.xonxoff or False
            rtscts = device_info.rtscts or False
            dsrdtr = device_info.dsrdtr or False

            # 创建串口连接
            temp_serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity = parity,
                stopbits=stopbits,
                timeout=timeout,
                write_timeout=write_timeout,
                xonxoff=xonxoff,
                rtscts=rtscts,
                dsrdtr=dsrdtr
            )

            # Serial 构造函数参数说明
            # Serial(
            #     port: str | None = None,            # 串口名称，例如 'COM1' 或 '/dev/ttyUSB0'
            #     baudrate: int = 9600,               # 波特率，常见值如 9600、115200
            #     bytesize: int = 8,                  # 数据位，通常为 5～8
            #     parity: str = "N",                  # 校验位：'N'=无校验, 'E'=偶校验, 'O'=奇校验
            #     stopbits: float = 1,                # 停止位：1、1.5 或 2
            #     timeout: float | None = None,       # 读超时时间，单位秒，None 表示阻塞直到读取
            #     xonxoff: bool = False,              # 软件流控制（XON/XOFF）
            #     rtscts: bool = False,               # 硬件流控制（RTS/CTS）
            #     write_timeout: float | None = None, # 写入超时时间，单位秒
            #     dsrdtr: bool = False,               # DSR/DTR 控制
            #     inter_byte_timeout: float | None = None, # 字节间隔超时
            #     exclusive: bool | None = None       # 是否独占串口资源，部分系统支持防冲突
            # )

            
            # 验证连接是否成功
            if not temp_serial.is_open:
                RBQLog.log(f"无法打开串口: {port}")
                self._update_connect_status(ConnectionStatus.CONNECT_FAIL)
                return
            
            # 连接成功，保存连接对象和设备信息
            self._serial = temp_serial
            self._device = device_info
            
            # 创建连接参数对象用于记录
            self._connection_params = SerialConnectionParameters(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                read_timeout=timeout,
                write_timeout=write_timeout,
                xonxoff=xonxoff,
                rtscts=rtscts,
                dsrdtr=dsrdtr
            )
            
            self._update_connect_status(ConnectionStatus.CONNECTED)

            # 打印串口连接成功
            RBQLog.log(f"[SerialConnectionStrategy]connect()串口连接成功")
            
            # 启动数据读取线程
            self._start_read_thread()
            
            RBQLog.log(f"成功连接到串口设备 连接参数: port={port}, 波特率={baudrate}, 数据位={bytesize}, 校验位={parity}, 停止位={stopbits}, 读取超时={timeout}, 写入超时={write_timeout}, 软件流控={xonxoff}, 硬件流控={rtscts}, DSR/DTR={dsrdtr}")
            
        except (serial.SerialException, OSError) as e:
            # 串口相关异常
            error_msg = f"串口连接失败: {str(e)}"
            RBQLog.log(error_msg)
            self._cleanup_failed_connection(temp_serial)
            self._update_connect_status(ConnectionStatus.CONNECT_FAIL)
            
        except ValueError as e:
            # 参数验证错误
            error_msg = f"设备信息错误: {str(e)}"
            RBQLog.log(error_msg)
            self._cleanup_failed_connection(temp_serial)
            self._update_connect_status(ConnectionStatus.CONNECT_FAIL)
            
        except Exception as e:
            # 其他未预期的异常
            error_msg = f"串口设备连接失败: {str(e)}"
            RBQLog.log(error_msg)
            self._cleanup_failed_connection(temp_serial)
            self._update_connect_status(ConnectionStatus.CONNECT_FAIL)

    def _cleanup_failed_connection(self, temp_serial: Optional[serial.Serial]) -> None:
        """清理失败连接的资源
        
        Args:
            temp_serial: 临时串口对象
        """
        try:
            # 清理临时串口对象
            if temp_serial and temp_serial.is_open:
                temp_serial.close()
        except Exception as cleanup_error:
            RBQLog.log(f"清理串口资源时出错: {str(cleanup_error)}")
        
        # 清理实例变量
        self._serial = None
        self._connection_params = None
        self._device = None

    def _cleanup_resources(self) -> None:
        """清理连接相关的所有资源
        
        该方法会安全地停止读取线程、关闭串口连接并清理实例变量。
        即使在清理过程中出现异常，也会确保所有资源都被正确释放。
        """
        # 停止读取线程
        try:
            self._stop_read_thread()
        except Exception as e:
            RBQLog.log(f"停止读取线程时出错: {str(e)}")
        
        # 关闭串口连接
        try:
            if self._serial and self._serial.is_open:
                self._serial.close()
        except (serial.SerialException, OSError) as e:
            RBQLog.log(f"关闭串口时出错: {str(e)}")
        except Exception as e:
            RBQLog.log(f"关闭串口时发生未知错误: {str(e)}")
        
        # 清理实例变量
        self._serial = None
        self._connection_params = None
        self._device = None

    def disconnect(self) -> None:
        """断开串口连接
        
        该方法会安全地关闭串口连接，停止数据读取线程，并清理所有相关资源。
        如果设备未连接，方法会直接返回而不执行任何操作。
        
        注意:
            - 断开操作是幂等的，多次调用不会产生副作用
            - 即使在断开过程中出现异常，也会确保资源被正确清理
            - 断开完成后会更新连接状态为 DISCONNECTED
        """
        # 检查是否已经在断开过程中，避免重复执行
        if self._disconnecting:
            RBQLog.log("断开操作已在进行中，避免重复执行")
            return
            
        if not self.is_connected():
            RBQLog.log("设备未连接，无需断开")
            return
        
        # 设置断开标志    
        self._disconnecting = True
        
        try:
            RBQLog.log(f"开始断开串口设备: {self._device.name if self._device else '未知设备'}")
            self._update_connect_status(ConnectionStatus.DISCONNECTING)
            
            # 执行断开操作
            self._cleanup_resources()
            self._update_connect_status(ConnectionStatus.DISCONNECTED)
            RBQLog.log("串口设备已成功断开连接")
            
        except Exception as e:
            RBQLog.log(f"断开串口连接时发生错误: {str(e)}")
            # 确保资源被清理和状态被更新
            self._cleanup_resources()
            self._update_connect_status(ConnectionStatus.DISCONNECTED)
        finally:
            # 重置断开标志
            self._disconnecting = False

    def is_connected(self) -> bool:
        """检查是否已连接到串口设备

        Returns:
            bool: 已连接返回True，未连接返回False
        """
        return (self._conn_status == ConnectionStatus.CONNECTED and 
                self._serial is not None and 
                self._serial.is_open)

    def write_data(self, tag: int, data: bytes) -> None:
        """发送数据到串口设备

        Args:
            tag: 数据块标志位，用于区分业务上下文
            data: 要发送的数据
        """
        #保存tag
        self._tag = tag

        if not self.is_connected():
            # 写入失败回调
            self._trigger_data_write_failure(0, self._tag, data, -1, "设备未连接")
            return
            
        try:
            # 如果数据较大，分块发送并报告进度
            total_bytes = len(data)
            bytes_sent = 0
            chunk_size = 1024*10  # 每次最多发送10k
            index = 0
            
            while bytes_sent < total_bytes:
                # 计算当前块的大小
                current_chunk_size = min(chunk_size, total_bytes - bytes_sent)
                chunk = data[bytes_sent:bytes_sent + current_chunk_size]
                
                # 发送当前块
                chunk_bytes_written = self._serial.write(chunk)
                bytes_sent += chunk_bytes_written
                
                # 确保数据被发送出去
                self._serial.flush()
                
                # 更新进度
                progress = int((bytes_sent / total_bytes) * 100)
                self._trigger_data_write_progress(index, self._tag, chunk, bytes_sent, total_bytes, progress)
                
                # 如果写入的字节数不等于块大小，说明出现了问题
                if chunk_bytes_written != current_chunk_size:
                    RBQLog.log(f"串口写入不完整: 期望 {current_chunk_size} 字节，实际写入 {chunk_bytes_written} 字节")
                    # 写入失败回调
                    self._trigger_data_write_failure(index, self._tag, data, -2, "写入不完整")
                    return
                
                # 在大数据块之间添加短暂延迟，确保设备有时间处理
                if total_bytes > chunk_size and bytes_sent < total_bytes:
                    time.sleep(0.01)  # 10ms延迟
                
                # 递增索引，确保每个块有唯一标识
                index += 1
            
            # 最后再次确保所有数据都被发送
            self._serial.flush()
            
            # 写入成功回调
            self._trigger_data_write_success(0, self._tag, data, total_bytes)
            
        except serial.SerialTimeoutException as e:
            RBQLog.log(f"串口发送数据超时: {str(e)}")
            # 写入失败回调
            self._trigger_data_write_failure(index, self._tag, data, -4, f"写入超时: {str(e)}")
            
        except Exception as e:
            RBQLog.log(f"串口发送数据失败: {str(e)}")
            # 写入失败回调
            self._trigger_data_write_failure(index, self._tag, data, -3, str(e))


    #不触发策略中定义的回调事件，暂不考虑分包
    def write_CommandContext(self, command_context: CommandContext) -> None:
        """发送CommandContext

        Args:
            command_context: 要发送的CommandContext对象
        """
        #保存command_context
        self._command_context = command_context
        if not self.is_connected():
            RBQLog.log("设备未连接，无法发送CommandContext")
            self._trigger_command_error(command_context, "设备未连接")
            return
        try:
            # 获取要发送的数据
            data: bytes = command_context.command.data
            # 发送数据
            bytes_written: int = self._serial.write(data)
            # 打印写入数据长度
            # RBQLog.log(f"写入CommandContext数据长度: {bytes_written} 字节")
            # 确保数据被发送出去
            self._serial.flush()
            
            # 验证写入的字节数
            if bytes_written != len(data):
                error_msg = f"命令数据写入不完整: 期望 {len(data)} 字节，实际写入 {bytes_written} 字节"
                RBQLog.log(error_msg)
                self._trigger_command_error(command_context, error_msg)
                return
                
            # 发送成功回调
            self._trigger_command_success(command_context)
            
        except serial.SerialTimeoutException as e:
            error_msg = f"发送CommandContext数据超时: {str(e)}"
            RBQLog.log(error_msg)
            self._trigger_command_error(command_context, error_msg)
        except Exception as e:
            RBQLog.log(f"发送CommandContext数据失败: {str(e)}")
            self._trigger_command_error(command_context, str(e))

    #不触发策略中定义的回调事件，暂不考虑分包
    def write_DataObjContext(self, data_obj_context: DataObjContext) -> None:
        """发送DataObjContext

        Args:
            data_obj_context: 要发送的DataObjContext对象
        """
        #保存data_obj_context
        self._data_obj_context = data_obj_context
        if not self.is_connected():
            RBQLog.log("设备未连接，无法发送DataObjContext")
            self._trigger_obj_error(data_obj_context, "设备未连接")
            return
        try:
            # 获取要发送的数据
            data: bytes = data_obj_context.data_obj.data
            # 发送数据
            bytes_written: int = self._serial.write(data)
            # 打印写入数据长度
            # RBQLog.log(f"写入DataObjContext数据长度: {bytes_written} 字节")
            # 确保数据被发送出去
            self._serial.flush()
            
            # 验证写入的字节数
            if bytes_written != len(data):
                error_msg = f"数据对象写入不完整: 期望 {len(data)} 字节，实际写入 {bytes_written} 字节"
                RBQLog.log(error_msg)
                self._trigger_obj_error(data_obj_context, error_msg)
                return
                
            # 发送成功回调
            self._trigger_obj_success(data_obj_context)
            
        except serial.SerialTimeoutException as e:
            error_msg = f"发送DataObjContext数据超时: {str(e)}"
            RBQLog.log(error_msg)
            self._trigger_obj_error(data_obj_context, error_msg)
        except Exception as e:
            RBQLog.log(f"发送DataObjContext数据失败: {str(e)}")
            self._trigger_obj_error(data_obj_context, str(e))
    
    def _start_read_thread(self) -> None:
        """启动数据读取线程"""
        if self._read_thread is None or not self._read_thread.is_alive():
            self._stop_reading = False
            self._read_thread = threading.Thread(target=self._read_data_loop, daemon=True)
            self._read_thread.start()
            RBQLog.log("串口数据读取线程已启动")
    
    def _stop_read_thread(self) -> None:
        """停止数据读取线程"""
        if self._read_thread and self._read_thread.is_alive():
            self._stop_reading = True
            self._read_thread.join(timeout=2.0)
            RBQLog.log("串口数据读取线程已停止")
    
    # def _read_data_loop(self) -> None:
    #     """数据读取循环（在独立线程中运行）"""
    #     while not self._stop_reading and self.is_connected():
    #         try:
    #             if self._serial and self._serial.in_waiting > 0:
    #                 # 读取可用数据
    #                 data = self._serial.read(self._serial.in_waiting)
    #                 if data:
    #                     # 调用数据接收回调
    #                     self._trigger_data_read(data)

    #             else:
    #                 # 短暂休眠避免CPU占用过高
    #                 time.sleep(0.01)
    #         except Exception as e:
    #             RBQLog.log(f"串口数据读取错误: {str(e)}")
    #             # 发生错误时短暂休眠后继续
    #             time.sleep(0.1)

    def _read_data_loop(self) -> None:
        """数据读取循环（在独立线程中运行）
        
        改进后的实现：
        1. 使用阻塞读取提高效率
        2. 增加读取缓冲区大小控制
        3. 精细化异常处理
        4. 增加连接状态监控
        """
        read_buffer_size = 1024  # 每次读取的缓冲区大小
        consecutive_errors = 0   # 连续错误计数
        max_consecutive_errors = 5  # 最大连续错误次数
        
        RBQLog.log("串口数据读取循环开始")
        
        while not self._stop_reading and self.is_connected():
            try:
                # 使用阻塞读取，timeout 在串口初始化时设置
                # 这样可以避免频繁的 CPU 轮询
                data = self._serial.read(read_buffer_size)
                
                if data:
                    # 重置错误计数
                    consecutive_errors = 0
                    
                    # 调用数据接收回调
                    self._trigger_data_read(data)
                    
                    # 如果读取到满缓冲区的数据，可能还有更多数据
                    # 立即检查是否有更多数据可读
                    while self._serial.in_waiting > 0 and not self._stop_reading:
                        additional_data = self._serial.read(min(self._serial.in_waiting, read_buffer_size))
                        if additional_data:
                            self._trigger_data_read(additional_data)
                        else:
                            break
                
                # 如果没有数据且是非阻塞模式，短暂休眠
                # elif self._serial.timeout == 0:
                #     time.sleep(0.01)
                    
            except serial.SerialTimeoutException:
                # 读取超时是正常的，继续循环
                consecutive_errors = 0
                continue
                
            except (serial.SerialException, OSError) as e:
                # 串口相关错误，可能是连接断开
                consecutive_errors += 1
                RBQLog.log(f"串口读取错误 ({consecutive_errors}/{max_consecutive_errors}): {str(e)}")
                
                if consecutive_errors >= max_consecutive_errors:
                    RBQLog.log("串口连续错误过多，可能连接已断开")
                    # 更新连接状态
                    self._update_connect_status(ConnectionStatus.DISCONNECTED)
                    break
                
                # 短暂休眠后重试
                # time.sleep(0.1)
                
            except Exception as e:
                # 其他未预期的异常
                consecutive_errors += 1
                RBQLog.log(f"串口读取发生未知错误 ({consecutive_errors}/{max_consecutive_errors}): {str(e)}")
                
                if consecutive_errors >= max_consecutive_errors:
                    RBQLog.log("串口读取异常过多，停止读取")
                    self._update_connect_status(ConnectionStatus.DISCONNECTED)
                    break
                    
                time.sleep(0.1)
        
        RBQLog.log("串口数据读取循环结束")


    # 另一种更高效的实现方式（使用事件驱动）
    def _read_data_loop_event_driven(self) -> None:
        """基于事件驱动的数据读取循环
        
        这种实现方式使用较小的读取超时和更智能的数据聚合。
        """
        read_timeout = 0.1  # 100ms 超时
        max_read_size = 4096  # 最大单次读取大小
        data_buffer = bytearray()  # 数据缓冲区
        last_data_time = time.time()
        buffer_timeout = 0.05  # 50ms 缓冲区超时
        
        # 临时设置较短的超时用于事件驱动
        original_timeout = self._serial.timeout
        self._serial.timeout = read_timeout
        
        try:
            while not self._stop_reading and self.is_connected():
                try:
                    # 尝试读取数据
                    chunk = self._serial.read(max_read_size)
                    current_time = time.time()
                    
                    if chunk:
                        # 有数据到达
                        data_buffer.extend(chunk)
                        last_data_time = current_time
                        
                        # 如果缓冲区已满或者是单次完整读取，立即处理
                        if len(data_buffer) >= max_read_size or len(chunk) < max_read_size:
                            if data_buffer:
                                self._trigger_data_read(bytes(data_buffer))
                                data_buffer.clear()
                    
                    elif data_buffer and (current_time - last_data_time) >= buffer_timeout:
                        # 缓冲区有数据且超时，处理缓冲区数据
                        self._trigger_data_read(bytes(data_buffer))
                        data_buffer.clear()
                    
                except serial.SerialTimeoutException:
                    # 超时是正常的，检查缓冲区
                    if data_buffer and (time.time() - last_data_time) >= buffer_timeout:
                        self._trigger_data_read(bytes(data_buffer))
                        data_buffer.clear()
                    continue
                    
                except Exception as e:
                    RBQLog.log(f"串口事件驱动读取错误: {str(e)}")
                    # 处理缓冲区中的剩余数据
                    if data_buffer:
                        self._trigger_data_read(bytes(data_buffer))
                        data_buffer.clear()
                    break
                    
        finally:
            # 恢复原始超时设置
            if self._serial and self._serial.is_open:
                self._serial.timeout = original_timeout
            
            # 处理缓冲区中的剩余数据
            if data_buffer:
                self._trigger_data_read(bytes(data_buffer))


    # 推荐的最终实现
    def _read_data_loop_recommended(self) -> None:
        """推荐的串口数据读取循环实现
        
        结合了效率和稳定性，适合大多数使用场景。
        """
        read_buffer_size = 1024
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        while not self._stop_reading and self.is_connected():
            try:
                # 使用串口配置的超时进行阻塞读取
                data = self._serial.read(read_buffer_size)
                
                if data:
                    consecutive_errors = 0
                    self._trigger_data_read(data)
                    
                    # 继续读取缓冲区中的剩余数据
                    while (self._serial.in_waiting > 0 and 
                        not self._stop_reading and 
                        self.is_connected()):
                        additional_data = self._serial.read(
                            min(self._serial.in_waiting, read_buffer_size)
                        )
                        if additional_data:
                            self._trigger_data_read(additional_data)
                        else:
                            break
                
            except serial.SerialTimeoutException:
                # 读取超时是正常的，继续循环
                consecutive_errors = 0
                
            except (serial.SerialException, OSError) as e:
                consecutive_errors += 1
                RBQLog.log(f"串口读取错误: {str(e)}")
                
                if consecutive_errors >= max_consecutive_errors:
                    RBQLog.log("串口连接可能已断开")
                    self._update_connect_status(ConnectionStatus.DISCONNECTED)
                    break
                
                time.sleep(0.1)
                
            except Exception as e:
                RBQLog.log(f"串口读取发生未知错误: {str(e)}")
                break
        
        RBQLog.log("串口数据读取循环结束")