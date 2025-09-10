#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edenx打印机SDK演示程序

作者: RBQ
版本: 1.0.0
Python版本: 3.9+
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                            QComboBox, QFileDialog, QMessageBox, QGroupBox,
                            QSplitter, QFrame)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtCore import QDateTime

# 添加SDK路径到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sdk_path = os.path.join(current_dir, 'sdk', 'python')
if sdk_path not in sys.path:
    sys.path.insert(0, sdk_path)

# 导入SDK模块
try:
    from mxSdk.connection import ConnectManager
    from mxSdk.models.device_info import DeviceInfo
    from mxSdk.enums.conn_type import ConnType
    from mxSdk.enums.connection_status import ConnectionStatus
    from mxSdk.factories.multi_row_data_factory import MultiRowDataFactory
    from mxSdk.factories.logo_data_factory import LogoDataFactory
    from mxSdk.data.row_image import RowImage
    from mxSdk.data.multi_row_image import MultiRowImage
    from mxSdk.data.row_data import RowData
    from mxSdk.data.multi_row_data import MultiRowData
    from mxSdk.data.logo_image import LogoImage
    from mxSdk.data.logo_data import LogoData
    from mxSdk.enums.row_layout_direction import RowLayoutDirection
    from mxSdk.utils.rbq_log import RBQLog
    from mxSdk.connection.manager import DeviceDiscoveryProtocol
    from mxSdk.connection.manager import DeviceConnectionProtocol
    from mxSdk.connection.manager import DeviceDataTransferProtocol
    from mxSdk.connection.manager import DeviceReadProtocol
    from mxSdk.transport.protocol import SOH, STX, STX_A, STX_B, STX_C, STX_D, STX_E
    SDK_AVAILABLE = True
except ImportError as e:
    print(f"无法导入SDK模块: {e}")
    SDK_AVAILABLE = False


class PrinterDemoWindow(QMainWindow):
    """打印机SDK演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edenx打印机SDK演示")
        self.resize(1000, 700)
        
        # 初始化变量
        self.serial_device_infos = []
        self.usb_device_infos = []
        self.current_image_path = None
        self.current_multi_row_data = None
        self.current_logo_data = None
        self.current_ota_data = None
        
        # 初始化连接管理器
        self.connect_manager = ConnectManager.share()
        
        # 创建事件处理器
        self._init_event_handlers()
        
        # 初始化UI
        self._init_ui()
        
        # 刷新设备列表
        self.refresh_serial_ports()
        self.refresh_usb_devices()
        
    def _init_event_handlers(self):
        """初始化事件处理器"""
        # 设备发现处理器
        self.discovery_handler = self.DeviceDiscoveryHandler(self)
        self.connect_manager.register_device_discovery_handler(self.discovery_handler)
        
        # 设备连接处理器
        self.connection_handler = self.DeviceConnectionHandler(self)
        self.connect_manager.register_device_connection_handler(self.connection_handler)
        
        # 设备读取处理器
        self.read_handler = self.DeviceReadHandler(self)
        self.connect_manager.register_device_read_handler(self.read_handler)
        
        # 数据传输处理器
        self.data_transfer_handler = self.DeviceDataTransferHandler(self)
        self.connect_manager.register_device_data_transfer_handler(self.data_transfer_handler)
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧区域：图像处理
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 图像预览区域
        image_group = QGroupBox("图像预览与处理")
        image_layout = QVBoxLayout(image_group)
        
        # 图像显示区域
        image_splitter = QSplitter(Qt.Horizontal)
        
        # 原图显示
        original_group = QGroupBox("原图")
        original_layout = QVBoxLayout(original_group)
        self.original_image_label = QLabel()
        self.original_image_label.setFixedSize(250, 250)
        self.original_image_label.setAlignment(Qt.AlignCenter)
        self.original_image_label.setFrameShape(QFrame.Box)
        self.original_image_label.setText("尚未选择图像")
        original_layout.addWidget(self.original_image_label)
        
        # 处理后图像显示
        processed_group = QGroupBox("处理后")
        processed_layout = QVBoxLayout(processed_group)
        self.processed_image_label = QLabel()
        self.processed_image_label.setFixedSize(250, 250)
        self.processed_image_label.setAlignment(Qt.AlignCenter)
        self.processed_image_label.setFrameShape(QFrame.Box)
        self.processed_image_label.setText("尚未处理图像")
        processed_layout.addWidget(self.processed_image_label)
        
        # 添加到分割器
        image_splitter.addWidget(original_group)
        image_splitter.addWidget(processed_group)
        
        # 图像处理按钮
        image_buttons_layout = QHBoxLayout()
        self.select_button = QPushButton("选择图片")
        self.process_button = QPushButton("处理图片")
        self.clear_button = QPushButton("清除图片")
        
        self.select_button.clicked.connect(self.select_image)
        self.process_button.clicked.connect(self.process_image)
        self.clear_button.clicked.connect(self.clear_image)
        
        image_buttons_layout.addWidget(self.select_button)
        image_buttons_layout.addWidget(self.process_button)
        image_buttons_layout.addWidget(self.clear_button)
        
        image_layout.addWidget(image_splitter)
        image_layout.addLayout(image_buttons_layout)
        left_layout.addWidget(image_group)
        
        # 右侧区域：设备管理和数据传输
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 设备管理区域
        device_group = QGroupBox("设备管理")
        device_layout = QVBoxLayout(device_group)
        
        # 设备分割器
        device_splitter = QSplitter(Qt.Vertical)
        
        # USB设备管理
        usb_group = QGroupBox("USB设备")
        usb_layout = QVBoxLayout(usb_group)
        
        usb_selection_layout = QHBoxLayout()
        usb_selection_layout.addWidget(QLabel("USB设备:"))
        self.usb_combo = QComboBox()
        usb_selection_layout.addWidget(self.usb_combo)
        
        usb_buttons_layout = QHBoxLayout()
        self.refresh_usb_button = QPushButton("刷新")
        self.connect_usb_button = QPushButton("连接")
        self.refresh_usb_button.clicked.connect(self.refresh_usb_devices)
        self.connect_usb_button.clicked.connect(self.connect_or_disconnect_usb)
        usb_buttons_layout.addWidget(self.refresh_usb_button)
        usb_buttons_layout.addWidget(self.connect_usb_button)
        
        usb_layout.addLayout(usb_selection_layout)
        usb_layout.addLayout(usb_buttons_layout)
        
        # 串口设备管理
        serial_group = QGroupBox("串口设备")
        serial_layout = QVBoxLayout(serial_group)
        
        serial_selection_layout = QHBoxLayout()
        serial_selection_layout.addWidget(QLabel("串口:"))
        self.port_combo = QComboBox()
        serial_selection_layout.addWidget(self.port_combo)
        
        serial_buttons_layout = QHBoxLayout()
        self.refresh_serial_button = QPushButton("刷新")
        self.connect_serial_button = QPushButton("连接")
        self.refresh_serial_button.clicked.connect(self.refresh_serial_ports)
        self.connect_serial_button.clicked.connect(self.connect_or_disconnect_serial)
        serial_buttons_layout.addWidget(self.refresh_serial_button)
        serial_buttons_layout.addWidget(self.connect_serial_button)
        
        serial_layout.addLayout(serial_selection_layout)
        serial_layout.addLayout(serial_buttons_layout)
        
        # 添加到设备分割器
        device_splitter.addWidget(usb_group)
        device_splitter.addWidget(serial_group)
        
        # 日志显示区域
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMinimumHeight(150)
        
        # 数据传输区域
        transfer_group = QGroupBox("数据传输")
        transfer_layout = QVBoxLayout(transfer_group)
        
        # 传输协议选择
        protocol_layout = QHBoxLayout()
        protocol_layout.addWidget(QLabel("传输协议:"))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["SOH", "STX", "STX_A", "STX_B", "STX_C", "STX_D", "STX_E"])
        protocol_layout.addWidget(self.protocol_combo)
        protocol_layout.addStretch()
        transfer_layout.addLayout(protocol_layout)
        
        # 传输按钮
        transfer_buttons_layout = QHBoxLayout()
        self.transfer_image_button = QPushButton("传输图像")
        self.transfer_logo_button = QPushButton("传输Logo")
        self.transfer_ota_button = QPushButton("传输OTA")
        self.stop_transfer_button = QPushButton("停止传输")
        
        self.transfer_image_button.clicked.connect(lambda: self.transfer_data(0))
        self.transfer_logo_button.clicked.connect(lambda: self.transfer_data(1))
        self.transfer_ota_button.clicked.connect(lambda: self.transfer_data(2))
        self.stop_transfer_button.clicked.connect(self.stop_transfer)
        
        transfer_buttons_layout.addWidget(self.transfer_image_button)
        transfer_buttons_layout.addWidget(self.transfer_logo_button)
        transfer_buttons_layout.addWidget(self.transfer_ota_button)
        transfer_buttons_layout.addWidget(self.stop_transfer_button)
        
        transfer_layout.addLayout(transfer_buttons_layout)
        
        # 添加到右侧布局
        device_layout.addWidget(device_splitter)
        device_layout.addWidget(self.log_display)
        right_layout.addWidget(device_group)
        right_layout.addWidget(transfer_group)
        
        # 添加到主分割器
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([500, 500])
        
        # 设置中央窗口部件
        self.setCentralWidget(main_splitter)
        
        # 设置状态栏
        self.statusBar().showMessage("就绪")
    
    def refresh_usb_devices(self):
        """刷新USB设备列表"""
        self.log_display.append("[系统] 刷新USB设备列表")
        self.usb_device_infos.clear()
        self.usb_combo.clear()
        self.connect_manager.discover_devices([ConnType.USB])
    
    def refresh_serial_ports(self):
        """刷新串口列表"""
        self.log_display.append("[系统] 刷新串口列表")
        self.serial_device_infos.clear()
        self.port_combo.clear()
        self.connect_manager.discover_devices([ConnType.SERIAL])
    
    def connect_or_disconnect_usb(self):
        """连接或断开USB设备"""
        if self.connect_manager.is_connected():
            self.disconnect_device()
        else:
            self.connect_usb_device()
    
    def connect_or_disconnect_serial(self):
        """连接或断开串口设备"""
        if self.connect_manager.is_connected():
            self.disconnect_device()
        else:
            self.connect_serial_device()
    
    def connect_usb_device(self):
        """连接USB设备"""
        if self.connect_manager.is_connected():
            self.log_display.append("[错误] 请先断开当前连接")
            return
        
        current_index = self.usb_combo.currentIndex()
        if current_index < 0 or current_index >= len(self.usb_device_infos):
            self.log_display.append("[错误] 请先选择有效的USB设备")
            return
        
        try:
            device_info = self.usb_device_infos[current_index]
            self.connect_manager.connect(device_info)
        except Exception as e:
            self.log_display.append(f"[错误] 连接USB设备失败: {str(e)}")
    
    def connect_serial_device(self):
        """连接串口设备"""
        if self.connect_manager.is_connected():
            self.log_display.append("[错误] 请先断开当前连接")
            return
        
        current_index = self.port_combo.currentIndex()
        if current_index < 0 or current_index >= len(self.serial_device_infos):
            self.log_display.append("[错误] 请先选择有效的串口设备")
            return
        
        try:
            device_info = self.serial_device_infos[current_index]
            # 设置默认串口参数
            device_info.baudrate = 115200
            device_info.data_bits = 8
            device_info.stop_bits = 1
            device_info.parity = 'N'
            self.connect_manager.connect(device_info)
        except Exception as e:
            self.log_display.append(f"[错误] 连接串口设备失败: {str(e)}")
    
    def disconnect_device(self):
        """断开设备连接"""
        if self.connect_manager.is_connected():
            self.connect_manager.disconnect()
        else:
            self.log_display.append("[错误] 没有连接的设备")
    
    def select_image(self):
        """选择图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.current_image_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.original_image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.original_image_label.setPixmap(scaled_pixmap)
                
                # 清除处理后的图像显示
                self.processed_image_label.clear()
                self.processed_image_label.setText("尚未处理图像")
                
                self.statusBar().showMessage("图片已加载")
            else:
                self.statusBar().showMessage("图片加载失败")
    
    def process_image(self):
        """处理图片"""
        if not self.current_image_path:
            self.statusBar().showMessage("请先选择图片")
            return
        
        self.statusBar().showMessage("正在处理图像...")
        
        # 创建RowImage对象
        row_image = RowImage(
            image_path=self.current_image_path,
            top_beyond_distance=0,
            bottom_beyond_distance=0
        )
        
        # 创建MultiRowImage对象
        multi_row_image = MultiRowImage(
            row_images=[row_image],
            thumb_path=None,
            row_layout_direction=RowLayoutDirection.VERTICAL,
            is_contiguous_cropped_images=False
        )
        
        # 定义回调函数
        def on_start():
            self.statusBar().showMessage("开始处理图像...")
        
        def on_complete(multi_row_data):
            try:
                if multi_row_data and multi_row_data.image_paths:
                    # 保存处理后的MultiRowData对象供传输使用
                    self.current_multi_row_data = multi_row_data
                    # 显示处理后的第一张图像
                    processed_image_path = multi_row_data.image_paths[0]
                    self.display_processed_image_from_path(processed_image_path)
                    self.statusBar().showMessage("图像处理完成")
                else:
                    self.current_multi_row_data = None
                    self.statusBar().showMessage("图像处理失败：无处理结果")
            except Exception as e:
                self.current_multi_row_data = None
                self.statusBar().showMessage(f"显示处理结果错误: {str(e)}")
        
        def on_error():
            self.statusBar().showMessage("图像处理失败")
        
        # 使用异步处理图像
        MultiRowDataFactory.better_merge_bitmap_to_multi_row_data_async(
            multi_row_image=multi_row_image,
            threshold=128,
            clear_background=False,
            dithering=True,
            compress=True,
            flip_horizontally=False,
            is_simulation=True,
            thumb_to_simulation=False,
            on_start=on_start,
            on_complete=on_complete,
            on_error=on_error
        )
    
    def display_processed_image_from_path(self, image_path):
        """从路径显示处理后的图像"""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.processed_image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.processed_image_label.setPixmap(scaled_pixmap)
    
    def clear_image(self):
        """清除图像"""
        self.original_image_label.clear()
        self.original_image_label.setText("尚未选择图像")
        self.processed_image_label.clear()
        self.processed_image_label.setText("尚未处理图像")
        self.current_image_path = None
        self.current_multi_row_data = None
        self.current_logo_data = None
        self.statusBar().showMessage("已清除图像")
    
    def transfer_data(self, data_type):
        """传输数据"""
        if not self.connect_manager.is_connected():
            self.log_display.append("[错误] 请先连接设备")
            return
        
        # 获取选择的传输协议
        protocol_index = self.protocol_combo.currentIndex()
        protocol_constants = [SOH, STX, STX_A, STX_B, STX_C, STX_D, STX_E]
        selected_protocol = protocol_constants[protocol_index]
        
        try:
            if data_type == 0:  # 传输图像数据
                if not self.current_multi_row_data:
                    self.log_display.append("[错误] 请先处理图像")
                    return
                self.connect_manager.set_with_send_multi_row_data_packet(
                    multi_row_data=self.current_multi_row_data,
                    fn=selected_protocol
                )
            elif data_type == 1:  # 传输Logo数据
                if not self.current_logo_data:
                    # 如果没有Logo数据，尝试从当前图像创建
                    if not self.current_image_path:
                        self.log_display.append("[错误] 请先选择图像")
                        return
                    
                    logo_image = LogoImage(image_path=self.current_image_path)
                    
                    def on_logo_complete(logo_data):
                        self.current_logo_data = logo_data
                        self.connect_manager.set_with_send_logo_packet(
                            logo_data=self.current_logo_data,
                            fn=selected_protocol
                        )
                    
                    LogoDataFactory.logo_image_to_data_async(
                        logo_image=logo_image,
                        threshold=128,
                        on_start=lambda: self.statusBar().showMessage("开始处理Logo..."),
                        on_complete=on_logo_complete,
                        on_error=lambda: self.statusBar().showMessage("Logo处理失败")
                    )
                else:
                    self.connect_manager.set_with_send_logo_packet(
                        logo_data=self.current_logo_data,
                        fn=selected_protocol
                    )
            elif data_type == 2:  # 传输OTA数据
                if not self.current_ota_data:
                    # 选择OTA文件
                    file_path, _ = QFileDialog.getOpenFileName(
                        self, "选择OTA文件", "", "OTA Files (*.rbl)"
                    )
                    if file_path:
                        with open(file_path, 'rb') as file:
                            self.current_ota_data = file.read()
                    else:
                        return
                
                self.connect_manager.set_with_send_ota_data_packet(
                    data=self.current_ota_data,
                    fn=selected_protocol
                )
        except Exception as e:
            self.log_display.append(f"[错误] 传输数据失败: {str(e)}")
    
    def stop_transfer(self):
        """停止传输"""
        try:
            self.connect_manager.cancel_send_multi_row_data_packet()
            self.connect_manager.cancel_send_logo_packet()
            self.connect_manager.cancel_send_ota_data_packet()
            self.log_display.append("[系统] 已停止传输")
        except Exception as e:
            self.log_display.append(f"[错误] 停止传输失败: {str(e)}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            self.connect_manager.disconnect()
            # 注销事件处理器
            self.connect_manager.unregister_device_discovery_handler(self.discovery_handler)
            self.connect_manager.unregister_device_connection_handler(self.connection_handler)
            self.connect_manager.unregister_device_read_handler(self.read_handler)
            self.connect_manager.unregister_device_data_transfer_handler(self.data_transfer_handler)
        except Exception as e:
            print(f"关闭连接错误: {e}")
        event.accept()
    
    # 设备发现事件处理器
    class DeviceDiscoveryHandler(DeviceDiscoveryProtocol):
        def __init__(self, main_window):
            self.main_window = main_window
        
        def on_device_discover_start(self) -> None:
            self.main_window.log_display.append("[系统] 设备发现开始")
        
        def on_device_discover(self, device: DeviceInfo) -> None:
            if device.conn_type == ConnType.SERIAL:
                self.main_window.serial_device_infos.append(device)
                self.main_window.port_combo.addItem(f"{device.serial_port_path}")
            elif device.conn_type == ConnType.USB:
                self.main_window.usb_device_infos.append(device)
                self.main_window.usb_combo.addItem(f"{device.usb_path}")
        
        def on_device_discover_stop(self) -> None:
            self.main_window.log_display.append("[系统] 设备发现完成")
    
    # 设备连接事件处理器
    class DeviceConnectionHandler(DeviceConnectionProtocol):
        def __init__(self, main_window):
            self.main_window = main_window
        
        def on_device_connect_start(self, device: DeviceInfo) -> None:
            self.main_window.log_display.append(f"[系统] 设备开始连接: {device.name}")
            self.main_window.statusBar().showMessage("正在连接设备...")
        
        def on_device_connect_succeed(self, device: DeviceInfo) -> None:
            self.main_window.log_display.append(f"[系统] 设备连接成功: {device.name}")
            self.main_window.statusBar().showMessage("设备连接成功")
            # 更新按钮状态
            if device.conn_type == ConnType.USB:
                self.main_window.connect_usb_button.setText("断开")
            elif device.conn_type == ConnType.SERIAL:
                self.main_window.connect_serial_button.setText("断开")
        
        def on_device_disconnect(self, device: DeviceInfo) -> None:
            self.main_window.log_display.append(f"[系统] 设备断开连接: {device.name}")
            self.main_window.statusBar().showMessage("设备断开连接")
            # 更新按钮状态
            self.main_window.connect_usb_button.setText("连接")
            self.main_window.connect_serial_button.setText("连接")
        
        def on_device_connect_fail(self, device: DeviceInfo) -> None:
            self.main_window.log_display.append(f"[系统] 设备连接失败: {device.name}")
            self.main_window.statusBar().showMessage("设备连接失败")
    
    # 设备读取事件处理器
    class DeviceReadHandler(DeviceReadProtocol):
        def __init__(self, main_window):
            self.main_window = main_window
        
        def on_device_read_data(self, device: DeviceInfo, data: bytes) -> None:
            try:
                text = data.decode('utf-8')
                self.main_window.log_display.append(f"[接收] {text}")
            except:
                self.main_window.log_display.append(f"[接收] {data.hex()}")
    
    # 数据传输事件处理器
    class DeviceDataTransferHandler(DeviceDataTransferProtocol):
        def __init__(self, main_window):
            self.main_window = main_window
        
        def on_device_data_transfer_start(self, device: DeviceInfo, size: float, startTime: int, currentTime: int) -> None:
            self.main_window.log_display.append("[系统] 数据传输开始")
            self.main_window.statusBar().showMessage("正在传输数据...")
        
        def on_device_data_transfer_progress(self, device: DeviceInfo, size: float, progress: int, startTime: int, currentTime: int) -> None:
            self.main_window.log_display.append(f"[系统] 传输进度: {progress}%, 已传输: {size}字节")
            self.main_window.statusBar().showMessage(f"正在传输数据... {progress}%")
        
        def on_device_data_transfer_success(self, device: DeviceInfo, size: float, startTime: int, currentTime: int) -> None:
            self.main_window.log_display.append("[系统] 数据传输成功")
            self.main_window.statusBar().showMessage("数据传输成功")
        
        def on_device_data_transfer_error(self, error_code: int, error_message: str) -> None:
            self.main_window.log_display.append(f"[错误] 数据传输失败: {error_message}")
            self.main_window.statusBar().showMessage("数据传输失败")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = PrinterDemoWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()