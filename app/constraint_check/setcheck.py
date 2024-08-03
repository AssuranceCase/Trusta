import os

class SetCheck:
    def get_python_code(self, parent_expr, list_child_expr):
        template_code = """
{premise}
result = ({target})
if type(result) != type(True):
    print('Error: The target expression is required to be of type Boolean.')
if not result:
    print('The target expression is False.')
        """
        return template_code.format(premise='\n'.join(list_child_expr), target=parent_expr)

    def check(self, parent_expr, list_child_expr):
        code_path = os.path.abspath('./history/tmp_python_code.py')
        with open(code_path, 'w', encoding='utf-8') as f:
            python_code = self.get_python_code(parent_expr, list_child_expr)
            f.write(python_code)

        cmd = r'python %s' % code_path
        with os.popen(cmd) as pf:
            output = pf.read()
        return output

if __name__ == '__main__':
    sc = SetCheck()
    list_child_expr = ['s = {1,2,3,4}']
    parent_expr = 'len(s) == 4'
    ret = sc.checkSet(parent_expr, list_child_expr)
    print(ret)
