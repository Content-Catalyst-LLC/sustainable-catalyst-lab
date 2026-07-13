<?php
/**
 * Bioprocess validation and provenance REST engine.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Bioprocess_Validation_REST_V0223 {
    const VERSION = '0.22.3';
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
            . 'bioprocess-validation-provenance-v0223.json';
    }

    public static function contract() {
        $path = self::contract_path();

        if (!is_file($path)) {
            return array(
                'version' => self::VERSION,
                'profiles' => array(),
                'eventTypes' => array(),
                'dispositions' => array(),
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

    private static function profile($profile_id) {
        foreach (
            self::contract()['profiles']
            as $profile
        ) {
            if ($profile['id'] === $profile_id) {
                return $profile;
            }
        }

        throw new InvalidArgumentException(
            'Unknown validation profile: '
            . $profile_id
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

    private static function mean($values) {
        if (count($values) === 0) {
            throw new InvalidArgumentException(
                'At least one value is required.'
            );
        }

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

    private static function cv($values) {
        $mean = self::mean($values);

        if ($mean == 0.0) {
            return null;
        }

        return abs(self::sd($values) / $mean) * 100;
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

    private static function thresholds(
        $profile,
        $supplied
    ) {
        $resolved = array();

        foreach (
            $profile['thresholds']
            as $definition
        ) {
            $key = $definition['key'];
            $resolved[$key] = self::finite(
                array_key_exists($key, $supplied)
                    ? $supplied[$key]
                    : $definition['default'],
                $definition['label']
            );
        }

        return $resolved;
    }

    private static function require_rows(
        $profile,
        $rows
    ) {
        if (!is_array($rows) || count($rows) === 0) {
            throw new InvalidArgumentException(
                'Validation requires at least one data row.'
            );
        }

        foreach ($rows as $index => $row) {
            foreach (
                $profile['requiredColumns']
                as $column
            ) {
                if (!array_key_exists($column, $row)) {
                    throw new InvalidArgumentException(
                        'Required column '
                        . $column
                        . ' is missing from row '
                        . ($index + 1)
                        . '.'
                    );
                }
            }
        }
    }

    private static function regression($points) {
        if (count($points) < 2) {
            throw new InvalidArgumentException(
                'At least two hold-time points are required.'
            );
        }

        $x_values = array_column($points, 0);
        $y_values = array_column($points, 1);
        $x_mean = self::mean($x_values);
        $y_mean = self::mean($y_values);
        $denominator = 0.0;
        $numerator = 0.0;

        foreach ($points as $point) {
            $denominator += (
                ($point[0] - $x_mean) ** 2
            );
            $numerator += (
                ($point[0] - $x_mean)
                * ($point[1] - $y_mean)
            );
        }

        if ($denominator == 0.0) {
            throw new InvalidArgumentException(
                'Hold-time observations must use distinct times.'
            );
        }

        $slope = $numerator / $denominator;

        return array(
            'slope' => $slope,
            'intercept' => (
                $y_mean - $slope * $x_mean
            ),
        );
    }

    public static function evaluate(
        $profile_id,
        $rows,
        $supplied_thresholds = array()
    ) {
        $profile = self::profile($profile_id);
        self::require_rows($profile, $rows);
        $limits = self::thresholds(
            $profile,
            is_array($supplied_thresholds)
                ? $supplied_thresholds
                : array()
        );
        $metrics = array();
        $checks = array();

        if (
            $profile_id
            === 'batch-record-completeness'
        ) {
            $required = array(
                'batchId',
                'lotId',
                'startedAt',
                'endedAt',
                'operator',
                'materialLot',
            );
            $missing = 0;
            $minimum_evidence = null;
            $batches = array();

            foreach ($rows as $row) {
                $missing_fields = array();

                foreach ($required as $key) {
                    if (
                        trim(
                            (string) ($row[$key] ?? '')
                        ) === ''
                    ) {
                        $missing_fields[] = $key;
                    }
                }

                $evidence = $row['evidenceLinks'];

                if (is_string($evidence)) {
                    $evidence = array_values(
                        array_filter(
                            array_map(
                                'trim',
                                explode('|', $evidence)
                            )
                        )
                    );
                }

                if (!is_array($evidence)) {
                    $evidence = array();
                }

                $evidence_count = count($evidence);
                $minimum_evidence = (
                    $minimum_evidence === null
                    ? $evidence_count
                    : min(
                        $minimum_evidence,
                        $evidence_count
                    )
                );
                $missing += count($missing_fields);
                $batches[] = array(
                    'batchId' => $row['batchId'] ?? null,
                    'missingFields' => $missing_fields,
                    'evidenceCount' => $evidence_count,
                );
            }

            $metrics = array(
                'batchCount' => count($rows),
                'missingFieldCount' => $missing,
                'minimumEvidenceLinks' =>
                    $minimum_evidence,
                'batches' => $batches,
            );
            $checks = array(
                self::check(
                    'maximum-missing-fields',
                    'Missing required fields',
                    $missing,
                    '<=',
                    $limits['maximumMissingFields'],
                    $missing
                    <= $limits['maximumMissingFields']
                ),
                self::check(
                    'minimum-evidence-links',
                    'Minimum evidence links',
                    $minimum_evidence,
                    '>=',
                    $limits['minimumEvidenceLinks'],
                    $minimum_evidence
                    >= $limits['minimumEvidenceLinks']
                ),
            );
        } elseif (
            $profile_id === 'cpp-conformance'
        ) {
            $action_count = 0;
            $warning_count = 0;
            $observations = array();

            foreach ($rows as $index => $row) {
                $value = self::finite(
                    $row['value'],
                    'value on row ' . ($index + 1)
                );
                $low = self::finite(
                    $row['low'],
                    'low on row ' . ($index + 1)
                );
                $high = self::finite(
                    $row['high'],
                    'high on row ' . ($index + 1)
                );

                if ($low > $high) {
                    throw new InvalidArgumentException(
                        'low exceeds high on row '
                        . ($index + 1)
                        . '.'
                    );
                }

                $status = 'pass';

                if ($value < $low || $value > $high) {
                    $status = 'action';
                    $action_count++;
                } else {
                    $band = ($high - $low) * 0.1;

                    if (
                        $value < $low + $band
                        || $value > $high - $band
                    ) {
                        $status = 'warning';
                        $warning_count++;
                    }
                }

                $observations[] = array(
                    'parameter' =>
                        $row['parameter'] ?? null,
                    'value' => $value,
                    'low' => $low,
                    'high' => $high,
                    'status' => $status,
                );
            }

            $warning_percent = (
                $warning_count
                / count($rows)
                * 100
            );
            $metrics = array(
                'observationCount' => count($rows),
                'actionExcursionCount' =>
                    $action_count,
                'warningCount' => $warning_count,
                'warningPercent' => $warning_percent,
                'observations' => $observations,
            );
            $checks = array(
                self::check(
                    'maximum-action-excursions',
                    'Action-limit excursions',
                    $action_count,
                    '<=',
                    $limits['maximumActionExcursions'],
                    $action_count
                    <= $limits['maximumActionExcursions']
                ),
                self::check(
                    'maximum-warning-percent',
                    'Warning observations',
                    $warning_percent,
                    '<=',
                    $limits['maximumWarningPercent'],
                    $warning_percent
                    <= $limits['maximumWarningPercent'],
                    '%'
                ),
            );
        } elseif (
            $profile_id === 'cqa-conformance'
        ) {
            $failures = 0;
            $observations = array();

            foreach ($rows as $row) {
                $value = self::finite(
                    $row['value'],
                    'value'
                );
                $low = self::finite(
                    $row['low'],
                    'low'
                );
                $high = self::finite(
                    $row['high'],
                    'high'
                );
                $passed = (
                    $value >= $low
                    && $value <= $high
                );

                if (!$passed) {
                    $failures++;
                }

                $observations[] = array(
                    'attribute' =>
                        $row['attribute'] ?? null,
                    'value' => $value,
                    'low' => $low,
                    'high' => $high,
                    'status' =>
                        $passed ? 'pass' : 'fail',
                );
            }

            $pass_percent = (
                (count($rows) - $failures)
                / count($rows)
                * 100
            );
            $metrics = array(
                'observationCount' => count($rows),
                'failureCount' => $failures,
                'passPercent' => $pass_percent,
                'observations' => $observations,
            );
            $checks = array(
                self::check(
                    'maximum-failures',
                    'Failed CQA observations',
                    $failures,
                    '<=',
                    $limits['maximumFailures'],
                    $failures
                    <= $limits['maximumFailures']
                ),
                self::check(
                    'minimum-pass-percent',
                    'CQA pass rate',
                    $pass_percent,
                    '>=',
                    $limits['minimumPassPercent'],
                    $pass_percent
                    >= $limits['minimumPassPercent'],
                    '%'
                ),
            );
        } elseif (
            $profile_id
            === 'cross-batch-consistency'
        ) {
            $yields = array();
            $titers = array();
            $cycle_times = array();

            foreach ($rows as $row) {
                $yields[] = self::finite(
                    $row['yield'],
                    'yield'
                );
                $titers[] = self::finite(
                    $row['titer'],
                    'titer'
                );
                $cycle_times[] = self::finite(
                    $row['cycleTime'],
                    'cycleTime'
                );
            }

            $yield_cv = self::cv($yields);
            $titer_cv = self::cv($titers);
            $cycle_cv = self::cv($cycle_times);
            $metrics = array(
                'batchCount' => count($rows),
                'yield' => array(
                    'mean' => self::mean($yields),
                    'standardDeviation' =>
                        self::sd($yields),
                    'coefficientOfVariationPercent' =>
                        $yield_cv,
                ),
                'titer' => array(
                    'mean' => self::mean($titers),
                    'standardDeviation' =>
                        self::sd($titers),
                    'coefficientOfVariationPercent' =>
                        $titer_cv,
                ),
                'cycleTime' => array(
                    'mean' =>
                        self::mean($cycle_times),
                    'standardDeviation' =>
                        self::sd($cycle_times),
                    'coefficientOfVariationPercent' =>
                        $cycle_cv,
                ),
            );
            $checks = array(
                self::check(
                    'minimum-batches',
                    'Comparable batches',
                    count($rows),
                    '>=',
                    $limits['minimumBatches'],
                    count($rows)
                    >= $limits['minimumBatches']
                ),
                self::check(
                    'maximum-yield-cv',
                    'Yield CV',
                    $yield_cv,
                    '<=',
                    $limits['maximumYieldCvPercent'],
                    $yield_cv !== null
                    && $yield_cv
                    <= $limits['maximumYieldCvPercent'],
                    '%'
                ),
                self::check(
                    'maximum-titer-cv',
                    'Titer CV',
                    $titer_cv,
                    '<=',
                    $limits['maximumTiterCvPercent'],
                    $titer_cv !== null
                    && $titer_cv
                    <= $limits['maximumTiterCvPercent'],
                    '%'
                ),
                self::check(
                    'maximum-cycle-time-cv',
                    'Cycle-time CV',
                    $cycle_cv,
                    '<=',
                    $limits[
                        'maximumCycleTimeCvPercent'
                    ],
                    $cycle_cv !== null
                    && $cycle_cv
                    <= $limits[
                        'maximumCycleTimeCvPercent'
                    ],
                    '%'
                ),
            );
        } elseif (
            $profile_id
            === 'monitoring-control-performance'
        ) {
            $actions = 0.0;
            $warnings = 0.0;
            $final_errors = array();
            $iae_values = array();

            foreach ($rows as $row) {
                $actions += self::finite(
                    $row['actionCount'],
                    'actionCount'
                );
                $warnings += self::finite(
                    $row['warningCount'],
                    'warningCount'
                );
                $final_errors[] = abs(
                    self::finite(
                        $row['finalError'],
                        'finalError'
                    )
                );
                $iae_values[] = self::finite(
                    $row['integralAbsoluteError'],
                    'integralAbsoluteError'
                );
            }

            $maximum_final_error =
                max($final_errors);
            $maximum_iae = max($iae_values);
            $metrics = array(
                'runCount' => count($rows),
                'actionCount' => $actions,
                'warningCount' => $warnings,
                'maximumAbsoluteFinalError' =>
                    $maximum_final_error,
                'meanAbsoluteFinalError' =>
                    self::mean($final_errors),
                'maximumIntegralAbsoluteError' =>
                    $maximum_iae,
                'meanIntegralAbsoluteError' =>
                    self::mean($iae_values),
            );
            $checks = array(
                self::check(
                    'maximum-actions',
                    'Action excursions',
                    $actions,
                    '<=',
                    $limits['maximumActionCount'],
                    $actions
                    <= $limits['maximumActionCount']
                ),
                self::check(
                    'maximum-warnings',
                    'Warnings',
                    $warnings,
                    '<=',
                    $limits['maximumWarningCount'],
                    $warnings
                    <= $limits['maximumWarningCount']
                ),
                self::check(
                    'maximum-final-error',
                    'Maximum absolute final error',
                    $maximum_final_error,
                    '<=',
                    $limits[
                        'maximumAbsoluteFinalError'
                    ],
                    $maximum_final_error
                    <= $limits[
                        'maximumAbsoluteFinalError'
                    ]
                ),
                self::check(
                    'maximum-iae',
                    'Maximum integral absolute error',
                    $maximum_iae,
                    '<=',
                    $limits[
                        'maximumIntegralAbsoluteError'
                    ],
                    $maximum_iae
                    <= $limits[
                        'maximumIntegralAbsoluteError'
                    ]
                ),
            );
        } elseif (
            $profile_id === 'excursion-disposition'
        ) {
            $open_actions = 0;
            $undocumented = 0;

            foreach ($rows as $row) {
                $severity = strtolower(
                    trim(
                        (string) ($row['severity'] ?? '')
                    )
                );
                $status = strtolower(
                    trim(
                        (string) ($row['status'] ?? '')
                    )
                );
                $closed = in_array(
                    $status,
                    array(
                        'closed',
                        'resolved',
                        'accepted',
                    ),
                    true
                );

                if (
                    $severity === 'action'
                    && !$closed
                ) {
                    $open_actions++;
                }

                if (
                    trim(
                        (string) (
                            $row['investigationId']
                            ?? ''
                        )
                    ) === ''
                    || trim(
                        (string) (
                            $row['evidenceLink']
                            ?? ''
                        )
                    ) === ''
                ) {
                    $undocumented++;
                }
            }

            $metrics = array(
                'excursionCount' => count($rows),
                'openActionExcursionCount' =>
                    $open_actions,
                'undocumentedExcursionCount' =>
                    $undocumented,
            );
            $checks = array(
                self::check(
                    'maximum-open-actions',
                    'Open action excursions',
                    $open_actions,
                    '<=',
                    $limits[
                        'maximumOpenActionExcursions'
                    ],
                    $open_actions
                    <= $limits[
                        'maximumOpenActionExcursions'
                    ]
                ),
                self::check(
                    'maximum-undocumented',
                    'Undocumented excursions',
                    $undocumented,
                    '<=',
                    $limits[
                        'maximumUndocumentedExcursions'
                    ],
                    $undocumented
                    <= $limits[
                        'maximumUndocumentedExcursions'
                    ]
                ),
            );
        } elseif (
            $profile_id === 'hold-time-stability'
        ) {
            $points = array();

            foreach ($rows as $row) {
                $points[] = array(
                    self::finite(
                        $row['time'],
                        'time'
                    ),
                    self::finite(
                        $row['value'],
                        'value'
                    ),
                );
            }

            usort(
                $points,
                static function ($left, $right) {
                    return $left[0] <=> $right[0];
                }
            );

            $baseline = $points[0][1];

            if ($baseline == 0.0) {
                throw new InvalidArgumentException(
                    'The initial hold-time value '
                    . 'cannot be zero.'
                );
            }

            $last = $points[count($points) - 1];
            $signed_change = (
                ($last[1] - $baseline)
                / $baseline
                * 100
            );
            $fit = self::regression($points);
            $slope_percent = (
                $fit['slope']
                / $baseline
                * 100
            );
            $metrics = array(
                'pointCount' => count($points),
                'initialValue' => $baseline,
                'finalValue' => $last[1],
                'absoluteChangePercent' =>
                    abs($signed_change),
                'signedChangePercent' =>
                    $signed_change,
                'slope' => $fit['slope'],
                'slopePercentPerHour' =>
                    $slope_percent,
            );
            $checks = array(
                self::check(
                    'minimum-points',
                    'Hold-time observations',
                    count($points),
                    '>=',
                    $limits['minimumPoints'],
                    count($points)
                    >= $limits['minimumPoints']
                ),
                self::check(
                    'maximum-change',
                    'Absolute hold-time change',
                    abs($signed_change),
                    '<=',
                    $limits[
                        'maximumAbsoluteChangePercent'
                    ],
                    abs($signed_change)
                    <= $limits[
                        'maximumAbsoluteChangePercent'
                    ],
                    '%'
                ),
                self::check(
                    'maximum-slope',
                    'Absolute hold-time slope',
                    abs($slope_percent),
                    '<=',
                    $limits[
                        'maximumSlopePercentPerHour'
                    ],
                    abs($slope_percent)
                    <= $limits[
                        'maximumSlopePercentPerHour'
                    ],
                    '%/h'
                ),
            );
        } elseif (
            $profile_id === 'release-readiness'
        ) {
            $failed_critical = 0;
            $open_major = 0;
            $evidence_count = 0;

            foreach ($rows as $row) {
                $status = strtolower(
                    trim(
                        (string) ($row['status'] ?? '')
                    )
                );
                $category = strtolower(
                    trim(
                        (string) (
                            $row['category'] ?? ''
                        )
                    )
                );
                $critical_value = strtolower(
                    trim(
                        (string) (
                            $row['critical'] ?? ''
                        )
                    )
                );
                $critical = in_array(
                    $critical_value,
                    array(
                        '1',
                        'true',
                        'yes',
                        'critical',
                    ),
                    true
                );
                $complete = in_array(
                    $status,
                    array(
                        'pass',
                        'passed',
                        'closed',
                        'complete',
                    ),
                    true
                );

                if ($critical && !$complete) {
                    $failed_critical++;
                }

                if (
                    $category === 'major'
                    && !$complete
                ) {
                    $open_major++;
                }

                if (
                    trim(
                        (string) (
                            $row['evidence'] ?? ''
                        )
                    ) !== ''
                ) {
                    $evidence_count++;
                }
            }

            $evidence_percent = (
                $evidence_count
                / count($rows)
                * 100
            );
            $metrics = array(
                'checkCount' => count($rows),
                'failedCriticalCheckCount' =>
                    $failed_critical,
                'openMajorCheckCount' =>
                    $open_major,
                'evidenceCoveragePercent' =>
                    $evidence_percent,
            );
            $checks = array(
                self::check(
                    'maximum-failed-critical',
                    'Failed critical checks',
                    $failed_critical,
                    '<=',
                    $limits[
                        'maximumFailedCriticalChecks'
                    ],
                    $failed_critical
                    <= $limits[
                        'maximumFailedCriticalChecks'
                    ]
                ),
                self::check(
                    'maximum-open-major',
                    'Open major checks',
                    $open_major,
                    '<=',
                    $limits[
                        'maximumOpenMajorChecks'
                    ],
                    $open_major
                    <= $limits[
                        'maximumOpenMajorChecks'
                    ]
                ),
                self::check(
                    'minimum-evidence-coverage',
                    'Evidence coverage',
                    $evidence_percent,
                    '>=',
                    $limits[
                        'minimumEvidenceCoveragePercent'
                    ],
                    $evidence_percent
                    >= $limits[
                        'minimumEvidenceCoveragePercent'
                    ],
                    '%'
                ),
            );
        } else {
            throw new InvalidArgumentException(
                'Unsupported validation profile: '
                . $profile_id
            );
        }

        $failed = array_values(
            array_filter(
                $checks,
                static function ($item) {
                    return !$item['passed'];
                }
            )
        );
        $decision = count($failed)
            ? 'fail'
            : 'pass';

        return array(
            'schema' =>
                'sc-lab-bioprocess-validation-result/1.0',
            'version' => self::VERSION,
            'profile' => $profile,
            'thresholds' => $limits,
            'metrics' => $metrics,
            'checks' => $checks,
            'decision' => $decision,
            'failedCheckCount' => count($failed),
            'releaseRecommendation' =>
                $decision === 'pass'
                    ? 'release'
                    : 'hold',
        );
    }

    private static function canonicalize($value) {
        if (!is_array($value)) {
            return $value;
        }

        if (
            array_keys($value)
            === range(0, count($value) - 1)
        ) {
            return array_map(
                array(__CLASS__, 'canonicalize'),
                $value
            );
        }

        ksort($value, SORT_STRING);

        foreach ($value as $key => $item) {
            $value[$key] =
                self::canonicalize($item);
        }

        return $value;
    }

    public static function canonical_json($value) {
        return json_encode(
            self::canonicalize($value),
            JSON_UNESCAPED_SLASHES
            | JSON_UNESCAPED_UNICODE
            | JSON_PRESERVE_ZERO_FRACTION
            | JSON_THROW_ON_ERROR
        );
    }

    public static function fingerprint($value) {
        return hash(
            'sha256',
            self::canonical_json($value)
        );
    }

    public static function create_record(
        $payload,
        $metadata = array(),
        $previous_hash = null
    ) {
        $contract = self::contract();
        $event_type = (
            $metadata['eventType']
            ?? $contract['defaults']['eventType']
        );
        $allowed = array_column(
            $contract['eventTypes'],
            'id'
        );

        if (
            !in_array(
                $event_type,
                $allowed,
                true
            )
        ) {
            throw new InvalidArgumentException(
                'Unknown provenance event type: '
                . $event_type
            );
        }

        $timestamp = (
            $metadata['timestamp']
            ?? gmdate('c')
        );
        $record = array(
            'schema' =>
                'sc-lab-bioprocess-batch-provenance/1.0',
            'version' => self::VERSION,
            'recordId' => (
                $metadata['recordId']
                ?? (
                    'scbatch-'
                    . gmdate('YmdHis')
                    . '-'
                    . bin2hex(random_bytes(5))
                )
            ),
            'eventType' => $event_type,
            'timestamp' => $timestamp,
            'batchId' =>
                $metadata['batchId'] ?? null,
            'lotId' =>
                $metadata['lotId'] ?? null,
            'runId' =>
                $metadata['runId'] ?? null,
            'profileId' =>
                $metadata['profileId'] ?? null,
            'analyst' =>
                $metadata['analyst'] ?? null,
            'reviewer' =>
                $metadata['reviewer'] ?? null,
            'organization' => (
                $metadata['organization']
                ?? $contract['defaults']['organization']
            ),
            'instrument' =>
                $metadata['instrument'] ?? null,
            'sourceRecordIds' =>
                array_values(
                    $metadata['sourceRecordIds']
                    ?? array()
                ),
            'evidenceLinks' =>
                array_values(
                    $metadata['evidenceLinks']
                    ?? array()
                ),
            'disposition' => (
                $metadata['disposition']
                ?? $contract['defaults']['disposition']
            ),
            'notes' =>
                $metadata['notes'] ?? null,
            'previousHash' => $previous_hash,
            'payloadHash' =>
                self::fingerprint($payload),
            'payload' => $payload,
            'engine' => array(
                'validationRelease' =>
                    self::VERSION,
                'bioprocessEngineVersion' =>
                    '0.22.0',
                'productionReliabilityVersion' =>
                    '0.22.1',
                'monitoringControlVersion' =>
                    '0.22.2',
            ),
        );

        $record['recordHash'] =
            self::fingerprint($record);

        return $record;
    }

    public static function verify_ledger($records) {
        $results = array();
        $previous_hash = null;

        foreach ($records as $record) {
            $copy = $record;
            $stored_hash = (string) (
                $copy['recordHash'] ?? ''
            );
            unset($copy['recordHash']);

            $calculated_hash =
                self::fingerprint($copy);
            $payload_valid = (
                ($record['payloadHash'] ?? '')
                === self::fingerprint(
                    $record['payload'] ?? null
                )
            );
            $hash_valid = hash_equals(
                $stored_hash,
                $calculated_hash
            );
            $chain_valid = (
                ($record['previousHash'] ?? null)
                === $previous_hash
            );
            $results[] = array(
                'recordId' =>
                    $record['recordId'] ?? null,
                'payloadValid' =>
                    $payload_valid,
                'hashValid' => $hash_valid,
                'chainValid' => $chain_valid,
                'valid' => (
                    $payload_valid
                    && $hash_valid
                    && $chain_valid
                ),
                'storedHash' => $stored_hash,
                'calculatedHash' =>
                    $calculated_hash,
            );
            $previous_hash = $stored_hash;
        }

        $valid = true;

        foreach ($results as $result) {
            if (!$result['valid']) {
                $valid = false;
                break;
            }
        }

        return array(
            'schema' =>
                'sc-lab-bioprocess-ledger-verification/1.0',
            'version' => self::VERSION,
            'valid' => $valid,
            'recordCount' => count($records),
            'results' => $results,
        );
    }

    public static function create_dossier(
        $validation_results,
        $batch = array(),
        $records = array(),
        $disposition = null
    ) {
        $failed = array_values(
            array_filter(
                $validation_results,
                static function ($result) {
                    return (
                        ($result['decision'] ?? null)
                        !== 'pass'
                    );
                }
            )
        );
        $ledger = self::verify_ledger($records);
        $resolved_disposition = (
            $disposition
            ?? (
                count($failed)
                || !$ledger['valid']
                    ? 'hold'
                    : 'release'
            )
        );
        $dossier = array(
            'schema' =>
                'sc-lab-bioprocess-validation-dossier/1.0',
            'version' => self::VERSION,
            'createdAt' => gmdate('c'),
            'batch' => $batch,
            'summary' => array(
                'validationResultCount' =>
                    count($validation_results),
                'failedValidationCount' =>
                    count($failed),
                'recordCount' =>
                    count($records),
                'ledgerValid' =>
                    $ledger['valid'],
                'disposition' =>
                    $resolved_disposition,
                'releaseReady' => (
                    count($failed) === 0
                    && $ledger['valid']
                    && $resolved_disposition
                        === 'release'
                ),
            ),
            'validationResults' =>
                $validation_results,
            'provenanceLedger' => $records,
            'ledgerVerification' => $ledger,
            'responsibleUse' =>
                self::contract()['responsibleUse'],
        );
        $dossier['dossierHash'] =
            self::fingerprint($dossier);

        return $dossier;
    }

    public static function register_routes() {
        register_rest_route(
            self::NAMESPACE,
            '/compute/bioprocess/validation/profiles',
            array(
                'methods' => 'GET',
                'callback' =>
                    array(__CLASS__, 'profiles_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/bioprocess/validation/evaluate',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'evaluate_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/bioprocess/provenance/record',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'record_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/bioprocess/provenance/verify',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'verify_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/bioprocess/validation/dossier',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'dossier_response'),
                'permission_callback' => '__return_true',
            )
        );
    }

    public static function profiles_response() {
        return rest_ensure_response(
            self::contract()
        );
    }

    public static function evaluate_response($request) {
        try {
            $payload = $request->get_json_params();

            return rest_ensure_response(
                self::evaluate(
                    (string) (
                        $payload['profileId'] ?? ''
                    ),
                    $payload['rows'] ?? array(),
                    $payload['thresholds'] ?? array()
                )
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_v0223_validation_error',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function record_response($request) {
        try {
            $payload = $request->get_json_params();

            return rest_ensure_response(
                self::create_record(
                    $payload['payload'] ?? null,
                    $payload['metadata'] ?? array(),
                    $payload['previousHash'] ?? null
                )
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_v0223_provenance_error',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function verify_response($request) {
        $payload = $request->get_json_params();

        return rest_ensure_response(
            self::verify_ledger(
                $payload['records'] ?? array()
            )
        );
    }

    public static function dossier_response($request) {
        $payload = $request->get_json_params();

        return rest_ensure_response(
            self::create_dossier(
                $payload['validationResults']
                    ?? array(),
                $payload['batch'] ?? array(),
                $payload['records'] ?? array(),
                $payload['disposition'] ?? null
            )
        );
    }
}

SC_Lab_Bioprocess_Validation_REST_V0223::boot();
