from __future__ import annotations

from dataclasses import dataclass

from .schemas import TraceInput


@dataclass(frozen=True)
class RoutingContext:
    text: str
    was_truncated: bool


def _clip(value: str, limit: int) -> tuple[str, bool]:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized, False
    return f"{normalized[:limit].rstrip()} …[truncated]", True


def build_routing_context(trace: TraceInput, *, char_budget: int = 2800) -> RoutingContext:
    """Create a stable, bounded view for semantic routing, not model execution."""
    sections: list[str] = []
    truncated = False
    systems = [message.content for message in trace.messages if message.role in {"system", "developer"}]
    users = [message.content for message in trace.messages if message.role == "user"]
    history = [message for message in trace.messages if message.role not in {"system", "developer"}]

    if systems:
        text, was_clipped = _clip("\n".join(systems[-2:]), 500)
        sections.append(f"[system]\n{text}")
        truncated |= was_clipped
    if users:
        text, was_clipped = _clip(users[-1], 1000)
        sections.append(f"[current_user_task]\n{text}")
        truncated |= was_clipped

    recent_history = history[-4:-1] if len(history) > 1 else []
    if recent_history:
        entries = []
        for message in recent_history:
            text, was_clipped = _clip(message.content, 260)
            entries.append(f"{message.role}: {text}")
            truncated |= was_clipped
        sections.append("[recent_history]\n" + "\n".join(entries))

    if trace.tools:
        entries = []
        for tool in trace.tools[:8]:
            detail = tool.result_summary or tool.description or "available"
            text, was_clipped = _clip(detail, 220)
            entries.append(f"{tool.name} ({'ok' if tool.succeeded else 'unknown'}): {text}")
            truncated |= was_clipped
        sections.append("[tools]\n" + "\n".join(entries))

    if trace.agent_state:
        state = ", ".join(f"{key}={value}" for key, value in sorted(trace.agent_state.items()))
        text, was_clipped = _clip(state, 300)
        sections.append(f"[agent_state]\n{text}")
        truncated |= was_clipped

    text, was_clipped = _clip("\n\n".join(sections) or "[empty_trace]", char_budget)
    return RoutingContext(text=text, was_truncated=truncated or was_clipped)
