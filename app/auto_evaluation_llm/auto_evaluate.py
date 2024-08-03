import os, requests, json, re
import traceback
from llm_base.ollama_call import OllamaCall
from llm_base.chat_server_call import ChatServerCall

class AutoEvaluate:
    def __init__(self, prompt_temp_path='gsn_evaluation.txt'):
        self.prompt_temp_path = prompt_temp_path
        self.url = 'http://47.254.92.46:8000/openai/'

        self.data_path = './auto_evaluation_llm/evaluate_data.json'
        if not os.path.exists(self.data_path):
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.buffer_build = json.load(f)
    
    def evaluate(self, gsn_yaml, temperature=0.8, model='gpt-3.5'):
        # 先查缓存
        gsn_yaml = gsn_yaml.strip()
        if gsn_yaml in self.buffer_build:
            return self.buffer_build[gsn_yaml]

        # 调用LLM
        with open(self.prompt_temp_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
            prompt = prompt.replace('<ASSURANCE_CASES_TO_BE_EVALUATED>', gsn_yaml)

        # 尝试3次
        for i in range(3):
            print('try:', i)
            ret = self.chat(prompt, 1, temperature, model)
            if ret['status'] != 'OK':
                continue
            list_result = self.parse_output_choices(ret['output_choices'], gsn_yaml)
            if len(list_result) == 0:
                continue
            self.save_buffer(gsn_yaml, list_result[0])
            return list_result[0]

        return {}
    
    def save_buffer(self, gsn_yaml, result):
        self.buffer_build[gsn_yaml] = result
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.buffer_build, f, indent=4)
    
    def parse_output_choices(self, output_choices, gsn_yaml):
        list_result = []
        for choice in output_choices:
            try:
                json_ratings, improved_gsn_yaml = self.parse_choice(choice, gsn_yaml)
                list_result.append({
                    "gsn_yaml": gsn_yaml,
                    "json_ratings": json_ratings,
                    "improved_gsn_yaml": improved_gsn_yaml
                })
            except:
                traceback.print_exc()
                print('Parse Fail.')
        return list_result
    
    def parse_choice(self, choice, goal):
        json_ratings, improved_gsn_yaml = "", ""

        json_ratings = self.find_center(choice, left='Rating, reasons, and suggestions:', right='Improved Assurance Case:').strip(' ')
        improved_gsn_yaml = self.find_center(choice, left='Improved Assurance Case:', right='!!Output Ends!!').strip(' ')

        return json_ratings, improved_gsn_yaml

    def get_json(self, total, left, right):
        dict_json = self.find_center(total, left, right).strip(' ')
        if dict_json:
            try:
                dict_json = json.loads(dict_json)
            except:
                print(f'Warning: JSON {dict_json} fails to parse.')
                return None
        return dict_json

    def find_center(self, total, left, right):
        total = total.replace('\n', '###')
        pattern = re.escape(left) + "(.*?)" + re.escape(right)
        center = re.findall(pattern, total)
        if len(center) > 0:
            return center[0].replace('###', '\n')
        else:
            return None
    
    def chat(self, input_prompt, num_tries, temperature, model, chat_session_id=None, msg=''):
        # 使用代理模型服务
        # ret = ChatServerCall().chat_server(input_prompt, num_tries, temperature, model, chat_session_id)
        # 使用本地模型
        ret = OllamaCall().chat_ollama(input_prompt, temperature, msg)
        return ret