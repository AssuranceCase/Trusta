from PyQt5.QtWidgets import QVBoxLayout, QDialog, QLabel, QLineEdit, QFormLayout, QDialogButtonBox
from PyQt5.QtCore import *
from internation import HAN_EN

class DelForm(QDialog):

    def __init__(self):
        super(DelForm, self).__init__()
        self.setWindowTitle(HAN_EN.get("Delete Node"))
        self.resize(350, 100)
        self.initUI()
        self.connSlot()

    def initUI(self):
        #  Enter information 
        IDLabel = QLabel(HAN_EN.get('Node ID'))
        self.IDEdit = QLineEdit()
        self.IDEdit.setPlaceholderText(HAN_EN.get("1,2,3"))

        formLayout = QFormLayout()
        formLayout.addRow(IDLabel, self.IDEdit)

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

    def getID(self):
        return self.IDEdit.text()
