"""
Auth API — login / logout / me
POST /auth/login   → httpOnly cookie JWT
POST /auth/logout  → clear cookie
GET  /auth/me      → current user info
"""
from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import COOKIE, EXPIRE_H, create_token, hash_password, verify_password
from app.core.postgres_client import get_pg_session

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginBody(BaseModel):
    login: str
    password: str


class ChangePasswordBody(BaseModel):
    current_password: str
    new_password: str


async def _get_user(session: AsyncSession, login: str) -> dict | None:
    res = await session.execute(
        text("""
            SELECT u.user_id, u.login, u.password_hash, u.role,
                   u.student_id, u.must_change_password, u.is_active
            FROM app_user u WHERE u.login = :login
        """),
        {"login": login},
    )
    row = res.mappings().first()
    return dict(row) if row else None


@router.post("/login")
async def login(
    body: LoginBody,
    response: Response,
    session: AsyncSession = Depends(get_pg_session),
):
    user = await _get_user(session, body.login)
    if not user or not user["is_active"]:
        raise HTTPException(401, "Identifiants invalides")
    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Identifiants invalides")

    # Update last_login
    await session.execute(
        text("UPDATE app_user SET last_login_at = now() WHERE user_id = :uid"),
        {"uid": user["user_id"]},
    )
    await session.commit()

    token = create_token(user["user_id"], user["login"], user["role"])
    response.set_cookie(
        key=COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=EXPIRE_H * 3600,
        path="/",
    )
    return {
        "user_id": user["user_id"],
        "login": user["login"],
        "role": user["role"],
        "student_id": user["student_id"],
        "must_change_password": user["must_change_password"],
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=COOKIE, path="/")
    return {"ok": True}


@router.get("/me")
async def me(
    session: AsyncSession = Depends(get_pg_session),
    apt_token: str | None = Cookie(default=None),
):
    from jose import JWTError
    from app.core.auth import decode_token
    if not apt_token:
        raise HTTPException(401, "Non authentifié")
    try:
        payload = decode_token(apt_token)
    except JWTError:
        raise HTTPException(401, "Token invalide ou expiré")

    user = await _get_user(session, payload["login"])
    if not user or not user["is_active"]:
        raise HTTPException(401, "Compte désactivé")
    return {
        "user_id": user["user_id"],
        "login": user["login"],
        "role": user["role"],
        "student_id": user["student_id"],
        "must_change_password": user["must_change_password"],
    }


@router.post("/change-password")
async def change_password(
    body: ChangePasswordBody,
    response: Response,
    session: AsyncSession = Depends(get_pg_session),
    apt_token: str | None = Cookie(default=None),
):
    from jose import JWTError
    from app.core.auth import decode_token
    if not apt_token:
        raise HTTPException(401, "Non authentifié")
    try:
        payload = decode_token(apt_token)
    except JWTError:
        raise HTTPException(401, "Token invalide")

    user = await _get_user(session, payload["login"])
    if not user:
        raise HTTPException(401, "Utilisateur introuvable")
    if not verify_password(body.current_password, user["password_hash"]):
        raise HTTPException(400, "Mot de passe actuel incorrect")
    if len(body.new_password) < 8:
        raise HTTPException(400, "Le nouveau mot de passe doit faire au moins 8 caractères")

    await session.execute(
        text("""
            UPDATE app_user
            SET password_hash = :h, must_change_password = false
            WHERE user_id = :uid
        """),
        {"h": hash_password(body.new_password), "uid": user["user_id"]},
    )
    await session.commit()

    # Reissue token
    token = create_token(user["user_id"], user["login"], user["role"])
    response.set_cookie(
        key=COOKIE, value=token, httponly=True,
        samesite="lax", max_age=EXPIRE_H * 3600, path="/",
    )
    return {"ok": True}
