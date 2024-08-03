import os, requests, json, re

class ChatServerCall:
    def chat_server(self, input_prompt, num_tries, temperature, model, chat_session_id=None):
        #  Use remote model proxy service 
        print('input_prompt:', input_prompt[-150:])
        print('temperature:', temperature)
        print('model:', model)
        
        param = {
            "input_prompt": input_prompt,
            "temperature": temperature,
            "num_tries": num_tries,
            "model": model
        }
        if chat_session_id:
            param['chat_session_id'] = chat_session_id

        r = requests.post(url=self.url, json=param)
        return r.json()
