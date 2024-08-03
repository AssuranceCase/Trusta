
class Internation:
    HAN_EN = {
        'Yes': '是',
        'No': '否',
        'New': '新建',
        'JSON Open': 'Json打开',
        'Save': '保存',
        'Python Code Import': 'Python代码导入',
        'Dot Import': 'Dot导入',

        'JSON Save': 'Json保存',
        'JSON Save As': 'Json另存为',
        'YAML Open': 'Yaml打开',
        'YAML Save': 'Yaml保存',
        'YAML Save As': 'Yaml另存为',
        'CSV Open': 'Csv打开',
        'CSV Save': 'Csv保存',
        'CSV Save As': 'Csv另存为',
        'CSV Merge': 'Csv合并',
        'Formal Save As': 'Formal另存为',
        'File Path': '文件路径',
        'Encoding': '编码',
        'Select File': '选择文件',
        'Retain the current tree structure': '保留当前树结构',

        'Fresh': '刷新',
        'Add': '添加',
        'Auto Add': '自动添加',
        'Auto Evaluate': '自动评估',
        'Delete': '删除',
        'Prune Node': '裁剪结点',
        'Edit': '编辑',
        'Add Node': '添加结点',
        'Delete Node': '删除结点',
        'Edit Node': '编辑结点',
        'Interactive Formalization': '辅助形式化',
        'Please enter the node ID': '请输入结点ID',
        'Please set the node width: (unit: px) \n When the node width is 0, the default width is displayed.': '请设置结点宽度：（单位：像素px）\n结点宽度为0时，显示默认宽度。',


        'Prolog Import': 'Prolog导入',
        'Prolog Export': 'Prolog导出',
        'Prolog Check': 'Prolog检查',

        'Rotate Tree': '旋转树',
        'Node Width': '结点宽度',
        'Node Highlight': '结点高亮',
        'Node ID path': '结点ID路径',
        'Node Mode': '结点模式',
        'Strategy Switch': '策略开关',

        'Export DS-Tree': '导出定量推理树',
        'Evaluation': '约束证明',
        'Formalise': '约束形式化',
        'Quantitative Reason': '定量推理',
        'Function Analyzer': '函数分析',
        
        'Search': '搜索',
        'Description': '描述',
        'ID Path': '路径',

        'Explorer': '资源管理',
        'Node Edit': '结点编辑',
        'Overview': '概览图',
        'History': '操作历史',
        'Outline': '大纲视图',
        'Chat History': '会话历史',

        'File': '文件',
        'Diagram': '图形',
        'Windows': '窗口',
        'Evaluation': '证明',
        'StudyCase': '案例研究',

        'Translate': '翻译',
        'To English': '翻译为英语',
        'To Chinese': '翻译为简体中文',
        'To GSN': '转化为目标结构符号(GSN)',
        'Display GSN': '显示GSN格式',

        'Trustworthiness Derivation Tree': '可信树',
        'Sub-Tree ID:Level': '操作子树的根结点ID和操作层数',
        'Search Content': '请输入要搜索的内容',

        'Node ID': '结点ID',
        'Parent ID': '父结点ID',
        'Description': '结点名称',
        'Node Type': '结点类型',
        'Reason Type': '推理类型',
        'Relationship': '结点关系',
        'Formal Expressions': 'THEN',
        'Quantitative Info': '定量信息',
        'Qualitative Info': '定性信息',
        'Auxiliary Components': '附加信息',

        'TECH': '技术',
        'ENVI': '环境',
        'PROC': '过程',
        'EVID': '证据',

        'Goal': '目标',
        'Strategy': '策略',
        'Solution': '解决方案',
        'Context': '背景',
        'Assumption': '假设',
        'Justification': '理由',

        'Default': '不涉及',
        'Arithmetic': '数值运算',
        'Functional': '函数运算',
        'AbstractSets': '抽象集合推导',
        'SpecificSets': '具体集合推导',
        'LogicalRelations': '关系推导',
        'Quantified': '可信度计算',

        'And': '与',
        'Or': '或',

        'Field': '字段名',
        'Value': '值',

        'Natural Language Formalization': '自然语言到形式化语言翻译',
        'Natural Language': '自然语言',
        'Please enter natural language': '请输入自然语言',
        'Parameter setting': '参数设置',
        'Number of tries': '输入尝试次数',
        'Adding subtranslations': '添加子翻译',
        'Translate': '翻译',
        'Accuracy': '准确率',
        'Temperature': '翻译发散度',
        'Temperature': '发散度',
        'Constraint Type': '约束类型',

        'Node mode setting': '结点模式设置',
        'Please select the tree display mode': '请选择树显示模式',
        'Show all': '全部显示',
        'Description only': '仅树主干',
        'GSN mode': 'GSN模式',
        'Qualitative mode': '定性模式',
        'Quantitative mode': '定量模式',
        'Unsupported file format': '不支持的文件格式',
        'File does not exist': '文件不存在',

        'Content': '内容',
        'Replication node': '复制结点',
        'Statement in quotation marks': '语句带引号',
    }
    def get(self, en):
        return en
        return self.HAN_EN.get(en, en)

    def gets(self, en):
        return [self.HAN_EN.get(en, en), en]

HAN_EN = Internation()