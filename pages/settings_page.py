#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置页面模块

作者: RBQ
版本: 1.0.0
Python版本: 3.9+
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QPushButton, QTabWidget, QCheckBox,
    QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit, QGroupBox,
    QSlider, QFormLayout, QGridLayout, QRadioButton
)
from PyQt5.QtCore import Qt, QSettings


class SettingsPage(QDialog):
    """设置页面类
    
    提供应用程序的各种设置选项，包括常规设置、串口设置和图像设置。
    """
    
    # 校验位映射关系
    PARITY_TO_CHAR = {
        '无': 'N',
        '偶校验': 'E',
        '奇校验': 'O',
        '标记': 'M',
        '空格': 'S'
    }
    
    # 校验位反向映射关系
    CHAR_TO_PARITY = {
        'N': '无',
        'E': '偶校验',
        'O': '奇校验',
        'M': '标记',
        'S': '空格'
    }
    
    def __init__(self, parent=None):
        """初始化设置页面
        
        Args:
            parent: 父窗口实例
        """
        super().__init__(parent)
        self.setWindowTitle("设置相关")
        self.resize(700, 500)
        
        # 初始化设置存储
        self.settings = QSettings('RBQ', 'EdenxPrinter')
        
        # 初始化UI控件引用
        self._init_control_refs()
        
        # 初始化UI
        self.init_ui()
        
        # 加载设置
        self.load_settings()
    
    def _init_control_refs(self):
        """初始化控件引用"""
        # 常规设置控件
        self.auto_save_checkbox = None
        self.theme_combo = None
        self.language_combo = None
        self.restore_session_checkbox = None
        self.check_updates_checkbox = None
        
        # 串口设置相关控件
        self.default_baudrate_combo = None
        self.timeout_spinbox = None
        self.auto_reconnect_checkbox = None
        self.buffer_size_spinbox = None
        self.data_format_combo = None
        self.data_bits_combo = None
        self.parity_combo = None
        self.stop_bits_combo = None
        # 流控制相关控件
        self.xonxoff_checkbox = None  # 软件流控制
        self.rtscts_checkbox = None   # 硬件流控制 RTS/CTS
        self.dsrdtr_checkbox = None   # 硬件流控制 DSR/DTR
        self.retry_count_spinbox = None
        self.retry_interval_spinbox = None
        
        # USB设置相关控件
        self.usb_vendor_id_edit = None
        self.usb_product_id_edit = None
        self.usb_timeout_spinbox = None
        self.usb_auto_reconnect_checkbox = None
        self.usb_buffer_size_spinbox = None
        self.usb_data_format_combo = None
        self.usb_retry_count_spinbox = None
        self.usb_retry_interval_spinbox = None
        self.usb_endpoint_in_spinbox = None
        self.usb_endpoint_out_spinbox = None
        
        # 传输设置控件
        self.protocol_combo = None
        self.max_errors_spinbox = None
        
        # 图像设置控件
        self.image_quality_slider = None
        self.quality_label = None
        self.auto_resize_checkbox = None
        self.max_width_spinbox = None
        self.max_height_spinbox = None
        self.processing_mode_combo = None
        self.dithering_combo = None
        
        # 数据类型设置控件
        self.data_type_group = None
        self.print_data_radio = None
        self.logo_data_radio = None
        self.ota_data_radio = None
        self.stop_bits_combo = None
        # 流控制相关控件
        self.xonxoff_checkbox = None  # 软件流控制
        self.rtscts_checkbox = None   # 硬件流控制 RTS/CTS
        self.dsrdtr_checkbox = None   # 硬件流控制 DSR/DTR
        self.retry_count_spinbox = None
        self.retry_interval_spinbox = None
        
        # USB设置相关控件
        self.usb_vendor_id_edit = None
        self.usb_product_id_edit = None
        self.usb_timeout_spinbox = None
        self.usb_auto_reconnect_checkbox = None
        self.usb_buffer_size_spinbox = None
        self.usb_data_format_combo = None
        self.usb_retry_count_spinbox = None
        self.usb_retry_interval_spinbox = None
        self.usb_endpoint_in_spinbox = None
        self.usb_endpoint_out_spinbox = None
        
        # 传输设置控件
        self.protocol_combo = None
        self.max_errors_spinbox = None
        
        # 图像设置控件
        self.image_quality_slider = None
        self.quality_label = None
        self.auto_resize_checkbox = None
        self.max_width_spinbox = None
        self.max_height_spinbox = None
        self.processing_mode_combo = None
        self.dithering_combo = None

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 创建标签页
        tab_widget = QTabWidget()

        # 添加各个设置页面
        tab_widget.addTab(self.create_general_tab(), "常规设置")
        tab_widget.addTab(self.create_serial_tab(), "串口设置")
        tab_widget.addTab(self.create_usb_tab(), "USB设置")
        tab_widget.addTab(self.create_transport_tab(), "传输设置")
        tab_widget.addTab(self.create_image_tab(), "图像设置")
        tab_widget.addTab(self.create_data_type_tab(), "数据传输类型")

        layout.addWidget(tab_widget)

        # 添加确定和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        apply_button = QPushButton("应用")

        ok_button.clicked.connect(self._on_ok_clicked)
        cancel_button.clicked.connect(self.reject)
        apply_button.clicked.connect(self._on_apply_clicked)

        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_general_tab(self):
        """创建常规设置标签页
        
        Returns:
            QWidget: 常规设置页面控件
        """
        widget = QWidget()
        layout = QVBoxLayout()

        # 应用程序设置组
        app_group = QGroupBox("应用程序设置")
        app_layout = QFormLayout()
        
        # 自动保存设置
        self.auto_save_checkbox = QCheckBox("启用自动保存")
        self.auto_save_checkbox.setToolTip("自动保存应用程序设置和工作状态")
        app_layout.addRow("自动保存:", self.auto_save_checkbox)
        
        # 主题设置
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色主题", "深色主题", "系统默认"])
        self.theme_combo.setToolTip("选择应用程序的外观主题")
        app_layout.addRow("主题:", self.theme_combo)
        
        # 语言设置
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English"])
        self.language_combo.setToolTip("选择应用程序界面语言")
        app_layout.addRow("语言:", self.language_combo)
        
        app_group.setLayout(app_layout)
        layout.addWidget(app_group)
        
        # 启动设置组
        startup_group = QGroupBox("启动设置")
        startup_layout = QFormLayout()
        
        # 启动时恢复上次会话
        self.restore_session_checkbox = QCheckBox("恢复上次会话")
        self.restore_session_checkbox.setToolTip("启动时恢复上次关闭时的工作状态")
        startup_layout.addRow("会话恢复:", self.restore_session_checkbox)
        
        # 启动时检查更新
        self.check_updates_checkbox = QCheckBox("检查更新")
        self.check_updates_checkbox.setToolTip("启动时自动检查软件更新")
        startup_layout.addRow("更新检查:", self.check_updates_checkbox)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def load_settings(self):
        """加载设置"""
        # 加载常规设置
        self.auto_save_checkbox.setChecked(
            self.settings.value('general/auto_save', True, type=bool)
        )
        self.theme_combo.setCurrentText(
            self.settings.value('general/theme', '浅色主题', type=str)
        )
        self.language_combo.setCurrentText(
            self.settings.value('general/language', '简体中文', type=str)
        )
        self.restore_session_checkbox.setChecked(
            self.settings.value('general/restore_session', True, type=bool)
        )
        self.check_updates_checkbox.setChecked(
            self.settings.value('general/check_updates', True, type=bool)
        )
        
        # 加载串口设置
        self.default_baudrate_combo.setCurrentText(
            self.settings.value('serial/default_baudrate', '115200', type=str)
        )
        # 确保从设置中加载整数类型的数据位，然后转换为字符串
        data_bits = self.settings.value('serial/data_bits', 8, type=int)
        self.data_bits_combo.setCurrentText(str(data_bits))
        # 加载校验位设置并转换为中文显示
        parity_char = self.settings.value('serial/parity', 'N', type=str)
        parity_text = self.CHAR_TO_PARITY.get(parity_char, '无')  # 默认为'无'
        self.parity_combo.setCurrentText(parity_text)
        self.stop_bits_combo.setCurrentText(
            self.settings.value('serial/stop_bits', '1', type=str)
        )
        # 加载流控制设置
        self.xonxoff_checkbox.setChecked(
            self.settings.value('serial/xonxoff', False, type=bool)
        )
        self.rtscts_checkbox.setChecked(
            self.settings.value('serial/rtscts', False, type=bool)
        )
        self.dsrdtr_checkbox.setChecked(
            self.settings.value('serial/dsrdtr', False, type=bool)
        )
        self.read_timeout_spinbox.setValue(
            self.settings.value('serial/read_timeout', 0.001, type=float)
        )
        self.write_timeout_spinbox.setValue(
            self.settings.value('serial/write_timeout', 0.001, type=float)
        )
        self.auto_reconnect_checkbox.setChecked(
            self.settings.value('serial/auto_reconnect', False, type=bool)
        )
        self.retry_count_spinbox.setValue(
            self.settings.value('serial/retry_count', 3, type=int)
        )
        self.retry_interval_spinbox.setValue(
            self.settings.value('serial/retry_interval', 2, type=int)
        )
        self.buffer_size_spinbox.setValue(
            self.settings.value('serial/buffer_size', 4096, type=int)
        )
        self.data_format_combo.setCurrentText(
            self.settings.value('serial/data_format', '十六进制', type=str)
        )
        
        # 加载USB设置
        self.usb_vendor_id_edit.setText(
            self.settings.value('usb/vendor_id', '', type=str)
        )
        self.usb_product_id_edit.setText(
            self.settings.value('usb/product_id', '', type=str)
        )
        self.usb_endpoint_in_spinbox.setValue(
            self.settings.value('usb/endpoint_in', 1, type=int)
        )
        self.usb_endpoint_out_spinbox.setValue(
            self.settings.value('usb/endpoint_out', 2, type=int)
        )
        self.usb_timeout_spinbox.setValue(
            self.settings.value('usb/timeout', 5, type=int)
        )
        self.usb_auto_reconnect_checkbox.setChecked(
            self.settings.value('usb/auto_reconnect', False, type=bool)
        )
        self.usb_retry_count_spinbox.setValue(
            self.settings.value('usb/retry_count', 3, type=int)
        )
        self.usb_retry_interval_spinbox.setValue(
            self.settings.value('usb/retry_interval', 2, type=int)
        )
        self.usb_buffer_size_spinbox.setValue(
            self.settings.value('usb/buffer_size', 8192, type=int)
        )
        self.usb_data_format_combo.setCurrentText(
            self.settings.value('usb/data_format', '十六进制', type=str)
        )
        
        # 加载传输设置
        protocol_index = self.settings.value('transport/protocol_index', 0, type=int)
        if 0 <= protocol_index < self.protocol_combo.count():
            self.protocol_combo.setCurrentIndex(protocol_index)
        
        self.max_errors_spinbox.setValue(
            self.settings.value('transport/max_errors', 10, type=int)
        )
        
        # 加载图像设置（仅保留处理相关参数）
        
        # 加载图像处理参数
        threshold = self.settings.value('image/threshold', 128, type=int)
        self.threshold_slider.setValue(threshold)
        self.threshold_label.setText(str(threshold))
        
        self.clear_background_checkbox.setChecked(
            self.settings.value('image/clear_background', False, type=bool)
        )
        self.dithering_combo.setCurrentText(
            self.settings.value('image/dithering', 'Floyd-Steinberg', type=str)
        )
        self.compress_checkbox.setChecked(
            self.settings.value('image/compress', True, type=bool)
        )
        self.flip_horizontally_checkbox.setChecked(
            self.settings.value('image/flip_horizontally', False, type=bool)
        )
        self.row_layout_direction_combo.setCurrentText(
            self.settings.value('image/row_layout_direction', '垂直方向', type=str)
        )

        data_type = self.settings.value('data/type', 0, type=int)
        if data_type == 0:
            self.print_data_radio.setChecked(True)
        elif data_type == 1:
            self.logo_data_radio.setChecked(True)
        elif data_type == 2:
            self.ota_data_radio.setChecked(True)
    
    def save_settings(self):
        """保存设置"""
        # 保存常规设置
        self.settings.setValue('general/auto_save', self.auto_save_checkbox.isChecked())
        self.settings.setValue('general/theme', self.theme_combo.currentText())
        self.settings.setValue('general/language', self.language_combo.currentText())
        self.settings.setValue('general/restore_session', self.restore_session_checkbox.isChecked())
        self.settings.setValue('general/check_updates', self.check_updates_checkbox.isChecked())
        
        # 保存串口设置
        self.settings.setValue('serial/default_baudrate', self.default_baudrate_combo.currentText())
        self.settings.setValue('serial/data_bits', int(self.data_bits_combo.currentText()))
        # 转换奇偶校验值：从中文转换为字符
        parity = self.parity_combo.currentText()
        parity_char = self.PARITY_TO_CHAR.get(parity, 'N')  # 默认为'N'
        self.settings.setValue('serial/parity', parity_char)
        self.settings.setValue('serial/stop_bits', self.stop_bits_combo.currentText())
        # 保存流控制设置
        self.settings.setValue('serial/xonxoff', self.xonxoff_checkbox.isChecked())
        self.settings.setValue('serial/rtscts', self.rtscts_checkbox.isChecked())
        self.settings.setValue('serial/dsrdtr', self.dsrdtr_checkbox.isChecked())
        self.settings.setValue('serial/read_timeout', float(self.read_timeout_spinbox.value()))
        self.settings.setValue('serial/write_timeout', float(self.write_timeout_spinbox.value()))
        self.settings.setValue('serial/auto_reconnect', self.auto_reconnect_checkbox.isChecked())
        self.settings.setValue('serial/retry_count', self.retry_count_spinbox.value())
        self.settings.setValue('serial/retry_interval', self.retry_interval_spinbox.value())
        self.settings.setValue('serial/buffer_size', self.buffer_size_spinbox.value())
        self.settings.setValue('serial/data_format', self.data_format_combo.currentText())
        
        # 保存USB设置
        self.settings.setValue('usb/vendor_id', self.usb_vendor_id_edit.text())
        self.settings.setValue('usb/product_id', self.usb_product_id_edit.text())
        self.settings.setValue('usb/endpoint_in', self.usb_endpoint_in_spinbox.value())
        self.settings.setValue('usb/endpoint_out', self.usb_endpoint_out_spinbox.value())
        self.settings.setValue('usb/timeout', self.usb_timeout_spinbox.value())
        self.settings.setValue('usb/auto_reconnect', self.usb_auto_reconnect_checkbox.isChecked())
        self.settings.setValue('usb/retry_count', self.usb_retry_count_spinbox.value())
        self.settings.setValue('usb/retry_interval', self.usb_retry_interval_spinbox.value())
        self.settings.setValue('usb/buffer_size', self.usb_buffer_size_spinbox.value())
        self.settings.setValue('usb/data_format', self.usb_data_format_combo.currentText())
        
        # 保存传输设置
        self.settings.setValue('transport/protocol_index', self.protocol_combo.currentIndex())
        self.settings.setValue('transport/max_errors', self.max_errors_spinbox.value())
        
        # 保存图像设置（仅保留处理相关参数）
        
        # 保存图像处理参数
        self.settings.setValue('image/threshold', self.threshold_slider.value())
        self.settings.setValue('image/clear_background', self.clear_background_checkbox.isChecked())
        self.settings.setValue('image/dithering', self.dithering_combo.currentText())
        self.settings.setValue('image/compress', self.compress_checkbox.isChecked())
        self.settings.setValue('image/flip_horizontally', self.flip_horizontally_checkbox.isChecked())
        self.settings.setValue('image/row_layout_direction', self.row_layout_direction_combo.currentText())

        # 数据类型设置
        if self.print_data_radio.isChecked():
            self.settings.setValue('data/type', 0)
        elif self.logo_data_radio.isChecked():
            self.settings.setValue('data/type', 1)
        elif self.ota_data_radio.isChecked():
            self.settings.setValue('data/type', 2)
        
        # 同步设置到磁盘
        self.settings.sync()
    
    def _on_ok_clicked(self):
        """确定按钮点击事件"""
        self.save_settings()
        self.accept()
    
    def _on_apply_clicked(self):
        """应用按钮点击事件"""
        self.save_settings()
    
    @staticmethod
    def get_setting(key, default_value=None, value_type=str):
        """获取设置值
        
        Args:
            key (str): 设置键名
            default_value: 默认值
            value_type: 值类型
            
        Returns:
            设置值
        """
        settings = QSettings('RBQ', 'EdenxPrinter')
        return settings.value(key, default_value, type=value_type)
    
    @staticmethod
    def set_setting(key, value):
        """设置值
        
        Args:
            key (str): 设置键名
            value: 设置值
        """
        settings = QSettings('RBQ', 'EdenxPrinter')
        settings.setValue(key, value)
        settings.sync()

    def create_serial_tab(self):
        """创建串口设置标签页
        
        Returns:
            QWidget: 串口设置页面控件
        """
        widget = QWidget()
        layout = QVBoxLayout()

        # 串口连接设置组
        connection_group = QGroupBox("连接设置")
        connection_layout = QFormLayout()
        
        # 默认波特率
        self.default_baudrate_combo = QComboBox()
        self.default_baudrate_combo.addItems([
            "1200", "2400", "4800", "9600", "14400", "19200", 
            "28800", "38400", "57600", "115200", "128000", 
            "230400", "256000", "460800", "500000", "921600", 
            "1000000", "1500000", "2000000"
        ])
        self.default_baudrate_combo.setCurrentText("115200")
        self.default_baudrate_combo.setToolTip("设置串口通信的默认波特率")
        connection_layout.addRow("默认波特率:", self.default_baudrate_combo)
        
        # 数据位
        self.data_bits_combo = QComboBox()
        self.data_bits_combo.addItems(["5", "6", "7", "8"])
        self.data_bits_combo.setCurrentText("8")
        self.data_bits_combo.setToolTip("设置串口通信的数据位数")
        connection_layout.addRow("数据位:", self.data_bits_combo)
        
        # 校验位
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["无", "奇校验", "偶校验", "标记", "空格"])
        self.parity_combo.setCurrentText("无")
        self.parity_combo.setToolTip("设置串口通信的校验位")
        connection_layout.addRow("校验位:", self.parity_combo)
        
        # 停止位
        self.stop_bits_combo = QComboBox()
        self.stop_bits_combo.addItems(["1", "1.5", "2"])
        self.stop_bits_combo.setCurrentText("1")
        self.stop_bits_combo.setToolTip("设置串口通信的停止位数")
        connection_layout.addRow("停止位:", self.stop_bits_combo)
        
        # 流控制组
        flow_control_group = QGroupBox("流控制")
        flow_layout = QVBoxLayout()
        
        # 软件流控制 (XON/XOFF)
        self.xonxoff_checkbox = QCheckBox("XON/XOFF (软件流控)")
        self.xonxoff_checkbox.setToolTip("启用软件流控制 (XON/XOFF)")
        
        # 硬件流控制 (RTS/CTS)
        self.rtscts_checkbox = QCheckBox("RTS/CTS (硬件流控)")
        self.rtscts_checkbox.setToolTip("启用硬件流控制 (RTS/CTS)")
        
        # 硬件流控制 (DSR/DTR)
        self.dsrdtr_checkbox = QCheckBox("DSR/DTR (硬件流控)")
        self.dsrdtr_checkbox.setToolTip("启用硬件流控制 (DSR/DTR)")
        
        flow_layout.addWidget(self.xonxoff_checkbox)
        flow_layout.addWidget(self.rtscts_checkbox)
        flow_layout.addWidget(self.dsrdtr_checkbox)
        
        flow_control_group.setLayout(flow_layout)
        connection_layout.addRow("", flow_control_group)
        
        # 读超时设置
        self.read_timeout_spinbox = QDoubleSpinBox()
        self.read_timeout_spinbox.setRange(0.001, 3.0)
        self.read_timeout_spinbox.setValue(0.05)
        self.read_timeout_spinbox.setDecimals(3)
        self.read_timeout_spinbox.setSingleStep(0.001)
        self.read_timeout_spinbox.setSuffix(" 秒")
        self.read_timeout_spinbox.setToolTip("设置串口通信读超时时间")
        connection_layout.addRow("读超时时间:", self.read_timeout_spinbox)
        
        # 写超时设置
        self.write_timeout_spinbox = QDoubleSpinBox()
        self.write_timeout_spinbox.setRange(0.001, 3.0)
        self.write_timeout_spinbox.setValue(0.05)
        self.write_timeout_spinbox.setDecimals(3)
        self.write_timeout_spinbox.setSingleStep(0.001)
        self.write_timeout_spinbox.setSuffix(" 秒")
        self.write_timeout_spinbox.setToolTip("设置串口通信写超时时间")
        connection_layout.addRow("写超时时间:", self.write_timeout_spinbox)
        
        # 自动重连
        self.auto_reconnect_checkbox = QCheckBox("启用自动重连")
        self.auto_reconnect_checkbox.setToolTip("连接断开时自动尝试重新连接")
        connection_layout.addRow("自动重连:", self.auto_reconnect_checkbox)
        
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)
        
        # 重连设置组
        retry_group = QGroupBox("重连设置")
        retry_layout = QFormLayout()
        
        # 重试次数
        self.retry_count_spinbox = QSpinBox()
        self.retry_count_spinbox.setRange(1, 10)
        self.retry_count_spinbox.setValue(3)
        self.retry_count_spinbox.setToolTip("设置连接失败时的重试次数")
        retry_layout.addRow("重试次数:", self.retry_count_spinbox)
        
        # 重试间隔
        self.retry_interval_spinbox = QSpinBox()
        self.retry_interval_spinbox.setRange(1, 30)
        self.retry_interval_spinbox.setValue(2)
        self.retry_interval_spinbox.setSuffix(" 秒")
        self.retry_interval_spinbox.setToolTip("设置重试之间的间隔时间")
        retry_layout.addRow("重试间隔:", self.retry_interval_spinbox)
        
        retry_group.setLayout(retry_layout)
        layout.addWidget(retry_group)
        
        # 数据处理设置组
        data_group = QGroupBox("数据处理")
        data_layout = QFormLayout()
        
        # 数据缓冲区大小
        self.buffer_size_spinbox = QSpinBox()
        self.buffer_size_spinbox.setRange(1024, 65536)
        self.buffer_size_spinbox.setValue(4096)
        self.buffer_size_spinbox.setSuffix(" 字节")
        self.buffer_size_spinbox.setToolTip("设置串口数据缓冲区大小")
        data_layout.addRow("缓冲区大小:", self.buffer_size_spinbox)
        
        # 数据格式
        self.data_format_combo = QComboBox()
        self.data_format_combo.addItems(["十六进制", "ASCII", "UTF-8"])
        self.data_format_combo.setToolTip("设置数据显示格式")
        data_layout.addRow("数据格式:", self.data_format_combo)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_usb_tab(self):
        """创建USB设置标签页
        
        Returns:
            QWidget: USB设置页面控件
        """
        widget = QWidget()
        layout = QVBoxLayout()

        # USB设备识别设置组
        device_group = QGroupBox("设备识别")
        device_layout = QFormLayout()
        
        # 厂商ID
        self.usb_vendor_id_edit = QLineEdit()
        self.usb_vendor_id_edit.setPlaceholderText("例如: 0x1234")
        self.usb_vendor_id_edit.setToolTip("设置USB设备的厂商ID (十六进制格式)")
        device_layout.addRow("厂商ID (VID):", self.usb_vendor_id_edit)
        
        # 产品ID
        self.usb_product_id_edit = QLineEdit()
        self.usb_product_id_edit.setPlaceholderText("例如: 0x5678")
        self.usb_product_id_edit.setToolTip("设置USB设备的产品ID (十六进制格式)")
        device_layout.addRow("产品ID (PID):", self.usb_product_id_edit)
        
        # 输入端点
        self.usb_endpoint_in_spinbox = QSpinBox()
        self.usb_endpoint_in_spinbox.setRange(1, 15)
        self.usb_endpoint_in_spinbox.setValue(1)
        self.usb_endpoint_in_spinbox.setToolTip("设置USB输入端点地址")
        device_layout.addRow("输入端点:", self.usb_endpoint_in_spinbox)
        
        # 输出端点
        self.usb_endpoint_out_spinbox = QSpinBox()
        self.usb_endpoint_out_spinbox.setRange(1, 15)
        self.usb_endpoint_out_spinbox.setValue(2)
        self.usb_endpoint_out_spinbox.setToolTip("设置USB输出端点地址")
        device_layout.addRow("输出端点:", self.usb_endpoint_out_spinbox)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # USB连接设置组
        connection_group = QGroupBox("连接设置")
        connection_layout = QFormLayout()
        
        # 超时设置
        self.usb_timeout_spinbox = QSpinBox()
        self.usb_timeout_spinbox.setRange(1, 60)
        self.usb_timeout_spinbox.setValue(5)
        self.usb_timeout_spinbox.setSuffix(" 秒")
        self.usb_timeout_spinbox.setToolTip("设置USB通信超时时间")
        connection_layout.addRow("超时时间:", self.usb_timeout_spinbox)
        
        # 自动重连
        self.usb_auto_reconnect_checkbox = QCheckBox("启用自动重连")
        self.usb_auto_reconnect_checkbox.setToolTip("USB设备断开时自动尝试重新连接")
        connection_layout.addRow("自动重连:", self.usb_auto_reconnect_checkbox)
        
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)
        
        # USB重连设置组
        retry_group = QGroupBox("重连设置")
        retry_layout = QFormLayout()
        
        # 重试次数
        self.usb_retry_count_spinbox = QSpinBox()
        self.usb_retry_count_spinbox.setRange(1, 10)
        self.usb_retry_count_spinbox.setValue(3)
        self.usb_retry_count_spinbox.setToolTip("设置USB连接失败时的重试次数")
        retry_layout.addRow("重试次数:", self.usb_retry_count_spinbox)
        
        # 重试间隔
        self.usb_retry_interval_spinbox = QSpinBox()
        self.usb_retry_interval_spinbox.setRange(1, 30)
        self.usb_retry_interval_spinbox.setValue(2)
        self.usb_retry_interval_spinbox.setSuffix(" 秒")
        self.usb_retry_interval_spinbox.setToolTip("设置USB重试之间的间隔时间")
        retry_layout.addRow("重试间隔:", self.usb_retry_interval_spinbox)
        
        retry_group.setLayout(retry_layout)
        layout.addWidget(retry_group)
        
        # USB数据处理设置组
        data_group = QGroupBox("数据处理")
        data_layout = QFormLayout()
        
        # 数据缓冲区大小
        self.usb_buffer_size_spinbox = QSpinBox()
        self.usb_buffer_size_spinbox.setRange(1024, 65536)
        self.usb_buffer_size_spinbox.setValue(8192)
        self.usb_buffer_size_spinbox.setSuffix(" 字节")
        self.usb_buffer_size_spinbox.setToolTip("设置USB数据缓冲区大小")
        data_layout.addRow("缓冲区大小:", self.usb_buffer_size_spinbox)
        
        # 数据格式
        self.usb_data_format_combo = QComboBox()
        self.usb_data_format_combo.addItems(["十六进制", "ASCII", "UTF-8"])
        self.usb_data_format_combo.setToolTip("设置USB数据显示格式")
        data_layout.addRow("数据格式:", self.usb_data_format_combo)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_transport_tab(self):
        """创建传输设置标签页
        
        Returns:
            QWidget: 传输设置页面控件
        """
        widget = QWidget()
        layout = QVBoxLayout()

        # 传输协议设置组
        protocol_group = QGroupBox("传输协议")
        protocol_layout = QFormLayout()
        
        # 协议选择
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems([
            "SOH - 128字节 (0x18)",
            "STX - 512字节 (0x19)",
            "STX_A - 1KB (0x1A)",
            "STX_B - 2KB (0x1B)",
            "STX_C - 5KB (0x1C)",
            "STX_D - 10KB (0x1D)",
            "STX_E - 124字节 (0x1E)"
        ])
        self.protocol_combo.setCurrentIndex(0)  # 默认选择SOH
        self.protocol_combo.setToolTip("选择数据传输协议")
        protocol_layout.addRow("传输协议:", self.protocol_combo)
        
        # 最大错误包数
        self.max_errors_spinbox = QSpinBox()
        self.max_errors_spinbox.setRange(1, 30)
        self.max_errors_spinbox.setValue(10)  # 默认值10，与protocol.py中的MAX_ERRORS一致
        self.max_errors_spinbox.setToolTip("设置最大错误（无应答）包数")
        protocol_layout.addRow("最大错误包数:", self.max_errors_spinbox)
        
        protocol_group.setLayout(protocol_layout)
        layout.addWidget(protocol_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_image_tab(self):
        """创建图像设置标签页
        
        Returns:
            QWidget: 图像设置页面控件
        """
        widget = QWidget()
        layout = QVBoxLayout()

        # 图像处理设置组
        processing_group = QGroupBox("图像处理")
        processing_layout = QFormLayout()
        
        # 二值化阈值
        threshold_layout_h = QHBoxLayout()
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 255)
        self.threshold_slider.setValue(128)
        self.threshold_slider.setToolTip("设置二值化阈值 (0-255)")
        
        self.threshold_label = QLabel("128")
        self.threshold_slider.valueChanged.connect(
            lambda v: self.threshold_label.setText(str(v))
        )
        
        threshold_layout_h.addWidget(self.threshold_slider)
        threshold_layout_h.addWidget(self.threshold_label)
        processing_layout.addRow("二值化阈值:", threshold_layout_h)
        
        # 清除背景
        self.clear_background_checkbox = QCheckBox("启用背景清除")
        self.clear_background_checkbox.setToolTip("清除图像背景")
        processing_layout.addRow("背景清除:", self.clear_background_checkbox)
        
        # 抖动算法
        self.dithering_combo = QComboBox()
        self.dithering_combo.addItems([
            "Floyd-Steinberg", "无"
        ])
        self.dithering_combo.setCurrentText("Floyd-Steinberg")
        self.dithering_combo.setToolTip("选择图像抖动算法")
        processing_layout.addRow("抖动算法:", self.dithering_combo)
        
        # 数据压缩
        self.compress_checkbox = QCheckBox("启用数据压缩")
        self.compress_checkbox.setChecked(True)
        self.compress_checkbox.setToolTip("压缩打印数据以提高传输效率")
        processing_layout.addRow("数据压缩:", self.compress_checkbox)
        
        # 水平翻转
        self.flip_horizontally_checkbox = QCheckBox("水平翻转")
        self.flip_horizontally_checkbox.setToolTip("水平翻转图像")
        processing_layout.addRow("水平翻转:", self.flip_horizontally_checkbox)
        
        # 行布局方向
        self.row_layout_direction_combo = QComboBox()
        self.row_layout_direction_combo.addItems([
            "垂直方向", "水平方向"
        ])
        self.row_layout_direction_combo.setCurrentText("垂直方向")
        self.row_layout_direction_combo.setToolTip("设置行图像的排列方向")
        processing_layout.addRow("行布局方向:", self.row_layout_direction_combo)
        
        processing_group.setLayout(processing_layout)
        layout.addWidget(processing_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_data_type_tab(self):
        """创建数据类型设置标签页"""

        widget = QWidget()
        layout = QVBoxLayout()

        # 数据类型设置组（唯一的 QGroupBox）
        data_type_group = QGroupBox("数据传输类型")
        group_layout = QVBoxLayout()

        # 打印数据单选按钮
        self.print_data_radio = QRadioButton("打印数据")
        self.print_data_radio.setChecked(True)
        self.print_data_radio.setToolTip("选择打印数据类型")

        # Logo 数据单选按钮
        self.logo_data_radio = QRadioButton("Logo数据")
        self.logo_data_radio.setToolTip("选择Logo数据类型")

        # OTA 数据单选按钮
        self.ota_data_radio = QRadioButton("OTA数据")
        self.ota_data_radio.setToolTip("选择OTA数据类型")

        # 添加到组布局
        group_layout.addWidget(self.print_data_radio)
        group_layout.addWidget(self.logo_data_radio)
        group_layout.addWidget(self.ota_data_radio)

        data_type_group.setLayout(group_layout)
        layout.addWidget(data_type_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

        
    def show(self):
        """显示设置对话框"""
        return self.exec()