import re
from z3 import *
import lexical_analyzer as LA

class Z3Check:
    def findAllVariable(self, list_condition):
        return re.findall(r'[a-zA-Z]\w*', str(list_condition))

    def check_old(self, parent_expr, list_child_expr):
        # 自动识别变量
        list_condition = [parent_expr] + list_child_expr
        list_all_variable = self.findAllVariable(list_condition)
        list_all_variable = list(set(list_all_variable))
        for variable in list_all_variable:
            exec(r"{v_name} = Real('{v_name}')".format(v_name=variable))

        # 预处理表达式
        list_z3_cond = [self.change_format(cond) for cond in list_child_expr]
        list_z3_cond.append('Not({})'.format(self.change_format(parent_expr)))

        # 执行求解
        s = Solver()
        for z3_cond in list_z3_cond:
            s.add(eval(z3_cond))

        ret = s.check()
        if ret == sat:
            return str(s.model())
        else:
            return ''

    def get_z3py_code(self, parent_expr, list_child_expr):
        result = 'from z3 import *\n'
        result += 'try:\n    '

        # 自动识别变量
        list_condition = [parent_expr] + list_child_expr
        list_all_variable = self.findAllVariable(list_condition)
        list_all_variable = list(set(list_all_variable))
        for variable in list_all_variable:
            result += "%s = Real('%s')\n    " % (variable, variable)

        # 预处理表达式
        list_z3_cond = [self.change_format(cond) for cond in list_child_expr]
        list_z3_cond.append('Not({})'.format(self.change_format(parent_expr)))

        result += "solve(%s)\n    " % ','.join(list_z3_cond)

        # 输出
        result += """
except:
    print('Expression error!')
"""
        return result

    def check(self, parent_expr, list_child_expr):
        code_path = './history/tmp_z3.py'
        with open(code_path, 'w', encoding='utf-8') as f:
            z3code = self.get_z3py_code(parent_expr, list_child_expr)
            f.write(z3code)

        cmd = r'python %s' % code_path
        with os.popen(cmd) as pf:
            output = pf.read().strip()
            if output == 'no solution':
                return ''
            else:
                return output
            

    def change_format(self, expr):
        expr = expr.replace('=', '==')
        expr = expr.replace('<==', '<=')
        expr = expr.replace('>==', '>=')
        la = LA.LexicalAnalyzer()
        expr = la.change_format(expr)
        return expr

if __name__ == '__main__':
    zc = Z3Check()

    list_condition = [
        'response_time=proc_all_time+send_time',
        'proc_all_time<1',
        'send_time<1.5'
    ]

    ret = zc.checkTrans('response_time<2', list_condition)
    print(ret)
