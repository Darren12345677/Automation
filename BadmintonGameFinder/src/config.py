"""
config.py — load .env once here, import settings everywhere else.
Never call load_dotenv() in any other file.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        raise ValueError(f"Missing required env var: {key}  (check your .env file)")
    return val


# --- Telegram credentials (required) ---
API_ID   = int(_require("TELEGRAM_API_ID"))
API_HASH = _require("TELEGRAM_API_HASH")

# --- Where to send alerts ---
# "me" = your Saved Messages
# "@channelname" = public channel
# integer = private channel ID (e.g. -1001234567890)
_alert_raw = os.environ.get("ALERT_CHAT", "me")
try:
    ALERT_CHAT = int(_alert_raw)   # numeric channel ID
except ValueError:
    ALERT_CHAT = _alert_raw        # "me" or @username

# --- Groups to monitor ---
# List group titles or @usernames. Empty list = monitor ALL groups.
WATCH_GROUPS: list[str] = [
    "🏸 SG Badminton Community",
    "sg_badminton",
]

# --- Topics to listen to within those groups (forum/thread groups) ---
# Empty list = listen to all topics.
WATCH_TOPICS: list[str] = [
    "Available games",
    "Looking for Games/Game requests",
]

# --- West Singapore venue keywords (lowercase, partial match) ---
WEST_VENUES: list[str] = [
    # MRT / estates
    "jurong", "clementi", "buona vista", "dover", "boon lay", "lakeside",
    "chinese garden", "pioneer", "joo koon", "tuas",
    "west coast", "kent ridge", "one-north", "pasir panjang",
    "commonwealth", "queenstown", "redhill", "tiong bahru",
    "bukit timah", "beauty world", "king albert park", "sixth avenue",
    "tan kah kee", "botanic garden", "holland", "farrer road",
    "bukit batok", "bukit gombak", "choa chu kang", "tengah",
    "ayer rajah", "science park", "yuhua", "taman jurong",
    # Shorthands common in SG group chats
    "j east", "j west", "ccg", "bbt", "cck", "clmti",
    # Sports halls & CCs
    "jurong east sports", "jurong west sports", "clementi sports",
    "bukit batok sports", "choa chu kang sports", "commonwealth sports",
    "queenstown sports", "west coast cc", "clementi cc", "boon lay cc",
    "bukit timah cc", "ayer rajah cc", "hong kah cc", "yuhua cc",
    "taman jurong cc", "pioneer cc", "jurong green cc",
]

# --- Badminton signal keywords ---
# Message must contain at least one to be considered a game post.
BADMINTON_SIGNALS: list[str] = [
    "badminton", "court", "shuttle", "shuttlecock",
    "per pax", "/pax", "per person",
    "friendly", "social game", "social badminton",
    "looking for player", "lfp",
    "join us to play", "join us for",
    "li ning", "lining", "yonex", "victor",
]

# --- Session file for Telethon login persistence ---
SESSION_FILE = "badminton_session"