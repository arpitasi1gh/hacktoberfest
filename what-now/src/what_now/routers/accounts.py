import re
import sqlite3

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from .. import auth, database as db
from ..dependencies import require_user, verify_csrf
from ..web import render

router = APIRouter()
EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$"
)
DUMMY_PASSWORD_HASH = auth.hash_password("invalid-account-password")


def _login_redirect(request: Request) -> RedirectResponse | None:
    if request.session.get("user_id") is not None:
        return RedirectResponse("/", status_code=303)
    return None


@router.get("/login")
def login_page(request: Request):
    redirect = _login_redirect(request)
    if redirect:
        return redirect
    return render(request, "auth.html", {"auth_mode": "login"})


@router.get("/signup")
def signup_page(request: Request):
    redirect = _login_redirect(request)
    if redirect:
        return redirect
    return render(request, "auth.html", {"auth_mode": "signup"})


@router.post("/login", dependencies=[Depends(verify_csrf)])
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    normalized_email = email.strip().lower()
    user = db.get_user_for_login(normalized_email)
    stored_hash = user["password_hash"] if user else DUMMY_PASSWORD_HASH
    candidate_password = password if 1 <= len(password) <= 128 else "invalid-account-password"
    valid_password = auth.verify_password(candidate_password, stored_hash)
    valid_password = valid_password and 1 <= len(password) <= 128
    if user is None or not valid_password:
        return render(
            request,
            "auth.html",
            {
                "auth_mode": "login",
                "error": "That email and password combination was not recognized.",
                "email": email,
            },
            status_code=401,
        )

    theme = request.session.get("theme", "light")
    request.session.clear()
    request.session["user_id"] = user["id"]
    request.session["theme"] = theme
    return RedirectResponse("/", status_code=303)


@router.post("/signup", dependencies=[Depends(verify_csrf)])
def signup(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    full_name = full_name.strip()
    email = email.strip().lower()
    error = None
    if not full_name or len(full_name) > 80:
        error = "Enter a name between 1 and 80 characters."
    elif (
        len(email) > 254
        or len(email.rsplit("@", 1)[0]) > 64
        or not EMAIL_PATTERN.fullmatch(email)
    ):
        error = "Enter a valid email address."
    elif len(password) < 10 or len(password) > 128:
        error = "Choose a password between 10 and 128 characters."
    elif password != confirm_password:
        error = "Your passwords do not match."

    if error:
        return render(
            request,
            "auth.html",
            {
                "auth_mode": "signup",
                "error": error,
                "full_name": full_name,
                "email": email,
            },
            status_code=422,
        )

    try:
        user_id = db.create_user(full_name, email, auth.hash_password(password))
    except sqlite3.IntegrityError:
        return render(
            request,
            "auth.html",
            {
                "auth_mode": "signup",
                "error": "An account with that email already exists.",
                "full_name": full_name,
                "email": email,
            },
            status_code=409,
        )

    theme = request.session.get("theme", "light")
    request.session.clear()
    request.session["user_id"] = user_id
    request.session["theme"] = theme
    return RedirectResponse("/", status_code=303)


@router.post("/logout", dependencies=[Depends(require_user), Depends(verify_csrf)])
def logout(request: Request):
    theme = request.session.get("theme", "light")
    request.session.clear()
    request.session["theme"] = theme
    return RedirectResponse("/login", status_code=303)
