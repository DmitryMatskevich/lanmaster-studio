from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Protocol

from pydantic import BaseModel, Field


class EditOperation(BaseModel):
    op: Literal["setParameter", "addComponent", "removeComponent"]
    path: str = Field(min_length=1)
    value: Any = None
    reason: str = Field(min_length=1)


class EditIntent(BaseModel):
    modelId: str = Field(min_length=1)
    baseRevisionId: Optional[str] = None
    operations: List[EditOperation] = Field(min_length=1)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    missingInformation: List[str] = Field(default_factory=list)


class LlmProvider(Protocol):
    def complete_json(self, *, system: str, user: str, schema_name: str) -> Dict[str, Any]:
        ...


class StaticJsonProvider:
    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload

    def complete_json(self, *, system: str, user: str, schema_name: str) -> Dict[str, Any]:
        if "tool" in user.lower():
            raise ValueError("Provider prompt must not request direct tool execution")
        return self.payload


def propose_edit_intent(provider: LlmProvider, *, model_id: str, prompt: str, context: List[Dict[str, Any]]) -> EditIntent:
    payload = provider.complete_json(
        system=(
            "Return only a typed EditIntent JSON object. Do not call tools. "
            "If sources are insufficient, fill missingInformation."
        ),
        user=f"modelId={model_id}\ncontext={context}\nrequest={prompt}",
        schema_name="EditIntent",
    )
    payload.setdefault("modelId", model_id)
    return EditIntent.model_validate(payload)
