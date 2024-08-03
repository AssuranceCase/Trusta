import json
import pydot
import networkx as nx

# pydot==2.0.0
# networkx==3.0

def dot_to_json(dot_string):
    pydot_graph = pydot.graph_from_dot_data(dot_string)[0]
    nx_graph = nx.nx_pydot.from_pydot(pydot_graph)

    nodes = [{'id': n, 'label': nx_graph.nodes[n].get('label', n)} for n in nx_graph.nodes]
    edges = [{'from': e[0], 'to': e[1], 'label': nx_graph[e[0]][e[1]].get('label', '')} for e in nx_graph.edges]

    return json.dumps({'graph': {'nodes': nodes, 'edges': edges}}, indent=4)

def dot_to_tdt(dot_string):
    pydot_graph = pydot.graph_from_dot_data(dot_string)[0]
    nx_graph = nx.nx_pydot.from_pydot(pydot_graph)

    dict_name_key = {}

    nodes = []
    for i, name in enumerate(nx_graph.nodes):
        key = i + 1
        tmp_node = {'key': key, 'question': f'{key} {name}', "nodetype": "Goal"}
        # 设置假设
        justification = nx_graph.nodes[name].get('label', name)
        tmp_node['Addition'] = [{"text": '{"Info": "%s"}' % justification.strip('"').strip('脳')}]
        # 节点颜色
        frameColor = nx_graph.nodes[name].get('color', None)
        if frameColor:
            tmp_node['frameColor'] = frameColor.strip('"')
        # 字体颜色
        nameTextColor = nx_graph.nodes[name].get('fontcolor', None)
        if nameTextColor:
            tmp_node['nameTextColor'] = nameTextColor.strip('"')

        nodes.append(tmp_node)

        dict_name_key[name] = key

    edges = []
    for e in nx_graph.edges:
        tmp_edge = {'from': dict_name_key[e[0]],
                    'to': dict_name_key[e[1]],
                    'answer': 'And'}
        edges.append(tmp_edge)
         

    return {'nodeDataArray': nodes, 'linkDataArray': edges}

# 示例 DOT 字符串
dot_string = """
digraph G {
  A -> B [label="edge from A to B"];
  A [label="Node A"];
  B [label="Node B"];
}
"""

if __name__ == '__main__':
    with open('test/test_pycallgraph/input.dot', 'r', encoding='utf-8') as f:
        dot_string = f.read()
    # 转换并打印 JSON
    dict_output = dot_to_tdt(dot_string)
    with open('resource/json/deployer_call.json', 'w', encoding='utf-8') as f:
        json.dump(dict_output, f, indent=4)
    print(dict_output)

