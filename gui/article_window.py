from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QMainWindow, QSplitter, QFrame, QHBoxLayout


class CustomWebEnginePage(QWebEnginePage):
    external_windows = []

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)


class ArticleWindow(QMainWindow):
    def __init__(self, url: str):
        super().__init__()
        self.setWindowTitle('Article')
        self.setGeometry(100, 100, 1440, 900)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(44, 46, 53))
        self.setPalette(palette)

        self.web_view = QWebEngineView()
        self.web_view.setPage(CustomWebEnginePage(self))
        self.web_view.load(QUrl(url))

        self.frame = QFrame()
        layout = QHBoxLayout()
        layout.addWidget(self.web_view)
        self.frame.setLayout(layout)
        self.setCentralWidget(self.frame)
        width = self.width() // 2
        self.frame.setFixedSize(width, self.height())
        self.frame.move(0, 0)
        self.resizeEvent = self.resize_handler

    def resize_handler(self, event):
        size = event.size()
        width = size.width() // 2
        self.frame.setFixedSize(width, size.height())
        self.frame.move(0, 0)
        super().resizeEvent(event)
