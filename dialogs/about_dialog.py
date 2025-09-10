from PyQt5.QtWidgets import QMessageBox
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关于对话框模块

作者: RBQ
版本: 1.0.0
Python版本: 3.9+
"""

import sys
import platform
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5.QtGui import QIcon


class AboutDialog:
    @staticmethod
    def show_about(parent=None):
        """显示关于对话框
        
        显示应用程序的详细信息，包括版本、作者、系统信息等。
        
        Args:
            parent: 父窗口实例，用于设置对话框的父级
        """
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 获取系统信息
        system_info = AboutDialog._get_system_info()
        
        # 构建关于信息
        about_text = AboutDialog._build_about_text(current_time, system_info)
        
        # 显示关于对话框
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle("关于 EdenxPrinter")
        msg_box.setText(about_text)
        msg_box.setIcon(QMessageBox.Information)
        
        # 设置详细信息
        detailed_info = AboutDialog._build_detailed_info(system_info)
        msg_box.setDetailedText(detailed_info)
        
        msg_box.exec_()
    
    @staticmethod
    def _get_system_info():
        """获取系统信息
        
        Returns:
            dict: 包含系统信息的字典
        """
        return {
            'python_version': sys.version.split()[0],
            'platform': platform.platform(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor() or platform.machine(),
            'qt_version': QT_VERSION_STR,
            'pyqt_version': PYQT_VERSION_STR
        }
    
    @staticmethod
    def _build_about_text(current_time, system_info):
        """构建关于文本
        
        Args:
            current_time (str): 当前时间字符串
            system_info (dict): 系统信息字典
            
        Returns:
            str: 格式化的关于文本
        """
        return (
            "<h2>🖨️ EdenxPrinter</h2>"
            "<p><b>版本:</b> 1.0.0</p>"
            "<p><b>作者:</b> RBQ</p>"
            "<p><b>构建时间:</b> {}</p>"
            "<br>"
            "<p><b>描述:</b></p>"
            "<p>一个功能强大的图像处理与设备通讯上位机软件，"
            "支持多种打印设备的连接和控制。</p>"
            "<br>"
            "<p><b>主要功能:</b></p>"
            "<ul>"
            "<li>📷 图像处理与预览</li>"
            "<li>🔌 USB/串口设备连接</li>"
            "<li>📊 实时数据监控</li>"
            "<li>⚙️ 设备参数配置</li>"
            "</ul>"
        ).format(current_time)
    
    @staticmethod
    def _build_detailed_info(system_info):
        """构建详细信息
        
        Args:
            system_info (dict): 系统信息字典
            
        Returns:
            str: 格式化的详细信息文本
        """
        return (
            "=== 系统信息 ===\n"
            f"Python版本: {system_info['python_version']}\n"
            f"操作系统: {system_info['platform']}\n"
            f"系统架构: {system_info['architecture']}\n"
            f"处理器: {system_info['processor']}\n\n"
            "=== 框架信息 ===\n"
            f"Qt版本: {system_info['qt_version']}\n"
            f"PyQt版本: {system_info['pyqt_version']}\n\n"
            "=== 许可证信息 ===\n"
            "本软件基于MIT许可证发布\n"
            "Copyright (c) 2024 RBQ\n\n"
            "=== 联系方式 ===\n"
            "如有问题或建议，请联系开发者。"
        )