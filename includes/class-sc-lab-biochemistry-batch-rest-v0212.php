<?php
/**
 * Batch-analysis REST services for Lab v0.21.2.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Biochemistry_Batch_REST_V0212 {
    const VERSION = '0.21.2';
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
            '/compute/biochemistry/batch',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'batch_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/biochemistry/visualizations',
            array(
                'methods' => 'GET',
                'callback' =>
                    array(__CLASS__, 'presets_response'),
                'permission_callback' => '__return_true',
            )
        );
    }

    private static function presets_path() {
        return dirname(__DIR__)
            . '/contracts/'
            . 'biochemistry-visualization-presets-v0212.json';
    }

    public static function presets() {
        $path = self::presets_path();

        if (!is_file($path)) {
            throw new RuntimeException(
                'The Biochemistry visualization preset '
                . 'contract is missing.'
            );
        }

        $decoded = json_decode(
            file_get_contents($path),
            true
        );

        if (!is_array($decoded)) {
            throw new RuntimeException(
                'The Biochemistry visualization preset '
                . 'contract is invalid.'
            );
        }

        return $decoded;
    }

    private static function mean($values) {
        return array_sum($values) / count($values);
    }

    private static function standard_deviation($values) {
        $count = count($values);

        if ($count < 2) {
            return 0.0;
        }

        $mean = self::mean($values);
        $sum = 0.0;

        foreach ($values as $value) {
            $sum += pow($value - $mean, 2);
        }

        return sqrt($sum / ($count - 1));
    }

    private static function summarize($values) {
        $clean = array_values(
            array_filter(
                array_map(
                    static function ($value) {
                        return is_numeric($value)
                            ? (float) $value
                            : null;
                    },
                    $values
                ),
                static function ($value) {
                    return $value !== null
                        && is_finite($value);
                }
            )
        );

        if (!$clean) {
            return array(
                'n' => 0,
                'mean' => null,
                'standardDeviation' => null,
                'coefficientOfVariationPercent' => null,
                'minimum' => null,
                'maximum' => null,
                'status' => 'unavailable',
            );
        }

        $mean = self::mean($clean);
        $deviation = self::standard_deviation($clean);
        $cv = $mean == 0.0
            ? null
            : abs($deviation / $mean) * 100.0;

        return array(
            'n' => count($clean),
            'mean' => $mean,
            'standardDeviation' => $deviation,
            'coefficientOfVariationPercent' => $cv,
            'minimum' => min($clean),
            'maximum' => max($clean),
            'status' =>
                $cv !== null && $cv > 20.0
                    ? 'review'
                    : 'screened',
        );
    }

    public static function batch_calculate(
        $method_id,
        $rows
    ) {
        if (
            !class_exists(
                'SC_Lab_Biochemistry_Molecular_Analysis_REST'
            )
        ) {
            throw new RuntimeException(
                'The Biochemistry analysis engine is unavailable.'
            );
        }

        if (!is_array($rows) || !$rows) {
            throw new InvalidArgumentException(
                'At least one batch row is required.'
            );
        }

        $results = array();

        foreach ($rows as $index => $row) {
            if (!is_array($row)) {
                $row = array();
            }

            $sample = isset($row['sample'])
                ? (string) $row['sample']
                : 'sample-' . ((int) $index + 1);

            $inputs = isset($row['inputs'])
                && is_array($row['inputs'])
                ? $row['inputs']
                : $row;

            unset(
                $inputs['sample'],
                $inputs['sampleId'],
                $inputs['inputs']
            );

            try {
                $analysis =
                    SC_Lab_Biochemistry_Molecular_Analysis_REST::
                        calculate(
                            (string) $method_id,
                            $inputs
                        );

                $results[] = array(
                    'sample' => $sample,
                    'row' => (int) $index + 1,
                    'ok' => true,
                    'inputs' => $analysis['inputs'],
                    'outputs' => $analysis['outputs'],
                    'warnings' => $analysis['warnings'],
                    'analysis' => $analysis,
                );
            } catch (Throwable $error) {
                $results[] = array(
                    'sample' => $sample,
                    'row' => (int) $index + 1,
                    'ok' => false,
                    'inputs' => $inputs,
                    'outputs' => array(),
                    'warnings' => array(),
                    'error' => $error->getMessage(),
                );
            }
        }

        $output_keys = array();

        foreach ($results as $result) {
            if (!empty($result['ok'])) {
                $output_keys = array_keys(
                    $result['outputs']
                );
                break;
            }
        }

        $statistics = array();

        foreach ($output_keys as $key) {
            $values = array();

            foreach ($results as $result) {
                if (
                    !empty($result['ok'])
                    && isset($result['outputs'][$key])
                ) {
                    $values[] = $result['outputs'][$key];
                }
            }

            $statistics[$key] =
                self::summarize($values);
        }

        $flags = array();

        foreach ($statistics as $key => $summary) {
            if ($summary['status'] === 'review') {
                $flags[] =
                    $key . ' has CV above 20%.';
            }
        }

        $error_count = count(
            array_filter(
                $results,
                static function ($result) {
                    return empty($result['ok']);
                }
            )
        );

        if ($error_count > 0) {
            $flags[] =
                $error_count
                . ' batch row(s) could not be calculated.';
        }

        return array(
            'schema' =>
                'sc-lab-biochemistry-batch-analysis/1.0',
            'version' => self::VERSION,
            'analysisEngineVersion' => '0.21.0',
            'methodId' => (string) $method_id,
            'rowCount' => count($results),
            'successCount' =>
                count($results) - $error_count,
            'errorCount' => $error_count,
            'results' => $results,
            'statistics' => $statistics,
            'flags' => $flags,
            'status' => $flags
                ? 'review'
                : 'screened',
            'audit' => array(
                'createdAt' => gmdate('c'),
                'engine' =>
                    'sc-lab-biochemistry-batch-php',
                'release' => self::VERSION,
            ),
        );
    }

    public static function presets_response() {
        try {
            return rest_ensure_response(
                self::presets()
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_biochemistry_visualization_error',
                $error->getMessage(),
                array('status' => 500)
            );
        }
    }

    public static function batch_response($request) {
        $payload = $request->get_json_params();
        $method_id = isset($payload['methodId'])
            ? (string) $payload['methodId']
            : '';
        $rows = isset($payload['rows'])
            && is_array($payload['rows'])
            ? $payload['rows']
            : array();

        if ($method_id === '') {
            return new WP_Error(
                'sc_lab_biochemistry_batch_method_required',
                'methodId is required.',
                array('status' => 422)
            );
        }

        try {
            return rest_ensure_response(
                self::batch_calculate(
                    $method_id,
                    $rows
                )
            );
        } catch (InvalidArgumentException $error) {
            return new WP_Error(
                'sc_lab_biochemistry_batch_invalid',
                $error->getMessage(),
                array('status' => 422)
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_biochemistry_batch_error',
                $error->getMessage(),
                array('status' => 500)
            );
        }
    }
}

SC_Lab_Biochemistry_Batch_REST_V0212::boot();
