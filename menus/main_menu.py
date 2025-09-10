from PyQt5.QtWidgets import QMenuBar, QAction, QMenu, QMessageBox
from style.styles import MENU_STYLE
from dialogs.about_dialog import AboutDialog

class MainMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # 设置菜单栏样式
        self.setStyleSheet(MENU_STYLE)

        # 创建菜单
        self.create_menus()

    def create_menus(self):
        """创建所有菜单"""
        self.create_file_menu()
        self.create_help_menu()

    def create_file_menu(self):
        """创建文件菜单"""
        file_menu = self.addMenu('文件')

        # 设置动作
        settings_action = QAction('设置', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.parent.show_settings)

        # 退出动作
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.parent.confirm_exit)

        # 添加到文件菜单
        file_menu.addAction(settings_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

    def create_help_menu(self):
        """创建帮助菜单"""
        help_menu = self.addMenu('帮助')

        # 关于动作
        about_action = QAction('关于', self)
        about_action.triggered.connect(lambda: AboutDialog.show_about(self.parent))
        help_menu.addAction(about_action)