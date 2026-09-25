from backend.app import graph_studio_provenance_authority_v0135851 as m

def test_health():
    h=m.health(); assert h['ok'] and h['version']=='0.135.8.5.1' and h['api_route_count']==6
    assert h['legacy_interaction_enabled'] is False and h['legacy_observer_attached'] is False

def test_authority_contract():
    a=m.authority_contract(); assert a['sole_provenance_owner']=='graph-studio-native-provenance-v013585'
    assert a['legacy_v0135841_runtime_enqueued'] is False
    assert a['mutation_observer_interaction_owner'] is False

def test_browser_contract_requires_real_actions():
    b=m.browser_contract(); assert b['certifier']=='headless-chromium'; assert b['declared_contract_is_not_browser_proof'] is True
    assert 'node-selection' in b['required_actions'] and 'reload-restore' in b['required_actions']

def test_diagnostics():
    d=m.runtime_diagnostics(); assert d['measure_in_browser'] is True; assert d['expected']['legacy_observers']==0

def test_acceptance():
    a=m.acceptance_report(); assert a['single_provenance_owner'] and a['legacy_interaction_shutdown'] and a['real_browser_certification']

def test_deployment_gate():
    g=m.deployment_gate(); assert g['requires_native_v013585'] and g['requires_renderer31'] and g['requires_platform_core_v3']
