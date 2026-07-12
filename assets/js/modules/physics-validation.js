(function (w) {
  'use strict';

  const Lab = w.SCLab = w.SCLab || {};
  const Physics = Lab.PhysicsLab;
  const U = Lab.util;
  if (!Physics) return;

  const metadata = {
    kinematics:{title:'Uniform-acceleration kinematics',equation:'v = v₀ + at; Δx = v₀t + ½at²',inputs:'v₀ [m s⁻¹], a [m s⁻²], t [s]',outputs:'v [m s⁻¹], Δx [m]',assumptions:['One-dimensional motion','Constant acceleration']},
    projectile:{title:'Projectile trajectory',equation:'x = v₀ cosθ·t; y = y₀ + v₀ sinθ·t − ½gt²',inputs:'v₀ [m s⁻¹], θ [°], y₀ [m], g [m s⁻²]',outputs:'time [s], range [m], height [m]',assumptions:['Uniform gravity','No aerodynamic drag','Flat landing surface']},
    pendulum:{title:'Pendulum period',equation:'T₀ = 2π√(L/g)',inputs:'L [m], amplitude [°], g [m s⁻²]',outputs:'period [s], frequency [Hz]',assumptions:['Rigid massless support','Finite-amplitude series through θ⁴']},
    spring:{title:'Mass–spring oscillator',equation:'F = −kx; ω = √(k/m)',inputs:'k [N m⁻¹], m [kg], x [m]',outputs:'force [N], energy [J], frequency [Hz]',assumptions:['Linear Hookean spring','Negligible damping']},
    wave:{title:'Wave relation',equation:'v = fλ; y = A sin(kx)',inputs:'f [Hz], v [m s⁻¹], A [selected unit]',outputs:'λ [m], ω [rad s⁻¹], k [rad m⁻¹]',assumptions:['Monochromatic sinusoidal wave']},
    sound:{title:'Acoustic intensity',equation:'L = 10 log₁₀(I/I₀)',inputs:'I, I₀ [W m⁻²]',outputs:'level [dB], RMS pressure [Pa]',assumptions:['Plane progressive wave','Air properties fixed at representative values']},
    idealGas:{title:'Ideal gas state',equation:'PV = nRT',inputs:'n [mol], T [K], P [Pa]',outputs:'V [m³], U [J]',assumptions:['Ideal monatomic gas','Thermodynamic equilibrium']},
    thermodynamics:{title:'First law and ideal limits',equation:'ΔU = Q + W; η₍Carnot₎ = 1 − Tc/Th',inputs:'Q, W [J], T [K]',outputs:'ΔU [J], ideal efficiency',assumptions:['Work sign is positive on the system','Reservoir temperatures are absolute']},
    fluid:{title:'Flow regime and pressure',equation:'Re = ρvL/μ; p = ρgh',inputs:'ρ [kg m⁻³], v [m s⁻¹], L [m], μ [Pa s], h [m]',outputs:'Re, pressure [Pa]',assumptions:['Newtonian fluid','Flow-regime thresholds are approximate']},
    bernoulli:{title:'Bernoulli relation',equation:'p + ½ρv² + ρgz = constant',inputs:'p [Pa], ρ [kg m⁻³], v [m s⁻¹], z [m]',outputs:'p₂ [Pa]',assumptions:['Steady incompressible inviscid streamline flow','No shaft work or losses']},
    optics:{title:'Refraction and thin lens',equation:'n₁ sinθ₁ = n₂ sinθ₂; 1/f = 1/do + 1/di',inputs:'indices, angle [°], distances [m]',outputs:'angle [°], image distance [m], magnification',assumptions:['Paraxial thin lens','Homogeneous isotropic media']},
    diffraction:{title:'Diffraction scale',equation:'sinθ = λ/a; θR = 1.22λ/a',inputs:'λ [nm], aperture [mm], distance [m]',outputs:'angle [°], width [m]',assumptions:['Fraunhofer/small-aperture approximation as applicable']},
    coulomb:{title:'Coulomb interaction',equation:'F = q₁q₂/(4πε₀r²)',inputs:'q [C], r [m]',outputs:'force [N], energy [J]',assumptions:['Point charges','Vacuum permittivity']},
    pointField:{title:'Point-charge field',equation:'E = Σ q r̂/(4πε₀r²)',inputs:'charge positions [m], q [C]',outputs:'E [V m⁻¹], V [V]',assumptions:['Point charges','Two-dimensional evaluation plane']},
    capacitor:{title:'Capacitor network',equation:'Cparallel = ΣC; 1/Cseries = Σ1/C',inputs:'C [F], V [V]',outputs:'Ceq [F], Q [C], U [J]',assumptions:['Ideal capacitors','No dielectric loss']},
    magnetic:{title:'Magnetic fields',equation:'Bwire = μ₀I/(2πr); Bsolenoid = μ₀nI',inputs:'I [A], dimensions [m], turns',outputs:'B [T]',assumptions:['Ideal geometries','Air/vacuum permeability']},
    lorentz:{title:'Lorentz force and orbit',equation:'F = qvB sinθ; r = mv/(|q|B)',inputs:'q [C], v [m s⁻¹], B [T], m [kg]',outputs:'F [N], r [m], f [Hz]',assumptions:['Uniform magnetic field','Non-relativistic orbit radius']},
    induction:{title:'Faraday induction',equation:'ε = −NΔΦ/Δt',inputs:'turns, flux [Wb], time [s], R [Ω]',outputs:'emf [V], current [A], power [W]',assumptions:['Average flux change over interval','Resistive load']},
    rlc:{title:'Series RLC',equation:'Z = R + j(ωL − 1/ωC)',inputs:'R [Ω], L [H], C [F], f [Hz], V [V RMS]',outputs:'|Z| [Ω], phase [°], current [A], power [W/var/VA]',assumptions:['Sinusoidal steady state','Ideal lumped components']},
    frequencySweep:{title:'RLC frequency sweep',equation:'Z(f) = R + j(2πfL − 1/(2πfC))',inputs:'R [Ω], L [H], C [F], f [Hz]',outputs:'response [dB], phase [°]',assumptions:['Log-spaced frequencies','Series RLC normalized to 1 V']},
    filter:{title:'First-order RC filter',equation:'|HLP| = 1/√(1+(ωRC)²)',inputs:'R [Ω], C [F], f [Hz]',outputs:'gain, gain [dB], phase [°]',assumptions:['Ideal first-order network']},
    emWave:{title:'Electromagnetic wave and skin depth',equation:'v = 1/√(με); δ = √(2/(ωμσ))',inputs:'f [Hz], σ [S m⁻¹], μr, εr, P [W], r [m]',outputs:'v [m s⁻¹], λ [m], η [Ω], δ [m], S [W m⁻²]',assumptions:['Linear isotropic medium','Good-conductor skin-depth approximation']},
    waveguide:{title:'Rectangular waveguide',equation:'fc,10 = c/(2a√εr)',inputs:'a [m], εr, f [Hz]',outputs:'cutoff [Hz], guide wavelength [m]',assumptions:['Ideal rectangular guide','Dominant TE10 mode']},
    photon:{title:'Photon properties',equation:'E = hc/λ; p = h/λ',inputs:'λ [nm]',outputs:'f [Hz], E [J/eV], p [kg m s⁻¹]',assumptions:['Vacuum wavelength']},
    deBroglie:{title:'Relativistic de Broglie wavelength',equation:'λ = h/(γmv)',inputs:'m [kg], v [m s⁻¹]',outputs:'λ [m], p [kg m s⁻¹], energy [J]',assumptions:['Free particle']},
    particleBox:{title:'Particle in a one-dimensional box',equation:'En = n²π²ℏ²/(2mL²)',inputs:'n, m [kg], L [m]',outputs:'energy [J/eV]',assumptions:['Infinite square well','Integer quantum number']},
    tunneling:{title:'Rectangular barrier tunneling',equation:'T ≈ exp(−2κa)',inputs:'m [kg], energies [eV], width [nm]',outputs:'transmission estimate',assumptions:['One-dimensional rectangular barrier','WKB-like exponential estimate']},
    hydrogen:{title:'Hydrogen transition',equation:'ΔE = 13.6057 eV |1/nf² − 1/ni²|',inputs:'integer levels',outputs:'energy [J/eV], wavelength [nm]',assumptions:['Hydrogenic non-relativistic spectrum']},
    decay:{title:'Radioactive decay',equation:'N = N₀ exp(−λt); λ = ln2/t½',inputs:'time and half-life in same unit, initial amount',outputs:'remaining amount, activity in inverse input-time unit',assumptions:['Single exponential decay','Closed population']},
    binding:{title:'Nuclear binding energy',equation:'Eb = Δmc²',inputs:'Z, N, neutral atomic mass [u]',outputs:'mass defect [u], energy [MeV]',assumptions:['Atomic electron masses subtracted','Tabulated mass conventions']},
    relativistic:{title:'Relativistic kinematics',equation:'γ = 1/√(1−v²/c²)',inputs:'m [kg], v [m s⁻¹]',outputs:'energy [J], momentum [kg m s⁻¹]',assumptions:['Special relativity','Inertial frames']},
    invariantMass:{title:'Invariant mass reconstruction',equation:'m² = E² − |p|² (c=1)',inputs:'four-vectors in consistent natural units',outputs:'invariant mass in matching energy unit',assumptions:['All vectors share units and frame convention']},
    twoBodyDecay:{title:'Two-body decay',equation:'p = √[(M²−(m₁+m₂)²)(M²−(m₁−m₂)²)]/(2M)',inputs:'masses in one consistent unit',outputs:'momentum and energy in that unit (c=1)',assumptions:['Parent rest frame','On-shell daughters']},
    detector:{title:'Detector and track reconstruction',equation:'pT [GeV/c] = 0.299792458 |q|Br',inputs:'B [T], r [m], distance [m], time [s], event counts',outputs:'pT [GeV/c], β, significance, cross section',assumptions:['Uniform field','Transverse circular track','Simple counting statistics']},
    uncertainty:{title:'Independent uncertainty combination',equation:'u = √Σuᵢ²',inputs:'standard uncertainties in a common output unit',outputs:'combined and k=2 expanded uncertainty',assumptions:['Independent uncorrelated standard uncertainties']},
    powerLawUncertainty:{title:'Power-law uncertainty propagation',equation:'y = C∏xᵢᵖⁱ; (uᵧ/y)² = Σ(pᵢuᵢ/xᵢ)²',inputs:'variables with value, standard uncertainty, and power',outputs:'y, standard and expanded uncertainty',assumptions:['Independent small uncertainties','First-order propagation']},
    weightedMean:{title:'Uncertainty-weighted mean',equation:'x̄ = Σ(xᵢ/uᵢ²)/Σ(1/uᵢ²)',inputs:'measurements with standard uncertainties',outputs:'weighted mean, uncertainty, χ², reduced χ²',assumptions:['Independent normally distributed measurements']}
  };

  function finiteEntries(value, path = 'result', rows = []) {
    if (typeof value === 'number') {
      rows.push({ path, finite: Number.isFinite(value), value });
    } else if (Array.isArray(value)) {
      value.forEach((item, index) => finiteEntries(item, `${path}[${index}]`, rows));
    } else if (value && typeof value === 'object') {
      Object.entries(value).forEach(([key, item]) => key !== 'series' && finiteEntries(item, `${path}.${key}`, rows));
    }
    return rows;
  }

  function check(label, passed, severity = 'error', detail = '') {
    return { label, passed: Boolean(passed), severity, detail };
  }

  function validate(id, input, result) {
    const checks = [];
    const warnings = [];
    const numeric = finiteEntries(result);
    const badFinite = numeric.filter(row => !row.finite);
    checks.push(check('Finite numerical outputs', badFinite.length === 0, 'error', badFinite.map(row => row.path).join(', ')));

    const x = key => Number(input?.[key]);
    switch (id) {
      case 'projectile':
        checks.push(check('Launch angle is within a conventional 0–90° trajectory domain', x('angle') >= 0 && x('angle') <= 90, 'warning'));
        if (x('y0') < 0) warnings.push('Initial height is below the selected reference plane.');
        break;
      case 'pendulum': {
        const amplitude = Math.abs(x('amplitude'));
        checks.push(check('Finite-amplitude series is used within 45°', amplitude <= 45, 'warning', `Amplitude: ${amplitude}°`));
        if (amplitude > 15) warnings.push('Small-angle period alone would be inaccurate; use the finite-amplitude value and validate experimentally.');
        break;
      }
      case 'idealGas':
        if (x('temperature') < 150 || x('pressure') > 1e7) warnings.push('Ideal-gas behavior may be poor at low temperature or high pressure.');
        break;
      case 'thermodynamics':
        checks.push(check('Carnot efficiency lies between 0 and 1', result.carnotEfficiency >= 0 && result.carnotEfficiency < 1));
        break;
      case 'fluid':
        warnings.push('Laminar/transitional/turbulent thresholds depend on geometry, roughness, and disturbance conditions.');
        break;
      case 'bernoulli':
        if (result.p2 < 0) warnings.push('Calculated absolute pressure is negative; check whether pressures are gauge or absolute and include losses/cavitation constraints.');
        break;
      case 'optics':
        if (!Number.isFinite(result.imageDistance)) warnings.push('Object distance is at the focal plane; the ideal thin-lens image is at infinity.');
        if (result.totalInternalReflection) warnings.push('No transmitted refracted ray exists in the ideal interface model.');
        break;
      case 'pointField':
        if (!String(input.charges || '').trim()) checks.push(check('At least one point charge is supplied', false));
        break;
      case 'capacitor':
        if (!String(input.capacitances || '').trim()) checks.push(check('At least one capacitance is supplied', false));
        break;
      case 'lorentz': {
        const beta = x('v') / Physics.constants.c;
        checks.push(check('Speed remains below c', beta < 1));
        if (beta > 0.1) warnings.push('Orbit radius uses non-relativistic momentum; use relativistic momentum for high-speed particles.');
        break;
      }
      case 'rlc':
        checks.push(check('Power factor is physically bounded', Math.abs(result.powerFactor) <= 1 + 1e-12));
        break;
      case 'frequencySweep':
        checks.push(check('Maximum frequency exceeds minimum frequency', x('fmax') > x('fmin')));
        break;
      case 'emWave':
        if (x('conductivity') < 1e3) warnings.push('The good-conductor skin-depth approximation may be inappropriate at the supplied conductivity.');
        break;
      case 'waveguide':
        if (!result.aboveCutoff) warnings.push('Operating frequency is below TE10 cutoff; the ideal propagating guide wavelength is undefined.');
        break;
      case 'particleBox':
      case 'hydrogen':
        checks.push(check('Quantum numbers are positive integers', Object.entries(input).filter(([key]) => ['n','ni','nf'].includes(key)).every(([,value]) => Number.isInteger(Number(value)) && Number(value) > 0)));
        break;
      case 'tunneling':
        if (result.regime === 'above barrier') warnings.push('The exponential tunneling approximation is bypassed because particle energy is at or above the barrier.');
        break;
      case 'binding':
        checks.push(check('Binding energy is positive', result.bindingEnergyMeV > 0));
        break;
      case 'relativistic': {
        const beta = x('velocity') / Physics.constants.c;
        checks.push(check('Speed remains below c', beta < 1));
        if (beta > 0.99) warnings.push('Results are highly sensitive to velocity near c; propagate velocity uncertainty carefully.');
        break;
      }
      case 'invariantMass':
        checks.push(check('Combined four-vector is timelike or null', result.massSquared >= -1e-10, 'warning', `m² = ${result.massSquared}`));
        break;
      case 'detector':
        checks.push(check('Time-of-flight velocity does not exceed c', result.beta <= 1 + 1e-9));
        checks.push(check('Efficiency is in the interval (0,1]', x('efficiency') > 0 && x('efficiency') <= 1));
        if (x('background') > x('events')) warnings.push('Background exceeds observed events; the clipped signal estimate is zero.');
        break;
      case 'weightedMean':
        if (result.reducedChiSquare > 2) warnings.push('Reduced χ² is high; measurements may be inconsistent or uncertainties underestimated.');
        break;
    }

    const failedErrors = checks.filter(item => !item.passed && item.severity === 'error');
    const failedWarnings = checks.filter(item => !item.passed && item.severity === 'warning');
    const status = failedErrors.length ? 'invalid' : (failedWarnings.length || warnings.length ? 'warning' : 'validated');
    return {
      status,
      checks,
      warnings,
      method: metadata[id] || { title:id, equation:'Method-specific relation', inputs:'Use stated SI or documented natural units', outputs:'See result record', assumptions:['Review method documentation'] },
      constantsVersion:'SI exact constants and CODATA-compatible values embedded in Lab v0.4.1',
      validatedAt:new Date().toISOString()
    };
  }

  function parseJson(value, label) {
    try { return typeof value === 'string' ? JSON.parse(value) : value; }
    catch (_) { throw new Error(`${label} must be valid JSON`); }
  }

  Physics.tools.powerLawUncertainty = function (input) {
    const coefficient = Number(input.coefficient ?? 1);
    if (!Number.isFinite(coefficient)) throw new Error('Invalid coefficient');
    const variables = parseJson(input.variables, 'Variables');
    if (!Array.isArray(variables) || !variables.length) throw new Error('Provide at least one variable');
    let value = coefficient;
    let relativeVariance = 0;
    const terms = variables.map((row, index) => {
      const x = Number(row.value), u = Number(row.uncertainty), power = Number(row.power ?? 1);
      if (!Number.isFinite(x) || x === 0) throw new Error(`Variable ${index + 1} value must be finite and nonzero`);
      if (!Number.isFinite(u) || u < 0) throw new Error(`Variable ${index + 1} uncertainty must be nonnegative`);
      if (!Number.isFinite(power)) throw new Error(`Variable ${index + 1} power is invalid`);
      value *= Math.pow(x, power);
      const contribution = Math.pow(power * u / x, 2);
      relativeVariance += contribution;
      return { name:row.name || `x${index + 1}`, value:x, standardUncertainty:u, power, relativeVarianceContribution:contribution };
    });
    const relativeStandardUncertainty = Math.sqrt(relativeVariance);
    const standardUncertainty = Math.abs(value) * relativeStandardUncertainty;
    return { value, standardUncertainty, expandedUncertaintyK2:2 * standardUncertainty, relativeStandardUncertainty, terms };
  };

  Physics.tools.weightedMean = function (input) {
    const measurements = parseJson(input.measurements, 'Measurements');
    if (!Array.isArray(measurements) || measurements.length < 2) throw new Error('Provide at least two measurements');
    let sumWeights = 0, weighted = 0;
    const rows = measurements.map((row, index) => {
      const value = Number(row.value), uncertainty = Number(row.uncertainty);
      if (!Number.isFinite(value)) throw new Error(`Measurement ${index + 1} value is invalid`);
      if (!Number.isFinite(uncertainty) || !(uncertainty > 0)) throw new Error(`Measurement ${index + 1} uncertainty must be greater than zero`);
      const weight = 1 / (uncertainty * uncertainty);
      sumWeights += weight; weighted += weight * value;
      return { value, uncertainty, weight };
    });
    const mean = weighted / sumWeights;
    const standardUncertainty = Math.sqrt(1 / sumWeights);
    const chiSquare = rows.reduce((sum, row) => sum + row.weight * Math.pow(row.value - mean, 2), 0);
    const degreesOfFreedom = rows.length - 1;
    const reducedChiSquare = chiSquare / degreesOfFreedom;
    return { weightedMean:mean, standardUncertainty, expandedUncertaintyK2:2 * standardUncertainty, chiSquare, degreesOfFreedom, reducedChiSquare, birgeRatio:Math.sqrt(Math.max(0, reducedChiSquare)), measurements:rows };
  };

  Object.keys(Physics.tools).forEach(id => {
    const original = Physics.tools[id];
    if (original._scValidationWrapped) return;
    const wrapped = function (input) {
      const result = original(input);
      const validation = validate(id, input, result);
      return Object.assign({}, result, { _validation:validation, _method:validation.method });
    };
    wrapped._scValidationWrapped = true;
    Physics.tools[id] = wrapped;
  });

  const benchmarks = [
    {id:'kinematics-final-velocity',tool:'kinematics',input:{vi:5,a:2,t:10},path:'finalVelocity',expected:25,tolerance:1e-12},
    {id:'kinematics-displacement',tool:'kinematics',input:{vi:5,a:2,t:10},path:'displacement',expected:150,tolerance:1e-12},
    {id:'projectile-range-45deg',tool:'projectile',input:{v:20,angle:45,y0:0,g:9.80665},path:'range',expected:400/9.80665,tolerance:1e-9},
    {id:'pendulum-one-meter',tool:'pendulum',input:{length:1,amplitude:0,g:9.80665},path:'smallAnglePeriod',expected:2*Math.PI*Math.sqrt(1/9.80665),tolerance:1e-12},
    {id:'coulomb-reference',tool:'coulomb',input:{q1:1e-6,q2:-2e-6,r:0.25},path:'forceMagnitude',expected:(1/(4*Math.PI*Physics.constants.eps0))*2e-12/0.0625,tolerance:1e-9},
    {id:'rlc-resonance-phase',tool:'rlc',input:{R:100,L:0.01,C:1e-6,frequency:1/(2*Math.PI*Math.sqrt(0.01e-6)),voltage:10},path:'phaseDegrees',expected:0,tolerance:1e-8},
    {id:'photon-500nm',tool:'photon',input:{wavelengthNm:500},path:'energyEv',expected:2.479683968664005,tolerance:1e-9},
    {id:'two-half-lives',tool:'decay',input:{halfLife:10,time:20,initial:1000},path:'remaining',expected:250,tolerance:1e-10},
    {id:'massless-two-body-decay',tool:'twoBodyDecay',input:{parentMass:125.25,mass1:0,mass2:0},path:'daughterMomentum',expected:62.625,tolerance:1e-12}
  ];

  function getPath(object, path) { return path.split('.').reduce((value, key) => value?.[key], object); }
  function runBenchmarks() {
    const rows = benchmarks.map(test => {
      try {
        const result = Physics.tools[test.tool](test.input);
        const actual = Number(getPath(result, test.path));
        const absoluteError = Math.abs(actual - test.expected);
        const scale = Math.max(1, Math.abs(test.expected));
        const passed = Number.isFinite(actual) && absoluteError <= test.tolerance * scale;
        return Object.assign({}, test, { actual, absoluteError, passed });
      } catch (error) {
        return Object.assign({}, test, { actual:null, absoluteError:null, passed:false, error:error.message });
      }
    });
    return { passed:rows.filter(row => row.passed).length, failed:rows.filter(row => !row.passed).length, total:rows.length, rows, runAt:new Date().toISOString(), version:'0.4.1' };
  }

  function cleanResult(result) {
    const copy = Object.assign({}, result);
    delete copy.series;
    return copy;
  }

  function formatNumber(value) {
    if (!Number.isFinite(Number(value))) return String(value);
    const number = Number(value);
    if (number === 0) return '0';
    if (Math.abs(number) >= 1e5 || Math.abs(number) < 1e-4) return number.toExponential(5);
    return Number(number.toPrecision(7)).toString();
  }

  function advancedSvg(series, options = {}) {
    const sets = Array.isArray(series?.[0]?.series) ? series : [{ label:options.label || 'Result', series:series || [] }];
    const points = sets.flatMap(set => set.series || []).filter(point => Number.isFinite(Number(point.x)) && Number.isFinite(Number(point.y)));
    if (points.length < 2) return '<div class="sc-lab-data-note">No plottable series.</div>';
    const logX = Boolean(options.logX) && points.every(point => Number(point.x) > 0);
    const tx = value => logX ? Math.log10(Number(value)) : Number(value);
    const xs = points.map(point => tx(point.x)), ys = points.map(point => Number(point.y));
    let xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys);
    if (xmin === xmax) { xmin -= 0.5; xmax += 0.5; }
    if (ymin === ymax) { ymin -= Math.abs(ymin || 1) * 0.1; ymax += Math.abs(ymax || 1) * 0.1; }
    const ypad=(ymax-ymin)*0.08; ymin-=ypad; ymax+=ypad;
    const W=760,H=330,L=68,R=24,T=28,B=54;
    const sx=x=>L+(tx(x)-xmin)/(xmax-xmin)*(W-L-R);
    const sy=y=>H-B-(Number(y)-ymin)/(ymax-ymin)*(H-T-B);
    const colors=['#d00000','#1d5f8a','#3d7a4f','#7a4b8f'];
    const ticks=5;
    const grid=[];
    for(let i=0;i<=ticks;i++){
      const xp=L+i*(W-L-R)/ticks, yp=T+i*(H-T-B)/ticks;
      const xv=xmin+i*(xmax-xmin)/ticks, yv=ymax-i*(ymax-ymin)/ticks;
      grid.push(`<line x1="${xp}" y1="${T}" x2="${xp}" y2="${H-B}" stroke="#e4e9ed"/><text x="${xp}" y="${H-B+18}" font-size="10" text-anchor="middle" fill="#53616b">${U.esc(formatNumber(logX?Math.pow(10,xv):xv))}</text>`);
      grid.push(`<line x1="${L}" y1="${yp}" x2="${W-R}" y2="${yp}" stroke="#e4e9ed"/><text x="${L-8}" y="${yp+3}" font-size="10" text-anchor="end" fill="#53616b">${U.esc(formatNumber(yv))}</text>`);
    }
    if (ymin < 0 && ymax > 0) grid.push(`<line x1="${L}" y1="${sy(0)}" x2="${W-R}" y2="${sy(0)}" stroke="#8e989f" stroke-dasharray="4 4"/>`);
    const paths=sets.map((set,index)=>{
      const valid=(set.series||[]).filter(point=>Number.isFinite(Number(point.x))&&Number.isFinite(Number(point.y))&&(logX?Number(point.x)>0:true));
      const path=valid.map((point,n)=>`${n?'L':'M'}${sx(point.x).toFixed(2)},${sy(point.y).toFixed(2)}`).join(' ');
      return `<path d="${path}" fill="none" stroke="${colors[index%colors.length]}" stroke-width="2.2" vector-effect="non-scaling-stroke"/>`;
    }).join('');
    const legend=sets.map((set,index)=>`<g transform="translate(${L+index*150},16)"><line x1="0" y1="0" x2="18" y2="0" stroke="${colors[index%colors.length]}" stroke-width="3"/><text x="24" y="3" font-size="10" fill="#303940">${U.esc(set.label || `Series ${index+1}`)}</text></g>`).join('');
    return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="sc-physics-plot-title sc-physics-plot-desc"><title id="sc-physics-plot-title">${U.esc(options.title||options.label||'Physics visualization')}</title><desc id="sc-physics-plot-desc">Validated numerical visualization generated by Sustainable Catalyst Lab.</desc><rect width="${W}" height="${H}" fill="#fff"/>${grid.join('')}<line x1="${L}" y1="${H-B}" x2="${W-R}" y2="${H-B}" stroke="#53616b"/><line x1="${L}" y1="${T}" x2="${L}" y2="${H-B}" stroke="#53616b"/>${paths}${legend}<text x="${(L+W-R)/2}" y="${H-12}" font-size="11" text-anchor="middle" fill="#303940">${U.esc(options.xLabel || (logX?'x (log scale)':'x'))}</text><text x="16" y="${(T+H-B)/2}" font-size="11" text-anchor="middle" fill="#303940" transform="rotate(-90 16 ${(T+H-B)/2})">${U.esc(options.yLabel||'y')}</text></svg>`;
  }

  function seriesCsv(series) {
    return ['x,y'].concat((series || []).map(point => `${point.x},${point.y}`)).join('\n');
  }

  function renderValidation(card, run) {
    let box = card.querySelector('[data-physics-validation]');
    if (!box) {
      box = document.createElement('div');
      box.dataset.physicsValidation = '';
      card.querySelector('[data-physics-output]')?.before(box);
    }
    const v = run.result._validation;
    const failed = v.checks.filter(item => !item.passed);
    box.className = `sc-lab-physics-validation is-${v.status}`;
    box.innerHTML = `<div class="sc-lab-validation-head"><strong>${U.esc(v.status.toUpperCase())}</strong><span>${U.esc(v.method.title)}</span></div><div class="sc-lab-validation-method"><code>${U.esc(v.method.equation)}</code><small>${U.esc(v.method.inputs)} → ${U.esc(v.method.outputs)}</small></div>${failed.length?`<ul>${failed.map(item=>`<li>${U.esc(item.label)}${item.detail?`: ${U.esc(item.detail)}`:''}</li>`).join('')}</ul>`:''}${v.warnings.length?`<ul>${v.warnings.map(item=>`<li>${U.esc(item)}</li>`).join('')}</ul>`:''}`;
  }

  function addMethodSummary(card, id) {
    if (card.querySelector('[data-physics-method-summary]')) return;
    const meta=metadata[id]; if(!meta)return;
    const details=document.createElement('details'); details.className='sc-lab-physics-method'; details.dataset.physicsMethodSummary='';
    details.innerHTML=`<summary>Method, units, and assumptions</summary><p><strong>Equation:</strong> <code>${U.esc(meta.equation)}</code></p><p><strong>Inputs:</strong> ${U.esc(meta.inputs)}</p><p><strong>Outputs:</strong> ${U.esc(meta.outputs)}</p><ul>${meta.assumptions.map(item=>`<li>${U.esc(item)}</li>`).join('')}</ul>`;
    card.querySelector('h4')?.after(details);
  }

  function enhanceChart(card) {
    const chart=card.querySelector('[data-physics-chart]'); if(!chart)return;
    const id=card.dataset.physicsTool;
    let actions=card.querySelector('[data-physics-chart-actions]');
    if(!actions){
      actions=document.createElement('div');actions.className='sc-lab-inline-actions sc-lab-physics-chart-actions';actions.dataset.physicsChartActions='';
      actions.innerHTML='<button type="button" class="sc-lab-button" data-physics-baseline>Set comparison baseline</button><button type="button" class="sc-lab-button" data-physics-export-svg>Export SVG</button><button type="button" class="sc-lab-button" data-physics-export-csv>Export CSV</button>';
      chart.after(actions);
    }
    actions.querySelector('[data-physics-baseline]').addEventListener('click',()=>{
      if(!card._lastPhysics?.result?.series)return U.toast(card.closest('.sc-lab-app'),'Run the model first.');
      card._physicsBaseline={label:'Baseline',series:card._lastPhysics.result.series.map(point=>Object.assign({},point))};
      U.toast(card.closest('.sc-lab-app'),'Comparison baseline stored. Change inputs and run again.');
    });
    actions.querySelector('[data-physics-export-svg]').addEventListener('click',()=>{
      const svg=chart.querySelector('svg');if(!svg)return U.toast(card.closest('.sc-lab-app'),'Generate a plot first.');
      U.download(`${id}-physics-plot.svg`,new XMLSerializer().serializeToString(svg),'image/svg+xml');
    });
    actions.querySelector('[data-physics-export-csv]').addEventListener('click',()=>{
      const series=card._lastPhysics?.result?.series;if(!series)return U.toast(card.closest('.sc-lab-app'),'Generate a series first.');
      U.download(`${id}-physics-series.csv`,seriesCsv(series),'text/csv');
    });
  }

  const originalInit = Physics.init;
  Physics.init = function (root, projects) {
    originalInit(root, projects);
    const panel=root.querySelector('[data-lab-module="physics"]');if(!panel)return;
    panel.querySelectorAll('[data-physics-tool]').forEach(card=>{
      const id=card.dataset.physicsTool;addMethodSummary(card,id);enhanceChart(card);
      card.querySelector('[data-physics-run]')?.addEventListener('click',()=>{
        const run=card._lastPhysics;if(!run)return;
        renderValidation(card,run);
        const chart=card.querySelector('[data-physics-chart]');
        if(chart&&run.result.series){
          const sets=card._physicsBaseline?[card._physicsBaseline,{label:'Current',series:run.result.series}]:run.result.series;
          const chartMeta={label:metadata[id]?.title||id,title:metadata[id]?.title||id,xLabel:id==='projectile'?'Horizontal distance (m)':id==='frequencySweep'?'Frequency (Hz)':id==='wave'?'Position (m)':'x',yLabel:id==='projectile'?'Height (m)':id==='frequencySweep'?'Response (dB)':id==='wave'?'Amplitude':'y',logX:id==='frequencySweep'};
          chart.innerHTML=advancedSvg(sets,chartMeta);
        }
      });
    });

    const benchmarkOutput=panel.querySelector('[data-physics-benchmark-output]');
    const benchmarkTable=panel.querySelector('[data-physics-benchmark-table]');
    const runButton=panel.querySelector('[data-physics-run-benchmarks]');
    const exportButton=panel.querySelector('[data-physics-export-validation]');
    let lastReport=null;
    function renderReport(report){
      lastReport=report;
      if(benchmarkOutput)benchmarkOutput.innerHTML=`<strong>${report.passed}/${report.total} benchmark cases passed</strong><span class="${report.failed?'is-failed':'is-passed'}">${report.failed?`${report.failed} failed`:'Validation suite clean'}</span><small>${U.esc(new Date(report.runAt).toLocaleString())}</small>`;
      if(benchmarkTable)benchmarkTable.innerHTML=`<table><thead><tr><th>Case</th><th>Method</th><th>Expected</th><th>Actual</th><th>Error</th><th>Status</th></tr></thead><tbody>${report.rows.map(row=>`<tr><td>${U.esc(row.id)}</td><td>${U.esc(row.tool)}</td><td>${U.esc(formatNumber(row.expected))}</td><td>${U.esc(row.actual===null?'—':formatNumber(row.actual))}</td><td>${U.esc(row.absoluteError===null?'—':formatNumber(row.absoluteError))}</td><td><span class="sc-lab-validation-badge ${row.passed?'is-passed':'is-failed'}">${row.passed?'PASS':'FAIL'}</span></td></tr>`).join('')}</tbody></table>`;
    }
    runButton?.addEventListener('click',()=>{
      const report=runBenchmarks();renderReport(report);
      projects.add('physicsValidationRecords',{type:'physics-benchmark-suite',report},`Physics validation suite: ${report.passed}/${report.total} passed`);
      U.toast(root,`Physics validation complete: ${report.passed}/${report.total} passed.`);
    });
    exportButton?.addEventListener('click',()=>{
      const report=lastReport||runBenchmarks();renderReport(report);U.download('physics-validation-report-v0.4.1.json',JSON.stringify(report,null,2),'application/json');
    });
  };

  Physics.validation={metadata,validate,benchmarks,runBenchmarks,advancedSvg,seriesCsv};
})(window);
