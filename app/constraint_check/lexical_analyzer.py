
import unittest, sys, os

class LexicalAnalyzer:
    # 词法分析
    def process_not(self, expr):
        if expr[0] != '!':
            print('error: rocess_not error')
        return 'Not(%s)' % expr[1:]

    def process_logic(self, expr, z3_logic, label):
        if -1 != expr.find(label):
            list_condt = expr.split(label)
            str_ret = '{}('.format(z3_logic)
            for condt in list_condt:
                if condt[0] == '!':
                    condt = self.process_not(condt)
                str_ret += (condt + ',')
            str_ret = str_ret[0:-1] + ')'
            return str_ret
        return expr

    def change_format(self, expr):
        expr = expr.replace(' ', '')
        if -1 != expr.find('&&'):
            return self.process_logic(expr, 'And', '&&')
        elif -1 != expr.find('||'):
            return self.process_logic(expr, 'Or', '||')
        elif expr[0] == '!':
            return self.process_not(expr)
        else:
            return expr

"""
词法分析测试用例
"""

class TestLexicalAnalysis(unittest.TestCase):
    def setUp(self):
        self.la = LexicalAnalyzer()

    def tearDown(self):
        pass

    def test_Not(self):
        src = '!Activate'
        expect_dst = 'Not(Activate)'

        dst = self.la.change_format(src)
        self.assertEqual(dst, expect_dst)

    def test_And(self):
        src = 'S_ChannelA && S_ChannelB'
        expect_dst = 'And(S_ChannelA,S_ChannelB)'

        dst = self.la.change_format(src)
        self.assertEqual(dst, expect_dst)

    def test_And_Multi(self):
        src = 'S_ChannelA && S_ChannelB && S_ChannelC'
        expect_dst = 'And(S_ChannelA,S_ChannelB,S_ChannelC)'

        dst = self.la.change_format(src)
        self.assertEqual(dst, expect_dst)

    def test_Or(self):
        src = 'S_ChannelA || S_ChannelB'
        expect_dst = 'Or(S_ChannelA,S_ChannelB)'

        dst = self.la.change_format(src)
        self.assertEqual(dst, expect_dst)

    def test_Not_And(self):
        src = '!S_ChannelA && !S_ChannelB'
        expect_dst = 'And(Not(S_ChannelA),Not(S_ChannelB))'

        dst = self.la.change_format(src)
        self.assertEqual(dst, expect_dst)

    def test_Not_Or(self):
        src = '!S_ChannelA || !S_ChannelB'
        expect_dst = 'Or(Not(S_ChannelA),Not(S_ChannelB))'

        dst = self.la.change_format(src)
        self.assertEqual(dst, expect_dst)

    def test_Other1(self):
        src = 'S_ChannelB'
        expect_dst = 'S_ChannelB'

        dst = self.la.change_format(src)
        self.assertEqual(dst, expect_dst)

    def test_Other2(self):
        src = 'Timer >= DiscrepancyTime'
        expect_dst = 'Timer>=DiscrepancyTime'

        dst = self.la.change_format(src)
        self.assertEqual(dst, expect_dst)


if __name__ == '__main__':
    unittest.main()
