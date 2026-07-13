(() => {
  'use strict';

  const W = typeof window !== 'undefined'
    ? window
    : globalThis;
  const Lab = W.SCLab = W.SCLab || {};
  const VERSION = '0.22.3';
  const ROOT_SELECTOR =
    '[data-bioprocess-validation-provenance-root]';

  const profiles = [
    {
      id: 'batch-record-completeness',
      label: 'Batch record completeness',
      thresholds: {
        maximumMissingFields: 0,
        minimumEvidenceLinks: 1,
      },
      sample: [
        'batchId,lotId,startedAt,endedAt,operator,materialLot,evidenceLinks',
        'B-001,L-001,2026-07-13T08:00:00Z,2026-07-16T12:00:00Z,Analyst A,M-100,record://batch-B-001|record://materials-B-001',
      ].join('\n'),
    },
    {
      id: 'cpp-conformance',
      label: 'Critical process parameter conformance',
      thresholds: {
        maximumActionExcursions: 0,
        maximumWarningPercent: 10,
      },
      sample: [
        'parameter,value,low,high',
        'temperature,37,35,39',
        'pH,7.0,6.8,7.2',
        'dissolved oxygen,45,20,100',
      ].join('\n'),
    },
    {
      id: 'cqa-conformance',
      label: 'Critical quality attribute conformance',
      thresholds: {
        maximumFailures: 0,
        minimumPassPercent: 100,
      },
      sample: [
        'attribute,value,low,high',
        'purity,98.5,95,100',
        'potency,101,90,110',
        'bioburden,0,0,1',
      ].join('\n'),
    },
    {
      id: 'cross-batch-consistency',
      label: 'Cross-batch consistency',
      thresholds: {
        minimumBatches: 3,
        maximumYieldCvPercent: 10,
        maximumTiterCvPercent: 10,
        maximumCycleTimeCvPercent: 15,
      },
      sample: [
        'batchId,yield,titer,cycleTime',
        'B-001,82,3.9,72',
        'B-002,84,4.0,70',
        'B-003,83,4.1,71',
      ].join('\n'),
    },
    {
      id: 'monitoring-control-performance',
      label: 'Monitoring and control performance',
      thresholds: {
        maximumActionCount: 0,
        maximumWarningCount: 5,
        maximumAbsoluteFinalError: 2,
        maximumIntegralAbsoluteError: 100,
      },
      sample: [
        'runId,actionCount,warningCount,finalError,integralAbsoluteError',
        'run-1,0,1,0.8,24',
        'run-2,0,2,-0.6,27',
      ].join('\n'),
    },
    {
      id: 'excursion-disposition',
      label: 'Excursion disposition',
      thresholds: {
        maximumOpenActionExcursions: 0,
        maximumUndocumentedExcursions: 0,
      },
      sample: [
        'eventId,severity,status,investigationId,evidenceLink',
        'E-001,warning,closed,INV-001,record://investigation-E-001',
        'E-002,action,resolved,INV-002,record://investigation-E-002',
      ].join('\n'),
    },
    {
      id: 'hold-time-stability',
      label: 'Hold-time stability',
      thresholds: {
        minimumPoints: 3,
        maximumAbsoluteChangePercent: 5,
        maximumSlopePercentPerHour: 1,
      },
      sample: [
        'time,value',
        '0,100',
        '2,99',
        '4,98',
      ].join('\n'),
    },
    {
      id: 'release-readiness',
      label: 'Batch release readiness',
      thresholds: {
        maximumFailedCriticalChecks: 0,
        maximumOpenMajorChecks: 0,
        minimumEvidenceCoveragePercent: 100,
      },
      sample: [
        'checkId,category,critical,status,evidence',
        'C-001,critical,true,pass,record://cqa-B-001',
        'C-002,major,false,closed,record://cpp-B-001',
        'C-003,minor,false,complete,record://review-B-001',
      ].join('\n'),
    },
  ];

  const eventTypes = [
    'monitoring-analysis',
    'control-simulation',
    'validation-decision',
    'batch-disposition',
    'dossier-export',
  ];

  const state = {
    lastResult: null,
    ledger: [],
    lastDossier: null,
    rendered: false,
    lastError: null,
  };

  function finite(value, label) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      throw new Error(`${label} must be numerical and finite.`);
    }

    return number;
  }

  function mean(values) {
    if (!values.length) {
      throw new Error('At least one value is required.');
    }

    return values.reduce(
      (sum, value) => sum + value,
      0
    ) / values.length;
  }

  function sd(values) {
    if (values.length < 2) {
      return 0;
    }

    const average = mean(values);

    return Math.sqrt(
      values.reduce(
        (sum, value) => (
          sum + (value - average) ** 2
        ),
        0
      ) / (values.length - 1)
    );
  }

  function cv(values) {
    const average = mean(values);

    return average === 0
      ? null
      : Math.abs(sd(values) / average) * 100;
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

  function profile(profileId) {
    const found = profiles.find(
      (item) => item.id === profileId
    );

    if (!found) {
      throw new Error(
        `Unknown validation profile: ${profileId}`
      );
    }

    return found;
  }

  function parseCsv(text) {
    const lines = String(text || '')
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean);

    if (lines.length < 2) {
      throw new Error(
        'CSV input requires a header and at least one data row.'
      );
    }

    function split(line) {
      const values = [];
      let current = '';
      let quoted = false;

      for (let index = 0; index < line.length; index += 1) {
        const character = line[index];

        if (character === '"') {
          if (
            quoted
            && line[index + 1] === '"'
          ) {
            current += '"';
            index += 1;
          } else {
            quoted = !quoted;
          }
        } else if (
          character === ','
          && !quoted
        ) {
          values.push(current.trim());
          current = '';
        } else {
          current += character;
        }
      }

      values.push(current.trim());
      return values;
    }

    const headers = split(lines[0]);

    return lines.slice(1).map((line) => {
      const values = split(line);

      return Object.fromEntries(
        headers.map(
          (header, index) => [
            header,
            values[index] ?? '',
          ]
        )
      );
    });
  }

  function resolveThresholds(definition, supplied = {}) {
    return Object.fromEntries(
      Object.entries(definition.thresholds)
        .map(([key, value]) => [
          key,
          finite(
            supplied[key] ?? value,
            key
          ),
        ])
    );
  }

  function regression(points) {
    if (points.length < 2) {
      throw new Error(
        'At least two hold-time points are required.'
      );
    }

    const xMean = mean(
      points.map((point) => point[0])
    );
    const yMean = mean(
      points.map((point) => point[1])
    );
    const denominator = points.reduce(
      (sum, point) => (
        sum + (point[0] - xMean) ** 2
      ),
      0
    );

    if (denominator === 0) {
      throw new Error(
        'Hold-time observations must use distinct times.'
      );
    }

    const slope = points.reduce(
      (sum, point) => (
        sum
        + (point[0] - xMean)
        * (point[1] - yMean)
      ),
      0
    ) / denominator;

    return {
      slope,
      intercept: yMean - slope * xMean,
    };
  }

  function evaluate(
    profileId,
    rows,
    suppliedThresholds = {}
  ) {
    const definition = profile(profileId);
    const thresholds = resolveThresholds(
      definition,
      suppliedThresholds
    );

    if (!Array.isArray(rows) || !rows.length) {
      throw new Error(
        'Validation requires at least one data row.'
      );
    }

    let metrics = {};
    let checks = [];

    if (profileId === 'batch-record-completeness') {
      const required = [
        'batchId',
        'lotId',
        'startedAt',
        'endedAt',
        'operator',
        'materialLot',
      ];
      let missing = 0;
      const batches = rows.map((row) => {
        const missingFields = required.filter(
          (key) => !String(row[key] || '').trim()
        );
        const evidence = Array.isArray(row.evidenceLinks)
          ? row.evidenceLinks
          : String(row.evidenceLinks || '')
              .split('|')
              .map((item) => item.trim())
              .filter(Boolean);

        missing += missingFields.length;

        return {
          batchId: row.batchId,
          missingFields,
          evidenceCount: evidence.length,
        };
      });
      const minimumEvidenceLinks = Math.min(
        ...batches.map(
          (batch) => batch.evidenceCount
        )
      );

      metrics = {
        batchCount: rows.length,
        missingFieldCount: missing,
        minimumEvidenceLinks,
        batches,
      };
      checks = [
        check(
          'maximum-missing-fields',
          'Missing required fields',
          missing,
          '<=',
          thresholds.maximumMissingFields,
          missing <= thresholds.maximumMissingFields
        ),
        check(
          'minimum-evidence-links',
          'Minimum evidence links',
          minimumEvidenceLinks,
          '>=',
          thresholds.minimumEvidenceLinks,
          minimumEvidenceLinks
            >= thresholds.minimumEvidenceLinks
        ),
      ];
    } else if (profileId === 'cpp-conformance') {
      let actionExcursionCount = 0;
      let warningCount = 0;
      const observations = rows.map((row, index) => {
        const value = finite(
          row.value,
          `value on row ${index + 1}`
        );
        const low = finite(
          row.low,
          `low on row ${index + 1}`
        );
        const high = finite(
          row.high,
          `high on row ${index + 1}`
        );

        if (low > high) {
          throw new Error(
            `low exceeds high on row ${index + 1}.`
          );
        }

        let status = 'pass';

        if (value < low || value > high) {
          status = 'action';
          actionExcursionCount += 1;
        } else {
          const band = (high - low) * 0.1;

          if (
            value < low + band
            || value > high - band
          ) {
            status = 'warning';
            warningCount += 1;
          }
        }

        return {
          parameter: row.parameter,
          value,
          low,
          high,
          status,
        };
      });
      const warningPercent = (
        warningCount / rows.length * 100
      );

      metrics = {
        observationCount: rows.length,
        actionExcursionCount,
        warningCount,
        warningPercent,
        observations,
      };
      checks = [
        check(
          'maximum-action-excursions',
          'Action-limit excursions',
          actionExcursionCount,
          '<=',
          thresholds.maximumActionExcursions,
          actionExcursionCount
            <= thresholds.maximumActionExcursions
        ),
        check(
          'maximum-warning-percent',
          'Warning observations',
          warningPercent,
          '<=',
          thresholds.maximumWarningPercent,
          warningPercent
            <= thresholds.maximumWarningPercent,
          '%'
        ),
      ];
    } else if (profileId === 'cqa-conformance') {
      let failureCount = 0;
      const observations = rows.map((row, index) => {
        const value = finite(
          row.value,
          `value on row ${index + 1}`
        );
        const low = finite(row.low, 'low');
        const high = finite(row.high, 'high');
        const passed = value >= low && value <= high;

        failureCount += passed ? 0 : 1;

        return {
          attribute: row.attribute,
          value,
          low,
          high,
          status: passed ? 'pass' : 'fail',
        };
      });
      const passPercent = (
        (rows.length - failureCount)
        / rows.length
        * 100
      );

      metrics = {
        observationCount: rows.length,
        failureCount,
        passPercent,
        observations,
      };
      checks = [
        check(
          'maximum-failures',
          'Failed CQA observations',
          failureCount,
          '<=',
          thresholds.maximumFailures,
          failureCount <= thresholds.maximumFailures
        ),
        check(
          'minimum-pass-percent',
          'CQA pass rate',
          passPercent,
          '>=',
          thresholds.minimumPassPercent,
          passPercent >= thresholds.minimumPassPercent,
          '%'
        ),
      ];
    } else if (profileId === 'cross-batch-consistency') {
      const yields = rows.map(
        (row) => finite(row.yield, 'yield')
      );
      const titers = rows.map(
        (row) => finite(row.titer, 'titer')
      );
      const cycleTimes = rows.map(
        (row) => finite(row.cycleTime, 'cycleTime')
      );
      const yieldCv = cv(yields);
      const titerCv = cv(titers);
      const cycleTimeCv = cv(cycleTimes);

      metrics = {
        batchCount: rows.length,
        yield: {
          mean: mean(yields),
          standardDeviation: sd(yields),
          coefficientOfVariationPercent: yieldCv,
        },
        titer: {
          mean: mean(titers),
          standardDeviation: sd(titers),
          coefficientOfVariationPercent: titerCv,
        },
        cycleTime: {
          mean: mean(cycleTimes),
          standardDeviation: sd(cycleTimes),
          coefficientOfVariationPercent: cycleTimeCv,
        },
      };
      checks = [
        check(
          'minimum-batches',
          'Comparable batches',
          rows.length,
          '>=',
          thresholds.minimumBatches,
          rows.length >= thresholds.minimumBatches
        ),
        check(
          'maximum-yield-cv',
          'Yield CV',
          yieldCv,
          '<=',
          thresholds.maximumYieldCvPercent,
          yieldCv !== null
            && yieldCv <= thresholds.maximumYieldCvPercent,
          '%'
        ),
        check(
          'maximum-titer-cv',
          'Titer CV',
          titerCv,
          '<=',
          thresholds.maximumTiterCvPercent,
          titerCv !== null
            && titerCv <= thresholds.maximumTiterCvPercent,
          '%'
        ),
        check(
          'maximum-cycle-time-cv',
          'Cycle-time CV',
          cycleTimeCv,
          '<=',
          thresholds.maximumCycleTimeCvPercent,
          cycleTimeCv !== null
            && cycleTimeCv
              <= thresholds.maximumCycleTimeCvPercent,
          '%'
        ),
      ];
    } else if (
      profileId === 'monitoring-control-performance'
    ) {
      const actionCount = rows.reduce(
        (sum, row) => (
          sum + finite(row.actionCount, 'actionCount')
        ),
        0
      );
      const warningCount = rows.reduce(
        (sum, row) => (
          sum + finite(row.warningCount, 'warningCount')
        ),
        0
      );
      const finalErrors = rows.map(
        (row) => Math.abs(
          finite(row.finalError, 'finalError')
        )
      );
      const iaeValues = rows.map(
        (row) => finite(
          row.integralAbsoluteError,
          'integralAbsoluteError'
        )
      );
      const maximumAbsoluteFinalError = Math.max(
        ...finalErrors
      );
      const maximumIntegralAbsoluteError = Math.max(
        ...iaeValues
      );

      metrics = {
        runCount: rows.length,
        actionCount,
        warningCount,
        maximumAbsoluteFinalError,
        meanAbsoluteFinalError: mean(finalErrors),
        maximumIntegralAbsoluteError,
        meanIntegralAbsoluteError: mean(iaeValues),
      };
      checks = [
        check(
          'maximum-actions',
          'Action excursions',
          actionCount,
          '<=',
          thresholds.maximumActionCount,
          actionCount <= thresholds.maximumActionCount
        ),
        check(
          'maximum-warnings',
          'Warnings',
          warningCount,
          '<=',
          thresholds.maximumWarningCount,
          warningCount <= thresholds.maximumWarningCount
        ),
        check(
          'maximum-final-error',
          'Maximum absolute final error',
          maximumAbsoluteFinalError,
          '<=',
          thresholds.maximumAbsoluteFinalError,
          maximumAbsoluteFinalError
            <= thresholds.maximumAbsoluteFinalError
        ),
        check(
          'maximum-iae',
          'Maximum integral absolute error',
          maximumIntegralAbsoluteError,
          '<=',
          thresholds.maximumIntegralAbsoluteError,
          maximumIntegralAbsoluteError
            <= thresholds.maximumIntegralAbsoluteError
        ),
      ];
    } else if (profileId === 'excursion-disposition') {
      let openActionExcursionCount = 0;
      let undocumentedExcursionCount = 0;

      rows.forEach((row) => {
        const severity = String(
          row.severity || ''
        ).toLowerCase();
        const status = String(
          row.status || ''
        ).toLowerCase();
        const closed = [
          'closed',
          'resolved',
          'accepted',
        ].includes(status);

        if (severity === 'action' && !closed) {
          openActionExcursionCount += 1;
        }

        if (
          !String(row.investigationId || '').trim()
          || !String(row.evidenceLink || '').trim()
        ) {
          undocumentedExcursionCount += 1;
        }
      });

      metrics = {
        excursionCount: rows.length,
        openActionExcursionCount,
        undocumentedExcursionCount,
      };
      checks = [
        check(
          'maximum-open-actions',
          'Open action excursions',
          openActionExcursionCount,
          '<=',
          thresholds.maximumOpenActionExcursions,
          openActionExcursionCount
            <= thresholds.maximumOpenActionExcursions
        ),
        check(
          'maximum-undocumented',
          'Undocumented excursions',
          undocumentedExcursionCount,
          '<=',
          thresholds.maximumUndocumentedExcursions,
          undocumentedExcursionCount
            <= thresholds.maximumUndocumentedExcursions
        ),
      ];
    } else if (profileId === 'hold-time-stability') {
      const points = rows.map((row) => [
        finite(row.time, 'time'),
        finite(row.value, 'value'),
      ]).sort((a, b) => a[0] - b[0]);
      const baseline = points[0][1];

      if (baseline === 0) {
        throw new Error(
          'The initial hold-time value cannot be zero.'
        );
      }

      const signedChangePercent = (
        (points.at(-1)[1] - baseline)
        / baseline
        * 100
      );
      const fit = regression(points);
      const slopePercentPerHour = (
        fit.slope / baseline * 100
      );

      metrics = {
        pointCount: points.length,
        initialValue: baseline,
        finalValue: points.at(-1)[1],
        absoluteChangePercent:
          Math.abs(signedChangePercent),
        signedChangePercent,
        slope: fit.slope,
        slopePercentPerHour,
      };
      checks = [
        check(
          'minimum-points',
          'Hold-time observations',
          points.length,
          '>=',
          thresholds.minimumPoints,
          points.length >= thresholds.minimumPoints
        ),
        check(
          'maximum-change',
          'Absolute hold-time change',
          Math.abs(signedChangePercent),
          '<=',
          thresholds.maximumAbsoluteChangePercent,
          Math.abs(signedChangePercent)
            <= thresholds.maximumAbsoluteChangePercent,
          '%'
        ),
        check(
          'maximum-slope',
          'Absolute hold-time slope',
          Math.abs(slopePercentPerHour),
          '<=',
          thresholds.maximumSlopePercentPerHour,
          Math.abs(slopePercentPerHour)
            <= thresholds.maximumSlopePercentPerHour,
          '%/h'
        ),
      ];
    } else if (profileId === 'release-readiness') {
      let failedCriticalCheckCount = 0;
      let openMajorCheckCount = 0;
      let evidenceCount = 0;

      rows.forEach((row) => {
        const status = String(
          row.status || ''
        ).toLowerCase();
        const category = String(
          row.category || ''
        ).toLowerCase();
        const critical = [
          '1',
          'true',
          'yes',
          'critical',
        ].includes(
          String(row.critical || '').toLowerCase()
        );
        const complete = [
          'pass',
          'passed',
          'closed',
          'complete',
        ].includes(status);

        if (critical && !complete) {
          failedCriticalCheckCount += 1;
        }

        if (category === 'major' && !complete) {
          openMajorCheckCount += 1;
        }

        if (String(row.evidence || '').trim()) {
          evidenceCount += 1;
        }
      });

      const evidenceCoveragePercent = (
        evidenceCount / rows.length * 100
      );

      metrics = {
        checkCount: rows.length,
        failedCriticalCheckCount,
        openMajorCheckCount,
        evidenceCoveragePercent,
      };
      checks = [
        check(
          'maximum-failed-critical',
          'Failed critical checks',
          failedCriticalCheckCount,
          '<=',
          thresholds.maximumFailedCriticalChecks,
          failedCriticalCheckCount
            <= thresholds.maximumFailedCriticalChecks
        ),
        check(
          'maximum-open-major',
          'Open major checks',
          openMajorCheckCount,
          '<=',
          thresholds.maximumOpenMajorChecks,
          openMajorCheckCount
            <= thresholds.maximumOpenMajorChecks
        ),
        check(
          'minimum-evidence-coverage',
          'Evidence coverage',
          evidenceCoveragePercent,
          '>=',
          thresholds.minimumEvidenceCoveragePercent,
          evidenceCoveragePercent
            >= thresholds.minimumEvidenceCoveragePercent,
          '%'
        ),
      ];
    }

    const failed = checks.filter(
      (item) => !item.passed
    );
    const decision = failed.length
      ? 'fail'
      : 'pass';

    return {
      schema:
        'sc-lab-bioprocess-validation-result/1.0',
      version: VERSION,
      profile: {
        id: definition.id,
        label: definition.label,
      },
      thresholds,
      metrics,
      checks,
      decision,
      failedCheckCount: failed.length,
      releaseRecommendation:
        decision === 'pass'
          ? 'release'
          : 'hold',
    };
  }

  function canonicalize(value) {
    if (Array.isArray(value)) {
      return value.map(canonicalize);
    }

    if (
      value
      && typeof value === 'object'
    ) {
      return Object.fromEntries(
        Object.keys(value)
          .sort()
          .map((key) => [
            key,
            canonicalize(value[key]),
          ])
      );
    }

    return value;
  }

  function canonicalJson(value) {
    return JSON.stringify(canonicalize(value));
  }

  function sha256(text) {
    const rightRotate = (value, amount) => (
      (value >>> amount)
      | (value << (32 - amount))
    );
    const maxWord = 2 ** 32;
    const words = [];
    const ascii = unescape(
      encodeURIComponent(String(text))
    );
    const length = ascii.length;
    const hash = sha256.h = sha256.h || [];
    const k = sha256.k = sha256.k || [];
    let primeCounter = k.length;
    const isComposite = {};

    for (
      let candidate = 2;
      primeCounter < 64;
      candidate += 1
    ) {
      if (!isComposite[candidate]) {
        for (
          let multiple = 0;
          multiple < 313;
          multiple += candidate
        ) {
          isComposite[multiple] = candidate;
        }

        hash[primeCounter] = (
          Math.pow(candidate, 0.5) * maxWord
        ) | 0;
        k[primeCounter] = (
          Math.pow(candidate, 1 / 3) * maxWord
        ) | 0;
        primeCounter += 1;
      }
    }

    let message = `${ascii}\x80`;

    while (message.length % 64 !== 56) {
      message += '\x00';
    }

    for (let index = 0; index < message.length; index += 1) {
      words[index >> 2] |= (
        message.charCodeAt(index)
        << ((3 - index) % 4) * 8
      );
    }

    words[words.length] = (
      (length / maxWord) | 0
    );
    words[words.length] = (
      length << 3
    );

    let currentHash = hash.slice(0);

    for (
      let block = 0;
      block < words.length;
      block += 16
    ) {
      const schedule = words.slice(
        block,
        block + 16
      );
      const oldHash = currentHash.slice(0);

      for (let index = 0; index < 64; index += 1) {
        const w15 = schedule[index - 15];
        const w2 = schedule[index - 2];
        const a = currentHash[0];
        const e = currentHash[4];
        const temp1 = (
          currentHash[7]
          + (
            rightRotate(e, 6)
            ^ rightRotate(e, 11)
            ^ rightRotate(e, 25)
          )
          + (
            (e & currentHash[5])
            ^ ((~e) & currentHash[6])
          )
          + k[index]
          + (
            schedule[index] = index < 16
              ? schedule[index]
              : (
                schedule[index - 16]
                + (
                  rightRotate(w15, 7)
                  ^ rightRotate(w15, 18)
                  ^ (w15 >>> 3)
                )
                + schedule[index - 7]
                + (
                  rightRotate(w2, 17)
                  ^ rightRotate(w2, 19)
                  ^ (w2 >>> 10)
                )
              ) | 0
          )
        ) | 0;
        const temp2 = (
          (
            rightRotate(a, 2)
            ^ rightRotate(a, 13)
            ^ rightRotate(a, 22)
          )
          + (
            (a & currentHash[1])
            ^ (a & currentHash[2])
            ^ (
              currentHash[1]
              & currentHash[2]
            )
          )
        ) | 0;

        currentHash = [
          (temp1 + temp2) | 0,
          a,
          currentHash[1],
          currentHash[2],
          (currentHash[3] + temp1) | 0,
          e,
          currentHash[5],
          currentHash[6],
        ];
      }

      currentHash = currentHash.map(
        (value, index) => (
          (value + oldHash[index]) | 0
        )
      );
    }

    return currentHash
      .map((value) => (
        (value >>> 0)
          .toString(16)
          .padStart(8, '0')
      ))
      .join('');
  }

  function fingerprint(value) {
    return sha256(canonicalJson(value));
  }

  function randomHex(length = 10) {
    const bytes = new Uint8Array(
      Math.ceil(length / 2)
    );

    if (W.crypto?.getRandomValues) {
      W.crypto.getRandomValues(bytes);
    } else {
      bytes.forEach((_, index) => {
        bytes[index] = Math.floor(
          Math.random() * 256
        );
      });
    }

    return Array.from(bytes)
      .map(
        (value) => value
          .toString(16)
          .padStart(2, '0')
      )
      .join('')
      .slice(0, length);
  }

  function createRecord(
    payload,
    metadata = {},
    previousHash = null
  ) {
    const eventType = (
      metadata.eventType
      || 'validation-decision'
    );

    if (!eventTypes.includes(eventType)) {
      throw new Error(
        `Unknown provenance event type: ${eventType}`
      );
    }

    const timestamp = (
      metadata.timestamp
      || new Date().toISOString()
    );
    const record = {
      schema:
        'sc-lab-bioprocess-batch-provenance/1.0',
      version: VERSION,
      recordId: (
        metadata.recordId
        || `scbatch-${timestamp.replace(/\D/g, '').slice(0, 14)}-${randomHex()}`
      ),
      eventType,
      timestamp,
      batchId: metadata.batchId || null,
      lotId: metadata.lotId || null,
      runId: metadata.runId || null,
      profileId: metadata.profileId || null,
      analyst: metadata.analyst || null,
      reviewer: metadata.reviewer || null,
      organization:
        metadata.organization
        || 'Sustainable Catalyst',
      instrument: metadata.instrument || null,
      sourceRecordIds:
        metadata.sourceRecordIds || [],
      evidenceLinks:
        metadata.evidenceLinks || [],
      disposition:
        metadata.disposition
        || 'research-review',
      notes: metadata.notes || null,
      previousHash,
      payloadHash: fingerprint(payload),
      payload,
      engine: {
        validationRelease: VERSION,
        bioprocessEngineVersion: '0.22.0',
        productionReliabilityVersion: '0.22.1',
        monitoringControlVersion: '0.22.2',
      },
    };

    record.recordHash = fingerprint(record);
    return record;
  }

  function verifyLedger(records) {
    let previousHash = null;
    const results = records.map((record) => {
      const copy = { ...record };
      const storedHash = String(
        copy.recordHash || ''
      );

      delete copy.recordHash;

      const calculatedHash = fingerprint(copy);
      const payloadValid = (
        record.payloadHash
        === fingerprint(record.payload)
      );
      const hashValid = (
        storedHash === calculatedHash
      );
      const chainValid = (
        record.previousHash === previousHash
      );

      previousHash = storedHash;

      return {
        recordId: record.recordId,
        payloadValid,
        hashValid,
        chainValid,
        valid:
          payloadValid
          && hashValid
          && chainValid,
        storedHash,
        calculatedHash,
      };
    });

    return {
      schema:
        'sc-lab-bioprocess-ledger-verification/1.0',
      version: VERSION,
      valid: results.every(
        (result) => result.valid
      ),
      recordCount: records.length,
      results,
    };
  }

  function createDossier(
    validationResults,
    batch = {},
    records = [],
    disposition = null
  ) {
    const failed = validationResults.filter(
      (result) => result.decision !== 'pass'
    );
    const ledgerVerification = verifyLedger(records);
    const resolvedDisposition = (
      disposition
      || (
        failed.length
        || !ledgerVerification.valid
          ? 'hold'
          : 'release'
      )
    );
    const dossier = {
      schema:
        'sc-lab-bioprocess-validation-dossier/1.0',
      version: VERSION,
      createdAt: new Date().toISOString(),
      batch,
      summary: {
        validationResultCount:
          validationResults.length,
        failedValidationCount: failed.length,
        recordCount: records.length,
        ledgerValid: ledgerVerification.valid,
        disposition: resolvedDisposition,
        releaseReady:
          !failed.length
          && ledgerVerification.valid
          && resolvedDisposition === 'release',
      },
      validationResults,
      provenanceLedger: records,
      ledgerVerification,
      responsibleUse: {
        scope:
          'Research, education, process development, and quality-system prototyping.',
        boundary:
          'Not a substitute for validated manufacturing systems, regulatory review, qualified personnel, or formal batch release authority.',
      },
    };

    dossier.dossierHash = fingerprint(dossier);
    return dossier;
  }

  function downloadJson(name, value) {
    if (
      typeof document === 'undefined'
      || typeof Blob === 'undefined'
    ) {
      return false;
    }

    const blob = new Blob(
      [JSON.stringify(value, null, 2)],
      { type: 'application/json' }
    );
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = url;
    link.download = name;
    link.click();
    URL.revokeObjectURL(url);
    return true;
  }

  function render() {
    if (typeof document === 'undefined') {
      return false;
    }

    const roots = Array.from(
      document.querySelectorAll(ROOT_SELECTOR)
    );

    if (!roots.length) {
      return false;
    }

    const root = roots[0];

    roots.slice(1).forEach(
      (duplicate) => duplicate.remove()
    );

    if (
      root.dataset.scBpvVersion === VERSION
      && root.querySelector('.sc-bpv-shell')
    ) {
      state.rendered = true;
      return true;
    }

    root.innerHTML = `
      <section class="sc-bpv-shell">
        <header class="sc-bpv-header">
          <p class="sc-bpv-kicker">
            LAB/BIOPROCESS/VALIDATION
          </p>
          <h3>
            Bioprocess Validation and Batch Provenance
          </h3>
          <p>
            Evaluate batch evidence, record validation
            decisions, verify hash-linked provenance, and
            export release-readiness dossiers.
          </p>
          <div class="sc-bpv-status">
            <span>8 validation profiles</span>
            <span>5 provenance event types</span>
            <span>SHA-256 ledger verification</span>
          </div>
        </header>

        <div class="sc-bpv-grid">
          <section class="sc-bpv-card">
            <h4>Validation profile</h4>
            <label>
              Profile
              <select data-bpv-profile>
                ${profiles.map(
                  (item) => `
                    <option value="${item.id}">
                      ${item.label}
                    </option>
                  `
                ).join('')}
              </select>
            </label>
            <label>
              CSV evidence
              <textarea
                data-bpv-csv
                rows="12"
                spellcheck="false"
              ></textarea>
            </label>
            <div class="sc-bpv-actions">
              <button
                type="button"
                data-bpv-run
              >
                Run validation
              </button>
              <button
                type="button"
                data-bpv-load
              >
                Load sample
              </button>
            </div>
          </section>

          <section class="sc-bpv-card">
            <h4>Batch provenance</h4>
            <div class="sc-bpv-fields">
              <label>
                Batch ID
                <input
                  data-bpv-batch
                  value="B-001"
                />
              </label>
              <label>
                Analyst
                <input
                  data-bpv-analyst
                  value=""
                />
              </label>
              <label>
                Disposition
                <select data-bpv-disposition>
                  <option value="research-review">
                    Research review
                  </option>
                  <option value="release">Release</option>
                  <option value="conditional-release">
                    Conditional release
                  </option>
                  <option value="hold">Hold</option>
                  <option value="reject">Reject</option>
                </select>
              </label>
            </div>
            <div class="sc-bpv-actions">
              <button
                type="button"
                data-bpv-record
              >
                Add validation record
              </button>
              <button
                type="button"
                data-bpv-verify
              >
                Verify ledger
              </button>
              <button
                type="button"
                data-bpv-dossier
              >
                Build dossier
              </button>
            </div>
          </section>
        </div>

        <section class="sc-bpv-card">
          <div class="sc-bpv-output-header">
            <h4>Decision and integrity output</h4>
            <button
              type="button"
              data-bpv-export
            >
              Export current JSON
            </button>
          </div>
          <pre data-bpv-output aria-live="polite">
Load a sample and run a validation profile.
          </pre>
        </section>

        <p class="sc-bpv-boundary">
          Research and process-development support only.
          This workspace does not replace a validated
          manufacturing system, formal quality review,
          regulatory requirements, or authorized batch
          disposition.
        </p>
      </section>
    `;

    const profileSelect = root.querySelector(
      '[data-bpv-profile]'
    );
    const csv = root.querySelector('[data-bpv-csv]');
    const output = root.querySelector(
      '[data-bpv-output]'
    );
    const batch = root.querySelector(
      '[data-bpv-batch]'
    );
    const analyst = root.querySelector(
      '[data-bpv-analyst]'
    );
    const disposition = root.querySelector(
      '[data-bpv-disposition]'
    );

    function selectedProfile() {
      return profile(profileSelect.value);
    }

    function show(value) {
      output.textContent = JSON.stringify(
        value,
        null,
        2
      );
    }

    function loadSample() {
      csv.value = selectedProfile().sample;
    }

    profileSelect.addEventListener(
      'change',
      loadSample
    );

    root.querySelector(
      '[data-bpv-load]'
    ).addEventListener(
      'click',
      loadSample
    );

    root.querySelector(
      '[data-bpv-run]'
    ).addEventListener(
      'click',
      () => {
        try {
          state.lastResult = evaluate(
            profileSelect.value,
            parseCsv(csv.value)
          );
          state.lastError = null;
          show(state.lastResult);
        } catch (error) {
          state.lastError = String(
            error?.message || error
          );
          show({
            error: state.lastError,
          });
        }
      }
    );

    root.querySelector(
      '[data-bpv-record]'
    ).addEventListener(
      'click',
      () => {
        try {
          if (!state.lastResult) {
            throw new Error(
              'Run a validation profile first.'
            );
          }

          const previousHash = (
            state.ledger.at(-1)?.recordHash
            || null
          );
          const record = createRecord(
            state.lastResult,
            {
              eventType: 'validation-decision',
              batchId: batch.value,
              analyst: analyst.value || null,
              profileId:
                state.lastResult.profile.id,
              disposition: disposition.value,
            },
            previousHash
          );

          state.ledger.push(record);
          state.lastError = null;
          show({
            record,
            ledgerLength: state.ledger.length,
          });
        } catch (error) {
          state.lastError = String(
            error?.message || error
          );
          show({
            error: state.lastError,
          });
        }
      }
    );

    root.querySelector(
      '[data-bpv-verify]'
    ).addEventListener(
      'click',
      () => show(
        verifyLedger(state.ledger)
      )
    );

    root.querySelector(
      '[data-bpv-dossier]'
    ).addEventListener(
      'click',
      () => {
        state.lastDossier = createDossier(
          state.lastResult
            ? [state.lastResult]
            : [],
          {
            batchId: batch.value,
            analyst: analyst.value || null,
          },
          state.ledger,
          disposition.value
        );
        show(state.lastDossier);
      }
    );

    root.querySelector(
      '[data-bpv-export]'
    ).addEventListener(
      'click',
      () => {
        const value = (
          state.lastDossier
          || state.ledger.at(-1)
          || state.lastResult
          || {
            version: VERSION,
            profiles,
          }
        );

        downloadJson(
          `sc-lab-bioprocess-validation-${Date.now()}.json`,
          value
        );
      }
    );

    loadSample();
    root.dataset.scBpvVersion = VERSION;
    state.rendered = true;
    state.lastError = null;
    return true;
  }

  function init() {
    const attempts = [0, 100, 300, 800, 1800];

    attempts.forEach((delay) => {
      W.setTimeout(render, delay);
    });

    if (
      typeof MutationObserver !== 'undefined'
      && typeof document !== 'undefined'
    ) {
      const observer = new MutationObserver(
        () => render()
      );

      observer.observe(
        document.documentElement,
        {
          childList: true,
          subtree: true,
        }
      );
    }
  }

  function status() {
    const root = typeof document === 'undefined'
      ? null
      : document.querySelector(ROOT_SELECTOR);

    return {
      version: VERSION,
      profileCount: profiles.length,
      eventTypeCount: eventTypes.length,
      rootFound: Boolean(root),
      rendered: Boolean(
        root?.querySelector('.sc-bpv-shell')
      ),
      ledgerRecordCount: state.ledger.length,
      lastDecision:
        state.lastResult?.decision || null,
      lastError: state.lastError,
    };
  }

  Lab.BioprocessValidationProvenance = {
    VERSION,
    profiles,
    eventTypes,
    parseCsv,
    evaluate,
    canonicalJson,
    fingerprint,
    createRecord,
    verifyLedger,
    createDossier,
    render,
    init,
    status,
    state,
  };

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener(
        'DOMContentLoaded',
        init,
        { once: true }
      );
    } else {
      init();
    }
  }
})();
