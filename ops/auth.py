import os
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException
from starlette.config import Config
from starlette.datastructures import URL
from starlette.requests import Request
from starlette.responses import RedirectResponse

from kyc.config import OAuthConfig


oauth = OAuth(
    Config(
        environ={
            'GOOGLE_CLIENT_ID': OAuthConfig.GOOGLE_CLIENT_ID,
            'GOOGLE_CLIENT_SECRET': OAuthConfig.GOOGLE_CLIENT_SECRET
        }
    )
)

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


auth_router = APIRouter(
    tags=["auth"]
)


async def get_user(request: Request) -> Optional[dict]:
    """
        Fetches the logged in User
    """
    user = request.session.get('user')
    internal_redirect_uri = str(request.url)
    if "local" not in internal_redirect_uri:
        """if local is not present in url, then this is happening on ecr which requires all requests to be https"""
        internal_redirect_uri = "https" + internal_redirect_uri[4:]
    if user is not None:
        return user
    else:
        login_redirect_uri = str(URL(auth_router.url_path_for("login")).include_query_params(
            internal_redirect_uri=internal_redirect_uri))
        raise HTTPException(
            status_code=302,
            detail='Could not validate credentials.',
            headers={
                "Location": login_redirect_uri
            }
        )


@auth_router.get('/login', tags=['authentication'])
async def login(request: Request):
    # Redirect Google OAuth back to our application
    redirect_uri = str(request.url).replace("login", "auth").split("?")[0]
    if "local" not in redirect_uri:
        """if local is not present in url, then this is happening on ecr which requires all requests to be https"""
        redirect_uri = "https" + redirect_uri[4:]
    internal_redirect_uri = request.query_params["internal_redirect_uri"]

    return await oauth.google.authorize_redirect(request, redirect_uri, state=internal_redirect_uri)


@auth_router.get('/auth')
async def auth(request: Request):
    # Perform Google OAuth
    token = await oauth.google.authorize_access_token(request)
    user = token['userinfo']
    internal_redirect_uri = request.query_params["state"]

    # Save the user
    request.session['user'] = dict(user)

    return RedirectResponse(url=internal_redirect_uri)
