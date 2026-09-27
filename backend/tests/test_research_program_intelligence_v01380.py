
from app import research_program_intelligence_v01380 as m

def payload():
    return {'programId':'program-a','studies':[
        {'studyId':'s1','projectId':'p1','nodes':[{'id':'data','type':'dataset'},{'id':'fig','type':'figure'}],'edges':[{'id':'e1','from':'data','to':'fig'}],'changeEvents':[{'id':'c1','objectId':'data','objectType':'dataset'}]},
        {'studyId':'s2','projectId':'p2','nodes':[{'id':'data','type':'dataset'},{'id':'finding','type':'finding'}],'edges':[{'id':'e2','from':'data','to':'finding'}],'changeEvents':[]}
    ],'relationships':[{'fromStudyId':'s2','toStudyId':'s1','type':'replication-of'}]}

def test_program_normalizes():
    x=m.normalize_program(payload()); assert x['ok']; assert len(x['record']['studies'])==2

def test_shared_object_index():
    x=m.shared_object_index(payload()); assert x['ok']; assert x['sharedObjects'][0]['objectId']=='data'; assert x['sharedObjects'][0]['studyCount']==2

def test_change_propagates_across_studies():
    p=payload(); p['changeEvent']={'id':'chg','objectId':'data','objectType':'dataset'}
    x=m.program_change_impact(p); assert x['ok']; assert set(x['record']['affectedStudyIds'])=={'s1','s2'}

def test_program_living_status():
    x=m.program_living_status(payload()); assert x['ok']; assert x['studyCount']==2; assert x['assessmentRequiredCount']>=1

def test_policy_has_no_automatic_truth_or_consensus():
    x=m.policy(); assert x['automaticScientificValidity'] is False; assert x['automaticConsensus'] is False; assert x['truthRanking'] is False
