#百度通用翻译API,不包含词典、tts语音合成等资源，如有相关需求请联系translate_api@baidu.com
# 教程：http://api.fanyi.baidu.com/api/trans/product/apidoc
# 控制台：https://api.fanyi.baidu.com/api/trans/product/desktop
# coding=utf-8

import http.client
import hashlib
import urllib
import random
import json

class LocalTranslation:
    def __init__(self, dest_lang, trans_path = 'others/translate.json'):
        print('LocalTranslation: __init__')
        self.set_lang_mode(dest_lang)
        self.trans_path = trans_path
        self.list_trans = []
        with open(self.trans_path, 'r', encoding='utf-8') as f:
            self.list_trans = json.load(f)
    
    def __del__(self):
        print('LocalTranslation: __del__')
        with open(self.trans_path, 'w', encoding='utf-8') as f:
            json.dump(self.list_trans, f, ensure_ascii=False, indent=4)
        
    def query(self, src_text):
        for it in self.list_trans:
            if it[self.src_lang] == src_text:
                return it[self.dest_lang]
        return ''

    def add(self, src_text, dest_text):
        item = {self.src_lang: src_text, self.dest_lang: dest_text}
        self.list_trans.append(item)

    def set_lang_mode(self, dest_lang):
        self.dest_lang = dest_lang
        if dest_lang == 'zh':
            self.src_lang = 'en'
        else:
            self.src_lang = 'zh'

def Translate(src_text, dest_lang, ls):
    if not src_text:
        return ''
    dest_text = ls.query(src_text)
    if dest_text:
        return dest_text
    else:
        dest_text = baidu_translate(src_text, dest_lang)
        ls.add(src_text, dest_text)
        return dest_text

def baidu_translate(src_text, dest_lang='zh'):
    appid = '20221017001397987'  # 填写你的appid
    secretKey = 'XbFqQTOLDHV_ED0i4A3L'  # 填写你的密钥

    httpClient = None
    myurl = '/api/trans/vip/translate'

    fromLang = 'auto'   #原文语种
    toLang = dest_lang   #译文语种
    salt = random.randint(32768, 65536)
    q = src_text
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
    salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        print(result)
        dest_text = ''
        for res in result['trans_result']:
            dest_text += res['dst']
            dest_text += '\n'
        return dest_text.rstrip('\n')

    except Exception as e:
        print (e)
    finally:
        if httpClient:
            httpClient.close()

if __name__ == '__main__':
    # zh	中文
    # en	英语
    # result = baidu_translate('可信树工具', 'en')
    result = baidu_translate('The following describes how to verify a two-level subtree is safe.', 'zh')
    print(result)