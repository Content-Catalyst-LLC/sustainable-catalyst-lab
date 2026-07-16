from __future__ import annotations

import argparse
import json
import sys

from .config import AgentConfig
from .runtime import WorkerAgent


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Sustainable Catalyst Lab secure pull-based worker agent")
    p.add_argument("--coordinator", dest="coordinator_url")
    p.add_argument("--worker-id")
    p.add_argument("--name")
    p.add_argument("--worker-type")
    p.add_argument("--once", action="store_true")
    p.add_argument("--allow-insecure-contracts", action="store_true")
    p.add_argument("--validate-config", action="store_true")
    p.add_argument("--print-capabilities", action="store_true")
    p.add_argument("--rotate-credential", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    overrides = {key: value for key, value in vars(args).items() if key in {"coordinator_url", "worker_id", "name", "worker_type"} and value}
    if args.once:
        overrides["once"] = True
    if args.allow_insecure_contracts:
        overrides["allow_insecure_contracts"] = True
    try:
        config = AgentConfig.from_env(**overrides)
    except ValueError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    if args.validate_config:
        print(json.dumps({"ok": True, "workerId": config.worker_id, "coordinator": config.coordinator_url, "methodCount": len(config.methods), "contractVerification": bool(config.contract_secret)}, indent=2))
        return 0
    if args.print_capabilities:
        print(json.dumps(config.worker_payload(), indent=2))
        return 0
    agent = WorkerAgent(config)
    if args.rotate_credential:
        print(json.dumps(agent.client.rotate_credential(), indent=2))
        return 0
    agent.run_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
