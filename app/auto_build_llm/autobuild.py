import os, requests, json, re
import traceback
from llm_base.ollama_call import OllamaCall
from llm_base.chat_server_call import ChatServerCall

class AutoBuild:
    def __init__(self, prompt_temp_path='gsn_builder.txt'):
        self.prompt_temp_path = prompt_temp_path
        self.url = 'http://47.254.92.46:8000/openai/'

        data_path = './auto_build_llm/build_data.json'
        if not os.path.exists(data_path):
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        with open('./auto_build_llm/build_data.json', 'r', encoding='utf-8') as f:
            self.buffer_build = json.load(f)
    
    def build(self, goal, temperature=0.8, model='gpt-3.5'):
        # 先查缓存
        goal = goal.strip()
        if goal in self.buffer_build:
            return self.buffer_build[goal]

        # 调用LLM
        with open(self.prompt_temp_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
            prompt = prompt.replace('<A_NEW_GOAL>', goal)

        # 尝试3次
        for i in range(3):
            print('try:', i)
            ret = self.chat(prompt, 1, temperature, model)
            if ret['status'] != 'OK':
                continue

            list_result = self.parse_output_choices(ret['output_choices'], goal)
            if len(list_result) == 0:
                continue
            self.save_buffer(goal, list_result[0])
            return list_result[0]

        return {}
    
    def save_buffer(self, goal, result):
        self.buffer_build[goal] = result
        with open('./auto_build_llm/build_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.buffer_build, f, indent=4)
    
    def parse_output_choices(self, output_choices, goal):
        list_result = []
        for choice in output_choices:
            try:
                str_goal, str_block, str_strategy, dict_subgoals, dict_solutions = self.parse_choice(choice, goal)
                list_result.append({
                    "goal": str_goal,
                    "block": str_block,
                    "strategy": str_strategy,
                    "subgoals": dict_subgoals,
                    "solutions": dict_solutions
                })
            except Exception as error:
                traceback.print_exc()
                print('Parse Fail.', str(error))
        return list_result
    
    def parse_choice(self, choice, goal):
        choice = choice.replace('**', '')
        str_goal, str_block, str_strategy, dict_subgoals, dict_solutions = '', '', '', {}, {}
        if 'Goal G1:' in choice:
            str_goal = self.find_center(choice, left='Goal G1:', right='Building Blocks:').strip(' ')
        else:
            str_goal = goal

        str_block = self.find_center(choice, left='Building Blocks:', right='Break down Strategy:').strip(' ')

        dict_strategy = self.get_json(choice, left='Break down Strategy:', right='Sub-goals dictionary:')
        if dict_strategy:
            str_strategy = dict_strategy.get('strategy', '')

        dict_subgoals = self.get_json(choice, left='Sub-goals dictionary:', right='Solutions dictionary:')
        if not dict_subgoals:
            raise Exception('subgoals parse fail.')

        dict_solutions = self.get_json(choice, left='Solutions dictionary:', right='Explanation:')
        if not dict_solutions:
            raise Exception('solutions parse fail.')

        return str_goal, str_block, str_strategy, dict_subgoals, dict_solutions

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
        total = total.replace('\n', ' ')
        pattern = re.escape(left) + "(.*?)" + re.escape(right)
        center = re.findall(pattern, total)
        if len(center) > 0:
            return center[0]
        else:
            return None
    
    def chat(self, input_prompt, num_tries, temperature, model, chat_session_id=None):
        # 使用代理模型服务
        # ret = ChatServerCall().chat_server(input_prompt, num_tries, temperature, model, chat_session_id)
        # 使用本地模型
        ret = OllamaCall().chat_ollama(input_prompt, temperature)
        return ret
    

    
        