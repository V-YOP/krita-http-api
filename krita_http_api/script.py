import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QTextEdit

class FloatableMainWindow(QMainWindow):
    """自定义的QMainWindow，用于承载浮动的QDockWidget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Floating Dock Window')
        self.setGeometry(150, 150, 400, 300)
        
        # 设置为无框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

    def addDockWidget(self, area, dockwidget):
        """添加QDockWidget并连接关闭信号"""
        super().addDockWidget(area, dockwidget)
        dockwidget.visibilityChanged.connect(self.check_for_docks)  

    def check_for_docks(self):
        """检查是否还有QDockWidget，如果没有则关闭窗口"""
        docks = self.findChildren(QDockWidget)
        if not any(d.isVisible() and not d.isFloating() for d in docks):
            self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 800, 600)

        # 创建主中央小部件
        central_widget = QTextEdit()
        self.setCentralWidget(central_widget)

        # 创建两个Dock Widget
        self.dock1 = QDockWidget('Dock 1', self)
        self.dock1.setWidget(QTextEdit('This is Dock 1'))
        self.dock1.setFloating(True)

        self.dock2 = QDockWidget('Dock 2', self)
        self.dock2.setWidget(QTextEdit('This is Dock 2'))
        self.dock2.setFloating(True)

        # 创建一个临时的无框QMainWindow
        self.floating_window = FloatableMainWindow(self)

        # 将两个Dock Widget添加到临时的QMainWindow中
        self.floating_window.addDockWidget(Qt.LeftDockWidgetArea, self.dock1)
        self.floating_window.addDockWidget(Qt.LeftDockWidgetArea, self.dock2)

        # 合并两个Dock Widget
        self.floating_window.tabifyDockWidget(self.dock1, self.dock2)

        # 显示临时的QMainWindow
        self.floating_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
