import os
import secrets
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
SESSION_SECRET_FILE = DATA_DIR / ".session-secret"


def get_session_secret() -> str:
    configured_secret = os.getenv("WHATNOW_SECRET_KEY")
    if configured_secret:
        return configured_secret

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(
            SESSION_SECRET_FILE,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
    except FileExistsError:
        return SESSION_SECRET_FILE.read_text(encoding="utf-8").strip()

    with os.fdopen(descriptor, "w", encoding="utf-8") as secret_file:
        secret_file.write(secrets.token_urlsafe(48))
    return SESSION_SECRET_FILE.read_text(encoding="utf-8").strip()


def https_only_cookies() -> bool:
    return os.getenv("WHATNOW_HTTPS_ONLY", "").lower() in {"1", "true", "yes"}
