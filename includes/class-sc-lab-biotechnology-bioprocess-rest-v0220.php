<?php
/**
 * Biotechnology and Bioprocess Engineering REST engine.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Biotechnology_Bioprocess_REST_V0220 {
    const VERSION = '0.22.0';
    const NAMESPACE = 'sc-lab/v1';

    public static function boot() {
        add_action(
            'rest_api_init',
            array(__CLASS__, 'register_routes')
        );
    }

    public static function register_routes() {
        $routes = array(
            '/compute/bioprocess/methods' => array('GET', 'methods_response'),
            '/compute/bioprocess/run' => array('POST', 'run_response'),
            '/compute/bioprocess/batch' => array('POST', 'batch_response'),
            '/compute/bioprocess/simulate' => array('POST', 'simulation_response'),
            '/compute/bioprocess/health' => array('GET', 'health_response'),
        );

        foreach ($routes as $route => $definition) {
            register_rest_route(
                self::NAMESPACE,
                $route,
                array(
                    'methods' => $definition[0],
                    'callback' => array(__CLASS__, $definition[1]),
                    'permission_callback' => '__return_true',
                )
            );
        }
    }

    private static function catalog_path() {
        return dirname(__DIR__)
            . '/contracts/'
            . 'biotechnology-bioprocess-methods-v0220.json';
    }

    public static function catalog() {
        $path = self::catalog_path();

        if (!is_file($path)) {
            throw new RuntimeException(
                'The bioprocess method contract is missing.'
            );
        }

        $decoded = json_decode(
            file_get_contents($path),
            true
        );

        if (!is_array($decoded)) {
            throw new RuntimeException(
                'The bioprocess method contract is invalid.'
            );
        }

        return $decoded;
    }

    private static function method($method_id) {
        foreach (self::catalog()['methods'] as $method) {
            if ($method['id'] === $method_id) {
                return $method;
            }
        }

        throw new InvalidArgumentException(
            'Unknown bioprocess method: ' . $method_id
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

    private static function normalize_inputs($method, $supplied) {
        $values = array();
        $supplied = is_array($supplied) ? $supplied : array();

        foreach ($method['inputs'] as $input) {
            $value = array_key_exists($input['key'], $supplied)
                ? $supplied[$input['key']]
                : $input['default'];
            $number = self::finite($value, $input['label']);

            if (
                array_key_exists('min', $input)
                && $number < (float) $input['min']
            ) {
                throw new InvalidArgumentException(
                    $input['label']
                    . ' must be at least '
                    . $input['min']
                    . '.'
                );
            }

            if (
                array_key_exists('max', $input)
                && $number > (float) $input['max']
            ) {
                throw new InvalidArgumentException(
                    $input['label']
                    . ' must be at most '
                    . $input['max']
                    . '.'
                );
            }

            $values[$input['key']] = $number;
        }

        return $values;
    }

    private static function calculate_operation($operation, $a) {
        switch ($operation) {
            case 'exponential_biomass':
                return $a['x0'] * exp($a['mu'] * $a['time']);
            case 'specific_growth_rate':
                return log($a['x2'] / $a['x1']) / ($a['t2'] - $a['t1']);
            case 'doubling_time':
                return log(2.0) / $a['mu'];
            case 'monod_growth_rate':
                return $a['mu_max'] * $a['substrate'] / ($a['ks'] + $a['substrate']);
            case 'logistic_biomass':
                return $a['carrying_capacity'] / (1.0 + (($a['carrying_capacity'] - $a['x0']) / $a['x0']) * exp(-$a['mu'] * $a['time']));
            case 'viable_cell_density':
                return $a['total_cells'] * $a['viability_percent'] / 100.0;
            case 'substrate_consumed':
                return $a['initial_substrate'] - $a['final_substrate'];
            case 'biomass_yield':
                return $a['biomass_increase'] / $a['substrate_consumed'];
            case 'product_yield':
                return $a['product_formed'] / $a['substrate_consumed'];
            case 'batch_productivity':
                return $a['product_concentration'] / $a['batch_time'];
            case 'maintenance_substrate':
                return $a['maintenance_coefficient'] * $a['biomass'] * $a['time'];
            case 'carbon_recovery':
                return $a['carbon_outputs'] / $a['carbon_inputs'] * 100.0;
            case 'feed_volume':
                return $a['feed_rate'] * $a['time'];
            case 'fed_batch_final_volume':
                return $a['initial_volume'] + $a['feed_rate'] * $a['time'];
            case 'substrate_mass_fed':
                return $a['feed_rate'] * $a['feed_concentration'] * $a['time'];
            case 'exponential_feed_rate':
                return $a['initial_feed_rate'] * exp($a['mu_set'] * $a['time']);
            case 'apparent_dilution_rate':
                return $a['feed_rate'] / $a['reactor_volume'];
            case 'fed_batch_substrate_balance':
                return $a['initial_substrate_mass'] + $a['substrate_fed'] - $a['substrate_consumed'];
            case 'dilution_rate':
                return $a['flow_rate'] / $a['reactor_volume'];
            case 'residence_time':
                return $a['reactor_volume'] / $a['flow_rate'];
            case 'chemostat_biomass':
                return $a['yield_coefficient'] * ($a['feed_substrate'] - $a['residual_substrate']);
            case 'washout_margin':
                return $a['mu_max'] - $a['dilution_rate'];
            case 'continuous_productivity':
                return $a['dilution_rate'] * $a['product_concentration'];
            case 'critical_dilution_monod':
                return $a['mu_max'] * $a['feed_substrate'] / ($a['ks'] + $a['feed_substrate']);
            case 'oxygen_transfer_rate':
                return $a['kla'] * ($a['saturation_concentration'] - $a['liquid_concentration']);
            case 'oxygen_uptake_rate':
                return $a['specific_oxygen_uptake'] * $a['biomass'];
            case 'kla_from_otr':
                return $a['otr'] / ($a['saturation_concentration'] - $a['liquid_concentration']);
            case 'oxygen_balance_margin':
                return $a['otr'] - $a['our'];
            case 'aeration_vvm':
                return $a['gas_flow'] / $a['reactor_volume'];
            case 'gas_molar_flow':
                return $a['volumetric_flow'] * $a['pressure'] / (0.082057 * $a['temperature']);
            case 'metabolic_heat':
                return $a['heat_per_biomass'] * $a['biomass_rate'];
            case 'cooling_water_flow':
                return $a['heat_duty'] / ($a['heat_capacity'] * $a['temperature_rise']);
            case 'impeller_tip_speed':
                return M_PI * $a['impeller_diameter'] * $a['rotation_speed'] / 60.0;
            case 'power_per_volume':
                return $a['power'] / $a['volume'];
            case 'reynolds_mixing':
                return $a['density'] * $a['rotation_speed'] * pow($a['impeller_diameter'], 2) / $a['dynamic_viscosity'];
            case 'mixing_time_correlation':
                return $a['coefficient'] * pow($a['volume'] / $a['power'], $a['exponent']);
            case 'geometric_scale_factor':
                return $a['target_volume'] / $a['base_volume'];
            case 'linear_scale_factor':
                return pow($a['target_volume'] / $a['base_volume'], 1.0 / 3.0);
            case 'constant_tip_speed_rpm':
                return $a['base_rpm'] * $a['base_diameter'] / $a['target_diameter'];
            case 'constant_power_volume':
                return $a['base_power'] * $a['target_volume'] / $a['base_volume'];
            case 'cylinder_area_volume':
                return (M_PI * $a['diameter'] * $a['height'] + 2.0 * M_PI * pow($a['diameter'] / 2.0, 2)) / (M_PI * pow($a['diameter'] / 2.0, 2) * $a['height']);
            case 'superficial_gas_velocity':
                return $a['gas_flow'] / $a['cross_section_area'];
            case 'luedeking_piret_product':
                return ($a['alpha'] * $a['mu'] + $a['beta']) * $a['biomass'] * $a['time'];
            case 'specific_productivity':
                return $a['product_rate'] / $a['biomass'];
            case 'harvest_titer':
                return $a['product_mass'] / $a['harvest_volume'];
            case 'downstream_recovery':
                return $a['recovered_mass'] / $a['feed_mass'] * 100.0;
            case 'volumetric_productivity':
                return $a['product_mass'] / ($a['reactor_volume'] * $a['process_time']);
            case 'overall_process_yield':
                return $a['final_product_mass'] / $a['theoretical_product_mass'] * 100.0;
            default:
                throw new InvalidArgumentException(
                    'Unsupported bioprocess operation: '
                    . $operation
                );
        }
    }

    public static function calculate($method_id, $inputs = array()) {
        $method = self::method((string) $method_id);
        $values = self::normalize_inputs($method, $inputs);

        if (
            $method['operation'] === 'specific_growth_rate'
            && $values['t2'] == $values['t1']
        ) {
            throw new InvalidArgumentException(
                'Final time must differ from initial time.'
            );
        }

        if (
            $method['operation'] === 'substrate_consumed'
            && $values['final_substrate']
                > $values['initial_substrate']
        ) {
            throw new InvalidArgumentException(
                'Final substrate cannot exceed initial substrate.'
            );
        }

        if (
            $method['operation'] === 'kla_from_otr'
            && $values['saturation_concentration']
                == $values['liquid_concentration']
        ) {
            throw new InvalidArgumentException(
                'Oxygen driving force must be non-zero.'
            );
        }

        $result = self::calculate_operation(
            $method['operation'],
            $values
        );

        if (!is_finite($result)) {
            throw new RuntimeException(
                'Calculation produced a non-finite result.'
            );
        }

        return array(
            'schema' =>
                'sc-lab-biotechnology-bioprocess-result/1.0',
            'version' => self::VERSION,
            'methodId' => $method['id'],
            'title' => $method['title'],
            'category' => $method['category'],
            'formula' => $method['formula'],
            'inputs' => $values,
            'outputs' => array('result' => $result),
            'outputDefinition' => $method['outputs']['result'],
            'warnings' => array(),
            'audit' => array(
                'createdAt' => gmdate('c'),
                'engine' => 'sc-lab-bioprocess-php',
                'release' => self::VERSION,
            ),
        );
    }

    private static function summarize($values) {
        if (!$values) {
            return array(
                'n' => 0,
                'mean' => null,
                'standardDeviation' => null,
                'coefficientOfVariationPercent' => null,
                'minimum' => null,
                'maximum' => null,
            );
        }

        $mean = array_sum($values) / count($values);
        $sd = 0.0;

        if (count($values) > 1) {
            $sum = 0.0;

            foreach ($values as $value) {
                $sum += pow($value - $mean, 2);
            }

            $sd = sqrt($sum / (count($values) - 1));
        }

        return array(
            'n' => count($values),
            'mean' => $mean,
            'standardDeviation' => $sd,
            'coefficientOfVariationPercent' =>
                $mean == 0.0
                    ? null
                    : abs($sd / $mean) * 100.0,
            'minimum' => min($values),
            'maximum' => max($values),
        );
    }

    public static function batch_calculate($method_id, $rows) {
        if (!is_array($rows) || !$rows) {
            throw new InvalidArgumentException(
                'At least one batch row is required.'
            );
        }

        $results = array();
        $values = array();

        foreach ($rows as $index => $row) {
            $row = is_array($row) ? $row : array();
            $sample = isset($row['sample'])
                ? (string) $row['sample']
                : 'sample-' . ($index + 1);
            $inputs = isset($row['inputs'])
                && is_array($row['inputs'])
                    ? $row['inputs']
                    : $row;
            unset($inputs['sample'], $inputs['inputs']);

            try {
                $analysis = self::calculate(
                    $method_id,
                    $inputs
                );
                $values[] = $analysis['outputs']['result'];
                $results[] = array(
                    'sample' => $sample,
                    'ok' => true,
                    'analysis' => $analysis,
                );
            } catch (Throwable $error) {
                $results[] = array(
                    'sample' => $sample,
                    'ok' => false,
                    'error' => $error->getMessage(),
                );
            }
        }

        $statistics = self::summarize($values);
        $flags = array();

        if (
            $statistics['coefficientOfVariationPercent'] !== null
            && $statistics['coefficientOfVariationPercent'] > 20.0
        ) {
            $flags[] =
                'Coefficient of variation exceeds 20%.';
        }

        $error_count = count($results) - count($values);

        if ($error_count > 0) {
            $flags[] =
                $error_count . ' row(s) failed.';
        }

        return array(
            'schema' => 'sc-lab-bioprocess-batch/1.0',
            'version' => self::VERSION,
            'methodId' => (string) $method_id,
            'rowCount' => count($results),
            'successCount' => count($values),
            'errorCount' => $error_count,
            'results' => $results,
            'statistics' => $statistics,
            'flags' => $flags,
            'audit' => array(
                'createdAt' => gmdate('c'),
                'engine' =>
                    'sc-lab-bioprocess-batch-php',
                'release' => self::VERSION,
            ),
        );
    }

    public static function simulate($mode, $parameters = array()) {
        $p = is_array($parameters) ? $parameters : array();

        if ($mode === 'batch') {
            $x0 = self::finite($p['x0'] ?? 1, 'Initial biomass');
            $mu = self::finite($p['mu'] ?? 0.3, 'Growth rate');
            $time = self::finite($p['time'] ?? 24, 'Time');
            $s0 = self::finite($p['substrate0'] ?? 40, 'Initial substrate');
            $yield_xs = self::finite($p['yieldXs'] ?? 0.5, 'Biomass yield');
            $yield_ps = self::finite($p['yieldPs'] ?? 0.2, 'Product yield');
            $points = array();

            for ($index = 0; $index <= 40; $index++) {
                $t = $time * $index / 40.0;
                $ideal = $x0 * exp($mu * $t);
                $maximum = $x0 + $s0 * $yield_xs;
                $biomass = min($ideal, $maximum);
                $substrate = max(
                    0.0,
                    $s0 - ($biomass - $x0) / $yield_xs
                );
                $product = ($s0 - $substrate) * $yield_ps;
                $points[] = compact(
                    't',
                    'biomass',
                    'substrate',
                    'product'
                );
                $points[count($points) - 1]['time'] = $t;
                unset($points[count($points) - 1]['t']);
            }

            return array(
                'mode' => 'batch',
                'points' => $points,
                'summary' => $points[count($points) - 1],
            );
        }

        if ($mode === 'fed-batch') {
            $v0 = self::finite($p['initialVolume'] ?? 5, 'Initial volume');
            $f0 = self::finite($p['initialFeedRate'] ?? 0.05, 'Initial feed rate');
            $mu = self::finite($p['muSet'] ?? 0.15, 'Target growth rate');
            $cf = self::finite($p['feedConcentration'] ?? 500, 'Feed concentration');
            $x0 = self::finite($p['x0'] ?? 2, 'Initial biomass');
            $time = self::finite($p['time'] ?? 24, 'Time');
            $points = array();

            for ($index = 0; $index <= 40; $index++) {
                $t = $time * $index / 40.0;
                $feed_rate = $f0 * exp($mu * $t);
                $cumulative = $index === 0
                    ? 0.0
                    : $f0 / $mu * (exp($mu * $t) - 1.0);
                $volume = $v0 + $cumulative;
                $biomass =
                    $x0 * exp($mu * $t) * $v0 / $volume;
                $points[] = array(
                    'time' => $t,
                    'feedRate' => $feed_rate,
                    'volume' => $volume,
                    'biomass' => $biomass,
                    'substrateFed' => $cumulative * $cf,
                );
            }

            return array(
                'mode' => 'fed-batch',
                'points' => $points,
                'summary' => $points[count($points) - 1],
            );
        }

        if ($mode === 'continuous') {
            $volume = self::finite($p['volume'] ?? 10, 'Volume');
            $flow = self::finite($p['flowRate'] ?? 1.5, 'Flow rate');
            $mu_max = self::finite($p['muMax'] ?? 0.5, 'Maximum growth rate');
            $ks = self::finite($p['ks'] ?? 0.5, 'Ks');
            $feed = self::finite($p['feedSubstrate'] ?? 20, 'Feed substrate');
            $yield = self::finite($p['yieldXs'] ?? 0.5, 'Yield');
            $product = self::finite($p['productConcentration'] ?? 12, 'Product concentration');
            $dilution = $flow / $volume;
            $washout = $dilution >= $mu_max;
            $residual = $washout
                ? $feed
                : min(
                    $feed,
                    $ks * $dilution / ($mu_max - $dilution)
                );
            $biomass = $washout
                ? 0.0
                : $yield * ($feed - $residual);
            $summary = array(
                'dilutionRate' => $dilution,
                'residualSubstrate' => $residual,
                'biomass' => $biomass,
                'productivity' => $dilution * $product,
                'washoutMargin' => $mu_max - $dilution,
                'washout' => $washout,
            );

            return array(
                'mode' => 'continuous',
                'points' => array($summary),
                'summary' => $summary,
            );
        }

        throw new InvalidArgumentException(
            'Unknown simulation mode: ' . $mode
        );
    }

    public static function methods_response() {
        return rest_ensure_response(self::catalog());
    }

    public static function run_response($request) {
        $payload = $request->get_json_params();

        try {
            return rest_ensure_response(
                self::calculate(
                    isset($payload['methodId'])
                        ? $payload['methodId']
                        : '',
                    isset($payload['inputs'])
                        ? $payload['inputs']
                        : array()
                )
            );
        } catch (InvalidArgumentException $error) {
            return new WP_Error(
                'sc_lab_bioprocess_invalid',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function batch_response($request) {
        $payload = $request->get_json_params();

        try {
            return rest_ensure_response(
                self::batch_calculate(
                    isset($payload['methodId'])
                        ? $payload['methodId']
                        : '',
                    isset($payload['rows'])
                        ? $payload['rows']
                        : array()
                )
            );
        } catch (InvalidArgumentException $error) {
            return new WP_Error(
                'sc_lab_bioprocess_batch_invalid',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function simulation_response($request) {
        $payload = $request->get_json_params();

        try {
            return rest_ensure_response(
                self::simulate(
                    isset($payload['mode'])
                        ? $payload['mode']
                        : '',
                    isset($payload['parameters'])
                        ? $payload['parameters']
                        : array()
                )
            );
        } catch (InvalidArgumentException $error) {
            return new WP_Error(
                'sc_lab_bioprocess_simulation_invalid',
                $error->getMessage(),
                array('status' => 422)
            );
        }
    }

    public static function health_response() {
        $catalog = self::catalog();

        return rest_ensure_response(
            array(
                'ok' => true,
                'status' => 'ready',
                'release' => self::VERSION,
                'methodCount' => count($catalog['methods']),
                'benchmarkCount' => count($catalog['benchmarks']),
                'categoryCount' => count($catalog['categories']),
            )
        );
    }
}

SC_Lab_Biotechnology_Bioprocess_REST_V0220::boot();
