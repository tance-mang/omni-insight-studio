import pandas as pd
import streamlit as st
from shujuku import liebiao, baocun, zhuangtai
from hexin import daoru, fenxi, ai, tuomin, excel

def xianshi():
    st.set_page_config(page_title='小红书 AI 爆文研究室', page_icon='✦', layout='wide')
    st.title('✦ 小红书 AI 爆文研究室')
    st.caption('XHS Insight Studio · 从内容数据到原创灵感 · 本地优先')
    page = st.sidebar.radio('工作台',['首页','笔记导入与分析','评论研究','产品知识库','AI 创作','草稿管理','系统设置'])
    st.sidebar.caption('源码公开 · 未经作者书面授权不得转售')
    if page == '首页':
        st.header('把灵感，变成有依据的创作')
        cols=st.columns(3)
        for col,kind in zip(cols,['笔记','产品','草稿']): col.metric(kind,len(liebiao(kind)))
        st.info('① 导入授权数据 → ② 分析互动与需求 → ③ 录入产品 → ④ 生成并人工审核 → ⑤ 导出发布')
        st.write('不自动采集、不自动发布。规则评论统计无需联网；AI 内容会发送到你配置的模型服务。')
    elif page == '笔记导入与分析':
        st.download_button('下载 CSV 模板','标题,正文,点赞,收藏,评论\n虚构示例,这是一条虚构笔记,120,80,15\n'.encode('utf-8-sig'),'模板.csv')
        f=st.file_uploader('导入 CSV / XLSX',type=['csv','xlsx'])
        if f and st.button('验证并追加导入'):
            try:
                rows=daoru(f,f.name)
                for r in rows: baocun('笔记',**r)
                st.success(f'已追加 {len(rows)} 条；重复导入会追加，请勿重复点击。')
            except Exception as e: st.error(str(e))
        rows=liebiao('笔记')
        if rows:
            df=pd.DataFrame(rows); df['互动分']=df.zan+2*df.cang+3*df.ping
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
    elif page == '产品知识库':
        with st.form('product'):
            title=st.text_input('产品名称'); body=st.text_area('价格、真实卖点、目标用户、禁用宣传词')
            if st.form_submit_button('保存产品') and title.strip(): baocun('产品',biaoti=title,neirong=body); st.success('已保存')
        st.dataframe(liebiao('产品'))
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
        if not products: st.info('请先保存一个产品'); return
        product=st.selectbox('选择产品',products,format_func=lambda r:r['biaoti'])
        mode=st.selectbox('创作模式',['选题结构','商品种草','情绪共鸣','竞品对比','小程序推广'])
        context=st.text_area('研究摘要与要求（不要粘贴他人完整原文）')
        consent=st.checkbox('同意将产品资料和脱敏摘要发送到所配置的模型服务')
        prompt=f'你是原创内容编辑。模式：{mode}。产品真实资料：{product["biaoti"]} {product["neirong"]}。研究摘要：{tuomin(context)}。提供5个标题、3版正文、标签、封面文案、配图建议和适合人群。不抄袭，不编造体验、效果、资质或竞品事实，遵守禁用词；最后提醒人工核实。'
        st.download_button('导出提示词（可手动使用）',prompt,'创作提示词.txt')
        if st.button('调用模型生成') and consent:
            try:
                config=st.session_state.get('ai_config',{})
                with st.spinner('生成中…'): st.session_state.result=ai(config.get('base',''),config.get('model',''),config.get('key',''),prompt,config.get('mode')=='Ollama')
            except Exception as e: st.error(str(e))
        result=st.text_area('编辑草稿',value=st.session_state.get('result',''),height=300)
        if st.button('保存草稿') and result.strip(): baocun('草稿',biaoti=product['biaoti'],neirong=result); st.success('已保存')
    else:
        rows=liebiao('草稿')
        for r in rows:
            with st.expander(f'{r["biaoti"]} · {r["zhuangtai"]} · #{r["id"]}'):
                st.write(r['neirong'])
                value=st.selectbox('状态',['待审核','已采用','已发布'],key=f's{r["id"]}')
                if st.button('更新状态',key=f'u{r["id"]}'): zhuangtai(r['id'],value); st.rerun()
                st.download_button('下载 Markdown',r['neirong'],f'draft-{r["id"]}.md',key=f'd{r["id"]}')
