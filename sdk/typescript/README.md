# Sustainable Catalyst Lab TypeScript SDK v1.0.0

A dependency-light client for typed handoffs, webhooks, embeds, institutional governance, security operations, and multi-instance recovery.

```ts
import { LabClient } from "@sustainable-catalyst/lab-sdk";

const client = new LabClient("https://lab.example.org", "...", "principal-123");
console.log(await client.governancePolicies());
console.log(await client.listInstitutions());
console.log(await client.multiInstanceOperationsDashboard());
console.log(await client.listBackups());
```
