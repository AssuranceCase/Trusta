import csv, os
import dataservice
import subprocess

TAMPLATE =\
"""
BEGIN

A -> B : 0.3
A -> C : 0.7
C -> D : 0.5
C -> E : 0.5

A : "type:PC"
C : "type:PC"
B : "dec:0.6,conf:0.4"
D : "dec:0.5,conf:0.4"
E : "dec:0.7,conf:0.6"

A = "通过比较反馈机制验证两次构建生成的二进制包的一致性并反馈不可解释的差异"
B = "使用比较工具验证两次构建生成的二进制包的一致性"
C = "有反馈机制以消除经比较发现的不可解释的差异"
D = "消除比较发现的不可解释的差异"
E = "将比较发现的不可解释的差异积累为新的已知差异因素"

END
"""


def run_SafetyCase(*args, **kwargs):
    script = kwargs["script"]
    curr_dir = os.getcwd()
    exec_path = '../../DsSafetyCase/app/FS.py'
    work_dir = os.path.dirname(exec_path)
    os.chdir(work_dir)

    with open('./model/TextUML.txt', 'w', encoding='utf-8') as f:
        f.write(script)

    cmd = f'python {exec_path}'
    subprocess.call(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    os.chdir(curr_dir)

class SafetyCase:
    trustedTree = []
    safetyCaseScript = []

    def __init__(self, csv_path):
        self.csv_path = csv_path
        # self.trustedTree, err = self.getTrustedTree()

    def readTrustedTree(self):
        # 获取数据
        try:
            with open(self.csv_path, mode='r', encoding='ansi') as f:
                reader = csv.reader(f)
                title_flag = True
                for row in reader:
                    # 跳过第一行 表头
                    if title_flag:
                        title_flag = False
                        continue
                    self.trustedTree.append(dataservice.CsvData(row))
            return ''
        except UnicodeDecodeError:
            return '文件编码有误'
        except FileNotFoundError:
            return '文件不存在'
        except IndexError:
            return '文件格式不正确'

    def createSafetyCase(self):
        self.initChildNum()
        for node in self.trustedTree:
            self.safetyCaseScript.append(self.getLink(node))
            self.safetyCaseScript.append(self.getNodeLogic(node))
            self.safetyCaseScript.append(self.getNodeText(node))

        return "BEGIN\n%s\nEND" % '\n'.join(self.safetyCaseScript)

    def initChildNum(self):
        self.dict_childNum = {}
        for node in self.trustedTree:
            if node.parentID in list(self.dict_childNum.keys()):
                self.dict_childNum[node.parentID] += 1
            else:
                self.dict_childNum[node.parentID] = 1

    def getLink(self, node):
        if node.parentID == '' or node.parentID == '0':
            return ''
        src = node.parentID
        dst = str(node.nodeID)
        weight = 1 / int(self.dict_childNum[node.parentID])
        weight = round(weight, 2) # 平均分配权重
        script = '%s -> %s : %f' % (src, dst, weight)
        return script

    def getNodeLogic(self, node):
        if str(node.nodeID) in list(self.dict_childNum.keys()): # 存在子结点，即非叶子结点
            script = '%s : "type:PC"' % str(node.nodeID)
        else: # 叶子结点
            script = '%s : "dec:1,conf:1"' % str(node.nodeID)
        return script

    def getNodeText(self, node):
        script = '%s = "%s"' % (str(node.nodeID), node.nodeName)
        return script

if __name__ == '__main__':
    sc = SafetyCase('./构建一致性_可信推理树.csv')
    sc.readTrustedTree()
    script = sc.createSafetyCase()
    a = 1
