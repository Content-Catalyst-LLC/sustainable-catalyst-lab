(() => {
  'use strict';

  const rootWindow = typeof window !== 'undefined'
    ? window
    : globalThis;
  const Lab = rootWindow.SCLab = rootWindow.SCLab || {};
  const VERSION = '0.21.2';
  const MODULE_ID = 'biochemistry-molecular-analysis';
  const ROOT_SELECTOR =
    '[data-biochemistry-visualization-batch-root]';
  const ANALYSIS_ROOT_SELECTOR =
    '[data-biochemistry-molecular-analysis-root]';
  const PANEL_SELECTOR = [
    `[data-lab-module="${MODULE_ID}"]`,
    `[data-module-panel="${MODULE_ID}"]`,
  ].join(',');

  const PRESETS = {"schema":"sc-lab-biochemistry-visualization-presets/1.0","version":"0.21.2","presets":[{"id":"standard-curve","title":"Standard curve and linear regression","description":"Fit signal against known concentration and calculate slope, intercept, R², and unknown concentration.","mode":"observed","xLabel":"Concentration","yLabel":"Signal","defaultData":[{"x":0,"y":0.02},{"x":1,"y":0.51},{"x":2,"y":1.03},{"x":3,"y":1.49},{"x":4,"y":2.02}]},{"id":"michaelis-menten","title":"Michaelis–Menten kinetics","description":"Generate substrate–velocity curves from Vmax and Km.","mode":"generated","xLabel":"Substrate concentration","yLabel":"Initial velocity","parameters":[{"key":"vmax","label":"Vmax","default":100,"min":0},{"key":"km","label":"Km","default":0.5,"min":1e-06},{"key":"xMax","label":"Maximum substrate","default":5,"min":0.001}]},{"id":"hill-response","title":"Hill binding response","description":"Generate fractional occupancy from ligand concentration, Kd, and Hill coefficient.","mode":"generated","xLabel":"Ligand concentration","yLabel":"Fractional occupancy","parameters":[{"key":"kd","label":"Kd","default":1,"min":1e-06},{"key":"hill","label":"Hill coefficient","default":2,"min":0.01},{"key":"xMax","label":"Maximum ligand","default":5,"min":0.001}]},{"id":"buffer-protonation","title":"Buffer protonation profile","description":"Plot protonated and deprotonated fractions across a pH interval.","mode":"generated-multi","xLabel":"pH","yLabel":"Fraction","parameters":[{"key":"pKa","label":"pKa","default":7.2},{"key":"pHMin","label":"Minimum pH","default":4},{"key":"pHMax","label":"Maximum pH","default":10}]},{"id":"absorbance-comparison","title":"Absorbance comparison","description":"Compare wavelength-indexed absorbance measurements.","mode":"observed","xLabel":"Wavelength (nm)","yLabel":"Absorbance","defaultData":[{"x":240,"y":0.12},{"x":260,"y":0.81},{"x":280,"y":0.52},{"x":300,"y":0.18},{"x":320,"y":0.08}]},{"id":"fluorescence-comparison","title":"Fluorescence comparison","description":"Compare wavelength-indexed fluorescence intensity.","mode":"observed","xLabel":"Wavelength (nm)","yLabel":"Fluorescence intensity","defaultData":[{"x":420,"y":12},{"x":450,"y":35},{"x":480,"y":72},{"x":510,"y":44},{"x":540,"y":18}]},{"id":"chromatography-trace","title":"Chromatography trace","description":"Plot retention time against detector response and inspect peak separation.","mode":"observed","xLabel":"Retention time (min)","yLabel":"Detector response","defaultData":[{"x":0,"y":0.01},{"x":1,"y":0.03},{"x":2,"y":0.32},{"x":2.5,"y":1.12},{"x":3,"y":0.28},{"x":4,"y":0.08},{"x":5,"y":0.44},{"x":5.5,"y":0.96},{"x":6,"y":0.31},{"x":7,"y":0.04}]}]};

  const state = {
    currentVisualization: null,
    currentBatch: null,
    initializedAt: null,
    lastError: null,
  };

  function finite(value, label) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      throw new Error(`${label} must be a finite number.`);
    }

    return number;
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
      return number.toExponential(5);
    }

    return Number(number.toPrecision(7)).toString();
  }

  function analysisApi() {
    const candidate = Lab.BiochemistryMolecularAnalysis;

    if (
      candidate
      && typeof candidate.run === 'function'
      && Array.isArray(candidate.definitions)
    ) {
      return candidate;
    }

    return null;
  }

  function presetById(id) {
    return PRESETS.presets.find(
      (preset) => preset.id === id
    ) || PRESETS.presets[0];
  }

  function csvEscape(value) {
    const text = String(value ?? '');

    if (/[",\n\r]/.test(text)) {
      return `"${text.replaceAll('"', '""')}"`;
    }

    return text;
  }

  function parseCsvLine(line) {
    const cells = [];
    let current = '';
    let quoted = false;

    for (let index = 0; index < line.length; index += 1) {
      const character = line[index];

      if (character === '"') {
        if (quoted && line[index + 1] === '"') {
          current += '"';
          index += 1;
        } else {
          quoted = !quoted;
        }
      } else if (character === ',' && !quoted) {
        cells.push(current.trim());
        current = '';
      } else {
        current += character;
      }
    }

    cells.push(current.trim());
    return cells;
  }

  function parseCsv(text) {
    const lines = String(text)
      .replaceAll('\r\n', '\n')
      .replaceAll('\r', '\n')
      .split('\n')
      .filter((line) => line.trim() !== '');

    if (!lines.length) {
      return [];
    }

    const headers = parseCsvLine(lines[0]);

    return lines.slice(1).map((line, rowIndex) => {
      const cells = parseCsvLine(line);
      const row = {
        __row: rowIndex + 2,
      };

      headers.forEach((header, index) => {
        row[header] = cells[index] ?? '';
      });

      return row;
    });
  }

  function mean(values) {
    return values.reduce(
      (total, value) => total + value,
      0
    ) / values.length;
  }

  function standardDeviation(values) {
    if (values.length < 2) {
      return 0;
    }

    const average = mean(values);
    const variance = values.reduce(
      (total, value) => (
        total + ((value - average) ** 2)
      ),
      0
    ) / (values.length - 1);

    return Math.sqrt(variance);
  }

  function summarize(values) {
    const clean = values
      .map(Number)
      .filter(Number.isFinite);

    if (!clean.length) {
      return {
        n: 0,
        mean: null,
        standardDeviation: null,
        coefficientOfVariationPercent: null,
        minimum: null,
        maximum: null,
        status: 'unavailable',
      };
    }

    const average = mean(clean);
    const deviation = standardDeviation(clean);
    const cv = average === 0
      ? null
      : Math.abs(deviation / average) * 100;

    return {
      n: clean.length,
      mean: average,
      standardDeviation: deviation,
      coefficientOfVariationPercent: cv,
      minimum: Math.min(...clean),
      maximum: Math.max(...clean),
      status: (
        cv !== null && cv > 20
      ) ? 'review' : 'screened',
    };
  }

  function linearRegression(points) {
    const clean = points
      .map((point) => ({
        x: Number(point.x),
        y: Number(point.y),
      }))
      .filter(
        (point) => (
          Number.isFinite(point.x)
          && Number.isFinite(point.y)
        )
      );

    if (clean.length < 2) {
      throw new Error(
        'At least two numerical points are required.'
      );
    }

    const xMean = mean(clean.map((point) => point.x));
    const yMean = mean(clean.map((point) => point.y));

    const numerator = clean.reduce(
      (total, point) => (
        total
        + ((point.x - xMean) * (point.y - yMean))
      ),
      0
    );

    const denominator = clean.reduce(
      (total, point) => (
        total + ((point.x - xMean) ** 2)
      ),
      0
    );

    if (denominator === 0) {
      throw new Error(
        'Regression requires more than one x value.'
      );
    }

    const slope = numerator / denominator;
    const intercept = yMean - (slope * xMean);

    const totalVariation = clean.reduce(
      (total, point) => (
        total + ((point.y - yMean) ** 2)
      ),
      0
    );

    const residualVariation = clean.reduce(
      (total, point) => {
        const predicted = (
          slope * point.x
          + intercept
        );

        return (
          total + ((point.y - predicted) ** 2)
        );
      },
      0
    );

    const rSquared = totalVariation === 0
      ? 1
      : 1 - (residualVariation / totalVariation);

    return {
      slope,
      intercept,
      rSquared,
      pointCount: clean.length,
      fittedPoints: clean.map((point) => ({
        x: point.x,
        y: (slope * point.x) + intercept,
      })),
    };
  }

  function generatePresetData(preset, parameters) {
    if (preset.mode === 'observed') {
      return {
        series: [{
          label: 'Observed',
          points: preset.defaultData.map(
            (point) => ({ ...point })
          ),
        }],
        metrics: (
          preset.id === 'standard-curve'
            ? linearRegression(preset.defaultData)
            : {}
        ),
      };
    }

    const points = 41;

    if (preset.id === 'michaelis-menten') {
      const vmax = finite(parameters.vmax, 'Vmax');
      const km = finite(parameters.km, 'Km');
      const xMax = finite(
        parameters.xMax,
        'Maximum substrate'
      );

      return {
        series: [{
          label: 'Velocity',
          points: Array.from(
            { length: points },
            (_, index) => {
              const x = (
                xMax * index / (points - 1)
              );

              return {
                x,
                y: x === 0
                  ? 0
                  : (vmax * x) / (km + x),
              };
            }
          ),
        }],
        metrics: { vmax, km },
      };
    }

    if (preset.id === 'hill-response') {
      const kd = finite(parameters.kd, 'Kd');
      const hill = finite(
        parameters.hill,
        'Hill coefficient'
      );
      const xMax = finite(
        parameters.xMax,
        'Maximum ligand'
      );

      return {
        series: [{
          label: 'Fractional occupancy',
          points: Array.from(
            { length: points },
            (_, index) => {
              const x = (
                xMax * index / (points - 1)
              );
              const xPower = x ** hill;
              const kdPower = kd ** hill;

              return {
                x,
                y: x === 0
                  ? 0
                  : xPower / (kdPower + xPower),
              };
            }
          ),
        }],
        metrics: { kd, hill },
      };
    }

    if (preset.id === 'buffer-protonation') {
      const pKa = finite(parameters.pKa, 'pKa');
      const pHMin = finite(
        parameters.pHMin,
        'Minimum pH'
      );
      const pHMax = finite(
        parameters.pHMax,
        'Maximum pH'
      );

      if (pHMax <= pHMin) {
        throw new Error(
          'Maximum pH must be greater than minimum pH.'
        );
      }

      const acid = [];
      const base = [];

      for (let index = 0; index < points; index += 1) {
        const x = pHMin
          + ((pHMax - pHMin) * index / (points - 1));
        const ratio = 10 ** (x - pKa);
        const acidFraction = 1 / (1 + ratio);

        acid.push({ x, y: acidFraction });
        base.push({ x, y: 1 - acidFraction });
      }

      return {
        series: [
          {
            label: 'Protonated fraction',
            points: acid,
          },
          {
            label: 'Deprotonated fraction',
            points: base,
          },
        ],
        metrics: { pKa, pHMin, pHMax },
      };
    }

    throw new Error(
      `Unsupported visualization preset: ${preset.id}`
    );
  }

  function observedDataFromText(text) {
    return parseCsv(text)
      .map((row) => ({
        x: Number(
          row.x
          ?? row.X
          ?? row.wavelength
          ?? row.time
        ),
        y: Number(
          row.y
          ?? row.Y
          ?? row.signal
          ?? row.absorbance
          ?? row.intensity
          ?? row.response
        ),
      }))
      .filter(
        (point) => (
          Number.isFinite(point.x)
          && Number.isFinite(point.y)
        )
      );
  }

  function visualizationFromObserved(
    preset,
    text
  ) {
    const points = observedDataFromText(text);

    if (points.length < 2) {
      throw new Error(
        'Observed visualizations require at least two x,y rows.'
      );
    }

    const metrics = preset.id === 'standard-curve'
      ? linearRegression(points)
      : {};

    const series = [{
      label: 'Observed',
      points,
      pointOnly: preset.id === 'standard-curve',
    }];

    if (
      preset.id === 'standard-curve'
      && Array.isArray(metrics.fittedPoints)
    ) {
      series.push({
        label: 'Linear fit',
        points: metrics.fittedPoints,
      });
    }

    return { series, metrics };
  }

  function chartBounds(series) {
    const points = series.flatMap(
      (item) => item.points
    );
    const xs = points.map((point) => point.x);
    const ys = points.map((point) => point.y);

    let xMin = Math.min(...xs);
    let xMax = Math.max(...xs);
    let yMin = Math.min(...ys);
    let yMax = Math.max(...ys);

    if (xMin === xMax) {
      xMin -= 1;
      xMax += 1;
    }

    if (yMin === yMax) {
      yMin -= 1;
      yMax += 1;
    }

    const xPadding = (xMax - xMin) * 0.05;
    const yPadding = (yMax - yMin) * 0.08;

    return {
      xMin: xMin - xPadding,
      xMax: xMax + xPadding,
      yMin: yMin - yPadding,
      yMax: yMax + yPadding,
    };
  }

  function renderSvgChart(
    container,
    series,
    xLabel,
    yLabel
  ) {
    const width = 760;
    const height = 420;
    const margin = {
      top: 28,
      right: 28,
      bottom: 66,
      left: 78,
    };
    const bounds = chartBounds(series);
    const plotWidth = (
      width - margin.left - margin.right
    );
    const plotHeight = (
      height - margin.top - margin.bottom
    );

    const xScale = (value) => (
      margin.left
      + (
        (value - bounds.xMin)
        / (bounds.xMax - bounds.xMin)
      ) * plotWidth
    );

    const yScale = (value) => (
      margin.top
      + plotHeight
      - (
        (value - bounds.yMin)
        / (bounds.yMax - bounds.yMin)
      ) * plotHeight
    );

    const ticks = 5;
    const grid = [];

    for (let index = 0; index <= ticks; index += 1) {
      const x = (
        margin.left + (plotWidth * index / ticks)
      );
      const y = (
        margin.top + (plotHeight * index / ticks)
      );
      const xValue = bounds.xMin
        + (
          (bounds.xMax - bounds.xMin)
          * index / ticks
        );
      const yValue = bounds.yMax
        - (
          (bounds.yMax - bounds.yMin)
          * index / ticks
        );

      grid.push(`
        <line
          x1="${x}"
          y1="${margin.top}"
          x2="${x}"
          y2="${margin.top + plotHeight}"
          class="sc-bvb-grid"
        />
        <text
          x="${x}"
          y="${margin.top + plotHeight + 24}"
          text-anchor="middle"
          class="sc-bvb-tick"
        >${escapeHtml(formatNumber(xValue))}</text>
        <line
          x1="${margin.left}"
          y1="${y}"
          x2="${margin.left + plotWidth}"
          y2="${y}"
          class="sc-bvb-grid"
        />
        <text
          x="${margin.left - 12}"
          y="${y + 4}"
          text-anchor="end"
          class="sc-bvb-tick"
        >${escapeHtml(formatNumber(yValue))}</text>
      `);
    }

    const seriesMarkup = series.map(
      (item, seriesIndex) => {
        const path = item.points
          .map((point, index) => (
            `${index === 0 ? 'M' : 'L'} `
            + `${xScale(point.x)} ${yScale(point.y)}`
          ))
          .join(' ');

        const circles = item.points.map(
          (point) => `
            <circle
              cx="${xScale(point.x)}"
              cy="${yScale(point.y)}"
              r="${item.pointOnly ? 4.5 : 3}"
              class="sc-bvb-point sc-bvb-series-${seriesIndex + 1}"
            >
              <title>
                ${escapeHtml(item.label)}:
                ${escapeHtml(formatNumber(point.x))},
                ${escapeHtml(formatNumber(point.y))}
              </title>
            </circle>
          `
        ).join('');

        return `
          ${item.pointOnly ? '' : `
            <path
              d="${path}"
              class="sc-bvb-line sc-bvb-series-${seriesIndex + 1}"
            />
          `}
          ${circles}
        `;
      }
    ).join('');

    const legend = series.map(
      (item, index) => `
        <span>
          <i class="sc-bvb-legend-key sc-bvb-series-${index + 1}"></i>
          ${escapeHtml(item.label)}
        </span>
      `
    ).join('');

    container.innerHTML = `
      <div class="sc-bvb-chart-frame">
        <svg
          class="sc-bvb-chart"
          viewBox="0 0 ${width} ${height}"
          role="img"
          aria-label="${escapeHtml(
            `${yLabel} by ${xLabel}`
          )}"
        >
          ${grid.join('')}
          <line
            x1="${margin.left}"
            y1="${margin.top + plotHeight}"
            x2="${margin.left + plotWidth}"
            y2="${margin.top + plotHeight}"
            class="sc-bvb-axis"
          />
          <line
            x1="${margin.left}"
            y1="${margin.top}"
            x2="${margin.left}"
            y2="${margin.top + plotHeight}"
            class="sc-bvb-axis"
          />
          ${seriesMarkup}
          <text
            x="${margin.left + (plotWidth / 2)}"
            y="${height - 16}"
            text-anchor="middle"
            class="sc-bvb-axis-label"
          >${escapeHtml(xLabel)}</text>
          <text
            x="20"
            y="${margin.top + (plotHeight / 2)}"
            text-anchor="middle"
            transform="rotate(-90 20 ${margin.top + (plotHeight / 2)})"
            class="sc-bvb-axis-label"
          >${escapeHtml(yLabel)}</text>
        </svg>
      </div>
      <div class="sc-bvb-legend">${legend}</div>
    `;
  }

  function metricMarkup(metrics) {
    const entries = Object.entries(metrics)
      .filter(([, value]) => (
        typeof value === 'number'
      ));

    if (!entries.length) {
      return '<p>No derived metrics for this plot.</p>';
    }

    return `
      <dl class="sc-bvb-metrics">
        ${entries.map(([key, value]) => `
          <div>
            <dt>${escapeHtml(key)}</dt>
            <dd>${escapeHtml(formatNumber(value))}</dd>
          </div>
        `).join('')}
      </dl>
    `;
  }

  function methodOptions() {
    const api = analysisApi();

    if (!api) {
      return '';
    }

    return api.definitions.map(
      (method) => `
        <option value="${escapeHtml(method.id)}">
          ${escapeHtml(method.category)} — ${escapeHtml(method.title)}
        </option>
      `
    ).join('');
  }

  function methodById(id) {
    const api = analysisApi();

    return api?.definitions.find(
      (method) => method.id === id
    ) || null;
  }

  function sampleCsv(method) {
    if (!method) {
      return '';
    }

    const headers = [
      'sample',
      ...method.inputs.map((input) => input.key),
    ];

    const first = [
      'sample-1',
      ...method.inputs.map((input) => input.default),
    ];

    const second = [
      'sample-2',
      ...method.inputs.map((input) => (
        Number(input.default) * 1.02
      )),
    ];

    const third = [
      'sample-3',
      ...method.inputs.map((input) => (
        Number(input.default) * 0.98
      )),
    ];

    return [headers, first, second, third]
      .map((row) => row.map(csvEscape).join(','))
      .join('\n');
  }

  function batchRun(methodId, csvText) {
    const api = analysisApi();

    if (!api) {
      throw new Error(
        'The Biochemistry analysis engine is unavailable.'
      );
    }

    const method = methodById(methodId);

    if (!method) {
      throw new Error(
        `Unknown Biochemistry method: ${methodId}`
      );
    }

    const rows = parseCsv(csvText);

    if (!rows.length) {
      throw new Error(
        'Batch analysis requires at least one data row.'
      );
    }

    const results = rows.map((row, index) => {
      const sample = String(
        row.sample
        || row.sampleId
        || `sample-${index + 1}`
      );
      const inputs = Object.fromEntries(
        method.inputs.map((input) => [
          input.key,
          row[input.key],
        ])
      );

      try {
        const analysis = api.run(methodId, inputs);

        return {
          sample,
          row: row.__row,
          ok: true,
          inputs: analysis.inputs,
          outputs: analysis.outputs,
          warnings: analysis.warnings,
          analysis,
        };
      } catch (error) {
        return {
          sample,
          row: row.__row,
          ok: false,
          inputs,
          outputs: {},
          warnings: [],
          error: String(
            error && error.message
              ? error.message
              : error
          ),
        };
      }
    });

    const outputKeys = Object.keys(
      method.outputs
    );

    const statistics = Object.fromEntries(
      outputKeys.map((key) => [
        key,
        summarize(
          results
            .filter((result) => result.ok)
            .map((result) => result.outputs[key])
        ),
      ])
    );

    const flags = [];

    for (
      const [key, summary]
      of Object.entries(statistics)
    ) {
      if (summary.status === 'review') {
        flags.push(
          `${key} has CV above 20%.`
        );
      }
    }

    const errorCount = results.filter(
      (result) => !result.ok
    ).length;

    if (errorCount) {
      flags.push(
        `${errorCount} batch row(s) could not be calculated.`
      );
    }

    return {
      schema: 'sc-lab-biochemistry-batch-analysis/1.0',
      version: VERSION,
      analysisEngineVersion: api.VERSION,
      methodId,
      methodTitle: method.title,
      category: method.category,
      rowCount: results.length,
      successCount: results.length - errorCount,
      errorCount,
      results,
      statistics,
      flags,
      status: flags.length ? 'review' : 'screened',
      audit: {
        createdAt: new Date().toISOString(),
        engine:
          'sc-lab-biochemistry-visualization-batch-browser',
        release: VERSION,
      },
    };
  }

  function batchTableMarkup(batch, method) {
    const outputKeys = Object.keys(method.outputs);

    const rows = batch.results.map((result) => `
      <tr class="${result.ok ? '' : 'sc-bvb-row-error'}">
        <th>${escapeHtml(result.sample)}</th>
        <td>${result.ok ? 'Calculated' : 'Error'}</td>
        ${outputKeys.map((key) => `
          <td>
            ${result.ok
              ? escapeHtml(formatNumber(result.outputs[key]))
              : '—'}
          </td>
        `).join('')}
        <td>${escapeHtml(
          result.ok
            ? result.warnings.join(' ')
            : result.error
        )}</td>
      </tr>
    `).join('');

    return `
      <div class="sc-bvb-table-scroll">
        <table class="sc-bvb-table">
          <thead>
            <tr>
              <th>Sample</th>
              <th>Status</th>
              ${outputKeys.map((key) => `
                <th>
                  ${escapeHtml(method.outputs[key].label)}
                  <small>${escapeHtml(method.outputs[key].unit)}</small>
                </th>
              `).join('')}
              <th>Review notes</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
  }

  function statisticsMarkup(batch, method) {
    return `
      <div class="sc-bvb-stat-grid">
        ${Object.entries(batch.statistics).map(
          ([key, summary]) => `
            <article class="sc-bvb-stat-card">
              <h5>${escapeHtml(
                method.outputs[key].label
              )}</h5>
              <dl>
                <div>
                  <dt>n</dt>
                  <dd>${summary.n}</dd>
                </div>
                <div>
                  <dt>Mean</dt>
                  <dd>${escapeHtml(
                    formatNumber(summary.mean)
                  )}</dd>
                </div>
                <div>
                  <dt>SD</dt>
                  <dd>${escapeHtml(
                    formatNumber(
                      summary.standardDeviation
                    )
                  )}</dd>
                </div>
                <div>
                  <dt>CV</dt>
                  <dd>${escapeHtml(
                    summary.coefficientOfVariationPercent
                      === null
                      ? '—'
                      : `${formatNumber(
                          summary.coefficientOfVariationPercent
                        )}%`
                  )}</dd>
                </div>
                <div>
                  <dt>Range</dt>
                  <dd>
                    ${escapeHtml(
                      formatNumber(summary.minimum)
                    )}
                    –
                    ${escapeHtml(
                      formatNumber(summary.maximum)
                    )}
                  </dd>
                </div>
              </dl>
              <span class="sc-bvb-status sc-bvb-status-${summary.status}">
                ${escapeHtml(summary.status)}
              </span>
            </article>
          `
        ).join('')}
      </div>
    `;
  }

  function downloadFile(filename, type, content) {
    const blob = new Blob(
      [content],
      { type }
    );
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = url;
    link.download = filename;
    link.click();

    rootWindow.setTimeout(
      () => URL.revokeObjectURL(url),
      500
    );
  }

  function batchToCsv(batch, method) {
    const outputKeys = Object.keys(method.outputs);
    const headers = [
      'sample',
      'status',
      ...outputKeys,
      'review_notes',
    ];

    const lines = [headers];

    for (const result of batch.results) {
      lines.push([
        result.sample,
        result.ok ? 'calculated' : 'error',
        ...outputKeys.map((key) => (
          result.ok ? result.outputs[key] : ''
        )),
        result.ok
          ? result.warnings.join(' ')
          : result.error,
      ]);
    }

    return lines.map(
      (row) => row.map(csvEscape).join(',')
    ).join('\n');
  }

  function persistFallback(bucket, record) {
    try {
      const key = `sc-lab:${bucket}`;
      const records = JSON.parse(
        rootWindow.localStorage?.getItem(key)
        || '[]'
      );

      records.unshift(record);
      rootWindow.localStorage?.setItem(
        key,
        JSON.stringify(records.slice(0, 100))
      );

      return true;
    } catch (_error) {
      return false;
    }
  }

  function saveProject(record) {
    if (
      Lab.Projects
      && typeof Lab.Projects.addAnalysis === 'function'
    ) {
      Lab.Projects.addAnalysis(record);
      return true;
    }

    if (
      Lab.Projects
      && typeof Lab.Projects.saveAnalysis === 'function'
    ) {
      Lab.Projects.saveAnalysis(record);
      return true;
    }

    return persistFallback(
      'project-analyses',
      record
    );
  }

  function addNotebook(record) {
    if (
      Lab.Notebook
      && typeof Lab.Notebook.add === 'function'
    ) {
      Lab.Notebook.add(record);
      return true;
    }

    return persistFallback('notebook', record);
  }

  function ensureRoot() {
    let root = document.querySelector(ROOT_SELECTOR);

    if (root) {
      return root;
    }

    const panel = document.querySelector(PANEL_SELECTOR);

    if (!panel) {
      return null;
    }

    root = document.createElement('div');
    root.setAttribute(
      'data-biochemistry-visualization-batch-root',
      ''
    );

    const analysisRoot = panel.querySelector(
      ANALYSIS_ROOT_SELECTOR
    );

    if (analysisRoot) {
      analysisRoot.insertAdjacentElement(
        'afterend',
        root
      );
    } else {
      panel.appendChild(root);
    }

    return root;
  }

  function render(root) {
    if (
      root.dataset.scBiochemistryVisualizationBatch
        === VERSION
      && root.children.length
    ) {
      return;
    }

    root.innerHTML = `
      <section class="sc-bvb-shell">
        <header class="sc-bvb-header">
          <div>
            <p class="sc-bvb-kicker">
              LAB/BIOCHEMISTRY/ANALYSIS
            </p>
            <h3>
              Visualization and Batch Analysis
            </h3>
            <p>
              Plot biochemical relationships, import replicate
              data, run any validated Biochemistry method across
              multiple samples, review precision, and export
              reproducible records.
            </p>
          </div>
          <span class="sc-bvb-version">v${VERSION}</span>
        </header>

        <div class="sc-bvb-tabs" role="tablist">
          <button
            type="button"
            class="is-active"
            data-bvb-tab="visualization"
          >
            Visualization studio
          </button>
          <button
            type="button"
            data-bvb-tab="batch"
          >
            Batch analysis
          </button>
        </div>

        <section
          class="sc-bvb-workspace"
          data-bvb-workspace="visualization"
        >
          <div class="sc-bvb-control-grid">
            <label>
              <span>Visualization</span>
              <select data-bvb-preset>
                ${PRESETS.presets.map((preset) => `
                  <option value="${escapeHtml(preset.id)}">
                    ${escapeHtml(preset.title)}
                  </option>
                `).join('')}
              </select>
            </label>
            <div data-bvb-parameters></div>
          </div>

          <div
            class="sc-bvb-observed"
            data-bvb-observed
          >
            <label>
              <span>Observed data CSV</span>
              <textarea
                rows="8"
                data-bvb-observed-data
                spellcheck="false"
              ></textarea>
              <small>
                Required columns: x,y
              </small>
            </label>
          </div>

          <div class="sc-bvb-actions">
            <button
              type="button"
              class="sc-bvb-primary"
              data-bvb-plot
            >
              Generate visualization
            </button>
            <button
              type="button"
              data-bvb-save-visualization
              disabled
            >
              Save to project
            </button>
            <button
              type="button"
              data-bvb-notebook-visualization
              disabled
            >
              Add to notebook
            </button>
            <button
              type="button"
              data-bvb-export-visualization
              disabled
            >
              Export JSON
            </button>
          </div>

          <p
            class="sc-bvb-status-line"
            data-bvb-visualization-status
            aria-live="polite"
          ></p>

          <div
            class="sc-bvb-chart-host"
            data-bvb-chart
          ></div>

          <div
            class="sc-bvb-metric-host"
            data-bvb-metrics
          ></div>
        </section>

        <section
          class="sc-bvb-workspace"
          data-bvb-workspace="batch"
          hidden
        >
          <div class="sc-bvb-control-grid">
            <label>
              <span>Biochemistry method</span>
              <select data-bvb-method>
                ${methodOptions()}
              </select>
            </label>
            <label>
              <span>Import CSV</span>
              <input
                type="file"
                accept=".csv,text/csv"
                data-bvb-file
              />
            </label>
          </div>

          <label class="sc-bvb-csv-label">
            <span>Batch sample data</span>
            <textarea
              rows="10"
              data-bvb-csv
              spellcheck="false"
            ></textarea>
          </label>

          <div class="sc-bvb-actions">
            <button
              type="button"
              class="sc-bvb-primary"
              data-bvb-run-batch
            >
              Run batch analysis
            </button>
            <button
              type="button"
              data-bvb-reset-csv
            >
              Load sample CSV
            </button>
            <button
              type="button"
              data-bvb-export-csv
              disabled
            >
              Export results CSV
            </button>
            <button
              type="button"
              data-bvb-export-json
              disabled
            >
              Export audit JSON
            </button>
            <button
              type="button"
              data-bvb-save-batch
              disabled
            >
              Save to project
            </button>
            <button
              type="button"
              data-bvb-notebook-batch
              disabled
            >
              Add to notebook
            </button>
          </div>

          <p
            class="sc-bvb-status-line"
            data-bvb-batch-status
            aria-live="polite"
          ></p>

          <div data-bvb-batch-statistics></div>
          <div data-bvb-batch-results></div>
        </section>
      </section>
    `;

    const tabButtons = root.querySelectorAll(
      '[data-bvb-tab]'
    );
    const workspaces = root.querySelectorAll(
      '[data-bvb-workspace]'
    );
    const presetSelect = root.querySelector(
      '[data-bvb-preset]'
    );
    const parameterRoot = root.querySelector(
      '[data-bvb-parameters]'
    );
    const observedRoot = root.querySelector(
      '[data-bvb-observed]'
    );
    const observedTextarea = root.querySelector(
      '[data-bvb-observed-data]'
    );
    const chartRoot = root.querySelector(
      '[data-bvb-chart]'
    );
    const metricsRoot = root.querySelector(
      '[data-bvb-metrics]'
    );
    const visualizationStatus = root.querySelector(
      '[data-bvb-visualization-status]'
    );
    const plotButton = root.querySelector(
      '[data-bvb-plot]'
    );
    const saveVisualizationButton = root.querySelector(
      '[data-bvb-save-visualization]'
    );
    const notebookVisualizationButton = root.querySelector(
      '[data-bvb-notebook-visualization]'
    );
    const exportVisualizationButton = root.querySelector(
      '[data-bvb-export-visualization]'
    );

    const methodSelect = root.querySelector(
      '[data-bvb-method]'
    );
    const csvTextarea = root.querySelector(
      '[data-bvb-csv]'
    );
    const fileInput = root.querySelector(
      '[data-bvb-file]'
    );
    const runBatchButton = root.querySelector(
      '[data-bvb-run-batch]'
    );
    const resetCsvButton = root.querySelector(
      '[data-bvb-reset-csv]'
    );
    const exportCsvButton = root.querySelector(
      '[data-bvb-export-csv]'
    );
    const exportJsonButton = root.querySelector(
      '[data-bvb-export-json]'
    );
    const saveBatchButton = root.querySelector(
      '[data-bvb-save-batch]'
    );
    const notebookBatchButton = root.querySelector(
      '[data-bvb-notebook-batch]'
    );
    const batchStatus = root.querySelector(
      '[data-bvb-batch-status]'
    );
    const statisticsRoot = root.querySelector(
      '[data-bvb-batch-statistics]'
    );
    const batchResultsRoot = root.querySelector(
      '[data-bvb-batch-results]'
    );

    function activateTab(id) {
      tabButtons.forEach((button) => {
        button.classList.toggle(
          'is-active',
          button.dataset.bvbTab === id
        );
      });

      workspaces.forEach((workspace) => {
        workspace.hidden = (
          workspace.dataset.bvbWorkspace !== id
        );
      });
    }

    tabButtons.forEach((button) => {
      button.addEventListener('click', () => {
        activateTab(button.dataset.bvbTab);
      });
    });

    function refreshPreset() {
      const preset = presetById(
        presetSelect.value
      );

      parameterRoot.innerHTML = '';

      if (
        Array.isArray(preset.parameters)
        && preset.parameters.length
      ) {
        parameterRoot.innerHTML = `
          <div class="sc-bvb-parameter-grid">
            ${preset.parameters.map((parameter) => `
              <label>
                <span>${escapeHtml(parameter.label)}</span>
                <input
                  type="number"
                  step="any"
                  data-bvb-parameter="${escapeHtml(parameter.key)}"
                  value="${escapeHtml(parameter.default)}"
                  ${Number.isFinite(parameter.min)
                    ? `min="${parameter.min}"`
                    : ''}
                />
              </label>
            `).join('')}
          </div>
        `;
      }

      observedRoot.hidden = (
        preset.mode !== 'observed'
      );

      observedTextarea.value = [
        'x,y',
        ...(preset.defaultData || []).map(
          (point) => `${point.x},${point.y}`
        ),
      ].join('\n');

      chartRoot.innerHTML = '';
      metricsRoot.innerHTML = '';
      visualizationStatus.textContent =
        preset.description;

      state.currentVisualization = null;
      saveVisualizationButton.disabled = true;
      notebookVisualizationButton.disabled = true;
      exportVisualizationButton.disabled = true;
    }

    function parameters() {
      return Object.fromEntries(
        Array.from(
          root.querySelectorAll(
            '[data-bvb-parameter]'
          )
        ).map((input) => [
          input.dataset.bvbParameter,
          input.value,
        ])
      );
    }

    presetSelect.addEventListener(
      'change',
      refreshPreset
    );

    plotButton.addEventListener('click', () => {
      try {
        const preset = presetById(
          presetSelect.value
        );
        const generated = preset.mode === 'observed'
          ? visualizationFromObserved(
              preset,
              observedTextarea.value
            )
          : generatePresetData(
              preset,
              parameters()
            );

        renderSvgChart(
          chartRoot,
          generated.series,
          preset.xLabel,
          preset.yLabel
        );

        metricsRoot.innerHTML = metricMarkup(
          generated.metrics
        );

        state.currentVisualization = {
          schema:
            'sc-lab-biochemistry-visualization/1.0',
          version: VERSION,
          presetId: preset.id,
          title: preset.title,
          description: preset.description,
          xLabel: preset.xLabel,
          yLabel: preset.yLabel,
          series: generated.series,
          metrics: generated.metrics,
          parameters: parameters(),
          audit: {
            createdAt: new Date().toISOString(),
            engine:
              'sc-lab-biochemistry-visualization-browser',
            release: VERSION,
          },
        };

        visualizationStatus.textContent =
          `${preset.title} generated.`;
        saveVisualizationButton.disabled = false;
        notebookVisualizationButton.disabled = false;
        exportVisualizationButton.disabled = false;
      } catch (error) {
        state.currentVisualization = null;
        visualizationStatus.textContent = String(
          error && error.message
            ? error.message
            : error
        );
      }
    });

    saveVisualizationButton.addEventListener(
      'click',
      () => {
        if (!state.currentVisualization) {
          return;
        }

        visualizationStatus.textContent =
          saveProject(state.currentVisualization)
            ? 'Visualization saved to project.'
            : 'Project storage was unavailable.';
      }
    );

    notebookVisualizationButton.addEventListener(
      'click',
      () => {
        if (!state.currentVisualization) {
          return;
        }

        visualizationStatus.textContent =
          addNotebook(state.currentVisualization)
            ? 'Visualization added to notebook.'
            : 'Notebook storage was unavailable.';
      }
    );

    exportVisualizationButton.addEventListener(
      'click',
      () => {
        if (!state.currentVisualization) {
          return;
        }

        downloadFile(
          `biochemistry-visualization-${Date.now()}.json`,
          'application/json',
          JSON.stringify(
            state.currentVisualization,
            null,
            2
          )
        );
      }
    );

    function refreshSampleCsv() {
      csvTextarea.value = sampleCsv(
        methodById(methodSelect.value)
      );
      batchStatus.textContent =
        'Sample CSV loaded for the selected method.';
      state.currentBatch = null;
      statisticsRoot.innerHTML = '';
      batchResultsRoot.innerHTML = '';
      exportCsvButton.disabled = true;
      exportJsonButton.disabled = true;
      saveBatchButton.disabled = true;
      notebookBatchButton.disabled = true;
    }

    methodSelect.addEventListener(
      'change',
      refreshSampleCsv
    );

    resetCsvButton.addEventListener(
      'click',
      refreshSampleCsv
    );

    fileInput.addEventListener('change', () => {
      const [file] = fileInput.files || [];

      if (!file) {
        return;
      }

      const reader = new FileReader();

      reader.addEventListener('load', () => {
        csvTextarea.value = String(
          reader.result || ''
        );
        batchStatus.textContent =
          `${file.name} loaded.`;
      });

      reader.addEventListener('error', () => {
        batchStatus.textContent =
          'The CSV file could not be read.';
      });

      reader.readAsText(file);
    });

    runBatchButton.addEventListener('click', () => {
      try {
        const method = methodById(
          methodSelect.value
        );

        state.currentBatch = batchRun(
          methodSelect.value,
          csvTextarea.value
        );

        statisticsRoot.innerHTML = statisticsMarkup(
          state.currentBatch,
          method
        );
        batchResultsRoot.innerHTML = batchTableMarkup(
          state.currentBatch,
          method
        );

        batchStatus.textContent = (
          `${state.currentBatch.successCount} of `
          + `${state.currentBatch.rowCount} rows calculated. `
          + (
            state.currentBatch.flags.length
              ? 'Review flags are present.'
              : 'No batch review flags.'
          )
        );

        exportCsvButton.disabled = false;
        exportJsonButton.disabled = false;
        saveBatchButton.disabled = false;
        notebookBatchButton.disabled = false;
      } catch (error) {
        state.currentBatch = null;
        batchStatus.textContent = String(
          error && error.message
            ? error.message
            : error
        );
      }
    });

    exportCsvButton.addEventListener('click', () => {
      if (!state.currentBatch) {
        return;
      }

      const method = methodById(
        state.currentBatch.methodId
      );

      downloadFile(
        `biochemistry-batch-${Date.now()}.csv`,
        'text/csv',
        batchToCsv(state.currentBatch, method)
      );
    });

    exportJsonButton.addEventListener('click', () => {
      if (!state.currentBatch) {
        return;
      }

      downloadFile(
        `biochemistry-batch-${Date.now()}.json`,
        'application/json',
        JSON.stringify(
          state.currentBatch,
          null,
          2
        )
      );
    });

    saveBatchButton.addEventListener('click', () => {
      if (!state.currentBatch) {
        return;
      }

      batchStatus.textContent =
        saveProject(state.currentBatch)
          ? 'Batch analysis saved to project.'
          : 'Project storage was unavailable.';
    });

    notebookBatchButton.addEventListener(
      'click',
      () => {
        if (!state.currentBatch) {
          return;
        }

        batchStatus.textContent =
          addNotebook(state.currentBatch)
            ? 'Batch analysis added to notebook.'
            : 'Notebook storage was unavailable.';
      }
    );

    refreshPreset();
    refreshSampleCsv();

    root.dataset.scBiochemistryVisualizationBatch =
      VERSION;
    state.initializedAt = new Date().toISOString();
  }

  function init() {
    if (typeof document === 'undefined') {
      return false;
    }

    const root = ensureRoot();

    if (!root) {
      state.lastError =
        'Biochemistry visualization mount unavailable.';
      return false;
    }

    if (!analysisApi()) {
      state.lastError =
        'Biochemistry analysis engine unavailable.';
      return false;
    }

    try {
      render(root);
      state.lastError = null;
      return true;
    } catch (error) {
      state.lastError = String(
        error && error.message
          ? error.message
          : error
      );
      return false;
    }
  }

  function status() {
    const root = document.querySelector(
      ROOT_SELECTOR
    );

    return {
      version: VERSION,
      analysisEngineVersion:
        analysisApi()?.VERSION || null,
      presetCount: PRESETS.presets.length,
      methodCount:
        analysisApi()?.definitions?.length || 0,
      rootFound: Boolean(root),
      rendered: Boolean(
        root?.querySelector('.sc-bvb-shell')
      ),
      currentVisualization:
        state.currentVisualization?.presetId || null,
      currentBatchMethod:
        state.currentBatch?.methodId || null,
      initializedAt: state.initializedAt,
      lastError: state.lastError,
    };
  }

  Lab.BiochemistryVisualizationBatch = {
    VERSION,
    presets: PRESETS.presets,
    parseCsv,
    summarize,
    linearRegression,
    generatePresetData,
    batchRun,
    init,
    status,
  };

  function start() {
    const delays = [0, 80, 220, 600, 1400];

    delays.forEach((delay) => {
      rootWindow.setTimeout(init, delay);
    });

    document.addEventListener(
      'sc-lab:module-opened',
      init
    );

    if (typeof MutationObserver !== 'undefined') {
      const observer = new MutationObserver(() => {
        if (!document.querySelector(ROOT_SELECTOR)) {
          init();
        }
      });

      observer.observe(
        document.documentElement,
        {
          childList: true,
          subtree: true,
        }
      );
    }
  }

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener(
        'DOMContentLoaded',
        start,
        { once: true }
      );
    } else {
      start();
    }
  }
})();
