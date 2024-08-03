from PyQt5.QtWidgets import QVBoxLayout, QDialog, QLabel, QTextEdit, QComboBox, QFormLayout, QDialogButtonBox
from PyQt5.QtCore import *

class TextBox(QDialog):

    def __init__(self, title = "TextBox", content = ''):
        super(TextBox, self).__init__()
        self.setWindowTitle(title)
        self.resize(800, 300)
        self.initUI()
        self.initUIData(content)
        self.connSlot()

    def initUIData(self, content):
        self.contentEdit.setText(content)

    def initUI(self):
        #  Information box 
        self.contentEdit = QTextEdit()

        #  layout 
        vbox = QVBoxLayout()
        vbox.addWidget(self.contentEdit)

        self.setLayout(vbox)

    def connSlot(self):
        # self.btnAdd.clicked.connect(self.btnAddOnClick)
        pass

    def readOnly(self):
        self.contentEdit.setReadOnly(True)
        self.contentEdit.setStyleSheet('background:#DDDDDD')

    def getContent(self):
        return self.contentEdit.toPlainText()
