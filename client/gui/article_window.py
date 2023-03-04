from urllib.parse import quote

from PyQt5.QtCore import QUrl, Qt, QByteArray
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineHttpRequest
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QMainWindow, QSplitter, QSizePolicy


class CustomWebEnginePage(QWebEnginePage):
    external_windows = []

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            w = ArticleWindow(url.toString())
            w.show()

            self.external_windows.append(w)
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
        summary_settings = self.summary_view.settings()
        summary_settings.setAttribute(summary_settings.JavascriptEnabled, True)
        self.splitter.addWidget(self.summary_view)
        self.update_summary(url)

        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(self.splitter)

        self.web_view.page().titleChanged.connect(self.setWindowTitle)

        self.web_view.page().iconChanged.connect(self.setWindowIcon)

    def set_icon(self):
        # get icon from the web view's page and set it as the window's icon
        self.setWindowIcon(self.web_view.page().icon())

    def update_summary(self, url: str | QUrl):
        SERVER_URL = 'http://localhost:6969'
        if isinstance(url, QUrl):
            url = url.toString()
        url = quote(url, safe='')
        url = f"{SERVER_URL}/?url={url}"
        self.summary_view.load(QUrl(url))
