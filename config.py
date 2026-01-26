
from dotenv import load_dotenv
import os
from pathlib import Path

ENV_FILE = Path("config.env")

def _load_env_file(path: Path) -> None:

    encodings_to_try = ["utf-8", "utf-16", "utf-16-le", "utf-16-be"]
    for enc in encodings_to_try:
        try:
            # override=False keeps any pre-set environment values (safer for prod)
            if load_dotenv(path, encoding=enc, override=False):
                return
        except UnicodeDecodeError:
            continue
    if path.exists():
        raise RuntimeError(
            f"Failed to read {path} with encodings {encodings_to_try}. "
            "Re-save the file as UTF-8 (without BOM) or recreate it."
        )

# Perform load
_load_env_file(ENV_FILE)

class Config:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    BOT_LOGO = os.environ.get("BOT_LOGO", "https://files.catbox.moe/xz4i4q.jpg")
    BOT_NAME = os.environ.get("BOT_NAME", "Roxe")
    # Allow space-separated prefixes; default single '!'
    PREFIX = os.environ.get("PREFIX", "!").split()
    # Support multiple owners: OWNER_IDS or OWNER_ID can contain comma/space separated IDs
    _owners_raw = os.environ.get("OWNER_IDS") or os.environ.get("OWNER_ID", "0")
    OWNER_IDS = []
    for token in _owners_raw.replace(",", " ").split():
        try:
            OWNER_IDS.append(int(token))
        except ValueError:
            continue
    if not OWNER_IDS:
        OWNER_IDS = [0]
    # Backwards compatible single ID attribute (first one)
    OWNER_ID = OWNER_IDS[0]

    DATABASE_URL = os.environ.get("DATABASE_URL", "")  

    # Early validation of required secrets
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing. Set it in config.env or environment.")
    
    BOT_VERSION = "1.0.0"  
    # Privileged intents configuration flags (string 'true' -> True)
    INTENTS_MESSAGE_CONTENT = os.environ.get("INTENTS_MESSAGE_CONTENT", "true").lower() == "true"
    INTENTS_GUILD_MEMBERS = os.environ.get("INTENTS_GUILD_MEMBERS", "false").lower() == "true"
    INTENTS_PRESENCES = os.environ.get("INTENTS_PRESENCES", "false").lower() == "true"

