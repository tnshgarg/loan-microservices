from providers.auth_provider import MyAuthProvider
from models.Starlette_Employers import StarletteEmployers
from mongoengine import connect

from starlette_admin.contrib.mongoengine import Admin

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware import Middleware
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.config import Config
from config import config
from authlib.integrations.starlette_client import OAuth
from views.employer_approval_view import EmployerApprovalView

from starlette.responses import RedirectResponse

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


"""Initialize DB"""
client = connect(
    host='mongodb+srv://aws_lambda_dev:15HYlXJ3wG0821WD@cluster1.sebmken.mongodb.net/dev?retryWrites=true&w=majority')

db = client['dev']


"""Main App"""
app = Starlette(
    routes=[
        Route("/{stage}/ops-service", lambda r: HTMLResponse(
            '<a href="/dev/ops-service/admin">Login to Employer Approval Portal</a>')),
        Mount("/static", app=StaticFiles(directory="static"), name="static"),
    ]
)

app.state.mongodb = client
app.state.mongodb_db = db
app.add_middleware(SessionMiddleware, secret_key=config.secret)

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
    route_name="admin-mongoengine",
    logo_url="https://static.wixstatic.com/media/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png/v1/fill/w_400,h_80,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png",
    login_logo_url="https://static.wixstatic.com/media/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png/v1/fill/w_400,h_80,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png",
    templates_dir="templates/admin/mongoengine",
    auth_provider=MyAuthProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key=config.secret)],
)


"""Employer Approval View"""
admin.add_view(EmployerApprovalView(StarletteEmployers,
               label="Employer Approval", icon="fa fa-users"))


"""Mount All The Views"""
admin.mount_to(app)


"""Run the Server"""
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
