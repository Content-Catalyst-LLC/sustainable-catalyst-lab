"""Authenticated proposed-study adapter over Lab's existing design engine."""
from __future__ import annotations
from collections import Counter,defaultdict
import hashlib,json
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field,model_validator
from typing import Literal
from .experimental_design_power_analysis_v01280 import blocked_randomization_plan,randomization_schedule
from .security import require_compute_auth
class Strict(BaseModel):model_config=ConfigDict(extra='forbid',strict=True,allow_inf_nan=False)
class Unit(Strict):
 id:str=Field(min_length=1,max_length=160)
 block:str=Field(min_length=1,max_length=160)
 management_ref:str|None=Field(default=None,max_length=300)
 baseline_ref:str|None=Field(default=None,max_length=300)
class StudyPlan(Strict):
 project_id:str=Field(min_length=1,max_length=160)
 title:str=Field(min_length=1,max_length=300)
 source_kind:Literal['simulation','conceptual']
 source_refs:list[str]=Field(min_length=1,max_length=100)
 seed:int=Field(ge=0,le=2**32-1)
 units:list[Unit]=Field(min_length=4,max_length=2000)
 groups:list[str]=Field(min_length=2,max_length=16)
 untreated_control:str=Field(min_length=1,max_length=160)
 primary_outcome:str=Field(min_length=1,max_length=1000)
 observation_windows:list[str]=Field(min_length=2,max_length=30)
 sampling_protocol_ref:str=Field(min_length=1,max_length=300)
 @model_validator(mode='after')
 def design(self):
  if len(set(u.id for u in self.units))!=len(self.units):raise ValueError('Experimental unit identities must be unique.')
  if len(set(self.groups))!=len(self.groups) or any(not g.strip() or len(g)>160 for g in self.groups):raise ValueError('Groups require distinct non-empty labels.')
  if self.untreated_control not in self.groups:raise ValueError('An explicit untreated control is required.')
  counts=Counter(u.block for u in self.units)
  if len(counts)<2:raise ValueError('This blocked adapter requires at least two experimental blocks.')
  if any(n%len(self.groups) for n in counts.values()):raise ValueError('Each completed block must support equal group allocation.')
  if len(set(self.observation_windows))!=len(self.observation_windows) or any(not w.strip() for w in self.observation_windows):raise ValueError('Declare distinct baseline and follow-up windows.')
  return self

def build_plan(recipe:StudyPlan):
 blocks=defaultdict(list)
 for unit in recipe.units:blocks[unit.block].append(unit)
 assignments=[];block_plans=[];block_seeds={}
 for block,units in sorted(blocks.items()):
  # Stable ordering makes source-list reorderings immaterial to allocation.
  units=sorted(units,key=lambda unit:unit.id)
  seed=int.from_bytes(hashlib.sha256(json.dumps([recipe.seed,block],separators=(',',':')).encode()).digest()[:4],'big')
  block_seeds[block]=seed
  native=blocked_randomization_plan({'groups':recipe.groups,'block_size':len(units),'blocks':1})
  schedule=randomization_schedule({'groups':recipe.groups,'n':len(units),'seed':seed})
  block_plans.append({'block':block,'native_plan':native,'schedule_hash':schedule['schedule_hash']})
  for unit,group in zip(units,schedule['assignments']):assignments.append({**unit.model_dump(),'group':group})
 result={'schema':'sc-lab-proposed-scientific-study/1.0','engine_version':'sc-lab-experimental-design-power-analysis/0.128.0','recipe':recipe.model_dump(),'assignments':assignments,'blocks':block_plans,'block_seeds':block_seeds,
  'status':'PROPOSED_SYNTHETIC_PLAN' if recipe.source_kind=='simulation' else 'PROPOSED_CONCEPTUAL_PLAN','human_review':'pending','preregistered':False,'field_execution_authorized':False,'field_observations_present':False,'coordinates_assumed':False,'allocation_concealment_guaranteed':False,'causal_attribution_established':False,'net_removal':'NOT_QUANTIFIED',
  'blockers':['Permissioned site and experimental-unit geometry have not been supplied.','Baseline measurements, management history, calibration and hydrological comparability require review.','Sampling frequency, safety thresholds and missing-data rules require a reviewed protocol.','Randomization is a proposed schedule; no independent approval or pre-result freeze is recorded.']}
 result['plan_sha256']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
 return result
router=APIRouter(prefix='/v1/scientific-study',tags=['scientific-study'])
@router.post('/plan',dependencies=[Depends(require_compute_auth)])
def plan(recipe:StudyPlan):return build_plan(recipe)
