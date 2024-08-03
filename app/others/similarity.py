import requests
import json

def Similarity(text_1, text_2):
    try:
        resp = baidu_similarity(text_1, text_2)
        score = resp['score']
        return score
    except:
        print('API Error:', resp)
        return -1

def baidu_similarity(text_1, text_2):
    url = "https://aip.baidubce.com/rpc/2.0/nlp/v2/simnet?charset=UTF-8&access_token=" + get_access_token()
    
    payload = json.dumps({
        "text_1": text_1,
        "text_2": text_2
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    '''{
        "log_id": 12345,
        "texts":{
            "text_1":"浙富股份",
            "text_2":"万事通自考网"
        },
        "score":0.3300237655639648 //相似度结果
    }'''
    return response.json()
    

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    API_KEY = "SycpIszcvnDzpbwPaBN7G81y"
    SECRET_KEY = "9h9u2UUPTQ5n1dpJEiyE2lwxpIF2GaJs"
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

if __name__ == '__main__':
    base = [
        "Each UAV in the managed airspace knows the altitude of the terrain in its current vicinity.",
        "The infrastructure provides a map documenting the coordinates and height of all FGBs in the managed area.",
        "Each UAV will avoid FGB obstacles."
    ]
    gpt35 = [
        "The UAV's obstacle detection system is reliable.",
        "The UAV's obstacle avoidance algorithm is effective.",
        "The UAV's communication system is reliable to receive obstacle information from the airspace management system."
    ]
    gpt4 = [
        "The flight algorithms accurately identify and avoid FGB.",
        "The sensor systems reliably detect FGB.",
        "The communication systems promptly transmit information about FGB."
    ]
    palm2 = [
        "The flight paths of UAVs are known and predictable.",
        "The locations of fixed ground-based obstacles are known and accurate."
    ]
    score = Similarity('.'.join(base), '.'.join(gpt35+gpt4+palm2))
    print(score)
