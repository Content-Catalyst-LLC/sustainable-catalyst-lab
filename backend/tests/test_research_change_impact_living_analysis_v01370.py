
from app import research_change_impact_living_analysis_v01370 as m

def payload():
    return {'projectId':'p1','changeEvent':{'objectId':'data','objectType':'dataset','beforeRef':'v1','afterRef':'v2'},'nodes':[{'id':'data','type':'dataset'},{'id':'model','type':'model'},{'id':'finding','type':'finding'}],'edges':[{'from':'data','to':'model'},{'from':'model','to':'finding'}]}

def test_change_impact():
    r=m.analyze_change(payload()); assert r['ok']; assert [x['id'] for x in r['record']['potentiallyAffected']]==['model','finding']; assert len(r['record']['obligations'])==2

def test_living_status():
    p=payload(); p['changeEvents']=[p['changeEvent']]; r=m.living_status(p); assert r['ok']; assert r['state']=='attention-required'; assert r['assessmentRequiredCount']==2

def test_acknowledge_human():
    r=m.acknowledge({'objectId':'model','action':'reviewed'}); assert r['ok']; assert r['record']['scientificJudgment']=='human'
