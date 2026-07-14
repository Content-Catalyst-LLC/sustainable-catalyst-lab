(() => {
  'use strict';

  const W = typeof window !== 'undefined' ? window : globalThis;
  const Lab = W.SCLab = W.SCLab || {};
  const VERSION = '0.25.2';
  const ENGINE_VERSION = '0.25.0';
  const PRODUCTION_VERSION = '0.25.1';
  const ROOT_SELECTOR = '[data-instrumentation-live-visualization-root]';
  const CONTRACT = {"schema":"sc-lab-instrumentation-live-visualization-contract/1.0","version":"0.25.2","title":"Live Sensor and Instrument Visualization","preservedEngine":{"version":"0.25.0","methodCount":48,"benchmarkCount":48,"categoryCount":8,"recordTypeCount":9,"connectionProfileCount":8,"qualityFlagCount":8},"productionLayer":{"version":"0.25.1"},"modes":[{"id":"live-multichannel","label":"Live multi-channel dashboard"},{"id":"buffered-trends","label":"Buffered time-series trends"},{"id":"threshold-overlays","label":"Warning and action overlays"},{"id":"event-timeline","label":"Event and quality timeline"},{"id":"pause-playback","label":"Pause, playback, and replay"},{"id":"channel-comparison","label":"Channel comparison"},{"id":"connection-diagnostics","label":"Connection diagnostics"},{"id":"export-handoff","label":"Export and research handoff"}],"analysisMethods":[{"id":"append-ring-buffer","operation":"append_ring_buffer"},{"id":"trim-time-window","operation":"trim_time_window"},{"id":"channel-summary","operation":"channel_summary"},{"id":"latest-channel-values","operation":"latest_channel_values"},{"id":"threshold-status","operation":"threshold_status"},{"id":"detect-threshold-events","operation":"detect_threshold_events"},{"id":"detect-gap-events","operation":"detect_gap_events"},{"id":"rolling-mean-series","operation":"rolling_mean_series"},{"id":"rolling-sd-series","operation":"rolling_sd_series"},{"id":"exponential-smoothing-series","operation":"exponential_smoothing_series"},{"id":"min-max-downsample","operation":"min_max_downsample"},{"id":"align-channels","operation":"align_channels"},{"id":"common-time-window","operation":"common_time_window"},{"id":"event-rate","operation":"event_rate"},{"id":"connection-uptime","operation":"connection_uptime"},{"id":"dashboard-summary","operation":"dashboard_summary"}],"benchmarks":[{"id":"benchmark-append-ring-buffer","methodId":"append-ring-buffer","inputs":{"existing":[{"timestamp":1,"channel":"temperature","value":20}],"incoming":[{"timestamp":2,"channel":"temperature","value":21},{"timestamp":3,"channel":"temperature","value":22}],"maximumPoints":2},"expected":[{"timestamp":2.0,"channel":"temperature","value":21.0},{"timestamp":3.0,"channel":"temperature","value":22.0}]},{"id":"benchmark-trim-time-window","methodId":"trim-time-window","inputs":{"points":[{"timestamp":1,"value":1},{"timestamp":5,"value":2},{"timestamp":10,"value":3}],"windowStart":4,"windowEnd":9},"expected":[{"timestamp":5.0,"value":2.0}]},{"id":"benchmark-channel-summary","methodId":"channel-summary","inputs":{"values":[1,2,3,4]},"expected":{"count":4,"mean":2.5,"standardDeviation":1.2909944487358056,"minimum":1.0,"maximum":4.0,"range":3.0,"latest":4.0}},{"id":"benchmark-latest-channel-values","methodId":"latest-channel-values","inputs":{"records":[{"timestamp":1,"channel":"temperature","value":20},{"timestamp":2,"channel":"pressure","value":100},{"timestamp":3,"channel":"temperature","value":21}]},"expected":{"temperature":{"timestamp":3.0,"channel":"temperature","value":21.0},"pressure":{"timestamp":2.0,"channel":"pressure","value":100.0}}},{"id":"benchmark-threshold-status","methodId":"threshold-status","inputs":{"value":15,"warningLow":10,"warningHigh":20,"actionLow":5,"actionHigh":25},"expected":"normal"},{"id":"benchmark-detect-threshold-events","methodId":"detect-threshold-events","inputs":{"records":[{"timestamp":1,"channel":"temperature","value":20},{"timestamp":2,"channel":"temperature","value":26},{"timestamp":3,"channel":"temperature","value":24}],"thresholds":{"temperature":{"warningLow":10,"warningHigh":20,"actionLow":5,"actionHigh":25}}},"expected":[{"type":"action","channel":"temperature","timestamp":2.0,"value":26.0,"message":"temperature entered action range."},{"type":"warning","channel":"temperature","timestamp":3.0,"value":24.0,"message":"temperature entered warning range."}]},{"id":"benchmark-detect-gap-events","methodId":"detect-gap-events","inputs":{"records":[{"timestamp":1,"channel":"temperature","value":20},{"timestamp":2,"channel":"temperature","value":21},{"timestamp":8,"channel":"temperature","value":22}],"maximumGapSeconds":3},"expected":[{"type":"gap","channel":"temperature","timestamp":8.0,"gapSeconds":6.0}]},{"id":"benchmark-rolling-mean-series","methodId":"rolling-mean-series","inputs":{"values":[1,2,3,4],"windowSize":2},"expected":[1.0,1.5,2.5,3.5]},{"id":"benchmark-rolling-sd-series","methodId":"rolling-sd-series","inputs":{"values":[1,2,3,4],"windowSize":3},"expected":[0.0,0.7071067811865476,1.0,1.0]},{"id":"benchmark-exponential-smoothing-series","methodId":"exponential-smoothing-series","inputs":{"values":[0,10,10],"alpha":0.5},"expected":[0.0,5.0,7.5]},{"id":"benchmark-min-max-downsample","methodId":"min-max-downsample","inputs":{"points":[{"timestamp":0,"value":1},{"timestamp":1,"value":3},{"timestamp":2,"value":2},{"timestamp":3,"value":7},{"timestamp":4,"value":4},{"timestamp":5,"value":6}],"bucketCount":2},"expected":[{"timestamp":0.0,"value":1.0},{"timestamp":1.0,"value":3.0},{"timestamp":3.0,"value":7.0},{"timestamp":4.0,"value":4.0}]},{"id":"benchmark-align-channels","methodId":"align-channels","inputs":{"reference":[{"timestamp":1,"value":10},{"timestamp":2,"value":20},{"timestamp":3,"value":30}],"comparison":[{"timestamp":1.1,"value":11},{"timestamp":2.1,"value":21},{"timestamp":3.1,"value":31}],"toleranceSeconds":0.2},"expected":[{"timestamp":1.0,"referenceValue":10.0,"comparisonValue":11.0,"timeDeltaSeconds":0.10000000000000009},{"timestamp":2.0,"referenceValue":20.0,"comparisonValue":21.0,"timeDeltaSeconds":0.10000000000000009},{"timestamp":3.0,"referenceValue":30.0,"comparisonValue":31.0,"timeDeltaSeconds":0.10000000000000009}]},{"id":"benchmark-common-time-window","methodId":"common-time-window","inputs":{"series":[[{"timestamp":1,"value":1},{"timestamp":5,"value":2}],[{"timestamp":2,"value":3},{"timestamp":6,"value":4}]]},"expected":{"start":2.0,"end":5.0,"durationSeconds":3.0}},{"id":"benchmark-event-rate","methodId":"event-rate","inputs":{"eventCount":12,"durationSeconds":120},"expected":6.0},{"id":"benchmark-connection-uptime","methodId":"connection-uptime","inputs":{"onlineSeconds":90,"totalSeconds":100},"expected":90.0},{"id":"benchmark-dashboard-summary","methodId":"dashboard-summary","inputs":{"records":[{"timestamp":1,"channel":"temperature","value":20},{"timestamp":2,"channel":"temperature","value":21},{"timestamp":2,"channel":"pressure","value":100}],"events":[{"type":"warning"},{"type":"gap"}],"connectionState":"online"},"expected":{"recordCount":3,"channelCount":2,"eventCount":2,"connectionState":"online","latest":{"temperature":{"timestamp":2.0,"channel":"temperature","value":21.0},"pressure":{"timestamp":2.0,"channel":"pressure","value":100.0}},"channels":{"temperature":{"count":2,"mean":20.5,"standardDeviation":0.7071067811865476,"minimum":20.0,"maximum":21.0,"range":1.0,"latest":21.0},"pressure":{"count":1,"mean":100.0,"standardDeviation":0.0,"minimum":100.0,"maximum":100.0,"range":0.0,"latest":100.0}},"eventTypeCounts":{"gap":1,"warning":1}}}],"channelTemplates":[{"id":"temperature","label":"Temperature","unit":"°C"},{"id":"pressure","label":"Pressure","unit":"kPa"},{"id":"humidity","label":"Humidity","unit":"%"},{"id":"ph","label":"pH","unit":"pH"},{"id":"conductivity","label":"Conductivity","unit":"mS/cm"},{"id":"flow","label":"Flow","unit":"L/min"},{"id":"voltage","label":"Voltage","unit":"V"},{"id":"custom","label":"Custom channel","unit":"a.u."}],"connectionStates":["disconnected","connecting","online","paused","replaying","degraded","stale","error"],"eventTypes":["warning","action","gap","connection","calibration","maintenance","annotation","quality"],"bufferDefaults":{"maximumPoints":1200,"maximumAgeSeconds":900,"renderPointLimit":400,"staleAfterSeconds":30,"maximumGapSeconds":10},"responsibleUse":{"scope":"Research, education, laboratory prototyping, replay, and non-clinical visualization.","boundaries":{"automaticLocalDeviceAccess":false,"clinicalMonitoring":false,"alarmAuthority":false,"regulatedControl":false,"localFirstReplay":true}}};

  const state = {
    records: [],
    events: [],
    thresholds: {
      temperature: {
        warningLow: 18,
        warningHigh: 26,
        actionLow: 10,
        actionHigh: 32,
      },
      pressure: {
        warningLow: 90,
        warningHigh: 110,
        actionLow: 80,
        actionHigh: 120,
      },
    },
    connectionState: 'disconnected',
    paused: false,
    replaying: false,
    selectedChannels: ['temperature', 'pressure'],
    maximumPoints: CONTRACT.bufferDefaults.maximumPoints,
    maximumGapSeconds: CONTRACT.bufferDefaults.maximumGapSeconds,
    demoTimer: null,
    replayTimer: null,
    lastRenderAt: null,
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

  function records(value, label = 'records') {
    if (!Array.isArray(value)) {
      throw new Error(`${label} must be an array.`);
    }
    return value.map((record, index) => {
      if (!record || typeof record !== 'object') {
        throw new Error(`${label}[${index}] must be an object.`);
      }
      const normalized = {
        ...record,
        timestamp: finite(
          record.timestamp,
          `${label}[${index}].timestamp`
        ),
      };
      if ('value' in record) {
        normalized.value = finite(
          record.value,
          `${label}[${index}].value`
        );
      }
      return normalized;
    });
  }

  function values(value, label = 'values') {
    if (!Array.isArray(value) || !value.length) {
      throw new Error(`${label} must be a non-empty array.`);
    }
    return value.map(
      (item, index) => finite(item, `${label}[${index}]`)
    );
  }

  const mean = (items) => (
    items.reduce((sum, item) => sum + item, 0) / items.length
  );

  function standardDeviation(items) {
    if (items.length < 2) {
      return 0;
    }
    const average = mean(items);
    return Math.sqrt(
      items.reduce(
        (sum, item) => sum + (item - average) ** 2,
        0
      ) / (items.length - 1)
    );
  }

  function appendRingBuffer(existing, incoming, maximumPoints) {
    const maximum = Math.trunc(
      positive(maximumPoints, 'maximumPoints')
    );
    return [...records(existing, 'existing'), ...records(incoming, 'incoming')]
      .sort((left, right) => left.timestamp - right.timestamp)
      .slice(-maximum);
  }

  function trimTimeWindow(points, windowStart, windowEnd) {
    const start = finite(windowStart, 'windowStart');
    const end = finite(windowEnd, 'windowEnd');
    if (end < start) {
      throw new Error('windowEnd must be at least windowStart.');
    }
    return records(points, 'points').filter(
      (point) => point.timestamp >= start && point.timestamp <= end
    );
  }

  function channelSummary(rawValues) {
    const numbers = values(rawValues);
    const minimum = Math.min(...numbers);
    const maximum = Math.max(...numbers);
    return {
      count: numbers.length,
      mean: mean(numbers),
      standardDeviation: standardDeviation(numbers),
      minimum,
      maximum,
      range: maximum - minimum,
      latest: numbers.at(-1),
    };
  }

  function latestChannelValues(rawRecords) {
    const latest = {};
    records(rawRecords).forEach((record) => {
      const channel = String(record.channel || '');
      if (!channel) {
        return;
      }
      if (
        !latest[channel]
        || record.timestamp >= latest[channel].timestamp
      ) {
        latest[channel] = record;
      }
    });
    return latest;
  }

  function thresholdStatus(
    value,
    warningLow,
    warningHigh,
    actionLow,
    actionHigh
  ) {
    const number = finite(value, 'value');
    const wl = finite(warningLow, 'warningLow');
    const wh = finite(warningHigh, 'warningHigh');
    const al = finite(actionLow, 'actionLow');
    const ah = finite(actionHigh, 'actionHigh');
    if (!(al <= wl && wl <= wh && wh <= ah)) {
      throw new Error(
        'Thresholds must satisfy actionLow <= warningLow <= warningHigh <= actionHigh.'
      );
    }
    if (number < al || number > ah) {
      return 'action';
    }
    if (number < wl || number > wh) {
      return 'warning';
    }
    return 'normal';
  }

  function detectThresholdEvents(rawRecords, thresholds) {
    if (!thresholds || typeof thresholds !== 'object') {
      throw new Error('thresholds must be an object.');
    }
    const previous = {};
    const events = [];
    records(rawRecords).forEach((record) => {
      const channel = String(record.channel || '');
      const definition = thresholds[channel];
      if (!channel || !definition) {
        return;
      }
      const status = thresholdStatus(
        record.value,
        definition.warningLow,
        definition.warningHigh,
        definition.actionLow,
        definition.actionHigh
      );
      if (
        status !== 'normal'
        && status !== previous[channel]
      ) {
        events.push({
          type: status,
          channel,
          timestamp: record.timestamp,
          value: record.value,
          message: `${channel} entered ${status} range.`,
        });
      }
      previous[channel] = status;
    });
    return events;
  }

  function detectGapEvents(rawRecords, maximumGapSeconds) {
    const maximum = positive(
      maximumGapSeconds,
      'maximumGapSeconds'
    );
    const previous = {};
    const events = [];
    records(rawRecords)
      .sort((left, right) => {
        const channelOrder = String(left.channel || '')
          .localeCompare(String(right.channel || ''));
        return channelOrder || left.timestamp - right.timestamp;
      })
      .forEach((record) => {
        const channel = String(record.channel || '');
        if (!channel) {
          return;
        }
        if (previous[channel] !== undefined) {
          const gap = record.timestamp - previous[channel];
          if (gap > maximum) {
            events.push({
              type: 'gap',
              channel,
              timestamp: record.timestamp,
              gapSeconds: gap,
            });
          }
        }
        previous[channel] = record.timestamp;
      });
    return events;
  }

  function rollingMeanSeries(rawValues, windowSize) {
    const numbers = values(rawValues);
    const window = Math.trunc(positive(windowSize, 'windowSize'));
    return numbers.map(
      (_, index) => mean(
        numbers.slice(Math.max(0, index - window + 1), index + 1)
      )
    );
  }

  function rollingSdSeries(rawValues, windowSize) {
    const numbers = values(rawValues);
    const window = Math.trunc(positive(windowSize, 'windowSize'));
    return numbers.map(
      (_, index) => standardDeviation(
        numbers.slice(Math.max(0, index - window + 1), index + 1)
      )
    );
  }

  function exponentialSmoothingSeries(rawValues, alpha) {
    const numbers = values(rawValues);
    const weight = finite(alpha, 'alpha');
    if (!(weight > 0 && weight <= 1)) {
      throw new Error('alpha must be greater than zero and at most one.');
    }
    const smoothed = [numbers[0]];
    numbers.slice(1).forEach((number) => {
      smoothed.push(
        weight * number + (1 - weight) * smoothed.at(-1)
      );
    });
    return smoothed;
  }

  function minMaxDownsample(rawPoints, bucketCount) {
    const points = records(rawPoints, 'points')
      .sort((left, right) => left.timestamp - right.timestamp);
    const buckets = Math.trunc(positive(bucketCount, 'bucketCount'));
    if (buckets >= points.length) {
      return points;
    }
    const output = [];
    for (let bucket = 0; bucket < buckets; bucket += 1) {
      const start = Math.floor(bucket * points.length / buckets);
      const end = Math.floor((bucket + 1) * points.length / buckets);
      const group = points.slice(start, Math.max(start + 1, end));
      const minimum = group.reduce(
        (best, point) => point.value < best.value ? point : best
      );
      const maximum = group.reduce(
        (best, point) => point.value > best.value ? point : best
      );
      const distinct = minimum === maximum ? [minimum] : [minimum, maximum];
      output.push(
        ...distinct.sort((left, right) => left.timestamp - right.timestamp)
      );
    }
    return output;
  }

  function alignChannels(reference, comparison, toleranceSeconds) {
    const left = records(reference, 'reference')
      .sort((a, b) => a.timestamp - b.timestamp);
    const right = records(comparison, 'comparison')
      .sort((a, b) => a.timestamp - b.timestamp);
    const tolerance = positive(
      toleranceSeconds,
      'toleranceSeconds'
    );
    const used = new Set();
    const matches = [];
    left.forEach((referencePoint) => {
      const candidates = right
        .map((point, index) => ({
          delta: Math.abs(point.timestamp - referencePoint.timestamp),
          index,
          point,
        }))
        .filter(
          (candidate) => (
            !used.has(candidate.index)
            && candidate.delta <= tolerance
          )
        )
        .sort((a, b) => a.delta - b.delta);
      if (!candidates.length) {
        return;
      }
      const best = candidates[0];
      used.add(best.index);
      matches.push({
        timestamp: referencePoint.timestamp,
        referenceValue: referencePoint.value,
        comparisonValue: best.point.value,
        timeDeltaSeconds:
          best.point.timestamp - referencePoint.timestamp,
      });
    });
    return matches;
  }

  function commonTimeWindow(series) {
    if (!Array.isArray(series) || !series.length) {
      throw new Error('series must be a non-empty array.');
    }
    const normalized = series.map(
      (item, index) => records(item, `series[${index}]`)
    );
    if (normalized.some((item) => !item.length)) {
      return { start: null, end: null, durationSeconds: 0 };
    }
    const start = Math.max(
      ...normalized.map((item) => Math.min(...item.map((point) => point.timestamp)))
    );
    const end = Math.min(
      ...normalized.map((item) => Math.max(...item.map((point) => point.timestamp)))
    );
    return {
      start,
      end,
      durationSeconds: Math.max(0, end - start),
    };
  }

  function eventRate(eventCount, durationSeconds) {
    return finite(eventCount, 'eventCount')
      * 60
      / positive(durationSeconds, 'durationSeconds');
  }

  function connectionUptime(onlineSeconds, totalSeconds) {
    return Math.max(
      0,
      Math.min(
        100,
        finite(onlineSeconds, 'onlineSeconds')
        / positive(totalSeconds, 'totalSeconds')
        * 100
      )
    );
  }

  function dashboardSummary(rawRecords, rawEvents, connectionState) {
    if (!Array.isArray(rawEvents)) {
      throw new Error('events must be an array.');
    }
    const normalized = records(rawRecords);
    const grouped = {};
    normalized.forEach((record) => {
      const channel = String(record.channel || '');
      if (channel) {
        grouped[channel] = grouped[channel] || [];
        grouped[channel].push(record.value);
      }
    });
    const types = {};
    rawEvents.forEach((event) => {
      const type = String(event.type || '');
      if (type) {
        types[type] = (types[type] || 0) + 1;
      }
    });
    return {
      recordCount: normalized.length,
      channelCount: Object.keys(grouped).length,
      eventCount: rawEvents.length,
      connectionState: String(connectionState),
      latest: latestChannelValues(normalized),
      channels: Object.fromEntries(
        Object.entries(grouped).map(
          ([channel, channelValues]) => [
            channel,
            channelSummary(channelValues),
          ]
        )
      ),
      eventTypeCounts: types,
    };
  }

  function execute(methodId, inputs = {}) {
    const i = inputs || {};
    const dispatch = {
      'append-ring-buffer': () => appendRingBuffer(
        i.existing || [],
        i.incoming || [],
        i.maximumPoints
      ),
      'trim-time-window': () => trimTimeWindow(
        i.points || [],
        i.windowStart,
        i.windowEnd
      ),
      'channel-summary': () => channelSummary(i.values),
      'latest-channel-values': () => latestChannelValues(i.records || []),
      'threshold-status': () => thresholdStatus(
        i.value,
        i.warningLow,
        i.warningHigh,
        i.actionLow,
        i.actionHigh
      ),
      'detect-threshold-events': () => detectThresholdEvents(
        i.records || [],
        i.thresholds || {}
      ),
      'detect-gap-events': () => detectGapEvents(
        i.records || [],
        i.maximumGapSeconds
      ),
      'rolling-mean-series': () => rollingMeanSeries(
        i.values,
        i.windowSize
      ),
      'rolling-sd-series': () => rollingSdSeries(
        i.values,
        i.windowSize
      ),
      'exponential-smoothing-series': () => exponentialSmoothingSeries(
        i.values,
        i.alpha
      ),
      'min-max-downsample': () => minMaxDownsample(
        i.points || [],
        i.bucketCount
      ),
      'align-channels': () => alignChannels(
        i.reference || [],
        i.comparison || [],
        i.toleranceSeconds
      ),
      'common-time-window': () => commonTimeWindow(i.series || []),
      'event-rate': () => eventRate(
        i.eventCount,
        i.durationSeconds
      ),
      'connection-uptime': () => connectionUptime(
        i.onlineSeconds,
        i.totalSeconds
      ),
      'dashboard-summary': () => dashboardSummary(
        i.records || [],
        i.events || [],
        i.connectionState || 'disconnected'
      ),
    };
    if (!dispatch[methodId]) {
      throw new Error(`Unknown live visualization method: ${methodId}`);
    }
    return {
      schema: 'sc-lab-instrumentation-live-analysis/1.0',
      version: VERSION,
      methodId,
      inputs,
      value: dispatch[methodId](),
    };
  }

  function buildSnapshot(
    rawRecords,
    thresholds = {},
    maximumGapSeconds = 10,
    connectionState = 'disconnected'
  ) {
    const normalized = records(rawRecords);
    const events = [
      ...detectThresholdEvents(normalized, thresholds),
      ...(normalized.length
        ? detectGapEvents(normalized, maximumGapSeconds)
        : []),
    ];
    return {
      schema: 'sc-lab-instrumentation-live-snapshot/1.0',
      version: VERSION,
      createdFromRecordCount: normalized.length,
      events,
      summary: dashboardSummary(
        normalized,
        events,
        connectionState
      ),
      records: normalized,
    };
  }

  class StreamBuffer {
    constructor(options = {}) {
      this.maximumPoints = Number(
        options.maximumPoints
        || CONTRACT.bufferDefaults.maximumPoints
      );
      this.maximumAgeSeconds = Number(
        options.maximumAgeSeconds
        || CONTRACT.bufferDefaults.maximumAgeSeconds
      );
      this.records = [];
      this.connectionState = 'disconnected';
      this.paused = false;
    }

    ingest(record) {
      if (this.paused) {
        return this.snapshot();
      }
      const normalized = records([record], 'record')[0];
      normalized.channel = String(normalized.channel || 'custom');
      normalized.unit = String(normalized.unit || '');
      normalized.qualityFlags = Array.isArray(normalized.qualityFlags)
        ? normalized.qualityFlags
        : [];
      this.records = appendRingBuffer(
        this.records,
        [normalized],
        this.maximumPoints
      );
      const latestTimestamp = this.records.at(-1)?.timestamp;
      if (Number.isFinite(latestTimestamp)) {
        const minimum = latestTimestamp - this.maximumAgeSeconds;
        this.records = this.records.filter(
          (point) => point.timestamp >= minimum
        );
      }
      return this.snapshot();
    }

    ingestBatch(batch) {
      records(batch, 'batch').forEach((record) => this.ingest(record));
      return this.snapshot();
    }

    clear() {
      this.records = [];
      return this.snapshot();
    }

    pause() {
      this.paused = true;
      this.connectionState = 'paused';
      return this.snapshot();
    }

    resume() {
      this.paused = false;
      this.connectionState = 'online';
      return this.snapshot();
    }

    setConnectionState(connectionState) {
      if (!CONTRACT.connectionStates.includes(connectionState)) {
        throw new Error(`Unknown connection state: ${connectionState}`);
      }
      this.connectionState = connectionState;
      return this.snapshot();
    }

    snapshot() {
      return buildSnapshot(
        this.records,
        state.thresholds,
        state.maximumGapSeconds,
        this.connectionState
      );
    }
  }

  const stream = new StreamBuffer({
    maximumPoints: state.maximumPoints,
  });

  function parseCsv(text) {
    const lines = String(text || '')
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean);
    if (lines.length < 2) {
      throw new Error('CSV requires a header and at least one data row.');
    }
    const headers = lines[0].split(',').map((header) => header.trim());
    const required = ['timestamp', 'channel', 'value'];
    required.forEach((header) => {
      if (!headers.includes(header)) {
        throw new Error(`CSV is missing required column: ${header}`);
      }
    });
    return lines.slice(1).map((line, rowIndex) => {
      const fields = line.split(',');
      const record = Object.fromEntries(
        headers.map((header, index) => [header, fields[index]?.trim() ?? ''])
      );
      return {
        ...record,
        timestamp: finite(record.timestamp, `row ${rowIndex + 1} timestamp`),
        value: finite(record.value, `row ${rowIndex + 1} value`),
        qualityFlags: record.qualityFlags
          ? record.qualityFlags.split('|').filter(Boolean)
          : [],
      };
    });
  }

  function groupChannels(rawRecords) {
    const grouped = {};
    records(rawRecords).forEach((record) => {
      const channel = String(record.channel || 'custom');
      grouped[channel] = grouped[channel] || [];
      grouped[channel].push(record);
    });
    return grouped;
  }

  function chartSvg(rawRecords, selectedChannels, rawEvents = []) {
    const width = 980;
    const height = Math.max(280, selectedChannels.length * 150);
    const left = 58;
    const right = 24;
    const top = 20;
    const bottom = 34;
    const grouped = groupChannels(rawRecords);
    const selected = selectedChannels.filter(
      (channel) => grouped[channel]?.length
    );
    if (!selected.length) {
      return '<p class="sc-live-empty">No selected channel data is available.</p>';
    }
    const all = selected.flatMap((channel) => grouped[channel]);
    const minTime = Math.min(...all.map((point) => point.timestamp));
    const maxTime = Math.max(...all.map((point) => point.timestamp));
    const timeRange = maxTime - minTime || 1;
    const plotWidth = width - left - right;
    const rowHeight = (height - top - bottom) / selected.length;
    const traces = selected.map((channel, channelIndex) => {
      const points = minMaxDownsample(
        grouped[channel],
        Math.min(
          CONTRACT.bufferDefaults.renderPointLimit / 2,
          Math.max(1, Math.floor(grouped[channel].length / 2))
        )
      );
      const values = points.map((point) => point.value);
      const minimum = Math.min(...values);
      const maximum = Math.max(...values);
      const range = maximum - minimum || 1;
      const yTop = top + channelIndex * rowHeight;
      const line = points.map((point) => {
        const x = left + (point.timestamp - minTime) / timeRange * plotWidth;
        const y = yTop + rowHeight - 24
          - (point.value - minimum) / range * (rowHeight - 48);
        return `${x.toFixed(2)},${y.toFixed(2)}`;
      }).join(' ');
      const events = rawEvents
        .filter((event) => event.channel === channel)
        .map((event) => {
          const x = left + (event.timestamp - minTime) / timeRange * plotWidth;
          return `<line x1="${x}" x2="${x}" y1="${yTop + 18}" y2="${yTop + rowHeight - 18}" class="sc-live-event sc-live-event-${event.type}"><title>${event.type}: ${channel}</title></line>`;
        })
        .join('');
      return `
        <g>
          <text x="8" y="${yTop + 24}" class="sc-live-label">${channel}</text>
          <text x="8" y="${yTop + 43}" class="sc-live-range">${minimum.toPrecision(4)} – ${maximum.toPrecision(4)}</text>
          <line x1="${left}" x2="${width - right}" y1="${yTop + rowHeight - 24}" y2="${yTop + rowHeight - 24}" class="sc-live-axis"/>
          ${events}
          <polyline points="${line}" class="sc-live-trace sc-live-trace-${channel}"/>
        </g>
      `;
    }).join('');

    return `
      <svg class="sc-live-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Live sensor and instrument time-series chart">
        ${traces}
        <text x="${left}" y="${height - 8}" class="sc-live-time">${minTime.toFixed(2)}</text>
        <text x="${width - right}" y="${height - 8}" text-anchor="end" class="sc-live-time">${maxTime.toFixed(2)}</text>
      </svg>
    `;
  }

  function download(name, type, content) {
    if (
      typeof document === 'undefined'
      || typeof Blob === 'undefined'
    ) {
      return false;
    }
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = name;
    link.click();
    URL.revokeObjectURL(url);
    return true;
  }

  function toCsv(rawRecords) {
    const header = 'timestamp,channel,value,unit,qualityFlags';
    const rows = records(rawRecords).map((record) => [
      record.timestamp,
      record.channel || '',
      record.value,
      record.unit || '',
      (record.qualityFlags || []).join('|'),
    ].map((field) => `"${String(field).replaceAll('"', '""')}"`).join(','));
    return [header, ...rows].join('\n');
  }

  function dispatchHandoff(eventName, snapshot) {
    if (typeof document === 'undefined') {
      return false;
    }
    document.dispatchEvent(
      new CustomEvent(eventName, {
        detail: {
          source: 'instrumentation-live-visualization',
          version: VERSION,
          record: snapshot,
        },
      })
    );
    return true;
  }

  function refreshStateFromStream() {
    const snapshot = stream.snapshot();
    state.records = snapshot.records;
    state.events = snapshot.events;
    state.connectionState = snapshot.summary.connectionState;
    return snapshot;
  }

  function ingest(record) {
    const snapshot = stream.ingest(record);
    state.records = snapshot.records;
    state.events = snapshot.events;
    state.connectionState = snapshot.summary.connectionState;
    scheduleRender();
    return snapshot;
  }

  function ingestBatch(batch) {
    const snapshot = stream.ingestBatch(batch);
    state.records = snapshot.records;
    state.events = snapshot.events;
    state.connectionState = snapshot.summary.connectionState;
    scheduleRender();
    return snapshot;
  }

  function startDemo() {
    stopDemo();
    stream.setConnectionState('online');
    const start = Date.now() / 1000;
    let index = 0;
    state.demoTimer = W.setInterval(() => {
      const timestamp = start + index;
      ingestBatch([
        {
          timestamp,
          channel: 'temperature',
          value: 22 + Math.sin(index / 5) * 2.8,
          unit: '°C',
          qualityFlags: [],
        },
        {
          timestamp,
          channel: 'pressure',
          value: 100 + Math.cos(index / 7) * 7,
          unit: 'kPa',
          qualityFlags: [],
        },
      ]);
      index += 1;
    }, 500);
    state.connectionState = 'online';
    return refreshStateFromStream();
  }

  function stopDemo() {
    if (state.demoTimer) {
      W.clearInterval(state.demoTimer);
      state.demoTimer = null;
    }
    return refreshStateFromStream();
  }

  function pause() {
    stopDemo();
    stream.pause();
    state.paused = true;
    return refreshStateFromStream();
  }

  function resume() {
    stream.resume();
    state.paused = false;
    return refreshStateFromStream();
  }

  function replay(rawRecords, options = {}) {
    if (state.replayTimer) {
      W.clearInterval(state.replayTimer);
    }
    const source = records(rawRecords)
      .sort((left, right) => left.timestamp - right.timestamp);
    const speed = positive(options.speed || 4, 'speed');
    let index = 0;
    stream.clear();
    stream.setConnectionState('replaying');
    state.replaying = true;
    state.replayTimer = W.setInterval(() => {
      if (index >= source.length) {
        W.clearInterval(state.replayTimer);
        state.replayTimer = null;
        state.replaying = false;
        stream.setConnectionState('paused');
        scheduleRender();
        return;
      }
      stream.ingest(source[index]);
      index += 1;
      refreshStateFromStream();
      scheduleRender();
    }, 1000 / speed);
    return refreshStateFromStream();
  }

  let renderScheduled = false;
  function scheduleRender() {
    if (renderScheduled) {
      return;
    }
    renderScheduled = true;
    W.setTimeout(() => {
      renderScheduled = false;
      updateRenderedDashboard();
    }, 60);
  }

  function updateRenderedDashboard() {
    if (typeof document === 'undefined') {
      return false;
    }
    const root = document.querySelector(ROOT_SELECTOR);
    if (!root) {
      return false;
    }
    const snapshot = refreshStateFromStream();
    const chart = root.querySelector('[data-live-chart]');
    const output = root.querySelector('[data-live-output]');
    const status = root.querySelector('[data-live-connection-status]');
    const events = root.querySelector('[data-live-events]');
    if (chart) {
      chart.innerHTML = chartSvg(
        snapshot.records,
        state.selectedChannels,
        snapshot.events
      );
    }
    if (output) {
      output.textContent = JSON.stringify(snapshot.summary, null, 2);
    }
    if (status) {
      status.textContent = snapshot.summary.connectionState;
      status.dataset.state = snapshot.summary.connectionState;
    }
    if (events) {
      events.innerHTML = snapshot.events.length
        ? snapshot.events.slice(-20).reverse().map(
            (event) => `
              <li>
                <strong>${String(event.type)}</strong>
                ${String(event.channel || '')}
                <span>${Number(event.timestamp).toFixed(2)}</span>
              </li>
            `
          ).join('')
        : '<li>No warning, action, or gap events.</li>';
    }
    state.lastRenderAt = new Date().toISOString();
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
    roots.slice(1).forEach((duplicate) => duplicate.remove());

    if (
      root.dataset.scLiveVisualizationVersion === VERSION
      && root.querySelector('.sc-live-shell')
    ) {
      state.rendered = true;
      updateRenderedDashboard();
      return true;
    }

    root.innerHTML = `
      <section class="sc-live-shell">
        <header class="sc-live-header">
          <p class="sc-live-kicker">LAB/INSTRUMENTATION/LIVE</p>
          <h3>Live Sensor and Instrument Visualization</h3>
          <p>Visualize bounded multi-channel streams, replay recorded measurements, inspect thresholds and data gaps, and export auditable research snapshots.</p>
          <div class="sc-live-status-row">
            <span>8 visualization modes</span>
            <span>16 deterministic methods</span>
            <span>8 connection states</span>
            <span data-live-connection-status data-state="disconnected">disconnected</span>
          </div>
        </header>

        <div class="sc-live-controls">
          <button type="button" data-live-demo>Start demo stream</button>
          <button type="button" data-live-pause>Pause</button>
          <button type="button" data-live-resume>Resume</button>
          <button type="button" data-live-clear>Clear buffer</button>
          <button type="button" data-live-export-json>Export JSON</button>
          <button type="button" data-live-export-csv>Export CSV</button>
          <button type="button" data-live-export-svg>Export SVG</button>
        </div>

        <div class="sc-live-grid">
          <section class="sc-live-card sc-live-card-wide">
            <div class="sc-live-card-header">
              <h4>Buffered channels</h4>
              <div class="sc-live-channel-controls">
                ${CONTRACT.channelTemplates.map(
                  (channel) => `
                    <label>
                      <input
                        type="checkbox"
                        value="${channel.id}"
                        data-live-channel
                        ${state.selectedChannels.includes(channel.id) ? 'checked' : ''}
                      >
                      ${channel.label}
                    </label>
                  `
                ).join('')}
              </div>
            </div>
            <div data-live-chart class="sc-live-chart"></div>
          </section>

          <section class="sc-live-card">
            <h4>Replay/import</h4>
            <label>
              CSV records
              <span>timestamp,channel,value,unit,qualityFlags</span>
              <textarea rows="10" data-live-csv>timestamp,channel,value,unit,qualityFlags
1,temperature,22.1,°C,
1,pressure,101.2,kPa,
2,temperature,22.8,°C,
2,pressure,100.4,kPa,
8,temperature,27.1,°C,review-required</textarea>
            </label>
            <div class="sc-live-controls sc-live-controls-compact">
              <button type="button" data-live-load>Load buffer</button>
              <button type="button" data-live-replay>Replay</button>
            </div>
          </section>

          <section class="sc-live-card">
            <h4>Latest dashboard summary</h4>
            <pre data-live-output aria-live="polite">No records have been ingested.</pre>
          </section>

          <section class="sc-live-card">
            <h4>Events</h4>
            <ul data-live-events class="sc-live-events">
              <li>No warning, action, or gap events.</li>
            </ul>
          </section>

          <section class="sc-live-card">
            <h4>Research handoff</h4>
            <div class="sc-live-controls sc-live-controls-stack">
              <button type="button" data-live-project>Send to project</button>
              <button type="button" data-live-notebook>Send to notebook</button>
              <button type="button" data-live-provenance>Create provenance record</button>
            </div>
          </section>
        </div>

        <p class="sc-live-boundary">
          Local-first research and laboratory prototyping only. This workspace does not silently connect to devices, replace a validated monitoring or alarm system, provide clinical surveillance, or exercise regulated instrument control.
        </p>
      </section>
    `;

    root.querySelectorAll('[data-live-channel]').forEach((checkbox) => {
      checkbox.addEventListener('change', () => {
        state.selectedChannels = Array.from(
          root.querySelectorAll('[data-live-channel]:checked')
        ).map((input) => input.value);
        updateRenderedDashboard();
      });
    });

    root.querySelector('[data-live-demo]').addEventListener(
      'click',
      startDemo
    );
    root.querySelector('[data-live-pause]').addEventListener(
      'click',
      () => {
        pause();
        updateRenderedDashboard();
      }
    );
    root.querySelector('[data-live-resume]').addEventListener(
      'click',
      () => {
        resume();
        updateRenderedDashboard();
      }
    );
    root.querySelector('[data-live-clear]').addEventListener(
      'click',
      () => {
        stopDemo();
        stream.clear();
        state.records = [];
        state.events = [];
        updateRenderedDashboard();
      }
    );

    const csv = root.querySelector('[data-live-csv]');
    root.querySelector('[data-live-load]').addEventListener(
      'click',
      () => {
        try {
          stopDemo();
          stream.clear();
          ingestBatch(parseCsv(csv.value));
          stream.setConnectionState('paused');
          updateRenderedDashboard();
        } catch (error) {
          state.lastError = String(error?.message || error);
        }
      }
    );
    root.querySelector('[data-live-replay]').addEventListener(
      'click',
      () => {
        try {
          replay(parseCsv(csv.value), { speed: 4 });
        } catch (error) {
          state.lastError = String(error?.message || error);
        }
      }
    );

    root.querySelector('[data-live-export-json]').addEventListener(
      'click',
      () => {
        const snapshot = refreshStateFromStream();
        download(
          `sc-lab-live-instrumentation-${Date.now()}.json`,
          'application/json',
          JSON.stringify(snapshot, null, 2)
        );
      }
    );
    root.querySelector('[data-live-export-csv]').addEventListener(
      'click',
      () => download(
        `sc-lab-live-instrumentation-${Date.now()}.csv`,
        'text/csv',
        toCsv(state.records)
      )
    );
    root.querySelector('[data-live-export-svg]').addEventListener(
      'click',
      () => {
        const svg = root.querySelector('.sc-live-svg');
        if (svg) {
          download(
            `sc-lab-live-instrumentation-${Date.now()}.svg`,
            'image/svg+xml',
            svg.outerHTML
          );
        }
      }
    );

    root.querySelector('[data-live-project]').addEventListener(
      'click',
      () => dispatchHandoff(
        'sc-lab:project-record',
        refreshStateFromStream()
      )
    );
    root.querySelector('[data-live-notebook]').addEventListener(
      'click',
      () => dispatchHandoff(
        'sc-lab:notebook-entry',
        refreshStateFromStream()
      )
    );
    root.querySelector('[data-live-provenance]').addEventListener(
      'click',
      () => {
        const provenance = Lab.BioprocessValidationProvenance;
        const snapshot = refreshStateFromStream();
        if (provenance?.createRecord) {
          const record = provenance.createRecord(
            snapshot,
            {
              eventType: 'validation-decision',
              profileId: 'instrumentation-live-visualization',
              disposition: 'research-review',
              notes: 'Live instrumentation snapshot handoff.',
            }
          );
          root.querySelector('[data-live-output]').textContent =
            JSON.stringify(record, null, 2);
        } else {
          root.querySelector('[data-live-output]').textContent =
            JSON.stringify(
              {
                error: 'The shared provenance engine is unavailable.',
                snapshot,
              },
              null,
              2
            );
        }
      }
    );

    root.dataset.scLiveVisualizationVersion = VERSION;
    state.rendered = true;
    updateRenderedDashboard();
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
      new MutationObserver(() => render()).observe(
        document.documentElement,
        { childList: true, subtree: true }
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
      productionVersion: PRODUCTION_VERSION,
      modeCount: CONTRACT.modes.length,
      analysisMethodCount: CONTRACT.analysisMethods.length,
      benchmarkCount: CONTRACT.benchmarks.length,
      channelTemplateCount: CONTRACT.channelTemplates.length,
      connectionStateCount: CONTRACT.connectionStates.length,
      eventTypeCount: CONTRACT.eventTypes.length,
      preservedMethodCount:
        Lab.LaboratoryDataInstrumentation?.catalog?.methods?.length || 0,
      preservedBenchmarkCount:
        Lab.LaboratoryDataInstrumentation?.catalog?.benchmarks?.length || 0,
      recordCount: state.records.length,
      eventCount: state.events.length,
      connectionState: state.connectionState,
      rootFound: Boolean(root),
      rendered: Boolean(root?.querySelector('.sc-live-shell')),
      lastRenderAt: state.lastRenderAt,
      lastError: state.lastError,
    };
  }

  Lab.InstrumentationLiveVisualization = {
    VERSION,
    ENGINE_VERSION,
    PRODUCTION_VERSION,
    contract: CONTRACT,
    execute,
    appendRingBuffer,
    trimTimeWindow,
    channelSummary,
    latestChannelValues,
    thresholdStatus,
    detectThresholdEvents,
    detectGapEvents,
    rollingMeanSeries,
    rollingSdSeries,
    exponentialSmoothingSeries,
    minMaxDownsample,
    alignChannels,
    commonTimeWindow,
    eventRate,
    connectionUptime,
    dashboardSummary,
    buildSnapshot,
    StreamBuffer,
    stream,
    parseCsv,
    chartSvg,
    toCsv,
    ingest,
    ingestBatch,
    startDemo,
    stopDemo,
    pause,
    resume,
    replay,
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
