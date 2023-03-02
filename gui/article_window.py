from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QMainWindow, QSplitter, QFrame, QStatusBar, QProgressBar


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
        self.set_icon()

        # Add the web view to the main layout
        self.frame = QFrame()
        self.splitter = QSplitter()
        self.splitter.setStyleSheet('QSplitter::handle { border: none; }')
        self.splitter.addWidget(self.web_view)
        self.splitter.addWidget(self.frame)
        self.setCentralWidget(self.splitter)

        # Create the status bar and progress bar
        self.status_bar = QStatusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setValue(0)
        self.status_bar.addWidget(self.progress_bar)
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.setFixedHeight(20)
        self.status_bar.setStyleSheet('QStatusBar::item { border: none; }')
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.status_bar.layout().setAlignment(self.progress_bar, Qt.AlignRight | Qt.AlignVCenter)
        self.status_bar.layout().setContentsMargins(0, 0, 0, 0)
        self.setStatusBar(self.status_bar)

        # Set the window icon and title to match the website
        self.web_view.page().titleChanged.connect(self.setWindowTitle)
        self.web_view.page().iconChanged.connect(self.setWindowIcon)

    def set_icon(self):
        # get icon from the web view's page and set it as the window's icon
        self.setWindowIcon(self.web_view.page().icon())
