import secrets

from fastapi import Form, HTTPException, Request

from . import database as db


def require_user(request: Request) -> dict:
    user_id = request.session.get("user_id")
    if not isinstance(user_id, int):
        raise HTTPException(status_code=303, headers={"Location": "/login"})

    user = db.get_user_by_id(user_id)
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user


def csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not isinstance(token, str):
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token


def verify_csrf(
    request: Request,
    submitted_token: str = Form(..., alias="csrf_token"),
) -> None:
    expected_token = request.session.get("csrf_token")
    if not isinstance(expected_token, str) or not secrets.compare_digest(
        expected_token,
        submitted_token,
    ):
        raise HTTPException(status_code=403, detail="Invalid form token. Reload and try again.")
