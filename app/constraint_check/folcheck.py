import re, os
import lexical_analyzer as LA

class FolCheck:

    def get_var_expr_name(self, fol_line):
        fol_line = fol_line.replace(' ', '')
        fol_line = fol_line.replace('(', '__').replace(')', '__')
        fol_line = fol_line.replace(',', '_')
        var = re.findall('\w+', fol_line)[0]
        return var, fol_line

    def get_var_expr(self, fol_line):
        fol_line = fol_line.replace(' ', '')
        fol_line = fol_line.replace('(', '__').replace(')', '__')
        fol_line = fol_line.replace(',', '_')
        return fol_line

    def logical_formula_to_py(self, logical_formula):
        logical_formula = logical_formula.replace(' ', '')
        logical_formula = logical_formula.replace('=', ':\n        return ')
        logical_formula = 'def ' + logical_formula
        return logical_formula

    def parse_sentence(self, sentence='func(a,b,c)'):
        sentence = sentence.replace(' ', '')
        s_obj = re.search(r'(\w+)\(([\w,\(\)]+)\)', sentence)
        if not s_obj:
            return ''

        func_name = s_obj.group(1)
        func_param = s_obj.group(2)
        list_func_param = func_param.split(',')
        return func_name, func_param, list_func_param

    def logical_var_to_py(self, logical_var):
        func_name, func_param, list_func_param = self.parse_sentence(logical_var)

        result = 'def %s:\n    ' % logical_var
        result += "    return eval('%s_%s__'.format(%s))"\
                % (func_name, '_{}'*len(list_func_param), func_param)
        return result

    def is_formula(self, expr):
        expr = expr.replace(' ', '')
        pos = expr.find('=')
        if pos == -1:
            return False
        body = expr[pos+1:]
        s_obj = re.search(r'(\w+)\(([\w,]+)\)', body)
        if s_obj:
            return True
        return False

    def get_body_logical_var(self, expr):
        expr = expr.replace(' ', '')
        if not self.is_formula(expr):
            return None

        pos = expr.find('=')
        body = expr[pos+1:]
        # 第一层解析
        list_logical_var = re.findall(r'\w+\([\w,\(\)]+\)', body)
        # 第二层解析，非嵌套场景不执行
        for logical_var in list_logical_var:
            func_name, func_param, list_func_param = self.parse_sentence(logical_var)
            for param in list_func_param:
                list_logical_var_level2 = re.findall(r'\w+\([\w,]+\)', param)
                list_logical_var.extend(list_logical_var_level2)

        # 消去参数括号
        list_logical_var_finish = []
        for logical_var in list_logical_var:
            func_name, func_param, list_func_param = self.parse_sentence(logical_var)
            if '(' in func_param:
                func_param = func_param.replace('(', '__').replace(')', '__') # 待完善：仅支持嵌套函数一个参数场景
                logical_var = "%s(%s)" % (func_name, func_param)
            list_logical_var_finish.append(logical_var)

        return list_logical_var_finish
    
    def get_formula_child(self, list_child_expr):
        for expr in list_child_expr:
            if self.is_formula(expr):
                return expr
        return ''

    def param_to_str(self, function):
        func_name, func_param, list_func_param = self.parse_sentence(function)
        result = func_name + '('
        for param in list_func_param:
            result += "'%s'," % param
        result = result.rstrip(',')
        result += ')'
        return result

    def parent_process(self, expr):
        expr = expr.replace(' ', '')
        # 将匹配的数字乘以 2
        def func(matched):
            value = matched.group()
            return self.param_to_str(value)
        
        return re.sub(r'\w+\([\w,]+\)', func, expr)

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            pass
    
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
    
        return False

    def is_number_value(self, fol_line):
        list_judge_sym = ['=', '>', '<', '>=', '<=']
        list_var = re.split('|'.join(list_judge_sym), fol_line)
        if self.is_number(list_var[-1]):
            return True
        else:
            return False

    def get_py_ver_define(self, fol_line):
        if fol_line.count('=') != 1:
            print('Expression error! 赋值非数字不支持“与、或、非”运算')
        list_var = fol_line.split('=') # 注意：字符串支持赋值，不支持大小比较
        return "%s='%s'\n    " % (list_var[0], list_var[1])

    def change_format(self, expr):
        expr = expr.replace('=', '==')
        la = LA.LexicalAnalyzer()
        expr = la.change_format(expr)
        return expr

    def get_fol_z3py_code(self, parent_expr, list_child_expr):
        result = 'from z3 import *\n'
        result += 'try:\n    '
        # 函数部分
        logical_formula = self.get_formula_child(list_child_expr)

        list_logical_var = self.get_body_logical_var(logical_formula)
        for logical_var in list_logical_var:
            py_var = self.logical_var_to_py(logical_var)
            result += py_var + '\n    '

        py_formula = self.logical_formula_to_py(logical_formula)
        result += py_formula + '\n    '

        # 逻辑部分
        result += 's = Solver()\n    '
        for expr in list_child_expr:
            if self.is_formula(expr):
                continue
            
            fol_line = self.get_var_expr(expr)
            # 添加表达式
            if self.is_number_value(fol_line):
                list_all_variable = re.findall(r'[a-zA-Z]\w+', fol_line)
                for var in list_all_variable:
                    result += "%s = Real('%s')\n    " % (var, var)
                result += "s.add(%s)\n    " % self.change_format(fol_line)
            else:
                result += self.get_py_ver_define(fol_line)

        # 父结点
        parent_expr = self.parent_process(parent_expr)
        parent_expr = self.change_format(parent_expr)
        result += "s.add(Not(%s))\n    " % parent_expr

        # 输出
        result += """
    ret = s.check()
    if ret == sat:
        print(s.model())
except:
    print('Expression error!')
"""
        return result

    def check(self, parent_expr, list_child_expr):
        code_path = './history/tmp_fol_z3.py'
        with open(code_path, 'w', encoding='utf-8') as f:
            z3code = self.get_fol_z3py_code(parent_expr, list_child_expr)
            f.write(z3code)

        cmd = r'python %s' % code_path
        with os.popen(cmd) as pf:
            return pf.read()


if __name__ == '__main__':
    
    parent_expr = 'response_time_obj(A,b)<2'

    list_child_expr = [
    'response_time(A,C)<2',
    'response_time_obj(module,response) = response_time(module,get_type(response))',
    'get_type(b)=C'
    ]

    fc = FolCheck()
    code = fc.get_fol_z3py_code(parent_expr, list_child_expr)
    with open('test.py', 'w') as f:
        f.write(code)
