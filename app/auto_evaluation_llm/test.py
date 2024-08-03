import os, pprint
import unittest
WORK_DIR = os.path.dirname(__file__)
os.chdir(WORK_DIR)
from auto_evaluate import AutoEvaluate

TEST_gsn_yaml = """
G1:
 text: Main Goal
 supportedBy: [S1]
 inContextOf: [A1]
 classes: [additionalclass1, additionalclass2]

S1:
 text: Strategy 1
 supportedBy: [G2,G3]

A1: 
 text: Assumption 1

G2:
 text: Subgoal 1
 inContextOf: [J1]
 undeveloped: true

G3:
 text: Subgoal 2
 supportedBy: [Sn1] 
 inContextOf: [J1,C1]

Sn1: 
 text: Solution 1
 url: https://github.com/jonasthewolf/gsn2x

J1: 
 text: Justification 1

C1:
 text: Context 1
"""

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.ae = AutoEvaluate('./prompts/gsn_evaluation.txt')

    def tearDown(self):
        pass
    
    def test_01_equation(self):

        evaluate_info = self.ae.evaluate(
            gsn_yaml=TEST_gsn_yaml,
            temperature=0.8,
            model='gpt-3.5'
        )
        print(evaluate_info)


if __name__ == '__main__':
    # 测试用例执行顺序，按函数名字典序
    unittest.main()
