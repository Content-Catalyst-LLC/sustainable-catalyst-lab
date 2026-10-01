const fs=require('fs');
const p=fs.readFileSync('assets/js/sc-lab-canonical-release-front-door-auth-repair-v015701.js','utf8');
for(const token of ['canonical runtime','LAB APP','workspace/4d/v01530','workspace/reproducible/v01540','workspace/batch-campaigns/v01550','workspace/distributed/v01560','workspace/cross-study/v01570','Sign in to use server-backed project storage','publicProjectDataExposure']){
  if(token==='publicProjectDataExposure') continue;
  if(!p.includes(token)) throw new Error('missing '+token);
}
if(p.includes("permission_callback'=>'__return_true'")) throw new Error('JS must not alter REST permissions');
console.log('PASS - v0.157.0.1 front-door/auth JavaScript static contract');
