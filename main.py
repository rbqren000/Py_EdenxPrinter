#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edenx打印上位机主程序

作者: RBQ
版本: 1.0.0
Python版本: 3.9+
"""

import sys
import os

# 添加SDK路径到Python路径
sdk_path = os.path.join(os.path.dirname(__file__), 'sdk', 'python')
if sdk_path not in sys.path:
    sys.path.insert(0, sdk_path)

from PyQt5.QtWidgets import QApplication
from pages.main_window import MainWindow


def main():
    """
    主函数 - 启动应用程序
    
    Returns:
        int: 应用程序退出代码
    """
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())