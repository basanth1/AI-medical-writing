"""
backend/api/auth.py
Session-based authentication for the CTDGen application.
- In-memory sessions (reset on server restart)
- Cookie-based tokens
- Middleware for route protection
- Self-registration for user-role accounts
"""
from __future__ import annotations
import secrets
import time
import logging
from typing import Optional, Dict
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.config import get_settings
from backend.db.user_store import register_user, verify_user, user_exists
logger = logging.getLogger(__name__)
# ── Session store (in-memory) ─────────────────────────────────────────────────
_sessions: Dict[str, dict] = {}
COOKIE_NAME = "ctdgen_session"
SESSION_TTL = 86400  # 24 hours
def create_session(username: str, role: str) -> str:
    token = secrets.token_urlsafe(32)
    _sessions[token] = {
        "username": username,
        "role": role,
        "created_at": time.time(),
    }
    return token
def validate_session(token: str) -> Optional[dict]:
    session = _sessions.get(token)
    if not session:
        return None
    if time.time() - session["created_at"] > SESSION_TTL:
        _sessions.pop(token, None)
        return None
    return session
def destroy_session(token: str) -> None:
    _sessions.pop(token, None)
# ── Credential check ─────────────────────────────────────────────────────────
def authenticate(username: str, password: str) -> Optional[str]:
    """Return role ('admin' | 'user') or None if invalid."""
    # 1. Check .env admin/user credentials first
    cfg = get_settings()
    if username == cfg.admin_username and password == cfg.admin_password:
        return "admin"
    if username == cfg.user_username and password == cfg.user_password:
        return "user"
    # 2. Check self-registered users
    registered = verify_user(username, password)
    if registered:
        return registered["role"]
    return None
# ── Auth router ───────────────────────────────────────────────────────────────
auth_router = APIRouter(tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str
    password: str
    full_name: str = ""
    email: str = ""

@auth_router.post("/auth/signup")
def signup(body: SignupRequest):
    """Register a new user account (role='user'). Admin accounts are team-provisioned."""
    # Block reserved usernames (the .env admin/user names)
    cfg = get_settings()
    reserved = {cfg.admin_username.lower(), cfg.user_username.lower()}
    if body.username.lower().strip() in reserved:
        raise HTTPException(status_code=409, detail="This username is reserved")
    try:
        user = register_user(
            username=body.username,
            password=body.password,
            full_name=body.full_name,
            email=body.email,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    # Auto-login after signup
    token = create_session(user["username"], user["role"])
    response = JSONResponse(content={
        "ok": True,
        "role": user["role"],
        "username": user["username"],
        "redirect": cfg.frontend_url,
    })
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_TTL,
        path="/",
    )
    return response

@auth_router.post("/auth/login")
def login(body: LoginRequest):
    role = authenticate(body.username, body.password)
    if not role:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_session(body.username, role)
    cfg = get_settings()
    redirect_url = "/admin/ui" if role == "admin" else cfg.frontend_url
    response = JSONResponse(content={
        "ok": True,
        "role": role,
        "username": body.username,
        "redirect": redirect_url,
    })
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_TTL,
        path="/",
    )
    return response
@auth_router.post("/auth/logout")
def logout(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        destroy_session(token)
    cfg = get_settings()
    response = RedirectResponse(url=f"{cfg.frontend_url.rstrip('/')}/login", status_code=302)
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return response
@auth_router.get("/auth/check")
def check_auth(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    session = validate_session(token) if token else None
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"ok": True, "username": session["username"], "role": session["role"]}
# ── Login page route ─────────────────────────────────────────────────────────
@auth_router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request):
    # If already authenticated, redirect to appropriate page
    token = request.cookies.get(COOKIE_NAME)
    session = validate_session(token) if token else None
    if session:
        if session["role"] == "admin":
            return RedirectResponse(url="/admin/ui", status_code=302)
        cfg = get_settings()
        return RedirectResponse(url=cfg.frontend_url, status_code=302)
    cfg = get_settings()
    return RedirectResponse(url=f"{cfg.frontend_url.rstrip('/')}/login", status_code=302)
# ── Auth middleware ───────────────────────────────────────────────────────────
# Paths that never require authentication
_PUBLIC_PATHS = frozenset({
    "/login", "/auth/login", "/auth/logout", "/auth/check", "/auth/signup",
    "/docs", "/redoc", "/openapi.json",
})
_PUBLIC_PREFIXES = ("/api/",)  # Keep API public for frontend access
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Always allow public paths
        if path in _PUBLIC_PATHS or any(path.startswith(p) for p in _PUBLIC_PREFIXES):
            return await call_next(request)
        # Allow static assets
        if path.startswith("/assets"):
            return await call_next(request)
        token = request.cookies.get(COOKIE_NAME)
        session = validate_session(token) if token else None
        # Root path — redirect based on auth state
        if path == "/":
            if not session:
                return RedirectResponse(url="/login", status_code=302)
            if session["role"] == "admin":
                return RedirectResponse(url="/admin/ui", status_code=302)
            # User role — pass through to SPA/frontend handler
            cfg = get_settings()
            return RedirectResponse(url=cfg.frontend_url, status_code=302)
        # Admin routes — require admin role
        if path.startswith("/admin"):
            if not session:
                return RedirectResponse(url="/login", status_code=302)
            if session["role"] != "admin":
                return RedirectResponse(url="/login", status_code=302)
            return await call_next(request)
        # Everything else — pass through
        return await call_next(request)
