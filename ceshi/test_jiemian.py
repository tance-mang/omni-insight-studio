from streamlit.testing.v1 import AppTest
from pathlib import Path

def test_pages(tmp_path, monkeypatch):
    monkeypatch.setenv('XHS_DATA_DIR',str(tmp_path))
    app=AppTest.from_file(Path(__file__).resolve().parents[1] / 'app.py', default_timeout=20).run()
    assert not app.exception
    for page in ['笔记导入与分析','评论研究','产品知识库','选品机会分析','AI 创作','草稿管理','系统设置']:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception

def test_product_to_draft(tmp_path, monkeypatch):
    monkeypatch.setenv('XHS_DATA_DIR',str(tmp_path))
    from shujuku import baocun, liebiao
    baocun('产品',biaoti='虚构产品',maidian='练习用品')
    app=AppTest.from_file(Path(__file__).resolve().parents[1] / 'app.py',default_timeout=20).run()
    app.sidebar.radio[0].set_value('AI 创作').run()
    app.text_area[1].set_value('人工编辑的原创草稿')
    app.button[1].click().run()
    assert not app.exception
    assert liebiao('草稿')[0]['neirong']=='人工编辑的原创草稿'
