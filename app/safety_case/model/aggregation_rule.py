from model import aggregation_comm as comm
from model import aggregation_algo as algo

class AggregationRule:
    np = comm.NodeParse()
    lp = comm.LinkParse()
    dm = comm.DataMng()
    algo = algo.AggregationAlgo()

    def Cal(self, dict_data):
        # 初始化数据管理类
        self.dm.setData(dict_data)

        for node in dict_data["nodeDataArray"]:
            if self.np.isWellInfo(node):
                continue
            if self.np.needCal(node):
                node = self.calInfo(node)
            else:
                self.print('unexpected node: %s' % self.np.getTitle(node))
        return dict_data

    def calInfoAll(self, list_node):
        for node in list_node:
            if self.np.isWellInfo(node):
                continue
            if self.np.needCal(node):
                node = self.calInfo(node)
            else:
                self.print('unexpected node: %s' % self.np.getTitle(node))
        return list_node

    def calInfo(self, node):
        # 获取所有子节点
        list_child_node = self.dm.getChildNodes(node)
        # 完善子结点信息
        list_child_node = self.calInfoAll(list_child_node)
        # 计算父节点信息
        ret_node = self.algo.calParent(node, list_child_node)
        return ret_node

    def print(self, str):
        print(str)

