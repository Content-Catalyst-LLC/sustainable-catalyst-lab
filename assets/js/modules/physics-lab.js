(function (w) {
  'use strict';

  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util;
  const K = Object.freeze({
    c: 299792458,
    h: 6.62607015e-34,
    hbar: 1.054571817e-34,
    e: 1.602176634e-19,
    me: 9.1093837015e-31,
    mp: 1.67262192369e-27,
    mn: 1.67492749804e-27,
    eps0: 8.8541878128e-12,
    mu0: 1.25663706212e-6,
    G: 6.67430e-11,
    g: 9.80665,
    kB: 1.380649e-23,
    R: 8.314462618,
    sigma: 5.670374419e-8,
    Na: 6.02214076e23,
    u: 1.66053906660e-27,
    alpha: 7.2973525693e-3
  });

  const particles = [
    {id:'electron',name:'Electron',symbol:'e⁻',family:'Lepton',massMeV:0.51099895,charge:-1,spin:'1/2',lifetime:'Stable',interactions:'Electromagnetic, weak, gravitational',decays:'Stable'},
    {id:'muon',name:'Muon',symbol:'μ⁻',family:'Lepton',massMeV:105.6583755,charge:-1,spin:'1/2',lifetime:'2.197 µs',interactions:'Electromagnetic, weak, gravitational',decays:'e⁻ + ν̄e + νμ'},
    {id:'tau',name:'Tau',symbol:'τ⁻',family:'Lepton',massMeV:1776.86,charge:-1,spin:'1/2',lifetime:'2.903×10⁻¹³ s',interactions:'Electromagnetic, weak, gravitational',decays:'Leptonic and hadronic channels'},
    {id:'electron-neutrino',name:'Electron neutrino',symbol:'νe',family:'Lepton',massMeV:'<8×10⁻⁷',charge:0,spin:'1/2',lifetime:'Stable',interactions:'Weak, gravitational',decays:'No established decay'},
    {id:'up',name:'Up quark',symbol:'u',family:'Quark',massMeV:'2.16',charge:2/3,spin:'1/2',lifetime:'Confined',interactions:'Strong, electromagnetic, weak, gravitational',decays:'Confined in hadrons'},
    {id:'down',name:'Down quark',symbol:'d',family:'Quark',massMeV:'4.67',charge:-1/3,spin:'1/2',lifetime:'Confined',interactions:'Strong, electromagnetic, weak, gravitational',decays:'Confined in hadrons'},
    {id:'charm',name:'Charm quark',symbol:'c',family:'Quark',massMeV:'1270',charge:2/3,spin:'1/2',lifetime:'Confined',interactions:'Strong, electromagnetic, weak, gravitational',decays:'Weak decay in charmed hadrons'},
    {id:'strange',name:'Strange quark',symbol:'s',family:'Quark',massMeV:'93.4',charge:-1/3,spin:'1/2',lifetime:'Confined',interactions:'Strong, electromagnetic, weak, gravitational',decays:'Weak decay in strange hadrons'},
    {id:'top',name:'Top quark',symbol:'t',family:'Quark',massMeV:'172760',charge:2/3,spin:'1/2',lifetime:'~5×10⁻²⁵ s',interactions:'Strong, electromagnetic, weak, gravitational',decays:'W boson + bottom quark'},
    {id:'bottom',name:'Bottom quark',symbol:'b',family:'Quark',massMeV:'4180',charge:-1/3,spin:'1/2',lifetime:'Confined',interactions:'Strong, electromagnetic, weak, gravitational',decays:'Weak decay in bottom hadrons'},
    {id:'photon',name:'Photon',symbol:'γ',family:'Gauge boson',massMeV:0,charge:0,spin:'1',lifetime:'Stable',interactions:'Electromagnetic mediator',decays:'Stable'},
    {id:'gluon',name:'Gluon',symbol:'g',family:'Gauge boson',massMeV:0,charge:0,spin:'1',lifetime:'Confined',interactions:'Strong mediator',decays:'Confined'},
    {id:'w',name:'W boson',symbol:'W±',family:'Gauge boson',massMeV:'80369.2',charge:'±1',spin:'1',lifetime:'~3×10⁻²⁵ s',interactions:'Weak mediator',decays:'Leptons or quark pairs'},
    {id:'z',name:'Z boson',symbol:'Z⁰',family:'Gauge boson',massMeV:'91188.0',charge:0,spin:'1',lifetime:'~3×10⁻²⁵ s',interactions:'Weak mediator',decays:'Fermion–antifermion pairs'},
    {id:'higgs',name:'Higgs boson',symbol:'H⁰',family:'Scalar boson',massMeV:'125250',charge:0,spin:'0',lifetime:'~1.6×10⁻²² s',interactions:'Mass-generating scalar field',decays:'bb̄, WW, gg, ττ, ZZ, γγ'},
    {id:'proton',name:'Proton',symbol:'p',family:'Baryon',massMeV:938.27208816,charge:1,spin:'1/2',lifetime:'Stable or >10³⁴ y',interactions:'Strong, electromagnetic, weak, gravitational',decays:'No observed decay'},
    {id:'neutron',name:'Neutron',symbol:'n',family:'Baryon',massMeV:939.56542052,charge:0,spin:'1/2',lifetime:'879.4 s free',interactions:'Strong, weak, gravitational',decays:'p + e⁻ + ν̄e'},
    {id:'pion-plus',name:'Charged pion',symbol:'π±',family:'Meson',massMeV:139.57039,charge:'±1',spin:'0',lifetime:'2.603×10⁻⁸ s',interactions:'Strong, electromagnetic, weak',decays:'μ± + neutrino'},
    {id:'pion-zero',name:'Neutral pion',symbol:'π⁰',family:'Meson',massMeV:134.9768,charge:0,spin:'0',lifetime:'8.43×10⁻¹⁷ s',interactions:'Strong, electromagnetic',decays:'γ + γ'},
    {id:'kaon',name:'Charged kaon',symbol:'K±',family:'Meson',massMeV:493.677,charge:'±1',spin:'0',lifetime:'1.238×10⁻⁸ s',interactions:'Strong, electromagnetic, weak',decays:'Muon, pion, and leptonic channels'}
  ];

  function num(value, name) {
    const x = Number(value);
    if (!Number.isFinite(x)) throw new Error(`Invalid ${name}`);
    return x;
  }
  function positive(value, name) {
    const x = num(value, name);
    if (!(x > 0)) throw new Error(`${name} must be greater than zero`);
    return x;
  }
  function nonnegative(value, name) {
    const x = num(value, name);
    if (x < 0) throw new Error(`${name} cannot be negative`);
    return x;
  }
  function round(value, digits = 8) {
    if (!Number.isFinite(value)) return value;
    return Number(value.toPrecision(digits));
  }
  function vectorMagnitude(v) { return Math.sqrt(v.reduce((s, x) => s + x * x, 0)); }
  function linspace(a, b, n) { return Array.from({length:n}, (_, i) => a + (b - a) * i / Math.max(1, n - 1)); }

  const tools = {
    kinematics(i) {
      const vi=num(i.vi,'initial velocity'), a=num(i.a,'acceleration'), t=positive(i.t,'time');
      return {finalVelocity:vi+a*t,displacement:vi*t+0.5*a*t*t,averageVelocity:vi+0.5*a*t};
    },
    projectile(i) {
      const v=positive(i.v,'speed'), angle=num(i.angle,'angle')*Math.PI/180, y0=num(i.y0||0,'initial height'), g=positive(i.g||K.g,'gravity');
      const vx=v*Math.cos(angle), vy=v*Math.sin(angle), tf=(vy+Math.sqrt(vy*vy+2*g*y0))/g;
      const range=vx*tf, h=y0+vy*vy/(2*g);
      return {flightTime:tf,range,maximumHeight:h,horizontalVelocity:vx,initialVerticalVelocity:vy,series:linspace(0,tf,80).map(t=>({x:vx*t,y:y0+vy*t-0.5*g*t*t}))};
    },
    pendulum(i) {
      const L=positive(i.length,'length'), g=positive(i.g||K.g,'gravity'), amplitude=num(i.amplitude||5,'amplitude')*Math.PI/180;
      const small=2*Math.PI*Math.sqrt(L/g), corrected=small*(1+amplitude*amplitude/16+11*Math.pow(amplitude,4)/3072);
      return {smallAnglePeriod:small,finiteAmplitudePeriod:corrected,frequency:1/corrected};
    },
    spring(i) {
      const k=positive(i.k,'spring constant'), m=positive(i.m,'mass'), x=num(i.x,'displacement');
      const omega=Math.sqrt(k/m);
      return {force:-k*x,potentialEnergy:0.5*k*x*x,angularFrequency:omega,period:2*Math.PI/omega,frequency:omega/(2*Math.PI)};
    },
    wave(i) {
      const f=positive(i.frequency,'frequency'), v=positive(i.speed,'wave speed'), A=num(i.amplitude||1,'amplitude');
      const lambda=v/f, omega=2*Math.PI*f, k=2*Math.PI/lambda;
      return {wavelength:lambda,angularFrequency:omega,wavenumber:k,series:linspace(0,2*lambda,120).map(x=>({x,y:A*Math.sin(k*x)}))};
    },
    sound(i) {
      const intensity=positive(i.intensity,'intensity'), reference=positive(i.reference||1e-12,'reference intensity');
      return {soundLevelDb:10*Math.log10(intensity/reference),rmsPressure:Math.sqrt(intensity*1.21*343)};
    },
    idealGas(i) {
      const n=positive(i.n,'moles'), T=positive(i.temperature,'temperature'), P=positive(i.pressure,'pressure');
      return {volume:n*K.R*T/P,internalEnergyMonatomic:1.5*n*K.R*T};
    },
    thermodynamics(i) {
      const q=num(i.q,'heat'), w=num(i.w,'work on system'), Tcold=positive(i.tcold,'cold temperature'), Thot=positive(i.thot,'hot temperature');
      if (Tcold>=Thot) throw new Error('Cold temperature must be below hot temperature');
      return {deltaInternalEnergy:q+w,carnotEfficiency:1-Tcold/Thot,carnotCOPRefrigerator:Tcold/(Thot-Tcold)};
    },
    fluid(i) {
      const rho=positive(i.density,'density'), v=positive(i.velocity,'velocity'), L=positive(i.length,'characteristic length'), mu=positive(i.viscosity,'dynamic viscosity'), depth=num(i.depth||0,'depth');
      const Re=rho*v*L/mu;
      return {reynoldsNumber:Re,flowRegime:Re<2300?'laminar':Re>4000?'turbulent':'transitional',hydrostaticGaugePressure:rho*K.g*depth,dynamicPressure:0.5*rho*v*v};
    },
    bernoulli(i) {
      const p1=num(i.p1,'P1'),rho=positive(i.density,'density'),v1=num(i.v1,'v1'),v2=num(i.v2,'v2'),z1=num(i.z1||0,'z1'),z2=num(i.z2||0,'z2');
      return {p2:p1+0.5*rho*(v1*v1-v2*v2)+rho*K.g*(z1-z2)};
    },
    optics(i) {
      const n1=positive(i.n1,'n1'),n2=positive(i.n2,'n2'),theta1=num(i.theta1,'incident angle')*Math.PI/180,f=num(i.focalLength,'focal length'),do_=num(i.objectDistance,'object distance');
      const sin2=n1*Math.sin(theta1)/n2;
      const theta2=Math.abs(sin2)<=1?Math.asin(sin2)*180/Math.PI:null;
      const di=Math.abs(1/f-1/do_)>1e-15?1/(1/f-1/do_):Infinity;
      return {refractedAngleDeg:theta2,totalInternalReflection:Math.abs(sin2)>1,imageDistance:di,magnification:-di/do_};
    },
    diffraction(i) {
      const lambda=positive(i.wavelengthNm,'wavelength')*1e-9, a=positive(i.apertureMm,'aperture')*1e-3, L=positive(i.screenDistance,'screen distance');
      const theta=Math.asin(Math.min(1,lambda/a));
      return {firstMinimumAngleDeg:theta*180/Math.PI,centralMaximumWidth:2*L*Math.tan(theta),rayleighAngularResolution:1.22*lambda/a};
    },
    coulomb(i) {
      const q1=num(i.q1,'q1'), q2=num(i.q2,'q2'), r=positive(i.r,'distance');
      const force=(1/(4*Math.PI*K.eps0))*q1*q2/(r*r);
      return {force,forceMagnitude:Math.abs(force),interaction:force<0?'attractive':'repulsive',potentialEnergy:(1/(4*Math.PI*K.eps0))*q1*q2/r};
    },
    pointField(i) {
      const charges=typeof i.charges==='string'?JSON.parse(i.charges):i.charges;
      const x=num(i.x,'x'),y=num(i.y,'y'); let ex=0,ey=0,V=0;
      (charges||[]).forEach((c,index)=>{const dx=x-num(c.x,`charge ${index+1} x`),dy=y-num(c.y,`charge ${index+1} y`),r=Math.hypot(dx,dy);if(r<1e-12)throw new Error('Evaluation point overlaps a charge');const q=num(c.q,`charge ${index+1} q`),coef=q/(4*Math.PI*K.eps0);ex+=coef*dx/(r*r*r);ey+=coef*dy/(r*r*r);V+=coef/r;});
      return {electricFieldX:ex,electricFieldY:ey,electricFieldMagnitude:Math.hypot(ex,ey),potential:V};
    },
    capacitor(i) {
      const values=String(i.capacitances).split(/[ ,;]+/).filter(Boolean).map(v=>positive(v,'capacitance'));
      const mode=i.mode||'parallel', voltage=num(i.voltage||0,'voltage');
      const ceq=mode==='series'?1/values.reduce((s,c)=>s+1/c,0):values.reduce((s,c)=>s+c,0);
      return {equivalentCapacitance:ceq,charge:ceq*voltage,storedEnergy:0.5*ceq*voltage*voltage};
    },
    magnetic(i) {
      const current=num(i.current,'current'), r=positive(i.r,'radius'), turns=positive(i.turns||1,'turns'), length=positive(i.length||1,'length');
      return {straightWireField:K.mu0*current/(2*Math.PI*r),solenoidField:K.mu0*(turns/length)*current,loopCenterField:K.mu0*turns*current/(2*r)};
    },
    lorentz(i) {
      const q=num(i.q,'charge'),v=positive(i.v,'speed'),B=positive(i.B,'magnetic field'),angle=num(i.angle||90,'angle')*Math.PI/180,mass=positive(i.mass,'mass');
      const F=q*v*B*Math.sin(angle), radius=mass*v/(Math.abs(q)*B), omega=Math.abs(q)*B/mass;
      return {magneticForce:F,orbitRadius:radius,cyclotronAngularFrequency:omega,cyclotronFrequency:omega/(2*Math.PI)};
    },
    induction(i) {
      const turns=positive(i.turns,'turns'),dFlux=num(i.deltaFlux,'flux change'),dt=positive(i.deltaTime,'time interval'),resistance=positive(i.resistance||1,'resistance');
      const emf=-turns*dFlux/dt;
      return {inducedEmf:emf,current:emf/resistance,power:emf*emf/resistance};
    },
    rlc(i) {
      const R=positive(i.R,'resistance'),L=positive(i.L,'inductance'),C=positive(i.C,'capacitance'),f=positive(i.frequency,'frequency'),V=positive(i.voltage||1,'voltage');
      const w=2*Math.PI*f, xl=w*L, xc=1/(w*C), reactance=xl-xc, z=Math.hypot(R,reactance), phase=Math.atan2(reactance,R);
      return {inductiveReactance:xl,capacitiveReactance:xc,impedanceMagnitude:z,phaseRadians:phase,phaseDegrees:phase*180/Math.PI,currentRms:V/z,realPower:V*V*R/(z*z),reactivePower:V*V*reactance/(z*z),apparentPower:V*V/z,powerFactor:Math.cos(phase),resonantFrequency:1/(2*Math.PI*Math.sqrt(L*C))};
    },
    frequencySweep(i) {
      const R=positive(i.R,'resistance'),L=positive(i.L,'inductance'),C=positive(i.C,'capacitance'),fmin=positive(i.fmin,'minimum frequency'),fmax=positive(i.fmax,'maximum frequency'),points=Math.max(20,Math.min(400,Math.round(num(i.points||120,'points'))));
      const ratio=Math.pow(fmax/fmin,1/(points-1)); const series=[];
      for(let n=0,f=fmin;n<points;n++,f*=ratio){const r=tools.rlc({R,L,C,frequency:f,voltage:1});series.push({x:f,y:20*Math.log10(1/r.impedanceMagnitude),phase:r.phaseDegrees,impedance:r.impedanceMagnitude});}
      return {resonantFrequency:1/(2*Math.PI*Math.sqrt(L*C)),series};
    },
    filter(i) {
      const R=positive(i.R,'resistance'),C=positive(i.C,'capacitance'),f=positive(i.frequency,'frequency'),type=i.type||'lowpass',w=2*Math.PI*f,rc=w*R*C;
      const gain=type==='highpass'?rc/Math.sqrt(1+rc*rc):1/Math.sqrt(1+rc*rc);
      const phase=type==='highpass'?Math.atan2(1,rc): -Math.atan(rc);
      return {cutoffFrequency:1/(2*Math.PI*R*C),gain,gainDb:20*Math.log10(gain),phaseDegrees:phase*180/Math.PI};
    },
    emWave(i) {
      const f=positive(i.frequency,'frequency'),conductivity=positive(i.conductivity||5.8e7,'conductivity'),mur=positive(i.relativePermeability||1,'relative permeability'),er=positive(i.relativePermittivity||1,'relative permittivity'),power=positive(i.power||1,'power'),distance=positive(i.distance||1,'distance');
      const mu=K.mu0*mur, eps=K.eps0*er, velocity=1/Math.sqrt(mu*eps), wavelength=velocity/f, skin=Math.sqrt(2/(2*Math.PI*f*mu*conductivity));
      return {phaseVelocity:velocity,wavelength,intrinsicImpedance:Math.sqrt(mu/eps),skinDepth:skin,isotropicPowerDensity:power/(4*Math.PI*distance*distance)};
    },
    waveguide(i) {
      const a=positive(i.width,'broad dimension'),er=positive(i.relativePermittivity||1,'relative permittivity'),f=positive(i.frequency,'frequency');
      const fc=K.c/(2*a*Math.sqrt(er));
      return {te10CutoffFrequency:fc,aboveCutoff:f>fc,guideWavelength:f>fc?(K.c/(f*Math.sqrt(er)))/Math.sqrt(1-Math.pow(fc/f,2)):null};
    },
    photon(i) {
      const wavelength=positive(i.wavelengthNm,'wavelength')*1e-9; const E=K.h*K.c/wavelength;
      return {frequency:K.c/wavelength,energyJ:E,energyEv:E/K.e,momentum:E/K.c,wavenumber:2*Math.PI/wavelength};
    },
    deBroglie(i) {
      const mass=positive(i.mass,'mass'), velocity=positive(i.velocity,'velocity');
      if(velocity>=K.c)throw new Error('Velocity must be below c');const gamma=1/Math.sqrt(1-velocity*velocity/(K.c*K.c));const p=gamma*mass*velocity;
      return {lorentzFactor:gamma,momentum:p,wavelength:K.h/p,totalEnergy:gamma*mass*K.c*K.c,kineticEnergy:(gamma-1)*mass*K.c*K.c};
    },
    particleBox(i) {
      const n=positive(i.n,'quantum number'),m=positive(i.mass,'particle mass'),L=positive(i.length,'box length'); const E=n*n*Math.PI*Math.PI*K.hbar*K.hbar/(2*m*L*L);
      return {energyJ:E,energyEv:E/K.e,adjacentLevelSpacingJ:(2*n+1)*Math.PI*Math.PI*K.hbar*K.hbar/(2*m*L*L)};
    },
    tunneling(i) {
      const mass=positive(i.mass,'mass'),barrierEv=positive(i.barrierEv,'barrier energy')*K.e,energyEv=positive(i.energyEv,'particle energy')*K.e,width=positive(i.widthNm,'barrier width')*1e-9;
      if(energyEv>=barrierEv)return{transmissionApproximation:1,regime:'above barrier'};const kappa=Math.sqrt(2*mass*(barrierEv-energyEv))/K.hbar;
      return {decayConstant:kappa,transmissionApproximation:Math.exp(-2*kappa*width),regime:'tunneling'};
    },
    hydrogen(i) {
      const ni=positive(i.ni,'initial level'),nf=positive(i.nf,'final level');if(ni===nf)throw new Error('Levels must differ');
      const Eev=13.605693122994*Math.abs(1/(nf*nf)-1/(ni*ni)),E=Eev*K.e;
      return {photonEnergyEv:Eev,photonEnergyJ:E,wavelengthNm:K.h*K.c/E*1e9,transition:ni>nf?'emission':'absorption'};
    },
    decay(i) {
      const halfLife=positive(i.halfLife,'half-life'),time=positive(i.time,'time'),initial=positive(i.initial,'initial amount'); const lambda=Math.log(2)/halfLife,remaining=initial*Math.exp(-lambda*time);
      return {decayConstant:lambda,remaining,decayed:initial-remaining,fractionRemaining:remaining/initial,activity:lambda*remaining};
    },
    binding(i) {
      const Z=positive(i.protons,'protons'),N=positive(i.neutrons,'neutrons'),atomicMassU=positive(i.atomicMassU,'atomic mass');
      const electronMassU=0.000548579909065, protonMassU=1.007276466621, neutronMassU=1.00866491595;
      const nuclearMass=atomicMassU-Z*electronMassU,defect=Z*protonMassU+N*neutronMassU-nuclearMass,energy=defect*931.49410242;
      return {massDefectU:defect,bindingEnergyMeV:energy,bindingEnergyPerNucleonMeV:energy/(Z+N)};
    },
    relativistic(i) {
      const massKg=positive(i.massKg,'rest mass'),velocity=positive(i.velocity,'velocity');if(velocity>=K.c)throw new Error('Velocity must be below c');
      const gamma=1/Math.sqrt(1-velocity*velocity/(K.c*K.c));return{lorentzFactor:gamma,totalEnergyJ:gamma*massKg*K.c*K.c,kineticEnergyJ:(gamma-1)*massKg*K.c*K.c,momentum:gamma*massKg*velocity,timeDilationFactor:gamma,lengthContractionFactor:1/gamma};
    },
    invariantMass(i) {
      const events=typeof i.fourVectors==='string'?JSON.parse(i.fourVectors):i.fourVectors;let E=0,px=0,py=0,pz=0;
      (events||[]).forEach((v,index)=>{E+=num(v.E,`vector ${index+1} E`);px+=num(v.px||0,`vector ${index+1} px`);py+=num(v.py||0,`vector ${index+1} py`);pz+=num(v.pz||0,`vector ${index+1} pz`);});const m2=E*E-px*px-py*py-pz*pz;
      return {totalEnergy:E,totalMomentum:[px,py,pz],totalMomentumMagnitude:Math.hypot(px,py,pz),invariantMass:Math.sqrt(Math.max(0,m2)),massSquared:m2,units:'Input values assumed in consistent natural units (c=1)'};
    },
    twoBodyDecay(i) {
      const M=positive(i.parentMass,'parent mass'),m1=nonnegative(i.mass1,'daughter mass 1'),m2=nonnegative(i.mass2,'daughter mass 2');if(M<m1+m2)throw new Error('Parent mass is below decay threshold');
      const p=Math.sqrt((M*M-Math.pow(m1+m2,2))*(M*M-Math.pow(m1-m2,2)))/(2*M);
      return {daughterMomentum:p,energy1:Math.sqrt(p*p+m1*m1),energy2:Math.sqrt(p*p+m2*m2),kineticEnergyRelease:M-m1-m2};
    },
    detector(i) {
      const B=positive(i.B,'magnetic field'),radius=positive(i.radius,'track radius'),charge=positive(Math.abs(num(i.charge,'charge number')),'charge number'),distance=positive(i.distance,'flight distance'),time=positive(i.time,'flight time'),events=positive(i.events,'events'),background=num(i.background||0,'background'),efficiency=positive(i.efficiency||1,'efficiency'),luminosity=positive(i.luminosity||1,'integrated luminosity');
      const beta=distance/(time*K.c),pGeV=0.299792458*charge*B*radius,signal=Math.max(0,events-background);
      return {transverseMomentumGeVPerC:pGeV,beta,timeOfFlightVelocity:distance/time,signalEvents:signal,poissonSignificance:background>0?signal/Math.sqrt(background):null,crossSection:signal/(efficiency*luminosity)};
    },
    uncertainty(i) {
      const values=typeof i.values==='string'?JSON.parse(i.values):i.values; const total=Math.sqrt((values||[]).reduce((s,v)=>s+Math.pow(num(v,'uncertainty'),2),0));
      return {combinedStandardUncertainty:total,expandedUncertaintyK2:2*total};
    }
  };

  function svgLine(series, options = {}) {
    if (!series || series.length < 2) return '<div class="sc-lab-data-note">No plottable series.</div>';
    const xs=series.map(p=>Number(p.x)),ys=series.map(p=>Number(p.y));
    const xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys);
    const W=720,H=300,P=38; const sx=x=>P+(x-xmin)/(xmax-xmin||1)*(W-2*P); const sy=y=>H-P-(y-ymin)/(ymax-ymin||1)*(H-2*P);
    const path=series.map((p,n)=>`${n?'L':'M'}${sx(p.x).toFixed(2)},${sy(p.y).toFixed(2)}`).join(' ');
    return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${U.esc(options.label||'Physics plot')}"><rect width="${W}" height="${H}" fill="#fff"/><line x1="${P}" y1="${H-P}" x2="${W-P}" y2="${H-P}" stroke="#7a8791"/><line x1="${P}" y1="${P}" x2="${P}" y2="${H-P}" stroke="#7a8791"/><path d="${path}" fill="none" stroke="#d00000" stroke-width="2"/><text x="${P}" y="${H-10}" font-size="10">${U.esc(round(xmin,4))}</text><text x="${W-P}" y="${H-10}" font-size="10" text-anchor="end">${U.esc(round(xmax,4))}</text><text x="6" y="${P+4}" font-size="10">${U.esc(round(ymax,4))}</text><text x="6" y="${H-P}" font-size="10">${U.esc(round(ymin,4))}</text></svg>`;
  }

  function collect(card) {
    const input={};
    card.querySelectorAll('[data-physics-field]').forEach(el=>{input[el.dataset.physicsField]=el.value;});
    return input;
  }

  function compactResult(result) {
    const copy={...result}; delete copy.series; return copy;
  }

  function init(root, projects) {
    const panel=root.querySelector('[data-lab-module="physics"]');
    if(!panel)return;
    panel.querySelectorAll('[data-physics-tab]').forEach(button=>button.addEventListener('click',()=>{
      const tab=button.dataset.physicsTab;
      panel.querySelectorAll('[data-physics-tab]').forEach(b=>b.classList.toggle('is-active',b===button));
      panel.querySelectorAll('[data-physics-pane]').forEach(p=>{p.hidden=p.dataset.physicsPane!==tab;});
    }));

    panel.querySelectorAll('[data-physics-run]').forEach(button=>button.addEventListener('click',()=>{
      const card=button.closest('[data-physics-tool]'); const id=card.dataset.physicsTool; const output=card.querySelector('[data-physics-output]'); const chart=card.querySelector('[data-physics-chart]');
      try{
        const input=collect(card),result=tools[id](input); card._lastPhysics={id,input,result};
        if(output)output.textContent=JSON.stringify(compactResult(result),null,2);
        if(chart)chart.innerHTML=svgLine(result.series,{label:id});
      }catch(error){if(output)output.textContent=`Error: ${error.message}`;if(chart)chart.innerHTML='';}
    }));

    panel.querySelectorAll('[data-physics-save]').forEach(button=>button.addEventListener('click',()=>{
      const card=button.closest('[data-physics-tool]'); if(!card._lastPhysics){card.querySelector('[data-physics-run]')?.click();}
      if(!card._lastPhysics)return;
      const map={
        pointField:'fieldModels',coulomb:'fieldModels',magnetic:'fieldModels',lorentz:'fieldModels',induction:'fieldModels',emWave:'fieldModels',waveguide:'fieldModels',
        rlc:'circuitAnalyses',frequencySweep:'circuitAnalyses',filter:'circuitAnalyses',
        wave:'waveforms',sound:'waveforms',projectile:'physicsRecords',kinematics:'physicsRecords',pendulum:'physicsRecords',spring:'physicsRecords',idealGas:'physicsRecords',thermodynamics:'physicsRecords',fluid:'physicsRecords',bernoulli:'physicsRecords',
        optics:'opticalAnalyses',diffraction:'opticalAnalyses',photon:'opticalAnalyses',
        decay:'nuclearRecords',binding:'nuclearRecords',
        relativistic:'particleEvents',invariantMass:'particleEvents',twoBodyDecay:'particleEvents',detector:'detectorAnalyses',
        deBroglie:'physicsRecords',particleBox:'physicsRecords',tunneling:'physicsRecords',hydrogen:'physicsRecords',uncertainty:'physicsRecords',powerLawUncertainty:'physicsValidationRecords',weightedMean:'physicsValidationRecords'
      };
      const collection=map[card._lastPhysics.id]||'physicsRecords';
      projects.add(collection,{type:card._lastPhysics.id,inputs:card._lastPhysics.input,result:compactResult(card._lastPhysics.result),assumptions:'Calculated with Lab v0.4.1 constants, validation checks, and stated inputs.'},`Physics analysis saved: ${card._lastPhysics.id}`);
      U.toast(root,'Physics analysis saved to the active project.');
    }));

    const particleSearch=panel.querySelector('[data-particle-search]'); const particleFamily=panel.querySelector('[data-particle-family]'); const particleList=panel.querySelector('[data-particle-list]'); const particleDetail=panel.querySelector('[data-particle-detail]');
    function renderParticles(){
      const q=(particleSearch?.value||'').toLowerCase(),family=particleFamily?.value||'all';
      const rows=particles.filter(p=>(family==='all'||p.family===family)&&(!q||`${p.name} ${p.symbol} ${p.family}`.toLowerCase().includes(q)));
      particleList.innerHTML=rows.map(p=>`<button type="button" data-particle-id="${U.esc(p.id)}"><strong>${U.esc(p.symbol)}</strong><span>${U.esc(p.name)}</span><small>${U.esc(p.family)}</small></button>`).join('');
      particleList.querySelectorAll('[data-particle-id]').forEach(b=>b.addEventListener('click',()=>{const p=particles.find(x=>x.id===b.dataset.particleId);particleDetail.innerHTML=`<h4>${U.esc(p.name)} <span>${U.esc(p.symbol)}</span></h4><dl><div><dt>Family</dt><dd>${U.esc(p.family)}</dd></div><div><dt>Mass</dt><dd>${U.esc(p.massMeV)} MeV/c²</dd></div><div><dt>Charge</dt><dd>${U.esc(p.charge)} e</dd></div><div><dt>Spin</dt><dd>${U.esc(p.spin)}</dd></div><div><dt>Lifetime</dt><dd>${U.esc(p.lifetime)}</dd></div><div><dt>Interactions</dt><dd>${U.esc(p.interactions)}</dd></div><div><dt>Decay modes</dt><dd>${U.esc(p.decays)}</dd></div></dl>`;}));
    }
    particleSearch?.addEventListener('input',renderParticles); particleFamily?.addEventListener('change',renderParticles); renderParticles();

    panel.querySelectorAll('[data-physics-experiment]').forEach(experimentButton => experimentButton.addEventListener('click',()=>{
      const title=w.prompt('Physics experiment title','RLC resonance measurement');if(title===null)return;
      const method=w.prompt('Method or procedure','Sweep frequency, record amplitude and phase, fit resonance and uncertainty.');if(method===null)return;
      projects.add('experiments',{title,question:'What physical relationship or parameter is being tested?',hypothesis:'State the predicted relationship.',method,status:'planned',domain:'physics'},`Physics experiment created: ${title}`);U.toast(root,'Physics experiment added.');
    }));
    panel.querySelector('[data-physics-note]')?.addEventListener('click',()=>{
      const title=w.prompt('Notebook title','Physics laboratory note');if(title===null)return;const body=w.prompt('Observation, result, or interpretation','');if(body===null)return;projects.add('notes',{type:'physics',title,body,tags:['physics']},`Physics notebook entry added: ${title}`);U.toast(root,'Notebook entry saved.');
    });
  }

  Lab.PhysicsLab={constants:K,particles,tools,svgLine,init};
})(window);
