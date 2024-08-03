from PyQt5.QtWidgets import QVBoxLayout, QDialog, QLabel, QTextEdit, QComboBox, QFormLayout, QDialogButtonBox
from PyQt5.QtCore import *
from internation import HAN_EN

class PrologForm(QDialog):

    def __init__(self, title = "Prolog", content = ''):
        super(PrologForm, self).__init__()
        self.setWindowTitle(title)
        self.resize(800, 300)
        self.initUI()
        self.initUIData(content)
        self.connSlot()

    def initUIData(self, content):
        if content == '' or content == False:
            with open('../resource/prolog.txt', 'r', encoding='utf-8') as f:
                content = f.read()
        self.contentEdit.setText(content)

    def initUI(self):
        #  Enter information 
        contentLabel = QLabel(HAN_EN.get('Content'))
        self.switchLabel = QLabel(HAN_EN.get('Replication node'))
        self.quotesSwitchLabel = QLabel(HAN_EN.get('Statement in quotation marks'))

        self.contentEdit = QTextEdit()
        self.switchComBox = QComboBox()
        self.switchComBox.addItems([HAN_EN.get('No'), HAN_EN.get('Yes')])
        self.quotesSwitchComBox = QComboBox()
        self.quotesSwitchComBox.addItems([HAN_EN.get('No'), HAN_EN.get('Yes')])

        formLayout = QFormLayout()
        formLayout.addRow(contentLabel, self.contentEdit)
        formLayout.addRow(self.switchLabel, self.switchComBox)
        formLayout.addRow(self.quotesSwitchLabel, self.quotesSwitchComBox)

        #  Use two button(ok and cancel) Connect separately accept() and reject() Slot function 
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        #  layout 
        vbox = QVBoxLayout()
        vbox.addLayout(formLayout)
        vbox.addWidget(buttons)

        self.setLayout(vbox)

    def connSlot(self):
        # self.btnAdd.clicked.connect(self.btnAddOnClick)
        pass

    def initExportUI(self):
        self.switchLabel.setVisible(False)
        self.switchComBox.setVisible(False)
        self.quotesSwitchLabel.setVisible(False)
        self.quotesSwitchComBox.setVisible(False)
        self.contentEdit.setReadOnly(True)
        self.contentEdit.setStyleSheet('background:#DDDDDD')

    def getContent(self):
        return self.contentEdit.toPlainText()

    def getSwitch(self):
        return self.switchComBox.currentText()

    def getQuotesSwitch(self):
        return self.quotesSwitchComBox.currentText()
