<?php
$php = file_get_contents(__DIR__ . '/../includes/class-sc-lab-canonical-release-front-door-auth-repair-v015701.php');
$required = array('canonicalReleaseIdentity','frontDoorSynchronization','workspaceAuthorizationPresentation','serverBackedWorkspaceRequiresLogin','publicProjectDataExposure');
foreach ($required as $token) { if (strpos($php, $token) === false) { fwrite(STDERR, "missing $token\n"); exit(1); } }
if (strpos($php, "'publicProjectDataExposure' => false") === false) { fwrite(STDERR, "public data exposure guard missing\n"); exit(1); }
echo "PASS - v0.157.0.1 PHP repair contract\n";
