from __future__ import annotations
import json, math
from pathlib import Path
from typing import Any
VERSION='0.22.2'
CONTRACT_PATH=Path(__file__).resolve().parents[2]/'contracts'/'bioprocess-monitoring-control-v0222.json'
class MonitoringError(ValueError): pass
def contract()->dict[str,Any]: return json.loads(CONTRACT_PATH.read_text(encoding='utf-8'))
def _finite(v:Any,label:str)->float:
 try:n=float(v)
 except (TypeError,ValueError) as exc: raise MonitoringError(f'{label} must be numerical.') from exc
 if not math.isfinite(n): raise MonitoringError(f'{label} must be finite.')
 return n
def _mean(v:list[float])->float:return sum(v)/len(v)
def _sd(v:list[float])->float:
 if len(v)<2:return 0.0
 m=_mean(v);return math.sqrt(sum((x-m)**2 for x in v)/(len(v)-1))
def _trapz(p:list[dict[str,float]])->float:return sum((p[i]['time']-p[i-1]['time'])*(p[i]['value']+p[i-1]['value'])/2 for i in range(1,len(p)))
def _channel(cid:str)->dict[str,Any]:
 for c in contract()['channels']:
  if c['id']==cid:return c
 raise MonitoringError(f'Unknown monitoring channel: {cid}')
def analyze(rows:list[dict[str,Any]],channel_id:str,options:dict[str,Any]|None=None)->dict[str,Any]:
 options=options or {};c=_channel(channel_id);window=max(2,int(_finite(options.get('rollingWindow',contract()['defaults']['rollingWindow']),'rollingWindow')));low=_finite(options.get('low',c['low']),'low');high=_finite(options.get('high',c['high']),'high');rate_limit=_finite(options.get('rateLimit',c['rateLimit']),'rateLimit');cv_limit=_finite(options.get('cvLimit',c['cvLimit']),'cvLimit')
 if not rows:raise MonitoringError('Monitoring analysis requires data rows.')
 points=[];missing=0
 for i,r in enumerate(rows):
  raw=r.get(channel_id)
  if raw in ('',None):missing+=1;continue
  points.append({'time':_finite(r.get('time'),f'time on row {i+1}'),'value':_finite(raw,f'{channel_id} on row {i+1}'),'phase':str(r.get('phase') or ''),'run':str(r.get('run') or 'run-1')})
 if not points:raise MonitoringError(f'No numerical {channel_id} values were found.')
 points.sort(key=lambda p:p['time']);values=[p['value'] for p in points];flags=[]
 for i,p in enumerate(points):
  slice_values=values[max(0,i-window+1):i+1];m=_mean(slice_values);s=_sd(slice_values);cv=None if m==0 else abs(s/m)*100;p.update({'rollingMean':m,'rollingSd':s,'rollingCvPercent':cv})
  if p['value']<low:flags.append({'type':'low-limit','severity':'action','time':p['time'],'value':p['value'],'limit':low})
  if p['value']>high:flags.append({'type':'high-limit','severity':'action','time':p['time'],'value':p['value'],'limit':high})
  if i:
   dt=p['time']-points[i-1]['time']
   if dt<=0:flags.append({'type':'time-order','severity':'action','time':p['time']})
   else:
    rate=abs((p['value']-points[i-1]['value'])/dt)
    if rate>rate_limit:flags.append({'type':'rate-of-change','severity':'warning','time':p['time'],'value':rate,'limit':rate_limit})
  if cv is not None and cv>cv_limit:flags.append({'type':'rolling-cv','severity':'warning','time':p['time'],'value':cv,'limit':cv_limit})
 missing_pct=missing/len(rows)*100
 if missing_pct>float(options.get('missingDataLimitPercent',contract()['defaults']['missingDataLimitPercent'])):flags.append({'type':'missing-data','severity':'warning','value':missing_pct,'limit':float(options.get('missingDataLimitPercent',contract()['defaults']['missingDataLimitPercent']))})
 action=sum(1 for f in flags if f['severity']=='action');warning=sum(1 for f in flags if f['severity']=='warning');m=_mean(values);s=_sd(values)
 return {'schema':'sc-lab-bioprocess-monitoring-analysis/1.0','version':VERSION,'channel':c,'limits':{'low':low,'high':high,'rateLimit':rate_limit,'cvLimit':cv_limit,'rollingWindow':window},'summary':{'rowCount':len(rows),'validPointCount':len(points),'missingCount':missing,'missingPercent':missing_pct,'mean':m,'standardDeviation':s,'coefficientOfVariationPercent':None if m==0 else abs(s/m)*100,'minimum':min(values),'maximum':max(values),'initial':values[0],'final':values[-1],'areaUnderCurve':_trapz(points),'actionCount':action,'warningCount':warning,'status':'action' if action else 'warning' if warning else 'normal'},'points':points,'flags':flags}
def pid(params:dict[str,Any]|None=None)->dict[str,Any]:
 p=params or {};sp=_finite(p.get('setpoint',40),'setpoint');pv=_finite(p.get('pv0',20),'pv0');kp=_finite(p.get('kp',1),'kp');ki=_finite(p.get('ki',.2),'ki');kd=_finite(p.get('kd',.05),'kd');gain=_finite(p.get('processGain',1),'processGain');tau=max(1e-9,_finite(p.get('timeConstant',3),'timeConstant'));dt=max(1e-6,_finite(p.get('dt',.1),'dt'));duration=max(dt,_finite(p.get('duration',20),'duration'));umin=_finite(p.get('outputMin',0),'outputMin');umax=_finite(p.get('outputMax',100),'outputMax');integral=0;prev=sp-pv;points=[];t=0
 while t<=duration+1e-9:
  err=sp-pv;integral+=err*dt;der=(err-prev)/dt;out=min(umax,max(umin,kp*err+ki*integral+kd*der));pv+=dt*((gain*out-pv)/tau);points.append({'time':round(t,10),'setpoint':sp,'processValue':pv,'controllerOutput':out,'error':err});prev=err;t+=dt
 errors=[abs(x['error']) for x in points]
 return {'schema':'sc-lab-bioprocess-control-simulation/1.0','version':VERSION,'parameters':{'setpoint':sp,'pv0':p.get('pv0',20),'kp':kp,'ki':ki,'kd':kd,'processGain':gain,'timeConstant':tau,'dt':dt,'duration':duration,'outputMin':umin,'outputMax':umax},'summary':{'finalProcessValue':points[-1]['processValue'],'finalError':points[-1]['error'],'integralAbsoluteError':sum(x*dt for x in errors),'maximumOutput':max(x['controllerOutput'] for x in points),'minimumOutput':min(x['controllerOutput'] for x in points)},'points':points}
def compare(rows:list[dict[str,Any]],channel_id:str)->dict[str,Any]:
 groups={}
 for i,r in enumerate(rows):
  raw=r.get(channel_id)
  if raw in ('',None):continue
  groups.setdefault(str(r.get('run') or 'run-1'),[]).append({'time':_finite(r.get('time'),f'time on row {i+1}'),'value':_finite(raw,channel_id)})
 if not groups:raise MonitoringError('No comparable run data were found.')
 runs=[]
 for name,pts in groups.items():
  pts.sort(key=lambda x:x['time']);v=[x['value'] for x in pts];runs.append({'run':name,'pointCount':len(pts),'mean':_mean(v),'standardDeviation':_sd(v),'minimum':min(v),'maximum':max(v),'initial':v[0],'final':v[-1],'areaUnderCurve':_trapz(pts),'points':pts})
 finals=[r['final'] for r in runs]
 return {'schema':'sc-lab-bioprocess-run-comparison/1.0','version':VERSION,'channel':_channel(channel_id),'runs':runs,'summary':{'runCount':len(runs),'finalMean':_mean(finals),'finalStandardDeviation':_sd(finals),'finalRange':max(finals)-min(finals)}}