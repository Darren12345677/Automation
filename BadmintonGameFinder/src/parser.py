"""
parser.py — regex patterns to extract session details from game posts,
and formatting of the final alert message.
"""

import re
from filters import extract_venue_line

# ---------------------------------------------------------------------------
# PATTERNS
# ---------------------------------------------------------------------------

DATE_PATTERN = re.compile(
    r"""
    (?:(?:mon|tue|wed|thu|fri|sat|sun)\w*[\s,]*)?
    (?:
        \d{1,2}(?:st|nd|rd|th)?[\s/\-]*
        (?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*
        (?:[\s,]*\d{4})?
        |
        (?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*[\s/\-]*\d{1,2}
        |
        \d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

TIME_PATTERN = re.compile(
    r'\b\d{1,2}(?::\d{2})?\s*(?:am|pm)?\s*[-\u2013to]+\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)\b',
    re.IGNORECASE,
)

PRICE_PATTERN = re.compile(
    r'\$\s*\d+(?:\.\d{1,2})?(?:\s*(?:/\s*pax|per\s*pax|per\s*person))?'
    r'|\d+\s*(?:per\s*pax|per\s*person|\/pax)',
    re.IGNORECASE,
)

CONTACT_PATTERN = re.compile(
    r'(?:wa|whatsapp|text|call|contact)[:\s]+(?:\w+\s+)?(\+?6?\d[\d\s]{6,11}\d)'
    r'|(\+?65[\s\-]?\d{4}[\s\-]?\d{4})'
    r'|(?<!\d)([89]\d{7})(?!\d)',
    re.IGNORECASE,
)

LEVEL_PATTERN = re.compile(
    r'\b(beginner|intermediate|advanced|open|all\s*level|'
    r'lb[\s\-]*mb|mb[\s\-]*hb|hb[\s\-]*li|lb|mb|hb|li)\b',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# SESSION EXTRACTION
# ---------------------------------------------------------------------------

def _extract_single_session(chunk: str, date_str: str = None) -> dict | None:
    """Extract one session's details from a text chunk."""
    if not date_str:
        m = DATE_PATTERN.search(chunk)
        date_str = m.group().strip() if m else None

    tm = TIME_PATTERN.search(chunk)
    pm = PRICE_PATTERN.search(chunk)
    lm = LEVEL_PATTERN.search(chunk)
    cm = CONTACT_PATTERN.search(chunk)

    time_str    = tm.group().strip() if tm else None
    price_str   = pm.group().strip() if pm else None
    level_str   = lm.group().strip() if lm else None
    contact_str = next((g for g in cm.groups() if g), None) if cm else None

    # Require at least a time or price to count as a real session
    if not time_str and not price_str:
        return None

    return {
        "date":    date_str,
        "time":    time_str,
        "price":   price_str,
        "level":   level_str,
        "contact": contact_str,
    }


def parse_sessions(text: str) -> list[dict]:
    """
    Split message on date markers and extract a session from each chunk.
    Falls back to a single session parse if no dates are found.
    """
    date_matches = list(DATE_PATTERN.finditer(text))

    if not date_matches:
        s = _extract_single_session(text)
        return [s] if s else []

    sessions = []
    for i, m in enumerate(date_matches):
        start = m.start()
        end   = date_matches[i + 1].start() if i + 1 < len(date_matches) else len(text)
        s = _extract_single_session(text[start:end], m.group().strip())
        if s:
            sessions.append(s)

    # Fallback if chunking yielded nothing
    if not sessions:
        s = _extract_single_session(text)
        if s:
            sessions.append(s)

    return sessions


# ---------------------------------------------------------------------------
# ALERT FORMATTING
# ---------------------------------------------------------------------------

def format_alert(
    text: str,
    chat_title: str,
    sender: object,          # Telethon User object
) -> str:
    """Build the alert message to send to the private channel."""

    # Sender mention — prefer @username, fall back to inline tg:// link
    if getattr(sender, "username", None):
        sender_mention = f"@{sender.username}"
    else:
        name = getattr(sender, "first_name", None) or "Unknown"
        sender_mention = f"[{name}](tg://user?id={sender.id})"

    lines = [
        "🏸 **West SG Badminton Game Found!**",
        f"📍 Group: {chat_title}",
        f"👤 Posted by: {sender_mention}",
    ]

    lines.append("")

    lines.append(text)

    return "\n".join(lines)