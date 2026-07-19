from pathlib import Path
import json, hmac, hashlib
import pytest
from fastapi.testclient import TestClient
from app.public_research_integrations import PublicResearchIntegrationGateway, IntegrationError, policies, sdk_manifest, public_api_catalog, validate_webhook_url
from app.team_workspaces import TeamWorkspaceManager

def setup(tmp_path:Path):
    ws=TeamWorkspaceManager(str(tmp_path/'ws.sqlite3'),100,1000,10000)
    ws.create({'id':'research-team','title':'Research Team'},'alice','Alice')
    for actor,role in [('dana','editor'),('cory','contributor'),('eve','viewer')]:
        inv=ws.invite('research-team',{'inviteeActorId':actor,'role':role},'alice'); ws.accept_invitation({'token':inv['invitation']['token']},actor,actor.title())
    return ws,PublicResearchIntegrationGateway(str(tmp_path/'integrations.sqlite3'),ws,'master-secret')

def test_policy_catalog_and_sdk():
    assert policies()['version']=='0.38.2'; assert len(public_api_catalog()['catalogHash'])==64; assert sdk_manifest()['packages'][0]['language']=='python'

def test_webhook_url_safety():
    assert validate_webhook_url('https://example.org/hooks')=='https://example.org/hooks'
    for bad in ['http://example.org/hook','https://localhost/hook','https://127.0.0.1/hook','https://user:pass@example.org/hook']:
        with pytest.raises(IntegrationError): validate_webhook_url(bad)

def test_register_and_list_webhook(tmp_path):
    _,gateway=setup(tmp_path)
    made=gateway.register_webhook('research-team',{'id':'decision-hook','url':'https://example.org/hooks/lab','events':['research.handoff.sealed']},'dana')
    assert made['subscription']['status']=='active' and len(made['signingSecret'])>20
    listed=gateway.list_webhooks('research-team','eve'); assert listed['count']==1 and 'signingSecret' not in listed['subscriptions'][0]

def test_viewer_cannot_register_webhook(tmp_path):
    _,gateway=setup(tmp_path)
    with pytest.raises(IntegrationError) as exc: gateway.register_webhook('research-team',{'url':'https://example.org/h','events':['research.dataset.updated']},'eve')
    assert exc.value.status_code==403

def test_signed_event_delivery(tmp_path):
    _,gateway=setup(tmp_path)
    made=gateway.register_webhook('research-team',{'id':'hook','url':'https://example.org/h','events':['research.dataset.updated']},'dana')
    result=gateway.emit_event('research-team',{'id':'evt-1','eventType':'research.dataset.updated','data':{'datasetId':'d1'}},'cory')
    assert result['count']==1 and result['deliveries'][0]['status']=='queued'
    delivery=gateway.list_deliveries('research-team','eve')['deliveries'][0]
    envelope=json.dumps(delivery['envelope'],sort_keys=True,separators=(',',':'),ensure_ascii=False)
    timestamp=delivery['envelope']['timestamp']; expected=hmac.new(made['signingSecret'].encode(),f'{timestamp}.{json.dumps(delivery["envelope"]["event"],sort_keys=True,separators=(",",":"),ensure_ascii=False)}'.encode(),hashlib.sha256).hexdigest()
    assert len(delivery['signature'])==64 and delivery['signature']==expected

def test_embed_sign_and_verify(tmp_path):
    _,gateway=setup(tmp_path)
    created=gateway.create_embed('research-team',{'view':'publication','resource':{'id':'pub-1','sha256':'1'*64},'ttlSeconds':300},'eve')
    verified=gateway.verify_embed(created['token']); assert verified['manifest']['resource']['id']=='pub-1'
    with pytest.raises(IntegrationError): gateway.verify_embed(created['token']+'x')

def test_embed_rejects_restricted_payload(tmp_path):
    _,gateway=setup(tmp_path)
    with pytest.raises(IntegrationError): gateway.create_embed('research-team',{'view':'dataset','resource':{'id':'d1','rawData':[1,2]}},'eve')

def test_fastapi_routes(tmp_path,monkeypatch):
    monkeypatch.setenv('SC_LAB_TEAM_WORKSPACE_DB_PATH',str(tmp_path/'route-ws.sqlite3'))
    monkeypatch.setenv('SC_LAB_PUBLIC_INTEGRATION_DB_PATH',str(tmp_path/'route-integrations.sqlite3'))
    monkeypatch.setenv('SC_LAB_WEBHOOK_SIGNING_SECRET','route-secret')
    monkeypatch.setenv('SC_LAB_PUBLIC_API_KEY','public-key')
    monkeypatch.setenv('SC_LAB_PUBLIC_API_SCOPES','research:read,research:write,webhooks:read,webhooks:write,webhooks:emit,embeds:write')
    import importlib, app.config as config_module, app.main as main_module
    importlib.reload(config_module); importlib.reload(main_module)
    client=TestClient(main_module.app); headers={'X-SC-Lab-API-Key':'public-key','X-SC-Lab-Actor':'alice'}
    assert client.get('/v1/public-research-api').status_code==200
    assert client.post('/v1/team-workspaces',headers={'X-SC-Lab-Key':'public-key','X-SC-Lab-Actor':'alice'},json={'id':'route-team','title':'Route Team'}).status_code==200
    created=client.post('/v1/team-workspaces/route-team/webhooks',headers=headers,json={'id':'hook','url':'https://example.org/h','events':['research.dataset.updated']})
    assert created.status_code==200
    emitted=client.post('/v1/team-workspaces/route-team/webhook-events',headers=headers,json={'eventType':'research.dataset.updated','data':{'id':'d1'}})
    assert emitted.status_code==200 and emitted.json()['count']==1
    embed=client.post('/v1/team-workspaces/route-team/research-embeds',headers=headers,json={'view':'dataset','resource':{'id':'d1'}})
    assert embed.status_code==200
    assert client.get(embed.json()['embedPath']).status_code==200


def test_guarded_https_dispatch(tmp_path,monkeypatch):
    ws,_=setup(tmp_path); gateway=PublicResearchIntegrationGateway(str(tmp_path/'dispatch.sqlite3'),ws,'master-secret',delivery_enabled=True)
    gateway.register_webhook('research-team',{'id':'dispatch-hook','url':'https://example.org/h','events':['research.dataset.updated']},'dana')
    delivery_id=gateway.emit_event('research-team',{'eventType':'research.dataset.updated','data':{'id':'d1'}},'cory')['deliveries'][0]['id']
    class Response:
        status=204
        def __enter__(self): return self
        def __exit__(self,*args): return False
        def read(self,n=-1): return b''
        def getcode(self): return 204
    import app.public_research_integrations as module
    monkeypatch.setattr(module,'validate_webhook_url',lambda value,resolve_dns=False:value)
    monkeypatch.setattr(module,'urlopen',lambda request,timeout=15:Response())
    result=gateway.dispatch_delivery('research-team',delivery_id,'cory')
    assert result['ok'] is True and result['delivery']['status']=='delivered' and result['delivery']['attempt']==1

def test_contract_instances_and_public_payload_safety(tmp_path):
    import jsonschema
    _, gateway = setup(tmp_path)
    registered = gateway.register_webhook('research-team', {'id':'schema-hook','url':'https://example.org/schema','events':['research.dataset.updated']}, 'dana')
    emitted = gateway.emit_event('research-team', {'eventType':'research.dataset.updated','subject':'dataset:d1','data':{'id':'d1'}}, 'cory')
    delivery = gateway.list_deliveries('research-team', 'eve')['deliveries'][0]
    embed = gateway.create_embed('research-team', {'view':'dataset','resource':{'id':'d1'},'metadata':{'summary':'Public reference'}}, 'eve')['manifest']
    contract_root = Path(__file__).resolve().parents[1] / 'contracts'
    for name, value in [
        ('webhook-subscription-v0382.schema.json', registered['subscription']),
        ('research-webhook-event-v0382.schema.json', emitted['event']),
        ('webhook-delivery-v0382.schema.json', delivery),
        ('research-embed-manifest-v0382.schema.json', embed),
        ('research-sdk-manifest-v0382.schema.json', sdk_manifest()),
    ]:
        jsonschema.Draft202012Validator(json.loads((contract_root / name).read_text())).validate(value)
    with pytest.raises(IntegrationError):
        gateway.emit_event('research-team', {'eventType':'research.dataset.updated','data':{'accessToken':'not-allowed'}}, 'cory')


def test_wordpress_bridge_and_compute_key_header(tmp_path, monkeypatch):
    monkeypatch.setenv('SC_LAB_TEAM_WORKSPACE_DB_PATH', str(tmp_path/'wp-ws.sqlite3'))
    monkeypatch.setenv('SC_LAB_PUBLIC_INTEGRATION_DB_PATH', str(tmp_path/'wp-integrations.sqlite3'))
    monkeypatch.setenv('SC_LAB_WEBHOOK_SIGNING_SECRET', 'wp-secret')
    monkeypatch.setenv('SC_LAB_PUBLIC_API_KEY', 'shared-key')
    monkeypatch.setenv('SC_LAB_PUBLIC_API_SCOPES', 'research:read,research:write,webhooks:read,webhooks:write,webhooks:emit,embeds:write')
    import importlib, app.config as config_module, app.main as main_module
    importlib.reload(config_module); importlib.reload(main_module)
    client = TestClient(main_module.app)
    assert client.get('/v1/research-integrations/health', headers={'X-SC-Lab-Key':'shared-key','X-SC-Lab-Actor':'alice'}).status_code == 200
    repo_root = Path(__file__).resolve().parents[2]
    proxy = (repo_root/'includes/class-sc-lab-python-compute-core-v0261.php').read_text()
    template = (repo_root/'templates/lab-app.php').read_text()
    browser = (repo_root/'assets/js/modules/public-research-integrations.js').read_text()
    assert '/compute/core/research-integrations/health' in proxy
    assert '/compute/core/team-workspaces/(?P<workspace>' in proxy and '/webhook-events' in proxy
    assert 'data-lab-module="public-research-integrations"' in template
    assert "registerModule('public-research-integrations'" in browser

def test_event_idempotency_and_conflict(tmp_path):
    _, gateway = setup(tmp_path)
    gateway.register_webhook('research-team', {'id':'idempotent-hook','url':'https://example.org/idempotent','events':['research.dataset.updated']}, 'dana')
    payload = {'id':'evt-idempotent','eventType':'research.dataset.updated','data':{'id':'d1'}}
    first = gateway.emit_event('research-team', payload, 'cory')
    second = gateway.emit_event('research-team', payload, 'cory')
    assert first['idempotent'] is False and second['idempotent'] is True
    assert first['deliveries'][0]['id'] == second['deliveries'][0]['id']
    with pytest.raises(IntegrationError) as exc:
        gateway.emit_event('research-team', {**payload, 'data':{'id':'d2'}}, 'cory')
    assert exc.value.status_code == 409
