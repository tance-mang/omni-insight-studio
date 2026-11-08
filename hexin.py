import io
import json
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

def fenxi_ai(text, base, model, key, ollama=False):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines: return {}
    if not base or not model:
        return fenxi(text)
    prompt = f"""分析以下评论，按四个维度分类。每个维度列出匹配的原始评论作为证据。

评论列表：
{chr(10).join(f'{i+1}. {l}' for i,l in enumerate(lines))}

维度：
- 购买意向：询问购买方式、价格、渠道
- 用户痛点：抱怨、不满、使用困难
- 产品建议：改进建议、功能期望
- 用户需求：明确表达想要什么

严格按以下JSON格式返回，不要返回其他内容：
{{"购买意向": {{"count": 数字, "evidence": ["原始评论1", "原始评论2"]}}, "用户痛点": {{"count": 数字, "evidence": [...]}}, "产品建议": {{"count": 数字, "evidence": [...]}}, "用户需求": {{"count": 数字, "evidence": [...]}}}}"""
    result_text = ai(base, model, key, prompt, ollama)
    try:
        match = re.search(r'\{[\s\S]*\}', result_text)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, TypeError):
        pass
    return fenxi(text)

def tuomin(text):
    return re.sub(r'1[3-9]\d{9}', '[手机号]', re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[邮箱]', text))

def ai(base, model, key, prompt, ollama=False):
    base = base.rstrip('/')
    if not base.startswith(('http://','https://')): raise ValueError('接口地址需要 http:// 或 https:// 开头')
    url = base + '/api/chat' if ollama else base + '/chat/completions'
    payload = {'model':model,'stream':False,'messages':[{'role':'user','content':prompt}]} if ollama else {'model':model,'messages':[{'role':'user','content':prompt}]}
    headers = {'Authorization':'Bearer '+key} if not ollama else {}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=120)
    except requests.ConnectionError:
        raise ValueError('无法连接到模型服务，请检查地址和网络')
    except requests.Timeout:
        raise ValueError('模型请求超时（120秒），请检查模型负载或换用更快的模型')
    except requests.RequestException as e:
        raise ValueError(f'网络请求失败：{e}')
    if not r.ok:
        raise ValueError(f'接口返回错误 HTTP {r.status_code}，请检查模型名称、API Key 额度和地址')
    try:
        data = r.json()
    except ValueError:
        raise ValueError('模型返回了无效的 JSON 响应，请检查接口地址是否正确')
    try:
        return data['message']['content'] if ollama else data['choices'][0]['message']['content']
    except (KeyError, TypeError, IndexError):
        raise ValueError('模型响应格式异常，未找到预期字段，请检查模型配置')

def pingfen(rows):
    if not rows: return []
    df = pd.DataFrame(rows)
    df['hudong'] = df.zan + 2*df.cang + 3*df.ping
    avg_hudong = df.hudong.mean()
    topics = df.biaoti.value_counts()
    top_topic_ratio = topics.iloc[0] / len(df) if len(topics) > 0 else 0
    results = []
    for _, r in df.iterrows():
        hudong_score = min(r.hudong / max(avg_hudong, 1) * 40, 40)
        saturation = max(0, 20 - top_topic_ratio * 40)
        demand_score = min(r.ping / max(df.ping.mean(), 1) * 20, 20)
        quality = min((r.zan / max(r.hudong, 1)) * 20, 20)
        total = round(hudong_score + saturation + demand_score + quality, 1)
        results.append(dict(biaoti=r.biaoti, platform=r.platform, zan=r.zan, cang=r.cang, ping=r.ping, hudong=r.hudong, score=total))
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def baogao(rows, base, model, key, ollama=False):
    if not rows: return {'stats':{},'summary':''}
    df = pd.DataFrame(rows)
    df['hudong'] = df.zan + 2*df.cang + 3*df.ping
    stats = {
        'total': len(df),
        'avg_hudong': round(df.hudong.mean(), 1),
        'max_hudong': int(df.hudong.max()),
        'total_zan': int(df.zan.sum()),
        'total_cang': int(df.cang.sum()),
        'total_ping': int(df.ping.sum()),
        'platforms': df.platform.value_counts().to_dict(),
        'top_titles': df.nlargest(5, 'hudong')[['biaoti','hudong','platform']].to_dict('records'),
    }
    if not base or not model:
        return {'stats':stats,'summary':'请先在系统设置中配置 AI 模型以生成分析报告。'}
    summary_prompt = f"""你是内容选品分析师。根据以下数据给出选品建议：
共{stats['total']}条内容，平均互动分{stats['avg_hudong']}，最高{stats['max_hudong']}。
平台分布：{stats['platforms']}
互动最高的5条：
{chr(10).join(f'- {t["biaoti"]}（{t["platform"]}）互动分{t["hudong"]}' for t in stats['top_titles'])}

请分析：1) 哪些主题/需求值得切入 2) 竞争饱和度和机会点 3) 内容创作方向建议 4) 需要注意的风险。控制在300字以内。"""
    try:
        summary = ai(base, model, key, summary_prompt, ollama)
    except Exception as e:
        summary = f'AI 分析暂时不可用：{e}'
    return {'stats':stats,'summary':summary}

def excel(rows):
    b = io.BytesIO(); pd.DataFrame(rows).to_excel(b,index=False); return b.getvalue()
