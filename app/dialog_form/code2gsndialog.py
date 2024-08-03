import sys, os, shutil, json, traceback, time
import subprocess
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from func_analysis_llm.py_func_get import PyFunctionGetter
from others.config_oper import Config

class CodeExecutionDialog(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Python Code to GSN')
        # self.setGeometry(100, 100, 500, 900)
        # self.setGeometry(100, 100, 900, 1200)
        self.setWindowIcon(QIcon(os.path.join('images', 'CodeIcon.ico')))
        
        layout = QVBoxLayout()
        
        # Select file and set execution path
        self.file_label = QLabel('Select Startup Script File:')
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.browse_file)
        
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.browse_button)
        
        layout.addLayout(file_layout)
        
        # Execution path
        self.work_path_label = QLabel('Working Directory:')
        self.work_path_edit = QLineEdit()
        self.exec_path_label = QLabel('Command:')
        self.exec_path_edit = QLineEdit()

        file_name = Config().get_config('PROJECT_START_FILE')
        if file_name:
            file_name = os.path.abspath(file_name)
            self.file_path_edit.setText(file_name)
            self.work_path_edit.setText(os.path.dirname(file_name))
            self.exec_path_edit.setText('python ' + os.path.basename(file_name))
        
        exec_path_layout = QVBoxLayout()
        exec_path_layout.addWidget(self.work_path_label)
        exec_path_layout.addWidget(self.work_path_edit)
        exec_path_layout.addWidget(self.exec_path_label)
        exec_path_layout.addWidget(self.exec_path_edit)
        
        layout.addLayout(exec_path_layout)
        
        # Start execution button
        self.start_button = QPushButton('Start Execution and Generate GSN')
        self.start_button.clicked.connect(self.start_execution)
        
        layout.addWidget(self.start_button)
        
        # Execution result
        self.result_label = QLabel('Log:')
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        
        layout.addWidget(self.result_label)
        layout.addWidget(self.result_display)
        
        # Processing steps
        self.step1_label = QLabel('Step 1: Not Started')
        self.step1_info = QTextEdit()
        self.step1_info.setFixedHeight(18)
        self.step1_info.setReadOnly(True)
        
        self.step2_label = QLabel('Step 2: Not Started')
        self.step2_info = QTextEdit()
        self.step2_info.setFixedHeight(18)
        self.step2_info.setReadOnly(True)
        
        self.step3_label = QLabel('Step 3: Not Started')
        self.step3_info = QTextEdit()
        self.step3_info.setFixedHeight(18)
        self.step3_info.setReadOnly(True)

        self.step4_label = QLabel('Step 4: Not Started')
        self.step4_info = QTextEdit()
        self.step4_info.setFixedHeight(18)
        self.step4_info.setReadOnly(True)

        self.step5_label = QLabel('Step 5: Not Started')
        self.step5_info = QTextEdit()
        self.step5_info.setFixedHeight(18)
        self.step5_info.setReadOnly(True)

        self.step6_label = QLabel('Step 6: Not Started')
        self.step6_info = QTextEdit()
        self.step6_info.setFixedHeight(18)
        self.step6_info.setReadOnly(True)
        
        layout.addWidget(self.step1_label)
        layout.addWidget(self.step1_info)
        layout.addWidget(self.step2_label)
        layout.addWidget(self.step2_info)
        layout.addWidget(self.step3_label)
        layout.addWidget(self.step3_info)
        layout.addWidget(self.step4_label)
        layout.addWidget(self.step4_info)
        layout.addWidget(self.step5_label)
        layout.addWidget(self.step5_info)
        layout.addWidget(self.step6_label)
        layout.addWidget(self.step6_info)
        
        self.setLayout(layout)

        # Apply a stylesheet to the entire dialog
        self.setStyleSheet("""
            QPushButton {
                background: #448aff;
                color: white;
                font-weight: 800;
                font-size: 14px;
            }
            QTextEdit {
                font-size: 14px;
            }
            QLineEdit {
                font-size: 14px;
            }
            QLabel {
                font-size: 14px;
            }
        """)
        
    def browse_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Code File", "../resource/demo_project", "Python Files (*.py);;All Files (*)", options=options)
        if file_name:
            self.file_path_edit.setText(file_name)
            self.work_path_edit.setText(os.path.dirname(file_name))
            self.exec_path_edit.setText('python ' + os.path.basename(file_name))
            
    def start_execution(self):
        # Clear previous results
        self.result_display.clear()
        self.step1_info.clear()
        self.step2_info.clear()
        self.step3_info.clear()
        self.step4_info.clear()
        self.step5_info.clear()
        self.step6_info.clear()
        
        # Update steps to indicate execution
        self.step1_label.setText('Step 1: Not Started')
        self.step1_label.setStyleSheet('color: gray')
        self.step2_label.setText('Step 2: Not Started')
        self.step2_label.setStyleSheet('color: gray')
        self.step3_label.setText('Step 3: Not Started')
        self.step3_label.setStyleSheet('color: gray')
        self.step4_label.setText('Step 4: Not Started')
        self.step4_label.setStyleSheet('color: gray')
        self.step5_label.setText('Step 5: Not Started')
        self.step5_label.setStyleSheet('color: gray')
        self.step6_label.setText('Step 6: Not Started')
        self.step6_label.setStyleSheet('color: gray')
        
        self.result_display.append(f"Executing script, please wait.")
        # clean select tree
        self.main_window.proveTreeEdit.setText('')
        QApplication.processEvents()  # Force UI update

        # Step 0: Copy config.json
        work_path = self.work_path_edit.text()
        config_path = os.path.join(work_path, 'config.json')
        if not os.path.exists(config_path):
            self.result_display.append(f'{config_path} not found!')
            return
        shutil.copyfile(config_path, 'config.json')
        self.result_display.append(f'Apply {config_path}')
        QApplication.processEvents()  # Force UI update

        # Step 1
        self.step1_label.setText('Step 1: In Progress')
        self.step1_label.setStyleSheet('color: blue')
        QApplication.processEvents()  # Force UI update
        time.sleep(0.5)
        try:
            is_ok = self.step1_callgraph_gen()
        except Exception as e:
            err_info = traceback.format_exc()
            self.result_display.append(f"Execution failed: {err_info}")
            is_ok = False
        if is_ok:
            self.step1_info.append("step (1): Function call graph generation. OK")
            self.step1_label.setText('Step 1: Success')
            self.step1_label.setStyleSheet('color: green')
        else:
            self.step1_info.append("step (1): Function call graph generation. Error")
            self.step1_label.setText('Step 1: Failed')
            self.step1_label.setStyleSheet('color: red')
            return

        # Step 2
        self.step2_label.setText('Step 2: In Progress')
        self.step2_label.setStyleSheet('color: blue')
        QApplication.processEvents()  # Force UI update
        time.sleep(0.5)
        try:
            is_ok = self.step2_func_node_filter()
        except Exception as e:
            err_info = traceback.format_exc()
            self.result_display.append(f"Execution failed: {err_info}")
            is_ok = False
        if is_ok:
            self.step2_info.append("step (2): Function node filtration. OK")
            self.step2_label.setText('Step 2: Success')
            self.step2_label.setStyleSheet('color: green')
        else:
            self.step2_info.append("step (2): Function node filtration. Error")
            self.step2_label.setText('Step 2: Failed')
            self.step2_label.setStyleSheet('color: red')
            return

        # Step 3
        self.step3_label.setText('Step 3: In Progress')
        self.step3_label.setStyleSheet('color: blue')
        QApplication.processEvents()  # Force UI update
        time.sleep(0.5)
        try:
            is_ok = self.step3_NL_trans_using_LLMs()
        except Exception as e:
            err_info = traceback.format_exc()
            self.result_display.append(f"Execution failed: {err_info}")
            is_ok = False
        if is_ok:
            self.step3_info.append("step (3): Natural language transformation using LLMs. OK")
            self.step3_label.setText('Step 3: Success')
            self.step3_label.setStyleSheet('color: green')
        else:
            self.step3_info.append("step (3): Natural language transformation using LLMs. Error")
            self.step3_label.setText('Step 3: Failed')
            self.step3_label.setStyleSheet('color: red')
            return

        # Step 4
        self.step4_label.setText('Step 4: In Progress')
        self.step4_label.setStyleSheet('color: blue')
        QApplication.processEvents()  # Force UI update
        time.sleep(0.5)
        try:
            is_ok = self.step4_context_cons_init()
        except Exception as e:
            err_info = traceback.format_exc()
            self.result_display.append(f"Execution failed: {err_info}")
            is_ok = False
        if is_ok:
            self.step4_info.append("step (4): Contextualization of constructors and initializers. OK")
            self.step4_label.setText('Step 4: Success')
            self.step4_label.setStyleSheet('color: green')
        else:
            self.step4_info.append("step (4): Contextualization of constructors and initializers. Error")
            self.step4_label.setText('Step 4: Failed')
            self.step4_label.setStyleSheet('color: red')
            return

        # Step 5
        self.step5_label.setText('Step 5: In Progress')
        self.step5_label.setStyleSheet('color: blue')
        QApplication.processEvents()  # Force UI update
        time.sleep(0.5)
        try:
            is_ok = self.step5_testcases_evidences()
        except Exception as e:
            err_info = traceback.format_exc()
            self.result_display.append(f"Execution failed: {err_info}")
            is_ok = False
        if is_ok:
            self.step5_info.append("step (5): Integration of test cases as evidence nodes. OK")
            self.step5_label.setText('Step 5: Success')
            self.step5_label.setStyleSheet('color: green')
        else:
            self.step5_info.append("step (5): Integration of test cases as evidence nodes. Error")
            self.step5_label.setText('Step 5: Failed')
            self.step5_label.setStyleSheet('color: red')
            return

        # Step 6
        self.step6_label.setText('Step 6: Edit as needed on the main interface.')
        self.step6_label.setStyleSheet('color: blue')
        QApplication.processEvents()  # Force UI update
        self.step6_info.append("step (6): Assumptions and justifications.")

    def step5_testcases_evidences(self):
        self.main_window.btnCaseAddSolutionOnClick()
        self.main_window.btnStrategySwitchOnClick()
        self.main_window.dataService.setAllNodeMode('DSTheory')
        self.main_window.color_fill_stroke(is_gsn=True)
        return True

    def step4_context_cons_init(self):
        self.main_window.btnCaseInitToContextOnClick()
        return True

    def step3_NL_trans_using_LLMs(self):
        self.main_window.btnCaseFuncAnalysisOnClick()
        return True

    def step2_func_node_filter(self):
        self.main_window.btnCaseAdjustGraphOnClick()
        return True

    def step1_callgraph_gen(self):
        # Execute the Python script and capture the output
        script_path = self.file_path_edit.text()
        work_path = self.work_path_edit.text()
        exec_cmd = self.exec_path_edit.text()

        Config().set_config("PROJECT_START_FILE", script_path)
        if script_path:
            trusta_driven_path = self.edit_code_for_callgraph(script_path)
            final_cmd = exec_cmd.replace(os.path.basename(script_path), os.path.basename(trusta_driven_path))

            output = self.exec_cmd_by_popen(work_dir=work_path, cmd=final_cmd)
            # output = self.exec_cmd_by_process(work_dir=work_path, list_cmd=[final_cmd])

            self.result_display.append(output)
            QApplication.processEvents()  # Force UI update

            #  The generated dot File import Trusta
            dot_path = os.path.join(os.path.dirname(trusta_driven_path), 'trusta_callgraph.dot')
            self.main_window.btnDotOpenOnClick(dot_path)

            #  Create a function call graph 
            func_body_path = self.get_func_body(os.path.dirname(trusta_driven_path))
            test_body_path = self.get_testcase_body(func_body_path)
            info = f'dot path: {dot_path}\nfunc body path: {func_body_path}\ntest body path: {test_body_path}'
            self.result_display.append(info)
            Config().set_config("FUNCTION_CODE_PATH", func_body_path)
            Config().set_config("TESTCASE_CODE_PATH", test_body_path)

            return os.path.exists(dot_path) and os.path.exists(func_body_path)
        else:
            self.result_display.append('Error: Run script not found.')
            return False

    def get_testcase_body(self, func_body_path):
        with open(func_body_path, 'r', encoding='utf-8') as f:
            all_functions_bodies = json.load(f)
        
        #  Filter out test case functions 
        testcase_bodies = {}
        for func_name, func_body in all_functions_bodies.items():
            short_func_name = func_name.rsplit('.', 1)[1]
            if short_func_name.startswith('test_'):
                testcase_bodies[func_name] = func_body

        test_body_path = os.path.join(os.path.dirname(func_body_path), 'trusta_test_body.json')
        with open(test_body_path, 'w', encoding='utf-8') as f:
            json.dump(testcase_bodies, f, indent=4)
        return test_body_path 

    def get_func_body(self, dir_path):
        pfg = PyFunctionGetter()
        all_functions_bodies = pfg.select_dir_functions_bodies(dir_path)
        # all_functions_bodies = pfg.filter_functions(all_functions_bodies)

        func_body_path = os.path.join(dir_path, 'trusta_func_body.json')
        with open(func_body_path, 'w', encoding='utf-8') as f:
            json.dump(all_functions_bodies, f, indent=4)
        return func_body_path

    def edit_code_for_callgraph(self, script_path):
        trusta_mian_path = os.path.join(os.path.dirname(script_path), 'trusta_main.py')
        trusta_driven_path = os.path.join(os.path.dirname(script_path), 'trusta_driven.py')

        shutil.copy(script_path, trusta_mian_path)
        shutil.copy('others/run_oo_driven.py', trusta_driven_path)
        
        with open(trusta_mian_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i in range(len(lines)):
            if '__name__' in lines[i] and '__main__' in lines[i]:
                lines[i] = 'def trusta_main():\n'
                break

        with open(trusta_mian_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return trusta_driven_path

    def exec_cmd_by_popen(self, work_dir, cmd):
        print(f'exec_cmd: {cmd}')
        dir_backup = os.getcwd()
        os.chdir(work_dir)
        with os.popen(cmd) as pf:
            output = pf.read()
        os.chdir(dir_backup)
        return output
    
    def exec_cmd_by_process(self, work_dir, list_cmd):
        result = subprocess.run(
            list_cmd, 
            cwd=work_dir,
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        output = []
        output.append(result.stdout)
        if result.returncode != 0:
            output.append(f"Error: {result.stderr}")
        return ''.join(output)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CodeExecutionDialog()
    ex.show()
    sys.exit(app.exec_())
