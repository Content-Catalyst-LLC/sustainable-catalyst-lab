const fs=require('fs'),vm=require('vm'),path=require('path');
const root=path.resolve(__dirname,'..');
const context={window:{},console,setTimeout,clearTimeout,Blob:function(){},URL:{createObjectURL(){return''},revokeObjectURL(){}}};context.window.window=context.window;vm.createContext(context);
function load(file){vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),context,{filename:file})}
load('assets/js/modules/core.js');load('assets/js/modules/stoichiometry.js');load('assets/js/modules/spectrometry.js');load('assets/js/modules/calculators.js');
const elements=JSON.parse(fs.readFileSync(path.join(root,'assets/data/elements.json'),'utf8'));
function assert(cond,msg){if(!cond)throw new Error(msg)}
assert(elements.length===118,'Expected 118 elements');
const S=context.window.SCLab.Stoichiometry;S.setElements(elements);
let c=S.parseFormula('H2O');assert(c.H===2&&c.O===1,'H2O parse failed');
c=S.parseFormula('Al2(SO4)3');assert(c.Al===2&&c.S===3&&c.O===12,'Parenthesized formula failed');
const mm=S.molarMass('H2O').molarMass;assert(Math.abs(mm-18.015)<0.02,'Molar mass failed');
const b=S.balanceEquation('Fe + O2 -> Fe2O3');assert(b.coefficients.join(',')==='4,3,2','Equation balance failed: '+b.coefficients);
const lim=S.limitingReagent('2 H2 + O2 -> 2 H2O',{H2:3,O2:2});assert(lim.limiting==='H2'&&Math.abs(lim.productMoles[0].moles-3)<1e-9,'Limiting reagent failed');
const Sp=context.window.SCLab.Spectrometry,pts=Sp.parse('400,0\n450,1\n500,0');assert(Sp.peaks(pts).length===1,'Peak detection failed');assert(Math.abs(Sp.integrate(pts)-50)<1e-9,'Integration failed');
const Calc=context.window.SCLab.Calculators;assert(Calc.definitions.length>=30,'Expected at least 30 calculators');
const photon=Calc.run('photon',{wavelengthNm:500});assert(Math.abs(photon.electronVolts-2.47968)<0.001,'Photon calculator failed');
const michaelis=Calc.run('michaelis',{vmax:100,substrate:8,km:2});assert(Math.abs(michaelis.rate-80)<1e-9,'Michaelis-Menten failed');
console.log(`JS tests passed: ${elements.length} elements, ${Calc.definitions.length} calculators.`);
