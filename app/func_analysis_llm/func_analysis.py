import os, requests, json, re
import traceback
from llm_base.ollama_call import OllamaCall
from llm_base.chat_server_call import ChatServerCall

class FunctionAnalysis:
    def __init__(self, prompt_temp_path='function_analysis.txt'):
        self.prompt_temp_path = prompt_temp_path
        self.url = 'http://47.254.92.46:8000/openai/'

        self.data_path = './func_analysis_llm/func_data.json'
        if not os.path.exists(self.data_path):
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.buffer_build = json.load(f)
    
    def analysis(self, func_name, func_code, list_external_func, temperature=0.5, model='gpt-3.5', msg=''):
        #  First check the cache 
        func_name = func_name.strip()
        if func_name in self.buffer_build:
            return self.buffer_build[func_name]

        #  call LLM
        with open(self.prompt_temp_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
            prompt = prompt.replace('<NEW_FUNCTION_CODE>', func_code)

            external_func = self.list_ex_func_to_str(list_external_func)
            prompt = prompt.replace('<NEW_EXTERNAL_FUNCTIONS>', external_func)

        #  attempt 3 second 
        for i in range(3):
            print('try:', i)
            ret = self.chat(prompt, 1, temperature, model, msg=msg)
            if ret['status'] != 'OK':
                continue

            list_result = self.parse_output_choices(ret['output_choices'], func_name)
            if len(list_result) == 0:
                continue
                # return {"func_name": func_name, 'error_info': f" Output format error! Original text: {str(ret['output_choices'])}"}
            self.save_buffer(func_name, list_result[0])
            return list_result[0]

        return {}
        
    def list_ex_func_to_str(self, list_external_func):
        return str(list_external_func)

        if len(list_external_func) == 0:
            return 'None'
        
        list_ex_func_str = []
        for ex_func in list_external_func:
            list_ex_func_str.append('- ' + ex_func)
        return '\n'.join(list_ex_func_str)
    
    def save_buffer(self, gsn_yaml, result):
        self.buffer_build[gsn_yaml] = result
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.buffer_build, f, indent=4)
    
    def parse_output_choices(self, output_choices, func_name):
        list_result = []
        for choice in output_choices:
            try:
                function_goal, strategy = self.parse_choice(choice)
                list_result.append({
                    "func_name": func_name,
                    "function_goal": function_goal,
                    "strategy": strategy
                })
            except:
                traceback.print_exc()
                print('Parse Fail.')
        return list_result
    
    def parse_choice(self, choice):
        choice = choice.replace('**', '')
        choice += "FINISH."

        function_goal = self.find_center(choice, left='Function Goal:', right='One-sentence Strategy:').replace('(2)', '').strip('\n').strip(' ')
        strategy = self.find_center(choice, left='One-sentence Strategy:', right='FINISH.').strip(' ')

        return function_goal, strategy

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
        #  Using Proxy Model Services 
        # ret = ChatServerCall().chat_server(input_prompt, num_tries, temperature, model, chat_session_id)
        #  Use local model 
        ret = OllamaCall().chat_ollama(input_prompt, temperature, msg)
        return ret