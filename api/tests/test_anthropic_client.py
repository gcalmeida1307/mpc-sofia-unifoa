from unittest.mock import Mock, patch
from ai.client import OpenAIResponsesClient

def test_anthropic_payload_and_response(monkeypatch):
    monkeypatch.setattr('ai.client.settings.ANTHROPIC_API_KEY','test-key')
    monkeypatch.setattr('ai.client.settings.ANTHROPIC_MODEL','claude-test')
    monkeypatch.setattr('ai.client.settings.ANTHROPIC_MAX_TOKENS',321)
    monkeypatch.setattr('ai.client.settings.OLLAMA_BASE_URL','')
    response=Mock(); response.raise_for_status.return_value=None
    response.json.return_value={'content':[{'type':'text','text':'Olá'}],'model':'claude-test','usage':{'input_tokens':2,'output_tokens':1}}
    with patch('ai.client.requests.post',return_value=response) as post:
        result=OpenAIResponsesClient().ask([{'role':'system','content':'Seja breve'},{'role':'user','content':'Oi'}])
    assert result['provider']=='anthropic' and result['text']=='Olá'
    payload=post.call_args.kwargs['json']
    assert payload=={'model':'claude-test','max_tokens':321,'cache_control':{'type':'ephemeral'},'messages':[{'role':'user','content':'Oi'}],'system':'Seja breve'}
    assert post.call_args.kwargs['headers']['x-api-key']=='test-key'

def test_ollama_is_fallback(monkeypatch):
    monkeypatch.setattr('ai.client.settings.ANTHROPIC_API_KEY','key')
    client=OpenAIResponsesClient()
    monkeypatch.setattr(client,'_ask_anthropic',lambda messages: None)
    monkeypatch.setattr(client,'_ask_ollama',lambda messages: {'text':'local','provider':'ollama'})
    assert client.ask([{'role':'user','content':'oi'}])['provider']=='ollama'
