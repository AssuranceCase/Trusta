import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
try:
    from sents_formal_llm.sentsformal import SentsFormal
except:
    pass
from internation import HAN_EN

'''
 To be done: 
1.  Add prompts on the interface Label
2.  Variable name modification 
3.  English translation 
4.  Integrate large model translation 
'''

class TranslationDialog(QDialog):
    def __init__(self, data={}):
        super().__init__()
        self.setWindowTitle(HAN_EN.get("Natural Language Formalization"))
        self.resize(800, 300)
        self.initUI()
        self.subTranslations = []  #  Create a new list to save sub translations 
        self.setData(data)

    def initUI(self):
        self.layout = QVBoxLayout()

        nlLabel = QLabel(HAN_EN.get('Natural Language'))
        self.layout.addWidget(nlLabel)

        self.inputLine = QLineEdit()
        self.inputLine.setPlaceholderText(HAN_EN.get('Please enter natural language'))
        self.layout.addWidget(self.inputLine)

        paramLabel = QLabel(HAN_EN.get('Parameter setting'))
        self.layout.addWidget(paramLabel)

        #  Create a horizontal layout for placing drop-down boxes, try count input boxes, and sliding controls 
        self.horizontalLayout = QHBoxLayout()

        #  Create a dropdown selection box to choose translation prompt words 
        
        constraintTypeLabel = QLabel(HAN_EN.get('Constraint Type'))
        self.horizontalLayout.addWidget(constraintTypeLabel)
        self.translationHintComboBox = QComboBox()
        self.translationHintComboBox.addItem(HAN_EN.get('Arithmetic'))
        self.translationHintComboBox.addItem(HAN_EN.get('AbstractSets'))
        self.translationHintComboBox.addItem(HAN_EN.get('LogicalRelations'))
        self.horizontalLayout.addWidget(self.translationHintComboBox)

        #  Create an input box for entering the number of attempts 
        tryNumLabel = QLabel(HAN_EN.get('Number of tries'))
        self.horizontalLayout.addWidget(tryNumLabel)
        self.attemptsInput = QLineEdit()
        self.attemptsInput.setPlaceholderText(HAN_EN.get("Number of tries"))
        self.horizontalLayout.addWidget(self.attemptsInput)

        #  Create a slider to set translation divergence 
        self.divergenceSlider = QSlider(Qt.Horizontal)
        self.divergenceSlider.setRange(0, 100)  #  multiply 100 To increase accuracy 
        self.divergenceSlider.setValue(20)  #  Set the default value to  20
        self.divergenceSlider.valueChanged.connect(self.sliderChanged)
        self.horizontalLayout.addWidget(self.divergenceSlider)

        #  Create a label to display the current value of the slider 
        self.divergenceLabel = QLabel()
        self.horizontalLayout.addWidget(self.divergenceLabel)
        self.sliderChanged() #  Display default values 

        #  Add horizontal layout to the main layout 
        self.layout.addLayout(self.horizontalLayout)

        self.addButton = QPushButton(HAN_EN.get("Adding subtranslations"))
        self.addButton.clicked.connect(self.addSubTranslation)
        self.layout.addWidget(self.addButton)

        self.translateButton = QPushButton(HAN_EN.get("Translate"))
        self.translateButton.clicked.connect(self.translate)
        self.layout.addWidget(self.translateButton)

        self.translationEdit = QTextEdit()
        # self.translationEdit.setFixedHeight(100)
        self.layout.addWidget(self.translationEdit)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        self.setLayout(self.layout)

    def translate(self):
        data = self.exportData()
        #  This is the logic of translation. In this example, some fake translation results were simply added 
        sf = SentsFormal(prompt_temp_path='./sents_formal_llm/prompts/arithmetic.txt')
        list_formal, sub_trans_stats_result = sf.formalize(
            sentence = data['input'],
            given_trans = self.getSubTranslation(),
            num_tries = data['attempts'],
            temperature = data['divergence']
        )
        #  Set the final result 
        self.translationEdit.setText('\n'.join(list_formal))

        #  Set sub translation 
        self.clearSubTranslations() #  Clear existing translations 
        for info in sub_trans_stats_result:
            self.addSubTranslation()  #  Create a new sub translation 
            source_edit, target_edit, accuracy_label, _ = self.subTranslations[-1]  #  Get the newly created  QLineEdit  control 
            source_edit.setText(info['nl'])  #  set up  QLineEdit  The value of the control 
            target_edit.setText(info['formal'])
            acc = info['rate'] * 100
            accuracy_label.setText("{} :  {}%".format(HAN_EN.get('Accuracy'), acc))
            self.adjustHeight()  #  Adjust the size of the dialog box to fit the new control 

    
    def getSubTranslation(self):
        dict_subtrans = {}
        for source_edit, target_edit, _, _ in self.subTranslations:
            dict_subtrans[source_edit.text()] = target_edit.text()
        return dict_subtrans

    def addSubTranslation(self):
        #  Create a new one  QHBoxLayout , and add it to the layout 
        sub_translation_layout = QHBoxLayout()

        #  Create original word editing and target word editing controls, and add them to  sub_translation_layout
        source_edit = QLineEdit()
        source_edit.setPlaceholderText(" Translate the original text into English ")
        target_edit = QLineEdit()
        target_edit.setPlaceholderText(" Subtranslation Translation ")
        sub_translation_layout.addWidget(source_edit)
        sub_translation_layout.addWidget(target_edit)

        #  Create an accuracy display control and add it to  sub_translation_layout
        accuracy_label = QLabel("{} :  0%".format(HAN_EN.get('Accuracy')))
        sub_translation_layout.addWidget(accuracy_label)

        #  Create a delete current row button and add it to  sub_translation_layout
        delete_button = QPushButton(HAN_EN.get("Delete"))
        delete_button.clicked.connect(lambda: self.removeSubTranslation(sub_translation_layout))
        sub_translation_layout.addWidget(delete_button)

        # layout preservation 
        self.subTranslations.append((source_edit, target_edit, accuracy_label, sub_translation_layout))  #  Newly created  QLineEdit  Add control to list 

        #  take  sub_translation_layout  Add to main layout 
        self.layout.insertLayout(self.layout.count() - 3, sub_translation_layout)
        self.adjustHeight()  #  Adjust the size of the dialog box to fit the new control 

    def removeSubTranslation(self, layout_to_remove):
        #  Delete the specified layout and all its contained controls 
        while layout_to_remove.count():
            item = layout_to_remove.takeAt(0)
            widget_to_delete = item.widget()
            if widget_to_delete:
                widget_to_delete.setParent(None)
        layout_to_remove.setParent(None)
        self.adjustHeight()  #  Adjust the size of the dialog box to fit the deleted control 

    def clearSubTranslations(self):
        #  Qingkongzi Translation 
        while self.subTranslations:
            source_edit, target_edit, _, layout_to_remove = self.subTranslations.pop()  #  Remove and retrieve the last sub translation from the list 
            self.removeSubTranslation(layout_to_remove)  #  delete  QHBoxLayout

    def sliderChanged(self):
        #  The value of the slider divided by 100 To obtain 0 reach 1 Between values 
        divergence = self.divergenceSlider.value() / 100
        self.divergenceLabel.setText("{} :  {:.2f}".format(HAN_EN.get('Temperature'), divergence))

    def adjustHeight(self):
        ideal_height = self.sizeHint().height()
        self.setFixedHeight(ideal_height)

    def getInput(self):
        return self.inputLine.text()

    def getTranslationResult(self):
        return self.translationEdit.toPlainText()

    def exportData(self):
        data = {
            'input': self.inputLine.text(),
            'translationHint': self.translationHintComboBox.currentText(),
            'attempts': int(self.attemptsInput.text()),
            'divergence': self.divergenceSlider.value() / 100,  #  Convert the value of the slider back to its original range 
            'subTranslations': [
                {'source': source_edit.text(), 'target': target_edit.text(), 'accuracy': accuracy_label.text()}
                for source_edit, target_edit, accuracy_label, _ in self.subTranslations  #  Traverse the list to obtain data 
            ],
            'translation': self.translationEdit.toPlainText()
        }
        return data
    
    def setData(self, data):
        self.inputLine.setText(data.get('input', ''))
        index = self.translationHintComboBox.findText(data.get('translationHint', ''))
        if index >= 0:
            self.translationHintComboBox.setCurrentIndex(index)
        self.attemptsInput.setText(str(data.get('attempts', 1)))
        self.divergenceSlider.setValue(int(data.get('divergence', 0.2) * 100))  #  Convert the value back to the range of the slider 

        for subTranslation in data.get('subTranslations', []):
            self.addSubTranslation()  #  Create a new sub translation 
            source_edit, target_edit, accuracy_label, _ = self.subTranslations[-1]  #  Get the newly created  QLineEdit  control 
            source_edit.setText(subTranslation.get('source', ''))  #  set up  QLineEdit  The value of the control 
            target_edit.setText(subTranslation.get('target', ''))
            accuracy_label.setText(subTranslation.get('accuracy', ''))

        self.translationEdit.setText(data.get('translation', ''))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    data={'input': 'The friction force generated by the goods during braking is less than 0.5 N.',
        'translationHint': ' cue word 1',
        'attempts': '1',
        'divergence': 0.29,
        'subTranslations': [{'source': 'friction force', 'target': 'Fm'},
                            {'source': 'less than', 'target': '<'},
                            {'source': '0.5 N', 'target': '0.5'}],
        'translation': 'Fm < 0.5'}
    dialog = TranslationDialog(data)
    if dialog.exec_():
        print(" Natural language input: ", dialog.getInput())
        print(" Selected translation: ", dialog.getTranslationResult())
        print("Json:\n", dialog.exportData())

    sys.exit(app.exec_())
