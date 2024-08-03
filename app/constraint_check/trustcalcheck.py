from safety_case.model import aggregation_algo as algo

class TrustCalCheck:
    algo = algo.AggregationAlgo()
    def cal_parent(self, parent_expr, list_child_expr):
        # 处理数据
        node = {}
        node['detail'] = self.get_line(parent_expr, 'type')

        list_child_node = []
        for expr in list_child_expr:
            tmp_node = {}
            tmp_node['detail'] = self.get_line(expr, 'dec')
            tmp_node['weight'] = float(self.expr_to_detail(self.get_line(expr, 'weight'))['weight'])
            list_child_node.append(tmp_node)

        # 计算
        ret_node = self.algo.calParent(node, list_child_node)

        str_node_content = '{}\n{}\n{}'.format(
            self.get_line(parent_expr, 'weight'),
            ret_node['detail'],
            ret_node['reliability']
        )

        return str_node_content.strip()

    def expr_to_detail(self, expr):
        list_kvs = expr.replace('\n', ',').split(',')
        dist_detail = {}
        for kv in list_kvs:
            list_kv = kv.split(':')
            dist_detail[list_kv[0]] = list_kv[1]
        return dist_detail

    def get_line(self, lines, key):
        for line in lines.split('\n'):
            if line.find(key) != -1:
                return line
        return ''

