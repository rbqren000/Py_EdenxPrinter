# -*- coding: utf-8 -*-
"""
USB连接策略

实现USB设备的发现、连接和数据传输功能。
使用pyusb库与USB设备通信。

作者: RBQ
版本: 1.0.0
创建时间: 2025
Python版本: 3.9+
"""

import time
import uuid
import threading
from typing import Dict, List, Optional, Tuple, Any
import usb.core
import usb.util
from .strategy import ConnectionStrategy
from .parameters import UsbConnectionParameters
from ..enums import ConnType
from ..enums.connection_status import ConnectionStatus
from ..models.device_info import DeviceInfo
from ..utils.rbq_log import RBQLog
from ..models.command_context import CommandContext
from ..models.data_obj_context import DataObjContext


class UsbConnectionStrategy(ConnectionStrategy):
    """USB连接策略类

    实现USB设备的发现、连接和数据传输功能。
    使用pyusb库与USB设备通信。

    Attributes:
        _usb_device: USB设备对象
        _connection_params: 连接参数
        _interface: USB接口
        _endpoint_in: 输入端点
        _endpoint_out: 输出端点
        _read_thread: 数据读取线程
        _stop_reading: 停止读取标志
        _cancel_discovery: 取消发现标志
        _discover_devices_thread: 发现设备线程
    """

    def __init__(self):
        """初始化USB连接策略"""
        super().__init__()
        self._usb_device = None
        self._connection_params: Optional[UsbConnectionParameters] = None
        self._interface = None
        self._endpoint_in = None
        self._endpoint_out = None
        self._read_thread: Optional[threading.Thread] = None
        self._stop_reading: bool = False
        self._cancel_discovery: bool = False
        self._discover_devices_thread: Optional[threading.Thread] = None
        self._disconnecting: bool = False  # 断开连接操作状态标志

    @property
    def connection_type(self) -> ConnType:
        """获取连接类型

        Returns:
            ConnType: USB连接类型
        """
        return ConnType.USB

    def discover_devices(self, timeout: float = 5.0) -> None:
        """发现USB设备

        搜索系统中所有可用的USB设备，并通过回调函数返回设备信息列表。
        使用独立线程执行，支持超时和取消操作。

        Args:
            timeout: 发现超时时间（秒），USB发现通常不需要等待
        """
        # 如果已经在发现中，先取消之前的发现
        if self.is_discovering:
            self.cancel_discover_devices()
            
        # 重置取消标志
        self._cancel_discovery = False
        
        # 在新线程中执行设备发现
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
            while not self._cancel_discovery:
                # 检查超时
                if time.time() - start_time >= timeout:
                    RBQLog.log(f"USB设备发现超时 ({timeout}秒)")
                    break
                    
                # 获取所有USB设备
                usb_devices = usb.core.find(find_all=True)
                
                # 遍历设备并创建设备信息
                for usb_device in usb_devices:
                    if self._cancel_discovery:
                        break
                        
                    try:
                        # 尝试获取设备信息
                        vendor_id = usb_device.idVendor
                        product_id = usb_device.idProduct
                        device_class = getattr(usb_device, 'bDeviceClass', None)
                        device_subclass = getattr(usb_device, 'bDeviceSubclass', None)
                        device_protocol = getattr(usb_device, 'bDeviceProtocol', None)
                        
                        # 尝试获取设备名称
                        try:
                            manufacturer = usb.util.get_string(usb_device, usb_device.iManufacturer)
                        except:
                            manufacturer = "Unknown"
                            
                        try:
                            product = usb.util.get_string(usb_device, usb_device.iProduct)
                        except:
                            product = f"USB Device {vendor_id:04x}:{product_id:04x}"
                        
                        # 创建设备名称
                        name = f"{manufacturer} {product}".strip()
                        if not name or name == "Unknown":
                            name = f"USB Device {vendor_id:04x}:{product_id:04x}"
                        
                        device_id = DeviceInfo._generate_device_id(ConnType.USB, vendor_id=vendor_id, product_id=product_id, usb_serial_number=usb_device.serial_number)
                        device_exists = any(d.device_id == device_id for d in devices)
                        if not device_exists:
                            # 创建设备信息
                            device_info = DeviceInfo(
                                name=name,
                                device_id=device_id,
                                conn_type=ConnType.USB,
                                usb_path=f"usb://{vendor_id:04x}:{product_id:04x}",
                                vendor_id=vendor_id,
                                product_id=product_id,
                                usb_serial_number=usb_device.serial_number,
                                device_class=device_class,
                                device_subclass=device_subclass,
                                device_protocol=device_protocol,
                            )
                            
                            devices.append(device_info)
                            
                            # 发现单个设备时立即回调
                            self._trigger_discover_found(device_info)
                            
                    except Exception as e:
                        RBQLog.log(f"获取USB设备信息时出错: {str(e)}")
                        continue
                
            if not self._cancel_discovery:
                RBQLog.log(f"发现 {len(devices)} 个USB设备")
                
                # 循环打印出 usb 设备
                for device in devices:
                    RBQLog.log(f"发现USB设备: {device.name} ({device.usb_path})")
            else:
                RBQLog.log("USB设备发现已取消")
                
        except Exception as e:
            RBQLog.log(f"USB设备发现失败: {str(e)}")
            
        finally:
            # 触发发现停止回调
            self._trigger_discover_stop()
            
    def cancel_discover_devices(self) -> None:
        """取消设备发现
        
        停止正在进行的设备发现操作。
        """
        if self.is_discovering:
            RBQLog.log("正在取消USB设备发现...")
            self._cancel_discovery = True
            
            # 等待发现线程结束
            if self._discover_devices_thread and self._discover_devices_thread.is_alive():
                self._discover_devices_thread.join(timeout=2.0)
                
            RBQLog.log("USB设备发现已取消")

    def connect(self, device_info: DeviceInfo) -> None:
        """连接到USB设备

        Args:
            device_info: 设备信息对象，包含USB连接所需的所有参数：
                - vendor_id: 厂商ID（必需）
                - product_id: 产品ID（必需）
                - interface_number: 接口号（可选，默认为0）
                - endpoint_in: 输入端点（可选，自动查找）
                - endpoint_out: 输出端点（可选，自动查找）
                - usb_read_timeout: 读取超时时间（毫秒，默认1000）
                - usb_write_timeout: 写入超时时间（毫秒，默认1000）

        Note:
            连接结果通过事件通知，不通过返回值
        """
        # 重置断开标志，确保可以正常执行断开操作
        self._disconnecting = False
    
        if self.is_connected():
            RBQLog.log("已经连接到USB设备，请先断开连接")
            return
        
        # 更新状态
        self._update_connect_status(ConnectionStatus.CONNECTING)
        
        try:
            # 从 device_info 对象获取连接参数
            vendor_id = device_info.vendor_id
            product_id = device_info.product_id
            interface_number = device_info.interface_number if device_info.interface_number is not None else 0
            endpoint_in = device_info.endpoint_in
            endpoint_out = device_info.endpoint_out
            read_timeout = device_info.usb_read_timeout or 1000
            write_timeout = device_info.usb_write_timeout or 1000

            # 验证必需参数
            if vendor_id is None or product_id is None:
                # 连接失败
                error_msg = "vendor_id 和 product_id 是必需的参数"
                RBQLog.log(error_msg)
                self._update_connect_status(ConnectionStatus.CONNECT_FAIL)
                return

            # 记录连接参数
            RBQLog.log(f"USB连接参数: vendor_id=0x{vendor_id:04X}, product_id=0x{product_id:04X}, "
                      f"interface={interface_number}, read_timeout={read_timeout}, "
                      f"write_timeout={write_timeout}")

            # 创建连接参数对象
            params = UsbConnectionParameters(
                vendor_id=vendor_id,
                product_id=product_id,
                interface_number=interface_number,
                endpoint_in=endpoint_in,
                endpoint_out=endpoint_out,
                read_timeout=read_timeout,
                write_timeout=write_timeout
            )
            
            # 查找设备
            self._usb_device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
            if self._usb_device is None:
                error_msg = f"未找到USB设备: {vendor_id:04x}:{product_id:04x}"
                RBQLog.log(error_msg)
                self._update_connect_status(ConnectionStatus.CONNECT_FAIL)
                return
            
            # 设置配置
            try:
                self._usb_device.set_configuration()
            except Exception as e:
                RBQLog.log(f"设置USB配置失败: {str(e)}")
                self._cleanup_failed_connection()
                return
            
            # 获取接口
            if interface_number is None:
                # 使用第一个接口
                cfg = self._usb_device.get_active_configuration()
                interface_number = cfg[(0, 0)].bInterfaceNumber
                
            # 如果接口被内核驱动程序占用，则分离它
            driver_detached = True
            try:
                if self._usb_device.is_kernel_driver_active(interface_number):
                    self._usb_device.detach_kernel_driver(interface_number)
            except Exception as e:
                RBQLog.log(f"分离内核驱动程序失败: {str(e)}")
                driver_detached = False
                # 继续尝试，因为在某些系统上可能不需要分离
                
            # 获取接口
            if not driver_detached:
                RBQLog.log("警告: 内核驱动未成功分离，但尝试继续获取接口")
            
            cfg = self._usb_device.get_active_configuration()
            self._interface = cfg[(0, interface_number)]
            
            # 获取端点
            endpoint_in = params.endpoint_in
            endpoint_out = params.endpoint_out
            
            if endpoint_in is None or endpoint_out is None:
                # 自动查找端点
                for ep in self._interface:
                    ep_addr = ep.bEndpointAddress
                    ep_attributes = ep.bmAttributes
                    # 查找批量传输端点
                    if usb.util.endpoint_direction(ep_addr) == usb.util.ENDPOINT_IN and \
                       (ep_attributes & 0x03) == usb.util.ENDPOINT_TYPE_BULK:
                        endpoint_in = ep_addr
                    elif usb.util.endpoint_direction(ep_addr) == usb.util.ENDPOINT_OUT and \
                         (ep_attributes & 0x03) == usb.util.ENDPOINT_TYPE_BULK:
                        endpoint_out = ep_addr
                        
            # 验证端点类型
            if endpoint_in is not None and endpoint_out is not None:
                # 确认端点类型为批量传输
                cfg = self._usb_device.get_active_configuration()
                ep_in = usb.util.find_descriptor(
                    self._interface,
                    bEndpointAddress=endpoint_in
                )
                ep_out = usb.util.find_descriptor(
                    self._interface,
                    bEndpointAddress=endpoint_out
                )
                
                if ep_in is None or ep_out is None or \
                   (ep_in.bmAttributes & 0x03) != usb.util.ENDPOINT_TYPE_BULK or \
                   (ep_out.bmAttributes & 0x03) != usb.util.ENDPOINT_TYPE_BULK:
                    endpoint_in = None
                    endpoint_out = None
                        
            if endpoint_in is None or endpoint_out is None:
                error_msg = "未找到USB端点"
                RBQLog.log(error_msg)
                self._cleanup_failed_connection()
                return
            
            self._endpoint_in = endpoint_in
            self._endpoint_out = endpoint_out
            
            # 保存连接参数和设备信息
            self._connection_params = params
            self._device = device_info
            
            # 更新状态
            self._update_connect_status(ConnectionStatus.CONNECTED)
            
            # 启动数据读取线程
            self._start_read_thread()
            
            RBQLog.log(f"成功连接到USB设备: {device_info.name}")
            
        except Exception as e:
            RBQLog.log(f"USB设备连接失败: {str(e)}")
            self._cleanup_failed_connection()

    def disconnect(self) -> None:
            """断开USB连接
        
            Note:
                断开结果通过状态变化事件通知，不返回值
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
                self._update_connect_status(ConnectionStatus.DISCONNECTING)
            
                # 清理USB资源
                self._cleanup_usb_resources()
            
                self._update_connect_status(ConnectionStatus.DISCONNECTED)
                RBQLog.log("USB设备已断开连接")
            
            except Exception as e:
                RBQLog.log(f"断开USB连接失败: {str(e)}")
                # 即使出现异常也要清理资源
                self._cleanup_usb_resources()
                self._update_connect_status(ConnectionStatus.DISCONNECTED)
            finally:
                # 重置断开标志
                self._disconnecting = False

    def _cleanup_failed_connection(self) -> None:
        """清理失败连接的资源"""
        try:
            self._cleanup_usb_resources()
        except Exception as e:
            RBQLog.log(f"清理失败连接资源时出错: {e}")
        finally:
            self._update_connect_status(ConnectionStatus.CONNECT_FAIL)

    def _cleanup_usb_resources(self) -> None:
        """清理USB连接资源"""
        try:
            self._stop_read_thread()
        except Exception as e:
            RBQLog.log(f"停止读取线程失败: {e}")
        
        try:
            if self._usb_device and self._interface:
                usb.util.release_interface(self._usb_device, self._interface)
        except Exception as e:
            RBQLog.log(f"释放USB接口失败: {e}")
        
        try:
            if self._usb_device:
                self._usb_device.reset()
        except Exception as e:
            RBQLog.log(f"重置USB设备失败: {e}")
        
        # 清理实例变量
        self._usb_device = None
        self._interface = None
        self._endpoint_in = None
        self._endpoint_out = None
        self._connection_params = None
        self._device = None

    def is_connected(self) -> bool:
        """检查是否已连接到USB设备

        Returns:
            bool: 已连接返回True，未连接返回False
        """
        return (self._conn_status == ConnectionStatus.CONNECTED and 
                self._usb_device is not None and 
                self._endpoint_in is not None and 
                self._endpoint_out is not None)

    def write_data(self, tag: int, data: bytes) -> None:
        """发送数据到USB设备

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
            chunk_size = 1024*10   # 每次最多发送10k
            index = 0
            
            while bytes_sent < total_bytes:
                # 计算当前块的大小
                current_chunk_size = min(chunk_size, total_bytes - bytes_sent)
                chunk = data[bytes_sent:bytes_sent + current_chunk_size]
                
                # 发送当前块
                chunk_bytes_written = self._usb_device.write(
                    self._endpoint_out, 
                    chunk, 
                    timeout=self._connection_params.write_timeout if self._connection_params else 1000
                )
                bytes_sent += chunk_bytes_written
                
                # 更新进度
                progress = int((bytes_sent / total_bytes) * 100)
                self._trigger_data_write_progress(index, self._tag, chunk, bytes_sent, total_bytes, progress)
                
                # 如果写入的字节数不等于块大小，说明出现了问题
                if chunk_bytes_written != current_chunk_size:
                    RBQLog.log(f"USB写入不完整: 期望 {current_chunk_size} 字节，实际写入 {chunk_bytes_written} 字节")
                    # 写入失败回调
                    self._trigger_data_write_failure(index, self._tag, data, -2, "写入不完整")
                    return
            
            # 写入成功回调
            self._trigger_data_write_success(index, self._tag, data, total_bytes)
            
        except Exception as e:
            RBQLog.log(f"USB发送数据失败: {str(e)}")
            # 写入失败回调
            self._trigger_data_write_failure(0, self._tag, data, -3, str(e))

    def write_CommandContext(self, command_context: CommandContext) -> None:
        #保存command_context
        self._command_context = command_context
        if not self.is_connected():
            self._trigger_command_error(command_context, "设备未连接")
            return
        try:
            # 发送数据
            self._usb_device.write(
                self._endpoint_out, 
                command_context.command.data, 
                timeout=self._connection_params.write_timeout if self._connection_params else 1000
            )
            # 发送成功回调
            self._trigger_command_success(command_context)
        except Exception as e:
            RBQLog.log(f"USB发送数据失败: {str(e)}")
            # 发送失败回调
            self._trigger_command_error(command_context, str(e))

    def write_DataObjContext(self, data_obj_context: DataObjContext) -> None:
        #保存data_obj_context
        self._data_obj_context = data_obj_context
        if not self.is_connected():
            self._trigger_obj_error(data_obj_context, "设备未连接")
            return
        try:
            # 发送数据
            self._usb_device.write(
                self._endpoint_out, 
                data_obj_context.data_obj.data, 
                timeout=self._connection_params.write_timeout if self._connection_params else 1000
            )
            # 发送成功回调
            self._trigger_obj_success(data_obj_context)
        except Exception as e:
            RBQLog.log(f"USB发送数据失败: {str(e)}")
            # 发送失败回调
            self._trigger_obj_error(data_obj_context, str(e))

    def _start_read_thread(self) -> None:
        """启动数据读取线程"""
        if self._read_thread is None or not self._read_thread.is_alive():
            self._stop_reading = False
            self._read_thread = threading.Thread(target=self._read_data_loop, daemon=True)
            self._read_thread.start()
            RBQLog.log("USB数据读取线程已启动")
    
    def _stop_read_thread(self) -> None:
        """停止数据读取线程"""
        if self._read_thread and self._read_thread.is_alive():
            self._stop_reading = True
            self._read_thread.join(timeout=2.0)
            RBQLog.log("USB数据读取线程已停止")
    
    def _read_data_loop(self) -> None:
        """数据读取循环（在独立线程中运行）"""
        while not self._stop_reading and self.is_connected():
            try:
                # 尝试读取数据
                timeout_ms = self._connection_params.read_timeout if self._connection_params else 100
                data = self._usb_device.read(self._endpoint_in, 1024, timeout=timeout_ms)
                
                if data:
                    # 调用数据接收回调
                    self._trigger_data_read(bytes(data))
                    
            except usb.core.USBError as e:
                if e.errno == 110:  # 超时错误
                    # 超时是正常的，继续循环
                    continue
                else:
                    RBQLog.log(f"USB数据读取错误: {str(e)}")
                    # 发生错误时短暂休眠后继续
                    time.sleep(0.1)
            except Exception as e:
                RBQLog.log(f"USB数据读取错误: {str(e)}")
                # 发生错误时短暂休眠后继续
                time.sleep(0.1)