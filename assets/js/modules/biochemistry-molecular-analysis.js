(() => {
  'use strict';

  const rootWindow = typeof window !== 'undefined'
    ? window
    : globalThis;
  const Lab = rootWindow.SCLab = rootWindow.SCLab || {};
  const VERSION = '0.21.0';
  const CATALOG = {"schema":"sc-lab-biochemistry-molecular-analysis-methods/1.0","version":"0.21.0","title":"Biochemistry and Molecular Analysis","description":"Auditable calculations for biomolecule quantification, proteins, enzyme kinetics, nucleic acids, molecular binding, buffers, spectroscopy, separations, and laboratory quality control.","categories":[{"id":"biomolecule-quantification","label":"Biomolecule quantification"},{"id":"protein-peptide-analysis","label":"Protein and peptide analysis"},{"id":"enzyme-kinetics-inhibition","label":"Enzyme kinetics and inhibition"},{"id":"nucleic-acid-analysis","label":"Nucleic acid analysis"},{"id":"binding-equilibria","label":"Binding equilibria and molecular interactions"},{"id":"buffers-ionic-systems","label":"Buffers, pH, and ionic systems"},{"id":"spectrophotometry-fluorescence","label":"Spectrophotometry and fluorescence"},{"id":"molecular-separations-qc","label":"Molecular separations and quality control"}],"methods":[{"id":"bc.mass_concentration","version":"1.0.0","category":"Biomolecule quantification","title":"Mass concentration","equation":"c = m / V","inputs":[{"key":"massMg","label":"Biomolecule mass","unit":"mg","default":10,"min":0},{"key":"volumeMl","label":"Solution volume","unit":"mL","default":2,"min":1e-12}],"outputs":{"massConcentrationMgMl":{"label":"Mass concentration","unit":"mg/mL","expression":"massMg / volumeMl"}},"assumptions":["Mass and volume describe the same prepared sample."],"notes":[]},{"id":"bc.molar_concentration","version":"1.0.0","category":"Biomolecule quantification","title":"Molar concentration from mass","equation":"C = (m/1000) / (M V)","inputs":[{"key":"massMg","label":"Solute mass","unit":"mg","default":18,"min":0},{"key":"molecularWeightGMol","label":"Molecular weight","unit":"g/mol","default":180.156,"min":1e-12},{"key":"volumeL","label":"Solution volume","unit":"L","default":0.1,"min":1e-12}],"outputs":{"molarConcentrationMolL":{"label":"Molar concentration","unit":"mol/L","expression":"(massMg / 1000) / (molecularWeightGMol * volumeL)"}},"assumptions":[],"notes":[]},{"id":"bc.dilution_concentration","version":"1.0.0","category":"Biomolecule quantification","title":"Dilution concentration","equation":"C₂ = C₁V₁ / V₂","inputs":[{"key":"initialConcentration","label":"Initial concentration","unit":"user unit","default":10,"min":0},{"key":"initialVolumeMl","label":"Transferred volume","unit":"mL","default":2,"min":0},{"key":"finalVolumeMl","label":"Final volume","unit":"mL","default":20,"min":1e-12}],"outputs":{"finalConcentration":{"label":"Final concentration","unit":"same as C₁","expression":"initialConcentration * initialVolumeMl / finalVolumeMl"}},"assumptions":[],"notes":[]},{"id":"bc.percent_recovery","version":"1.0.0","category":"Biomolecule quantification","title":"Analytical recovery","equation":"Recovery = measured / expected × 100","inputs":[{"key":"measuredAmount","label":"Measured amount","unit":"user unit","default":9.6,"min":0},{"key":"expectedAmount","label":"Expected amount","unit":"user unit","default":10,"min":1e-12}],"outputs":{"recoveryPercent":{"label":"Recovery","unit":"%","expression":"measuredAmount / expectedAmount * 100"}},"assumptions":[],"notes":[]},{"id":"bc.specific_activity","version":"1.0.0","category":"Biomolecule quantification","title":"Protein-specific enzyme activity","equation":"Specific activity = activity / protein mass","inputs":[{"key":"enzymeActivityUnits","label":"Enzyme activity","unit":"U","default":250,"min":0},{"key":"proteinMassMg","label":"Protein mass","unit":"mg","default":5,"min":1e-12}],"outputs":{"specificActivityUMg":{"label":"Specific activity","unit":"U/mg","expression":"enzymeActivityUnits / proteinMassMg"}},"assumptions":[],"notes":[]},{"id":"bc.purity_fraction","version":"1.0.0","category":"Biomolecule quantification","title":"Target biomolecule purity","equation":"Purity = target mass / total mass × 100","inputs":[{"key":"targetMassMg","label":"Target mass","unit":"mg","default":8.5,"min":0},{"key":"totalMassMg","label":"Total recovered mass","unit":"mg","default":10,"min":1e-12}],"outputs":{"purityPercent":{"label":"Purity","unit":"%","expression":"targetMassMg / totalMassMg * 100"}},"assumptions":[],"notes":[]},{"id":"bc.protein_molar_absorbance","version":"1.0.0","category":"Protein and peptide analysis","title":"Protein molarity from absorbance","equation":"c = A / (εl)","inputs":[{"key":"absorbance","label":"Absorbance","unit":"AU","default":0.75,"min":0},{"key":"extinctionCoefficient","label":"Molar extinction coefficient","unit":"L/(mol·cm)","default":50000,"min":1e-12},{"key":"pathLengthCm","label":"Optical path length","unit":"cm","default":1,"min":1e-12}],"outputs":{"proteinConcentrationMolL":{"label":"Protein concentration","unit":"mol/L","expression":"absorbance / (extinctionCoefficient * pathLengthCm)"}},"assumptions":[],"notes":[]},{"id":"bc.protein_mass_absorbance","version":"1.0.0","category":"Protein and peptide analysis","title":"Protein mass concentration from absorbance","equation":"c = A / (εₘl)","inputs":[{"key":"absorbance","label":"Absorbance","unit":"AU","default":0.8,"min":0},{"key":"massExtinctionCoefficient","label":"Mass extinction coefficient","unit":"mL/(mg·cm)","default":1.2,"min":1e-12},{"key":"pathLengthCm","label":"Optical path length","unit":"cm","default":1,"min":1e-12}],"outputs":{"proteinConcentrationMgMl":{"label":"Protein concentration","unit":"mg/mL","expression":"absorbance / (massExtinctionCoefficient * pathLengthCm)"}},"assumptions":[],"notes":[]},{"id":"bc.peptide_bond_count","version":"1.0.0","category":"Protein and peptide analysis","title":"Peptide-bond count","equation":"Bonds = residues − chains","inputs":[{"key":"residueCount","label":"Total amino-acid residues","unit":"count","default":300,"min":1},{"key":"chainCount","label":"Polypeptide chains","unit":"count","default":2,"min":1}],"outputs":{"peptideBondCount":{"label":"Peptide bonds","unit":"count","expression":"residueCount - chainCount"}},"assumptions":[],"notes":[]},{"id":"bc.protein_amount_moles","version":"1.0.0","category":"Protein and peptide analysis","title":"Protein amount in moles","equation":"n = (m/1000) / M","inputs":[{"key":"massMg","label":"Protein mass","unit":"mg","default":5,"min":0},{"key":"molecularWeightGMol","label":"Protein molecular weight","unit":"g/mol","default":50000,"min":1e-12}],"outputs":{"proteinAmountMol":{"label":"Protein amount","unit":"mol","expression":"(massMg / 1000) / molecularWeightGMol"}},"assumptions":[],"notes":[]},{"id":"bc.fraction_protonated","version":"1.0.0","category":"Protein and peptide analysis","title":"Protonated-site fraction","equation":"f = 1 / (1 + 10^(pH−pKa))","inputs":[{"key":"pH","label":"Solution pH","unit":"pH","default":7.4},{"key":"pKa","label":"Site pKa","unit":"pKa","default":6.5}],"outputs":{"fractionProtonated":{"label":"Fraction protonated","unit":"fraction","expression":"1 / (1 + pow(10, pH - pKa))"}},"assumptions":[],"notes":[]},{"id":"bc.isoelectric_point_two_pka","version":"1.0.0","category":"Protein and peptide analysis","title":"Two-pKa isoelectric-point estimate","equation":"pI = (pKa₁ + pKa₂) / 2","inputs":[{"key":"pKaLower","label":"Lower bracketing pKa","unit":"pKa","default":2.34},{"key":"pKaUpper","label":"Upper bracketing pKa","unit":"pKa","default":9.6}],"outputs":{"isoelectricPoint":{"label":"Estimated pI","unit":"pH","expression":"(pKaLower + pKaUpper) / 2"}},"assumptions":[],"notes":[]},{"id":"bc.michaelis_menten","version":"1.0.0","category":"Enzyme kinetics and inhibition","title":"Michaelis–Menten velocity","equation":"v = Vmax[S] / (Km + [S])","inputs":[{"key":"vmax","label":"Maximum velocity","unit":"rate unit","default":100,"min":0},{"key":"substrate","label":"Substrate concentration","unit":"concentration unit","default":2,"min":0},{"key":"km","label":"Michaelis constant","unit":"concentration unit","default":0.5,"min":1e-12}],"outputs":{"velocity":{"label":"Initial velocity","unit":"rate unit","expression":"vmax * substrate / (km + substrate)"}},"assumptions":[],"notes":[]},{"id":"bc.turnover_number","version":"1.0.0","category":"Enzyme kinetics and inhibition","title":"Enzyme turnover number","equation":"kcat = Vmax / [E]ₜ","inputs":[{"key":"vmaxMolS","label":"Maximum molar velocity","unit":"mol/s","default":2e-06,"min":0},{"key":"enzymeMol","label":"Total enzyme amount","unit":"mol","default":1e-09,"min":1e-30}],"outputs":{"turnoverNumberPerS":{"label":"Turnover number","unit":"1/s","expression":"vmaxMolS / enzymeMol"}},"assumptions":[],"notes":[]},{"id":"bc.catalytic_efficiency","version":"1.0.0","category":"Enzyme kinetics and inhibition","title":"Catalytic efficiency","equation":"Efficiency = kcat / Km","inputs":[{"key":"turnoverNumberPerS","label":"Turnover number","unit":"1/s","default":1500,"min":0},{"key":"kmMolL","label":"Michaelis constant","unit":"mol/L","default":0.0002,"min":1e-30}],"outputs":{"catalyticEfficiency":{"label":"Catalytic efficiency","unit":"L/(mol·s)","expression":"turnoverNumberPerS / kmMolL"}},"assumptions":[],"notes":[]},{"id":"bc.competitive_apparent_km","version":"1.0.0","category":"Enzyme kinetics and inhibition","title":"Competitive-inhibition apparent Km","equation":"Km,app = Km(1 + [I]/Ki)","inputs":[{"key":"km","label":"Uninhibited Km","unit":"concentration unit","default":0.5,"min":0},{"key":"inhibitor","label":"Inhibitor concentration","unit":"concentration unit","default":1,"min":0},{"key":"ki","label":"Inhibition constant","unit":"concentration unit","default":0.25,"min":1e-12}],"outputs":{"apparentKm":{"label":"Apparent Km","unit":"concentration unit","expression":"km * (1 + inhibitor / ki)"}},"assumptions":[],"notes":[]},{"id":"bc.noncompetitive_apparent_vmax","version":"1.0.0","category":"Enzyme kinetics and inhibition","title":"Pure noncompetitive apparent Vmax","equation":"Vmax,app = Vmax / (1 + [I]/Ki)","inputs":[{"key":"vmax","label":"Uninhibited Vmax","unit":"rate unit","default":120,"min":0},{"key":"inhibitor","label":"Inhibitor concentration","unit":"concentration unit","default":0.5,"min":0},{"key":"ki","label":"Inhibition constant","unit":"concentration unit","default":0.5,"min":1e-12}],"outputs":{"apparentVmax":{"label":"Apparent Vmax","unit":"rate unit","expression":"vmax / (1 + inhibitor / ki)"}},"assumptions":[],"notes":[]},{"id":"bc.hill_velocity","version":"1.0.0","category":"Enzyme kinetics and inhibition","title":"Cooperative Hill velocity","equation":"v = Vmax[S]^n / (K₀.₅^n + [S]^n)","inputs":[{"key":"vmax","label":"Maximum velocity","unit":"rate unit","default":100,"min":0},{"key":"substrate","label":"Substrate concentration","unit":"concentration unit","default":2,"min":0},{"key":"halfSaturation","label":"Half-saturation constant","unit":"concentration unit","default":1,"min":1e-12},{"key":"hillCoefficient","label":"Hill coefficient","unit":"dimensionless","default":2,"min":1e-12}],"outputs":{"velocity":{"label":"Hill-model velocity","unit":"rate unit","expression":"vmax * pow(substrate, hillCoefficient) / (pow(halfSaturation, hillCoefficient) + pow(substrate, hillCoefficient))"}},"assumptions":[],"notes":[]},{"id":"bc.dsdna_a260_concentration","version":"1.0.0","category":"Nucleic acid analysis","title":"dsDNA concentration from A260","equation":"c = A260 × 50 × dilution","inputs":[{"key":"absorbance260","label":"A260 absorbance","unit":"AU","default":0.2,"min":0},{"key":"dilutionFactor","label":"Dilution factor","unit":"dimensionless","default":10,"min":0}],"outputs":{"dnaConcentrationUgMl":{"label":"dsDNA concentration","unit":"µg/mL","expression":"absorbance260 * 50 * dilutionFactor"}},"assumptions":[],"notes":[]},{"id":"bc.rna_a260_concentration","version":"1.0.0","category":"Nucleic acid analysis","title":"RNA concentration from A260","equation":"c = A260 × 40 × dilution","inputs":[{"key":"absorbance260","label":"A260 absorbance","unit":"AU","default":0.25,"min":0},{"key":"dilutionFactor","label":"Dilution factor","unit":"dimensionless","default":10,"min":0}],"outputs":{"rnaConcentrationUgMl":{"label":"RNA concentration","unit":"µg/mL","expression":"absorbance260 * 40 * dilutionFactor"}},"assumptions":[],"notes":[]},{"id":"bc.dsdna_amount_moles","version":"1.0.0","category":"Nucleic acid analysis","title":"dsDNA amount in moles","equation":"n = m / (bp × 660)","inputs":[{"key":"massNg","label":"DNA mass","unit":"ng","default":100,"min":0},{"key":"basePairs","label":"Fragment length","unit":"bp","default":1000,"min":1}],"outputs":{"dnaAmountMol":{"label":"DNA amount","unit":"mol","expression":"massNg * 1e-9 / (basePairs * 660)"}},"assumptions":[],"notes":[]},{"id":"bc.ssrna_amount_moles","version":"1.0.0","category":"Nucleic acid analysis","title":"ssRNA amount in moles","equation":"n = m / (nt × 340)","inputs":[{"key":"massNg","label":"RNA mass","unit":"ng","default":100,"min":0},{"key":"nucleotides","label":"Transcript length","unit":"nt","default":1000,"min":1}],"outputs":{"rnaAmountMol":{"label":"RNA amount","unit":"mol","expression":"massNg * 1e-9 / (nucleotides * 340)"}},"assumptions":[],"notes":[]},{"id":"bc.gc_content","version":"1.0.0","category":"Nucleic acid analysis","title":"GC content","equation":"GC% = (G + C) / total × 100","inputs":[{"key":"guanineCount","label":"Guanine count","unit":"count","default":25,"min":0},{"key":"cytosineCount","label":"Cytosine count","unit":"count","default":25,"min":0},{"key":"totalBases","label":"Total base count","unit":"count","default":100,"min":1}],"outputs":{"gcPercent":{"label":"GC content","unit":"%","expression":"(guanineCount + cytosineCount) / totalBases * 100"}},"assumptions":[],"notes":[]},{"id":"bc.oligo_melting_temperature","version":"1.0.0","category":"Nucleic acid analysis","title":"Short-oligo melting temperature","equation":"Tm = 2(A + T) + 4(G + C)","inputs":[{"key":"adenineCount","label":"Adenine count","unit":"count","default":5,"min":0},{"key":"thymineCount","label":"Thymine count","unit":"count","default":5,"min":0},{"key":"guanineCount","label":"Guanine count","unit":"count","default":5,"min":0},{"key":"cytosineCount","label":"Cytosine count","unit":"count","default":5,"min":0}],"outputs":{"meltingTemperatureC":{"label":"Estimated melting temperature","unit":"°C","expression":"2 * (adenineCount + thymineCount) + 4 * (guanineCount + cytosineCount)"}},"assumptions":["Wallace-rule estimate for short oligonucleotides under simplified conditions."],"notes":[]},{"id":"bc.binding_occupancy","version":"1.0.0","category":"Binding equilibria and molecular interactions","title":"Single-site binding occupancy","equation":"θ = [L] / (Kd + [L])","inputs":[{"key":"ligand","label":"Free ligand concentration","unit":"concentration unit","default":5,"min":0},{"key":"kd","label":"Dissociation constant","unit":"concentration unit","default":2,"min":1e-12}],"outputs":{"occupancy":{"label":"Fractional occupancy","unit":"fraction","expression":"ligand / (kd + ligand)"}},"assumptions":[],"notes":[]},{"id":"bc.hill_binding_occupancy","version":"1.0.0","category":"Binding equilibria and molecular interactions","title":"Hill binding occupancy","equation":"θ = [L]^n / (Kd^n + [L]^n)","inputs":[{"key":"ligand","label":"Ligand concentration","unit":"concentration unit","default":4,"min":0},{"key":"kd","label":"Half-occupancy concentration","unit":"concentration unit","default":2,"min":1e-12},{"key":"hillCoefficient","label":"Hill coefficient","unit":"dimensionless","default":2,"min":1e-12}],"outputs":{"occupancy":{"label":"Hill occupancy","unit":"fraction","expression":"pow(ligand, hillCoefficient) / (pow(kd, hillCoefficient) + pow(ligand, hillCoefficient))"}},"assumptions":[],"notes":[]},{"id":"bc.association_constant","version":"1.0.0","category":"Binding equilibria and molecular interactions","title":"Association constant","equation":"Ka = 1 / Kd","inputs":[{"key":"kdMolL","label":"Dissociation constant","unit":"mol/L","default":1e-06,"min":1e-30}],"outputs":{"associationConstant":{"label":"Association constant","unit":"L/mol","expression":"1 / kdMolL"}},"assumptions":[],"notes":[]},{"id":"bc.binding_free_energy","version":"1.0.0","category":"Binding equilibria and molecular interactions","title":"Binding free energy from Kd","equation":"ΔG° = RT ln(Kd / 1 M)","inputs":[{"key":"kdMolL","label":"Dissociation constant","unit":"mol/L","default":1e-06,"min":1e-30},{"key":"temperatureK","label":"Temperature","unit":"K","default":298.15,"min":1e-12}],"outputs":{"bindingFreeEnergyKJMol":{"label":"Standard binding free energy","unit":"kJ/mol","expression":"0.008314462618 * temperatureK * log(kdMolL)"}},"assumptions":[],"notes":[]},{"id":"bc.exact_complex_concentration","version":"1.0.0","category":"Binding equilibria and molecular interactions","title":"Exact 1:1 complex concentration","equation":"[PL] = ((P+L+Kd) − √((P+L+Kd)²−4PL)) / 2","inputs":[{"key":"proteinTotal","label":"Total protein","unit":"concentration unit","default":10,"min":0},{"key":"ligandTotal","label":"Total ligand","unit":"concentration unit","default":8,"min":0},{"key":"kd","label":"Dissociation constant","unit":"concentration unit","default":2,"min":0}],"outputs":{"complexConcentration":{"label":"Complex concentration","unit":"concentration unit","expression":"((proteinTotal + ligandTotal + kd) - sqrt(pow(proteinTotal + ligandTotal + kd, 2) - 4 * proteinTotal * ligandTotal)) / 2"}},"assumptions":[],"notes":[]},{"id":"bc.bound_free_ratio","version":"1.0.0","category":"Binding equilibria and molecular interactions","title":"Bound-to-free ratio","equation":"R = bound / free","inputs":[{"key":"boundConcentration","label":"Bound concentration","unit":"concentration unit","default":3,"min":0},{"key":"freeConcentration","label":"Free concentration","unit":"concentration unit","default":2,"min":1e-12}],"outputs":{"boundFreeRatio":{"label":"Bound/free ratio","unit":"dimensionless","expression":"boundConcentration / freeConcentration"}},"assumptions":[],"notes":[]},{"id":"bc.henderson_hasselbalch","version":"1.0.0","category":"Buffers, pH, and ionic systems","title":"Henderson–Hasselbalch pH","equation":"pH = pKa + log10([A−]/[HA])","inputs":[{"key":"pKa","label":"Acid dissociation pKa","unit":"pKa","default":6.1},{"key":"baseConcentration","label":"Conjugate-base concentration","unit":"mol/L","default":0.2,"min":1e-30},{"key":"acidConcentration","label":"Acid concentration","unit":"mol/L","default":0.1,"min":1e-30}],"outputs":{"pH":{"label":"Buffer pH","unit":"pH","expression":"pKa + log10(baseConcentration / acidConcentration)"}},"assumptions":[],"notes":[]},{"id":"bc.base_acid_ratio","version":"1.0.0","category":"Buffers, pH, and ionic systems","title":"Base-to-acid ratio from pH","equation":"[A−]/[HA] = 10^(pH−pKa)","inputs":[{"key":"pH","label":"Target pH","unit":"pH","default":7.4},{"key":"pKa","label":"Buffer pKa","unit":"pKa","default":6.8}],"outputs":{"baseAcidRatio":{"label":"Base/acid ratio","unit":"dimensionless","expression":"pow(10, pH - pKa)"}},"assumptions":[],"notes":[]},{"id":"bc.fraction_deprotonated","version":"1.0.0","category":"Buffers, pH, and ionic systems","title":"Deprotonated fraction","equation":"f = 1 / (1 + 10^(pKa−pH))","inputs":[{"key":"pH","label":"Solution pH","unit":"pH","default":7.4},{"key":"pKa","label":"Acid pKa","unit":"pKa","default":6.8}],"outputs":{"fractionDeprotonated":{"label":"Fraction deprotonated","unit":"fraction","expression":"1 / (1 + pow(10, pKa - pH))"}},"assumptions":[],"notes":[]},{"id":"bc.buffer_capacity","version":"1.0.0","category":"Buffers, pH, and ionic systems","title":"Monoprotic buffer capacity","equation":"β = 2.303 C Ka[H+] / (Ka + [H+])²","inputs":[{"key":"totalBufferConcentration","label":"Total buffer concentration","unit":"mol/L","default":0.1,"min":0},{"key":"pKa","label":"Buffer pKa","unit":"pKa","default":7.0},{"key":"pH","label":"Solution pH","unit":"pH","default":7.0}],"outputs":{"bufferCapacityMolLPerPh":{"label":"Buffer capacity","unit":"mol/(L·pH)","expression":"2.303 * totalBufferConcentration * pow(10, -pKa) * pow(10, -pH) / pow(pow(10, -pKa) + pow(10, -pH), 2)"}},"assumptions":[],"notes":[]},{"id":"bc.ionic_strength_three_species","version":"1.0.0","category":"Buffers, pH, and ionic systems","title":"Ionic strength for three species","equation":"I = 1/2 Σcᵢzᵢ²","inputs":[{"key":"concentration1","label":"Species 1 concentration","unit":"mol/L","default":0.1,"min":0},{"key":"charge1","label":"Species 1 charge","unit":"integer","default":1},{"key":"concentration2","label":"Species 2 concentration","unit":"mol/L","default":0.1,"min":0},{"key":"charge2","label":"Species 2 charge","unit":"integer","default":-1},{"key":"concentration3","label":"Species 3 concentration","unit":"mol/L","default":0,"min":0},{"key":"charge3","label":"Species 3 charge","unit":"integer","default":2}],"outputs":{"ionicStrengthMolL":{"label":"Ionic strength","unit":"mol/L","expression":"0.5 * (concentration1 * pow(charge1, 2) + concentration2 * pow(charge2, 2) + concentration3 * pow(charge3, 2))"}},"assumptions":[],"notes":[]},{"id":"bc.temperature_adjusted_pka","version":"1.0.0","category":"Buffers, pH, and ionic systems","title":"Temperature-adjusted buffer pKa","equation":"pKa(T) = pKa(ref) + slope(T − Tref)","inputs":[{"key":"pKaReference","label":"Reference pKa","unit":"pKa","default":8.06},{"key":"slopePerC","label":"Temperature coefficient","unit":"pKa/°C","default":-0.028},{"key":"temperatureC","label":"Working temperature","unit":"°C","default":37},{"key":"referenceTemperatureC","label":"Reference temperature","unit":"°C","default":25}],"outputs":{"adjustedPka":{"label":"Adjusted pKa","unit":"pKa","expression":"pKaReference + slopePerC * (temperatureC - referenceTemperatureC)"}},"assumptions":[],"notes":[]},{"id":"bc.beer_lambert_absorbance","version":"1.0.0","category":"Spectrophotometry and fluorescence","title":"Beer–Lambert absorbance","equation":"A = εcl","inputs":[{"key":"extinctionCoefficient","label":"Extinction coefficient","unit":"L/(mol·cm)","default":15000,"min":0},{"key":"concentrationMolL","label":"Concentration","unit":"mol/L","default":2e-05,"min":0},{"key":"pathLengthCm","label":"Path length","unit":"cm","default":1,"min":0}],"outputs":{"absorbance":{"label":"Absorbance","unit":"AU","expression":"extinctionCoefficient * concentrationMolL * pathLengthCm"}},"assumptions":[],"notes":[]},{"id":"bc.transmittance_from_absorbance","version":"1.0.0","category":"Spectrophotometry and fluorescence","title":"Transmittance from absorbance","equation":"T% = 100 × 10^(−A)","inputs":[{"key":"absorbance","label":"Absorbance","unit":"AU","default":0.3,"min":0}],"outputs":{"transmittancePercent":{"label":"Transmittance","unit":"%","expression":"100 * pow(10, -absorbance)"}},"assumptions":[],"notes":[]},{"id":"bc.blank_corrected_signal","version":"1.0.0","category":"Spectrophotometry and fluorescence","title":"Blank-corrected signal","equation":"S = sample − blank","inputs":[{"key":"sampleSignal","label":"Sample signal","unit":"instrument unit","default":1250},{"key":"blankSignal","label":"Blank signal","unit":"instrument unit","default":200}],"outputs":{"correctedSignal":{"label":"Blank-corrected signal","unit":"instrument unit","expression":"sampleSignal - blankSignal"}},"assumptions":[],"notes":[]},{"id":"bc.stern_volmer_ratio","version":"1.0.0","category":"Spectrophotometry and fluorescence","title":"Stern–Volmer quenching ratio","equation":"F0/F = 1 + Ksv[Q]","inputs":[{"key":"sternVolmerConstant","label":"Stern–Volmer constant","unit":"1/concentration","default":4,"min":0},{"key":"quencherConcentration","label":"Quencher concentration","unit":"concentration unit","default":0.2,"min":0}],"outputs":{"fluorescenceRatio":{"label":"F0/F ratio","unit":"dimensionless","expression":"1 + sternVolmerConstant * quencherConcentration"}},"assumptions":[],"notes":[]},{"id":"bc.corrected_fluorescence","version":"1.0.0","category":"Spectrophotometry and fluorescence","title":"Blank- and dilution-corrected fluorescence","equation":"Fcorrected = (Fsample − Fblank) × dilution","inputs":[{"key":"sampleFluorescence","label":"Sample fluorescence","unit":"RFU","default":800},{"key":"blankFluorescence","label":"Blank fluorescence","unit":"RFU","default":50},{"key":"dilutionFactor","label":"Dilution factor","unit":"dimensionless","default":5,"min":0}],"outputs":{"correctedFluorescence":{"label":"Corrected fluorescence","unit":"RFU","expression":"(sampleFluorescence - blankFluorescence) * dilutionFactor"}},"assumptions":[],"notes":[]},{"id":"bc.relative_quantum_yield","version":"1.0.0","category":"Spectrophotometry and fluorescence","title":"Relative fluorescence quantum yield","equation":"Φx = Φr(Ix/Ir)(Ar/Ax)(nx²/nr²)","inputs":[{"key":"referenceQuantumYield","label":"Reference quantum yield","unit":"fraction","default":0.55,"min":0},{"key":"integratedSampleIntensity","label":"Sample integrated intensity","unit":"area unit","default":12000,"min":0},{"key":"integratedReferenceIntensity","label":"Reference integrated intensity","unit":"area unit","default":10000,"min":1e-30},{"key":"referenceAbsorbance","label":"Reference absorbance","unit":"AU","default":0.05,"min":1e-30},{"key":"sampleAbsorbance","label":"Sample absorbance","unit":"AU","default":0.04,"min":1e-30},{"key":"sampleRefractiveIndex","label":"Sample refractive index","unit":"dimensionless","default":1.34,"min":1e-30},{"key":"referenceRefractiveIndex","label":"Reference refractive index","unit":"dimensionless","default":1.33,"min":1e-30}],"outputs":{"relativeQuantumYield":{"label":"Relative quantum yield","unit":"fraction","expression":"referenceQuantumYield * (integratedSampleIntensity / integratedReferenceIntensity) * (referenceAbsorbance / sampleAbsorbance) * (pow(sampleRefractiveIndex, 2) / pow(referenceRefractiveIndex, 2))"}},"assumptions":[],"notes":[]},{"id":"bc.chromatography_resolution","version":"1.0.0","category":"Molecular separations and quality control","title":"Chromatographic resolution","equation":"Rs = 2(tR2 − tR1)/(w1 + w2)","inputs":[{"key":"retentionTime1","label":"Peak 1 retention time","unit":"time unit","default":5},{"key":"retentionTime2","label":"Peak 2 retention time","unit":"time unit","default":6},{"key":"peakWidth1","label":"Peak 1 baseline width","unit":"time unit","default":0.4,"min":1e-30},{"key":"peakWidth2","label":"Peak 2 baseline width","unit":"time unit","default":0.5,"min":1e-30}],"outputs":{"resolution":{"label":"Resolution","unit":"dimensionless","expression":"2 * (retentionTime2 - retentionTime1) / (peakWidth1 + peakWidth2)"}},"assumptions":[],"notes":[]},{"id":"bc.retention_factor","version":"1.0.0","category":"Molecular separations and quality control","title":"Chromatographic retention factor","equation":"k′ = (tR − t0)/t0","inputs":[{"key":"retentionTime","label":"Analyte retention time","unit":"time unit","default":6},{"key":"deadTime","label":"Dead time","unit":"time unit","default":1.2,"min":1e-30}],"outputs":{"retentionFactor":{"label":"Retention factor","unit":"dimensionless","expression":"(retentionTime - deadTime) / deadTime"}},"assumptions":[],"notes":[]},{"id":"bc.gel_relative_mobility","version":"1.0.0","category":"Molecular separations and quality control","title":"Gel relative mobility","equation":"Rf = band distance / dye-front distance","inputs":[{"key":"bandDistanceMm","label":"Band migration distance","unit":"mm","default":45,"min":0},{"key":"dyeFrontDistanceMm","label":"Dye-front distance","unit":"mm","default":60,"min":1e-30}],"outputs":{"relativeMobility":{"label":"Relative mobility","unit":"fraction","expression":"bandDistanceMm / dyeFrontDistanceMm"}},"assumptions":[],"notes":[]},{"id":"bc.gel_molecular_weight","version":"1.0.0","category":"Molecular separations and quality control","title":"Molecular weight from semilog gel calibration","equation":"MW = 10^(intercept + slope·Rf)","inputs":[{"key":"intercept","label":"Calibration intercept","unit":"log10(MW)","default":5.0},{"key":"slope","label":"Calibration slope","unit":"log10(MW)/Rf","default":-2.0},{"key":"relativeMobility","label":"Relative mobility","unit":"fraction","default":0.5}],"outputs":{"molecularWeightDa":{"label":"Estimated molecular weight","unit":"Da","expression":"pow(10, intercept + slope * relativeMobility)"}},"assumptions":[],"notes":[]},{"id":"bc.relative_centrifugal_force","version":"1.0.0","category":"Molecular separations and quality control","title":"Relative centrifugal force","equation":"RCF = 1.118×10⁻⁵ r·rpm²","inputs":[{"key":"radiusCm","label":"Rotor radius","unit":"cm","default":10,"min":0},{"key":"rpm","label":"Rotational speed","unit":"rpm","default":10000,"min":0}],"outputs":{"relativeCentrifugalForce":{"label":"Relative centrifugal force","unit":"×g","expression":"1.118e-5 * radiusCm * pow(rpm, 2)"}},"assumptions":[],"notes":[]},{"id":"bc.coefficient_of_variation","version":"1.0.0","category":"Molecular separations and quality control","title":"Coefficient of variation","equation":"CV = SD / mean × 100","inputs":[{"key":"standardDeviation","label":"Standard deviation","unit":"measurement unit","default":2.5,"min":0},{"key":"mean","label":"Mean","unit":"measurement unit","default":100,"min":1e-30}],"outputs":{"coefficientOfVariationPercent":{"label":"Coefficient of variation","unit":"%","expression":"standardDeviation / mean * 100"}},"assumptions":[],"notes":[]}],"benchmarks":[{"id":"bc.mass_concentration.benchmark","methodId":"bc.mass_concentration","inputs":{"massMg":10,"volumeMl":2},"expected":{"massConcentrationMgMl":5.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.molar_concentration.benchmark","methodId":"bc.molar_concentration","inputs":{"massMg":18,"molecularWeightGMol":180.156,"volumeL":0.1},"expected":{"molarConcentrationMolL":0.0009991340837940449},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.dilution_concentration.benchmark","methodId":"bc.dilution_concentration","inputs":{"initialConcentration":10,"initialVolumeMl":2,"finalVolumeMl":20},"expected":{"finalConcentration":1.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.percent_recovery.benchmark","methodId":"bc.percent_recovery","inputs":{"measuredAmount":9.6,"expectedAmount":10},"expected":{"recoveryPercent":96.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.specific_activity.benchmark","methodId":"bc.specific_activity","inputs":{"enzymeActivityUnits":250,"proteinMassMg":5},"expected":{"specificActivityUMg":50.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.purity_fraction.benchmark","methodId":"bc.purity_fraction","inputs":{"targetMassMg":8.5,"totalMassMg":10},"expected":{"purityPercent":85.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.protein_molar_absorbance.benchmark","methodId":"bc.protein_molar_absorbance","inputs":{"absorbance":0.75,"extinctionCoefficient":50000,"pathLengthCm":1},"expected":{"proteinConcentrationMolL":1.5e-05},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.protein_mass_absorbance.benchmark","methodId":"bc.protein_mass_absorbance","inputs":{"absorbance":0.8,"massExtinctionCoefficient":1.2,"pathLengthCm":1},"expected":{"proteinConcentrationMgMl":0.6666666666666667},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.peptide_bond_count.benchmark","methodId":"bc.peptide_bond_count","inputs":{"residueCount":300,"chainCount":2},"expected":{"peptideBondCount":298.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.protein_amount_moles.benchmark","methodId":"bc.protein_amount_moles","inputs":{"massMg":5,"molecularWeightGMol":50000},"expected":{"proteinAmountMol":1e-07},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.fraction_protonated.benchmark","methodId":"bc.fraction_protonated","inputs":{"pH":7.4,"pKa":6.5},"expected":{"fractionProtonated":0.11181576977811687},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.isoelectric_point_two_pka.benchmark","methodId":"bc.isoelectric_point_two_pka","inputs":{"pKaLower":2.34,"pKaUpper":9.6},"expected":{"isoelectricPoint":5.97},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.michaelis_menten.benchmark","methodId":"bc.michaelis_menten","inputs":{"vmax":100,"substrate":2,"km":0.5},"expected":{"velocity":80.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.turnover_number.benchmark","methodId":"bc.turnover_number","inputs":{"vmaxMolS":2e-06,"enzymeMol":1e-09},"expected":{"turnoverNumberPerS":1999.9999999999998},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.catalytic_efficiency.benchmark","methodId":"bc.catalytic_efficiency","inputs":{"turnoverNumberPerS":1500,"kmMolL":0.0002},"expected":{"catalyticEfficiency":7500000.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.competitive_apparent_km.benchmark","methodId":"bc.competitive_apparent_km","inputs":{"km":0.5,"inhibitor":1,"ki":0.25},"expected":{"apparentKm":2.5},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.noncompetitive_apparent_vmax.benchmark","methodId":"bc.noncompetitive_apparent_vmax","inputs":{"vmax":120,"inhibitor":0.5,"ki":0.5},"expected":{"apparentVmax":60.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.hill_velocity.benchmark","methodId":"bc.hill_velocity","inputs":{"vmax":100,"substrate":2,"halfSaturation":1,"hillCoefficient":2},"expected":{"velocity":80.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.dsdna_a260_concentration.benchmark","methodId":"bc.dsdna_a260_concentration","inputs":{"absorbance260":0.2,"dilutionFactor":10},"expected":{"dnaConcentrationUgMl":100.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.rna_a260_concentration.benchmark","methodId":"bc.rna_a260_concentration","inputs":{"absorbance260":0.25,"dilutionFactor":10},"expected":{"rnaConcentrationUgMl":100.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.dsdna_amount_moles.benchmark","methodId":"bc.dsdna_amount_moles","inputs":{"massNg":100,"basePairs":1000},"expected":{"dnaAmountMol":1.5151515151515153e-13},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.ssrna_amount_moles.benchmark","methodId":"bc.ssrna_amount_moles","inputs":{"massNg":100,"nucleotides":1000},"expected":{"rnaAmountMol":2.9411764705882354e-13},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.gc_content.benchmark","methodId":"bc.gc_content","inputs":{"guanineCount":25,"cytosineCount":25,"totalBases":100},"expected":{"gcPercent":50.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.oligo_melting_temperature.benchmark","methodId":"bc.oligo_melting_temperature","inputs":{"adenineCount":5,"thymineCount":5,"guanineCount":5,"cytosineCount":5},"expected":{"meltingTemperatureC":60.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.binding_occupancy.benchmark","methodId":"bc.binding_occupancy","inputs":{"ligand":5,"kd":2},"expected":{"occupancy":0.7142857142857143},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.hill_binding_occupancy.benchmark","methodId":"bc.hill_binding_occupancy","inputs":{"ligand":4,"kd":2,"hillCoefficient":2},"expected":{"occupancy":0.8},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.association_constant.benchmark","methodId":"bc.association_constant","inputs":{"kdMolL":1e-06},"expected":{"associationConstant":1000000.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.binding_free_energy.benchmark","methodId":"bc.binding_free_energy","inputs":{"kdMolL":1e-06,"temperatureK":298.15},"expected":{"bindingFreeEnergyKJMol":-34.24805701458034},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.exact_complex_concentration.benchmark","methodId":"bc.exact_complex_concentration","inputs":{"proteinTotal":10,"ligandTotal":8,"kd":2},"expected":{"complexConcentration":5.52786404500042},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.bound_free_ratio.benchmark","methodId":"bc.bound_free_ratio","inputs":{"boundConcentration":3,"freeConcentration":2},"expected":{"boundFreeRatio":1.5},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.henderson_hasselbalch.benchmark","methodId":"bc.henderson_hasselbalch","inputs":{"pKa":6.1,"baseConcentration":0.2,"acidConcentration":0.1},"expected":{"pH":6.401029995663981},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.base_acid_ratio.benchmark","methodId":"bc.base_acid_ratio","inputs":{"pH":7.4,"pKa":6.8},"expected":{"baseAcidRatio":3.9810717055349776},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.fraction_deprotonated.benchmark","methodId":"bc.fraction_deprotonated","inputs":{"pH":7.4,"pKa":6.8},"expected":{"fractionDeprotonated":0.7992399910868984},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.buffer_capacity.benchmark","methodId":"bc.buffer_capacity","inputs":{"totalBufferConcentration":0.1,"pKa":7.0,"pH":7.0},"expected":{"bufferCapacityMolLPerPh":0.057575},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.ionic_strength_three_species.benchmark","methodId":"bc.ionic_strength_three_species","inputs":{"concentration1":0.1,"charge1":1,"concentration2":0.1,"charge2":-1,"concentration3":0,"charge3":2},"expected":{"ionicStrengthMolL":0.1},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.temperature_adjusted_pka.benchmark","methodId":"bc.temperature_adjusted_pka","inputs":{"pKaReference":8.06,"slopePerC":-0.028,"temperatureC":37,"referenceTemperatureC":25},"expected":{"adjustedPka":7.724},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.beer_lambert_absorbance.benchmark","methodId":"bc.beer_lambert_absorbance","inputs":{"extinctionCoefficient":15000,"concentrationMolL":2e-05,"pathLengthCm":1},"expected":{"absorbance":0.30000000000000004},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.transmittance_from_absorbance.benchmark","methodId":"bc.transmittance_from_absorbance","inputs":{"absorbance":0.3},"expected":{"transmittancePercent":50.11872336272722},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.blank_corrected_signal.benchmark","methodId":"bc.blank_corrected_signal","inputs":{"sampleSignal":1250,"blankSignal":200},"expected":{"correctedSignal":1050.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.stern_volmer_ratio.benchmark","methodId":"bc.stern_volmer_ratio","inputs":{"sternVolmerConstant":4,"quencherConcentration":0.2},"expected":{"fluorescenceRatio":1.8},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.corrected_fluorescence.benchmark","methodId":"bc.corrected_fluorescence","inputs":{"sampleFluorescence":800,"blankFluorescence":50,"dilutionFactor":5},"expected":{"correctedFluorescence":3750.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.relative_quantum_yield.benchmark","methodId":"bc.relative_quantum_yield","inputs":{"referenceQuantumYield":0.55,"integratedSampleIntensity":12000,"integratedReferenceIntensity":10000,"referenceAbsorbance":0.05,"sampleAbsorbance":0.04,"sampleRefractiveIndex":1.34,"referenceRefractiveIndex":1.33},"expected":{"relativeQuantumYield":0.8374526541918709},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.chromatography_resolution.benchmark","methodId":"bc.chromatography_resolution","inputs":{"retentionTime1":5,"retentionTime2":6,"peakWidth1":0.4,"peakWidth2":0.5},"expected":{"resolution":2.2222222222222223},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.retention_factor.benchmark","methodId":"bc.retention_factor","inputs":{"retentionTime":6,"deadTime":1.2},"expected":{"retentionFactor":4.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.gel_relative_mobility.benchmark","methodId":"bc.gel_relative_mobility","inputs":{"bandDistanceMm":45,"dyeFrontDistanceMm":60},"expected":{"relativeMobility":0.75},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.gel_molecular_weight.benchmark","methodId":"bc.gel_molecular_weight","inputs":{"intercept":5.0,"slope":-2.0,"relativeMobility":0.5},"expected":{"molecularWeightDa":10000.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.relative_centrifugal_force.benchmark","methodId":"bc.relative_centrifugal_force","inputs":{"radiusCm":10,"rpm":10000},"expected":{"relativeCentrifugalForce":11180.0},"absoluteTolerance":1e-09,"relativeTolerance":1e-09},{"id":"bc.coefficient_of_variation.benchmark","methodId":"bc.coefficient_of_variation","inputs":{"standardDeviation":2.5,"mean":100},"expected":{"coefficientOfVariationPercent":2.5},"absoluteTolerance":1e-09,"relativeTolerance":1e-09}],"responsibleUse":"These transparent equations support education, research planning, laboratory documentation, quality control, and reproducible analysis. They do not replace validated laboratory protocols, calibrated instrumentation, biosafety review, clinical interpretation, regulated testing, or qualified biochemical and molecular-science judgment."};
  const METHODS = Object.fromEntries(
    CATALOG.methods.map((method) => [method.id, method])
  );
  const SAFE_FUNCTIONS = {
    pow: Math.pow,
    sqrt: Math.sqrt,
    log: Math.log,
    log10: Math.log10,
    exp: Math.exp,
    abs: Math.abs,
    min: Math.min,
    max: Math.max,
  };

  function finite(value, label) {
    const number = Number(value);
    if (!Number.isFinite(number)) {
      throw new Error(`${label} must be a finite number.`);
    }
    return number;
  }

  function evaluate(expression, inputs) {
    const scope = { ...SAFE_FUNCTIONS, ...inputs };
    const names = Object.keys(scope);
    const values = names.map((name) => scope[name]);
    const calculator = Function(
      ...names,
      `"use strict"; return (${expression});`
    );
    return finite(calculator(...values), 'Calculated output');
  }

  function warningsFor(methodId, outputs, inputs) {
    const warnings = [];

    for (const [key, value] of Object.entries(outputs)) {
      const lowered = key.toLowerCase();

      if (
        lowered.includes('percent')
        && (value < 0 || value > 100)
      ) {
        warnings.push(
          `${key} lies outside the expected 0–100% interval.`
        );
      }

      if (
        lowered.includes('fraction')
        && (value < 0 || value > 1)
      ) {
        warnings.push(
          `${key} lies outside the expected 0–1 interval.`
        );
      }
    }

    if (
      Object.hasOwn(inputs, 'pH')
      && (inputs.pH < 0 || inputs.pH > 14)
    ) {
      warnings.push(
        'The stated pH is outside the conventional aqueous 0–14 range.'
      );
    }

    if (
      methodId === 'bc.chromatography_resolution'
      && outputs.resolution < 1.5
    ) {
      warnings.push(
        'Resolution is below 1.5; baseline separation may not be achieved.'
      );
    }

    if (
      methodId === 'bc.coefficient_of_variation'
      && outputs.coefficientOfVariationPercent > 20
    ) {
      warnings.push(
        'Coefficient of variation exceeds 20%; review assay precision.'
      );
    }

    if (
      methodId === 'bc.relative_quantum_yield'
      && outputs.relativeQuantumYield > 1
    ) {
      warnings.push(
        'Relative quantum yield exceeds 1; verify absorbance, integration, and refractive-index corrections.'
      );
    }

    return warnings;
  }

  function run(methodId, rawInputs = {}) {
    const method = METHODS[methodId];

    if (!method) {
      throw new Error(
        `Unknown biochemistry method: ${methodId}`
      );
    }

    const inputs = {};

    for (const specification of method.inputs) {
      const value = finite(
        rawInputs[specification.key],
        specification.label
      );

      if (
        Number.isFinite(specification.min)
        && value < specification.min
      ) {
        throw new Error(
          `${specification.label} must be at least ${specification.min}.`
        );
      }

      if (
        Number.isFinite(specification.max)
        && value > specification.max
      ) {
        throw new Error(
          `${specification.label} must not exceed ${specification.max}.`
        );
      }

      inputs[specification.key] = value;
    }

    const outputs = {};
    const outputUnits = {};
    const expressions = {};

    for (
      const [key, specification]
      of Object.entries(method.outputs)
    ) {
      outputs[key] = evaluate(
        specification.expression,
        inputs
      );
      outputUnits[key] = specification.unit;
      expressions[key] = specification.expression;
    }

    const warnings = warningsFor(
      method.id,
      outputs,
      inputs
    );

    return {
      schema: 'sc-lab-biochemistry-analysis/1.0',
      version: VERSION,
      methodId: method.id,
      methodVersion: method.version,
      category: method.category,
      title: method.title,
      equation: method.equation,
      expressions,
      inputs,
      inputUnits: Object.fromEntries(
        method.inputs.map((item) => [
          item.key,
          item.unit,
        ])
      ),
      outputs,
      outputUnits,
      assumptions: [...(method.assumptions || [])],
      notes: [...(method.notes || [])],
      warnings,
      validation: {
        status: warnings.length ? 'review' : 'screened',
        benchmarkSuite:
          'sc-lab-biochemistry-molecular-analysis-benchmarks/1.0',
      },
      audit: {
        createdAt: new Date().toISOString(),
        engine:
          'sc-lab-biochemistry-molecular-analysis-browser',
        release: VERSION,
      },
    };
  }

  function closeEnough(actual, expected, absolute, relative) {
    const difference = Math.abs(actual - expected);
    const scale = Math.max(
      Math.abs(actual),
      Math.abs(expected),
      1
    );
    return (
      difference <= absolute
      || difference <= relative * scale
    );
  }

  function runBenchmarks() {
    const cases = CATALOG.benchmarks.map((benchmark) => {
      try {
        const result = run(
          benchmark.methodId,
          benchmark.inputs
        );

        const checks = Object.entries(
          benchmark.expected
        ).map(([key, expected]) => {
          const actual = result.outputs[key];
          return {
            key,
            expected,
            actual,
            passed: closeEnough(
              actual,
              expected,
              benchmark.absoluteTolerance,
              benchmark.relativeTolerance
            ),
          };
        });

        return {
          id: benchmark.id,
          methodId: benchmark.methodId,
          passed: checks.every((check) => check.passed),
          checks,
        };
      } catch (error) {
        return {
          id: benchmark.id,
          methodId: benchmark.methodId,
          passed: false,
          error: String(
            error && error.message
              ? error.message
              : error
          ),
          checks: [],
        };
      }
    });

    return {
      schema:
        'sc-lab-biochemistry-molecular-analysis-benchmarks/1.0',
      version: VERSION,
      total: cases.length,
      passed: cases.filter((item) => item.passed).length,
      failed: cases.filter((item) => !item.passed).length,
      cases,
    };
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function formatNumber(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      return String(value);
    }

    const absolute = Math.abs(number);

    if (
      absolute !== 0
      && (absolute < 0.0001 || absolute >= 100000)
    ) {
      return number.toExponential(6);
    }

    return Number(number.toPrecision(8)).toString();
  }

  function methodOptions(category) {
    return CATALOG.methods
      .filter((method) => method.category === category)
      .map(
        (method) => (
          `<option value="${escapeHtml(method.id)}">`
          + `${escapeHtml(method.title)}`
          + '</option>'
        )
      )
      .join('');
  }

  function inputMarkup(method) {
    return method.inputs
      .map((input) => {
        const min = Number.isFinite(input.min)
          ? ` min="${input.min}"`
          : '';
        const max = Number.isFinite(input.max)
          ? ` max="${input.max}"`
          : '';

        return `
          <label class="sc-bma-field">
            <span>${escapeHtml(input.label)}</span>
            <input
              type="number"
              step="any"
              data-bma-input="${escapeHtml(input.key)}"
              value="${escapeHtml(input.default)}"
              ${min}${max}
            />
            <small>${escapeHtml(input.unit)}</small>
          </label>
        `;
      })
      .join('');
  }

  function outputMarkup(result, method) {
    const rows = Object.entries(result.outputs)
      .map(([key, value]) => {
        const specification = method.outputs[key];

        return `
          <tr>
            <th>${escapeHtml(specification.label)}</th>
            <td>${escapeHtml(formatNumber(value))}</td>
            <td>${escapeHtml(specification.unit)}</td>
          </tr>
        `;
      })
      .join('');

    const warnings = result.warnings.length
      ? `
        <div class="sc-bma-warning">
          <strong>Review flags</strong>
          <ul>
            ${result.warnings.map(
              (warning) => `<li>${escapeHtml(warning)}</li>`
            ).join('')}
          </ul>
        </div>
      `
      : `
        <p class="sc-bma-validation">
          Deterministic screening checks passed for the stated inputs.
        </p>
      `;

    return `
      <table class="sc-bma-output-table">
        <thead>
          <tr>
            <th>Output</th>
            <th>Value</th>
            <th>Unit</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
      ${warnings}
      <details class="sc-bma-audit">
        <summary>Analysis and audit record</summary>
        <pre>${escapeHtml(JSON.stringify(result, null, 2))}</pre>
      </details>
    `;
  }

  function dispatchResult(result) {
    if (typeof document === 'undefined') {
      return;
    }

    for (const name of [
      'sc-lab:analysis',
      'sc-lab:analysis-complete',
      'sc-lab:result',
    ]) {
      document.dispatchEvent(
        new CustomEvent(name, {
          detail: result,
        })
      );
    }
  }

  function persistFallback(bucket, result) {
    try {
      const key = `sc-lab:${bucket}`;
      const current = JSON.parse(
        rootWindow.localStorage?.getItem(key) || '[]'
      );

      current.unshift(result);
      rootWindow.localStorage?.setItem(
        key,
        JSON.stringify(current.slice(0, 100))
      );
      return true;
    } catch (_error) {
      return false;
    }
  }

  function saveToProject(result) {
    if (
      Lab.Projects
      && typeof Lab.Projects.addAnalysis === 'function'
    ) {
      Lab.Projects.addAnalysis(result);
      return true;
    }

    if (
      Lab.Projects
      && typeof Lab.Projects.saveAnalysis === 'function'
    ) {
      Lab.Projects.saveAnalysis(result);
      return true;
    }

    return persistFallback('project-analyses', result);
  }

  function addToNotebook(result) {
    if (
      Lab.Notebook
      && typeof Lab.Notebook.add === 'function'
    ) {
      Lab.Notebook.add(result);
      return true;
    }

    return persistFallback('notebook', result);
  }

  function render(mount) {
    if (
      mount.dataset.scBiochemistryVersion === VERSION
      && mount.children.length
    ) {
      return;
    }

    mount.innerHTML = `
      <div class="sc-bma-shell">
        <header class="sc-bma-header">
          <div>
            <p class="sc-bma-kicker">LAB/BIOCHEMISTRY</p>
            <h3>Biochemistry and Molecular Analysis</h3>
            <p>
              Formula-visible calculations for biomolecule
              quantification, proteins, enzyme kinetics, nucleic
              acids, binding, buffers, spectroscopy, separations,
              and laboratory quality control.
            </p>
          </div>
          <span class="sc-bma-version">v${VERSION}</span>
        </header>

        <div class="sc-bma-boundary">
          <strong>Responsible-use boundary.</strong>
          ${escapeHtml(CATALOG.responsibleUse)}
        </div>

        <div class="sc-bma-controls">
          <label class="sc-bma-field">
            <span>Analysis area</span>
            <select data-bma-category>
              ${CATALOG.categories.map(
                (category) => (
                  `<option value="${escapeHtml(category.label)}">`
                  + `${escapeHtml(category.label)}`
                  + '</option>'
                )
              ).join('')}
            </select>
          </label>

          <label class="sc-bma-field">
            <span>Method</span>
            <select data-bma-method></select>
          </label>
        </div>

        <section class="sc-bma-method-card">
          <div class="sc-bma-method-heading">
            <div>
              <p
                class="sc-bma-method-category"
                data-bma-method-category
              ></p>
              <h4 data-bma-method-title></h4>
            </div>
            <code data-bma-equation></code>
          </div>

          <div
            class="sc-bma-input-grid"
            data-bma-inputs
          ></div>

          <div class="sc-bma-actions">
            <button
              type="button"
              class="sc-bma-primary"
              data-bma-run
            >
              Run analysis
            </button>
            <button type="button" data-bma-save disabled>
              Save to project
            </button>
            <button type="button" data-bma-notebook disabled>
              Add to notebook
            </button>
            <button type="button" data-bma-benchmarks>
              Run 48 benchmarks
            </button>
          </div>

          <p
            class="sc-bma-status"
            data-bma-status
            aria-live="polite"
          >
            Select a method and review its inputs.
          </p>

          <div class="sc-bma-results" data-bma-results>
            <p>No analysis has been run.</p>
          </div>
        </section>
      </div>
    `;

    const categorySelect = mount.querySelector(
      '[data-bma-category]'
    );
    const methodSelect = mount.querySelector(
      '[data-bma-method]'
    );
    const inputsRoot = mount.querySelector(
      '[data-bma-inputs]'
    );
    const titleRoot = mount.querySelector(
      '[data-bma-method-title]'
    );
    const categoryRoot = mount.querySelector(
      '[data-bma-method-category]'
    );
    const equationRoot = mount.querySelector(
      '[data-bma-equation]'
    );
    const resultsRoot = mount.querySelector(
      '[data-bma-results]'
    );
    const statusRoot = mount.querySelector(
      '[data-bma-status]'
    );
    const runButton = mount.querySelector(
      '[data-bma-run]'
    );
    const saveButton = mount.querySelector(
      '[data-bma-save]'
    );
    const notebookButton = mount.querySelector(
      '[data-bma-notebook]'
    );
    const benchmarkButton = mount.querySelector(
      '[data-bma-benchmarks]'
    );

    let currentResult = null;

    function selectedMethod() {
      return METHODS[methodSelect.value];
    }

    function refreshMethodList() {
      methodSelect.innerHTML = methodOptions(
        categorySelect.value
      );
      refreshMethod();
    }

    function refreshMethod() {
      const method = selectedMethod();

      if (!method) {
        return;
      }

      titleRoot.textContent = method.title;
      categoryRoot.textContent = method.category;
      equationRoot.textContent = method.equation;
      inputsRoot.innerHTML = inputMarkup(method);
      resultsRoot.innerHTML =
        '<p>No analysis has been run for this method.</p>';
      statusRoot.textContent =
        'Review the formula and stated units before running.';
      currentResult = null;
      saveButton.disabled = true;
      notebookButton.disabled = true;
    }

    function rawInputs(method) {
      return Object.fromEntries(
        method.inputs.map((input) => [
          input.key,
          mount.querySelector(
            `[data-bma-input="${input.key}"]`
          )?.value,
        ])
      );
    }

    categorySelect.addEventListener(
      'change',
      refreshMethodList
    );
    methodSelect.addEventListener(
      'change',
      refreshMethod
    );

    runButton.addEventListener('click', () => {
      const method = selectedMethod();

      try {
        currentResult = run(
          method.id,
          rawInputs(method)
        );
        resultsRoot.innerHTML = outputMarkup(
          currentResult,
          method
        );
        statusRoot.textContent =
          `Completed ${method.title}.`;
        saveButton.disabled = false;
        notebookButton.disabled = false;
        dispatchResult(currentResult);
      } catch (error) {
        currentResult = null;
        saveButton.disabled = true;
        notebookButton.disabled = true;
        statusRoot.textContent =
          error && error.message
            ? error.message
            : String(error);
        resultsRoot.innerHTML =
          '<p class="sc-bma-error">The analysis could not be completed.</p>';
      }
    });

    saveButton.addEventListener('click', () => {
      if (!currentResult) {
        return;
      }

      statusRoot.textContent = saveToProject(currentResult)
        ? 'Analysis saved to the active project record.'
        : 'The project record was unavailable.';
    });

    notebookButton.addEventListener('click', () => {
      if (!currentResult) {
        return;
      }

      statusRoot.textContent = addToNotebook(currentResult)
        ? 'Analysis added to the laboratory notebook.'
        : 'The notebook was unavailable.';
    });

    benchmarkButton.addEventListener('click', () => {
      const report = runBenchmarks();

      resultsRoot.innerHTML = `
        <div class="sc-bma-benchmark-summary">
          <strong>${report.passed} / ${report.total} passed</strong>
          <span>${report.failed} failed</span>
        </div>
        <details class="sc-bma-audit" open>
          <summary>Deterministic benchmark report</summary>
          <pre>${escapeHtml(JSON.stringify(report, null, 2))}</pre>
        </details>
      `;

      statusRoot.textContent = report.failed
        ? 'Benchmark review required.'
        : 'All 48 deterministic benchmarks passed.';

      dispatchResult({
        ...report,
        schema:
          'sc-lab-biochemistry-benchmark-report/1.0',
        title:
          'Biochemistry and Molecular Analysis benchmark report',
        audit: {
          createdAt: new Date().toISOString(),
          engine:
            'sc-lab-biochemistry-molecular-analysis-browser',
          release: VERSION,
        },
      });
    });

    refreshMethodList();
    mount.dataset.scBiochemistryVersion = VERSION;
  }

  function init(root) {
    const selectedRoot = root || (
      typeof document !== 'undefined'
        ? document
        : null
    );

    if (
      !selectedRoot
      || typeof selectedRoot.querySelectorAll !== 'function'
    ) {
      return;
    }

    const mounts = [];

    if (
      selectedRoot.matches
      && selectedRoot.matches(
        '[data-biochemistry-molecular-analysis-root]'
      )
    ) {
      mounts.push(selectedRoot);
    }

    mounts.push(
      ...selectedRoot.querySelectorAll(
        '[data-biochemistry-molecular-analysis-root]'
      )
    );

    for (const mount of new Set(mounts)) {
      render(mount);
    }
  }

  function autoInit() {
    if (typeof document === 'undefined') {
      return;
    }

    if (document.readyState === 'loading') {
      document.addEventListener(
        'DOMContentLoaded',
        () => init(document),
        { once: true }
      );
    } else {
      init(document);
    }

    document.addEventListener(
      'sc-lab:module-opened',
      () => init(document)
    );
  }

  Lab.BiochemistryMolecularAnalysis = {
    VERSION,
    catalog: CATALOG,
    definitions: CATALOG.methods,
    categories: CATALOG.categories,
    benchmarks: CATALOG.benchmarks,
    run,
    runBenchmarks,
    init,
    autoInit,
  };

  autoInit();
})();
