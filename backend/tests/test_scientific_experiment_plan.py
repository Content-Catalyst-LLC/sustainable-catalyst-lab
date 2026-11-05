from collections import Counter
from copy import deepcopy
import pytest
from pydantic import ValidationError
from app.scientific_experiment_plan import StudyPlan,build_plan

def recipe():return {'project_id':'synthetic-project','title':'Synthetic blocked study proposal','source_kind':'simulation','source_refs':['synthetic:protocol'],'seed':42,'units':[{'id':f'SYNTHETIC-{b}-{i}','block':b} for b in ['A','B'] for i in range(4)],'groups':['untreated','treatment'],'untreated_control':'untreated','primary_outcome':'Proposed transported solute; not removal','observation_windows':['baseline-pending','follow-up-pending'],'sampling_protocol_ref':'synthetic:protocol'}
def test_native_block_balance_reproducibility_and_pending_status():
 x=recipe();a=build_plan(StudyPlan.model_validate(x));b=build_plan(StudyPlan.model_validate(x))
 assert a==b
 for block in ['A','B']:assert Counter(r['group'] for r in a['assignments'] if r['block']==block)=={'untreated':2,'treatment':2}
 assert not a['preregistered'] and not a['coordinates_assumed'] and not a['field_execution_authorized'] and a['net_removal']=='NOT_QUANTIFIED'
 assert all(r['baseline_ref'] is None for r in a['assignments'])
@pytest.mark.parametrize('mutation',['duplicate','unbalanced','no-control','coordinates','bool-seed'])
def test_invalid_or_assumed_study_inputs_are_rejected(mutation):
 x=recipe()
 if mutation=='duplicate':x['units'][1]['id']=x['units'][0]['id']
 if mutation=='unbalanced':x['units'].pop()
 if mutation=='no-control':x['untreated_control']='missing'
 if mutation=='coordinates':x['units'][0]['latitude']=52
 if mutation=='bool-seed':x['seed']=True
 with pytest.raises(ValidationError):StudyPlan.model_validate(x)
