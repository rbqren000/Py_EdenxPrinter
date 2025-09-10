import sys
import os
import asyncio
import io
import threading
from PyQt5.QtWidgets import (
    QMainWindow, QApplication,
    QStackedWidget, QLabel, QVBoxLayout, QHBoxLayout, QWidget,
    QFileDialog, QTextEdit, QListWidget, QFrame, QSplitter,
    QGroupBox, QStatusBar, QHeaderView, QTableWidget,
    QTableWidgetItem, QComboBox, QMessageBox, QDialog, QLineEdit
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QDateTime, QMetaType, pyqtSlot
# 尝试导入QVector类型
try:
    from PyQt5.QtCore import QVector
except ImportError:
    # 如果导入失败，创建一个空的QVector类
    class QVector:
        pass
from pages.custom_widgets import CustomButton
from sdk.python.mxSdk.transport.protocol import SOH,STX,STX_A,STX_B,STX_C,STX_D,STX_E
from style.styles import *
from helper.image_processor import ImageProcessor
from pages.settings_page import SettingsPage
from dialogs.exit_confirm_dialog import ExitConfirmDialog
from menus.main_menu import MainMenuBar

# SDK导入
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'sdk', 'python'))
# ConnectionFactory现在由ConnectManager内部管理，不需要直接导入
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 注册QVector<int>类型以避免警告
        try:
            # 使用PyQt5的方式注册QVector<int>类型
            # 这种方法通过将警告级别设置为忽略来解决问题
            import warnings
            warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*QVector<int>.*")
            
            # 尝试使用QMetaType注册
            try:
                QMetaType.type("QVector<int>")
            except:
                pass
        except Exception as e:
            print(f"处理QVector<int>警告时出错: {e}")
            pass
        
        self._closing = False  # 添加退出状态标记
        self.setWindowTitle("Edenx打印上位机 - 图像处理与设备通讯系统")
        self.resize(1200, 800)

        # 初始化属性及事件
        self.init_attributes_and_handlers()

        # 设置菜单栏
        self.setMenuBar(MainMenuBar(self))

        # 设置样式
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        # 初始化状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("系统就绪")

        # 连接信号
        self._connect_signals()

        # 初始化UI
        self.initUI()

        # 打印 usb设置的 vid pid
        target_vid = SettingsPage.get_setting('usb/vendor_id', '', str).strip()
        target_pid = SettingsPage.get_setting('usb/product_id', '', str).strip()
        RBQLog.log(f"usb设置的 vid pid: {target_vid} {target_pid}")

    def _connect_signals(self):
        """连接所有信号"""
        # 图像处理器信号 - 使用Qt.DirectConnection避免QVector<int>警告
        self.image_processor.processing_error.connect(self.status_bar.showMessage, Qt.DirectConnection)
        self.image_processor.processing_success.connect(self._on_image_info_ready, Qt.DirectConnection)

    # 初始化属性及事件
    def init_attributes_and_handlers(self):
        
        #保存串口设备DeviceInfo列表
        self.serial_device_infos: list[DeviceInfo] = []
        #保存USB设备DeviceInfo列表
        self.usb_device_infos: list[DeviceInfo] = []

        self.current_image_path: str = None
        # 连接管理现在由ConnectManager统一处理
        self.image_processor: ImageProcessor = ImageProcessor()

        self.current_multi_row_data: MultiRowData = None  # 存储处理后的MultiRowData对象
        self.current_logo_data: LogoData = None  # 存储处理后的LogoData对象
        self.current_ota_data: bytes = None  # 存储处理后的OtaData对象
        
        # 初始化连接管理器
        self.connect_manager = ConnectManager.share()
        
        # 创建设备发现处理器并注册
        self.discovery_handler = self.DeviceDiscoveryHandler(self)
        self.connect_manager.register_device_discovery_handler(self.discovery_handler)

        # 创建设备连接事件处理器并注册
        self.connection_handler = self.DeviceConnectionHandler(self)
        self.connect_manager.register_device_connection_handler(self.connection_handler)

        # 创建设备读取事件处理器并注册
        self.read_handler = self.DeviceReadHandler(self)
        self.connect_manager.register_device_read_handler(self.read_handler)

        # 创建设备数据传输处理器并注册
        self.data_transfer_handler = self.DeviceDataTransferHandler(self)
        self.connect_manager.register_device_data_transfer_handler(self.data_transfer_handler)

    def initUI(self):
        """初始化用户界面"""
        # 创建主分割器
        main_splitter = QSplitter(Qt.Horizontal)

        # ===== 左侧区域：ota 和 图片处理部分 =====
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # ota 区域
        ota_group = QGroupBox("设备ota")
        ota_layout = QVBoxLayout(ota_group)
        self.ota_file_button = CustomButton("选择OTA文件")
        self.ota_file_button.clicked.connect(self.select_ota_file)
        ota_layout.addWidget(self.ota_file_button)
        ota_group.setMaximumHeight(100)
        left_layout.addWidget(ota_group)

        # 图片预览区域
        image_group = QGroupBox("图像预览与处理")
        image_layout = QVBoxLayout(image_group)

        # 创建图像显示的水平分割器
        image_splitter = QSplitter(Qt.Horizontal)
        
        # 原图显示区域
        original_group = QGroupBox("原图")
        original_layout = QVBoxLayout(original_group)
        # 用来显示原图的QLabel
        self.original_image_label = QLabel()
        self.original_image_label.setFixedSize(280, 280)
        self.original_image_label.setAlignment(Qt.AlignCenter)
        self.original_image_label.setFrameShape(QFrame.StyledPanel)
        self.original_image_label.setStyleSheet(LABEL_STYLE)
        self.original_image_label.setText("尚未选择图像")
        original_layout.addWidget(self.original_image_label)
        
        # 处理后图像显示区域
        processed_group = QGroupBox("处理后")
        processed_layout = QVBoxLayout(processed_group)
        # 用来显示处理后图像的QLabel
        self.processed_image_label = QLabel()
        self.processed_image_label.setFixedSize(280, 280)
        self.processed_image_label.setAlignment(Qt.AlignCenter)
        self.processed_image_label.setFrameShape(QFrame.StyledPanel)
        self.processed_image_label.setStyleSheet(LABEL_STYLE)
        self.processed_image_label.setStyleSheet("background-color: #f0f0f0;")
        self.processed_image_label.setText("尚未处理图像")
        processed_layout.addWidget(self.processed_image_label)
        
        # 添加到分割器
        image_splitter.addWidget(original_group)
        image_splitter.addWidget(processed_group)
        image_splitter.setSizes([300, 300])

        # 图像处理按钮区域
        image_buttons_layout = QHBoxLayout()
        self.select_button = CustomButton("选择图片")
        self.process_button = CustomButton("处理图片")
        self.clear_image_button = CustomButton("清除图片")

        self.select_button.clicked.connect(self.select_image)
        self.process_button.clicked.connect(self.process_image)
        self.clear_image_button.clicked.connect(self.clear_image)

        image_buttons_layout.addWidget(self.select_button)
        image_buttons_layout.addWidget(self.process_button)
        image_buttons_layout.addWidget(self.clear_image_button)

        image_layout.addWidget(image_splitter)
        image_layout.addLayout(image_buttons_layout)
        left_layout.addWidget(image_group)

        # ===== 右侧区域：数据和设备管理 =====
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 数据显示区域
        data_group = QGroupBox("数据处理与显示")
        data_layout = QVBoxLayout(data_group)

        self.data_table = QTableWidget(0, 2)
        self.data_table.setHorizontalHeaderLabels(["参数", "值"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setStyleSheet(TABLE_WIDGET_STYLE)

        # 数据操作按钮
        data_buttons_layout = QHBoxLayout()
        self.transfer_button = CustomButton("传输数据")
        self.stop_transfer_button = CustomButton("停止传输")
        self._clear_data_button = CustomButton("清除数据")
        self._refresh_data_button = CustomButton("刷新数据")

        # 数据传输按钮的点击事件
        self.transfer_button.clicked.connect(self._transfer_data)
        self.stop_transfer_button.clicked.connect(self._stop_transfer_data)
        self._clear_data_button.clicked.connect(self._clear_data)
        self._refresh_data_button.clicked.connect(self._refresh_data)

        data_buttons_layout.addWidget(self.transfer_button)
        data_buttons_layout.addWidget(self.stop_transfer_button)
        data_buttons_layout.addWidget(self._clear_data_button)
        data_buttons_layout.addWidget(self._refresh_data_button)

        data_layout.addWidget(self.data_table)
        data_layout.addLayout(data_buttons_layout)

        # 设备管理区域
        device_group = QGroupBox("设备管理")
        device_layout = QVBoxLayout(device_group)

        # 创建USB和串口的分割器
        device_splitter = QSplitter(Qt.Vertical)
        device_splitter.setChildrenCollapsible(False)

        # === USB设备管理区域 ===
        usb_group = QGroupBox("USB设备")
        usb_layout = QVBoxLayout(usb_group)

        # USB设备选择
        usb_selection_layout = QHBoxLayout()
        usb_selection_layout.addWidget(QLabel("USB设备:"))
        
        self.usb_combo = QComboBox()
        self.usb_combo.setMinimumWidth(180)
        self.usb_combo.setStyleSheet(COMBOBOX_STYLE)
        usb_selection_layout.addWidget(self.usb_combo)
        usb_selection_layout.addStretch()
        
        # USB操作按钮（垂直排列）
        usb_buttons_layout = QHBoxLayout()
        
        self.refresh_usb_button = CustomButton("刷新")
        self.refresh_usb_button.setMinimumWidth(80)
        self.connect_usb_button = CustomButton("连接")
        self.connect_usb_button.setMinimumWidth(80)

        # 刷新USB和连接USB按钮的点击事件
        self.refresh_usb_button.clicked.connect(self.refresh_usb_devices)
        self.connect_usb_button.clicked.connect(self.connect_or_disconnect_usb)

        usb_buttons_layout.addWidget(self.refresh_usb_button)
        usb_buttons_layout.addWidget(self.connect_usb_button)
        usb_buttons_layout.addStretch()

        usb_layout.addLayout(usb_selection_layout)
        usb_layout.addLayout(usb_buttons_layout)

        # === 串口设备管理区域 ===
        serial_group = QGroupBox("串口设备")
        serial_layout = QVBoxLayout(serial_group)

        # 串口设备选择
        serial_selection_layout = QHBoxLayout()
        serial_selection_layout.addWidget(QLabel("串口:"))
        
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(180)
        self.port_combo.setStyleSheet(COMBOBOX_STYLE)
        serial_selection_layout.addWidget(self.port_combo)
        serial_selection_layout.addStretch()

        # 串口操作按钮（垂直排列）
        serial_buttons_layout = QHBoxLayout()
        
        self.refresh_serial_button = CustomButton("刷新")
        self.refresh_serial_button.setMinimumWidth(80)
        self.connect_serial_button = CustomButton("连接")
        self.connect_serial_button.setMinimumWidth(80)

        serial_buttons_layout.addWidget(self.refresh_serial_button)
        serial_buttons_layout.addWidget(self.connect_serial_button)
        serial_buttons_layout.addStretch()

         # 刷新串口和连接串口按钮的点击事件
        self.refresh_serial_button.clicked.connect(self.refresh_serial_ports)
        self.connect_serial_button.clicked.connect(self.connect_or_disconnect_serial)

        # 创建设备数据显示区域（优化高度）
        self.log_display_text_edit = QTextEdit()
        self.log_display_text_edit.setReadOnly(True)
        self.log_display_text_edit.setMinimumHeight(80)  # 设置最小高度
        self.log_display_text_edit.setMaximumHeight(150)  # 增加最大高度
        self.log_display_text_edit.setStyleSheet(TEXT_EDIT_STYLE)
        self.log_display_text_edit.setPlaceholderText("设备连接后，相关信息将在此显示...")

        serial_layout.addLayout(serial_selection_layout)
        serial_layout.addLayout(serial_buttons_layout)

        # 将USB和串口组添加到分割器
        device_splitter.addWidget(usb_group)
        device_splitter.addWidget(serial_group)

        # 添加调试区域
        debug_group = QGroupBox("调试工具")
        debug_layout = QVBoxLayout(debug_group)
        debug_layout.setContentsMargins(5, 5, 5, 5)  # 减少边距
        
        # 数据发送区域
        send_layout = QHBoxLayout()
        
        # 数据格式选择
        self.data_format_combo = QComboBox()
        self.data_format_combo.addItems(["字符", "16进制"])
        self.data_format_combo.setMaximumWidth(80)
        self.data_format_combo.setStyleSheet(COMBOBOX_STYLE)
        send_layout.addWidget(QLabel("格式:"))
        send_layout.addWidget(self.data_format_combo)
        
        # 数据输入框
        self.debug_input = QLineEdit()
        self.debug_input.setPlaceholderText("输入要发送的数据...")
        self.debug_input.setStyleSheet(DEBUG_INPUT_STYLE)
        send_layout.addWidget(self.debug_input)
        
        # 发送按钮
        self.send_debug_button = CustomButton("发送")
        self.send_debug_button.setMaximumWidth(60)
        self.send_debug_button.setMaximumHeight(25)
        self.send_debug_button.clicked.connect(self.send_debug_data)
        send_layout.addWidget(self.send_debug_button)
        
        # 接收数据显示设置区域
        receive_layout = QHBoxLayout()
        
        # 接收显示类型选择
        self.receive_format_combo = QComboBox()
        self.receive_format_combo.addItems(["字符+字节", "仅字符", "仅字节", "仅16进制"])
        self.receive_format_combo.setMaximumWidth(100)
        self.receive_format_combo.setStyleSheet(COMBOBOX_STYLE)
        receive_layout.addWidget(QLabel("接收显示:"))
        receive_layout.addWidget(self.receive_format_combo)
        receive_layout.addStretch()  # 添加弹性空间
        
        debug_layout.addLayout(send_layout)
        debug_layout.addLayout(receive_layout)
        
        # 添加数据显示区域，调整布局顺序和比例
        device_layout.addWidget(device_splitter, 3)  # 设备选择区域占更多空间
        device_layout.addWidget(self.log_display_text_edit, 2)  # 数据显示区域
        device_layout.addWidget(debug_group, 0)  # 调试工具占最少空间

        # 调整右侧布局比例：增加数据组的比例，减少设备组的比例
        right_layout.addWidget(data_group, 4)  # 从3增加到4
        right_layout.addWidget(device_group, 1)  # 从2减少到1

        # 添加到主分割器
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        # 调整左右比例：给右侧更多空间以便更好地显示信息
        main_splitter.setSizes([700, 500])  # 从[800, 400]调整为[700, 500]

        # 设置中央窗口部件
        self.setCentralWidget(main_splitter)

        # 初始化时刷新设备列表
        self.refresh_serial_ports()
        self.refresh_usb_devices()
        
        # 连接回车键发送功能
        self.debug_input.returnPressed.connect(self.send_debug_data)

    def show_settings(self):
        """显示设置页面"""
        settings_dialog = SettingsPage(self)
        if settings_dialog.exec():  # 使用 exec() 而不是 exec_()
            # 如果用户点击了确定按钮
            self.status_bar.showMessage("设置已更新")
        else:
            # 如果用户点击了取消按钮
            self.status_bar.showMessage("设置已取消")

    def confirm_exit(self):
        """菜单退出选项的处理方法"""
        if not self._closing:  # 防止重复触发
            self._closing = True
            dialog = ExitConfirmDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                
                #清理资源
                self._cleanup_before_exit()
                # 退出应用
                QApplication.instance().quit()

            self._closing = False

    def closeEvent(self, event):
        """窗口关闭按钮的处理方法"""
        if not self._closing:  # 防止重复触发
            self._closing = True
            dialog = ExitConfirmDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                
                #清理资源
                self._cleanup_before_exit()
                event.accept()
                # 确保应用完全退出
                QApplication.instance().quit()
            else:
                event.ignore()
            self._closing = False

    def _cleanup_before_exit(self):
        """在应用退出前清理资源"""
        try:
            RBQLog.log_info("应用退出前清理资源")
            self.connect_manager.disconnect()
            # 注销设备发现处理器
            self.connect_manager.unregister_device_discovery_handler(self.discovery_handler)
            # 注销设备连接处理器
            self.connect_manager.unregister_device_connection_handler(self.connection_handler)
            # 注销设备读取处理器
            self.connect_manager.unregister_device_read_handler(self.read_handler)
            # 注销数据传输处理器
            self.connect_manager.unregister_device_data_transfer_handler(self.data_transfer_handler)

        except Exception as e:
            print(f"关闭连接错误: {e}")

    # 搜索设备事件
    class DeviceDiscoveryHandler(DeviceDiscoveryProtocol):
        """设备发现事件处理器"""

        def __init__(self, main_window):
            self.main_window = main_window
        
        def on_device_discover_start(self) -> None:
            """设备开始发现事件"""
            RBQLog.log("设备发现开始")
            self.main_window.log_display_text_edit.append("[系统] 设备发现开始")
            # 刷新按钮状态
            self.main_window.refresh_serial_button.setEnabled(False)
            self.main_window.refresh_usb_button.setEnabled(False)
            
        def on_device_discover(self, device: DeviceInfo) -> None:
            """发现设备事件"""
            
            #根据设备类型添加到对应列表
            if device.conn_type == ConnType.SERIAL:

                RBQLog.log(f"发现串口设备: {device.serial_port_path}")

                self.main_window.serial_device_infos.append(device)
                self.main_window.log_display_text_edit.append(f"[系统] 发现串口设备 {device.serial_port_path}")
                #将串口设备显示到port_combo
                self.main_window.port_combo.addItem(f"{device.serial_port_path}")

            elif device.conn_type == ConnType.USB:
                # 从设置中获取目标VID/PID
                target_vid = SettingsPage.get_setting('usb/vendor_id', '', str).strip()
                target_pid = SettingsPage.get_setting('usb/product_id', '', str).strip()

                device_class_name: str = self.main_window._get_device_class_name(device.device_class)

                # 打印设备vid和pid
                RBQLog.log(f"发现USB设备: {device.name} - VID: {device.vendor_id} - PID: {device.product_id} - 设备类: {device_class_name}")
                self.main_window.log_display_text_edit.append(f"[系统] 发现USB设备 {device.usb_path} - {device_class_name}")
                
                # 调试信息：显示当前的过滤设置
                self.main_window.log_display_text_edit.append(f"[调试] 过滤设置 - VID: {target_vid}, PID: {target_pid}")
                
                # 根据target_vid和target_pid过滤usb_combo
                if target_vid and target_pid:
                    try:
                        if device.vendor_id == int(target_vid, 16) and device.product_id == int(target_pid, 16):
                            self.main_window.usb_device_infos.append(device)
                            self.main_window.usb_combo.addItem(f"{device.usb_path} - {device_class_name}")
                            self.main_window.log_display_text_edit.append(f"[系统] 设备已添加到列表 (符合VID/PID过滤条件)-{device.usb_path}")
                        else:
                            self.main_window.log_display_text_edit.append(f"[系统] 设备未添加到列表 (不符合VID/PID过滤条件)-{device.usb_path}")
                    except ValueError:
                        # 处理无效的VID/PID格式
                        self.main_window.log_display_text_edit.append(f"[错误] 无效的VID/PID格式 - VID: {target_vid}, PID: {target_pid}")
                        # 格式无效时，仍然添加设备
                        self.main_window.usb_device_infos.append(device)
                        self.main_window.usb_combo.addItem(f"{device.usb_path} - {device_class_name}")
                else:
                    self.main_window.usb_device_infos.append(device)
                    self.main_window.usb_combo.addItem(f"{device.usb_path} - {device_class_name}")
                    self.main_window.log_display_text_edit.append(f"[系统] 设备已添加到列表 (未设置过滤条件)-{device.usb_path}")
            
        def on_device_discover_stop(self) -> None:
            """设备发现完成事件"""
            RBQLog.log("设备发现停止")
            self.main_window.log_display_text_edit.append("[系统] 设备发现停止")
            # 刷新按钮状态
            self.main_window.refresh_serial_button.setEnabled(True)
            self.main_window.refresh_usb_button.setEnabled(True)
            
            # 如果有串口设备，默认选中第一个
            if self.main_window.port_combo.count() > 0:
                self.main_window.port_combo.setCurrentIndex(0)
                RBQLog.log("默认选中第一个串口设备")
            
            # 如果有USB设备，默认选中第一个
            if self.main_window.usb_combo.count() > 0:
                self.main_window.usb_combo.setCurrentIndex(0)
                RBQLog.log("默认选中第一个USB设备")

    #连接设备事件
    class DeviceConnectionHandler(DeviceConnectionProtocol):
        def __init__(self, main_window):
            self.main_window = main_window

        def on_device_connect_start(self, device: DeviceInfo) -> None:
            """设备开始连接事件"""
            RBQLog.log(f"设备开始连接: {device.name}")
            self.main_window.log_display_text_edit.append(f"[系统] 设备开始连接-{device.name}")
            self.main_window.status_bar.showMessage("正在连接设备...")
            # 更新连接按钮状态
            if device.conn_type == ConnType.USB:
                self.main_window.update_connect_button_states(False,True)
            # 更新串口连接按钮状态
            if device.conn_type == ConnType.SERIAL:
                self.main_window.update_connect_button_states(True,False)

        def on_device_connect_succeed(self, device: DeviceInfo) -> None:
            """设备连接成功事件"""
            RBQLog.log(f"设备连接成功: {device.name}")
            self.main_window.log_display_text_edit.append(f"[系统] 设备连接成功-{device.name}")
            self.main_window.status_bar.showMessage("设备连接成功")
            # 更新连接按钮状态
            if device.conn_type == ConnType.USB:
                self.main_window.update_connect_button_states(False,True)
            # 更新串口连接按钮状态
            if device.conn_type == ConnType.SERIAL:
                self.main_window.update_connect_button_states(True,False)
            # 读取软件版本
            self.main_window.connect_manager.read_software_info()

        def on_device_disconnect(self, device: DeviceInfo) -> None:
            """设备断开连接事件"""
            RBQLog.log(f"设备断开连接: {device.name}")
            self.main_window.log_display_text_edit.append(f"[系统] 设备断开连接-{device.name}")
            self.main_window.status_bar.showMessage("设备断开连接")
            # 更新连接按钮状态
            self.main_window.update_connect_button_states(False,False)

        def on_device_connect_fail(self, device: DeviceInfo) -> None:
            """设备连接失败事件"""
            RBQLog.log(f"设备连接失败: {device.name}")
            self.main_window.log_display_text_edit.append(f"[系统] 设备连接失败-{device.name}")
            self.main_window.status_bar.showMessage("设备连接失败")
            # 更新usb连接按钮状态
            self.main_window.update_connect_button_states(False,False)

    #读取数据事件
    class DeviceReadHandler(DeviceReadProtocol):
        def __init__(self, main_window):
            self.main_window = main_window

        def on_device_read_data(self, device: DeviceInfo, data: bytes) -> None:
            """设备读取数据事件，这个无论啥数据都会返回，是未进行解析的数据"""
            # RBQLog.log(f"设备读取数据: {device.name}, 数据: {data.encode('utf-8')}")
            # 显示成字符串
            self.main_window.log_display_text_edit.append(f"[系统] 设备读取数据-{device.name}-{data.decode('utf-8')}")

    # 数据传输事件
    class DeviceDataTransferHandler(DeviceDataTransferProtocol):
        def __init__(self, main_window):
            self.main_window = main_window

        def on_device_data_transfer_start(self, device: DeviceInfo, size: float, startTime: int, currentTime: int) -> None:
            """设备数据传输开始事件"""
            RBQLog.log(f"设备数据传输开始: {device.name}")
            self.main_window.log_display_text_edit.append("[系统] 设备数据传输开始")
            self.main_window.status_bar.showMessage("正在传输数据...")

        def on_device_data_transfer_progress(self, device: DeviceInfo, size: float, progress: int, startTime: int, currentTime: int) -> None:
            """设备数据传输进度事件"""
            RBQLog.log(f"设备数据传输进度: {device.name}, 进度: {progress}%, 已传输: {size}字节")
            self.main_window.log_display_text_edit.append(f"[系统] 设备数据传输进度: {progress}%, 已传输: {size}字节")
            self.main_window.status_bar.showMessage(f"正在传输数据... {progress}%")

        def on_device_data_transfer_success(self, device: DeviceInfo, size: float, startTime: int, currentTime: int) -> None:
            """设备数据传输成功事件"""
            RBQLog.log(f"设备数据传输成功: {device.name}, 已传输: {size}字节")
            self.main_window.log_display_text_edit.append("[系统] 设备数据传输成功")
            self.main_window.status_bar.showMessage("数据传输成功")
        
        def on_device_data_transfer_error(self, error_code: int, error_message: str) -> None:
            """设备数据传输失败事件"""
            RBQLog.log(f"设备数据传输失败, 错误码: {error_code}, 错误信息: {error_message}")
            self.main_window.log_display_text_edit.append(f"[系统] 设备数据传输失败: 错误码: {error_code}, 错误信息: {error_message}")
            self.main_window.status_bar.showMessage("数据传输失败")

    # 更新串口连接按钮和USB连接按钮状态
    def update_connect_button_states(self,serial_connect_state:bool,usb_connect_state:bool):
        """更新连接按钮状态
        
        根据当前连接状态更新连接按钮的文本和启用状态。
        如果都没连接，则都可点击
        如果usb已连接，则usb连接按钮可点击，串口连接按钮不可点击
        如果串口已连接，则usb连接按钮不可点击，串口连接按钮可点击
        如果usb和串口都连接，则都不可点击
        """
        if serial_connect_state and usb_connect_state:
            self.connect_serial_button.setText("断开")
            self.connect_usb_button.setText("断开")
            self.connect_serial_button.setEnabled(True)
            self.connect_usb_button.setEnabled(True)
        elif serial_connect_state and not usb_connect_state:
            self.connect_serial_button.setText("断开")
            self.connect_usb_button.setText("连接")
            self.connect_serial_button.setEnabled(True)
            self.connect_usb_button.setEnabled(False)
        elif not serial_connect_state and usb_connect_state:
            self.connect_serial_button.setText("连接")
            self.connect_usb_button.setText("断开")
            self.connect_serial_button.setEnabled(False)
            self.connect_usb_button.setEnabled(True)
        elif not serial_connect_state and not usb_connect_state:
            self.connect_serial_button.setText("连接")
            self.connect_usb_button.setText("连接")
            self.connect_serial_button.setEnabled(True)
            self.connect_usb_button.setEnabled(True)
        else:
            self.connect_serial_button.setEnabled(False)
            self.connect_usb_button.setEnabled(False)
            self.status_bar.showMessage("[错误] 当前设备已连接")
            self.log_display_text_edit.append("[错误] 当前设备已连接")

    ##刷新USB设备列表USB设备列表
    def refresh_usb_devices(self):
        """刷新USB设备列表
        
        根据设置中的VID/PID过滤设备，如果未设置则显示所有设备。
        显示设备类型信息以帮助用户识别设备。
        """
        RBQLog.log("刷新USB设备列表")
        self.log_display_text_edit.append("[系统] 刷新USB设备列表")
        #清除usb设备列表
        self.usb_device_infos.clear()
        self.usb_combo.clear()
        # 使用ConnectManager发现USB设备
        self.connect_manager.discover_devices([ConnType.USB])
    
    #刷新串口列表
    def refresh_serial_ports(self):
        """刷新串口列表

        """
        RBQLog.log("刷新串口列表")
        self.log_display_text_edit.append("[系统] 刷新串口列表")
        #清空串口设备列表
        self.serial_device_infos.clear()
        self.port_combo.clear()
        # 使用ConnectManager发现串口设备
        self.connect_manager.discover_devices([ConnType.SERIAL])

    def connect_or_disconnect_serial(self):
        RBQLog.log(f"执行connect_or_disconnect_serial()方法-->当前设备是否已连接: {self.connect_manager.is_connected()}")
        if self.connect_manager.is_connected():
            self.disconnect_serial()
        else:
            self.connect_serial()

    def connect_serial(self):
        """连接串口
        
        使用新的连接框架进行串口连接，包含连接前验证和详细日志记录。

        """
        if self.connect_manager.is_connected():
            self.log_display_text_edit.append("[错误] 请先断开当前连接")
            self.status_bar.showMessage("[错误] 请先断开当前连接")
            return
        # 获取目前选中port_combo第几项
        current_index: int = self.port_combo.currentIndex()
        RBQLog.log(f"当前选中串口设备索引: {current_index};当前串口设备数:{len(self.serial_device_infos)}")
        # 检查索引是否有效
        if current_index < 0 or current_index >= len(self.serial_device_infos):
            self.log_display_text_edit.append("[错误] 请先选择有效的串口设备")
            self.status_bar.showMessage("[错误] 请先选择有效的串口设备")
            return
        
        # 获取当前选中的设备信息
        try:
            # 获取串口设置参数，确保正确的数据类型
            baudrate: int = SettingsPage.get_setting("serial/default_baudrate", value_type=int)
            data_bits: int = SettingsPage.get_setting("serial/data_bits", value_type=int)
            parity: str = SettingsPage.get_setting("serial/parity")
            stop_bits: float = SettingsPage.get_setting("serial/stop_bits", value_type=float)
            
            # 获取流控制设置
            xonxoff: bool = SettingsPage.get_setting("serial/xonxoff", False, bool)  # 软件流控制
            rtscts: bool = SettingsPage.get_setting("serial/rtscts", False, bool)    # 硬件流控制 RTS/CTS
            dsrdtr: bool = SettingsPage.get_setting("serial/dsrdtr", False, bool)    # 硬件流控制 DSR/DTR
            
            read_timeout: float = SettingsPage.get_setting("serial/read_timeout", value_type=float)
            write_timeout: float = SettingsPage.get_setting("serial/write_timeout", value_type=float)
            # auto_reconnect: bool = SettingsPage.get_setting("serial/auto_reconnect")
            # retry_count: int = SettingsPage.get_setting("serial/retry_count")
            # retry_interval: int = SettingsPage.get_setting("serial/retry_interval")
            # buffer_size: int = SettingsPage.get_setting("serial/buffer_size")
            # data_format: str = SettingsPage.get_setting("serial/data_format")
            
            RBQLog.log(f"设置的参数: baudrate:{baudrate}, data_bits:{data_bits}, parity:{parity}, stop_bits:{stop_bits}, " +
                      f"xonxoff:{xonxoff}, rtscts:{rtscts}, dsrdtr:{dsrdtr}, " +
                      f"read_timeout:{read_timeout}, write_timeout:{write_timeout}")
            
            device_info: DeviceInfo = self.serial_device_infos[current_index]
            device_info.baudrate = baudrate
            device_info.data_bits = data_bits
            device_info.stop_bits = stop_bits
            device_info.parity = parity
            
            # 设置流控制参数
            device_info.xonxoff = xonxoff  # 软件流控制
            device_info.rtscts = rtscts    # 硬件流控制 RTS/CTS
            device_info.dsrdtr = dsrdtr    # 硬件流控制 DSR/DTR
            
            device_info.read_timeout = read_timeout
            device_info.write_timeout = write_timeout
            # 打印设备信息
            RBQLog.log(f"选中的串口设备信息: {device_info}")
            self.connect_manager.connect(device_info)
        except Exception as e:
            self.log_display_text_edit.append(f"[错误] 连接串口设备失败: {str(e)}")
            self.status_bar.showMessage(f"[错误] 连接串口设备失败")
            RBQLog.log_error(f"连接串口设备失败: {str(e)}")

    def disconnect_serial(self):
        """断开串口连接"""
        if self.connect_manager.is_connected():
            RBQLog.log("当前串口设备已连接，执行断开操作")
            self.connect_manager.disconnect()
        else:
            RBQLog.log("当前串口设备未连接，无需执行断开操作")
            self.log_display_text_edit.append("[错误] 没有连接的串口设备")
            self.status_bar.showMessage("[错误] 没有连接的串口设备")

    def connect_or_disconnect_usb(self):
        RBQLog.log(f"执行connect_or_disconnect_usb()方法 -->当前设备是否已连接: {self.connect_manager.is_connected()}")
        if self.connect_manager.is_connected():
            self.disconnect_usb_device()
        else:
            self.connect_usb_device()

    def connect_usb_device(self):
        """连接USB设备
        
        实现USB设备的连接和断开功能，包含详细的错误处理和用户提示。

        """
        if self.connect_manager.is_connected():
            self.log_display_text_edit.append("[错误] 请先断开当前连接")
            self.status_bar.showMessage("[错误] 请先断开当前连接")
            return
        # 获取目前选中usb_combo第几项
        current_index: int = self.usb_combo.currentIndex()
        RBQLog.log(f"当前选中USB设备索引: {current_index};当前USB设备数:{len(self.usb_device_infos)}")
        # 检查索引是否有效
        if current_index < 0 or current_index >= len(self.usb_device_infos):
            self.log_display_text_edit.append("[错误] 请先选择有效的USB设备")
            self.status_bar.showMessage("[错误] 请先选择有效的USB设备")
            return
        
        # 获取当前选中的设备信息
        try:
            device_info: DeviceInfo = self.usb_device_infos[current_index]
            self.connect_manager.connect(device_info)
        except Exception as e:
            self.log_display_text_edit.append(f"[错误] 连接USB设备失败: {str(e)}")
            self.status_bar.showMessage(f"[错误] 连接USB设备失败")
            RBQLog.log_error(f"连接USB设备失败: {str(e)}")

    def disconnect_usb_device(self):
        """断开USB设备连接"""
        if self.connect_manager.is_connected():
            self.connect_manager.disconnect()
        else:
            self.log_display_text_edit.append("[错误] 没有连接的USB设备")
            self.status_bar.showMessage("[错误] 没有连接的USB设备")

    # 用于根据 USB 设备类代码（十六进制）返回对应的人类可读类型名称
    def _get_device_class_name(self, device_class: int) -> str:
        """获取USB设备类型名称
        
        Args:
            device_class: USB设备类代码
            
        Returns:
            str: 设备类型名称

        """
        class_names = {
            0x00: "接口定义",
            0x01: "音频设备",
            0x02: "通信设备",
            0x03: "人机接口",
            0x05: "物理设备",
            0x06: "图像设备",
            0x07: "打印机",
            0x08: "存储设备",
            0x09: "USB Hub",
            0x0A: "通信数据",
            0x0B: "智能卡",
            0x0D: "安全设备",
            0x0E: "视频设备",
            0x0F: "医疗设备",
            0x10: "音视频设备",
            0x11: "诊断设备",
            0xDC: "诊断设备",
            0xE0: "无线控制器",
            0xEF: "其他设备",
            0xFE: "应用特定",
            0xFF: "厂商特定"
        }
        return class_names.get(device_class, f"未知类型(0x{device_class:02x})")

    
    def _get_usb_connection_error_message(self, device_text: str, vid: int, pid: int) -> str:
        """生成详细的USB连接错误信息
        
        Args:
            device_text: 设备显示文本
            vid: 厂商ID
            pid: 产品ID
            
        Returns:
            str: 详细的错误信息

        """
        # 检查是否为已知的非打印机设备
        non_printer_keywords = ['hub', 'mouse', 'keyboard', 'camera', 'storage', 'disk', 'card reader']
        device_lower = device_text.lower()
        
        if any(keyword in device_lower for keyword in non_printer_keywords):
            return f"[警告] 设备'{device_text}'可能不是打印机设备，请确认选择正确的设备"
        
        # 检查是否为USB Hub (GenesysLogic)
        if vid == 0x5e3 and pid == 0x610:
            return f"[错误] 检测到USB Hub设备，请连接实际的打印机设备而非USB集线器"
        
        # 检查常见的USB Hub厂商
        hub_vendors = {0x5e3: "GenesysLogic", 0x1a40: "Terminus Technology", 0x0424: "Microchip"}
        if vid in hub_vendors:
            return f"[警告] 设备可能是{hub_vendors[vid]} USB Hub，请选择打印机设备"
        
        # 通用错误信息
        return f"[错误] USB设备连接失败: {device_text} (VID: 0x{vid:04x}, PID: 0x{pid:04x}) - 请检查设备是否为支持的打印机型号或尝试重新插拔设备"

    def select_ota_file(self):
        """选择OTA文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择OTA文件", "", "OTA Files (*.rbl)"
        )
        if file_path:
            # 加载ota 数据
            ota_data: bytes = self._read_file(file_path)
            self.current_ota_data = ota_data

    def _read_file(self, file_path: str) -> bytes:
        """读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            bytes: 文件内容

        """
        with open(file_path, 'rb') as file:
            return file.read()

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
                
                self.image_processor.get_image_info(file_path)
            else:
                self.status_bar.showMessage("图片加载失败！")

    def process_image(self):

        if not self.current_image_path:
            self.status_bar.showMessage("请先选择图片")
            return
        
        self.status_bar.showMessage("正在处理图像...")
        
        # 获取图像处理设置（确保类型正确）
        threshold = SettingsPage.get_setting('image/threshold', 128, int)
        clear_background = SettingsPage.get_setting('image/clear_background', False, bool)
        dithering = SettingsPage.get_setting('image/dithering', 'Floyd-Steinberg') == 'Floyd-Steinberg'
        compress = SettingsPage.get_setting('image/compress', True, bool)
        flip_horizontally = SettingsPage.get_setting('image/flip_horizontally', False, bool)
        row_layout_direction_text = SettingsPage.get_setting('image/row_layout_direction', '垂直方向', str)

        # 将文本转换为枚举值
        if row_layout_direction_text == '水平方向':
            row_layout_direction = RowLayoutDirection.HORIZONTAL
        else:
            row_layout_direction = RowLayoutDirection.VERTICAL

        # 打印获取的设置
        print(f"阈值: {threshold}, 背景清除: {clear_background}, 抖动: {dithering}, 压缩: {compress}, 水平翻转: {flip_horizontally}, 行布局方向: {row_layout_direction_text}")

        # 要传输的数据类型
        data_type = SettingsPage.get_setting('data/type', 0, int)
        if data_type == 0:
            # 传输打印图片数据
            RBQLog.log("处理打印数据")
            self._process_image_data(threshold, clear_background, dithering, compress, flip_horizontally, row_layout_direction)
        elif data_type == 1:
            # 传输logo数据
            RBQLog.log("处理logo数据")
            self._process_logo_data()
        elif data_type == 2:
            # 传输ota数据
            RBQLog.log("处理ota数据")
            self._process_ota_data()
            
    
    # 处理图片数据
    def _process_image_data(self, threshold: int, clear_background: bool, dithering: bool, compress: bool, flip_horizontally: bool, row_layout_direction: RowLayoutDirection):
        """传输图片数据到设备
        """
        try:

            if not self.current_image_path:
                self.status_bar.showMessage("请先选择图片")
                return

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
                row_layout_direction=row_layout_direction,
                is_contiguous_cropped_images=False
            )
            
            # 定义回调函数
            def on_start():
                self.status_bar.showMessage("开始处理图像...")
            
            def on_complete(multi_row_data):
                try:
                    if multi_row_data and multi_row_data.image_paths:
                        # 保存处理后的MultiRowData对象供传输使用
                        self.current_multi_row_data = multi_row_data
                        # 显示处理后的第一张图像
                        processed_image_path: str = multi_row_data.image_paths[0]
                        RBQLog.log(f"处理模拟图的路径 processed_image_path: {processed_image_path}")
                        # 显示处理后的图像
                        self.display_processed_image_from_path(processed_image_path)
                        
                        # 生成打印数据信息
                        self.generate_print_data_from_multi_row_data(multi_row_data)
                        
                        self.status_bar.showMessage("图像处理完成")
                    else:
                        self.current_multi_row_data = None
                        self.status_bar.showMessage("图像处理失败：无处理结果")
                except Exception as e:
                    self.current_multi_row_data = None
                    self.status_bar.showMessage(f"显示处理结果错误: {str(e)}")
                    print(f"显示处理结果错误: {e}")
            
            def on_error():
                self.status_bar.showMessage("图像处理失败")
            
            # 使用await等待异步操作完成
            MultiRowDataFactory.better_merge_bitmap_to_multi_row_data_async(
                    multi_row_image=multi_row_image,
                    threshold=threshold,
                    clear_background=clear_background,
                    dithering=dithering,
                    compress=compress,
                    flip_horizontally=flip_horizontally,
                    is_simulation=True,  # 需要生成模拟图像
                    thumb_to_simulation=False,
                    on_start=on_start,
                    on_complete=on_complete,
                    on_error=on_error
                )
                
        except Exception as e:
            self.status_bar.showMessage(f"图像处理错误: {str(e)}")
            RBQLog.log_error(f"图像处理错误: {e}")
    
    # 处理logo数据
    def _process_logo_data(self):
        """传输logo数据到设备
        """
        try:

            if not self.current_image_path:
                self.status_bar.showMessage("请先选择图片")
                return

            logoImage = LogoImage(
                image_path=self.current_image_path
            )

            def on_start():
                self.status_bar.showMessage("开始处理图像...")
            
            def on_complete(logo_data: LogoData):
                self.current_logo_data = logo_data
                self.status_bar.showMessage("处理完成")
                image_path = logo_data.image_path
                self.display_processed_image_from_path(image_path)
            
            def on_error():
                self.status_bar.showMessage("处理失败")

            LogoDataFactory.logo_image_to_data_async(
                logo_image=logoImage,
                threshold=128,
                on_start=on_start,
                on_complete=on_complete,
                on_error=on_error
            )

        except Exception as e:
            self.status_bar.showMessage(f"logo数据处理错误: {str(e)}")
            RBQLog.log_error(f"logo数据处理错误: {str(e)}")
    # 处理ota数据
    def _process_ota_data(self):
        """传输ota数据到设备
        """
        try:
            if not self.current_ota_data:
                self.status_bar.showMessage("请先选择ota文件")
                return
            
            self.connect_manager.send_ota_data(self.current_ota_data)

        except Exception as e:
            self.status_bar.showMessage(f"ota数据处理错误: {str(e)}")
            RBQLog.log_error(f"传输ota数据错误: {e}")

    def clear_image(self):
        """清除当前显示的图片"""
        self.original_image_label.clear()
        self.original_image_label.setText("尚未选择图像")
        self.processed_image_label.clear()
        self.processed_image_label.setText("尚未处理图像")
        self.current_image_path = None
        self._clear_data()
        self.status_bar.showMessage("已清除图像")

    # 传输数据按钮transfer_button的点击事件
    def _transfer_data(self):
        """传输数据到设备
        """
        try:
            
            # 从设置中获取用户选择的传输协议
            protocol_index = SettingsPage.get_setting('transport/protocol_index', 0, int)
            
            # 根据索引选择对应的协议常量
            protocol_constants = [SOH, STX, STX_A, STX_B, STX_C, STX_D, STX_E]
            if 0 <= protocol_index < len(protocol_constants):
                selected_protocol = protocol_constants[protocol_index]
                protocol_names = ["SOH", "STX", "STX_A", "STX_B", "STX_C", "STX_D", "STX_E"]
                protocol_name = protocol_names[protocol_index]
                RBQLog.log(f"使用传输协议: {protocol_name} (0x{selected_protocol:02X})")
                self.log_display_text_edit.append(f"[系统] 使用传输协议: {protocol_name}")
            else:
                # 默认使用STX_E
                selected_protocol = STX_E
                RBQLog.log(f"使用默认传输协议: STX_E (0x{STX_E:02X})")
                self.log_display_text_edit.append("[系统] 使用默认传输协议: STX_E")
            
            # 获取传输数据类型设置
            data_type = SettingsPage.get_setting('data/type', 0, int)
            if data_type == 0:
                # 传输图片数据
                self._transfer_image_data(selected_protocol)
            elif data_type == 1:
                # 传输logo数据
                self._transfer_logo_data(selected_protocol)
            elif data_type == 2:
                # 传输ota数据
                self._transfer_ota_data(selected_protocol)
            else:
                self.status_bar.showMessage("无效的传输数据类型")
                return

                
        except Exception as e:
            error_msg = f"传输数据时发生错误: {str(e)}"
            RBQLog.log_error(error_msg)
            self.log_display_text_edit.append(f"[错误] {error_msg}")
            self.status_bar.showMessage(error_msg)

    # 传输图片数据
    def _transfer_image_data(self, selected_fn:int):
        """传输图片数据到设备
        """
        try:
            if not self.current_multi_row_data:
                self.status_bar.showMessage("请先处理图像")
                return
            # 使用ConnectManager发送多行数据
            self.connect_manager.set_with_send_multi_row_data_packet(
                multi_row_data=self.current_multi_row_data,
                fn=selected_fn
            )
        except Exception as e:
            self.status_bar.showMessage(f"传输图片数据错误: {str(e)}")
            print(f"传输图片数据错误: {e}")

    # 传输logo数据
    def _transfer_logo_data(self, selected_fn:int):
        """传输logo数据到设备
        """
        try:
            if not self.current_logo_data:
                self.status_bar.showMessage("请先处理logo数据")
                return
            # 使用ConnectManager发送logo数据
            self.connect_manager.set_with_send_logo_packet(
                logo_data=self.current_logo_data,
                fn=selected_fn
            )
        except Exception as e:
            self.status_bar.showMessage(f"传输logo数据错误: {str(e)}")
            print(f"传输logo数据错误: {e}")

    # 传输ota数据
    def _transfer_ota_data(self, selected_fn:int):
        """传输ota数据到设备
        """
        try:
            if not self.current_ota_data:
                self.status_bar.showMessage("请先处理ota数据")
                return
            # 使用ConnectManager发送ota数据
            self.connect_manager.set_with_send_ota_data_packet(
                data=self.current_ota_data,
                fn=selected_fn
            )
        except Exception as e:
            self.status_bar.showMessage(f"传输ota数据错误: {str(e)}")
            print(f"传输ota数据错误: {e}")

    def _stop_transfer_data(self):
        """停止传输数据
        """
        

    # 停止图片数据传输
    def _stop_transfer_image_data(self):
        """停止传输图片数据
        """
        try:
            # 检查是否有活动连接
            if not self.connect_manager.is_connected():
                self.log_display_text_edit.append("[错误] 没有连接的设备")
                return

            # 停止数据传输
            self.connect_manager.cancel_send_multi_row_data_packet()

        except Exception as e:
            error_msg = f"停止传输图片数据时发生错误: {str(e)}"
            RBQLog.log_error(error_msg)
            self.log_display_text_edit.append(f"[错误] {error_msg}")
            self.status_bar.showMessage(error_msg)

    # 停止logo数据传输
    def _stop_transfer_logo_data(self):
        """停止传输logo数据
        """
        try:
            # 检查是否有活动连接
            if not self.connect_manager.is_connected():
                self.log_display_text_edit.append("[错误] 没有连接的设备")
                return

            # 停止数据传输
            self.connect_manager.cancel_send_logo_packet()

        except Exception as e:
            error_msg = f"停止传输logo数据时发生错误: {str(e)}"
            RBQLog.log_error(error_msg)
            self.log_display_text_edit.append(f"[错误] {error_msg}")
            self.status_bar.showMessage(error_msg)

    # 停止ota数据传输
    def _stop_transfer_ota_data(self):
        """停止传输ota数据
        """
        try:
            # 检查是否有活动连接
            if not self.connect_manager.is_connected():
                self.log_display_text_edit.append("[错误] 没有连接的设备")
                return

            # 停止数据传输
            self.connect_manager.cancel_send_ota_data_packet()

        except Exception as e:
            error_msg = f"停止传输ota数据时发生错误: {str(e)}"
            RBQLog.log_error(error_msg)
            self.log_display_text_edit.append(f"[错误] {error_msg}")
            self.status_bar.showMessage(error_msg)

    def _clear_data(self):
        """清除数据表格"""
        self.data_table.setRowCount(0)
        self.status_bar.showMessage("已清除数据")

    def display_processed_image_from_path(self, image_path):
        """从路径显示处理后的图像"""
        try:
            # 加载图像
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # 缩放图像以适应标签
                scaled_pixmap = pixmap.scaled(
                    self.processed_image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                self.processed_image_label.setPixmap(scaled_pixmap)
            else:
                self.processed_image_label.setText("图像加载失败")
                
        except Exception as e:
            print(f"显示处理后图像错误: {e}")
            self.status_bar.showMessage(f"显示图像错误: {str(e)}")
            
    def display_processed_image(self, processed_image):
        """显示处理后的图像（PIL图像）"""
        try:
            # 将PIL图像转换为QPixmap
            if hasattr(processed_image, 'save'):
                # PIL图像
                buffer = io.BytesIO()
                processed_image.save(buffer, format='PNG')
                buffer.seek(0)
                
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
                
                # 缩放图像以适应标签
                scaled_pixmap = pixmap.scaled(
                    self.processed_image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                self.processed_image_label.setPixmap(scaled_pixmap)
                
        except Exception as e:
            print(f"显示处理后图像错误: {e}")
            self.status_bar.showMessage(f"显示图像错误: {str(e)}")
    # 显示处理完后的信息
    def generate_print_data_from_multi_row_data(self, multi_row_data):
        """从MultiRowData生成打印数据信息"""
        try:
            # 清除现有数据
            self.data_table.setRowCount(0)
            
            # 获取基本信息
            row_count = len(multi_row_data.row_data_arr)
            total_data_length = sum(row_data.data_length for row_data in multi_row_data.row_data_arr)
            compress_status = "是" if multi_row_data.compress else "否"
            layout_direction = "垂直" if multi_row_data.row_layout_direction.name == "VERTICAL" else "水平"
            
            # 添加基本信息到表格
            info_data = [
                ("行数", f"{row_count}"),
                ("总数据长度", f"{total_data_length} 字节"),
                ("数据压缩", compress_status),
                ("布局方向", layout_direction),
                ("处理图像数", f"{len(multi_row_data.image_paths) if multi_row_data.image_paths else 0}"),
            ]
            
            # 添加每行的详细信息
            for i, row_data in enumerate(multi_row_data.row_data_arr):
                info_data.append((f"第{i+1}行数据长度", f"{row_data.data_length} 字节"))
            
            for i, (key, value) in enumerate(info_data):
                self.data_table.insertRow(i)
                self.data_table.setItem(i, 0, QTableWidgetItem(key))
                self.data_table.setItem(i, 1, QTableWidgetItem(value))
                
        except Exception as e:
            print(f"生成打印数据错误: {e}")
            self.status_bar.showMessage(f"生成数据错误: {str(e)}")
    
    def generate_print_data(self, processed_image):
        """生成打印数据"""
        try:
            # 清除现有数据
            self.data_table.setRowCount(0)
            
            # 获取图像信息
            width, height = processed_image.size
            mode = processed_image.mode
            
            # 添加基本信息到表格
            info_data = [
                ("图像宽度", f"{width} 像素"),
                ("图像高度", f"{height} 像素"),
                ("颜色模式", mode),
                ("数据大小", f"{width * height} 字节"),
            ]
            
            for i, (key, value) in enumerate(info_data):
                self.data_table.insertRow(i)
                self.data_table.setItem(i, 0, QTableWidgetItem(key))
                self.data_table.setItem(i, 1, QTableWidgetItem(value))
            
            # 如果是黑白图像，生成打印数据预览
            if mode in ['1', 'L']:
                self.generate_print_preview(processed_image)
                
        except Exception as e:
            print(f"生成打印数据错误: {e}")
            self.status_bar.showMessage(f"生成数据错误: {str(e)}")
    
    def generate_print_preview(self, image):
        """生成打印预览数据"""
        try:
            # 转换为黑白图像
            if image.mode != '1':
                image = image.convert('1')
            
            # 获取图像数据
            width, height = image.size
            pixels = list(image.getdata())
            
            # 计算数据包数量
            bytes_per_line = (width + 7) // 8
            total_bytes = bytes_per_line * height
            packet_size = 1024  # 假设每包1024字节
            packet_count = (total_bytes + packet_size - 1) // packet_size
            
            # 添加打印预览信息
            current_row = self.data_table.rowCount()
            preview_data = [
                ("每行字节数", f"{bytes_per_line}"),
                ("总字节数", f"{total_bytes}"),
                ("数据包数量", f"{packet_count}"),
                ("打印模式", "黑白模式"),
            ]
            
            for key, value in preview_data:
                self.data_table.insertRow(current_row)
                self.data_table.setItem(current_row, 0, QTableWidgetItem(key))
                self.data_table.setItem(current_row, 1, QTableWidgetItem(value))
                current_row += 1
                
        except Exception as e:
            print(f"生成打印预览错误: {e}")

    def _refresh_data(self):
        """刷新数据"""
        if self.current_image_path:
            self.image_processor.get_image_info(self.current_image_path)
        else:
            self.status_bar.showMessage("没有图片可以刷新")

    def _data_received(self, data):
        """处理接收到的串口数据
        
        根据用户选择的接收显示类型来控制数据显示格式。
        
        Args:
            data: 接收到的数据
        """
        
        # 打印原始数据
        RBQLog.log_debug(f"_data_received: {data}")

        current_time = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss.zzz')
        
        # 获取用户选择的接收显示类型
        display_format = self.receive_format_combo.currentText()
        
        # 将数据转换为可读格式
        if isinstance(data, bytes):
            try:
                # 尝试解码为UTF-8文本
                text_data = data.decode('utf-8', errors='replace')
                byte_values = list(data)
                hex_data = ' '.join([f"{b:02X}" for b in data])
                
                # 根据用户选择显示不同格式
                if display_format == "字符+字节":
                    self.log_display_text_edit.append(f"[{current_time}] 接收字符: '{text_data}'")
                    self.log_display_text_edit.append(f"[{current_time}] 接收字节: {byte_values}")
                elif display_format == "仅字符":
                    self.log_display_text_edit.append(f"[{current_time}] 接收字符: '{text_data}'")
                elif display_format == "仅字节":
                    self.log_display_text_edit.append(f"[{current_time}] 接收字节: {byte_values}")
                elif display_format == "仅16进制":
                    self.log_display_text_edit.append(f"[{current_time}] 接收16进制: {hex_data}")
                    
            except Exception:
                # 如果解码失败，根据选择显示格式
                byte_values = list(data)
                hex_data = ' '.join([f"{b:02X}" for b in data])
                
                if display_format == "字符+字节":
                    self.log_display_text_edit.append(f"[{current_time}] 接收16进制: {hex_data}")
                    self.log_display_text_edit.append(f"[{current_time}] 接收字节: {byte_values}")
                elif display_format == "仅字符":
                    self.log_display_text_edit.append(f"[{current_time}] 接收数据: (无法解码为字符)")
                elif display_format == "仅字节":
                    self.log_display_text_edit.append(f"[{current_time}] 接收字节: {byte_values}")
                elif display_format == "仅16进制":
                    self.log_display_text_edit.append(f"[{current_time}] 接收16进制: {hex_data}")
        else:
            # 如果不是字节类型，直接转换为字符串
            self.log_display_text_edit.append(f"[{current_time}] 接收: {str(data)}")

    @pyqtSlot(dict)
    def _on_image_info_ready(self, info):
        """处理图像信息"""
        self.data_table.setRowCount(0)
        for key, value in info.items():
            self.add_table_row(key, str(value))
        self.status_bar.showMessage("图片信息已更新")

    def add_table_row(self, param, value):
        """向数据表格添加或更新一行"""
        # 查找是否已存在该参数行
        found = False
        for row in range(self.data_table.rowCount()):
            if self.data_table.item(row, 0) and \
                    self.data_table.item(row, 0).text() == param:
                self.data_table.item(row, 1).setText(value)
                found = True
                break

        # 如果不存在则添加新行
        if not found:
            row = self.data_table.rowCount()
            self.data_table.insertRow(row)
            self.data_table.setItem(row, 0, QTableWidgetItem(param))
            self.data_table.setItem(row, 1, QTableWidgetItem(value))
    
    def send_debug_data(self):
        """发送调试数据到串口设备
        
        根据选择的数据格式（字符或10进制）发送数据到当前连接的串口设备。
        发送的数据和结果会显示在设备数据显示区域中。

        """
        # 获取输入的数据
        input_text = self.debug_input.text().strip()
        if not input_text:
            self.log_display_text_edit.append("[调试] 请输入要发送的数据")
            return
        
        # 检查是否有活动连接
        if not self.connect_manager.is_connected():
            self.log_display_text_edit.append("[调试] 错误: 未连接设备")
            return
        
        try:
            # 根据选择的格式处理数据
            data_format = self.data_format_combo.currentText()
            
            if data_format == "字符":
                # 字符格式：直接发送字符串（UTF-8编码）
                data_to_send: bytes = input_text.encode('utf-8')
                self.log_display_text_edit.append(f"[调试] 发送字符: '{input_text}'")
                
            elif data_format == "16进制":
                # 16进制格式：将空格分隔的十六进制数字转换为字节
                try:
                    # 分割输入的十六进制数字
                    hex_numbers = input_text.replace(',', ' ').split()
                    byte_values = []
                    
                    for hex_str in hex_numbers:
                        # 移除可能的0x前缀
                        hex_str = hex_str.strip().lower()
                        if hex_str.startswith('0x'):
                            hex_str = hex_str[2:]
                        
                        # 转换为整数
                        num = int(hex_str, 16)
                        if 0 <= num <= 255:
                            byte_values.append(num)
                        else:
                            raise ValueError(f"十六进制数值 {hex_str} 超出范围 (0x00-0xFF)")
                    
                    data_to_send = bytes(byte_values)
                    hex_display = ' '.join([f"{b:02X}" for b in byte_values])
                    self.log_display_text_edit.append(f"[调试] 发送16进制: {input_text} -> {hex_display}")
                    
                except ValueError as e:
                    self.log_display_text_edit.append(f"[调试] 错误: 16进制格式无效 - {str(e)}")
                    return
            
            self.connect_manager.write_data(data=data_to_send)
                
        except Exception as e:
            #打印log
            RBQLog.log_error(f"数据发送错误: {str(e)}")
            self.log_display_text_edit.append(f"[调试] 发送错误: {str(e)}")