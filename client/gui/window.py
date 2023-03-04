import ctypes

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QMainWindow

from client.gui.article_window import ArticleWindow


class CustomWebEnginePage(QWebEnginePage):
    external_windows = []

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            w = ArticleWindow(url)
            w.show()

            self.external_windows.append(w)
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'andrew264.news_summarizer.0.1.0')
        self.setWindowTitle('News Summarizer')
        self.setWindowIcon(QIcon('client/static/images/icon.png'))
        self.setGeometry(100, 100, 1920, 1080)

        self.web_view = QWebEngineView(self)
        self.web_view.setPage(CustomWebEnginePage(self))

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(44, 46, 53))
        self.setPalette(palette)

        # Set the web view as the central widget
        self.setCentralWidget(self.web_view)

    def load_flask(self):
        self.web_view.load(QUrl('http://localhost:5420'))

        self.show()
