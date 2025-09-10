from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QSize

class CustomButton(QPushButton):
    """自定义按钮样式"""
    def __init__(self, text, icon_path=None):
        super().__init__(text)
        self.setMinimumHeight(36)
        self.setFont(QFont(QFont().family(), 10))

        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(18, 18))

        self.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)