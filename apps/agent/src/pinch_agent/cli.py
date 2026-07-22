from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from pinch_router.engine import CheckpointRouter

from .agent import RoutedAgent
from .cases import load_case, prepare_workspace


ROOT = Path(__file__).resolve().parents[4]


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--case", required=True)
    run.add_argument("--max-steps", type=int, default=8)
    args = parser.parse_args()
    skill_dir = ROOT / "pinchbench-skill"
    case = load_case(skill_dir, args.case)
    run_dir = ROOT / "apps" / "agent" / "var" / "runs" / datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace = run_dir / "workspace"
    prepare_workspace(skill_dir, case, workspace)
    router = CheckpointRouter(ROOT / "apps" / "router" / "var" / "assets", ROOT / "apps" / "router" / "config" / "models.json")
    result = RoutedAgent(router, workspace, args.max_steps).run(case.prompt)
    for event in result["events"]:
        print(json.dumps(event, ensure_ascii=False))
    print(json.dumps({"event": "run_completed", "case_id": case.case_id, "workspace": str(workspace), "answer": result["answer"]}, ensure_ascii=False))
