import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from sents_formal_llm.sentsformal import SentsFormal
from internation import HAN_EN

'''
待办：
1. 界面加上提示Label
2. 变量名修改
3. 英文翻译
4. 接入大模型翻译
'''

class TranslationDialog(QDialog):
    def __init__(self, data={}):
        super().__init__()
        self.setWindowTitle(HAN_EN.get("Natural Language Formalization"))
        self.resize(800, 300)
        self.initUI()
        self.subTranslations = []  # 新建一个列表来保存子翻译
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

        # 创建一个水平布局，用于放置下拉框、尝试次数输入框和滑动控件
        self.horizontalLayout = QHBoxLayout()

        # 创建一个下拉选择框，用于选择翻译提示词
        
        constraintTypeLabel = QLabel(HAN_EN.get('Constraint Type'))
        self.horizontalLayout.addWidget(constraintTypeLabel)
        self.translationHintComboBox = QComboBox()
        self.translationHintComboBox.addItem(HAN_EN.get('Arithmetic'))
        self.translationHintComboBox.addItem(HAN_EN.get('AbstractSets'))
        self.translationHintComboBox.addItem(HAN_EN.get('LogicalRelations'))
        self.horizontalLayout.addWidget(self.translationHintComboBox)

        # 创建一个输入框，用于输入尝试次数
        tryNumLabel = QLabel(HAN_EN.get('Number of tries'))
        self.horizontalLayout.addWidget(tryNumLabel)
        self.attemptsInput = QLineEdit()
        self.attemptsInput.setPlaceholderText(HAN_EN.get("Number of tries"))
        self.horizontalLayout.addWidget(self.attemptsInput)

        # 创建一个滑动条，用于设置翻译发散度
        self.divergenceSlider = QSlider(Qt.Horizontal)
        self.divergenceSlider.setRange(0, 100)  # 乘以100以增加精度
        self.divergenceSlider.setValue(20)  # 设置默认值为 20
        self.divergenceSlider.valueChanged.connect(self.sliderChanged)
        self.horizontalLayout.addWidget(self.divergenceSlider)

        # 创建一个标签，用于显示滑动条的当前值
        self.divergenceLabel = QLabel()
        self.horizontalLayout.addWidget(self.divergenceLabel)
        self.sliderChanged() # 显示默认值

        # 将水平布局添加到主布局中
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
        # 这里是翻译的逻辑，这个例子中只是简单地添加了一些假的翻译结果
        sf = SentsFormal(prompt_temp_path='./sents_formal_llm/prompts/arithmetic.txt')
        list_formal, sub_trans_stats_result = sf.formalize(
            sentence = data['input'],
            given_trans = self.getSubTranslation(),
            num_tries = data['attempts'],
            temperature = data['divergence']
        )
        # 设置最终结果
        self.translationEdit.setText('\n'.join(list_formal))

        # 设置子翻译
        self.clearSubTranslations() # 清空现有翻译
        for info in sub_trans_stats_result:
            self.addSubTranslation()  # 新建一个子翻译
            source_edit, target_edit, accuracy_label, _ = self.subTranslations[-1]  # 获取刚刚新建的 QLineEdit 控件
            source_edit.setText(info['nl'])  # 设置 QLineEdit 控件的值
            target_edit.setText(info['formal'])
            acc = info['rate'] * 100
            accuracy_label.setText("{}：{}%".format(HAN_EN.get('Accuracy'), acc))
            self.adjustHeight()  # 调整对话框大小以适应新的控件

    
    def getSubTranslation(self):
        dict_subtrans = {}
        for source_edit, target_edit, _, _ in self.subTranslations:
            dict_subtrans[source_edit.text()] = target_edit.text()
        return dict_subtrans

    def addSubTranslation(self):
        # 创建一个新的 QHBoxLayout，并添加到布局中
        sub_translation_layout = QHBoxLayout()

        # 创建原词编辑和目标词编辑控件，并添加到 sub_translation_layout
        source_edit = QLineEdit()
        source_edit.setPlaceholderText("子翻译原文")
        target_edit = QLineEdit()
        target_edit.setPlaceholderText("子翻译译文")
        sub_translation_layout.addWidget(source_edit)
        sub_translation_layout.addWidget(target_edit)

        # 创建准确率显示控件，并添加到 sub_translation_layout
        accuracy_label = QLabel("{}：0%".format(HAN_EN.get('Accuracy')))
        sub_translation_layout.addWidget(accuracy_label)

        # 创建删除当前行按钮，并添加到 sub_translation_layout
        delete_button = QPushButton(HAN_EN.get("Delete"))
        delete_button.clicked.connect(lambda: self.removeSubTranslation(sub_translation_layout))
        sub_translation_layout.addWidget(delete_button)

        # layout保存
        self.subTranslations.append((source_edit, target_edit, accuracy_label, sub_translation_layout))  # 将新建的 QLineEdit 控件添加到列表中

        # 将 sub_translation_layout 添加到主布局中
        self.layout.insertLayout(self.layout.count() - 3, sub_translation_layout)
        self.adjustHeight()  # 调整对话框大小以适应新的控件

    def removeSubTranslation(self, layout_to_remove):
        # 删除指定的布局及其包含的所有控件
        while layout_to_remove.count():
            item = layout_to_remove.takeAt(0)
            widget_to_delete = item.widget()
            if widget_to_delete:
                widget_to_delete.setParent(None)
        layout_to_remove.setParent(None)
        self.adjustHeight()  # 调整对话框大小以适应删除的控件

    def clearSubTranslations(self):
        # 清空子翻译
        while self.subTranslations:
            source_edit, target_edit, _, layout_to_remove = self.subTranslations.pop()  # 从列表中移除并获取最后一个子翻译
            self.removeSubTranslation(layout_to_remove)  # 删除 QHBoxLayout

    def sliderChanged(self):
        # 滑动条的值除以100以获取0到1之间的值
        divergence = self.divergenceSlider.value() / 100
        self.divergenceLabel.setText("{}：{:.2f}".format(HAN_EN.get('Temperature'), divergence))

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
            'divergence': self.divergenceSlider.value() / 100,  # 把滑动条的值转换回原来的范围
            'subTranslations': [
                {'source': source_edit.text(), 'target': target_edit.text(), 'accuracy': accuracy_label.text()}
                for source_edit, target_edit, accuracy_label, _ in self.subTranslations  # 遍历列表来获取数据
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
        self.divergenceSlider.setValue(int(data.get('divergence', 0.2) * 100))  # 把数值转换回滑动条的范围

        for subTranslation in data.get('subTranslations', []):
            self.addSubTranslation()  # 新建一个子翻译
            source_edit, target_edit, accuracy_label, _ = self.subTranslations[-1]  # 获取刚刚新建的 QLineEdit 控件
            source_edit.setText(subTranslation.get('source', ''))  # 设置 QLineEdit 控件的值
            target_edit.setText(subTranslation.get('target', ''))
            accuracy_label.setText(subTranslation.get('accuracy', ''))

        self.translationEdit.setText(data.get('translation', ''))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    data={'input': 'The friction force generated by the goods during braking is less than 0.5 N.',
        'translationHint': '提示词1',
        'attempts': '1',
        'divergence': 0.29,
        'subTranslations': [{'source': 'friction force', 'target': 'Fm'},
                            {'source': 'less than', 'target': '<'},
                            {'source': '0.5 N', 'target': '0.5'}],
        'translation': 'Fm < 0.5'}
    dialog = TranslationDialog(data)
    if dialog.exec_():
        print("输入的自然语言：", dialog.getInput())
        print("选择的翻译：", dialog.getTranslationResult())
        print("Json:\n", dialog.exportData())

    sys.exit(app.exec_())
