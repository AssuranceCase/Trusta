import os, requests, json, re
from waitbox import show_wait_dialog

class OllamaCall:
    @show_wait_dialog
    def chat_ollama(self, input_prompt, temperature=0.8, model="llama3:8b", msg=''):
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        llm_info = config['LLM_INFO'][config['LLM_USE']]

        data = {
            "model": llm_info['model'],
            "messages": [{"role": "user",
                          "content": input_prompt}],
            "temperature": temperature,
            "stream": False
        }
        r = requests.post(url=llm_info['url'], json=data)
        # print(json.dumps(r.json(), indent=2))
        output_choice = r.json()['message']['content']
        with open('latest_output.md', 'w', encoding='utf-8') as f:
            f.write(output_choice)
        return {'output_choices': [output_choice], 'chat_session_id': "without id", 'status': 'OK'}