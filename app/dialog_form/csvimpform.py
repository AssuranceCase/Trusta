from PyQt5.QtWidgets import QVBoxLayout, QDialog, QLabel, QLineEdit, QPushButton, QComboBox, QFormLayout, \
    QDialogButtonBox, QHBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import *
import os
import history
from internation import HAN_EN

class CsvImpForm(QDialog):

    def __init__(self, title="Open File", list_encoding=['ansi', 'utf-8']):
        super(CsvImpForm, self).__init__()
        self.list_encoding = list_encoding
        self.setWindowTitle(title)
        self.resize(970, 200)
        self.initUI()
        self.initUIData()
        self.connSlot()

    def initUIData(self):
        if not os.path.exists(history.lastCsvPath):
            filePath = ''
            encoding = 'utf-16'
        else:
            with open(history.lastCsvPath, 'r', encoding='utf-8') as f:
                info = f.readlines()
                filePath = info[0].strip('\n')
                encoding = info[1].strip('\n')
        self.filePathEdit.setText(filePath)
        self.encodingComBox.setCurrentText(encoding)

    def initUI(self):
        #  Enter information 
        filePathLabel = QLabel(HAN_EN.get('File Path'))
        retainTreeLabel = QLabel(HAN_EN.get('Retain the current tree structure'))
        encodingLabel = QLabel(HAN_EN.get('Encoding'))

        self.filePathEdit = QLineEdit()
        self.btnSelect = QPushButton(HAN_EN.get('Select File'))
        self.btnSelect.setMaximumHeight(self.filePathEdit.height())
        hbox = QHBoxLayout()
        hbox.addWidget(self.filePathEdit)
        hbox.addWidget(self.btnSelect)

        self.retainTreeComBox = QComboBox()
        self.retainTreeComBox.addItems([HAN_EN.get('No'), HAN_EN.get('Yes')])

        self.encodingComBox = QComboBox()
        self.encodingComBox.addItems(self.list_encoding)

        formLayout = QFormLayout()
        formLayout.addRow(filePathLabel, hbox)
        formLayout.addRow(retainTreeLabel, self.retainTreeComBox)
        formLayout.addRow(encodingLabel, self.encodingComBox)

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
        self.btnSelect.clicked.connect(self.btnSelectOnClick)

    def btnSelectOnClick(self):
        select_filepath, ok = QFileDialog.getOpenFileName(self, HAN_EN.get("Open"),
                                                        "../resource/qemu_project", #  Default current path 
                                                        "All Files (*);;DOT Files (*.dot);;CSV Files (*.csv);;JSON Files (*.json)")
        if ok:
            self.filePathEdit.setText(str(select_filepath))
        else:
            QMessageBox.warning(self, "Warning", "The selected file failed. Please try again.")
            return False

    def getFilePath(self):
        return self.filePathEdit.text()

    def getRetainTree(self):
        return self.retainTreeComBox.currentText()

    def getEncoding(self):
        return self.encodingComBox.currentText()

