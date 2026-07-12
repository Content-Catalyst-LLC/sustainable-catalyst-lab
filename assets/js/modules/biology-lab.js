(function (w) {
  'use strict';

  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util;
  const R = 8.314462618;
  const F = 96485.33212;

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
  function cleanSequence(value, alphabet = 'DNA') {
    const raw = String(value || '').replace(/^>.*$/gm, '').replace(/\s+/g, '').toUpperCase();
    const allowed = alphabet === 'PROTEIN' ? /^[ACDEFGHIKLMNPQRSTVWYBXZJUO*.-]*$/ : alphabet === 'RNA' ? /^[ACGUNRYKMSWBDHV.-]*$/ : /^[ACGTUNRYKMSWBDHV.-]*$/;
    if (!raw.length) throw new Error('Sequence is empty');
    if (!allowed.test(raw)) throw new Error(`Sequence contains characters outside the ${alphabet} alphabet`);
    return raw;
  }
  function round(value, digits = 8) {
    if (!Number.isFinite(value)) return value;
    return Number(value.toPrecision(digits));
  }
  function mean(values) { return values.reduce((s, x) => s + x, 0) / values.length; }
  function variance(values, sample = true) {
    if (values.length < (sample ? 2 : 1)) return 0;
    const m = mean(values);
    return values.reduce((s, x) => s + (x - m) ** 2, 0) / (values.length - (sample ? 1 : 0));
  }
  function parseNumbers(value) {
    const values = String(value || '').split(/[\s,;]+/).filter(Boolean).map(Number);
    if (!values.length || values.some(x => !Number.isFinite(x))) throw new Error('Enter a valid numerical series');
    return values;
  }
  function parsePairs(value) {
    const rows = String(value || '').trim().split(/\r?\n/).filter(Boolean).map(line => line.split(/[\s,;]+/).filter(Boolean).map(Number));
    if (!rows.length || rows.some(row => row.length < 2 || row.slice(0, 2).some(x => !Number.isFinite(x)))) throw new Error('Enter one x,y pair per line');
    return rows.map(row => ({ x: row[0], y: row[1] }));
  }

  const codonTable = {
    TTT:'F',TTC:'F',TTA:'L',TTG:'L',TCT:'S',TCC:'S',TCA:'S',TCG:'S',TAT:'Y',TAC:'Y',TAA:'*',TAG:'*',TGT:'C',TGC:'C',TGA:'*',TGG:'W',
    CTT:'L',CTC:'L',CTA:'L',CTG:'L',CCT:'P',CCC:'P',CCA:'P',CCG:'P',CAT:'H',CAC:'H',CAA:'Q',CAG:'Q',CGT:'R',CGC:'R',CGA:'R',CGG:'R',
    ATT:'I',ATC:'I',ATA:'I',ATG:'M',ACT:'T',ACC:'T',ACA:'T',ACG:'T',AAT:'N',AAC:'N',AAA:'K',AAG:'K',AGT:'S',AGC:'S',AGA:'R',AGG:'R',
    GTT:'V',GTC:'V',GTA:'V',GTG:'V',GCT:'A',GCC:'A',GCA:'A',GCG:'A',GAT:'D',GAC:'D',GAA:'E',GAG:'E',GGT:'G',GGC:'G',GGA:'G',GGG:'G'
  };
  const aaMass = {A:89.094,R:174.203,N:132.119,D:133.104,C:121.154,E:147.131,Q:146.146,G:75.067,H:155.156,I:131.175,L:131.175,K:146.189,M:149.208,F:165.192,P:115.132,S:105.093,T:119.120,W:204.228,Y:181.191,V:117.148};
  const hydropathy = {I:4.5,V:4.2,L:3.8,F:2.8,C:2.5,M:1.9,A:1.8,G:-0.4,T:-0.7,S:-0.8,W:-0.9,Y:-1.3,P:-1.6,H:-3.2,E:-3.5,Q:-3.5,D:-3.5,N:-3.5,K:-3.9,R:-4.5};
  const complements = {A:'T',T:'A',U:'A',G:'C',C:'G',R:'Y',Y:'R',K:'M',M:'K',S:'S',W:'W',B:'V',V:'B',D:'H',H:'D',N:'N','-':'-','.':'.'};

  const rawTools = {
    diffusion(i) {
      const D = positive(i.diffusionCoefficient, 'diffusion coefficient');
      const deltaC = num(i.concentrationDifference, 'concentration difference');
      const distance = positive(i.distance, 'distance');
      return { flux: -D * deltaC / distance, magnitude: Math.abs(D * deltaC / distance), direction: deltaC > 0 ? 'toward lower concentration' : deltaC < 0 ? 'toward higher coordinate' : 'no net gradient' };
    },
    osmosis(i) {
      const vanthoff = positive(i.vantHoffFactor || 1, 'van’t Hoff factor');
      const molarity = nonnegative(i.molarity, 'molarity');
      const temperature = positive(i.temperatureK || 298.15, 'temperature');
      return { osmoticPressurePa: vanthoff * molarity * 1000 * R * temperature, osmoticPressureAtm: vanthoff * molarity * R * temperature / 101.325 };
    },
    membraneNernst(i) {
      const temperature = positive(i.temperatureK || 310.15, 'temperature');
      const z = num(i.valence, 'ion valence');
      if (z === 0) throw new Error('Ion valence cannot be zero');
      const outside = positive(i.outside, 'outside concentration');
      const inside = positive(i.inside, 'inside concentration');
      const volts = R * temperature / (z * F) * Math.log(outside / inside);
      return { equilibriumPotentialV: volts, equilibriumPotentialMv: volts * 1000, concentrationRatio: outside / inside };
    },
    bacterialGrowth(i) {
      const initial = positive(i.initial, 'initial population');
      const time = nonnegative(i.timeHours, 'time');
      const doubling = positive(i.doublingHours, 'doubling time');
      const generations = time / doubling;
      return { generations, finalPopulation: initial * 2 ** generations, specificGrowthRatePerHour: Math.log(2) / doubling };
    },
    michaelisMenten(i) {
      const vmax = positive(i.vmax, 'Vmax');
      const substrate = nonnegative(i.substrate, 'substrate concentration');
      const km = positive(i.km, 'Km');
      return { rate: vmax * substrate / (km + substrate), fractionVmax: substrate / (km + substrate), substrateAtHalfMaximum: km };
    },
    hillResponse(i) {
      const maximum = positive(i.maximum || 1, 'maximum response');
      const ligand = nonnegative(i.ligand, 'ligand concentration');
      const kd = positive(i.kd, 'half-response concentration');
      const n = positive(i.hillCoefficient || 1, 'Hill coefficient');
      const ln = ligand ** n, kn = kd ** n;
      return { response: maximum * ln / (kn + ln), fractionMaximum: ln / (kn + ln), cooperativity: n > 1 ? 'positive' : n < 1 ? 'negative' : 'noncooperative' };
    },
    enzymeInhibition(i) {
      const vmax = positive(i.vmax, 'Vmax'), km = positive(i.km, 'Km'), substrate = nonnegative(i.substrate, 'substrate'), inhibitor = nonnegative(i.inhibitor, 'inhibitor'), ki = positive(i.ki, 'Ki');
      const type = String(i.type || 'competitive');
      let apparentKm = km, apparentVmax = vmax;
      if (type === 'competitive') apparentKm = km * (1 + inhibitor / ki);
      else if (type === 'noncompetitive') apparentVmax = vmax / (1 + inhibitor / ki);
      else if (type === 'uncompetitive') { apparentKm = km / (1 + inhibitor / ki); apparentVmax = vmax / (1 + inhibitor / ki); }
      else if (type === 'mixed') { apparentKm = km * (1 + inhibitor / ki); apparentVmax = vmax / (1 + inhibitor / ki); }
      else throw new Error('Unsupported inhibition model');
      return { type, apparentKm, apparentVmax, rate: apparentVmax * substrate / (apparentKm + substrate), alpha: 1 + inhibitor / ki };
    },
    sequenceStats(i) {
      const sequence = cleanSequence(i.sequence, 'DNA').replace(/U/g, 'T').replace(/[.-]/g, '');
      const counts = {A:0,C:0,G:0,T:0,N:0,other:0};
      [...sequence].forEach(base => { if (base in counts) counts[base]++; else counts.other++; });
      const canonical = counts.A + counts.C + counts.G + counts.T;
      const gc = canonical ? (counts.G + counts.C) / canonical * 100 : 0;
      return { length: sequence.length, canonicalBases: canonical, counts, gcPercent: gc, atPercent: canonical ? 100 - gc : 0, approximateMolecularWeightDa: canonical * 660, ambiguousFraction: sequence.length ? (sequence.length - canonical) / sequence.length : 0 };
    },
    reverseComplement(i) {
      const sequence = cleanSequence(i.sequence, 'DNA').replace(/U/g, 'T');
      return { reverseComplement: [...sequence].reverse().map(base => complements[base] || 'N').join(''), length: sequence.length };
    },
    transcribe(i) {
      const sequence = cleanSequence(i.sequence, 'DNA').replace(/U/g, 'T');
      const mode = String(i.mode || 'coding');
      const rna = mode === 'template' ? [...sequence].reverse().map(base => complements[base] || 'N').join('').replace(/T/g, 'U') : sequence.replace(/T/g, 'U');
      return { mode, rna, length: rna.length };
    },
    translate(i) {
      const sequence = cleanSequence(i.sequence, 'DNA').replace(/U/g, 'T').replace(/[.-]/g, '');
      const frame = Math.max(0, Math.min(2, Math.floor(num(i.frame || 0, 'frame'))));
      let protein = '';
      const codons = [];
      for (let p = frame; p + 2 < sequence.length; p += 3) {
        const codon = sequence.slice(p, p + 3);
        const aa = codonTable[codon] || 'X';
        codons.push({ position: p + 1, codon, aminoAcid: aa }); protein += aa;
        if (aa === '*' && String(i.stopAtStop || 'yes') !== 'no') break;
      }
      return { frame, protein, aminoAcids: protein.replace(/\*/g, '').length, stopCodons: [...protein].filter(x => x === '*').length, codons };
    },
    orfFinder(i) {
      const sequence = cleanSequence(i.sequence, 'DNA').replace(/U/g, 'T').replace(/[.-]/g, '');
      const minimum = Math.max(0, Math.floor(num(i.minimumAminoAcids || 10, 'minimum amino acids')));
      const strands = [{name:'forward',seq:sequence},{name:'reverse',seq:[...sequence].reverse().map(base => complements[base] || 'N').join('')}];
      const orfs = [];
      strands.forEach(strand => {
        for (let frame = 0; frame < 3; frame++) {
          for (let p = frame; p + 2 < strand.seq.length; p += 3) {
            if (strand.seq.slice(p,p+3) !== 'ATG') continue;
            for (let q = p + 3; q + 2 < strand.seq.length; q += 3) {
              const codon = strand.seq.slice(q,q+3);
              if (['TAA','TAG','TGA'].includes(codon)) {
                const aa = (q - p) / 3;
                if (aa >= minimum) orfs.push({strand:strand.name,frame,start:p+1,end:q+3,lengthNt:q+3-p,lengthAa:aa,sequence:strand.seq.slice(p,q+3)});
                break;
              }
            }
          }
        }
      });
      return { count: orfs.length, longestAminoAcids: orfs.length ? Math.max(...orfs.map(o=>o.lengthAa)) : 0, orfs };
    },
    motifSearch(i) {
      const sequence = cleanSequence(i.sequence, 'DNA').replace(/U/g, 'T');
      const motif = cleanSequence(i.motif, 'DNA').replace(/U/g, 'T');
      const positions = [];
      for (let p = 0; p <= sequence.length - motif.length; p++) if (sequence.slice(p,p+motif.length) === motif) positions.push(p + 1);
      return { motif, count: positions.length, positions, densityPerKb: sequence.length ? positions.length / sequence.length * 1000 : 0 };
    },
    kmerProfile(i) {
      const sequence = cleanSequence(i.sequence, 'DNA').replace(/U/g, 'T').replace(/[^ACGT]/g, '');
      const k = Math.max(1, Math.min(8, Math.floor(num(i.k || 3, 'k'))));
      const counts = {};
      for (let p = 0; p <= sequence.length - k; p++) { const kmer = sequence.slice(p,p+k); counts[kmer] = (counts[kmer] || 0) + 1; }
      const sorted = Object.entries(counts).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));
      return { k, totalKmers: Math.max(0, sequence.length-k+1), uniqueKmers: sorted.length, top: sorted.slice(0,50).map(([kmer,count])=>({kmer,count,frequency:count/Math.max(1,sequence.length-k+1)})) };
    },
    globalAlignment(i) {
      const a = cleanSequence(i.sequenceA, 'DNA').replace(/U/g,'T'), b = cleanSequence(i.sequenceB, 'DNA').replace(/U/g,'T');
      if (a.length > 600 || b.length > 600) throw new Error('Global alignment is limited to 600 bases per sequence in the browser');
      const match = num(i.match || 1,'match score'), mismatch = num(i.mismatch ?? -1,'mismatch score'), gap = num(i.gap ?? -2,'gap score');
      const m=a.length,n=b.length,score=Array.from({length:m+1},()=>Array(n+1).fill(0)),trace=Array.from({length:m+1},()=>Array(n+1).fill(''));
      for(let x=1;x<=m;x++){score[x][0]=x*gap;trace[x][0]='U';} for(let y=1;y<=n;y++){score[0][y]=y*gap;trace[0][y]='L';}
      for(let x=1;x<=m;x++)for(let y=1;y<=n;y++){const d=score[x-1][y-1]+(a[x-1]===b[y-1]?match:mismatch),u=score[x-1][y]+gap,l=score[x][y-1]+gap;score[x][y]=Math.max(d,u,l);trace[x][y]=score[x][y]===d?'D':score[x][y]===u?'U':'L';}
      let x=m,y=n,aa='',bb=''; while(x||y){const t=trace[x][y];if(t==='D'){aa=a[--x]+aa;bb=b[--y]+bb;}else if(t==='U'){aa=a[--x]+aa;bb='-'+bb;}else{aa='-'+aa;bb=b[--y]+bb;}}
      const identities=[...aa].filter((c,p)=>c===bb[p]).length;
      return {score:score[m][n],alignedA:aa,alignedB:bb,alignmentLength:aa.length,identityPercent:aa.length?identities/aa.length*100:0,gaps:[...aa+bb].filter(c=>c==='-').length};
    },
    localAlignment(i) {
      const a=cleanSequence(i.sequenceA,'DNA').replace(/U/g,'T'),b=cleanSequence(i.sequenceB,'DNA').replace(/U/g,'T');
      if(a.length>600||b.length>600)throw new Error('Local alignment is limited to 600 bases per sequence in the browser');
      const match=num(i.match||2,'match score'),mismatch=num(i.mismatch??-1,'mismatch score'),gap=num(i.gap??-2,'gap score');
      const m=a.length,n=b.length,s=Array.from({length:m+1},()=>Array(n+1).fill(0)),t=Array.from({length:m+1},()=>Array(n+1).fill('0'));let best=0,bx=0,by=0;
      for(let x=1;x<=m;x++)for(let y=1;y<=n;y++){const d=s[x-1][y-1]+(a[x-1]===b[y-1]?match:mismatch),u=s[x-1][y]+gap,l=s[x][y-1]+gap;s[x][y]=Math.max(0,d,u,l);t[x][y]=s[x][y]===0?'0':s[x][y]===d?'D':s[x][y]===u?'U':'L';if(s[x][y]>best){best=s[x][y];bx=x;by=y;}}
      let x=bx,y=by,aa='',bb='';while(x&&y&&s[x][y]>0){const q=t[x][y];if(q==='D'){aa=a[--x]+aa;bb=b[--y]+bb;}else if(q==='U'){aa=a[--x]+aa;bb='-'+bb;}else{aa='-'+aa;bb=b[--y]+bb;}}
      const identities=[...aa].filter((c,p)=>c===bb[p]).length;
      return {score:best,alignedA:aa,alignedB:bb,startA:x+1,endA:bx,startB:y+1,endB:by,identityPercent:aa.length?identities/aa.length*100:0};
    },
    primerAnalysis(i) {
      const sequence=cleanSequence(i.sequence,'DNA').replace(/U/g,'T').replace(/[^ACGT]/g,'');
      const counts={A:0,C:0,G:0,T:0};[...sequence].forEach(x=>counts[x]++);const gc=(counts.G+counts.C)/sequence.length*100;
      const tm=sequence.length<14?2*(counts.A+counts.T)+4*(counts.G+counts.C):64.9+41*(counts.G+counts.C-16.4)/sequence.length;
      const tail=sequence.slice(-5),gcClamp=[...tail].filter(x=>x==='G'||x==='C').length;
      let maxHomopolymer=1,current=1;for(let p=1;p<sequence.length;p++){current=sequence[p]===sequence[p-1]?current+1:1;maxHomopolymer=Math.max(maxHomopolymer,current);}
      return {length:sequence.length,gcPercent:gc,meltingTemperatureC:tm,gcClampLast5:gcClamp,maxHomopolymer,reverseComplement:[...sequence].reverse().map(b=>complements[b]).join(''),warnings:[sequence.length<18||sequence.length>30?'Primer length outside common 18–30 nt screening range':null,gc<35||gc>65?'GC content outside common 35–65% screening range':null,maxHomopolymer>4?'Long homopolymer detected':null].filter(Boolean)};
    },
    qpcr(i) {
      const targetSample=num(i.targetSampleCt,'target sample Ct'),targetReference=num(i.targetReferenceCt,'target reference Ct'),controlSample=num(i.controlSampleCt,'control sample Ct'),controlReference=num(i.controlReferenceCt,'control reference Ct');
      const efficiency=positive(i.efficiency||2,'amplification factor per cycle');const deltaSample=targetSample-targetReference,deltaControl=controlSample-controlReference,deltaDelta=deltaSample-deltaControl;
      return {deltaCtSample:deltaSample,deltaCtControl:deltaControl,deltaDeltaCt:deltaDelta,relativeExpression:efficiency**(-deltaDelta),log2FoldChange:-deltaDelta*Math.log2(efficiency)};
    },
    gelMigration(i) {
      const sizes=parseNumbers(i.fragmentSizes).sort((a,b)=>b-a);const smallest=Math.min(...sizes),largest=Math.max(...sizes);const minDistance=positive(i.minimumDistanceMm||10,'minimum distance'),maxDistance=positive(i.maximumDistanceMm||80,'maximum distance');
      const lo=Math.log10(smallest),hi=Math.log10(largest);const bands=sizes.map(size=>({sizeBp:size,distanceMm:hi===lo?(minDistance+maxDistance)/2:minDistance+(hi-Math.log10(size))/(hi-lo)*(maxDistance-minDistance)}));
      return {bands,relationship:'Migration distance modeled as linear with log10 fragment size',rangeBp:[smallest,largest]};
    },
    proteinStats(i) {
      const sequence=cleanSequence(i.sequence,'PROTEIN').replace(/[.*-]/g,'');const counts={};let mass=18.01528,known=0,hydro=0;
      [...sequence].forEach(aa=>{counts[aa]=(counts[aa]||0)+1;if(aaMass[aa]){mass+=aaMass[aa]-18.01528;known++;hydro+=hydropathy[aa]||0;}});
      const aromatic=(counts.F||0)+(counts.W||0)+(counts.Y||0);const extinction=5500*(counts.W||0)+1490*(counts.Y||0)+125*(counts.C||0)/2;
      return {length:sequence.length,knownResidues:known,molecularWeightDa:mass,averageResidueMassDa:known?mass/known:0,meanHydropathy:known?hydro/known:0,aromaticFraction:sequence.length?aromatic/sequence.length:0,estimatedExtinctionCoefficient280:extinction,counts};
    },
    hydropathyProfile(i) {
      const sequence=cleanSequence(i.sequence,'PROTEIN').replace(/[.*-]/g,'');const window=Math.max(3,Math.min(31,Math.floor(num(i.window||9,'window'))));const radius=Math.floor(window/2),series=[];
      for(let p=0;p<sequence.length;p++){let total=0,count=0;for(let q=Math.max(0,p-radius);q<=Math.min(sequence.length-1,p+radius);q++){if(hydropathy[sequence[q]]!==undefined){total+=hydropathy[sequence[q]];count++;}}series.push({x:p+1,y:count?total/count:0});}
      const segments=[];let start=null;series.forEach((point,index)=>{if(point.y>1.6&&start===null)start=index+1;if((point.y<=1.6||index===series.length-1)&&start!==null){const end=point.y<=1.6?index:index+1;if(end-start+1>=15)segments.push({start,end});start=null;}});
      return {window,series,hydrophobicSegments:segments,maximum:Math.max(...series.map(p=>p.y)),minimum:Math.min(...series.map(p=>p.y))};
    },
    isoelectricPoint(i) {
      const sequence=cleanSequence(i.sequence,'PROTEIN').replace(/[.*-]/g,'');const counts={};[...sequence].forEach(a=>counts[a]=(counts[a]||0)+1);
      function charge(ph){const positive=1/(1+10**(ph-9.69))+(counts.K||0)/(1+10**(ph-10.5))+(counts.R||0)/(1+10**(ph-12.4))+(counts.H||0)/(1+10**(ph-6.0));const negative=1/(1+10**(2.34-ph))+(counts.D||0)/(1+10**(3.86-ph))+(counts.E||0)/(1+10**(4.25-ph))+(counts.C||0)/(1+10**(8.33-ph))+(counts.Y||0)/(1+10**(10.07-ph));return positive-negative;}
      let low=0,high=14;for(let n=0;n<80;n++){const mid=(low+high)/2;if(charge(mid)>0)low=mid;else high=mid;}const pI=(low+high)/2;
      return {estimatedPI:pI,netChargeAt7:charge(7),method:'Bisection over simplified side-chain pKa model',limitations:'Approximation excludes local structure, post-translational modifications, and terminal context'};
    },
    hardyWeinberg(i) {
      const p=nonnegative(i.p,'allele frequency p');if(p>1)throw new Error('p cannot exceed 1');const q=1-p;
      return {p,q,AA:p*p,Aa:2*p*q,aa:q*q,heterozygosity:2*p*q};
    },
    selectionChange(i) {
      const p=nonnegative(i.p,'allele frequency');if(p>1)throw new Error('p cannot exceed 1');const q=1-p,wAA=positive(i.wAA,'wAA'),wAa=positive(i.wAa,'wAa'),waa=positive(i.waa,'waa');const meanFitness=p*p*wAA+2*p*q*wAa+q*q*waa;const next=(p*p*wAA+p*q*wAa)/meanFitness;
      return {currentP:p,nextP:next,change:next-p,meanFitness,genotypeContributions:{AA:p*p*wAA,Aa:2*p*q*wAa,aa:q*q*waa}};
    },
    geneticDrift(i) {
      const p=nonnegative(i.p,'allele frequency');if(p>1)throw new Error('p cannot exceed 1');const N=positive(i.populationSize,'diploid population size'),generations=nonnegative(i.generations||1,'generations');const varianceOne=p*(1-p)/(2*N);const heterozygosity=2*p*(1-p)*(1-1/(2*N))**generations;
      return {variancePerGeneration:varianceOne,standardDeviationPerGeneration:Math.sqrt(varianceOne),expectedHeterozygosity:heterozygosity,retainedFraction:(1-1/(2*N))**generations};
    },
    jukesCantor(i) {
      const p=nonnegative(i.proportionDifferences,'proportion differences');if(p>=0.75)throw new Error('Jukes–Cantor correction is undefined at or above 0.75 observed differences');return {observedDifference:p,substitutionsPerSite:-0.75*Math.log(1-4*p/3),saturationFraction:p/0.75};
    },
    chiSquareGenetics(i) {
      const observed=parseNumbers(i.observed),expected=parseNumbers(i.expected);if(observed.length!==expected.length)throw new Error('Observed and expected series must have equal length');if(expected.some(x=>x<=0))throw new Error('Expected counts must be positive');const chi=observed.reduce((s,o,n)=>s+(o-expected[n])**2/expected[n],0);
      return {chiSquare:chi,degreesOfFreedom:observed.length-1,contributions:observed.map((o,n)=>({observed:o,expected:expected[n],contribution:(o-expected[n])**2/expected[n]})),interpretation:'Compare χ² with an appropriate critical value or p-value calculation for the stated model'};
    },
    sequenceConsensus(i) {
      const sequences=String(i.sequences||'').trim().split(/\r?\n/).filter(line=>line.trim()&&!line.startsWith('>')).map(x=>cleanSequence(x,'DNA').replace(/U/g,'T'));if(sequences.length<2)throw new Error('Enter at least two aligned sequences');const length=Math.max(...sequences.map(s=>s.length));let consensus='';const columns=[];
      for(let p=0;p<length;p++){const counts={};sequences.forEach(s=>{const c=s[p]||'-';counts[c]=(counts[c]||0)+1;});const sorted=Object.entries(counts).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));consensus+=sorted[0][0];columns.push({position:p+1,consensus:sorted[0][0],support:sorted[0][1]/sequences.length,counts});}
      return {sequenceCount:sequences.length,length,consensus,meanSupport:mean(columns.map(c=>c.support)),columns};
    },
    shannonDiversity(i) {
      const counts=parseNumbers(i.counts);if(counts.some(x=>x<0))throw new Error('Counts cannot be negative');const total=counts.reduce((s,x)=>s+x,0);if(!total)throw new Error('Total count must be positive');const proportions=counts.filter(x=>x>0).map(x=>x/total);const H=-proportions.reduce((s,p)=>s+p*Math.log(p),0);return {shannonIndex:H,effectiveSpecies:Math.exp(H),richness:proportions.length,evenness:proportions.length>1?H/Math.log(proportions.length):1,total};
    },
    simpsonDiversity(i) {
      const counts=parseNumbers(i.counts);if(counts.some(x=>x<0))throw new Error('Counts cannot be negative');const total=counts.reduce((s,x)=>s+x,0);if(!total)throw new Error('Total count must be positive');const D=counts.reduce((s,x)=>s+(x/total)**2,0);return {simpsonDominance:D,simpsonDiversity:1-D,inverseSimpson:1/D,richness:counts.filter(x=>x>0).length,total};
    },
    logisticGrowth(i) {
      const initial=positive(i.initial,'initial population'),K=positive(i.carryingCapacity,'carrying capacity'),r=num(i.growthRate,'growth rate'),time=nonnegative(i.time,'time');const value=K/(1+((K-initial)/initial)*Math.exp(-r*time));const series=Array.from({length:101},(_,n)=>{const t=time*n/100;return{x:t,y:K/(1+((K-initial)/initial)*Math.exp(-r*t))};});return {population:value,fractionCarryingCapacity:value/K,instantaneousGrowth:r*value*(1-value/K),series};
    },
    lotkaVolterra(i) {
      let prey=positive(i.prey,'prey'),pred=positive(i.predators,'predators');const alpha=positive(i.alpha,'prey growth'),beta=positive(i.beta,'predation'),delta=positive(i.delta,'predator conversion'),gamma=positive(i.gamma,'predator loss'),dt=positive(i.dt||0.01,'time step'),steps=Math.max(1,Math.min(5000,Math.floor(num(i.steps||1000,'steps'))));const series=[];
      for(let n=0;n<=steps;n++){if(n%(Math.max(1,Math.floor(steps/200)))===0)series.push({x:n*dt,y:prey,predators:pred});const dPrey=alpha*prey-beta*prey*pred,dPred=delta*prey*pred-gamma*pred;prey=Math.max(0,prey+dPrey*dt);pred=Math.max(0,pred+dPred*dt);}return {finalPrey:prey,finalPredators:pred,series,equilibrium:{prey:gamma/delta,predators:alpha/beta}};
    },
    markRecapture(i) {
      const marked=positive(i.markedFirst,'marked first sample'),second=positive(i.secondSample,'second sample'),recaptured=positive(i.recaptured,'recaptured marked');if(recaptured>Math.min(marked,second))throw new Error('Recaptured count cannot exceed either sample');const estimate=marked*second/recaptured;return {lincolnPetersenEstimate:estimate,chapmanEstimate:((marked+1)*(second+1)/(recaptured+1))-1,recaptureFraction:recaptured/second};
    },
    allometricScaling(i) {
      const referenceValue=positive(i.referenceValue,'reference value'),referenceMass=positive(i.referenceMass,'reference mass'),targetMass=positive(i.targetMass,'target mass'),exponent=num(i.exponent||0.75,'exponent');return {scaledValue:referenceValue*(targetMass/referenceMass)**exponent,massRatio:targetMass/referenceMass,exponent};
    },
    cardiacOutput(i) {
      const hr=positive(i.heartRate,'heart rate'),sv=positive(i.strokeVolumeMl,'stroke volume'),bodySurface=positive(i.bodySurfaceArea||1.8,'body surface area');const output=hr*sv/1000;return {cardiacOutputLMin:output,cardiacIndexLMinM2:output/bodySurface,beatsPerDay:hr*60*24};
    },
    oxygenContent(i) {
      const hb=positive(i.hemoglobinGdl,'hemoglobin'),saturation=nonnegative(i.saturation,'saturation'),po2=nonnegative(i.po2,'partial pressure');if(saturation>1)throw new Error('Saturation must be expressed as a fraction from 0 to 1');const content=1.34*hb*saturation+0.0031*po2;return {arterialOxygenContentMlDl:content,boundOxygenMlDl:1.34*hb*saturation,dissolvedOxygenMlDl:0.0031*po2};
    },
    doseResponse(i) {
      const top=num(i.top||1,'top'),bottom=num(i.bottom||0,'bottom'),dose=nonnegative(i.dose,'dose'),ec50=positive(i.ec50,'EC50'),hill=positive(i.hill||1,'Hill slope');const response=bottom+(top-bottom)/(1+(ec50/Math.max(dose,Number.MIN_VALUE))**hill);return {response,fractionalResponse:(response-bottom)/(top-bottom),log10Dose:dose>0?Math.log10(dose):null};
    },
    serialDilution(i) {
      const initial=positive(i.initialConcentration,'initial concentration'),factor=positive(i.dilutionFactor,'dilution factor'),steps=Math.max(1,Math.min(50,Math.floor(num(i.steps,'steps'))));if(factor<=1)throw new Error('Dilution factor must exceed 1');const series=Array.from({length:steps+1},(_,n)=>({step:n,concentration:initial/factor**n,cumulativeDilution:factor**n}));return {finalConcentration:series[series.length-1].concentration,cumulativeDilution:factor**steps,series};
    },
    colonyCount(i) {
      const colonies=nonnegative(i.colonies,'colony count'),dilution=positive(i.dilution,'dilution denominator'),volumeMl=positive(i.volumeMl,'plated volume');return {cfuPerMl:colonies*dilution/volumeMl,countingRangeStatus:colonies<30?'below common countable range':colonies>300?'above common countable range':'within common 30–300 screening range'};
    },
    bootstrapMean(i) {
      const values=parseNumbers(i.values),replicates=Math.max(100,Math.min(20000,Math.floor(num(i.replicates||2000,'replicates')))),seed=Math.floor(num(i.seed||12345,'seed'));let state=seed>>>0;function random(){state=(1664525*state+1013904223)>>>0;return state/4294967296;}const boot=[];for(let b=0;b<replicates;b++){let sum=0;for(let n=0;n<values.length;n++)sum+=values[Math.floor(random()*values.length)];boot.push(sum/values.length);}boot.sort((a,b)=>a-b);const q=p=>boot[Math.min(boot.length-1,Math.max(0,Math.floor(p*(boot.length-1))))];return {mean:mean(values),sampleStandardDeviation:Math.sqrt(variance(values,true)),bootstrapStandardError:Math.sqrt(variance(boot,true)),confidence95:[q(0.025),q(0.975)],replicates,seed};
    }
  };

  const metadata = {
    diffusion:{name:'Fick diffusion flux',tab:'cellular',collection:'physiologyRecords',equation:'J = −D ΔC/Δx',assumptions:['One-dimensional steady concentration gradient','Constant diffusion coefficient']},
    osmosis:{name:'Osmotic pressure',tab:'cellular',collection:'physiologyRecords',equation:'π = iMRT',assumptions:['Ideal dilute solution','Complete specification of van’t Hoff factor']},
    membraneNernst:{name:'Membrane Nernst potential',tab:'cellular',collection:'physiologyRecords',equation:'E = RT/(zF) ln(Cout/Cin)',assumptions:['Single-ion equilibrium','Activities approximated by concentrations']},
    bacterialGrowth:{name:'Bacterial exponential growth',tab:'cellular',collection:'biologyRecords',equation:'N = N₀ 2^(t/g)',assumptions:['Constant doubling time','No resource limitation']},
    michaelisMenten:{name:'Michaelis–Menten kinetics',tab:'enzymes',collection:'biologyRecords',equation:'v = Vmax[S]/(Km+[S])',assumptions:['Initial-rate conditions','Quasi-steady-state enzyme complex']},
    hillResponse:{name:'Hill response',tab:'enzymes',collection:'biologyRecords',equation:'θ = [L]ⁿ/(Kdⁿ+[L]ⁿ)',assumptions:['Phenomenological cooperative binding model']},
    enzymeInhibition:{name:'Enzyme inhibition models',tab:'enzymes',collection:'biologyRecords',equation:'Apparent Km and Vmax model',assumptions:['Simplified pure inhibition classes']},
    sequenceStats:{name:'DNA sequence statistics',tab:'sequences',collection:'sequences',equation:'GC% = (G+C)/(A+T+G+C)',assumptions:['Ambiguous bases excluded from canonical GC denominator']},
    reverseComplement:{name:'Reverse complement',tab:'sequences',collection:'sequences',equation:'5′↔3′ complementary strand',assumptions:['IUPAC nucleotide complements']},
    transcribe:{name:'DNA transcription',tab:'sequences',collection:'sequences',equation:'DNA → RNA',assumptions:['No splicing or RNA editing']},
    translate:{name:'Codon translation',tab:'sequences',collection:'sequences',equation:'Codons → amino acids',assumptions:['Standard genetic code']},
    orfFinder:{name:'Open reading frame finder',tab:'sequences',collection:'sequences',equation:'ATG…stop codon scan',assumptions:['Standard start and stop codons','Six-frame scan without introns']},
    motifSearch:{name:'Exact motif search',tab:'sequences',collection:'sequences',equation:'Exact substring matching',assumptions:['No degeneracy or mismatch allowance']},
    kmerProfile:{name:'k-mer profile',tab:'sequences',collection:'sequences',equation:'Sliding k-length word counts',assumptions:['Ambiguous bases removed']},
    globalAlignment:{name:'Global sequence alignment',tab:'sequences',collection:'alignments',equation:'Needleman–Wunsch dynamic programming',assumptions:['Linear gap penalty','User-supplied scoring']},
    localAlignment:{name:'Local sequence alignment',tab:'sequences',collection:'alignments',equation:'Smith–Waterman dynamic programming',assumptions:['Linear gap penalty','User-supplied scoring']},
    primerAnalysis:{name:'Primer screening',tab:'genetics',collection:'geneticAnalyses',equation:'Wallace/long-primer Tm estimates',assumptions:['Screening approximation, not oligo thermodynamics']},
    qpcr:{name:'qPCR ΔΔCt',tab:'genetics',collection:'geneticAnalyses',equation:'Relative expression = efficiency^(−ΔΔCt)',assumptions:['Comparable amplification efficiencies','Stable reference target']},
    gelMigration:{name:'DNA gel migration model',tab:'genetics',collection:'geneticAnalyses',equation:'Distance linear in log10 fragment size',assumptions:['Empirical screening relationship']},
    hardyWeinberg:{name:'Hardy–Weinberg frequencies',tab:'population',collection:'populationAnalyses',equation:'p² + 2pq + q² = 1',assumptions:['Random mating','No selection, migration, mutation, or drift']},
    selectionChange:{name:'One-generation selection',tab:'population',collection:'populationAnalyses',equation:'p′ from genotype fitness weights',assumptions:['Diploid viability selection','Random mating']},
    geneticDrift:{name:'Genetic-drift expectation',tab:'population',collection:'populationAnalyses',equation:'Var(Δp)=p(1−p)/(2N)',assumptions:['Wright–Fisher diploid population']},
    jukesCantor:{name:'Jukes–Cantor distance',tab:'population',collection:'populationAnalyses',equation:'d = −3/4 ln(1−4p/3)',assumptions:['Equal base frequencies and substitution rates']},
    chiSquareGenetics:{name:'Genetic count χ²',tab:'population',collection:'geneticAnalyses',equation:'χ² = Σ(O−E)²/E',assumptions:['Independent counts','Expected counts sufficiently large']},
    sequenceConsensus:{name:'Aligned-sequence consensus',tab:'genetics',collection:'alignments',equation:'Per-column majority consensus',assumptions:['Input sequences already aligned']},
    proteinStats:{name:'Protein sequence properties',tab:'proteins',collection:'proteinAnalyses',equation:'Residue composition and additive mass',assumptions:['Unmodified linear peptide']},
    hydropathyProfile:{name:'Protein hydropathy profile',tab:'proteins',collection:'proteinAnalyses',equation:'Kyte–Doolittle moving average',assumptions:['Sequence-only membrane screening']},
    isoelectricPoint:{name:'Protein pI approximation',tab:'proteins',collection:'proteinAnalyses',equation:'Net charge root over simplified pKa set',assumptions:['No structure or post-translational modifications']},
    shannonDiversity:{name:'Shannon diversity',tab:'ecology',collection:'ecologyAnalyses',equation:'H′ = −Σpᵢ ln pᵢ',assumptions:['Observed counts represent sampled community']},
    simpsonDiversity:{name:'Simpson diversity',tab:'ecology',collection:'ecologyAnalyses',equation:'D = Σpᵢ²',assumptions:['Observed counts represent sampled community']},
    logisticGrowth:{name:'Logistic population growth',tab:'ecology',collection:'ecologyAnalyses',equation:'N(t)=K/[1+((K−N₀)/N₀)e^(−rt)]',assumptions:['Constant carrying capacity and growth rate']},
    lotkaVolterra:{name:'Predator–prey simulation',tab:'ecology',collection:'ecologyAnalyses',equation:'Lotka–Volterra ODE Euler integration',assumptions:['Homogeneous populations','Fixed coefficients']},
    markRecapture:{name:'Mark–recapture population estimate',tab:'ecology',collection:'ecologyAnalyses',equation:'N≈MC/R',assumptions:['Closed population','Equal capture probability','Marks retained']},
    allometricScaling:{name:'Allometric scaling',tab:'ecology',collection:'ecologyAnalyses',equation:'Y₂=Y₁(M₂/M₁)^b',assumptions:['Shared scaling exponent across compared systems']},
    cardiacOutput:{name:'Cardiac output',tab:'physiology',collection:'physiologyRecords',equation:'CO = HR × SV',assumptions:['Mean heart rate and stroke volume represent interval']},
    oxygenContent:{name:'Arterial oxygen content',tab:'physiology',collection:'physiologyRecords',equation:'CaO₂=1.34HbSaO₂+0.0031PaO₂',assumptions:['Standard oxygen-binding coefficient']},
    doseResponse:{name:'Four-parameter dose response',tab:'physiology',collection:'physiologyRecords',equation:'Bottom+(Top−Bottom)/(1+(EC50/dose)^Hill)',assumptions:['Equilibrium sigmoidal response']},
    serialDilution:{name:'Serial dilution planner',tab:'measurement',collection:'biologyRecords',equation:'Cₙ=C₀/fⁿ',assumptions:['Exact transfer and mixing']},
    colonyCount:{name:'Colony-forming unit estimate',tab:'measurement',collection:'biologyRecords',equation:'CFU/mL = colonies × dilution / plated volume',assumptions:['One viable unit produces one colony']},
    bootstrapMean:{name:'Bootstrap mean interval',tab:'measurement',collection:'biologyValidationRecords',equation:'Nonparametric resampling',assumptions:['Observations are exchangeable']}
  };

  const fieldSets = {
    diffusion:[['diffusionCoefficient','Diffusion coefficient','number','1e-9'],['concentrationDifference','Δ concentration','number','1'],['distance','Distance','number','0.001']],
    osmosis:[['vantHoffFactor','van’t Hoff factor','number','1'],['molarity','Molarity (mol/L)','number','0.1'],['temperatureK','Temperature (K)','number','298.15']],
    membraneNernst:[['outside','Outside concentration','number','145'],['inside','Inside concentration','number','15'],['valence','Ion valence','number','1'],['temperatureK','Temperature (K)','number','310.15']],
    bacterialGrowth:[['initial','Initial population','number','1000'],['timeHours','Time (h)','number','8'],['doublingHours','Doubling time (h)','number','0.5']],
    michaelisMenten:[['vmax','Vmax','number','100'],['substrate','[S]','number','8'],['km','Km','number','2']],
    hillResponse:[['maximum','Maximum response','number','1'],['ligand','Ligand concentration','number','5'],['kd','Half-response concentration','number','3'],['hillCoefficient','Hill coefficient','number','2']],
    enzymeInhibition:[['vmax','Vmax','number','100'],['km','Km','number','2'],['substrate','[S]','number','8'],['inhibitor','[I]','number','1'],['ki','Ki','number','0.5'],['type','Model','select','competitive',{competitive:'Competitive',noncompetitive:'Noncompetitive',uncompetitive:'Uncompetitive',mixed:'Mixed'}]],
    sequenceStats:[['sequence','DNA sequence','textarea','>example\nATGCGCGTTAACNN']],reverseComplement:[['sequence','DNA sequence','textarea','ATGCGTTA']],transcribe:[['sequence','DNA sequence','textarea','ATGCGTTA'],['mode','Input strand','select','coding',{coding:'Coding strand',template:'Template strand'}]],translate:[['sequence','DNA/RNA sequence','textarea','ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG'],['frame','Reading frame','number','0'],['stopAtStop','Stop at first stop','select','yes',{yes:'Yes',no:'No'}]],orfFinder:[['sequence','DNA sequence','textarea','AAATGAAACCCGGGTAAATGCCCCCCCCCTGA'],['minimumAminoAcids','Minimum amino acids','number','3']],motifSearch:[['sequence','DNA sequence','textarea','ATGCGATGCGATG'],['motif','Motif','text','ATG']],kmerProfile:[['sequence','DNA sequence','textarea','ATGCGATGCGATG'],['k','k','number','3']],
    globalAlignment:[['sequenceA','Sequence A','textarea','GATTACA'],['sequenceB','Sequence B','textarea','GCATGCU'],['match','Match','number','1'],['mismatch','Mismatch','number','-1'],['gap','Gap','number','-2']],localAlignment:[['sequenceA','Sequence A','textarea','TGTTACGG'],['sequenceB','Sequence B','textarea','GGTTGACTA'],['match','Match','number','2'],['mismatch','Mismatch','number','-1'],['gap','Gap','number','-2']],
    primerAnalysis:[['sequence','Primer sequence','textarea','AGCTGACCTGATCGTACGTA']],qpcr:[['targetSampleCt','Target sample Ct','number','22'],['targetReferenceCt','Reference sample Ct','number','18'],['controlSampleCt','Target control Ct','number','25'],['controlReferenceCt','Reference control Ct','number','18'],['efficiency','Amplification factor','number','2']],gelMigration:[['fragmentSizes','Fragment sizes (bp)','textarea','10000,5000,2000,1000,500,100'],['minimumDistanceMm','Largest-fragment distance (mm)','number','10'],['maximumDistanceMm','Smallest-fragment distance (mm)','number','80']],
    proteinStats:[['sequence','Protein sequence','textarea','MKWVTFISLLFLFSSAYSRGVFRR']],hydropathyProfile:[['sequence','Protein sequence','textarea','MKWVTFISLLFLFSSAYSRGVFRR'],['window','Window','number','9']],isoelectricPoint:[['sequence','Protein sequence','textarea','MKWVTFISLLFLFSSAYSRGVFRR']],
    hardyWeinberg:[['p','Allele frequency p','number','0.6']],selectionChange:[['p','Allele frequency p','number','0.4'],['wAA','Fitness AA','number','1'],['wAa','Fitness Aa','number','0.9'],['waa','Fitness aa','number','0.6']],geneticDrift:[['p','Allele frequency p','number','0.4'],['populationSize','Diploid N','number','100'],['generations','Generations','number','20']],jukesCantor:[['proportionDifferences','Observed difference','number','0.1']],chiSquareGenetics:[['observed','Observed counts','textarea','315,108,101,32'],['expected','Expected counts','textarea','312.75,104.25,104.25,34.75']],sequenceConsensus:[['sequences','Aligned sequences','textarea','ATGCTA\nATGCCA\nATGCTA\nATGATA']],
    shannonDiversity:[['counts','Species counts','textarea','20,15,10,5,2']],simpsonDiversity:[['counts','Species counts','textarea','20,15,10,5,2']],logisticGrowth:[['initial','Initial population','number','50'],['carryingCapacity','Carrying capacity','number','1000'],['growthRate','Growth rate','number','0.4'],['time','Time','number','20']],lotkaVolterra:[['prey','Initial prey','number','40'],['predators','Initial predators','number','9'],['alpha','Prey growth α','number','0.1'],['beta','Predation β','number','0.02'],['delta','Conversion δ','number','0.01'],['gamma','Predator loss γ','number','0.1'],['dt','Time step','number','0.02'],['steps','Steps','number','1500']],markRecapture:[['markedFirst','Marked first sample','number','50'],['secondSample','Second sample','number','60'],['recaptured','Recaptured marked','number','10']],allometricScaling:[['referenceValue','Reference value','number','100'],['referenceMass','Reference mass','number','10'],['targetMass','Target mass','number','80'],['exponent','Exponent','number','0.75']],
    cardiacOutput:[['heartRate','Heart rate (bpm)','number','72'],['strokeVolumeMl','Stroke volume (mL)','number','70'],['bodySurfaceArea','Body surface area (m²)','number','1.8']],oxygenContent:[['hemoglobinGdl','Hemoglobin (g/dL)','number','15'],['saturation','O₂ saturation fraction','number','0.98'],['po2','PO₂ (mmHg)','number','95']],doseResponse:[['top','Top','number','1'],['bottom','Bottom','number','0'],['dose','Dose','number','3'],['ec50','EC50','number','2'],['hill','Hill slope','number','1.5']],
    serialDilution:[['initialConcentration','Initial concentration','number','100'],['dilutionFactor','Dilution factor','number','10'],['steps','Steps','number','6']],colonyCount:[['colonies','Colonies','number','145'],['dilution','Dilution denominator','number','10000'],['volumeMl','Plated volume (mL)','number','0.1']],bootstrapMean:[['values','Measurements','textarea','9.8,10.1,9.9,10.0,10.2'],['replicates','Replicates','number','2000'],['seed','Seed','number','12345']]
  };

  const definitions = Object.entries(metadata).map(([id, meta]) => ({ id, ...meta, fields: fieldSets[id] || [] }));

  function validate(id, input, result) {
    const warnings = [];
    function finiteDeep(value) {
      if (typeof value === 'number') return Number.isFinite(value);
      if (Array.isArray(value)) return value.every(finiteDeep);
      if (value && typeof value === 'object') return Object.values(value).every(finiteDeep);
      return true;
    }
    const checks = [{name:'Finite numerical output',passed:finiteDeep(result)}];
    if (['globalAlignment','localAlignment'].includes(id) && (String(input.sequenceA||'').length > 300 || String(input.sequenceB||'').length > 300)) warnings.push('Browser alignment cost grows quadratically with sequence length.');
    if (id === 'primerAnalysis') warnings.push(...(result.warnings || []));
    if (id === 'colonyCount' && result.countingRangeStatus !== 'within common 30–300 screening range') warnings.push(result.countingRangeStatus);
    if (id === 'lotkaVolterra') warnings.push('Euler integration is illustrative; use a higher-order solver for quantitative ecological inference.');
    if (id === 'proteinStats' || id === 'isoelectricPoint') warnings.push('Sequence-only estimates do not include post-translational modifications or structure.');
    return { status: checks.some(check => !check.passed) ? 'invalid' : warnings.length ? 'warning' : 'validated', checks, warnings, method: metadata[id]?.equation || '', assumptions: metadata[id]?.assumptions || [], validatedAt: new Date().toISOString() };
  }
  const tools = {};
  Object.entries(rawTools).forEach(([id, fn]) => { tools[id] = input => { const result = fn(input || {}); result._validation = validate(id, input || {}, result); return result; }; });
  function run(id, input) { if (!tools[id]) throw new Error(`Unknown biology method: ${id}`); return tools[id](input); }

  function svgSeries(result, title) {
    const series = result?.series;
    if (!Array.isArray(series) || series.length < 2) return '';
    const keys = Object.keys(series[0]).filter(k => k !== 'x' && typeof series[0][k] === 'number');
    if (!keys.length) return '';
    const W=720,H=280,P=42;const xs=series.map(p=>Number(p.x));const values=keys.flatMap(k=>series.map(p=>Number(p[k])));const xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...values),ymax=Math.max(...values);const sx=x=>P+(x-xmin)/(xmax-xmin||1)*(W-2*P),sy=y=>H-P-(y-ymin)/(ymax-ymin||1)*(H-2*P);const palette=['#d00000','#1e5b86','#3b7f4b','#7a4f9a'];
    const lines=keys.map((key,index)=>`<path d="${series.map((p,n)=>`${n?'L':'M'}${sx(p.x).toFixed(2)},${sy(p[key]).toFixed(2)}`).join(' ')}" fill="none" stroke="${palette[index%palette.length]}" stroke-width="2"/>`).join('');
    const legend=keys.map((k,n)=>`<text x="${P+n*140}" y="18" font-size="10" fill="${palette[n%palette.length]}">${U.esc(k)}</text>`).join('');
    return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${U.esc(title)}"><title>${U.esc(title)}</title><rect width="${W}" height="${H}" fill="#fff"/><line x1="${P}" y1="${H-P}" x2="${W-P}" y2="${H-P}" stroke="#7a8791"/><line x1="${P}" y1="${P}" x2="${P}" y2="${H-P}" stroke="#7a8791"/>${lines}${legend}<text x="${P}" y="${H-12}" font-size="9">${round(xmin,4)}</text><text x="${W-P}" y="${H-12}" font-size="9" text-anchor="end">${round(xmax,4)}</text><text x="6" y="${P+4}" font-size="9">${round(ymax,4)}</text><text x="6" y="${H-P}" font-size="9">${round(ymin,4)}</text></svg>`;
  }

  const benchmarks = [
    {id:'michaelis',tool:'michaelisMenten',input:{vmax:100,substrate:8,km:2},check:r=>Math.abs(r.rate-80)<1e-12,expected:'rate = 80'},
    {id:'hardy',tool:'hardyWeinberg',input:{p:0.6},check:r=>Math.abs(r.Aa-0.48)<1e-12,expected:'heterozygotes = 0.48'},
    {id:'gc',tool:'sequenceStats',input:{sequence:'GCGCATAT'},check:r=>Math.abs(r.gcPercent-50)<1e-12,expected:'GC = 50%'},
    {id:'translate',tool:'translate',input:{sequence:'ATGGGCTAA',frame:0,stopAtStop:'yes'},check:r=>r.protein==='MG*',expected:'protein = MG*'},
    {id:'diversity',tool:'shannonDiversity',input:{counts:'1,1,1,1'},check:r=>Math.abs(r.shannonIndex-Math.log(4))<1e-12,expected:'H = ln(4)'},
    {id:'cardiac',tool:'cardiacOutput',input:{heartRate:70,strokeVolumeMl:70,bodySurfaceArea:1.75},check:r=>Math.abs(r.cardiacOutputLMin-4.9)<1e-12,expected:'CO = 4.9 L/min'},
    {id:'qpcr',tool:'qpcr',input:{targetSampleCt:22,targetReferenceCt:18,controlSampleCt:25,controlReferenceCt:18,efficiency:2},check:r=>Math.abs(r.relativeExpression-8)<1e-12,expected:'relative expression = 8'},
    {id:'osmosis',tool:'osmosis',input:{vantHoffFactor:1,molarity:0.1,temperatureK:298.15},check:r=>r.osmoticPressurePa>240000&&r.osmoticPressurePa<250000,expected:'π ≈ 248 kPa'}
  ];
  function runBenchmarks() {
    const records = benchmarks.map(b => { try { const result=run(b.tool,b.input);const passed=!!b.check(result);return{id:b.id,tool:b.tool,passed,expected:b.expected,result}; } catch(error){ return{id:b.id,tool:b.tool,passed:false,expected:b.expected,error:error.message}; } });
    return {total:records.length,passed:records.filter(r=>r.passed).length,failed:records.filter(r=>!r.passed).length,records,ranAt:new Date().toISOString()};
  }

  function fieldHTML(field) {
    const [key,label,type,defaultValue,options] = field;
    if (type === 'textarea') return `<label>${U.esc(label)}<textarea rows="5" data-biology-field="${U.esc(key)}">${U.esc(defaultValue)}</textarea></label>`;
    if (type === 'select') return `<label>${U.esc(label)}<select data-biology-field="${U.esc(key)}">${Object.entries(options||{}).map(([value,text])=>`<option value="${U.esc(value)}"${String(value)===String(defaultValue)?' selected':''}>${U.esc(text)}</option>`).join('')}</select></label>`;
    return `<label>${U.esc(label)}<input data-biology-field="${U.esc(key)}" type="${type==='text'?'text':'number'}" step="any" value="${U.esc(defaultValue)}"></label>`;
  }
  function toolHTML(def) {
    return `<article class="sc-lab-tool sc-lab-biology-tool" data-biology-tool="${U.esc(def.id)}"><h4>${U.esc(def.name)}</h4><details class="sc-lab-biology-method"><summary>Method and assumptions</summary><p><code>${U.esc(def.equation)}</code></p><ul>${def.assumptions.map(x=>`<li>${U.esc(x)}</li>`).join('')}</ul></details><div class="sc-lab-inline-fields">${def.fields.map(fieldHTML).join('')}</div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-biology-run>Run analysis</button><button type="button" class="sc-lab-button" data-biology-save>Save</button><button type="button" class="sc-lab-button" data-biology-note>Add to notebook</button></div><div class="sc-lab-chart sc-lab-biology-chart" data-biology-chart></div><div data-biology-validation></div><pre data-biology-output></pre></article>`;
  }
  function collect(card) { const input={};card.querySelectorAll('[data-biology-field]').forEach(el=>input[el.dataset.biologyField]=el.value);return input; }
  function renderValidation(target, validation) {
    if (!validation) { target.innerHTML=''; return; }
    target.innerHTML=`<div class="sc-lab-biology-validation is-${U.esc(validation.status)}"><div><strong>${U.esc(validation.status.toUpperCase())}</strong><span>${U.esc(validation.method)}</span></div>${validation.warnings.length?`<ul>${validation.warnings.map(w=>`<li>${U.esc(w)}</li>`).join('')}</ul>`:''}</div>`;
  }
  function init(root, projects) {
    root.querySelectorAll('[data-biology-tool-grid]').forEach(grid => { const tab=grid.dataset.biologyToolGrid;grid.innerHTML=definitions.filter(d=>d.tab===tab).map(toolHTML).join(''); });
    root.querySelectorAll('[data-biology-tab]').forEach(button=>button.addEventListener('click',()=>{const value=button.dataset.biologyTab;root.querySelectorAll('[data-biology-tab]').forEach(b=>b.classList.toggle('is-active',b===button));root.querySelectorAll('[data-biology-pane]').forEach(p=>p.hidden=p.dataset.biologyPane!==value);}));
    root.querySelectorAll('[data-biology-tool]').forEach(card=>{
      let current=null;const id=card.dataset.biologyTool,def=definitions.find(d=>d.id===id);
      card.querySelector('[data-biology-run]').addEventListener('click',()=>{try{const input=collect(card);const result=run(id,input);current={id,input,result,def,createdAt:new Date().toISOString()};card.querySelector('[data-biology-output]').textContent=JSON.stringify(result,null,2);card.querySelector('[data-biology-chart]').innerHTML=svgSeries(result,def.name);renderValidation(card.querySelector('[data-biology-validation]'),result._validation);}catch(error){card.querySelector('[data-biology-output]').textContent=`Error: ${error.message}`;card.querySelector('[data-biology-chart]').innerHTML='';card.querySelector('[data-biology-validation]').innerHTML='<div class="sc-lab-biology-validation is-invalid"><strong>INVALID</strong></div>';}});
      card.querySelector('[data-biology-save]').addEventListener('click',()=>{if(!current)card.querySelector('[data-biology-run]').click();if(!current)return;projects.add(def.collection,{type:def.name,methodId:id,inputs:current.input,result:current.result,validation:current.result._validation},`${def.name} saved`);if(def.collection!=='biologyRecords')projects.add('biologyRecords',{type:def.name,methodId:id,collection:def.collection,recordedAt:new Date().toISOString()},`Biology index updated: ${def.name}`);U.toast(root,'Biology analysis saved to the active project.');});
      card.querySelector('[data-biology-note]').addEventListener('click',()=>{if(!current)card.querySelector('[data-biology-run]').click();if(!current)return;projects.add('notes',{title:`${def.name} analysis`,body:JSON.stringify({inputs:current.input,result:current.result},null,2),tags:['biology',def.tab,id]},`Notebook entry added: ${def.name}`);U.toast(root,'Analysis added to the notebook.');});
    });
    const benchmarkButton=root.querySelector('[data-biology-run-benchmarks]');if(benchmarkButton)benchmarkButton.addEventListener('click',()=>{const report=runBenchmarks();const target=root.querySelector('[data-biology-benchmark-table]');target.innerHTML=`<div class="sc-lab-validation-summary"><strong>${report.passed}/${report.total} benchmarks passed</strong><span class="${report.failed?'is-failed':'is-passed'}">${report.failed?'Review failures':'Validated'}</span><small>${U.esc(report.ranAt)}</small></div><div class="sc-lab-table-wrap"><table><thead><tr><th>Method</th><th>Expected</th><th>Status</th></tr></thead><tbody>${report.records.map(r=>`<tr><td>${U.esc(r.tool)}</td><td>${U.esc(r.expected)}</td><td><span class="sc-lab-validation-badge ${r.passed?'is-passed':'is-failed'}">${r.passed?'PASS':'FAIL'}</span></td></tr>`).join('')}</tbody></table></div>`;root._biologyBenchmarkReport=report;});
    const saveBench=root.querySelector('[data-biology-save-benchmarks]');if(saveBench)saveBench.addEventListener('click',()=>{const report=root._biologyBenchmarkReport||runBenchmarks();projects.add('biologyValidationRecords',{type:'biology-benchmark-suite',report},`Biology benchmark suite saved: ${report.passed}/${report.total} passed`);U.toast(root,'Biology validation report saved.');});
    const experiment=root.querySelector('[data-biology-experiment]');if(experiment)experiment.addEventListener('click',()=>{projects.add('experiments',{title:'Biology laboratory experiment',question:'Define the biological system or sequence question.',hypothesis:'Record a falsifiable biological hypothesis.',method:'Select a Biology Laboratory method, record samples and controls, run the analysis, review validation, and preserve outputs.',status:'planned',domain:'biology'},'Biology experiment template created');U.toast(root,'Biology experiment record created.');});
  }

  Lab.BiologyLab = { tools, rawTools, definitions, metadata, run, runBenchmarks, benchmarks, init, codonTable, aaMass, hydropathy };
})(window);
