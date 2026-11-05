from copy import deepcopy
import hashlib,json
import pytest
from pydantic import ValidationError
from app.scientific_research_figures import FigureSpec,render

SOURCE={'id':'published-example','citation':'Synthetic citation for renderer testing','uri':'https://example.org/synthetic','sha256':'a'*64,'source_kind':'simulation','locator':'Synthetic fixture','review':'pending','rights_ref':'Synthetic test data'}
PANEL={'label':'Separate endpoint','source_id':SOURCE['id'],'material':'Synthetic material','time_window':'4 years','denominator':'per experimental hectare over four years','endpoint':'potential','value':10.5,'plus_minus':3.8,'uncertainty_type':'reported +/-; interval type not inferred','unit':'t CO2/ha','finding':'Synthetic test only; never pooled or transferred to a site.'}
def fixture():return {'title':'Separate scientific endpoints','description':'Synthetic source-bound renderer regression','project_id':'synthetic-project','revision':1,'family':'evidence-comparison','status':'simulation','sources':[SOURCE],'panels':[PANEL],'limitations':['No pooled estimate or site-specific removal.']}

def test_separate_panels_and_qualitative_null_are_reproducible():
 x=fixture();x['panels'].append({**PANEL,'label':'Null signal','endpoint':'qualitative-response','value':None,'plus_minus':None,'finding':'No statistically significant response.'})
 spec=FigureSpec.model_validate(x);first=render(spec)
 assert first==render(spec)
 assert '10.5 +/- 3.8' in first['svg'] and 'Qualitative finding' in first['svg']
 assert first['table']['rows'][1][5] is None
 assert first['figure_reference']['immutable_underlying_figure'] is True
 assert first['net_removal_status']=='NOT_QUANTIFIED'

@pytest.mark.parametrize('mutation',['pooled','zero-null','bad-source','reversed','review','duplicate'])
def test_invalid_or_overclaimed_data_is_rejected(mutation):
 x=deepcopy(fixture())
 if mutation=='pooled':x['pooled_estimate']=10
 if mutation=='zero-null':x['panels'][0]['endpoint']='qualitative-response'
 if mutation=='bad-source':x['panels'][0]['source_id']='missing'
 if mutation=='reversed':x['panels'][0].update(lower=12,upper=10)
 if mutation=='review':x['sources'][0]['review']='human-reviewed'
 if mutation=='duplicate':x['panels'].append(x['panels'][0])
 with pytest.raises(ValidationError):FigureSpec.model_validate(x)

def test_distinct_denominators_and_conceptual_gates():
 x=deepcopy(fixture());x['family']='denominator-ranges'
 x['panels']=[{**PANEL,'endpoint':'transport-fraction','value':None,'plus_minus':None,'lower':9.5,'upper':11,'unit':'%','denominator':'theoretical potential exported over two years'},
 {**PANEL,'label':'Seasonal streamwater','endpoint':'transport-fraction','value':None,'plus_minus':None,'lower':7,'upper':17,'unit':'%','denominator':'observed seasonal streamwater alkalinity'}]
 result=render(FigureSpec.model_validate(x));assert 'theoretical potential' in result['svg'] and 'observed seasonal' in result['svg']
 x.update(family='evidence-gates',status='conceptual',panels=[],nodes=[{'id':'a','label':'Independent review','detail':'Awaiting reviewer','blockers':['Missing field observations']}])
 assert render(FigureSpec.model_validate(x))['table']['rows'][0][4]=='unreviewed'
 x['nodes'][0].update(disposition='positive',reviewer_ref='human-review:1')
 with pytest.raises(ValidationError):FigureSpec.model_validate(x)
