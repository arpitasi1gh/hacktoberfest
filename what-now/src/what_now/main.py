from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from . import database as db
from .config import get_session_secret, https_only_cookies
from .routers import accounts, pages, suggestions, tasks


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    db.init_db()
    yield


app = FastAPI(title="What Now?", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=get_session_secret(),
    session_cookie="whatnow_session",
    same_site="lax",
    https_only=https_only_cookies(),
    max_age=60 * 60 * 24 * 14,
)
app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).resolve().parent / "static")),
    name="static",
)
app.include_router(pages.router)
app.include_router(accounts.router)
app.include_router(tasks.router)
app.include_router(suggestions.router)
