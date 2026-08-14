from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from studio_api.rag.intents import EditIntent


class PMDPatchProposal(BaseModel):
    id: str
    modelId: str
    baseRevisionId: Optional[str] = None
    operations: List[Dict[str, Any]] = Field(min_length=1)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    status: Literal["proposed", "rejected", "accepted"] = "proposed"
    authorizationErrors: List[str] = Field(default_factory=list)


ALLOWED_BY_ROLE = {
    "viewer": set(),
    "engineer": {"setParameter"},
    "admin": {"setParameter", "addComponent", "removeComponent"},
}


def proposal_from_intent(intent: EditIntent, *, proposal_id: str, roles: List[str]) -> PMDPatchProposal:
    allowed_ops = set().union(*(ALLOWED_BY_ROLE.get(role, set()) for role in roles))
    errors: List[str] = []
    operations: List[Dict[str, Any]] = []
    for operation in intent.operations:
        if operation.op not in allowed_ops:
            errors.append(f"{operation.op} is not allowed for roles {','.join(roles) or 'none'}")
        operations.append({
            "op": operation.op,
            "path": operation.path,
            "value": operation.value,
            "reason": operation.reason,
        })
    return PMDPatchProposal(
        id=proposal_id,
        modelId=intent.modelId,
        baseRevisionId=intent.baseRevisionId,
        operations=operations,
        citations=intent.citations,
        authorizationErrors=errors,
    )


def proposal_to_patch(proposal: PMDPatchProposal, *, base_revision_token: str) -> Dict[str, Any]:
    if proposal.authorizationErrors:
        raise ValueError("Proposal is not authorized")
    if proposal.status != "accepted":
        raise ValueError("Proposal must be accepted before patch creation")
    return {
        "baseRevisionToken": base_revision_token,
        "operations": proposal.operations,
    }
