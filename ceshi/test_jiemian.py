from streamlit.testing.v1 import AppTest
from pathlib import Path

def test_pages(tmp_path, monkeypatch):
    monkeypatch.setenv('XHS_DATA_DIR',str(tmp_path))
    app=AppTest.from_file(Path(__file__).resolve().parents[1] / 'app.py', default_timeout=20).run()
    assert not app.exception
    for page in ['笔记导入与分析','评论研究','产品知识库','AI 创作','草稿管理','系统设置']:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception
