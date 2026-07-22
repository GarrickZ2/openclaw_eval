from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class PinchCase:
    case_id: str
    prompt: str
    workspace_files: list[dict[str, str]]


def load_case(skill_dir: Path, case_id: str) -> PinchCase:
    path = skill_dir / "tasks" / f"{case_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"PinchBench case not found: {path}")
    _, frontmatter, body = path.read_text(encoding="utf-8").split("---", 2)
    metadata = yaml.safe_load(frontmatter)
    prompt = body.split("## Prompt", 1)[1].split("## Expected Behavior", 1)[0].strip()
    return PinchCase(metadata["id"], prompt, metadata.get("workspace_files", []))


def prepare_workspace(skill_dir: Path, case: PinchCase, workspace: Path) -> None:
    workspace.mkdir(parents=True, exist_ok=True)
    for spec in case.workspace_files:
        source = skill_dir / "assets" / spec["source"]
        destination = workspace / spec["dest"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
