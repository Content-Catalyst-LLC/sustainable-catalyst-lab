<?php
/**
 * Molecular Analysis Validation and Provenance REST engine.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Molecular_Validation_REST_V0213 {
    const VERSION = '0.21.3';
    const NAMESPACE = 'sc-lab/v1';

    public static function boot() {
        add_action(
            'rest_api_init',
            array(__CLASS__, 'register_routes')
        );
    }

    public static function register_routes() {
        register_rest_route(
            self::NAMESPACE,
            '/compute/biochemistry/validation/profiles',
            array(
                'methods' => 'GET',
                'callback' =>
                    array(__CLASS__, 'profiles_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/biochemistry/validation/run',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'validation_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/biochemistry/provenance/record',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'provenance_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/biochemistry/provenance/verify',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'verify_response'),
                'permission_callback' => '__return_true',
            )
        );
    }

    private static function profiles_path() {
        return dirname(__DIR__)
            . '/contracts/'
            . 'molecular-analysis-validation-profiles-v0213.json';
    }

    public static function profiles() {
        $path = self::profiles_path();

        if (!is_file($path)) {
            throw new RuntimeException(
                'The molecular validation profile contract '
                . 'is missing.'
            );
        }

        $decoded = json_decode(
            file_get_contents($path),
            true
        );

        if (!is_array($decoded)) {
            throw new RuntimeException(
                'The molecular validation profile contract '
                . 'is invalid.'
            );
        }

        return $decoded;
    }

    private static function profile($profile_id) {
        $contract = self::profiles();

        foreach ($contract['profiles'] as $profile) {
            if ($profile['id'] === $profile_id) {
                return $profile;
            }
        }

        throw new InvalidArgumentException(
            'Unknown validation profile: ' . $profile_id
        );
    }

    private static function finite($value, $label) {
        if (!is_numeric($value)) {
            throw new InvalidArgumentException(
                $label . ' must be numerical.'
            );
        }

        $number = (float) $value;

        if (!is_finite($number)) {
            throw new InvalidArgumentException(
                $label . ' must be finite.'
            );
        }

        return $number;
    }

    private static function mean($values) {
        return array_sum($values) / count($values);
    }

    private static function standard_deviation($values) {
        if (count($values) < 2) {
            return 0.0;
        }

        $mean = self::mean($values);
        $sum = 0.0;

        foreach ($values as $value) {
            $sum += pow($value - $mean, 2);
        }

        return sqrt($sum / (count($values) - 1));
    }

    private static function regression($points) {
        if (count($points) < 2) {
            throw new InvalidArgumentException(
                'At least two calibration points are required.'
            );
        }

        $xs = array_column($points, 'x');
        $ys = array_column($points, 'y');
        $x_mean = self::mean($xs);
        $y_mean = self::mean($ys);
        $numerator = 0.0;
        $denominator = 0.0;

        foreach ($points as $point) {
            $numerator +=
                ($point['x'] - $x_mean)
                * ($point['y'] - $y_mean);
            $denominator +=
                pow($point['x'] - $x_mean, 2);
        }

        if ($denominator == 0.0) {
            throw new InvalidArgumentException(
                'Calibration concentrations must vary.'
            );
        }

        $slope = $numerator / $denominator;
        $intercept = $y_mean - ($slope * $x_mean);
        $total = 0.0;
        $residual = 0.0;

        foreach ($points as $point) {
            $fitted =
                ($slope * $point['x']) + $intercept;
            $total += pow($point['y'] - $y_mean, 2);
            $residual += pow($point['y'] - $fitted, 2);
        }

        return array(
            'slope' => $slope,
            'intercept' => $intercept,
            'rSquared' =>
                $total == 0.0
                    ? 1.0
                    : 1.0 - ($residual / $total),
        );
    }

    private static function check(
        $id,
        $label,
        $value,
        $operator,
        $limit,
        $passed,
        $unit = ''
    ) {
        return array(
            'id' => $id,
            'label' => $label,
            'value' => $value,
            'operator' => $operator,
            'limit' => $limit,
            'unit' => $unit,
            'passed' => (bool) $passed,
            'status' => $passed ? 'pass' : 'fail',
        );
    }

    private static function required_columns(
        $profile,
        $rows
    ) {
        if (!is_array($rows) || !$rows) {
            throw new InvalidArgumentException(
                'Validation requires at least one data row.'
            );
        }

        foreach ($profile['requiredColumns'] as $column) {
            if (
                !is_array($rows[0])
                || !array_key_exists($column, $rows[0])
            ) {
                throw new InvalidArgumentException(
                    'Required data column is missing: '
                    . $column
                );
            }
        }
    }

    private static function thresholds(
        $profile,
        $supplied
    ) {
        $resolved = array();

        foreach ($profile['thresholds'] as $definition) {
            $key = $definition['key'];
            $value = array_key_exists($key, $supplied)
                ? $supplied[$key]
                : $definition['default'];

            $resolved[$key] = self::finite(
                $value,
                $definition['label']
            );
        }

        return $resolved;
    }

    private static function numeric_column(
        $rows,
        $key
    ) {
        $values = array();

        foreach ($rows as $index => $row) {
            $values[] = self::finite(
                isset($row[$key]) ? $row[$key] : null,
                $key . ' on data row ' . ($index + 1)
            );
        }

        return $values;
    }

    private static function grouped_values(
        $rows,
        $group_key
    ) {
        $groups = array();

        foreach ($rows as $index => $row) {
            $group = isset($row[$group_key])
                ? trim((string) $row[$group_key])
                : '';

            if ($group === '') {
                throw new InvalidArgumentException(
                    $group_key
                    . ' is required on data row '
                    . ($index + 1)
                );
            }

            $value = self::finite(
                isset($row['value'])
                    ? $row['value']
                    : null,
                'value on data row ' . ($index + 1)
            );

            if (!isset($groups[$group])) {
                $groups[$group] = array();
            }

            $groups[$group][] = $value;
        }

        return $groups;
    }

    public static function validate(
        $profile_id,
        $rows,
        $thresholds = array()
    ) {
        $profile = self::profile((string) $profile_id);
        self::required_columns($profile, $rows);

        $resolved = self::thresholds(
            $profile,
            is_array($thresholds)
                ? $thresholds
                : array()
        );
        $metrics = array();
        $checks = array();

        if ($profile_id === 'precision-repeatability') {
            $values = self::numeric_column(
                $rows,
                'value'
            );
            $mean = self::mean($values);
            $sd = self::standard_deviation($values);
            $cv = $mean == 0.0
                ? null
                : abs($sd / $mean) * 100.0;

            $metrics = array(
                'n' => count($values),
                'mean' => $mean,
                'standardDeviation' => $sd,
                'coefficientOfVariationPercent' => $cv,
                'minimum' => min($values),
                'maximum' => max($values),
            );

            $checks[] = self::check(
                'minimum-replicates',
                'Replicate count',
                count($values),
                '>=',
                $resolved['minimumReplicates'],
                count($values)
                    >= $resolved['minimumReplicates']
            );
            $checks[] = self::check(
                'maximum-cv',
                'Coefficient of variation',
                $cv,
                '<=',
                $resolved['maximumCvPercent'],
                $cv !== null
                    && $cv
                    <= $resolved['maximumCvPercent'],
                '%'
            );
        }

        if ($profile_id === 'accuracy-recovery') {
            $recoveries = array();
            $biases = array();

            foreach ($rows as $index => $row) {
                $expected = self::finite(
                    isset($row['expected'])
                        ? $row['expected']
                        : null,
                    'expected on data row ' . ($index + 1)
                );
                $measured = self::finite(
                    isset($row['measured'])
                        ? $row['measured']
                        : null,
                    'measured on data row ' . ($index + 1)
                );

                if ($expected == 0.0) {
                    throw new InvalidArgumentException(
                        'expected cannot be zero on data row '
                        . ($index + 1)
                    );
                }

                $recovery = $measured / $expected * 100.0;
                $recoveries[] = $recovery;
                $biases[] = $recovery - 100.0;
            }

            $mean_recovery = self::mean($recoveries);
            $mean_bias = self::mean($biases);
            $maximum_bias = max(
                array_map('abs', $biases)
            );

            $metrics = array(
                'n' => count($recoveries),
                'meanRecoveryPercent' => $mean_recovery,
                'meanBiasPercent' => $mean_bias,
                'maximumAbsoluteBiasPercent' =>
                    $maximum_bias,
                'recoveryStandardDeviation' =>
                    self::standard_deviation($recoveries),
            );

            $checks[] = self::check(
                'minimum-recovery',
                'Mean recovery lower bound',
                $mean_recovery,
                '>=',
                $resolved['minimumRecoveryPercent'],
                $mean_recovery
                    >= $resolved['minimumRecoveryPercent'],
                '%'
            );
            $checks[] = self::check(
                'maximum-recovery',
                'Mean recovery upper bound',
                $mean_recovery,
                '<=',
                $resolved['maximumRecoveryPercent'],
                $mean_recovery
                    <= $resolved['maximumRecoveryPercent'],
                '%'
            );
            $checks[] = self::check(
                'maximum-absolute-bias',
                'Maximum absolute row bias',
                $maximum_bias,
                '<=',
                $resolved['maximumAbsoluteBiasPercent'],
                $maximum_bias
                    <= $resolved['maximumAbsoluteBiasPercent'],
                '%'
            );
        }

        if ($profile_id === 'calibration-linearity') {
            $points = array();

            foreach ($rows as $index => $row) {
                $points[] = array(
                    'x' => self::finite(
                        isset($row['concentration'])
                            ? $row['concentration']
                            : null,
                        'concentration on data row '
                        . ($index + 1)
                    ),
                    'y' => self::finite(
                        isset($row['signal'])
                            ? $row['signal']
                            : null,
                        'signal on data row '
                        . ($index + 1)
                    ),
                );
            }

            $fit = self::regression($points);
            $metrics = array(
                'levelCount' => count($points),
                'slope' => $fit['slope'],
                'intercept' => $fit['intercept'],
                'rSquared' => $fit['rSquared'],
            );

            $checks[] = self::check(
                'minimum-levels',
                'Calibration level count',
                count($points),
                '>=',
                $resolved['minimumLevels'],
                count($points)
                    >= $resolved['minimumLevels']
            );
            $checks[] = self::check(
                'minimum-r-squared',
                'Coefficient of determination',
                $fit['rSquared'],
                '>=',
                $resolved['minimumRSquared'],
                $fit['rSquared']
                    >= $resolved['minimumRSquared']
            );
            $checks[] = self::check(
                'positive-slope',
                'Positive calibration slope',
                $fit['slope'],
                '>',
                0,
                $resolved['requirePositiveSlope'] < 0.5
                    || $fit['slope'] > 0
            );
        }

        if ($profile_id === 'detection-quantitation') {
            $blanks = self::numeric_column(
                $rows,
                'blank'
            );
            $slopes = self::numeric_column(
                $rows,
                'slope'
            );
            $blank_sd =
                self::standard_deviation($blanks);
            $mean_slope = self::mean($slopes);

            if ($mean_slope <= 0.0) {
                throw new InvalidArgumentException(
                    'Mean calibration slope must be positive.'
                );
            }

            $lod = 3.3 * $blank_sd / $mean_slope;
            $loq = 10.0 * $blank_sd / $mean_slope;

            $metrics = array(
                'blankReplicates' => count($blanks),
                'blankMean' => self::mean($blanks),
                'blankStandardDeviation' => $blank_sd,
                'meanSlope' => $mean_slope,
                'lod' => $lod,
                'loq' => $loq,
            );

            $checks[] = self::check(
                'minimum-blank-replicates',
                'Blank replicate count',
                count($blanks),
                '>=',
                $resolved['minimumBlankReplicates'],
                count($blanks)
                    >= $resolved['minimumBlankReplicates']
            );
            $checks[] = self::check(
                'maximum-lod',
                'Estimated LOD',
                $lod,
                '<=',
                $resolved['maximumLod'],
                $lod <= $resolved['maximumLod']
            );
            $checks[] = self::check(
                'maximum-loq',
                'Estimated LOQ',
                $loq,
                '<=',
                $resolved['maximumLoq'],
                $loq <= $resolved['maximumLoq']
            );
        }

        if ($profile_id === 'blank-background') {
            $values = self::numeric_column(
                $rows,
                'value'
            );
            $mean = self::mean($values);
            $maximum = max($values);

            $metrics = array(
                'n' => count($values),
                'meanBlank' => $mean,
                'maximumBlank' => $maximum,
                'standardDeviation' =>
                    self::standard_deviation($values),
            );

            $checks[] = self::check(
                'minimum-blanks',
                'Blank count',
                count($values),
                '>=',
                $resolved['minimumBlanks'],
                count($values)
                    >= $resolved['minimumBlanks']
            );
            $checks[] = self::check(
                'maximum-mean',
                'Mean blank response',
                $mean,
                '<=',
                $resolved['maximumMean'],
                $mean <= $resolved['maximumMean']
            );
            $checks[] = self::check(
                'maximum-single',
                'Maximum single blank',
                $maximum,
                '<=',
                $resolved['maximumSingle'],
                $maximum <= $resolved['maximumSingle']
            );
        }

        if ($profile_id === 'control-performance') {
            $z_scores = array();

            foreach ($rows as $index => $row) {
                $value = self::finite(
                    isset($row['value'])
                        ? $row['value']
                        : null,
                    'value on data row ' . ($index + 1)
                );
                $target = self::finite(
                    isset($row['target'])
                        ? $row['target']
                        : null,
                    'target on data row ' . ($index + 1)
                );
                $sd = self::finite(
                    isset($row['sd'])
                        ? $row['sd']
                        : null,
                    'sd on data row ' . ($index + 1)
                );

                if ($sd <= 0.0) {
                    throw new InvalidArgumentException(
                        'sd must be positive on data row '
                        . ($index + 1)
                    );
                }

                $z_scores[] =
                    ($value - $target) / $sd;
            }

            $warning_count = 0;
            $action_count = 0;
            $maximum_z = 0.0;

            foreach ($z_scores as $z) {
                $absolute = abs($z);
                $maximum_z = max($maximum_z, $absolute);

                if ($absolute >= $resolved['actionZ']) {
                    $action_count++;
                } elseif (
                    $absolute >= $resolved['warningZ']
                ) {
                    $warning_count++;
                }
            }

            $metrics = array(
                'n' => count($z_scores),
                'meanZ' => self::mean($z_scores),
                'maximumAbsoluteZ' => $maximum_z,
                'warningCount' => $warning_count,
                'actionCount' => $action_count,
            );

            $checks[] = self::check(
                'action-limit',
                'Control action-limit events',
                $action_count,
                '=',
                0,
                $action_count === 0
            );
            $checks[] = self::check(
                'maximum-z',
                'Maximum absolute z-score',
                $maximum_z,
                '<',
                $resolved['actionZ'],
                $maximum_z < $resolved['actionZ']
            );
        }

        if ($profile_id === 'robustness') {
            $groups = self::grouped_values(
                $rows,
                'condition'
            );
            $group_means = array();

            foreach ($groups as $name => $values) {
                $group_means[$name] =
                    self::mean($values);
            }

            $means = array_values($group_means);
            $center = self::mean($means);
            $difference = max($means) - min($means);
            $relative = $center == 0.0
                ? null
                : abs($difference / $center) * 100.0;

            $metrics = array(
                'conditionCount' => count($groups),
                'conditionMeans' => $group_means,
                'relativeDifferencePercent' => $relative,
            );

            $checks[] = self::check(
                'minimum-conditions',
                'Condition count',
                count($groups),
                '>=',
                $resolved['minimumConditions'],
                count($groups)
                    >= $resolved['minimumConditions']
            );
            $checks[] = self::check(
                'maximum-relative-difference',
                'Maximum relative condition difference',
                $relative,
                '<=',
                $resolved[
                    'maximumRelativeDifferencePercent'
                ],
                $relative !== null
                    && $relative
                    <= $resolved[
                        'maximumRelativeDifferencePercent'
                    ],
                '%'
            );
        }

        if ($profile_id === 'inter-run-comparability') {
            $groups = self::grouped_values(
                $rows,
                'run'
            );
            $run_means = array();
            $all_values = array();

            foreach ($groups as $name => $values) {
                $run_means[$name] =
                    self::mean($values);
                $all_values = array_merge(
                    $all_values,
                    $values
                );
            }

            $means = array_values($run_means);
            $center = self::mean($means);
            $bias = $center == 0.0
                ? null
                : (
                    (max($means) - min($means))
                    / $center
                ) * 100.0;
            $pooled_mean = self::mean($all_values);
            $pooled_sd =
                self::standard_deviation($all_values);
            $pooled_cv = $pooled_mean == 0.0
                ? null
                : abs(
                    $pooled_sd / $pooled_mean
                ) * 100.0;

            $metrics = array(
                'runCount' => count($groups),
                'runMeans' => $run_means,
                'relativeRunBiasPercent' => $bias,
                'pooledMean' => $pooled_mean,
                'pooledStandardDeviation' => $pooled_sd,
                'pooledCvPercent' => $pooled_cv,
            );

            $checks[] = self::check(
                'minimum-runs',
                'Run count',
                count($groups),
                '>=',
                $resolved['minimumRuns'],
                count($groups)
                    >= $resolved['minimumRuns']
            );
            $checks[] = self::check(
                'maximum-run-bias',
                'Relative run bias',
                $bias,
                '<=',
                $resolved['maximumBiasPercent'],
                $bias !== null
                    && $bias
                    <= $resolved['maximumBiasPercent'],
                '%'
            );
            $checks[] = self::check(
                'maximum-pooled-cv',
                'Pooled coefficient of variation',
                $pooled_cv,
                '<=',
                $resolved['maximumPooledCvPercent'],
                $pooled_cv !== null
                    && $pooled_cv
                    <= $resolved[
                        'maximumPooledCvPercent'
                    ],
                '%'
            );
        }

        $failed = array_values(
            array_filter(
                $checks,
                static function ($item) {
                    return empty($item['passed']);
                }
            )
        );

        return array(
            'profile' => $profile,
            'thresholds' => $resolved,
            'metrics' => $metrics,
            'checks' => $checks,
            'decision' => $failed ? 'fail' : 'pass',
            'failedCheckCount' => count($failed),
        );
    }

    private static function canonical_sort($value) {
        if (!is_array($value)) {
            return $value;
        }

        if (
            array_keys($value)
            === range(0, count($value) - 1)
        ) {
            return array_map(
                array(__CLASS__, 'canonical_sort'),
                $value
            );
        }

        ksort($value, SORT_STRING);

        foreach ($value as $key => $item) {
            $value[$key] = self::canonical_sort($item);
        }

        return $value;
    }

    public static function canonical_json($value) {
        return wp_json_encode(
            self::canonical_sort($value),
            JSON_UNESCAPED_SLASHES
            | JSON_UNESCAPED_UNICODE
            | JSON_PRESERVE_ZERO_FRACTION
        );
    }

    public static function fingerprint($value) {
        return hash(
            'sha256',
            self::canonical_json($value)
        );
    }

    public static function provenance_record(
        $payload,
        $metadata = array(),
        $previous_hash = null
    ) {
        $record = array(
            'schema' =>
                'sc-lab-molecular-analysis-provenance/1.0',
            'version' => self::VERSION,
            'recordId' => isset($metadata['recordId'])
                ? (string) $metadata['recordId']
                : (
                    'scprov-'
                    . gmdate('YmdHis')
                    . '-'
                    . substr(
                        hash('sha256', uniqid('', true)),
                        0,
                        10
                    )
                ),
            'eventType' =>
                isset($metadata['eventType'])
                    ? (string) $metadata['eventType']
                    : 'validation-dossier',
            'timestamp' =>
                isset($metadata['timestamp'])
                    ? (string) $metadata['timestamp']
                    : gmdate('c'),
            'methodId' =>
                isset($metadata['methodId'])
                    ? $metadata['methodId']
                    : null,
            'profileId' =>
                isset($metadata['profileId'])
                    ? $metadata['profileId']
                    : null,
            'analyst' =>
                isset($metadata['analyst'])
                    ? $metadata['analyst']
                    : null,
            'organization' =>
                isset($metadata['organization'])
                    ? $metadata['organization']
                    : null,
            'instrument' =>
                isset($metadata['instrument'])
                    ? $metadata['instrument']
                    : null,
            'sampleSet' =>
                isset($metadata['sampleSet'])
                    ? $metadata['sampleSet']
                    : null,
            'sourceIdentifiers' =>
                isset($metadata['sourceIdentifiers'])
                && is_array($metadata['sourceIdentifiers'])
                    ? array_values(
                        $metadata['sourceIdentifiers']
                    )
                    : array(),
            'evidenceLinks' =>
                isset($metadata['evidenceLinks'])
                && is_array($metadata['evidenceLinks'])
                    ? array_values(
                        $metadata['evidenceLinks']
                    )
                    : array(),
            'notes' =>
                isset($metadata['notes'])
                    ? $metadata['notes']
                    : null,
            'previousHash' =>
                $previous_hash
                    ? (string) $previous_hash
                    : null,
            'payloadHash' => self::fingerprint($payload),
            'payload' => $payload,
            'engine' => array(
                'validationRelease' => self::VERSION,
                'analysisEngineVersion' => '0.21.0',
                'visualizationBatchVersion' => '0.21.2',
            ),
        );

        $record['recordHash'] =
            self::fingerprint($record);

        return $record;
    }

    public static function verify_ledger($records) {
        if (!is_array($records)) {
            throw new InvalidArgumentException(
                'records must be an array.'
            );
        }

        $results = array();
        $previous_hash = null;

        foreach ($records as $record) {
            if (!is_array($record)) {
                $results[] = array(
                    'recordId' => null,
                    'hashValid' => false,
                    'chainValid' => false,
                    'valid' => false,
                );
                continue;
            }

            $stored_hash = isset($record['recordHash'])
                ? (string) $record['recordHash']
                : '';
            $copy = $record;
            unset($copy['recordHash']);

            $calculated_hash =
                self::fingerprint($copy);
            $hash_valid =
                hash_equals(
                    $stored_hash,
                    $calculated_hash
                );
            $chain_value =
                isset($record['previousHash'])
                && $record['previousHash'] !== ''
                    ? (string) $record['previousHash']
                    : null;
            $chain_valid =
                $chain_value === $previous_hash;

            $results[] = array(
                'recordId' =>
                    isset($record['recordId'])
                        ? $record['recordId']
                        : null,
                'hashValid' => $hash_valid,
                'chainValid' => $chain_valid,
                'valid' => $hash_valid && $chain_valid,
                'storedHash' => $stored_hash,
                'calculatedHash' => $calculated_hash,
            );

            $previous_hash = $stored_hash;
        }

        $valid = true;

        foreach ($results as $result) {
            if (empty($result['valid'])) {
                $valid = false;
                break;
            }
        }

        return array(
            'valid' => $valid,
            'recordCount' => count($records),
            'results' => $results,
        );
    }

    public static function profiles_response() {
        try {
            return rest_ensure_response(
                self::profiles()
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_molecular_validation_profiles_error',
                $error->getMessage(),
                array('status' => 500)
            );
        }
    }

    public static function validation_response($request) {
        $payload = $request->get_json_params();

        try {
            $validation = self::validate(
                isset($payload['profileId'])
                    ? (string) $payload['profileId']
                    : '',
                isset($payload['rows'])
                && is_array($payload['rows'])
                    ? $payload['rows']
                    : array(),
                isset($payload['thresholds'])
                && is_array($payload['thresholds'])
                    ? $payload['thresholds']
                    : array()
            );

            return rest_ensure_response(
                array(
                    'schema' =>
                        'sc-lab-molecular-analysis-validation-dossier/1.0',
                    'version' => self::VERSION,
                    'methodId' =>
                        isset($payload['methodId'])
                            ? $payload['methodId']
                            : null,
                    'profileId' =>
                        isset($payload['profileId'])
                            ? $payload['profileId']
                            : null,
                    'decision' =>
                        $validation['decision'],
                    'validation' => $validation,
                    'dataset' => array(
                        'rowCount' =>
                            isset($payload['rows'])
                            && is_array($payload['rows'])
                                ? count($payload['rows'])
                                : 0,
                        'rows' =>
                            isset($payload['rows'])
                            && is_array($payload['rows'])
                                ? $payload['rows']
                                : array(),
                    ),
                    'audit' => array(
                        'createdAt' => gmdate('c'),
                        'engine' =>
                            'sc-lab-molecular-validation-php',
                        'release' => self::VERSION,
                        'analysisEngineVersion' =>
                            '0.21.0',
                    ),
                )
            );
        } catch (InvalidArgumentException $error) {
            return new WP_Error(
                'sc_lab_molecular_validation_invalid',
                $error->getMessage(),
                array('status' => 422)
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_molecular_validation_error',
                $error->getMessage(),
                array('status' => 500)
            );
        }
    }

    public static function provenance_response($request) {
        $payload = $request->get_json_params();

        if (!array_key_exists('payload', $payload)) {
            return new WP_Error(
                'sc_lab_molecular_provenance_payload_required',
                'payload is required.',
                array('status' => 422)
            );
        }

        return rest_ensure_response(
            self::provenance_record(
                $payload['payload'],
                isset($payload['metadata'])
                && is_array($payload['metadata'])
                    ? $payload['metadata']
                    : array(),
                isset($payload['previousHash'])
                    ? $payload['previousHash']
                    : null
            )
        );
    }

    public static function verify_response($request) {
        $payload = $request->get_json_params();

        try {
            return rest_ensure_response(
                self::verify_ledger(
                    isset($payload['records'])
                    && is_array($payload['records'])
                        ? $payload['records']
                        : array()
                )
            );
        } catch (InvalidArgumentException $error) {
            return new WP_Error(
                'sc_lab_molecular_provenance_invalid',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }
}

SC_Lab_Molecular_Validation_REST_V0213::boot();
