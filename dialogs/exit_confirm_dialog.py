from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QDateTime
from pages.custom_widgets import CustomButton
from style.styles import (
    EXIT_DIALOG_STYLE,
    EXIT_DIALOG_TITLE_STYLE,
    EXIT_DIALOG_HINT_STYLE,
    EXIT_BUTTON_STYLE
)


class ExitConfirmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("确认退出")
        self.setFixedSize(400, 200)
        self.setStyleSheet(EXIT_DIALOG_STYLE)
        self.setModal(True)  # 确保是模态对话框

        # 创建布局
        layout = QVBoxLayout(self)

        # 添加当前时间和用户信息
        current_time = QDateTime.currentDateTimeUtc().toString('yyyy-MM-dd HH:mm:ss')
        info_label = QLabel(f"退出确认 - {current_time}")
        info_label.setStyleSheet(EXIT_DIALOG_HINT_STYLE)
        info_label.setAlignment(Qt.AlignCenter)

        # 添加问题文本
        question_label = QLabel("确定要退出应用程序吗？")
        question_label.setStyleSheet(EXIT_DIALOG_TITLE_STYLE)
        question_label.setAlignment(Qt.AlignCenter)

        # 添加提示文本
        hint_label = QLabel("如果有未保存的内容将会丢失。")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet(EXIT_DIALOG_HINT_STYLE)

        # 按钮布局
        buttons_layout = QHBoxLayout()
        self.exit_button = CustomButton("确认退出")
        self.cancel_button = CustomButton("取消")

        # 设置退出按钮的特殊样式
        self.exit_button.setStyleSheet(EXIT_BUTTON_STYLE)

        # 使用直接的信号连接
        self.exit_button.clicked.connect(self._handle_exit)
        self.cancel_button.clicked.connect(self._handle_cancel)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.exit_button)
        buttons_layout.addWidget(self.cancel_button)

        # 组装布局
        layout.addStretch()
        layout.addWidget(info_label)
        layout.addWidget(question_label)
        layout.addWidget(hint_label)
        layout.addStretch()
        layout.addLayout(buttons_layout)

    def _handle_exit(self):
        """处理确认退出"""
        self.done(QDialog.Accepted)

    def _handle_cancel(self):
        """处理取消退出"""
        self.done(QDialog.Rejected)