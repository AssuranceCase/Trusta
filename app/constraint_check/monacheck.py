import os

class MonaCheck:
    def get_mona_code(self, parent_expr, list_child_expr):
        var_code = ''
        formula_code = ''
        for expr in list_child_expr:
            if expr[-1] != ';':
                expr += ';'
            if expr.find('Set ') != -1 or expr.find('Elem ') != -1:
                var_code += expr.replace('Set ', 'var2 ').replace('Elem ', 'var1 ')
            else:
                formula_code += expr

        target_code = '~(%s);' % parent_expr.strip(';')
        result = var_code + formula_code + target_code
        return result

    def check(self, parent_expr, list_child_expr):
        code_path = os.path.abspath('./history/tmp_mona_code.mona')
        with open(code_path, 'w', encoding='utf-8') as f:
            mona_code = self.get_mona_code(parent_expr, list_child_expr)
            f.write(mona_code)

        curr_dir = os.getcwd()
        os.chdir('../bin/mona')
        cmd = r'mona.exe %s' % code_path
        with os.popen(cmd) as pf:
            output = pf.read()
        os.chdir(curr_dir)
        return self.parse_output(output)

    def parse_output(self, output):
        # print(output)
        if output.find('Formula is unsatisfiable') != -1:
            return '' # 无错误

        # 有错误，返回反例（求解器的满足例子，是原问题的反例）
        pos_start = output.find('A satisfying example')
        pos_end = output.find('Total time')
        satisfy_content = output[pos_start:pos_end]
        ret = satisfy_content.split('\n\n')[1]
        return ret.replace('\n', ', ')

if __name__ == '__main__':
    mc = MonaCheck()
    mc.checkSet(None, None)

    