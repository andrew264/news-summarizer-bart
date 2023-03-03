import requests
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QMainWindow, QSplitter, QSizePolicy


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

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet('QSplitter::handle { border: none; }')
        self.web_view = QWebEngineView()
        self.web_view.setPage(CustomWebEnginePage(self))
        self.web_view.load(QUrl(url))
        self.splitter.addWidget(self.web_view)
        self.set_icon()
        self.summary_view = QWebEngineView()
        self.summary_view.setPage(CustomWebEnginePage(self))
        self.splitter.addWidget(self.summary_view)
        self.update_summary(url)

        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(self.splitter)

        # Set the window icon and title to match the website
        self.web_view.page().titleChanged.connect(self.setWindowTitle)
        self.web_view.page().iconChanged.connect(self.setWindowIcon)

    def set_icon(self):
        # get icon from the web view's page and set it as the window's icon
        self.setWindowIcon(self.web_view.page().icon())

    def update_summary(self, url: QUrl | str):
        if isinstance(url, QUrl):
            url = url.url()
        req = requests.post('http://localhost:6969/', data={'url': url})

        self.summary_view.setHtml(req.text, QUrl('http://localhost:6969/'))
