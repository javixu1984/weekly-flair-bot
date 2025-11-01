# weekly_flair_bot.py (cabecera reforzada)
import os, sys, traceback, re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

def require_env(name):
    v = os.environ.get(name)
    if not v:
        raise RuntimeError(f"Missing required env var: {name}")
    return v

SUBREDDIT = os.environ.get("SUBREDDIT", "RoccoSiffrediPorn")
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"

# Verificación temprana de variables
CLIENT_ID = require_env("REDDIT_CLIENT_ID")
CLIENT_SECRET = require_env("REDDIT_CLIENT_SECRET")
USERNAME = require_env("REDDIT_USERNAME")
PASSWORD = require_env("REDDIT_PASSWORD")
USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "weekly-flair-bot by u/WeeklyFlairBot v1")

import praw

def debug_auth_and_perms():
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        username=USERNAME,
        password=PASSWORD,
        user_agent=USER_AGENT,
    )
    me = reddit.user.me()
    print("Authenticated as:", me)
    sub = reddit.subreddit(SUBREDDIT)
    # Comprobar que el bot es mod
    mods = {m.name for m in sub.moderator()}
    print("Is bot moderator?", str(me) in mods)
    return reddit, sub

def main():
    reddit, sub = debug_auth_and_perms()
    # ... aquí continúa tu script original (funciones, lógica, etc.)
    # Puedes pegar a partir de donde empezaba antes: MEDALS, regex, week_range, etc.

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        sys.exit(1)
