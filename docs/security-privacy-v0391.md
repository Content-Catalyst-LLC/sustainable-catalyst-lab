# Security, Privacy, Secrets, and Audit Hardening v0.39.1

This module adds a fail-closed AES-256-GCM secret vault, versioned key rotation, one-time service credentials stored as scrypt hashes, signed tamper-evident audit chains, request nonce replay protection, recursive privacy scanning and deterministic redaction, and privacy-request operations. Secret values are never returned by list endpoints or written to audit detail. The vault remains locked until `SC_LAB_SECRET_MASTER_KEY` contains a 32-byte URL-safe base64 or 64-character hexadecimal key.
