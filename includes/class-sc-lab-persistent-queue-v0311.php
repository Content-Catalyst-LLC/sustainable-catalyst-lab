<?php
if(!defined('ABSPATH')){exit;}
final class SC_Lab_Persistent_Queue_V0311{
 const VERSION='0.31.1';
 public static function init(){add_action('rest_api_init',array(__CLASS__,'routes'));add_filter('sc_lab_panel_aliases_v02631',array(__CLASS__,'aliases'));add_shortcode('sc_lab_persistent_queue',array(__CLASS__,'shortcode'));}
 public static function aliases($a){$a=is_array($a)?$a:array();foreach(array('persistent-queue','dispatch-queue','queue-infrastructure','dispatcher-queue') as $k){$a[$k]='persistent-queue';}return $a;}
 public static function shortcode(){return do_shortcode('[sc_lab_app module="persistent-queue"]');}
 public static function routes(){register_rest_route('sc-lab/v1','/dispatcher/v0311/health',array('methods'=>'GET','callback'=>array(__CLASS__,'health'),'permission_callback'=>'__return_true'));register_rest_route('sc-lab/v1','/dispatcher/v0311/schema',array('methods'=>'GET','callback'=>array(__CLASS__,'schema'),'permission_callback'=>'__return_true'));}
 private static function fs($r){$p=SC_LAB_DIR.$r;return array('exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null);}
 public static function schema(){return rest_ensure_response(array('ok'=>true,'version'=>self::VERSION,'queueSchema'=>'sc-lab-dispatch-queue-item/0.31.1','leaseSchema'=>'sc-lab-dispatch-lease/0.31.1','eventSchema'=>'sc-lab-dispatch-event/0.31.1','storage'=>'sqlite-wal','persistentWorkerRegistry'=>true,'atomicLeaseClaims'=>true,'restartRecovery'=>true));}
 public static function health(){$req=array('assets/js/modules/persistent-queue-v0311.js','assets/css/sc-lab-persistent-queue-v0311.css','contracts/persistent-queue-policy-v0311.json','contracts/dispatcher-queue-item-v0311.schema.json','contracts/dispatcher-lease-v0311.schema.json','contracts/dispatcher-event-v0311.schema.json','includes/class-sc-lab-persistent-queue-v0311.php');$files=array();$ok=true;foreach($req as $r){$files[$r]=self::fs($r);if(empty($files[$r]['exists'])){$ok=false;}}return rest_ensure_response(array('ok'=>$ok,'status'=>$ok?'ready':'incomplete','version'=>self::VERSION,'architecture'=>'persistent-distributed-queue-infrastructure','storage'=>'sqlite-wal','persistentWorkerRegistry'=>true,'persistentWorkloadQueue'=>true,'leaseRecovery'=>true,'files'=>$files,'time'=>gmdate('c')));}
}
