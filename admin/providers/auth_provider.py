import os
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette_admin.auth import AdminUser, AuthMiddleware, AuthProvider
from starlette_admin.base import BaseAdmin
from starlette.datastructures import URL
from dal.models.sales_users import SalesUser
from starlette.routing import Route
from starlette.middleware import Middleware


actions_for_roles = {
    'super-admin': ["super-admin", "admin", "commercial_loans", "commercial_loans_create", "commercial_loan_loc", "employers", "commercial_loan_kyc", "payouts_credentials"],
    'admin': ["admin", "employers", "commercial_loans", "commercial_loans_create", "commercial_loan_loc", "commercial_loan_kyc", "payouts_credentials"],
    'ops': ["commercial_loans", "commercial_loans_create", "ops-admin", "employers", "employees", "commercial_loan_kyc", "payouts_credentials"],
    "manager": ["employers"],
    'rm': ["employers", "employees"],
    'sm': ["employers", "employees"],
    "default": [],
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


class GoogleOAuthProvider(AuthProvider):

    async def render_login(self, request: Request, admin: "BaseAdmin") -> Response:
        redirect_uri = request.url_for('admin:auth')
        return await oauth.google.authorize_redirect(
            request,
            redirect_uri,
            state=request.query_params.get(
                "next", str(request.url_for('admin:index')))
        )

    async def is_authenticated(self, request) -> bool:
          if request.session.get("user", None) is not None:
            request.state.user = request.session.get("user")
            request.state.user["roles"] = actions_for_roles[
                request.state.user.get(
                    "sales_user_type", "default")]
             # request.state.user["roles"] = actions_for_roles[
            #     request.state.user.get(
            #         "sales_user_type", "default")]
            request.state.user["roles"] = actions_for_roles["super-admin"]
            return True
    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user  # Retrieve current user
        photo_url = None
        if user["picture"] is not None:
            photo_url = user["picture"]
        return AdminUser(username=user["name"], photo_url=photo_url)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        redirect_url = request.url_for("admin:prelogin")
        return RedirectResponse(url=redirect_url)

    async def handle_auth_callback(self, request: Request):
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')
        internal_redirect_uri = request.query_params["state"]
        if user:
            sales_user = SalesUser.find_one({"email": user['email']})
            if sales_user is not None:
                user["sales_id"] = str(sales_user["_id"])
                user["sales_user_type"] = sales_user["type"]
                user["roles"] = actions_for_roles[sales_user["type"]]
            else:
                user["sales_id"] = "aaaaaaaaaaaaaaaaaaaaaaaa"
                user["sales_user_type"] = "default"
                user["roles"] = actions_for_roles["default"]
            request.session.update({"user": user})
        return RedirectResponse(internal_redirect_uri)

    def setup_admin(self, admin: "BaseAdmin"):
        super().setup_admin(admin)
        """add custom authentication callback route"""
        admin.routes.append(
            Route(
                "/auth",
                self.handle_auth_callback,
                methods=["GET"],
                name="auth",
            )
        )

    def get_middleware(self, admin: "BaseAdmin") -> Middleware:
        return Middleware(
            AuthMiddleware, provider=self, allow_paths=["/auth"]
        )
