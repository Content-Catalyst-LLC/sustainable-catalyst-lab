<?php
/**
 * Biomedical engineering and biosignals REST engine.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Biomedical_Biosignals_REST_V0230 {
    const VERSION = '0.23.0';
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
            . 'biomedical-engineering-biosignals-v0230.json';
    }

    public static function catalog() {
        $path = self::contract_path();

        if (!is_file($path)) {
            return array(
                'version' => self::VERSION,
                'categories' => array(),
                'methods' => array(),
                'benchmarks' => array(),
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

    private static function method($method_id) {
        foreach (
            self::catalog()['methods']
            as $method
        ) {
            if ($method['id'] === $method_id) {
                return $method;
            }
        }

        throw new InvalidArgumentException(
            'Unknown biosignal method: '
            . $method_id
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
        if (is_string($value)) {
            $trimmed = trim($value);

            if (
                str_starts_with($trimmed, '[')
                && str_ends_with($trimmed, ']')
            ) {
                $decoded = json_decode(
                    $trimmed,
                    true
                );

                if (is_array($decoded)) {
                    $value = $decoded;
                }
            } else {
                $value = preg_split(
                    '/[,\s]+/',
                    $trimmed,
                    -1,
                    PREG_SPLIT_NO_EMPTY
                );
            }
        }

        if (!is_array($value)) {
            throw new InvalidArgumentException(
                $label . ' must be an array.'
            );
        }

        $numbers = array();

        foreach ($value as $index => $item) {
            $numbers[] = self::finite(
                $item,
                $label . '[' . $index . ']'
            );
        }

        if (count($numbers) < $minimum) {
            throw new InvalidArgumentException(
                $label
                . ' requires at least '
                . $minimum
                . ' values.'
            );
        }

        return $numbers;
    }

    private static function mean($values) {
        return array_sum($values) / count($values);
    }

    private static function sd($values) {
        $count = count($values);

        if ($count < 2) {
            return 0.0;
        }

        $mean = self::mean($values);
        $sum = 0.0;

        foreach ($values as $value) {
            $sum += ($value - $mean) ** 2;
        }

        return sqrt($sum / ($count - 1));
    }

    private static function rms($values) {
        $squares = array_map(
            static function ($value) {
                return $value * $value;
            },
            $values
        );

        return sqrt(self::mean($squares));
    }

    private static function paired(
        $left,
        $right,
        $left_label,
        $right_label
    ) {
        $a = self::values(
            $left,
            $left_label
        );
        $b = self::values(
            $right,
            $right_label
        );

        if (count($a) !== count($b)) {
            throw new InvalidArgumentException(
                $left_label
                . ' and '
                . $right_label
                . ' must have equal length.'
            );
        }

        return array($a, $b);
    }

    public static function execute(
        $method_id,
        $inputs
    ) {
        $method = self::method($method_id);
        $operation = $method['operation'];
        $i = is_array($inputs)
            ? $inputs
            : array();

        switch ($operation) {
            case 'sampling_interval_ms':
                $result = 1000
                    / self::positive(
                        $i['sampleRateHz'] ?? null,
                        'sampleRateHz'
                    );
                break;

            case 'nyquist_frequency':
                $result = self::positive(
                    $i['sampleRateHz'] ?? null,
                    'sampleRateHz'
                ) / 2;
                break;

            case 'sample_count':
                $result = round(
                    self::finite(
                        $i['durationSeconds'] ?? null,
                        'durationSeconds'
                    )
                    * self::positive(
                        $i['sampleRateHz'] ?? null,
                        'sampleRateHz'
                    )
                );
                break;

            case 'duration_from_samples':
                $result = self::finite(
                    $i['sampleCount'] ?? null,
                    'sampleCount'
                ) / self::positive(
                    $i['sampleRateHz'] ?? null,
                    'sampleRateHz'
                );
                break;

            case 'adc_levels':
                $bits = (int) self::positive(
                    $i['bits'] ?? null,
                    'bits'
                );
                $result = 2 ** $bits;
                break;

            case 'quantization_step':
                $bits = (int) self::positive(
                    $i['bits'] ?? null,
                    'bits'
                );
                $result = self::positive(
                    $i['inputRange'] ?? null,
                    'inputRange'
                ) / ((2 ** $bits) - 1);
                break;

            case 'heart_rate_from_rr':
                $result = 60
                    / self::positive(
                        $i['rrSeconds'] ?? null,
                        'rrSeconds'
                    );
                break;

            case 'rr_from_heart_rate':
                $result = 60
                    / self::positive(
                        $i['heartRateBpm'] ?? null,
                        'heartRateBpm'
                    );
                break;

            case 'qtc_bazett':
                $result = self::finite(
                    $i['qtSeconds'] ?? null,
                    'qtSeconds'
                ) / sqrt(
                    self::positive(
                        $i['rrSeconds'] ?? null,
                        'rrSeconds'
                    )
                );
                break;

            case 'qtc_fridericia':
                $result = self::finite(
                    $i['qtSeconds'] ?? null,
                    'qtSeconds'
                ) / (
                    self::positive(
                        $i['rrSeconds'] ?? null,
                        'rrSeconds'
                    ) ** (1 / 3)
                );
                break;

            case 'ecg_axis_angle':
                $result = rad2deg(
                    atan2(
                        self::finite(
                            $i['yComponent'] ?? null,
                            'yComponent'
                        ),
                        self::finite(
                            $i['xComponent'] ?? null,
                            'xComponent'
                        )
                    )
                );
                break;

            case 'hrv_rmssd':
                $samples = self::values(
                    $i['rrIntervalsMs'] ?? null,
                    'rrIntervalsMs',
                    2
                );
                $squares = array();

                for (
                    $index = 1;
                    $index < count($samples);
                    $index++
                ) {
                    $difference = (
                        $samples[$index]
                        - $samples[$index - 1]
                    );
                    $squares[] = (
                        $difference * $difference
                    );
                }

                $result = sqrt(
                    self::mean($squares)
                );
                break;

            case 'hrv_sdnn':
                $result = self::sd(
                    self::values(
                        $i['rrIntervalsMs'] ?? null,
                        'rrIntervalsMs',
                        2
                    )
                );
                break;

            case 'pulse_rate_from_interval':
                $result = 60
                    / self::positive(
                        $i['pulseIntervalSeconds']
                            ?? null,
                        'pulseIntervalSeconds'
                    );
                break;

            case 'perfusion_index':
                $result = self::finite(
                    $i['acAmplitude'] ?? null,
                    'acAmplitude'
                ) / self::positive(
                    $i['dcLevel'] ?? null,
                    'dcLevel'
                ) * 100;
                break;

            case 'spo2_ratio_estimate':
                $ratio = (
                    self::finite(
                        $i['acRed'] ?? null,
                        'acRed'
                    )
                    / self::positive(
                        $i['dcRed'] ?? null,
                        'dcRed'
                    )
                ) / (
                    self::positive(
                        $i['acInfrared'] ?? null,
                        'acInfrared'
                    )
                    / self::positive(
                        $i['dcInfrared'] ?? null,
                        'dcInfrared'
                    )
                );
                $result = max(
                    0.0,
                    min(
                        100.0,
                        110 - 25 * $ratio
                    )
                );
                break;

            case 'pulse_transit_time':
                $result = self::finite(
                    $i['distalTimeSeconds'] ?? null,
                    'distalTimeSeconds'
                ) - self::finite(
                    $i['proximalTimeSeconds'] ?? null,
                    'proximalTimeSeconds'
                );
                break;

            case 'pulse_wave_velocity':
                $result = self::finite(
                    $i['distanceMeters'] ?? null,
                    'distanceMeters'
                ) / self::positive(
                    $i['transitTimeSeconds'] ?? null,
                    'transitTimeSeconds'
                );
                break;

            case 'respiratory_rate':
                $result = 60
                    / self::positive(
                        $i['breathIntervalSeconds']
                            ?? null,
                        'breathIntervalSeconds'
                    );
                break;

            case 'minute_ventilation':
                $result = self::finite(
                    $i['tidalVolumeLiters'] ?? null,
                    'tidalVolumeLiters'
                ) * self::finite(
                    $i['respiratoryRate'] ?? null,
                    'respiratoryRate'
                );
                break;

            case 'ie_ratio':
                $result = self::finite(
                    $i['inspirationSeconds'] ?? null,
                    'inspirationSeconds'
                ) / self::positive(
                    $i['expirationSeconds'] ?? null,
                    'expirationSeconds'
                );
                break;

            case 'inspiratory_duty_cycle':
                $inspiration = self::finite(
                    $i['inspirationSeconds'] ?? null,
                    'inspirationSeconds'
                );
                $expiration = self::finite(
                    $i['expirationSeconds'] ?? null,
                    'expirationSeconds'
                );
                $duration = (
                    $inspiration + $expiration
                );

                if ($duration <= 0.0) {
                    throw new InvalidArgumentException(
                        'The respiratory cycle duration '
                        . 'must be greater than zero.'
                    );
                }

                $result = (
                    $inspiration
                    / $duration
                    * 100
                );
                break;

            case 'apnea_burden':
                $result = self::finite(
                    $i['apneaSeconds'] ?? null,
                    'apneaSeconds'
                ) / self::positive(
                    $i['recordingSeconds'] ?? null,
                    'recordingSeconds'
                ) * 100;
                break;

            case 'integrated_respiratory_volume':
                $result = self::finite(
                    $i['meanFlowLitersPerSecond']
                        ?? null,
                    'meanFlowLitersPerSecond'
                ) * self::finite(
                    $i['durationSeconds'] ?? null,
                    'durationSeconds'
                );
                break;

            case 'emg_rms':
                $result = self::rms(
                    self::values(
                        $i['samples'] ?? null,
                        'samples'
                    )
                );
                break;

            case 'emg_mav':
                $samples = self::values(
                    $i['samples'] ?? null,
                    'samples'
                );
                $result = self::mean(
                    array_map(
                        'abs',
                        $samples
                    )
                );
                break;

            case 'integrated_emg':
                $samples = self::values(
                    $i['samples'] ?? null,
                    'samples'
                );
                $result = array_sum(
                    array_map(
                        'abs',
                        $samples
                    )
                ) * self::finite(
                    $i['sampleIntervalSeconds']
                        ?? null,
                    'sampleIntervalSeconds'
                );
                break;

            case 'emg_waveform_length':
                $samples = self::values(
                    $i['samples'] ?? null,
                    'samples',
                    2
                );
                $result = 0.0;

                for (
                    $index = 1;
                    $index < count($samples);
                    $index++
                ) {
                    $result += abs(
                        $samples[$index]
                        - $samples[$index - 1]
                    );
                }
                break;

            case 'zero_crossing_rate':
                $samples = self::values(
                    $i['samples'] ?? null,
                    'samples',
                    2
                );
                $crossings = 0;

                for (
                    $index = 1;
                    $index < count($samples);
                    $index++
                ) {
                    if (
                        (
                            $samples[$index - 1] < 0
                            && $samples[$index] >= 0
                        )
                        || (
                            $samples[$index - 1] >= 0
                            && $samples[$index] < 0
                        )
                    ) {
                        $crossings++;
                    }
                }

                $result = (
                    $crossings
                    / (count($samples) - 1)
                    * self::positive(
                        $i['sampleRateHz'] ?? null,
                        'sampleRateHz'
                    )
                );
                break;

            case 'peak_to_peak':
                $samples = self::values(
                    $i['samples'] ?? null,
                    'samples'
                );
                $result = max($samples)
                    - min($samples);
                break;

            case 'crest_factor':
                $samples = self::values(
                    $i['samples'] ?? null,
                    'samples'
                );
                $rms = self::rms($samples);
                $maximum = max(
                    array_map(
                        'abs',
                        $samples
                    )
                );
                $result = $rms != 0.0
                    ? $maximum / $rms
                    : 0.0;
                break;

            case 'absolute_band_power':
                list($frequencies, $powers) =
                    self::paired(
                        $i['frequenciesHz'] ?? null,
                        $i['powerValues'] ?? null,
                        'frequenciesHz',
                        'powerValues'
                    );
                $low = self::finite(
                    $i['lowHz'] ?? null,
                    'lowHz'
                );
                $high = self::finite(
                    $i['highHz'] ?? null,
                    'highHz'
                );
                $width = self::positive(
                    $i['binWidthHz'] ?? null,
                    'binWidthHz'
                );
                $sum = 0.0;

                foreach (
                    $frequencies
                    as $index => $frequency
                ) {
                    if (
                        $frequency >= $low
                        && $frequency <= $high
                    ) {
                        $sum += $powers[$index];
                    }
                }

                $result = $sum * $width;
                break;

            case 'relative_band_power':
                $result = self::finite(
                    $i['bandPower'] ?? null,
                    'bandPower'
                ) / self::positive(
                    $i['totalPower'] ?? null,
                    'totalPower'
                ) * 100;
                break;

            case 'alpha_beta_ratio':
                $result = self::finite(
                    $i['alphaPower'] ?? null,
                    'alphaPower'
                ) / self::positive(
                    $i['betaPower'] ?? null,
                    'betaPower'
                );
                break;

            case 'theta_beta_ratio':
                $result = self::finite(
                    $i['thetaPower'] ?? null,
                    'thetaPower'
                ) / self::positive(
                    $i['betaPower'] ?? null,
                    'betaPower'
                );
                break;

            case 'spectral_centroid':
                list($frequencies, $powers) =
                    self::paired(
                        $i['frequenciesHz'] ?? null,
                        $i['powerValues'] ?? null,
                        'frequenciesHz',
                        'powerValues'
                    );
                $total = array_sum($powers);

                if ($total <= 0.0) {
                    throw new InvalidArgumentException(
                        'powerValues must contain '
                        . 'positive total power.'
                    );
                }

                $weighted = 0.0;

                foreach (
                    $powers
                    as $index => $power
                ) {
                    $weighted += (
                        $frequencies[$index]
                        * $power
                    );
                }

                $result = $weighted / $total;
                break;

            case 'spectral_entropy':
                $powers = self::values(
                    $i['powerValues'] ?? null,
                    'powerValues',
                    2
                );
                $total = array_sum($powers);

                if ($total <= 0.0) {
                    throw new InvalidArgumentException(
                        'powerValues must contain '
                        . 'positive total power.'
                    );
                }

                $entropy = 0.0;

                foreach ($powers as $power) {
                    if ($power <= 0.0) {
                        continue;
                    }

                    $probability = $power / $total;
                    $entropy -= (
                        $probability
                        * log($probability, 2)
                    );
                }

                $result = (
                    $entropy
                    / log(count($powers), 2)
                );
                break;

            case 'dominant_frequency':
                list($frequencies, $powers) =
                    self::paired(
                        $i['frequenciesHz'] ?? null,
                        $i['powerValues'] ?? null,
                        'frequenciesHz',
                        'powerValues'
                    );
                $maximum = max($powers);
                $index = array_search(
                    $maximum,
                    $powers,
                    true
                );
                $result = $frequencies[$index];
                break;

            case 'hemispheric_asymmetry':
                $left = self::finite(
                    $i['leftPower'] ?? null,
                    'leftPower'
                );
                $right = self::finite(
                    $i['rightPower'] ?? null,
                    'rightPower'
                );
                $denominator = $right + $left;

                if ($denominator == 0.0) {
                    throw new InvalidArgumentException(
                        'leftPower and rightPower '
                        . 'cannot both be zero.'
                    );
                }

                $result = (
                    ($right - $left)
                    / $denominator
                    * 100
                );
                break;

            case 'rc_cutoff':
                $result = 1 / (
                    2
                    * M_PI
                    * self::positive(
                        $i['resistanceOhms'] ?? null,
                        'resistanceOhms'
                    )
                    * self::positive(
                        $i['capacitanceFarads']
                            ?? null,
                        'capacitanceFarads'
                    )
                );
                break;

            case 'moving_average_latest':
                $samples = self::values(
                    $i['samples'] ?? null,
                    'samples'
                );
                $window = (int) self::positive(
                    $i['windowSize'] ?? null,
                    'windowSize'
                );

                if ($window > count($samples)) {
                    throw new InvalidArgumentException(
                        'windowSize cannot exceed '
                        . 'the sample count.'
                    );
                }

                $result = self::mean(
                    array_slice(
                        $samples,
                        -$window
                    )
                );
                break;

            case 'exponential_smoothing_alpha':
                $interval = self::finite(
                    $i['sampleIntervalSeconds']
                        ?? null,
                    'sampleIntervalSeconds'
                );
                $constant = self::positive(
                    $i['timeConstantSeconds']
                        ?? null,
                    'timeConstantSeconds'
                );
                $result = (
                    $interval
                    / ($constant + $interval)
                );
                break;

            case 'snr_db':
                $result = 20 * log10(
                    self::positive(
                        $i['signalRms'] ?? null,
                        'signalRms'
                    ) / self::positive(
                        $i['noiseRms'] ?? null,
                        'noiseRms'
                    )
                );
                break;

            case 'missing_sample_percent':
                $result = self::finite(
                    $i['missingCount'] ?? null,
                    'missingCount'
                ) / self::positive(
                    $i['totalCount'] ?? null,
                    'totalCount'
                ) * 100;
                break;

            case 'clipping_percent':
                $result = self::finite(
                    $i['clippedCount'] ?? null,
                    'clippedCount'
                ) / self::positive(
                    $i['totalCount'] ?? null,
                    'totalCount'
                ) * 100;
                break;

            case 'pearson_correlation':
                list($x_values, $y_values) =
                    self::paired(
                        $i['xValues'] ?? null,
                        $i['yValues'] ?? null,
                        'xValues',
                        'yValues'
                    );
                $x_mean = self::mean($x_values);
                $y_mean = self::mean($y_values);
                $numerator = 0.0;
                $x_squares = 0.0;
                $y_squares = 0.0;

                foreach (
                    $x_values
                    as $index => $x_value
                ) {
                    $x_delta = (
                        $x_value - $x_mean
                    );
                    $y_delta = (
                        $y_values[$index] - $y_mean
                    );
                    $numerator += (
                        $x_delta * $y_delta
                    );
                    $x_squares += (
                        $x_delta * $x_delta
                    );
                    $y_squares += (
                        $y_delta * $y_delta
                    );
                }

                $denominator = sqrt(
                    $x_squares * $y_squares
                );

                if ($denominator == 0.0) {
                    throw new InvalidArgumentException(
                        'Correlation requires '
                        . 'non-constant arrays.'
                    );
                }

                $result = (
                    $numerator / $denominator
                );
                break;

            case 'signal_quality_index':
                $result = max(
                    0.0,
                    min(
                        100.0,
                        50
                        + 2 * self::finite(
                            $i['snrDb'] ?? null,
                            'snrDb'
                        )
                        - 2 * self::finite(
                            $i['missingPercent'] ?? null,
                            'missingPercent'
                        )
                        - 3 * self::finite(
                            $i['clippingPercent'] ?? null,
                            'clippingPercent'
                        )
                    )
                );
                break;

            default:
                throw new InvalidArgumentException(
                    'Unsupported biosignal operation: '
                    . $operation
                );
        }

        return array(
            'schema' =>
                'sc-lab-biomedical-biosignal-result/1.0',
            'version' => self::VERSION,
            'method' => $method,
            'inputs' => $inputs,
            'value' => $result,
            'unit' => $method['output']['unit'],
        );
    }

    public static function analyze_signal(
        $raw_samples,
        $raw_sample_rate
    ) {
        $samples = self::values(
            $raw_samples,
            'samples',
            2
        );
        $sample_rate = self::positive(
            $raw_sample_rate,
            'sampleRateHz'
        );
        $average = self::mean($samples);
        $rms = self::rms($samples);
        $crossings = 0;

        for (
            $index = 1;
            $index < count($samples);
            $index++
        ) {
            if (
                (
                    $samples[$index - 1] < 0
                    && $samples[$index] >= 0
                )
                || (
                    $samples[$index - 1] >= 0
                    && $samples[$index] < 0
                )
            ) {
                $crossings++;
            }
        }

        return array(
            'schema' =>
                'sc-lab-biosignal-waveform-analysis/1.0',
            'version' => self::VERSION,
            'sampleCount' => count($samples),
            'sampleRateHz' => $sample_rate,
            'durationSeconds' => (
                (count($samples) - 1)
                / $sample_rate
            ),
            'mean' => $average,
            'standardDeviation' =>
                self::sd($samples),
            'rms' => $rms,
            'minimum' => min($samples),
            'maximum' => max($samples),
            'peakToPeak' => (
                max($samples) - min($samples)
            ),
            'zeroCrossingCount' => $crossings,
            'zeroCrossingRate' => (
                $crossings
                / (count($samples) - 1)
                * $sample_rate
            ),
            'crestFactor' => (
                $rms != 0.0
                    ? max(
                        array_map(
                            'abs',
                            $samples
                        )
                    ) / $rms
                    : 0.0
            ),
        );
    }

    public static function batch_execute($rows) {
        $results = array();

        foreach ($rows as $index => $row) {
            try {
                $results[] = array(
                    'row' => $index + 1,
                    'ok' => true,
                    'result' => self::execute(
                        (string) (
                            $row['methodId'] ?? ''
                        ),
                        $row['inputs'] ?? array()
                    ),
                );
            } catch (Throwable $error) {
                $results[] = array(
                    'row' => $index + 1,
                    'ok' => false,
                    'error' => $error->getMessage(),
                );
            }
        }

        $success_count = count(
            array_filter(
                $results,
                static function ($item) {
                    return $item['ok'];
                }
            )
        );

        return array(
            'schema' =>
                'sc-lab-biomedical-biosignal-batch/1.0',
            'version' => self::VERSION,
            'rowCount' => count($rows),
            'successCount' => $success_count,
            'errorCount' => (
                count($rows) - $success_count
            ),
            'results' => $results,
        );
    }

    public static function register_routes() {
        register_rest_route(
            self::NAMESPACE,
            '/compute/biomedical/biosignals/methods',
            array(
                'methods' => 'GET',
                'callback' =>
                    array(__CLASS__, 'methods_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/biomedical/biosignals/health',
            array(
                'methods' => 'GET',
                'callback' =>
                    array(__CLASS__, 'health_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/biomedical/biosignals/run',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'run_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/biomedical/biosignals/analyze',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'analyze_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/biomedical/biosignals/batch',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'batch_response'),
                'permission_callback' => '__return_true',
            )
        );
    }

    public static function methods_response() {
        return rest_ensure_response(
            self::catalog()
        );
    }

    public static function health_payload() {
        $catalog = self::catalog();
        $ready = (
            ($catalog['version'] ?? null)
                === self::VERSION
            && count(
                $catalog['methods'] ?? array()
            ) === 48
            && count(
                $catalog['benchmarks'] ?? array()
            ) === 48
            && count(
                $catalog['categories'] ?? array()
            ) === 8
        );

        return array(
            'ok' => $ready,
            'status' => $ready
                ? 'ready'
                : 'contract-incomplete',
            'release' => self::VERSION,
            'methodCount' => count(
                $catalog['methods'] ?? array()
            ),
            'benchmarkCount' => count(
                $catalog['benchmarks'] ?? array()
            ),
            'categoryCount' => count(
                $catalog['categories'] ?? array()
            ),
        );
    }

    public static function health_response() {
        return rest_ensure_response(
            self::health_payload()
        );
    }

    public static function run_response($request) {
        try {
            $payload = $request->get_json_params();

            return rest_ensure_response(
                self::execute(
                    (string) (
                        $payload['methodId'] ?? ''
                    ),
                    $payload['inputs'] ?? array()
                )
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_v0230_biosignal_error',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function analyze_response($request) {
        try {
            $payload = $request->get_json_params();

            return rest_ensure_response(
                self::analyze_signal(
                    $payload['samples'] ?? array(),
                    $payload['sampleRateHz'] ?? null
                )
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_v0230_waveform_error',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function batch_response($request) {
        $payload = $request->get_json_params();

        return rest_ensure_response(
            self::batch_execute(
                $payload['rows'] ?? array()
            )
        );
    }
}

SC_Lab_Biomedical_Biosignals_REST_V0230::boot();
