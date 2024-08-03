'''
 Main interface layout 
'''
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import  QWebChannel
import sys
import os
import shutil
sys.path.append('dialog_form')
sys.path.append('others')
import json
import traceback
from copy import deepcopy
import jstrans
import addform
import delform
import editform
import prologform
import csvimpform
import csvexpform
import csvmergeform
import caseconfigform
import chartdialog
import code2gsndialog
import additionform
import textbox
import webbox
import dataservice
try:
    import safecase
except:
    pass
import history
import re
from multiprocessing import Process
from collections import deque
from functools import partial
from internation import HAN_EN

try:
    sys.path.append('./python_prolog')
    from python_prolog import editor as py_prolog_editer
    from python_prolog.prologpy import solver as py_prolog_solver
except:
    pass
try:
    sys.path.append('./safety_case')
    from safety_case import SC
except:
    pass

channel = QWebChannel()

class MainLayout(QMainWindow):
    current_file = ''
    current_encoding = ''
    current_language = ''
    all_node_width = 150
    strategy_open = False

    def makeWindowTitle(self):
        return HAN_EN.get('Trusta') + " v3.0 " + f'[{self.current_file}] - {self.current_encoding} - {self.current_language}'

    def __init__(self):
        super(MainLayout, self).__init__()
        self.setWindowTitle(self.makeWindowTitle())
        self.setWindowIcon(QIcon(os.path.join('images', 'Logo.ico')))
        # self.setWindowOpacity(0.9) #  Set window transparency 
        # self.setAttribute(Qt.WA_TranslucentBackground) #  Set window background transparency 
        self.setStyleSheet('''
            QMainWindow {
                background: #C4ECFF;
                border:1px solid white;
                border-radius:10px;
            }
        ''')
        # self.resize(1600, 1200)
        self.resize(1200, 900)

        self.url_gsn = os.getcwd() + '/web_view/show_gsn.html'
        self.url_gojs = os.getcwd() + '/web_view/show.html'
        self.url_evaluation = os.getcwd() + '/web_view/evaluation.html'

        self.initData()
        self.initUI()
        self.connSlot()

    def initData(self):
        jstrans.js2py()
        try:
            import show_data as data
            self.dataService = dataservice.DataService()
            self.dataService.nodeDataArray = data.nodeDataArray
            self.dataService.linkDataArray = data.linkDataArray
        except ModuleNotFoundError:
            self.dataService = dataservice.DataService()
            self.dataService.nodeDataArray = []
            self.dataService.linkDataArray = []
            history.log('ModuleNotFoundError: show_data')

    def initMenu(self):
        #  establish Action
        self.actNew = QAction(QIcon(os.path.join('images', 'NewIcon.ico')), HAN_EN.get("New"))
        self.actAutoSave = QAction(QIcon(os.path.join('images', 'SavedIcon.ico')), HAN_EN.get("Save"))
        self.actJsonOpen = QAction(QIcon(os.path.join('images', 'OpenIcon.ico')), HAN_EN.get("JSON Open"))
        self.actJsonSave = QAction(QIcon(os.path.join('images', 'SavedIcon.ico')), HAN_EN.get("JSON Save"))
        self.actJsonSaveAs = QAction(QIcon(os.path.join('images', 'SaveAsIcon.ico')), HAN_EN.get("JSON Save As"))
        
        self.actPythonCodeOpen = QAction(QIcon(os.path.join('images', 'CodeIcon.ico')), HAN_EN.get("Python Code Import"))
        self.actDotOpen = QAction(QIcon(os.path.join('images', 'OpenIcon.ico')), HAN_EN.get("Dot Import"))

        self.actYamlOpen = QAction(QIcon(os.path.join('images', 'OpenIcon.ico')), HAN_EN.get("YAML Open"))
        self.actYamlSave = QAction(QIcon(os.path.join('images', 'SavedIcon.ico')), HAN_EN.get("YAML Save"))
        self.actYamlSaveAs = QAction(QIcon(os.path.join('images', 'SaveAsIcon.ico')), HAN_EN.get("YAML Save As"))

        self.actCsvImp = QAction(QIcon(os.path.join('images', 'OpenIcon.ico')), HAN_EN.get("CSV Open"))
        self.actCsvSave = QAction(QIcon(os.path.join('images', 'SavedIcon.ico')), HAN_EN.get("CSV Save"))
        self.actCsvExp = QAction(QIcon(os.path.join('images', 'SaveAsIcon.ico')), HAN_EN.get("CSV Save As"))
#         self.actCsvMerge = QAction(QIcon(os.path.join('images', 'MergeIcon.ico')), HAN_EN.get("CSV Merge"))
#         self.actFormalExp = QAction(QIcon(os.path.join('images', 'FormalExpIcon.ico')), HAN_EN.get("Formal Save As"))

        self.actFlash = QAction(QIcon(os.path.join('images', 'FreshedIcon.ico')), HAN_EN.get("Fresh"))
        self.actAdd = QAction(QIcon(os.path.join('images', 'AddedIcon.ico')), HAN_EN.get("Add"))
        self.actDel = QAction(QIcon(os.path.join('images', 'DeletedIcon.ico')), HAN_EN.get("Delete"))
        self.actEdit = QAction(QIcon(os.path.join('images', 'EditedIcon.ico')), HAN_EN.get("Edit"))
#         self.actAutoAdd = QAction(QIcon(os.path.join('images', 'AutoAddedIcon.ico')), HAN_EN.get("Auto Add"))        
        self.actPruneNode = QAction(QIcon(os.path.join('images', 'PruneNodeIcon.ico')), HAN_EN.get("Prune Node"))
        self.actAddAddition = QAction(QIcon(os.path.join('images', 'AddAddition.ico')), HAN_EN.get("Add Addition"))

#         self.actPrologImp = QAction(QIcon(os.path.join('images', 'PrologImportIcon.ico')), HAN_EN.get("Prolog Import"))
#         self.actPrologExp = QAction(QIcon(os.path.join('images', 'PrologExportIcon.ico')), HAN_EN.get("Prolog Export"))
#         self.actPrologCheck = QAction(QIcon(os.path.join('images', 'PrologCheckIcon.ico')), HAN_EN.get("Prolog Check"))

        self.actTransAngle = QAction(QIcon(os.path.join('images', 'RotateIcon.ico')), HAN_EN.get("Rotate Tree"))
        self.actNodeWidth = QAction(QIcon(os.path.join('images', 'WidthIcon.ico')), HAN_EN.get("Node Width"))
        self.actNodesHighlight = QAction(QIcon(os.path.join('images', 'HighLightIcon.ico')), HAN_EN.get("Node Highlight"))
        self.actNodesMode = QAction(QIcon(os.path.join('images', 'ModeIcon.ico')), HAN_EN.get("Node Mode"))
        self.actStrategySwitch = QAction(QIcon(os.path.join('images', 'StrategyIcon.ico')), HAN_EN.get("Strategy Switch"))

#         self.actSafetyCase = QAction(QIcon(os.path.join('images', 'SafetyCaseIcon.ico')), HAN_EN.get("Export DS-Tree"))
#         self.actConstraintProve = QAction(QIcon(os.path.join('images', 'ProveIcon.ico')), HAN_EN.get("Evaluation"))
#         self.actConstraintFormal = QAction(QIcon(os.path.join('images', 'FormalIcon.ico')), HAN_EN.get("Formalise"))
#         self.actDSTheory = QAction(QIcon(os.path.join('images', 'DSTheoryIcon.ico')), HAN_EN.get("Quantitative Reason"))
#         self.actAutoEvaluate = QAction(QIcon(os.path.join('images', 'AutoEvaluateIcon.png')), HAN_EN.get("Auto Evaluate"))

#         self.actTranslateEn = QAction(QIcon(os.path.join('images', 'TranslateEnIcon.ico')), HAN_EN.get("To English"))
#         self.actTranslateZh = QAction(QIcon(os.path.join('images', 'TranslateZhIcon.ico')), HAN_EN.get("To Chinese"))
#         self.actTranslate = QAction(QIcon(os.path.join('images', 'TranslateIcon.ico')), HAN_EN.get("Translate"))
        self.actToGSN = QAction(QIcon(os.path.join('images', 'ToGSN.png')), HAN_EN.get("To GSN"))

        self.actTemperature = QAction(QIcon(os.path.join('images', 'TemperatureIcon.ico')), HAN_EN.get("Temperature"))
        self.actSearch = QAction(QIcon(os.path.join('images', 'SearchIcon.ico')), HAN_EN.get("Search"))

#         self.actCaseAddGoals = QAction(QIcon(os.path.join('images', 'AddedIcon.ico')), HAN_EN.get(" Adding artificial data to the case set "))
#         self.actCaseCreateGoals = QAction(QIcon(os.path.join('images', 'EditedIcon.ico')), HAN_EN.get("LLM Generate comparative cases "))
#         self.actCaseEvaluateSimilar = QAction(QIcon(os.path.join('images', 'PrologCheckIcon.ico')), HAN_EN.get("LLM Evaluate similarity "))
#         self.actCaseDrawChart = QAction(QIcon(os.path.join('images', 'OverviewIcon.png')), HAN_EN.get(" Draw a similarity statistical chart "))

#         self.actCaseOneStep = QAction(QIcon(os.path.join('images', 'Logo.ico')), HAN_EN.get(" One click generation: sequentially execute the following steps "))
#         self.actCaseLoadCallGraph = QAction(QIcon(os.path.join('images', 'OpenIcon.ico')), HAN_EN.get(" Objective: Import function call diagram "))
#         self.actCaseAdjustGraph = QAction(QIcon(os.path.join('images', 'PruneNodeIcon.ico')), HAN_EN.get(" Goal: Make necessary adjustments (remove irrelevant targets) "))
        self.actFuncAnalysis = QAction(QIcon(os.path.join('images', 'FunctionAnalyzerIcon.ico')), HAN_EN.get("Function Analyzer"))
#         self.actCaseFuncAnalysis = QAction(QIcon(os.path.join('images', 'FunctionAnalyzerIcon.ico')), HAN_EN.get(" Goal and Strategy: LLM Function objective expression and generation strategy "))
#         self.actCaseInitToContext = QAction(QIcon(os.path.join('images', 'TranslateIcon.ico')), HAN_EN.get(" Background: Constructor conversion Context"))
#         self.actCaseAddSolution = QAction(QIcon(os.path.join('images', 'AutoAddedIcon.ico')), HAN_EN.get(" Solution: Add evidence that supports underlying objectives "))

#         self.actCaseEvalCallPathCompare = QAction(QIcon(os.path.join('images', 'TranslateIcon.ico')), HAN_EN.get(" assessment 1 : Call path difference "))
#         self.actCaseUnitTestParse = QAction(QIcon(os.path.join('images', 'TranslateIcon.ico')), HAN_EN.get(" assessment 2 Test case tagging "))

#         self.actWinFileTree = QAction(QIcon(os.path.join('images', 'FileTreeIcon.ico')), HAN_EN.get("Explorer"))
        self.actWinNodeEdit = QAction(QIcon(os.path.join('images', 'EditTableIcon.ico')), HAN_EN.get("Node Edit"))
        self.actWinOverview = QAction(QIcon(os.path.join('images', 'OverviewIcon.png')), HAN_EN.get("Overview"))
        self.actWinHistory = QAction(QIcon(os.path.join('images', 'HistoryIcon.ico')), HAN_EN.get("History"))
        self.actWinOutline = QAction(QIcon(os.path.join('images', 'OutlineIcon.ico')), HAN_EN.get("Outline"))
#         self.actWinChatHistory = QAction(QIcon(os.path.join('images', 'chatGPT.png')), HAN_EN.get("Chat History"))
        self.actWinShowGSN = QAction(QIcon(os.path.join('images', 'ToGSN.png')), HAN_EN.get("Display GSN"))

        
        #  Shortcut keys 
        self.actAutoSave.setShortcut('Ctrl+S')
        self.actAdd.setShortcut('Ctrl+A')
        self.actEdit.setShortcut('Ctrl+E')
        self.actFlash.setShortcut('F5')
#         self.actTranslate.setShortcut('T')

        #  menu bar 
        bar = self.menuBar()  #  Get menu bar 

        file = bar.addMenu(HAN_EN.get("File"))
        file.addAction(self.actNew)
        file.addAction(self.actAutoSave)
        file.addAction(self.actPythonCodeOpen)
        file.addAction(self.actDotOpen)
        file.addSeparator()
        file.addAction(self.actJsonOpen)
        file.addAction(self.actJsonSave)
        file.addAction(self.actJsonSaveAs)
        file.addSeparator()
        file.addAction(self.actYamlOpen)
        file.addAction(self.actYamlSave)
        file.addAction(self.actYamlSaveAs)
        file.addSeparator()
        file.addAction(self.actCsvImp)
        file.addAction(self.actCsvSave)
        file.addAction(self.actCsvExp)
        file.addSeparator()
#         file.addAction(self.actCsvMerge)
#         file.addAction(self.actFormalExp)

        edit = bar.addMenu(HAN_EN.get("Edit"))
        edit.addAction(self.actFlash)
        edit.addAction(self.actAdd)
        edit.addAction(self.actDel)
        edit.addAction(self.actEdit)
        edit.addAction(self.actAddAddition)
#         edit.addAction(self.actAutoAdd)
        edit.addAction(self.actPruneNode)

#         prolog = bar.addMenu(HAN_EN.get("Prolog"))
#         prolog.addAction(self.actPrologImp)
#         prolog.addAction(self.actPrologExp)
#         prolog.addAction(self.actPrologCheck)

        graph = bar.addMenu(HAN_EN.get("Diagram"))
        graph.addAction(self.actTransAngle)
        graph.addAction(self.actNodeWidth)
        graph.addAction(self.actNodesHighlight)
        graph.addAction(self.actNodesMode)
        graph.addAction(self.actStrategySwitch)
        
        win = bar.addMenu(HAN_EN.get("Windows"))
#         win.addAction(self.actWinFileTree)
        win.addAction(self.actWinNodeEdit)
        win.addAction(self.actWinOverview)
        win.addAction(self.actWinHistory)
        win.addAction(self.actWinOutline)
#         win.addAction(self.actWinChatHistory)
        win.addAction(self.actWinShowGSN)

#         prove = bar.addMenu(HAN_EN.get("Evaluation"))
#         prove.addAction(self.actSafetyCase)
#         prove.addAction(self.actConstraintFormal)
#         prove.addAction(self.actConstraintProve)
#         prove.addAction(self.actDSTheory)
#         prove.addAction(self.actAutoEvaluate)
        
        translate = bar.addMenu(HAN_EN.get("Translate"))
#         translate.addAction(self.actTranslateEn)
#         translate.addAction(self.actTranslateZh)
#         translate.addAction(self.actTranslate)
        translate.addAction(self.actToGSN)
        translate.addAction(self.actFuncAnalysis)

#         studycase = bar.addMenu(HAN_EN.get("StudyCase"))
#         studycase.addAction(self.actCaseAddGoals)
#         studycase.addAction(self.actCaseCreateGoals)
#         studycase.addAction(self.actCaseEvaluateSimilar)
#         studycase.addAction(self.actCaseDrawChart)
#         studycase.addSeparator()
#         studycase.addAction(self.actCaseOneStep)
#         studycase.addAction(self.actCaseLoadCallGraph)
#         studycase.addAction(self.actCaseAdjustGraph)
#         studycase.addAction(self.actCaseFuncAnalysis)
#         studycase.addAction(self.actCaseInitToContext)
#         studycase.addAction(self.actCaseAddSolution)
#         studycase.addSeparator()
#         studycase.addAction(self.actCaseEvalCallPathCompare)
#         studycase.addAction(self.actCaseUnitTestParse)

        # toolbar 
        tool = self.addToolBar(" Upper toolbar ")
        # tool.addAction(self.actPythonCodeOpen)
        tool.addAction(self.actAutoSave)
        tool.addAction(self.actFlash)
        tool.addAction(self.actAdd)
        tool.addAction(self.actDel)
        tool.addAction(self.actEdit)
        tool.addAction(self.actTransAngle)
        tool.addAction(self.actNodeWidth)
        tool.addAction(self.actNodesHighlight)
        tool.addAction(self.actNodesMode)
        tool.addAction(self.actStrategySwitch)
        tool.addAction(self.actAddAddition)
        tool.addAction(self.actToGSN)
        tool.addSeparator()
#         tool.addAction(self.actDSTheory)
#         tool.addAction(self.actAutoAdd)
        tool.addAction(self.actPruneNode)
        tool.addAction(self.actFuncAnalysis)
#         tool.addAction(self.actConstraintFormal)
#         tool.addAction(self.actConstraintProve)
#         tool.addAction(self.actAutoEvaluate)
        #  Checked subtree 
        self.proveTreeEdit = QLineEdit()
        self.proveTreeEdit.setMaximumWidth(220)
        self.proveTreeEdit.setPlaceholderText(HAN_EN.get("Sub-Tree ID:Level"))
        self.proveTreeEdit.setStyleSheet('''
            height: 30px;
        ''')
        tool.addWidget(self.proveTreeEdit)

        #  Divergence setting 
        tool.addAction(self.actTemperature)
        self.temperatureEdit = QLineEdit("0")
        self.temperatureEdit.setMaximumWidth(180)
        self.temperatureEdit.setPlaceholderText(HAN_EN.get("Temperature"))
        self.temperatureEdit.setStyleSheet('''
            height: 30px;
        ''')
        tool.addWidget(self.temperatureEdit)

        #  search 
        tool.addSeparator()
        tool.addAction(self.actSearch)
        self.searchEdit = QLineEdit()
        self.searchEdit.setPlaceholderText(HAN_EN.get("Search Content"))
        self.searchEdit.setStyleSheet('''
            margin-right: 15px;
            height: 32px;
        ''')
        tool.addWidget(self.searchEdit)

        #  Left toolbar 
        left_tool = QToolBar(" Left toolbar ", self)
        left_tool.setIconSize(QSize(46,46))
        self.addToolBar(Qt.LeftToolBarArea, left_tool)
#         left_tool.addAction(self.actWinFileTree)
        left_tool.addAction(self.actWinNodeEdit)
        left_tool.addAction(self.actWinOverview)
        left_tool.addAction(self.actWinHistory)
        left_tool.addAction(self.actWinOutline)
#         left_tool.addAction(self.actWinChatHistory)
        left_tool.addAction(self.actWinShowGSN)

    def initUI(self):
        self.initMenu()

        #  Open the last record 
        history.log(' Open the software ')
        if os.path.exists(history.lastCsvPath):
            with open(history.lastCsvPath, 'r', encoding='utf-8') as f:
                info = f.readlines()
                filePath = info[0].strip('\n')
                encoding = info[1].strip('\n')
        else:
            filePath = '../resource/demo_en.csv'
            encoding = 'ansi'

        if os.path.exists(filePath):
            if filePath.endswith('.csv'):
                list_notImpNode, err = self.dataService.csvImport(filePath, HAN_EN.get("No"), encoding)
            elif filePath.endswith('.json'):
                err = self.dataService.jsonImport(filePath, encoding)
            elif filePath.endswith('.yaml'):
                err = self.dataService.yamlImport(filePath, encoding)
            elif filePath.endswith('.dot'):
                # Step 0: Copy config.json
                work_path = os.path.dirname(filePath)
                config_path = os.path.join(work_path, 'config.json')
                if os.path.exists(config_path):
                    shutil.copyfile(config_path, 'config.json')
                err = self.dataService.loadDot(filePath, encoding)
            else:
                err = HAN_EN.get("Unsupported file format")
        else:
            err = 'File does not exist'

        if err != '':
            # QMessageBox.critical(self, " error ", "[%s] %s ！ Open failed " % (filePath, err))
            try:
                os.remove(history.lastCsvPath)
            except:
                pass
        else:
            history.log(' load [%s] data ' % filePath)
            self.changeCsvFile(filePath, encoding)

        self.url = self.url_gojs
        self.browser = QWebEngineView()
        self.browser.load(QUrl.fromLocalFile(self.url))
        channel.registerObject("layout_obj", self)
        self.browser.page().setWebChannel(channel)

        self.dataService.setAllNodeMode('Addition') #  Default display 
        self.dataService.setAllNodeWidth(200) #  Node default width 

        vbox = QVBoxLayout()
        vbox.addWidget(self.browser)

        widget = QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

        self.setDockWidget()
    
    @pyqtSlot(int, result=int)
    def factorial(self,n):
        if n == 0 or n == 1:
            return 1
        else:
            return self.factorial(n - 1) * n
        
    @pyqtSlot(str, result=str)
    def html_message(self, str_json_input):
        json_input = json.loads(str_json_input)
        print(json_input)

        if json_input.get('action') == 'edit_node':
            ID = int(json_input.get('node_id'))
            self.btnEditOnClick(ID)
        if json_input.get('action') == 'show_node':
            ID = int(json_input.get('node_id'))
            self.dockShowNodeInfo(ID)
            level = 2
            if self.dataService.findNodeByKey(ID).nodeType not in HAN_EN.gets('Goal'):
                parent_ids, cnt = self.dataService.getParentIDs(ID)
                ID = int(parent_ids.split(' ')[0])
            str_yaml = self.dataService.toGsnYaml(ID, level)
            self.create_gsn_svg(str_yaml)
            self.browser_show_GSN.load(QUrl.fromLocalFile(self.url_gsn))
        if json_input.get('action') == 'evaluate':
            ID = int(json_input.get('node_id'))
            level = int(json_input.get('level', 1))
            self.btnAutoEvaluateOnClick(ID, level)
        if json_input.get('action') == 'auto_add':
            ID = int(json_input.get('node_id'))
            level = int(json_input.get('level', 1))
            self.btnAutoAddOnClick(ID, level)
        if json_input.get('action') == 'func_analysis':
            ID = int(json_input.get('node_id'))
            level = int(json_input.get('level', 1))
            self.btnCaseFuncAnalysisOnClick(ID, level)
        if json_input.get('action') == 'add_assumption':
            ID = int(json_input.get('node_id'))
            level = int(json_input.get('level', 1))
            self.btnAddAdditionOnClick(ID, 'Assumption')
        if json_input.get('action') == 'add_justification':
            ID = int(json_input.get('node_id'))
            level = int(json_input.get('level', 1))
            self.btnAddAdditionOnClick(ID, 'Justification')
        if json_input.get('action') == 'add':
            ID = int(json_input.get('node_id'))
            # level = int(json_input.get('level', 1))
            self.btnAddOnClick(parentID=ID)
        if json_input.get('action') == 'delete':
            ID = int(json_input.get('node_id'))
            # level = int(json_input.get('level', 1))
            self.btnDelOnClick(str(ID))


        json_output = {"state": "OK"}
        str_json_output = json.dumps(json_output)
        return str_json_output
    
    def dockShowNodeInfo(self, ID):
        info = self.dataService.findNodeByKey(ID)
        list_field = [
            (HAN_EN.get('Node ID'), str(info.nodeID)),
            (HAN_EN.get('Description'), info.nodeName),
            (HAN_EN.get('Auxiliary Components'), info.Addition),
            (HAN_EN.get('Qualitative Info'), info.content),
            (HAN_EN.get('Parent ID'), info.parentID),
        ]
        node_edit_table = self.dockNodeEditTable(list_field)
        self.node_edit_dock.setWidget(node_edit_table)
        # self.node_edit_dock.show()

    def setDockWidget(self):
        #  create a window 
        self.resource_mng_dock = QDockWidget(HAN_EN.get('Explorer'), self)
        file_model = QDirModel()
        file_tree = QTreeView()
        file_tree.header().setDefaultSectionSize(280)
        file_tree.setModel(file_model)
        self.resource_mng_dock.setWidget(file_tree)

        self.history_dock = QDockWidget(HAN_EN.get('History'), self)
        history_model = QStringListModel()
        history_list = QListView()
        list_log = history.get_logs()
        history_model.setStringList(list_log)
        history_list.setModel(history_model)
        self.history_dock.setWidget(history_list)

        self.node_edit_dock = QDockWidget(HAN_EN.get('Node Edit'), self)
        node_edit_table = self.dockNodeEditTable()
        self.node_edit_dock.setWidget(node_edit_table)

        self.outline_tree_dock = QDockWidget(HAN_EN.get('Outline'), self)
        outline_tree_view = self.dockDataTreeView()
        self.outline_tree_dock.setWidget(outline_tree_view)

        self.chat_history_dock = QDockWidget(HAN_EN.get('Chat History'), self)
        url_chat = os.getcwd() + '/web_view/show_chats.html'
        browser_chat_history = QWebEngineView()
        browser_chat_history.load(QUrl.fromLocalFile(url_chat))
        self.chat_history_dock.setWidget(browser_chat_history)

        self.show_GSN_dock = QDockWidget(HAN_EN.get('Display GSN'), self)
        self.browser_show_GSN = QWebEngineView()
        self.browser_show_GSN.load(QUrl.fromLocalFile(self.url_gsn))
        self.show_GSN_dock.setWidget(self.browser_show_GSN)

        #  window position 
        self.addDockWidget(Qt.LeftDockWidgetArea, self.resource_mng_dock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.history_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.node_edit_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.outline_tree_dock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.chat_history_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.show_GSN_dock)

        #  Default Display Window 
        self.resource_mng_dock.hide()
        self.history_dock.hide()
        self.node_edit_dock.hide()
        self.outline_tree_dock.hide()
        self.chat_history_dock.hide()
        self.show_GSN_dock.hide()

    def btnWinFileTreeOnClick(self):
        #  Open and close the file tree window 
        print('btnWinFileTreeOnClick')
        if self.resource_mng_dock.isHidden():
            self.resource_mng_dock.show()
        else:
            self.resource_mng_dock.hide()

    def btnWinNodeEditOnClick(self):
        #  Open and close node editing 
        print('btnWinNodeEditOnClick')
        if self.node_edit_dock.isHidden():
            self.node_edit_dock.show()
            self.resetMyDiagramDivHeight()
        else:
            self.node_edit_dock.hide()
            self.resetMyDiagramDivHeight(self.height())

    def btnWinHistoryOnClick(self):
        #  Open and close node editing 
        print('btnWinHistoryOnClick')
        if self.history_dock.isHidden():
            self.history_dock.show()
        else:
            self.history_dock.hide()

    def btnWinOutlineOnClick(self):
        #  Open and close the outline view 
        print('btnWinOutlineOnClick')
        if self.outline_tree_dock.isHidden():
            #  Regenerate outline tree 
            outline_tree_view = self.dockDataTreeView()
            self.outline_tree_dock.setWidget(outline_tree_view)

            self.outline_tree_dock.show()
        else:
            self.outline_tree_dock.hide()

    def btnWinChatHistoryOnClick(self):
        #  Open and close chat history 
        print('btnWinChatHistoryOnClick')
        if self.chat_history_dock.isHidden():
            self.chat_history_dock.show()
        else:
            self.chat_history_dock.hide()

    def btnWinShowGSNOnClick(self):
        #  Open Close GSN Small window 
        print('btnWinShowGSNOnClick')
        if self.show_GSN_dock.isHidden():
            self.show_GSN_dock.show()
            self.resetMyDiagramDivHeight()
        else:
            self.show_GSN_dock.hide()
            self.resetMyDiagramDivHeight(self.height())

    def btnWinOverviewOnClick(self):
        #  Open and close node editing 
        print('btnWinOverviewOnClick')

        with open(self.url_gojs, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i in range(len(lines)):
            if lines[i].find('    setMyOverviewDivSize') != 0:
                continue
            if 0 == lines[i].find('    setMyOverviewDivSize(0'):
                lines[i] = '    setMyOverviewDivSize(200, 200);\n'
            else:
                lines[i] = '    setMyOverviewDivSize(0, 0);\n'
            break

        with open(self.url_gojs, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        #  Refresh Display 
        self.btnFlashOnClick()

    def dockDataTreeView(self):
        tree = QTreeView(self)
        self.model_tree_view = QStandardItemModel()
        self.model_tree_view.setHorizontalHeaderLabels([HAN_EN.get('Description')])
        tree.header().setDefaultSectionSize(380)
        tree.setModel(self.model_tree_view)

        #  Data preprocessing: settings parent_id
        data = []
        for node in self.dataService.nodeDataArray:
            str_parentIDs, cnt = self.dataService.getParentIDs(node['key'])
            # if cnt != 1: #  Only one parent node 
            #     print('Err: only one father node.')
            #     continue
            if cnt == 0: #  Without a parent node, it is the root node 
                node['parent_id'] = 0
                data.append(node)
            else: #  There is a parent node, set pid . (Multiple parent node scenes, not recursively displayed, only displayed) 1 Layer) 
                list_parentIDs = str_parentIDs.split(' ')
                for parentID in list_parentIDs:
                    tmp_node = deepcopy(node)
                    tmp_node['parent_id'] = int(parentID)
                    data.append(tmp_node)

        self.makeDataTreeView(data)
        tree.expandAll()

        return tree
    
    def makeDataTreeView(self, data, root=None):
        self.model_tree_view.setRowCount(0)
        if root is None:
            root = self.model_tree_view.invisibleRootItem()
        seen = {}   # Dictionary of QStandardItem
        values = deque(data)
        retry_counts = {}  # Dictionary to track the number of retries for each item
        max_retries = 10   # Maximum number of retries before giving up on an item

        while values:
            value = values.popleft()
            unique_id = value['key']
            pid = value['parent_id']

            # Check if the item has exceeded the maximum number of retries
            if retry_counts.get(unique_id, 0) > max_retries:
                print(f"Skipping item with unique_id {unique_id} after {max_retries} retries.")
                continue

            if pid == 0:
                # Special handling for the first node, treat it as root
                node = [
                    QStandardItem(value['question']),
                ]
                root.appendRow(node)
                seen[unique_id] = root.child(root.rowCount() - 1)
                first_node = False
                continue

            if pid not in seen:
                values.append(value)
                retry_counts[unique_id] = retry_counts.get(unique_id, 0) + 1
                print('continue', value)
                continue

            parent = seen[pid]
            print(value)
            parent.appendRow([
                QStandardItem(value['question']),
            ])
            seen[unique_id] = parent.child(parent.rowCount() - 1)
            # Reset the retry count for the item as it has been successfully added
            retry_counts[unique_id] = 0

    def dockNodeEditTable(self, list_field=None):
        model = QStandardItemModel(9,2)
        model.setHorizontalHeaderLabels([HAN_EN.get('Field'), HAN_EN.get('Value')])

        tableview = QTableView()
        tableview.setModel(model)
        tableview.setColumnWidth(0, 200)
        tableview.setColumnWidth(1, 1290)

        #  Add data 
        if not list_field:
            list_field = [
                (HAN_EN.get('Node ID'), '22'),
                (HAN_EN.get('Description'), 'Message sending time of module A is less than 0.5ms'),
                # (HAN_EN.get('Node Type'), '22'),
                (HAN_EN.get('Reason Type'), 'Default'),
                (HAN_EN.get('Formal Expressions'), 'send_time<1.5'),
                (HAN_EN.get('Relationship'), 'And'),
                # (HAN_EN.get('Quantitative Info'), '22'),
                (HAN_EN.get('Parent ID'), '19'),
            ]

        for i in range(len(list_field)):
            item_key = QStandardItem(list_field[i][0])
            item_value = QStandardItem(list_field[i][1])
            model.setItem(i, 0, item_key)
            model.setItem(i, 1, item_value)

        return tableview

    def connSlot(self):
        # csv File action 
        self.actNew.triggered.connect(self.btnNewOnClick)
        self.actAutoSave.triggered.connect(self.btnAutoSaveOnClick)
        self.actJsonOpen.triggered.connect(self.btnJsonOpenOnClick)
        self.actJsonSave.triggered.connect(self.btnJsonSaveOnClick)
        self.actJsonSaveAs.triggered.connect(self.btnJsonSaveAsOnClick)

        self.actPythonCodeOpen.triggered.connect(self.btnPythonCodeOpenOnClick)
        self.actDotOpen.triggered.connect(self.btnDotOpenOnClick)

        self.actYamlOpen.triggered.connect(self.btnYamlOpenOnClick)
        self.actYamlSave.triggered.connect(self.btnYamlSaveOnClick)
        self.actYamlSaveAs.triggered.connect(self.btnYamlSaveAsOnClick)

        self.actCsvImp.triggered.connect(self.btnCsvImpOnClick)
        self.actCsvSave.triggered.connect(self.btnCsvSaveOnClick)
        self.actCsvExp.triggered.connect(self.btnCsvExpOnClick)
#         self.actCsvMerge.triggered.connect(self.btnCsvMergeOnClick)
#         self.actFormalExp.triggered.connect(self.btnFormalExpOnClick)

        #  Edit node action 
        self.actFlash.triggered.connect(partial(self.btnFlashOnClick, True))
        self.actAdd.triggered.connect(self.btnAddOnClick)
        self.actDel.triggered.connect(self.btnDelOnClick)
        self.actEdit.triggered.connect(self.btnEditOnClick)
#         self.actAutoAdd.triggered.connect(self.btnAutoAddOnClick)
        self.actPruneNode.triggered.connect(self.btnCaseAdjustGraphOnClick)
        self.actAddAddition.triggered.connect(self.btnAddAdditionOnClick)

        # prolog action 
#         self.actPrologImp.triggered.connect(self.btnPrologImpOnClick)
#         self.actPrologExp.triggered.connect(self.btnPrologExpOnClick)
#         self.actPrologCheck.triggered.connect(self.btnPrologCheckOnClick)

        #  view 
        self.actTransAngle.triggered.connect(self.btnTransAngleOnClick)
        self.actNodeWidth.triggered.connect(self.btnNodeWidthOnClick)
        self.actNodesHighlight.triggered.connect(self.btnNodesHighlightOnClick)
        self.actNodesMode.triggered.connect(self.btnNodesModeOnClick)
        self.actStrategySwitch.triggered.connect(self.btnStrategySwitchOnClick)

        #  translate 
#         self.actTranslateEn.triggered.connect(self.btnTranslateEnOnClick)
#         self.actTranslateZh.triggered.connect(self.btnTranslateZhOnClick)
#         self.actTranslate.triggered.connect(self.btnTranslateOnClick)
        self.actToGSN.triggered.connect(self.btnToGSNOnClick)

        #  Left toolbar 
#         self.actWinFileTree.triggered.connect(self.btnWinFileTreeOnClick)
        self.actWinNodeEdit.triggered.connect(self.btnWinNodeEditOnClick)
        self.actWinOverview.triggered.connect(self.btnWinOverviewOnClick)
        self.actWinHistory.triggered.connect(self.btnWinHistoryOnClick)
        self.actWinOutline.triggered.connect(self.btnWinOutlineOnClick)
#         self.actWinChatHistory.triggered.connect(self.btnWinChatHistoryOnClick)
        self.actWinShowGSN.triggered.connect(self.btnWinShowGSNOnClick)

        # SafetyCase
#         self.actSafetyCase.triggered.connect(self.btnSafetyCaseOnClick)
#         self.actDSTheory.triggered.connect(self.btnDSTheoryOnClick)
#         self.actAutoEvaluate.triggered.connect(self.btnAutoEvaluateOnClick)
        #  Constraint proof 
#         self.actConstraintFormal.triggered.connect(self.btnConstraintFormalOnClick)
#         self.actConstraintProve.triggered.connect(self.btnConstraintProveOnClick)
        # self.proveTreeEdit.returnPressed.connect(self.btnConstraintProveOnClick)
        #  search 
        self.actSearch.triggered.connect(self.btnSearchOnClick)
        self.searchEdit.returnPressed.connect(self.btnSearchOnClick)

        #  case study  
#         self.actCaseAddGoals.triggered.connect(self.btnCaseAddGoalsOnClick)
#         self.actCaseCreateGoals.triggered.connect(self.btnCaseCreateGoalsOnClick)
#         self.actCaseEvaluateSimilar.triggered.connect(self.btnCaseEvaluateSimilarOnClick)
#         self.actCaseDrawChart.triggered.connect(self.btnCaseDrawChartOnClick)

#         self.actCaseOneStep.triggered.connect(self.btnCaseOneStepOnClick)
#         self.actCaseLoadCallGraph.triggered.connect(self.btnCaseLoadCallGraphOnClick)
#         self.actCaseAdjustGraph.triggered.connect(self.btnCaseAdjustGraphOnClick)
        self.actFuncAnalysis.triggered.connect(self.btnCaseFuncAnalysisOnClick)
#         self.actCaseFuncAnalysis.triggered.connect(self.btnCaseFuncAnalysisOnClick)
#         self.actCaseInitToContext.triggered.connect(self.btnCaseInitToContextOnClick)
#         self.actCaseAddSolution.triggered.connect(self.btnCaseAddSolutionOnClick)

#         self.actCaseEvalCallPathCompare.triggered.connect(self.btnCaseEvalCallPathCompareOnClick)
#         self.actCaseUnitTestParse.triggered.connect(self.btnCaseUnitTestParseOnClick)

    def btnCaseUnitTestParseOnClick(self):
        print('btnCaseUnitTestParseOnClick')
        fail_node_ids = self.dataService.flagFailSolution(unit_test_log_path='func_analysis_llm/callgraph_data/unit_test.log')

        self.dataService.setNodesHighlight(fail_node_ids, frameColor='#FFFF66')
        #  Refresh Display 
        self.btnFlashOnClick()

        self.textBox = textbox.TextBox(' Evaluation result: Failed test cases ', json.dumps(fail_node_ids, ensure_ascii=False))
        self.textBox.readOnly()
        self.textBox.exec_()

    def btnCaseEvalCallPathCompareOnClick(self):
        print('btnCaseEvalCallPathCompareOnClick')
        list_diff_node = self.dataService.compareOtherJson('func_analysis_llm/callgraph_data/3-load_fail.json')

        list_ID = [node['key'] for node in list_diff_node]
        self.dataService.setNodesHighlight(list_ID, frameColor='#FFFF66')
        #  Refresh Display 
        self.btnFlashOnClick()

        self.textBox = textbox.TextBox(' Evaluation results ', json.dumps(list_diff_node, indent=4, ensure_ascii=False))
        self.textBox.readOnly()
        self.textBox.exec_()

    def btnCaseOneStepOnClick(self):
        print('btnCaseOneStepOnClick')
        self.btnCaseLoadCallGraphOnClick()
        self.btnCaseAdjustGraphOnClick()
        self.btnCaseFuncAnalysisOnClick()
        self.btnCaseInitToContextOnClick()
        self.btnCaseAddSolutionOnClick()

    def btnCaseAddSolutionOnClick(self):
        print('btnCaseAddSolutionOnClick')
        self.dataService.AddSolutions()
        #  Refresh Display 
        self.btnFlashOnClick()

    def btnCaseInitToContextOnClick(self):
        print('btnCaseInitToContextOnClick')
        self.dataService.InitNodeToContext()
        #  Refresh Display 
        self.btnFlashOnClick()

    def btnCaseLoadCallGraphOnClick(self):
        print('btnCaseLoadCallGraphOnClick')
        self.dataService.loadDot('func_analysis_llm/callgraph_data/2-load_infer.dot')
        #  Refresh Display 
        self.btnFlashOnClick()

    def btnCaseAdjustGraphOnClick(self):
        print('btnCaseAdjustGraphOnClick')
        config = self.dataService.get_config()

        #  adjustment 1 : Keep only related functions 
        list_need_keyword = config.get('FUNCTION_NEED_KEYWORDS', [])
        for keyword in list_need_keyword:
            not_like_nodes = self.dataService.searchNodeNotLikeAddition(searchKey=keyword)
            for node in not_like_nodes:
                self.dataService.delNode(node['key'])

        #  adjustment 2 Ignore some functions again 
        list_del_keyword = config.get('FUNCTION_IGNORE_KEYWORDS', [])
        # list_del_keyword = [] #  Close adjustment 
        for keyword in list_del_keyword:
            like_nodes = self.dataService.searchNodeByLikeName(searchKey=keyword)
            for node in like_nodes:
                self.dataService.delNode(node['key'])

        #  adjustment 3 : Preserve the main tree structure 
        proveRootText = self.proveTreeEdit.text()
        if proveRootText:
            proveRootID, proveLevel = self.get_select_subtree()
            if proveRootID == -1:
                return False
            #  Selected tree nodes ID
            list_descendant_ids = []
            self.dataService.getDescendantIDs(proveRootID, list_descendant_ids, proveLevel)

            #  Delete unselected nodes 
            self.dataService.delNodesExcept(list_descendant_ids)


        self.dataService.setAllNodeMode('Addition')
        #  Refresh Display 
        self.btnFlashOnClick()

    def btnCaseFuncAnalysisOnClick(self, ID=None, level=None):
        print('btnCaseFuncAnalysisOnClick')
        if not ID:
            proveRootID, proveLevel = self.get_select_subtree()
            if proveRootID == -1:
                return False
        else:
            proveRootID = ID
            proveLevel = level
        
        temperature = float(self.temperatureEdit.text())
        is_ok, list_ID, list_error_info = self.dataService.functionAnalysisLLM(proveRootID, proveLevel, temperature)

        if not is_ok:
            info = f'Info: {len(list_ID)} succeeded and {len(list_error_info)} failed!\n' + json.dumps(list_error_info, indent=2)
            QMessageBox.information(self, "information", info)
        
        self.dataService.setDSColor(list_ID)
        self.dataService.setNodesHighlight(list_ID, frameColor='GreenYellow', nameTextColor='black')
        self.dataService.setAllNodeMode('DS_Addition')
        if len(list_ID) > 0:
            self.set_center_node(list_ID[-1])
        #  Refresh Display 
        self.btnFlashOnClick()


    def btnCaseEvaluateSimilarOnClick(self):
        print('btnCaseEvaluateSimilarOnClick')
        # temperature = float(self.temperatureEdit.text())
        # self.dataService.evaluateSimilar(temperature=0) #  use 0 More stable evaluation 
        self.dataService.evaluateSimilarAPI(compare_data_path='auto_build_llm/history_data/compare_data_temp-0.8.json',
                                            field_name='similarity_baidu') # baidu API assessment 


    def btnCaseDrawChartOnClick(self):
        print('btnCaseDrawChartOnClick')
        #  Dialogue box display 
        # self.cd = chartdialog.ChartDialog()
        # self.cd.exec_()

        #  New process display 
        os.system('python auto_build_llm/show_chart.py')


    def btnCaseCreateGoalsOnClick(self):
        print('btnCaseCreateGoalsOnClick')
        self.ccf = caseconfigform.CaseConfigForm(' Comparison of Case Data Creation ')
        result = self.ccf.exec_()
        if result != QDialog.Accepted:
            return False
        
        domain = self.ccf.getData()['domain']
        creator = self.ccf.getData()['creator']
        print(domain, creator)

        #  Obtain divergence 
        temperature = float(self.temperatureEdit.text())
        self.dataService.createCompareData(domain, creator, temperature)


    def btnCaseAddGoalsOnClick(self):
        print('btnCaseAddGoalsOnClick')
        self.ccf = caseconfigform.CaseConfigForm(' Add the current tree to the case data ')
        result = self.ccf.exec_()
        if result != QDialog.Accepted:
            return False
        
        domain = self.ccf.getData()['domain']
        creator = self.ccf.getData()['creator']
        print(domain, creator)

        #  Get the root node of the operation 
        proveRootID, proveLevel = self.get_select_subtree()
        if proveRootID == -1:
            return False

        self.dataService.addToCompareData(proveRootID, proveLevel, domain, creator)

    def btnAutoSaveOnClick(self):
        print('btnAutoSaveOnClick')
        if self.current_file == '' or self.current_encoding == '':
            # QMessageBox.error(self, " error ", " Save failed! Please save as JSON or CSV Format. ")
            self.btnJsonSaveOnClick()
            return True
        
        if self.current_file.endswith('.json'):
            self.btnJsonSaveOnClick()
        elif self.current_file.endswith('.yaml'):
            self.btnYamlSaveOnClick()
        elif self.current_file.endswith('.csv'):
            self.btnCsvSaveOnClick()
        elif self.current_file.endswith('.dot'):
            self.btnJsonSaveAsOnClick()
        else:
            print(self.current_file)
            QMessageBox.error(self, " error ", " Save failed! The file type is not supported. ")
            return False
        
    def btnPythonCodeOpenOnClick(self):
        print('btnPythonCodeOpenOnClick')
        dialog_width = 500
        dialog_height = self.height()
        dialog_x = self.x() - dialog_width
        dialog_y = self.geometry().y()

        self.c2gForm = code2gsndialog.CodeExecutionDialog(self)
        self.c2gForm.setGeometry(dialog_x, dialog_y, dialog_width, dialog_height)
        self.c2gForm.show()

    def btnDotOpenOnClick(self, dot_path=None):
        print('btnDotOpenOnClick')

        if dot_path:
            srcFilePath = dot_path
            retainTreeSwitch = HAN_EN.get('No')
            encoding = 'utf-8'
        else:
            self.dotImpForm = csvimpform.CsvImpForm("Open .dot", list_encoding=['utf-16', 'utf-8'])
            result = self.dotImpForm.exec_()
            if result != QDialog.Accepted:
                return False

            srcFilePath = self.dotImpForm.getFilePath()
            retainTreeSwitch = self.dotImpForm.getRetainTree()
            encoding = self.dotImpForm.getEncoding()

            # Step 0: Copy config.json
            work_path = os.path.dirname(srcFilePath)
            config_path = os.path.join(work_path, 'config.json')
            if os.path.exists(config_path):
                shutil.copyfile(config_path, 'config.json')

        print(srcFilePath, retainTreeSwitch, encoding)

        #  Clear the cache of the previous project 
        self.dataService.src_func_data = None

        #  from dot File Open Data 
        err = self.dataService.loadDot(srcFilePath, encoding)
        if err != '':
            QMessageBox.critical(self, "Error", "%s Open failed!" % err)
            return False

        self.color_fill_stroke(is_gsn=False)

        history.log('Open [%s]' % srcFilePath)
        self.changeCsvFile(srcFilePath, encoding)

        
        self.dataService.setAllNodeMode('Addition')
        #  Refresh Display 
        self.btnFlashOnClick()

    def btnYamlOpenOnClick(self):
        print('btnYamlOpenOnClick')
        self.yamlImpForm = csvimpform.CsvImpForm("Open .yaml", list_encoding=['utf-8'])
        result = self.yamlImpForm.exec_()
        if result != QDialog.Accepted:
            return False

        srcFilePath = self.yamlImpForm.getFilePath()
        retainTreeSwitch = self.yamlImpForm.getRetainTree()
        encoding = self.yamlImpForm.getEncoding()

        print(srcFilePath, retainTreeSwitch, encoding)

        #  from yaml File Open Data 
        err = self.dataService.yamlImport(srcFilePath, encoding)
        if err != '':
            QMessageBox.critical(self, " error ", "%s ！ Open failed " % err)
            return False

        history.log(' open [%s] data ' % srcFilePath)
        self.changeCsvFile(srcFilePath, encoding)

        #  Refresh Display 
        self.btnFlashOnClick()

    def btnYamlSaveOnClick(self):
        print('btnYamlSaveOnClick')
        try:
            if self.current_file != '' and self.current_encoding != '':
                self.dataService.yamlExport(self.current_file, self.current_encoding)
                history.log(' preservation [%s] data ' % self.current_file)
            else:
                ret = self.btnYamlSaveAsOnClick()
                if ret != False:
                    history.log(' Data has been saved to a new file [%s]' % ret)
        except:
            QMessageBox.warning(self, " warning ", " Save failed! The file may be occupied , {}".format(traceback.format_exc()))
            traceback.print_exc()
            return False

        self.needSaveUI(False)

    def btnYamlSaveAsOnClick(self):
        print('btnYamlSaveAsOnClick')
        self.yamlExpForm = csvexpform.CsvExpForm("Save As .yaml", list_encoding=['utf-8'])
        result = self.yamlExpForm.exec_()
        if result != QDialog.Accepted:
            return False

        dstFilePath = self.yamlExpForm.getFilePath()
        encoding = self.yamlExpForm.getEncoding()

        print(dstFilePath, encoding)

        #  Save as Data to json file 
        err = self.dataService.yamlExport(dstFilePath, encoding)
        if err != '':
            QMessageBox.critical(self, " error ", "%s ！ Save failed " % err)
            return False

        history.log(' Save as [%s] data ' % dstFilePath)
        self.changeCsvFile(dstFilePath, encoding)

        QMessageBox.information(self, ' Tips ', ' The data has been saved as to  [%s]' % dstFilePath, QMessageBox.Yes)
        return dstFilePath

    def btnJsonOpenOnClick(self):
        print('btnJsonOpenOnClick')
        self.jsonImpForm = csvimpform.CsvImpForm("Open .json", list_encoding=['utf-8'])
        result = self.jsonImpForm.exec_()
        if result != QDialog.Accepted:
            return False

        srcFilePath = self.jsonImpForm.getFilePath()
        retainTreeSwitch = self.jsonImpForm.getRetainTree()
        encoding = self.jsonImpForm.getEncoding()

        print(srcFilePath, retainTreeSwitch, encoding)

        #  from json File Open Data 
        err = self.dataService.jsonImport(srcFilePath, encoding)
        if err != '':
            QMessageBox.critical(self, " error ", "%s ！ Open failed " % err)
            return False

        history.log(' open [%s] data ' % srcFilePath)
        self.changeCsvFile(srcFilePath, encoding)

        #  Refresh Display 
        self.btnFlashOnClick()

    def btnJsonSaveOnClick(self):
        print('btnJsonSaveOnClick')
        try:
            if self.current_file != '' and self.current_encoding != '':
                self.dataService.jsonExport(self.current_file, self.current_encoding)
                history.log(' preservation [%s] data ' % self.current_file)
            else:
                ret = self.btnJsonSaveAsOnClick()
                if ret != False:
                    history.log(' Data has been saved to a new file [%s]' % ret)
        except:
            QMessageBox.warning(self, " warning ", " Save failed! The file may be occupied , {}".format(traceback.format_exc()))
            traceback.print_exc()
            return False

        self.needSaveUI(False)

    def btnJsonSaveAsOnClick(self):
        print('btnJsonSaveAsOnClick')
        self.jsonExpForm = csvexpform.CsvExpForm("Save As .json", list_encoding=['utf-8'])
        result = self.jsonExpForm.exec_()
        if result != QDialog.Accepted:
            return False

        dstFilePath = self.jsonExpForm.getFilePath()
        encoding = self.jsonExpForm.getEncoding()

        print(dstFilePath, encoding)

        #  Save as Data to json file 
        err = self.dataService.jsonExport(dstFilePath, encoding)
        if err != '':
            QMessageBox.critical(self, " error ", "%s ！ Save failed " % err)
            return False

        history.log(' Save as [%s] data ' % dstFilePath)
        self.changeCsvFile(dstFilePath, encoding)

        QMessageBox.information(self, ' Tips ', ' The data has been saved as to  [%s]' % dstFilePath, QMessageBox.Yes)
        return dstFilePath

    def btnTranslateEnOnClick(self):
        print('btnTranslateEnOnClick')
        self.dataService.translateTo('en')
        self.current_language = 'en'
        self.setWindowTitle(self.makeWindowTitle())

        #  Refresh Display 
        self.btnFlashOnClick()

    def btnTranslateZhOnClick(self):
        print('btnTranslateZhOnClick')
        self.dataService.translateTo('zh')
        self.current_language = 'zh'
        self.setWindowTitle(self.makeWindowTitle())

        #  Refresh Display 
        self.btnFlashOnClick()
    
    def btnTranslateOnClick(self):
        print('btnTranslateOnClick')
        if self.current_language == 'en':
            self.btnTranslateZhOnClick()
        elif self.current_language == 'zh':
            self.btnTranslateEnOnClick()
        else:
            QMessageBox.critical(self, " warning ", " Please perform a specified language translation first. ")
            return
        #  Refresh Display 
        self.btnFlashOnClick()

    def btnToGSNOnClick(self):
        print('btnToGSNOnClick')
        # print(self.dataService.json('ds.json'))
        if self.url == self.url_gsn:
            self.url = self.url_gojs
        else: #  generate gsn chart 
            #  Obtain proof of root node 
            proveRootID, proveLevel = self.get_select_subtree()
            if proveRootID == -1:
                return False

            #  generate yaml
            str_yaml = self.dataService.toGsnYaml(proveRootID, proveLevel)
            #  generate gsn chart 
            self.create_gsn_svg(str_yaml)

            #  display GSN
            self.url = self.url_gsn

        #  Refresh Display 
        self.btnFlashOnClick()
    
    #  Generated svg Definitely and yaml Same directory, cannot be modified. When multiple are generated simultaneously, they can be backed up, replicated, and called consecutively. 
    def create_gsn_svg(self, str_yaml):
        code_path = os.path.abspath('./history/tmp_gsn2x_code.yaml')
        with open(code_path, 'w', encoding='utf-8') as f:
            f.write(str_yaml)

        #  generate svg chart 
        curr_dir = os.getcwd()
        os.chdir('../bin/gsn2x')
        cmd = r'gsn2x-v2.7.4.exe %s' % os.path.relpath(code_path)
        # cmd = r'gsn2x-v3.0.0.exe %s -w 32' % os.path.relpath(code_path)
        with os.popen(cmd + ' 2>&1') as pf:
            output = pf.read()
            if output:
                # QMessageBox.critical(self, " error ", " generate GSN Failed: %s" % (output))
                print(" generate GSN Failed: %s" % (output))
            print(output)
        os.chdir(curr_dir)
        return code_path.replace('.yaml', '.svg')
        
    def btnSearchOnClick(self):
        print('btnSearchOnClick')
        search_result = []
        #  Find nodes 
        searchText = self.searchEdit.text()
        like_nodes = self.dataService.searchNodeByLikeName(searchText)

        #  Splicing information 
        for node in like_nodes:
            node_id = node["key"]
            #  Get node path 
            list_IDs = []
            self.dataService.getPathParentIDs(node_id, list_IDs)
            list_IDs = list_IDs[::-1] + [node_id]
            #  output 
            search_result.append({
                HAN_EN.get("Description"): self.dataService.getNodeName(node),
                HAN_EN.get("ID Path"): '->'.join([str(ID) for ID in list_IDs[1:]])
            })

        #  Dialogue box display 
        str_result = json.dumps(search_result, ensure_ascii=False, indent=2)
        self.prologForm = prologform.PrologForm('The node containing "%s"' % searchText, str_result)
        self.prologForm.initExportUI()
        self.prologForm.setWindowModality(Qt.WindowModal) #  Non modal dialog box, non blocking 
        self.prologForm.exec_()


    def btnFlashOnClick(self, is_actFlash=False):
        print('btnFlashOnClick')
        self.browser.load(QUrl.fromLocalFile(self.url))
        self.dataService.setAllNodeWidth(self.all_node_width)
        if is_actFlash:
            self.dataService.cleanAllColor()
        self.needSaveUI(True)

    def btnFlashCsvOnClick(self):
        print('btnFlashCsvOnClick')
        if self.current_file == '':
            QMessageBox.critical(self, " error ", " Target file without refresh ")
            return
        list_notImpNode, err = self.dataService.csvImport(self.current_file, HAN_EN.get("No"), self.current_encoding)
        if err != '':
            QMessageBox.critical(self, " error ", "[%s] %s ！ Open failed " % (self.current_file, err))
        else:
            history.log(' refresh data [%s]' % self.current_file)
        self.needSaveUI(True)
        #  Refresh Display 
        self.btnFlashOnClick()

    def btnAutoAddOnClick(self, ID=None, level=None):
        print('btnAutoAddOnClick')
        #  Obtain proof of root node 
        if not ID:
            proveRootID, proveLevel = self.get_select_subtree()
            if proveRootID == -1:
                return False
        else:
            proveRootID = ID
            proveLevel = level
        
        #  Obtain divergence 
        temperature = float(self.temperatureEdit.text())

        self.AutoAddNode(proveRootID, proveLevel, temperature)

    def AutoAddNode(self, parentID, level, temperature):
        if level <= 0:
            return []
        level -= 1

        list_subIDs = self.dataService.autoAddSubNodes(parentID, level, temperature)
        for ID in list_subIDs:
            self.AutoAddNode(ID, level, temperature)
        
        self.needSaveUI(True)
        self.set_center_node(parentID) #  Set the center node 
        #  Refresh Display 
        self.btnFlashOnClick()

    def btnAddOnClick(self, parentID=''):
        print('btnAddOnClick')
        self.addForm = addform.AddForm(parentID)
        result = self.addForm.exec_()
        if result != QDialog.Accepted:
            return False

        parentID = self.addForm.getParentID()
        nodeName = self.addForm.getNodeName()
        attribute = self.addForm.getAttribute()
        nodeType = self.addForm.getNodeType()
        reason = self.addForm.getReason()

        ifContent = self.addForm.getIfContent()
        thenContent = self.addForm.getThenContent()
        DSTheory = self.addForm.getDSTheoryContent()
        Addition = self.addForm.getAdditionContent()

        if ifContent:
            content = 'IF {} THEN {}'.format(ifContent, thenContent)
        else:
            content = thenContent

        print(parentID, nodeName, content, attribute, nodeType, reason, DSTheory, Addition)

        #  Add data to js file 
        ID = self.dataService.addNode((parentID, nodeName, content, attribute, nodeType, reason, DSTheory, Addition))
        history.log(' Add node: %s' % nodeName)
        self.needSaveUI(True)

        self.set_center_node(ID) #  Set the center node 
        #  Refresh Display 
        self.btnFlashOnClick()

    def btnDelOnClick(self, ID=None):
        print('btnDelOnClick')
        if not ID:
            self.delForm = delform.DelForm()
            result = self.delForm.exec_()
            if result != QDialog.Accepted:
                return False

            ID = self.delForm.getID()
        print(ID)

        str_parentIDs, cnt = self.dataService.getParentIDs(ID)
        parentID = str_parentIDs.split(' ')[0]

        #  Delete data to js file 
        self.dataService.delNodes(ID)
        history.log(' Delete node: %s' % ID)
        self.needSaveUI(True)

        self.set_center_node(parentID) #  Set the center node 
        #  Refresh Display 
        self.btnFlashOnClick()

    def btnEditOnClick(self, ID=None):
        print('btnEditOnClick')

        if not ID:
            ID, okPressed = QInputDialog.getInt(self, HAN_EN.get("Edit"), HAN_EN.get('Please enter the node ID'), 1, 0, 10000, 1)
            if not okPressed:
                return False

        info = self.dataService.findNodeByKey(ID)
        print(info)

        self.editForm = editform.EditForm(info)
        result = self.editForm.exec_()
        if result != QDialog.Accepted:
            return False

        info.parentID = self.editForm.getParentID()
        info.nodeName = self.editForm.getNodeName()
        info.nodeType = self.editForm.getNodeType()
        info.reason = self.editForm.getReason()
        info.attribute = self.editForm.getAttribute()
        info.DSTheory = self.editForm.getDSTheoryContent()
        info.Addition = self.editForm.getAdditionContent()
        info.nodeWidth = self.editForm.getNodeWidth()

        ifContent = self.editForm.getIfContent()
        thenContent = self.editForm.getThenContent()
        if ifContent:
            info.content = 'IF {} THEN {}'.format(ifContent, thenContent)
        else:
            info.content = thenContent

        print(info)

        #  Edit data to js file 
        self.dataService.editNode(ID, info)
        history.log(' Edit Node: %d %s' % (ID, info.nodeName))
        self.needSaveUI(True)

        self.set_center_node(ID) #  Set the center node 
        #  Refresh Display 
        self.btnFlashOnClick()

    def btnAddAdditionOnClick(self, ID=None, Type=None):
        print('btnAddAdditionOnClick')

        self.additionForm = additionform.AdditionForm(ID, Type)
        result = self.additionForm.exec_()
        if result != QDialog.Accepted:
            return False

        ID = int(self.additionForm.getID())
        Type = self.additionForm.getType()
        Content = self.additionForm.getContent()

        self.dataService.setAddAddition(ID, Type, Content)

        self.needSaveUI(True)
        self.set_center_node(ID) #  Set the center node 
        self.dataService.setAllNodeMode('DS_Addition')
        #  Refresh Display 
        self.btnFlashOnClick()

    def btnPrologImpOnClick(self, content = ''):
        print('btnPrologImpOnClick')

        self.prologForm = prologform.PrologForm('Prolog Import', content)
        result = self.prologForm.exec_()
        if result != QDialog.Accepted:
            return False

        content = self.prologForm.getContent()
        switch = self.prologForm.getSwitch()
        quotesSwitch = self.prologForm.getQuotesSwitch()

        print(content, switch, quotesSwitch)

        if ':-' not in content:
            self.dataService.nodeDataArray.clear()
            self.dataService.linkDataArray.clear()
            self.dataService.addNodeByName(0, content)
            self.newCsvFile()
            #  Refresh Display 
            self.btnFlashOnClick()
            return

        # prolog Import data into js file 
        ret = self.dataService.prologImport((content, switch, quotesSwitch))
        if not ret:
            QMessageBox.warning(self, ' warning ', 'prolog Data is incorrect ,  Please revise. ', QMessageBox.Yes)
            with open('prolog.txt', 'w', encoding='utf-8') as f:
                f.write(content)
            self.btnPrologImpOnClick()
            return False
        history.log(' Import Prolog data ')
        self.newCsvFile()
        self.needSaveUI(True)

        #  Refresh Display 
        self.btnFlashOnClick()

    def btnPrologExpOnClick(self):
        print('btnPrologExpOnClick')
        #  export prolog data 
        filePath = './prolog.txt'
        list_line = self.dataService.prologExport()
        list_line = sorted(set(list_line), key=list_line.index) #  Go ahead and repeat , Keep order 

        prolog_data = '\n'.join(list_line)
        self.prologForm = prologform.PrologForm('Prolog Export', prolog_data)
        self.prologForm.initExportUI()
        result = self.prologForm.exec_()
        if result != QDialog.Accepted:
            return False

        content = self.prologForm.getContent()
        switch = self.prologForm.getSwitch()

        print(content, switch)

        #  write file 
        with open(filePath, 'w', encoding='utf-8') as f:
            f.write(content)
        history.log(' export Prolog data ')

    def btnPrologCheckOnClick(self):
        print('btnPrologCheckOnClick')
        # 1.  Obtain evidence and formulas 
        list_line = self.dataService.prologExport(is_content=True)
        list_line.extend(self.dataService.getAllEvidenceContent())
        list_line = sorted(set(list_line), key=list_line.index) #  Go ahead and repeat , Keep order 
        prolog_data = '\n'.join(list_line)
        rules_text = prolog_data

        # 2.  Get top-level declaration (target) 
        root_node = self.dataService.getRootNode()
        top_claim = root_node.content
        query_text, have_not = self.dataService.anlyTopClaim(top_claim)

        # 3.  reasoning 
        state_info = []
        state = py_prolog_solver.run_query(rules_text, query_text, state_info)
        node_state = self.dataService.getNodeState(state, state_info, have_not)

        # 4.  display 
        self.dataService.setNodeColor(root_node.nodeID, node_state)
        self.btnFlashOnClick() #  Refresh tree display 
        py_prolog_editer.main(rules_text, query_text, state_info) #  open prolog dialog box 
        history.log(' verification Prolog data ')

    def btnCsvExpOnClick(self):
        print('csv  Save as ')
        self.csvExpForm = csvexpform.CsvExpForm("Save As .csv")
        result = self.csvExpForm.exec_()
        if result != QDialog.Accepted:
            return False

        dstFilePath = self.csvExpForm.getFilePath()
        encoding = self.csvExpForm.getEncoding()

        print(dstFilePath, encoding)

        #  Save as Data to csv file 
        err = self.dataService.csvExport(dstFilePath, encoding)
        if err != '':
            QMessageBox.critical(self, " error ", "%s ！ Save failed " % err)
            return False

        history.log(' Save as [%s] data ' % dstFilePath)
        self.changeCsvFile(dstFilePath, encoding)

        QMessageBox.information(self, ' Tips ', ' The data has been saved as to  [%s]' % dstFilePath, QMessageBox.Yes)
        return dstFilePath

    def btnCsvMergeOnClick(self):
        print('csv  merge ')
        self.csvMergeForm = csvmergeform.CsvMergeForm()
        result = self.csvMergeForm.exec_()
        if result != QDialog.Accepted:
            return False

        srcFilePath = self.csvMergeForm.getFilePath()
        encoding = self.csvMergeForm.getEncoding()
        mountNodeID = self.csvMergeForm.getMountNode()

        print(srcFilePath, encoding, mountNodeID)

        #  from csv File Open Data 
        err = self.dataService.csvMerge(srcFilePath, encoding, mountNodeID)
        if err != '':
            QMessageBox.critical(self, " error ", "%s ！ Open failed " % err)
            return False

        history.log(' merge [%s] data ' % srcFilePath)

        #  Refresh Display 
        self.btnFlashOnClick()

    def btnFormalExpOnClick(self):
        print('btnFormalExpOnClick')

        self.csvExpForm = csvexpform.CsvExpForm("Save As .json", ['utf-8'])
        result = self.csvExpForm.exec_()
        if result != QDialog.Accepted:
            return False

        dstFilePath = self.csvExpForm.getFilePath()
        encoding = self.csvExpForm.getEncoding()

        print(dstFilePath, encoding)

        #  Save as Data to csv file 
        err = self.dataService.formalExport(dstFilePath, encoding)
        if err != '':
            QMessageBox.critical(self, " error ", "%s ！ Save failed " % err)
            return False

        history.log(' Save as [%s] data ' % dstFilePath)
        QMessageBox.information(self, ' Tips ', ' The data has been saved as to  [%s]' % dstFilePath, QMessageBox.Yes)
        return dstFilePath


    def btnNewOnClick(self):
        self.btnPrologImpOnClick('A :- B, C.\n')
        history.log(' newly build ')

    def btnCsvImpOnClick(self):
        print('csv  open ')
        self.csvImpForm = csvimpform.CsvImpForm("Open .csv")
        result = self.csvImpForm.exec_()
        if result != QDialog.Accepted:
            return False

        srcFilePath = self.csvImpForm.getFilePath()
        retainTreeSwitch = self.csvImpForm.getRetainTree()
        encoding = self.csvImpForm.getEncoding()

        print(srcFilePath, retainTreeSwitch, encoding)

        #  from csv File Open Data 
        list_notImpNode, err = self.dataService.csvImport(srcFilePath, retainTreeSwitch, encoding)
        if err != '':
            QMessageBox.critical(self, " error ", "%s ！ Open failed " % err)
            return False

        history.log(' open [%s] data ' % srcFilePath)
        self.changeCsvFile(srcFilePath, encoding)

        if len(list_notImpNode) > 0:
            QMessageBox.warning(self, " warning ", " The following nodes do not exist, and some node data has not been imported: \n%s" % str(list_notImpNode))

        #  Refresh Display 
        self.btnFlashOnClick()

    def btnCsvSaveOnClick(self):
        print('btnCsvSaveOnClick')
        #  Save data to csv file 
        try:
            if self.current_file != '' and self.current_encoding != '':
                self.dataService.csvExport(self.current_file, self.current_encoding)
                history.log(' preservation [%s] data ' % self.current_file)
            else:
                ret = self.btnCsvExpOnClick()
                if ret != False:
                    history.log(' Data has been saved to a new file [%s]' % ret)
        except:
            QMessageBox.warning(self, " warning ", " Save failed! The file may be occupied , {}".format(traceback.format_exc()))
            traceback.print_exc()
            return False

        self.needSaveUI(False)

    def btnTransAngleOnClick(self):
        topRoot = "setAngle('topRoot');"
        leftRoot = "setAngle('leftRoot');"

        with open(self.url_gojs, 'r', encoding='utf-8') as f:
            content = f.read()

        if -1 != content.find(topRoot):
            content = content.replace(topRoot, leftRoot)
        elif -1 != content.find(leftRoot):
            content = content.replace(leftRoot, topRoot)
        else:
            pass

        with open(self.url_gojs, 'w', encoding='utf-8') as f:
            f.write(content)

        #  Refresh Display 
        self.btnFlashOnClick()

    def color_fill_stroke(self, is_gsn=True):
        with open(self.url_gojs, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if 'python:color_fill_stroke' in line:
                if is_gsn:
                    lines[i] = '              new go.Binding("stroke", "frameColor"), // python:color_fill_stroke\n'
                    lines[i+1] = '              new go.Binding("fill", "nodetype", getFrameColor)\n'
                else:
                    lines[i] = '              new go.Binding("fill", "frameColor"), // python:color_fill_stroke\n'
                    lines[i+1] = '              new go.Binding("stroke", "nodetype", getFrameColor)\n'
                break

        with open(self.url_gojs, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        #  Refresh Display 
        self.btnFlashOnClick()

    def set_center_node(self, ID):
        ID = int(ID)
        with open(self.url_gojs, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if 'python:centerNode' in line:
                lines[i] = f'          centerNode({ID}); // python:centerNode\n'
                break

        with open(self.url_gojs, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        #  Refresh Display 
        self.btnFlashOnClick()

    def btnSafetyCaseOnClick(self):
        print(' generate SafetyCase script ')
        sc = safecase.SafetyCase(self.current_file)
        sc.readTrustedTree()
        script = sc.createSafetyCase()

        #  open SafetyCase tool 
        # SC.main(script)
        d = {"script": script}
        proc = Process(target=SC.main, args=(1,), kwargs=d)
        proc.start()

        #  Dialogue box display 
        # self.prologForm = prologform.PrologForm('SafetyCase script ', script)
        # self.prologForm.initExportUI()
        # result = self.prologForm.exec_()
        # if result != QDialog.Accepted:
        #     return False
        # return False

    def btnDSTheoryOnClick(self):
        print(' Quantitative reasoning ')
        #  Obtain proof of root node 
        proveRootText = self.proveTreeEdit.text()
        if proveRootText:
            try:
                proveRootID = int(proveRootText)
            except:
                QMessageBox.critical(self, " error ", " Please fill in the integer type   Tree node ID")
                return False
        else:
            proveRootID = self.dataService.getRootNode().nodeID
        
        list_descendant = []
        self.dataService.getDescendantIDLevel(proveRootID, list_descendant, level=1)
        list_descendant.sort(key=lambda x:x[1], reverse=True)
        
        for it in list_descendant:
            try:
                self.dataService.DSTheoryCal(it[0])
            except:
                QMessageBox.critical(self, " error ", f" Data error, subtree parent node ID :  {it[0]}")
                return False

        #  Refresh Display 
        self.btnFlashOnClick()

    def btnAutoEvaluateOnClick(self, ID=None, level=None):
        print('btnAutoEvaluateOnClick')
        #  Obtain proof of root node 
        if not ID:
            proveRootID, proveLevel = self.get_select_subtree()
            if proveRootID == -1:
                return False
        else:
            proveRootID = ID
            proveLevel = level
        
        #  Obtain divergence 
        temperature = float(self.temperatureEdit.text())

        evaluate_info = self.dataService.autoEvaluateNode(proveRootID, proveLevel, temperature)
        json_ratings = evaluate_info['json_ratings'].replace('```json', '').replace('```', '')
        json_ratings = json.loads(json_ratings)
        json_ratings['Images'] = {}
        json_ratings['Images']['original'] = 'tmp_gsn_original.svg'
        json_ratings['Images']['suggested'] = 'tmp_gsn_suggested.svg'

        url_evaluation_tmp = os.path.abspath('history/tmp_evaluation_report.html')

        gsn_yaml = evaluate_info['gsn_yaml']
        improved_gsn_yaml = evaluate_info['improved_gsn_yaml'].replace('```yaml', '').replace('```', '')
        tmp_path = self.create_gsn_svg(gsn_yaml)
        shutil.copyfile(tmp_path, 'history/tmp_gsn_original.svg')
        tmp_path = self.create_gsn_svg(improved_gsn_yaml)
        shutil.copyfile(tmp_path, 'history/tmp_gsn_suggested.svg')

        # self.textBox = textbox.TextBox(' Inspection results ', json.dumps(evaluate_info, indent=4, ensure_ascii=False))
        # self.textBox.readOnly()
        # self.textBox.exec_()

        with open(self.url_evaluation, 'r', encoding='utf-8') as f:
            html = f.read()
        
        html = html.replace('<RATINGS_DATA>', json.dumps(json_ratings, indent=4, ensure_ascii=False))

        with open(url_evaluation_tmp, 'w', encoding='utf-8') as f:
            f.write(html)

        self.webbox = webbox.WebBox('Report', url_evaluation_tmp)
        self.webbox.show()

    def btnConstraintFormalOnClick(self):
        print(' Formalization of node constraints ')
        #  Obtain proof of root node 
        proveRootID, proveLevel = self.get_select_subtree()
        if proveRootID == -1:
            print(' Node acquisition failed! ')
            return False
        
        list_ID = self.dataService.formalAllEmptyLLM(proveRootID, proveLevel)
        self.dataService.setNodesHighlight(list_ID, frameColor='GreenYellow')
        #  Refresh Display 
        self.btnFlashOnClick()

    def get_select_subtree(self):
        proveRootText = self.proveTreeEdit.text()
        
        proveLevel = 99999
        if proveRootText:
            if ':' in proveRootText:
                proveRootID = proveRootText.split(':')[0]
                proveLevel = proveRootText.split(':')[1]
            else:
                proveRootID = proveRootText
            try:
                proveRootID = int(proveRootID)
                proveLevel = int(proveLevel)
            except:
                QMessageBox.critical(self, " error ", " Please fill in the integer type   Tree node ID  or   Layer number, for example  1:3 , indicating 1 Starting from node number 3 layer ")
                return -1
        else:
            proveRootID = self.dataService.getRootNode().nodeID
        return proveRootID, proveLevel

    def btnConstraintProveOnClick(self):
        print(' Node constraint proof ')
        #  Obtain proof of root node 
        proveRootID, proveLevel = self.get_select_subtree()
        if proveRootID == -1:
            return False

        dict_err_info = self.dataService.checkAllExpr(proveRootID)
        #  Refresh Display 
        self.btnFlashOnClick()

        err_info = str(dict_err_info).replace("', '", "', \n'")

        self.proveForm = prologform.PrologForm('Error Report', err_info)
        self.proveForm.initExportUI()
        self.proveForm.show()

        print(dict_err_info)
        

    def btnNodeWidthOnClick(self, e):
        #  Change node width 
        print('btnNodeWidthOnClick')
        width, okPressed = QInputDialog.getInt(self, HAN_EN.get("Edit"),
                                               HAN_EN.get("Please set the node width: (unit: px) \n When the node width is 0, the default width is displayed."), 250)
        if not okPressed:
            return False

        self.dataService.setAllNodeWidth(width, force=True)
        self.all_node_width = width

        #  Refresh Display 
        self.btnFlashOnClick()

    def btnNodesHighlightOnClick(self):
        #  Node Highlighting 
        print('btnNodesHighlightOnClick')
        text, okPressed = QInputDialog.getText(self, HAN_EN.get("Node Highlight"), HAN_EN.get("Node ID path"), QLineEdit.Normal, "1->2->4")
        if okPressed and text != '':
            list_ID = re.findall(r'\d+', text)
            list_ID = [int(ID) for ID in list_ID]
            self.dataService.setNodesHighlight(list_ID)

            #  Refresh Display 
            self.btnFlashOnClick()

    def btnNodesModeOnClick(self):
        #  Node mode switching 
        print('btnNodesModeOnClick')

        name_map = {
            HAN_EN.get('Show all'): 'allshow',
            HAN_EN.get('Description only'): 'allhide',
            HAN_EN.get('GSN mode'): 'Addition',
            HAN_EN.get('Function mode'): 'DS_Addition',
            HAN_EN.get('Qualitative mode'): 'actions',
            HAN_EN.get('Quantitative mode'): 'DSTheory',
        }

        mode, ok = QInputDialog.getItem(self, HAN_EN.get('Node mode setting'),
            self.tr(HAN_EN.get('Please select the tree display mode')),
            list(name_map.keys()),
            0, False)
        if ok:
            self.dataService.setAllNodeMode(name_map[mode])
            # if name_map[mode] == 'Addition':
            #     self.color_fill_stroke(is_gsn=True)
            # else:
            #     self.color_fill_stroke(is_gsn=False)

        #  Refresh Display 
        self.btnFlashOnClick()

    def btnStrategySwitchOnClick(self):
        #  Expand strategy node 
        print('btnNodesModeOnClick')
        if not self.strategy_open:
            self.dataService.createAllStrategyNode()
            self.strategy_open = True
        else:
            self.dataService.closeAllStrategyNode()
            self.strategy_open = False

        #  Refresh Display 
        self.btnFlashOnClick()

    def resetMyDiagramDivHeight(self, height=0):
        if height > 0:
            t_height = height - 100
        else:
            t_height = self.browser.height() - 18
        
        print('resetMyDiagramDivHeight: ', t_height)

        with open(self.url_gojs, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i in range(len(lines)):
            if 0 == lines[i].find('    setMyDiagramDivHeight'):
                lines[i] = '    setMyDiagramDivHeight(%d);\n' % t_height
                break

        with open(self.url_gojs, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        #  Refresh Display 
        self.btnFlashOnClick()

    def resizeEvent(self, e):
        #  Change window size in response to events 
        print("w = {0}; h = {1}".format(e.size().width(), e.size().height()))
        self.resetMyDiagramDivHeight(e.size().height())
        
        QtWidgets.QWidget.resizeEvent(self, e)

    def changeCsvFile(self, filePath, encoding):
        self.current_file = filePath
        self.current_encoding = encoding
        self.setWindowTitle(self.makeWindowTitle())
        self.needSaveUI(False)

        with open(history.lastCsvPath, 'w', encoding='utf-8') as f:
            f.writelines([filePath+'\n', encoding+'\n'])

    def newCsvFile(self):
        self.current_file = ''
        self.current_encoding = ''
        self.setWindowTitle(self.makeWindowTitle())
        self.needSaveUI(True)

    def needSaveUI(self, isSave = True):
        self.actAutoSave.setEnabled(isSave)
        self.actCsvSave.setEnabled(isSave)
        self.actJsonSave.setEnabled(isSave)

def handle_exception(exc_type, exc_value, exc_traceback):
    """ Exception handling function """    
    traceback.print_tb(exc_traceback)
    err_trace = traceback.format_tb(exc_traceback)
    err_trace = '\n'.join(err_trace)

    message = f"An exception of type {exc_type.__name__} occurred.\n{exc_value}\n{err_trace}"
    QMessageBox.critical(None, "Error", message)


def main():
    sys.excepthook = handle_exception #  Exception handling function 
    app = QApplication(sys.argv)
    main = MainLayout()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()