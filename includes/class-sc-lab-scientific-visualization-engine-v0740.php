<?php
/** Sustainable Catalyst Lab v0.74.0 Advanced 2D Scientific Plot Grammar. */
if (!defined('ABSPATH')) { exit; }
final class SC_Lab_Scientific_Visualization_Engine_V0740 {
    const VERSION = '0.74.0';
    const ENGINE_VERSION = '2.1.0';
    private static $initialized = false;
    public static function init() { if (self::$initialized) { return; } self::$initialized = true; add_action('rest_api_init', array(__CLASS__, 'routes')); }
    public static function routes() {
        register_rest_route('sc-lab/v1', '/visualization/v0740/health', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));
        register_rest_route('sc-lab/v1', '/visualization/v0740/schema', array('methods'=>WP_REST_Server::READABLE,'callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));
    }
    private static function file_state($relative) { $path = SC_LAB_DIR . ltrim((string)$relative, '/'); return array('exists'=>is_file($path),'sha256'=>is_file($path)?hash_file('sha256',$path):null); }
    public static function schema() {
        return rest_ensure_response(array(
            'ok'=>true,'version'=>self::VERSION,'engineVersion'=>self::ENGINE_VERSION,
            'plotGrammar'=>'sc-lab-advanced-2d-plot-grammar/0.74.0',
            'specSchema'=>'sc-lab-scientific-visualization/0.74.0','figureSchema'=>'sc-lab-scientific-figure/0.74.0','workspaceSchema'=>'sc-lab-figure-workspace/0.74.0',
            'renderers'=>array(
                'svg2d'=>array('version'=>'0.74.0','kinds'=>array('line','scatter','line-scatter','step','area','stacked-area','bar','grouped-bar','stacked-bar','histogram','horizontal-bars','density','box','violin','error-bar','confidence-band','heatmap','contour','hexbin','ecdf','qq','residual','waterfall','pareto'),'exports'=>array('svg','png','csv','json')),
                'canvas4d'=>array('version'=>'0.71.0','kinds'=>array('surface-4d'),'exports'=>array('png','json')),
            ),
            'axisScales'=>array('linear','log','symlog','probability','datetime','categorical'),
            'tickFormats'=>array('auto','scientific','si','plain','percent'),
            'boundaries'=>array('polarRadar'=>false,'dualAxis'=>false,'rawDataTransformationPipeline'=>'v0.75.0','surface4dProjectDataBinding'=>false,'arbitraryCode'=>false),
        ));
    }
    public static function health() {
        $required=array('backend/app/visualization_engine_v0740.py','backend/tests/test_visualization_engine_v0740.py','assets/js/modules/scientific-visualization-engine-v0740.js','assets/js/modules/graph-studio-v0740.js','assets/css/sc-lab-scientific-visualization-engine-v0740.css','contracts/advanced-2d-plot-grammar-v0740.json','contracts/scientific-visualization-v0740.schema.json','contracts/scientific-figure-v0740.schema.json','contracts/figure-workspace-v0740.schema.json','assets/js/modules/scientific-visualization-engine-v0730.js','assets/js/modules/advanced-visualization-front-door-v0710.js');
        $files=array();$ok=true;foreach($required as $relative){$files[$relative]=self::file_state($relative);if(empty($files[$relative]['exists'])){$ok=false;}}
        return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'advanced-2d-plot-grammar-ready':'incomplete','version'=>self::VERSION,'release'=>defined('SC_LAB_RELEASE_VERSION')?SC_LAB_RELEASE_VERSION:null,'platformVersion'=>defined('SC_LAB_PLATFORM_VERSION')?SC_LAB_PLATFORM_VERSION:null,'engineVersion'=>self::ENGINE_VERSION,'rendererRegistry'=>array('svg2d','canvas4d'),'advanced2d'=>true,'legacy2dCompatibility'=>true,'canvas4dCompatibility'=>true,'axisScales'=>array('linear','log','symlog','probability','datetime','categorical'),'polarRadarDeferred'=>true,'dualAxisDeferred'=>true,'surface4dProjectDataBinding'=>false,'arbitraryCode'=>false,'files'=>$files,'time'=>gmdate('c')));
    }
}
