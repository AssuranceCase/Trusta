import os, pprint
import unittest
WORK_DIR = os.path.dirname(__file__)
os.chdir(WORK_DIR)
from autobuild import AutoBuild

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.ab = AutoBuild('./prompts/gsn_builder.txt')

    def tearDown(self):
        pass
    
    def test_01_equation(self):
        sub_info = self.ab.build(
            goal="The AGV's sensor can accurately detect obstacles",
            temperature=0.8
        )
        print(sub_info)
        '''temperature=0.2
        ret = {'output_choices': 
        ['Goal G1: The AGV\'s sensor can accurately detect obstacles.\n
        Break down Strategy: {"strategy": "The accuracy of the sensor can be evaluated based on its ability to correctly identify obstacles."}\n
        Sub-goals dictionary: {"G1.1": "The sensor can correctly identify obstacles.",
                                "G1.2": "The sensor has a low false positive rate."}\n
        Solutions dictionary: {"Sn1.1": "In a laboratory environment, the sensor correctly identified obstacles in 95% of the tests.",
                                "Sn1.2": "In a laboratory environment, the sensor had a false positive rate of less than 5%."}\n
        Explanation: G1.1 and G1.2 can support G1, Sn1.1 can support G1.1, Sn1.2 can support G1.2.\n'],
        'chat_session_id': 'Without session-id.', 'status': 'OK'}
        '''
        '''temperature=0.8
        {'output_choices': 
        ['Goal G1: The AGV\'s sensor can accurately detect obstacles.\n
        Break down Strategy: {"strategy": "To ensure accurate obstacle detection, the sensor should have a low false positive and false negative rate."}\n
        Sub-goals dictionary: {"G1.1": "The sensor has a low false positive rate.",
                                "G1.2": "The sensor has a low false negative rate."}\n
        Solutions dictionary: {"Sn1.1": "In a laboratory environment, the sensor had a false positive rate of less than 5%.",
                                "Sn1.2": "In a laboratory environment, the sensor had a false negative rate of less than 3%."}\n
        Explanation: G1.1 and G1.2 can support G1, Sn1.1 can support G1.1, Sn1.2 can support G1.2.\n'],
        'chat_session_id': 'Without session-id.', 'status': 'OK'}
        '''
        # temperature=1.8 格式已变
        # self.assertEqual(ret, 'Fm < 0.5')

import json
def compare_data_only_person():
    with open('compare_data_temp-0.8.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for goal, info in data.items():
        subgoal = info['subgoal']
        info['subgoal'] = {
            "person": subgoal['person']
        }
    with open('compare_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    # 测试用例执行顺序，按函数名字典序
    # unittest.main()
    compare_data_only_person()
