from PyQt5.QtWidgets import QVBoxLayout, QDialog, QLabel, QLineEdit, QPushButton, QComboBox, QFormLayout, \
    QDialogButtonBox, QHBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import *
import os
import history

class CsvMergeForm(QDialog):

    def __init__(self):
        super(CsvMergeForm, self).__init__()
        self.setWindowTitle(" Open the one to be closed .csv data ")
        self.resize(970, 200)
        self.initUI()
        self.initUIData()
        self.connSlot()

    def initUIData(self):
        if not os.path.exists(history.lastCsvPath):
            filePath = '../resource/demo_en.csv'
            encoding = 'ansi'
        else:
            with open(history.lastCsvPath, 'r', encoding='utf-8') as f:
                info = f.readlines()
                filePath = info[0].strip('\n')
                encoding = info[1].strip('\n')
        self.filePathEdit.setText(filePath)
        self.encodingComBox.setCurrentText(encoding)

    def initUI(self):
        #  Enter information 
        filePathLabel = QLabel('csv route ')
        encodingLabel = QLabel(' File encoding ')
        mountNodeLabel = QLabel(' Mount tree nodes ')

        self.filePathEdit = QLineEdit()
        self.btnSelect = QPushButton(" Select file ")
        self.btnSelect.setMaximumHeight(self.filePathEdit.height())
        hbox = QHBoxLayout()
        hbox.addWidget(self.filePathEdit)
        hbox.addWidget(self.btnSelect)

        self.encodingComBox = QComboBox()
        self.encodingComBox.addItems(['ansi', 'utf-8'])

        self.mountNodeEdit = QLineEdit()

        formLayout = QFormLayout()
        formLayout.addRow(filePathLabel, hbox)
        formLayout.addRow(encodingLabel, self.encodingComBox)
        formLayout.addRow(mountNodeLabel, self.mountNodeEdit)

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
        self.btnSelect.clicked.connect(self.btnSelectOnClick)

    def btnSelectOnClick(self):
        select_filepath, ok = QFileDialog.getOpenFileName(self, " Open file ",
                                                        "../resource", #  Default current path 
                                                        "CSV Files (*.csv);;All Files (*)")
        if ok:
            self.filePathEdit.setText(str(select_filepath))
        else:
            QMessageBox.warning(self, " warning ", " The selected file failed, please try again ")
            return False

    def getFilePath(self):
        return self.filePathEdit.text()

    def getEncoding(self):
        return self.encodingComBox.currentText()

    def getMountNode(self):
        return self.mountNodeEdit.text()