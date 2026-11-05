"""EPA 136 ingestion into the existing Lab numeric figure grammar.

Checks the publisher PDF bytes, not the scientific truth or human review. The
national published estimates must never be labeled as field observations/CDR.
"""
from pathlib import Path
import hashlib

PDF_SHA256 = '9cc7ef390d6b19bd4d1a89d3b1d9c9d8c1c81e1adf8e40b6c4267d4fb93ae27a'
VALUES = [(52.2,.6,29.9,1.6), (127.1,1.7,81.3,4.5),
          (170.9,2.7,117.6,7.2), (213.8,4.5,167.5,12.2)]
GRASSLAND_VALUES = [(50.9,.6,29.9,1.6),(121.5,1.7,81.3,4.5),
                    (160.6,2.8,117.6,7.2),(194.9,4.7,167.5,12.2)]
CITATION = ('Khalil, M.I. (2014) Development of Methodologies and Modelling for Accounting '
            'Greenhouse Gases and Organic Carbon Stocks in Agricultural Soils of Ireland. '
            'EPA Research Report 136. Environmental Protection Agency, Ireland, Table 2.4, p. 19. Catalog lists 2015.')


def ingest_pdf(raw, land_use_group='grassland-and-rough-grazing'):
    from .visualization import build_spec, VisualizationInputError
    if not isinstance(raw, bytes) or len(raw) > 5_000_000 or hashlib.sha256(raw).hexdigest() != PDF_SHA256:
        raise VisualizationInputError('EPA Report 136 publisher PDF SHA256 mismatch; re-review source revisions before import.')
    if land_use_group not in {'grassland','grassland-and-rough-grazing'}:
        raise VisualizationInputError('Unknown EPA Table 2.4 land-use column.')
    values = GRASSLAND_VALUES if land_use_group == 'grassland' else VALUES
    spec = build_spec({'method':'published-epa-136-table-2.4', 'outputs':{
        'xValues':[0,1], 'yValues':[0,1,2,3], 'zMatrix':[[g,a] for g,_,a,_ in values]},
        'visualization':{'type':'heatmap','title':'National non-peat soil organic carbon',
            'description':'Published model-based stock estimates; not measured Wexford removal.',
            'xLabel':'Land use','yLabel':'Cumulative depth (cm)'}})
    spec['axisLabels'] = {'x':['Grassland' if land_use_group == 'grassland' else 'Grassland + rough grazing','Arable lands'], 'y':['0-10','0-30','0-50','0-100']}
    for yi, (_,gs,_,ase) in enumerate(values):
        spec['cells'][yi*2]['standardError'] = gs
        spec['cells'][yi*2+1]['standardError'] = ase
    spec['scientificContext'] = {'unit':'t C/ha','uncertainty_kind':'SE','depth_semantics':'cumulative',
        'status':'published-model-estimate',
        'warning':'Cumulative depths overlap; do not sum. SOC stock is not an ERW removal estimate.',
        'source':{'publisher':'Environmental Protection Agency, Ireland','author':'Khalil, M.I.',
            'report_number':136,'isbn':'978-1-84095-558-3','pdf_copyright_year':2014,'catalog_year':2015,
            'citation':CITATION,'url':'https://www.epa.ie/publications/research/reports/30217-Research-Report-136-Web.pdf',
            'sha256':PDF_SHA256,'table':'2.4','printed_page':19,'pdf_page':26,
            'extraction_review':{'method':'manual transcription checked against PDF text and rendered page by Codex',
                'human_review':'pending','checked_on':'2026-11-04'},
            'rights':'PDF p. ii permits reproduction with source acknowledgment.',
            'library_binding':None,'core_binding':None}}
    spec['publication'] = {'caption':spec['scientificContext']['warning'], 'source':CITATION, 'showGrid':False}
    spec['interaction'] = {'zoom':False,'pan':False,'crosshair':False,'tooltip':True}
    # Native CSV/tabular fallback keeps categorical labels and reported errors.
    spec['table'] = {'columns':[{'key':k,'label':v} for k,v in [
        ('land_use','Land use'),('depth','Cumulative depth (cm)'),('value','SOC (t C/ha)'),('se','SE (t C/ha)')]],
        'rows':[{'land_use':spec['axisLabels']['x'][c['xIndex']],
            'depth':spec['axisLabels']['y'][c['yIndex']], 'value':c['z'],'se':c['standardError']} for c in spec['cells']],
        'truncated':False,'rowCount':8}
    spec['source_verification'] = {'publisher_pdf_bytes_match':True,'human_extraction_review':False,
        'library_registered':False,'core_registered':False,'net_removal_status':'NOT_QUANTIFIED'}
    if land_use_group == 'grassland':
        spec['scientificContext']['source']['land_use_group'] = land_use_group
    return spec


def ingest_request(request):
    from .visualization import VisualizationInputError
    if (not isinstance(request, dict) or set(request) != {'id','pdf_sha256'}
            or request['id'] != 'epa-136-table-2.4' or request['pdf_sha256'] != PDF_SHA256):
        raise VisualizationInputError('Unsupported publisher source or pinned source hash.')
    # Resolve an allowlisted packaged source, never a caller-provided URL/path.
    try:
        raw = (Path(__file__).parent/'publisher_sources/epa-report-136.pdf').read_bytes()
    except OSError as exc:
        raise VisualizationInputError('Pinned publisher source unavailable; import rejected.') from exc
    return ingest_pdf(raw)
