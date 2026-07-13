(() => {
  'use strict';

  const rootWindow = typeof window !== 'undefined'
    ? window
    : globalThis;
  const Lab = rootWindow.SCLab = rootWindow.SCLab || {};
  const VERSION = '0.21.3';
  const MODULE_ID = 'biochemistry-molecular-analysis';
  const ROOT_SELECTOR =
    '[data-molecular-validation-provenance-root]';
  const PANEL_SELECTOR = [
    `[data-lab-module="${MODULE_ID}"]`,
    `[data-module-panel="${MODULE_ID}"]`,
  ].join(',');
  const PROFILES = {"schema":"sc-lab-molecular-validation-profiles/1.0","version":"0.21.3","profiles":[{"id":"precision-repeatability","title":"Precision and repeatability","description":"Evaluate replicate dispersion using mean, sample standard deviation, and coefficient of variation.","requiredColumns":["value"],"thresholds":[{"key":"minimumReplicates","label":"Minimum replicates","default":3,"min":2,"step":1},{"key":"maximumCvPercent","label":"Maximum CV (%)","default":10,"min":0,"step":0.1}]},{"id":"accuracy-recovery","title":"Accuracy and recovery","description":"Compare measured values with expected values and evaluate mean recovery and absolute bias.","requiredColumns":["expected","measured"],"thresholds":[{"key":"minimumRecoveryPercent","label":"Minimum recovery (%)","default":90,"step":0.1},{"key":"maximumRecoveryPercent","label":"Maximum recovery (%)","default":110,"step":0.1},{"key":"maximumAbsoluteBiasPercent","label":"Maximum absolute bias (%)","default":10,"min":0,"step":0.1}]},{"id":"calibration-linearity","title":"Calibration linearity","description":"Fit concentration against signal and evaluate slope, intercept, and coefficient of determination.","requiredColumns":["concentration","signal"],"thresholds":[{"key":"minimumLevels","label":"Minimum calibration levels","default":5,"min":2,"step":1},{"key":"minimumRSquared","label":"Minimum R²","default":0.99,"min":0,"max":1,"step":0.0001},{"key":"requirePositiveSlope","label":"Require positive slope","default":1,"min":0,"max":1,"step":1}]},{"id":"detection-quantitation","title":"Detection and quantitation limits","description":"Estimate LOD and LOQ from blank response variation and calibration slope.","requiredColumns":["blank","slope"],"thresholds":[{"key":"minimumBlankReplicates","label":"Minimum blank replicates","default":5,"min":2,"step":1},{"key":"maximumLod","label":"Maximum acceptable LOD","default":1,"min":0,"step":0.001},{"key":"maximumLoq","label":"Maximum acceptable LOQ","default":3,"min":0,"step":0.001}]},{"id":"blank-background","title":"Blank and background performance","description":"Evaluate mean and maximum blank response against acceptance limits.","requiredColumns":["value"],"thresholds":[{"key":"minimumBlanks","label":"Minimum blanks","default":3,"min":1,"step":1},{"key":"maximumMean","label":"Maximum mean blank","default":0.05,"min":0,"step":0.001},{"key":"maximumSingle","label":"Maximum single blank","default":0.1,"min":0,"step":0.001}]},{"id":"control-performance","title":"Control performance","description":"Evaluate control results using target values, assigned standard deviations, z-scores, and warning/action limits.","requiredColumns":["value","target","sd"],"thresholds":[{"key":"warningZ","label":"Warning |z|","default":2,"min":0,"step":0.1},{"key":"actionZ","label":"Action |z|","default":3,"min":0,"step":0.1}]},{"id":"robustness","title":"Robustness across conditions","description":"Compare condition-group means and evaluate maximum relative difference.","requiredColumns":["condition","value"],"thresholds":[{"key":"minimumConditions","label":"Minimum conditions","default":2,"min":2,"step":1},{"key":"maximumRelativeDifferencePercent","label":"Maximum relative difference (%)","default":10,"min":0,"step":0.1}]},{"id":"inter-run-comparability","title":"Inter-run comparability","description":"Compare run-group means, pooled dispersion, and relative bias between runs.","requiredColumns":["run","value"],"thresholds":[{"key":"minimumRuns","label":"Minimum runs","default":2,"min":2,"step":1},{"key":"maximumBiasPercent","label":"Maximum run bias (%)","default":10,"min":0,"step":0.1},{"key":"maximumPooledCvPercent","label":"Maximum pooled CV (%)","default":15,"min":0,"step":0.1}]}]};

  const state = {
    currentDossier: null,
    ledger: [],
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
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function formatNumber(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      return value === null || value === undefined
        ? '—'
        : String(value);
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

    return lines.slice(1).map((line, index) => {
      const cells = parseCsvLine(line);
      const row = { __row: index + 2 };

      headers.forEach((header, columnIndex) => {
        row[header] = cells[columnIndex] ?? '';
      });

      return row;
    });
  }

  function mean(values) {
    return values.reduce(
      (sum, value) => sum + value,
      0
    ) / values.length;
  }

  function standardDeviation(values) {
    if (values.length < 2) {
      return 0;
    }

    const average = mean(values);

    return Math.sqrt(
      values.reduce(
        (sum, value) => (
          sum + ((value - average) ** 2)
        ),
        0
      ) / (values.length - 1)
    );
  }

  function regression(points) {
    if (points.length < 2) {
      throw new Error(
        'At least two calibration points are required.'
      );
    }

    const xMean = mean(points.map((point) => point.x));
    const yMean = mean(points.map((point) => point.y));
    const numerator = points.reduce(
      (sum, point) => (
        sum
        + ((point.x - xMean) * (point.y - yMean))
      ),
      0
    );
    const denominator = points.reduce(
      (sum, point) => (
        sum + ((point.x - xMean) ** 2)
      ),
      0
    );

    if (denominator === 0) {
      throw new Error(
        'Calibration concentrations must vary.'
      );
    }

    const slope = numerator / denominator;
    const intercept = yMean - (slope * xMean);
    const total = points.reduce(
      (sum, point) => (
        sum + ((point.y - yMean) ** 2)
      ),
      0
    );
    const residual = points.reduce(
      (sum, point) => {
        const fitted = (
          slope * point.x + intercept
        );

        return (
          sum + ((point.y - fitted) ** 2)
        );
      },
      0
    );

    return {
      slope,
      intercept,
      rSquared: total === 0
        ? 1
        : 1 - (residual / total),
    };
  }

  function check(
    id,
    label,
    value,
    operator,
    limit,
    passed,
    unit = ''
  ) {
    return {
      id,
      label,
      value,
      operator,
      limit,
      unit,
      passed: Boolean(passed),
      status: passed ? 'pass' : 'fail',
    };
  }

  function numericColumn(rows, key) {
    return rows.map((row) => (
      finite(row[key], `${key} on CSV row ${row.__row}`)
    ));
  }

  function groupedValues(rows, groupKey) {
    const groups = new Map();

    for (const row of rows) {
      const group = String(row[groupKey] || '').trim();

      if (!group) {
        throw new Error(
          `${groupKey} is required on CSV row ${row.__row}.`
        );
      }

      const value = finite(
        row.value,
        `value on CSV row ${row.__row}`
      );

      if (!groups.has(group)) {
        groups.set(group, []);
      }

      groups.get(group).push(value);
    }

    return groups;
  }

  function validateRequiredColumns(
    profile,
    rows
  ) {
    if (!rows.length) {
      throw new Error(
        'Validation requires at least one data row.'
      );
    }

    for (const column of profile.requiredColumns) {
      if (!(column in rows[0])) {
        throw new Error(
          `Required CSV column is missing: ${column}`
        );
      }
    }
  }

  function validateProfile(
    profileId,
    rows,
    thresholds = {}
  ) {
    const profile = PROFILES.profiles.find(
      (candidate) => candidate.id === profileId
    );

    if (!profile) {
      throw new Error(
        `Unknown validation profile: ${profileId}`
      );
    }

    validateRequiredColumns(profile, rows);

    const resolved = Object.fromEntries(
      profile.thresholds.map((definition) => [
        definition.key,
        finite(
          thresholds[definition.key]
          ?? definition.default,
          definition.label
        ),
      ])
    );

    const checks = [];
    const metrics = {};

    if (profileId === 'precision-repeatability') {
      const values = numericColumn(rows, 'value');
      const average = mean(values);
      const sd = standardDeviation(values);
      const cv = average === 0
        ? null
        : Math.abs(sd / average) * 100;

      Object.assign(metrics, {
        n: values.length,
        mean: average,
        standardDeviation: sd,
        coefficientOfVariationPercent: cv,
        minimum: Math.min(...values),
        maximum: Math.max(...values),
      });

      checks.push(
        check(
          'minimum-replicates',
          'Replicate count',
          values.length,
          '>=',
          resolved.minimumReplicates,
          values.length >= resolved.minimumReplicates
        ),
        check(
          'maximum-cv',
          'Coefficient of variation',
          cv,
          '<=',
          resolved.maximumCvPercent,
          cv !== null
            && cv <= resolved.maximumCvPercent,
          '%'
        )
      );
    }

    if (profileId === 'accuracy-recovery') {
      const recoveries = [];
      const biases = [];

      for (const row of rows) {
        const expected = finite(
          row.expected,
          `expected on CSV row ${row.__row}`
        );
        const measured = finite(
          row.measured,
          `measured on CSV row ${row.__row}`
        );

        if (expected === 0) {
          throw new Error(
            `expected cannot be zero on CSV row ${row.__row}.`
          );
        }

        const recovery = measured / expected * 100;
        recoveries.push(recovery);
        biases.push(recovery - 100);
      }

      const meanRecovery = mean(recoveries);
      const meanBias = mean(biases);
      const maximumAbsoluteBias = Math.max(
        ...biases.map(Math.abs)
      );

      Object.assign(metrics, {
        n: recoveries.length,
        meanRecoveryPercent: meanRecovery,
        meanBiasPercent: meanBias,
        maximumAbsoluteBiasPercent:
          maximumAbsoluteBias,
        recoveryStandardDeviation:
          standardDeviation(recoveries),
      });

      checks.push(
        check(
          'minimum-recovery',
          'Mean recovery lower bound',
          meanRecovery,
          '>=',
          resolved.minimumRecoveryPercent,
          meanRecovery
            >= resolved.minimumRecoveryPercent,
          '%'
        ),
        check(
          'maximum-recovery',
          'Mean recovery upper bound',
          meanRecovery,
          '<=',
          resolved.maximumRecoveryPercent,
          meanRecovery
            <= resolved.maximumRecoveryPercent,
          '%'
        ),
        check(
          'maximum-absolute-bias',
          'Maximum absolute row bias',
          maximumAbsoluteBias,
          '<=',
          resolved.maximumAbsoluteBiasPercent,
          maximumAbsoluteBias
            <= resolved.maximumAbsoluteBiasPercent,
          '%'
        )
      );
    }

    if (profileId === 'calibration-linearity') {
      const points = rows.map((row) => ({
        x: finite(
          row.concentration,
          `concentration on CSV row ${row.__row}`
        ),
        y: finite(
          row.signal,
          `signal on CSV row ${row.__row}`
        ),
      }));
      const fit = regression(points);

      Object.assign(metrics, {
        levelCount: points.length,
        slope: fit.slope,
        intercept: fit.intercept,
        rSquared: fit.rSquared,
      });

      checks.push(
        check(
          'minimum-levels',
          'Calibration level count',
          points.length,
          '>=',
          resolved.minimumLevels,
          points.length >= resolved.minimumLevels
        ),
        check(
          'minimum-r-squared',
          'Coefficient of determination',
          fit.rSquared,
          '>=',
          resolved.minimumRSquared,
          fit.rSquared >= resolved.minimumRSquared
        ),
        check(
          'positive-slope',
          'Positive calibration slope',
          fit.slope,
          '>',
          0,
          resolved.requirePositiveSlope < 0.5
            || fit.slope > 0
        )
      );
    }

    if (profileId === 'detection-quantitation') {
      const blanks = numericColumn(rows, 'blank');
      const slopes = numericColumn(rows, 'slope');
      const blankSd = standardDeviation(blanks);
      const averageSlope = mean(slopes);

      if (averageSlope <= 0) {
        throw new Error(
          'Mean calibration slope must be positive.'
        );
      }

      const lod = 3.3 * blankSd / averageSlope;
      const loq = 10 * blankSd / averageSlope;

      Object.assign(metrics, {
        blankReplicates: blanks.length,
        blankMean: mean(blanks),
        blankStandardDeviation: blankSd,
        meanSlope: averageSlope,
        lod,
        loq,
      });

      checks.push(
        check(
          'minimum-blank-replicates',
          'Blank replicate count',
          blanks.length,
          '>=',
          resolved.minimumBlankReplicates,
          blanks.length
            >= resolved.minimumBlankReplicates
        ),
        check(
          'maximum-lod',
          'Estimated LOD',
          lod,
          '<=',
          resolved.maximumLod,
          lod <= resolved.maximumLod
        ),
        check(
          'maximum-loq',
          'Estimated LOQ',
          loq,
          '<=',
          resolved.maximumLoq,
          loq <= resolved.maximumLoq
        )
      );
    }

    if (profileId === 'blank-background') {
      const values = numericColumn(rows, 'value');
      const average = mean(values);
      const maximum = Math.max(...values);

      Object.assign(metrics, {
        n: values.length,
        meanBlank: average,
        maximumBlank: maximum,
        standardDeviation: standardDeviation(values),
      });

      checks.push(
        check(
          'minimum-blanks',
          'Blank count',
          values.length,
          '>=',
          resolved.minimumBlanks,
          values.length >= resolved.minimumBlanks
        ),
        check(
          'maximum-mean',
          'Mean blank response',
          average,
          '<=',
          resolved.maximumMean,
          average <= resolved.maximumMean
        ),
        check(
          'maximum-single',
          'Maximum single blank',
          maximum,
          '<=',
          resolved.maximumSingle,
          maximum <= resolved.maximumSingle
        )
      );
    }

    if (profileId === 'control-performance') {
      const zScores = rows.map((row) => {
        const value = finite(
          row.value,
          `value on CSV row ${row.__row}`
        );
        const target = finite(
          row.target,
          `target on CSV row ${row.__row}`
        );
        const sd = finite(
          row.sd,
          `sd on CSV row ${row.__row}`
        );

        if (sd <= 0) {
          throw new Error(
            `sd must be positive on CSV row ${row.__row}.`
          );
        }

        return (value - target) / sd;
      });
      const warningCount = zScores.filter(
        (value) => (
          Math.abs(value) >= resolved.warningZ
          && Math.abs(value) < resolved.actionZ
        )
      ).length;
      const actionCount = zScores.filter(
        (value) => (
          Math.abs(value) >= resolved.actionZ
        )
      ).length;
      const maximumAbsZ = Math.max(
        ...zScores.map(Math.abs)
      );

      Object.assign(metrics, {
        n: zScores.length,
        meanZ: mean(zScores),
        maximumAbsoluteZ: maximumAbsZ,
        warningCount,
        actionCount,
      });

      checks.push(
        check(
          'action-limit',
          'Control action-limit events',
          actionCount,
          '=',
          0,
          actionCount === 0
        ),
        check(
          'maximum-z',
          'Maximum absolute z-score',
          maximumAbsZ,
          '<',
          resolved.actionZ,
          maximumAbsZ < resolved.actionZ
        )
      );
    }

    if (profileId === 'robustness') {
      const groups = groupedValues(rows, 'condition');
      const groupMeans = Object.fromEntries(
        Array.from(groups.entries()).map(
          ([name, values]) => [
            name,
            mean(values),
          ]
        )
      );
      const means = Object.values(groupMeans);
      const center = mean(means);
      const difference = (
        Math.max(...means) - Math.min(...means)
      );
      const relativeDifference = center === 0
        ? null
        : Math.abs(difference / center) * 100;

      Object.assign(metrics, {
        conditionCount: groups.size,
        conditionMeans: groupMeans,
        relativeDifferencePercent:
          relativeDifference,
      });

      checks.push(
        check(
          'minimum-conditions',
          'Condition count',
          groups.size,
          '>=',
          resolved.minimumConditions,
          groups.size >= resolved.minimumConditions
        ),
        check(
          'maximum-relative-difference',
          'Maximum relative condition difference',
          relativeDifference,
          '<=',
          resolved.maximumRelativeDifferencePercent,
          relativeDifference !== null
            && relativeDifference
              <= resolved.maximumRelativeDifferencePercent,
          '%'
        )
      );
    }

    if (profileId === 'inter-run-comparability') {
      const groups = groupedValues(rows, 'run');
      const runMeans = Object.fromEntries(
        Array.from(groups.entries()).map(
          ([name, values]) => [
            name,
            mean(values),
          ]
        )
      );
      const values = Array.from(groups.values()).flat();
      const means = Object.values(runMeans);
      const center = mean(means);
      const bias = center === 0
        ? null
        : (
            (Math.max(...means) - Math.min(...means))
            / center
          ) * 100;
      const pooledMean = mean(values);
      const pooledSd = standardDeviation(values);
      const pooledCv = pooledMean === 0
        ? null
        : Math.abs(pooledSd / pooledMean) * 100;

      Object.assign(metrics, {
        runCount: groups.size,
        runMeans,
        relativeRunBiasPercent: bias,
        pooledMean,
        pooledStandardDeviation: pooledSd,
        pooledCvPercent: pooledCv,
      });

      checks.push(
        check(
          'minimum-runs',
          'Run count',
          groups.size,
          '>=',
          resolved.minimumRuns,
          groups.size >= resolved.minimumRuns
        ),
        check(
          'maximum-run-bias',
          'Relative run bias',
          bias,
          '<=',
          resolved.maximumBiasPercent,
          bias !== null
            && bias <= resolved.maximumBiasPercent,
          '%'
        ),
        check(
          'maximum-pooled-cv',
          'Pooled coefficient of variation',
          pooledCv,
          '<=',
          resolved.maximumPooledCvPercent,
          pooledCv !== null
            && pooledCv
              <= resolved.maximumPooledCvPercent,
          '%'
        )
      );
    }

    const failedChecks = checks.filter(
      (item) => !item.passed
    );

    return {
      profile,
      thresholds: resolved,
      metrics,
      checks,
      decision: failedChecks.length
        ? 'fail'
        : 'pass',
      failedCheckCount: failedChecks.length,
    };
  }

  function canonicalize(value) {
    if (Array.isArray(value)) {
      return `[${value.map(canonicalize).join(',')}]`;
    }

    if (
      value !== null
      && typeof value === 'object'
    ) {
      return `{${Object.keys(value)
        .sort()
        .map((key) => (
          `${JSON.stringify(key)}:${canonicalize(value[key])}`
        ))
        .join(',')}}`;
    }

    return JSON.stringify(value);
  }

  async function sha256(value) {
    const canonical = typeof value === 'string'
      ? value
      : canonicalize(value);

    if (
      rootWindow.crypto
      && rootWindow.crypto.subtle
      && typeof TextEncoder !== 'undefined'
    ) {
      const bytes = new TextEncoder().encode(canonical);
      const digest = await rootWindow.crypto.subtle.digest(
        'SHA-256',
        bytes
      );

      return Array.from(new Uint8Array(digest))
        .map((byte) => byte.toString(16).padStart(2, '0'))
        .join('');
    }

    let first = 0x811c9dc5;
    let second = 0x01000193;

    for (let index = 0; index < canonical.length; index += 1) {
      first ^= canonical.charCodeAt(index);
      first = Math.imul(first, 0x01000193);
      second ^= canonical.charCodeAt(index);
      second = Math.imul(second, 0x85ebca6b);
    }

    return [
      first >>> 0,
      second >>> 0,
      (first ^ second) >>> 0,
      Math.imul(first, second) >>> 0,
      (first + second) >>> 0,
      (first - second) >>> 0,
      Math.imul(first ^ 0x9e3779b9, second) >>> 0,
      Math.imul(second ^ 0x7f4a7c15, first) >>> 0,
    ].map((number) => (
      number.toString(16).padStart(8, '0')
    )).join('');
  }

  async function createProvenanceRecord(
    payload,
    metadata = {},
    previousHash = null
  ) {
    const payloadHash = await sha256(payload);
    const record = {
      schema:
        'sc-lab-molecular-analysis-provenance/1.0',
      version: VERSION,
      recordId:
        metadata.recordId
        || `scprov-${Date.now()}-${Math.random()
          .toString(16)
          .slice(2, 10)}`,
      eventType:
        metadata.eventType || 'validation-dossier',
      timestamp:
        metadata.timestamp || new Date().toISOString(),
      methodId: metadata.methodId || null,
      profileId: metadata.profileId || null,
      analyst: metadata.analyst || null,
      organization: metadata.organization || null,
      instrument: metadata.instrument || null,
      sampleSet: metadata.sampleSet || null,
      sourceIdentifiers:
        metadata.sourceIdentifiers || [],
      evidenceLinks: metadata.evidenceLinks || [],
      notes: metadata.notes || null,
      previousHash,
      payloadHash,
      payload,
      engine: {
        validationRelease: VERSION,
        analysisEngineVersion:
          Lab.BiochemistryMolecularAnalysis?.VERSION
          || '0.21.0',
        visualizationBatchVersion:
          Lab.BiochemistryVisualizationBatch?.VERSION
          || '0.21.2',
      },
    };

    record.recordHash = await sha256(record);
    return record;
  }

  async function verifyLedger(records) {
    const results = [];
    let previousHash = null;

    for (const record of records) {
      const copy = { ...record };
      const storedHash = copy.recordHash;
      delete copy.recordHash;

      const calculatedHash = await sha256(copy);
      const hashValid = calculatedHash === storedHash;
      const chainValid = (
        (record.previousHash || null) === previousHash
      );

      results.push({
        recordId: record.recordId,
        hashValid,
        chainValid,
        valid: hashValid && chainValid,
        storedHash,
        calculatedHash,
      });

      previousHash = storedHash;
    }

    return {
      valid: results.every((result) => result.valid),
      recordCount: records.length,
      results,
    };
  }

  function profileById(id) {
    return PROFILES.profiles.find(
      (profile) => profile.id === id
    ) || PROFILES.profiles[0];
  }

  function analysisMethods() {
    return (
      Lab.BiochemistryMolecularAnalysis?.definitions
      || []
    );
  }

  function sampleCsv(profileId) {
    const examples = {
      'precision-repeatability': [
        'value',
        '100.1',
        '99.8',
        '100.4',
        '100.0',
        '99.9',
      ],
      'accuracy-recovery': [
        'expected,measured',
        '10,9.8',
        '20,20.4',
        '30,29.7',
        '40,40.8',
        '50,49.5',
      ],
      'calibration-linearity': [
        'concentration,signal',
        '0,0.02',
        '1,0.51',
        '2,1.03',
        '3,1.49',
        '4,2.02',
      ],
      'detection-quantitation': [
        'blank,slope',
        '0.010,0.50',
        '0.012,0.50',
        '0.009,0.50',
        '0.011,0.50',
        '0.010,0.50',
        '0.013,0.50',
      ],
      'blank-background': [
        'value',
        '0.010',
        '0.014',
        '0.012',
        '0.011',
      ],
      'control-performance': [
        'value,target,sd',
        '100.5,100,1',
        '99.2,100,1',
        '101.1,100,1',
        '100.2,100,1',
      ],
      robustness: [
        'condition,value',
        'baseline,100.2',
        'baseline,99.8',
        'temperature-plus,101.5',
        'temperature-plus,100.9',
      ],
      'inter-run-comparability': [
        'run,value',
        'run-1,100.2',
        'run-1,99.8',
        'run-1,100.5',
        'run-2,101.0',
        'run-2,100.6',
        'run-2,100.8',
      ],
    };

    return (examples[profileId] || []).join('\n');
  }

  function csvEscape(value) {
    const text = String(value ?? '');

    return /[",\n\r]/.test(text)
      ? `"${text.replaceAll('"', '""')}"`
      : text;
  }

  function downloadFile(filename, type, content) {
    const blob = new Blob([content], { type });
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

  function persistLedger() {
    try {
      rootWindow.localStorage?.setItem(
        'sc-lab:molecular-provenance-ledger',
        JSON.stringify(state.ledger)
      );
    } catch (_error) {
      // Storage is an optional fallback.
    }
  }

  function loadLedger() {
    try {
      const parsed = JSON.parse(
        rootWindow.localStorage?.getItem(
          'sc-lab:molecular-provenance-ledger'
        ) || '[]'
      );

      state.ledger = Array.isArray(parsed)
        ? parsed
        : [];
    } catch (_error) {
      state.ledger = [];
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

    try {
      const key = 'sc-lab:project-analyses';
      const records = JSON.parse(
        rootWindow.localStorage?.getItem(key) || '[]'
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

  function addNotebook(record) {
    if (
      Lab.Notebook
      && typeof Lab.Notebook.add === 'function'
    ) {
      Lab.Notebook.add(record);
      return true;
    }

    try {
      const key = 'sc-lab:notebook';
      const records = JSON.parse(
        rootWindow.localStorage?.getItem(key) || '[]'
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

  function metricRows(metrics, prefix = '') {
    return Object.entries(metrics).flatMap(
      ([key, value]) => {
        const label = prefix
          ? `${prefix}.${key}`
          : key;

        if (
          value !== null
          && typeof value === 'object'
          && !Array.isArray(value)
        ) {
          return metricRows(value, label);
        }

        return [{
          label,
          value,
        }];
      }
    );
  }

  function dossierMarkup(dossier) {
    return `
      <div class="sc-mvp-decision sc-mvp-${dossier.decision}">
        <strong>${escapeHtml(
          dossier.decision.toUpperCase()
        )}</strong>
        <span>
          ${dossier.validation.failedCheckCount}
          failed acceptance check(s)
        </span>
      </div>

      <div class="sc-mvp-grid">
        <article>
          <h5>Validation identity</h5>
          <dl>
            <div>
              <dt>Method</dt>
              <dd>${escapeHtml(dossier.methodTitle)}</dd>
            </div>
            <div>
              <dt>Profile</dt>
              <dd>${escapeHtml(
                dossier.validation.profile.title
              )}</dd>
            </div>
            <div>
              <dt>Dataset rows</dt>
              <dd>${dossier.dataset.rowCount}</dd>
            </div>
            <div>
              <dt>Created</dt>
              <dd>${escapeHtml(
                dossier.audit.createdAt
              )}</dd>
            </div>
          </dl>
        </article>

        <article>
          <h5>Calculated metrics</h5>
          <dl>
            ${metricRows(
              dossier.validation.metrics
            ).map((row) => `
              <div>
                <dt>${escapeHtml(row.label)}</dt>
                <dd>${escapeHtml(
                  formatNumber(row.value)
                )}</dd>
              </div>
            `).join('')}
          </dl>
        </article>
      </div>

      <div class="sc-mvp-table-scroll">
        <table class="sc-mvp-table">
          <thead>
            <tr>
              <th>Acceptance check</th>
              <th>Observed</th>
              <th>Criterion</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${dossier.validation.checks.map(
              (item) => `
                <tr>
                  <th>${escapeHtml(item.label)}</th>
                  <td>
                    ${escapeHtml(formatNumber(item.value))}
                    ${escapeHtml(item.unit)}
                  </td>
                  <td>
                    ${escapeHtml(item.operator)}
                    ${escapeHtml(formatNumber(item.limit))}
                    ${escapeHtml(item.unit)}
                  </td>
                  <td>
                    <span class="sc-mvp-badge sc-mvp-${item.status}">
                      ${escapeHtml(item.status)}
                    </span>
                  </td>
                </tr>
              `
            ).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

  function ledgerMarkup(records) {
    if (!records.length) {
      return `
        <p class="sc-mvp-empty">
          No provenance records have been created.
        </p>
      `;
    }

    return `
      <div class="sc-mvp-ledger-list">
        ${records.map((record, index) => `
          <article class="sc-mvp-ledger-record">
            <header>
              <div>
                <span>Record ${index + 1}</span>
                <h5>${escapeHtml(record.eventType)}</h5>
              </div>
              <span class="sc-mvp-badge">
                ${escapeHtml(record.version)}
              </span>
            </header>
            <dl>
              <div>
                <dt>Record ID</dt>
                <dd><code>${escapeHtml(record.recordId)}</code></dd>
              </div>
              <div>
                <dt>Timestamp</dt>
                <dd>${escapeHtml(record.timestamp)}</dd>
              </div>
              <div>
                <dt>Method</dt>
                <dd>${escapeHtml(record.methodId || '—')}</dd>
              </div>
              <div>
                <dt>Profile</dt>
                <dd>${escapeHtml(record.profileId || '—')}</dd>
              </div>
              <div>
                <dt>Payload hash</dt>
                <dd><code>${escapeHtml(record.payloadHash)}</code></dd>
              </div>
              <div>
                <dt>Previous hash</dt>
                <dd><code>${escapeHtml(record.previousHash || 'GENESIS')}</code></dd>
              </div>
              <div>
                <dt>Record hash</dt>
                <dd><code>${escapeHtml(record.recordHash)}</code></dd>
              </div>
            </dl>
          </article>
        `).join('')}
      </div>
    `;
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
      'data-molecular-validation-provenance-root',
      ''
    );
    panel.appendChild(root);
    return root;
  }

  function render(root) {
    if (
      root.dataset.scMolecularValidationProvenance
        === VERSION
      && root.children.length
    ) {
      return;
    }

    loadLedger();

    root.innerHTML = `
      <section class="sc-mvp-shell">
        <header class="sc-mvp-header">
          <div>
            <p class="sc-mvp-kicker">
              LAB/MOLECULAR/VALIDATION
            </p>
            <h3>
              Molecular Analysis Validation and Provenance
            </h3>
            <p>
              Evaluate analytical performance against explicit
              acceptance criteria and create tamper-evident,
              evidence-linked validation records.
            </p>
          </div>
          <span class="sc-mvp-version">v${VERSION}</span>
        </header>

        <div class="sc-mvp-tabs" role="tablist">
          <button
            type="button"
            class="is-active"
            data-mvp-tab="validation"
          >
            Validation studio
          </button>
          <button
            type="button"
            data-mvp-tab="provenance"
          >
            Provenance ledger
          </button>
        </div>

        <section
          class="sc-mvp-workspace"
          data-mvp-workspace="validation"
        >
          <div class="sc-mvp-control-grid">
            <label>
              <span>Biochemistry method</span>
              <select data-mvp-method>
                ${analysisMethods().map((method) => `
                  <option value="${escapeHtml(method.id)}">
                    ${escapeHtml(method.category)}
                    —
                    ${escapeHtml(method.title)}
                  </option>
                `).join('')}
              </select>
            </label>

            <label>
              <span>Validation profile</span>
              <select data-mvp-profile>
                ${PROFILES.profiles.map((profile) => `
                  <option value="${escapeHtml(profile.id)}">
                    ${escapeHtml(profile.title)}
                  </option>
                `).join('')}
              </select>
            </label>
          </div>

          <div data-mvp-thresholds></div>

          <label class="sc-mvp-data-label">
            <span>Validation dataset CSV</span>
            <textarea
              rows="10"
              spellcheck="false"
              data-mvp-csv
            ></textarea>
          </label>

          <div class="sc-mvp-actions">
            <button
              type="button"
              class="sc-mvp-primary"
              data-mvp-run
            >
              Run validation
            </button>
            <button
              type="button"
              data-mvp-sample
            >
              Load sample CSV
            </button>
            <button
              type="button"
              data-mvp-export-dossier
              disabled
            >
              Export dossier
            </button>
            <button
              type="button"
              data-mvp-save-project
              disabled
            >
              Save to project
            </button>
            <button
              type="button"
              data-mvp-add-notebook
              disabled
            >
              Add to notebook
            </button>
          </div>

          <p
            class="sc-mvp-status-line"
            aria-live="polite"
            data-mvp-validation-status
          ></p>

          <div data-mvp-dossier></div>
        </section>

        <section
          class="sc-mvp-workspace"
          data-mvp-workspace="provenance"
          hidden
        >
          <div class="sc-mvp-control-grid">
            <label>
              <span>Analyst or responsible party</span>
              <input type="text" data-mvp-analyst />
            </label>
            <label>
              <span>Organization</span>
              <input type="text" data-mvp-organization />
            </label>
            <label>
              <span>Instrument or system</span>
              <input type="text" data-mvp-instrument />
            </label>
            <label>
              <span>Sample set</span>
              <input type="text" data-mvp-sample-set />
            </label>
          </div>

          <label class="sc-mvp-data-label">
            <span>Source identifiers</span>
            <textarea
              rows="3"
              placeholder="One source identifier per line"
              data-mvp-sources
            ></textarea>
          </label>

          <label class="sc-mvp-data-label">
            <span>Evidence links</span>
            <textarea
              rows="3"
              placeholder="One URL or evidence reference per line"
              data-mvp-evidence
            ></textarea>
          </label>

          <label class="sc-mvp-data-label">
            <span>Provenance notes</span>
            <textarea
              rows="4"
              data-mvp-notes
            ></textarea>
          </label>

          <div class="sc-mvp-actions">
            <button
              type="button"
              class="sc-mvp-primary"
              data-mvp-create-record
              disabled
            >
              Create provenance record
            </button>
            <button
              type="button"
              data-mvp-verify-ledger
            >
              Verify ledger
            </button>
            <button
              type="button"
              data-mvp-export-ledger
              disabled
            >
              Export ledger
            </button>
            <button
              type="button"
              data-mvp-clear-ledger
            >
              Clear local ledger
            </button>
          </div>

          <p
            class="sc-mvp-status-line"
            aria-live="polite"
            data-mvp-provenance-status
          ></p>

          <div data-mvp-ledger></div>
        </section>

        <aside class="sc-mvp-boundary">
          <strong>Research-use boundary</strong>
          Validation outputs document computational checks against
          user-defined criteria. They do not establish regulatory
          compliance, replace qualified laboratory review, validate
          an instrument, or authorize clinical use.
        </aside>
      </section>
    `;

    const tabButtons = root.querySelectorAll(
      '[data-mvp-tab]'
    );
    const workspaces = root.querySelectorAll(
      '[data-mvp-workspace]'
    );
    const methodSelect = root.querySelector(
      '[data-mvp-method]'
    );
    const profileSelect = root.querySelector(
      '[data-mvp-profile]'
    );
    const thresholdRoot = root.querySelector(
      '[data-mvp-thresholds]'
    );
    const csvTextarea = root.querySelector(
      '[data-mvp-csv]'
    );
    const runButton = root.querySelector(
      '[data-mvp-run]'
    );
    const sampleButton = root.querySelector(
      '[data-mvp-sample]'
    );
    const exportDossierButton = root.querySelector(
      '[data-mvp-export-dossier]'
    );
    const saveProjectButton = root.querySelector(
      '[data-mvp-save-project]'
    );
    const notebookButton = root.querySelector(
      '[data-mvp-add-notebook]'
    );
    const validationStatus = root.querySelector(
      '[data-mvp-validation-status]'
    );
    const dossierRoot = root.querySelector(
      '[data-mvp-dossier]'
    );

    const analystInput = root.querySelector(
      '[data-mvp-analyst]'
    );
    const organizationInput = root.querySelector(
      '[data-mvp-organization]'
    );
    const instrumentInput = root.querySelector(
      '[data-mvp-instrument]'
    );
    const sampleSetInput = root.querySelector(
      '[data-mvp-sample-set]'
    );
    const sourcesInput = root.querySelector(
      '[data-mvp-sources]'
    );
    const evidenceInput = root.querySelector(
      '[data-mvp-evidence]'
    );
    const notesInput = root.querySelector(
      '[data-mvp-notes]'
    );
    const createRecordButton = root.querySelector(
      '[data-mvp-create-record]'
    );
    const verifyLedgerButton = root.querySelector(
      '[data-mvp-verify-ledger]'
    );
    const exportLedgerButton = root.querySelector(
      '[data-mvp-export-ledger]'
    );
    const clearLedgerButton = root.querySelector(
      '[data-mvp-clear-ledger]'
    );
    const provenanceStatus = root.querySelector(
      '[data-mvp-provenance-status]'
    );
    const ledgerRoot = root.querySelector(
      '[data-mvp-ledger]'
    );

    function activateTab(id) {
      tabButtons.forEach((button) => {
        button.classList.toggle(
          'is-active',
          button.dataset.mvpTab === id
        );
      });

      workspaces.forEach((workspace) => {
        workspace.hidden = (
          workspace.dataset.mvpWorkspace !== id
        );
      });
    }

    tabButtons.forEach((button) => {
      button.addEventListener('click', () => {
        activateTab(button.dataset.mvpTab);
      });
    });

    function renderThresholds() {
      const profile = profileById(
        profileSelect.value
      );

      thresholdRoot.innerHTML = `
        <div class="sc-mvp-profile-summary">
          <h4>${escapeHtml(profile.title)}</h4>
          <p>${escapeHtml(profile.description)}</p>
          <p>
            Required columns:
            <code>${escapeHtml(
              profile.requiredColumns.join(', ')
            )}</code>
          </p>
        </div>
        <div class="sc-mvp-threshold-grid">
          ${profile.thresholds.map((definition) => `
            <label>
              <span>${escapeHtml(definition.label)}</span>
              <input
                type="number"
                step="${escapeHtml(
                  definition.step ?? 'any'
                )}"
                value="${escapeHtml(definition.default)}"
                data-mvp-threshold="${escapeHtml(definition.key)}"
                ${definition.min !== undefined
                  ? `min="${definition.min}"`
                  : ''}
                ${definition.max !== undefined
                  ? `max="${definition.max}"`
                  : ''}
              />
            </label>
          `).join('')}
        </div>
      `;

      csvTextarea.value = sampleCsv(profile.id);
      state.currentDossier = null;
      dossierRoot.innerHTML = '';
      exportDossierButton.disabled = true;
      saveProjectButton.disabled = true;
      notebookButton.disabled = true;
      createRecordButton.disabled = true;
      validationStatus.textContent =
        profile.description;
    }

    function thresholdValues() {
      return Object.fromEntries(
        Array.from(
          root.querySelectorAll(
            '[data-mvp-threshold]'
          )
        ).map((input) => [
          input.dataset.mvpThreshold,
          input.value,
        ])
      );
    }

    profileSelect.addEventListener(
      'change',
      renderThresholds
    );

    sampleButton.addEventListener('click', () => {
      csvTextarea.value = sampleCsv(
        profileSelect.value
      );
      validationStatus.textContent =
        'Sample validation dataset loaded.';
    });

    runButton.addEventListener('click', () => {
      try {
        const rows = parseCsv(csvTextarea.value);
        const validation = validateProfile(
          profileSelect.value,
          rows,
          thresholdValues()
        );
        const method = analysisMethods().find(
          (candidate) => (
            candidate.id === methodSelect.value
          )
        );

        state.currentDossier = {
          schema:
            'sc-lab-molecular-analysis-validation-dossier/1.0',
          version: VERSION,
          methodId: methodSelect.value,
          methodTitle:
            method?.title || methodSelect.value,
          category: method?.category || null,
          profileId: profileSelect.value,
          decision: validation.decision,
          validation,
          dataset: {
            rowCount: rows.length,
            columns: Object.keys(rows[0] || {})
              .filter((key) => key !== '__row'),
            rows,
            sourceFormat: 'csv',
          },
          responsibleUse: {
            researchUseOnly: true,
            regulatoryComplianceEstablished: false,
            clinicalUseAuthorized: false,
          },
          audit: {
            createdAt: new Date().toISOString(),
            engine:
              'sc-lab-molecular-validation-browser',
            release: VERSION,
            analysisEngineVersion:
              Lab.BiochemistryMolecularAnalysis?.VERSION
              || '0.21.0',
          },
        };

        dossierRoot.innerHTML = dossierMarkup(
          state.currentDossier
        );

        validationStatus.textContent =
          validation.decision === 'pass'
            ? 'All configured acceptance checks passed.'
            : (
                `${validation.failedCheckCount} `
                + 'acceptance check(s) failed.'
              );

        exportDossierButton.disabled = false;
        saveProjectButton.disabled = false;
        notebookButton.disabled = false;
        createRecordButton.disabled = false;
      } catch (error) {
        state.currentDossier = null;
        dossierRoot.innerHTML = '';
        validationStatus.textContent = String(
          error && error.message
            ? error.message
            : error
        );
      }
    });

    exportDossierButton.addEventListener(
      'click',
      () => {
        if (!state.currentDossier) {
          return;
        }

        downloadFile(
          `molecular-validation-dossier-${Date.now()}.json`,
          'application/json',
          JSON.stringify(
            state.currentDossier,
            null,
            2
          )
        );
      }
    );

    saveProjectButton.addEventListener(
      'click',
      () => {
        if (!state.currentDossier) {
          return;
        }

        validationStatus.textContent =
          saveProject(state.currentDossier)
            ? 'Validation dossier saved to project.'
            : 'Project storage was unavailable.';
      }
    );

    notebookButton.addEventListener(
      'click',
      () => {
        if (!state.currentDossier) {
          return;
        }

        validationStatus.textContent =
          addNotebook(state.currentDossier)
            ? 'Validation dossier added to notebook.'
            : 'Notebook storage was unavailable.';
      }
    );

    function lines(value) {
      return String(value)
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean);
    }

    function refreshLedger() {
      ledgerRoot.innerHTML = ledgerMarkup(
        state.ledger
      );
      exportLedgerButton.disabled = (
        state.ledger.length === 0
      );
    }

    createRecordButton.addEventListener(
      'click',
      async () => {
        if (!state.currentDossier) {
          provenanceStatus.textContent =
            'Run a validation before creating provenance.';
          return;
        }

        createRecordButton.disabled = true;
        provenanceStatus.textContent =
          'Creating SHA-256 provenance record…';

        try {
          const previous = state.ledger.at(-1);
          const record = await createProvenanceRecord(
            state.currentDossier,
            {
              methodId:
                state.currentDossier.methodId,
              profileId:
                state.currentDossier.profileId,
              analyst: analystInput.value.trim(),
              organization:
                organizationInput.value.trim(),
              instrument:
                instrumentInput.value.trim(),
              sampleSet:
                sampleSetInput.value.trim(),
              sourceIdentifiers:
                lines(sourcesInput.value),
              evidenceLinks:
                lines(evidenceInput.value),
              notes: notesInput.value.trim(),
            },
            previous?.recordHash || null
          );

          state.ledger.push(record);
          persistLedger();
          refreshLedger();
          provenanceStatus.textContent =
            `Provenance record ${record.recordId} created.`;
        } catch (error) {
          provenanceStatus.textContent = String(
            error && error.message
              ? error.message
              : error
          );
        } finally {
          createRecordButton.disabled = false;
        }
      }
    );

    verifyLedgerButton.addEventListener(
      'click',
      async () => {
        const verification = await verifyLedger(
          state.ledger
        );

        provenanceStatus.textContent = (
          verification.valid
            ? (
                `Ledger verified: `
                + `${verification.recordCount} valid record(s).`
              )
            : 'Ledger verification failed.'
        );
      }
    );

    exportLedgerButton.addEventListener(
      'click',
      () => {
        downloadFile(
          `molecular-provenance-ledger-${Date.now()}.json`,
          'application/json',
          JSON.stringify(
            {
              schema:
                'sc-lab-molecular-provenance-ledger/1.0',
              version: VERSION,
              exportedAt: new Date().toISOString(),
              recordCount: state.ledger.length,
              records: state.ledger,
            },
            null,
            2
          )
        );
      }
    );

    clearLedgerButton.addEventListener(
      'click',
      () => {
        state.ledger = [];
        persistLedger();
        refreshLedger();
        provenanceStatus.textContent =
          'Local provenance ledger cleared.';
      }
    );

    renderThresholds();
    refreshLedger();

    root.dataset.scMolecularValidationProvenance =
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
        'Molecular validation mount unavailable.';
      return false;
    }

    if (!analysisMethods().length) {
      state.lastError =
        'Biochemistry method catalog unavailable.';
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
    const root = typeof document !== 'undefined'
      ? document.querySelector(ROOT_SELECTOR)
      : null;

    return {
      version: VERSION,
      profileCount: PROFILES.profiles.length,
      methodCount: analysisMethods().length,
      ledgerRecordCount: state.ledger.length,
      currentProfileId:
        state.currentDossier?.profileId || null,
      currentDecision:
        state.currentDossier?.decision || null,
      rootFound: Boolean(root),
      rendered: Boolean(
        root?.querySelector('.sc-mvp-shell')
      ),
      initializedAt: state.initializedAt,
      lastError: state.lastError,
    };
  }

  Lab.MolecularAnalysisValidationProvenance = {
    VERSION,
    profiles: PROFILES.profiles,
    parseCsv,
    regression,
    validateProfile,
    canonicalize,
    sha256,
    createProvenanceRecord,
    verifyLedger,
    init,
    status,
  };

  function start() {
    [0, 80, 220, 600, 1400].forEach(
      (delay) => rootWindow.setTimeout(init, delay)
    );

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
