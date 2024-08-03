import re

def js2py(js_path='web_view/show_data.js', py_path='web_view/show_data.py'):
    js_str = ''
    with open(js_path, 'r', encoding='utf-8') as f:
        js_str = f.read()

    #  Match the key Add double quotation marks 
    def topy(matched):
        str_key = '\"' + matched.group('key') + '\":'
        return str_key
    py_str = re.sub('(?P<key>[a-z]+):', topy, js_str)

    py_str = py_str.replace("/*", "\"\"\"", 1)
    py_str = py_str.replace("*/", "\"\"\"", 1)
    py_str = py_str.replace("var ", "")
    with open(py_path, 'w', encoding='utf-8') as f:
        f.write(py_str)
    return py_str

def py2js(py_str = ''):
    if py_str == '':
        with open('web_view/show_data.py', 'r', encoding='utf-8') as f:
            py_str = f.read()

    #  Match the key Remove double quotation marks 
    def tojs(matched):
        str_key = matched.group('key') + ':'
        return str_key
    js_str = re.sub('\"(?P<key>[a-z]+)\":', tojs, py_str)

    js_str = js_str.replace("\"\"\"", "/*", 1)
    js_str = js_str.replace("\"\"\"", "*/", 1)
    js_str = js_str.replace("linkDataArray", "var linkDataArray").replace("nodeDataArray", "var nodeDataArray")
    with open('web_view/show_data.js', 'w', encoding='utf-8') as f:
        f.write(js_str)

#  Used for restoring historical records 
def history_to_json(js_path, json_path):
    py_path = 'restore_show_data.py'
    py_str = js2py(js_path, py_path)

    import sys, os, json
    sys.path.append('.')
    import restore_show_data
    dict_data = {
        'nodeDataArray': restore_show_data.nodeDataArray,
        'linkDataArray': restore_show_data.linkDataArray
    }

    # os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(dict_data, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    # js2py()
    # py2js()
    history_to_json(js_path='app/web_view/20230905222231_show_data.js',
    json_path='restore_show_data.json')