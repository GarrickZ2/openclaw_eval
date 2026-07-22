from pinch_router.context import build_routing_context
from pinch_router.schemas import TraceInput


def test_context_keeps_current_task_and_excludes_large_tool_payload() -> None:
    trace = TraceInput.model_validate(
        {
            "messages": [
                {"role": "system", "content": "system instructions"},
                {"role": "user", "content": "old request"},
                {"role": "assistant", "content": "old response"},
                {"role": "user", "content": "current task"},
            ],
            "tools": [{"name": "search", "result_summary": "x" * 2_000}],
        }
    )
    context = build_routing_context(trace, char_budget=900)
    assert "current task" in context.text
    assert len(context.text) <= 900
    assert context.was_truncated
