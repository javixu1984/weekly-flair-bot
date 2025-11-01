# weekly_flair_bot.py
import os, re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import praw

SUBREDDIT = os.environ.get("SUBREDDIT", "RoccoSiffrediPorn")
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"

MEDALS = ["🥇 Gold", "🥈 Silver", "🥉 Bronze"]
MEDAL_PREFIX_RE = re.compile(r"^(🥇 Gold|🥈 Silver|🥉 Bronze)\s*\|\s*", re.IGNORECASE)

reddit = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    user_agent=os.environ.get("REDDIT_USER_AGENT", "weekly-flair-bot by u/WeeklyFlairBot v1"),
    username=os.environ["REDDIT_USERNAME"],   # WeeklyFlairBot
    password=os.environ["REDDIT_PASSWORD"],
)

sub = reddit.subreddit(SUBREDDIT)

def week_range_eu_madrid_prev():
    tz = ZoneInfo("Europe/Madrid")
    now = datetime.now(tz)
    this_monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    start = this_monday - timedelta(days=7)
    end = this_monday
    return start, end

def utc_ts(dt): return int(dt.astimezone(timezone.utc).timestamp())

def exclusions():
    mods = {m.name.lower() for m in sub.moderator()}
    mods.add("automoderator")
    return mods

def collect_scores(start_dt, end_dt):
    start_ts, end_ts = utc_ts(start_dt), utc_ts(end_dt)
    excl = exclusions()
    scores = {}  # user -> dict

    def bump(author, score, ts, kind):
        if not author: return
        name = author.lower()
        if name in excl or name.endswith("bot"): return
        d = scores.setdefault(name, {"total":0,"post":0,"comment":0,"first":ts})
        d["total"] += score
        d[kind] += score
        d["first"] = min(d["first"], ts)

    # submissions
    for s in sub.new(limit=None):
        if s.created_utc < start_ts: break
        if s.created_utc < end_ts:
            bump(getattr(s.author, "name", None), s.score, s.created_utc, "post")

    # comments
    for c in sub.comments(limit=None):
        if c.created_utc < start_ts: break
        if c.created_utc < end_ts:
            bump(getattr(c.author, "name", None), c.score, c.created_utc, "comment")

    return scores

def rank_top3(scores):
    arr = [(u,d["total"],d["post"],d["comment"],d["first"]) for u,d in scores.items()]
    arr.sort(key=lambda x: (-x[1], -x[2], -x[3], x[4]))
    return arr[:3]

def get_flair_text(user):
    try:
        for f in sub.flair(redditor=user):
            return (f.get("flair_text") or "").strip()
    except Exception:
        pass
    return ""

def set_flair(user, medal_text):
    old = get_flair_text(user)
    base = MEDAL_PREFIX_RE.sub("", old).strip()
    new_text = f"{medal_text} | {base}" if base else medal_text
    if DRY_RUN:
        print(f"[DRY RUN] Set u/{user} -> '{new_text}'"); return
    sub.flair.set(user, text=new_text)
    print(f"Set u/{user} -> '{new_text}'")

def clear_medal(user):
    old = get_flair_text(user)
    if not old or not MEDAL_PREFIX_RE.match(old): return
    base = MEDAL_PREFIX_RE.sub("", old).strip()
    if DRY_RUN:
        print(f"[DRY RUN] Clear medal u/{user}: '{old}' -> '{base}'"); return
    if base: sub.flair.set(user, text=base)
    else: sub.flair.delete(user)
    print(f"Cleared medal u/{user}")

def main():
    start, end = week_range_eu_madrid_prev()
    print(f"Window (Europe/Madrid): {start.isoformat()} -> {end.isoformat()}")
    scores = collect_scores(start, end)
    top = rank_top3(scores)

    users = [u for u, *_ in top]
    for u in users: clear_medal(u)
    for i, u in enumerate(users):
        set_flair(u, MEDALS[i])

    print("Winners:")
    for i, (u, tot, ps, cs, _) in enumerate(top, 1):
        print(f"{i}. u/{u} — total={tot} (posts={ps}, comments={cs})")

if __name__ == "__main__":
    main()
