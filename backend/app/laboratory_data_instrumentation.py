from __future__ import annotations
import hashlib,json,math,statistics,secrets
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
VERSION="0.25.0"
CONTRACT_PATH=Path(__file__).resolve().parents[1]/"contracts"/"laboratory-data-instrumentation-v0250.json"
class InstrumentationError(ValueError):pass
def catalog():return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
def _f(v,n):
 try:x=float(v)
 except (TypeError,ValueError) as e:raise InstrumentationError(f"{n} must be numerical.") from e
 if not math.isfinite(x):raise InstrumentationError(f"{n} must be finite.")
 return x
def _p(v,n):
 x=_f(v,n)
 if x<=0:raise InstrumentationError(f"{n} must be greater than zero.")
 return x
def _a(v,n,minn=1):
 if not isinstance(v,list):raise InstrumentationError(f"{n} must be an array.")
 x=[_f(z,f"{n}[{i}]") for i,z in enumerate(v)]
 if len(x)<minn:raise InstrumentationError(f"{n} requires at least {minn} values.")
 return x
def execute(method_id:str,inputs:dict[str,Any]):
 defs={m['id']:m for m in catalog()['methods']}
 if method_id not in defs:raise InstrumentationError(f"Unknown instrumentation method: {method_id}")
 m=defs[method_id];op=m['operation'];i=inputs or {};p=lambda k:_f(i.get(k),k);pos=lambda k:_p(i.get(k),k);x=_a(i.get('values'),'values') if 'values' in i else []
 if op=='sample_rate_from_interval':r=1/pos('intervalSeconds')
 elif op=='sample_interval_ms':r=1000/pos('sampleRateHz')
 elif op=='sample_count':r=round(p('durationSeconds')*pos('sampleRateHz'))
 elif op=='acquisition_duration':r=p('sampleCount')/pos('sampleRateHz')
 elif op=='data_throughput':r=p('sampleRateHz')*p('channelCount')*p('bytesPerSample')
 elif op=='storage_size':r=p('durationSeconds')*p('throughputBytesPerSecond')/1e6
 elif op=='adc_levels':r=2**int(pos('bits'))
 elif op=='quantization_step':r=pos('inputRange')/(2**int(pos('bits'))-1)
 elif op=='two_point_gain':r=(p('referenceHigh')-p('referenceLow'))/(p('rawHigh')-p('rawLow'))
 elif op=='two_point_offset':r=p('referenceLow')-p('gain')*p('rawLow')
 elif op=='apply_calibration':r=p('gain')*p('rawValue')+p('offset')
 elif op=='inverse_calibration':r=(p('calibratedValue')-p('offset'))/p('gain')
 elif op=='absolute_error':r=abs(p('measured')-p('reference'))
 elif op=='percent_error':r=abs(p('measured')-p('reference'))/abs(p('reference'))*100
 elif op=='drift_rate':r=(p('finalValue')-p('initialValue'))/pos('elapsedHours')
 elif op=='calibration_due_days':r=p('intervalDays')-p('daysSinceCalibration')
 elif op=='mean':r=statistics.mean(x)
 elif op=='median':r=statistics.median(x)
 elif op=='sd':r=statistics.stdev(x)
 elif op=='cv':r=statistics.stdev(x)/abs(statistics.mean(x))*100
 elif op=='minimum':r=min(x)
 elif op=='maximum':r=max(x)
 elif op=='range':r=max(x)-min(x)
 elif op=='rms':r=math.sqrt(sum(v*v for v in x)/len(x))
 elif op=='moving_average_latest':
  w=int(pos('windowSize'))
  if w>len(x):raise InstrumentationError('windowSize cannot exceed sample count.')
  r=statistics.mean(x[-w:])
 elif op=='smoothing_alpha':r=p('sampleIntervalSeconds')/(pos('timeConstantSeconds')+p('sampleIntervalSeconds'))
 elif op=='linear_interpolation':r=p('y0')+(p('x')-p('x0'))*(p('y1')-p('y0'))/(p('x1')-p('x0'))
 elif op=='trapezoid_area':r=(p('x1')-p('x0'))*(p('y0')+p('y1'))/2
 elif op=='finite_difference':r=(p('y1')-p('y0'))/(p('x1')-p('x0'))
 elif op=='baseline_corrected':r=p('value')-p('baseline')
 elif op=='c_to_f':r=p('celsius')*9/5+32
 elif op=='f_to_c':r=(p('fahrenheit')-32)*5/9
 elif op=='c_to_k':r=p('celsius')+273.15
 elif op=='k_to_c':r=p('kelvin')-273.15
 elif op=='pa_to_kpa':r=p('pascal')/1000
 elif op=='ml_to_l':r=p('milliliter')/1000
 elif op=='mg_to_g':r=p('milligram')/1000
 elif op=='ug_to_mg':r=p('microgram')/1000
 elif op=='elapsed_seconds':r=p('endEpochSeconds')-p('startEpochSeconds')
 elif op=='timezone_adjusted_epoch':r=p('epochSeconds')+p('offsetMinutes')*60
 elif op=='events_per_hour':r=p('eventCount')*3600/pos('durationSeconds')
 elif op=='schedule_progress':r=p('elapsedSeconds')/pos('plannedSeconds')*100
 elif op=='missing_percent':r=p('missingCount')/pos('totalCount')*100
 elif op=='duplicate_percent':r=p('duplicateCount')/pos('totalCount')*100
 elif op=='out_of_range_percent':r=p('outOfRangeCount')/pos('totalCount')*100
 elif op=='data_quality_index':r=max(0,min(100,100-2*p('missingPercent')-1.5*p('duplicatePercent')-2*p('outOfRangePercent')))
 elif op=='custody_completeness':r=p('completedSteps')/pos('requiredSteps')*100
 elif op=='uptime_percent':r=p('availableSeconds')/pos('scheduledSeconds')*100
 else:raise InstrumentationError(f"Unsupported operation: {op}")
 return {'schema':'sc-lab-instrumentation-result/1.0','version':VERSION,'method':m,'inputs':inputs,'value':r,'unit':m['output']['unit']}
def canonical_json(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def fingerprint(v):return hashlib.sha256(canonical_json(v).encode()).hexdigest()
def create_record(record_type:str,data:dict[str,Any],metadata:dict[str,Any]|None=None):
 if record_type not in catalog()['recordTypes']:raise InstrumentationError(f"Unknown record type: {record_type}")
 meta=dict(metadata or {});payload={'recordType':record_type,'data':data,'metadata':meta}
 return {'schema':'sc-lab-instrumentation-record/1.0','version':VERSION,'recordId':meta.get('recordId') or 'sclab-'+secrets.token_hex(8),'recordType':record_type,'createdAt':meta.get('createdAt') or datetime.now(timezone.utc).isoformat(),'payload':payload,'payloadHash':fingerprint(payload)}
def create_manifest(records:list[dict[str,Any]]):
 components=[{'recordId':r.get('recordId'),'recordType':r.get('recordType'),'payloadHash':r.get('payloadHash')} for r in records]
 manifest={'schema':'sc-lab-instrumentation-manifest/1.0','version':VERSION,'recordCount':len(records),'components':components}
 manifest['manifestHash']=fingerprint(manifest);return manifest
def create_custody_event(sample_id:str,action:str,actor:str,location:str,previous_hash:str|None=None,notes:str|None=None):
 event={'schema':'sc-lab-custody-event/1.0','version':VERSION,'eventId':'custody-'+secrets.token_hex(8),'timestamp':datetime.now(timezone.utc).isoformat(),'sampleId':sample_id,'action':action,'actor':actor,'location':location,'notes':notes,'previousHash':previous_hash}
 event['eventHash']=fingerprint(event);return event
def verify_custody(events:list[dict[str,Any]]):
 prev=None;results=[]
 for e in events:
  copy=dict(e);stored=copy.pop('eventHash','');calc=fingerprint(copy);chain=e.get('previousHash')==prev;valid=stored==calc and chain;results.append({'eventId':e.get('eventId'),'hashValid':stored==calc,'chainValid':chain,'valid':valid});prev=stored
 return {'schema':'sc-lab-custody-verification/1.0','version':VERSION,'valid':all(x['valid'] for x in results),'eventCount':len(events),'results':results}
def normalize_measurements(rows:list[dict[str,Any]],unit_map:dict[str,float]|None=None):
 unit_map=unit_map or {};out=[]
 for idx,row in enumerate(rows):
  value=_f(row.get('value'),f'value row {idx+1}');factor=_f(unit_map.get(str(row.get('unit')),1),f'unit factor row {idx+1}')
  out.append({**row,'normalizedValue':value*factor,'sourceIndex':idx+1,'qualityFlags':list(row.get('qualityFlags') or [])})
 return {'schema':'sc-lab-measurement-ingest/1.0','version':VERSION,'rowCount':len(out),'rows':out,'datasetHash':fingerprint(out)}
