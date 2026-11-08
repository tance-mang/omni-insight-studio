import io
import pytest
from hexin import daoru, fenxi, fenxi_ai, tuomin, pingfen, baogao
from shujuku import baocun, liebiao, engine, an_id

def test_import():
    assert daoru(io.StringIO('标题,点赞\n测试,12\n'),'a.csv')[0]['zan']==12
    with pytest.raises(ValueError): daoru(io.StringIO('标题,点赞\n测试,-1\n'),'a.csv')

def test_privacy():
    assert '13812345678' not in tuomin('联系13812345678')
    assert fenxi('哪里买\n希望便宜')['购买意向']==1

def test_persistence(tmp_path,monkeypatch):
    monkeypatch.setenv('XHS_DATA_DIR',str(tmp_path))
    baocun('笔记',biaoti='测试'); engine().dispose()
    assert len(liebiao('笔记'))==1

def test_dedup(tmp_path, monkeypatch):
    monkeypatch.setenv('XHS_DATA_DIR', str(tmp_path))
    assert baocun('笔记', biaoti='唯一标题', zan=1, cang=0, ping=0) == True
    assert baocun('笔记', biaoti='唯一标题', zan=2, cang=0, ping=0) == False
    assert len(liebiao('笔记')) == 1

def test_structured_product(tmp_path, monkeypatch):
    monkeypatch.setenv('XHS_DATA_DIR', str(tmp_path))
    baocun('产品', biaoti='测试产品', jiage='99', maidian='好用', yonghu='学生', jinyongci='最')
    products = liebiao('产品')
    assert len(products) == 1
    p = products[0]
    assert p['jiage'] == '99'
    assert p['maidian'] == '好用'
    assert p['yonghu'] == '学生'
    assert p['jinyongci'] == '最'

def test_an_id(tmp_path, monkeypatch):
    monkeypatch.setenv('XHS_DATA_DIR', str(tmp_path))
    baocun('笔记', biaoti='查找我', zan=5, cang=3, ping=2)
    records = liebiao('笔记')
    r = an_id(records[0]['id'])
    assert r is not None
    assert r['biaoti'] == '查找我'
    assert an_id(99999) is None

def test_pingfen(tmp_path, monkeypatch):
    monkeypatch.setenv('XHS_DATA_DIR', str(tmp_path))
    baocun('笔记', biaoti='热门', zan=300, cang=180, ping=50, platform='小红书')
    baocun('笔记', biaoti='冷门', zan=10, cang=5, ping=2, platform='小红书')
    notes = liebiao('笔记')
    scores = pingfen(notes)
    assert len(scores) == 2
    assert scores[0]['score'] > scores[1]['score']
    assert scores[0]['biaoti'] == '热门'

def test_baogao_no_ai(tmp_path, monkeypatch):
    monkeypatch.setenv('XHS_DATA_DIR', str(tmp_path))
    baocun('笔记', biaoti='测试', zan=100, cang=50, ping=10, platform='小红书')
    notes = liebiao('笔记')
    report = baogao(notes, '', '', '')
    assert report['stats']['total'] == 1
    assert '请先' in report['summary']

def test_fenxi_ai_fallback(tmp_path, monkeypatch):
    monkeypatch.setenv('XHS_DATA_DIR', str(tmp_path))
    result = fenxi_ai('哪里买这个产品\n希望便宜一点', '', '', '')
    assert result == fenxi('哪里买这个产品\n希望便宜一点')
