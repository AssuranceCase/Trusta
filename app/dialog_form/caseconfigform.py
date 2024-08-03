from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class CaseConfigForm(QDialog):

    def __init__(self, title = "CaseConfigForm", content = ''):
        super(CaseConfigForm, self).__init__()
        self.setWindowTitle(title)
        self.resize(800, 300)
        self.initUI()
        self.initUIData(content)
        self.connSlot()

    def initUIData(self, content):
        pass
        # if content == '' or content == False:
        #     with open('../resource/prolog.txt', 'r', encoding='utf-8') as f:
        #         content = f.read()
        # self.contentEdit.setText(content)

    def initUI(self):
        # 输入信息
        self.domainLabel = QLabel('领域')
        self.creatorLabel = QLabel('创建者')

        self.domainEdit = QLineEdit('Aircraft')
        self.creatorComBox = QComboBox()
        self.creatorComBox.addItems(['person', 'gpt-3.5', 'gpt-4', 'PaLM 2'])

        formLayout = QFormLayout()
        formLayout.addRow(self.domainLabel, self.domainEdit)
        formLayout.addRow(self.creatorLabel, self.creatorComBox)

        # 使用两个button(ok和cancel)分别连接accept()和reject()槽函数
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # 布局
        vbox = QVBoxLayout()
        vbox.addLayout(formLayout)
        vbox.addWidget(buttons)

        self.setLayout(vbox)

    def connSlot(self):
        # self.btnAdd.clicked.connect(self.btnAddOnClick)
        pass

    def initExportUI(self):
        pass
        # self.switchLabel.setVisible(False)
        # self.switchComBox.setVisible(False)
        # self.quotesSwitchLabel.setVisible(False)
        # self.quotesSwitchComBox.setVisible(False)
        # self.contentEdit.setReadOnly(True)
        # self.contentEdit.setStyleSheet('background:#DDDDDD')

    def getData(self):
        return {
            "domain": self.domainEdit.text(),
            "creator": self.creatorComBox.currentText()
        }


