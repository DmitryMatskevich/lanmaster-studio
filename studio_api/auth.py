from __future__ import annotations

from enum import Enum
from typing import Callable, Iterable, Optional

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from .config import get_settings


class Role(str, Enum):
    VIEWER = "viewer"
    ENGINEER = "engineer"
    ADMIN = "admin"


ROLE_ORDER = {
    Role.VIEWER: 10,
    Role.ENGINEER: 20,
    Role.ADMIN: 30,
}


class UserContext(BaseModel):
    subject: str = Field(min_length=1)
    displayName: str
    roles: list[Role]
    authMode: str

    def has_any(self, allowed: Iterable[Role]) -> bool:
        allowed_set = set(allowed)
        return any(role in allowed_set for role in self.roles)


def _parse_roles(raw: Optional[str]) -> list[Role]:
    if not raw:
        return [Role.VIEWER]
    roles: list[Role] = []
    for item in raw.split(","):
        name = item.strip().lower()
        if not name:
            continue
        try:
            roles.append(Role(name))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown role: {name}",
            ) from exc
    return roles or [Role.VIEWER]


def current_user(
    x_dev_user: Optional[str] = Header(default=None, alias="X-Dev-User"),
    x_dev_roles: Optional[str] = Header(default=None, alias="X-Dev-Roles"),
) -> UserContext:
    settings = get_settings()
    if settings.auth_mode == "dev":
        subject = x_dev_user or "dev-user"
        roles = _parse_roles(x_dev_roles)
        return UserContext(
            subject=subject,
            displayName=subject,
            roles=roles,
            authMode="dev",
        )

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OIDC authentication is not configured for this environment",
    )


def require_roles(*allowed: Role) -> Callable[[UserContext], UserContext]:
    def dependency(user: UserContext = Depends(current_user)) -> UserContext:
        if not user.has_any(allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role for this operation",
            )
        return user

    return dependency
