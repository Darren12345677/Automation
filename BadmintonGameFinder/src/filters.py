"""
filters.py — keyword-based filters to decide if a message is relevant.
No regex here, just fast string matching.
"""

from config import BADMINTON_SIGNALS, WEST_VENUES


def is_badminton_post(text: str) -> bool:
    """Return True if the message looks like a badminton game announcement."""
    tl = text.lower()
    return any(kw in tl for kw in BADMINTON_SIGNALS)


def is_west_singapore(text: str) -> bool:
    """Return True if the message mentions a West Singapore location."""
    tl = text.lower()
    return any(venue in tl for venue in WEST_VENUES)


def extract_venue_line(text: str) -> str | None:
    """Return the first line that contains a West SG keyword, or None."""
    for line in text.splitlines():
        if is_west_singapore(line) and len(line.strip()) > 3:
            return line.strip()
    return None