from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QDialog, QLabel, QLineEdit, QTextEdit, QComboBox, QFormLayout, QDialogButtonBox
from PyQt5.QtCore import *
from internation import HAN_EN
import llmtransform

class AddForm(QDialog):

    def __init__(self, parentID=''):
        super(AddForm, self).__init__()
        self.setWindowTitle(HAN_EN.get("Add Node"))
        self.resize(950, 300)
        self.parentID = parentID
        self.initUI()
        self.connSlot()

    def btnLLMOnClick(self):
        data = {
            'input': self.getNodeName()
        }
        self.llmForm = llmtransform.TranslationDialog(data)
        result = self.llmForm.exec_()
        if result != QDialog.Accepted:
            return False

        trans_result = self.llmForm.exportData()['translation']
        self.thenEdit.setText(trans_result)

    def initUI(self):
        self.llmButton = QPushButton(HAN_EN.get("Auxiliary formalization"))
        self.llmButton.clicked.connect(self.btnLLMOnClick)

        #  Enter information 
        parentIDLabel = QLabel(HAN_EN.get('Parent ID'))
        nodeNameLabel = QLabel(HAN_EN.get('Description'))
        typeLabel = QLabel(HAN_EN.get('Node Type'))
        reasonLabel = QLabel(HAN_EN.get('Reason Type'))
        attrLabel = QLabel(HAN_EN.get('Relationship'))
        ifLabel = QLabel(HAN_EN.get('IF'))
        thenLabel = QLabel(HAN_EN.get('Qualitative Info'))
        DSTheoryLabel = QLabel(HAN_EN.get('Quantitative Info'))
        AdditionLabel = QLabel(HAN_EN.get('Auxiliary Components'))
        nodeWidthLabel = QLabel(HAN_EN.get('Node Width'))

        self.parentIDEdit = QLineEdit(str(self.parentID))
        self.nodeNameEdit = QLineEdit()
        self.ifEdit = QLineEdit('')
        self.thenEdit = QTextEdit()
        self.DSTheoryEdit = QTextEdit()
        self.AdditionEdit = QTextEdit()
        self.nodeWidthEdit = QLineEdit()

        self.attrComBox = QComboBox()
        self.attrComBox.addItems([HAN_EN.get('And'), HAN_EN.get('Or')])

        self.typeComBox = QComboBox()
        self.typeComBox.addItems([HAN_EN.get('Goal'), HAN_EN.get('Strategy'), HAN_EN.get('Solution'), HAN_EN.get('TECH'), HAN_EN.get('ENVI'), HAN_EN.get('PROC'), HAN_EN.get('EVID')])

        self.reasonComBox = QComboBox()
        self.reasonComBox.addItems([HAN_EN.get('Default'), HAN_EN.get('Arithmetic'), HAN_EN.get('Functional'),
        HAN_EN.get('AbstractSets'), HAN_EN.get('SpecificSets'), HAN_EN.get('LogicalRelations'), HAN_EN.get('Quantified')])

        formLayout = QFormLayout()
        formLayout.addRow(parentIDLabel, self.parentIDEdit)
        formLayout.addRow(nodeNameLabel, self.nodeNameEdit)
        formLayout.addRow(typeLabel, self.typeComBox)
        formLayout.addRow(reasonLabel, self.reasonComBox)
        formLayout.addRow(attrLabel, self.attrComBox)
        # formLayout.addRow(ifLabel, self.ifEdit)
        formLayout.addRow(thenLabel, self.thenEdit)
        formLayout.addRow(DSTheoryLabel, self.DSTheoryEdit)
        formLayout.addRow(AdditionLabel, self.AdditionEdit)
        formLayout.addRow(nodeWidthLabel, self.nodeWidthEdit)

        #  Use two button(ok and cancel) Connect separately accept() and reject() Slot function 
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        #  layout 
        vbox = QVBoxLayout()
        # vbox.addWidget(self.llmButton)
        vbox.addLayout(formLayout)
        vbox.addWidget(buttons)

        self.setLayout(vbox)

    def connSlot(self):
        # self.btnAdd.clicked.connect(self.btnAddOnClick)
        pass

    def getParentID(self):
        return self.parentIDEdit.text()

    def getNodeName(self):
        return self.nodeNameEdit.text()

    def getIfContent(self):
        return self.ifEdit.text()

    def getThenContent(self):
        return self.thenEdit.toPlainText()

    def getDSTheoryContent(self):
        return self.DSTheoryEdit.toPlainText()

    def getAdditionContent(self):
        return self.AdditionEdit.toPlainText()
    
    def getAttribute(self):
        return self.attrComBox.currentText()

    def getNodeType(self):
        return self.typeComBox.currentText()

    def getReason(self):
        return self.reasonComBox.currentText()
    
    def getNodeWidth(self):
        return self.nodeWidthEdit.text()


