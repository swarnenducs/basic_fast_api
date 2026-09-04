"""Build Azure App Service appsettings JSON from the project .env file."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
OUTPUT_PATH = Path(__file__).resolve().parent / "appsettings.json"

AZURE_RUNTIME_SETTINGS = [
    {"name": "WEBSITES_PORT", "value": "8000", "slotSetting": False},
    {"name": "SCM_DO_BUILD_DURING_DEPLOYMENT", "value": "true", "slotSetting": False},
    {"name": "WEBSITE_HTTPLOGGING_RETENTION_DAYS", "value": "3", "slotSetting": False},
]


def parse_env(path: Path) -> list[dict]:
    settings: list[dict] = []
    seen: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if not name or name in seen:
            continue
        seen.add(name)
        settings.append({"name": name, "value": value.strip(), "slotSetting": False})
    return settings


def main() -> None:
    app_settings = parse_env(ENV_PATH)
    existing = {item["name"] for item in app_settings}
    for extra in AZURE_RUNTIME_SETTINGS:
        if extra["name"] not in existing:
            app_settings.append(extra)
    OUTPUT_PATH.write_text(json.dumps(app_settings, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({len(app_settings)} settings)")


if __name__ == "__main__":
    main()
