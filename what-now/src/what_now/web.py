from typing import Any
from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from .dependencies import csrf_token

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


def render(
    request: Request,
    template_name: str,
    context: dict[str, Any] | None = None,
    status_code: int = 200,
):
    values = dict(context or {})
    values.setdefault("user", None)
    values.setdefault("theme", request.session.get("theme", "light"))
    values.setdefault("csrf_token", csrf_token(request))
    return templates.TemplateResponse(
        request,
        template_name,
        values,
        status_code=status_code,
    )


def render_fragment(
    request: Request,
    template_name: str,
    context: dict[str, Any] | None = None,
) -> str:
    values = dict(context or {})
    values.setdefault("user", None)
    values.setdefault("theme", request.session.get("theme", "light"))
    values.setdefault("csrf_token", csrf_token(request))
    return templates.get_template(template_name).render(request=request, **values)
