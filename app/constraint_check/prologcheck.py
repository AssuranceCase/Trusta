import sys
sys.path.append('constraint_check/python_prolog')
from python_prolog.prologpy import solver as py_prolog_solver

class PrologCheck:
    def check(self, parent_expr, list_child_expr):
        list_child_expr = sorted(set(list_child_expr), key=list_child_expr.index) # 去重复,保留顺序

        rules_text = '\n'.join(list_child_expr)
        query_text, have_not = self.anlyTopClaim(parent_expr)

        # 推理
        state_info = []
        state = py_prolog_solver.run_query(rules_text, query_text, state_info)
        node_state = self.getNodeState(state, state_info, have_not)
        if not node_state:
            return str(state_info)
        else:
            return ''

    def getNodeState(self, state, state_info, have_not):
        # 语法错误
        if state == -1 or state == -2:
            return False

        if state == 1 and state_info[0] == 'Yes': # 成立
            node_state = True
        elif state == 2: # 有解
            node_state = True
        else: # 不成立、无解
            node_state = False
        if have_not: # 是否取反
            node_state = not node_state
        return node_state
    
    def anlyTopClaim(self, top_claim):
        have_not = False
        if top_claim.find('\+') == 0:
            have_not = True
            query_text = top_claim[2:].strip()
        else:
            query_text = top_claim.strip()
        return query_text, have_not
        