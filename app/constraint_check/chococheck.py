import requests, json

class ChocoCheck:
    def checkSet(self, parent_AtomicExpr, list_child_AtomicExpr):
        url = 'http://120.27.151.237:8081/set_solver'
        d = {
            "parent": parent_AtomicExpr,
            "children": list_child_AtomicExpr
        }
        r = requests.post(url, json=d)
        dict_rep = json.loads(r.text)
        if dict_rep['result'] == 'unsolvable':
            return ''
        else:
            print(r.text)
            return r.text

if __name__ == '__main__':
    cc = ChocoCheck()
    cc.checkSet(None, None)

# elif reason == '集合推导_choco':
#     list_child_AtomicExpr = self.getAtomicExpr(list_child_expr)
#     parent_AtomicExpr = self.getAtomicExpr([parent_expr])[0]
#     cc = chococheck.ChocoCheck()
#     ret = cc.checkSet(parent_AtomicExpr, list_child_AtomicExpr)

    