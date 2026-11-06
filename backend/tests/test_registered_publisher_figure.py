import json
from pathlib import Path
import pytest
from fastapi import HTTPException
from app import registered_publisher_figure as integration

def test_registered_source_validates_core_and_original_library_bytes(monkeypatch):
 for name,value in [('CORE_URL','http://core.test'),('LIBRARY_URL','http://library.test'),('CORE_KEY','synthetic-key'),('LIBRARY_KEY','synthetic-key')]:
  monkeypatch.setenv('SC_LAB_SCIENTIFIC_'+name,value)
 sha=integration.PDF_SHA256
 component={'id':1,'component_key':'dataset-v1','component_kind':'dataset','content':{'publisherArtifactId':'artifact:sha256:'+sha,'publisherSha256':sha}}
 pdf=(Path(integration.__file__).parent/'publisher_sources/epa-report-136.pdf').read_bytes()
 def fetch(url,headers,limit):
  return json.dumps({'components':[component]}).encode() if url.startswith('http://core.test') else pdf
 monkeypatch.setattr(integration,'fetch',fetch)
 body=integration.RegisteredPublisher(coreProjectId='test-project',datasetVersionKey='dataset-v1')
 result=integration.registered_figure(body)
 assert result['source_verification']['core_registered'] is True
 assert result['scientificContext']['source']['core_binding']['componentId']==1
 assert result['source_verification']['human_extraction_review'] is False
 component['content']['publisherSha256']='0'*64
 with pytest.raises(HTTPException) as e:integration.registered_figure(body)
 assert e.value.status_code==409

def test_grassland_column_is_distinct_and_source_correct():
 from app.publisher_soil_carbon import ingest_pdf
 pdf=(Path(integration.__file__).parent/'publisher_sources/epa-report-136.pdf').read_bytes()
 result=ingest_pdf(pdf,land_use_group='grassland')
 assert result['axisLabels']['x']==['Grassland','Arable lands']
 assert [(c['z'],c['standardError']) for c in result['cells'][::2]]==[(50.9,.6),(121.5,1.7),(160.6,2.8),(194.9,4.7)]
 assert result['scientificContext']['source']['land_use_group']=='grassland'
