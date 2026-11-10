import json
from pathlib import Path

TONES_FILE = Path("tone.json")

def get_tones() -> str:
    if TONES_FILE.exists():
        try:
            return "\n\n".join(json.loads(TONES_FILE.read_text()))
        except Exception:
            return ""
    return ""

def save_tone(text: str):
    tones = []
    if TONES_FILE.exists():
        try:
            tones = json.loads(TONES_FILE.read_text())
        except Exception:
            pass
    tones.append(text)
    TONES_FILE.write_text(json.dumps(tones))