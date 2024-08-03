import os, pprint
import unittest
WORK_DIR = os.path.dirname(__file__)
os.chdir(WORK_DIR)
from func_analysis import FunctionAnalysis

NEW_FUNCTION_CODE = """
def calculate_average_score(scores):
    total = sum(scores)
    count = len(scores)
    average = total / count
    return average
"""

list_external_func = [
    'sum: Used to calculate the total sum of all elements in the scores list.',
    'len: Used to determine the number of elements in the scores list.'
]

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.fa = FunctionAnalysis('./prompts/function_analysis.txt')

    def tearDown(self):
        pass
    
    def test_01_equation(self):

        result_info = self.fa.analysis(
            func_name='calculate_average_score',
            func_code=NEW_FUNCTION_CODE,
            list_external_func=list_external_func,
            temperature=0.5,
            model='gpt-3.5'
        )
        print(result_info)


if __name__ == '__main__':
    #  Test case execution order, in alphabetical order by function name 
    unittest.main()
