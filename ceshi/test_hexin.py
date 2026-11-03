import io
import pytest
from hexin import daoru, fenxi, tuomin
from shujuku import baocun, liebiao, engine

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
