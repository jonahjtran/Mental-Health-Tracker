from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse, Response

from backend.app.core.config import settings
from backend.app.core.security import create_access_token
from backend.app.db.session import get_db
from backend.app.services.users_services import get_or_create_user_from_oauth

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    client_kwargs={"scope": "openid email profile"},
)

@router.get("/login/google")
async def login_with_google(request: Request):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Google client ID or secret is not configured")

    return await oauth.google.authorize_redirect(request, settings.google_redirect_uri)

@router.get("/callback/google")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get("userinfo")
    except OAuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Google OAuth error: {e}") from e

    if not userinfo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch user information from Google")

    email = userinfo.get("email")
    subject = userinfo.get("sub")
    name = userinfo.get("name") or userinfo.get("given_name") or email
    avatar_url = userinfo.get("picture")

    if not email or not subject:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or subject is missing in Google user information")

    user = get_or_create_user_from_oauth(
        db,
        provider="google",
        subject=subject,
        email=email,
        name=name,
        avatar_url=avatar_url,
    )

    access_token = create_access_token(user_id = user.id)

    response = RedirectResponse(url=settings.frontend_url)
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=False, # TODO: change to True in production
        samesite="lax",
        max_age=settings.jwt_expiration_minutes * 60,
    )
    return response

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie("access_token")
    return response

@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url=settings.frontend_url)
    response.delete_cookie("access_token")
    return response
