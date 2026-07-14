# Live Sensor and Instrument Visualization

Sustainable Catalyst Lab v0.25.2 adds an explicit, local-first
visualization and replay layer above the v0.25.0 instrumentation
platform and the v0.25.1 reliability layer.

## Visualization modes

1. Live multi-channel dashboard
2. Buffered time-series trends
3. Warning and action overlays
4. Event and quality timeline
5. Pause, playback, and replay
6. Channel comparison
7. Connection diagnostics
8. Export and research handoff

## Deterministic analysis

The 16-method analysis contract covers:

- Bounded ring-buffer appends
- Time-window trimming
- Channel summaries
- Latest channel snapshots
- Threshold status
- Threshold-transition events
- Missing-data gap events
- Rolling means
- Rolling standard deviations
- Exponential smoothing
- Min/max downsampling
- Time-based channel alignment
- Common time windows
- Event rates
- Connection uptime
- Complete dashboard summaries

## Adapter model

The browser does not silently open serial ports, MQTT brokers, or
network endpoints. A deliberate adapter supplies normalized records:

```javascript
window.SCLab.InstrumentationLiveVisualization.ingest({
  timestamp: Date.now() / 1000,
  channel: "temperature",
  value: 22.4,
  unit: "°C",
  qualityFlags: []
});
```

Batch adapters may use `ingestBatch(records)`.

## Focused shortcode

```text
[sc_lab_live_sensor_instrument_visualization]
```

## Browser API

```javascript
window.SCLab.InstrumentationLiveVisualization.status()
window.SCLab.InstrumentationLiveVisualization.ingest(record)
window.SCLab.InstrumentationLiveVisualization.ingestBatch(records)
window.SCLab.InstrumentationLiveVisualization.pause()
window.SCLab.InstrumentationLiveVisualization.resume()
window.SCLab.InstrumentationLiveVisualization.replay(records, {speed: 4})
window.SCLab.InstrumentationLiveVisualization.buildSnapshot(
  records,
  thresholds,
  maximumGapSeconds,
  connectionState
)
```

## WordPress REST

```text
GET  /wp-json/sc-lab/v1/compute/instrumentation/live/methods
GET  /wp-json/sc-lab/v1/compute/instrumentation/live/health
POST /wp-json/sc-lab/v1/compute/instrumentation/live/analyze
POST /wp-json/sc-lab/v1/compute/instrumentation/live/snapshot
POST /wp-json/sc-lab/v1/compute/instrumentation/live/events
POST /wp-json/sc-lab/v1/compute/instrumentation/live/replay
```

## FastAPI

```text
GET  /v1/instrumentation/live/methods
GET  /v1/instrumentation/live/health
POST /v1/instrumentation/live/analyze
POST /v1/instrumentation/live/snapshot
POST /v1/instrumentation/live/events
POST /v1/instrumentation/live/replay
```

## Boundaries

The module supports research, education, laboratory prototyping,
recorded-data replay, and non-clinical visualization. It is not a
validated monitoring system, clinical surveillance system, alarm
authority, or regulated control system.
