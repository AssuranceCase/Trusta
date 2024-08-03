
class DecConf:
    dec = 0
    conf = 0

class BelDisbUncer:
    bel = 0
    disb = 0
    uncer = 0

class NodeParse:
    def getId(self, node):
        return node['id']

    def getTitle(self, node):
        return node['text']

    def getDetail(self, node):
        detail = node['detail']
        list_kvs = detail.split(',')
        dist_detail = {}
        for kv in list_kvs:
            list_kv = kv.split(':')
            dist_detail[list_kv[0]] = list_kv[1]
        return dist_detail

    def getDetailStr(self, dist_detail):
        str_detail = ''
        for k, v in dist_detail.items():
            str_detail += '%s:%s,' % (str(k), str(v))
        return str_detail.strip(',')

    def getDecConf(self, node):
        dc = DecConf()
        dist_detail = self.getDetail(node)
        dc.dec = float(dist_detail['dec'])
        dc.conf = float(dist_detail['conf'])
        return dc

    def isWellInfo(self, node):
        dist_detail = self.getDetail(node)
        list_keys = list(dist_detail.keys())
        if 'dec' in list_keys and 'conf' in list_keys:
            return True
        return False

    def needCal(self, node):
        dist_detail = self.getDetail(node)
        if len(dist_detail) == 1 and list(dist_detail.keys())[0] == 'type':
            return True
        return False


class LinkParse:
    def getFrom(self, link):
        return link['from']

    def getTo(self, link):
        return link['to']

    def getWeight(self, link):
        return float(link['text'])

class DataMng:
    np = NodeParse()
    lp = LinkParse()
    dict_data = {}
    def setData(self, dict_data):
        self.dict_data = dict_data.copy() # 浅拷贝

    def findNodeById(self, id):
        for node in self.dict_data["nodeDataArray"]:
            if self.np.getId(node) == id:
                return node
        return None

    def getChildNodes(self, node):
        list_nodes = []
        nodeId = self.np.getId(node)
        for link in self.dict_data["linkDataArray"]:
            if self.lp.getFrom(link) == nodeId:
                cnode = self.findNodeById(self.lp.getTo(link))
                cnode['weight'] = self.lp.getWeight(link)
                list_nodes.append(cnode)
        return list_nodes
