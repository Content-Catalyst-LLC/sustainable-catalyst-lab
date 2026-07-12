(function (w) {
  'use strict';
  const Lab = w.SCLab = w.SCLab || {};
  const U = Lab.util;
  const n = v => Number(v);
  const arr = v => Array.isArray(v) ? v : JSON.parse(v);
  const round = (x, d = 8) => Number.isFinite(x) ? Number(x.toPrecision(d)) : x;
  const positive = (v, name) => { const x = n(v); if (!(x > 0)) throw new Error(`${name} must be positive.`); return x; };
  const nonnegative = (v, name) => { const x = n(v); if (!(x >= 0)) throw new Error(`${name} must be nonnegative.`); return x; };
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const R = 8.31446261815324;
  const F = 96485.33212;
  const kB = 1.380649e-23;
  const q = 1.602176634e-19;
  const eps0 = 8.8541878128e-12;
  const h = 6.62607015e-34;
  const c = 299792458;
  const NA = 6.02214076e23;

  function linearRegression(points) {
    const p = arr(points).map(x => ({ x:n(x.x ?? x[0]), y:n(x.y ?? x[1]) })).filter(x => Number.isFinite(x.x) && Number.isFinite(x.y));
    if (p.length < 2) throw new Error('At least two finite points are required.');
    const xm = p.reduce((s,v)=>s+v.x,0)/p.length, ym = p.reduce((s,v)=>s+v.y,0)/p.length;
    const sxx = p.reduce((s,v)=>s+(v.x-xm)**2,0), sxy = p.reduce((s,v)=>s+(v.x-xm)*(v.y-ym),0);
    if (sxx === 0) throw new Error('The x values must vary.');
    const slope = sxy/sxx, intercept = ym-slope*xm;
    const ssTot = p.reduce((s,v)=>s+(v.y-ym)**2,0), ssRes = p.reduce((s,v)=>s+(v.y-(slope*v.x+intercept))**2,0);
    return { slope, intercept, r2:ssTot ? 1-ssRes/ssTot : 1, points:p };
  }
  function trapz(points) {
    const p = arr(points).map(x=>({x:n(x.x??x[0]),y:n(x.y??x[1])})).sort((a,b)=>a.x-b.x);
    if (p.length < 2) throw new Error('At least two points are required.');
    let area = 0; for (let i=1;i<p.length;i++) area += (p[i].x-p[i-1].x)*(p[i].y+p[i-1].y)/2;
    return area;
  }
  function mean(xs){return xs.reduce((s,v)=>s+v,0)/xs.length;}
  function std(xs){if(xs.length<2)return 0;const m=mean(xs);return Math.sqrt(xs.reduce((s,v)=>s+(v-m)**2,0)/(xs.length-1));}

  const rawTools = {
    engineeringStress({forceN,areaMm2}) { const f=n(forceN), a=positive(areaMm2,'Area'); return {stressMPa:round(f/a)}; },
    trueStressStrain({engineeringStressMPa,engineeringStrain}) { const s=n(engineeringStressMPa), e=n(engineeringStrain); if(e<=-1)throw new Error('Engineering strain must exceed -1.'); return {trueStressMPa:round(s*(1+e)),trueStrain:round(Math.log(1+e))}; },
    elasticConstants({youngsModulusGPa,poissonRatio}) { const E=positive(youngsModulusGPa,'Young modulus'),nu=n(poissonRatio); if(!(nu>-1&&nu<0.5))throw new Error('Poisson ratio must be between -1 and 0.5.'); return {shearModulusGPa:round(E/(2*(1+nu))),bulkModulusGPa:round(E/(3*(1-2*nu)))}; },
    resilience({yieldStrengthMPa,youngsModulusGPa}) { const sy=positive(yieldStrengthMPa,'Yield strength')*1e6,E=positive(youngsModulusGPa,'Young modulus')*1e9; return {modulusOfResilienceJm3:round(sy*sy/(2*E))}; },
    fractureK({stressMPa,crackMm,geometryFactor}) { const s=positive(stressMPa,'Stress')*1e6,a=positive(crackMm,'Crack length')/1000,Y=positive(geometryFactor,'Geometry factor'); return {stressIntensityMPaSqrtM:round(Y*s*Math.sqrt(Math.PI*a)/1e6)}; },
    basquin({fatigueStrengthCoefficientMPa,fatigueExponent,cycles}) { const sf=positive(fatigueStrengthCoefficientMPa,'Fatigue coefficient'), b=n(fatigueExponent), N=positive(cycles,'Cycles'); return {stressAmplitudeMPa:round(sf*Math.pow(2*N,b))}; },
    nortonCreep({coefficient,stressMPa,stressExponent,activationEnergyKJmol,tempK}) { const A=positive(coefficient,'Coefficient'),s=positive(stressMPa,'Stress'),nn=positive(stressExponent,'Stress exponent'),Q=nonnegative(activationEnergyKJmol,'Activation energy')*1000,T=positive(tempK,'Temperature'); return {creepRatePerS:round(A*Math.pow(s,nn)*Math.exp(-Q/(R*T)),12)}; },

    thermalExpansion({alphaMicroPerK,lengthM,deltaK}) { const a=n(alphaMicroPerK)*1e-6,L=positive(lengthM,'Length'),dT=n(deltaK); return {lengthChangeM:round(a*L*dT),finalLengthM:round(L*(1+a*dT))}; },
    steadyConduction({conductivityWmK,areaM2,deltaK,lengthM}) { const k=positive(conductivityWmK,'Conductivity'),A=positive(areaM2,'Area'),L=positive(lengthM,'Length'); return {heatFlowW:round(k*A*n(deltaK)/L)}; },
    thermalDiffusivity({conductivityWmK,densityKgM3,specificHeatJkgK}) { const k=positive(conductivityWmK,'Conductivity'),rho=positive(densityKgM3,'Density'),cp=positive(specificHeatJkgK,'Specific heat'); return {thermalDiffusivityM2S:round(k/(rho*cp),12)}; },
    thermalShock({fractureStrengthMPa,conductivityWmK,youngsModulusGPa,alphaMicroPerK,poissonRatio}) { const sf=positive(fractureStrengthMPa,'Fracture strength')*1e6,k=positive(conductivityWmK,'Conductivity'),E=positive(youngsModulusGPa,'Young modulus')*1e9,a=positive(alphaMicroPerK,'Expansion coefficient')*1e-6,nu=n(poissonRatio); return {thermalShockParameterWKPerM:round(sf*k*(1-nu)/(E*a))}; },
    dscEnthalpy({points,heatingRateKMin,sampleMassMg}) { const area=trapz(points),rate=positive(heatingRateKMin,'Heating rate')/60,mass=positive(sampleMassMg,'Sample mass')/1e6; return {integratedSignal:round(area),specificEnthalpyJkg:round(area/(rate*mass))}; },

    resistivity({resistanceOhm,areaMm2,lengthM}) { const r=positive(resistanceOhm,'Resistance'),A=positive(areaMm2,'Area')*1e-6,L=positive(lengthM,'Length'); const rho=r*A/L; return {resistivityOhmM:round(rho,12),conductivitySm:round(1/rho)}; },
    tempResistivity({rho0OhmM,alphaPerK,tempC,referenceC}) { const rho=positive(rho0OhmM,'Reference resistivity'),a=n(alphaPerK),dT=n(tempC)-n(referenceC); return {resistivityOhmM:round(rho*(1+a*dT),12)}; },
    hallEffect({hallVoltageV,currentA,thicknessMm,magneticFieldT,chargeSign}) { const V=n(hallVoltageV),I=positive(currentA,'Current'),t=positive(thicknessMm,'Thickness')/1000,B=positive(magneticFieldT,'Magnetic field'),sign=n(chargeSign)||1,Rh=V*t/(I*B),carrier=1/(Math.abs(Rh)*q); return {hallCoefficientM3C:round(Rh,12),carrierDensityM3:round(carrier),carrierType:sign<0?'electron-like':'hole-like'}; },
    dielectricCapacitance({relativePermittivity,areaCm2,thicknessMm}) { const er=positive(relativePermittivity,'Relative permittivity'),A=positive(areaCm2,'Area')*1e-4,d=positive(thicknessMm,'Thickness')/1000; return {capacitanceF:round(eps0*er*A/d,12)}; },
    intrinsicCarrier({bandGapEv,tempK,NcM3,NvM3}) { const Eg=positive(bandGapEv,'Band gap')*q,T=positive(tempK,'Temperature'),Nc=positive(NcM3,'Nc'),Nv=positive(NvM3,'Nv'); return {intrinsicCarrierDensityM3:round(Math.sqrt(Nc*Nv)*Math.exp(-Eg/(2*kB*T)))}; },

    curieWeiss({curieConstantK,tempK,curieTempK}) { const Cc=positive(curieConstantK,'Curie constant'),T=n(tempK),Tc=n(curieTempK); if(T===Tc)throw new Error('Temperature cannot equal the Curie temperature in this model.'); return {susceptibility:round(Cc/(T-Tc),12)}; },
    magneticMoment({magnetizationAm,volumeCm3}) { return {magneticMomentAm2:round(n(magnetizationAm)*positive(volumeCm3,'Volume')*1e-6,12)}; },
    hysteresisLoss({points,frequencyHz,densityKgM3}) { const area=Math.abs(trapz(points)),f=positive(frequencyHz,'Frequency'),rho=positive(densityKgM3,'Density'); return {loopEnergyJm3:round(area),powerLossWm3:round(area*f),specificPowerLossWkg:round(area*f/rho)}; },
    energyProduct({remanenceT,coercivityAm}) { const B=positive(remanenceT,'Remanence'),H=positive(coercivityAm,'Coercivity'); return {estimatedMaxEnergyProductJm3:round(B*H/4)}; },

    reflectanceIndex({refractiveIndex,extinctionCoefficient}) { const nn=positive(refractiveIndex,'Refractive index'),kappa=nonnegative(extinctionCoefficient,'Extinction coefficient'); return {normalReflectance:round(((nn-1)**2+kappa**2)/((nn+1)**2+kappa**2),12)}; },
    absorptionCoefficient({transmittanceFraction,thicknessMm}) { const T=positive(transmittanceFraction,'Transmittance'),d=positive(thicknessMm,'Thickness')/1000; if(T>1)throw new Error('Transmittance fraction must not exceed 1.'); return {absorptionCoefficientPerM:round(-Math.log(T)/d)}; },
    taucBandGap({points,transitionPower}) { const p=positive(transitionPower,'Transition power'),data=arr(points).map(x=>({x:n(x.x??x[0]),y:Math.pow(Math.max(0,n(x.y??x[1]))*n(x.x??x[0]),p)})); const fit=linearRegression(data); return {bandGapEv:round(-fit.intercept/fit.slope,10),slope:round(fit.slope),intercept:round(fit.intercept),r2:round(fit.r2,10),series:data}; },
    opticalPath({refractiveIndex,lengthMm}) { return {opticalPathMm:round(positive(refractiveIndex,'Refractive index')*positive(lengthMm,'Length'))}; },

    braggLaw({wavelengthNm,twoThetaDeg,order}) { const lambda=positive(wavelengthNm,'Wavelength')*1e-9,theta=n(twoThetaDeg)*Math.PI/360,m=positive(order,'Order'); const d=m*lambda/(2*Math.sin(theta)); return {dSpacingM:round(d,12),dSpacingAngstrom:round(d*1e10,10)}; },
    cubicDSpacing({latticeParameterAngstrom,h,k,l}) { const a=positive(latticeParameterAngstrom,'Lattice parameter'),den=Math.sqrt(n(h)**2+n(k)**2+n(l)**2); if(!den)throw new Error('At least one Miller index must be nonzero.'); return {dSpacingAngstrom:round(a/den,10)}; },
    latticeFromPeak({wavelengthNm,twoThetaDeg,h,k,l,order}) { const d=rawTools.braggLaw({wavelengthNm,twoThetaDeg,order}).dSpacingAngstrom,den=Math.sqrt(n(h)**2+n(k)**2+n(l)**2); if(!den)throw new Error('At least one Miller index must be nonzero.'); return {latticeParameterAngstrom:round(d*den,10),dSpacingAngstrom:d}; },
    scherrer({wavelengthNm,fwhmDeg,twoThetaDeg,shapeFactor}) { const lam=positive(wavelengthNm,'Wavelength')*1e-9,beta=positive(fwhmDeg,'FWHM')*Math.PI/180,theta=n(twoThetaDeg)*Math.PI/360,K=positive(shapeFactor,'Shape factor'); return {crystalliteSizeNm:round(K*lam/(beta*Math.cos(theta))*1e9,10)}; },
    crystalDensity({formulaMassGmol,atomsPerCell,latticeAangstrom,latticeBangstrom,latticeCangstrom}) { const M=positive(formulaMassGmol,'Formula mass')/1000,Z=positive(atomsPerCell,'Formula units per cell'),a=positive(latticeAangstrom,'a')*1e-10,b=positive(latticeBangstrom,'b')*1e-10,c0=positive(latticeCangstrom,'c')*1e-10; return {densityKgM3:round(Z*M/(NA*a*b*c0)),densityGcm3:round(Z*M/(NA*a*b*c0)/1000)}; },

    leverRule({composition,alphaComposition,betaComposition}) { const C0=n(composition),Ca=n(alphaComposition),Cb=n(betaComposition); if(Cb===Ca)throw new Error('Phase compositions must differ.'); const fa=(Cb-C0)/(Cb-Ca),fb=(C0-Ca)/(Cb-Ca); return {alphaFraction:round(fa,10),betaFraction:round(fb,10)}; },
    gibbsPhaseRule({components,phases,variables}) { const Cc=positive(components,'Components'),P=positive(phases,'Phases'),v=n(variables); return {degreesOfFreedom:round(Cc-P+v)}; },
    arrheniusDiffusion({preExponentialM2S,activationEnergyKJmol,tempK}) { const D0=positive(preExponentialM2S,'Pre-exponential factor'),Q=nonnegative(activationEnergyKJmol,'Activation energy')*1000,T=positive(tempK,'Temperature'); return {diffusivityM2S:round(D0*Math.exp(-Q/(R*T)),12)}; },
    diffusionLength({diffusivityM2S,timeS,dimensions}) { const D=positive(diffusivityM2S,'Diffusivity'),t=positive(timeS,'Time'),dim=positive(dimensions,'Dimensions'); return {rmsDiffusionLengthM:round(Math.sqrt(2*dim*D*t),12)}; },

    corrosionRate({massLossMg,densityGcm3,areaCm2,timeHours}) { const W=positive(massLossMg,'Mass loss'),rho=positive(densityGcm3,'Density'),A=positive(areaCm2,'Area'),t=positive(timeHours,'Time'); return {corrosionRateMmYr:round(87.6*W/(rho*A*t),10)}; },
    faradayCorrosion({currentA,timeS,molarMassGmol,electrons,densityGcm3,areaCm2}) { const I=positive(currentA,'Current'),tt=positive(timeS,'Time'),M=positive(molarMassGmol,'Molar mass'),z=positive(electrons,'Electrons'),rho=positive(densityGcm3,'Density'),A=positive(areaCm2,'Area'); const massG=I*tt*M/(z*F),depthCm=massG/(rho*A); return {massLossG:round(massG,10),penetrationMm:round(depthCm*10,10)}; },
    sternGeary({betaAnodicMvDec,betaCathodicMvDec,polarizationResistanceOhmCm2}) { const ba=positive(betaAnodicMvDec,'Anodic slope')/1000,bc=positive(betaCathodicMvDec,'Cathodic slope')/1000,Rp=positive(polarizationResistanceOhmCm2,'Polarization resistance'),B=ba*bc/(2.303*(ba+bc)); return {sternGearyConstantV:round(B,10),corrosionCurrentDensityAcm2:round(B/Rp,12)}; },

    degreePolymerization({numberAverageMassGmol,repeatUnitMassGmol}) { return {numberAverageDegreePolymerization:round(positive(numberAverageMassGmol,'Molecular mass')/positive(repeatUnitMassGmol,'Repeat-unit mass'),10)}; },
    foxTg({fractions,tgK}) { const wv=arr(fractions).map(Number),tv=arr(tgK).map(Number); if(wv.length!==tv.length||!wv.length)throw new Error('Fraction and Tg arrays must have equal nonzero length.'); const sum=wv.reduce((s,v)=>s+v,0); return {glassTransitionK:round(1/wv.reduce((s,v,i)=>s+(v/sum)/positive(tv[i],'Component Tg'),0),10)}; },
    crystallinityDSC({meltingEnthalpyJg,coldCrystallizationJg,referenceEnthalpyJg}) { const hm=n(meltingEnthalpyJg),hc=n(coldCrystallizationJg),href=positive(referenceEnthalpyJg,'Reference enthalpy'); return {crystallinityPercent:round((hm-hc)/href*100,10)}; },
    ruleOfMixtures({fiberFraction,fiberModulusGPa,matrixModulusGPa}) { const vf=clamp(n(fiberFraction),0,1),Ef=positive(fiberModulusGPa,'Fiber modulus'),Em=positive(matrixModulusGPa,'Matrix modulus'); return {longitudinalModulusGPa:round(vf*Ef+(1-vf)*Em,10),transverseModulusGPa:round(1/(vf/Ef+(1-vf)/Em),10)}; },
    halpinTsai({fiberFraction,fiberModulusGPa,matrixModulusGPa,shapeParameter}) { const vf=clamp(n(fiberFraction),0,0.999999),Ef=positive(fiberModulusGPa,'Fiber modulus'),Em=positive(matrixModulusGPa,'Matrix modulus'),xi=positive(shapeParameter,'Shape parameter'),eta=(Ef/Em-1)/(Ef/Em+xi); return {effectiveModulusGPa:round(Em*(1+xi*eta*vf)/(1-eta*vf),10)}; },
    compositeDensity({fiberFraction,fiberDensityGcm3,matrixDensityGcm3}) { const vf=clamp(n(fiberFraction),0,1); return {densityGcm3:round(vf*positive(fiberDensityGcm3,'Fiber density')+(1-vf)*positive(matrixDensityGcm3,'Matrix density'),10)}; },
    maxwellRelaxation({viscosityPaS,modulusPa,timeS}) { const eta=positive(viscosityPaS,'Viscosity'),E=positive(modulusPa,'Modulus'),t=nonnegative(timeS,'Time'); return {relaxationTimeS:round(eta/E,10),stressFraction:round(Math.exp(-t/(eta/E)),12)}; },

    particleStats({diameters}) { const xs=arr(diameters).map(Number).filter(x=>x>0); if(!xs.length)throw new Error('Enter positive particle diameters.'); const sorted=[...xs].sort((a,b)=>a-b),m=mean(xs),s=std(xs); const q=p=>sorted[Math.min(sorted.length-1,Math.max(0,Math.floor((sorted.length-1)*p)))]; return {count:xs.length,mean:round(m),standardDeviation:round(s),coefficientVariationPercent:round(s/m*100),d10:round(q(.1)),d50:round(q(.5)),d90:round(q(.9))}; },
    areaFraction({featurePixels,totalPixels}) { const f=nonnegative(featurePixels,'Feature pixels'),t=positive(totalPixels,'Total pixels'); if(f>t)throw new Error('Feature pixels cannot exceed total pixels.'); return {areaFraction:round(f/t,12),areaPercent:round(f/t*100,10)}; },
    grainIntercept({testLineLengthMm,intercepts,magnification}) { const L=positive(testLineLengthMm,'Test-line length')/positive(magnification,'Magnification'),N=positive(intercepts,'Intercepts'); return {meanLinearInterceptMm:round(L/N,10),meanLinearInterceptMicrometers:round(L/N*1000,10)}; },
    microscopyCalibration({knownDistanceUm,pixelDistance}) { return {micrometersPerPixel:round(positive(knownDistanceUm,'Known distance')/positive(pixelDistance,'Pixel distance'),12)}; },
    abbeResolution({wavelengthNm,numericalAperture}) { return {lateralResolutionNm:round(positive(wavelengthNm,'Wavelength')/(2*positive(numericalAperture,'Numerical aperture')),10)}; }
  };

  const specs = [
    ['engineeringStress','Engineering stress','mechanical','σ = F/A','mechanicalRecords',[['forceN','Force (N)','number','5000'],['areaMm2','Original area (mm²)','number','20']]],
    ['trueStressStrain','True stress and strain','mechanical','σt = σe(1+e); εt = ln(1+e)','mechanicalRecords',[['engineeringStressMPa','Engineering stress (MPa)','number','250'],['engineeringStrain','Engineering strain','number','0.12']]],
    ['elasticConstants','Elastic-constant conversion','mechanical','G=E/[2(1+ν)]; K=E/[3(1−2ν)]','mechanicalRecords',[['youngsModulusGPa','Young modulus (GPa)','number','210'],['poissonRatio','Poisson ratio','number','0.30']]],
    ['resilience','Modulus of resilience','mechanical','Ur = σy²/(2E)','mechanicalRecords',[['yieldStrengthMPa','Yield strength (MPa)','number','350'],['youngsModulusGPa','Young modulus (GPa)','number','210']]],
    ['fractureK','Mode-I stress intensity','mechanical','KI = Yσ√(πa)','mechanicalRecords',[['stressMPa','Applied stress (MPa)','number','120'],['crackMm','Crack length (mm)','number','2'],['geometryFactor','Geometry factor','number','1.12']]],
    ['basquin','Basquin fatigue relation','mechanical','σa = σf′(2N)^b','mechanicalRecords',[['fatigueStrengthCoefficientMPa','Fatigue coefficient (MPa)','number','1000'],['fatigueExponent','Fatigue exponent b','number','-0.09'],['cycles','Cycles N','number','1000000']]],
    ['nortonCreep','Norton–Arrhenius creep','mechanical','ε̇ = Aσⁿexp(−Q/RT)','mechanicalRecords',[['coefficient','Coefficient A','number','1e-20'],['stressMPa','Stress (MPa)','number','100'],['stressExponent','Stress exponent','number','4'],['activationEnergyKJmol','Activation energy (kJ/mol)','number','250'],['tempK','Temperature (K)','number','1000']]],

    ['thermalExpansion','Linear thermal expansion','thermal','ΔL = αLΔT','thermalRecords',[['alphaMicroPerK','α (µm/m·K)','number','12'],['lengthM','Length (m)','number','1'],['deltaK','Temperature change (K)','number','100']]],
    ['steadyConduction','Steady one-dimensional conduction','thermal','Q̇ = kAΔT/L','thermalRecords',[['conductivityWmK','Conductivity (W/m·K)','number','205'],['areaM2','Area (m²)','number','0.01'],['deltaK','Temperature difference (K)','number','50'],['lengthM','Length (m)','number','0.1']]],
    ['thermalDiffusivity','Thermal diffusivity','thermal','α = k/(ρcp)','thermalRecords',[['conductivityWmK','Conductivity (W/m·K)','number','205'],['densityKgM3','Density (kg/m³)','number','2700'],['specificHeatJkgK','Specific heat (J/kg·K)','number','900']]],
    ['thermalShock','Thermal-shock parameter','thermal','R = σfk(1−ν)/(Eα)','thermalRecords',[['fractureStrengthMPa','Fracture strength (MPa)','number','300'],['conductivityWmK','Conductivity (W/m·K)','number','25'],['youngsModulusGPa','Young modulus (GPa)','number','200'],['alphaMicroPerK','α (µm/m·K)','number','10'],['poissonRatio','Poisson ratio','number','0.28']]],
    ['dscEnthalpy','DSC enthalpy integration','thermal','ΔH = ∫signal dT /(βm)','thermalRecords',[['points','Temperature, signal points','textarea','[[50,0],[100,1],[150,2],[200,0]]'],['heatingRateKMin','Heating rate (K/min)','number','10'],['sampleMassMg','Sample mass (mg)','number','10']]],

    ['resistivity','Electrical resistivity','electrical','ρ = RA/L','electricalRecords',[['resistanceOhm','Resistance (Ω)','number','0.5'],['areaMm2','Area (mm²)','number','1'],['lengthM','Length (m)','number','1']]],
    ['tempResistivity','Temperature-dependent resistivity','electrical','ρ = ρ0[1+α(T−T0)]','electricalRecords',[['rho0OhmM','Reference resistivity (Ω·m)','number','1.68e-8'],['alphaPerK','Temperature coefficient (1/K)','number','0.0039'],['tempC','Temperature (°C)','number','100'],['referenceC','Reference temperature (°C)','number','20']]],
    ['hallEffect','Hall coefficient and carrier density','electrical','RH = VHt/(IB); n = 1/(|RH|q)','electricalRecords',[['hallVoltageV','Hall voltage (V)','number','0.001'],['currentA','Current (A)','number','0.01'],['thicknessMm','Thickness (mm)','number','0.5'],['magneticFieldT','Magnetic field (T)','number','1'],['chargeSign','Carrier sign (+1 holes, −1 electrons)','number','-1']]],
    ['dielectricCapacitance','Parallel-plate dielectric','electrical','C = ε0εrA/d','electricalRecords',[['relativePermittivity','Relative permittivity','number','4.2'],['areaCm2','Area (cm²)','number','1'],['thicknessMm','Thickness (mm)','number','0.1']]],
    ['intrinsicCarrier','Intrinsic carrier density','electrical','ni = √(NcNv)exp(−Eg/2kT)','electricalRecords',[['bandGapEv','Band gap (eV)','number','1.12'],['tempK','Temperature (K)','number','300'],['NcM3','Nc (m⁻³)','number','2.8e25'],['NvM3','Nv (m⁻³)','number','1.04e25']]],

    ['curieWeiss','Curie–Weiss susceptibility','magnetic','χ = C/(T−θ)','magneticRecords',[['curieConstantK','Curie constant (K)','number','1'],['tempK','Temperature (K)','number','350'],['curieTempK','Curie temperature (K)','number','300']]],
    ['magneticMoment','Magnetic moment','magnetic','m = MV','magneticRecords',[['magnetizationAm','Magnetization (A/m)','number','800000'],['volumeCm3','Volume (cm³)','number','1']]],
    ['hysteresisLoss','Hysteresis-loop energy loss','magnetic','W = |∮H dB|','magneticRecords',[['points','H,B loop points','textarea','[[-100000,0],[-50000,-0.8],[0,-1],[50000,-0.8],[100000,0],[50000,0.8],[0,1],[-50000,0.8],[-100000,0]]'],['frequencyHz','Frequency (Hz)','number','50'],['densityKgM3','Density (kg/m³)','number','7500']]],
    ['energyProduct','Estimated permanent-magnet energy product','magnetic','(BH)max ≈ BrHc/4','magneticRecords',[['remanenceT','Remanence Br (T)','number','1.2'],['coercivityAm','Coercivity Hc (A/m)','number','800000']]],

    ['reflectanceIndex','Normal-incidence reflectance','optical','R=[(n−1)²+k²]/[(n+1)²+k²]','opticalRecords',[['refractiveIndex','Refractive index n','number','1.5'],['extinctionCoefficient','Extinction coefficient k','number','0']]],
    ['absorptionCoefficient','Absorption coefficient','optical','α = −ln(T)/d','opticalRecords',[['transmittanceFraction','Transmittance fraction','number','0.5'],['thicknessMm','Thickness (mm)','number','1']]],
    ['taucBandGap','Tauc band-gap fit','optical','(αhν)^r versus hν','opticalRecords',[['points','Photon energy, absorption points','textarea','[[1.5,0.1],[1.7,0.2],[1.9,0.5],[2.1,0.9],[2.3,1.3]]'],['transitionPower','Transition power r','number','2']]],
    ['opticalPath','Optical path length','optical','OPL = nL','opticalRecords',[['refractiveIndex','Refractive index','number','1.5'],['lengthMm','Physical length (mm)','number','10']]],

    ['braggLaw','Bragg d-spacing','crystallography','nλ = 2d sinθ','crystallographyRecords',[['wavelengthNm','Wavelength (nm)','number','0.15406'],['twoThetaDeg','2θ (degrees)','number','44.7'],['order','Diffraction order','number','1']]],
    ['cubicDSpacing','Cubic d-spacing','crystallography','d = a/√(h²+k²+l²)','crystallographyRecords',[['latticeParameterAngstrom','Lattice parameter (Å)','number','3.615'],['h','h','number','1'],['k','k','number','1'],['l','l','number','1']]],
    ['latticeFromPeak','Cubic lattice parameter from peak','crystallography','a = d√(h²+k²+l²)','crystallographyRecords',[['wavelengthNm','Wavelength (nm)','number','0.15406'],['twoThetaDeg','2θ (degrees)','number','44.7'],['h','h','number','1'],['k','k','number','1'],['l','l','number','1'],['order','Order','number','1']]],
    ['scherrer','Scherrer crystallite size','crystallography','D = Kλ/(βcosθ)','crystallographyRecords',[['wavelengthNm','Wavelength (nm)','number','0.15406'],['fwhmDeg','FWHM (degrees)','number','0.2'],['twoThetaDeg','2θ (degrees)','number','44.7'],['shapeFactor','Shape factor K','number','0.9']]],
    ['crystalDensity','Unit-cell density','crystallography','ρ = ZM/(NₐVcell)','crystallographyRecords',[['formulaMassGmol','Formula mass (g/mol)','number','63.546'],['atomsPerCell','Formula units per cell','number','4'],['latticeAangstrom','a (Å)','number','3.615'],['latticeBangstrom','b (Å)','number','3.615'],['latticeCangstrom','c (Å)','number','3.615']]],

    ['leverRule','Binary phase lever rule','phase','fα=(Cβ−C0)/(Cβ−Cα)','phaseRecords',[['composition','Overall composition','number','40'],['alphaComposition','Alpha composition','number','20'],['betaComposition','Beta composition','number','80']]],
    ['gibbsPhaseRule','Gibbs phase rule','phase','F = C−P+V','phaseRecords',[['components','Components','number','2'],['phases','Phases','number','2'],['variables','Independent variables (usually 2)','number','2']]],
    ['arrheniusDiffusion','Arrhenius diffusivity','phase','D = D0 exp(−Q/RT)','phaseRecords',[['preExponentialM2S','D0 (m²/s)','number','1e-5'],['activationEnergyKJmol','Activation energy (kJ/mol)','number','200'],['tempK','Temperature (K)','number','1000']]],
    ['diffusionLength','Root-mean-square diffusion length','phase','Lrms = √(2nDt)','phaseRecords',[['diffusivityM2S','Diffusivity (m²/s)','number','1e-14'],['timeS','Time (s)','number','3600'],['dimensions','Dimensions n','number','1']]],

    ['corrosionRate','Weight-loss corrosion rate','corrosion','CR = 87.6W/(ρAt)','corrosionRecords',[['massLossMg','Mass loss (mg)','number','100'],['densityGcm3','Density (g/cm³)','number','7.87'],['areaCm2','Area (cm²)','number','10'],['timeHours','Time (h)','number','168']]],
    ['faradayCorrosion','Faradaic corrosion penetration','corrosion','m = ItM/(zF)','corrosionRecords',[['currentA','Current (A)','number','0.01'],['timeS','Time (s)','number','86400'],['molarMassGmol','Molar mass (g/mol)','number','55.845'],['electrons','Electrons z','number','2'],['densityGcm3','Density (g/cm³)','number','7.87'],['areaCm2','Area (cm²)','number','10']]],
    ['sternGeary','Stern–Geary corrosion current','corrosion','icorr = B/Rp','corrosionRecords',[['betaAnodicMvDec','Anodic Tafel slope (mV/dec)','number','120'],['betaCathodicMvDec','Cathodic Tafel slope (mV/dec)','number','120'],['polarizationResistanceOhmCm2','Polarization resistance (Ω·cm²)','number','1000']]],

    ['degreePolymerization','Polymer degree of polymerization','polymers','Xn = Mn/M0','polymerRecords',[['numberAverageMassGmol','Mn (g/mol)','number','100000'],['repeatUnitMassGmol','Repeat-unit mass (g/mol)','number','104.15']]],
    ['foxTg','Fox copolymer glass transition','polymers','1/Tg = Σwi/Tgi','polymerRecords',[['fractions','Mass fractions','textarea','[0.6,0.4]'],['tgK','Component Tg values (K)','textarea','[373,423]']]],
    ['crystallinityDSC','Polymer crystallinity from DSC','polymers','Xc=(ΔHm−ΔHcc)/ΔHm°','polymerRecords',[['meltingEnthalpyJg','Melting enthalpy (J/g)','number','120'],['coldCrystallizationJg','Cold crystallization (J/g)','number','20'],['referenceEnthalpyJg','100% crystalline reference (J/g)','number','293']]],
    ['ruleOfMixtures','Composite rule of mixtures','composites','EL=VfEf+VmEm; 1/ET=Vf/Ef+Vm/Em','compositeRecords',[['fiberFraction','Fiber volume fraction','number','0.6'],['fiberModulusGPa','Fiber modulus (GPa)','number','230'],['matrixModulusGPa','Matrix modulus (GPa)','number','3.5']]],
    ['halpinTsai','Halpin–Tsai composite modulus','composites','E/Em=(1+ξηVf)/(1−ηVf)','compositeRecords',[['fiberFraction','Fiber volume fraction','number','0.3'],['fiberModulusGPa','Fiber modulus (GPa)','number','70'],['matrixModulusGPa','Matrix modulus (GPa)','number','3'],['shapeParameter','Shape parameter ξ','number','2']]],
    ['compositeDensity','Composite density','composites','ρc=Vfρf+Vmρm','compositeRecords',[['fiberFraction','Fiber volume fraction','number','0.6'],['fiberDensityGcm3','Fiber density (g/cm³)','number','1.8'],['matrixDensityGcm3','Matrix density (g/cm³)','number','1.2']]],
    ['maxwellRelaxation','Maxwell viscoelastic relaxation','polymers','τ=η/E; σ/σ0=exp(−t/τ)','polymerRecords',[['viscosityPaS','Viscosity (Pa·s)','number','1e9'],['modulusPa','Modulus (Pa)','number','1e6'],['timeS','Time (s)','number','100']]],

    ['particleStats','Particle-size statistics','microscopy','D10, D50, D90 and sample moments','microscopyRecords',[['diameters','Diameters','textarea','[1.2,1.5,1.7,2.0,2.2,2.5,3.0,3.5,4.0]']]],
    ['areaFraction','Image area fraction','microscopy','Af = feature pixels / total pixels','microscopyRecords',[['featurePixels','Feature pixels','number','25000'],['totalPixels','Total pixels','number','100000']]],
    ['grainIntercept','Mean linear intercept grain size','microscopy','l̄ = L/(MN)','microscopyRecords',[['testLineLengthMm','Test-line length on image (mm)','number','100'],['intercepts','Intercept count','number','50'],['magnification','Magnification','number','100']]],
    ['microscopyCalibration','Image spatial calibration','microscopy','scale = known distance / pixels','microscopyRecords',[['knownDistanceUm','Known distance (µm)','number','100'],['pixelDistance','Pixel distance','number','500']]],
    ['abbeResolution','Abbe lateral resolution','microscopy','d = λ/(2NA)','microscopyRecords',[['wavelengthNm','Wavelength (nm)','number','550'],['numericalAperture','Numerical aperture','number','1.4']]]
  ];

  const assumptions = {
    mechanical:['Continuum, homogeneous specimen assumptions apply unless noted.','Input dimensions and loads must use the displayed units.'],
    thermal:['Material properties are treated as constant over the supplied range.','Contact resistance and radiation are omitted unless included explicitly.'],
    electrical:['Bulk, homogeneous behavior and ideal contacts are assumed.','Carrier and dielectric models are simplified analytical approximations.'],
    magnetic:['Quasistatic homogeneous-material behavior is assumed.','Demagnetizing fields and texture may require separate treatment.'],
    optical:['Single-pass, homogeneous optical behavior is assumed.','Surface roughness, scattering, and multiple reflections may alter measured values.'],
    crystallography:['Peak positions and widths must be instrument-corrected for rigorous characterization.','Cubic/unit-cell simplifications apply only to matching crystal systems.'],
    phase:['Local equilibrium or dilute diffusion assumptions apply as indicated.','Real multicomponent systems require assessed thermodynamic and kinetic data.'],
    corrosion:['Uniform corrosion is assumed unless the method states otherwise.','Electrolyte chemistry, localization, and mass-transfer limitations need independent review.'],
    polymers:['Reported polymer relations are approximate bulk models.','Molecular-weight distribution, morphology, and thermal history can change results.'],
    composites:['Perfect bonding, uniform dispersion, and idealized orientation are assumed.','Void content and interface damage are not included.'],
    microscopy:['Segmentation and calibration quality control the result.','Representative fields and uncertainty analysis are required for defensible statistics.']
  };

  const definitions = specs.map(([id,name,tab,equation,collection,fields]) => ({ id,name,tab,equation,collection,fields,assumptions:assumptions[tab]||['Review method assumptions and units before use.'] }));

  function validate(def,input,result) {
    const warnings=[]; let status='validated';
    const walk=v=>{if(typeof v==='number'&&!Number.isFinite(v)){status='invalid';warnings.push('A numerical result is not finite.');} else if(Array.isArray(v))v.forEach(walk); else if(v&&typeof v==='object')Object.values(v).forEach(walk);}; walk(result);
    if(def.id==='leverRule'&&(result.alphaFraction<0||result.betaFraction<0||result.alphaFraction>1||result.betaFraction>1)){status='warning';warnings.push('Overall composition lies outside the supplied two-phase tie line.');}
    if(def.id==='scherrer')warnings.push('Instrument broadening and microstrain are not removed from the supplied peak width.');
    if(def.id==='taucBandGap'&&result.r2<0.95){status='warning';warnings.push('The selected Tauc region is weakly linear (R² < 0.95).');}
    if(def.id==='corrosionRate')warnings.push('Weight-loss calculation assumes uniform surface attack.');
    if(def.id==='intrinsicCarrier')warnings.push('Effective density-of-states values are treated as fixed inputs.');
    if(def.id==='thermalShock')warnings.push('This parameter is a screening metric, not a complete transient fracture simulation.');
    result._validation={status,method:def.name,warnings,constantsVersion:'SI 2019 constants; materials release 0.7.0',equation:def.equation,assumptions:def.assumptions};
    return result;
  }
  function run(id,input){const def=definitions.find(d=>d.id===id);if(!def||!rawTools[id])throw new Error('Unknown materials method.');return validate(def,input,rawTools[id](input));}

  function svgSeries(result,title){const series=result?.series;if(!Array.isArray(series)||series.length<2)return'';const keys=Object.keys(series[0]).filter(k=>k!=='x'&&typeof series[0][k]==='number');if(!keys.length)return'';const W=720,H=280,P=44,xs=series.map(p=>n(p.x)),ys=keys.flatMap(k=>series.map(p=>n(p[k]))),xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys),sx=x=>P+(x-xmin)/(xmax-xmin||1)*(W-2*P),sy=y=>H-P-(y-ymin)/(ymax-ymin||1)*(H-2*P);const paths=keys.map((k,i)=>`<path d="${series.map((p,j)=>`${j?'L':'M'}${sx(p.x).toFixed(2)},${sy(p[k]).toFixed(2)}`).join(' ')}" fill="none" stroke="${['#d00000','#245d83','#5a4a91'][i%3]}" stroke-width="2"/>`).join('');return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${U.esc(title)}"><title>${U.esc(title)}</title><rect width="${W}" height="${H}" fill="#fff"/><line x1="${P}" y1="${H-P}" x2="${W-P}" y2="${H-P}" stroke="#687681"/><line x1="${P}" y1="${P}" x2="${P}" y2="${H-P}" stroke="#687681"/>${paths}</svg>`;}

  const benchmarks = [
    {id:'stress',tool:'engineeringStress',input:{forceN:1000,areaMm2:10},expected:'100 MPa',check:r=>Math.abs(r.stressMPa-100)<1e-10},
    {id:'elastic',tool:'elasticConstants',input:{youngsModulusGPa:210,poissonRatio:.3},expected:'G ≈ 80.77 GPa',check:r=>Math.abs(r.shearModulusGPa-80.76923077)<1e-6},
    {id:'diffusivity',tool:'thermalDiffusivity',input:{conductivityWmK:205,densityKgM3:2700,specificHeatJkgK:900},expected:'≈8.44×10⁻⁵ m²/s',check:r=>r.thermalDiffusivityM2S>8.4e-5&&r.thermalDiffusivityM2S<8.5e-5},
    {id:'resistivity',tool:'resistivity',input:{resistanceOhm:1,areaMm2:1,lengthM:1},expected:'1×10⁻⁶ Ω·m',check:r=>Math.abs(r.resistivityOhmM-1e-6)<1e-15},
    {id:'reflectance',tool:'reflectanceIndex',input:{refractiveIndex:1.5,extinctionCoefficient:0},expected:'4%',check:r=>Math.abs(r.normalReflectance-.04)<1e-12},
    {id:'bragg',tool:'braggLaw',input:{wavelengthNm:.15406,twoThetaDeg:60,order:1},expected:'1.5406 Å',check:r=>Math.abs(r.dSpacingAngstrom-1.5406)<1e-4},
    {id:'lever',tool:'leverRule',input:{composition:50,alphaComposition:20,betaComposition:80},expected:'0.5 / 0.5',check:r=>Math.abs(r.alphaFraction-.5)<1e-12&&Math.abs(r.betaFraction-.5)<1e-12},
    {id:'corrosion',tool:'corrosionRate',input:{massLossMg:100,densityGcm3:7.87,areaCm2:10,timeHours:168},expected:'≈0.662 mm/yr',check:r=>r.corrosionRateMmYr>.65&&r.corrosionRateMmYr<.67},
    {id:'mixtures',tool:'ruleOfMixtures',input:{fiberFraction:.5,fiberModulusGPa:100,matrixModulusGPa:10},expected:'55 GPa longitudinal',check:r=>Math.abs(r.longitudinalModulusGPa-55)<1e-12},
    {id:'abbe',tool:'abbeResolution',input:{wavelengthNm:500,numericalAperture:1.25},expected:'200 nm',check:r=>Math.abs(r.lateralResolutionNm-200)<1e-12}
  ];
  function runBenchmarks(){const records=benchmarks.map(b=>{try{const result=run(b.tool,b.input);return{...b,passed:!!b.check(result),result};}catch(error){return{...b,passed:false,error:error.message};}});return{total:records.length,passed:records.filter(r=>r.passed).length,failed:records.filter(r=>!r.passed).length,records,ranAt:new Date().toISOString()};}

  function fieldHTML(f){const[key,label,type,def,options]=f;if(type==='textarea')return`<label>${U.esc(label)}<textarea rows="5" data-materials-field="${U.esc(key)}">${U.esc(def)}</textarea></label>`;if(type==='select')return`<label>${U.esc(label)}<select data-materials-field="${U.esc(key)}">${Object.entries(options||{}).map(([v,t])=>`<option value="${U.esc(v)}"${String(v)===String(def)?' selected':''}>${U.esc(t)}</option>`).join('')}</select></label>`;return`<label>${U.esc(label)}<input data-materials-field="${U.esc(key)}" type="${type==='text'?'text':'number'}" step="any" value="${U.esc(def)}"></label>`;}
  function toolHTML(def){return`<article class="sc-lab-tool sc-lab-materials-tool" data-materials-tool="${U.esc(def.id)}"><h4>${U.esc(def.name)}</h4><details class="sc-lab-materials-method"><summary>Method and assumptions</summary><p><code>${U.esc(def.equation)}</code></p><ul>${def.assumptions.map(x=>`<li>${U.esc(x)}</li>`).join('')}</ul></details><div class="sc-lab-inline-fields">${def.fields.map(fieldHTML).join('')}</div><div class="sc-lab-inline-actions"><button type="button" class="sc-lab-button sc-lab-button-primary" data-materials-run>Run analysis</button><button type="button" class="sc-lab-button" data-materials-save>Save</button><button type="button" class="sc-lab-button" data-materials-note>Add to notebook</button></div><div class="sc-lab-chart sc-lab-materials-chart" data-materials-chart></div><div data-materials-validation></div><pre data-materials-output></pre></article>`;}
  function collect(card){const input={};card.querySelectorAll('[data-materials-field]').forEach(el=>input[el.dataset.materialsField]=el.value);return input;}
  function renderValidation(target,v){target.innerHTML=v?`<div class="sc-lab-materials-validation is-${U.esc(v.status)}"><div><strong>${U.esc(v.status.toUpperCase())}</strong><span>${U.esc(v.method)}</span></div>${v.warnings.length?`<ul>${v.warnings.map(x=>`<li>${U.esc(x)}</li>`).join('')}</ul>`:''}</div>`:'';}
  function init(root,projects){
    root.querySelectorAll('[data-materials-tool-grid]').forEach(grid=>{grid.innerHTML=definitions.filter(d=>d.tab===grid.dataset.materialsToolGrid).map(toolHTML).join('');});
    root.querySelectorAll('[data-materials-tab]').forEach(button=>button.addEventListener('click',()=>{const v=button.dataset.materialsTab;root.querySelectorAll('[data-materials-tab]').forEach(b=>b.classList.toggle('is-active',b===button));root.querySelectorAll('[data-materials-pane]').forEach(p=>p.hidden=p.dataset.materialsPane!==v);}));
    root.querySelectorAll('[data-materials-tool]').forEach(card=>{let current=null;const id=card.dataset.materialsTool,def=definitions.find(d=>d.id===id);card.querySelector('[data-materials-run]').addEventListener('click',()=>{try{const input=collect(card),result=run(id,input);current={input,result};card.querySelector('[data-materials-output]').textContent=JSON.stringify(result,null,2);card.querySelector('[data-materials-chart]').innerHTML=svgSeries(result,def.name);renderValidation(card.querySelector('[data-materials-validation]'),result._validation);}catch(error){current=null;card.querySelector('[data-materials-output]').textContent=`Error: ${error.message}`;card.querySelector('[data-materials-chart]').innerHTML='';renderValidation(card.querySelector('[data-materials-validation]'),{status:'invalid',method:def.name,warnings:[error.message]});}});card.querySelector('[data-materials-save]').addEventListener('click',()=>{if(!current)card.querySelector('[data-materials-run]').click();if(!current)return;projects.add(def.collection,{type:def.name,methodId:id,inputs:current.input,result:current.result,validation:current.result._validation},`${def.name} saved`);if(def.collection!=='materialsRecords')projects.add('materialsRecords',{type:def.name,methodId:id,collection:def.collection,recordedAt:new Date().toISOString()},`Materials index updated: ${def.name}`);U.toast(root,'Materials analysis saved.');});card.querySelector('[data-materials-note]').addEventListener('click',()=>{if(!current)card.querySelector('[data-materials-run]').click();if(!current)return;projects.add('notes',{title:`${def.name} analysis`,body:JSON.stringify({inputs:current.input,result:current.result},null,2),tags:['materials',def.tab,id]},`Notebook entry added: ${def.name}`);U.toast(root,'Materials analysis added to notebook.');});});
    const runButton=root.querySelector('[data-materials-run-benchmarks]');if(runButton)runButton.addEventListener('click',()=>{const report=runBenchmarks();root._materialsBenchmarkReport=report;root.querySelector('[data-materials-benchmark-table]').innerHTML=`<div class="sc-lab-validation-summary"><strong>${report.passed}/${report.total} benchmarks passed</strong><span class="${report.failed?'is-failed':'is-passed'}">${report.failed?'Review failures':'Validated'}</span><small>${U.esc(report.ranAt)}</small></div><div class="sc-lab-table-wrap"><table><thead><tr><th>Method</th><th>Expected</th><th>Status</th></tr></thead><tbody>${report.records.map(r=>`<tr><td>${U.esc(r.tool)}</td><td>${U.esc(r.expected)}</td><td><span class="sc-lab-validation-badge ${r.passed?'is-passed':'is-failed'}">${r.passed?'PASS':'FAIL'}</span></td></tr>`).join('')}</tbody></table></div>`;});
    const save=root.querySelector('[data-materials-save-benchmarks]');if(save)save.addEventListener('click',()=>{const report=root._materialsBenchmarkReport||runBenchmarks();projects.add('materialsValidationRecords',{type:'materials-benchmark-suite',report},`Materials benchmark suite saved: ${report.passed}/${report.total} passed`);U.toast(root,'Materials validation report saved.');});
    const exp=root.querySelector('[data-materials-experiment]');if(exp)exp.addEventListener('click',()=>{projects.add('experiments',{title:'Materials characterization study',question:'Define the material, process condition, and property or microstructure question.',hypothesis:'Record a falsifiable property–structure–processing hypothesis.',method:'Select a Materials Laboratory method, preserve specimen preparation and instrument settings, run the analysis, review validation, and connect raw data and outputs.',status:'planned',domain:'materials-science'},'Materials experiment template created');U.toast(root,'Materials experiment record created.');});
  }

  Lab.MaterialsLab={constants:{R,F,kB,q,eps0,h,c,NA},rawTools,tools:rawTools,definitions,run,benchmarks,runBenchmarks,svgSeries,init};
})(window);
