import json, re

# 数据样例
dict_data_temp = {
    "nodeKeyProperty": "id",
    "nodeDataArray": [
        {"id": -1, "category": "Start"},
        {"id": 0, "text": "State1", "detail": "State1 info", "bcolor": "blue"},
        {"id": 1, "text": "State2", "detail": "State2 info", "bcolor": "blue"},
        {"id": -2, "category": "End"}
    ],
    "linkDataArray": [
        {"from": -1, "to": 0, "text": "next"},
        {"from": 0, "to": 1,  "progress": "false", "text": "next"},
        {"from": 0, "to": -2,  "progress": "true", "text": "next"},
        {"from": 1, "to": -2,  "progress": "true", "text": "next", "category": "relation"}
    ]
}

class DataService:
    pattern_varName = r'[0-9a-zA-z_\[\]*]+'
    dict_pattern = {
        "node": r'(%s)[ ]+:[ ]+"(.*)"\n' % pattern_varName,
        "link": r'(%s)[ ]+[-]{1,2}>[ ]+(%s)([ ]+:[ ]+.*){0,1}\n' % (pattern_varName, pattern_varName),
        "title": r'(%s)[ ]+=[ ]+"(.*)"\n' % pattern_varName,
        "nattr": r'(%s)[ ]+<<[ ]+"(.*)"\n' % pattern_varName,
        "relation": r'(%s)[ ]+--[ ]+(%s)\n' % (pattern_varName, pattern_varName),
    }
    dict_data = {
        "nodeKeyProperty": "id",
        "nodeDataArray": [],
        "linkDataArray": []
    }

    def getDefaultText(self):
        with open('./model/TextUML.txt', 'r', encoding='utf-8') as f:
            text = f.read()
        return text

    def clearData(self):
        self.dict_data = {
            "nodeKeyProperty": "id",
            "nodeDataArray": [],
            "linkDataArray": []
        }

    def plantUmltoGojs(self, code):
        self.clearData()

        # 清理注释
        list_line = code.split('\n')
        list_line = [line for line in list_line if line.find('#') != 0]
        code = '\n'.join(list_line)

        # 处理link数据
        pattern = re.compile(self.dict_pattern["link"])  # 查找连线
        linkData = pattern.findall(code)
        print(linkData)

        for link in linkData:
            fromNode = link[0]
            toNode = link[1]
            trans = link[2].lstrip(' ').lstrip(':').lstrip(' ')
            fromId = self.addNode(fromNode)
            toId = self.addNode(toNode)
            self.addLink(fromId, toId, trans)

        # 处理relation数据
        pattern = re.compile(self.dict_pattern["relation"])  # 查找关联
        relationData = pattern.findall(code)
        print(relationData)

        for relation in relationData:
            fromNode = relation[0]
            toNode = relation[1]
            fromId = self.addNode(fromNode)
            toId = self.addNode(toNode)
            self.addRelation(fromId, toId)

        # 处理node数据
        pattern = re.compile(self.dict_pattern["node"])  # 查找节点信息
        nodeData = pattern.findall(code)
        print(nodeData)

        for node in nodeData:
            nodeName = node[0]
            detail = node[1]
            self.setDetail(nodeName, detail)

        # 处理title数据
        pattern = re.compile(self.dict_pattern["title"])  # 查找名字信息
        titleData = pattern.findall(code)
        print(titleData)

        for title in titleData:
            nodeName = title[0]
            title = title[1]
            self.setTitle(nodeName, title)

        # 处理node attr数据
        pattern = re.compile(self.dict_pattern["nattr"])  # 查找节点属性信息
        nattrData = pattern.findall(code)
        print(nattrData)

        for nattr in nattrData:
            nodeName = nattr[0]
            nattr = nattr[1]
            self.setNattr(nodeName, nattr)

        return json.dumps(self.dict_data)


    def addNode(self, nodeName):
        # 若结点存在则直接返回Id
        node = self.findNode(nodeName)
        if node:
            return node["id"]

        # 添加结点
        nodeNum = len(self.dict_data["nodeDataArray"])
        nodeId = nodeNum + 1
        node = {"id": nodeId, "text": nodeName}
        if nodeName == '[Start]':
            node["category"] = 'Start'
        if nodeName == '[End]':
            node["category"] = 'End'
        self.dict_data["nodeDataArray"].append(node)
        return nodeId

    def addLink(self, fromId, toId, trans):
        self.dict_data["linkDataArray"].append({"from": fromId, "to": toId,  "progress": "false", "text": trans})

    def addRelation(self, fromId, toId):
        # 若结点不存在，则创建
        link = self.findLink(fromId, toId)
        if not link:
            self.addLink(fromId, toId, '')

        link = self.findLink(fromId, toId)
        link["category"] = "relation"

    def findNode(self, nodeName):
        for node in self.dict_data["nodeDataArray"]:
            if node["text"] == nodeName:
                return node
        return None

    def findLink(self, fromId, toId):
        for link in self.dict_data["linkDataArray"]:
            if link["from"] == fromId and link["to"] == toId:
                return link
        return None

    def setDetail(self, nodeName, detail):
        for node in self.dict_data["nodeDataArray"]:
            if node["text"] == nodeName:
                node["detail"] = detail

    def setTitle(self, nodeName, title):
        for node in self.dict_data["nodeDataArray"]:
            if node["text"] == nodeName:
                node["title"] = title

    def setNattr(self, nodeName, nattr):
        dict_nattr = self.getDict(nattr)
        for node in self.dict_data["nodeDataArray"]:
            if node["text"] == nodeName:
                node["bcolor"] = dict_nattr["bcolor"]

    def getDict(self, str_kv):
        list_kvs = str_kv.split(',')
        dist_detail = {}
        for kv in list_kvs:
            list_kv = kv.split(':')
            dist_detail[list_kv[0]] = list_kv[1]
        return dist_detail

if __name__ == '__main__':
    print(DataService().plantUmltoGojs('test'))
