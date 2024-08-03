from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5.QtWebEngineWidgets import *
import os, json

from model import dataservice
from model import aggregation_rule
from controller import textbox

class MainLayout(QMainWindow):
    current_file = ''
    dataserv = dataservice.DataService()
    aggrl = aggregation_rule.AggregationRule()

    def __init__(self, script=''):
        super(MainLayout, self).__init__()
        self.setWindowTitle("Safety Case [v2.0]")
        self.resize(1300, 810)

        self.initUI()
        self.initData(script)
        self.connSlot()

    def initData(self, script):
        if script:
            self.code.setText(script)
        else:
            self.code.setText(self.dataserv.getDefaultText())

    def initMenu(self):
        # 创建Action
        self.actSave = QAction("保存")
        self.actFlash = QAction("刷新")
        self.actDraw = QAction("渲染")
        self.actGetJson = QAction("显示json")
        self.actCal = QAction("聚合计算")
        # 菜单栏
        # bar = self.menuBar()  # 获取菜单栏
        # edit = bar.addMenu("编辑")
        # edit.addAction(self.actFlash)

        #工具栏
        tool = self.addToolBar("Tool")
        tool.addAction(self.actSave)
        # tool.addAction(self.actFlash)
        tool.addAction(self.actDraw)
        # tool.addAction(self.actGetJson)
        tool.addAction(self.actCal)
        tool.setToolButtonStyle(Qt.ToolButtonTextOnly)

    def initUI(self):
        self.initMenu()

        self.code = QTextEdit()

        self.url = os.getcwd() + '/view/stateChart.html'
        self.browser = QWebEngineView()
        self.browser.load(QUrl.fromLocalFile(self.url))

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.code)
        splitter.addWidget(self.browser)
        splitter.setSizes([400, 900])

        hbox = QHBoxLayout()
        hbox.addWidget(splitter)

        widget = QWidget()
        widget.setLayout(hbox)
        self.setCentralWidget(widget)

    def connSlot(self):
        # 保存
        self.actSave.triggered.connect(self.actSaveOnClick)
        # 刷新页面
        self.actFlash.triggered.connect(self.actFlashOnClick)
        # 绘制图形
        self.actDraw.triggered.connect(self.actDrawOnClick)
        # 获取Json数据
        self.actGetJson.triggered.connect(self.actGetJsonOnClick)
        # 聚合计算
        self.actCal.triggered.connect(self.actCalOnClick)

    def resizeEvent(self, e):
        # 改变窗口大小响应事件
        print("w = {0}; h = {1}".format(e.size().width(), e.size().height()))

        winMenuHeight = 37
        divHeight = e.size().height() - 110
        divHeight += winMenuHeight # 有菜单时去掉此行
        self.browser.page().runJavaScript('setMyDiagramDivHeight(%d);' % divHeight)

        QtWidgets.QWidget.resizeEvent(self, e)

    def actSaveOnClick(self):
        print('actSaveOnClick')
        code = self.code.toPlainText()
        
        if self.current_file == '': # 首次保存
            select_filepath, ok = QFileDialog.getSaveFileName(self, "保存文件",
                                                        "../resource", # 默认当前路径
                                                        "TXT Files (*.txt);;All Files (*)")
            if ok:
                with open(select_filepath, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.current_file = select_filepath
                self.setWindowTitle("Safety Case [{}]".format(self.current_file))
            else:
                QMessageBox.warning(self, "警告", "保存失败，请重试")
                return False
        else: # 二次保存
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(code)

    def actFlashOnClick(self):
        print('actFlashOnClick')
        self.browser.load(QUrl.fromLocalFile(self.url))

    def updateGraph(self, json_data):
        gojs = json_data.replace('"', '\\"').replace('\n', '\\n')
        self.browser.page().runJavaScript('setModel("' + gojs + '");')

    def actDrawOnClick(self):
        print('actDrawOnClick')
        code = self.code.toPlainText()
        json_data = self.dataserv.plantUmltoGojs(code)
        self.updateGraph(json_data)

    def showJsonTextBox_callback(self, result):
        print(result)
        # 预处理
        dict_data = json.loads(result)
        for link in dict_data["linkDataArray"]:
            link['points'] = []

        # 对话框中显示
        json_data = json.dumps(dict_data, indent=4)
        self.textBox = textbox.TextBox('图形Json数据', json_data)
        self.textBox.readOnly()
        self.textBox.exec_()

    def actGetJsonOnClick(self):
        print('actGetJsonOnClick')
        self.browser.page().runJavaScript('getModelJson();', self.showJsonTextBox_callback)

    def aggregationCal_callback(self, result):
        print(result)
        # 聚合计算
        dict_data = json.loads(result)
        try:
            dict_data = self.aggrl.Cal(dict_data)
        except:
            QMessageBox.critical(self, "错误", "计算数据错误，请核查！")

        # 刷新图形显示
        json_data = json.dumps(dict_data, indent=4)
        self.updateGraph(json_data)

    def actCalOnClick(self):
        print('actCalOnClick')
        self.browser.page().runJavaScript('getModelJson();', self.aggregationCal_callback)
