from __future__ import annotations

import argparse
from pathlib import Path

from .context import build_routing_context
from .schemas import TraceInput


PROJECT_DIR = Path(__file__).resolve().parents[2]


def _trace(path: str) -> TraceInput:
    return TraceInput.model_validate_json(Path(path).read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local PinchBench model router")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("context", "route", "execute"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--trace", required=True)
        command_parser.add_argument("--char-budget", type=int, default=2800)
        if command in {"route", "execute"}:
            command_parser.add_argument("--assets-dir", type=Path, default=PROJECT_DIR / "var" / "assets")
            command_parser.add_argument("--config", type=Path, default=PROJECT_DIR / "config" / "models.json")
    args = parser.parse_args()
    trace = _trace(args.trace)
    context = build_routing_context(trace, char_budget=args.char_budget)
    if args.command == "context":
        print(context.text)
        return
    # Keep `context` usable without importing the local ML runtime.
    from .engine import CheckpointRouter, execution_as_json, result_as_json

    router = CheckpointRouter(args.assets_dir, args.config)
    route_result = router.route(trace, context)
    if args.command == "route":
        print(result_as_json(route_result))
        return
    print(execution_as_json(route_result, router.execute_selected(route_result, trace)))
