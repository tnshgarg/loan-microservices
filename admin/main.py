import os

from authlib.integrations.starlette_client import OAuth
from admin.config import config
from admin.models.employers import StarletteEmployers
from admin.providers.auth_provider import MyAuthProvider
from starlette.applications import Starlette
from starlette.config import Config
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette_admin.contrib.mongoengine import Admin
from admin.views.commercial_loans_view import CommercialLoansView
from admin.views.employer_approval_view import EmployerApprovalView
from admin.views.promoters_view import PromotersView
from admin.views.repayment_reconcilation_view import RepaymentReconcilation

from dal.models.db_manager import DBManager
from admin.views.employer_leads_view import \
    EmployerLeadsView
from admin.config import config

"""Initialize Middlewares"""
middleware = [
    Middleware(SessionMiddleware)
]

"""Authorization"""
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


"""Main App"""
admin_app = Starlette(
    routes=[
        Route("/", lambda r: HTMLResponse(
            '<a href="/dev/ops-admin/admin">Login to Employer Approval Portal</a>')),
        Mount("/static", app=StaticFiles(directory="admin/static"), name="static"),
    ]
)


admin_app.add_middleware(SessionMiddleware, secret_key=config.secret)


@admin_app.on_event("startup")
def startup_db_client():
    stage = os.environ["STAGE"]
    DBManager.init(stage=stage, asset="employer-approval-service")


@admin_app.on_event("shutdown")
def shutdown_db_client():
    DBManager.terminate()


"""Routes"""


@admin_app.route('/auth', name="auth")
async def auth(request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get('userinfo')
    internal_redirect_uri = request.query_params["state"]

    if user:
        # request.session['user'] = user
        request.session['username'] = user["email"]
    return RedirectResponse(url=internal_redirect_uri)


"""Initialize Admin Dashboard App"""
admin = Admin(
    "Unipe Employer Dashboard",
    base_url="/admin",
    logo_url="https://static.wixstatic.com/media/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png/v1/fill/w_400,h_80,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png",
    login_logo_url="https://static.wixstatic.com/media/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png/v1/fill/w_400,h_80,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png",
    auth_provider=MyAuthProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key=config.secret)],
)


"""Add Admin Views Here admin.add_view"""
admin.add_view(EmployerApprovalView)
admin.add_view(EmployerLeadsView)
admin.add_view(CommercialLoansView)
admin.add_view(PromotersView)
admin.add_view(RepaymentReconcilation)


"""Mount All The Views"""
admin.mount_to(admin_app)


"""Run the Server"""
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(admin_app, host="127.0.0.1", port=8000)
