import os
import unittest
WORK_DIR = os.path.dirname(__file__)
os.chdir(WORK_DIR)
from sentsformal import SentsFormal

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.sf = SentsFormal('./')
        self.constraint_data = {
            6: ['障碍物检测的距离为3米', '障碍物检测 的 距离 为 3 米', 's = 3'],
            7: ['小车的速度小于等于1米/秒', '小车 的 速度 小于等于 1 米/秒', 'v <= 1'],
            8: ['小车的加速度大于等于0.18米/秒^2', '小车 的 加速度 大于等于 0.18 米/秒^2', 'a >= 0.18'],
            25: ['制动反应时间大于0', '制动反应 时间 大于 0', 'Td > 0'],
            9: ['制动反应时间小于0.1秒', '制动反应 时间 小于 0.1 秒', 'Td < 0.1'],
            10: ['货物和货架之间的摩擦系数大于0.2', '货物和货架之间 的 摩擦系数 大于 0.2', 'u > 0.2'],
            11: ['货物质量为1千克', '货物 质量 为 1 千克', 'm = 1'],
            16: ['小车的加速度小于等于0.5米/秒^2', '小车 的 加速度 小于等于 0.5 米/秒^2', 'a <= 0.5'],
            17: ['货物对货架的压力为9.8牛顿', '货物对货架 的 压力 为 9.8 牛顿', 'Fn = 9.8'],
            18: ['重力加速度为9.8牛顿/千克', '重力加速度 为 9.8 牛顿/千克', 'g = 9.8'],
            21: ['制动时货物产生的摩擦力小于等于0.5牛顿', '制动时货物产生 的 摩擦力 小于等于 0.5 牛顿', 'Fm <= 0.5'],
            23: ['货架能给到货物的摩擦力大于0.5牛顿', '货架能给到货物 的 摩擦力 大于 0.5 牛顿', 'F > 0.5'],
        }

    def tearDown(self):
        pass
    
    def test_01_equation(self):
        data = {
            20: ['摩擦力 = 摩擦系数 * 压力', 'F = u * Fn'],
            19: ['水平面上物体的压力 = 质量 * 重力加速度', 'Fn = m * g'],
            22: ['物体所受到的外力 = 质量 * 加速度', 'Fm = m * a'],
            15: ['速率 * 速率 = 2 * 加速度 * 距离', 'v * v = 2 * a * x'],
        }
        for dv in data.values():
            formal = self.sf.formalize(dv[0])
            self.assertEqual(formal, dv[1])

    def test_02_word_tokenize(self):
        for dv in self.constraint_data.values():
            tokens = self.sf._word_tokenize(dv[0])
            target = dv[1].split(' ')
            self.assertEqual(tokens, target)

    def test_03_constraint(self):
        for dv in self.constraint_data.values():
            formal = self.sf.formalize(dv[0])
            self.assertEqual(formal, dv[2])


if __name__ == '__main__':
    # 测试用例执行顺序，按函数名字典序
    unittest.main()
