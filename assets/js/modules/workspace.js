(function (w) {
  'use strict';

  const Lab = w.SCLab = w.SCLab || {};

  const modules = [
    { id: 'overview', label: 'Overview', group: 'Project', keywords: ['dashboard', 'project', 'summary'] },
    { id: 'activity', label: 'Activity', group: 'Project', keywords: ['history', 'audit', 'recent'] },
    { id: 'scientific-feeds', label: 'Scientific signals', group: 'Observe', keywords: ['feeds', 'USGS', 'NASA', 'PubMed', 'arXiv', 'events'] },
    { id: 'climate-maps', label: 'Climate maps', group: 'Observe', keywords: ['Earth observation', 'GIBS', 'temperature', 'precipitation', 'aerosol'] },
    { id: 'space-telescopes', label: 'Space observations', group: 'Observe', keywords: ['JWST', 'Hubble', 'NASA', 'astronomy', 'galaxy'] },
    { id: 'marine-biology', label: 'Marine biology', group: 'Observe', keywords: ['OBIS', 'ocean', 'species', 'biodiversity', 'taxon'] },
    { id: 'chemistry', label: 'Chemistry', group: 'Analyze', keywords: ['periodic table', 'stoichiometry', 'molar mass', 'reaction', 'dilution'] },
    { id: 'science-engineering', label: 'Science & engineering', group: 'Analyze', keywords: ['physics', 'biology', 'astronomy', 'materials', 'energy', 'spectrometry', 'calculator'] },
    { id: 'experiments', label: 'Experiments', group: 'Record', keywords: ['method', 'procedure', 'result', 'test'] },
    { id: 'evidence-decisions', label: 'Evidence & decisions', group: 'Record', keywords: ['evidence', 'hypothesis', 'decision', 'claim'] },
    { id: 'notebook', label: 'Notebook', group: 'Record', keywords: ['note', 'observation', 'lab record'] },
    { id: 'documentation', label: 'Documentation', group: 'Record', keywords: ['report', 'technical document', 'brief', 'export'] },
    { id: 'system-status', label: 'Connector status', group: 'System', keywords: ['health', 'source', 'API', 'status'] }
  ];

  const quickTools = [
    { id: 'periodic-table', label: 'Periodic Table', kind: 'chem-tab', module: 'chemistry', tab: 'periodic', keywords: ['elements', 'atomic number', 'chemistry'] },
    { id: 'stoichiometry', label: 'Stoichiometry', kind: 'chem-tab', module: 'chemistry', tab: 'stoichiometry', keywords: ['balance equation', 'molar mass', 'yield'] },
    { id: 'spectrometry', label: 'Spectrometry', kind: 'analysis-tab', module: 'science-engineering', tab: 'spectrometry', keywords: ['spectrum', 'peak', 'baseline', 'UV-vis', 'mass spec'] },
    { id: 'photon', label: 'Photon Energy', kind: 'calculator', module: 'science-engineering', calculatorId: 'photon', keywords: ['wavelength', 'frequency', 'Planck'] },
    { id: 'rlc', label: 'RLC Impedance', kind: 'calculator', module: 'science-engineering', calculatorId: 'rlc', keywords: ['electromagnetism', 'resonance', 'circuit'] },
    { id: 'orbit', label: 'Orbital Mechanics', kind: 'calculator', module: 'science-engineering', calculatorId: 'orbit', keywords: ['astronomy', 'period', 'velocity'] },
    { id: 'uncertainty', label: 'Uncertainty Propagation', kind: 'calculator', module: 'science-engineering', calculatorId: 'uncertainty', keywords: ['measurement', 'error', 'standard uncertainty'] },
    { id: 'pv', label: 'Photovoltaic Output', kind: 'calculator', module: 'science-engineering', calculatorId: 'pv', keywords: ['energy', 'solar', 'power'] }
  ];

  const trace = [
    { key: 'evidence', label: 'Sources', module: 'scientific-feeds', count: p => new Set((p.evidence || []).map(x => x.source || x.record?.source).filter(Boolean)).size },
    { key: 'evidence', label: 'Evidence', module: 'evidence-decisions', count: p => (p.evidence || []).length },
    { key: 'hypotheses', label: 'Hypotheses', module: 'evidence-decisions', count: p => (p.hypotheses || []).length },
    { key: 'calculations', label: 'Calculations', module: 'science-engineering', count: p => (p.calculations || []).length },
    { key: 'experiments', label: 'Experiments', module: 'experiments', count: p => (p.experiments || []).length },
    { key: 'decisions', label: 'Decisions', module: 'evidence-decisions', count: p => (p.decisions || []).length },
    { key: 'documents', label: 'Documents', module: 'documentation', count: p => (p.documents || []).length }
  ];

  function normalize(value) {
    return String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  }

  function search(query, calculatorDefinitions) {
    const q = normalize(query);
    if (!q) return [];

    const calculatorItems = (calculatorDefinitions || []).map(def => ({
      id: def.id,
      label: def.name,
      group: def.domain,
      kind: 'calculator',
      module: 'science-engineering',
      calculatorId: def.id,
      keywords: [def.domain, ...(def.fields || []).map(field => field[1])]
    }));

    return [...modules.map(x => ({ ...x, kind: 'module' })), ...quickTools, ...calculatorItems]
      .map(item => {
        const haystack = normalize([item.label, item.group, ...(item.keywords || [])].join(' '));
        let score = 0;
        if (normalize(item.label) === q) score += 100;
        if (normalize(item.label).startsWith(q)) score += 50;
        if (haystack.includes(q)) score += 20;
        q.split(' ').forEach(token => { if (token && haystack.includes(token)) score += 4; });
        return { item, score };
      })
      .filter(row => row.score > 0)
      .sort((a, b) => b.score - a.score || a.item.label.localeCompare(b.item.label))
      .slice(0, 10)
      .map(row => row.item);
  }

  function traceCounts(project) {
    return trace.map(stage => ({
      ...stage,
      value: stage.count(project || {})
    }));
  }

  function projectTotal(project) {
    return ['evidence', 'experiments', 'hypotheses', 'decisions', 'notes', 'calculations', 'documents', 'maps']
      .reduce((total, key) => total + ((project && project[key]) || []).length, 0);
  }

  Lab.Workspace = { modules, quickTools, trace, search, traceCounts, projectTotal };
})(window);
