import unittest
from main import Cannon

class TestCannon(unittest.TestCase):

    def setUp(self):
        self.cannon = Cannon(M=2000, m=10, alpha=0, v=600, k=0.3)

    def test_calculate_recoil_velocity(self):
        expected_velocity = 3  # 计算 (10 * 600 * cos(0)) / 2000
        self.assertAlmostEqual(self.cannon.calculate_recoil_velocity(), expected_velocity, places=2)

    def test_calculate_resistance(self):
        expected_resistance = 6000  # 计算 0.3 * 2000 * 10
        self.assertEqual(self.cannon.calculate_resistance(0.3), expected_resistance)

    def test_calculate_recoil_distance(self):
        # 由于计算涉及多步骤，这里直接从已知值做验证
        expected_distance = (3 ** 2) * 2000 / 2 / 6000  # 使用之前计算的初速度和阻力
        self.assertAlmostEqual(self.cannon.calculate_recoil_distance(), expected_distance, places=2)

    def test_is_soldier_safe(self):
        # 2步，每步0.7米，距离 1.4 米
        self.assertFalse(self.cannon.is_soldier_safe(steps=2))
        # 100步，每步0.7米，距离 70 米
        self.assertTrue(self.cannon.is_soldier_safe(steps=100))

if __name__ == '__main__':
    unittest.main()
