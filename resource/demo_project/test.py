import unittest
from main import Cannon

class TestCannon(unittest.TestCase):

    def setUp(self):
        self.cannon = Cannon(M=2000, m=10, alpha=0, v=600, k=0.3)

    def test_calculate_recoil_velocity(self):
        expected_velocity = 3  # Calculate (10 * 600 * cos(0)) / 2000
        self.assertAlmostEqual(self.cannon.calculate_recoil_velocity(), expected_velocity, places=2)

    def test_calculate_resistance(self):
        expected_resistance = 6000  # Calculate 0.3 * 2000 * 10
        self.assertEqual(self.cannon.calculate_resistance(0.3), expected_resistance)

    def test_calculate_recoil_distance(self):
        # Since the calculation involves multiple steps, directly verify from a known value
        expected_distance = (3 ** 2) * 2000 / 2 / 6000  # Using the previously calculated initial velocity and resistance
        self.assertAlmostEqual(self.cannon.calculate_recoil_distance(), expected_distance, places=2)

    def test_is_soldier_safe(self):
        # 2 steps, each step is 0.7 meters, total distance 1.4 meters
        self.assertFalse(self.cannon.is_soldier_safe(steps=2))
        # 100 steps, each step is 0.7 meters, total distance 70 meters
        self.assertTrue(self.cannon.is_soldier_safe(steps=100))

if __name__ == '__main__':
    unittest.main()
