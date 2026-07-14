(() => {
  'use strict';

  const W = typeof window !== 'undefined' ? window : globalThis;
  const Lab = W.SCLab = W.SCLab || {};
  const VERSION = '0.25.3';
  const ENGINE_VERSION = '0.25.0';
  const PRODUCTION_VERSION = '0.25.1';
  const LIVE_VERSION = '0.25.2';
  const ROOT_SELECTOR =
    '[data-instrumentation-validation-custody-root]';
  const CONTRACT = {"schema":"sc-lab-instrumentation-validation-custody-contract/1.0","version":"0.25.3","title":"Calibration, Validation, and Chain of Custody","preservedInstrumentation":{"version":"0.25.0","methodCount":48,"benchmarkCount":48,"categoryCount":8,"recordTypeCount":9,"connectionProfileCount":8,"qualityFlagCount":8},"productionLayer":{"version":"0.25.1"},"liveLayer":{"version":"0.25.2","modeCount":8,"analysisMethodCount":16,"benchmarkCount":16},"validationProfiles":[{"id":"instrument-identity","label":"Instrument identity and configuration"},{"id":"calibration-acceptance","label":"Calibration acceptance"},{"id":"sensor-channel-readiness","label":"Sensor and channel readiness"},{"id":"maintenance-readiness","label":"Maintenance readiness"},{"id":"measurement-quality","label":"Measurement quality"},{"id":"sample-specimen-linkage","label":"Sample and specimen linkage"},{"id":"custody-chain-integrity","label":"Chain-of-custody integrity"},{"id":"release-readiness","label":"Laboratory release readiness"}],"acceptanceStates":["draft","pending-review","accepted","conditionally-accepted","hold","rejected","expired","superseded"],"provenanceEventTypes":["instrument-registration","calibration","verification","maintenance","sample-transfer","measurement-ingest","validation-decision","dossier-export"],"deviationTypes":["calibration-out-of-tolerance","maintenance-overdue","missing-identifier","quality-flag-excursion","custody-break","timestamp-order","reference-mismatch","review-incomplete"],"analysisMethods":[{"id":"calibration-absolute-error","operation":"calibration_absolute_error"},{"id":"calibration-percent-error","operation":"calibration_percent_error"},{"id":"calibration-bias","operation":"calibration_bias"},{"id":"calibration-rmse","operation":"calibration_rmse"},{"id":"calibration-linearity-r2","operation":"calibration_linearity_r2"},{"id":"repeatability-cv","operation":"repeatability_cv"},{"id":"acceptance-window-status","operation":"acceptance_window_status"},{"id":"calibration-due-state","operation":"calibration_due_state"},{"id":"maintenance-due-state","operation":"maintenance_due_state"},{"id":"measurement-completeness","operation":"measurement_completeness"},{"id":"quality-flag-rate","operation":"quality_flag_rate"},{"id":"custody-completeness","operation":"custody_completeness"},{"id":"custody-sequence-status","operation":"custody_sequence_status"},{"id":"deviation-rate","operation":"deviation_rate"},{"id":"validation-score","operation":"validation_score"},{"id":"validation-disposition","operation":"validation_disposition"}],"benchmarks":[{"id":"benchmark-calibration-absolute-error","methodId":"calibration-absolute-error","inputs":{"measured":10.4,"reference":10.0},"expected":0.40000000000000036},{"id":"benchmark-calibration-percent-error","methodId":"calibration-percent-error","inputs":{"measured":10.4,"reference":10.0},"expected":4.0000000000000036},{"id":"benchmark-calibration-bias","methodId":"calibration-bias","inputs":{"measuredValues":[10.1,9.9,10.2],"referenceValues":[10,10,10]},"expected":0.06666666666666643},{"id":"benchmark-calibration-rmse","methodId":"calibration-rmse","inputs":{"measuredValues":[10.1,9.9,10.2],"referenceValues":[10,10,10]},"expected":0.141421356237309},{"id":"benchmark-calibration-linearity-r2","methodId":"calibration-linearity-r2","inputs":{"referenceValues":[0,1,2,3],"measuredValues":[0.1,1.1,2.1,3.1]},"expected":1.0},{"id":"benchmark-repeatability-cv","methodId":"repeatability-cv","inputs":{"values":[9.9,10.0,10.1,10.0]},"expected":0.8164965809277231},{"id":"benchmark-acceptance-window-status","methodId":"acceptance-window-status","inputs":{"value":10.2,"target":10,"warningTolerance":0.3,"actionTolerance":0.5},"expected":"accepted"},{"id":"benchmark-calibration-due-state","methodId":"calibration-due-state","inputs":{"daysSinceCalibration":28,"calibrationIntervalDays":30,"warningLeadDays":5},"expected":"due-soon"},{"id":"benchmark-maintenance-due-state","methodId":"maintenance-due-state","inputs":{"daysSinceMaintenance":95,"maintenanceIntervalDays":90,"warningLeadDays":10},"expected":"overdue"},{"id":"benchmark-measurement-completeness","methodId":"measurement-completeness","inputs":{"presentCount":97,"expectedCount":100},"expected":97.0},{"id":"benchmark-quality-flag-rate","methodId":"quality-flag-rate","inputs":{"flaggedCount":4,"totalCount":100},"expected":4.0},{"id":"benchmark-custody-completeness","methodId":"custody-completeness","inputs":{"completeEventCount":9,"totalEventCount":10},"expected":90.0},{"id":"benchmark-custody-sequence-status","methodId":"custody-sequence-status","inputs":{"events":[{"timestamp":1,"eventHash":"a","previousHash":""},{"timestamp":2,"eventHash":"b","previousHash":"a"},{"timestamp":3,"eventHash":"c","previousHash":"b"}]},"expected":{"valid":true,"eventCount":3,"problems":[],"headHash":"c"}},{"id":"benchmark-deviation-rate","methodId":"deviation-rate","inputs":{"deviationCount":3,"reviewedItemCount":120},"expected":2.5},{"id":"benchmark-validation-score","methodId":"validation-score","inputs":{"profileScores":{"instrument-identity":100,"calibration-acceptance":95,"sensor-channel-readiness":90,"maintenance-readiness":80,"measurement-quality":92,"sample-specimen-linkage":100,"custody-chain-integrity":100,"release-readiness":90},"weights":{"instrument-identity":1,"calibration-acceptance":2,"sensor-channel-readiness":1,"maintenance-readiness":1,"measurement-quality":2,"sample-specimen-linkage":1,"custody-chain-integrity":2,"release-readiness":2}},"expected":93.66666666666667},{"id":"benchmark-validation-disposition","methodId":"validation-disposition","inputs":{"score":91,"criticalFailureCount":0,"openDeviationCount":1,"expiredRecordCount":0},"expected":"conditionally-accepted"}],"responsibleUse":{"scope":"Research, education, laboratory prototyping, internal validation, and auditable sample-history workflows.","boundaries":{"gmpCertification":false,"clinicalReleaseAuthority":false,"regulatoryApproval":false,"automaticDeviceControl":false,"tamperEvidence":true}}};

  const state = {
    profileResults: {},
    manifest: null,
    custodyEvents: [],
    deviations: [],
    dossier: null,
    lastError: null,
    rendered: false,
  };

  function finite(value, label) {
    const number = Number(value);
    if (!Number.isFinite(number)) {
      throw new Error(`${label} must be numerical and finite.`);
    }
    return number;
  }

  function positive(value, label) {
    const number = finite(value, label);
    if (number <= 0) {
      throw new Error(`${label} must be greater than zero.`);
    }
    return number;
  }

  function numbers(value, label, minimum = 1) {
    if (!Array.isArray(value) || value.length < minimum) {
      throw new Error(
        `${label} must contain at least ${minimum} values.`
      );
    }
    return value.map(
      (item, index) => finite(item, `${label}[${index}]`)
    );
  }

  function paired(left, right) {
    const measured = numbers(left, 'measuredValues');
    const reference = numbers(right, 'referenceValues');
    if (measured.length !== reference.length) {
      throw new Error(
        'measuredValues and referenceValues must have equal length.'
      );
    }
    return [measured, reference];
  }

  const mean = (values) => (
    values.reduce((sum, value) => sum + value, 0)
    / values.length
  );

  function standardDeviation(values) {
    if (values.length < 2) {
      return 0;
    }
    const average = mean(values);
    return Math.sqrt(
      values.reduce(
        (sum, value) => sum + (value - average) ** 2,
        0
      ) / (values.length - 1)
    );
  }

  function calibrationAbsoluteError(measured, reference) {
    return Math.abs(
      finite(measured, 'measured')
      - finite(reference, 'reference')
    );
  }

  function calibrationPercentError(measured, reference) {
    return calibrationAbsoluteError(measured, reference)
      / Math.abs(positive(reference, 'reference'))
      * 100;
  }

  function calibrationBias(measuredValues, referenceValues) {
    const [measured, reference] = paired(
      measuredValues,
      referenceValues
    );
    return mean(
      measured.map(
        (value, index) => value - reference[index]
      )
    );
  }

  function calibrationRmse(measuredValues, referenceValues) {
    const [measured, reference] = paired(
      measuredValues,
      referenceValues
    );
    return Math.sqrt(
      mean(
        measured.map(
          (value, index) => (
            value - reference[index]
          ) ** 2
        )
      )
    );
  }

  function calibrationLinearityR2(
    referenceValues,
    measuredValues
  ) {
    const [reference, measured] = paired(
      referenceValues,
      measuredValues
    );
    const xMean = mean(reference);
    const yMean = mean(measured);
    let numerator = 0;
    let xSquare = 0;
    let ySquare = 0;

    reference.forEach((xValue, index) => {
      const xDelta = xValue - xMean;
      const yDelta = measured[index] - yMean;
      numerator += xDelta * yDelta;
      xSquare += xDelta * xDelta;
      ySquare += yDelta * yDelta;
    });

    if (xSquare === 0 || ySquare === 0) {
      throw new Error(
        'Linearity requires non-constant measured and reference values.'
      );
    }

    const correlation = numerator / Math.sqrt(
      xSquare * ySquare
    );

    return correlation * correlation;
  }

  function repeatabilityCv(rawValues) {
    const values = numbers(rawValues, 'values', 2);
    const average = mean(values);
    if (average === 0) {
      throw new Error(
        'repeatability CV requires a non-zero mean.'
      );
    }
    return standardDeviation(values)
      / Math.abs(average)
      * 100;
  }

  function acceptanceWindowStatus(
    value,
    target,
    warningTolerance,
    actionTolerance
  ) {
    const delta = Math.abs(
      finite(value, 'value')
      - finite(target, 'target')
    );
    const warning = positive(
      warningTolerance,
      'warningTolerance'
    );
    const action = positive(
      actionTolerance,
      'actionTolerance'
    );
    if (action < warning) {
      throw new Error(
        'actionTolerance must be at least warningTolerance.'
      );
    }
    if (delta > action) {
      return 'action';
    }
    if (delta > warning) {
      return 'warning';
    }
    return 'accepted';
  }

  function dueState(elapsed, interval, warningLead) {
    const days = finite(elapsed, 'elapsedDays');
    const limit = positive(interval, 'intervalDays');
    const lead = Math.max(
      0,
      finite(warningLead, 'warningLeadDays')
    );
    if (days > limit) {
      return 'overdue';
    }
    if (days >= Math.max(0, limit - lead)) {
      return 'due-soon';
    }
    return 'current';
  }

  function measurementCompleteness(
    presentCount,
    expectedCount
  ) {
    return Math.max(
      0,
      Math.min(
        100,
        finite(presentCount, 'presentCount')
        / positive(expectedCount, 'expectedCount')
        * 100
      )
    );
  }

  function qualityFlagRate(flaggedCount, totalCount) {
    return Math.max(
      0,
      Math.min(
        100,
        finite(flaggedCount, 'flaggedCount')
        / positive(totalCount, 'totalCount')
        * 100
      )
    );
  }

  function custodyCompleteness(
    completeEventCount,
    totalEventCount
  ) {
    return measurementCompleteness(
      completeEventCount,
      totalEventCount
    );
  }

  function custodySequenceStatus(events) {
    if (!Array.isArray(events)) {
      throw new Error('events must be an array.');
    }
    let previousHash = '';
    let previousTimestamp = null;
    const problems = [];

    events.forEach((event, index) => {
      if (!event || typeof event !== 'object') {
        problems.push(`event-${index + 1}-not-object`);
        return;
      }
      const timestamp = finite(
        event.timestamp,
        `events[${index}].timestamp`
      );
      if (
        previousTimestamp !== null
        && timestamp < previousTimestamp
      ) {
        problems.push(
          `event-${index + 1}-timestamp-order`
        );
      }
      if (
        String(event.previousHash || '')
        !== previousHash
      ) {
        problems.push(
          `event-${index + 1}-parent-hash`
        );
      }
      const eventHash = String(event.eventHash || '');
      if (!eventHash) {
        problems.push(
          `event-${index + 1}-missing-hash`
        );
      }
      previousHash = eventHash;
      previousTimestamp = timestamp;
    });

    return {
      valid: problems.length === 0,
      eventCount: events.length,
      problems,
      headHash: previousHash,
    };
  }

  function deviationRate(
    deviationCount,
    reviewedItemCount
  ) {
    return finite(deviationCount, 'deviationCount')
      / positive(
        reviewedItemCount,
        'reviewedItemCount'
      )
      * 100;
  }

  function validationScore(profileScores, weights = {}) {
    if (
      !profileScores
      || typeof profileScores !== 'object'
      || Array.isArray(profileScores)
      || !Object.keys(profileScores).length
    ) {
      throw new Error(
        'profileScores must be a non-empty object.'
      );
    }

    let numerator = 0;
    let denominator = 0;

    Object.entries(profileScores).forEach(
      ([profileId, rawScore]) => {
        const score = Math.max(
          0,
          Math.min(
            100,
            finite(rawScore, profileId)
          )
        );
        const weight = Math.max(
          0,
          finite(
            weights?.[profileId] ?? 1,
            `weight:${profileId}`
          )
        );
        numerator += score * weight;
        denominator += weight;
      }
    );

    if (denominator === 0) {
      throw new Error(
        'At least one validation weight must be positive.'
      );
    }

    return numerator / denominator;
  }

  function validationDisposition(
    score,
    criticalFailureCount,
    openDeviationCount,
    expiredRecordCount
  ) {
    const value = finite(score, 'score');
    const critical = Math.trunc(
      finite(
        criticalFailureCount,
        'criticalFailureCount'
      )
    );
    const deviations = Math.trunc(
      finite(
        openDeviationCount,
        'openDeviationCount'
      )
    );
    const expired = Math.trunc(
      finite(
        expiredRecordCount,
        'expiredRecordCount'
      )
    );

    if (critical > 0) {
      return 'rejected';
    }
    if (expired > 0 || value < 70) {
      return 'hold';
    }
    if (value < 85 || deviations > 0) {
      return 'conditionally-accepted';
    }
    return 'accepted';
  }

  function execute(methodId, inputs = {}) {
    const i = inputs || {};
    const dispatch = {
      'calibration-absolute-error': () => (
        calibrationAbsoluteError(
          i.measured,
          i.reference
        )
      ),
      'calibration-percent-error': () => (
        calibrationPercentError(
          i.measured,
          i.reference
        )
      ),
      'calibration-bias': () => (
        calibrationBias(
          i.measuredValues,
          i.referenceValues
        )
      ),
      'calibration-rmse': () => (
        calibrationRmse(
          i.measuredValues,
          i.referenceValues
        )
      ),
      'calibration-linearity-r2': () => (
        calibrationLinearityR2(
          i.referenceValues,
          i.measuredValues
        )
      ),
      'repeatability-cv': () => (
        repeatabilityCv(i.values)
      ),
      'acceptance-window-status': () => (
        acceptanceWindowStatus(
          i.value,
          i.target,
          i.warningTolerance,
          i.actionTolerance
        )
      ),
      'calibration-due-state': () => (
        dueState(
          i.daysSinceCalibration,
          i.calibrationIntervalDays,
          i.warningLeadDays
        )
      ),
      'maintenance-due-state': () => (
        dueState(
          i.daysSinceMaintenance,
          i.maintenanceIntervalDays,
          i.warningLeadDays
        )
      ),
      'measurement-completeness': () => (
        measurementCompleteness(
          i.presentCount,
          i.expectedCount
        )
      ),
      'quality-flag-rate': () => (
        qualityFlagRate(
          i.flaggedCount,
          i.totalCount
        )
      ),
      'custody-completeness': () => (
        custodyCompleteness(
          i.completeEventCount,
          i.totalEventCount
        )
      ),
      'custody-sequence-status': () => (
        custodySequenceStatus(i.events)
      ),
      'deviation-rate': () => (
        deviationRate(
          i.deviationCount,
          i.reviewedItemCount
        )
      ),
      'validation-score': () => (
        validationScore(
          i.profileScores,
          i.weights
        )
      ),
      'validation-disposition': () => (
        validationDisposition(
          i.score,
          i.criticalFailureCount,
          i.openDeviationCount,
          i.expiredRecordCount
        )
      ),
    };

    if (!dispatch[methodId]) {
      throw new Error(
        `Unknown instrumentation validation method: ${methodId}`
      );
    }

    return {
      schema:
        'sc-lab-instrumentation-validation-result/1.0',
      version: VERSION,
      methodId,
      inputs,
      value: dispatch[methodId](),
    };
  }

  function canonicalJson(value) {
    if (
      value === null
      || typeof value !== 'object'
    ) {
      return JSON.stringify(value);
    }

    if (Array.isArray(value)) {
      return `[${value.map(canonicalJson).join(',')}]`;
    }

    return `{${
      Object.keys(value)
        .sort()
        .map(
          (key) => (
            `${JSON.stringify(key)}:${canonicalJson(value[key])}`
          )
        )
        .join(',')
    }}`;
  }

  async function sha256Text(value) {
    const input = String(value);

    if (
      typeof globalThis.crypto !== 'undefined'
      && globalThis.crypto?.subtle
      && typeof TextEncoder !== 'undefined'
    ) {
      const encoded = new TextEncoder().encode(input);
      const digest = await globalThis.crypto.subtle.digest(
        'SHA-256',
        encoded
      );
      return Array.from(new Uint8Array(digest))
        .map((byte) => byte.toString(16).padStart(2, '0'))
        .join('');
    }

    if (typeof require === 'function') {
      return require('node:crypto')
        .createHash('sha256')
        .update(input, 'utf8')
        .digest('hex');
    }

    throw new Error(
      'A SHA-256 implementation is unavailable.'
    );
  }

  async function createManifest(
    components,
    metadata = {}
  ) {
    if (
      !components
      || typeof components !== 'object'
      || Array.isArray(components)
      || !Object.keys(components).length
    ) {
      throw new Error(
        'components must be a non-empty object.'
      );
    }

    const componentHashes = {};

    for (
      const key
      of Object.keys(components).sort()
    ) {
      componentHashes[key] = await sha256Text(
        canonicalJson(components[key])
      );
    }

    const manifest = {
      schema:
        'sc-lab-instrumentation-validation-manifest/1.0',
      version: VERSION,
      components,
      componentHashes,
      metadata,
    };

    manifest.manifestHash = await sha256Text(
      canonicalJson(manifest)
    );

    return manifest;
  }

  async function createCustodyEvent({
    sampleId,
    action,
    actor,
    location,
    timestamp,
    previousHash = '',
    metadata = {},
  }) {
    const event = {
      schema:
        'sc-lab-instrumentation-custody-event/1.0',
      version: VERSION,
      sampleId: String(sampleId || ''),
      action: String(action || ''),
      actor: String(actor || ''),
      location: String(location || ''),
      timestamp: finite(timestamp, 'timestamp'),
      previousHash: String(previousHash || ''),
      metadata,
    };

    event.eventHash = await sha256Text(
      canonicalJson(event)
    );

    return event;
  }

  async function verifyCustodyChain(events) {
    if (!Array.isArray(events)) {
      throw new Error('events must be an array.');
    }

    let previousHash = '';
    const problems = [];

    for (
      let index = 0;
      index < events.length;
      index += 1
    ) {
      const event = events[index];

      if (!event || typeof event !== 'object') {
        problems.push(
          `event-${index + 1}-not-object`
        );
        continue;
      }

      const storedHash = String(
        event.eventHash || ''
      );
      const payload = { ...event };
      delete payload.eventHash;

      const calculatedHash = await sha256Text(
        canonicalJson(payload)
      );

      if (storedHash !== calculatedHash) {
        problems.push(
          `event-${index + 1}-hash`
        );
      }

      if (
        String(event.previousHash || '')
        !== previousHash
      ) {
        problems.push(
          `event-${index + 1}-chain`
        );
      }

      previousHash = storedHash;
    }

    return {
      valid: problems.length === 0,
      eventCount: events.length,
      headHash: previousHash,
      problems,
    };
  }

  async function createDossier({
    profileResults,
    manifest,
    custodyEvents = [],
    deviations = [],
    metadata = {},
  }) {
    const scores = Object.fromEntries(
      Object.entries(profileResults || {})
        .map(
          ([profileId, result]) => [
            profileId,
            Number(result?.score || 0),
          ]
        )
    );

    const score = validationScore(scores, {});
    const criticalFailureCount = Object.values(
      profileResults || {}
    ).filter(
      (result) => result?.criticalFailure
    ).length;
    const expiredRecordCount = Object.values(
      profileResults || {}
    ).filter(
      (result) => result?.expired
    ).length;
    const openDeviationCount = deviations.filter(
      (deviation) => !deviation?.closed
    ).length;
    const disposition = validationDisposition(
      score,
      criticalFailureCount,
      openDeviationCount,
      expiredRecordCount
    );
    const custodyVerification = await verifyCustodyChain(
      custodyEvents
    );

    const dossier = {
      schema:
        'sc-lab-instrumentation-validation-dossier/1.0',
      version: VERSION,
      profileResults,
      validationScore: score,
      disposition,
      manifest,
      custodyVerification,
      deviations,
      metadata,
    };

    dossier.dossierHash = await sha256Text(
      canonicalJson(dossier)
    );

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

  function dispatchHandoff(eventName, record) {
    if (typeof document === 'undefined') {
      return false;
    }
    document.dispatchEvent(
      new CustomEvent(
        eventName,
        {
          detail: {
            source:
              'instrumentation-validation-custody',
            version: VERSION,
            record,
          },
        }
      )
    );
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
      root.dataset.scInstrumentationValidationVersion
        === VERSION
      && root.querySelector('.sc-validation-shell')
    ) {
      state.rendered = true;
      return true;
    }

    root.innerHTML = `
      <section class="sc-validation-shell">
        <header class="sc-validation-header">
          <p class="sc-validation-kicker">
            LAB/INSTRUMENTATION/VALIDATION
          </p>
          <h3>
            Calibration, Validation, and Chain of Custody
          </h3>
          <p>
            Evaluate calibration and readiness, build
            component-hashed manifests, maintain immutable sample
            histories, verify custody continuity, review
            deviations, and export a validation dossier.
          </p>
          <div class="sc-validation-status">
            <span>8 validation profiles</span>
            <span>16 deterministic methods</span>
            <span>8 acceptance states</span>
            <span>SHA-256 custody ledger</span>
          </div>
        </header>

        <div class="sc-validation-grid">
          <section class="sc-validation-card">
            <h4>Validation profiles</h4>
            <div data-validation-profiles></div>
            <button
              type="button"
              data-validation-evaluate
            >
              Evaluate profiles
            </button>
          </section>

          <section class="sc-validation-card">
            <h4>Component manifest</h4>
            <textarea
              rows="12"
              data-validation-components
            >{
  "instrument": {
    "id": "INST-001",
    "model": "SC-100",
    "status": "active"
  },
  "calibration": {
    "status": "accepted",
    "completedAt": "2026-07-14"
  },
  "sample": {
    "id": "SAMPLE-001",
    "type": "research"
  }
}</textarea>
            <button
              type="button"
              data-validation-manifest
            >
              Create SHA-256 manifest
            </button>
          </section>

          <section class="sc-validation-card">
            <h4>Custody event</h4>
            <label>
              Sample or specimen ID
              <input
                value="SAMPLE-001"
                data-custody-sample
              >
            </label>
            <label>
              Action
              <input
                value="received"
                data-custody-action
              >
            </label>
            <label>
              Actor
              <input
                value="analyst-a"
                data-custody-actor
              >
            </label>
            <label>
              Location
              <input
                value="intake"
                data-custody-location
              >
            </label>
            <button
              type="button"
              data-custody-add
            >
              Add custody event
            </button>
            <button
              type="button"
              data-custody-verify
            >
              Verify custody chain
            </button>
          </section>

          <section class="sc-validation-card">
            <h4>Deviation review</h4>
            <select data-deviation-type>
              ${CONTRACT.deviationTypes.map(
                (type) => `
                  <option value="${type}">
                    ${type.replaceAll('-', ' ')}
                  </option>
                `
              ).join('')}
            </select>
            <textarea
              rows="5"
              data-deviation-notes
            >Document the deviation, evidence, review status, and corrective action.</textarea>
            <button
              type="button"
              data-deviation-add
            >
              Add open deviation
            </button>
          </section>

          <section class="sc-validation-card sc-validation-card-wide">
            <h4>Validation dossier</h4>
            <div class="sc-validation-actions">
              <button
                type="button"
                data-dossier-create
              >
                Create dossier
              </button>
              <button
                type="button"
                data-dossier-export
              >
                Export dossier JSON
              </button>
              <button
                type="button"
                data-dossier-project
              >
                Send to project
              </button>
              <button
                type="button"
                data-dossier-notebook
              >
                Send to notebook
              </button>
            </div>
            <pre
              data-validation-output
              aria-live="polite"
            >Run a validation action to inspect the record.</pre>
          </section>
        </div>

        <p class="sc-validation-boundary">
          Research, education, laboratory prototyping, and
          internal validation only. This workspace does not grant
          GMP certification, regulatory approval, clinical release
          authority, or automatic instrument-control authority.
        </p>
      </section>
    `;

    const profiles = root.querySelector(
      '[data-validation-profiles]'
    );

    profiles.innerHTML = CONTRACT.validationProfiles
      .map(
        (profile) => `
          <label class="sc-validation-profile">
            <span>${profile.label}</span>
            <input
              type="number"
              min="0"
              max="100"
              step="1"
              value="95"
              data-profile-score="${profile.id}"
            >
          </label>
        `
      )
      .join('');

    const output = root.querySelector(
      '[data-validation-output]'
    );

    const show = (value) => {
      output.textContent = JSON.stringify(
        value,
        null,
        2
      );
    };

    root.querySelector(
      '[data-validation-evaluate]'
    ).addEventListener(
      'click',
      () => {
        try {
          state.profileResults = Object.fromEntries(
            CONTRACT.validationProfiles.map(
              (profile) => {
                const field = root.querySelector(
                  `[data-profile-score="${profile.id}"]`
                );
                const score = Math.max(
                  0,
                  Math.min(
                    100,
                    Number(field.value)
                  )
                );

                return [
                  profile.id,
                  {
                    score,
                    state: score >= 85
                      ? 'accepted'
                      : (
                          score >= 70
                            ? 'conditionally-accepted'
                            : 'hold'
                        ),
                    criticalFailure: false,
                    expired: false,
                  },
                ];
              }
            )
          );

          const score = validationScore(
            Object.fromEntries(
              Object.entries(state.profileResults)
                .map(
                  ([key, value]) => [
                    key,
                    value.score,
                  ]
                )
            ),
            {}
          );

          show({
            profileResults: state.profileResults,
            validationScore: score,
            disposition: validationDisposition(
              score,
              0,
              state.deviations.filter(
                (item) => !item.closed
              ).length,
              0
            ),
          });
        } catch (error) {
          state.lastError = String(
            error?.message || error
          );
          show({ error: state.lastError });
        }
      }
    );

    root.querySelector(
      '[data-validation-manifest]'
    ).addEventListener(
      'click',
      async () => {
        try {
          const components = JSON.parse(
            root.querySelector(
              '[data-validation-components]'
            ).value
          );
          state.manifest = await createManifest(
            components,
            {
              source:
                'instrumentation-validation-interface',
            }
          );
          show(state.manifest);
        } catch (error) {
          state.lastError = String(
            error?.message || error
          );
          show({ error: state.lastError });
        }
      }
    );

    root.querySelector(
      '[data-custody-add]'
    ).addEventListener(
      'click',
      async () => {
        try {
          const previousHash =
            state.custodyEvents.at(-1)?.eventHash || '';
          const event = await createCustodyEvent({
            sampleId: root.querySelector(
              '[data-custody-sample]'
            ).value,
            action: root.querySelector(
              '[data-custody-action]'
            ).value,
            actor: root.querySelector(
              '[data-custody-actor]'
            ).value,
            location: root.querySelector(
              '[data-custody-location]'
            ).value,
            timestamp: Date.now() / 1000,
            previousHash,
          });
          state.custodyEvents.push(event);
          show({
            event,
            eventCount:
              state.custodyEvents.length,
          });
        } catch (error) {
          state.lastError = String(
            error?.message || error
          );
          show({ error: state.lastError });
        }
      }
    );

    root.querySelector(
      '[data-custody-verify]'
    ).addEventListener(
      'click',
      async () => {
        try {
          show(
            await verifyCustodyChain(
              state.custodyEvents
            )
          );
        } catch (error) {
          state.lastError = String(
            error?.message || error
          );
          show({ error: state.lastError });
        }
      }
    );

    root.querySelector(
      '[data-deviation-add]'
    ).addEventListener(
      'click',
      () => {
        const deviation = {
          type: root.querySelector(
            '[data-deviation-type]'
          ).value,
          notes: root.querySelector(
            '[data-deviation-notes]'
          ).value,
          createdAt:
            new Date().toISOString(),
          closed: false,
        };
        state.deviations.push(deviation);
        show({
          deviation,
          deviationCount:
            state.deviations.length,
        });
      }
    );

    root.querySelector(
      '[data-dossier-create]'
    ).addEventListener(
      'click',
      async () => {
        try {
          if (
            !Object.keys(state.profileResults).length
          ) {
            throw new Error(
              'Evaluate the validation profiles first.'
            );
          }

          if (!state.manifest) {
            throw new Error(
              'Create the component manifest first.'
            );
          }

          state.dossier = await createDossier({
            profileResults: state.profileResults,
            manifest: state.manifest,
            custodyEvents: state.custodyEvents,
            deviations: state.deviations,
            metadata: {
              createdAt:
                new Date().toISOString(),
            },
          });

          show(state.dossier);
        } catch (error) {
          state.lastError = String(
            error?.message || error
          );
          show({ error: state.lastError });
        }
      }
    );

    root.querySelector(
      '[data-dossier-export]'
    ).addEventListener(
      'click',
      () => downloadJson(
        `sc-lab-instrumentation-dossier-${Date.now()}.json`,
        state.dossier || {
          error:
            'Create a dossier before export.',
        }
      )
    );

    root.querySelector(
      '[data-dossier-project]'
    ).addEventListener(
      'click',
      () => dispatchHandoff(
        'sc-lab:project-record',
        state.dossier
      )
    );

    root.querySelector(
      '[data-dossier-notebook]'
    ).addEventListener(
      'click',
      () => dispatchHandoff(
        'sc-lab:notebook-entry',
        state.dossier
      )
    );

    root.dataset.scInstrumentationValidationVersion =
      VERSION;
    state.rendered = true;
    return true;
  }

  function init() {
    [0, 100, 300, 900, 1800].forEach(
      (delay) => W.setTimeout(render, delay)
    );

    if (
      typeof MutationObserver !== 'undefined'
      && typeof document !== 'undefined'
    ) {
      new MutationObserver(
        () => render()
      ).observe(
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
      engineVersion: ENGINE_VERSION,
      productionVersion:
        PRODUCTION_VERSION,
      liveVersion: LIVE_VERSION,
      validationProfileCount:
        CONTRACT.validationProfiles.length,
      acceptanceStateCount:
        CONTRACT.acceptanceStates.length,
      eventTypeCount:
        CONTRACT.provenanceEventTypes.length,
      deviationTypeCount:
        CONTRACT.deviationTypes.length,
      analysisMethodCount:
        CONTRACT.analysisMethods.length,
      benchmarkCount:
        CONTRACT.benchmarks.length,
      preservedMethodCount:
        Lab.LaboratoryDataInstrumentation
          ?.catalog?.methods?.length || 0,
      preservedBenchmarkCount:
        Lab.LaboratoryDataInstrumentation
          ?.catalog?.benchmarks?.length || 0,
      liveModeCount:
        Lab.InstrumentationLiveVisualization
          ?.contract?.modes?.length || 0,
      custodyEventCount:
        state.custodyEvents.length,
      deviationCount:
        state.deviations.length,
      manifestReady:
        Boolean(state.manifest),
      dossierReady:
        Boolean(state.dossier),
      rootFound: Boolean(root),
      rendered: Boolean(
        root?.querySelector(
          '.sc-validation-shell'
        )
      ),
      lastError: state.lastError,
    };
  }

  Lab.InstrumentationValidationCustody = {
    VERSION,
    ENGINE_VERSION,
    PRODUCTION_VERSION,
    LIVE_VERSION,
    contract: CONTRACT,
    execute,
    calibrationAbsoluteError,
    calibrationPercentError,
    calibrationBias,
    calibrationRmse,
    calibrationLinearityR2,
    repeatabilityCv,
    acceptanceWindowStatus,
    dueState,
    measurementCompleteness,
    qualityFlagRate,
    custodyCompleteness,
    custodySequenceStatus,
    deviationRate,
    validationScore,
    validationDisposition,
    canonicalJson,
    sha256Text,
    createManifest,
    createCustodyEvent,
    verifyCustodyChain,
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
