"""Resolve registered publisher bytes; Library storage and Core identity stay authoritative."""
import hashlib,json,os
from urllib.request import Request,build_opener,HTTPRedirectHandler,ProxyHandler
from urllib.error import URLError,HTTPError
from urllib.parse import quote
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from .security import require_compute_auth
from .publisher_soil_carbon import ingest_pdf,PDF_SHA256

router=APIRouter(tags=['registered-publisher-figures'])
class RegisteredPublisher(BaseModel):
    model_config=ConfigDict(extra='forbid')
    coreProjectId:str=Field(min_length=1,max_length=160)
    datasetVersionKey:str=Field(min_length=1,max_length=180)

def fetch(url,headers,limit):
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):return None
    try:
        with build_opener(ProxyHandler({}),NoRedirect()).open(Request(url,headers=headers),timeout=20) as response:
            # A configured service must not redirect credentials elsewhere.
            if response.url!=url:raise HTTPException(502,'Scientific source redirect rejected.')
            raw=response.read(limit+1)
            if len(raw)>limit:raise HTTPException(413,'Scientific source exceeds limit.')
            return raw
    except (URLError,HTTPError) as exc:raise HTTPException(502,'Registered scientific source unavailable.') from exc

@router.post('/v1/visualization/registered-publisher-figure',dependencies=[Depends(require_compute_auth)])
def registered_figure(body:RegisteredPublisher):
    core=os.getenv('SC_LAB_SCIENTIFIC_CORE_URL','').rstrip('/')
    library=os.getenv('SC_LAB_SCIENTIFIC_LIBRARY_URL','').rstrip('/')
    ck=os.getenv('SC_LAB_SCIENTIFIC_CORE_KEY','');lk=os.getenv('SC_LAB_SCIENTIFIC_LIBRARY_KEY','')
    if not all((core,library,ck,lk)):raise HTTPException(503,'Scientific source integration is not configured.')
    try:
        bundle=json.loads(fetch(core+'/v1/research/projects/'+quote(body.coreProjectId,safe='')+'/bundle',{'X-SC-API-Key':ck},2_000_000))
        components=[c for c in bundle['components'] if c['component_key']==body.datasetVersionKey and c['component_kind']=='dataset']
        if len(components)!=1:raise HTTPException(404,'Registered dataset version was not found.')
        component=components[0];content=component['content']
        artifact='artifact:sha256:'+PDF_SHA256
        if content.get('publisherArtifactId')!=artifact or content.get('publisherSha256')!=PDF_SHA256:
            raise HTTPException(409,'Registered publisher source hash mismatch.')
        raw=fetch(library+'/v1/admin/artifacts/'+quote(artifact,safe='')+'/content',{'Authorization':'Bearer '+lk},5_000_000)
        if hashlib.sha256(raw).hexdigest()!=PDF_SHA256:raise HTTPException(409,'Publisher bytes failed SHA256 verification.')
        group=content.get('landUseGroup','grassland-and-rough-grazing')
        if group not in {'grassland','grassland-and-rough-grazing'}:
            raise HTTPException(409,'Registered EPA land-use column is unsupported.')
        spec=ingest_pdf(raw,land_use_group=group)
        spec['scientificContext']['source']['library_binding']={'publisherArtifactId':artifact}
        spec['scientificContext']['source']['core_binding']={'projectId':body.coreProjectId,'datasetVersionKey':body.datasetVersionKey,'componentId':component['id']}
        spec['source_verification'].update(library_registered=True,core_registered=True)
        return spec
    except (KeyError,TypeError,ValueError) as exc:raise HTTPException(422,'Malformed registered scientific source.') from exc
