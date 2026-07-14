<?php
/**
 * Instrumentation validation and custody REST engine.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Instrumentation_Validation_REST_V0253 {
    const VERSION = '0.25.3';
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
            . 'instrumentation-validation-custody-v0253.json';
    }

    public static function contract() {
        $path = self::contract_path();

        if (!is_file($path)) {
            return array();
        }

        $decoded = json_decode(
            file_get_contents($path),
            true
        );

        return is_array($decoded)
            ? $decoded
            : array();
    }

    private static function canonicalize($value) {
        if (!is_array($value)) {
            return $value;
        }

        $keys = array_keys($value);
        $is_list = $keys === range(
            0,
            count($keys) - 1
        );

        if ($is_list) {
            return array_map(
                array(__CLASS__, 'canonicalize'),
                $value
            );
        }

        ksort($value);

        foreach ($value as $key => $item) {
            $value[$key] = self::canonicalize($item);
        }

        return $value;
    }

    private static function canonical_json($value) {
        return wp_json_encode(
            self::canonicalize($value),
            JSON_UNESCAPED_SLASHES
            | JSON_UNESCAPED_UNICODE
        );
    }

    private static function sha256($value) {
        return hash(
            'sha256',
            (string) $value
        );
    }

    private static function finite($value, $label) {
        if (
            !is_numeric($value)
            || !is_finite((float) $value)
        ) {
            throw new InvalidArgumentException(
                $label
                . ' must be numerical and finite.'
            );
        }

        return (float) $value;
    }

    private static function positive($value, $label) {
        $number = self::finite($value, $label);

        if ($number <= 0.0) {
            throw new InvalidArgumentException(
                $label
                . ' must be greater than zero.'
            );
        }

        return $number;
    }

    private static function values(
        $value,
        $label,
        $minimum = 1
    ) {
        if (
            !is_array($value)
            || count($value) < $minimum
        ) {
            throw new InvalidArgumentException(
                $label
                . ' must contain at least '
                . $minimum
                . ' values.'
            );
        }

        $numbers = array();

        foreach ($value as $index => $item) {
            $numbers[] = self::finite(
                $item,
                $label . '[' . $index . ']'
            );
        }

        return $numbers;
    }

    private static function paired($left, $right) {
        $measured = self::values(
            $left,
            'measuredValues'
        );
        $reference = self::values(
            $right,
            'referenceValues'
        );

        if (count($measured) !== count($reference)) {
            throw new InvalidArgumentException(
                'measuredValues and referenceValues '
                . 'must have equal length.'
            );
        }

        return array($measured, $reference);
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

        return sqrt(
            $sum / (count($values) - 1)
        );
    }

    public static function calibration_absolute_error(
        $measured,
        $reference
    ) {
        return abs(
            self::finite($measured, 'measured')
            - self::finite($reference, 'reference')
        );
    }

    public static function calibration_percent_error(
        $measured,
        $reference
    ) {
        return self::calibration_absolute_error(
            $measured,
            $reference
        )
            / abs(
                self::positive(
                    $reference,
                    'reference'
                )
            )
            * 100;
    }

    public static function calibration_bias(
        $measured_values,
        $reference_values
    ) {
        list($measured, $reference) =
            self::paired(
                $measured_values,
                $reference_values
            );
        $differences = array();

        foreach ($measured as $index => $value) {
            $differences[] = (
                $value - $reference[$index]
            );
        }

        return self::mean($differences);
    }

    public static function calibration_rmse(
        $measured_values,
        $reference_values
    ) {
        list($measured, $reference) =
            self::paired(
                $measured_values,
                $reference_values
            );
        $squares = array();

        foreach ($measured as $index => $value) {
            $difference = (
                $value - $reference[$index]
            );
            $squares[] = (
                $difference * $difference
            );
        }

        return sqrt(self::mean($squares));
    }

    public static function calibration_linearity_r2(
        $reference_values,
        $measured_values
    ) {
        list($reference, $measured) =
            self::paired(
                $reference_values,
                $measured_values
            );
        $x_mean = self::mean($reference);
        $y_mean = self::mean($measured);
        $numerator = 0.0;
        $x_square = 0.0;
        $y_square = 0.0;

        foreach (
            $reference
            as $index => $x_value
        ) {
            $x_delta = $x_value - $x_mean;
            $y_delta =
                $measured[$index] - $y_mean;
            $numerator += (
                $x_delta * $y_delta
            );
            $x_square += (
                $x_delta * $x_delta
            );
            $y_square += (
                $y_delta * $y_delta
            );
        }

        if (
            $x_square == 0.0
            || $y_square == 0.0
        ) {
            throw new InvalidArgumentException(
                'Linearity requires non-constant '
                . 'measured and reference values.'
            );
        }

        $correlation = (
            $numerator
            / sqrt($x_square * $y_square)
        );

        return $correlation * $correlation;
    }

    public static function repeatability_cv($raw_values) {
        $values = self::values(
            $raw_values,
            'values',
            2
        );
        $average = self::mean($values);

        if ($average == 0.0) {
            throw new InvalidArgumentException(
                'repeatability CV requires '
                . 'a non-zero mean.'
            );
        }

        return (
            self::sd($values)
            / abs($average)
            * 100
        );
    }

    public static function acceptance_window_status(
        $value,
        $target,
        $warning_tolerance,
        $action_tolerance
    ) {
        $delta = abs(
            self::finite($value, 'value')
            - self::finite($target, 'target')
        );
        $warning = self::positive(
            $warning_tolerance,
            'warningTolerance'
        );
        $action = self::positive(
            $action_tolerance,
            'actionTolerance'
        );

        if ($action < $warning) {
            throw new InvalidArgumentException(
                'actionTolerance must be at least '
                . 'warningTolerance.'
            );
        }

        if ($delta > $action) {
            return 'action';
        }

        if ($delta > $warning) {
            return 'warning';
        }

        return 'accepted';
    }

    private static function due_state(
        $elapsed,
        $interval,
        $warning_lead
    ) {
        $days = self::finite(
            $elapsed,
            'elapsedDays'
        );
        $limit = self::positive(
            $interval,
            'intervalDays'
        );
        $lead = max(
            0.0,
            self::finite(
                $warning_lead,
                'warningLeadDays'
            )
        );

        if ($days > $limit) {
            return 'overdue';
        }

        if (
            $days
            >= max(0.0, $limit - $lead)
        ) {
            return 'due-soon';
        }

        return 'current';
    }

    public static function measurement_completeness(
        $present_count,
        $expected_count
    ) {
        return max(
            0.0,
            min(
                100.0,
                self::finite(
                    $present_count,
                    'presentCount'
                )
                / self::positive(
                    $expected_count,
                    'expectedCount'
                )
                * 100
            )
        );
    }

    public static function quality_flag_rate(
        $flagged_count,
        $total_count
    ) {
        return max(
            0.0,
            min(
                100.0,
                self::finite(
                    $flagged_count,
                    'flaggedCount'
                )
                / self::positive(
                    $total_count,
                    'totalCount'
                )
                * 100
            )
        );
    }

    public static function custody_sequence_status(
        $events
    ) {
        if (!is_array($events)) {
            throw new InvalidArgumentException(
                'events must be an array.'
            );
        }

        $previous_hash = '';
        $previous_timestamp = null;
        $problems = array();

        foreach ($events as $index => $event) {
            if (!is_array($event)) {
                $problems[] =
                    'event-'
                    . ($index + 1)
                    . '-not-object';
                continue;
            }

            $timestamp = self::finite(
                $event['timestamp'] ?? null,
                'events[' . $index . '].timestamp'
            );

            if (
                $previous_timestamp !== null
                && $timestamp < $previous_timestamp
            ) {
                $problems[] =
                    'event-'
                    . ($index + 1)
                    . '-timestamp-order';
            }

            if (
                (string) (
                    $event['previousHash'] ?? ''
                )
                !== $previous_hash
            ) {
                $problems[] =
                    'event-'
                    . ($index + 1)
                    . '-parent-hash';
            }

            $event_hash = (string) (
                $event['eventHash'] ?? ''
            );

            if ($event_hash === '') {
                $problems[] =
                    'event-'
                    . ($index + 1)
                    . '-missing-hash';
            }

            $previous_hash = $event_hash;
            $previous_timestamp = $timestamp;
        }

        return array(
            'valid' => count($problems) === 0,
            'eventCount' => count($events),
            'problems' => $problems,
            'headHash' => $previous_hash,
        );
    }

    public static function validation_score(
        $profile_scores,
        $weights = array()
    ) {
        if (
            !is_array($profile_scores)
            || count($profile_scores) === 0
        ) {
            throw new InvalidArgumentException(
                'profileScores must be '
                . 'a non-empty object.'
            );
        }

        $numerator = 0.0;
        $denominator = 0.0;

        foreach (
            $profile_scores
            as $profile_id => $raw_score
        ) {
            $score = max(
                0.0,
                min(
                    100.0,
                    self::finite(
                        $raw_score,
                        $profile_id
                    )
                )
            );
            $weight = max(
                0.0,
                self::finite(
                    $weights[$profile_id] ?? 1,
                    'weight:' . $profile_id
                )
            );
            $numerator += $score * $weight;
            $denominator += $weight;
        }

        if ($denominator == 0.0) {
            throw new InvalidArgumentException(
                'At least one validation weight '
                . 'must be positive.'
            );
        }

        return $numerator / $denominator;
    }

    public static function validation_disposition(
        $score,
        $critical_failure_count,
        $open_deviation_count,
        $expired_record_count
    ) {
        $value = self::finite($score, 'score');
        $critical = (int) self::finite(
            $critical_failure_count,
            'criticalFailureCount'
        );
        $deviations = (int) self::finite(
            $open_deviation_count,
            'openDeviationCount'
        );
        $expired = (int) self::finite(
            $expired_record_count,
            'expiredRecordCount'
        );

        if ($critical > 0) {
            return 'rejected';
        }

        if ($expired > 0 || $value < 70) {
            return 'hold';
        }

        if ($value < 85 || $deviations > 0) {
            return 'conditionally-accepted';
        }

        return 'accepted';
    }

    public static function execute(
        $method_id,
        $inputs
    ) {
        $i = is_array($inputs)
            ? $inputs
            : array();

        switch ($method_id) {
            case 'calibration-absolute-error':
                $value =
                    self::calibration_absolute_error(
                        $i['measured'] ?? null,
                        $i['reference'] ?? null
                    );
                break;

            case 'calibration-percent-error':
                $value =
                    self::calibration_percent_error(
                        $i['measured'] ?? null,
                        $i['reference'] ?? null
                    );
                break;

            case 'calibration-bias':
                $value = self::calibration_bias(
                    $i['measuredValues'] ?? null,
                    $i['referenceValues'] ?? null
                );
                break;

            case 'calibration-rmse':
                $value = self::calibration_rmse(
                    $i['measuredValues'] ?? null,
                    $i['referenceValues'] ?? null
                );
                break;

            case 'calibration-linearity-r2':
                $value =
                    self::calibration_linearity_r2(
                        $i['referenceValues'] ?? null,
                        $i['measuredValues'] ?? null
                    );
                break;

            case 'repeatability-cv':
                $value = self::repeatability_cv(
                    $i['values'] ?? null
                );
                break;

            case 'acceptance-window-status':
                $value =
                    self::acceptance_window_status(
                        $i['value'] ?? null,
                        $i['target'] ?? null,
                        $i['warningTolerance']
                            ?? null,
                        $i['actionTolerance']
                            ?? null
                    );
                break;

            case 'calibration-due-state':
                $value = self::due_state(
                    $i['daysSinceCalibration']
                        ?? null,
                    $i['calibrationIntervalDays']
                        ?? null,
                    $i['warningLeadDays'] ?? null
                );
                break;

            case 'maintenance-due-state':
                $value = self::due_state(
                    $i['daysSinceMaintenance']
                        ?? null,
                    $i['maintenanceIntervalDays']
                        ?? null,
                    $i['warningLeadDays'] ?? null
                );
                break;

            case 'measurement-completeness':
                $value =
                    self::measurement_completeness(
                        $i['presentCount'] ?? null,
                        $i['expectedCount'] ?? null
                    );
                break;

            case 'quality-flag-rate':
                $value = self::quality_flag_rate(
                    $i['flaggedCount'] ?? null,
                    $i['totalCount'] ?? null
                );
                break;

            case 'custody-completeness':
                $value =
                    self::measurement_completeness(
                        $i['completeEventCount']
                            ?? null,
                        $i['totalEventCount'] ?? null
                    );
                break;

            case 'custody-sequence-status':
                $value =
                    self::custody_sequence_status(
                        $i['events'] ?? null
                    );
                break;

            case 'deviation-rate':
                $value = (
                    self::finite(
                        $i['deviationCount'] ?? null,
                        'deviationCount'
                    )
                    / self::positive(
                        $i['reviewedItemCount']
                            ?? null,
                        'reviewedItemCount'
                    )
                    * 100
                );
                break;

            case 'validation-score':
                $value = self::validation_score(
                    $i['profileScores'] ?? null,
                    $i['weights'] ?? array()
                );
                break;

            case 'validation-disposition':
                $value =
                    self::validation_disposition(
                        $i['score'] ?? null,
                        $i['criticalFailureCount']
                            ?? null,
                        $i['openDeviationCount']
                            ?? null,
                        $i['expiredRecordCount']
                            ?? null
                    );
                break;

            default:
                throw new InvalidArgumentException(
                    'Unknown instrumentation '
                    . 'validation method: '
                    . $method_id
                );
        }

        return array(
            'schema' =>
                'sc-lab-instrumentation-validation-result/1.0',
            'version' => self::VERSION,
            'methodId' => $method_id,
            'inputs' => $inputs,
            'value' => $value,
        );
    }

    public static function create_manifest(
        $components,
        $metadata = array()
    ) {
        if (
            !is_array($components)
            || count($components) === 0
        ) {
            throw new InvalidArgumentException(
                'components must be '
                . 'a non-empty object.'
            );
        }

        ksort($components);
        $hashes = array();

        foreach ($components as $key => $value) {
            $hashes[$key] = self::sha256(
                self::canonical_json($value)
            );
        }

        $manifest = array(
            'schema' =>
                'sc-lab-instrumentation-validation-manifest/1.0',
            'version' => self::VERSION,
            'components' => $components,
            'componentHashes' => $hashes,
            'metadata' => $metadata,
        );

        $manifest['manifestHash'] =
            self::sha256(
                self::canonical_json($manifest)
            );

        return $manifest;
    }

    public static function create_custody_event(
        $sample_id,
        $action,
        $actor,
        $location,
        $timestamp,
        $previous_hash = '',
        $metadata = array()
    ) {
        $event = array(
            'schema' =>
                'sc-lab-instrumentation-custody-event/1.0',
            'version' => self::VERSION,
            'sampleId' => (string) $sample_id,
            'action' => (string) $action,
            'actor' => (string) $actor,
            'location' => (string) $location,
            'timestamp' => self::finite(
                $timestamp,
                'timestamp'
            ),
            'previousHash' =>
                (string) $previous_hash,
            'metadata' => $metadata,
        );

        $event['eventHash'] = self::sha256(
            self::canonical_json($event)
        );

        return $event;
    }

    public static function verify_custody_chain(
        $events
    ) {
        if (!is_array($events)) {
            throw new InvalidArgumentException(
                'events must be an array.'
            );
        }

        $previous_hash = '';
        $problems = array();

        foreach ($events as $index => $event) {
            if (!is_array($event)) {
                $problems[] =
                    'event-'
                    . ($index + 1)
                    . '-not-object';
                continue;
            }

            $stored_hash = (string) (
                $event['eventHash'] ?? ''
            );
            $payload = $event;
            unset($payload['eventHash']);
            $calculated_hash = self::sha256(
                self::canonical_json($payload)
            );

            if ($stored_hash !== $calculated_hash) {
                $problems[] =
                    'event-'
                    . ($index + 1)
                    . '-hash';
            }

            if (
                (string) (
                    $event['previousHash'] ?? ''
                )
                !== $previous_hash
            ) {
                $problems[] =
                    'event-'
                    . ($index + 1)
                    . '-chain';
            }

            $previous_hash = $stored_hash;
        }

        return array(
            'valid' => count($problems) === 0,
            'eventCount' => count($events),
            'headHash' => $previous_hash,
            'problems' => $problems,
        );
    }

    public static function create_dossier(
        $profile_results,
        $manifest,
        $custody_events,
        $deviations,
        $metadata = array()
    ) {
        $scores = array();
        $critical = 0;
        $expired = 0;

        foreach (
            $profile_results
            as $profile_id => $result
        ) {
            $scores[$profile_id] = (float) (
                $result['score'] ?? 0
            );

            if (!empty($result['criticalFailure'])) {
                $critical++;
            }

            if (!empty($result['expired'])) {
                $expired++;
            }
        }

        $score = self::validation_score(
            $scores
        );
        $open_deviations = count(
            array_filter(
                $deviations,
                static function ($deviation) {
                    return empty(
                        $deviation['closed']
                    );
                }
            )
        );
        $disposition =
            self::validation_disposition(
                $score,
                $critical,
                $open_deviations,
                $expired
            );

        $dossier = array(
            'schema' =>
                'sc-lab-instrumentation-validation-dossier/1.0',
            'version' => self::VERSION,
            'profileResults' => $profile_results,
            'validationScore' => $score,
            'disposition' => $disposition,
            'manifest' => $manifest,
            'custodyVerification' =>
                self::verify_custody_chain(
                    $custody_events
                ),
            'deviations' => $deviations,
            'metadata' => $metadata,
        );

        $dossier['dossierHash'] = self::sha256(
            self::canonical_json($dossier)
        );

        return $dossier;
    }

    public static function health_payload() {
        $contract = self::contract();
        $ready = (
            ($contract['version'] ?? null)
                === self::VERSION
            && count(
                $contract['validationProfiles']
                    ?? array()
            ) === 8
            && count(
                $contract['acceptanceStates']
                    ?? array()
            ) === 8
            && count(
                $contract['provenanceEventTypes']
                    ?? array()
            ) === 8
            && count(
                $contract['deviationTypes']
                    ?? array()
            ) === 8
            && count(
                $contract['analysisMethods']
                    ?? array()
            ) === 16
            && count(
                $contract['benchmarks']
                    ?? array()
            ) === 16
        );

        return array(
            'ok' => $ready,
            'status' => $ready
                ? 'ready'
                : 'contract-incomplete',
            'release' => self::VERSION,
            'validationProfileCount' => count(
                $contract['validationProfiles']
                    ?? array()
            ),
            'acceptanceStateCount' => count(
                $contract['acceptanceStates']
                    ?? array()
            ),
            'eventTypeCount' => count(
                $contract['provenanceEventTypes']
                    ?? array()
            ),
            'deviationTypeCount' => count(
                $contract['deviationTypes']
                    ?? array()
            ),
            'analysisMethodCount' => count(
                $contract['analysisMethods']
                    ?? array()
            ),
            'benchmarkCount' => count(
                $contract['benchmarks']
                    ?? array()
            ),
            'preservedInstrumentation' =>
                $contract['preservedInstrumentation']
                    ?? array(),
            'liveLayer' =>
                $contract['liveLayer']
                    ?? array(),
            'boundaries' =>
                $contract['responsibleUse']['boundaries']
                    ?? array(),
        );
    }

    public static function register_routes() {
        $routes = array(
            '/compute/instrumentation/validation/profiles'
                => array(
                    'methods' => 'GET',
                    'callback' => array(
                        __CLASS__,
                        'profiles_response',
                    ),
                ),
            '/compute/instrumentation/validation/health'
                => array(
                    'methods' => 'GET',
                    'callback' => array(
                        __CLASS__,
                        'health_response',
                    ),
                ),
            '/compute/instrumentation/validation/evaluate'
                => array(
                    'methods' => 'POST',
                    'callback' => array(
                        __CLASS__,
                        'evaluate_response',
                    ),
                ),
            '/compute/instrumentation/validation/manifest'
                => array(
                    'methods' => 'POST',
                    'callback' => array(
                        __CLASS__,
                        'manifest_response',
                    ),
                ),
            '/compute/instrumentation/custody/event'
                => array(
                    'methods' => 'POST',
                    'callback' => array(
                        __CLASS__,
                        'custody_event_response',
                    ),
                ),
            '/compute/instrumentation/custody/verify'
                => array(
                    'methods' => 'POST',
                    'callback' => array(
                        __CLASS__,
                        'verify_response',
                    ),
                ),
            '/compute/instrumentation/validation/dossier'
                => array(
                    'methods' => 'POST',
                    'callback' => array(
                        __CLASS__,
                        'dossier_response',
                    ),
                ),
        );

        foreach ($routes as $path => $definition) {
            register_rest_route(
                self::NAMESPACE,
                $path,
                array_merge(
                    $definition,
                    array(
                        'permission_callback'
                            => '__return_true',
                    )
                )
            );
        }
    }

    public static function profiles_response() {
        return rest_ensure_response(
            self::contract()
        );
    }

    public static function health_response() {
        return rest_ensure_response(
            self::health_payload()
        );
    }

    public static function evaluate_response($request) {
        try {
            $payload = $request->get_json_params();

            return rest_ensure_response(
                self::execute(
                    (string) (
                        $payload['methodId'] ?? ''
                    ),
                    $payload['inputs']
                        ?? array()
                )
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_v0253_validation_error',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function manifest_response($request) {
        try {
            $payload = $request->get_json_params();

            return rest_ensure_response(
                self::create_manifest(
                    $payload['components']
                        ?? array(),
                    $payload['metadata']
                        ?? array()
                )
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_v0253_manifest_error',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function custody_event_response(
        $request
    ) {
        try {
            $payload = $request->get_json_params();

            return rest_ensure_response(
                self::create_custody_event(
                    $payload['sampleId'] ?? '',
                    $payload['action'] ?? '',
                    $payload['actor'] ?? '',
                    $payload['location'] ?? '',
                    $payload['timestamp'] ?? null,
                    $payload['previousHash'] ?? '',
                    $payload['metadata']
                        ?? array()
                )
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_v0253_custody_event_error',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function verify_response($request) {
        try {
            $payload = $request->get_json_params();

            return rest_ensure_response(
                self::verify_custody_chain(
                    $payload['events'] ?? array()
                )
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_v0253_custody_verify_error',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function dossier_response($request) {
        try {
            $payload = $request->get_json_params();

            return rest_ensure_response(
                self::create_dossier(
                    $payload['profileResults']
                        ?? array(),
                    $payload['manifest']
                        ?? array(),
                    $payload['custodyEvents']
                        ?? array(),
                    $payload['deviations']
                        ?? array(),
                    $payload['metadata']
                        ?? array()
                )
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_v0253_dossier_error',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }
}

SC_Lab_Instrumentation_Validation_REST_V0253::boot();
