<?php
/**
 * Live instrumentation visualization REST engine.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Instrumentation_Live_REST_V0252 {
    const VERSION = '0.25.2';
    const ENGINE_VERSION = '0.25.0';
    const PRODUCTION_VERSION = '0.25.1';
    const NAMESPACE = 'sc-lab/v1';

    public static function boot() {
        add_action(
            'rest_api_init',
            array(__CLASS__, 'register_routes')
        );
    }

    private static function contract_path() {
        return dirname(__DIR__)
            . '/contracts/'
            . 'instrumentation-live-visualization-v0252.json';
    }

    public static function contract() {
        $path = self::contract_path();

        if (!is_file($path)) {
            return array(
                'version' => self::VERSION,
                'modes' => array(),
                'analysisMethods' => array(),
                'benchmarks' => array(),
                'channelTemplates' => array(),
                'connectionStates' => array(),
                'eventTypes' => array(),
            );
        }

        $decoded = json_decode(
            file_get_contents($path),
            true
        );

        return is_array($decoded)
            ? $decoded
            : array();
    }

    private static function finite($value, $label) {
        if (
            !is_numeric($value)
            || !is_finite((float) $value)
        ) {
            throw new InvalidArgumentException(
                $label . ' must be numerical and finite.'
            );
        }

        return (float) $value;
    }

    private static function positive($value, $label) {
        $number = self::finite($value, $label);

        if ($number <= 0.0) {
            throw new InvalidArgumentException(
                $label . ' must be greater than zero.'
            );
        }

        return $number;
    }

    private static function records($value, $label = 'records') {
        if (!is_array($value)) {
            throw new InvalidArgumentException(
                $label . ' must be an array.'
            );
        }

        $result = array();

        foreach ($value as $index => $record) {
            if (!is_array($record)) {
                throw new InvalidArgumentException(
                    $label . '[' . $index . '] must be an object.'
                );
            }

            $normalized = $record;
            $normalized['timestamp'] = self::finite(
                $record['timestamp'] ?? null,
                $label . '[' . $index . '].timestamp'
            );

            if (array_key_exists('value', $record)) {
                $normalized['value'] = self::finite(
                    $record['value'],
                    $label . '[' . $index . '].value'
                );
            }

            $result[] = $normalized;
        }

        return $result;
    }

    private static function values($value, $label = 'values') {
        if (!is_array($value) || count($value) === 0) {
            throw new InvalidArgumentException(
                $label . ' must be a non-empty array.'
            );
        }

        return array_map(
            static function ($item) use ($label) {
                return self::finite($item, $label);
            },
            $value
        );
    }

    private static function mean($values) {
        return array_sum($values) / count($values);
    }

    private static function sd($values) {
        if (count($values) < 2) {
            return 0.0;
        }

        $average = self::mean($values);
        $sum = 0.0;

        foreach ($values as $value) {
            $sum += ($value - $average) ** 2;
        }

        return sqrt($sum / (count($values) - 1));
    }

    public static function append_ring_buffer(
        $existing,
        $incoming,
        $maximum_points
    ) {
        $combined = array_merge(
            self::records($existing, 'existing'),
            self::records($incoming, 'incoming')
        );

        usort(
            $combined,
            static function ($left, $right) {
                return $left['timestamp'] <=> $right['timestamp'];
            }
        );

        $maximum = (int) self::positive(
            $maximum_points,
            'maximumPoints'
        );

        return array_slice($combined, -$maximum);
    }

    public static function trim_time_window(
        $points,
        $window_start,
        $window_end
    ) {
        $start = self::finite($window_start, 'windowStart');
        $end = self::finite($window_end, 'windowEnd');

        if ($end < $start) {
            throw new InvalidArgumentException(
                'windowEnd must be at least windowStart.'
            );
        }

        return array_values(
            array_filter(
                self::records($points, 'points'),
                static function ($point) use ($start, $end) {
                    return (
                        $point['timestamp'] >= $start
                        && $point['timestamp'] <= $end
                    );
                }
            )
        );
    }

    public static function channel_summary($raw_values) {
        $values = self::values($raw_values);
        $minimum = min($values);
        $maximum = max($values);

        return array(
            'count' => count($values),
            'mean' => self::mean($values),
            'standardDeviation' => self::sd($values),
            'minimum' => $minimum,
            'maximum' => $maximum,
            'range' => $maximum - $minimum,
            'latest' => $values[count($values) - 1],
        );
    }

    public static function latest_channel_values($raw_records) {
        $latest = array();

        foreach (self::records($raw_records) as $record) {
            $channel = (string) ($record['channel'] ?? '');

            if ($channel === '') {
                continue;
            }

            if (
                !isset($latest[$channel])
                || $record['timestamp']
                    >= $latest[$channel]['timestamp']
            ) {
                $latest[$channel] = $record;
            }
        }

        return $latest;
    }

    public static function threshold_status(
        $value,
        $warning_low,
        $warning_high,
        $action_low,
        $action_high
    ) {
        $number = self::finite($value, 'value');
        $wl = self::finite($warning_low, 'warningLow');
        $wh = self::finite($warning_high, 'warningHigh');
        $al = self::finite($action_low, 'actionLow');
        $ah = self::finite($action_high, 'actionHigh');

        if (!($al <= $wl && $wl <= $wh && $wh <= $ah)) {
            throw new InvalidArgumentException(
                'Thresholds must satisfy actionLow <= warningLow '
                . '<= warningHigh <= actionHigh.'
            );
        }

        if ($number < $al || $number > $ah) {
            return 'action';
        }

        if ($number < $wl || $number > $wh) {
            return 'warning';
        }

        return 'normal';
    }

    public static function detect_threshold_events(
        $raw_records,
        $thresholds
    ) {
        if (!is_array($thresholds)) {
            throw new InvalidArgumentException(
                'thresholds must be an object.'
            );
        }

        $events = array();
        $previous = array();

        foreach (self::records($raw_records) as $record) {
            $channel = (string) ($record['channel'] ?? '');

            if (
                $channel === ''
                || !isset($thresholds[$channel])
                || !is_array($thresholds[$channel])
            ) {
                continue;
            }

            $definition = $thresholds[$channel];
            $status = self::threshold_status(
                $record['value'] ?? null,
                $definition['warningLow'] ?? null,
                $definition['warningHigh'] ?? null,
                $definition['actionLow'] ?? null,
                $definition['actionHigh'] ?? null
            );

            if (
                $status !== 'normal'
                && $status !== ($previous[$channel] ?? null)
            ) {
                $events[] = array(
                    'type' => $status,
                    'channel' => $channel,
                    'timestamp' => $record['timestamp'],
                    'value' => $record['value'],
                    'message' => (
                        $channel
                        . ' entered '
                        . $status
                        . ' range.'
                    ),
                );
            }

            $previous[$channel] = $status;
        }

        return $events;
    }

    public static function detect_gap_events(
        $raw_records,
        $maximum_gap_seconds
    ) {
        $records = self::records($raw_records);
        $maximum = self::positive(
            $maximum_gap_seconds,
            'maximumGapSeconds'
        );

        usort(
            $records,
            static function ($left, $right) {
                $channel = strcmp(
                    (string) ($left['channel'] ?? ''),
                    (string) ($right['channel'] ?? '')
                );

                return $channel !== 0
                    ? $channel
                    : ($left['timestamp'] <=> $right['timestamp']);
            }
        );

        $events = array();
        $previous = array();

        foreach ($records as $record) {
            $channel = (string) ($record['channel'] ?? '');

            if ($channel === '') {
                continue;
            }

            if (array_key_exists($channel, $previous)) {
                $gap = (
                    $record['timestamp']
                    - $previous[$channel]
                );

                if ($gap > $maximum) {
                    $events[] = array(
                        'type' => 'gap',
                        'channel' => $channel,
                        'timestamp' => $record['timestamp'],
                        'gapSeconds' => $gap,
                    );
                }
            }

            $previous[$channel] = $record['timestamp'];
        }

        return $events;
    }

    public static function rolling_mean_series(
        $raw_values,
        $window_size
    ) {
        $values = self::values($raw_values);
        $window = (int) self::positive(
            $window_size,
            'windowSize'
        );
        $result = array();

        foreach ($values as $index => $value) {
            $slice = array_slice(
                $values,
                max(0, $index - $window + 1),
                min($window, $index + 1)
            );
            $result[] = self::mean($slice);
        }

        return $result;
    }

    public static function rolling_sd_series(
        $raw_values,
        $window_size
    ) {
        $values = self::values($raw_values);
        $window = (int) self::positive(
            $window_size,
            'windowSize'
        );
        $result = array();

        foreach ($values as $index => $value) {
            $slice = array_slice(
                $values,
                max(0, $index - $window + 1),
                min($window, $index + 1)
            );
            $result[] = self::sd($slice);
        }

        return $result;
    }

    public static function exponential_smoothing_series(
        $raw_values,
        $alpha
    ) {
        $values = self::values($raw_values);
        $weight = self::finite($alpha, 'alpha');

        if (!($weight > 0.0 && $weight <= 1.0)) {
            throw new InvalidArgumentException(
                'alpha must be greater than zero and at most one.'
            );
        }

        $smoothed = array($values[0]);

        for ($index = 1; $index < count($values); $index++) {
            $smoothed[] = (
                $weight * $values[$index]
                + (1 - $weight)
                    * $smoothed[count($smoothed) - 1]
            );
        }

        return $smoothed;
    }

    public static function min_max_downsample(
        $raw_points,
        $bucket_count
    ) {
        $points = self::records($raw_points, 'points');

        usort(
            $points,
            static function ($left, $right) {
                return $left['timestamp'] <=> $right['timestamp'];
            }
        );

        $buckets = (int) self::positive(
            $bucket_count,
            'bucketCount'
        );

        if ($buckets >= count($points)) {
            return $points;
        }

        $output = array();

        for ($bucket = 0; $bucket < $buckets; $bucket++) {
            $start = (int) floor(
                $bucket * count($points) / $buckets
            );
            $end = (int) floor(
                ($bucket + 1)
                * count($points)
                / $buckets
            );
            $group = array_slice(
                $points,
                $start,
                max(1, $end - $start)
            );
            $minimum = $group[0];
            $maximum = $group[0];

            foreach ($group as $point) {
                if ($point['value'] < $minimum['value']) {
                    $minimum = $point;
                }
                if ($point['value'] > $maximum['value']) {
                    $maximum = $point;
                }
            }

            $pair = (
                $minimum == $maximum
                    ? array($minimum)
                    : array($minimum, $maximum)
            );

            usort(
                $pair,
                static function ($left, $right) {
                    return $left['timestamp'] <=> $right['timestamp'];
                }
            );

            $output = array_merge($output, $pair);
        }

        return $output;
    }

    public static function align_channels(
        $reference,
        $comparison,
        $tolerance_seconds
    ) {
        $left = self::records($reference, 'reference');
        $right = self::records($comparison, 'comparison');
        $tolerance = self::positive(
            $tolerance_seconds,
            'toleranceSeconds'
        );

        usort(
            $left,
            static function ($a, $b) {
                return $a['timestamp'] <=> $b['timestamp'];
            }
        );
        usort(
            $right,
            static function ($a, $b) {
                return $a['timestamp'] <=> $b['timestamp'];
            }
        );

        $used = array();
        $matches = array();

        foreach ($left as $reference_point) {
            $best_index = null;
            $best_delta = null;

            foreach ($right as $index => $point) {
                if (isset($used[$index])) {
                    continue;
                }

                $delta = abs(
                    $point['timestamp']
                    - $reference_point['timestamp']
                );

                if (
                    $delta <= $tolerance
                    && (
                        $best_delta === null
                        || $delta < $best_delta
                    )
                ) {
                    $best_delta = $delta;
                    $best_index = $index;
                }
            }

            if ($best_index === null) {
                continue;
            }

            $used[$best_index] = true;
            $point = $right[$best_index];
            $matches[] = array(
                'timestamp' => $reference_point['timestamp'],
                'referenceValue' => $reference_point['value'],
                'comparisonValue' => $point['value'],
                'timeDeltaSeconds' => (
                    $point['timestamp']
                    - $reference_point['timestamp']
                ),
            );
        }

        return $matches;
    }

    public static function common_time_window($series) {
        if (!is_array($series) || count($series) === 0) {
            throw new InvalidArgumentException(
                'series must be a non-empty array.'
            );
        }

        $starts = array();
        $ends = array();

        foreach ($series as $index => $raw_points) {
            $points = self::records(
                $raw_points,
                'series[' . $index . ']'
            );

            if (count($points) === 0) {
                return array(
                    'start' => null,
                    'end' => null,
                    'durationSeconds' => 0.0,
                );
            }

            $timestamps = array_column(
                $points,
                'timestamp'
            );
            $starts[] = min($timestamps);
            $ends[] = max($timestamps);
        }

        $start = max($starts);
        $end = min($ends);

        return array(
            'start' => $start,
            'end' => $end,
            'durationSeconds' => max(
                0.0,
                $end - $start
            ),
        );
    }

    public static function event_rate(
        $event_count,
        $duration_seconds
    ) {
        return (
            self::finite($event_count, 'eventCount')
            * 60
            / self::positive(
                $duration_seconds,
                'durationSeconds'
            )
        );
    }

    public static function connection_uptime(
        $online_seconds,
        $total_seconds
    ) {
        return max(
            0.0,
            min(
                100.0,
                self::finite(
                    $online_seconds,
                    'onlineSeconds'
                )
                / self::positive(
                    $total_seconds,
                    'totalSeconds'
                )
                * 100
            )
        );
    }

    public static function dashboard_summary(
        $raw_records,
        $events,
        $connection_state
    ) {
        if (!is_array($events)) {
            throw new InvalidArgumentException(
                'events must be an array.'
            );
        }

        $records = self::records($raw_records);
        $grouped = array();

        foreach ($records as $record) {
            $channel = (string) ($record['channel'] ?? '');

            if ($channel === '') {
                continue;
            }

            if (!isset($grouped[$channel])) {
                $grouped[$channel] = array();
            }

            $grouped[$channel][] = $record['value'];
        }

        $channels = array();

        foreach ($grouped as $channel => $values) {
            $channels[$channel] = self::channel_summary(
                $values
            );
        }

        $type_counts = array();

        foreach ($events as $event) {
            $type = (string) ($event['type'] ?? '');

            if ($type !== '') {
                $type_counts[$type] = (
                    ($type_counts[$type] ?? 0) + 1
                );
            }
        }

        return array(
            'recordCount' => count($records),
            'channelCount' => count($grouped),
            'eventCount' => count($events),
            'connectionState' => (string) $connection_state,
            'latest' => self::latest_channel_values(
                $records
            ),
            'channels' => $channels,
            'eventTypeCounts' => $type_counts,
        );
    }

    public static function execute(
        $method_id,
        $inputs
    ) {
        $i = is_array($inputs)
            ? $inputs
            : array();

        switch ($method_id) {
            case 'append-ring-buffer':
                $value = self::append_ring_buffer(
                    $i['existing'] ?? array(),
                    $i['incoming'] ?? array(),
                    $i['maximumPoints'] ?? null
                );
                break;
            case 'trim-time-window':
                $value = self::trim_time_window(
                    $i['points'] ?? array(),
                    $i['windowStart'] ?? null,
                    $i['windowEnd'] ?? null
                );
                break;
            case 'channel-summary':
                $value = self::channel_summary(
                    $i['values'] ?? null
                );
                break;
            case 'latest-channel-values':
                $value = self::latest_channel_values(
                    $i['records'] ?? array()
                );
                break;
            case 'threshold-status':
                $value = self::threshold_status(
                    $i['value'] ?? null,
                    $i['warningLow'] ?? null,
                    $i['warningHigh'] ?? null,
                    $i['actionLow'] ?? null,
                    $i['actionHigh'] ?? null
                );
                break;
            case 'detect-threshold-events':
                $value = self::detect_threshold_events(
                    $i['records'] ?? array(),
                    $i['thresholds'] ?? array()
                );
                break;
            case 'detect-gap-events':
                $value = self::detect_gap_events(
                    $i['records'] ?? array(),
                    $i['maximumGapSeconds'] ?? null
                );
                break;
            case 'rolling-mean-series':
                $value = self::rolling_mean_series(
                    $i['values'] ?? null,
                    $i['windowSize'] ?? null
                );
                break;
            case 'rolling-sd-series':
                $value = self::rolling_sd_series(
                    $i['values'] ?? null,
                    $i['windowSize'] ?? null
                );
                break;
            case 'exponential-smoothing-series':
                $value = self::exponential_smoothing_series(
                    $i['values'] ?? null,
                    $i['alpha'] ?? null
                );
                break;
            case 'min-max-downsample':
                $value = self::min_max_downsample(
                    $i['points'] ?? array(),
                    $i['bucketCount'] ?? null
                );
                break;
            case 'align-channels':
                $value = self::align_channels(
                    $i['reference'] ?? array(),
                    $i['comparison'] ?? array(),
                    $i['toleranceSeconds'] ?? null
                );
                break;
            case 'common-time-window':
                $value = self::common_time_window(
                    $i['series'] ?? array()
                );
                break;
            case 'event-rate':
                $value = self::event_rate(
                    $i['eventCount'] ?? null,
                    $i['durationSeconds'] ?? null
                );
                break;
            case 'connection-uptime':
                $value = self::connection_uptime(
                    $i['onlineSeconds'] ?? null,
                    $i['totalSeconds'] ?? null
                );
                break;
            case 'dashboard-summary':
                $value = self::dashboard_summary(
                    $i['records'] ?? array(),
                    $i['events'] ?? array(),
                    $i['connectionState'] ?? 'disconnected'
                );
                break;
            default:
                throw new InvalidArgumentException(
                    'Unknown live visualization method: '
                    . $method_id
                );
        }

        return array(
            'schema' =>
                'sc-lab-instrumentation-live-analysis/1.0',
            'version' => self::VERSION,
            'methodId' => $method_id,
            'inputs' => $inputs,
            'value' => $value,
        );
    }

    public static function build_snapshot(
        $records,
        $thresholds = array(),
        $maximum_gap_seconds = 10,
        $connection_state = 'disconnected'
    ) {
        $normalized = self::records($records);
        $events = array_merge(
            self::detect_threshold_events(
                $normalized,
                $thresholds
            ),
            count($normalized)
                ? self::detect_gap_events(
                    $normalized,
                    $maximum_gap_seconds
                )
                : array()
        );

        return array(
            'schema' =>
                'sc-lab-instrumentation-live-snapshot/1.0',
            'version' => self::VERSION,
            'createdFromRecordCount' => count($normalized),
            'events' => $events,
            'summary' => self::dashboard_summary(
                $normalized,
                $events,
                $connection_state
            ),
            'records' => $normalized,
        );
    }

    public static function health_payload() {
        $contract = self::contract();
        $ready = (
            ($contract['version'] ?? null)
                === self::VERSION
            && count($contract['modes'] ?? array()) === 8
            && count(
                $contract['analysisMethods'] ?? array()
            ) === 16
            && count(
                $contract['benchmarks'] ?? array()
            ) === 16
            && count(
                $contract['channelTemplates'] ?? array()
            ) === 8
            && count(
                $contract['connectionStates'] ?? array()
            ) === 8
            && count(
                $contract['eventTypes'] ?? array()
            ) === 8
        );

        return array(
            'ok' => $ready,
            'status' => $ready
                ? 'ready'
                : 'contract-incomplete',
            'release' => self::VERSION,
            'modeCount' => count(
                $contract['modes'] ?? array()
            ),
            'analysisMethodCount' => count(
                $contract['analysisMethods'] ?? array()
            ),
            'benchmarkCount' => count(
                $contract['benchmarks'] ?? array()
            ),
            'channelTemplateCount' => count(
                $contract['channelTemplates'] ?? array()
            ),
            'connectionStateCount' => count(
                $contract['connectionStates'] ?? array()
            ),
            'eventTypeCount' => count(
                $contract['eventTypes'] ?? array()
            ),
            'preservedEngine' =>
                $contract['preservedEngine'] ?? array(),
            'productionLayer' =>
                $contract['productionLayer'] ?? array(),
            'boundaries' =>
                $contract['responsibleUse']['boundaries']
                    ?? array(),
        );
    }

    public static function register_routes() {
        register_rest_route(
            self::NAMESPACE,
            '/compute/instrumentation/live/methods',
            array(
                'methods' => 'GET',
                'callback' =>
                    array(__CLASS__, 'methods_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/instrumentation/live/health',
            array(
                'methods' => 'GET',
                'callback' =>
                    array(__CLASS__, 'health_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/instrumentation/live/analyze',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'analyze_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/instrumentation/live/snapshot',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'snapshot_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/instrumentation/live/events',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'events_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/instrumentation/live/replay',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'replay_response'),
                'permission_callback' => '__return_true',
            )
        );
    }

    public static function methods_response() {
        return rest_ensure_response(
            self::contract()
        );
    }

    public static function health_response() {
        return rest_ensure_response(
            self::health_payload()
        );
    }

    public static function analyze_response($request) {
        try {
            $payload = $request->get_json_params();

            return rest_ensure_response(
                self::execute(
                    (string) ($payload['methodId'] ?? ''),
                    $payload['inputs'] ?? array()
                )
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_v0252_live_analysis_error',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function snapshot_response($request) {
        try {
            $payload = $request->get_json_params();

            return rest_ensure_response(
                self::build_snapshot(
                    $payload['records'] ?? array(),
                    $payload['thresholds'] ?? array(),
                    $payload['maximumGapSeconds'] ?? 10,
                    $payload['connectionState']
                        ?? 'disconnected'
                )
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_v0252_live_snapshot_error',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function events_response($request) {
        $response = self::snapshot_response($request);

        if (is_wp_error($response)) {
            return $response;
        }

        $data = $response->get_data();

        return rest_ensure_response(
            array(
                'schema' =>
                    'sc-lab-instrumentation-live-events/1.0',
                'version' => self::VERSION,
                'events' => $data['events'],
                'eventCount' => count($data['events']),
            )
        );
    }

    public static function replay_response($request) {
        $payload = $request->get_json_params();
        $speed = self::positive(
            $payload['speed'] ?? 1,
            'speed'
        );

        return rest_ensure_response(
            array(
                'schema' =>
                    'sc-lab-instrumentation-replay-plan/1.0',
                'version' => self::VERSION,
                'recordCount' => count(
                    $payload['records'] ?? array()
                ),
                'speed' => $speed,
                'records' =>
                    $payload['records'] ?? array(),
            )
        );
    }
}

SC_Lab_Instrumentation_Live_REST_V0252::boot();
