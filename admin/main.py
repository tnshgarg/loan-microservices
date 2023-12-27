import os

from authlib.integrations.starlette_client import OAuth
from starlette_admin import CustomView, DropDown
from admin.config import config
from admin.providers.auth_provider import GoogleOAuthProvider
from starlette.applications import Starlette
from starlette.config import Config
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette_admin.contrib.mongoengine import Admin
from admin.views.commercial_loans_view import CommercialLoansView
from admin.views.employees_view import EmployeesView
from admin.views.employer_approval_view import EmployerApprovalView
from admin.views.loan_application_view import LoanApplicationsView
from admin.views.offers_view import OffersView
from admin.views.promoters_view import PromotersView
from admin.views.repayment_reconciliation_view import RepaymentReconciliationView

from dal.models.db_manager import DBManager
from admin.views.employer_leads_view import \
    EmployerLeadsView
from admin.tasks.employer_emails import employer_emails_router
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
            f'<a href="/{os.getenv("STAGE")}/ops-admin/admin">Login to Employer Approval Portal</a>'), name="admin:prelogin"),
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


"""Initialize Admin Dashboard App"""
admin = Admin(
    "Unipe Employer Dashboard",
    base_url="/admin",
    logo_url="https://static.wixstatic.com/media/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png/v1/fill/w_400,h_80,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png",
    login_logo_url="https://static.wixstatic.com/media/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png/v1/fill/w_400,h_80,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/4d5c44_6938179427f345a0b5c4b2e491f50239~mv2.png",
    auth_provider=GoogleOAuthProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key=config.secret)],
    templates_dir="admin/templates",
    index_view=CustomView(
        label="Home Page",
        icon="fa fa-users",
        name="Home Page",
        add_to_menu=False,
        template_path="/index.html"
    )
)


"""Add Admin Views Here admin.add_view"""
admin.add_view(EmployerApprovalView)
admin.add_view(EmployeesView)
admin.add_view(EmployerLeadsView)

# admin.add_view(LoanApplicationsView)
admin.add_view(
    DropDown(
        "Loan Ops",
        icon="fa fa-inr",
        views=[
            OffersView(),
            LoanApplicationsView(),
            RepaymentReconciliationView(),
        ],
    )
)

admin.add_view(
    DropDown(
        "Commercial Loans",
        icon="fa fa-coins",
        views=[
            CommercialLoansView(),
            PromotersView()
        ],
    )
)

"""Mount All The Views"""
admin.mount_to(admin_app)

"""Mount Additional Services"""

admin_app.mount("/employer-emails", employer_emails_router)

"""Run the Server"""
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(admin_app, host="127.0.0.1", port=8000)
