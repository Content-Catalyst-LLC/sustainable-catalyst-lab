export class LabApiError extends Error {
    status;
    constructor(status, message) {
        super(message);
        this.status = status;
        this.name = "LabApiError";
    }
}
const segment = (value) => encodeURIComponent(String(value));
export class LabClient {
    baseUrl;
    apiKey;
    actorId;
    constructor(baseUrl, apiKey = "", actorId = "sdk-client") {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
        this.actorId = actorId;
        this.baseUrl = baseUrl.replace(/\/$/, "");
    }
    async request(method, path, payload) {
        const headers = { Accept: "application/json", "X-SC-Lab-Actor": this.actorId };
        if (this.apiKey) {
            headers["X-SC-Lab-API-Key"] = this.apiKey;
            headers["X-SC-Lab-Key"] = this.apiKey;
        }
        if (payload !== undefined)
            headers["Content-Type"] = "application/json";
        const response = await fetch(this.baseUrl + path, { method, headers, body: payload === undefined ? undefined : JSON.stringify(payload) });
        const body = await response.json().catch(() => ({ detail: response.statusText }));
        if (!response.ok)
            throw new LabApiError(response.status, body.detail ?? response.statusText);
        return body;
    }
    catalog() { return this.request("GET", "/v1/public-research-api"); }
    sdkManifest() { return this.request("GET", "/v1/research-integrations/sdk"); }
    integrationHealth() { return this.request("GET", "/v1/research-integrations/health"); }
    adapters() { return this.request("GET", "/v1/typed-cross-product-handoffs/adapters"); }
    planHandoff(workspaceId, payload) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/typed-research-handoffs/plan`, payload); }
    createHandoff(workspaceId, payload) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/typed-research-handoffs`, payload); }
    listWebhooks(workspaceId, status = "") { return this.request("GET", `/v1/team-workspaces/${segment(workspaceId)}/webhooks${status ? `?status=${segment(status)}` : ""}`); }
    registerWebhook(workspaceId, payload) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/webhooks`, payload); }
    updateWebhook(workspaceId, subscriptionId, payload) { return this.request("PATCH", `/v1/team-workspaces/${segment(workspaceId)}/webhooks/${segment(subscriptionId)}`, payload); }
    emitEvent(workspaceId, payload) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/webhook-events`, payload); }
    listDeliveries(workspaceId, status = "", limit = 200) {
        const params = new URLSearchParams({ limit: String(Math.max(1, Math.min(Math.trunc(limit), 2000))) });
        if (status)
            params.set("status", status);
        return this.request("GET", `/v1/team-workspaces/${segment(workspaceId)}/webhook-deliveries?${params.toString()}`);
    }
    dispatchWebhook(workspaceId, deliveryId) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/webhook-deliveries/${segment(deliveryId)}/dispatch`, {}); }
    createEmbed(workspaceId, payload) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/research-embeds`, payload); }
    readEmbed(token) { return this.request("GET", `/v1/public/research-embeds/${segment(token)}`); }
    governanceHealth() { return this.request("GET", "/v1/institutional-governance/health"); }
    governancePolicies() { return this.request("GET", "/v1/institutional-governance/policies"); }
    listInstitutions() { return this.request("GET", "/v1/institutions"); }
    createInstitution(payload) { return this.request("POST", "/v1/institutions", payload); }
    getInstitution(institutionId) { return this.request("GET", `/v1/institutions/${segment(institutionId)}`); }
    listUnits(institutionId) { return this.request("GET", `/v1/institutions/${segment(institutionId)}/units`); }
    createUnit(institutionId, payload) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/units`, payload); }
    listPrincipals(institutionId, status = "") { return this.request("GET", `/v1/institutions/${segment(institutionId)}/principals${status ? `?status=${segment(status)}` : ""}`); }
    createPrincipal(institutionId, payload) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/principals`, payload); }
    listRoleBindings(institutionId, principalId = "", workspaceId = "") {
        const params = new URLSearchParams();
        if (principalId)
            params.set("principalId", principalId);
        if (workspaceId)
            params.set("workspaceId", workspaceId);
        const query = params.toString();
        return this.request("GET", `/v1/institutions/${segment(institutionId)}/role-bindings${query ? `?${query}` : ""}`);
    }
    grantRole(institutionId, payload) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/role-bindings`, payload); }
    revokeRole(institutionId, bindingId) { return this.request("DELETE", `/v1/institutions/${segment(institutionId)}/role-bindings/${segment(bindingId)}`); }
    listRetentionPolicies(institutionId) { return this.request("GET", `/v1/institutions/${segment(institutionId)}/retention-policies`); }
    createRetentionPolicy(institutionId, payload) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/retention-policies`, payload); }
    getWorkspaceGovernance(workspaceId) { return this.request("GET", `/v1/team-workspaces/${segment(workspaceId)}/institutional-governance`); }
    configureWorkspaceGovernance(workspaceId, payload) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/institutional-governance`, payload); }
    evaluateGovernance(workspaceId, payload) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/institutional-governance/evaluate`, payload); }
    listGovernanceApprovals(workspaceId, status = "") { return this.request("GET", `/v1/team-workspaces/${segment(workspaceId)}/governance-approvals${status ? `?status=${segment(status)}` : ""}`); }
    createGovernanceApproval(workspaceId, payload) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/governance-approvals`, payload); }
    decideGovernanceApproval(workspaceId, requestId, payload) { return this.request("POST", `/v1/team-workspaces/${segment(workspaceId)}/governance-approvals/${segment(requestId)}/decisions`, payload); }
    governanceDashboard(institutionId) { return this.request("GET", `/v1/institutions/${segment(institutionId)}/governance-dashboard`); }
    governanceTimeline(institutionId, limit = 500) { return this.request("GET", `/v1/institutions/${segment(institutionId)}/governance-timeline?limit=${Math.max(1, Math.min(Math.trunc(limit), 5000))}`); }
    securityPrivacyHealth() { return this.request("GET", "/v1/security-privacy/health"); }
    securityPrivacyPolicies() { return this.request("GET", "/v1/security-privacy/policies"); }
    listSecrets(institutionId, name = "") { return this.request("GET", `/v1/institutions/${segment(institutionId)}/secrets${name ? `?name=${segment(name)}` : ""}`); }
    putSecret(institutionId, payload) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/secrets`, payload); }
    listServiceCredentials(institutionId, principalId = "") { return this.request("GET", `/v1/institutions/${segment(institutionId)}/service-credentials${principalId ? `?principalId=${segment(principalId)}` : ""}`); }
    issueServiceCredential(institutionId, principalId, payload) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/principals/${segment(principalId)}/service-credentials`, payload); }
    revokeServiceCredential(institutionId, credentialId) { return this.request("DELETE", `/v1/institutions/${segment(institutionId)}/service-credentials/${segment(credentialId)}`); }
    privacyScan(payload) { return this.request("POST", "/v1/security-privacy/privacy-scan", payload); }
    privacyRedact(payload) { return this.request("POST", "/v1/security-privacy/privacy-redact", payload); }
    listPrivacyRequests(institutionId, status = "") { return this.request("GET", `/v1/institutions/${segment(institutionId)}/privacy-requests${status ? `?status=${segment(status)}` : ""}`); }
    createPrivacyRequest(institutionId, payload) { return this.request("POST", `/v1/institutions/${segment(institutionId)}/privacy-requests`, payload); }
    verifySecurityAudit(institutionId) { return this.request("GET", `/v1/institutions/${segment(institutionId)}/security-audit/verify`); }
    multiInstanceOperationsHealth() { return this.request("GET", "/v1/multi-instance-operations/health"); }
    multiInstanceOperationsPolicies() { return this.request("GET", "/v1/multi-instance-operations/policies"); }
    instanceManifest() { return this.request("GET", "/v1/multi-instance-operations/instance"); }
    listInstances() { return this.request("GET", "/v1/multi-instance-operations/instances"); }
    registerInstance(payload) { return this.request("POST", "/v1/multi-instance-operations/instances", payload); }
    listBackups(limit = 200) { return this.request("GET", `/v1/multi-instance-operations/backups?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
    createBackup(payload) { return this.request("POST", "/v1/multi-instance-operations/backups", payload); }
    verifyBackup(backupId) { return this.request("POST", `/v1/multi-instance-operations/backups/${segment(backupId)}/verify`, {}); }
    stageRestore(backupId, payload) { return this.request("POST", `/v1/multi-instance-operations/backups/${segment(backupId)}/restore`, payload); }
    createMigrationPlan(payload) { return this.request("POST", "/v1/multi-instance-operations/migrations", payload); }
    executeMigration(migrationId, payload) { return this.request("POST", `/v1/multi-instance-operations/migrations/${segment(migrationId)}/execute`, payload); }
    createInstanceTransfer(payload) { return this.request("POST", "/v1/multi-instance-operations/transfers", payload); }
    verifyInstanceTransfer(transferId) { return this.request("POST", `/v1/multi-instance-operations/transfers/${segment(transferId)}/verify`, {}); }
    importInstanceTransfer(payload) { return this.request("POST", "/v1/multi-instance-operations/transfers/import", payload); }
    runRecoveryDrill(payload) { return this.request("POST", "/v1/multi-instance-operations/recovery-drills", payload); }
    multiInstanceOperationsDashboard() { return this.request("GET", "/v1/multi-instance-operations/dashboard"); }
    performanceValidationHealth() { return this.request("GET", "/v1/performance-validation/health"); }
    performanceValidationPolicies() { return this.request("GET", "/v1/performance-validation/policies"); }
    performanceValidationCatalog() { return this.request("GET", "/v1/performance-validation/catalog"); }
    listPerformanceRuns(kind = "", limit = 200) { const q = `?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}${kind ? `&kind=${segment(kind)}` : ""}`; return this.request("GET", `/v1/performance-validation/runs${q}`); }
    runLoadValidation(payload) { return this.request("POST", "/v1/performance-validation/load-runs", payload); }
    runChaosValidation(payload) { return this.request("POST", "/v1/performance-validation/chaos-runs", payload); }
    createCapacityReport(payload) { return this.request("POST", "/v1/performance-validation/capacity-reports", payload); }
    performanceValidationDashboard() { return this.request("GET", "/v1/performance-validation/dashboard"); }
    platformBetaHealth() { return this.request("GET", "/v1/platform-beta/health"); }
    platformBetaPolicies() { return this.request("GET", "/v1/platform-beta/policies"); }
    platformBetaCatalog() { return this.request("GET", "/v1/platform-beta/catalog"); }
    listBetaCohorts(limit = 200) { return this.request("GET", `/v1/platform-beta/cohorts?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
    createBetaCohort(payload) { return this.request("POST", "/v1/platform-beta/cohorts", payload); }
    listBetaOnboarding(limit = 200) { return this.request("GET", `/v1/platform-beta/onboarding?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
    startBetaOnboarding(payload) { return this.request("POST", "/v1/platform-beta/onboarding", payload); }
    advanceBetaOnboarding(onboardingId, payload) { return this.request("POST", `/v1/platform-beta/onboarding/${segment(onboardingId)}/advance`, payload); }
    listBetaProjectTemplates() { return this.request("GET", "/v1/platform-beta/project-templates"); }
    listBetaProjects(limit = 200) { return this.request("GET", `/v1/platform-beta/projects?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
    createBetaProject(payload) { return this.request("POST", "/v1/platform-beta/projects", payload); }
    advanceBetaProject(projectId, payload) { return this.request("POST", `/v1/platform-beta/projects/${segment(projectId)}/advance`, payload); }
    recordBetaTelemetry(payload) { return this.request("POST", "/v1/platform-beta/telemetry", payload); }
    betaTelemetrySummary() { return this.request("GET", "/v1/platform-beta/telemetry/summary"); }
    submitBetaFeedback(payload) { return this.request("POST", "/v1/platform-beta/feedback", payload); }
    listBetaFeedback(limit = 200) { return this.request("GET", `/v1/platform-beta/feedback?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
    createBetaLimitation(payload) { return this.request("POST", "/v1/platform-beta/limitations", payload); }
    listBetaLimitations(limit = 200) { return this.request("GET", `/v1/platform-beta/limitations?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
    createBetaSupportCase(payload) { return this.request("POST", "/v1/platform-beta/support-cases", payload); }
    listBetaSupportCases(limit = 200) { return this.request("GET", `/v1/platform-beta/support-cases?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
    evaluateBetaReadiness(payload) { return this.request("POST", "/v1/platform-beta/readiness-reports", payload); }
    platformBetaDashboard() { return this.request("GET", "/v1/platform-beta/dashboard"); }
    interfaceFinalizationHealth() { return this.request("GET", "/v1/interface-finalization/health"); }
    interfaceFinalizationPolicies() { return this.request("GET", "/v1/interface-finalization/policies"); }
    interfaceFinalizationCatalog() { return this.request("GET", "/v1/interface-finalization/catalog"); }
    createInterfaceAudit(payload) { return this.request("POST", "/v1/interface-finalization/audits", payload); }
    listInterfaceAudits(limit = 200) { return this.request("GET", `/v1/interface-finalization/audits?limit=${Math.max(1, Math.min(Math.trunc(limit), 2000))}`); }
    saveInterfacePreferences(profileId, payload) { return this.request("PUT", `/v1/interface-finalization/preferences/${segment(profileId)}`, payload); }
    createOfflineSnapshot(payload) { return this.request("POST", "/v1/interface-finalization/offline-snapshots", payload); }
    queueOfflineOperation(payload) { return this.request("POST", "/v1/interface-finalization/offline-operations", payload); }
    reconcileOfflineOperations(payload) { return this.request("POST", "/v1/interface-finalization/reconcile", payload); }
    interfaceFinalizationDashboard() { return this.request("GET", "/v1/interface-finalization/dashboard"); }
    publicReleaseHardeningHealth() { return this.request("GET", "/v1/public-release-hardening/health"); }
    publicReleaseHardeningCatalog() { return this.request("GET", "/v1/public-release-hardening/catalog"); }
    listPublicReleaseRecords(kind, limit = 200) { return this.request("GET", `/v1/public-release-hardening/records/${segment(kind)}?limit=${Math.max(1, Math.min(Math.trunc(limit), 5000))}`); }
    createCompatibilityMatrix(payload) { return this.request("POST", "/v1/public-release-hardening/compatibility-matrices", payload); }
    assessPublicReleaseMigration(payload) { return this.request("POST", "/v1/public-release-hardening/migration-assessments", payload); }
    registerDeprecation(payload) { return this.request("POST", "/v1/public-release-hardening/deprecations", payload); }
    createCleanInstallReport(payload) { return this.request("POST", "/v1/public-release-hardening/clean-install-reports", payload); }
    createRollbackPlan(payload) { return this.request("POST", "/v1/public-release-hardening/rollback-plans", payload); }
    evaluateReleaseCandidate(payload) { return this.request("POST", "/v1/public-release-hardening/release-candidates", payload); }
    publicReleaseHardeningDashboard() { return this.request("GET", "/v1/public-release-hardening/dashboard"); }
}
export async function verifyWebhook(secret, timestamp, body, signature) {
    const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
    const signed = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${timestamp}.${body}`));
    const expected = [...new Uint8Array(signed)].map(value => value.toString(16).padStart(2, "0")).join("");
    if (expected.length !== signature.length)
        return false;
    let mismatch = 0;
    for (let index = 0; index < expected.length; index += 1)
        mismatch |= expected.charCodeAt(index) ^ signature.charCodeAt(index);
    return mismatch === 0;
}
