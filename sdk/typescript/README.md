# Sustainable Catalyst Lab TypeScript SDK v0.39.1

A dependency-light client for typed handoffs, webhooks, embeds, and institutional governance.

```ts
import { LabClient } from "@sustainable-catalyst/lab-sdk";

const client = new LabClient("https://lab.example.org", "...", "principal-123");
console.log(await client.governancePolicies());
console.log(await client.listInstitutions());
```
