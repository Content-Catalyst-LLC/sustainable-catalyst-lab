import os, tempfile, sqlite3
import pytest
from app.institutional_research_governance_review_federation_v01630 import InstitutionalResearchGovernanceReviewFederationManager, InstitutionalGovernanceError

class Programs:
    def get_program(self,pid):
        if pid!='program:test': raise ValueError('missing')
        return {'id':pid,'title':'Program','state':'active','projects':[{'projectId':'research:a','status':'active'}]}

def manager(td): return InstitutionalResearchGovernanceReviewFederationManager(os.path.join(td,'gov.sqlite3'),Programs())
def seed(m):
    a=m.create_institution({'institutionId':'institution:a','title':'Institution A','jurisdiction':'US-MO'})['institution']
    b=m.create_institution({'institutionId':'institution:b','title':'Institution B','jurisdiction':'US-IL'})['institution']
    body=m.create_body(a['id'],{'bodyId':'review-body:a','bodyType':'scientific-review-board','title':'Scientific Review Board','mandate':'Review scientific research packages.'})['body']
    case=m.create_case(a['id'],{'caseId':'review-case:a','bodyId':body['id'],'caseType':'scientific','title':'Review A','scope':'Review program evidence.','programId':'program:test','projectId':'research:a'})['case']
    return a,b,body,case

def test_health_and_boundaries():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); h=m.health(); p=m.policies(); assert h['version']=='0.163.0'; assert h['automaticReviewerSelection'] is False; assert h['automaticEthicsApproval'] is False; assert p['explicitReviewerAssignmentsOnly'] is True

def test_institution_registry_and_human_state_change():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); a=m.create_institution({'institutionId':'institution:a','title':'A','jurisdiction':'US'})['institution']; assert a['state']=='active'
        with pytest.raises(InstitutionalGovernanceError): m.set_institution_state(a['id'],{'state':'limited'})
        a=m.set_institution_state(a['id'],{'state':'limited','humanAuthorization':True})['institution']; assert a['state']=='limited'

def test_governance_body_requires_institution():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td)
        with pytest.raises(InstitutionalGovernanceError): m.create_body('institution:none',{'title':'Board','mandate':'Review'})

def test_federation_link_requires_two_distinct_institutions_and_human_activation():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); a,b,_,_=seed(m)
        with pytest.raises(InstitutionalGovernanceError): m.create_federation_link({'fromInstitutionId':a['id'],'toInstitutionId':a['id'],'scope':'x'})
        with pytest.raises(InstitutionalGovernanceError): m.create_federation_link({'fromInstitutionId':a['id'],'toInstitutionId':b['id'],'state':'active','scope':'External review'})
        x=m.create_federation_link({'fromInstitutionId':a['id'],'toInstitutionId':b['id'],'state':'active','scope':'External review','humanAuthorization':True})['link']; assert x['state']=='active'

def test_case_validates_program_and_body():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); a=m.create_institution({'institutionId':'institution:a','title':'A','jurisdiction':'US'})['institution']; body=m.create_body(a['id'],{'bodyId':'review-body:a','title':'Board','mandate':'Review'})['body']
        with pytest.raises(InstitutionalGovernanceError): m.create_case(a['id'],{'bodyId':body['id'],'title':'X','scope':'Y','programId':'program:missing'})

def test_assignment_requires_explicit_independence_declaration():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); _,b,_,case=seed(m)
        with pytest.raises(InstitutionalGovernanceError): m.assign_reviewer(case['id'],{'reviewerId':'person:r1','role':'external'})
        a=m.assign_reviewer(case['id'],{'reviewerId':'person:r1','affiliationInstitutionId':b['id'],'role':'external','independenceDeclaration':'Reviewer declares no listed conflict.'})['assignment']; assert a['state']=='assigned'

def test_assignment_state_is_human_controlled():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); _,_,_,case=seed(m); a=m.assign_reviewer(case['id'],{'reviewerId':'person:r1','role':'primary','independenceDeclaration':'Declared.'})['assignment']
        with pytest.raises(InstitutionalGovernanceError): m.set_assignment_state(a['id'],{'state':'accepted'})
        a=m.set_assignment_state(a['id'],{'state':'accepted','humanAuthorization':True})['assignment']; assert a['state']=='accepted'

def test_decision_requires_human_authorization_and_does_not_auto_transition_case():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); _,_,_,case=seed(m); a=m.assign_reviewer(case['id'],{'reviewerId':'person:r1','role':'primary','independenceDeclaration':'Declared.'})['assignment']
        with pytest.raises(InstitutionalGovernanceError): m.record_decision(case['id'],{'assignmentId':a['id'],'outcome':'approve','statement':'Approve.'})
        d=m.record_decision(case['id'],{'assignmentId':a['id'],'outcome':'approve','statement':'Approve.','humanAuthorization':True}); assert d['caseStateChangedAutomatically'] is False; assert m.get_case(case['id'])['state']=='draft'

def test_dissent_is_preserved_not_resolved_automatically():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); _,_,_,case=seed(m); a=m.assign_reviewer(case['id'],{'reviewerId':'person:r1','role':'external','independenceDeclaration':'Declared.'})['assignment']; d=m.record_decision(case['id'],{'assignmentId':a['id'],'outcome':'dissent','statement':'I dissent.','humanAuthorization':True}); assert d['dissentPreserved'] is True; assert m.get_case(case['id'])['decisions'][0]['outcome']=='dissent'

def test_attestation_requires_human_authorization():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); _,_,_,case=seed(m)
        with pytest.raises(InstitutionalGovernanceError): m.add_attestation(case['id'],{'attestationType':'policy-compliance','statement':'Compliant.'})
        a=m.add_attestation(case['id'],{'attestationType':'policy-compliance','statement':'Reviewed against policy.','humanAuthorization':True})['attestation']; assert a['humanAuthorization'] is True

def test_case_terminal_transition_requires_decision_and_human_authorization():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); _,_,_,case=seed(m); m.transition_case(case['id'],{'targetState':'submitted','reason':'Submit','humanAuthorization':True}); m.transition_case(case['id'],{'targetState':'under-review','reason':'Start','humanAuthorization':True})
        with pytest.raises(InstitutionalGovernanceError): m.transition_case(case['id'],{'targetState':'approved','reason':'Approve','humanAuthorization':True})
        a=m.assign_reviewer(case['id'],{'reviewerId':'person:r1','role':'primary','independenceDeclaration':'Declared.'})['assignment']; m.record_decision(case['id'],{'assignmentId':a['id'],'outcome':'approve','statement':'Approve','humanAuthorization':True}); c=m.transition_case(case['id'],{'targetState':'approved','reason':'Board authorization','resolutionNote':'Human board sign-off.','humanAuthorization':True})['case']; assert c['state']=='approved'

def test_manifest_verification():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); a,_,_,_=seed(m); x=m.manifest(a['id']); assert m.verify_manifest(x)['valid'] is True; x['manifest']['institution']['state']='tampered'; assert m.verify_manifest(x)['valid'] is False

def test_snapshot_is_human_authorized_and_immutable():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); a,_,_,_=seed(m)
        with pytest.raises(InstitutionalGovernanceError): m.snapshot(a['id'],{})
        s=m.snapshot(a['id'],{'humanAuthorization':True})['snapshot']; assert m.get_snapshot(s['id'])['snapshot']['digest']==s['digest']

def test_command_center_and_timeline_are_descriptive():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); a,_,_,_=seed(m); c=m.command_center(a['id']); assert c['institution']['id']==a['id']; assert c['descriptiveOnly'] is True; assert m.timeline(a['id'])['count']>=3

def test_connection_context_closes_file_descriptor():
    with tempfile.TemporaryDirectory() as td:
        m=manager(td); db=m._connect(); assert db.execute('select 1').fetchone()[0]==1
        with db: pass
        with pytest.raises(sqlite3.ProgrammingError): db.execute('select 1')
