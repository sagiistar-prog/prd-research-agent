"""Rebuild committed fictional PRDs from their explicit authored plans."""
import argparse
import json
from pathlib import Path

from plugin_run import run

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
for input_name, plan_name, output_name in [
    ("plugin-input.json", "team-pulse-plan.json", "team-pulse-prd.md"),
    ("fitcheck-input.json", "fitcheck-plan.json", "fitcheck-prd.md"),
]:
    data = json.loads((ROOT / "examples" / input_name).read_text(encoding="utf-8"))
    data["product_plan"] = json.loads((ROOT / "examples" / plan_name).read_text(encoding="utf-8"))
    text = run(data)["result"]["markdown"]
    destination = ROOT / "examples" / output_name
    if args.check:
        if not destination.exists() or destination.read_text(encoding="utf-8") != text:
            raise SystemExit("Example differs from the current renderer: " + output_name)
    else:
        destination.write_text(text, encoding="utf-8")
print("Fictional examples checked." if args.check else "Fictional examples rebuilt.")
