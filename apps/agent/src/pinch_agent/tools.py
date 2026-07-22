from __future__ import annotations

import json
from pathlib import Path
from typing import Any


TOOL_SPEC = [
    {"name": "list_files", "arguments": {"path": "relative path, default ."}},
    {"name": "read_file", "arguments": {"path": "relative file path", "start_line": "optional", "end_line": "optional"}},
    {"name": "write_file", "arguments": {"path": "relative file path", "content": "text"}},
]


class WorkspaceTools:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()

    def _path(self, value: str) -> Path:
        path = (self.workspace / value).resolve()
        if path != self.workspace and self.workspace not in path.parents:
            raise ValueError("path must remain inside the case workspace")
        return path

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        if name == "list_files":
            path = self._path(str(arguments.get("path", ".")))
            result = [str(item.relative_to(self.workspace)) for item in sorted(path.rglob("*")) if item.is_file()]
            return json.dumps(result[:200])
        if name == "read_file":
            path = self._path(str(arguments["path"]))
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            start = max(int(arguments.get("start_line", 1)), 1)
            end = min(int(arguments.get("end_line", start + 199)), len(lines))
            return "\n".join(lines[start - 1 : end])[:16_000]
        if name == "write_file":
            path = self._path(str(arguments["path"]))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(arguments["content"]), encoding="utf-8")
            return f"wrote {path.relative_to(self.workspace)}"
        raise ValueError(f"unsupported tool: {name}")
