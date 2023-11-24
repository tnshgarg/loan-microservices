from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.base import BaseAdmin

from dal.models.sales_users import SalesUser

users = {
    "tanish@unipe.money": {
        "name": "Administrator",
        "avatar": "avatar.svg",
        "roles": ["read", "create", "edit", "delete", "view"],
    },
    "admin": {
        "name": "John Doe",
        "avatar": "avatar.svg",
        "roles": ["read", "create", "edit", "update_details", "approve_employer", "delete", "view"],
    },
    "viewer": {"name": "Viewer", "avatar": None, "roles": ["read"]},

}

actions_for_roles = {
    'admin': ["view", "edit", "upload_details", "approve_employer", "delete"],
    'rm': ["view", "edit", "upload_details"],
    'sm': ["view"],
}

googleConfig = Config('.env')
oauth = OAuth(googleConfig)
CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account',  # force to select account
    }
)


class MyAuthProvider(AuthProvider):

    async def render_login(self, request: Request, admin: "BaseAdmin") -> Response:
        redirect_uri = request.url_for('auth')
        return await oauth.google.authorize_redirect(request, redirect_uri, state=request.query_params["next"])

    async def is_authenticated(self, request) -> bool:
        username = request.session.get("username", None)
        if username:
            user = SalesUser.find_one({"email": str(username)})
            if user:
                user_data = {
                    "sales_id": user["_id"],
                    "name": username,
                    "roles": user["type"],
                    "avatar": None,
                }
                request.state.user = user_data
                return True

        return False

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user  # Retrieve current user

        photo_url = None
        if user["avatar"] is not None:
            photo_url = request.url_for("static", path=user["avatar"])
        return AdminUser(username=user["name"], photo_url=photo_url)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return RedirectResponse(url='/{stage}/ops-service')
