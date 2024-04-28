from typing import Any, Dict

from fastapi import Request


class PermissionsHandler:
    @staticmethod
    def is_admin_or_super_admin(user_roles: Dict[str, Any]) -> bool:
        return "admin" in user_roles or "super-admin" in user_roles

    @staticmethod
    def can_edit(user_roles: Dict[str, Any]) -> bool:
        return PermissionsHandler.is_admin_or_super_admin(user_roles)

    @staticmethod
    def can_access_view(request: Request, view_identity: str) -> bool:
        user_roles = request.state.user.get("roles", [])
        return PermissionsHandler.is_admin_or_super_admin(user_roles)
