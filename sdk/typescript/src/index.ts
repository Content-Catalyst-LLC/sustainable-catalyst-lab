export class LabApiError extends Error {
  constructor(public status: number, message: string) { super(message); this.name = "LabApiError"; }
}

const segment = (value: unknown) => encodeURIComponent(String(value));

export class LabClient {
  constructor(public baseUrl: string, public apiKey = "", public actorId = "sdk-client") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async request<T>(method: string, path: string, payload?: unknown): Promise<T> {
    const headers: Record<string, string> = { Accept: "application/json", "X-SC-Lab-Actor": this.actorId };
    if (this.apiKey) { headers["X-SC-Lab-API-Key"] = this.apiKey; headers["X-SC-Lab-Key"] = this.apiKey; }
    if (payload !== undefined) headers["Content-Type"] = "application/json";
    const response = await fetch(this.baseUrl + path, { method, headers, body: payload === undefined ? undefined : JSON.stringify(payload) });
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    if (!response.ok) throw new LabApiError(response.status, body.detail ?? response.statusText);
    return body as T;
  }

  catalog() { return this.request("GET", "/v1/public-research-api"); }
  sdkManifest() { return this.request("GET", "/v1/research-integrations/sdk"); }
  integrationHealth() { return this.request("GET", "/v1/research-integrations/health"); }
  adapters() { return this.request("GET", "/v1/typed-cross-product-handoffs/adapters"); }
  planHandoff(workspaceId: string, payload: unknown) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/typed-research-handoffs/plan`, payload); }
  createHandoff(workspaceId: string, payload: unknown) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/typed-research-handoffs`, payload); }
  listWebhooks(workspaceId: string, status = "") { return this.request("GET", `/v1/team-workspaces/${segment(workspaceId)}/webhooks${status ? `?status=${segment(status)}` : ""}`); }
  registerWebhook(workspaceId: string, payload: unknown) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/webhooks`, payload); }
  updateWebhook(workspaceId: string, subscriptionId: string, payload: unknown) { return this.request("PATCH", `/v1/team-workspaces/${segment(workspaceId)}/webhooks/${segment(subscriptionId)}`, payload); }
  emitEvent(workspaceId: string, payload: unknown) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/webhook-events`, payload); }
  listDeliveries(workspaceId: string, status = "", limit = 200) {
    const params = new URLSearchParams({ limit: String(Math.max(1, Math.min(Math.trunc(limit), 2000))) });
    if (status) params.set("status", status);
    return this.request("GET", `/v1/team-workspaces/${segment(workspaceId)}/webhook-deliveries?${params.toString()}`);
  }
  dispatchWebhook(workspaceId: string, deliveryId: string) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/webhook-deliveries/${segment(deliveryId)}/dispatch`, {}); }
  createEmbed(workspaceId: string, payload: unknown) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/research-embeds`, payload); }
  readEmbed(token: string) { return this.request("GET", `/v1/public/research-embeds/${segment(token)}`); }
  governanceHealth() { return this.request("GET", "/v1/institutional-governance/health"); }
  governancePolicies() { return this.request("GET", "/v1/institutional-governance/policies"); }
  listInstitutions() { return this.request("GET", "/v1/institutions"); }
  createInstitution(payload: unknown) { return this.request("POST", "/v1/institutions", payload); }
  getInstitution(institutionId: string) { return this.request("GET", `/v1/institutions/${segment(institutionId)}`); }
  listUnits(institutionId: string) { return this.request("GET", `/v1/institutions/${segment(institutionId)}/units`); }
  createUnit(institutionId: string, payload: unknown) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/units`, payload); }
  listPrincipals(institutionId: string, status = "") { return this.request("GET", `/v1/institutions/${segment(institutionId)}/principals${status ? `?status=${segment(status)}` : ""}`); }
  createPrincipal(institutionId: string, payload: unknown) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/principals`, payload); }
  listRoleBindings(institutionId: string, principalId = "", workspaceId = "") {
    const params = new URLSearchParams();
    if (principalId) params.set("principalId", principalId);
    if (workspaceId) params.set("workspaceId", workspaceId);
    const query = params.toString();
    return this.request("GET", `/v1/institutions/${segment(institutionId)}/role-bindings${query ? `?${query}` : ""}`);
  }
  grantRole(institutionId: string, payload: unknown) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/role-bindings`, payload); }
  revokeRole(institutionId: string, bindingId: string) { return this.request("DELETE", `/v1/institutions/${segment(institutionId)}/role-bindings/${segment(bindingId)}`); }
  listRetentionPolicies(institutionId: string) { return this.request("GET", `/v1/institutions/${segment(institutionId)}/retention-policies`); }
  createRetentionPolicy(institutionId: string, payload: unknown) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/retention-policies`, payload); }
  getWorkspaceGovernance(workspaceId: string) { return this.request("GET", `/v1/team-workspaces/${segment(workspaceId)}/institutional-governance`); }
  configureWorkspaceGovernance(workspaceId: string, payload: unknown) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/institutional-governance`, payload); }
  evaluateGovernance(workspaceId: string, payload: unknown) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/institutional-governance/evaluate`, payload); }
  listGovernanceApprovals(workspaceId: string, status = "") { return this.request("GET", `/v1/team-workspaces/${segment(workspaceId)}/governance-approvals${status ? `?status=${segment(status)}` : ""}`); }
  createGovernanceApproval(workspaceId: string, payload: unknown) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/governance-approvals`, payload); }
  decideGovernanceApproval(workspaceId: string, requestId: string, payload: unknown) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/governance-approvals/${segment(requestId)}/decisions`, payload); }
  governanceDashboard(institutionId: string) { return this.request("GET", `/v1/institutions/${segment(institutionId)}/governance-dashboard`); }
  governanceTimeline(institutionId: string, limit = 500) { return this.request("GET", `/v1/institutions/${segment(institutionId)}/governance-timeline?limit=${Math.max(1, Math.min(Math.trunc(limit), 5000))}`); }

  securityPrivacyHealth() { return this.request("GET", "/v1/security-privacy/health"); }
  securityPrivacyPolicies() { return this.request("GET", "/v1/security-privacy/policies"); }
  listSecrets(institutionId: string, name = "") { return this.request("GET", `/v1/institutions/${segment(institutionId)}/secrets${name ? `?name=${segment(name)}` : ""}`); }
  putSecret(institutionId: string, payload: unknown) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/secrets`, payload); }
  listServiceCredentials(institutionId: string, principalId = "") { return this.request("GET", `/v1/institutions/${segment(institutionId)}/service-credentials${principalId ? `?principalId=${segment(principalId)}` : ""}`); }
  issueServiceCredential(institutionId: string, principalId: string, payload: unknown) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/principals/${segment(principalId)}/service-credentials`, payload); }
  revokeServiceCredential(institutionId: string, credentialId: string) { return this.request("DELETE", `/v1/institutions/${segment(institutionId)}/service-credentials/${segment(credentialId)}`); }
  privacyScan(payload: unknown) { return this.request("POST", "/v1/security-privacy/privacy-scan", payload); }
  privacyRedact(payload: unknown) { return this.request("POST", "/v1/security-privacy/privacy-redact", payload); }
  listPrivacyRequests(institutionId: string, status = "") { return this.request("GET", `/v1/institutions/${segment(institutionId)}/privacy-requests${status ? `?status=${segment(status)}` : ""}`); }
  createPrivacyRequest(institutionId: string, payload: unknown) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/privacy-requests`, payload); }
  verifySecurityAudit(institutionId: string) { return this.request("GET", `/v1/institutions/${segment(institutionId)}/security-audit/verify`); }


  multiInstanceOperationsHealth() { return this.request("GET", "/v1/multi-instance-operations/health"); }
  multiInstanceOperationsPolicies() { return this.request("GET", "/v1/multi-instance-operations/policies"); }
  instanceManifest() { return this.request("GET", "/v1/multi-instance-operations/instance"); }
  listInstances() { return this.request("GET", "/v1/multi-instance-operations/instances"); }
  registerInstance(payload: unknown) { return this.request("POST", "/v1/multi-instance-operations/instances", payload); }
  listBackups(limit = 200) { return this.request("GET", `/v1/multi-instance-operations/backups?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
  createBackup(payload: unknown) { return this.request("POST", "/v1/multi-instance-operations/backups", payload); }
  verifyBackup(backupId: string) { return this.request("POST", `/v1/multi-instance-operations/backups/${segment(backupId)}/verify`, {}); }
  stageRestore(backupId: string, payload: unknown) { return this.request("POST", `/v1/multi-instance-operations/backups/${segment(backupId)}/restore`, payload); }
  createMigrationPlan(payload: unknown) { return this.request("POST", "/v1/multi-instance-operations/migrations", payload); }
  executeMigration(migrationId: string, payload: unknown) { return this.request("POST", `/v1/multi-instance-operations/migrations/${segment(migrationId)}/execute`, payload); }
  createInstanceTransfer(payload: unknown) { return this.request("POST", "/v1/multi-instance-operations/transfers", payload); }
  verifyInstanceTransfer(transferId: string) { return this.request("POST", `/v1/multi-instance-operations/transfers/${segment(transferId)}/verify`, {}); }
  importInstanceTransfer(payload: unknown) { return this.request("POST", "/v1/multi-instance-operations/transfers/import", payload); }
  runRecoveryDrill(payload: unknown) { return this.request("POST", "/v1/multi-instance-operations/recovery-drills", payload); }
  multiInstanceOperationsDashboard() { return this.request("GET", "/v1/multi-instance-operations/dashboard"); }

  performanceValidationHealth() { return this.request("GET", "/v1/performance-validation/health"); }
  performanceValidationPolicies() { return this.request("GET", "/v1/performance-validation/policies"); }
  performanceValidationCatalog() { return this.request("GET", "/v1/performance-validation/catalog"); }
  listPerformanceRuns(kind = "", limit = 200) { const q = `?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}${kind ? `&kind=${segment(kind)}` : ""}`; return this.request("GET", `/v1/performance-validation/runs${q}`); }
  runLoadValidation(payload: unknown) { return this.request("POST", "/v1/performance-validation/load-runs", payload); }
  runChaosValidation(payload: unknown) { return this.request("POST", "/v1/performance-validation/chaos-runs", payload); }
  createCapacityReport(payload: unknown) { return this.request("POST", "/v1/performance-validation/capacity-reports", payload); }
  performanceValidationDashboard() { return this.request("GET", "/v1/performance-validation/dashboard"); }


  platformBetaHealth() { return this.request("GET", "/v1/platform-beta/health"); }
  platformBetaPolicies() { return this.request("GET", "/v1/platform-beta/policies"); }
  platformBetaCatalog() { return this.request("GET", "/v1/platform-beta/catalog"); }
  listBetaCohorts(limit = 200) { return this.request("GET", `/v1/platform-beta/cohorts?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
  createBetaCohort(payload: unknown) { return this.request("POST", "/v1/platform-beta/cohorts", payload); }
  listBetaOnboarding(limit = 200) { return this.request("GET", `/v1/platform-beta/onboarding?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
  startBetaOnboarding(payload: unknown) { return this.request("POST", "/v1/platform-beta/onboarding", payload); }
  advanceBetaOnboarding(onboardingId: string, payload: unknown) { return this.request("POST", `/v1/platform-beta/onboarding/${segment(onboardingId)}/advance`, payload); }
  listBetaProjectTemplates() { return this.request("GET", "/v1/platform-beta/project-templates"); }
  listBetaProjects(limit = 200) { return this.request("GET", `/v1/platform-beta/projects?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
  createBetaProject(payload: unknown) { return this.request("POST", "/v1/platform-beta/projects", payload); }
  advanceBetaProject(projectId: string, payload: unknown) { return this.request("POST", `/v1/platform-beta/projects/${segment(projectId)}/advance`, payload); }
  recordBetaTelemetry(payload: unknown) { return this.request("POST", "/v1/platform-beta/telemetry", payload); }
  betaTelemetrySummary() { return this.request("GET", "/v1/platform-beta/telemetry/summary"); }
  submitBetaFeedback(payload: unknown) { return this.request("POST", "/v1/platform-beta/feedback", payload); }
  listBetaFeedback(limit = 200) { return this.request("GET", `/v1/platform-beta/feedback?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
  createBetaLimitation(payload: unknown) { return this.request("POST", "/v1/platform-beta/limitations", payload); }
  listBetaLimitations(limit = 200) { return this.request("GET", `/v1/platform-beta/limitations?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
  createBetaSupportCase(payload: unknown) { return this.request("POST", "/v1/platform-beta/support-cases", payload); }
  listBetaSupportCases(limit = 200) { return this.request("GET", `/v1/platform-beta/support-cases?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
  evaluateBetaReadiness(payload: unknown) { return this.request("POST", "/v1/platform-beta/readiness-reports", payload); }
  platformBetaDashboard() { return this.request("GET", "/v1/platform-beta/dashboard"); }

  interfaceFinalizationHealth() { return this.request("GET", "/v1/interface-finalization/health"); }
  interfaceFinalizationPolicies() { return this.request("GET", "/v1/interface-finalization/policies"); }
  interfaceFinalizationCatalog() { return this.request("GET", "/v1/interface-finalization/catalog"); }
  createInterfaceAudit(payload: unknown) { return this.request("POST", "/v1/interface-finalization/audits", payload); }
  listInterfaceAudits(limit = 200) { return this.request("GET", `/v1/interface-finalization/audits?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
  saveInterfacePreferences(profileId: string, payload: unknown) { return this.request("PUT", `/v1/interface-finalization/preferences/${segment(profileId)}`, payload); }
  createOfflineSnapshot(payload: unknown) { return this.request("POST", "/v1/interface-finalization/offline-snapshots", payload); }
  queueOfflineOperation(payload: unknown) { return this.request("POST", "/v1/interface-finalization/offline-operations", payload); }
  reconcileOfflineOperations(payload: unknown) { return this.request("POST", "/v1/interface-finalization/reconcile", payload); }
  interfaceFinalizationDashboard() { return this.request("GET", "/v1/interface-finalization/dashboard"); }
  publicReleaseHardeningHealth() { return this.request("GET", "/v1/public-release-hardening/health"); }
  publicReleaseHardeningCatalog() { return this.request("GET", "/v1/public-release-hardening/catalog"); }
  listPublicReleaseRecords(kind: string, limit = 200) { return this.request("GET", `/v1/public-release-hardening/records/${segment(kind)}?limit=${Math.max(1, Math.min(Math.trunc(limit), 5000))}`); }
  createCompatibilityMatrix(payload: unknown) { return this.request("POST", "/v1/public-release-hardening/compatibility-matrices", payload); }
  assessPublicReleaseMigration(payload: unknown) { return this.request("POST", "/v1/public-release-hardening/migration-assessments", payload); }
  registerDeprecation(payload: unknown) { return this.request("POST", "/v1/public-release-hardening/deprecations", payload); }
  createCleanInstallReport(payload: unknown) { return this.request("POST", "/v1/public-release-hardening/clean-install-reports", payload); }
  createRollbackPlan(payload: unknown) { return this.request("POST", "/v1/public-release-hardening/rollback-plans", payload); }
  evaluateReleaseCandidate(payload: unknown) { return this.request("POST", "/v1/public-release-hardening/release-candidates", payload); }
  publicReleaseHardeningDashboard() { return this.request("GET", "/v1/public-release-hardening/dashboard"); }

}

export async function verifyWebhook(secret: string, timestamp: string, body: string, signature: string): Promise<boolean> {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const signed = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${timestamp}.${body}`));
  const expected = [...new Uint8Array(signed)].map(value => value.toString(16).padStart(2, "0")).join("");
  if (expected.length !== signature.length) return false;
  let mismatch = 0;
  for (let index = 0; index < expected.length; index += 1) mismatch |= expected.charCodeAt(index) ^ signature.charCodeAt(index);
  return mismatch === 0;

}
