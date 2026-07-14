/**
 * Sustainable Catalyst Lab v0.25.2 explicit adapter example.
 *
 * Call `pushInstrumentRecord` from a deliberate serial/network bridge.
 * This file does not open a device or connection itself.
 */
export function pushInstrumentRecord(record) {
  const api =
    window.SCLab?.InstrumentationLiveVisualization;

  if (!api?.ingest) {
    throw new Error(
      "The Lab live instrumentation workspace is unavailable."
    );
  }

  return api.ingest({
    timestamp:
      Number(record.timestamp)
      || Date.now() / 1000,
    channel:
      String(record.channel || "custom"),
    value:
      Number(record.value),
    unit:
      String(record.unit || ""),
    qualityFlags:
      Array.isArray(record.qualityFlags)
        ? record.qualityFlags
        : [],
    instrumentId:
      record.instrumentId || null,
    sensorId:
      record.sensorId || null,
    sampleId:
      record.sampleId || null,
  });
}
