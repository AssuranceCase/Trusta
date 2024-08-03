import os, sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *

class WebBox(QDialog):

    def __init__(self, title="WebBox", url=''):
        super(WebBox, self).__init__()
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.resize(1300, 800)  # Adjusted for better web view

        self.url = url
        self.initUI()

    def initUI(self):
        # Web view
        self.browser = QWebEngineView()
        self.browser.load(QUrl.fromLocalFile(self.url))

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.browser)

        self.setLayout(vbox)

def main():
    app = QApplication(sys.argv)
    web_box = WebBox(title="Test WebBox", url=os.path.abspath('app/web_view/evaluation.html')) # url It must be an absolute path 
    web_box.show() # exec_ infeasible 
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
