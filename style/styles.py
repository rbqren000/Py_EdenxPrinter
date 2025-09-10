# 主窗口样式
MAIN_WINDOW_STYLE = """
    QMainWindow {
        background-color: #f0f0f0;
    }
    QLabel {
        font-size: 12px;
    }
    QGroupBox {
        font-size: 12px;
        font-weight: bold;
        border: 1px solid #bdc3c7;
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 14px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
"""

# 下拉框样式
COMBOBOX_STYLE = """
    QComboBox {
        background-color: white;
        border: 1px solid #bdc3c7;
        border-radius: 4px;
        padding: 5px;
    }
    QComboBox:hover {
        border: 1px solid #3498db;
    }
    QComboBox QAbstractItemView {
        selection-background-color: #3498db;
        selection-color: black;
    }
"""

# 调试输入框样式
DEBUG_INPUT_STYLE = """
    QLineEdit {
        border: 1px solid #bdc3c7;
        border-radius: 3px;
        padding: 4px;
        font-size: 10px;
    }
"""

# 列表控件样式
LIST_WIDGET_STYLE = """
    QListWidget {
        background-color: white;
        border: 1px solid #bdc3c7;
        border-radius: 4px;
    }
    QListWidget::item:alternate {
        background-color: #f5f6fa;
    }
    QListWidget::item:selected {
        background-color: #3498db;
        color: black;
    }
    QListWidget::item:hover {
        background-color: #e8f0fe;
    }
"""

# 表格控件样式
TABLE_WIDGET_STYLE = """
    QTableWidget {
        background-color: white;
        border: 1px solid #bdc3c7;
        border-radius: 4px;
    }
    QTableWidget::item:alternate {
        background-color: #f5f6fa;
    }
    QTableWidget::item:selected {
        background-color: #3498db;
        color: black;
    }
    QHeaderView::section {
        background-color: #2c3e50;
        color: white;
        padding: 4px;
        border: 1px solid #7f8c8d;
    }
"""

# 文本编辑器样式
TEXT_EDIT_STYLE = """
    QTextEdit {
        background-color: white;
        border: 1px solid #bdc3c7;
        border-radius: 4px;
        font-family: Consolas, Monaco, monospace;
    }
"""

# 标签样式
LABEL_STYLE = """
    QLabel {
        background-color: white;
        border: 1px solid #bdc3c7;
        border-radius: 4px;
    }
"""

# 菜单栏样式
MENU_STYLE = """
    QMenuBar {
        background-color: #f0f0f0;
        border-bottom: 1px solid #dcdcdc;
    }
    QMenuBar::item {
        padding: 4px 10px;
        background-color: transparent;
    }
    QMenuBar::item:selected {
        background-color: #e0e0e0;
    }
    QMenu {
        background-color: white;
        border: 1px solid #dcdcdc;
    }
    QMenu::item {
        padding: 5px 30px 5px 20px;
    }
    QMenu::item:selected {
        background-color: #e0e0e0;
    }
    QMenu::separator {
        height: 1px;
        background-color: #dcdcdc;
        margin: 4px 0px;
    }
"""


# 在已有的样式定义后添加

# 退出对话框样式
EXIT_DIALOG_STYLE = """
    QDialog {
        background-color: white;
        border: 1px solid #dcdcdc;
    }
"""

# 退出对话框标题样式
EXIT_DIALOG_TITLE_STYLE = """
    font-size: 16px; 
    font-weight: bold;
"""

# 退出对话框提示文本样式
EXIT_DIALOG_HINT_STYLE = """
    color: #7f8c8d;
"""

# 退出按钮样式
EXIT_BUTTON_STYLE = """
    QPushButton {
        background-color: #e74c3c;
        color: white;
        border-radius: 4px;
        padding: 6px 12px;
    }
    QPushButton:hover {
        background-color: #c0392b;
    }
    QPushButton:pressed {
        background-color: #a93226;
    }
"""

# 行编辑框样式
LINE_EDIT_STYLE = """
    QLineEdit {
        border: 1px solid #bdc3c7;
        border-radius: 3px;
        padding: 4px;
        font-size: 10px;
    }
"""