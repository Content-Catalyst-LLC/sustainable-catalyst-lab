(function (w) {
  'use strict';
  const Lab = w.SCLab = w.SCLab || {};

  function num(value, name) {
    const out = Number(value);
    if (!Number.isFinite(out)) throw new Error(`Invalid ${name}`);
    return out;
  }

  function parse(text) {
    const points = [];
    String(text).split(/\r?\n/).forEach((line, lineIndex) => {
      const trimmed = line.trim();
      if (!trimmed || /^#/.test(trimmed)) return;
      const parts = trimmed.split(/[\s,;\t]+/);
      if (parts.length < 2) return;
      const x = Number(parts[0]), y = Number(parts[1]);
      if (Number.isFinite(x) && Number.isFinite(y)) points.push({ x, y, sourceLine: lineIndex + 1 });
    });
    points.sort((a, b) => a.x - b.x);
    if (points.length < 2) throw new Error('At least two numeric x,y points are required');
    return points.map(({ x, y }) => ({ x, y }));
  }

  function clone(points) { return points.map(point => ({ x: Number(point.x), y: Number(point.y) })); }

  function linearBaseline(points) {
    const first = points[0], last = points[points.length - 1], dx = last.x - first.x || 1;
    return points.map(point => {
      const base = first.y + (last.y - first.y) * (point.x - first.x) / dx;
      return { x: point.x, y: point.y - base };
    });
  }

  function rollingMinimumBaseline(points, windowSize = 15) {
    const radius = Math.max(1, Math.floor(Number(windowSize) / 2));
    const minima = points.map((point, index) => {
      let min = Infinity;
      for (let i = Math.max(0, index - radius); i <= Math.min(points.length - 1, index + radius); i++) min = Math.min(min, points[i].y);
      return { x: point.x, y: min };
    });
    const smoothBase = smooth(minima, Math.max(2, Math.floor(radius / 2)));
    return points.map((point, index) => ({ x: point.x, y: point.y - smoothBase[index].y }));
  }

  function baseline(points, method = 'linear', options = {}) {
    if (!points.length) return [];
    if (method === 'rolling-minimum') return rollingMinimumBaseline(points, options.windowSize || 15);
    return linearBaseline(points);
  }

  function smooth(points, radius = 2) {
    const n = Math.max(1, Math.floor(Number(radius)));
    return points.map((point, index) => {
      let sum = 0, count = 0;
      for (let i = Math.max(0, index - n); i <= Math.min(points.length - 1, index + n); i++) {
        sum += points[i].y;
        count++;
      }
      return { x: point.x, y: sum / count };
    });
  }

  function medianSmooth(points, radius = 2) {
    const n = Math.max(1, Math.floor(Number(radius)));
    return points.map((point, index) => {
      const values = [];
      for (let i = Math.max(0, index - n); i <= Math.min(points.length - 1, index + n); i++) values.push(points[i].y);
      values.sort((a, b) => a - b);
      const middle = Math.floor(values.length / 2);
      const y = values.length % 2 ? values[middle] : (values[middle - 1] + values[middle]) / 2;
      return { x: point.x, y };
    });
  }

  function normalize(points, mode = 'max') {
    if (!points.length) return [];
    const ys = points.map(point => point.y);
    let divisor = 1, offset = 0;
    if (mode === 'area') divisor = Math.abs(integrate(points)) || 1;
    else if (mode === 'minmax') {
      offset = Math.min(...ys);
      divisor = Math.max(...ys) - offset || 1;
    } else divisor = Math.max(...ys.map(Math.abs)) || 1;
    return points.map(point => ({ x: point.x, y: (point.y - offset) / divisor }));
  }

  function derivative(points, order = 1) {
    let current = clone(points);
    const count = Math.max(1, Math.floor(Number(order)));
    for (let pass = 0; pass < count; pass++) {
      current = current.map((point, index) => {
        if (index === 0) {
          const next = current[1];
          return { x: point.x, y: (next.y - point.y) / (next.x - point.x || 1) };
        }
        if (index === current.length - 1) {
          const prev = current[index - 1];
          return { x: point.x, y: (point.y - prev.y) / (point.x - prev.x || 1) };
        }
        const prev = current[index - 1], next = current[index + 1];
        return { x: point.x, y: (next.y - prev.y) / (next.x - prev.x || 1) };
      });
    }
    return current;
  }

  function transmittanceToAbsorbance(points, inputScale = 'fraction') {
    return points.map(point => {
      let transmittance = point.y;
      if (inputScale === 'percent') transmittance /= 100;
      if (transmittance <= 0) throw new Error('Transmittance values must be greater than zero');
      return { x: point.x, y: -Math.log10(transmittance) };
    });
  }

  function absorbanceToTransmittance(points, outputScale = 'fraction') {
    return points.map(point => {
      let value = Math.pow(10, -point.y);
      if (outputScale === 'percent') value *= 100;
      return { x: point.x, y: value };
    });
  }

  function integrate(points, fromX = -Infinity, toX = Infinity) {
    const rows = points.filter(point => point.x >= fromX && point.x <= toX);
    let area = 0;
    for (let i = 1; i < rows.length; i++) area += (rows[i].x - rows[i - 1].x) * (rows[i].y + rows[i - 1].y) / 2;
    return area;
  }

  function estimateNoise(points) {
    if (points.length < 3) return 0;
    const diffs = [];
    for (let i = 1; i < points.length; i++) diffs.push(points[i].y - points[i - 1].y);
    const mean = diffs.reduce((sum, value) => sum + value, 0) / diffs.length;
    const variance = diffs.reduce((sum, value) => sum + (value - mean) ** 2, 0) / Math.max(1, diffs.length - 1);
    return Math.sqrt(variance) / Math.sqrt(2);
  }

  function peakWidth(points, index, baselineY = 0) {
    const peak = points[index];
    const half = baselineY + (peak.y - baselineY) / 2;
    let left = index, right = index;
    while (left > 0 && points[left].y > half) left--;
    while (right < points.length - 1 && points[right].y > half) right++;
    function interpolate(a, b) {
      const dy = b.y - a.y;
      if (dy === 0) return a.x;
      return a.x + (half - a.y) * (b.x - a.x) / dy;
    }
    const leftX = left === index ? peak.x : interpolate(points[left], points[Math.min(left + 1, index)]);
    const rightX = right === index ? peak.x : interpolate(points[Math.max(right - 1, index)], points[right]);
    return Math.max(0, rightX - leftX);
  }

  function peaks(points, options = {}) {
    if (typeof options === 'number') options = { threshold: options };
    const ys = points.map(point => point.y), min = Math.min(...ys), max = Math.max(...ys);
    const threshold = Number.isFinite(Number(options.threshold)) ? Number(options.threshold) : min + (max - min) * 0.25;
    const minDistance = Math.max(0, Number(options.minDistance || 0));
    const minProminence = Math.max(0, Number(options.minProminence || 0));
    const candidates = [];
    for (let i = 1; i < points.length - 1; i++) {
      if (!(points[i].y > points[i - 1].y && points[i].y >= points[i + 1].y && points[i].y >= threshold)) continue;
      let leftMin = points[i].y, rightMin = points[i].y;
      for (let j = i - 1; j >= 0; j--) { leftMin = Math.min(leftMin, points[j].y); if (points[j].y > points[i].y) break; }
      for (let j = i + 1; j < points.length; j++) { rightMin = Math.min(rightMin, points[j].y); if (points[j].y > points[i].y) break; }
      const prominence = points[i].y - Math.max(leftMin, rightMin);
      if (prominence < minProminence) continue;
      candidates.push({ index: i, x: points[i].x, y: points[i].y, prominence, fwhm: peakWidth(points, i, Math.max(leftMin, rightMin)) });
    }
    candidates.sort((a, b) => b.y - a.y);
    const accepted = [];
    candidates.forEach(candidate => {
      if (accepted.every(existing => Math.abs(existing.x - candidate.x) >= minDistance)) accepted.push(candidate);
    });
    return accepted.sort((a, b) => a.x - b.x);
  }

  function centroid(points, fromX = -Infinity, toX = Infinity) {
    const rows = points.filter(point => point.x >= fromX && point.x <= toX);
    const total = rows.reduce((sum, point) => sum + Math.max(0, point.y), 0);
    if (!total) return null;
    return rows.reduce((sum, point) => sum + point.x * Math.max(0, point.y), 0) / total;
  }

  function compare(a, b) {
    if (!a.length || !b.length) throw new Error('Two spectra are required');
    const bMap = new Map(b.map(point => [String(point.x), point.y]));
    const paired = a.filter(point => bMap.has(String(point.x))).map(point => [point.y, bMap.get(String(point.x))]);
    if (paired.length < 2) throw new Error('Spectra need at least two shared x values');
    let dot = 0, aa = 0, bb = 0, squaredError = 0;
    paired.forEach(([x, y]) => { dot += x * y; aa += x * x; bb += y * y; squaredError += (x - y) ** 2; });
    return { sharedPoints: paired.length, cosineSimilarity: dot / (Math.sqrt(aa) * Math.sqrt(bb) || 1), rmse: Math.sqrt(squaredError / paired.length) };
  }

  function linearRegression(points) {
    if (!Array.isArray(points) || points.length < 2) throw new Error('At least two calibration points are required');
    const rows = points.map((point, index) => ({ x: num(point.x, `x${index + 1}`), y: num(point.y, `y${index + 1}`) }));
    const count = rows.length;
    const sx = rows.reduce((s, p) => s + p.x, 0), sy = rows.reduce((s, p) => s + p.y, 0);
    const sxx = rows.reduce((s, p) => s + p.x * p.x, 0), sxy = rows.reduce((s, p) => s + p.x * p.y, 0);
    const denominator = count * sxx - sx * sx;
    if (Math.abs(denominator) < 1e-15) throw new Error('Calibration x values must vary');
    const slope = (count * sxy - sx * sy) / denominator;
    const intercept = (sy - slope * sx) / count;
    const meanY = sy / count;
    const ssTot = rows.reduce((s, p) => s + (p.y - meanY) ** 2, 0);
    const ssRes = rows.reduce((s, p) => s + (p.y - (slope * p.x + intercept)) ** 2, 0);
    const residualSD = count > 2 ? Math.sqrt(ssRes / (count - 2)) : 0;
    return { count, slope, intercept, rSquared: ssTot === 0 ? 1 : 1 - ssRes / ssTot, residualSD, points: rows };
  }

  function calibration(points, unknownSignal) {
    const regression = linearRegression(points);
    const signal = num(unknownSignal, 'unknown signal');
    if (Math.abs(regression.slope) < 1e-15) throw new Error('Calibration slope is zero');
    return {
      ...regression,
      unknownSignal: signal,
      estimatedConcentration: (signal - regression.intercept) / regression.slope,
      lod: 3.3 * regression.residualSD / Math.abs(regression.slope),
      loq: 10 * regression.residualSD / Math.abs(regression.slope)
    };
  }

  function methodDefaults(method) {
    const map = {
      uvvis: { xLabel: 'Wavelength (nm)', yLabel: 'Absorbance', baseline: 'linear' },
      ir: { xLabel: 'Wavenumber (cm⁻¹)', yLabel: 'Absorbance / transmittance', baseline: 'rolling-minimum' },
      raman: { xLabel: 'Raman shift (cm⁻¹)', yLabel: 'Intensity', baseline: 'rolling-minimum' },
      fluorescence: { xLabel: 'Wavelength (nm)', yLabel: 'Intensity', baseline: 'linear' },
      mass: { xLabel: 'm/z', yLabel: 'Relative abundance', baseline: 'linear' },
      generic: { xLabel: 'x', yLabel: 'Signal', baseline: 'linear' }
    };
    return map[method] || map.generic;
  }

  function svg(points, peakList = [], options = {}) {
    if (!points.length) return '';
    const W = 760, H = 360, left = 58, right = 24, top = 24, bottom = 48;
    const xs = points.map(p => p.x), ys = points.map(p => p.y);
    const xmin = Math.min(...xs), xmax = Math.max(...xs), ymin = Math.min(...ys), ymax = Math.max(...ys);
    const sx = x => left + (x - xmin) / (xmax - xmin || 1) * (W - left - right);
    const sy = y => H - bottom - (y - ymin) / (ymax - ymin || 1) * (H - top - bottom);
    const path = points.map((p, i) => `${i ? 'L' : 'M'} ${sx(p.x).toFixed(2)} ${sy(p.y).toFixed(2)}`).join(' ');
    const grid = [0, 0.25, 0.5, 0.75, 1].map(t => {
      const y = top + t * (H - top - bottom);
      return `<line x1="${left}" y1="${y}" x2="${W-right}" y2="${y}" stroke="#e3e8ec"/><text x="${left-8}" y="${y+4}" text-anchor="end" font-size="10" fill="#68737d">${(ymax - t * (ymax-ymin)).toPrecision(4)}</text>`;
    }).join('');
    const peakDots = peakList.map(p => `<g><circle cx="${sx(p.x)}" cy="${sy(p.y)}" r="4" fill="#c40000"><title>${p.x}, ${p.y}</title></circle><text x="${sx(p.x)}" y="${sy(p.y)-8}" text-anchor="middle" font-size="9" fill="#8e0000">${Number(p.x).toPrecision(5)}</text></g>`).join('');
    const defaults = methodDefaults(options.method || 'generic');
    return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Spectrum"><rect width="100%" height="100%" fill="white"/>${grid}<line x1="${left}" y1="${H-bottom}" x2="${W-right}" y2="${H-bottom}" stroke="#68737d"/><line x1="${left}" y1="${top}" x2="${left}" y2="${H-bottom}" stroke="#68737d"/><path d="${path}" fill="none" stroke="#1f5f89" stroke-width="2"/>${peakDots}<text x="${(left+W-right)/2}" y="${H-10}" text-anchor="middle" font-size="11" fill="#3c4650">${options.xLabel || defaults.xLabel}</text><text transform="translate(14 ${(top+H-bottom)/2}) rotate(-90)" text-anchor="middle" font-size="11" fill="#3c4650">${options.yLabel || defaults.yLabel}</text></svg>`;
  }

  function csv(points) { return 'x,y\n' + points.map(point => `${point.x},${point.y}`).join('\n'); }

  Lab.Spectrometry = {
    parse, clone, baseline, linearBaseline, rollingMinimumBaseline, smooth, medianSmooth, normalize,
    derivative, transmittanceToAbsorbance, absorbanceToTransmittance, integrate, estimateNoise,
    peaks, peakWidth, centroid, compare, linearRegression, calibration, methodDefaults, svg, csv
  };
})(window);
