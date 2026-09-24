<?php
if (!defined('ABSPATH')) define('ABSPATH',__DIR__);
$js=file_get_contents(dirname(__DIR__).'/assets/js/modules/graph-studio-recovery-v013583.js');
if (substr_count($js,'sc-lab-graph-studio-renderer-root')<1) { fwrite(STDERR,'unique root missing\n'); exit(1);}
if (strpos($js,'data-gs13582-host')===false || strpos($js,'active-graph')===false || strpos($js,'swimlane')===false) { fwrite(STDERR,'recovery contract missing\n'); exit(1);}
echo 'PASS - Lab v0.135.8.3 recovery contract\n';
