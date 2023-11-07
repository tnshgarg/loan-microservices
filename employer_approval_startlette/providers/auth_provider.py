from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.base import BaseAdmin
from starlette.responses import  RedirectResponse

from starlette.config import Config
from authlib.integrations.starlette_client import OAuth

users = {
    "tanish@unipe.money": {
        "name": "Administrator",
        "avatar": "avatar.svg",
        "roles": ["read", "create", "edit", "delete", "action_make_published"],
        "password": "123456"
    },
    "subadmin": {
        "name": "John Doe",
        "avatar": "avatar.svg",
        "roles": ["read", "create", "edit", "action_make_published"],
        "password": "123456"
    },
    "viewer": {"name": "Viewer", "avatar": None, "roles": ["read"], "password": "123456"},
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
        redirect_uri = request.url_for('auth', stage="dev")
        return await oauth.google.authorize_redirect(request, redirect_uri, state=request.query_params["next"])
    
    async def is_authenticated(self, request) -> bool:
        if request.session.get("username", None) in users:
            request.state.user = users.get(request.session["username"])
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
   