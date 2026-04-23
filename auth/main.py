"""
JWT-Auth-Service für Home Assistant.

Endpunkte:
  POST /auth/login       – Nutzername/Passwort → Access + Refresh Token
  POST /auth/refresh     – Refresh Token → neues Access Token
  GET  /auth/verify      – Access Token prüfen
  GET  /ha/...           – Geschützter HA-API-Proxy
"""

from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from config import settings
from jwt_handler import create_token, decode_token
from users import authenticate_user

app = FastAPI(title="HA JWT Auth Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bearer_scheme = HTTPBearer()

# ---------------------------------------------------------------------------
# Pydantic-Schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class VerifyResponse(BaseModel):
    valid: bool
    username: str


# ---------------------------------------------------------------------------
# Hilfsfunktion: Bearer-Token aus Header extrahieren & validieren
# ---------------------------------------------------------------------------


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> str:
    try:
        payload = decode_token(credentials.credentials, expected_type="access")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return payload["sub"]


# ---------------------------------------------------------------------------
# Auth-Endpunkte
# ---------------------------------------------------------------------------


@app.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
def login(body: LoginRequest):
    """Meldet einen Nutzer an und gibt Access + Refresh Token zurück."""
    if not authenticate_user(body.username, body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültige Anmeldedaten.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(
        access_token=create_token(body.username, "access"),
        refresh_token=create_token(body.username, "refresh"),
    )


@app.post("/auth/refresh", response_model=AccessTokenResponse, tags=["Auth"])
def refresh(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]):
    """Tauscht ein gültiges Refresh Token gegen ein neues Access Token."""
    try:
        payload = decode_token(credentials.credentials, expected_type="refresh")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return AccessTokenResponse(access_token=create_token(payload["sub"], "access"))


@app.get("/auth/verify", response_model=VerifyResponse, tags=["Auth"])
def verify(username: Annotated[str, Depends(get_current_user)]):
    """Prüft, ob das Access Token gültig ist."""
    return VerifyResponse(valid=True, username=username)


# ---------------------------------------------------------------------------
# HA-API-Proxy (geschützt durch JWT)
# ---------------------------------------------------------------------------


@app.api_route(
    "/ha/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
    tags=["Home Assistant Proxy"],
)
async def ha_proxy(
    path: str,
    request: Request,
    _username: Annotated[str, Depends(get_current_user)],
):
    """
    Leitet Anfragen an die HA-REST-API weiter.
    Authentifiziert sich gegenüber HA mit dem konfigurierten Long-Lived Token.
    """
    if not settings.HA_LONG_LIVED_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="HA_LONG_LIVED_TOKEN nicht konfiguriert.",
        )

    target_url = f"{settings.HA_BASE_URL}/api/{path}"
    headers = {
        "Authorization": f"Bearer {settings.HA_LONG_LIVED_TOKEN}",
        "Content-Type": "application/json",
    }
    body = await request.body()

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=dict(request.query_params),
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"HA nicht erreichbar: {exc}",
            ) from exc

    return response.json()
