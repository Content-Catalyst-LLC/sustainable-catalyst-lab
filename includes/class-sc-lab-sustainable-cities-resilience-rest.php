<?php
/**
 * Sustainable Cities and Urban Resilience REST proxy.
 *
 * @package Sustainable_Catalyst_Lab
 */

if (!defined('ABSPATH')) {
    exit;
}

final class SC_Lab_Sustainable_Cities_Resilience_REST {
    const VERSION = '0.15.0';

    /**
     * Register routes.
     *
     * @return void
     */
    public static function boot() {
        add_action(
            'rest_api_init',
            array(__CLASS__, 'register_routes')
        );
    }

    /**
     * Register browser-facing proxy routes.
     *
     * @return void
     */
    public static function register_routes() {
        register_rest_route(
            'sc-lab/v1',
            '/compute/sustainable-cities/methods',
            array(
                'methods' => 'GET',
                'callback' => array(__CLASS__, 'methods'),
                'permission_callback' => '__return_true',
            )
        );

        register_rest_route(
            'sc-lab/v1',
            '/compute/sustainable-cities/run',
            array(
                'methods' => 'POST',
                'callback' => array(__CLASS__, 'run'),
                'permission_callback' => '__return_true',
            )
        );
    }

    /**
     * Resolve the optional backend URL.
     *
     * @return string
     */
    private static function backend_url() {
        $candidates = array();

        if (defined('SC_LAB_BACKEND_URL')) {
            $candidates[] = constant('SC_LAB_BACKEND_URL');
        }

        if (defined('SC_LAB_COMPUTE_URL')) {
            $candidates[] = constant('SC_LAB_COMPUTE_URL');
        }

        $candidates[] = get_option('sc_lab_backend_url', '');
        $candidates[] = get_option('sc_lab_compute_url', '');
        $candidates[] = get_option('sc_lab_render_url', '');

        foreach ($candidates as $candidate) {
            $candidate = esc_url_raw(trim((string) $candidate));

            if ($candidate !== '') {
                return untrailingslashit($candidate);
            }
        }

        return '';
    }

    /**
     * Resolve the server-side API key.
     *
     * @return string
     */
    private static function api_key() {
        if (defined('SC_LAB_API_KEY')) {
            return trim((string) constant('SC_LAB_API_KEY'));
        }

        if (defined('SC_LAB_COMPUTE_API_KEY')) {
            return trim((string) constant('SC_LAB_COMPUTE_API_KEY'));
        }

        foreach (
            array(
                get_option('sc_lab_api_key', ''),
                get_option('sc_lab_compute_api_key', ''),
            )
            as $candidate
        ) {
            $candidate = trim((string) $candidate);

            if ($candidate !== '') {
                return $candidate;
            }
        }

        return '';
    }

    /**
     * Proxy a request to FastAPI.
     *
     * @param string               $path Backend path.
     * @param string               $method HTTP method.
     * @param array<string, mixed> $payload JSON payload.
     * @return mixed
     */
    private static function proxy(
        $path,
        $method = 'GET',
        $payload = array()
    ) {
        $backend = self::backend_url();

        if ($backend === '') {
            return new WP_Error(
                'sc_lab_sustainable_cities_backend_unavailable',
                'The optional Lab compute backend is not configured.',
                array('status' => 503)
            );
        }

        $headers = array(
            'Accept' => 'application/json',
            'Content-Type' => 'application/json',
        );

        $key = self::api_key();

        if ($key !== '') {
            $headers['X-SC-Lab-Key'] = $key;
        }

        $arguments = array(
            'method' => strtoupper((string) $method),
            'headers' => $headers,
            'timeout' => 30,
        );

        if (strtoupper((string) $method) !== 'GET') {
            $arguments['body'] = wp_json_encode($payload);
        }

        $response = wp_remote_request(
            $backend . '/' . ltrim((string) $path, '/'),
            $arguments
        );

        if (is_wp_error($response)) {
            return $response;
        }

        $status = (int) wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        $decoded = json_decode($body, true);

        if (!is_array($decoded)) {
            return new WP_Error(
                'sc_lab_sustainable_cities_backend_response',
                'The Lab backend returned an invalid JSON response.',
                array(
                    'status' => 502,
                    'backend_status' => $status,
                )
            );
        }

        if ($status < 200 || $status >= 300) {
            return new WP_Error(
                'sc_lab_sustainable_cities_backend_error',
                isset($decoded['detail'])
                    ? sanitize_text_field((string) $decoded['detail'])
                    : 'The Lab backend rejected the request.',
                array(
                    'status' => $status > 0 ? $status : 502,
                    'response' => $decoded,
                )
            );
        }

        return rest_ensure_response($decoded);
    }

    /**
     * Return the method catalog.
     *
     * @return mixed
     */
    public static function methods() {
        return self::proxy('/v1/sustainable-cities/methods');
    }

    /**
     * Run one method.
     *
     * @param WP_REST_Request $request Request object.
     * @return mixed
     */
    public static function run($request) {
        $body = $request->get_json_params();

        if (!is_array($body)) {
            return new WP_Error(
                'sc_lab_sustainable_cities_invalid_payload',
                'A JSON object is required.',
                array('status' => 422)
            );
        }

        $method_id = isset($body['methodId'])
            ? sanitize_text_field((string) $body['methodId'])
            : '';

        if ($method_id === '' || strpos($method_id, 'sc.') !== 0) {
            return new WP_Error(
                'sc_lab_sustainable_cities_invalid_method',
                'A methodId beginning with sc. is required.',
                array('status' => 422)
            );
        }

        $raw_inputs = (
            isset($body['inputs'])
            && is_array($body['inputs'])
        )
            ? $body['inputs']
            : array();

        $inputs = array();

        foreach ($raw_inputs as $key => $value) {
            if (!is_numeric($value)) {
                return new WP_Error(
                    'sc_lab_sustainable_cities_invalid_input',
                    'Sustainable-city inputs must be numeric.',
                    array('status' => 422)
                );
            }

            $inputs[sanitize_key((string) $key)] = (float) $value;
        }

        return self::proxy(
            '/v1/sustainable-cities/run',
            'POST',
            array(
                'methodId' => $method_id,
                'inputs' => $inputs,
            )
        );
    }
}

SC_Lab_Sustainable_Cities_Resilience_REST::boot();
