import os
from nltk import load_parser
from nltk.sem.logic import LogicParser

class SentsFormal:
    def __init__(self, fcfg_dir):
        # 分词词典
        with open(os.path.join(fcfg_dir, "word_dict.txt"), 'r', encoding='utf-8') as f:
            self.dictionary = f.read().splitlines()
            self.dictionary = [w for w in self.dictionary if (w != '' and w[0] != '#')]
            self.dictionary = list(set(self.dictionary))

        # 句子解析引擎
        self.engines = {}
        for file in os.listdir(fcfg_dir):
            if file.endswith('.fcfg'):
                fcfg_path = os.path.join(fcfg_dir, file)
                fcfg_name = file.replace('.fcfg', '')
                self.engines[fcfg_name] = load_parser(fcfg_path)

    def formalize(self, sentence):
        seg_sent = self._word_tokenize(sentence)
        for engine in self.engines.values():
            result = self._create_formal(engine, seg_sent)
            if result != '':
                return result
        return ''
            

    def _create_formal(self, engine, seg_sent):
        try:
            trees = list(engine.parse(seg_sent))
        except:
            return ''
        if len(trees) == 0:
            return ''
        # trees[0].draw()

        semantic_list = trees[0].label()['SEM']
        semantic_list = [s for s in semantic_list if s]
        result = ''.join(semantic_list)
        return result
    
    def _word_tokenize(self, sentence):
        if sentence.find(' = ') != -1:
            list_word = sentence.split()
        else:
            list_word = self.__RMM(self.dictionary, sentence)
        
        return list_word

    def __RMM(self, dict, sentence): # 逆向最大匹配算法RMM函数，参数dict: 词典 ，参数sentence: 句子 
        rmmresult = [] 
        max_len = max([len(item) for item in dict])# max_len定义为词典中最长词长度 
        start = len(sentence) 
        while start != 0: # RMM 为逆向，start 从末尾位置开始，指向开头位置即为结束 
            index = start - max_len # 逆向时 index 的初始值为 start 的索引 - 词典中元素的最大长度或句子开头 
            if index < 0: 
                index = 0
            for i in range(max_len): 
                # 当分词在字典中时或分到最后一个字时，将其加入到结果列表中 
                if (sentence[index:start] in dict) or (len(sentence[index:start]) == 1): 
                    # print(sentence[index:start], end='/') 
                    rmmresult.insert(0, sentence[index:start])   
                    start = index# 分出一个词，start 设置到 index 处 
                    break                                    
                index += 1 # 如果匹配失败，则去掉最前面一个字符
        return rmmresult
