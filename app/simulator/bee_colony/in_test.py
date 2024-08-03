
import unittest
from z3 import *
from bee_2d import *


class TestAPI(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_01_dist_greater(self):
        x1, y1, x2, y2 = Reals('x1 y1 x2 y2')

        # 有解例子
        s = Solver()
        s.add(x1 == 0, y1 == 0, x2 == 1, y2 == 1)        
        s.add(dist_greater(x1, y1, x2, y2, 1))
        self.assertEqual(s.check(), sat)

        # 无解例子
        s = Solver()
        s.add(x1 == 0, y1 == 0, x2 == 1, y2 == 1)        
        s.add(dist_greater(x1, y1, x2, y2, 2))
        self.assertEqual(s.check(), unsat)

        # if s.check() == sat:
        #     m = s.model()
        #     for d in m.decls():
        #         print("%s = %s" % (d.name(), m[d]))

    def test_02_dist_less(self):
        x1, y1, x2, y2 = Reals('x1 y1 x2 y2')

        # 有解例子
        s = Solver()
        s.add(x1 == 0, y1 == 0, x2 == 1, y2 == 1)        
        s.add(dist_less(x1, y1, x2, y2, 2))
        self.assertEqual(s.check(), sat)

        # 无解例子
        s = Solver()
        s.add(x1 == 0, y1 == 0, x2 == 1, y2 == 1)        
        s.add(dist_less(x1, y1, x2, y2, 1))
        self.assertEqual(s.check(), unsat)

    def test_03_xor(self):
        A, B = Bools('A B')

        s = Solver()
        s.add(A == True, B == True)        
        s.add(xor(A, B) == False)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(A == False, B == False)        
        s.add(xor(A, B) == False)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(A == False, B == True)        
        s.add(xor(A, B) == True)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(A == True, B == False)        
        s.add(xor(A, B) == True)
        self.assertEqual(s.check(), sat)

    def test_04_same_sign(self):
        n1, n2, n3, n4 = Reals('n1 n2 n3 n4')

        s = Solver()
        s.add(n1 == 1, n2 == 2, n3 == -3, n4 == -4)
        s.add(same_sign(n1, n2) == True)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(n1 == 1, n2 == 2, n3 == -3, n4 == -4)
        s.add(same_sign(n3, n4) == True)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(n1 == 1, n2 == 2, n3 == -3, n4 == -4)
        s.add(same_sign(n1, n3) == False)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(n1 == 1, n2 == 2, n3 == -3, n4 == -4)
        s.add(same_sign(n4, n2) == False)
        self.assertEqual(s.check(), sat)

    def test_05_if_else(self):

        s = Solver()
        s.add(if_else(True, True, False) == True)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(if_else(False, True, False) == False)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(if_else(False, False, True) == True)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(if_else(True, False, True) == False)
        self.assertEqual(s.check(), sat)

    def test_06_same_direction(self):
        x1, y1, x2, y2, x3, y3 = Reals('x1 y1 x2 y2 x3 y3')

        s = Solver()
        s.add(x1 == 0, y1 == 0, x2 == 1, y2 == 1, x3 == -2, y3 == -2) 
        s.add(same_direction(x1, y1, x2, y2, x3, y3) == True)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(x1 == 0, y1 == 0, x2 == 1, y2 == 1, x3 == 2, y3 == 3) 
        s.add(same_direction(x1, y1, x2, y2, x3, y3) == False)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(x1 == 0, y1 == 0, x2 == 1, y2 == 1, x3 == -2, y3 == 3) 
        s.add(same_direction(x1, y1, x2, y2, x3, y3) == False)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(x1 == 0, y1 == 0, x2 == 1, y2 == 1, x3 == 2, y3 == -3) 
        s.add(same_direction(x1, y1, x2, y2, x3, y3) == False)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(x1 == -1, y1 == 1, x2 == 0, y2 == 0, x3 == -2, y3 == 2) 
        s.add(same_direction(x1, y1, x2, y2, x3, y3) == True)
        self.assertEqual(s.check(), sat)

        s = Solver()
        s.add(x1 == -1, y1 == 0, x2 == 0, y2 == 0, x3 == 2, y3 == 0) 
        s.add(same_direction(x1, y1, x2, y2, x3, y3) == True)
        self.assertEqual(s.check(), sat)


if __name__ == '__main__':
    # 测试用例执行顺序，按函数名字典序
    unittest.main()
