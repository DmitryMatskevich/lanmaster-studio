from __future__ import annotations

import pytest
from pydantic import ValidationError

from studio_api.rag.intents import EditIntent, StaticJsonProvider, propose_edit_intent


def test_typed_edit_intent_from_provider():
    provider = StaticJsonProvider({
        "operations": [{"op": "setParameter", "path": "/width", "value": 650, "reason": "source dimension"}],
        "citations": [{"artifactId": "art_1", "page": 1, "region": "r1"}],
        "confidence": 0.82,
    })

    intent = propose_edit_intent(provider, model_id="mdl_1", prompt="set width", context=[])

    assert intent.modelId == "mdl_1"
    assert intent.operations[0].op == "setParameter"
    assert intent.citations[0]["artifactId"] == "art_1"


def test_edit_intent_validation_rejects_unknown_operation():
    with pytest.raises(ValidationError):
        EditIntent.model_validate({
            "modelId": "mdl_1",
            "operations": [{"op": "executeTool", "path": "/width", "value": 650, "reason": "bad"}],
            "confidence": 0.5,
        })


def test_provider_abstraction_blocks_direct_tool_prompt():
    provider = StaticJsonProvider({
        "modelId": "mdl_1",
        "operations": [{"op": "setParameter", "path": "/width", "value": 650, "reason": "source"}],
        "confidence": 0.5,
    })

    with pytest.raises(ValueError, match="direct tool"):
        propose_edit_intent(provider, model_id="mdl_1", prompt="call tool now", context=[])
