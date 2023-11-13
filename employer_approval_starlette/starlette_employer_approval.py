import os

from authlib.integrations.starlette_client import OAuth
from config import config
from providers.auth_provider import MyAuthProvider
from starlette.applications import Starlette
from starlette.config import Config
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette_admin.contrib.mongoengine import Admin

from dal.models.db_manager import DBManager
from employer_approval_starlette.views.employer_leads_view import \
    EmployerLeadsView

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
app = Starlette(
    routes=[
        Route("/{stage}/ops-service", lambda r: HTMLResponse(
            '<a href="/dev/ops-service/admin">Login to Employer Approval Portal</a>')),
        Mount("/static", app=StaticFiles(directory="static"), name="static"),
    ]
)


app.add_middleware(SessionMiddleware, secret_key=config.secret)


@app.on_event("startup")
def startup_db_client():
    stage = os.environ["STAGE"]
    DBManager.init(stage=stage, asset="employer-approval-service")


@app.on_event("shutdown")
def shutdown_db_client():
    DBManager.terminate()


"""Routes"""


@app.route('/{stage}/ops-service/auth', name="auth")
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
    base_url="/dev/ops-service/admin",
    logo_url="https://static.wixstatic.com/media/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png/v1/fill/w_400,h_80,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png",
    login_logo_url="https://static.wixstatic.com/media/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png/v1/fill/w_400,h_80,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png",
    auth_provider=MyAuthProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key=config.secret)],
)


"""Add Admin Views Here admin.add_view"""
admin.add_view(EmployerLeadsView)

"""Mount All The Views"""
admin.mount_to(app)


"""Run the Server"""
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
