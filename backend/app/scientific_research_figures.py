"""SC-RVF typed scientific figures in the existing Lab Figure Composer.

Canonical objects stay structured; rendering never pools endpoints or executes
conceptual processes. Source verification is declared separately from rendering.
"""
from __future__ import annotations
import hashlib,json,math,textwrap
from html import escape
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field,model_validator
from .security import require_compute_auth
from .visual_research_narrative_figure_composer_v01180 import normalize_figure_reference
SCHEMA='sc-lab-source-bound-scientific-figure/1.0'
RENDERER='sc-lab-figure-composer-scientific/1.1'
class Strict(BaseModel):model_config=ConfigDict(extra='forbid',allow_inf_nan=False,strict=True)
class Source(Strict):
 id:str=Field(min_length=1,max_length=160)
 citation:str=Field(min_length=1,max_length=1000)
 uri:str=Field(pattern=r'^https://[^\s]+$',max_length=2000)
 sha256:str=Field(pattern=r'^[a-f0-9]{64}$')
 source_kind:Literal['literature-derived','official-observed','modeled','simulation','user-entered','conceptual','field-observed','unquantified']
 locator:str=Field(min_length=1,max_length=300)
 review:Literal['pending','human-reviewed']
 review_ref:str|None=Field(default=None,max_length=300)
 rights_ref:str=Field(min_length=1,max_length=1000)
 crs:str|None=Field(default=None,max_length=80)
 scale_denominator:int|None=Field(default=None,ge=1)
 data_version:str|None=Field(default=None,max_length=160)
 @model_validator(mode='after')
 def review_support(self):
  if self.review=='human-reviewed' and not self.review_ref:raise ValueError('Human review requires a review record reference.')
  return self
class Panel(Strict):
 label:str=Field(min_length=1,max_length=160)
 source_id:str
 material:str=Field(min_length=1,max_length=160)
 time_window:str=Field(min_length=1,max_length=160)
 denominator:str=Field(min_length=1,max_length=240)
 endpoint:Literal['potential','gross-estimate','qualitative-response','transport-fraction']
 value:float|None=None
 value_qualifier:Literal['estimate','up-to']='estimate'
 lower:float|None=None
 upper:float|None=None
 plus_minus:float|None=Field(default=None,ge=0)
 uncertainty_type:str=Field(min_length=1,max_length=120)
 unit:str=Field(min_length=1,max_length=100)
 finding:str=Field(min_length=1,max_length=700)
 @model_validator(mode='after')
 def ranges(self):
  if self.endpoint=='qualitative-response':
   if any(x is not None for x in (self.value,self.lower,self.upper,self.plus_minus)):raise ValueError('Qualitative/null evidence cannot be encoded as a numeric zero.')
  elif self.value is None and (self.lower is None or self.upper is None):raise ValueError('A numerical panel requires a value or explicit bounds.')
  if (self.lower is None)!=(self.upper is None) or (self.lower is not None and self.lower>self.upper):raise ValueError('Invalid reported interval.')
  if self.plus_minus is not None and (self.value is None or self.lower is not None):raise ValueError('Declare reported +/- or bounds, without guessing an interval conversion.')
  if self.endpoint=='transport-fraction' and (self.unit!='%' or any(x is not None and not 0<=x<=100 for x in (self.value,self.lower,self.upper))):raise ValueError('Transport fractions require explicit percent bounds.')
  return self
class Node(Strict):
 id:str=Field(pattern=r'^[A-Za-z0-9_-]{1,60}$')
 label:str=Field(min_length=1,max_length=140)
 detail:str=Field(min_length=1,max_length=600)
 source_ids:list[str]=Field(default_factory=list,max_length=20)
 blockers:list[str]=Field(default_factory=list,max_length=20)
 disposition:Literal['unreviewed','positive','null','adverse','inconclusive']='unreviewed'
 reviewer_ref:str|None=Field(default=None,max_length=300)
 @model_validator(mode='after')
 def decision(self):
  if self.disposition!='unreviewed' and not self.reviewer_ref:raise ValueError('A human disposition requires its independent review reference.')
  if self.disposition=='positive' and self.blockers:raise ValueError('Unresolved blockers prevent a positive gate.')
  return self
class Edge(Strict):
 source:str
 target:str
 label:str=Field(min_length=1,max_length=160)
class ProtocolRow(Strict):
 domain:str=Field(min_length=1,max_length=100)
 measurements:str=Field(min_length=1,max_length=700)
 frequency:str=Field(min_length=1,max_length=200)
 responsible_authority:str=Field(min_length=1,max_length=200)
 reference_methods:str=Field(min_length=1,max_length=400)
 missing_data_rule:str=Field(min_length=1,max_length=400)
 protective_stop_rule:str=Field(min_length=1,max_length=400)
 reporting_status:Literal['proposed','approved','in-progress','complete','stopped']
class FigureSpec(Strict):
 title:str=Field(min_length=1,max_length=160)
 description:str=Field(min_length=1,max_length=1000)
 project_id:str=Field(min_length=1,max_length=160)
 revision:int=Field(ge=1)
 family:Literal['evidence-comparison','denominator-ranges','attribution-process','screening-workflow','evidence-gates','protocol-matrix']
 status:Literal['conceptual','literature-derived','simulation','unquantified']
 sources:list[Source]=Field(min_length=1,max_length=20)
 panels:list[Panel]=Field(default_factory=list,max_length=12)
 nodes:list[Node]=Field(default_factory=list,max_length=12)
 edges:list[Edge]=Field(default_factory=list,max_length=24)
 protocol:list[ProtocolRow]=Field(default_factory=list,max_length=20)
 limitations:list[str]=Field(min_length=1,max_length=20)
 @model_validator(mode='after')
 def integrity(self):
  source_ids=[s.id for s in self.sources]
  if len(source_ids)!=len(set(source_ids)):raise ValueError('Source IDs must be unique.')
  refs={p.source_id for p in self.panels}|{r for n in self.nodes for r in n.source_ids}
  if refs-set(source_ids):raise ValueError('Unresolved scientific source binding.')
  if self.family in {'evidence-comparison','denominator-ranges'}:
   if not self.panels or self.nodes or self.edges or self.protocol:raise ValueError('Comparison figures require only separate source-bound panels.')
   if len({p.label for p in self.panels})!=len(self.panels):raise ValueError('Panel identities must be unique.')
   if self.family=='denominator-ranges' and any(p.endpoint!='transport-fraction' for p in self.panels):raise ValueError('Range comparison requires separately declared transport fractions.')
  elif self.family=='protocol-matrix':
   if not self.protocol or self.panels or self.nodes or self.edges:raise ValueError('Protocol figure requires a measurement matrix.')
  else:
   if not self.nodes or self.panels or self.protocol:raise ValueError('Semantic scientific workflow requires nodes and edges.')
   ids=[n.id for n in self.nodes]
   if len(ids)!=len(set(ids)) or any(e.source not in ids or e.target not in ids for e in self.edges):raise ValueError('Invalid semantic graph identity.')
   if self.family in {'attribution-process','screening-workflow'} and self.status!='conceptual':raise ValueError('A declared analytical or screening workflow is conceptual, not an executed or mapped result.')
  return self

def stable(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def fingerprint(obj):return hashlib.sha256(stable(obj)).hexdigest()
def tabular(spec):
 if spec.panels:
  columns=['Panel','Material','Window','Denominator','Endpoint','Value','Lower','Upper','Reported +/-','Uncertainty','Unit','Finding','Source','Qualifier']
  rows=[[p.label,p.material,p.time_window,p.denominator,p.endpoint,p.value,p.lower,p.upper,p.plus_minus,p.uncertainty_type,p.unit,p.finding,p.source_id,p.value_qualifier] for p in spec.panels]
 elif spec.protocol:
  columns=['Domain','Measurements','Frequency','Authority','Methods','Missing data','Stop rule','Status']
  rows=[[r.domain,r.measurements,r.frequency,r.responsible_authority,r.reference_methods,r.missing_data_rule,r.protective_stop_rule,r.reporting_status] for r in spec.protocol]
 else:
  columns=['Node','Detail','Sources','Blockers','Disposition','Reviewer']
  rows=[[n.label,n.detail,'; '.join(n.source_ids),'; '.join(n.blockers),n.disposition,n.reviewer_ref] for n in spec.nodes]
 return {'columns':columns,'rows':rows}

def render(spec:FigureSpec):
 # Layout only: no numeric aggregation, denominator conversion, or claim promotion.
 blocks=[]
 if spec.panels:
  for p in spec.panels:
   number='Qualitative finding'
   if p.value is not None:number=('Up to ' if p.value_qualifier=='up-to' else '')+f'{p.value:g}'+(f' +/- {p.plus_minus:g}' if p.plus_minus is not None else '')+' '+p.unit
   elif p.lower is not None:number=f'{p.lower:g} to {p.upper:g} '+p.unit
   blocks.append((p.label,[number,p.endpoint+'; '+p.uncertainty_type,p.material+'; '+p.time_window,'Denominator: '+p.denominator,p.finding,'Source: '+p.source_id]))
 elif spec.protocol:
  for p in spec.protocol:blocks.append((p.domain,[p.measurements,'Frequency: '+p.frequency,'Authority: '+p.responsible_authority,'Methods: '+p.reference_methods,'Missing data: '+p.missing_data_rule,'Stop rule: '+p.protective_stop_rule,'Status: '+p.reporting_status]))
 else:
  for n in spec.nodes:
   outgoing=[e.label+' -> '+e.target for e in spec.edges if e.source==n.id]
   blocks.append((n.id+'  '+n.label,[n.detail,'Disposition: '+n.disposition,*(['Blockers: '+'; '.join(n.blockers)] if n.blockers else []),*outgoing]))
 body=[];positions={}
 columns=min(3,len(blocks)) if spec.panels else 2
 gap=18;width=(812-gap*(columns-1))/columns
 rows=(len(blocks)+columns-1)//columns
 card_height=360 if spec.panels else (230 if spec.protocol else 190)
 def text(x,y,words,size=16,bold=False):
  return f'<text x="{x:g}" y="{y:g}" font-family="Helvetica" font-size="{size}"'+(' font-weight="bold"' if bold else '')+'>'+escape(words)+'</text>'
 for index,(label,full_lines) in enumerate(blocks):
  x=24+(index%columns)*(width+gap);y=100+(index//columns)*(card_height+gap)
  positions[label.split('  ',1)[0]]=(x,y,width,card_height)
  body.append(f'<g tabindex="0"><title>{escape(label+": "+" | ".join(full_lines))}</title><rect x="{x:g}" y="{y:g}" width="{width:g}" height="{card_height}" rx="4" fill="#f2f6f8" stroke="#546a78"/>')
  char_width=max(22,int((width-24)/9))
  title_lines=textwrap.wrap(label,char_width)[:2]
  for line_no,line in enumerate(title_lines):body.append(text(x+12,y+25+line_no*21,line,18,True))
  cursor=y+76 if spec.panels else y+66
  if spec.panels:
   panel=spec.panels[index]
   display=[full_lines[0],'Denominator: '+panel.denominator,panel.finding,'Source: '+panel.source_id]
   for line_no,line in enumerate(display):
    wrapped=textwrap.wrap(line,char_width)
    maximum=[1,4,6,1][line_no]
    if len(wrapped)>maximum:wrapped=wrapped[:maximum];wrapped[-1]=wrapped[-1].rstrip('.')+'...'
    for part in wrapped:body.append(text(x+12,cursor,part,21 if line_no==0 else 18,line_no==0));cursor+=20
   if panel.endpoint!='qualitative-response':
    lo=panel.lower if panel.lower is not None else panel.value-(panel.plus_minus or 0)
    hi=panel.upper if panel.upper is not None else panel.value+(panel.plus_minus or 0)
    start=min(0,lo);end=max(hi,1e-9)*1.1
    def px(value):return x+24+(width-48)*(value-start)/(end-start)
    ay=y+card_height-34
    body.append(f'<line x1="{x+24:g}" y1="{ay:g}" x2="{x+width-24:g}" y2="{ay:g}" stroke="#82919b"/>')
    body.append(f'<line x1="{px(lo):.4f}" y1="{ay:g}" x2="{px(hi):.4f}" y2="{ay:g}" stroke="#176c62" stroke-width="7"/>')
    if panel.value is not None:body.append(f'<circle cx="{px(panel.value):.4f}" cy="{ay:g}" r="5" fill="#111111"/>')
    body.extend([text(x+18,ay+22,f'{start:g}',12),text(x+width-112,ay+22,f'{end:g} {panel.unit}',12)])
  else:
   item=spec.protocol[index] if spec.protocol else spec.nodes[index]
   if spec.protocol:
    display=[item.measurements,'Frequency: '+item.frequency,'Status: '+item.reporting_status,'Stop rules: '+item.protective_stop_rule]
   else:
    display=[item.detail,'Disposition: '+item.disposition]
   for line_no,line in enumerate(display):
    maximum=4 if line_no==0 else 1
    wrapped=textwrap.wrap(line,char_width)
    if len(wrapped)>maximum:wrapped=wrapped[:maximum];wrapped[-1]=wrapped[-1].rstrip('.')+'...'
    for part in wrapped:body.append(text(x+12,cursor,part,18));cursor+=21
  body.append('</g>')
 for edge in spec.edges:
  ax,ay,aw,ah=positions[edge.source];bx,by,bw,bh=positions[edge.target]
  if ay==by:
   x1=ax+aw;x2=bx;yy=ay+ah/2
   if x1<x2:body.append(f'<line x1="{x1:g}" y1="{yy:g}" x2="{x2:g}" y2="{yy:g}" stroke="#546a78"/><polygon points="{x2:g},{yy:g} {x2-7:g},{yy-4:g} {x2-7:g},{yy+4:g}" fill="#546a78"/>')
  else:
   # Source/target identities also remain in the accessible structured graph.
   body.append(text(ax+12,ay+ah-10,'Next: '+edge.target,12))
 y=100+rows*(card_height+gap)
 for panel in spec.panels:
  for line in textwrap.wrap(panel.label+': '+panel.material+'; '+panel.time_window+'; '+panel.uncertainty_type,112):body.append(text(24,y+16,line,12));y+=17
 for note in ['Status: '+spec.status+'. Net removal: NOT_QUANTIFIED. No certification is asserted.',*spec.limitations]:
  for line in textwrap.wrap(note,112):body.append(text(24,y+16,line,12));y+=17
 y+=8
 for source in spec.sources:
  for line in textwrap.wrap('Source '+source.id+' | '+source.uri+' | extraction review: '+source.review,112):body.append(text(24,y+16,line,12));y+=17
 height=y+24
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="860" height="{height}" viewBox="0 0 860 {height}" role="img"><title>{escape(spec.title)}</title><desc>{escape(spec.description)}</desc><rect width="860" height="{height}" fill="white"/>'+text(24,32,spec.title,20,True)
 for i,line in enumerate(textwrap.wrap(spec.description,110)[:2]):svg+=text(24,58+17*i,line,12)
 svg+=''.join(body)+'</svg>'
 raw=spec.model_dump();sh=fingerprint(raw)
 ref=normalize_figure_reference({'figure_ref':'urn:sha256:'+sh,'figure_kind':'small-multiples' if spec.panels else ('table' if spec.protocol else 'diagram'),'title':spec.title,'caption':spec.description,'source_refs':[s.uri for s in spec.sources],'provenance':{'scientific_spec_sha256':sh,'renderer_version':RENDERER,'status':spec.status}})
 return {'schema':SCHEMA,'title':spec.title,'description':spec.description,'spec':raw,'figure_reference':ref,'spec_sha256':sh,'renderer_version':RENDERER,'svg':svg,'svg_sha256':hashlib.sha256(svg.encode()).hexdigest(),'table':tabular(spec),'net_removal_status':'NOT_QUANTIFIED','scientific_verification_performed':False}
router=APIRouter(prefix='/v1/visual-research-narrative-figure-composer',tags=['scientific-research-figures'])
@router.post('/scientific-figure/render',dependencies=[Depends(require_compute_auth)])
def render_route(spec:FigureSpec):return render(spec)
