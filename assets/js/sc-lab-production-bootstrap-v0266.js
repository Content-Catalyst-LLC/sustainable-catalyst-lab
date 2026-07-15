(function (W) {
  'use strict';
  if (W.__SCLabProductionBootstrapV0266) return;
  W.__SCLabProductionBootstrapV0266 = true;
  const C = W.SCLabProductionBootstrapConfigV0266 || {};
  const projectKey = String(C.projectKey || 'scLabProjectsV010');
  const activeKey = String(C.activeProjectKey || 'scLabActiveProjectV010');
  const quarantineKey = String(C.quarantineKey || 'scLabRecoveryQuarantineV0266');
  const state = {
    version: '0.26.6', safeMode: !!C.safeMode, recoveryMode: !!C.recoveryMode,
    storageAvailable: true, storageBytes: 0, storageState: 'unchecked', repaired: false,
    quarantinePresent: false, errors: []
  };
  const memory = new Map();
  function byteLength(value) { try { return new Blob([String(value || '')]).size; } catch (_) { return String(value || '').length * 2; } }
  function get(key) {
    if (state.safeMode) return memory.has(key) ? memory.get(key) : null;
    try { return W.localStorage.getItem(key); } catch (error) { state.storageAvailable = false; state.errors.push(String(error?.message || error)); return memory.has(key) ? memory.get(key) : null; }
  }
  function set(key, value) {
    const text = String(value);
    memory.set(key, text);
    if (state.safeMode) return true;
    try { W.localStorage.setItem(key, text); return true; } catch (error) { state.storageAvailable = false; state.errors.push(String(error?.message || error)); return false; }
  }
  function remove(key) {
    memory.delete(key);
    if (state.safeMode) return;
    try { W.localStorage.removeItem(key); } catch (_) {}
  }
  function quarantine(raw, reason) {
    const record = { version:'0.26.6', reason:String(reason || 'invalid_json'), quarantinedAt:new Date().toISOString(), bytes:byteLength(raw), raw:String(raw || '').slice(0, 2000000) };
    try { W.sessionStorage.setItem(quarantineKey, JSON.stringify(record)); state.quarantinePresent = true; } catch (_) {}
    remove(projectKey); remove(activeKey); state.repaired = true; state.storageState = 'repaired';
  }
  function validate() {
    if (state.safeMode) { state.storageState = 'safe_mode_memory_only'; return; }
    let raw = null;
    try { raw = W.localStorage.getItem(projectKey); } catch (error) { state.storageAvailable = false; state.storageState = 'unavailable'; state.errors.push(String(error?.message || error)); return; }
    if (!raw) { state.storageState = 'empty'; return; }
    state.storageBytes = byteLength(raw);
    if (state.storageBytes > Number(C.storageBudgetBytes || 4194304)) { quarantine(raw, 'storage_budget_exceeded'); return; }
    try {
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) throw new Error('Project storage root is not an array.');
      const ids = new Set();
      parsed.forEach((project, index) => {
        if (!project || typeof project !== 'object' || Array.isArray(project)) throw new Error(`Project ${index + 1} is invalid.`);
        if (project.id) ids.add(String(project.id));
      });
      const active = W.localStorage.getItem(activeKey);
      if (active && ids.size && !ids.has(String(active))) W.localStorage.removeItem(activeKey);
      state.storageState = 'valid';
    } catch (error) { state.errors.push(String(error?.message || error)); quarantine(raw, 'invalid_project_json'); }
  }
  validate();
  W.__SCLabSafeModeV0266 = state.safeMode;
  W.SCLabProductionStorageV0266 = {
    get, set, remove,
    status: () => Object.assign({}, state),
    exportQuarantine() { try { return JSON.parse(W.sessionStorage.getItem(quarantineKey) || 'null'); } catch (_) { return null; } },
    clearQuarantine() { try { W.sessionStorage.removeItem(quarantineKey); } catch (_) {} state.quarantinePresent = false; }
  };
})(window);
