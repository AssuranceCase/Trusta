from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import history
from internation import HAN_EN

class AdditionForm(QDialog):

    def __init__(self, ID=None, Type=None):
        super(AdditionForm, self).__init__()
        self.setWindowTitle("Add Addition")
        self.resize(970, 200)
        self.ID = ID
        self.Type = Type
        self.initUI()
        self.initUIData()
        self.connSlot()

    def initUIData(self):
        if self.ID:
            self.IDEdit.setText(str(self.ID))
        if self.Type:
            self.typeComBox.setCurrentText(HAN_EN.get(self.Type))

    def initUI(self):
        #  Enter information 
        IDLabel = QLabel(HAN_EN.get('ID'))
        typeLabel = QLabel(HAN_EN.get('Type'))
        contentLabel = QLabel(HAN_EN.get('Content'))

        
        self.IDEdit = QLineEdit()
        # self.IDEdit.setPlaceholderText(HAN_EN.get("1,2,3"))

        self.typeComBox = QComboBox()
        self.typeComBox.addItems([HAN_EN.get('Context'),
                                  HAN_EN.get('Assumption'),
                                  HAN_EN.get('Justification'),
                                  HAN_EN.get('Strategy')
                                  ])

        self.contentEdit = QTextEdit()

        formLayout = QFormLayout()
        formLayout.addRow(IDLabel, self.IDEdit)
        formLayout.addRow(typeLabel, self.typeComBox)
        formLayout.addRow(contentLabel, self.contentEdit)

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

        # Apply a stylesheet to the entire dialog
        self.setStyleSheet("""
            QPushButton {
                background: #448aff;
                color: white;
                font-weight: 800;
            }
        """)

    def connSlot(self):
        pass

    def getID(self):
        return self.IDEdit.text()

    def getType(self):
        return self.typeComBox.currentText()

    def getContent(self):
        return self.contentEdit.toPlainText()

