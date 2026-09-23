#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import sys


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    repo = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    main_file = repo / "sustainable-catalyst-lab.php"
    compat_php = repo / "includes" / "class-sc-lab-legacy-compat-v0262.php"
    compat_js = repo / "assets" / "js" / "lab-legacy-compat-v0262.js"
    compat_css = repo / "assets" / "css" / "lab-legacy-compat-v0262.css"

    for path in (main_file, compat_php, compat_js, compat_css):
        require(path.is_file(), f"missing {path.relative_to(repo)}")

    main_text = main_file.read_text(encoding="utf-8", errors="replace")
    php_text = compat_php.read_text(encoding="utf-8")
    js_text = compat_js.read_text(encoding="utf-8")

    require(re.search(r"Version:\s*0\.26\.2\b", main_text) is not None, "plugin header is not v0.26.2")
    require("class-sc-lab-legacy-compat-v0262.php" in main_text, "main plugin does not load compatibility layer")
    require("sc_lab_legacy" in php_text, "legacy rendering flag is missing")
    require("sc_lab_isolated" in php_text, "isolated lifecycle escape hatch is missing")
    require("marine-biology" in php_text and "space-telescopes" in php_text, "legacy module aliases are incomplete")
    require("SCLabCompatibilityV0262" in js_text, "browser diagnostics API is missing")
    require("window.location.assign" in js_text, "server-rendered fallback reload is missing")
    require("sc-lab:module-ready" in js_text, "module-ready compatibility event is missing")
    require("Laboratory compatibility warning" in js_text, "visible runtime error boundary is missing")

    forbidden = [
        r"BEGIN (RSA|OPENSSH|EC) PRIVATE KEY",
        r"ghp_[A-Za-z0-9]{30,}",
        r"sk-[A-Za-z0-9]{20,}",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in (main_file, compat_php, compat_js, compat_css))
    for pattern in forbidden:
        require(re.search(pattern, combined) is None, f"potential secret matched {pattern}")

    print("PASS: Sustainable Catalyst Lab v0.26.2 compatibility release markers validated.")


if __name__ == "__main__":
    main()
