from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TraceMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool", "developer"]
    content: str
    name: str | None = None


class ToolTrace(BaseModel):
    name: str
    description: str | None = None
    result_summary: str | None = None
    succeeded: bool | None = None


class TraceInput(BaseModel):
    messages: list[TraceMessage]
    tools: list[ToolTrace] = Field(default_factory=list)
    agent_state: dict[str, Any] = Field(default_factory=dict)
    actual_input_tokens: int | None = Field(default=None, ge=0)
    candidate_labels: list[str] | None = None
    preference: int = Field(default=2, ge=1, le=6)


class ModelConfig(BaseModel):
    label: str
    representation_name: str
    input_price_per_million: float = Field(ge=0)
    output_price_per_million: float = Field(ge=0)
    latency_seconds: float = Field(ge=0)
    execution_profile: str


class ExecutionProfile(BaseModel):
    endpoint: str
    api_key: str = ""
    model_name: str
    timeout_seconds: float = Field(default=120, gt=0)


class RouterConfig(BaseModel):
    default_candidates: list[str]
    models: list[ModelConfig]
    execution_profiles: dict[str, ExecutionProfile]
