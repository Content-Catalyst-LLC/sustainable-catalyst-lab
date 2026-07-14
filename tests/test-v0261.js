const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const client=fs.readFileSync(path.join(root,'assets/js/modules/compute-client.js'),'utf8');
const switcher=fs.readFileSync(path.join(root,'assets/js/modules/code-switcher.js'),'utf8');
const checks={
  queueCore:'queueCore(payload, options = {})',
  listJobs:'listJobs(query = {})',
  retry:'retry(jobId)',
  queueStatus:'queueStatus()',
  workers:'workers()',
  timedOut:"'timed_out'",
  completedCompatibility:"'finished','completed','succeeded'"
};
for(const [name,token] of Object.entries(checks)){
  const source=name==='completedCompatibility'?switcher:client;
  if(!source.includes(token)) throw new Error(`Missing ${name}`);
  console.log(`PASS: ${name}`);
}
