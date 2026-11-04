import base64
import hashlib
from pathlib import Path
import os
import pytest
from app.publisher_soil_carbon import ingest_pdf, ingest_request, PDF_SHA256
from app.visualization import build_spec, VisualizationInputError, csv_text

@pytest.mark.parametrize('raw',[b'',b'%PDF corrupt',b'wrong source',None])
def test_changed_publisher_source_is_rejected(raw):
    with pytest.raises(VisualizationInputError): ingest_pdf(raw)

@pytest.mark.parametrize('payload',[{}, {'id':'unknown','pdf_base64':''}, {'id':'epa-136-table-2.4','pdf_base64':'@@@'}])
def test_invalid_request_fails(payload):
    with pytest.raises(VisualizationInputError): ingest_request(payload)


def test_publisher_values_cannot_be_overridden():
    with pytest.raises(VisualizationInputError): build_spec({'publisherSource':{},'outputs':{'zMatrix':[[999]]}})


def test_real_publisher_pdf_to_native_lab_spec():
    path = os.environ.get('SC_RVF_EPA_PDF', str(Path(__file__).parents[1]/'app/publisher_sources/epa-report-136.pdf'))
    raw = Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PDF_SHA256
    spec = build_spec({'publisherSource':{'id':'epa-136-table-2.4','pdf_sha256':PDF_SHA256}})
    assert spec['schema'] == 'sc-lab-scientific-visualization/1.0'
    assert [(c['z'],c['standardError']) for c in spec['cells']] == [(52.2,.6),(29.9,1.6),(127.1,1.7),(81.3,4.5),(170.9,2.7),(117.6,7.2),(213.8,4.5),(167.5,12.2)]
    assert 'Grassland + rough grazing' in csv_text(spec)
    assert spec['source_verification']['net_removal_status'] == 'NOT_QUANTIFIED'
    assert not spec['source_verification']['core_registered']


def test_existing_api_requires_auth_and_imports_with_valid_key(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    from app import security
    from dataclasses import replace
    monkeypatch.setattr(security, 'settings', replace(security.settings, signing_secret='', api_key='isolated-publisher-test-key'))
    raw = (Path(__file__).parents[1]/'app/publisher_sources/epa-report-136.pdf').read_bytes()
    payload = {'publisherSource':{'id':'epa-136-table-2.4','pdf_sha256':PDF_SHA256}}
    with TestClient(app) as client:
        assert client.post('/v1/visualization/spec', json=payload).status_code == 401
        response = client.post('/v1/visualization/spec',json=payload,headers={'X-SC-Lab-Key':'isolated-publisher-test-key'})
        assert response.status_code == 200, response.text
        assert response.json()['source_verification']['publisher_pdf_bytes_match'] is True
        assert response.json()['source_verification']['human_extraction_review'] is False
        assert response.json()['scientificContext']['source']['core_binding'] is None
