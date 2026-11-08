import pandas as pd
import streamlit as st
from shujuku import liebiao, baocun, zhuangtai, an_id
from hexin import daoru, fenxi, fenxi_ai, tuomin, excel, pingfen, baogao, ai

def xianshi():
    st.set_page_config(page_title='全域 AI 选品与内容研究室', page_icon='✦', layout='wide')
    st.title('✦ 全域 AI 选品与内容研究室')
    st.caption('Omni Insight Studio · 从内容数据到原创灵感 · 本地优先')
    page = st.sidebar.radio('工作台',['首页','笔记导入与分析','评论研究','产品知识库','选品机会分析','AI 创作','草稿管理','系统设置'])
    st.sidebar.caption('源码公开 · 未经作者书面授权不得转售')
    if page == '首页':
        st.header('把灵感，变成有依据的创作')
        cols=st.columns(3)
        for col,kind in zip(cols,['笔记','产品','草稿']): col.metric(kind,len(liebiao(kind)))
        st.info('① 导入授权数据 → ② 分析互动与需求 → ③ 录入产品 → ④ 选品评分 → ⑤ 生成并人工审核 → ⑥ 导出发布')
        st.write('不自动采集、不自动发布。规则评论统计无需联网；AI 内容会发送到你配置的模型服务。')
    elif page == '笔记导入与分析':
        platform=st.selectbox('导入数据所属平台',['小红书','闲鱼','拼多多','抖音','淘宝','视频号','快手','其他'])
        st.download_button('下载 CSV 模板','标题,正文,点赞,收藏,评论\n虚构示例,这是一条虚构笔记,120,80,15\n'.encode('utf-8-sig'),'模板.csv')
        f=st.file_uploader('导入 CSV / XLSX',type=['csv','xlsx'])
        if f and st.button('验证并追加导入'):
            try:
                rows=daoru(f,f.name)
                added, skipped = 0, 0
                for r in rows:
                    if baocun('笔记',platform=platform,**r): added += 1
                    else: skipped += 1
                msg = f'已追加 {added} 条'
                if skipped: msg += f'，跳过 {skipped} 条重复标题'
                msg += '；请勿重复点击。'
                st.success(msg)
            except Exception as e: st.error(str(e))
        rows=liebiao('笔记')
        if rows:
            df=pd.DataFrame(rows); df['互动分']=df.zan+2*df.cang+3*df.ping
            selected=st.multiselect('筛选平台',sorted(df.platform.unique()),default=sorted(df.platform.unique()))
            df=df[df.platform.isin(selected)]
            word=st.text_input('标题关键词'); df=df[df.biaoti.str.contains(word,regex=False)]
            st.caption('互动分 = 点赞 + 收藏×2 + 评论×3，仅供样本排序；无曝光数据不计算收藏率。')
            st.dataframe(df.sort_values('互动分',ascending=False),width='stretch')
            st.bar_chart(df.set_index('biaoti')[['zan','cang','ping']])
            st.download_button('导出 Excel',excel(df.to_dict('records')),'笔记分析.xlsx')
    elif page == '评论研究':
        text=st.text_area('每行一条评论，请勿输入个人身份资料',height=200)
        if st.button('本地规则分析'):
            st.caption('关键词规则统计，类别可重叠，并非 AI 语义理解。')
            st.bar_chart(pd.Series(fenxi(text)))
            st.text_area('脱敏文本',tuomin(text))
        config=st.session_state.get('ai_config',{})
        if config.get('base') and config.get('model'):
            if st.button('AI 语义分析（需要模型）'):
                with st.spinner('AI 分析中…'):
                    result = fenxi_ai(text, config['base'], config['model'], config.get('key',''), config.get('mode')=='Ollama')
                if result:
                    for cat, info in result.items():
                        if isinstance(info, dict):
                            st.subheader(f'{cat}（{info.get("count",0)} 条）')
                            for ev in info.get('evidence',[]): st.text(f'• {ev}')
                        else:
                            st.subheader(f'{cat}：{info}')
                else:
                    st.warning('未分析到有效评论')
        else:
            st.info('配置 AI 模型后可使用语义分析，自动识别评论中的购买意向、痛点和需求。')
    elif page == '产品知识库':
        with st.form('product'):
            title=st.text_input('产品名称')
            jiage=st.text_input('价格')
            maidian=st.text_area('真实卖点')
            yonghu=st.text_area('目标用户')
            jinyongci=st.text_area('禁用宣传词')
            if st.form_submit_button('保存产品') and title.strip():
                baocun('产品',biaoti=title,jiage=jiage,maidian=maidian,yonghu=yonghu,jinyongci=jinyongci)
                st.success('已保存')
        st.subheader('已保存产品')
        products = liebiao('产品')
        if products:
            for p in products:
                with st.expander(f'{p["biaoti"]} · ¥{p["jiage"] or "未定价"}'):
                    if p['maidian']: st.write(f'**卖点：** {p["maidian"]}')
                    if p['yonghu']: st.write(f'**目标用户：** {p["yonghu"]}')
                    if p['jinyongci']: st.write(f'**禁用词：** {p["jinyongci"]}')
        else:
            st.info('暂无产品，请在上方添加。')
    elif page == '选品机会分析':
        rows=liebiao('笔记')
        if not rows:
            st.info('请先在"笔记导入与分析"导入数据。')
        else:
            scores = pingfen(rows)
            st.subheader('选品评分排行')
            st.caption('评分维度：互动强度(40) + 竞争饱和度(20) + 评论需求(20) + 内容质量(20)，满分100')
            score_df = pd.DataFrame(scores)
            st.dataframe(score_df, width='stretch')
            st.bar_chart(score_df.set_index('biaoti')['score'])
            st.subheader('机会分析报告')
            config=st.session_state.get('ai_config',{})
            if st.button('生成 AI 分析报告'):
                with st.spinner('分析中…'):
                    report = baogao(rows, config.get('base',''), config.get('model',''), config.get('key',''), config.get('mode')=='Ollama')
                stats = report['stats']
                col1, col2, col3, col4 = st.columns(4)
                col1.metric('内容总数', stats.get('total',0))
                col2.metric('平均互动分', stats.get('avg_hudong',0))
                col3.metric('最高互动分', stats.get('max_hudong',0))
                col4.metric('总评论数', stats.get('total_ping',0))
                if stats.get('platforms'):
                    st.write('**平台分布：**', stats['platforms'])
                if stats.get('top_titles'):
                    st.write('**互动最高的内容：**')
                    for t in stats['top_titles']:
                        st.write(f'- {t["biaoti"]}（{t["platform"]}）互动分 {t["hudong"]}')
                st.write('**AI 分析：**')
                st.write(report['summary'])
    elif page == '系统设置':
        st.info('密钥仅存当前会话内存，关闭后重新填写。API 模式填写以 /v1 结尾的基础地址。')
        st.selectbox('模式',['API','Ollama'],key='mode')
        st.text_input('基础地址',value='http://localhost:11434',key='base')
        st.text_input('模型名称',key='model'); st.text_input('API Key',type='password',key='key')
        if st.button('应用设置到当前会话'):
            st.session_state.ai_config = {k:st.session_state[k] for k in ['base','model','key','mode']}
            st.success('设置已应用，关闭会话后密钥失效')
        if st.button('测试连接'):
            try: st.success(ai(st.session_state.base,st.session_state.model,st.session_state.key,'只回复：连接成功',st.session_state.mode=='Ollama'))
            except Exception as e: st.error(str(e))
    elif page == 'AI 创作':
        products=liebiao('产品')
        if not products: st.info('请先在"产品知识库"保存产品'); return
        product=st.selectbox('选择产品',products,format_func=lambda r:r['biaoti'])
        mode=st.selectbox('创作模式',['选题结构','商品种草','情绪共鸣','竞品对比','小程序推广'])
        target=st.selectbox('目标平台',['小红书','闲鱼','拼多多','抖音','淘宝','视频号','快手','其他'])
        context=st.text_area('研究摘要与要求（不要粘贴他人完整原文）')
        consent=st.checkbox('同意将产品资料和脱敏摘要发送到所配置的模型服务')
        product_info = f'{product["biaoti"]}'
        if product.get('jiage'): product_info += f' 价格：{product["jiage"]}'
        if product.get('maidian'): product_info += f' 卖点：{product["maidian"]}'
        if product.get('yonghu'): product_info += f' 目标用户：{product["yonghu"]}'
        if product.get('jinyongci'): product_info += f' 禁用词：{product["jinyongci"]}'
        prompt=f'你是原创内容编辑。目标平台：{target}，按其内容形式调整输出（闲鱼侧重商品描述，拼多多侧重商品卖点，抖音侧重短视频脚本，小红书侧重笔记）。模式：{mode}。产品真实资料：{product_info}。研究摘要：{tuomin(context)}。提供5个标题、3版正文或脚本、标签、封面文案、配图建议和适合人群。不抄袭，不编造体验、效果、资质或竞品事实，遵守禁用词；最后提醒人工核实平台规则。'
        st.download_button('导出提示词（可手动使用）',prompt,'创作提示词.txt')
        if st.button('调用模型生成') and consent:
            try:
                config=st.session_state.get('ai_config',{})
                if not config.get('base') or not config.get('model'):
                    st.error('请先在系统设置中配置 AI 模型')
                else:
                    with st.spinner('生成中…'): st.session_state.result=ai(config['base'],config['model'],config.get('key',''),prompt,config.get('mode')=='Ollama')
            except Exception as e: st.error(str(e))
        result=st.text_area('编辑草稿',value=st.session_state.get('result',''),height=300)
        if st.button('保存草稿') and result.strip(): baocun('草稿',platform=target,biaoti=product['biaoti'],neirong=result); st.success('已保存')
    else:
        rows=liebiao('草稿')
        for r in rows:
            with st.expander(f'{r["biaoti"]} · {r["zhuangtai"]} · #{r["id"]}'):
                st.write(r['neirong'])
                value=st.selectbox('状态',['待审核','已采用','已发布'],key=f's{r["id"]}')
                if st.button('更新状态',key=f'u{r["id"]}'): zhuangtai(r['id'],value); st.rerun()
                st.download_button('下载 Markdown',r['neirong'],f'draft-{r["id"]}.md',key=f'd{r["id"]}')
