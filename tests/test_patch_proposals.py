from __future__ import annotations

import pytest

from studio_api.rag.intents import EditIntent
from studio_api.rag.proposals import proposal_from_intent, proposal_to_patch


def _intent(op: str = "setParameter") -> EditIntent:
    return EditIntent.model_validate({
        "modelId": "mdl_1",
        "baseRevisionId": "rev_1",
        "operations": [{"op": op, "path": "/width", "value": 650, "reason": "source"}],
        "citations": [{"artifactId": "art_1", "page": 1}],
        "confidence": 0.8,
    })


def test_patch_proposal_validates_engineer_authorization():
    proposal = proposal_from_intent(_intent(), proposal_id="pp_1", roles=["engineer"])

    assert proposal.status == "proposed"
    assert proposal.authorizationErrors == []
    assert proposal.operations[0]["op"] == "setParameter"


def test_patch_proposal_rejects_unauthorized_component_change():
    proposal = proposal_from_intent(_intent("removeComponent"), proposal_id="pp_2", roles=["engineer"])

    assert proposal.authorizationErrors
    assert "removeComponent" in proposal.authorizationErrors[0]


def test_proposal_does_not_create_patch_until_accepted():
    proposal = proposal_from_intent(_intent(), proposal_id="pp_3", roles=["engineer"])

    with pytest.raises(ValueError, match="accepted"):
        proposal_to_patch(proposal, base_revision_token="tok_1")

    accepted = proposal.model_copy(update={"status": "accepted"})
    patch = proposal_to_patch(accepted, base_revision_token="tok_1")

    assert patch["baseRevisionToken"] == "tok_1"
    assert patch["operations"][0]["path"] == "/width"
