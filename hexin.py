import io
import re
import pandas as pd
import requests

def daoru(file, name):
    df = pd.read_excel(file) if name.lower().endswith('.xlsx') else pd.read_csv(file)
    df = df.rename(columns={'标题':'biaoti','正文':'neirong','点赞':'zan','收藏':'cang','评论':'ping'})
    if 'biaoti' not in df: raise ValueError('缺少标题列')
    rows = []
    for _, r in df.iterrows():
        if pd.isna(r.biaoti) or not str(r.biaoti).strip(): continue
        item = {'biaoti':str(r.biaoti).strip(), 'neirong':str(r.get('neirong','')) if pd.notna(r.get('neirong','')) else ''}
        for k in ['zan','cang','ping']:
            v = r.get(k, 0)
            v = 0 if pd.isna(v) else float(v)
            if v < 0 or not v.is_integer(): raise ValueError('互动数量必须为非负整数')
            item[k] = int(v)
        rows.append(item)
    return rows

def fenxi(text):
    rules = {'购买意向':['怎么买','哪里买','价格','多少钱'], '用户痛点':['太贵','麻烦','不会','不好'], '产品建议':['希望','建议','能不能'], '用户需求':['想要','需要','求','怎么']}
    return {k:sum(any(w in line for w in words) for line in text.splitlines() if line.strip()) for k,words in rules.items()}

def tuomin(text):
    return re.sub(r'1[3-9]\d{9}', '[手机号]', re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[邮箱]', text))

def ai(base, model, key, prompt, ollama=False):
    base = base.rstrip('/')
    if not base.startswith(('http://','https://')): raise ValueError('接口地址需要 http:// 或 https://')
    if ollama:
        r = requests.post(base+'/api/chat', json={'model':model,'stream':False,'messages':[{'role':'user','content':prompt}]}, timeout=120)
    else:
        r = requests.post(base+'/chat/completions', headers={'Authorization':'Bearer '+key}, json={'model':model,'messages':[{'role':'user','content':prompt}]}, timeout=120)
    if not r.ok: raise ValueError(f'接口请求失败 HTTP {r.status_code}，请检查模型、额度和地址')
    data = r.json()
    return data['message']['content'] if ollama else data['choices'][0]['message']['content']

def excel(rows):
    b = io.BytesIO(); pd.DataFrame(rows).to_excel(b,index=False); return b.getvalue()
