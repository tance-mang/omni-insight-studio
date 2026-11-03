import pytest
import hexin

def test_api_payload(monkeypatch):
    class Response:
        ok=True
        def json(self): return {'choices':[{'message':{'content':'原创结果'}}]}
    def post(url, **kwargs):
        assert url == 'https://example.test/v1/chat/completions'
        assert kwargs['timeout']==120
        assert kwargs['headers']['Authorization']=='Bearer test-key'
        return Response()
    monkeypatch.setattr(hexin.requests,'post',post)
    assert hexin.ai('https://example.test/v1','model','test-key','提示')=='原创结果'

def test_api_failure(monkeypatch):
    class Response:
        ok=False
        status_code=401
    monkeypatch.setattr(hexin.requests,'post',lambda *a,**k:Response())
    with pytest.raises(ValueError,match='401'): hexin.ai('https://example.test/v1','m','k','p')
