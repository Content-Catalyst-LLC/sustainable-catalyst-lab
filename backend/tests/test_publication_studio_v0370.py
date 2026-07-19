import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.publication_studio import ReproducibilityPublicationStudio, PublicationStudioError, policies
from app.team_workspaces import TeamWorkspaceManager

def setup(tmp_path: Path):
    ws=TeamWorkspaceManager(str(tmp_path/'workspaces.sqlite3'),100,1000,10000)
    ws.create({'id':'research-team','title':'Research Team'},'alice','Alice')
    for actor,role in [('bob','reviewer'),('dana','editor'),('eve','viewer')]:
        inv=ws.invite('research-team',{'inviteeActorId':actor,'role':role},'alice'); ws.accept_invitation({'token':inv['invitation']['token']},actor,actor.title())
    studio=ReproducibilityPublicationStudio(str(tmp_path/'publications.sqlite3'),ws,100,100,100,10000)
    return ws,studio

def draft(studio):
    p=studio.create_package('research-team',{'id':'wetland-repro','title':'Wetland Reproducibility Package'},'dana')['package']
    return studio.update_package('research-team',p['id'],{'resources':[{'id':'dataset-1','type':'dataset','title':'Wetland observations','sha256':'1'*64,'mediaType':'text/csv'}],'methods':{'protocol':'count observations','registeredMethods':['statistics.descriptive']},'environment':{'python':'3.12','packages':{'numpy':'2'}},'citations':[{'formatted':'Ahmad, T. (2026). Wetland study.'}],'provenance':{'workspace':'research-team','runIds':['run-1']}},'dana')['package']

def test_policy_contract():
    p=policies(10,20,30); assert p['version']=='0.37.0'; assert p['capabilities']['immutableSealedPackages'] is True; assert p['capabilities']['embeddedRestrictedData'] is False

def test_roles_and_draft_update(tmp_path):
    _,s=setup(tmp_path)
    with pytest.raises(PublicationStudioError) as exc: s.create_package('research-team',{'id':'blocked'},'eve')
    assert exc.value.status_code==403
    p=draft(s); assert p['resources'][0]['id']=='dataset-1' and p['status']=='draft'

def test_embedded_bytes_and_executable_fields_rejected(tmp_path):
    _,s=setup(tmp_path); p=s.create_package('research-team',{'id':'unsafe'},'dana')['package']
    with pytest.raises(PublicationStudioError) as exc: s.update_package('research-team',p['id'],{'methods':{'callbackUrl':'https://bad.example'}},'dana')
    assert exc.value.status_code==422

def test_seal_is_immutable_and_hashed(tmp_path):
    _,s=setup(tmp_path); p=draft(s); sealed=s.seal_package('research-team',p['id'],'dana')['package']; assert sealed['status']=='sealed' and len(sealed['packageHash'])==64
    with pytest.raises(PublicationStudioError) as exc: s.update_package('research-team',p['id'],{'title':'changed'},'dana')
    assert exc.value.status_code==409

def test_verification_detects_tampering(tmp_path):
    _,s=setup(tmp_path); p=s.seal_package('research-team',draft(s)['id'],'dana')['package']; assert s.verify_package('research-team',p['id'],'bob')['ok'] is True
    with s._connect() as con: con.execute("UPDATE reproducibility_packages SET resources_json=? WHERE id=?",(json.dumps([{'id':'x','type':'dataset','sha256':'2'*64}]),p['id']))
    assert s.verify_package('research-team',p['id'],'bob')['ok'] is False

def test_publication_render_and_html_escape(tmp_path):
    _,s=setup(tmp_path); p=s.seal_package('research-team',draft(s)['id'],'dana')['package']; s.verify_package('research-team',p['id'],'bob')
    pub=s.create_publication('research-team',{'id':'paper-1','packageId':p['id'],'title':'Wetlands <script>','abstract':'Findings & limits','authors':[{'name':'Tariq Ahmad'}],'sections':[{'title':'Methods','body':'Measured <carefully>.'}]},'dana')['publication']
    export=s.render_publication('research-team',pub['id'],'eve')['export']; assert '<script>' not in export['files']['publication.html']; assert '&lt;script&gt;' in export['files']['publication.html']; assert len(export['exportHash'])==64

def test_ready_requires_verified_package(tmp_path):
    _,s=setup(tmp_path); p=s.seal_package('research-team',draft(s)['id'],'dana')['package']; pub=s.create_publication('research-team',{'id':'paper-2','packageId':p['id'],'abstract':'A','authors':['Author'],'sections':[{'title':'Results','body':'B'}]},'dana')['publication']
    with pytest.raises(PublicationStudioError) as exc: s.mark_ready('research-team',pub['id'],'bob')
    assert exc.value.status_code==409
    s.verify_package('research-team',p['id'],'bob'); assert s.mark_ready('research-team',pub['id'],'bob')['publication']['status']=='ready'

def test_publish_requires_signoff_and_is_immutable(tmp_path):
    _,s=setup(tmp_path); p=s.seal_package('research-team',draft(s)['id'],'dana')['package']; s.verify_package('research-team',p['id'],'bob'); pub=s.create_publication('research-team',{'id':'paper-3','packageId':p['id'],'abstract':'A','authors':['Author'],'sections':[{'title':'Results','body':'B'}]},'dana')['publication']; s.mark_ready('research-team',pub['id'],'bob')
    with pytest.raises(PublicationStudioError): s.publish('research-team',pub['id'],{},'alice')
    out=s.publish('research-team',pub['id'],{'scientificSignoff':{'id':'signoff-1','signoffHash':'a'*64}},'alice'); assert out['publication']['status']=='published'; assert out['publication']['canonicalUri'].startswith('urn:sc-lab:publication:')

def test_health_and_hashed_timeline(tmp_path):
    _,s=setup(tmp_path); draft(s); h=s.health(); assert h['database']['integrity']=='ok' and h['database']['schemaVersion']==1; events=s.timeline('research-team','eve')['events']; assert events and all(len(e['eventHash'])==64 for e in events)

def test_fastapi_routes_use_workspace_actor(tmp_path, monkeypatch):
    from app import main
    ws,s=setup(tmp_path); monkeypatch.setattr(main,'team_workspaces',ws); monkeypatch.setattr(main,'publication_studio',s)
    headers={'X-SC-Lab-Actor':'dana','X-SC-Lab-Actor-Name':'Dana'}
    with TestClient(main.app) as client:
        health=client.get('/v1/publication-studio/health',headers=headers); assert health.status_code==200 and health.json()['serviceVersion']=='0.38.2'
        created=client.post('/v1/team-workspaces/research-team/reproducibility-packages',headers=headers,json={'id':'api-package','title':'API package'}); assert created.status_code==200
        listed=client.get('/v1/team-workspaces/research-team/reproducibility-packages',headers=headers); assert listed.status_code==200 and len(listed.json()['packages'])==1
