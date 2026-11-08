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

def test_api_connection_error(monkeypatch):
    def raise_conn(*a, **k):
        raise hexin.requests.ConnectionError('refused')
    monkeypatch.setattr(hexin.requests,'post',raise_conn)
    with pytest.raises(ValueError, match='无法连接'): hexin.ai('https://example.test/v1','m','k','p')

def test_api_timeout(monkeypatch):
    def raise_timeout(*a, **k):
        raise hexin.requests.Timeout('too slow')
    monkeypatch.setattr(hexin.requests,'post',raise_timeout)
    with pytest.raises(ValueError, match='超时'): hexin.ai('https://example.test/v1','m','k','p')

def test_api_invalid_json(monkeypatch):
    class Response:
        ok=True
        def json(self): raise ValueError('bad json')
    monkeypatch.setattr(hexin.requests,'post',lambda *a,**k:Response())
    with pytest.raises(ValueError, match='JSON'): hexin.ai('https://example.test/v1','m','k','p')

def test_api_bad_response_format(monkeypatch):
    class Response:
        ok=True
        def json(self): return {'unexpected':'format'}
    monkeypatch.setattr(hexin.requests,'post',lambda *a,**k:Response())
    with pytest.raises(ValueError, match='响应格式'): hexin.ai('https://example.test/v1','m','k','p')

def test_ollama_payload(monkeypatch):
    class Response:
        ok=True
        def json(self): return {'message':{'content':'ollama结果'}}
    def post(url, **kwargs):
        assert url == 'http://localhost:11434/api/chat'
        assert kwargs['json']['model'] == 'llama3'
        return Response()
    monkeypatch.setattr(hexin.requests,'post',post)
    assert hexin.ai('http://localhost:11434','llama3','','提示',ollama=True)=='ollama结果'

def test_invalid_url(monkeypatch):
    with pytest.raises(ValueError, match='http'): hexin.ai('not-a-url','m','k','p')
