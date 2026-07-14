(() => {
  'use strict';

  const W = typeof window !== 'undefined' ? window : globalThis;
  const Lab = W.SCLab = W.SCLab || {};
  const VERSION = '0.23.2';
  const ENGINE_VERSION = '0.23.0';
  const PRODUCTION_VERSION = '0.23.1';
  const ROOT_SELECTOR = '[data-biosignal-visualization-root]';
  const CONTRACT = {"schema":"sc-lab-biosignal-visualization-comparison-contract/1.0","version":"0.23.2","title":"Biosignal Visualization, Annotation, and Comparative Analysis","modes":[{"id":"synchronized-multichannel","label":"Synchronized multi-channel","description":"Stack and inspect multiple channels against a shared time axis."},{"id":"raw-filtered-overlay","label":"Raw and filtered overlay","description":"Compare unprocessed and smoothed or filtered waveforms."},{"id":"annotation-regions","label":"Annotations and regions","description":"Add event, artifact, quality, note, and interval records."},{"id":"event-intervals","label":"Event and interval analysis","description":"Summarize event rates, durations, burden, and spacing."},{"id":"channel-alignment","label":"Channel alignment","description":"Shift channels and inspect overlap and alignment quality."},{"id":"lag-correlation-scan","label":"Lag and correlation scan","description":"Find the lag with the strongest absolute correlation."},{"id":"run-overlay-comparison","label":"Run overlay comparison","description":"Compare repeated runs or research records on a common window."},{"id":"comparative-summary","label":"Comparative summary","description":"Produce explicit similarity, error, feature, and coverage metrics."}],"analysisMethods":[{"id":"descriptive-features","label":"Descriptive waveform features","operation":"descriptive_features"},{"id":"min-max-normalize","label":"Min-max normalization","operation":"min_max_normalize"},{"id":"z-score-normalize","label":"Z-score normalization","operation":"z_score_normalize"},{"id":"moving-average","label":"Moving average","operation":"moving_average"},{"id":"linear-resample","label":"Linear resampling","operation":"linear_resample"},{"id":"pearson-correlation","label":"Pearson correlation","operation":"pearson_correlation"},{"id":"mean-absolute-error","label":"Mean absolute error","operation":"mean_absolute_error"},{"id":"root-mean-square-error","label":"Root mean square error","operation":"root_mean_square_error"},{"id":"normalized-rmse","label":"Normalized root mean square error","operation":"normalized_rmse"},{"id":"shift-series","label":"Shift series by lag","operation":"shift_series"},{"id":"best-lag-correlation","label":"Best lag correlation","operation":"best_lag_correlation"},{"id":"event-rate","label":"Event rate","operation":"event_rate"},{"id":"interval-summary","label":"Interval summary","operation":"interval_summary"},{"id":"annotation-coverage","label":"Annotation coverage","operation":"annotation_coverage"},{"id":"common-time-window","label":"Common time window","operation":"common_time_window"},{"id":"compare-runs","label":"Run comparison","operation":"compare_runs"}],"benchmarks":[{"id":"benchmark-descriptive-features","methodId":"descriptive-features","inputs":{"samples":[-1,1,-1,1],"sampleRateHz":100},"expected":{"sampleCount":4,"sampleRateHz":100.0,"durationSeconds":0.03,"mean":0.0,"standardDeviation":1.1547005383792515,"rms":1.0,"minimum":-1.0,"maximum":1.0,"peakToPeak":2.0,"zeroCrossingCount":3,"zeroCrossingRate":100.0,"crestFactor":1.0}},{"id":"benchmark-min-max-normalize","methodId":"min-max-normalize","inputs":{"samples":[2,4,6]},"expected":[0.0,0.5,1.0]},{"id":"benchmark-z-score-normalize","methodId":"z-score-normalize","inputs":{"samples":[1,2,3]},"expected":[-1.0,0.0,1.0]},{"id":"benchmark-moving-average","methodId":"moving-average","inputs":{"samples":[1,2,3,4],"windowSize":2},"expected":[1.0,1.5,2.5,3.5]},{"id":"benchmark-linear-resample","methodId":"linear-resample","inputs":{"samples":[0,1,0],"sourceRateHz":2,"targetRateHz":4},"expected":[0.0,0.5,1.0,0.5,0.0]},{"id":"benchmark-pearson-correlation","methodId":"pearson-correlation","inputs":{"reference":[1,2,3,4],"comparison":[2,4,6,8]},"expected":1.0},{"id":"benchmark-mean-absolute-error","methodId":"mean-absolute-error","inputs":{"reference":[1,2,3],"comparison":[1,4,2]},"expected":1.0},{"id":"benchmark-root-mean-square-error","methodId":"root-mean-square-error","inputs":{"reference":[1,2,3],"comparison":[1,4,2]},"expected":1.2909944487358056},{"id":"benchmark-normalized-rmse","methodId":"normalized-rmse","inputs":{"reference":[0,2,4],"comparison":[0,3,3]},"expected":0.2041241452319315},{"id":"benchmark-shift-series","methodId":"shift-series","inputs":{"reference":[1,2,3,4,5],"comparison":[0,1,2,3,4],"lagSamples":1},"expected":{"lagSamples":1,"reference":[2.0,3.0,4.0,5.0],"comparison":[0.0,1.0,2.0,3.0],"overlapCount":4}},{"id":"benchmark-best-lag-correlation","methodId":"best-lag-correlation","inputs":{"reference":[1,4,2,5,0,3],"comparison":[4,2,5,0,3,9],"maxLagSamples":2},"expected":{"bestLagSamples":1,"bestCorrelation":1.0,"overlapCount":5,"scan":[{"lagSamples":-2,"correlation":0.24182541670333724,"overlapCount":4},{"lagSamples":-1,"correlation":-0.30311770301376645,"overlapCount":5},{"lagSamples":0,"correlation":-0.2969083193112956,"overlapCount":6},{"lagSamples":1,"correlation":1.0,"overlapCount":5},{"lagSamples":2,"correlation":-0.6860502374404129,"overlapCount":4}]}},{"id":"benchmark-event-rate","methodId":"event-rate","inputs":{"eventCount":12,"durationSeconds":60},"expected":12.0},{"id":"benchmark-interval-summary","methodId":"interval-summary","inputs":{"intervals":[{"startSeconds":0,"endSeconds":2},{"startSeconds":4,"endSeconds":7}]},"expected":{"intervalCount":2,"totalDurationSeconds":5.0,"meanDurationSeconds":2.5,"minimumDurationSeconds":2.0,"maximumDurationSeconds":3.0,"coveredSpanSeconds":7.0,"burdenPercent":71.42857142857143}},{"id":"benchmark-annotation-coverage","methodId":"annotation-coverage","inputs":{"annotations":[{"type":"artifact","startSeconds":1,"endSeconds":3},{"type":"event","startSeconds":2,"endSeconds":4}],"windowStartSeconds":0,"windowEndSeconds":10},"expected":{"annotationCount":2,"coveredSeconds":3.0,"coveragePercent":30.0,"typeCounts":{"artifact":1,"event":1},"mergedIntervals":[{"startSeconds":1.0,"endSeconds":4.0}]}},{"id":"benchmark-common-time-window","methodId":"common-time-window","inputs":{"runA":{"startSeconds":0,"durationSeconds":10},"runB":{"startSeconds":3,"durationSeconds":10}},"expected":{"startSeconds":3.0,"endSeconds":10.0,"durationSeconds":7.0,"overlap":true}},{"id":"benchmark-compare-runs","methodId":"compare-runs","inputs":{"reference":[0,1,2,3],"comparison":[0,1.2,1.8,3.1],"sampleRateHz":100},"expected":{"sampleCount":4,"sampleRateHz":100.0,"correlation":0.9912398251570825,"meanAbsoluteError":0.125,"rootMeanSquareError":0.15,"normalizedRootMeanSquareError":0.049999999999999996,"referenceFeatures":{"sampleCount":4,"sampleRateHz":100.0,"durationSeconds":0.03,"mean":1.5,"standardDeviation":1.2909944487358056,"rms":1.8708286933869707,"minimum":0.0,"maximum":3.0,"peakToPeak":3.0,"zeroCrossingCount":0,"zeroCrossingRate":0.0,"crestFactor":1.6035674514745464},"comparisonFeatures":{"sampleCount":4,"sampleRateHz":100.0,"durationSeconds":0.03,"mean":1.525,"standardDeviation":1.2893796958227628,"rms":1.89010581714358,"minimum":0.0,"maximum":3.1,"peakToPeak":3.1,"zeroCrossingCount":0,"zeroCrossingRate":0.0,"crestFactor":1.6401198133366264}}}],"annotationTypes":[{"id":"event","label":"Event"},{"id":"artifact","label":"Artifact"},{"id":"region","label":"Region"},{"id":"note","label":"Note"},{"id":"quality","label":"Quality flag"},{"id":"intervention","label":"Intervention marker"}],"imports":["channel-csv","multi-channel-csv","analysis-json","annotation-json"],"exports":["svg","csv","json","provenance-record","project-record","notebook-entry"],"preservedEngine":{"version":"0.23.0","methodCount":48,"benchmarkCount":48,"categoryCount":8},"productionLayer":{"version":"0.23.1"},"responsibleUse":{"scope":"Research, education, prototyping, and non-clinical comparative signal analysis.","boundary":"Not for diagnosis, treatment, patient monitoring, alarm generation, or clinical decision-making."}};
  const state = {
    dataset: null,
    annotations: [],
    analysis: null,
    svg: '',
    lastError: null,
    rendered: false,
  };

  function finite(value, label) {
    const number = Number(value);
    if (!Number.isFinite(number)) throw new Error(`${label} must be numerical and finite.`);
    return number;
  }
  function positive(value, label) {
    const number = finite(value, label);
    if (number <= 0) throw new Error(`${label} must be greater than zero.`);
    return number;
  }
  function values(value, label, minimum = 1) {
    let raw = value;
    if (typeof raw === 'string') {
      const trimmed = raw.trim();
      raw = trimmed.startsWith('[') ? JSON.parse(trimmed) : trimmed.split(/[,\s]+/).filter(Boolean);
    }
    if (!Array.isArray(raw)) throw new Error(`${label} must be an array.`);
    const result = raw.map((item, index) => finite(item, `${label}[${index}]`));
    if (result.length < minimum) throw new Error(`${label} requires at least ${minimum} values.`);
    return result;
  }
  function paired(reference, comparison) {
    const a = values(reference, 'reference', 2);
    const b = values(comparison, 'comparison', 2);
    if (a.length !== b.length) throw new Error('reference and comparison must have equal length.');
    return [a, b];
  }
  const mean = (items) => items.reduce((sum, item) => sum + item, 0) / items.length;
  function standardDeviation(items) {
    if (items.length < 2) return 0;
    const average = mean(items);
    return Math.sqrt(items.reduce((sum, item) => sum + (item - average) ** 2, 0) / (items.length - 1));
  }
  const rms = (items) => Math.sqrt(mean(items.map((item) => item * item)));

  function descriptiveFeatures(samples, sampleRateHz = 1) {
    const data = values(samples, 'samples', 2);
    const rate = positive(sampleRateHz, 'sampleRateHz');
    const average = mean(data);
    const rootMeanSquare = rms(data);
    let crossings = 0;
    for (let index = 1; index < data.length; index += 1) {
      if ((data[index - 1] < 0 && data[index] >= 0) || (data[index - 1] >= 0 && data[index] < 0)) crossings += 1;
    }
    return {
      sampleCount: data.length,
      sampleRateHz: rate,
      durationSeconds: (data.length - 1) / rate,
      mean: average,
      standardDeviation: standardDeviation(data),
      rms: rootMeanSquare,
      minimum: Math.min(...data),
      maximum: Math.max(...data),
      peakToPeak: Math.max(...data) - Math.min(...data),
      zeroCrossingCount: crossings,
      zeroCrossingRate: crossings / (data.length - 1) * rate,
      crestFactor: rootMeanSquare ? Math.max(...data.map(Math.abs)) / rootMeanSquare : 0,
    };
  }
  function minMaxNormalize(samples) {
    const data = values(samples, 'samples');
    const minimum = Math.min(...data);
    const span = Math.max(...data) - minimum;
    return span === 0 ? data.map(() => 0) : data.map((value) => (value - minimum) / span);
  }
  function zScoreNormalize(samples) {
    const data = values(samples, 'samples', 2);
    const average = mean(data);
    const deviation = standardDeviation(data);
    return deviation === 0 ? data.map(() => 0) : data.map((value) => (value - average) / deviation);
  }
  function movingAverage(samples, windowSize) {
    const data = values(samples, 'samples');
    const window = Math.trunc(positive(windowSize, 'windowSize'));
    if (window > data.length) throw new Error('windowSize cannot exceed the sample count.');
    return data.map((_, index) => mean(data.slice(Math.max(0, index - window + 1), index + 1)));
  }
  function linearResample(samples, sourceRateHz, targetRateHz) {
    const data = values(samples, 'samples', 2);
    const source = positive(sourceRateHz, 'sourceRateHz');
    const target = positive(targetRateHz, 'targetRateHz');
    const duration = (data.length - 1) / source;
    const count = Math.max(2, Math.round(duration * target) + 1);
    return Array.from({ length: count }, (_, index) => {
      const position = index / target * source;
      const left = Math.min(data.length - 1, Math.floor(position));
      const right = Math.min(data.length - 1, left + 1);
      const fraction = position - left;
      return data[left] + (data[right] - data[left]) * fraction;
    });
  }
  function pearsonCorrelation(reference, comparison) {
    const [a, b] = paired(reference, comparison);
    const am = mean(a); const bm = mean(b);
    let numerator = 0; let aSquares = 0; let bSquares = 0;
    a.forEach((value, index) => {
      const ad = value - am; const bd = b[index] - bm;
      numerator += ad * bd; aSquares += ad * ad; bSquares += bd * bd;
    });
    const denominator = Math.sqrt(aSquares * bSquares);
    if (denominator === 0) throw new Error('Correlation requires non-constant arrays.');
    return numerator / denominator;
  }
  function meanAbsoluteError(reference, comparison) {
    const [a, b] = paired(reference, comparison);
    return mean(a.map((value, index) => Math.abs(value - b[index])));
  }
  function rootMeanSquareError(reference, comparison) {
    const [a, b] = paired(reference, comparison);
    return Math.sqrt(mean(a.map((value, index) => (value - b[index]) ** 2)));
  }
  function normalizedRmse(reference, comparison) {
    const [a, b] = paired(reference, comparison);
    const span = Math.max(...a) - Math.min(...a);
    if (span === 0) throw new Error('Normalized RMSE requires a non-zero reference range.');
    return rootMeanSquareError(a, b) / span;
  }
  function shiftSeries(reference, comparison, lagSamples) {
    const [a, b] = paired(reference, comparison);
    const lag = Math.trunc(finite(lagSamples, 'lagSamples'));
    if (Math.abs(lag) >= a.length - 1) throw new Error('Absolute lag must leave at least two overlapping samples.');
    let alignedA; let alignedB;
    if (lag > 0) { alignedA = a.slice(lag); alignedB = b.slice(0, -lag); }
    else if (lag < 0) { alignedA = a.slice(0, lag); alignedB = b.slice(-lag); }
    else { alignedA = a; alignedB = b; }
    return { lagSamples: lag, reference: alignedA, comparison: alignedB, overlapCount: alignedA.length };
  }
  function bestLagCorrelation(reference, comparison, maxLagSamples) {
    const [a, b] = paired(reference, comparison);
    const maximum = Math.min(Math.abs(Math.trunc(finite(maxLagSamples, 'maxLagSamples'))), a.length - 2);
    const scan = [];
    for (let lag = -maximum; lag <= maximum; lag += 1) {
      const aligned = shiftSeries(a, b, lag);
      let correlation = 0;
      try { correlation = pearsonCorrelation(aligned.reference, aligned.comparison); } catch (_) { correlation = 0; }
      scan.push({ lagSamples: lag, correlation, overlapCount: aligned.overlapCount });
    }
    const best = [...scan].sort((left, right) => Math.abs(right.correlation) - Math.abs(left.correlation) || Math.abs(left.lagSamples) - Math.abs(right.lagSamples))[0];
    return { bestLagSamples: best.lagSamples, bestCorrelation: best.correlation, overlapCount: best.overlapCount, scan };
  }
  const eventRate = (eventCount, durationSeconds) => finite(eventCount, 'eventCount') * 60 / positive(durationSeconds, 'durationSeconds');
  function intervalSummary(intervals) {
    if (!Array.isArray(intervals) || !intervals.length) throw new Error('intervals must contain at least one interval.');
    const parsed = intervals.map((interval, index) => {
      const start = finite(interval.startSeconds, `intervals[${index}].startSeconds`);
      const end = finite(interval.endSeconds, `intervals[${index}].endSeconds`);
      if (end < start) throw new Error(`intervals[${index}] ends before it starts.`);
      return { start, end, duration: end - start };
    });
    const span = Math.max(...parsed.map((item) => item.end)) - Math.min(...parsed.map((item) => item.start));
    const durations = parsed.map((item) => item.duration);
    const total = durations.reduce((sum, item) => sum + item, 0);
    return { intervalCount: parsed.length, totalDurationSeconds: total, meanDurationSeconds: mean(durations), minimumDurationSeconds: Math.min(...durations), maximumDurationSeconds: Math.max(...durations), coveredSpanSeconds: span, burdenPercent: span > 0 ? total / span * 100 : 0 };
  }
  function annotationCoverage(annotations, windowStartSeconds, windowEndSeconds) {
    if (!Array.isArray(annotations)) throw new Error('annotations must be an array.');
    const start = finite(windowStartSeconds, 'windowStartSeconds');
    const end = finite(windowEndSeconds, 'windowEndSeconds');
    if (end <= start) throw new Error('windowEndSeconds must exceed windowStartSeconds.');
    const clipped = []; const typeCounts = {};
    annotations.forEach((annotation, index) => {
      const aStart = finite(annotation.startSeconds, `annotations[${index}].startSeconds`);
      const aEnd = finite(annotation.endSeconds ?? aStart, `annotations[${index}].endSeconds`);
      if (aEnd < aStart) throw new Error(`annotations[${index}] ends before it starts.`);
      const cStart = Math.max(start, aStart); const cEnd = Math.min(end, aEnd);
      if (cEnd > cStart) clipped.push([cStart, cEnd]);
      const type = String(annotation.type || 'note'); typeCounts[type] = (typeCounts[type] || 0) + 1;
    });
    clipped.sort((a, b) => a[0] - b[0]);
    const merged = [];
    clipped.forEach(([aStart, aEnd]) => {
      if (!merged.length || aStart > merged.at(-1)[1]) merged.push([aStart, aEnd]);
      else merged.at(-1)[1] = Math.max(merged.at(-1)[1], aEnd);
    });
    const covered = merged.reduce((sum, item) => sum + item[1] - item[0], 0);
    return { annotationCount: annotations.length, coveredSeconds: covered, coveragePercent: covered / (end - start) * 100, typeCounts, mergedIntervals: merged.map((item) => ({ startSeconds: item[0], endSeconds: item[1] })) };
  }
  function commonTimeWindow(runA, runB) {
    if (!runA || !runB || typeof runA !== 'object' || typeof runB !== 'object') throw new Error('runA and runB must be objects.');
    const aStart = finite(runA.startSeconds ?? 0, 'runA.startSeconds');
    const bStart = finite(runB.startSeconds ?? 0, 'runB.startSeconds');
    const aDuration = positive(runA.durationSeconds, 'runA.durationSeconds');
    const bDuration = positive(runB.durationSeconds, 'runB.durationSeconds');
    const start = Math.max(aStart, bStart); const end = Math.min(aStart + aDuration, bStart + bDuration);
    return { startSeconds: start, endSeconds: end, durationSeconds: Math.max(0, end - start), overlap: end > start };
  }
  function compareRuns(reference, comparison, sampleRateHz = 1) {
    const [a, b] = paired(reference, comparison);
    return { sampleCount: a.length, sampleRateHz: positive(sampleRateHz, 'sampleRateHz'), correlation: pearsonCorrelation(a, b), meanAbsoluteError: meanAbsoluteError(a, b), rootMeanSquareError: rootMeanSquareError(a, b), normalizedRootMeanSquareError: normalizedRmse(a, b), referenceFeatures: descriptiveFeatures(a, sampleRateHz), comparisonFeatures: descriptiveFeatures(b, sampleRateHz) };
  }
  function execute(methodId, inputs = {}) {
    const i = inputs; let value;
    switch (methodId) {
      case 'descriptive-features': value = descriptiveFeatures(i.samples, i.sampleRateHz ?? 1); break;
      case 'min-max-normalize': value = minMaxNormalize(i.samples); break;
      case 'z-score-normalize': value = zScoreNormalize(i.samples); break;
      case 'moving-average': value = movingAverage(i.samples, i.windowSize); break;
      case 'linear-resample': value = linearResample(i.samples, i.sourceRateHz, i.targetRateHz); break;
      case 'pearson-correlation': value = pearsonCorrelation(i.reference, i.comparison); break;
      case 'mean-absolute-error': value = meanAbsoluteError(i.reference, i.comparison); break;
      case 'root-mean-square-error': value = rootMeanSquareError(i.reference, i.comparison); break;
      case 'normalized-rmse': value = normalizedRmse(i.reference, i.comparison); break;
      case 'shift-series': value = shiftSeries(i.reference, i.comparison, i.lagSamples); break;
      case 'best-lag-correlation': value = bestLagCorrelation(i.reference, i.comparison, i.maxLagSamples); break;
      case 'event-rate': value = eventRate(i.eventCount, i.durationSeconds); break;
      case 'interval-summary': value = intervalSummary(i.intervals); break;
      case 'annotation-coverage': value = annotationCoverage(i.annotations, i.windowStartSeconds, i.windowEndSeconds); break;
      case 'common-time-window': value = commonTimeWindow(i.runA, i.runB); break;
      case 'compare-runs': value = compareRuns(i.reference, i.comparison, i.sampleRateHz ?? 1); break;
      default: throw new Error(`Unknown visualization analysis method: ${methodId}`);
    }
    return { schema: 'sc-lab-biosignal-visualization-result/1.0', version: VERSION, methodId, inputs, value };
  }

  function splitCsvLine(line) {
    const fields = []; let current = ''; let quoted = false;
    for (let index = 0; index < line.length; index += 1) {
      const char = line[index];
      if (char === '"') {
        if (quoted && line[index + 1] === '"') { current += '"'; index += 1; }
        else quoted = !quoted;
      } else if (char === ',' && !quoted) { fields.push(current.trim()); current = ''; }
      else current += char;
    }
    fields.push(current.trim()); return fields;
  }
  function parseMultiChannelCsv(text) {
    const lines = String(text || '').split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
    if (lines.length < 3) throw new Error('CSV requires a header and at least two data rows.');
    const headers = splitCsvLine(lines[0]);
    if (headers[0] !== 'timeSeconds') throw new Error('The first CSV column must be timeSeconds.');
    const channelIds = headers.slice(1);
    if (!channelIds.length) throw new Error('CSV requires at least one channel column.');
    const times = []; const channels = Object.fromEntries(channelIds.map((id) => [id, []]));
    lines.slice(1).forEach((line, rowIndex) => {
      const fields = splitCsvLine(line);
      times.push(finite(fields[0], `timeSeconds row ${rowIndex + 2}`));
      channelIds.forEach((id, index) => channels[id].push(finite(fields[index + 1], `${id} row ${rowIndex + 2}`)));
    });
    for (let index = 1; index < times.length; index += 1) if (times[index] <= times[index - 1]) throw new Error('timeSeconds values must be strictly increasing.');
    const differences = times.slice(1).map((time, index) => time - times[index]);
    const sampleRateHz = 1 / mean(differences);
    return { schema: 'sc-lab-multichannel-biosignal/1.0', version: VERSION, times, sampleRateHz, channelIds, channels };
  }
  function datasetToCsv(dataset) {
    const lines = [['timeSeconds', ...dataset.channelIds].join(',')];
    dataset.times.forEach((time, index) => lines.push([time, ...dataset.channelIds.map((id) => dataset.channels[id][index])].join(',')));
    return lines.join('\n');
  }
  function sampleCsv() {
    const lines = ['timeSeconds,ecg,ppg,respiration'];
    for (let index = 0; index <= 80; index += 1) {
      const time = index / 20;
      const ecg = Math.sin(time * Math.PI * 4) + 0.22 * Math.sin(time * Math.PI * 12);
      const ppg = 0.7 * Math.sin((time - 0.18) * Math.PI * 4) + 0.15;
      const respiration = 0.8 * Math.sin(time * Math.PI * 0.55);
      lines.push([time.toFixed(3), ecg.toFixed(6), ppg.toFixed(6), respiration.toFixed(6)].join(','));
    }
    return lines.join('\n');
  }
  function createAnnotation(type, startSeconds, endSeconds, label = '', channelId = null) {
    const start = finite(startSeconds, 'startSeconds'); const end = finite(endSeconds, 'endSeconds');
    if (end < start) throw new Error('Annotation end must not precede its start.');
    if (!CONTRACT.annotationTypes.some((item) => item.id === type)) throw new Error(`Unknown annotation type: ${type}`);
    return { id: `annotation-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`, type, label: String(label || ''), channelId: channelId || null, startSeconds: start, endSeconds: end };
  }
  function buildAnalysisRecord(dataset, options = {}) {
    const selected = options.channelIds?.length ? options.channelIds : dataset.channelIds;
    const smoothingWindow = Math.max(1, Math.trunc(Number(options.smoothingWindow || 5)));
    const channelSummaries = Object.fromEntries(selected.map((id) => [id, { raw: descriptiveFeatures(dataset.channels[id], dataset.sampleRateHz), filtered: descriptiveFeatures(movingAverage(dataset.channels[id], smoothingWindow), dataset.sampleRateHz) }]));
    let comparison = null; let lag = null;
    const referenceId = options.referenceId || selected[0]; const comparisonId = options.comparisonId || selected[1];
    if (referenceId && comparisonId && referenceId !== comparisonId) {
      comparison = compareRuns(dataset.channels[referenceId], dataset.channels[comparisonId], dataset.sampleRateHz);
      lag = bestLagCorrelation(dataset.channels[referenceId], dataset.channels[comparisonId], Math.min(Number(options.maxLagSamples || 20), dataset.times.length - 2));
    }
    const coverage = annotationCoverage(options.annotations || [], dataset.times[0], dataset.times.at(-1));
    return { schema: 'sc-lab-biosignal-visualization-analysis/1.0', version: VERSION, createdAt: new Date().toISOString(), mode: options.mode || 'synchronized-multichannel', dataset: { sampleCount: dataset.times.length, sampleRateHz: dataset.sampleRateHz, channelIds: selected, startSeconds: dataset.times[0], endSeconds: dataset.times.at(-1) }, smoothingWindow, channelSummaries, comparison: comparison ? { referenceId, comparisonId, metrics: comparison } : null, lag: lag ? { referenceId, comparisonId, ...lag } : null, annotations: options.annotations || [], annotationCoverage: coverage, responsibleUse: CONTRACT.responsibleUse };
  }

  const esc = (value) => String(value ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;');
  function buildSvg(dataset, options = {}) {
    const selected = options.channelIds?.length ? options.channelIds : dataset.channelIds;
    const start = Number.isFinite(Number(options.windowStart)) ? Number(options.windowStart) : dataset.times[0];
    const end = Number.isFinite(Number(options.windowEnd)) ? Number(options.windowEnd) : dataset.times.at(-1);
    const indexes = dataset.times.map((time, index) => ({ time, index })).filter((item) => item.time >= start && item.time <= end);
    if (indexes.length < 2) throw new Error('The selected time window must contain at least two samples.');
    const width = 1080; const laneHeight = 180; const paddingLeft = 72; const paddingRight = 22; const paddingTop = 32; const paddingBottom = 38;
    const height = paddingTop + selected.length * laneHeight + paddingBottom;
    const x = (time) => paddingLeft + (time - start) / (end - start) * (width - paddingLeft - paddingRight);
    const smoothingWindow = Math.max(1, Math.trunc(Number(options.smoothingWindow || 5)));
    const annotationMarkup = (options.annotations || []).map((annotation) => {
      if (annotation.endSeconds < start || annotation.startSeconds > end) return '';
      const left = x(Math.max(start, annotation.startSeconds)); const right = x(Math.min(end, annotation.endSeconds));
      return `<g class="sc-bv-annotation sc-bv-annotation-${esc(annotation.type)}"><rect x="${left.toFixed(2)}" y="${paddingTop}" width="${Math.max(2, right-left).toFixed(2)}" height="${selected.length*laneHeight}"/><text x="${(left+4).toFixed(2)}" y="${(paddingTop+14).toFixed(2)}">${esc(annotation.label || annotation.type)}</text></g>`;
    }).join('');
    const channelMarkup = selected.map((id, lane) => {
      const raw = dataset.channels[id]; const filtered = movingAverage(raw, smoothingWindow);
      const visible = indexes.map((item) => raw[item.index]); const minimum = Math.min(...visible); const maximum = Math.max(...visible); const span = maximum - minimum || 1;
      const y = (value) => paddingTop + lane*laneHeight + 22 + (1 - (value-minimum)/span) * (laneHeight-44);
      const rawPoints = indexes.map((item) => `${x(item.time).toFixed(2)},${y(raw[item.index]).toFixed(2)}`).join(' ');
      const filteredPoints = indexes.map((item) => `${x(item.time).toFixed(2)},${y(filtered[item.index]).toFixed(2)}`).join(' ');
      const laneY = paddingTop + lane*laneHeight;
      return `<g class="sc-bv-channel sc-bv-channel-${lane%6}"><rect class="sc-bv-lane" x="${paddingLeft}" y="${laneY}" width="${width-paddingLeft-paddingRight}" height="${laneHeight}"/><text class="sc-bv-label" x="12" y="${laneY+26}">${esc(id)}</text><text class="sc-bv-range" x="12" y="${laneY+48}">${minimum.toPrecision(4)}–${maximum.toPrecision(4)}</text><polyline class="sc-bv-raw" points="${rawPoints}"/><polyline class="sc-bv-filtered" points="${filteredPoints}"/></g>`;
    }).join('');
    const ticks = Array.from({ length: 6 }, (_, index) => start + (end-start)*index/5).map((time) => `<g><line class="sc-bv-gridline" x1="${x(time)}" x2="${x(time)}" y1="${paddingTop}" y2="${height-paddingBottom}"/><text class="sc-bv-tick" x="${x(time)}" y="${height-12}" text-anchor="middle">${time.toFixed(2)}s</text></g>`).join('');
    return `<svg xmlns="http://www.w3.org/2000/svg" class="sc-bv-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Synchronized multi-channel biosignal visualization"><rect class="sc-bv-background" x="0" y="0" width="${width}" height="${height}"/>${ticks}${annotationMarkup}${channelMarkup}<g class="sc-bv-legend"><line class="sc-bv-raw" x1="${width-250}" x2="${width-220}" y1="18" y2="18"/><text x="${width-214}" y="22">Raw</text><line class="sc-bv-filtered" x1="${width-130}" x2="${width-100}" y1="18" y2="18"/><text x="${width-94}" y="22">Filtered</text></g></svg>`;
  }

  function download(name, mime, content) {
    if (typeof document === 'undefined' || typeof Blob === 'undefined') return false;
    const blob = new Blob([content], { type: mime }); const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = name; link.click(); URL.revokeObjectURL(url); return true;
  }
  function show(element, value) { element.textContent = JSON.stringify(value, null, 2); }

  function render() {
    if (typeof document === 'undefined') return false;
    const roots = Array.from(document.querySelectorAll(ROOT_SELECTOR));
    if (!roots.length) return false;
    const root = roots[0]; roots.slice(1).forEach((item) => item.remove());
    if (root.dataset.scBiosignalVisualizationVersion === VERSION && root.querySelector('.sc-bv-shell')) { state.rendered = true; return true; }
    root.innerHTML = `
      <section class="sc-bv-shell">
        <header class="sc-bv-header"><p class="sc-bv-kicker">LAB/BIOMEDICAL/VISUALIZATION</p><h3>Biosignal Visualization, Annotation, and Comparative Analysis</h3><p>Synchronize channels, overlay raw and filtered signals, annotate events and regions, inspect lag and similarity, compare runs, and export reproducible analysis records.</p><div class="sc-bv-status"><span>8 visualization modes</span><span>16 analysis methods</span><span>16 benchmarks</span><span>6 annotation types</span></div></header>
        <div class="sc-bv-workspace">
          <aside class="sc-bv-controls sc-bv-card">
            <label>Visualization mode<select data-bv-mode>${CONTRACT.modes.map((item)=>`<option value="${esc(item.id)}">${esc(item.label)}</option>`).join('')}</select></label>
            <label>Multi-channel CSV<textarea rows="12" data-bv-csv spellcheck="false"></textarea></label>
            <div class="sc-bv-actions"><button type="button" data-bv-load>Load sample</button><button type="button" data-bv-import>Import CSV</button></div>
            <div data-bv-channels class="sc-bv-channel-options"></div>
            <div class="sc-bv-two-columns"><label>Window start (s)<input type="number" step="any" data-bv-start/></label><label>Window end (s)<input type="number" step="any" data-bv-end/></label><label>Smoothing window<input type="number" min="1" step="1" value="5" data-bv-smoothing/></label><label>Maximum lag (samples)<input type="number" min="0" step="1" value="20" data-bv-max-lag/></label></div>
            <div class="sc-bv-two-columns"><label>Reference channel<select data-bv-reference></select></label><label>Comparison channel<select data-bv-comparison></select></label></div>
            <fieldset><legend>Add annotation</legend><div class="sc-bv-two-columns"><label>Type<select data-bv-ann-type>${CONTRACT.annotationTypes.map((item)=>`<option value="${esc(item.id)}">${esc(item.label)}</option>`).join('')}</select></label><label>Label<input data-bv-ann-label value="Review"/></label><label>Start (s)<input type="number" step="any" value="1" data-bv-ann-start/></label><label>End (s)<input type="number" step="any" value="1.4" data-bv-ann-end/></label></div><button type="button" data-bv-add-annotation>Add annotation</button><div data-bv-annotations class="sc-bv-annotation-list"></div></fieldset>
            <div class="sc-bv-actions"><button type="button" data-bv-run>Render and analyze</button><button type="button" data-bv-clear>Clear annotations</button></div>
          </aside>
          <main class="sc-bv-results"><section class="sc-bv-card"><div class="sc-bv-output-header"><h4>Synchronized visualization</h4><span data-bv-window-label></span></div><div data-bv-chart class="sc-bv-chart-wrap"></div></section><section class="sc-bv-card"><div class="sc-bv-output-header"><h4>Comparative analysis</h4><div class="sc-bv-export-actions"><button type="button" data-bv-export-svg>SVG</button><button type="button" data-bv-export-csv>CSV</button><button type="button" data-bv-export-json>JSON</button></div></div><pre data-bv-output aria-live="polite">Import the sample dataset and run the analysis.</pre><div class="sc-bv-actions"><button type="button" data-bv-project>Project handoff</button><button type="button" data-bv-notebook>Notebook handoff</button><button type="button" data-bv-provenance>Provenance handoff</button></div></section></main>
        </div>
        <p class="sc-bv-boundary">Research, education, prototyping, and non-clinical comparison only. This workspace does not diagnose, monitor patients, generate clinical alarms, recommend treatment, or replace validated medical-device software and qualified interpretation.</p>
      </section>`;
    const csv = root.querySelector('[data-bv-csv]'); const channelBox = root.querySelector('[data-bv-channels]'); const referenceSelect = root.querySelector('[data-bv-reference]'); const comparisonSelect = root.querySelector('[data-bv-comparison]'); const output = root.querySelector('[data-bv-output]'); const chart = root.querySelector('[data-bv-chart]'); const windowLabel = root.querySelector('[data-bv-window-label]');
    function refreshDatasetControls() {
      if (!state.dataset) return;
      channelBox.innerHTML = state.dataset.channelIds.map((id)=>`<label class="sc-bv-check"><input type="checkbox" value="${esc(id)}" data-bv-channel checked/>${esc(id)}</label>`).join('');
      const options = state.dataset.channelIds.map((id)=>`<option value="${esc(id)}">${esc(id)}</option>`).join(''); referenceSelect.innerHTML = options; comparisonSelect.innerHTML = options; if (state.dataset.channelIds[1]) comparisonSelect.value = state.dataset.channelIds[1];
      root.querySelector('[data-bv-start]').value = state.dataset.times[0]; root.querySelector('[data-bv-end]').value = state.dataset.times.at(-1);
    }
    function importCsv() { state.dataset = parseMultiChannelCsv(csv.value); state.lastError = null; refreshDatasetControls(); return state.dataset; }
    function selectedChannels() { return Array.from(root.querySelectorAll('[data-bv-channel]:checked')).map((field)=>field.value); }
    function renderAnnotations() { root.querySelector('[data-bv-annotations]').innerHTML = state.annotations.length ? state.annotations.map((item,index)=>`<button type="button" data-bv-remove-annotation="${index}">${esc(item.type)} · ${item.startSeconds}–${item.endSeconds}s · ${esc(item.label)}</button>`).join('') : '<span>No annotations</span>'; root.querySelectorAll('[data-bv-remove-annotation]').forEach((button)=>button.addEventListener('click',()=>{ state.annotations.splice(Number(button.dataset.bvRemoveAnnotation),1); renderAnnotations(); })); }
    function runAnalysis() {
      try {
        if (!state.dataset) importCsv();
        const options = { mode: root.querySelector('[data-bv-mode]').value, channelIds: selectedChannels(), smoothingWindow: Number(root.querySelector('[data-bv-smoothing]').value), referenceId: referenceSelect.value, comparisonId: comparisonSelect.value, maxLagSamples: Number(root.querySelector('[data-bv-max-lag]').value), annotations: state.annotations, windowStart: Number(root.querySelector('[data-bv-start]').value), windowEnd: Number(root.querySelector('[data-bv-end]').value) };
        if (!options.channelIds.length) throw new Error('Select at least one channel.');
        state.analysis = buildAnalysisRecord(state.dataset, options); state.svg = buildSvg(state.dataset, options); chart.innerHTML = state.svg; show(output, state.analysis); windowLabel.textContent = `${options.windowStart.toFixed(2)}–${options.windowEnd.toFixed(2)} seconds`; state.lastError = null;
      } catch (error) { state.lastError = String(error?.message || error); show(output, { error: state.lastError }); }
    }
    csv.value = sampleCsv();
    root.querySelector('[data-bv-load]').addEventListener('click',()=>{ csv.value = sampleCsv(); importCsv(); });
    root.querySelector('[data-bv-import]').addEventListener('click',()=>{ try { importCsv(); show(output,{status:'dataset-imported',sampleCount:state.dataset.times.length,channelIds:state.dataset.channelIds,sampleRateHz:state.dataset.sampleRateHz}); } catch(error){ show(output,{error:String(error?.message||error)}); } });
    root.querySelector('[data-bv-add-annotation]').addEventListener('click',()=>{ try { state.annotations.push(createAnnotation(root.querySelector('[data-bv-ann-type]').value, root.querySelector('[data-bv-ann-start]').value, root.querySelector('[data-bv-ann-end]').value, root.querySelector('[data-bv-ann-label]').value)); renderAnnotations(); } catch(error){ show(output,{error:String(error?.message||error)}); } });
    root.querySelector('[data-bv-clear]').addEventListener('click',()=>{ state.annotations=[]; renderAnnotations(); });
    root.querySelector('[data-bv-run]').addEventListener('click', runAnalysis);
    root.querySelector('[data-bv-export-svg]').addEventListener('click',()=>download(`sc-lab-biosignal-visualization-${Date.now()}.svg`,'image/svg+xml',state.svg || buildSvg(state.dataset || importCsv(),{channelIds:state.dataset.channelIds,annotations:state.annotations})));
    root.querySelector('[data-bv-export-csv]').addEventListener('click',()=>download(`sc-lab-biosignal-dataset-${Date.now()}.csv`,'text/csv',datasetToCsv(state.dataset || importCsv())));
    root.querySelector('[data-bv-export-json]').addEventListener('click',()=>download(`sc-lab-biosignal-analysis-${Date.now()}.json`,'application/json',JSON.stringify(state.analysis || {version:VERSION},null,2)));
    function dispatch(name) { if (!state.analysis) runAnalysis(); document.dispatchEvent(new CustomEvent(name,{detail:{source:'biosignal-visualization-comparison',version:VERSION,record:state.analysis}})); show(output,{status:`${name}-dispatched`,record:state.analysis}); }
    root.querySelector('[data-bv-project]').addEventListener('click',()=>dispatch('sc-lab:project-record'));
    root.querySelector('[data-bv-notebook]').addEventListener('click',()=>dispatch('sc-lab:notebook-entry'));
    root.querySelector('[data-bv-provenance]').addEventListener('click',()=>{ try { if (!state.analysis) runAnalysis(); const provenance=Lab.BioprocessValidationProvenance; if (!provenance?.createRecord) throw new Error('The v0.22.3 provenance engine is unavailable.'); const record=provenance.createRecord(state.analysis,{eventType:'validation-decision',profileId:'biosignal-visualization-comparison',disposition:'research-review',notes:'Non-clinical visualization and comparison handoff.'}); show(output,record); } catch(error){ show(output,{error:String(error?.message||error)}); } });
    importCsv(); renderAnnotations(); runAnalysis(); root.dataset.scBiosignalVisualizationVersion=VERSION; state.rendered=true; return true;
  }
  function init() { [0,100,300,800,1800].forEach((delay)=>W.setTimeout(render,delay)); if (typeof MutationObserver!=='undefined' && typeof document!=='undefined') new MutationObserver(()=>render()).observe(document.documentElement,{childList:true,subtree:true}); }
  function status() { const root=typeof document==='undefined'?null:document.querySelector(ROOT_SELECTOR); return { version:VERSION, engineVersion:ENGINE_VERSION, productionVersion:PRODUCTION_VERSION, modeCount:CONTRACT.modes.length, analysisMethodCount:CONTRACT.analysisMethods.length, benchmarkCount:CONTRACT.benchmarks.length, annotationTypeCount:CONTRACT.annotationTypes.length, preservedMethodCount:CONTRACT.preservedEngine.methodCount, preservedBenchmarkCount:CONTRACT.preservedEngine.benchmarkCount, preservedCategoryCount:CONTRACT.preservedEngine.categoryCount, rootFound:Boolean(root), rendered:Boolean(root?.querySelector('.sc-bv-shell')), datasetLoaded:Boolean(state.dataset), annotationCount:state.annotations.length, lastError:state.lastError } }

  Lab.BiosignalVisualizationComparison = { VERSION, ENGINE_VERSION, PRODUCTION_VERSION, modes:CONTRACT.modes, analysisMethods:CONTRACT.analysisMethods, benchmarks:CONTRACT.benchmarks, annotationTypes:CONTRACT.annotationTypes, descriptiveFeatures, minMaxNormalize, zScoreNormalize, movingAverage, linearResample, pearsonCorrelation, meanAbsoluteError, rootMeanSquareError, normalizedRmse, shiftSeries, bestLagCorrelation, eventRate, intervalSummary, annotationCoverage, commonTimeWindow, compareRuns, execute, parseMultiChannelCsv, datasetToCsv, createAnnotation, buildAnalysisRecord, buildSvg, sampleCsv, render, init, status, state };
  if (typeof document!=='undefined') { if (document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true}); else init(); }
})();
