<?php
/**
 * REST endpoints and safe expression evaluator for v0.21.0.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Biochemistry_Expression_Parser {
    private $tokens = array();
    private $index = 0;
    private $variables = array();

    public function evaluate($expression, $variables) {
        $this->tokens = $this->tokenize(
            (string) $expression
        );
        $this->index = 0;
        $this->variables = is_array($variables)
            ? $variables
            : array();

        $value = $this->parse_expression();

        if ($this->current_type() !== 'eof') {
            throw new InvalidArgumentException(
                'Unexpected expression token.'
            );
        }

        if (!is_finite((float) $value)) {
            throw new InvalidArgumentException(
                'Expression did not produce a finite result.'
            );
        }

        return (float) $value;
    }

    private function tokenize($expression) {
        $tokens = array();
        $offset = 0;
        $length = strlen($expression);

        while ($offset < $length) {
            $fragment = substr($expression, $offset);

            if (
                !preg_match(
                    '/\A\s*(?:'
                    . '(\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)'
                    . '|([A-Za-z_][A-Za-z0-9_]*)'
                    . '|(\*\*|[+\-*\/(),])'
                    . ')/',
                    $fragment,
                    $match
                )
            ) {
                throw new InvalidArgumentException(
                    'Unsupported expression syntax.'
                );
            }

            $offset += strlen($match[0]);

            if (isset($match[1]) && $match[1] !== '') {
                $tokens[] = array(
                    'type' => 'number',
                    'value' => (float) $match[1],
                );
                continue;
            }

            if (isset($match[2]) && $match[2] !== '') {
                $tokens[] = array(
                    'type' => 'identifier',
                    'value' => $match[2],
                );
                continue;
            }

            $tokens[] = array(
                'type' => 'operator',
                'value' => $match[3],
            );
        }

        $tokens[] = array(
            'type' => 'eof',
            'value' => null,
        );

        return $tokens;
    }

    private function current() {
        return $this->tokens[$this->index];
    }

    private function current_type() {
        return $this->current()['type'];
    }

    private function current_value() {
        return $this->current()['value'];
    }

    private function advance() {
        $token = $this->current();
        $this->index += 1;
        return $token;
    }

    private function match_operator($operator) {
        if (
            $this->current_type() === 'operator'
            && $this->current_value() === $operator
        ) {
            $this->advance();
            return true;
        }

        return false;
    }

    private function expect_operator($operator) {
        if (!$this->match_operator($operator)) {
            throw new InvalidArgumentException(
                'Expected expression operator '
                . $operator
                . '.'
            );
        }
    }

    private function parse_expression() {
        $value = $this->parse_term();

        while (
            $this->current_type() === 'operator'
            && in_array(
                $this->current_value(),
                array('+', '-'),
                true
            )
        ) {
            $operator = $this->advance()['value'];
            $right = $this->parse_term();

            $value = $operator === '+'
                ? $value + $right
                : $value - $right;
        }

        return $value;
    }

    private function parse_term() {
        $value = $this->parse_power();

        while (
            $this->current_type() === 'operator'
            && in_array(
                $this->current_value(),
                array('*', '/'),
                true
            )
        ) {
            $operator = $this->advance()['value'];
            $right = $this->parse_power();

            if ($operator === '/') {
                if ((float) $right == 0.0) {
                    throw new InvalidArgumentException(
                        'Division by zero.'
                    );
                }

                $value /= $right;
            } else {
                $value *= $right;
            }
        }

        return $value;
    }

    private function parse_power() {
        $value = $this->parse_unary();

        if ($this->match_operator('**')) {
            $value = pow(
                $value,
                $this->parse_power()
            );
        }

        return $value;
    }

    private function parse_unary() {
        if ($this->match_operator('+')) {
            return $this->parse_unary();
        }

        if ($this->match_operator('-')) {
            return -$this->parse_unary();
        }

        return $this->parse_primary();
    }

    private function parse_primary() {
        if ($this->current_type() === 'number') {
            return $this->advance()['value'];
        }

        if ($this->current_type() === 'identifier') {
            $identifier = $this->advance()['value'];

            if ($this->match_operator('(')) {
                $arguments = array();

                if (!$this->match_operator(')')) {
                    do {
                        $arguments[] =
                            $this->parse_expression();
                    } while ($this->match_operator(','));

                    $this->expect_operator(')');
                }

                return $this->call_function(
                    $identifier,
                    $arguments
                );
            }

            if (
                !array_key_exists(
                    $identifier,
                    $this->variables
                )
            ) {
                throw new InvalidArgumentException(
                    'Unknown expression variable: '
                    . $identifier
                );
            }

            return (float) $this->variables[$identifier];
        }

        if ($this->match_operator('(')) {
            $value = $this->parse_expression();
            $this->expect_operator(')');
            return $value;
        }

        throw new InvalidArgumentException(
            'Expected a number, variable, or function.'
        );
    }

    private function call_function($name, $arguments) {
        switch ($name) {
            case 'pow':
                if (count($arguments) === 2) {
                    return pow(
                        $arguments[0],
                        $arguments[1]
                    );
                }
                break;

            case 'sqrt':
                if (count($arguments) === 1) {
                    if ($arguments[0] < 0) {
                        throw new InvalidArgumentException(
                            'Square-root input must not be negative.'
                        );
                    }
                    return sqrt($arguments[0]);
                }
                break;

            case 'log':
                if (count($arguments) === 1) {
                    if ($arguments[0] <= 0) {
                        throw new InvalidArgumentException(
                            'Natural-log input must be positive.'
                        );
                    }
                    return log($arguments[0]);
                }
                break;

            case 'log10':
                if (count($arguments) === 1) {
                    if ($arguments[0] <= 0) {
                        throw new InvalidArgumentException(
                            'Base-10-log input must be positive.'
                        );
                    }
                    return log10($arguments[0]);
                }
                break;

            case 'exp':
                if (count($arguments) === 1) {
                    return exp($arguments[0]);
                }
                break;

            case 'abs':
                if (count($arguments) === 1) {
                    return abs($arguments[0]);
                }
                break;

            case 'min':
                if ($arguments) {
                    return min($arguments);
                }
                break;

            case 'max':
                if ($arguments) {
                    return max($arguments);
                }
                break;
        }

        throw new InvalidArgumentException(
            'Unsupported function or argument count: '
            . $name
        );
    }
}

final class SC_Lab_Biochemistry_Molecular_Analysis_REST {
    const VERSION = '0.21.0';
    const NAMESPACE = 'sc-lab/v1';

    private static $catalog = null;

    public static function boot() {
        add_action(
            'rest_api_init',
            array(__CLASS__, 'register_routes')
        );
    }

    private static function catalog_path() {
        return dirname(__DIR__)
            . '/contracts/'
            . 'biochemistry-molecular-analysis-methods.json';
    }

    public static function catalog() {
        if (is_array(self::$catalog)) {
            return self::$catalog;
        }

        $path = self::catalog_path();

        if (!is_file($path)) {
            throw new RuntimeException(
                'The biochemistry method catalog is missing.'
            );
        }

        $decoded = json_decode(
            file_get_contents($path),
            true
        );

        if (!is_array($decoded)) {
            throw new RuntimeException(
                'The biochemistry method catalog is invalid.'
            );
        }

        self::$catalog = $decoded;
        return self::$catalog;
    }

    private static function method($method_id) {
        foreach (self::catalog()['methods'] as $method) {
            if ($method['id'] === $method_id) {
                return $method;
            }
        }

        throw new InvalidArgumentException(
            'Unknown biochemistry method: ' . $method_id
        );
    }

    public static function calculate($method_id, $raw_inputs) {
        $method = self::method((string) $method_id);
        $inputs = array();

        foreach ($method['inputs'] as $specification) {
            $key = $specification['key'];
            $value = isset($raw_inputs[$key])
                ? filter_var(
                    $raw_inputs[$key],
                    FILTER_VALIDATE_FLOAT
                )
                : false;

            if (
                $value === false
                || !is_finite((float) $value)
            ) {
                throw new InvalidArgumentException(
                    $specification['label']
                    . ' must be a finite number.'
                );
            }

            $value = (float) $value;

            if (
                isset($specification['min'])
                && $value < (float) $specification['min']
            ) {
                throw new InvalidArgumentException(
                    $specification['label']
                    . ' is below its allowed minimum.'
                );
            }

            if (
                isset($specification['max'])
                && $value > (float) $specification['max']
            ) {
                throw new InvalidArgumentException(
                    $specification['label']
                    . ' exceeds its allowed maximum.'
                );
            }

            $inputs[$key] = $value;
        }

        $parser =
            new SC_Lab_Biochemistry_Expression_Parser();
        $outputs = array();
        $output_units = array();
        $expressions = array();

        foreach (
            $method['outputs']
            as $key => $specification
        ) {
            $outputs[$key] = $parser->evaluate(
                $specification['expression'],
                $inputs
            );
            $output_units[$key] =
                $specification['unit'];
            $expressions[$key] =
                $specification['expression'];
        }

        $warnings = self::warnings(
            $method['id'],
            $outputs,
            $inputs
        );

        return array(
            'schema' =>
                'sc-lab-biochemistry-analysis/1.0',
            'version' => self::VERSION,
            'methodId' => $method['id'],
            'methodVersion' => $method['version'],
            'category' => $method['category'],
            'title' => $method['title'],
            'equation' => $method['equation'],
            'expressions' => $expressions,
            'inputs' => $inputs,
            'inputUnits' => array_column(
                $method['inputs'],
                'unit',
                'key'
            ),
            'outputs' => $outputs,
            'outputUnits' => $output_units,
            'assumptions' =>
                isset($method['assumptions'])
                    ? $method['assumptions']
                    : array(),
            'notes' =>
                isset($method['notes'])
                    ? $method['notes']
                    : array(),
            'warnings' => $warnings,
            'validation' => array(
                'status' => $warnings
                    ? 'review'
                    : 'screened',
                'benchmarkSuite' =>
                    'sc-lab-biochemistry-molecular-analysis-benchmarks/1.0',
            ),
            'audit' => array(
                'createdAt' => gmdate('c'),
                'engine' =>
                    'sc-lab-biochemistry-molecular-analysis-php',
                'release' => self::VERSION,
            ),
        );
    }

    private static function warnings(
        $method_id,
        $outputs,
        $inputs
    ) {
        $warnings = array();

        foreach ($outputs as $key => $value) {
            if (
                stripos($key, 'percent') !== false
                && ($value < 0 || $value > 100)
            ) {
                $warnings[] =
                    $key
                    . ' lies outside the expected 0–100% interval.';
            }

            if (
                stripos($key, 'fraction') !== false
                && ($value < 0 || $value > 1)
            ) {
                $warnings[] =
                    $key
                    . ' lies outside the expected 0–1 interval.';
            }
        }

        if (
            isset($inputs['pH'])
            && ($inputs['pH'] < 0 || $inputs['pH'] > 14)
        ) {
            $warnings[] =
                'The stated pH is outside the conventional '
                . 'aqueous 0–14 range.';
        }

        if (
            $method_id === 'bc.chromatography_resolution'
            && $outputs['resolution'] < 1.5
        ) {
            $warnings[] =
                'Resolution is below 1.5; baseline separation '
                . 'may not be achieved.';
        }

        return $warnings;
    }

    public static function register_routes() {
        register_rest_route(
            self::NAMESPACE,
            '/compute/biochemistry/methods',
            array(
                'methods' => 'GET',
                'callback' =>
                    array(__CLASS__, 'methods_response'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            self::NAMESPACE,
            '/compute/biochemistry/run',
            array(
                'methods' => 'POST',
                'callback' =>
                    array(__CLASS__, 'run_response'),
                'permission_callback' => '__return_true',
            )
        );
    }

    public static function methods_response() {
        try {
            return rest_ensure_response(self::catalog());
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_biochemistry_catalog_error',
                $error->getMessage(),
                array('status' => 500)
            );
        }
    }

    public static function run_response($request) {
        $payload = $request->get_json_params();
        $method_id = isset($payload['methodId'])
            ? (string) $payload['methodId']
            : '';
        $inputs = isset($payload['inputs'])
            && is_array($payload['inputs'])
            ? $payload['inputs']
            : array();

        if ($method_id === '') {
            return new WP_Error(
                'sc_lab_biochemistry_method_required',
                'methodId is required.',
                array('status' => 422)
            );
        }

        try {
            return rest_ensure_response(
                self::calculate($method_id, $inputs)
            );
        } catch (InvalidArgumentException $error) {
            return new WP_Error(
                'sc_lab_biochemistry_invalid_input',
                $error->getMessage(),
                array('status' => 422)
            );
        } catch (Throwable $error) {
            return new WP_Error(
                'sc_lab_biochemistry_run_error',
                $error->getMessage(),
                array('status' => 500)
            );
        }
    }
}

SC_Lab_Biochemistry_Molecular_Analysis_REST::boot();
