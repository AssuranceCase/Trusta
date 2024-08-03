import jstrans
import copy
import csv
import codecs
import os, sys, json, yaml, requests

try:
    sys.path.append('constraint_check')
    import z3check
    import chococheck
    import folcheck
    import monacheck
    import setcheck
    import prologcheck
    import trustcalcheck
except:
    pass
import re
import traceback
try:
    import translate
except:
    pass
from internation import HAN_EN
try:
    from sents_formal_llm.sentsformal import SentsFormal
    from auto_build_llm.autobuild import AutoBuild
    from auto_evaluation_llm.auto_evaluate import AutoEvaluate
    from sents_similarity_llm.sents_similarity import SentsSimilarity
except:
    pass
from func_analysis_llm.func_analysis import FunctionAnalysis
from func_analysis_llm.dot2json import dot_to_tdt
try:
    from others.similarity import Similarity
except:
    pass
from others.config_oper import Config


class NodeData:
    def __init__(self):
        self.nodeID = 0
        self.number = ''
        self.nodeName = ''
        self.nodeType = ''
        self.reason = ''
        self.attribute = HAN_EN.get('And')
        self.content = ''
        self.DSTheory = ''
        self.Addition = ''
        self.parentID = ''
        self.frameColor = ''
        self.nodeWidth = 0

class CsvData:
    def __init__(self, row, titles):
        data = {}
        for idx, title in enumerate(titles):
            data[title] = row[idx]

        self.nodeID = int(data.get('NODE_ID', 0))
        self.nodeName = data.get('NAME', '')
        self.nodeType = data.get('TYPE', '')
        self.reason = data.get('REASON', '')
        self.attribute = data.get('ATTRIBUTE', '')
        self.content = data.get('CONTENT', '')
        self.DSTheory = data.get('DSTHEORY', '')
        self.Addition = data.get('ADDITION', '')
        self.parentID = data.get('PARENT_ID', '')

class DataService:
    nodeDataArray = []
    linkDataArray = []
    src_func_data = None

    def get_config(self):
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config

    def json(self, file_path=None):
        dict_all = {
            'nodeDataArray': self.nodeDataArray,
            'linkDataArray': self.linkDataArray
        }
        j_all = json.dumps(dict_all, ensure_ascii=False, indent=4)
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(j_all)
        return j_all

    ''' assessment '''
    def autoEvaluateNode(self, ID, level, temperature):
        str_yaml = self.toGsnYaml(ID, level)
        
        ae = AutoEvaluate('./auto_evaluation_llm/prompts/gsn_evaluation.txt')
        evaluate_info = ae.evaluate(
            gsn_yaml=str_yaml,
            temperature=0.8,
            model='gpt-3.5'
        )
        return evaluate_info

    """ increase """
    def autoAddSubNodes(self, ID, level, temperature):
        node = self.findNodeByKey(ID)
        ab = AutoBuild('./auto_build_llm/prompts/gsn_builder_5_block.txt')
        sub_info = ab.build(
            goal=node.nodeName,
            temperature=temperature
        )
        print(sub_info)
        
        #  Add decomposition strategy 
        self.setAdditionKeyValue(ID, {"Strategy": sub_info['strategy'], "Block": sub_info['block']})

        #  Add child nodes 
        dict_subIDs = {}
        for G_id, subgoal in sub_info['subgoals'].items():
            new_ID = self.addNodeByName(parentID=ID, nodeName=subgoal, nodeType='Goal')
            dict_subIDs[G_id] = new_ID
        
        #  Add evidence node 
        if level == 0:
            for Sn_id, solution in sub_info['solutions'].items():
                support_G_id = Sn_id.replace('Sn', 'G')
                support_parentID = dict_subIDs.get(support_G_id, None)
                if support_parentID:
                    self.addNodeByName(parentID=support_parentID, nodeName=solution, nodeType='Solution')

        self.setNodesHighlight(list(dict_subIDs.values()), '#FFAAAA')
        return list(dict_subIDs.values())

    def addNodeByName(self, parentID, nodeName, nodeType='Goal', addition='', attribute=HAN_EN.get('And')):
        info = NodeData()
        info.nodeType = nodeType
        info.parentID = parentID
        info.nodeName = nodeName
        info.Addition = addition
        info.attribute = attribute

        new_ID = self.addNode((info.parentID, info.nodeName, info.content, info.attribute, info.nodeType,
                                info.reason, info.DSTheory, info.Addition))
        return new_ID

    #  Enter complete information of the node (including parent node information) and add the node 
    def addNode(self, info, ID = None, mklink=True):
        parentID = str(info[0])
        nodeName = info[1]
        content = info[2]
        attribute = info[3]
        nodeType = info[4]
        reason = info[5]
        DSTheory = info[6]
        Addition = info[7]
        if len(info) > 8:
            number = info[8]
        else:
            number = ''
        if parentID == '':
            parentID = '0'
        #  Add data 
        if ID == None:
            ID = self.getMaxID() + 1
        self.nodeDataArray.append({ "key": ID, "number": number, "question": "%d %s" % (ID, nodeName), "nodetype": nodeType, "reason": reason, "node_width": 0,
                                    "actions": [
                                        { "text": content }
                                    ],
                                    "DSTheory": [
                                        { "text": DSTheory }
                                    ],
                                    "Addition": [
                                        { "text": Addition }
                                    ]})

        #  Add a new one parentID
        if mklink:
            list_parentID = parentID.split(' ')
            for parentID in list_parentID:
                self.makeLink(int(parentID), ID, attribute)
        # self.linkDataArray.append({ "from": int(parentID), "to": ID, "answer": attribute })

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())
        return ID

    #  Create a default node using the node name 
    # force==True Indicates the mandatory creation of a node, regardless of whether the node name exists or not 
    def makeNode(self, nodeName, force = False):
        node = self.findNodeByName(nodeName)
        if node and not force:
            return node, node["key"]

        ID = self.getMaxID() + 1
        node = {"key": ID, "question": "%d %s" % (ID, nodeName),
         "actions": [
             {"text": ""}
         ],
         "DSTheory": [
             {"text": ""}
         ],
         "Addition": [
             {"text": ""}
         ]}
        self.nodeDataArray.append(node)
        return node, ID

    #  Create a link
    def makeLink(self, fromID, toID, answer = HAN_EN.get('And')):
        link =  {"from": fromID, "to": toID, "answer": answer}
        self.linkDataArray.append(link)
        return link

    #  copy ID To root a tree, return the root node of the new tree 
    def makeTree(self, ID):
        parentNode, parentID = self.makeNode(self.findNodeByKey(ID).nodeName, True)
        if not self.haveChild(ID):
            return parentNode

        list_childrenID = self.getChildrenID(ID)
        for ID in list_childrenID:
            node = self.makeTree(ID)
            self.makeLink(parentID, node["key"])

        return parentNode

    """ Delete """
    def delNode(self, str_ID):
        ID = int(str_ID)
        #  Delete data 
        tmp_nodeDataArray = []
        for node in self.nodeDataArray:
            if node["key"] != ID:
                tmp_nodeDataArray.append(node)
        self.nodeDataArray = copy.deepcopy(tmp_nodeDataArray)

        tmp_linkDataArray = []
        for link in self.linkDataArray:
            if link["to"] != ID and link["from"] != ID:
                tmp_linkDataArray.append(link)
        self.linkDataArray = copy.deepcopy(tmp_linkDataArray)

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    def delNodes(self, str_IDs):
        str_IDs = str_IDs.replace(' ， ', ',').replace(' ', ',')
        list_IDs = str_IDs.split(',')
        for ID in list_IDs:
            self.delNode(ID)
    
    def delNodesExcept(self, list_IDs):
        for node in self.nodeDataArray:
            ID = node["key"]
            if ID in list_IDs:
                continue
            self.delNode(ID)

    """ change """
    def editNode(self, ID, info):
        # self.delNode(ID)
        # self.addNode(info, ID)
        parentID = info.parentID
        nodeName = info.nodeName
        nodeType = info.nodeType
        reason = info.reason
        content = info.content
        attribute = info.attribute
        DSTheory = info.DSTheory
        Addition = info.Addition
        nodeWidth = info.nodeWidth

        for node in self.nodeDataArray:
            if node["key"] == ID:
                node["question"] = "%d %s" % (ID, nodeName)
                node["nodetype"] = nodeType
                node["reason"] = reason
                node["actions"][0]["text"] = content
                node["DSTheory"][0]["text"] = DSTheory
                node["Addition"][0]["text"] = Addition

                node["node_width"] = int(nodeWidth)
                node['actions'][0]['text_width'] = int(nodeWidth)
                node['DSTheory'][0]['text_width'] = int(nodeWidth)
                node['Addition'][0]['text_width'] = int(nodeWidth)

        for link in self.linkDataArray:
            if link["to"] == ID:
                link["answer"] = attribute

        # parentID Change, update Link
        str_parentID, cnt = self.getParentIDs(ID)
        if str_parentID != parentID:
            #  Delete current parentID
            list_tmplinkData = []
            for link in self.linkDataArray:
                if link["to"] != ID:
                    list_tmplinkData.append(link)
            self.linkDataArray = copy.deepcopy(list_tmplinkData)
            #  Add a new one parentID
            list_parentID = parentID.split(' ')
            for parentID in list_parentID:
                self.makeLink(int(parentID), ID, attribute)

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    def updateParentID(self, ID, new_ID):
        for link in self.linkDataArray:
            # to: Exclude self circulation situation 
            if link["from"] == ID and link["to"] != new_ID:
                link["from"] = new_ID

    def setAddAddition(self, ID, Type, Content):
        info = self.findNodeByKey(ID)
        if not info.Addition:
            info.Addition = '{}'
        dict_addition = json.loads(info.Addition)
        
        #  duplicate removal 
        src_type = Type
        for i in range(1, 100):
            if Type in dict_addition:
                Type = f'{src_type}_{i}'
        
        if Type not in dict_addition:
            self.setAdditionKeyValue(ID, {Type: Content})

            #  write in show_data.js file 
            jstrans.py2js(self.getStrData())
            return True

        return False

    def setAdditionKeyValue(self, ID, dict_kv):
        info = self.findNodeByKey(ID)
        if not info.Addition:
            info.Addition = '{}'
        dict_addition = json.loads(info.Addition)
        for k, v in dict_kv.items():
            dict_addition[k] = v
        info.Addition = json.dumps(dict_addition, indent=4, ensure_ascii=False)
        self.editNode(ID, info)

    def delAdditionKey(self, ID, list_key):
        info = self.findNodeByKey(ID)
        if not info.Addition:
            info.Addition = '{}'
        dict_addition = json.loads(info.Addition)
        for key in list_key:
            dict_addition.pop(key, '')
        info.Addition = json.dumps(dict_addition, indent=4, ensure_ascii=False)
        self.editNode(ID, info)

    def setNodeContent(self, ID, content):
        for node in self.nodeDataArray:
            if node["key"] == ID:
                node["actions"][0]["text"] = content
                return True
        return False

    def setNodeDSTheory(self, ID, content):
        for node in self.nodeDataArray:
            if node["key"] == ID:
                node["DSTheory"][0]["text"] = content
                # node["DSTheory"] = []
                # node["DSTheory"].append({"text": content})
                return True
        return False

    def setNodeAddition(self, ID, content):
        for node in self.nodeDataArray:
            if node["key"] == ID:
                node["Addition"][0]["text"] = content
                return True
        return False
    
    def setNodeColor(self, ID, is_normal):
        for node in self.nodeDataArray:
            if node["key"] == ID:
                if is_normal:
                    node['frameColor'] = '#C4ECFF' #  blue 
                else:
                    node['frameColor'] = '#FFFF66' #  yellow 

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    def setNodeWidth(self, ID, width):
        for node in self.nodeDataArray:
            if node["key"] == ID:
                node['node_width'] = width

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    def setAllNodeWidth(self, width, force=False):
        for node in self.nodeDataArray:
            if not force and 'node_width' in node and node['node_width'] != 0:
                width = node['node_width']
            node['node_width'] = width

            if 'actions' not in node:
                node['actions'] = [{}]
            node['actions'][0]['text_width'] = width

            if 'DSTheory' not in node:
                node['DSTheory'] = [{}]
            node['DSTheory'][0]['text_width'] = width

            if 'Addition' not in node:
                node['Addition'] = [{}]
            node['Addition'][0]['text_width'] = width

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    def cleanAllColor(self):
        for node in self.nodeDataArray:
            node.pop('frameColor', '')

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    #  Node Highlighting 
    def setNodesHighlight(self, list_ID, frameColor='#FF3333', nameTextColor='black'):
        for node in self.nodeDataArray:
            if node["key"] in list_ID:
                node['frameColor'] = frameColor
                node['nameTextColor'] = nameTextColor

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    # DS Change color 
    def setDSColor(self, list_ID, color='#ECECEC', textColor='white'):
        for node in self.nodeDataArray:
            if node["key"] in list_ID:
                #  background color  
                node['DSColor'] = node.get('frameColor', color)
                #  Font color 
                node['DSTheory'][0]['text_color'] = node.get('nameTextColor', textColor)

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    #  Set qualitative and quantitative panel switches 
    def setAllActionsShow(self, state):
        for node in self.nodeDataArray:
            if state:
                node["actions_show"] = 'show'
            else:
                node["actions_show"] = 'none'

    def setAllDSTheoryShow(self, state):
        for node in self.nodeDataArray:
            if state:
                node["DSTheory_show"] = 'show'
            else:
                node["DSTheory_show"] = 'none'

    def setAllAdditionShow(self, state):
        for node in self.nodeDataArray:
            if state:
                node["Addition_show"] = 'show'
            else:
                node["Addition_show"] = 'none'

    def createAllStrategyNode(self):
        for node in self.nodeDataArray:
            self.createStrategyNode(node)

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    def closeAllStrategyNode(self):
        for node in self.nodeDataArray:
            self.closeStrategyNode(node)

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    def closeStrategyNode(self, node):
        ID = node['key']
        if self.getNodeType(node) in HAN_EN.gets('Strategy'):
            str_Strategy = self.getNodeName(node)
            str_parentIDs, cnt = self.getParentIDs(ID)
            parentID = int(str_parentIDs)
            #  Write policy information to the parent node 
            self.setAdditionKeyValue(parentID, {"Strategy": str_Strategy})
            #  Modify child node attachment 
            self.updateParentID(ID, parentID)
            #  Delete policy node 
            self.delNode(ID)

    def createStrategyNode(self, node):
        ID = node['key']
        addition = self.getAdditionContent(node)
        if not addition:
            return
        addi_info = json.loads(addition)
        if "Strategy" in addi_info or "S" in addi_info:
            #  Obtain strategy information 
            if "S" in addi_info and "Strategy" not in addi_info:
                addi_info['Strategy'] = addi_info['S']
            str_Strategy = addi_info['Strategy']
            self.delAdditionKey(ID, ['Strategy', 'S'])
            #  Create policy node 
            new_ID = self.addNodeByName(ID, str_Strategy, 'Strategy')
            #  Modify child node attachment 
            self.updateParentID(ID, new_ID)


    def setAllNodeMode(self, mode):
        if mode == 'DSTheory':
            self.setAllActionsShow(False)
            self.setAllDSTheoryShow(True)
            self.setAllAdditionShow(False)
        elif mode == 'actions':
            self.setAllActionsShow(True)
            self.setAllDSTheoryShow(False)
            self.setAllAdditionShow(False)
        elif mode == 'Addition':
            self.setAllActionsShow(False)
            self.setAllDSTheoryShow(False)
            self.setAllAdditionShow(True)
        elif mode == 'allshow':
            self.setAllActionsShow(True)
            self.setAllDSTheoryShow(True)
            self.setAllAdditionShow(True)
        elif mode == 'normal':
            self.setAllActionsShow(True)
            self.setAllDSTheoryShow(False)
            self.setAllAdditionShow(True)
        elif mode == 'DS_Addition':
            self.setAllActionsShow(False)
            self.setAllDSTheoryShow(True)
            self.setAllAdditionShow(True)
        elif mode == 'allhide':
            self.setAllActionsShow(False)
            self.setAllDSTheoryShow(False)
            self.setAllAdditionShow(False)
        
        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    def setNodeName(self, node, new_name):
        id = node["question"].split(' ', 1)[0]
        node["question"] = f'{id} {new_name}'
        return node
    
    def setNodeNameWithID(self, node, new_question):
        node["question"] = new_question

    def translateTo(self, lang):
        ls = translate.LocalTranslation(lang)

        for node in self.nodeDataArray:
            #  Translate node name 
            name = self.getNodeName(node)
            dest_text = translate.Translate(src_text=name, dest_lang=lang, ls=ls)
            node = self.setNodeName(node, new_name=dest_text)

            #  Translate additional content 
            # addition = self.getAdditionContent(node)
            # if addition:
            #     dest_text = translate.Translate(src_text=addition, dest_lang=lang, ls=ls)
            #     self.setNodeAddition(node['key'], dest_text)
        
        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    """ check """
    def findNodeByName(self, nodeName):
        for node in self.nodeDataArray:
            if self.getNodeName(node) == nodeName:
                return node
        return None

    def findNodeByNumber(self, number):
        for node in self.nodeDataArray:
            if self.getNodeNumber(node) == number:
                return node
        return None
    
    def findNodeByID(self, ID):
        for node in self.nodeDataArray:
            if node['key'] == ID:
                return node
        return None
    
    def searchNodeByLikeName(self, searchKey):
        like_nodes = []
        for node in self.nodeDataArray:
            if self.getNodeName(node).find(searchKey) != -1:
                like_nodes.append(node)
        return like_nodes
    
    def searchNodeNotLikeAddition(self, searchKey):
        not_like_nodes = []
        for node in self.nodeDataArray:
            if self.getAdditionContent(node).find(searchKey) == -1:
                not_like_nodes.append(node)
        return not_like_nodes

    def findNodeByKey(self, ID):
        info = NodeData()
        info.nodeID = ID
        for node in self.nodeDataArray:
            if node["key"] == ID:
                info.nodeName = self.getNodeName(node)
                info.content = self.getNodeContent(node)
                info.DSTheory = self.getDSTheoryContent(node)
                info.Addition = self.getAdditionContent(node)
                info.nodeWidth = self.getNodeWidth(node)
                info.number = self.getNodeNumber(node)
                if 'reason' in node.keys():
                    info.reason = self.getReason(node)
                if 'nodetype' in node.keys():
                    info.nodeType = self.getNodeType(node)
                if 'frameColor' in node.keys():
                    info.frameColor = self.getNodeFrameColor(node)
                break

        for link in self.linkDataArray:
            if link["to"] == ID:
                info.parentID += (' ' + str(link["from"]))
                info.attribute = link["answer"]

        info.parentID = info.parentID.strip(' ')
        return info

    #  Through nodes ID , obtain all child nodes ID
    def getChildrenID(self, ID):
        list_childrenID = []
        for lk in self.linkDataArray:
            if lk["from"] == ID:
                list_childrenID.append(lk["to"])
        return list_childrenID
    
    #  Through nodes ID , obtain all child nodes   name 
    def getChildrenName(self, ID):
        dict_childrenName_nodetype = {}
        list_childrenID = self.getChildrenID(ID)
        for cID in list_childrenID:
            obj_node = self.findNodeByKey(cID)
            dict_childrenName_nodetype[obj_node.nodeName] = obj_node.nodeType
        return dict_childrenName_nodetype

    #  Through nodes ID , obtain all descendant nodes ID
    def getDescendantIDs(self, ID, list_descendant_ids, need_level=99999):
        if need_level <= 0:
            return
        list_descendant_ids.append(ID)
        list_childrenID = self.getChildrenID(ID)
        for cId in list_childrenID:
            self.getDescendantIDs(cId, list_descendant_ids, need_level-1)
    
    #  Through nodes ID , obtain all descendant nodes (ID, Level)
    def getDescendantIDLevel(self, ID, list_descendant, level):
        list_descendant.append((ID, level))
        list_childrenID = self.getChildrenID(ID)
        for cId in list_childrenID:
            self.getDescendantIDLevel(cId, list_descendant, level+1)

    #  Through nodes ID , obtain all parent nodes ID
    def getParentIDs(self, ID):
        ID = int(ID)
        #  Return node in degree (number of parent nodes) 
        cnt = 0
        str_parentIDs = ''
        for link in self.linkDataArray:
            if link["to"] == ID:
                cnt += 1
                str_parentIDs += (' ' + str(link["from"]))
        str_parentIDs = str_parentIDs.strip(' ')
        return str_parentIDs, cnt

    #  Through nodes ID , obtain the parent nodes on all paths ID
    def getPathParentIDs(self, ID, list_IDs):
        #  Return node in degree (number of parent nodes) 
        for link in self.linkDataArray:
            if link["to"] == ID:
                list_IDs.append(link["from"])
                self.getPathParentIDs(link["from"], list_IDs)

    #  judge ID Does the node have children 
    def haveChild(self, ID):
        for lk in self.linkDataArray:
            if lk["from"] == ID:
                return True
        return False

    #  Is it an evidence type node 
    def isEvidence(self, ID):
        for node in self.nodeDataArray:
            if node["key"] == ID and self.getNodeType(node) in (HAN_EN.gets('EVID') + HAN_EN.gets('Solution')):
                return True
        return False
    
    #  Is it a node of the target type 
    def isGoal(self, ID):
        for node in self.nodeDataArray:
            if node["key"] == ID and self.getNodeType(node) in HAN_EN.gets('Goal'):
                return True
        return False

    #  Collection of node contents for evidence types 
    def getAllEvidenceContent(self):
        allEvidence = []
        for node in self.nodeDataArray:
            if self.getNodeType(node) in HAN_EN.gets('EVID'):
                allEvidence.append(self.getNodeContent(node))
        return allEvidence

    #  Get root node 
    def getRootNode(self):
        root_id = None
        for lk in self.linkDataArray:
            if lk["from"] == 0:
                root_id = lk["to"]
                break

        if not root_id:
            list_from = [lk["from"] for lk in self.linkDataArray]
            list_to = [lk["to"] for lk in self.linkDataArray]
            set_root_id = set(list_from) - set(list_to)
            if len(set_root_id) == 1:
                root_id = list(set_root_id)[0]
                
        return self.findNodeByKey(root_id)

    #  Get the current maximum ID
    def getMaxID(self):
        maxID = 0
        for node in self.nodeDataArray:
            if node["key"] > maxID:
                maxID = node["key"]
        return maxID

    #  Get all content (constraint expression) 
    def getAllChildrenExpr(self, ID, DSTheory=False):
        list_childrenID = self.getChildrenID(ID)
        list_child_expr = []
        for cId in list_childrenID:
            if DSTheory:
                expr = self.findNodeByKey(cId).DSTheory
            else:
                expr = self.findNodeByKey(cId).content
            list_child_expr.append(expr)
        return list_child_expr
    
    #  Get all child node names 
    def getAllChildrenNameWithFuncName(self, ID):
        list_childrenID = self.getChildrenID(ID)
        list_child_func_goal = []
        for cId in list_childrenID:
            func_goal = self.findNodeByKey(cId).nodeName
            Addition = self.findNodeByKey(cId).Addition
            addi_info = json.loads(Addition)
            try: # python
                func_name = addi_info['Info'].split('\n')[0].rsplit('.', 1)[1]
            except: # callgrind
                func_name = addi_info['Info'].split('\n')[1]
            list_child_func_goal.append(f'{func_name}: {func_goal}')
        return list_child_func_goal

    #  Retrieve the properties of child nodes 
    def getAllChildrenAttr(self, ID):
        list_childrenID = self.getChildrenID(ID)
        list_child_attr = []
        for cId in list_childrenID:
            attr = self.findNodeByKey(cId).attribute
            list_child_attr.append(attr)

        set_child_attr = set(list_child_attr)
        if len(set_child_attr) != 1:
            return False
        else:
            return list(set_child_attr)[0]
    
    def getAllChildrenColor(self, ID):
        list_childrenID = self.getChildrenID(ID)
        list_child_color = []
        for cId in list_childrenID:
            frameColor = self.findNodeByKey(cId).frameColor
            list_child_color.append(frameColor)

        if list_child_color.count('#FFFF66') == len(list_childrenID) and len(list_childrenID) != 0: #  yellow 
            return 'all_#FFFF66'
        else:
            return ''

    def delete_if_then(self, parent_expr, list_child_expr):
        parent_expr = parent_expr.replace('IF  THEN', '').strip()
        list_child_expr = [child_expr.replace('IF  THEN', '').strip() for child_expr in list_child_expr]
        return parent_expr, list_child_expr

    def pretreatment_format(self, parent_expr, list_child_expr):
        #  Delete from the content if then
        parent_expr, list_child_expr = self.delete_if_then(parent_expr, list_child_expr)

        #  Only the first row of the parent node is the target 
        parent_expr_L = ''
        list_child_expr_L = []

        list_parent_expr = parent_expr.split('\n')
        parent_expr_L = list_parent_expr[0]

        list_child_expr_L.extend(list_parent_expr[1:])
        for child_expr in list_child_expr:
            list_child_expr_L.extend(child_expr.split('\n'))

        return parent_expr_L, list_child_expr_L

    def or_check(self, check_obj, parent_expr, list_child_expr):
        list_t_ret = []
        for child_expr in list_child_expr:
            t_ret = check_obj.check(parent_expr, [child_expr])
            list_t_ret.append(t_ret)
        if '' in list_t_ret:
            return ''
        else:
            return ', '.join(list_t_ret)

    #  Determine whether the constraints of the subtree are compliant 
    def ConstraintProve(self, parentID):
        list_child_expr = self.getAllChildrenExpr(parentID)
        if len(list_child_expr) == 0:
            return
        parentNode = self.findNodeByKey(parentID)
        parent_expr = parentNode.content
        reason = parentNode.reason

        attr = self.getAllChildrenAttr(parentID)
        if not attr:
            return ' The relationship between child nodes is unclear (and | Or) '

        ret = ''
        try:
            parent_expr, list_child_expr = self.pretreatment_format(parent_expr, list_child_expr)
            check_obj = None
            if reason in HAN_EN.gets('Arithmetic'): # z3
                check_obj = z3check.Z3Check()
            elif reason in HAN_EN.gets('AbstractSets'): # mona
                check_obj = monacheck.MonaCheck()
            elif reason in HAN_EN.gets('SpecificSets'): # python
                check_obj = setcheck.SetCheck()
            elif reason in HAN_EN.gets('Functional'): # z3
                check_obj = folcheck.FolCheck()
            elif reason in HAN_EN.gets('LogicalRelations'): # prolog type 
                check_obj = prologcheck.PrologCheck()
            elif reason in HAN_EN.gets('Quantified'): # D-S Theoretical extension 
                check_obj = trustcalcheck.TrustCalCheck()

                parent_content = parentNode.content
                list_child_content = self.getAllChildrenExpr(parentID)
                parent_content, list_child_content = self.delete_if_then(parent_content, list_child_content)

                str_node_content = check_obj.cal_parent(parent_content, list_child_content)
                # self.setNodeDSTheory(parentID, str_node_content)

                #  The credibility is 1 Believe it to be trustworthy 
                if str_node_content.find('bel:1') != -1:
                    return ''

                return str_node_content

            if not check_obj:
                return '' #  No above reasoning 
            if attr in HAN_EN.gets('And'):
                ret = check_obj.check(parent_expr, list_child_expr)
            elif attr in HAN_EN.gets('Or'):
                ret = self.or_check(check_obj, parent_expr, list_child_expr)
            else:
                return ' The relationship between child nodes is unknown (and | Or) '
        except:
            traceback.print_exc()
            return ' Expression error! '
        return ret

    def TestcaseCheck(self, ID):
        node = self.findNodeByID(ID)
        addition = self.getAdditionContent(node)
        if not addition:
            return True
        addition = json.loads(addition)
        try:
            r = requests.post(url=addition['url'], json=addition)
            resp = r.json()
            # result = 'OK' or 'Error'
            # resp = {"status": result, "msg": error_msg}
        except:
            return 'URL  The address is invalid. '

        if resp['status'] == 'OK':
            return ''
        else:
            return resp['msg']

    # DSTheory Calculate the second level subtree 
    def DSTheoryCal(self, parentID):
        list_child_expr = self.getAllChildrenExpr(parentID, DSTheory=True)
        if len(list_child_expr) == 0:
            return
        parentNode = self.findNodeByKey(parentID)
        parent_expr = parentNode.DSTheory
        
        if not parent_expr:
            return

        check_obj = trustcalcheck.TrustCalCheck()
        str_node_content = check_obj.cal_parent(parent_expr, list_child_expr)
        self.setNodeDSTheory(parentID, str_node_content)

        jstrans.py2js(self.getStrData())

    #  Get all set conditions 
    def getAtomicExpr(self, list_child_expr):
        list_AtomicExpr = []
        #  handle IF  THEN * form  or  Without it IF
        for child_expr in list_child_expr:
            if child_expr.strip().find('IF  THEN') == 0 or child_expr.strip()[:2] != 'IF':
                child_expr = child_expr.replace('IF  THEN', '').replace('`', '')
                tmp_list_expr = child_expr.split('&&')
                tmp_list_expr = [expr.strip() for expr in tmp_list_expr]
                list_AtomicExpr += tmp_list_expr
        
        #  handle IF * THEN * form 
        for child_expr in list_child_expr:
            if child_expr.strip().find('IF') == 0 and child_expr.strip().find('IF  THEN') == -1:
                pos = child_expr.find('THEN')
                ifContent = child_expr[2:pos].replace('`', '').strip()
                thenContent = child_expr[pos+4:].replace('`', '').strip()

                if_list_expr = ifContent.split('&&')
                if_list_expr = [expr.strip() for expr in if_list_expr]

                set_cut = set(if_list_expr) - set(list_AtomicExpr)
                if len(set_cut) == 0: # if Condition met 
                    list_AtomicExpr.append(thenContent)

        return list_AtomicExpr

    #  Dyeing of parent node path, considering the hindrance of or 
    def tintagePathParent(self, node):
        node['frameColor'] = '#FFFF66' #  yellow 
        ID = node["key"]

        list_IDs = [] #  Save the paths of all erroneous nodes and their parent nodes ID
        self.getPathParentIDs(ID, list_IDs) #  Save the parent node of the erroneous node ID
        #  All parent nodes are marked in yellow ( reach " or " by )
        stop_idx = len(list_IDs) - 1 #  Default to root node 
        for i in range(len(list_IDs)-1):
            attr =  self.getAllChildrenAttr(list_IDs[i])
            if attr == HAN_EN.get('Or'):
                stop_idx = i
                break

        set_IDs = set(list_IDs[:stop_idx])
        for node in self.nodeDataArray:
            if node["key"] in set_IDs:
                node['frameColor'] = '#FFFF66' #  yellow 

    #  Fill in formal text 
    def formalAllEmpty(self):
        sf = SentsFormal('./sents_formal')
        list_fill_ID = []
        for node in self.nodeDataArray:
            ID = node["key"]
            if self.getNodeContent(node) == '':
                nl = self.getNodeName(node)
                formal = sf.formalize(nl)
                if formal != '':
                    self.setNodeContent(ID, formal)
                    list_fill_ID.append(ID)
        return list_fill_ID

    def get_func_body(self, func_id):
        func_id = func_id.replace('.part.0', '')
        func_id = func_id.replace("'2", '')
        
        if not self.src_func_data:
            config = self.get_config()
            src_func_path = config['FUNCTION_CODE_PATH']
            if not os.path.exists(src_func_path):
                raise FileNotFoundError(f'Error: config.json: FUNCTION_CODE_PATH="{src_func_path}" not found!')
            with open(src_func_path, 'r', encoding='utf-8') as f:
                self.src_func_data = json.load(f)

        if func_id in self.src_func_data:
            return self.src_func_data[func_id]
        else:
            try:
                func_id = func_id.split('.', 1)[1]
            except:
                return None
            return self.src_func_data.get(func_id, None)

    def extract_and_format_test_log(self, s):
        pattern = r'FAIL: (\w+) \((\w+\.\w+)\)'
        match = re.search(pattern, s)
        if match:
            #  Extract matching parts 
            method_name, class_with_module = match.groups()
            #  Separate module name and class name 
            module_name, class_name = class_with_module.rsplit('.', 1)
            #  Format output 
            return f"{class_name}.{method_name}"
        else:
            return None

    def flagFailSolution(self, unit_test_log_path):
        #  Obtain failed test cases 
        with open(unit_test_log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        fail_tast_case = []
        for line in lines:
            result = self.extract_and_format_test_log(line)
            if result:
                fail_tast_case.append(result)
        
        #  Search for solution nodes 
        fail_node_ids = []
        for node in self.nodeDataArray:
            ID = node['key']
            if not self.isEvidence(ID):
                continue
            test_case_name = self.getNodeName(node).replace('TestCase: ', '')
            if test_case_name in fail_tast_case:
                fail_node_ids.append(ID)
        return fail_node_ids

    def compareOtherJson(self, new_tree_json):
        #  Import new tree
        with open(new_tree_json, 'r', encoding='utf-8') as f:
            dict_data = json.load(f)
        
        new_ds = DataService()
        new_ds.nodeDataArray = dict_data['nodeDataArray']
        new_ds.linkDataArray = dict_data['linkDataArray']

        list_diff_node = []
        root_1 = self.getRootNode().nodeID
        root_2 = new_ds.getRootNode().nodeID
        self.CompareTree(root_1, root_2, list_diff_node, new_ds)

        return list_diff_node
    
    def CompareTree(self, root_id_1, root_id_2, list_diff_node, new_ds):
        if root_id_1 == -1 and root_id_2 == -1:
            return
        elif root_id_1 == -1 and root_id_2 != -1:
            str_parentIDs, cnt = self.getParentIDs(root_id_1)
            for p_id in str_parentIDs.split(' '):
                p_id = int(p_id)
                list_diff_node.append({"key": p_id, "msg": "Extra function call."})
            return
        elif root_id_1 != -1 and root_id_2 == -1:
            list_diff_node.append({"key": root_id_1, "msg": "Break execution."})
            return
        else:
            node_1 = self.findNodeByKey(root_id_1)
            node_2 = new_ds.findNodeByKey(root_id_2)
            try:
                func_1 = json.loads(node_1.Addition)['Info'].split('\n')[0]
                func_2 = json.loads(node_2.Addition)['Info'].split('\n')[0]
            except:
                print('Addition Error:')
                print('node Ad 1: ', node_1.Addition)
                print('node Ad 2: ', node_2.Addition)
                return
            if func_1 != func_2:
                list_diff_node.append({"key": root_id_1, "msg": "Different execution path."})
                return
            else:
                list_childrenID_1 = self.getChildrenID(root_id_1)
                list_childrenID_2 = new_ds.getChildrenID(root_id_2)
                len1, len2 = len(list_childrenID_1), len(list_childrenID_2)
                for i in range(max(len1, len2)):
                    child1 = list_childrenID_1[i] if i < len1 else -1
                    child2 = list_childrenID_2[i] if i < len2 else -1
                    self.CompareTree(child1, child2, list_diff_node, new_ds)


    def AddSolutions(self):
        for node in self.nodeDataArray:
            ID = node['key']
            if not self.isGoal(ID):
                continue
            # if self.haveChild(ID):
            #     continue
            addition = self.getAdditionContent(node)
            addi_info = json.loads(addition)
            func_name = addi_info['Info'].split('\n')[0].rsplit('.', 1)[1]
            list_testcase = self.get_testcase_names(func_name)
            for test_name in list_testcase:
                test_name = test_name.replace('main.', '')
                self.addNodeByName(parentID=ID, nodeName=f'TestCase: {test_name}', nodeType='Solution', attribute=HAN_EN.get('Or'))
        
        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

    def get_testcase_names(self, func_name):
        # src_test_path='func_analysis_llm/callgraph_data/src_test_data.json'
        src_test_path = Config().get_config("TESTCASE_CODE_PATH")
        if not src_test_path:
            print('testcase body file not found.')
            return []
        with open(src_test_path, 'r', encoding='utf-8') as f:
            src_test_data = json.load(f)

        list_related_test = []
        for test_name, test_body in src_test_data.items():
            if f'{func_name}(' in test_body:
                list_related_test.append(test_name)
        return list_related_test

    def InitNodeToContext(self):
        need_del_ID = [] #  Prevent premature deletion of reused nodes 
        for node in self.nodeDataArray:
            C_num = 1
            ID = node['key']
            list_childrenID = self.getChildrenID(ID)
            for c_ID in list_childrenID:
                c_node = self.findNodeByID(c_ID)
                addition = self.getAdditionContent(c_node)
                if not addition:
                    continue
                addition = json.loads(addition)
                if addition['Info'].find('.__init__') != -1:
                    #  Constructor node 
                    context = self.getNodeName(c_node)
                    self.setAdditionKeyValue(ID, {f'C{C_num}': context})
                    C_num += 1
                    need_del_ID.append(c_ID)
        
        for ID in need_del_ID:
            self.delNode(ID)
        
        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())
        

    def loadDot(self, dot_path, encoding='utf-8'):
        try:
            with open(dot_path, 'r', encoding=encoding) as f:
                dot_string = f.read()
        except:
            if encoding == 'utf-8':
                encoding = 'utf-16'
            with open(dot_path, 'r', encoding=encoding) as f:
                dot_string = f.read()
        #  Convert and print  JSON
        dict_output = dot_to_tdt(dot_string)

        self.nodeDataArray = dict_output['nodeDataArray']
        self.linkDataArray = dict_output['linkDataArray']

        self.setAllNodeWidth(300) #  Node default width 
        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())

        return ''

    #  Large Language Model (LLM)   Analysis function 
    def functionAnalysisLLM(self, rootID, level, temperature):
        #  Determine the subtree range that needs to be checked 
        list_descendant_ids = []
        self.getDescendantIDs(rootID, list_descendant_ids, level)
        list_descendant_ids = list_descendant_ids[::-1] #  Traverse from the front sequence  ->  First access the child node, then access the parent node 
        
        fa = FunctionAnalysis(prompt_temp_path='./func_analysis_llm/prompts/function_analysis.txt')
        list_fill_ID = []
        list_error_info = []
        
        for i, ID in enumerate(list_descendant_ids):
            if ID in list_fill_ID:
                continue #  Double parent node situation, may occur repeatedly, filter here 

            node = self.findNodeByID(ID)
            func_id = self.getNodeName(node)
            func_body = self.get_func_body(func_id)
            if not func_body:
                list_error_info.append(f'Analysis failed, function "{func_id}" Not found.')
                continue
            
            list_external_func = self.getAllChildrenNameWithFuncName(ID)
            result_info = fa.analysis(
                func_name=func_id,
                func_code=func_body,
                list_external_func=list_external_func,
                temperature=temperature,
                model='gpt-3.5',
                msg = f'# [{i+1}/{len(list_descendant_ids)}] {func_id}.'
            )
            if 'error_info' in result_info:
                list_error_info.append(result_info)
                continue

            function_goal = result_info['function_goal'].strip('\n')
            self.setNodeName(node, new_name=f'{function_goal}')
            self.setNodeDSTheory(ID, func_id)
            # self.setAdditionKeyValue(ID, {"Function": func_id})
            if len(list_external_func) > 0:
                self.setAdditionKeyValue(ID, {"Strategy": result_info['strategy']})
            list_fill_ID.append(ID)

        if len(list_error_info) > 0:
            return False, list_fill_ID, list_error_info
        return True, list_fill_ID, list_error_info


    #  Large Language Model (LLM)   Fill in formal text 
    def formalAllEmptyLLM(self, formalRootID, proveLevel):
        #  Determine the subtree range that needs to be checked 
        list_descendant_ids = []
        self.getDescendantIDs(formalRootID, list_descendant_ids, proveLevel)
        
        sf = SentsFormal(prompt_temp_path='./sents_formal_llm/prompts/arithmetic.txt')
        list_fill_ID = []
        for node in self.nodeDataArray:
            ID = node["key"]
            #  Block some nodes 
            if ID not in list_descendant_ids:
                continue
            if self.getNodeContent(node) == '':
                nl = self.getNodeName(node)
                list_formal, sub_trans_stats_result = sf.formalize(
                    sentence = nl,
                    given_trans = {},
                    num_tries = 1,
                    temperature = 0.2
                )
                
                if len(list_formal) > 0:
                    formal = list_formal[0]
                    self.setNodeContent(ID, formal)
                    list_fill_ID.append(ID)
        return list_fill_ID

    #  Check if all subtrees in the tree are compliant 
    def checkAllExpr(self, proveRootID):
        #  Cancel all staining 
        for node in self.nodeDataArray:
            if 'frameColor' in node.keys():
                del node['frameColor']

        #  Determine the subtree range that needs to be checked 
        list_descendant_ids = []
        self.getDescendantIDs(proveRootID, list_descendant_ids)

        dict_err_info = {}
        for node in self.nodeDataArray:
            ID = node["key"]
            nodetype = self.getNodeType(node)
            if ID not in list_descendant_ids:
                continue
            if nodetype in HAN_EN.gets('Solution'):
                ret = self.TestcaseCheck(ID)
            else: #  Target subtree inference 
                ret = self.ConstraintProve(ID)
            if ret:
                dict_err_info[' Node number is  {}  Error message for subtree '.format(ID)] = ret
                self.tintagePathParent(node) #  Dyeing of parent nodes on the path 

        #  All sibling nodes are yellow, and the upper layer continues to be highlighted in yellow ,( Mainly targeting ” or “)
        have_all_yellow = True
        while have_all_yellow:
            tintage_flag = False
            for node in self.nodeDataArray:
                #  Child nodes are all yellow, current node is not yellow 
                if self.getAllChildrenColor(node["key"]) == 'all_#FFFF66' and self.getNodeFrameColor(node) != '#FFFF66':
                    self.tintagePathParent(node) #  Dyeing of parent nodes on the path 
                    tintage_flag = True
            if not tintage_flag:
                have_all_yellow = False


        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())
        return dict_err_info


    """ transcoding  """
    #  Convert member data into string format for writing text 
    def getStrData(self):
        str_data = 'nodeDataArray = %s\nlinkDataArray = %s\n' \
                   % (str(self.nodeDataArray), str(self.linkDataArray))
        return str_data

    def getNodeName(self, node):
        return node["question"].split(' ', 1)[1]
    
    def getNodeNumber(self, node):
        return node.get("number", False)

    def getNodeWidth(self, node):
        return node["node_width"]

    def getNodeType(self, node):
        return node.get("nodetype", "Goal")

    def getReason(self, node):
        return node["reason"]

    def getNodeContent(self, node):
        return node["actions"][0].get("text", "")

    def getDSTheoryContent(self, node):
        return node["DSTheory"][0].get("text", "")

    def getAdditionContent(self, node):
        return node["Addition"][0].get("text", "")
    
    def getNodeFrameColor(self, node):
        if "frameColor" in node.keys():
            return node["frameColor"]
        return ''

    """ Import prolog function  Begin"""
    def parse_prolog_all(self, src, quotesSwitch):
        # pattern = r'"?.*?"?\s*:-\s*("?.*?"?,\s*)*?("?.*?"?\.)' #  Quotation marks optional 
        if quotesSwitch in HAN_EN.gets('Yes'):
            pattern = r'".*?"\s*:-\s*(".*?",\s*)*?(".*?"\.)' #  matching  "A" :- "B C", D.
        else:
            pattern = r'.*?\s*:-\s*(.*?,\s*)*?(.*?\.)' #  matching  A :- B, C, D.
        src_one_line = src.replace('\n', '')

        lines = []
        search_obj = re.search(pattern, src_one_line)
        while search_obj:
            line = search_obj.group()
            lines.append(line)
            src_one_line = src_one_line.replace(line, '')
            search_obj = re.search(pattern, src_one_line)
        return lines

    def parse_prolog_line(self, src, quotesSwitch):
        sp = src.split(':-')
        head = sp[0].strip(' ').strip('"').strip()
        body = sp[1]

        if quotesSwitch in HAN_EN.gets('Yes'):
            pattern = r'"(.*?)"[,|.]' # "B C"
        else:
            pattern = r'(.*?)[,|.]' # "B C"

        list_child = re.findall(pattern, body)

        #  Is the statement enclosed in quotation marks, mixed use 
        # for child in list_child:
        #     body = body.replace('"%s"' % child, '')
        # body = body.replace(' ', '').replace('.', '')
        # list_child.extend(body.split(','))

        list_child = [child.strip() for child in list_child if child != '']

        return head, list_child

    def prologImport(self, info):
        content = info[0]
        switch = info[1]
        quotesSwitch = info[2]

        back_nodeDataArray = copy.deepcopy(self.nodeDataArray)
        back_linkDataArray = copy.deepcopy(self.linkDataArray)

        self.nodeDataArray.clear()
        self.linkDataArray.clear()
        try:
            list_line = self.parse_prolog_all(content, quotesSwitch)
            for line in list_line:
                self.makePrologLineData(line, quotesSwitch)

            if switch in HAN_EN.gets('Yes'):
                self.copyAllCommonTree()
        except:
            self.nodeDataArray = back_nodeDataArray
            self.linkDataArray = back_linkDataArray
            return False

        #  write in show_data.js file 
        jstrans.py2js('\"\"\"\n%s\n\"\"\"\n' % info[0] + self.getStrData())
        return True

    def prologExport(self, is_content=False):
        list_line = []
        for node in self.nodeDataArray:
            str_line = self.node2prologLine(node, is_content)
            if str_line != '':
                list_line.append(str_line)
        return list_line

    #  Create a row through nodes prolog
    def node2prologLine(self, node, is_content):
        list_childIDs = self.getChildrenID(node["key"])
        if len(list_childIDs) == 0:
            return ''
        
        #  Related to “ evidence ” Nodes of type, do not generate prolog inspect 
        if is_content:
            list_evidenct_childIDs = [ID for ID in list_childIDs if self.isEvidence(ID)]
            if self.isEvidence(node["key"]) or len(list_evidenct_childIDs) > 0:
                return ''

        if is_content:
            nodeName = self.getNodeContent(node)
        else:
            nodeName = self.getNodeName(node)
        str_line = '"%s"' % nodeName
        str_line += ' :- '
        for childID in list_childIDs:
            if is_content:
                name = self.findNodeByKey(childID).content
            else:
                name = self.findNodeByKey(childID).nodeName
            str_line += '"%s", ' % name
        str_line += '.'
        str_line = str_line.replace(', .', '.')
        return str_line


    #  analysis prolog One line of data and create corresponding data 
    def makePrologLineData(self, line, quotesSwitch):
        parent, children = self.parse_prolog_line(line, quotesSwitch)
        parentName = parent
        list_childName = children
        # print(list_childName)

        parentNode, parentID = self.makeNode(parentName)
        for childName in list_childName:
            childNode, childID = self.makeNode(childName)
            self.makeLink(parentID, childID)

    #  conduct prolog Import, node copy operation (to make a node have a unique parent node) 
    #  Copy path cannot be created " ring "
    def copyAllCommonTree(self):
        list_preNodeID = []
        for link in self.linkDataArray:
            if link["to"] in list_preNodeID:
                # self.copyTreeByLink(link)
                #  Copy a new tree 
                rootNode = self.makeTree(link["to"])
                #  Change to a new tree 
                link["to"] = rootNode["key"]
            else:
                list_preNodeID.append(link["to"])

    #  current link Copy the tree pointed to (not shared with other nodes) 
    def copyTreeByLink(self, link):
        #  Copy a new tree 
        rootNode = self.makeTree(link["to"])
        #  Change to a new tree 
        for lk in self.linkDataArray:
            if link == lk:
                lk["to"] = rootNode["key"]

    """ Import prolog function  End"""

    def formalExport(self, dstFilePath, encoding = 'utf-8'):
        #  collecting data  
        formal_data = []
        for node in self.nodeDataArray:
            info = self.findNodeByKey(node["key"])
            if not info.content:
                continue
            formal_data.append({
                "en": info.nodeName,
                "formal": info.content,
                "reason": info.reason
            })
        
        #  Export data 
        with open(dstFilePath, 'w', encoding=encoding) as f:
            json.dump(formal_data, f, indent=4, ensure_ascii=False)

        return ''

    def jsonExport(self, dstFilePath, encoding):
        dict_data = {
            'nodeDataArray': self.nodeDataArray,
            'linkDataArray': self.linkDataArray
        }

        os.makedirs(os.path.dirname(dstFilePath), exist_ok=True)
        with open(dstFilePath, 'w', encoding=encoding) as f:
            json.dump(dict_data, f, indent=4, ensure_ascii=False)

        return ''

    def jsonImport(self, dstFilePath, encoding):
        with open(dstFilePath, 'r', encoding=encoding) as f:
            dict_data = json.load(f)
        
        self.nodeDataArray = dict_data['nodeDataArray']
        self.linkDataArray = dict_data['linkDataArray']

        self.setAllNodeWidth(300) #  Node default width 
        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())
        return ''

    def gsnKey2Nodetype(self, number):
        if number[:2] == 'Sn':
            nodeType = 'Solution'
        elif number[0] == 'S':
            nodeType = 'Strategy'
        elif number[0] == 'G':
            nodeType = 'Goal'
        else:
            nodeType = ''
        return nodeType

    def yamlImport(self, dstFilePath, encoding):
        with open(dstFilePath, 'r', encoding=encoding) as f:
            dict_data = yaml.safe_load(f)

        # import pprint
        # pprint.pprint(dict_data)

        if self.nodeDataArray:
            self.nodeDataArray.clear()
        if self.linkDataArray:
            self.linkDataArray.clear()

        #  Create Node 
        for number, info in dict_data.items():
            nodeType = self.gsnKey2Nodetype(number)
            if nodeType == '':
                continue
            self.addNode((0, # parentID
                          info.get('text', '!!! The text property not found !!!'), # nodeName
                          info.get('coq', ''), # content
                          HAN_EN.get('And'), # attribute
                          nodeType, # nodeType
                          'Coq' if 'coq' in info else '', # reason
                          '', # DSTheory
                          '{}', # Addition
                          number), None, False)
        
        #  Create links and additional information 
        for number, info in dict_data.items():
            node = self.findNodeByNumber(number)
            if not node:
                continue
            if 'supportedBy' in info:
                for sub_number in info['supportedBy']:
                    sub_node = self.findNodeByNumber(sub_number)
                    self.makeLink(fromID=node['key'], toID=sub_node['key'])
            if 'inContextOf' in info:
                addition = {}
                for sub_number in info['inContextOf']:
                    addition[sub_number] = dict_data[sub_number].get('text', '!!! The text property not found !!!')
                self.setAdditionKeyValue(node['key'], addition)
            if 'url' in info:
                self.setAdditionKeyValue(node['key'], {"url": info['url']})

        self.setAllNodeWidth(300) #  Node default width , Update data 
        return ''

    #  Chinese utf-8 storage 
    def save_chinese(self, src_str, dstFilePath):
        src_str = codecs.decode(src_str, 'unicode_escape')
        os.makedirs(os.path.dirname(dstFilePath), exist_ok=True)
        with open(dstFilePath, 'w', encoding='gb2312') as f:
            f.write(src_str)
        
        with open(dstFilePath, 'r', encoding='gb2312') as f:
            src_str = f.read()
        
        with open(dstFilePath, 'w', encoding='utf-8') as f:
            f.write(src_str)

    def yamlExport(self, dstFilePath, encoding):
        proveRootID = self.getRootNode().nodeID
        proveLevel = 99999

        str_yaml = self.toGsnYaml(proveRootID, proveLevel)
        self.save_chinese(str_yaml, dstFilePath)
        return ''

    def csvExport(self, dstFilePath, encoding = 'ansi'):
        all_data = []
        for node in self.nodeDataArray:
            info = self.findNodeByKey(node["key"])

            parent_id = info.parentID
            name = info.nodeName
            content = info.content
            attr = info.attribute
            type = info.nodeType
            reason = info.reason
            DSTheory = info.DSTheory
            Addition = info.Addition

            node_info = [node["key"], name, type, reason, attr, content, DSTheory, Addition, parent_id]
            all_data.append(node_info)

        try:
            dstFileDir = os.path.dirname(dstFilePath)
            if not os.path.exists(dstFileDir):
                os.makedirs(dstFileDir)
            with open(dstFilePath, mode='w', encoding=encoding, newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['NODE_ID', 'NAME', 'TYPE', 'REASON', 'ATTRIBUTE', 'CONTENT', 'DSTHEORY', 'ADDITION', 'PARENT_ID'])
                writer.writerows(all_data)
        except FileNotFoundError:
            return ' directory does not exist '

        return ''

    def readCSV(self, srcFilePath, encoding = 'ansi'):
        #  get data 
        all_data = []
        try:
            with open(srcFilePath, mode='r', encoding=encoding) as f:
                reader = csv.reader(f)
                title_flag = True
                title = [] #  Header Fields 
                for row in reader:
                    #  Skip the first line   Header 
                    if title_flag:
                        title = row
                        title_flag = False
                        continue
                    all_data.append(CsvData(row, title))
        except UnicodeDecodeError:
            return [], ' The file encoding is incorrect '
        except FileNotFoundError:
            return [], ' file does not exist '
        except IndexError:
            return [], ' The file format is incorrect '
        return all_data, 'ok'

    def csvMerge(self, srcFilePath, encoding, mountNodeID):
        all_data, info = self.readCSV(srcFilePath, encoding)
        if info != 'ok':
            return info
        
        #  load csv
        mergeDataService = DataService()
        mergeDataService.csvImportAll(all_data)

        #  Offset Merge Data 
        parent_max_id = self.getMaxID()
        mergeDataService.offsetAllIds(parent_max_id, mountNodeID)
        nodeObj = mergeDataService.getRootNode()

        self.nodeDataArray += mergeDataService.nodeDataArray
        self.linkDataArray += mergeDataService.linkDataArray

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())
        return ''

    def offsetAllIds(self, offset, mountNodeID):
        for node in self.nodeDataArray:
            node['key'] += offset
            old_name = self.getNodeName(node)
            new_question = "%d %s" % (node['key'], old_name)
            self.setNodeNameWithID(node, new_question)

        for link in self.linkDataArray:
            if link['from'] == 0:
                link['from'] = mountNodeID
            else:
                link['from'] += offset
            link['to'] += offset
        

    def csvImport(self, srcFilePath, retainTreeSwitch = HAN_EN.get("No"), encoding = 'ansi'):
        all_data, info = self.readCSV(srcFilePath, encoding)
        if info != 'ok':
            return all_data, info

        list_notImpNode = []
        if retainTreeSwitch in HAN_EN.gets('Yes'):
            list_notImpNode = self.csvImportNodeInfo(all_data)
        else:
            self.csvImportAll(all_data)

        #  write in show_data.js file 
        jstrans.py2js(self.getStrData())
        return list_notImpNode, ''

    def csvImportNodeInfo(self, all_data):
        list_notImpNode = []
        for data in all_data:
            node = self.findNodeByName(data.nodeName)
            if node == None:
                list_notImpNode.append(data.nodeName)
                continue
            ID = node["key"]

            info = NodeData()
            info.parentID = self.getParentIDs(ID)[0]
            info.nodeName = data.nodeName
            info.nodeType = data.nodeType
            info.reason = data.reason
            info.content = data.content
            info.DSTheory = data.DSTheory
            info.Addition = data.Addition
            info.attribute = data.attribute
            self.editNode(ID, info)
        return list_notImpNode

    def csvImportAll(self, all_data):
        if self.nodeDataArray:
            self.nodeDataArray.clear()
        if self.linkDataArray:
            self.linkDataArray.clear()

        for data in all_data:
            self.addNode((data.parentID, data.nodeName, data.content, data.attribute, data.nodeType, data.reason, data.DSTheory, data.Addition), data.nodeID)
        return []

    def getNodeGsnKey(self, node):
        if node.number:
            return node.number
        
        id = node.nodeID
        if node.nodeType in HAN_EN.gets('Solution'):
            node_gsnkey = 'Sn{}'.format(id)
        elif node.nodeType in HAN_EN.gets('Goal'):
            node_gsnkey = 'G{}'.format(id)
        elif node.nodeType in HAN_EN.gets('Strategy'):
            node_gsnkey = 'S{}'.format(id)
        else:
            return id
        return node_gsnkey

    def isAdditionKey(self, addi_key):
        if len(addi_key) == 0:
            return False
        if addi_key[0] in ['C', 'J', 'A', 'S']:
            return True
        return False
        # gsn_addition_type = ['Strategy', 'S',
        #                 'Context', 'Assumption', 'Justification',
        #                 'Context1', 'Assumption1', 'Justification1',
        #                 'Context2', 'Assumption2', 'Justification2',
        #                 'Context3', 'Assumption3', 'Justification3',
        #                 'Context4', 'Assumption4', 'Justification4',
        #                 'Context5', 'Assumption5', 'Justification5',
        #                 'C1', 'A1', 'J1',
        #                 'C2', 'A2', 'J2',
        #                 'C3', 'A3', 'J3',
        #                 'C4', 'A4', 'J4',
        #                 'C5', 'A5', 'J5',
        #                 ]

    def wrap_text(self, sentence: str, width: int) -> str:
        """
        Wrap a given sentence to a specified width, ensuring that words are not broken across lines.
        
        :param sentence: The input sentence to be wrapped.
        :param width: The specified width for wrapping the text.
        :return: A new string with the sentence wrapped at the specified width.
        """
        words = sentence.split()  # Split the sentence into words
        if not words:  # If the list is empty, return an empty string
            return ""

        current_line_length = 0
        wrapped_text = ""

        for word in words:
            # Check if adding the next word exceeds the width
            if current_line_length + len(word) <= width:
                # If the line is not empty, add a space before the word
                if current_line_length > 0:
                    wrapped_text += " "
                    current_line_length += 1  # Account for the space
                wrapped_text += word
                current_line_length += len(word)
            else:
                # Start a new line with the current word
                wrapped_text += "\n" + word
                current_line_length = len(word)  # Reset the line length to the current word's length

        return wrapped_text

    def toGsnYaml(self, gsnRootID, proveLevel):
        gsn = {}
        #  Determine the subtree range that needs to be checked 
        list_descendant_ids = []
        self.getDescendantIDs(gsnRootID, list_descendant_ids, proveLevel)

        for node in self.nodeDataArray:
            #  Block some nodes 
            if node['key'] not in list_descendant_ids:
                continue
            
            # have_number = False
            # if self.getNodeNumber(node):
            #     have_number = True

            #  Obtain additional sections 
            addition = self.getAdditionContent(node)
            if addition:
                addition = addition.replace('“', '"').replace('”', '"').replace(' :  ', ':').replace(' ， ', ',').replace(' ｛ ', '{').replace(' ｝ ', '}')
                # addition = json.loads(addition)
                try:
                    addition = json.loads(addition)
                    # if " background " in addition:
                    #     addition['Context'] = addition[' background ']
                    #     del addition[' background ']
                    # if " strategy " in addition:
                    #     addition['Strategy'] = addition[' strategy ']
                    #     del addition[' strategy ']
                    # if " hypothesis " in addition:
                    #     addition['Assumption'] = addition[' hypothesis ']
                    #     del addition[' hypothesis ']
                    # if " reason " in addition:
                    #     addition['Justification'] = addition[' reason ']
                    #     del addition[' reason ']
                except:
                    addition = {" error ": "addition Not a correct one JSON"}
            else:
                addition = {}

            nodeData = self.findNodeByKey(node['key'])
            node_key = self.getNodeGsnKey(nodeData)
            text = self.getNodeName(node)

            #  Add nodes 
            gsn[node_key] = {
                'text': self.wrap_text(text, 32)
            }

            #  Evidence node processing 
            if self.getNodeType(node) == 'Solution':
                if 'url' in addition:
                    gsn[node_key]['url'] = addition['url']
                continue
            
            # -- Below are all   Non evidence node processing 
            list_ids = self.getChildrenID(node['key'])
            list_ids = list(set(list_descendant_ids).intersection(set(list_ids)))
            
            if not ('Strategy' in addition or 'S' in addition):
                if not list_ids:
                    gsn[node_key]['undeveloped'] = True
                else:
                    #  No, Strategy Add here, otherwise Strategy handle 
                    gsn[node_key]['supportedBy'] = []
                    for id in list_ids:
                        subnode = self.findNodeByKey(id)
                        subnode_key = self.getNodeGsnKey(subnode)
                        gsn[node_key]['supportedBy'].append(subnode_key)


            for type, cont in addition.items():
                if cont == '':
                    continue

                if self.isAdditionKey(type):
                    #  Add additional nodes 
                    add_key = '{}{}{}'.format(type[0], node['key'],
                                              type[-1] if len(type) > 1 and type[-1].isnumeric() else '') #  Take the last digit, do not take non digits 
                    gsn[add_key] = {
                        'text': self.wrap_text(cont, 32)
                    }
                    #  Add additional node index 
                    if type == 'Strategy' or type == 'S':
                        idx_name = 'supportedBy'
                    else:
                        idx_name = 'inContextOf'

                    if idx_name not in gsn[node_key]:
                        gsn[node_key][idx_name] = []
                    gsn[node_key][idx_name].append(add_key)

                    #  Strategy Node: Add Index 
                    if type == 'Strategy' or type == 'S':
                        if list_ids:
                            gsn[add_key]['supportedBy'] = []
                            for id in list_ids:
                                subnode = self.findNodeByKey(id)
                                subnode_key = self.getNodeGsnKey(subnode)
                                gsn[add_key]['supportedBy'].append(subnode_key)
                        else:
                            gsn[add_key]['undeveloped'] = True

        #  take JSON Convert string to YAML character string 
        gsn_yaml = yaml.safe_dump(gsn, sort_keys=False)
        gsn_yaml = gsn_yaml.replace('>', '&gt;')
        gsn_yaml = gsn_yaml.replace('<', '&lt;')
        gsn_yaml = gsn_yaml.replace('&', '&amp;')
        
        gsn_yaml = gsn_yaml.replace('    \\', '')
        
        return gsn_yaml

    def addToCompareData(self, proveRootID, proveLevel, domain, creator):
        #  obtain json
        with open('auto_build_llm/compare_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        #  modify json
        #  Determine the subtree range that needs to be operated on 
        list_descendant_ids = []
        self.getDescendantIDs(proveRootID, list_descendant_ids, proveLevel)

        for node in self.nodeDataArray:
            #  Block some nodes 
            if node['key'] not in list_descendant_ids:
                continue
            goal = self.getNodeName(node)
            dict_childrenName_nodetype = self.getChildrenName(node['key'])
            is_all_solution = (set(dict_childrenName_nodetype.values()) == {'Solution'})
            if len(dict_childrenName_nodetype) == 0 or is_all_solution:
                continue #  The last layer Solution Not considered, only counted  argument

            if goal not in data:
                data[goal] = { "domain": domain }
            if "subgoal" not in data[goal]:
                data[goal]['subgoal'] = {}
            if creator not in data[goal]['subgoal']:
                data[goal]['subgoal'][creator] = []
            data[goal]['subgoal'][creator].append({
                "subgoal": list(dict_childrenName_nodetype.keys()),
                "similarity": 100 if creator == 'person' else -1
            })

        #  write file 
        with open('auto_build_llm/compare_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def createCompareData(self, domain, creator, temperature):
        #  obtain json
        with open('auto_build_llm/compare_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        #  call LLM Create data 
        ab = AutoBuild('./auto_build_llm/prompts/gsn_builder_5_block.txt')
        for goal, info in data.items():
            if domain != 'ALL' and domain != info['domain']:
                continue #  Generate data in the specified domain 

            if creator not in info['subgoal']:
                info['subgoal'][creator] = []
            else:
                continue #  A model only generates one copy 

            sub_info = ab.build(
                goal=goal,
                temperature=temperature,
                model=creator
            )
            info['subgoal'][creator].append({
                "subgoal": list(sub_info['subgoals'].values()),
                "solution": list(sub_info['solutions'].values()),
                "strategy": sub_info['strategy'],
                "block": sub_info['block'],
                "goal": sub_info['goal'],
                "similarity": -1
            })
        
        #  write file 
        with open('auto_build_llm/compare_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def evaluateSimilar(self, temperature=0.2):
        #  obtain json
        with open('auto_build_llm/compare_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        ss = SentsSimilarity('sents_similarity_llm/prompts/two_sentences.txt')
        for goal, info in data.items():
            base_sents = '.'.join(info['subgoal']['person'][0]['subgoal'])
            for creator, list_subobj in info['subgoal'].items():
                if creator == 'person':
                    continue
                for subobj in list_subobj:
                    if subobj['similarity'] >= 0:
                        continue
                    compare_sents = '.'.join(subobj['subgoal'])
                    list_similarity = ss.compare(
                        sentence1=base_sents,
                        sentence2=compare_sents,
                        temperature=temperature
                    )
                    if len(list_similarity) > 0:
                        subobj['similarity'] = list_similarity[0]
                    else:
                        print(' Similarity analysis failed, please try again! ', base_sents)
 
        #  write file 
        with open('auto_build_llm/compare_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(' The similarity comparison has ended. ')

    def evaluateSimilarAPI(self, compare_data_path='auto_build_llm/compare_data.json', field_name='similarity_baidu'):
        #  obtain json
        with open(compare_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        all_num = len(data)
        done_num = 0
        for goal, info in data.items():
            base_sents = '.'.join(info['subgoal']['person'][0]['subgoal'])
            for creator, list_subobj in info['subgoal'].items():
                if creator == 'person':
                    continue
                for subobj in list_subobj:
                    if field_name in subobj and subobj[field_name] >= 0:
                        continue
                    if field_name == 'similarity_baidu_so':
                        list_compare_sents = subobj['solution'] + subobj['subgoal'] + [subobj['strategy']]
                    elif field_name == 'similarity_baidu_sosu':
                        list_compare_sents = subobj['solution'] + subobj['subgoal']
                    elif field_name == 'similarity_baidu_ss':
                        list_compare_sents = subobj['subgoal'] + [subobj['strategy']] + subobj['solution']
                    elif field_name == 'similarity_baidu':
                        list_compare_sents = subobj['subgoal']
                    else:
                        print('field_name error.')

                    compare_sents = '.'.join(list_compare_sents)
                    compare_sents = compare_sents[:510]
                    score = Similarity(
                        text_1=base_sents,
                        text_2=compare_sents
                    )
                    subobj[field_name] = score
            
            done_num += 1
            print(f'[{done_num}/{all_num}] {goal}')
 
        #  write file 
        with open(compare_data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(' The similarity comparison has ended. ')